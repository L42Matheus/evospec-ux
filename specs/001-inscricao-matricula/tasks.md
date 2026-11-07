---

description: "Lista de tarefas da feature 001-inscricao-matricula"
---

# Tarefas: Formulário de Inscrição Escolar (Matrícula Acadêmica)

**Versão da especificação de origem**: `001-inscricao-matricula@1.0.0`

**Input**: Documentos de desenho em `/specs/001-inscricao-matricula/` (plan.md, spec.md,
research.md, data-model.md, contracts/ui-contract.md, quickstart.md)

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: OBRIGATÓRIOS — o Princípio IV da constituição exige ao menos um teste de aceitação por
FR, escrito a partir da especificação e antes da implementação. Os testes devem FALHAR antes da
implementação.

**Organization**: tarefas agrupadas por história de usuário. Como a aplicação é um arquivo único
(`app/index.html`), as tarefas de implementação nesse arquivo são sequenciais (sem [P]).

## Format: `[ID] [P?] [Story] Descrição`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: história de usuário (US1, US2, US3)

## Path Conventions

- Aplicação: `app/index.html` (HTML + CSS + JS embutidos)
- Testes de aceitação: `tests/` (pytest + Playwright Python)

---

## Phase 1: Setup (Infraestrutura compartilhada)

**Purpose**: estrutura do projeto e infraestrutura de testes

- [ ] T001 Criar o esqueleto de `app/index.html` (`<!DOCTYPE html>`, `<html lang="pt-BR">`, `<meta charset="utf-8">`, `<meta name="viewport">`, `<title>Inscrição escolar</title>`, `<main>`, blocos `<style>` e `<script>` vazios) com o comentário `@spec 001-inscricao-matricula@1.0.0` no HTML, no CSS e no JS
- [ ] T002 [P] Criar `tests/conftest.py` com fixture `pagina` (Playwright síncrono, Chrome/Chromium headless, abre `file://<raiz>/app/index.html`) e cabeçalho `@spec 001-inscricao-matricula@1.0.0`
- [ ] T003 [P] Criar `pytest.ini` na raiz com `testpaths = tests`

---

## Phase 2: Foundational (Pré-requisitos bloqueantes)

**Purpose**: marcação do formulário conforme `contracts/ui-contract.md`, necessária a todas as histórias

- [ ] T004 Em `app/index.html`, criar `form#form-inscricao` com `novalidate`, `h1` "Inscrição escolar", campos `input#nome` (`type="text"`, `autocomplete="name"`, rótulo "Nome completo"), `input#cpf` (`type="text"`, `inputmode="numeric"`, rótulo "CPF", dica `#cpf-dica`), `input#email` (`type="email"`, `autocomplete="email"`, rótulo "E-mail"), parágrafos de erro vazios `#nome-erro`, `#cpf-erro`, `#email-erro` ligados por `aria-describedby`, região `#resumo-erros` (`role="alert"`), `button#continuar` (`type="submit"`, "Continuar") e seção `#confirmacao` (`role="status"`, `hidden`) com `#confirmacao-titulo` (`tabindex="-1"`), `#confirmacao-texto` e `button#nova-inscricao`
- [ ] T005 Em `app/index.html`, CSS base acessível: contraste de texto ≥ 4.5:1, foco visível (`:focus-visible` com contorno ≥ 2px e contraste ≥ 3:1), alvos ≥ 24×24 px, estado de erro indicado por texto + borda (não só cor), layout responsivo

**Checkpoint**: estrutura pronta — histórias podem começar

---

## Phase 3: User Story 1 - Enviar inscrição com dados válidos (Priority: P1) 🎯 MVP

**Goal**: com dados válidos, "Continuar" envia a inscrição e mostra a confirmação

**Independent Test**: preencher "Maria da Silva", "529.982.247-25", "maria@exemplo.com", acionar "Continuar" e ver a confirmação e 1 item em `window.inscricoesEnviadas`

### Testes da User Story 1 (escrever primeiro; devem FALHAR)

