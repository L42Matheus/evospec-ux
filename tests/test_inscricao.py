# @spec 001-inscricao-matricula@1.0.0
"""Testes de aceitação do fluxo do formulário de inscrição.

Cobrem FR-001 e FR-004 a FR-012. Escritos a partir de spec.md e contracts/ui-contract.md
antes da implementação. Dados fictícios.
"""
import re

import pytest

NOME = "Maria da Silva"
CPF_VALIDO = "529.982.247-25"
CPF_DV_ERRADO = "529.982.247-24"
EMAIL = "maria@exemplo.com"

MSG_CPF = "CPF inválido. Verifique os números digitados."
MSG_NOME_VAZIO = "Informe seu nome completo."
MSG_CPF_VAZIO = "Informe seu CPF."
MSG_EMAIL_VAZIO = "Informe seu e-mail."
MSG_EMAIL_FORMATO = "Informe um e-mail válido, por exemplo nome@dominio.com."
MSG_CONFIRMACAO = "Inscrição enviada com sucesso!"


def preencher(pagina, nome=NOME, cpf=CPF_VALIDO, email=EMAIL):
    pagina.fill("#nome", nome)
    pagina.fill("#cpf", cpf)
    pagina.fill("#email", email)


def continuar(pagina):
    pagina.click("#continuar")


def enviadas(pagina):
    return pagina.evaluate("() => window.inscricoesEnviadas")


def foco_id(pagina):
    return pagina.evaluate("() => document.activeElement && document.activeElement.id")


def texto(pagina, seletor):
    return pagina.locator(seletor).inner_text().strip()


# ---------------------------------------------------------------- US1


def test_fr001_formulario_tem_campos_rotulados_e_botao_continuar(pagina):
    """FR-001: campos Nome completo, CPF e E-mail com rótulos associados e botão Continuar."""
    assert pagina.get_by_label("Nome completo").get_attribute("id") == "nome"
    assert pagina.get_by_label("CPF", exact=True).get_attribute("id") == "cpf"
    assert pagina.get_by_label("E-mail").get_attribute("id") == "email"
    botao = pagina.get_by_role("button", name="Continuar")
    assert botao.is_visible()
    assert botao.get_attribute("type") == "submit"
    assert pagina.locator("form#form-inscricao").get_attribute("novalidate") is not None


@pytest.mark.parametrize("cpf", [CPF_VALIDO, "52998224725"])
def test_fr007_envia_com_dados_validos(pagina, cpf):
    """FR-007: com todos os campos válidos, a inscrição é enviada (1 registro)."""
    assert enviadas(pagina) == []
    preencher(pagina, cpf=cpf)
    continuar(pagina)
    registros = enviadas(pagina)
    assert len(registros) == 1
    r = registros[0]
    assert r["nome"] == NOME
    assert r["cpf"] == "52998224725"
    assert r["email"] == EMAIL
    assert r["situacao"] == "enviada"
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", r["enviadaEm"])


def test_fr007_dispara_evento_de_envio(pagina):
    """FR-007: o envio é observável pelo evento inscricao:enviada."""
    pagina.evaluate(
        "() => { window.__evt = null; document.addEventListener('inscricao:enviada',"
        " e => { window.__evt = e.detail; }); }"
    )
    preencher(pagina, nome="  " + NOME + "  ", email=" " + EMAIL + " ")
    continuar(pagina)
    detalhe = pagina.evaluate("() => window.__evt")
    assert detalhe["nome"] == NOME  # espaços nas extremidades desconsiderados
    assert detalhe["email"] == EMAIL


def test_fr008_confirmacao_exibe_nome(pagina):
    """FR-008: após o envio, aparece a confirmação com o nome do estudante."""
    assert not pagina.locator("#confirmacao").is_visible()
    preencher(pagina)
    continuar(pagina)
    assert pagina.locator("#confirmacao").is_visible()
    assert texto(pagina, "#confirmacao-titulo") == MSG_CONFIRMACAO
    assert NOME in texto(pagina, "#confirmacao")
    assert not pagina.locator("#form-inscricao").is_visible()


def test_fr009_confirmacao_anunciada_e_focada(pagina):
    """FR-009: a confirmação fica em região de status e recebe o foco."""
    assert pagina.locator("#confirmacao").get_attribute("role") == "status"
    preencher(pagina)
    continuar(pagina)
    assert foco_id(pagina) == "confirmacao-titulo"


