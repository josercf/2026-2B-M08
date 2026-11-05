"""Decks dos quatro grupos da Aula 02 e a ADR online (assets/js/inteli-adr.js).

Os testes de navegador rodam no modo de memória (?quiz-demo=1): as abas do mesmo
contexto conversam por localStorage e BroadcastChannel, como conversariam pelo
Supabase. O professor gera os links pelo painel do deck principal de teste
(fixture_adr_professor.html), igual ao slide de links da aula.
"""
import os
import re
import sys
import urllib.parse

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402
import gerar_decks_grupos_aula02 as gerador  # noqa: E402
import medidas_aula02 as m  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

RAIZ = m.RAIZ
SESSAO = "m08-aula02-2026-11-05"


def _ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as fh:
        return fh.read()


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


# ------------------------------------------------------------- estáticos

def test_decks_gerados_estao_atualizados():
    gerados = gerador.gerar()
    assert sorted(gerados) == ["aulas/aula02-g0%d.html" % i for i in range(1, 5)]
    for caminho, html in gerados.items():
        assert _ler(caminho) == html, "rode tools/gerar_decks_grupos_aula02.py: %s" % caminho


def test_afirmacoes_saem_das_medicoes():
    a = m.afirmacoes_grupos()
    assert "O BBAS3 deu prejuízo de %s entre 2019 e 2026." % a["bbas3_close"] in _ler("aulas/aula02-g01.html")
    assert "A MGLU3 caiu %s desde 2019. Uma alta de %s devolve o cliente ao zero a zero." % (
        a["mglu3_queda"], a["mglu3_queda"]) in _ler("aulas/aula02-g02.html")
    assert "A PETR4 tem volatilidade de %s ao ano, então o pior que acontece em um ano é perder %s." % (
        a["petr4_vol"], a["petr4_vol"]) in _ler("aulas/aula02-g03.html")
    assert "A WEGE3 ganhou da renda fixa no período." in _ler("aulas/aula02-g04.html")


def test_decks_nao_trazem_veredito():
    rotulo = "<small>a afirmação é sustentada ou enganosa, e por quê</small>"
    for i in range(1, 5):
        html = _ler("aulas/aula02-g0%d.html" % i)
        # As duas palavras só aparecem no rótulo do campo de decisão, igual nos quatro decks.
        assert html.count(rotulo) == 1, i
        texto = _texto(html.replace(rotulo, "")).lower()
        assert "enganosa" not in texto and "sustentada" not in texto, i
        assert "adj close" not in texto, i
        assert chr(0x2014) not in html


# ------------------------------------------------------------ navegador

@pytest.fixture
def sala():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce",
                                         accept_downloads=True)
        erros = []
        contexto.on("weberror", lambda e: erros.append(str(e.error)))
        try:
            yield contexto, "http://127.0.0.1:%d" % porta, erros
        finally:
            navegador.close()
    httpd.shutdown()


def _professor(contexto, base):
    page = contexto.new_page()
    page.goto("%s/tools/tests/fixture_adr_professor.html?quiz-demo=1&quiz-chave=teste" % base, wait_until="load")
    page.evaluate("localStorage.removeItem('inteli-aula02-demo')")
    page.reload(wait_until="load")
    page.wait_for_selector("[data-adr-links][data-pronto='sim']")
    # Com a chave no navegador, os links aparecem sozinhos.
    page.wait_for_selector("[data-adr-links] .adr-link-url")
    return page


def _link(professor, grupo):
    url = professor.locator("[data-adr-links] [data-grupo='%s'] .adr-link-url" % grupo).inner_text()
    assert "aulas/aula02-%s.html?t=" % grupo.lower() in url
    return url


def _grupo(contexto, url, nome="Aluna Teste"):
    page = contexto.new_page()
    page.goto(url + "#/adr", wait_until="load")
    page.wait_for_selector("form[data-adr][data-pronto='sim']")
    if page.locator(".adr-quem-nome").count():
        page.fill(".adr-quem-nome", nome)
        page.click(".adr-quem-ok")
    return page


def _valor(page, campo):
    return page.locator("form[data-adr] [name=%s]" % campo).input_value()


def test_dois_colegas_veem_a_edicao_um_do_outro(sala):
    contexto, base, erros = sala
    prof = _professor(contexto, base)
    url = _link(prof, "G02")
    a, b = _grupo(contexto, url), _grupo(contexto, url)
    a.fill("form[data-adr] [name=contexto]", "A MGLU3 caiu muito")
    b.wait_for_function("document.querySelector('form[data-adr] [name=contexto]').value === 'A MGLU3 caiu muito'",
                        timeout=5000)
    assert not erros


