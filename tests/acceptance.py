"""Testes de aceitação ligados aos critérios das especificações.

Cada teste declara o critério que verifica com @criterion("AC-xx.y").
Os testes são escritos a partir dos critérios aprovados, e não pelo agente
que implementa a mudança (verificação independente).
"""

CRITERIA = {}

CPF_INVALIDO = "123.456.789-00"
CPF_VALIDO = "529.982.247-25"


def criterion(ac_id):
    def wrap(fn):
        CRITERIA.setdefault(ac_id, []).append(fn)
        return fn
    return wrap


def preencher(page, cpf):
    page.fill("#nome", "Maria da Silva")
    page.fill("#cpf", cpf)
    page.fill("#email", "maria@exemplo.com")
    page.get_by_role("button", name="Continuar").click()


@criterion("AC-04.1")
def cpf_invalido_bloqueia_envio(page):
    preencher(page, CPF_INVALIDO)
    assert page.locator("#confirmacao").is_hidden(), "inscrição foi enviada com CPF inválido"


@criterion("AC-04.2")
def cpf_invalido_exibe_mensagem(page):
    preencher(page, CPF_INVALIDO)
    erro = page.get_by_text("CPF inválido")
    assert erro.count() > 0 and erro.first.is_visible(), "mensagem de erro não exibida"


@criterion("AC-04.3")
def cpf_valido_envia(page):
    preencher(page, CPF_VALIDO)
    assert page.locator("#confirmacao").is_visible(), "inscrição válida não foi enviada"


@criterion("AC-06.1")
def dados_preservados_apos_erro(page):
    preencher(page, CPF_INVALIDO)
    valores = {c: page.input_value(f"#{c}") for c in ("nome", "cpf", "email")}
    esperado = {"nome": "Maria da Silva", "cpf": CPF_INVALIDO, "email": "maria@exemplo.com"}
    assert valores == esperado, f"dados alterados após erro: {valores}"
