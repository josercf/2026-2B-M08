"""Ampulheta e marco de troca de papel do cronômetro (pedido de 20/10/2026).

O relógio do Playwright avança o setInterval do cronômetro sem esperar os 12
minutos reais da prática.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")


def test_ampulheta_nasce_no_play_e_o_marco_avisa_a_troca_de_papel():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    try:
        with sync_api.sync_playwright() as p:
            navegador = p.chromium.launch()
            page = navegador.new_page(viewport={"width": 1280, "height": 720})
            erros = []
            page.on("pageerror", lambda e: erros.append(str(e)))
            page.clock.install()
            page.goto("http://127.0.0.1:%d/aulas/aula01.html#/pratica-coletor" % porta, wait_until="load")
            page.clock.run_for(1500)
            sel = "section#pratica-coletor"
            assert page.query_selector(sel + " .ampulheta") is None

            page.click("#cronometro-coletor .cronometro-play")
            page.clock.run_for(1100)
            assert page.eval_on_selector(sel + " .ampulheta", "e => e.classList.contains('ampulheta-visivel')")
            assert page.eval_on_selector(sel, "e => e.classList.contains('com-ampulheta')")

            # antes do marco nada pisca
            page.clock.run_for(5 * 60 * 1000)
            assert page.eval_on_selector_all(sel + " li.marco-alcancado", "l => l.length") == 0
            page.clock.run_for(60 * 1000)
            assert page.eval_on_selector_all(sel + " li.marco-alcancado", "l => l.map(e => e.dataset.marco)") == ["6"]
            assert "troquem de papel" in page.inner_text(sel + " .cronometro-marco")

            # metade do tempo: areia de cima pela metade
            altura = float(page.eval_on_selector(sel + " .ampulheta-areia-cima", "e => e.getAttribute('height')"))
            assert 30 < altura < 40

            page.clock.run_for(6 * 60 * 1000 + 1000)
            assert page.inner_text("#cronometro-coletor .cronometro-tempo") == "00:00"
            assert page.eval_on_selector(sel + " .ampulheta", "e => e.classList.contains('ampulheta-virada')")
            assert erros == []
            navegador.close()
    finally:
        httpd.shutdown()
