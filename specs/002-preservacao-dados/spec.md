# Feature Specification: Preservação dos dados preenchidos

**Feature Branch**: `002-preservacao-dados`

**Created**: 2026-11-07

**Status**: Approved

**Version**: 1

**Input**: User description: "Preservação dos dados preenchidos no formulário de matrícula. Quando ocorrer um erro de validação (por exemplo, CPF inválido), os valores já digitados pelo estudante nos campos nome completo, CPF e e-mail devem ser mantidos, para que ele corrija apenas o que está errado sem redigitar tudo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Corrigir um erro sem redigitar o formulário (Priority: P1)

O estudante preenche nome, CPF e e-mail, aciona "Continuar" e recebe um erro de validação. Todos os
valores que ele digitou continuam nos campos, e ele corrige apenas o campo com problema.

**Why this priority**: redigitar dados após um erro aumenta o abandono e novos erros, com impacto
maior para quem usa tecnologias assistivas ou tem dificuldades motoras.

**Independent Test**: preencher os três campos com um CPF inválido, acionar "Continuar" e verificar
que nome, CPF e e-mail mantêm exatamente os valores digitados.

**Acceptance Scenarios**:

1. **Given** nome, CPF inválido e e-mail preenchidos, **When** o estudante aciona "Continuar",
   **Then** os três campos mantêm os valores informados.

---

### Edge Cases

- Erros sucessivos (acionar "Continuar" várias vezes com CPF inválido) não apagam nenhum campo.
- O campo com erro também mantém o valor digitado, para que o estudante veja o que precisa corrigir.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Após um erro de validação do CPF, o sistema MUST manter nos campos nome, CPF e e-mail
  os valores informados pelo estudante.

### Key Entities *(include if feature involves data)*

- **Inscrição**: mesma entidade da feature `001-validacao-cpf` (nome completo, CPF, e-mail).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos erros de validação, nenhum valor já digitado é perdido.
- **SC-002**: O estudante conclui a correção de um CPF inválido sem redigitar os demais campos.

## Assumptions

- A feature se aplica ao mesmo formulário da `001-validacao-cpf`.
- Não há persistência entre recarregamentos da página; a preservação vale durante a mesma visita.

## Histórico de versões (EvoSpec)

| Versão | Mudança | Proposta | Evidência | Aprovada por |
|--------|---------|----------|-----------|--------------|
| 1 | Versão inicial | — | — | — |
