# Implementation Plan: Preservação dos dados preenchidos

**Branch**: `002-preservacao-dados` | **Date**: 2026-11-07 | **Spec**: [spec.md](./spec.md)

**Spec Version**: 1

**Input**: Feature specification from `/specs/002-preservacao-dados/spec.md`

## Summary

Após um erro de validação do CPF, os valores de nome, CPF e e-mail permanecem nos campos (FR-001).
Abordagem: o tratador de erro nunca reinicia nem recria o formulário; apenas atualiza a mensagem e os
atributos de estado. Esta feature é "a preservar" em toda mudança da `001-validacao-cpf`.

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript (ES2020); Python 3.12 nas ferramentas

**Primary Dependencies**: nenhuma na aplicação

**Storage**: N/A (estado mantido nos próprios campos durante a visita)

**Testing**: `dados_preservados_apos_erro` em `tests/acceptance.py` (Playwright + Chromium)

**Target Platform**: navegadores modernos

**Project Type**: web (mesma página da feature 001)

**Performance Goals**: N/A

**Constraints**: proibido `form.reset()` ou re-renderização do formulário no fluxo de erro

**Scale/Scope**: três campos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Situação |
|-----------|-------------|----------|
| I. Acessibilidade verificável | Evita redigitação, que pesa mais para usuários de tecnologia assistiva | ✅ |
| II. Especificação como fonte da verdade | `app/index.html` anotado com `@spec 002-preservacao-dados@1` | ✅ |
| III. Evolução orientada por evidências | Versão inicial; sem mudanças | ✅ |
| IV. Verificação independente | FR-001 testado e listado como "a preservar" na CR-001 | ✅ |
| V. Simplicidade | Sem dependências | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/002-preservacao-dados/
├── plan.md
├── checklists/requirements.md
└── tasks.md
```

Sem `research.md`, `data-model.md` e `contracts/` próprios: a entidade e o contrato da interface são
os da feature 001 ([data-model](../001-validacao-cpf/data-model.md),
[contrato](../001-validacao-cpf/contracts/form-ui.md)).

### Source Code (repository root)

```text
app/index.html          # compartilhado com 001-validacao-cpf
tests/acceptance.py     # @criterion("002/FR-001")
```

**Structure Decision**: mesma página da feature 001.
