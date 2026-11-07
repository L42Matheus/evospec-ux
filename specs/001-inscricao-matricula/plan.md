# Plano de Implementação: Formulário de Inscrição Escolar (Matrícula Acadêmica)

**Branch**: `001-inscricao-matricula` | **Date**: 2026-11-07 | **Spec**: [spec.md](./spec.md)

**Versão da especificação de origem**: `001-inscricao-matricula@1.0.0`

**Input**: Especificação da feature em `/specs/001-inscricao-matricula/spec.md` (versão 1.0.0)

**Note**: Este plano foi gerado pelo comando `/speckit-plan`.

## Resumo

Página web única (`app/index.html`) com formulário de inscrição (nome completo, CPF, e-mail) e
botão "Continuar". Ao acionar o botão, o script da página valida os campos (obrigatoriedade,
formato de e-mail e CPF pelos dois dígitos verificadores, rejeitando dígitos repetidos). Com erro,
nada é enviado, as mensagens são exibidas por campo, os campos ficam marcados com
`aria-invalid` e o foco vai para o primeiro campo inválido. Sem erro, a inscrição é "enviada"
(registro local simulado, sem rede — ver research.md) e o formulário é substituído por uma
confirmação anunciada em região viva. Tudo em HTML, CSS e JavaScript puros, sem frameworks.

## Contexto Técnico

**Language/Version**: HTML5, CSS3, JavaScript (ES2020, sem transpilação) na aplicação; Python 3.13
nos testes de aceitação.

**Primary Dependencies**: nenhuma na aplicação. Testes: `pytest` e `playwright` (Python), já
instalados no ambiente — justificativa em "Acompanhamento de Complexidade".

**Storage**: N/A (inscrição mantida apenas em memória na página; ver research.md, decisão R2).

**Testing**: pytest + Playwright (Chromium/Chrome headless) abrindo `app/index.html` via `file://`.

**Target Platform**: navegadores modernos (Chrome, Firefox, Safari, Edge) em desktop e celular.

**Project Type**: aplicação web estática de página única.

**Performance Goals**: resposta (erro ou confirmação) em < 1 s após "Continuar" (SC-004); a
validação é local e instantânea.

**Constraints**: WCAG 2.2 AA; interface em português do Brasil; nenhum dado pessoal transmitido ou
persistido; arquivo único `app/index.html` (CSS e JS embutidos).

**Scale/Scope**: 1 tela, 3 campos, 1 estado de confirmação; 12 requisitos funcionais.

## Verificação da Constituição

*GATE: deve passar antes da Fase 0 e ser reavaliada após a Fase 1.*

| Princípio / regra | Situação | Como o plano atende |
|---|---|---|
| I. Acessibilidade verificável (WCAG 2.2 AA) | PASSA | Rótulos `<label for>`, mensagens ligadas por `aria-describedby`, `aria-invalid`, região `role="status"`/`aria-live`, foco no primeiro erro, foco visível, contraste ≥ 4.5:1, erros em texto (não só cor), alvo de toque ≥ 24×24 px. Testes automatizados cobrem a parte verificável; avaliação com pessoas com deficiência fica pendente (não há participantes neste workspace). |
| II. Especificação como fonte da verdade | PASSA | `app/index.html` e os testes trazem `@spec 001-inscricao-matricula@1.0.0`; este plano e `tasks.md` registram a versão de origem 1.0.0. |
| III. Evolução orientada por evidências | N/A (versão inicial) | Esta é a versão inicial da especificação; nenhuma evidência/proposta é exigida. Pastas `evidence/` e `changes/` não são criadas agora. |
| IV. Verificação independente (NÃO NEGOCIÁVEL) | PASSA COM RESSALVA | Cada FR terá ao menos um teste de aceitação com o identificador no nome/docstring, escrito a partir da spec **antes** da implementação. Ressalva: neste workspace o mesmo agente escreve testes e implementação; não há outra pessoa disponível. A revisão independente dos testes por um humano fica registrada como tarefa pendente. |
| V. Simplicidade | PASSA | Sem frameworks; app em HTML/CSS/JS puros; ferramentas de teste em Python. Dependências de teste justificadas abaixo. |
| Português do Brasil | PASSA | Interface e artefatos em pt-BR. |
| Dados anonimizados | PASSA | Testes usam dados fictícios (CPFs gerados válidos de exemplo, nomes fictícios); nada é gravado em `evidence/`. |
| Portões `python evospec.py validate` / `verify --set-baseline` | PENDENTE | `evospec.py` não existe neste workspace; os portões não podem ser executados. Registrado como tarefa pendente em `tasks.md`. Substituto provisório: `pytest tests/` sem falhas. |

**Resultado do gate (pré-Fase 0)**: aprovado com ressalvas documentadas (IV e portões evospec).

**Reavaliação pós-Fase 1**: o desenho (research.md, data-model.md, contracts/ui-contract.md,
quickstart.md) não introduz dependências na aplicação, mantém a página única e preserva as
anotações de versão. Resultado inalterado: aprovado com as mesmas ressalvas.

## Estrutura do Projeto

### Documentação (esta feature)

```text
specs/001-inscricao-matricula/
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Fase 0 (/speckit-plan)
├── data-model.md        # Fase 1 (/speckit-plan)
├── quickstart.md        # Fase 1 (/speckit-plan)
├── contracts/
│   └── ui-contract.md   # Fase 1: contrato da interface (IDs, mensagens, estados, API de teste)
├── checklists/
│   └── requirements.md  # /speckit-specify
└── tasks.md             # Fase 2 (/speckit-tasks — não criado por /speckit-plan)
```

### Código-fonte (raiz do repositório)

```text
app/
└── index.html                   # Página única: HTML + CSS + JS embutidos (@spec 001-inscricao-matricula@1.0.0)

tests/
├── conftest.py                  # Fixture Playwright que abre app/index.html
├── test_cpf.py                  # Testes de aceitação FR-002, FR-003 (validação de CPF)
└── test_inscricao.py            # Testes de aceitação FR-001, FR-004..FR-012 (fluxo do formulário)
```

**Structure Decision**: projeto único estático. A aplicação inteira fica em `app/index.html`
(exigência do pedido: página única). Os testes de aceitação ficam em `tests/`, em Python
(ferramentas do método usam Python, conforme Princípio V), sem alterar a aplicação.

## Acompanhamento de Complexidade

| Item | Por que é necessário | Alternativa mais simples rejeitada porque |
|---|---|---|
| Dependência de teste `pytest` + `playwright` (Python) | Princípio IV exige teste de aceitação por FR; vários FRs (foco, `aria-invalid`, região viva, teclado) só são verificáveis num navegador real. Já instalados no ambiente; não entram na aplicação. | Testar só a função de CPF em Python duplicaria a lógica e não verificaria a página; teste manual não é repetível nem ligado a FR. |
| Ressalva ao Princípio IV (mesmo agente escreve testes e código) | Não há outra pessoa disponível nesta execução. | Não implementar violaria o pedido; a mitigação é escrever os testes antes da implementação, a partir da spec, e deixar revisão humana pendente. |
