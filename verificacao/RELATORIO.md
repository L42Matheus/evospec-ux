# Rodada do zero — relatório da verificação independente

**Data**: 2026-11-07 · **Branch**: `rodada-do-zero` · **Feature**: `specs/001-inscricao-matricula` (spec 1.0.0)

## Como a rodada foi feita

1. Workspace isolado contendo apenas o GitHub Spec Kit (`.specify/`, `.claude/skills/`) e a constituição
   do projeto, **sem** evidências, propostas, código anterior ou qualquer menção ao problema EVD-17.
2. Um agente novo, sem contexto da pesquisa, recebeu somente o pedido do usuário ("formulário de
   inscrição escolar com nome, CPF e e-mail; CPF validado; erro se inválido; confirmação se válido") e
   executou `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`, com um commit
   por fase (ver `git log`).
3. O agente escreveu 48 testes (pytest + Playwright); todos passam. Como foram escritos pelo próprio
   implementador, não contam como verificação independente (princípio IV; tarefa T031 pendente).
4. A verificação independente (`verificacao_independente.py`) aplicou os mesmos critérios de
   acessibilidade da rodada anterior e o axe-core, a partir do contrato da interface, sem ler o código.

## Resultado

| Verificação | Resultado |
|---|---|
| Bloqueia envio com CPF inválido | passa |
| Mensagem de erro visível | passa |
| Envia com CPF válido | passa |
| Foco vai para o campo CPF | passa |
| Campo CPF com `aria-invalid` e mensagem como descrição acessível | passa |
| Mensagem do CPF inserida em região viva | **falha** (ver discussão) |
| Dados preservados após erro | passa |
| axe-core (WCAG 2.2 AA) | 0 violações |

## Discussão

- **A barreira da EVD-17 não se repetiu.** O agente, guiado apenas pela constituição (princípio I:
  WCAG 2.2 AA), escreveu por conta própria o FR-009 (mensagens anunciadas, foco no primeiro campo
  inválido, campos marcados como inválidos) e o implementou.
- **A falha é do teste, não necessariamente da interface.** A região viva (`#resumo-erros`,
  `role="alert"`) anuncia um resumo ("Há 1 campo com erro. Corrija-o para continuar."), e a mensagem
  "CPF inválido…" chega ao leitor de tela pela descrição do campo que recebe o foco. É uma solução
  válida pela WCAG; o critério de teste da rodada anterior estava preso a uma implementação específica.
- **Ponto em aberto para avaliação com usuários**: o anúncio do alerta e a mudança de foco acontecem ao
  mesmo tempo; leitores de tela podem interromper um com o outro. Só um teste com NVDA/usuários
  responde se a mensagem é efetivamente percebida.
- **Incompatibilidade de formato**: o agente versionou a especificação como `1.0.0` (semântico) e
  anotou o código com `@spec 001-inscricao-matricula@1.0.0`; o EvoSpec-UX espera versões inteiras.

## Implicações para a pesquisa

1. Uma constituição que exige WCAG já evitou a barreira "clássica" — é o que a condição B (SDD
   convencional com diretrizes) faria. A contribuição das evidências de usuários precisa ser
   demonstrada em problemas que as diretrizes **não** antecipam.
2. Critérios de aceitação derivados de evidências devem descrever o efeito para o usuário (a mensagem é
   percebida), não o mecanismo (texto dentro de `role="alert"`); caso contrário, o teste rejeita
   soluções válidas — ameaça à validade de construção.
3. Artefatos gerados por agentes reais não seguem exatamente as convenções do EvoSpec-UX; a extensão
   precisa ser tolerante a formatos (ou fornecer modelos via preset/extensão do Spec Kit).
