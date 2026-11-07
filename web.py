"""Painel web do EvoSpec-UX.

Rotas principais:
  /                 painel (especificações, evidências, propostas, verificação, rastreabilidade)
  /app/             aplicação de referência (formulário de matrícula, versão atual)
  /versoes/v1       versão 1 do formulário (antes da evidência EVD-17), para comparação
  /specs/<arquivo>  artefatos do GitHub Spec Kit (spec.md, plan.md, tasks.md...)
  /constituicao     constituição do projeto (.specify/memory/constitution.md)
  POST /evidencias  registra nova evidência
  POST /propor/<id> gera proposta de mudança via LLM (requer ANTHROPIC_API_KEY)
  POST /decidir/<id> registra decisão humana sobre uma proposta
  POST /verificar   executa a verificação independente (testes + axe-core)

Se a variável EVOSPEC_PASSWORD estiver definida, todas as ações (POST) exigem
autenticação HTTP básica (usuário qualquer, senha = EVOSPEC_PASSWORD).
"""
import json
import os
import re
from functools import wraps

import yaml
from flask import Flask, Response, abort, flash, redirect, render_template, request, send_from_directory, url_for

import evospec as es

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "evospec-ux-dev")
PASSWORD = os.environ.get("EVOSPEC_PASSWORD")


