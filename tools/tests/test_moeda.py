"""Jogo da moeda da Aula 02: celular (a tela do quiz, quiz/index.html) e slide (data-moeda).

O celular entra no quiz uma vez; quando o slide da moeda monta, ele abre no quiz
a rodada "moeda" e o celular troca de tela sozinho, com o nome do quiz.

Modo de memória (?quiz-demo=1): o slide e os celulares, abertos no mesmo
contexto do navegador, conversam por localStorage e BroadcastChannel. A
identidade do jogador fica no sessionStorage da aba, então cada aba é um
jogador diferente.
"""
import os
import statistics
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

SESSAO = "m08-aula02-2026-11-05"


@pytest.fixture
def sala():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        erros = []
        contexto.on("weberror", lambda e: erros.append(str(e.error)))
        try:
            yield contexto, "http://127.0.0.1:%d" % porta, erros
        finally:
            navegador.close()
    httpd.shutdown()


def _slide(contexto, base, chave=True):
    page = contexto.new_page()
    url = "%s/tools/tests/fixture_moeda.html?quiz-demo=1" % base
    page.goto(url + ("&quiz-chave=teste" if chave else ""), wait_until="load")
    page.evaluate("localStorage.removeItem('inteli-aula02-demo')")
    if not chave:
        page.evaluate("localStorage.removeItem('inteli-quiz-chave')")
    page.reload(wait_until="load")
    page.wait_for_selector("[data-moeda][data-pronto='sim']")
    return page


LIMPA_QUIZ = ("Object.keys(localStorage).filter(k => k.startsWith('inteli-quiz-eu') || "
              "k === 'inteli-quiz-perfil').forEach(k => localStorage.removeItem(k))")


def _celular(contexto, base, apelido):
    """Entra no quiz como um aluno novo e espera a tela trocar para a moeda, sem outro QR."""
    page = contexto.new_page()
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto("%s/quiz/?s=%s&quiz-demo=1" % (base, SESSAO), wait_until="load")
    page.evaluate(LIMPA_QUIZ)
    page.reload(wait_until="load")
    page.fill("#nome", apelido + " Teste")
    page.click(".avatar[data-avatar=star]")
    page.click(".principal")
    page.wait_for_selector(".aluno[data-estado='moeda'] .moeda-aluno[data-estado='jogar']", timeout=10000)
    return page


def _liberar(slide, rodada):
    slide.click("[data-moeda] .moeda-liberar")
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-rodada').dataset.rodada === '%d'" % rodada)


def _jogar_tudo(celular, n):
    """Joga as rodadas 1 a n, esperando o celular ver cada uma liberada; devolve os saldos."""
    for feitas in range(n):
        celular.wait_for_selector(".jogar:not([disabled])")
        celular.click(".jogar")
        celular.wait_for_function("document.querySelectorAll('.historico li').length > %d" % feitas)
    return [float(li.get_attribute("data-saldo")) for li in celular.locator(".historico li").all()]


def test_tres_jogadores_dez_rodadas_e_slide_mostra_media_e_mediana(sala):
    contexto, base, erros = sala
    slide = _slide(contexto, base)
    celulares = [_celular(contexto, base, n) for n in ("Ana", "Bia", "Caio")]
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-jogadores').dataset.n === '3'")
    for r in range(1, 11):
        _liberar(slide, r)
        for c in celulares:
            c.wait_for_selector(".jogar:not([disabled])")
            c.click(".jogar")
            c.wait_for_function("document.querySelectorAll('.historico li').length === %d" % r)
    finais = [float(c.locator(".historico li").last.get_attribute("data-saldo")) for c in celulares]
    media = round(sum(finais) / 3, 2)
    mediana = round(statistics.median(finais), 2)
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-media').dataset.valor === '%.2f'" % media)
    assert slide.locator("[data-moeda] .moeda-mediana").get_attribute("data-valor") == "%.2f" % mediana
    assert not erros