def test_fr011_sem_envio_duplicado(pagina):
    """FR-011: a mesma inscrição não é enviada de novo enquanto a confirmação está exibida."""
    preencher(pagina)
    pagina.locator("#cpf").focus()
    pagina.keyboard.press("Enter")
    pagina.keyboard.press("Enter")
    pagina.evaluate("() => document.getElementById('form-inscricao').requestSubmit()")
    assert len(enviadas(pagina)) == 1
    # Nova inscrição reexibe o formulário vazio
    pagina.click("#nova-inscricao")
    assert pagina.locator("#form-inscricao").is_visible()
    assert not pagina.locator("#confirmacao").is_visible()
    for campo in ("#nome", "#cpf", "#email"):
        assert pagina.input_value(campo) == ""
    assert foco_id(pagina) == "nome"
    preencher(pagina, nome="João Souza", cpf="111.444.777-35", email="joao@exemplo.com")
    continuar(pagina)
    assert len(enviadas(pagina)) == 2


# ---------------------------------------------------------------- US2


@pytest.mark.parametrize("cpf", [CPF_DV_ERRADO, "111.111.111-11", "000.000.000-00", "123.456.789"])
def test_fr004_cpf_invalido_nao_envia_e_mostra_erro(pagina, cpf):
    """FR-004: CPF inválido impede o envio e mostra a mensagem junto ao campo CPF."""
    preencher(pagina, cpf=cpf)
    continuar(pagina)
    assert enviadas(pagina) == []
    assert texto(pagina, "#cpf-erro") == MSG_CPF
    assert pagina.locator("#cpf-erro").is_visible()
    assert pagina.get_attribute("#cpf", "aria-invalid") == "true"
    assert "cpf-erro" in pagina.get_attribute("#cpf", "aria-describedby").split()
    assert foco_id(pagina) == "cpf"
    assert not pagina.locator("#confirmacao").is_visible()


def test_fr010_corrigir_cpf_remove_erro_e_envia(pagina):
    """FR-010: corrigir o CPF e continuar remove o erro e envia."""
    preencher(pagina, cpf=CPF_DV_ERRADO)
    continuar(pagina)
    assert texto(pagina, "#cpf-erro") == MSG_CPF
    pagina.fill("#cpf", CPF_VALIDO)
    continuar(pagina)
    assert len(enviadas(pagina)) == 1
    assert pagina.locator("#confirmacao").is_visible()
    assert pagina.get_attribute("#cpf", "aria-invalid") in (None, "false")
    assert texto(pagina, "#cpf-erro") == ""


def test_fr010_erro_removido_so_dos_campos_corrigidos(pagina):
    """FR-010: só as mensagens de campos que ficaram válidos são removidas."""
    continuar(pagina)  # tudo vazio
    pagina.fill("#nome", NOME)
    continuar(pagina)
    assert texto(pagina, "#nome-erro") == ""
    assert pagina.get_attribute("#nome", "aria-invalid") in (None, "false")
    assert texto(pagina, "#cpf-erro") == MSG_CPF_VAZIO
    assert texto(pagina, "#email-erro") == MSG_EMAIL_VAZIO


# ---------------------------------------------------------------- US3


def test_fr005_campos_vazios_nao_enviam(pagina):
    """FR-005: campos vazios impedem o envio e exibem mensagens específicas."""
    continuar(pagina)
    assert enviadas(pagina) == []
    assert texto(pagina, "#nome-erro") == MSG_NOME_VAZIO
    assert texto(pagina, "#cpf-erro") == MSG_CPF_VAZIO
    assert texto(pagina, "#email-erro") == MSG_EMAIL_VAZIO


def test_fr005_nome_so_com_espacos_e_vazio(pagina):
    """FR-005: nome apenas com espaços é tratado como vazio."""
    preencher(pagina, nome="    ")
    continuar(pagina)
    assert enviadas(pagina) == []
    assert texto(pagina, "#nome-erro") == MSG_NOME_VAZIO
    assert texto(pagina, "#cpf-erro") == ""
    assert texto(pagina, "#email-erro") == ""


