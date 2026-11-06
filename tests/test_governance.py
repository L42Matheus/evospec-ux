"""Autotestes das regras de governança do EvoSpec-UX.

Cada caso copia o projeto para um diretório temporário, introduz uma violação
e confere se `evospec.py validate` a detecta. Uso: python3 tests/test_governance.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def run_case(name, mutate, expected_rule):
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "p"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("node_modules", ".git", "results"))
        mutate(dst)
        out = subprocess.run([sys.executable, "evospec.py", "validate"], cwd=dst, capture_output=True, text=True).stdout
        ok = expected_rule in out
        print(f"  {'OK   ' if ok else 'FALHOU'} {name} (esperado {expected_rule})")
        if not ok:
            print(out)
        return ok


def edit_yaml(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def sem_observacao(d):
    edit_yaml(d / "changes/CR-001.yaml", lambda c: c.update(observed=""))


def spec_sem_aprovacao(d):
    def f(s):
        s["version"] += 1
        s["criteria"].append({"id": "AC-06.2", "text": "Novo critério sem proposta."})
        s["history"].append({"version": s["version"], "cr": "CR-999"})
    edit_yaml(d / "specs/SPEC-06.yaml", f)


def decisao_sem_responsavel(d):
    edit_yaml(d / "changes/CR-001.yaml", lambda c: c["decision"].pop("by"))


def drift_codigo(d):
    p = d / "app/index.html"
    p.write_text(p.read_text().replace("SPEC-04@2", "SPEC-04@1"))


def teste_orfao(d):
    p = d / "tests/acceptance.py"
    p.write_text(p.read_text() + '\n\n@criterion("AC-99.9")\ndef inexistente(page):\n    pass\n')


def evidencia_inexistente(d):
    edit_yaml(d / "changes/CR-001.yaml", lambda c: c.update(evidence=["EVD-99"]))


if __name__ == "__main__":
    print("== Autotestes de governança ==")
    casos = [
        ("proposta sem descrição observável é inadmissível", sem_observacao, "[R2]"),
        ("especificação alterada sem proposta aprovada", spec_sem_aprovacao, "[R3]"),
        ("decisão sem responsável humano", decisao_sem_responsavel, "[R3]"),
        ("código implementa versão antiga da especificação", drift_codigo, "[R6]"),
        ("teste para critério inexistente", teste_orfao, "[R5]"),
        ("proposta referencia evidência inexistente", evidencia_inexistente, "[R1]"),
    ]
    results = [run_case(*c) for c in casos]
    print(f"  {sum(results)}/{len(results)} casos detectados")
    sys.exit(0 if all(results) else 1)
