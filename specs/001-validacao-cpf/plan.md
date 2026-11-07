# Implementation Plan: Validação do CPF na matrícula acadêmica

**Branch**: `001-validacao-cpf` | **Date**: 2026-11-07 | **Spec**: [spec.md](./spec.md)

**Spec Version**: 2

**Input**: Feature specification from `/specs/001-validacao-cpf/spec.md`

## Summary

O formulário de matrícula valida o CPF pelos dígitos verificadores ao acionar "Continuar": com CPF
inválido, bloqueia o envio e mostra uma mensagem (FR-001, FR-002); com CPF válido, envia e confirma
(FR-003). A versão 2 da especificação (CR-001, evidência EVD-17) exige que o erro seja perceptível
por tecnologias assistivas: foco no campo (FR-004), campo marcado como inválido com a mensagem como
descrição acessível (FR-005) e anúncio automático em região viva (FR-006). Abordagem: página HTML
única com JavaScript sem framework, usando atributos ARIA nativos (ver [research.md](./research.md)).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript (ES2020) na aplicação; Python 3.12 nas ferramentas

**Primary Dependencies**: nenhuma na aplicação; Playwright e axe-core (vendorizado) na verificação

**Storage**: N/A (envio simulado na própria página)

**Testing**: testes de aceitação em `tests/acceptance.py` (Playwright + Chromium), um por
requisito, executados por `python evospec.py verify`; varredura axe-core WCAG 2.2 AA

**Target Platform**: navegadores modernos com leitores de tela (NVDA + Chrome como referência)

**Project Type**: web (página estática servida por `web.py` em `/app/`)

**Performance Goals**: validação instantânea (< 100 ms após o acionamento de "Continuar")

**Constraints**: WCAG 2.2 AA; textos em português do Brasil; sem dependências na aplicação

**Scale/Scope**: um formulário, três campos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Situação |
|-----------|-------------|----------|
| I. Acessibilidade verificável | FR-004 a FR-006 derivam de evidência observada (EVD-17); axe-core é piso, não prova | ✅ |
| II. Especificação como fonte da verdade | `app/index.html` anotado com `@spec 001-validacao-cpf@2`; plano registra **Spec Version** 2 | ✅ |
| III. Evolução orientada por evidências | Versão 2 vem da CR-001, aprovada por Lucas Matheus Silva; observado × inferido separados | ✅ |
| IV. Verificação independente | Testes de FR-004 a FR-006 escritos a partir da spec antes da implementação; FR-001 a FR-003 e 002/FR-001 marcados como "a preservar" | ✅ |
| V. Simplicidade | HTML/CSS/JS sem framework | ✅ |

Reavaliação pós-design: sem violações. Complexity Tracking não se aplica.

## Project Structure

### Documentation (this feature)

```text
specs/001-validacao-cpf/
├── plan.md              # Este arquivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── form-ui.md       # Contrato da interface usado pelos testes
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
app/
└── index.html           # formulário de matrícula (features 001 e 002)

tests/
├── acceptance.py        # testes de aceitação por requisito (@criterion("001/FR-00N"))
└── test_governance.py   # autotestes das regras do EvoSpec-UX
```

**Structure Decision**: página única em `app/index.html`, compartilhada com a feature
`002-preservacao-dados`; os testes ficam em `tests/acceptance.py` e referenciam os requisitos pelo
identificador global `<feature>/FR-NNN`.
