# Guia Rápido de Validação: Formulário de Inscrição Escolar

**Especificação de origem**: `001-inscricao-matricula@1.0.0`

## Pré-requisitos

- Navegador moderno (para uso manual).
- Para os testes automáticos: Python 3.11+, `pytest`, `playwright` (Python) e um Chromium/Chrome
  disponível (`python -m playwright install chromium` se necessário).

## Executar a aplicação

Abrir `app/index.html` diretamente no navegador (não há build nem servidor). Opcionalmente:
`python -m http.server -d app 8000` e acessar `http://localhost:8000`.

## Executar os testes de aceitação

```bash
pytest tests/ -v
```

Resultado esperado: todos os testes passam; cada teste cita no nome ou docstring o FR que verifica
(ver [contrato](./contracts/ui-contract.md)).

## Portões da constituição

`python evospec.py validate` e `python evospec.py verify --set-baseline` — **indisponíveis neste
workspace** (`evospec.py` não existe). Pendentes até a ferramenta ser adicionada.

## Roteiro manual

| # | Ação | Resultado esperado | FR |
|---|---|---|---|
| 1 | Acionar "Continuar" com tudo vazio | 3 mensagens de obrigatoriedade; foco em "Nome completo"; nada enviado | FR-005, FR-009 |
| 2 | Nome "Maria da Silva", CPF `111.111.111-11`, e-mail `maria@exemplo.com` → Continuar | "CPF inválido…" junto ao CPF; foco no CPF; nada enviado | FR-003, FR-004 |
| 3 | Trocar CPF por `529.982.247-24` → Continuar | mesma mensagem de CPF inválido | FR-002, FR-004 |
| 4 | Trocar CPF por `529.982.247-25` → Continuar | erro some; confirmação "Inscrição enviada com sucesso!" com "Maria da Silva" | FR-007, FR-008, FR-010 |
| 5 | Repetir 1–4 só com teclado (Tab/Enter) e com leitor de tela | erros e confirmação anunciados; foco visível | FR-009, FR-012 |
| 6 | Acionar "Nova inscrição" | formulário vazio reaparece | FR-011 |

Dados de exemplo são fictícios (CPFs gerados apenas para teste).