def test_saldo_aplica_mais_50_ou_menos_40(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    c = _celular(contexto, base, "Davi")
    for r in range(1, 7):
        _liberar(slide, r)
    saldos = [100.0] + _jogar_tudo(c, 6)
    assert len(saldos) == 7
    for antes, depois in zip(saldos, saldos[1:]):
        assert depois in (round(antes * 1.5, 2), round(antes * 0.6, 2)), (antes, depois)


def test_atrasado_joga_rodadas_liberadas_em_sequencia(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    for r in range(1, 5):
        _liberar(slide, r)
    c = _celular(contexto, base, "Eva")
    saldos = _jogar_tudo(c, 4)
    c.wait_for_timeout(300)
    assert c.locator(".jogar").is_disabled()
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-media').dataset.valor === '%.2f'"
                            % saldos[-1])


def test_recarregar_mantem_jogador_e_nao_rejoga(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    _liberar(slide, 1)
    _liberar(slide, 2)
    c = _celular(contexto, base, "Fabi")
    saldos = _jogar_tudo(c, 2)
    c.reload(wait_until="load")
    c.wait_for_selector(".historico li")
    assert [float(li.get_attribute("data-saldo")) for li in c.locator(".historico li").all()] == saldos
    assert c.locator(".jogar").is_disabled()
    _liberar(slide, 3)
    c.wait_for_selector(".jogar:not([disabled])")
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-jogadores').dataset.n === '1'")


def test_sem_chave_nao_ha_botao_de_liberar(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base, chave=False)
    assert slide.locator("[data-moeda] .moeda-liberar").is_hidden()


def test_zerar_pede_confirmacao_apaga_o_jogo_e_celular_volta_para_entrada(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    _liberar(slide, 1)
    c = _celular(contexto, base, "Gabi")
    _jogar_tudo(c, 1)
    slide.click("[data-moeda] .moeda-zerar")
    slide.wait_for_timeout(300)
    assert slide.locator("[data-moeda] .moeda-rodada").get_attribute("data-rodada") == "1"
    slide.click("[data-moeda] .moeda-zerar")
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-jogadores').dataset.n === '0'")
    assert slide.locator("[data-moeda] .moeda-media").get_attribute("data-valor") == ""
    # Vindo do quiz, o celular entra de novo sozinho, com o histórico zerado.
    c.wait_for_function("document.querySelectorAll('.historico li').length === 0", timeout=8000)
    slide.wait_for_function("document.querySelector('[data-moeda] .moeda-jogadores').dataset.n === '1'")


def test_celular_do_quiz_troca_para_a_moeda_e_volta_quando_o_slide_fecha(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    c = _celular(contexto, base, "Hugo")
    assert c.locator(".aluno-quem-nome").inner_text().startswith("Hugo")
    slide.evaluate("IntelIQuizDados.criar().fechar('teste', '%s')" % SESSAO)
    c.wait_for_selector(".aluno[data-estado='esperar']", timeout=8000)


def test_moeda_em_svg_e_trilha_marcam_cada_rodada(sala):
    contexto, base, _ = sala
    slide = _slide(contexto, base)
    for r in range(1, 5):
        _liberar(slide, r)
    c = _celular(contexto, base, "Iara")
    _jogar_tudo(c, 3)
    lados = [li.get_attribute("class") for li in c.locator(".historico li").all()]
    marcas = [m.get_attribute("class") for m in c.locator(".moeda-trilha .mt").all()]
    assert len(marcas) == 10
    assert [("mt mt-cara" if l == "cara" else "mt mt-coroa") for l in lados] == marcas[:3]
    assert marcas[3] == "mt mt-liberada" and marcas[4] == "mt mt-vazia"
    assert c.locator(".moeda-giro").get_attribute("data-lado") == lados[-1]
    assert c.locator(".moeda-face").count() == 2
