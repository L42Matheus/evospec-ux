"""Testes de aceitação ligados aos critérios das especificações.

Cada teste declara o requisito do Spec Kit que verifica com @criterion("<feature>/FR-NNN"),
por exemplo @criterion("001/FR-004") para o FR-004 de specs/001-validacao-cpf/spec.md.
Os testes são escritos a partir dos critérios aprovados, e não pelo agente
que implementa a mudança (verificação independente).
"""

import re

CRITERIA = {}

CPF_INVALIDO = "123.456.789-00"
CPF_VALIDO = "529.982.247-25"


def criterion(ac_id):
    def wrap(fn):
        CRITERIA.setdefault(ac_id, []).append(fn)
        return fn
    return wrap


def axe_setup(page):
    """Estado da página para a varredura do axe-core: erro de CPF exibido."""
    page.fill("#cpf", "000")
    page.get_by_role("button", name="Continuar").click()


def preencher(page, cpf):
    page.fill("#nome", "Maria da Silva")
    page.fill("#cpf", cpf)
    page.fill("#email", "maria@exemplo.com")
    page.get_by_role("button", name="Continuar").click()


@criterion("001/FR-001")
def cpf_invalido_bloqueia_envio(page):
    preencher(page, CPF_INVALIDO)
    assert page.locator("#confirmacao").is_hidden(), "inscrição foi enviada com CPF inválido"


@criterion("001/FR-002")
def cpf_invalido_exibe_mensagem(page):
    preencher(page, CPF_INVALIDO)
    erro = page.get_by_text("CPF inválido")
    assert erro.count() > 0 and erro.first.is_visible(), "mensagem de erro não exibida"


@criterion("001/FR-003")
def cpf_valido_envia(page):
    preencher(page, CPF_VALIDO)
    assert page.locator("#confirmacao").is_visible(), "inscrição válida não foi enviada"


# ---- Requisitos FR-004 a FR-006 da 001-validacao-cpf@2 (CR-001, evidência EVD-17),
# escritos pelo verificador antes da implementação

@criterion("001/FR-004")
def foco_vai_para_cpf(page):
    preencher(page, CPF_INVALIDO)
    foco = page.evaluate("document.activeElement && document.activeElement.id")
    assert foco == "cpf", f"foco está em '{foco}', esperado 'cpf'"


@criterion("001/FR-005")
def cpf_marcado_invalido_com_descricao(page):
    from playwright.sync_api import expect
    preencher(page, CPF_INVALIDO)
    campo = page.get_by_role("textbox", name="CPF")
    assert campo.get_attribute("aria-invalid") == "true", "campo CPF sem aria-invalid=true"
    # descrição acessível calculada pela árvore de acessibilidade do navegador
    expect(campo).to_have_accessible_description(re.compile("CPF inválido"), timeout=1000)


@criterion("001/FR-006")
def mensagem_em_regiao_viva(page):
    regioes = page.evaluate(
        "[...document.querySelectorAll('[role=alert],[aria-live=polite],[aria-live=assertive]')].map(e => e.id || e.outerHTML.slice(0, 40))")
    assert regioes, "nenhuma região viva presente no carregamento da página"
    preencher(page, CPF_INVALIDO)
    textos = page.evaluate(
        "[...document.querySelectorAll('[role=alert],[aria-live=polite],[aria-live=assertive]')].map(e => e.textContent)")
    assert any("CPF inválido" in t for t in textos), "mensagem de erro não foi inserida em região viva"


@criterion("002/FR-001")
def dados_preservados_apos_erro(page):
    preencher(page, CPF_INVALIDO)
    valores = {c: page.input_value(f"#{c}") for c in ("nome", "cpf", "email")}
    esperado = {"nome": "Maria da Silva", "cpf": CPF_INVALIDO, "email": "maria@exemplo.com"}
    assert valores == esperado, f"dados alterados após erro: {valores}"