- [ ] T006 [P] [US1] Em `tests/test_inscricao.py`, `test_fr001_formulario_tem_campos_rotulados_e_botao_continuar` (rótulos associados a `#nome`, `#cpf`, `#email`; botão com texto "Continuar")
- [ ] T007 [P] [US1] Em `tests/test_inscricao.py`, `test_fr007_envia_com_dados_validos` (com e sem máscara no CPF; `window.inscricoesEnviadas` ganha exatamente 1 item com `cpf` = "52998224725", `situacao` = "enviada")
- [ ] T008 [P] [US1] Em `tests/test_inscricao.py`, `test_fr008_confirmacao_exibe_nome` (`#confirmacao` visível, título "Inscrição enviada com sucesso!", texto contém o nome; formulário oculto)
- [ ] T009 [P] [US1] Em `tests/test_inscricao.py`, `test_fr009_confirmacao_anunciada_e_focada` (`#confirmacao` com `role="status"`; foco em `#confirmacao-titulo`)
- [ ] T010 [P] [US1] Em `tests/test_inscricao.py`, `test_fr011_sem_envio_duplicado` (após envio, Enter/clique repetidos não aumentam `inscricoesEnviadas`; "Nova inscrição" reexibe formulário vazio)

### Implementação da User Story 1

- [ ] T011 [US1] Em `app/index.html`, implementar o envio simulado (research.md R2): ao submeter sem erros, criar `{nome, cpf (somente dígitos), email, enviadaEm (ISO 8601), situacao: "enviada"}`, adicionar a `window.inscricoesEnviadas` e disparar `inscricao:enviada` em `document`
- [ ] T012 [US1] Em `app/index.html`, exibir a confirmação: ocultar o formulário, mostrar `#confirmacao` com "Inscrição enviada com sucesso!" e o nome, mover o foco para `#confirmacao-titulo`
- [ ] T013 [US1] Em `app/index.html`, bloquear reenvio (sinalizador + formulário oculto) e implementar `#nova-inscricao` (limpa campos/mensagens, reexibe formulário, foco em `#nome`)

**Checkpoint**: US1 funcional e testável sozinha

---

## Phase 4: User Story 2 - Bloquear inscrição com CPF inválido (Priority: P1)

**Goal**: CPF com DV incorreto, dígitos repetidos ou tamanho ≠ 11 impede o envio e mostra erro

**Independent Test**: com nome/e-mail válidos e CPF "111.111.111-11" ou "529.982.247-24", nada é enviado e aparece "CPF inválido. Verifique os números digitados."

### Testes da User Story 2 (escrever primeiro; devem FALHAR)

- [ ] T014 [P] [US2] Em `tests/test_cpf.py`, `test_fr002_cpfs_validos_aceitos` e `test_fr002_digito_verificador_incorreto_rejeitado` e `test_fr002_tamanho_diferente_de_11_rejeitado` via `window.validarCPF` (com/sem máscara; letras ignoradas)
- [ ] T015 [P] [US2] Em `tests/test_cpf.py`, `test_fr003_todos_digitos_iguais_rejeitados` (000.000.000-00 a 999.999.999-99)
- [ ] T016 [P] [US2] Em `tests/test_inscricao.py`, `test_fr004_cpf_invalido_nao_envia_e_mostra_erro` (texto exato em `#cpf-erro`; `inscricoesEnviadas` vazio; `#cpf` com `aria-invalid="true"` e foco)
- [ ] T017 [P] [US2] Em `tests/test_inscricao.py`, `test_fr010_corrigir_cpf_remove_erro_e_envia`

### Implementação da User Story 2

- [ ] T018 [US2] Em `app/index.html`, implementar `validarCPF(valor)` exposta em `window` (research.md R1): "remover tudo que não for dígito; exigir 11 dígitos; rejeitar se todos forem iguais"; DVs por módulo 11 com 10 → 0
- [ ] T019 [US2] Em `app/index.html`, integrar a validação do CPF ao envio: mensagem "CPF inválido. Verifique os números digitados." em `#cpf-erro`, `aria-invalid="true"`, sem envio; limpar erro quando válido (FR-010)

**Checkpoint**: US1 e US2 funcionam de forma independente

---

## Phase 5: User Story 3 - Orientar o preenchimento de campos obrigatórios (Priority: P2)

**Goal**: campos vazios e e-mail mal formado impedem o envio com mensagens por campo e foco no primeiro erro

**Independent Test**: acionar "Continuar" com o formulário vazio: 3 mensagens, foco em `#nome`, nada enviado

### Testes da User Story 3 (escrever primeiro; devem FALHAR)

- [ ] T020 [P] [US3] Em `tests/test_inscricao.py`, `test_fr005_campos_vazios_nao_enviam` (formulário vazio → 3 mensagens exatas; nome só com espaços tratado como vazio)
- [ ] T021 [P] [US3] Em `tests/test_inscricao.py`, `test_fr006_email_invalido_nao_envia` ("maria.exemplo.com" → "Informe um e-mail válido, por exemplo nome@dominio.com.")
- [ ] T022 [P] [US3] Em `tests/test_inscricao.py`, `test_fr009_foco_no_primeiro_erro_e_aria_invalid` (vários erros → foco no primeiro na ordem nome, CPF, e-mail; `aria-describedby` aponta para a mensagem; `#resumo-erros` com `role="alert"` não vazio)

