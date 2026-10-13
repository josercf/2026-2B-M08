"""Legibilidade em projeção, botão de exportar e vídeo no PDF, medidos no navegador.

As revisões das seis aulas em 13/10/2026 acharam o mesmo defeito do tema em
todos os decks: texto que o aluno precisa ler (feedback do quiz, opções da
escolha, botões e rótulos dos widgets, código, cabeçalho de tabela) saía no
token complementar de 14px, abaixo do piso de 18px da inteli-deck-design,
seção 3. O botão "Exportar PDF" cobria o número do rodapé, e o <video> saía
vazio no PDF. O piso é conferido por getComputedStyle, nunca a olho.
"""
import glob
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

DECKS = sorted(
    os.path.relpath(c, RAIZ) for c in glob.glob(os.path.join(RAIZ, "aulas", "*.html"))
)

# Texto de leitura: piso de 18px. Código e tabela densa: piso de 16px, porque
# um bloco de 18 linhas em 18px não cabe junto do título em 720px.
PISO_LEITURA = 18
PISO_DENSO = 16
LEITURA = [
    ".quiz-container .quiz-feedback",
    ".escolha-opcoes li",
    ".widget-controles button",
]
DENSO = [
    ".code-compact",
    ".reveal .tabela-leitura th",
    ".data-table",
    ".widget-controles .widget-rotulo",
]


@pytest.fixture(scope="module")
def navegador():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        nav = p.chromium.launch()
        try:
            yield nav, "http://127.0.0.1:%d/" % porta
        finally:
            nav.close()
    httpd.shutdown()


def _menores(page, seletores, piso):
    return page.evaluate(
        """([seletores, piso]) => {
            const ruins = [];
            for (const s of seletores) {
                for (const e of document.querySelectorAll(s)) {
                    const px = parseFloat(getComputedStyle(e).fontSize);
                    if (px < piso) ruins.push(s + ' = ' + px + 'px');
                }
            }
            return [...new Set(ruins)];
        }""",
        [seletores, piso],
    )


@pytest.mark.parametrize("deck", DECKS)
def test_texto_de_leitura_respeita_o_piso_de_projecao(navegador, deck):
    nav, base = navegador
    page = nav.new_page(viewport={"width": 1280, "height": 720})
    try:
        page.goto(base + deck, wait_until="load")
        assert _menores(page, LEITURA, PISO_LEITURA) == []
        assert _menores(page, DENSO, PISO_DENSO) == []
    finally:
        page.close()


@pytest.mark.parametrize("deck", DECKS)
def test_botao_de_exportar_nao_cobre_rodape_titulo_nem_marca(navegador, deck):
    nav, base = navegador
    page = nav.new_page(viewport={"width": 1280, "height": 720})
    try:
        page.goto(base + deck, wait_until="load")
        page.wait_for_selector(".print-button")
        # A capa não tem rodapé: vai para o primeiro slide que tem.
        page.wait_for_function("() => window.Reveal && Reveal.isReady()")
        page.evaluate(
            """() => {
                const i = Reveal.getSlides().findIndex(s => s.querySelector('.slide-footer'));
                Reveal.slide(i);
            }"""
        )
        page.wait_for_selector("section.present .slide-footer")
        botao = page.eval_on_selector(".print-button", "e => e.getBoundingClientRect().toJSON()")
        # Rodapé (número da página), área do título e marca: o botão cobriu o
        # primeiro no canto inferior direito e o segundo no superior esquerdo.
        rodapes = page.evaluate(
            """() => [...document.querySelectorAll(
                    'section.present .slide-footer, section.present .slide-title-area, '
                    + 'section.present .inteli-logo-header, section.present .accent-bar')]
                     .map(e => e.getBoundingClientRect().toJSON())"""
        )
        assert rodapes
        for r in rodapes:
            sobrepoe = not (
                botao["right"] <= r["left"] or botao["left"] >= r["right"]
                or botao["bottom"] <= r["top"] or botao["top"] >= r["bottom"]
            )
            assert not sobrepoe, (botao, r)
    finally:
        page.close()


@pytest.mark.parametrize("deck", DECKS)
def test_pdf_troca_cada_video_pelo_poster(navegador, deck):
    nav, base = navegador
    page = nav.new_page(viewport={"width": 1280, "height": 720})
    try:
        page.goto(base + deck, wait_until="load")
        posteres = page.evaluate(
            "() => [...document.querySelectorAll('video')].map(v => v.getAttribute('poster'))"
        )
        page.goto(base + deck + "?print-pdf", wait_until="load")
        page.wait_for_selector(".reveal .slides")
        assert page.evaluate("() => document.querySelectorAll('video').length") == 0
        imagens = page.evaluate(
            "() => [...document.querySelectorAll('img.video-poster')].map(i => i.getAttribute('src'))"
        )
        assert imagens == posteres
    finally:
        page.close()


@pytest.mark.parametrize("deck", DECKS)
def test_pdf_imprime_um_slide_por_pagina_com_fragments_revelados(deck):
    # Sem a opção, o Reveal imprime cada estado de fragment numa página, e o PDF
    # da Aula 06 saía com 26 páginas para 25 slides (medido em 13/10/2026).
    html = open(os.path.join(RAIZ, deck), encoding="utf-8").read()
    assert "pdfSeparateFragments: false" in html


@pytest.mark.parametrize("deck", DECKS)
def test_divisor_e_encerramento_ficam_centralizados_no_pdf(navegador, deck):
    # No modo ?print-pdf o Reveal reescreve o display da section, e o título
    # do divisor de seção subia para o topo da página impressa (PDF real da
    # Aula 01, 13/10/2026). O centro do bloco de texto precisa ficar no meio.
    nav, base = navegador
    page = nav.new_page(viewport={"width": 1280, "height": 720})
    try:
        page.goto(base + deck + "?print-pdf", wait_until="load")
        page.wait_for_selector("html.print-pdf .reveal .slides section")
        desvios = page.evaluate(
            """() => [...document.querySelectorAll(
                    '.reveal .slides section.section-slide, .reveal .slides section.end-slide')]
                .map(s => {
                    const caixa = s.getBoundingClientRect();
                    const filhos = [...s.children].filter(e => getComputedStyle(e).position !== 'absolute');
                    const topo = Math.min(...filhos.map(e => e.getBoundingClientRect().top));
                    const base = Math.max(...filhos.map(e => e.getBoundingClientRect().bottom));
                    return Math.abs((topo + base) / 2 - (caixa.top + caixa.height / 2));
                })"""
        )
        if not desvios:
            pytest.skip("deck sem divisor nem encerramento")
        assert max(desvios) < 60, desvios
    finally:
        page.close()
