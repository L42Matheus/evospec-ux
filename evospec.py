#!/usr/bin/env python3
"""EvoSpec-UX — protótipo de SDD orientado por evidências de usabilidade.

Comandos:
  status                         visão geral de specs, evidências e propostas
  validate                       regras de governança, rastreabilidade e drift
  propose EVD-ID                 gera rascunho de proposta de mudança via LLM
  decide CR-ID --by NOME --decision approved|rejected|clarification|deferred [--note ...]
  verify [--label X] [--set-baseline]
                                 verificação independente (testes + axe-core)
  trace                          gera a matriz de rastreabilidade (TRACE.md)
"""
import argparse
import datetime as dt
import difflib
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml

import speckit_adapter as sk

TOOL_ROOT = Path(__file__).resolve().parent
# EVOSPEC_ROOT permite aplicar o EvoSpec-UX a outro repositório que use o Spec Kit
ROOT = Path(os.environ.get("EVOSPEC_ROOT", TOOL_ROOT)).resolve()
SPECS, EVID, CHANGES, RESULTS = (ROOT / d for d in ("specs", "evidence", "changes", "results"))
APP = ROOT / "app"
TESTS = ROOT / "tests" / "acceptance.py"
AXE = TOOL_ROOT / "vendor" / "axe.min.js"   # axe-core (MPL-2.0), ver vendor/axe-core-LICENSE.txt
CHROME = os.environ.get("EVOSPEC_CHROME")  # opcional; sem ele usa o Chromium do Playwright


class EvoSpecError(Exception):
    """Erro de uso do método (proposta inexistente, decisão inválida etc.)."""


DECISIONS = {"pending", "approved", "rejected", "clarification", "deferred"}


# ---------------------------------------------------------------- utilidades
def load_specs():
    """Especificações do Spec Kit (specs/<feature>/spec.md) lidas pelo adaptador."""
    return sk.load_specs(SPECS)


def load_dir(d):
    return {y["id"]: (p, y) for p in sorted(d.glob("*.yaml")) for y in [yaml.safe_load(p.read_text())]}


def _clean(x):
    if isinstance(x, str):
        return " ".join(x.split())
    if isinstance(x, list):
        return [_clean(i) for i in x]
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    return x


def dump(path, data):
    path.write_text(yaml.safe_dump(_clean(data), allow_unicode=True, sort_keys=False, width=1000))


