"""Quiz ao vivo da Aula 01 (slide #preparo e as quatro perguntas das visões).

Roda no modo de memória (?quiz-demo=1): o slide e as páginas de aluno, no
mesmo contexto do navegador, conversam por localStorage e BroadcastChannel,
como conversariam pelo Supabase. Cada aluno apaga a identidade guardada antes
de entrar, porque o contexto compartilha o armazenamento.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SESSAO = "m08-aula01-2026-10-20"
LIMPA = ("Object.keys(localStorage).filter(k => k.startsWith('inteli-quiz-eu') || "
         "k === 'inteli-quiz-perfil').forEach(k => localStorage.removeItem(k))")


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


def _deck(contexto, base, slide):
    page = contexto.new_page()
    page.goto("%s/aulas/aula01.html?quiz-demo=1&quiz-chave=teste#/%s" % (base, slide), wait_until="load")
    page.wait_for_selector("section#%s.present .quiz-vivo[data-fase='aberta']" % slide)
    return page


def _aluno(contexto, base, nome, avatar):
    page = contexto.new_page()
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto("%s/quiz/?s=%s&quiz-demo=1" % (base, SESSAO), wait_until="load")
    page.evaluate(LIMPA)
    page.reload(wait_until="load")
    page.fill("#nome", nome)
    page.click(".avatar[data-avatar=%s]" % avatar)
    page.click(".principal")
    return page


def _estado(page):
    return page.eval_on_selector("main", "e => e.dataset.estado")


def _esperar(page, estado):
    page.wait_for_function("e => document.querySelector('main').dataset.estado === e", arg=estado, timeout=5000)


def test_preparo_vota_em_duas_rodadas_travadas_e_revela(sala):
    contexto, base, erros = sala
    deck = _deck(contexto, base, "preparo")
    ana = _aluno(contexto, base, "Ana Souza", "rocket_launch")
    bruno = _aluno(contexto, base, "Bruno Lima", "pets")
    _esperar(ana, "votar")
    _esperar(bruno, "votar")
    ana.click(".opcao-3")
    bruno.click(".opcao-2")
    _esperar(ana, "votou")
    _esperar(bruno, "votou")

    # voto travado: recarregar volta para "votou", sem nova escolha
    ana.reload(wait_until="load")
    _esperar(ana, "votou")

    sel = "section#preparo"
    deck.wait_for_function("s => document.querySelector(s + ' .qv-n-votos').textContent === '2'", arg=sel)
    assert deck.inner_text(sel + " .qv-n-sala") == "2"
    # durante a votação a distribuição fica escondida
    assert deck.eval_on_selector_all(sel + " .qv-pct", "els => els.map(e => e.textContent)") == ["", "", "", ""]

    deck.click(sel + " [data-acao=encerrar]")
    deck.wait_for_function("s => document.querySelector(s + ' .quiz-vivo').dataset.fase === 'encerrada'", arg=sel)
    deck.wait_for_function("s => document.querySelectorAll(s + ' .qv-pct')[3].textContent === '50%'", arg=sel)
    _esperar(ana, "esperar")

    deck.click(sel + " [data-acao=rodada]")
    _esperar(bruno, "votar")
    assert "rodada 2" in bruno.inner_text(".tela-votar .rodada").lower()
    bruno.click(".opcao-3")
    _esperar(bruno, "votou")
    deck.click(sel + " [data-acao=encerrar]")
    deck.wait_for_function("s => document.querySelector(s + ' .quiz-vivo').classList.contains('quiz-vivo-com-rodada-2')", arg=sel)
    deck.click(sel + " [data-acao=revelar]")
    certa = deck.eval_on_selector_all(sel + " .quiz-vivo-opcoes li", "els => els.map(e => e.classList.contains('qv-certa'))")
    assert certa == [False, False, False, True]
    assert deck.eval_on_selector(sel + " [data-acao=rodada]", "e => e.hidden")
    assert erros == []


def test_nome_completo_e_lembrado_na_proxima_aula(sala):
    contexto, base, _ = sala
    _deck(contexto, base, "preparo")
    page = contexto.new_page()
    page.goto("%s/quiz/?s=%s&quiz-demo=1" % (base, SESSAO), wait_until="load")
    page.evaluate(LIMPA)
    page.reload(wait_until="load")
    page.fill("#nome", "Ana")
    page.click(".avatar[data-avatar=bolt]")
    page.click(".principal")
    assert "nome completo" in page.inner_text(".tela-entrar .erro")
    page.fill("#nome", "Ana Souza")
    page.click(".principal")
    _esperar(page, "votar")
    # outra sessão (outra aula): entra sozinho com o nome guardado
    page.goto("%s/quiz/?s=outra-aula&quiz-demo=1" % base, wait_until="load")
    page.wait_for_function("document.querySelector('main').dataset.estado !== 'entrar' && "
                           "document.querySelector('main').dataset.estado !== 'carregando'", timeout=5000)
    assert page.inner_text(".aluno-quem-nome") == "Ana Souza"


def test_sair_do_slide_fecha_a_pergunta_no_celular(sala):
    contexto, base, _ = sala
    deck = _deck(contexto, base, "preparo")
    ana = _aluno(contexto, base, "Ana Souza", "eco")
    _esperar(ana, "votar")
    deck.evaluate("Reveal.next()")
    _esperar(ana, "esperar")


def test_cronometro_de_30_s_encerra_a_votacao_sozinho(sala):
    contexto, base, _ = sala
    page = contexto.new_page()
    page.clock.install()
    page.goto("%s/aulas/aula01.html?quiz-demo=1&quiz-chave=teste#/escolha-visoes" % base, wait_until="load")
    page.clock.run_for(1000)
    sel = "section#escolha-visoes .quiz-vivo"
    page.wait_for_selector(sel + "[data-fase='aberta']")
    page.clock.run_for(31000)
    page.wait_for_selector(sel + "[data-fase='encerrada']")


def test_quatro_perguntas_das_visoes_tem_30_s_e_a_certa_do_gabarito():
    html = open(os.path.join(RAIZ, "aulas", "aula01.html"), encoding="utf-8").read()
    ids = ["escolha-visoes", "escolha-visoes-2", "escolha-visoes-3", "escolha-visoes-4"]
    certas = []
    for id_ in ids:
        secao = re.search(r'<section[^>]*id="%s">(.*?)</section>' % id_, html, re.S).group(1)
        assert 'data-tempo="30"' in secao and 'data-rodadas="1"' in secao
        opcoes = re.findall(r"<li( data-correct=\"true\")?>([^<]+)</li>", secao)
        assert [o[1] for o in opcoes] == ["Negociado", "Close", "Adj Close"]
        indice = [i for i, o in enumerate(opcoes) if o[0]][0]
        assert 'data-correta="%d"' % indice in secao
        certas.append(opcoes[indice][1])
    assert certas == ["Adj Close", "Negociado", "Adj Close", "Negociado"]


def test_nome_do_aluno_nao_tem_leitura_publica_no_schema():
    sql = open(os.path.join(RAIZ, "exemplos", "quiz-supabase", "quiz.sql"), encoding="utf-8").read()
    assert "create policy quiz_participantes_ler" not in sql
    assert "create or replace function quiz_sala" in sql
    assert "primary key (rodada_id, participante_id)" in sql
    assert "TROQUE-PELA-SUA-CHAVE" in sql
