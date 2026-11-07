# Data Model: Validação do CPF na matrícula acadêmica

**Spec Version**: 2

## Inscrição

| Campo | Tipo | Regra |
|-------|------|-------|
| nome | texto | obrigatório para envio (sem validação própria nesta feature) |
| cpf | texto | 11 dígitos após remover pontuação; dígitos verificadores corretos; não pode ser sequência repetida |
| email | texto | obrigatório para envio (sem validação própria nesta feature) |

## Estados

```text
editando ──Continuar com CPF inválido──▶ erro_cpf ──(estudante corrige)──▶ editando
editando ──Continuar com CPF válido────▶ enviada
```

- **erro_cpf**: envio bloqueado (FR-001); mensagem exibida (FR-002), anunciada (FR-006) e associada
  ao campo marcado como inválido (FR-005); foco no campo CPF (FR-004); dados preservados
  (`002-preservacao-dados` FR-001).
- **enviada**: formulário oculto e confirmação exibida (FR-003); marcação de erro removida.
