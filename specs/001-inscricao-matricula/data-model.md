# Modelo de Dados (Fase 1): Formulário de Inscrição Escolar

**Especificação de origem**: `001-inscricao-matricula@1.0.0`

## Entidade: Inscrição

Registro em memória criado no envio bem-sucedido (ver research.md, R2). Não é persistido.

| Campo | Tipo | Origem | Regras de validação | FR |
|---|---|---|---|---|
| `nome` | texto | campo "Nome completo" | obrigatório após `trim`; mensagem "Informe seu nome completo." | FR-005 |
| `cpf` | texto com 11 dígitos | campo "CPF", somente dígitos | obrigatório ("Informe seu CPF."); exatamente 11 dígitos; não todos iguais; dois DVs conferem; senão "CPF inválido. Verifique os números digitados." | FR-002, FR-003, FR-004, FR-005 |
| `email` | texto | campo "E-mail" | obrigatório após `trim` ("Informe seu e-mail."); formato `^[^\s@]+@[^\s@]+\.[^\s@]+$`, senão "Informe um e-mail válido, por exemplo nome@dominio.com." | FR-005, FR-006 |
| `enviadaEm` | data/hora ISO 8601 | relógio do navegador no envio | gerado pelo sistema | FR-007 |
| `situacao` | `"enviada"` | sistema | constante na v1.0.0 | FR-007 |

Ordem de verificação por campo: obrigatoriedade primeiro; só então formato/CPF.

## Estados do formulário

```text
            Continuar (com erros)
   ┌──────────────┐ ───────────────► ┌──────────────┐
   │ preenchendo  │                  │  com_erros   │──┐ Continuar (com erros): atualiza mensagens
   └──────────────┘ ◄─────────────── └──────────────┘◄─┘
          │   ▲        (editar campos)       │
Continuar │   │ Nova inscrição               │ Continuar (tudo válido)
(válido)  ▼   │                              ▼
   ┌──────────────────────────────────────────────┐
   │ enviada (formulário oculto, confirmação visível) │  — novos envios bloqueados (FR-011)
   └──────────────────────────────────────────────┘
```

- `preenchendo` → `com_erros`: ao menos um campo inválido; nada enviado (FR-004, FR-005, FR-006).
- `com_erros` → `com_erros`: mensagens de campos agora válidos são removidas (FR-010).
- `preenchendo`/`com_erros` → `enviada`: todos válidos; 1 registro adicionado (FR-007, FR-008).
- `enviada` → `preenchendo`: botão "Nova inscrição" limpa campos e mensagens.
