# @spec 001-inscricao-matricula@1.0.0
"""Testes de aceitação da validação de CPF (FR-002, FR-003).

Escritos a partir de spec.md e contracts/ui-contract.md antes da implementação.
CPFs usados são fictícios, gerados apenas para teste.
"""
import pytest

CPFS_VALIDOS = [
    "529.982.247-25",
    "52998224725",
    "111.444.777-35",
    "123.456.789-09",
    " 529 982 247 25 ",
    "529a982b247c25",  # letras são ignoradas
]


def validar(pagina, valor):
    return pagina.evaluate("v => window.validarCPF(v)", valor)


@pytest.mark.parametrize("cpf", CPFS_VALIDOS)
def test_fr002_cpfs_validos_aceitos(pagina, cpf):
    """FR-002: CPF com dígitos verificadores corretos é aceito, com ou sem pontuação."""
    assert validar(pagina, cpf) is True


@pytest.mark.parametrize("cpf", ["529.982.247-24", "529.982.247-15", "111.444.777-36", "12345678900"])
def test_fr002_digito_verificador_incorreto_rejeitado(pagina, cpf):
    """FR-002: CPF com dígito verificador incorreto é rejeitado."""
    assert validar(pagina, cpf) is False


@pytest.mark.parametrize("cpf", ["", "123.456.789", "5299822472", "529982247250", "abc"])
def test_fr002_tamanho_diferente_de_11_rejeitado(pagina, cpf):
    """FR-002: CPF precisa ter exatamente 11 dígitos."""
    assert validar(pagina, cpf) is False


@pytest.mark.parametrize("digito", list("0123456789"))
def test_fr003_todos_digitos_iguais_rejeitados(pagina, digito):
    """FR-003: CPF com os 11 dígitos iguais é inválido (com e sem máscara)."""
    d = digito * 11
    assert validar(pagina, d) is False
    assert validar(pagina, f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}") is False