@pytest.mark.parametrize("email", ["maria.exemplo.com", "maria@exemplo", "maria @exemplo.com", "@exemplo.com"])
def test_fr006_email_invalido_nao_envia(pagina, email):
    """FR-006: e-mail com formato inválido impede o envio."""
    preencher(pagina, email=email)
    continuar(pagina)
    assert enviadas(pagina) == []
    assert texto(pagina, "#email-erro") == MSG_EMAIL_FORMATO
    assert pagina.get_attribute("#email", "aria-invalid") == "true"
    assert foco_id(pagina) == "email"


def test_fr009_foco_no_primeiro_erro_e_aria_invalid(pagina):
    """FR-009: com vários erros, foco no primeiro inválido; campos marcados; resumo anunciado."""
    preencher(pagina, nome="", cpf="111.111.111-11", email="x")
    continuar(pagina)
    assert foco_id(pagina) == "nome"
    for campo in ("nome", "cpf", "email"):
        assert pagina.get_attribute(f"#{campo}", "aria-invalid") == "true"
        assert f"{campo}-erro" in pagina.get_attribute(f"#{campo}", "aria-describedby").split()
    resumo = pagina.locator("#resumo-erros")
    assert resumo.get_attribute("role") == "alert"
    assert resumo.inner_text().strip() != ""
    # Corrigir só o nome: foco vai para o CPF
    pagina.fill("#nome", NOME)
    continuar(pagina)
    assert foco_id(pagina) == "cpf"


def test_fr009_resumo_limpo_apos_envio(pagina):
    """FR-009: o resumo de erros some quando a inscrição é enviada."""
    continuar(pagina)
    preencher(pagina)
    continuar(pagina)
    assert pagina.locator("#resumo-erros").inner_text().strip() == ""


# ---------------------------------------------------------------- Transversal


def test_fr012_operavel_por_teclado(pagina):
    """FR-012: Tab percorre nome, CPF, e-mail e Continuar; o fluxo completo funciona só com teclado."""
    pagina.locator("body").focus()
    ordem = []
    for _ in range(4):
        pagina.keyboard.press("Tab")
        ordem.append(foco_id(pagina))
    assert ordem == ["nome", "cpf", "email", "continuar"]
    pagina.locator("#nome").focus()
    pagina.keyboard.type(NOME)
    pagina.keyboard.press("Tab")
    pagina.keyboard.type(CPF_VALIDO)
    pagina.keyboard.press("Tab")
    pagina.keyboard.type(EMAIL)
    pagina.keyboard.press("Tab")
    pagina.keyboard.press("Enter")
    assert len(enviadas(pagina)) == 1
    pagina.keyboard.press("Tab")
    assert foco_id(pagina) == "nova-inscricao"


def _luminancia(rgb):
    def canal(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (canal(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contraste(a, b):
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


CORES_JS = """
sel => {
  const el = document.querySelector(sel);
  const rgb = s => (s.match(/[\\d.]+/g) || []).slice(0, 4).map(Number);
  let fundo = el, bg;
  while (fundo) {
    bg = getComputedStyle(fundo).backgroundColor;
    const v = rgb(bg);
    if (v.length === 3 || (v.length === 4 && v[3] > 0)) break;
    fundo = fundo.parentElement;
  }
  return {fg: rgb(getComputedStyle(el).color).slice(0, 3),
          bg: fundo ? rgb(bg).slice(0, 3) : [255, 255, 255]};
}
"""


def test_fr012_contraste_e_foco_visivel(pagina):
    """FR-012: contraste de texto >= 4.5:1 (WCAG 1.4.3) e indicador de foco visível (2.4.7)."""
    continuar(pagina)  # exibe mensagens de erro
    for sel in ["h1", "label[for=nome]", "#cpf-dica", "#nome", "#continuar", "#nome-erro", "#resumo-erros"]:
        cores = pagina.evaluate(CORES_JS, sel)
        assert _contraste(cores["fg"], cores["bg"]) >= 4.5, sel
    for sel in ["#nome", "#cpf", "#email", "#continuar"]:
        pagina.locator(sel).focus()
        pagina.keyboard.press("Shift+Tab")
        pagina.keyboard.press("Tab")
        estilo = pagina.evaluate(
            "s => { const c = getComputedStyle(document.querySelector(s));"
            " return [c.outlineStyle, parseFloat(c.outlineWidth)]; }",
            sel,
        )
        assert estilo[0] != "none" and estilo[1] >= 2, sel
    caixa = pagina.locator("#continuar").bounding_box()
    assert caixa["width"] >= 24 and caixa["height"] >= 24
