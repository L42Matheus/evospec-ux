# EvoSpec-UX Constitution

## Core Principles

### I. Acessibilidade verificável

A aplicação MUST atender, no mínimo, à WCAG 2.2 nível AA. A conformidade automática é um piso, não
uma prova de acessibilidade: quando uma dificuldade observada com pessoas com deficiência contradiz
uma verificação automática, a evidência observada prevalece e MUST ser tratada como defeito ou
lacuna da especificação.

*Justificativa*: ferramentas automáticas não detectam todas as barreiras vividas pelos usuários.

### II. Especificação como fonte da verdade

O comportamento da aplicação MUST ser derivado de `specs/<feature>/spec.md`. O agente de
programação implementa a partir da especificação aprovada, e não de pedidos avulsos. Todo arquivo
de código que implementa uma feature MUST declarar a versão implementada com a anotação
`@spec <feature>@<versão>`. Plano (`plan.md`) e tarefas (`tasks.md`) MUST registrar a versão da
especificação da qual foram gerados.

*Justificativa*: a anotação e o registro de versão permitem detectar divergência entre
especificação, plano, tarefas e código.

### III. Evolução orientada por evidências

Nenhuma alteração de especificação após a versão inicial MAY ser feita sem: (a) uma evidência de
uso registrada em `evidence/`; (b) uma proposta de mudança em `changes/` que separe o que foi
observado do que foi inferido; e (c) uma decisão humana registrada, com responsável e data. Uma
evidência não é automaticamente um requisito: a proposta MUST justificar a mudança e listar os
requisitos existentes que precisam ser preservados.

*Justificativa*: o apoio de LLMs na redação das propostas exige rastreabilidade e controle humano
para evitar requisitos distorcidos ou não sustentados pelas evidências.

### IV. Verificação independente e sem regressões (NÃO NEGOCIÁVEL)

Cada requisito funcional MUST ter ao menos um teste de aceitação ligado ao seu identificador. Os
testes de novos requisitos MUST ser escritos a partir da especificação aprovada, antes da
implementação, por quem não implementa a mudança. A cada mudança, os requisitos listados como
"a preservar" MUST ser reverificados; uma regressão impede a atualização da linha de base.

*Justificativa*: o agente que implementa não deve ser o único a atestar que sua implementação está
correta.

### V. Simplicidade

A aplicação de referência MUST usar HTML, CSS e JavaScript sem frameworks. As ferramentas do método
usam Python. Novas dependências MUST ser justificadas no plano.

*Justificativa*: reduzir variáveis de confusão no estudo e manter o objeto experimental
inspecionável.

## Restrições do projeto

- Textos da interface e artefatos de especificação MUST estar em português do Brasil.
- Dados de participantes MUST ser anonimizados (identificadores como P1, P2…); nenhum dado pessoal
  real é registrado em `evidence/`.
- As evidências de exemplo são ilustrativas e MUST ser identificadas como tal enquanto não vierem
  de sessões reais.

## Fluxo de desenvolvimento e portões de qualidade

1. Especificação inicial: `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` →
   `/speckit-implement`.
2. Evolução: evidência → proposta (`evospec propose`) → decisão humana (`evospec decide`) →
   especificação versionada → `/speckit-plan` e `/speckit-tasks` regenerados → testes dos novos
   requisitos → `/speckit-implement`.
3. Portões: `python evospec.py validate` MUST terminar sem erros e
   `python evospec.py verify --set-baseline` MUST terminar sem regressões antes de integrar uma
   mudança; o CI executa ambos a cada push.

## Governance

Esta constituição prevalece sobre outras práticas do repositório. Emendas exigem proposta escrita,
aprovação do pesquisador responsável e do orientador e atualização da versão: MAJOR para remoção ou
redefinição de princípios, MINOR para novos princípios ou seções, PATCH para ajustes de redação.
Toda revisão de mudança MUST verificar a conformidade com os princípios III e IV.

**Version**: 1.0.0 | **Ratified**: 2026-11-07 | **Last Amended**: 2026-11-07