def test_campo_com_foco_nao_e_sobrescrito_e_mostra_aviso(sala):
    contexto, base, _ = sala
    url = _link(_professor(contexto, base), "G01")
    a, b = _grupo(contexto, url), _grupo(contexto, url)
    a.click("form[data-adr] [name=opcoes]")
    a.keyboard.type("texto de A")
    a.wait_for_timeout(1200)
    b.fill("form[data-adr] [name=opcoes]", "texto de B")
    a.wait_for_selector("form[data-adr] [data-campo=opcoes] .adr-aviso:not([hidden])", timeout=5000)
    assert _valor(a, "opcoes") == "texto de A"


def test_prazo_encerrado_trava_formulario_e_backend_recusa(sala):
    contexto, base, _ = sala
    prof = _professor(contexto, base)
    url = _link(prof, "G03")
    g = _grupo(contexto, url)
    g.fill("form[data-adr] [name=titulo]", "antes do prazo")
    g.wait_for_timeout(1200)
    prof.eval_on_selector("[data-adr-links] .adr-minutos", "e => { e.value = '0'; }")
    prof.click("[data-adr-links] .adr-iniciar")
    g.wait_for_selector("form[data-adr].adr-travado", timeout=5000)
    assert g.locator("form[data-adr] [name=titulo]").get_attribute("readonly") is not None
    token = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["t"][0]
    erro = g.evaluate("""t => IntelIAula02Dados.criar().adrSalvar('%s', 'G03', t, 'titulo', 'depois', null)
                         .then(() => 'aceitou', e => e.message)""" % SESSAO, token)
    assert erro == "prazo encerrado"
    assert _valor(g, "titulo") == "antes do prazo"


def test_token_errado_abre_somente_leitura(sala):
    contexto, base, _ = sala
    _professor(contexto, base)
    g = _grupo(contexto, "%s/aulas/aula02-g04.html?t=errado&quiz-demo=1" % base)
    assert g.locator("form[data-adr] [name=contexto]").get_attribute("readonly") is not None
    assert "sem permissão de edição" in g.locator("form[data-adr] .adr-estado").inner_text()


def test_markdown_baixado_segue_o_template(sala):
    contexto, base, _ = sala
    g = _grupo(contexto, _link(_professor(contexto, base), "G01"))
    g.fill("form[data-adr] [name=titulo]", "Qual preço usar no retorno")
    g.fill("form[data-adr] [name=decisao]", "Decidimos pelo preço com proventos")
    with g.expect_download() as info:
        g.click("form[data-adr] .adr-baixar")
    with open(info.value.path(), encoding="utf-8") as fh:
        md = fh.read()
    assert md.startswith("# ADR NNNN: Qual preço usar no retorno")
    for secao in ("## Contexto e problema", "## Critérios de decisão", "## Opções consideradas",
                  "## Decisão", "## Consequências"):
        assert secao in md
    assert "Decidimos pelo preço com proventos" in md


def test_painel_comite_mostra_o_texto_ao_vivo(sala):
    contexto, base, _ = sala
    prof = _professor(contexto, base)
    g = _grupo(contexto, _link(prof, "G04"))
    g.fill("form[data-adr] [name=decisao]", "Veredito do G04 ao vivo")
    prof.wait_for_function(
        "document.querySelector('[data-adr-comite][data-grupo=G04] .adr-comite-decisao').textContent"
        ".includes('Veredito do G04 ao vivo')", timeout=5000)


def test_participacao_registra_quem_editou_e_reaproveita_o_nome_do_quiz(sala):
    contexto, base, _ = sala
    prof = _professor(contexto, base)
    url = _link(prof, "G03")
    a = _grupo(contexto, url, nome="Ana Souza")
    assert "Ana Souza" in a.locator("form[data-adr] .adr-estado").inner_text()
    a.fill("form[data-adr] [name=contexto]", "texto da Ana")
    a.wait_for_timeout(1200)
    # O mesmo navegador já tem o nome guardado: o segundo deck não pergunta de novo.
    b = _grupo(contexto, url)
    assert b.locator(".adr-quem-nome").count() == 0
    linhas = prof.evaluate("IntelIAula02Dados.criar().adrParticipacao('teste', 'm08-aula02-2026-11-05')")
    assert any(l["grupo"] == "G03" and l["nome"] == "Ana Souza" and l["edicoes"] >= 1 for l in linhas)
