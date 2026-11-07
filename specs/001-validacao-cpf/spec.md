# Feature Specification: Validação do CPF na matrícula acadêmica

**Feature Branch**: `001-validacao-cpf`

**Created**: 2026-11-07

**Status**: Approved

**Version**: 2

**Input**: User description: "Validação do CPF no formulário de matrícula acadêmica. O estudante preenche nome completo, CPF e e-mail e aciona "Continuar". Se o CPF for inválido (dígitos verificadores incorretos ou todos os dígitos iguais), a inscrição não deve ser enviada e uma mensagem de erro deve ser exibida. Se o CPF for válido e os demais campos estiverem preenchidos, a inscrição é enviada e uma confirmação é exibida. Esta é a versão inicial da especificação (antes de qualquer evidência de uso)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Impedir inscrição com CPF inválido (Priority: P1)

O estudante preenche o formulário de matrícula e digita o CPF com erro. Ao acionar "Continuar", a
inscrição não é enviada e o estudante é avisado de que o CPF é inválido, para que possa corrigi-lo.

**Why this priority**: inscrições com CPF inválido geram cadastros inconsistentes e retrabalho da
secretaria; é a regra central da feature.

**Independent Test**: preencher o formulário com um CPF de dígitos verificadores incorretos,
acionar "Continuar" e verificar que a confirmação não aparece e que a mensagem de erro é exibida.

**Acceptance Scenarios**:

1. **Given** o formulário preenchido com um CPF inválido, **When** o estudante aciona "Continuar",
   **Then** a inscrição não é enviada.
2. **Given** o formulário preenchido com um CPF inválido, **When** o estudante aciona "Continuar",
   **Then** uma mensagem informando que o CPF é inválido é exibida.

---

### User Story 2 - Enviar inscrição com CPF válido (Priority: P2)

O estudante preenche nome, CPF válido e e-mail e aciona "Continuar". A inscrição é enviada e ele
vê uma confirmação.

**Why this priority**: é o caminho feliz da matrícula; depende da regra de validação da história 1.

**Independent Test**: preencher o formulário com um CPF válido e os demais campos, acionar
"Continuar" e verificar que a confirmação de envio é exibida.

**Acceptance Scenarios**:

1. **Given** o formulário preenchido com CPF válido, nome e e-mail, **When** o estudante aciona
   "Continuar", **Then** a inscrição é enviada e a mensagem "Inscrição enviada com sucesso" é
   exibida.

---

### User Story 3 - Perceber o erro com tecnologia assistiva (Priority: P1)

O estudante que usa leitor de tela aciona "Continuar" com CPF inválido e é informado do erro
imediatamente, com o foco no campo que precisa corrigir. *(Origem: evidência EVD-17, proposta
CR-001.)*

**Why this priority**: sem isso, o estudante não descobre por que a inscrição não avança e
precisa de ajuda externa (falha observada na tarefa T2).

**Independent Test**: com o leitor de tela ativo, preencher um CPF inválido, acionar
"Continuar" e verificar que a mensagem é anunciada e que o foco está no campo CPF.

**Acceptance Scenarios**:

1. **Given** CPF inválido, **When** o estudante aciona "Continuar", **Then** o foco vai para o
   campo CPF.
2. **Given** CPF inválido, **When** o foco chega ao campo CPF, **Then** o leitor de tela informa
   que o campo é inválido e lê a mensagem de erro.
3. **Given** CPF inválido, **When** a mensagem de erro aparece, **Then** o leitor de tela a
   anuncia sem ação adicional do estudante.

---

### Edge Cases

- CPF com todos os dígitos iguais (por exemplo, 111.111.111-11) é considerado inválido, mesmo que
  os dígitos verificadores coincidam.
- CPF digitado com ou sem pontuação (pontos e hífen) é aceito; apenas os dígitos são considerados.
- CPF com menos ou mais de 11 dígitos é considerado inválido.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST impedir o envio da inscrição quando o CPF informado for inválido.
- **FR-002**: O sistema MUST exibir uma mensagem de erro informando que o CPF é inválido quando o
  estudante acionar "Continuar" com CPF inválido.
- **FR-003**: O sistema MUST enviar a inscrição e exibir uma confirmação quando o CPF for válido e
  os demais campos estiverem preenchidos.
- **FR-004**: Ao acionar "Continuar" com CPF inválido, o sistema MUST levar o foco para o campo CPF.
- **FR-005**: Com CPF inválido, o campo CPF MUST ser identificado como inválido para tecnologias
  assistivas e ter a mensagem de erro como sua descrição acessível.
- **FR-006**: A mensagem de erro MUST ser anunciada automaticamente por leitores de tela no momento
  em que aparece, sem que o estudante precise procurá-la.

### Key Entities *(include if feature involves data)*

- **Inscrição**: dados informados pelo estudante (nome completo, CPF, e-mail) e seu estado
  (não enviada, enviada).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das tentativas de envio com CPF inválido são bloqueadas.
- **SC-002**: 100% das inscrições com CPF válido e campos preenchidos são enviadas e confirmadas.
- **SC-003**: O estudante identifica o motivo do bloqueio e corrige o CPF sem ajuda externa em pelo
  menos 90% das tentativas.

## Assumptions

- A validação usa a regra oficial dos dígitos verificadores do CPF; não há consulta à Receita
  Federal.
- O envio da inscrição é simulado na própria página (não há servidor de matrícula no protótipo).
- Os campos nome e e-mail não têm regras de validação próprias nesta feature.
- A acessibilidade segue a constituição do projeto (WCAG 2.2 AA como piso).

## Histórico de versões (EvoSpec)

| Versão | Mudança | Proposta | Evidência | Aprovada por |
|--------|---------|----------|-----------|--------------|
| 1 | Versão inicial | — | — | — |
| 2 | Erro do CPF perceptível por tecnologias assistivas | CR-001 | EVD-17 | Lucas Matheus Silva |
