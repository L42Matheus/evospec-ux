"""Adaptador entre o EvoSpec-UX e os artefatos do GitHub Spec Kit.

Lê e altera `specs/<feature>/spec.md` sem sair do modelo oficial do Spec Kit. O EvoSpec-UX acrescenta
apenas dois elementos ao modelo, exigidos pelo princípio III da constituição:

  **Version**: N                          (no cabeçalho, logo após **Status**)
  ## Histórico de versões (EvoSpec)       (tabela ao final do arquivo)

Os requisitos são as linhas `- **FR-NNN**: ...` da seção "Functional Requirements". O identificador
global de um requisito é `<número da feature>/FR-NNN`, por exemplo `001/FR-004`.

Plano e tarefas (`plan.md`, `tasks.md`) registram a versão da especificação de origem na linha
`**Spec Version**: N`, permitindo detectar plano ou tarefas desatualizados (regra R7).
"""
import re
from pathlib import Path

FR_LINE = re.compile(r"^- \*\*(FR-\d{3})\*\*:\s*(.*)$")
HISTORY_HEADING = "## Histórico de versões (EvoSpec)"
FR_HEADING = "### Functional Requirements"


def feature_number(feature_id):
    return feature_id.split("-", 1)[0]


def global_id(feature_id, fr):
    return f"{feature_number(feature_id)}/{fr}"


def _requirements(lines):
    """Extrai requisitos FR-NNN, juntando linhas de continuação indentadas."""
    reqs, cur, inside = [], None, False
    for line in lines:
        if line.startswith(FR_HEADING):
            inside = True
            continue
        if inside and line.startswith("#"):
            break
        if not inside:
            continue
        m = FR_LINE.match(line)
        if m:
            cur = {"local": m.group(1), "text": m.group(2).strip()}
            reqs.append(cur)
        elif cur and line.startswith("  ") and line.strip():
            cur["text"] += " " + line.strip()
        else:
            cur = None
    return reqs


def _history(lines):
    rows, inside = [], False
    for line in lines:
        if line.startswith(HISTORY_HEADING):
            inside = True
            continue
        if inside and line.startswith("#"):
            break
        if inside and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5 and cells[0].isdigit():  # ignora cabeçalho e separador
                dash = lambda v: "" if v in {"—", "-"} else v
                rows.append({"version": int(cells[0]), "change": cells[1], "cr": dash(cells[2]),
                             "evidence": [e.strip() for e in dash(cells[3]).split(",") if e.strip()],
                             "approved_by": dash(cells[4])})
    return rows


def parse_spec(path):
    path = Path(path)
    text = path.read_text()
    lines = text.splitlines()
    fid = path.parent.name
    title = re.search(r"^# Feature Specification:\s*(.+)$", text, re.M)
    version = re.search(r"^\*\*Version\*\*:\s*(\d+)", text, re.M)
    status = re.search(r"^\*\*Status\*\*:\s*(.+)$", text, re.M)
    return {
        "id": fid,
        "title": title.group(1).strip() if title else fid,
        "version": int(version.group(1)) if version else None,
        "status": "active" if status and status.group(1).strip().lower() in {"approved", "active"} else
                  (status.group(1).strip().lower() if status else "draft"),
        "criteria": [{"id": global_id(fid, r["local"]), "local": r["local"], "text": r["text"]}
                     for r in _requirements(lines)],
        "history": _history(lines),
    }


def load_specs(specs_dir):
    return {p.parent.name: (p, parse_spec(p)) for p in sorted(Path(specs_dir).glob("*/spec.md"))}


def _wrap(prefix, text, width=100):
    words, out, line = text.split(), [], prefix
    for w in words:
        if len(line) + len(w) + 1 > width and line.strip() != prefix.strip():
            out.append(line.rstrip())
            line = "  " + w
        else:
            line = (line + " " + w) if line.strip() else line + w
    out.append(line.rstrip())
    return out


def apply_change(path, change, cr_id, evidence, approved_by, summary):
    """Aplica uma mudança aprovada ao spec.md: requisitos, seções, versão e histórico."""
    path = Path(path)
    lines = path.read_text().splitlines()
    spec = parse_spec(path)
    existing = {r["local"] for r in _requirements(lines)}

    # 1) modificar requisitos existentes
    for c in change.get("modify_criteria", []):
        local = c["id"].split("/")[-1]
        start = next(i for i, l in enumerate(lines) if l.startswith(f"- **{local}**:"))
        end = start + 1
        while end < len(lines) and lines[end].startswith("  ") and lines[end].strip():
            end += 1
        lines[start:end] = _wrap(f"- **{local}**:", c["text"])

    # 2) acrescentar novos requisitos após o último FR
    new = []
    for c in change.get("add_criteria", []):
        local = c["id"].split("/")[-1]
        if local in existing:
            raise ValueError(f"{c['id']} já existe em {spec['id']}")
        new += _wrap(f"- **{local}**:", c["text"])
    if new:
        fr_start = lines.index(FR_HEADING)
        last = fr_start
        for i in range(fr_start + 1, len(lines)):
            if lines[i].startswith("#"):
                break
            if FR_LINE.match(lines[i]) or (lines[i].startswith("  ") and lines[i].strip()):
                last = i
        lines[last + 1:last + 1] = new

    # 3) inserir seções em markdown (por exemplo, uma nova história de usuário)
    for block in change.get("insert_markdown", []):
        idx = lines.index(block["before"])
        lines[idx:idx] = block["text"].rstrip("\n").splitlines() + ["", "---", ""] \
            if block.get("separator", True) else block["text"].rstrip("\n").splitlines() + [""]

    # 4) versão e histórico
    new_version = (spec["version"] or 1) + 1
    lines = [re.sub(r"^\*\*Version\*\*:\s*\d+", f"**Version**: {new_version}", l) for l in lines]
    hist = lines.index(HISTORY_HEADING)
    end = hist + 1
    while end < len(lines) and (lines[end].startswith("|") or not lines[end].strip()):
        end += 1
    while not lines[end - 1].startswith("|"):
        end -= 1
    lines.insert(end, f"| {new_version} | {summary} | {cr_id} | {', '.join(evidence)} | {approved_by} |")
    path.write_text("\n".join(lines) + "\n")
    return new_version


def artifact_spec_version(path):
    """Versão da especificação registrada em plan.md ou tasks.md (None se ausente)."""
    path = Path(path)
    if not path.exists():
        return None
    m = re.search(r"\*\*Spec Version\*\*:\s*(\d+)", path.read_text())
    return int(m.group(1)) if m else None
