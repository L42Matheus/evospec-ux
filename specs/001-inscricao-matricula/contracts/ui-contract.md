# Contrato da Interface: `app/index.html`

**Especificação de origem**: `001-inscricao-matricula@1.0.0`

Este contrato define os pontos observáveis da página dos quais os testes de aceitação dependem.
Mudar qualquer item é uma mudança de contrato.

## Elementos

| Elemento | Seletor | Requisitos |
|---|---|---|
| Formulário | `form#form-inscricao` (`novalidate`) | FR-001 |
| Campo nome | `input#nome` (`type="text"`, `autocomplete="name"`), rótulo `label[for=nome]` = "Nome completo" | FR-001, FR-005 |
| Campo CPF | `input#cpf` (`type="text"`, `inputmode="numeric"`), rótulo "CPF", dica `#cpf-dica` | FR-001, FR-002 |
| Campo e-mail | `input#email` (`type="email"`, `autocomplete="email"`), rótulo "E-mail" | FR-001, FR-006 |
| Mensagens por campo | `#nome-erro`, `#cpf-erro`, `#email-erro` (vazias e ocultas quando sem erro) | FR-004..FR-006, FR-010 |
| Resumo de erros | `#resumo-erros` (`role="alert"`) | FR-009 |
| Botão | `button#continuar` (`type="submit"`), texto "Continuar" | FR-001, FR-007 |
| Confirmação | `#confirmacao` (`role="status"`, `hidden` até o envio); título `#confirmacao-titulo` (`tabindex="-1"`) com "Inscrição enviada com sucesso!"; texto com o nome do estudante | FR-008, FR-009 |
| Nova inscrição | `button#nova-inscricao` dentro de `#confirmacao` | FR-011 |

## Atributos ARIA

- Campo inválido: `aria-invalid="true"`; válido: atributo ausente ou `"false"`.
- `aria-describedby` de cada campo inclui o id da sua mensagem de erro (e, no CPF, da dica).

## Mensagens (texto exato)

| Situação | Texto |
|---|---|
| Nome vazio | `Informe seu nome completo.` |
| CPF vazio | `Informe seu CPF.` |
| CPF inválido | `CPF inválido. Verifique os números digitados.` |
| E-mail vazio | `Informe seu e-mail.` |
| E-mail com formato inválido | `Informe um e-mail válido, por exemplo nome@dominio.com.` |
| Confirmação (título) | `Inscrição enviada com sucesso!` |

## Interface programática (observabilidade para testes)

- `window.validarCPF(valor: string): boolean` — implementa FR-002/FR-003.
- `window.inscricoesEnviadas: Array<{nome, cpf, email, enviadaEm, situacao}>` — cada envio
  adiciona exatamente um item (envio simulado, research.md R2).
- Evento `inscricao:enviada` disparado em `document` com `detail` = a inscrição.
