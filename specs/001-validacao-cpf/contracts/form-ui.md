# Contrato da interface: formulário de matrícula

**Spec Version**: 2

Elementos e comportamentos dos quais dependem os testes de aceitação (`tests/acceptance.py`).
Alterar este contrato exige atualizar os testes correspondentes.

| Elemento | Identificação | Contrato |
|----------|---------------|----------|
| Campo nome | `#nome`, rótulo "Nome completo" | campo de texto |
| Campo CPF | `#cpf`, papel `textbox`, nome acessível "CPF" | com CPF inválido: `aria-invalid="true"` e descrição acessível contendo "CPF inválido" (FR-005); recebe o foco (FR-004) |
| Mensagem de erro | `#cpf-erro` | região viva (`role="alert"` ou `aria-live`) presente desde o carregamento; recebe o texto com "CPF inválido" (FR-002, FR-006) |
| Campo e-mail | `#email`, rótulo "E-mail" | campo de e-mail |
| Botão | papel `button`, nome "Continuar" | aciona a validação |
| Confirmação | `#confirmacao` | oculta até o envio; visível após envio válido (FR-003) |