def protected(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if PASSWORD:
            auth = request.authorization
            if not auth or auth.password != PASSWORD:
                return Response("Autenticação necessária", 401,
                                {"WWW-Authenticate": 'Basic realm="EvoSpec-UX"'})
        return fn(*args, **kwargs)
    return wrapper


def all_runs():
    if not es.RESULTS.exists():
        return []
    data = [json.loads(p.read_text()) for p in es.RESULTS.glob("run-*.json")]
    return sorted(data, key=lambda r: r["at"], reverse=True)


def runs():
    out = []
    for r in all_runs():
        crit = r["criteria"].values()
        out.append({"label": r["label"], "at": r["at"], "commit": r.get("commit"),
                    "passed": sum(c["passed"] for c in crit), "total": len(crit),
                    "axe": len(r["axe_violations"])})
    return out


@app.get("/")
def index():
    specs = []
    for path, s in es.load_specs().values():
        s = dict(s)
        s["plan_version"] = es.sk.artifact_spec_version(path.parent / "plan.md")
        s["tasks_version"] = es.sk.artifact_spec_version(path.parent / "tasks.md")
        s["docs"] = sorted(p.relative_to(path.parent).as_posix()
                           for p in path.parent.rglob("*.md"))
        specs.append(s)
    evid = [e for _, e in es.load_dir(es.EVID).values()]
    crs = [c for _, c in es.load_dir(es.CHANGES).values()]
    used = {e for c in crs for e in c.get("evidence", [])}
    errors, warns = es.validate(quiet=True)
    history = all_runs()
    last = history[0] if history else None
    base = es.load_baseline()
    regressions = []
    if last and base:
        regressions = [ac for ac, r in last["criteria"].items()
                       if base["criteria"].get(ac, {}).get("passed") and not r["passed"]]
    return render_template(
        "index.html", specs=specs, evid=evid, crs=crs, used=used, errors=errors, warns=warns,
        last=last, base=base, regressions=regressions, rows=es.trace_rows(), runs=runs(),
        has_llm=bool(os.environ.get("ANTHROPIC_API_KEY")), protected=bool(PASSWORD),
        prompt=request.args.get("prompt"))


@app.get("/app/")
def reference_app():
    return send_from_directory(es.APP, "index.html")


@app.get("/versoes/v1")
def reference_v1():
    return send_from_directory(es.ROOT / "docs" / "versoes", "v1.html")


@app.get("/specs/<path:name>")
def spec_file(name):
    if not name.endswith(".md"):
        abort(404)
    return send_from_directory(es.SPECS, name, mimetype="text/plain; charset=utf-8")


@app.get("/constituicao")
def constitution():
    return send_from_directory(es.ROOT / ".specify" / "memory", "constitution.md",
                               mimetype="text/plain; charset=utf-8")


@app.get("/prompts/<path:name>")
def prompt_file(name):
    return send_from_directory(es.CHANGES / "prompts", name, mimetype="text/plain")


@app.get("/saude")
def health():
    return {"status": "ok"}


@app.post("/evidencias")
@protected
def add_evidence():
    f = request.form
    if not f.get("observed", "").strip():
        flash("Descreva o comportamento observado: sem observação não há evidência (regra R2).", "erro")
        return redirect(url_for("index") + "#evidencias")
    ids = [int(re.sub(r"\D", "", p.stem) or 0) for p in es.EVID.glob("EVD-*.yaml")]
    eid = f"EVD-{max(ids + [0]) + 1:02d}"
    data = {
        "id": eid,
        "source": f.get("source") or "teste com usuário",
        "method": f.get("method") or "",
        "participant": f.get("participant") or "",
        "assistive_technology": f.get("assistive_technology") or "",
        "task": f.get("task") or "",
        "observed": f["observed"],
        "impact": f.get("impact") or "",
        "severity": f.get("severity") or "média",
        "wcag": [w.strip() for w in f.get("wcag", "").split(",") if w.strip()],
    }
    es.dump(es.EVID / f"{eid}.yaml", data)
    flash(f"Evidência {eid} registrada.", "ok")
    return redirect(url_for("index") + "#evidencias")


@app.post("/propor/<evd_id>")
@protected
def propose(evd_id):
    try:
        out = es.propose(evd_id, request.form.get("model") or "claude-sonnet-5-5")
    except es.EvoSpecError as exc:
        flash(str(exc), "erro")
        return redirect(url_for("index") + "#evidencias")
    except Exception as exc:  # falha na chamada ao modelo
        flash(f"Falha ao chamar o modelo: {exc}", "erro")
        return redirect(url_for("index") + "#evidencias")
    if out["cr"]:
        flash(f"Rascunho {out['cr']} gerado pelo LLM. Revise e registre a decisão.", "ok")
        return redirect(url_for("index") + "#propostas")
    flash("ANTHROPIC_API_KEY não configurada: o prompt foi gerado para uso manual.", "aviso")
    return redirect(url_for("index", prompt=out["prompt_file"].split("/")[-1]) + "#propostas")


@app.post("/decidir/<cr_id>")
@protected
def decide(cr_id):
    f = request.form
    try:
        diff = es.decide(cr_id, f.get("by", ""), f.get("decision", ""), f.get("note", ""))
    except es.EvoSpecError as exc:
        flash(str(exc), "erro")
        return redirect(url_for("index") + "#propostas")
    msg = f"{cr_id}: decisão '{f.get('decision')}' registrada."
    if diff:
        msg += " A especificação foi versionada; agora faltam testes e implementação (veja a validação)."
    flash(msg, "ok")
    return redirect(url_for("index") + "#propostas")


@app.post("/verificar")
@protected
def run_verify():
    label = re.sub(r"[^\w\-]", "-", request.form.get("label") or "painel")[:40]
    set_base = request.form.get("baseline") == "1"
    try:
        _, regs, ok = es.verify(label, set_base)
    except Exception as exc:
        flash(f"Falha na verificação: {exc}", "erro")
        return redirect(url_for("index") + "#verificacao")
    if regs:
        flash(f"{len(regs)} regressão(ões) detectada(s): {', '.join(regs)}. Linha de base mantida.", "erro")
    elif set_base and ok:
        flash("Verificação sem regressões. Linha de base atualizada.", "ok")
    else:
        flash("Verificação concluída sem regressões.", "ok")
    return redirect(url_for("index") + "#verificacao")


@app.template_filter("yaml")
def to_yaml(value):
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000).strip()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
