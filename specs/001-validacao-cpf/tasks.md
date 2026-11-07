# Tasks: Validação do CPF na matrícula acadêmica

**Spec Version**: 2

**Input**: Design documents from `/specs/001-validacao-cpf/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/form-ui.md, quickstart.md

**Tests**: obrigatórios pelo princípio IV da constituição. Os testes de cada requisito são escritos
pelo verificador a partir da especificação aprovada, **antes** da implementação, e devem falhar
primeiro.

**Organization**: tarefas agrupadas por história de usuário.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: história de usuário (US1, US2, US3)

## Phase 1: Setup

- [x] T001 Criar a página `app/index.html` com o formulário (nome, CPF, e-mail, botão "Continuar") e a anotação `@spec`, conforme [contracts/form-ui.md](./contracts/form-ui.md)

## Phase 2: Foundational

- [x] T002 Implementar `cpfValido()` em `app/index.html` (dígitos verificadores, sequências repetidas, 11 dígitos) — [research.md](./research.md) R1

---

## Phase 3: User Story 1 - Impedir inscrição com CPF inválido (Priority: P1) 🎯 MVP

**Goal**: bloquear o envio com CPF inválido e mostrar a mensagem.

**Independent Test**: CPF inválido + "Continuar" → sem confirmação e com mensagem.

### Tests for User Story 1

- [x] T003 [P] [US1] Teste `cpf_invalido_bloqueia_envio` para 001/FR-001 em `tests/acceptance.py`
- [x] T004 [P] [US1] Teste `cpf_invalido_exibe_mensagem` para 001/FR-002 em `tests/acceptance.py`

### Implementation for User Story 1

- [x] T005 [US1] Bloquear o envio e exibir "CPF inválido" no tratador de `submit` em `app/index.html`

---

## Phase 4: User Story 2 - Enviar inscrição com CPF válido (Priority: P2)

**Goal**: enviar e confirmar quando o CPF é válido.

**Independent Test**: CPF válido + "Continuar" → confirmação visível.

### Tests for User Story 2

- [x] T006 [P] [US2] Teste `cpf_valido_envia` para 001/FR-003 em `tests/acceptance.py`

### Implementation for User Story 2

- [x] T007 [US2] Ocultar o formulário e exibir `#confirmacao` no envio válido em `app/index.html`

---

## Phase 5: User Story 3 - Perceber o erro com tecnologia assistiva (Priority: P1) — CR-001 / EVD-17

**Goal**: tornar o erro perceptível por leitores de tela (spec versão 2).

**Independent Test**: com CPF inválido, foco no campo CPF, campo inválido com descrição acessível e
mensagem anunciada em região viva.

**A preservar** (CR-001): 001/FR-001, 001/FR-002, 001/FR-003, 002/FR-001.

### Tests for User Story 3 (escritos antes da implementação; devem falhar na versão 1)

- [x] T008 [P] [US3] Teste `foco_vai_para_cpf` para 001/FR-004 em `tests/acceptance.py`
- [x] T009 [P] [US3] Teste `cpf_marcado_invalido_com_descricao` para 001/FR-005 em `tests/acceptance.py`
- [x] T010 [P] [US3] Teste `mensagem_em_regiao_viva` para 001/FR-006 em `tests/acceptance.py`

### Implementation for User Story 3

- [x] T011 [US3] Tornar `#cpf-erro` uma região viva (`role="alert"`) presente desde o carregamento e associá-la ao campo com `aria-describedby` em `app/index.html` — research R2
- [x] T012 [US3] No erro, definir `aria-invalid="true"`, inserir a mensagem e mover o foco para `#cpf`, sem limpar os campos, em `app/index.html`
- [x] T013 [US3] Atualizar a anotação para `@spec 001-validacao-cpf@2` em `app/index.html`

---

## Phase 6: Polish & Cross-Cutting

- [x] T014 Rodar `python evospec.py validate` e `python evospec.py verify --set-baseline` (sem regressões)
- [ ] T015 Verificação manual com NVDA conforme [quickstart.md](./quickstart.md) (SC-003) — pendente de sessão com usuário

## Dependencies & Execution Order

- Setup (T001) → Foundational (T002) → US1 → US2; US3 depende de US1 (mesmo tratador de erro).
- Em cada história, os testes vêm antes da implementação.
- 002/FR-001 (preservação dos dados) deve continuar passando após US3.

## Parallel Opportunities

- T003/T004, T008/T009/T010: testes independentes no mesmo arquivo, escritos pelo verificador.

## Implementation Strategy

- MVP: US1. Depois US2. US3 entrou pela evolução orientada por evidências (CR-001).
- Nota de migração: as tarefas T001–T014 foram concluídas nas rodadas 0 e 1 do protótipo (commits
  b267447 e 31cdfc7), antes da adoção do Spec Kit; esta lista registra esse trabalho no formato
  oficial.