def load_tests():
    if not TESTS.exists():
        class _SemTestes:
            CRITERIA = {}
        return _SemTestes
    spec = importlib.util.spec_from_file_location("acceptance", TESTS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def code_annotations():
    """Lê anotações @spec <feature>@<versão> no código da aplicação."""
    found = {}
    for f in APP.rglob("*"):
        if f.suffix in {".html", ".js", ".ts", ".jsx", ".tsx"}:
            for m in re.finditer(r"@spec((?:\s+\d{3}-[\w-]+@\d+)+)", f.read_text()):
                for ref in m.group(1).split():
                    sid, ver = ref.split("@")
                    found.setdefault(sid, set()).add((int(ver), f.relative_to(ROOT).as_posix()))
    return found


def git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- validate
def validate(quiet=False):
    specs, evid, crs = load_specs(), load_dir(EVID), load_dir(CHANGES)
    tests = load_tests().CRITERIA
    errors, warns = [], []
    all_ac = {c["id"]: sid for sid, (_, s) in specs.items() for c in s["criteria"]}

    for cid, (_, cr) in crs.items():
        dec = cr.get("decision", {}).get("status", "pending")
        # R1 — referências existentes
        for e in cr.get("evidence", []):
            if e not in evid:
                errors.append(f"[R1] {cid}: evidência {e} não existe")
        for s in cr.get("affected_specs", []):
            if s not in specs:
                errors.append(f"[R1] {cid}: especificação {s} não existe")
        for ac in cr.get("preserve", []):
            if ac not in all_ac:
                errors.append(f"[R1] {cid}: critério a preservar {ac} não existe")
        # R2 — admissibilidade: sem observação não há mudança
        if not cr.get("observed") or not all(evid.get(e, (0, {}))[1].get("observed") for e in cr.get("evidence", [])):
            errors.append(f"[R2] {cid}: inadmissível — falta descrição observável na proposta ou na evidência")
        if cr.get("inferred") and not cr.get("justification"):
            errors.append(f"[R2] {cid}: inferências sem justificativa")
        if not cr.get("spec_changes"):
            warns.append(f"[R2] {cid}: proposta sem alteração de especificação")
        for ch in cr.get("spec_changes", []):
            for c in ch.get("add_criteria", []) + ch.get("modify_criteria", []):
                if not c.get("text"):
                    errors.append(f"[R2] {cid}: critério {c.get('id')} sem texto verificável")
        # R3 — decisão humana registrada
        if dec not in DECISIONS:
            errors.append(f"[R3] {cid}: decisão inválida '{dec}'")
        if dec != "pending" and not cr["decision"].get("by"):
            errors.append(f"[R3] {cid}: decisão '{dec}' sem responsável humano")

    # R3 — nenhuma versão de spec sem proposta aprovada
    for sid, (_, s) in specs.items():
        if s["version"] is None:
            errors.append(f"[R3] {sid}: spec.md sem a linha **Version** exigida pela constituição")
        for h in s.get("history", [])[1:]:
            cr = crs.get(h.get("cr"), (None, {}))[1]
            if cr.get("decision", {}).get("status") != "approved":
                errors.append(f"[R3] {sid} v{h['version']}: alteração sem proposta aprovada ({h.get('cr')})")

    # R7 — plano e tarefas do Spec Kit gerados a partir da versão vigente da especificação
    for sid, (path, s) in specs.items():
        for art, cmd in (("plan.md", "/speckit-plan"), ("tasks.md", "/speckit-tasks")):
            v = sk.artifact_spec_version(path.parent / art)
            if v is None:
                errors.append(f"[R7] {sid}: {art} ausente ou sem **Spec Version** — rode {cmd}")
            elif v != s["version"]:
                errors.append(f"[R7] {sid}: {art} gerado da versão {v}, mas a especificação está na versão "
                              f"{s['version']} — rode {cmd}")

    # R4/R5 — cobertura de critérios por testes
    for ac, sid in all_ac.items():
        if ac not in tests:
            errors.append(f"[R4] {ac} ({sid}): critério sem teste de aceitação")
    for ac in tests:
        if ac not in all_ac:
            errors.append(f"[R5] teste órfão para critério inexistente {ac}")

    # R6 — drift especificação × código
    ann = code_annotations()
    for sid, (_, s) in specs.items():
        if s.get("status") != "active":
            continue
        refs = ann.get(sid)
        if not refs:
            errors.append(f"[R6] drift: {sid} não é referenciada por nenhum arquivo do código")
            continue
        for ver, f in refs:
            if ver != s["version"]:
                errors.append(f"[R6] drift: {f} implementa {sid}@{ver}, mas a versão aprovada é {s['version']}")

    if not quiet:
        print("== Validação de governança ==")
        for e in errors:
            print("  ERRO ", e)
        for w in warns:
            print("  AVISO", w)
        print(f"  {len(errors)} erro(s), {len(warns)} aviso(s)")
    return errors, warns


# ---------------------------------------------------------------- propose (LLM)
PROMPT = """Você apoia a evolução de especificações em um fluxo Spec-Driven Development.
Transforme a EVIDÊNCIA abaixo em UMA proposta de mudança no formato YAML indicado.
Regras:
- Separe o que foi OBSERVADO (apenas o que está na evidência) do que é INFERIDO.
- Não invente requisitos sem relação com a evidência. Se a evidência for insuficiente,
  use change_type: needs_clarification e deixe spec_changes vazio.
- Cada novo critério deve ser verificável por um teste automatizado ou roteiro.
- Liste em preserve os critérios existentes que não podem regredir.
- decision.status deve ser "pending".

EVIDÊNCIA:
{evidence}

ESPECIFICAÇÕES ATUAIS:
{specs}

FORMATO:
id: {cr_id}
evidence: [{evd_id}]
drafted_by: llm
affected_specs: [...]
change_type: lacuna_da_especificacao | falha_de_implementacao | novo_requisito | needs_clarification
observed: ...
inferred: ...
justification: ...
wcag: [...]
spec_changes:
  - spec: NNN-nome-da-feature
    summary: resumo da mudança em uma linha
    add_criteria: [{{id: NNN/FR-MMM, text: "O sistema MUST ..."}}]
    modify_criteria: []
preserve: [...]
decision: {{status: pending}}

Responda apenas com o YAML."""


def propose(evd_id, model):
    evid = load_dir(EVID)
    if evd_id not in evid:
        raise EvoSpecError(f"evidência {evd_id} não encontrada")
    n = len(list(CHANGES.glob("CR-*.yaml"))) + 1
    cr_id = f"CR-{n:03d}"
    prompt = PROMPT.format(
        evidence=evid[evd_id][0].read_text(),
        specs="\n---\n".join(p.read_text() for p, _ in load_specs().values()),
        cr_id=cr_id, evd_id=evd_id)
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        out = CHANGES / "prompts" / f"{cr_id}-{evd_id}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prompt)
        return {"cr": None, "prompt_file": out.relative_to(ROOT).as_posix(), "prompt": prompt}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({"model": model, "max_tokens": 2000,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    text = json.load(urllib.request.urlopen(req))["content"][0]["text"]
    text = re.sub(r"^```(yaml)?|```$", "", text.strip(), flags=re.M).strip()
    data = yaml.safe_load(text)
    data["decision"] = {"status": "pending"}
    data["drafted_by"] = f"llm:{model}"
    data["id"] = cr_id
    dump(CHANGES / f"{cr_id}.yaml", data)
    return {"cr": cr_id, "prompt_file": None, "prompt": prompt}


# ---------------------------------------------------------------- decide
def decide(cr_id, by, decision, note):
    crs, specs = load_dir(CHANGES), load_specs()
    if cr_id not in crs:
        raise EvoSpecError(f"proposta {cr_id} não encontrada")
    path, cr = crs[cr_id]
    if decision not in DECISIONS - {"pending"}:
        raise EvoSpecError(f"decisão inválida: {decision}")
    if not by.strip():
        raise EvoSpecError("informe o nome do responsável pela decisão")
    if cr.get("decision", {}).get("status") == "approved":
        raise EvoSpecError(f"{cr_id} já foi aprovada")
    cr["decision"] = {"status": decision, "by": by, "at": now(), "note": note}
    if decision == "approved":
        diffs = []
        for ch in cr.get("spec_changes", []):
            if ch["spec"] not in specs:
                raise EvoSpecError(f"especificação {ch['spec']} não existe")
            spath, _ = specs[ch["spec"]]
            before = spath.read_text()
            try:
                sk.apply_change(spath, ch, cr_id, cr.get("evidence", []), by,
                                ch.get("summary") or cr.get("change_type", "mudança"))
            except ValueError as exc:
                raise EvoSpecError(str(exc))
            rel = spath.relative_to(ROOT).as_posix()
            diffs += difflib.unified_diff(before.splitlines(True), spath.read_text().splitlines(True),
                                          f"a/{rel}", f"b/{rel}")
        (CHANGES / "diffs").mkdir(exist_ok=True)
        (CHANGES / "diffs" / f"{cr_id}.diff").write_text("".join(diffs))
    dump(path, cr)
    return "".join(diffs) if decision == "approved" else ""


# ---------------------------------------------------------------- verify
def verify(label, set_baseline):
    from playwright.sync_api import sync_playwright

    tests = load_tests().CRITERIA
    specs = load_specs()
    url = (APP / "index.html").as_uri()
    results = {}
    with sync_playwright() as p:
        kwargs = {"executable_path": CHROME} if CHROME and Path(CHROME).exists() else {}
        browser = p.chromium.launch(args=["--no-sandbox"], **kwargs)
        for ac, fns in sorted(tests.items()):
            for fn in fns:
                page = browser.new_page()
                page.goto(url)
                try:
                    fn(page)
                    results[ac] = {"test": fn.__name__, "passed": True}
                except Exception as exc:  # falha ou erro do teste
                    results[ac] = {"test": fn.__name__, "passed": False, "detail": str(exc).splitlines()[0]}
                page.close()
        # varredura automática de acessibilidade no estado de erro
        page = browser.new_page()
        page.goto(url)
        page.fill("#cpf", "000")
        page.get_by_role("button", name="Continuar").click()
        page.add_script_tag(path=str(AXE))
        axe = page.evaluate("async () => (await axe.run(document, {runOnly: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']})).violations"
                            ".map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.length}))")
        browser.close()

    run = {"label": label, "at": now(), "commit": git_head(),
           "spec_versions": {sid: s["version"] for sid, (_, s) in specs.items()},
           "criteria": results, "axe_violations": axe}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"run-{label}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2))

    base_path = RESULTS / "baseline.json"
    base = json.loads(base_path.read_text()) if base_path.exists() else None
    regressions = [ac for ac, r in results.items()
                   if base and base["criteria"].get(ac, {}).get("passed") and not r["passed"]]

    baseline_set = False
    if set_baseline and not regressions:
        base_path.write_text(json.dumps(run, ensure_ascii=False, indent=2))
        baseline_set = True
    return run, regressions, baseline_set


def print_run(run, regressions, set_baseline, baseline_set):
    print(f"== Verificação independente: {run['label']} (commit {run['commit']}) ==")
    for ac, r in sorted(run["criteria"].items()):
        mark = "PASSA" if r["passed"] else "FALHA"
        flag = "  <-- REGRESSÃO" if ac in regressions else ""
        print(f"  {mark}  {ac:8} {r['test']}{flag}" + ("" if r["passed"] else f"\n           {r.get('detail', '')}"))
    axe = run["axe_violations"]
    print(f"  axe-core: {len(axe)} violação(ões) WCAG automática(s)" +
          "".join(f"\n           {v['id']} ({v['impact']}, {v['nodes']} nó(s))" for v in axe))
    print(f"  Regressões em relação à linha de base: {len(regressions)}")
    if set_baseline:
        print("  Linha de base atualizada." if baseline_set else "  Linha de base NÃO atualizada: há regressões.")


# ---------------------------------------------------------------- trace
def trace_rows():
    """Linhas da matriz: critério → spec@versão → evidência → proposta → teste → resultado."""
    specs, crs = load_specs(), load_dir(CHANGES)
    tests = load_tests().CRITERIA
    base = load_baseline()
    origin = {}
    for cid, (_, cr) in crs.items():
        for ch in cr.get("spec_changes", []):
            for c in ch.get("add_criteria", []) + ch.get("modify_criteria", []):
                origin[c["id"]] = (cid, cr)
    rows = []
    for sid, (_, s) in specs.items():
        for c in s["criteria"]:
            cid, cr = origin.get(c["id"], (None, {}))
            r = base["criteria"].get(c["id"]) if base else None
            rows.append({
                "criterion": c["id"], "text": c["text"], "spec": sid, "version": s["version"],
                "evidence": cr.get("evidence", []) if cr else [], "cr": cid,
                "decision": cr.get("decision", {}) if cr else {},
                "tests": [f.__name__ for f in tests.get(c["id"], [])],
                "result": None if r is None else r["passed"]})
    return rows


def load_baseline():
    p = RESULTS / "baseline.json"
    return json.loads(p.read_text()) if p.exists() else None


def trace():
    specs, evid, crs = load_specs(), load_dir(EVID), load_dir(CHANGES)
    tests = load_tests().CRITERIA
    base_path = RESULTS / "baseline.json"
    base = json.loads(base_path.read_text()) if base_path.exists() else {"criteria": {}, "commit": None}
    origin = {}
    for cid, (_, cr) in crs.items():
        for ch in cr.get("spec_changes", []):
            for c in ch.get("add_criteria", []) + ch.get("modify_criteria", []):
                origin[c["id"]] = (cid, cr)
    lines = ["# Matriz de rastreabilidade — EvoSpec-UX", "",
             f"Gerada em {now()} · linha de base: commit `{base.get('commit')}`", "",
             "| Critério | Spec@versão | Evidência | Proposta (decisão) | Teste | Resultado |",
             "|---|---|---|---|---|---|"]
    for sid, (_, s) in specs.items():
        for c in s["criteria"]:
            cid, cr = origin.get(c["id"], (None, {}))
            ev = ", ".join(cr.get("evidence", [])) if cr else "— (versão inicial)"
            dec = f"{cid} ({cr['decision']['status']}, {cr['decision'].get('by', '')})" if cr else "—"
            t = ", ".join(f.__name__ for f in tests.get(c["id"], [])) or "**sem teste**"
            r = base["criteria"].get(c["id"])
            res = "—" if r is None else ("passa" if r["passed"] else "**falha**")
            lines.append(f"| {c['id']} | {sid}@{s['version']} | {ev} | {dec} | `{t}` | {res} |")
    lines += ["", "## Evidências", ""]
    for eid, (_, e) in evid.items():
        used = [cid for cid, (_, cr) in crs.items() if eid in cr.get("evidence", [])]
        lines.append(f"- **{eid}** ({e.get('source')}, {e.get('assistive_technology', '')}): "
                     f"{' '.join(e['observed'].split())} → {', '.join(used) or 'sem proposta'}")
    (ROOT / "TRACE.md").write_text("\n".join(lines) + "\n")
    print("TRACE.md gerado")


# ---------------------------------------------------------------- status
def status():
    print("Especificações:")
    for sid, (_, s) in load_specs().items():
        print(f"  {sid}@{s['version']}  {s['title']}  ({len(s['criteria'])} critérios)")
    print("Evidências:")
    for eid, (_, e) in load_dir(EVID).items():
        print(f"  {eid}  {e.get('task')}  [severidade: {e.get('severity')}]")
    print("Propostas de mudança:")
    for cid, (_, c) in load_dir(CHANGES).items():
        d = c.get("decision", {})
        print(f"  {cid}  {c.get('change_type')}  -> {d.get('status')} {('por ' + d['by']) if d.get('by') else ''}")


def main():
    ap = argparse.ArgumentParser(description="EvoSpec-UX")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("validate")
    sub.add_parser("trace")
    p = sub.add_parser("propose"); p.add_argument("evidence"); p.add_argument("--model", default="claude-sonnet-5-5")
    p = sub.add_parser("decide"); p.add_argument("cr"); p.add_argument("--by", required=True)
    p.add_argument("--decision", required=True); p.add_argument("--note", default="")
    p = sub.add_parser("verify"); p.add_argument("--label", default="atual"); p.add_argument("--set-baseline", action="store_true")
    a = ap.parse_args()
    try:
        run_cli(a)
    except EvoSpecError as exc:
        sys.exit(f"erro: {exc}")


def run_cli(a):
    if a.cmd == "status":
        status()
    elif a.cmd == "validate":
        errors, _ = validate()
        sys.exit(1 if errors else 0)
    elif a.cmd == "propose":
        out = propose(a.evidence, a.model)
        if out["cr"]:
            print(f"Rascunho salvo em changes/{out['cr']}.yaml (status: pending)")
        else:
            print(f"ANTHROPIC_API_KEY não definida. Prompt salvo em {out['prompt_file']};\n"
                  f"cole a resposta do modelo em um novo arquivo changes/CR-xxx.yaml.")
    elif a.cmd == "decide":
        diff = decide(a.cr, a.by, a.decision, a.note)
        print(diff + f"{a.cr}: decisão '{a.decision}' registrada por {a.by}")
    elif a.cmd == "verify":
        run, regs, ok = verify(a.label, a.set_baseline)
        print_run(run, regs, a.set_baseline, ok)
        if a.set_baseline and not ok:
            sys.exit(1)
    elif a.cmd == "trace":
        trace()


if __name__ == "__main__":
    main()
