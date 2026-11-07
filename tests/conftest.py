# @spec 001-inscricao-matricula@1.0.0
"""Fixtures de teste de aceitação: abre app/index.html em navegador headless."""
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

APP = (Path(__file__).resolve().parent.parent / "app" / "index.html").as_uri()


@pytest.fixture(scope="session")
def navegador():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="chrome")
        yield browser
        browser.close()


@pytest.fixture
def pagina(navegador):
    contexto = navegador.new_context()
    contexto.set_default_timeout(2000)
    page = contexto.new_page()
    page.goto(APP)
    yield page
    contexto.close()
