# Tasks: Preservação dos dados preenchidos

**Spec Version**: 1

**Input**: Design documents from `/specs/002-preservacao-dados/`

**Prerequisites**: plan.md, spec.md

**Tests**: obrigatórios (princípio IV da constituição).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: User Story 1 - Corrigir um erro sem redigitar o formulário (Priority: P1) 🎯 MVP

**Goal**: manter nome, CPF e e-mail após um erro de validação.

**Independent Test**: CPF inválido + "Continuar" → os três campos mantêm os valores.

### Tests for User Story 1

- [x] T001 [US1] Teste `dados_preservados_apos_erro` para 002/FR-001 em `tests/acceptance.py`

### Implementation for User Story 1

- [x] T002 [US1] Garantir que o tratador de erro em `app/index.html` não chame `form.reset()` nem recrie o formulário
- [x] T003 [US1] Anotar `app/index.html` com `@spec 002-preservacao-dados@1`

## Phase 2: Polish

- [x] T004 Incluir 002/FR-001 em `preserve` de toda proposta que altere o fluxo de erro da feature 001

## Dependencies & Execution Order

- Depende da página criada em `001-validacao-cpf` (T001 daquela feature).

## Implementation Strategy

- Nota de migração: tarefas concluídas nas rodadas 0 e 1 do protótipo; a regressão de 002/FR-001
  detectada na rodada 1 (commit 5890e4e, revertido) motivou a tarefa T004.