### Implementação da User Story 3

- [ ] T023 [US3] Em `app/index.html`, validar obrigatoriedade após `trim` com as mensagens "Informe seu nome completo.", "Informe seu CPF.", "Informe seu e-mail." (obrigatoriedade antes de formato, data-model.md)
- [ ] T024 [US3] Em `app/index.html`, validar e-mail com `^[^\s@]+@[^\s@]+\.[^\s@]+$` e mensagem "Informe um e-mail válido, por exemplo nome@dominio.com."
- [ ] T025 [US3] Em `app/index.html`, preencher `#resumo-erros` com a quantidade de erros e mover o foco para o primeiro campo inválido

**Checkpoint**: todas as histórias funcionam de forma independente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: acessibilidade transversal (FR-012) e portões de qualidade

- [ ] T026 [P] Em `tests/test_inscricao.py`, `test_fr012_operavel_por_teclado` (Tab percorre nome → CPF → e-mail → Continuar; Enter envia; fluxo completo só com teclado) e `test_fr012_contraste_e_foco_visivel` (contraste de texto calculado ≥ 4.5:1 e contorno de foco presente)
- [ ] T027 Revisar `app/index.html` contra WCAG 2.2 AA (1.3.1, 1.4.1, 1.4.3, 1.4.11, 2.1.1, 2.4.3, 2.4.7, 2.5.8, 3.3.1, 3.3.2, 3.3.3, 4.1.2, 4.1.3) e confirmar a anotação `@spec 001-inscricao-matricula@1.0.0` em todos os arquivos de código
- [ ] T028 Executar `pytest tests/ -v` (roteiro de `quickstart.md`) — todos os testes devem passar
- [ ] T029 Executar `python evospec.py validate` (portão da constituição) — PENDENTE: `evospec.py` não existe neste workspace
- [ ] T030 Executar `python evospec.py verify --set-baseline` (portão da constituição) — PENDENTE: `evospec.py` não existe neste workspace
- [ ] T031 Revisão independente dos testes de aceitação por pessoa que não implementou a feature (Princípio IV) — PENDENTE: não há outra pessoa disponível nesta execução
- [ ] T032 Varredura automática de acessibilidade com ferramenta dedicada (ex.: axe-core) e avaliação com pessoas com deficiência (Princípio I, SC-005) — PENDENTE: ferramenta não instalada e sem participantes neste workspace

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — bloqueia as histórias
- **US1, US2, US3 (Phases 3–5)**: dependem da Phase 2; como compartilham `app/index.html`, a implementação é sequencial (US1 → US2 → US3)
- **Polish (Phase 6)**: depende das histórias; T029–T032 dependem de recursos externos

### User Story Dependencies

- **US1 (P1)**: após Phase 2; sem dependência de outras histórias
- **US2 (P1)**: após Phase 2; usa o envio de US1 apenas para verificar FR-010 (testável sozinha via `validarCPF` e bloqueio)
- **US3 (P2)**: após Phase 2; independente

### Within Each User Story

- Testes escritos e falhando antes da implementação
- Validação antes da integração com o envio

### Parallel Opportunities

- T002 e T003 em paralelo com T001
- Todos os testes de uma história ([P]) em paralelo; testes de `tests/test_cpf.py` e `tests/test_inscricao.py` em paralelo
- Implementação em `app/index.html` não paraleliza (mesmo arquivo)

---

## Parallel Example: User Story 2

```bash
Task: "test_fr002_* e test_fr003_* em tests/test_cpf.py"
Task: "test_fr004_* e test_fr010_* em tests/test_inscricao.py"
```

---

## Implementation Strategy

### MVP First

1. Phase 1 + Phase 2
2. Phase 3 (US1) → validar de forma independente
3. Phase 4 (US2) — também P1; necessária para atender ao pedido (CPF inválido não envia)

### Incremental Delivery

1. Setup + Foundational → estrutura pronta
2. US1 → envio e confirmação
3. US2 → bloqueio por CPF inválido
4. US3 → orientação de campos obrigatórios
5. Polish → acessibilidade transversal e portões

---

## Notes

- Cada teste cita o FR no nome (`test_frNNN_…`) para rastreabilidade (Princípio IV)
- Dados de teste fictícios; nenhum dado pessoal real
- Commit ao final de cada comando do Spec Kit
