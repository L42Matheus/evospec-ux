# EvoSpec-UX — protótipo

Protótipo do método descrito no pré-projeto *Spec-Driven Development Orientado por Evidências de Usabilidade* (PPGTI/IFPB, nov. 2026). Implementa o ciclo de evolução governada de especificações sobre o exemplo motivador (SPEC-04 / EVD-17: erro de CPF não anunciado por leitor de tela).

> Protótipo exploratório. Não constitui resultado experimental; serve para materializar o método, testar as regras de governança e preparar o piloto.

## Estrutura

```
app/index.html            aplicação de referência (formulário de matrícula), anotada com @spec SPEC-XX@versão
specs/SPEC-*.yaml         especificações versionadas com critérios de aceitação (AC-*)
evidence/EVD-*.yaml       evidências de uso estruturadas (observado, tarefa, tecnologia assistiva, severidade)
changes/CR-*.yaml         propostas de mudança (observado × inferido, justificativa, impacto, decisão humana)
changes/diffs/            diffs das especificações gerados na aprovação
changes/prompts/          prompts enviados ao LLM para redigir propostas
tests/acceptance.py       testes de aceitação ligados a critérios (@criterion("AC-04.4"))
tests/test_governance.py  autotestes das regras de governança
results/baseline.json     última verificação aceita (sem regressões)
TRACE.md                  matriz evidência → proposta → spec@versão → critério → teste → resultado
evospec.py                núcleo do método e CLI
web.py, templates/        painel web (Flask)
docs/versoes/v1.html      versão 1 do formulário, para comparação
vendor/axe.min.js         axe-core (MPL-2.0)
Dockerfile, railway.toml  deploy no Railway
.github/workflows/        CI: governança + verificação a cada push
```

## Como rodar

### Painel web (local)

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
python web.py            # http://localhost:8000
```

Ou com Docker: `docker build -t evospec-ux . && docker run -p 8000:8000 evospec-ux`.

### Deploy no Railway

1. No Railway: **New Project → Deploy from GitHub repo → `evospec-ux`**. O `Dockerfile` e o `railway.toml` são detectados automaticamente.
2. Em **Variables**, defina:
   - `EVOSPEC_PASSWORD`: senha exigida para ações (registrar evidência, decidir, verificar). Recomendado, porque a URL é pública.
   - `ANTHROPIC_API_KEY` (opcional): permite que o botão "Gerar proposta (LLM)" chame o modelo. Sem ela, o painel gera o prompt para uso manual.
   - `SECRET_KEY`: qualquer texto aleatório.
3. Em **Settings → Networking → Generate Domain** para obter a URL pública. O health check usa `/saude`.

O sistema de arquivos do Railway é temporário: evidências, decisões e execuções feitas pelo painel somem a cada novo deploy, a menos que se adicione um volume montado no diretório do projeto. O registro oficial do ciclo é o histórico do Git.

### Integração contínua

O workflow `.github/workflows/evospec.yml` roda a cada push: regras de governança, autotestes e verificação independente. O build falha se houver erro de governança ou regressão, funcionando como o portão de drift e regressão do método.

### Linha de comando

Requisitos: os mesmos do painel. O axe-core está em `vendor/` (licença MPL-2.0); o Chromium do Playwright é usado por padrão (`EVOSPEC_CHROME` permite indicar outro navegador).

```bash
python3 evospec.py status                     # visão geral
python3 evospec.py validate                   # regras de governança e drift
python3 evospec.py propose EVD-17             # rascunho de proposta via LLM (ANTHROPIC_API_KEY) ou prompt salvo
python3 evospec.py decide CR-001 --by "Nome" --decision approved --note "..."
python3 evospec.py verify --label r1 --set-baseline   # testes + axe-core + detecção de regressão
python3 evospec.py trace                      # gera TRACE.md
python3 tests/test_governance.py              # autotestes das regras
```

## Correspondência com o pré-projeto

| Etapa do método (Fig. 1) | No protótipo |
|---|---|
| 1. Evidências de usabilidade | `evidence/EVD-*.yaml` |
| 2. Normalização e incerteza | `propose`: o LLM redige a proposta separando `observed` e `inferred`; regra de admissibilidade R2 |
| 3. Coevolução de especificações | `decide`: aprovação humana aplica a mudança, incrementa a versão e gera o diff |
| 4. Implementação com agentes | o agente altera `app/` e atualiza a anotação `@spec` (commit no git) |
| 5. Verificação independente | `verify`: testes escritos a partir dos critérios aprovados, axe-core e comparação com a linha de base |
| 6. Realimentação | `trace` e `results/`; nova evidência inicia nova rodada |

Os dois mecanismos da Seção 4.1 estão separados no código: a **incorporação de evidência** (`propose`, `decide`, regras R1–R3) e o **controle de consistência** (regras R4–R6 e `verify`). Isso permite montar a condição de ablação B, desligando um deles.

### Regras de governança (`validate`)

| Regra | Verifica |
|---|---|
| R1 | proposta referencia evidências, especificações e critérios existentes |
| R2 | admissibilidade: sem descrição observável não há mudança; inferências exigem justificativa; critérios precisam de texto verificável |
| R3 | toda nova versão de especificação vem de proposta aprovada, com responsável humano registrado |
| R4 | todo critério ativo tem teste de aceitação |
| R5 | não há teste órfão (para critério inexistente) |
| R6 | drift: o código declara implementar a versão aprovada de cada especificação |

## Rodada de demonstração (histórico do git)

1. **r0**: app v1, SPEC-04@1, SPEC-06@1. Todos os critérios passam; **axe-core: 0 violações**, apesar da barreira real.
2. **EVD-17** registrada → `propose` gera o prompt → o LLM redige **CR-001** (pending).
3. **Aprovação humana** → SPEC-04@2 com AC-04.4 (foco), AC-04.5 (aria-invalid + descrição acessível) e AC-04.6 (região viva). O `validate` bloqueia: critérios sem teste (R4) e drift (R6).
4. O verificador escreve os testes → a v1 falha nos 3 novos critérios.
5. **Implementação 1 do agente** → corrige a acessibilidade, mas limpa o formulário: **regressão em AC-06.1** detectada; linha de base recusada; commit revertido.
6. **Implementação 2 do agente** → 7/7 critérios passam, 0 regressões; linha de base atualizada.

## Limitações conhecidas

- A anotação `@spec` é declarativa: o R6 detecta código que não acompanhou a versão da especificação, mas não prova que o código implementa a especificação. Isso fica a cargo dos testes (R4 + `verify`).
- As evidências e a proposta CR-001 são ilustrativas. Nesta demonstração, a proposta foi redigida pelo Claude a partir do prompt gerado, sem chamada de API.
- Os testes verificam propriedades da árvore de acessibilidade do Chrome, não a verbalização real de um leitor de tela. Isso exige reteste com usuários ou com NVDA.
- Uma única aplicação e uma única rodada; o experimento A/B/C ainda precisa de várias aplicações, rodadas e repetições.
