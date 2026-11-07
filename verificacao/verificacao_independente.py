import re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
URL = (Path(__file__).resolve().parents[1] / 'app' / 'index.html').as_uri()
AXE = str(Path(__file__).resolve().parent / 'axe.min.js')
INV, VAL = "123.456.789-00", "529.982.247-25"
def fill(pg, cpf):
    pg.fill("#nome","Maria da Silva"); pg.fill("#cpf",cpf); pg.fill("#email","maria@exemplo.com")
    pg.get_by_role("button", name="Continuar").click()
checks = {}
def check(name):
    def w(fn): checks[name]=fn; return fn
    return w
@check("bloqueia envio com CPF inválido")
def a(pg): fill(pg,INV); assert pg.locator("#confirmacao").is_hidden()
@check("mensagem de erro visível")
def b(pg): fill(pg,INV); assert pg.get_by_text("CPF inválido").first.is_visible()
@check("envia com CPF válido")
def c(pg): fill(pg,VAL); assert pg.locator("#confirmacao").is_visible()
@check("foco vai para o campo CPF")
def d(pg):
    fill(pg,INV); f=pg.evaluate("document.activeElement && document.activeElement.id"); assert f=="cpf", f"foco em '{f}'"
@check("campo CPF inválido com descrição acessível")
def e(pg):
    fill(pg,INV); cpf=pg.get_by_role("textbox", name=re.compile("^CPF")); assert cpf.get_attribute("aria-invalid")=="true"
    expect(cpf).to_have_accessible_description(re.compile("CPF inválido"), timeout=1000)
@check("mensagem em região viva presente desde o carregamento")
def f(pg):
    sel="[role=alert],[aria-live=polite],[aria-live=assertive]"
    assert pg.evaluate(f"document.querySelectorAll('{sel}').length")>0
    fill(pg,INV); t=pg.evaluate(f"[...document.querySelectorAll('{sel}')].map(e=>e.textContent)")
    assert any("CPF inválido" in x for x in t), t
@check("dados preservados após erro")
def g(pg):
    fill(pg,INV); v={k:pg.input_value(f"#{k}") for k in ("nome","cpf","email")}
    assert v=={"nome":"Maria da Silva","cpf":INV,"email":"maria@exemplo.com"}, v
with sync_playwright() as p:
    b_=p.chromium.launch(args=["--no-sandbox"]); ok=0
    for n,fn in checks.items():
        pg=b_.new_page(); pg.goto(URL)
        try: fn(pg); print("  PASSA ",n); ok+=1
        except Exception as ex: print("  FALHA ",n,"->",str(ex).splitlines()[0])
        pg.close()
    pg=b_.new_page(); pg.goto(URL); pg.fill("#cpf","000"); pg.get_by_role("button",name="Continuar").click()
    pg.add_script_tag(path=AXE)
    v=pg.evaluate("async()=>(await axe.run(document,{runOnly:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']})).violations.map(v=>v.id+' ('+v.impact+')')")
    print(f"  {ok}/{len(checks)} verificações; axe-core: {len(v)} violação(ões) {v}")
    # o que o leitor de tela recebe no erro: região viva e descrição do campo
    pg=b_.new_page(); pg.goto(URL); fill(pg,INV)
    print("  resumo role=alert:", repr(pg.inner_text('#resumo-erros')))
    print("  focado:", pg.evaluate("document.activeElement.id"), "| aria-describedby:", pg.get_attribute('#cpf','aria-describedby'))
    b_.close()
