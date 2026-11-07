# Quickstart: validar a feature 001-validacao-cpf

**Spec Version**: 2

## Pré-requisitos

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

## Verificação automática

```bash
python evospec.py validate          # governança: R1–R7 sem erros
python evospec.py verify --label 001 # testes de aceitação + axe-core
```

Resultado esperado: `001/FR-001` a `001/FR-006` passam; nenhuma regressão em relação à linha de
base; o axe-core é registrado, mas não substitui os testes (ver [research.md](./research.md), R3).

## Verificação manual com leitor de tela (SC-003)

1. Abra `/app/` com o NVDA e o Chrome.
2. Preencha nome e e-mail, digite `123.456.789-00` no CPF e acione "Continuar".
3. Esperado: o NVDA anuncia "CPF inválido. Digite os 11 números do CPF." e o foco fica no campo CPF,
   lido como inválido.
4. Corrija para `529.982.247-25` e acione "Continuar": a confirmação é exibida.

Contrato dos elementos verificados: [contracts/form-ui.md](./contracts/form-ui.md).
