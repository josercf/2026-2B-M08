"""Estado depois da interação do cronômetro e da escolha, medido no navegador.

O check_slides.py mede o deck sem clicar em nada (inteli-deck-design, seção 8.4).
Este teste clica e compara getComputedStyle, porque classe de estado que perde
na especificidade muda o DOM e não muda a tela (seção 8.1).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def deck():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1280, "height": 720})
        try:
            yield page, "http://127.0.0.1:%d/aulas/_fixture-tema.html" % porta
        finally:
            navegador.close()
    httpd.shutdown()


def _ir(deck, slide):
    # A query string força documento novo: sem ela, trocar só o hash mantém o
    # estado da interação do teste anterior.
    page, url = deck
    page.goto("%s?teste=%s#/%s" % (url, slide, slide), wait_until="load")
    page.wait_for_selector("section#%s.present" % slide)
    return page


def test_cronometro_conta_ate_zero_e_marca_esgotado(deck):
    page = _ir(deck, "cronometro")
    tempo = "#cronometro-fixture .cronometro-tempo"
    page.wait_for_selector(tempo)
    assert page.inner_text(tempo) == "00:03"
    page.click("#cronometro-fixture .cronometro-play")
    page.wait_for_function(
        "() => document.querySelector('#cronometro-fixture').classList.contains('esgotado')",
        timeout=8000,
    )
    assert page.inner_text(tempo) == "00:00"
    borda = page.eval_on_selector("#cronometro-fixture", "e => getComputedStyle(e).borderTopColor")
    assert borda == "rgb(255, 69, 69)"  # --seg-destaque


def test_escolha_errada_marca_a_errada_e_revela_a_certa(deck):
    page = _ir(deck, "escolha")
    opcoes = "#escolha-fixture .escolha-opcoes li"
    repouso = page.eval_on_selector(opcoes + ":nth-child(3)", "e => getComputedStyle(e).backgroundColor")
    page.click(opcoes + ":nth-child(1)")
    classes = page.eval_on_selector_all(opcoes, "els => els.map(e => e.className)")
    assert "errada" in classes[0]
    assert "revelada" in classes[2]
    revelada = page.eval_on_selector(opcoes + ":nth-child(3)", "e => getComputedStyle(e).backgroundColor")
    assert revelada != repouso


def test_escolha_certa_pinta_a_opcao(deck):
    page = _ir(deck, "escolha")
    opcoes = "#escolha-fixture-certa .escolha-opcoes li"
    repouso = page.eval_on_selector(opcoes + ":nth-child(2)", "e => getComputedStyle(e).backgroundColor")
    page.click(opcoes + ":nth-child(1)")
    assert "certa" in page.eval_on_selector(opcoes + ":nth-child(1)", "e => e.className")
    certa = page.eval_on_selector(opcoes + ":nth-child(1)", "e => getComputedStyle(e).backgroundColor")
    assert certa != repouso
