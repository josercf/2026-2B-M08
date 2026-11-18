"""Tela de spec da Aula 04 (aulas/aula04-spec.html): iniciais, selos e leitura.

A tela identifica quem edita pelas iniciais que o portal passa em a=, grava as
iniciais como autor (a tabela de campos tem leitura pública, então nenhum nome
vai ao banco), mostra em cada campo quem editou por último e há quanto tempo, e
tem uma visão somente leitura (?ver=1) para o projetor.

Os testes de navegador rodam em memória (?quiz-demo=1) com o token fixo que o
portal entrega nesse modo: as abas do mesmo contexto conversam por localStorage
e BroadcastChannel, como conversariam pelo Supabase.
"""
import glob
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_slides  # noqa: E402

SESSAO = "m08-aula04-2026-11-18"
ARQUIVOS = ["aulas/aula04-spec.html", "assets/js/aula04-spec.js", "assets/css/aula04-spec.css",
            "assets/js/inteli-adr.js", "assets/js/simulador-portal.js", "assets/js/simulador-dados.js",
            "assets/css/simulador.css", "simulador/index.html"]


def _ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------- estáticos

def test_arquivos_da_spec_e_do_portal_nao_tem_travessao():
    for caminho in ARQUIVOS:
        assert chr(0x2014) not in _ler(caminho), caminho


def test_tela_de_spec_carrega_a_folha_propria_depois_da_dos_turnos():
    html = _ler("aulas/aula04-spec.html")
    assert html.index("aula04-turnos.css") < html.index("aula04-spec.css")
    assert 'data-spec-barra' in html and 'data-spec-leitura' in html


def test_token_de_demonstracao_e_o_mesmo_no_portal_e_na_tela_de_spec():
    assert "var TOKEN_DEMO = 'demo-aula04';" in _ler("assets/js/simulador-dados.js")
    assert "var TOKEN_DEMO = 'demo-aula04';" in _ler("assets/js/aula04-spec.js")


def test_extensao_do_autor_e_opcional_e_a_aula_02_nao_usa():
    """Os decks da Aula 02 seguem com a lista de nomes: nenhum declara data-autor."""
    decks = sorted(glob.glob(os.path.join(RAIZ, "aulas", "aula02*.html")))
    assert len(decks) >= 5
    for deck in decks:
        with open(deck, encoding="utf-8") as fh:
            assert "data-autor" not in fh.read(), deck
    js = _ler("assets/js/inteli-adr.js")
    assert "form.hasAttribute('data-autor')" in js
    assert "Peça ao professor o link do grupo no Slack." in js  # texto da Aula 02 mantido


# ------------------------------------------------------------ navegador

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def base():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    yield "http://127.0.0.1:%d" % porta
    httpd.shutdown()


@pytest.fixture(scope="module")
def navegador():
    with sync_api.sync_playwright() as p:
        nav = p.chromium.launch()
        yield nav
        nav.close()


@pytest.fixture
def contexto(navegador):
    ctx = navegador.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
    erros = []
    ctx.on("weberror", lambda e: erros.append(str(e.error)))
    ctx.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    try:
        yield ctx
        assert erros == []
    finally:
        ctx.close()


def _spec(base, grupo="G02", turno=4, a=None, token="demo-aula04"):
    url = "%s/aulas/aula04-spec.html?g=%s&t=%s&turno=%d&quiz-demo=1" % (base, grupo, token, turno)
    return url + ("&a=" + a if a else "")


def _editar(contexto, url):
    page = contexto.new_page()
    page.goto(url, wait_until="load")
    page.wait_for_selector("form[data-adr][data-pronto='sim']")
    return page


def _ver(contexto, base, grupo="G02", turno=4):
    page = contexto.new_page()
    page.goto("%s/aulas/aula04-spec.html?g=%s&turno=%d&ver=1&quiz-demo=1" % (base, grupo, turno), wait_until="load")
    page.wait_for_selector("[data-spec-leitura][data-pronto='sim']")
    return page


def _selo(page, campo):
    return page.locator("[data-campo='%s'] .spec-selo" % campo)


def _gravado(page, turno=4, grupo="G02"):
    linhas = page.evaluate("IntelIAula02Dados.criar().adrCampos('%s-t%d', '%s')" % (SESSAO, turno, grupo))
    return sorted((l["campo"], l["texto"], l["autor"]) for l in linhas)


def test_duas_abas_do_grupo_gravam_as_iniciais_e_mostram_o_selo(contexto, base):
    jr = _editar(contexto, _spec(base, a="JR"))
    ms = _editar(contexto, _spec(base, a="MS"))
    assert jr.get_attribute("form[data-adr] [name=contexto]", "readonly") is None
    assert "Editando como JR, grupo G02" in jr.inner_text("form[data-adr] .adr-estado")
    assert jr.inner_text("[data-spec-eu]") == "Você edita como JR"
    assert not jr.is_visible("[data-spec-iniciais]")

    # O cabeçalho mostra quem está na spec do grupo agora, nas duas abas.
    for page in (jr, ms):
        page.wait_for_function("document.querySelector('[data-spec-fichas]').dataset.quem === 'JR,MS'")
        assert page.locator(".spec-ficha").all_inner_texts() == ["JR", "MS"]
    assert jr.locator(".spec-ficha-eu").inner_text() == "JR" and ms.locator(".spec-ficha-eu").inner_text() == "MS"

    # JR digita: enquanto o campo está em foco, as duas abas mostram quem edita.
    jr.fill("form[data-adr] [name=contexto]", "retornos: DataFrame de N pregões")
    ms.wait_for_function(
        "document.querySelector(\"[data-campo='contexto'] .spec-selo\").textContent === 'JR, editando'")
    assert _selo(ms, "contexto").get_attribute("data-vivo") == "sim"
    ms.wait_for_function("document.querySelector('form[data-adr] [name=contexto]').value.startsWith('retornos')")
    # O autor gravado são as iniciais, e não um nome.
    assert _gravado(jr) == [("contexto", "retornos: DataFrame de N pregões", "JR")]

    # JR sai do campo: o selo passa a dizer há quanto tempo, com destaque nos primeiros 10 s.
    jr.fill("form[data-adr] [name=decisao]", "python conferir.py 4 imprime TURNO 4: OK")
    for page in (jr, ms):
        page.wait_for_function(
            "document.querySelector(\"[data-campo='contexto'] .spec-selo\").textContent === 'JR, agora'")
        assert _selo(page, "contexto").get_attribute("data-vivo") == "sim"
        assert page.get_attribute("[data-campo='contexto']", "data-vivo") == "sim"
    ms.wait_for_function(
        "/^JR, há 1\\d s$/.test(document.querySelector(\"[data-campo='contexto'] .spec-selo\").textContent)",
        timeout=15000)
    assert _selo(ms, "contexto").get_attribute("data-vivo") == "nao"

    # MS edita outro campo: cada campo guarda o seu autor.
    ms.fill("form[data-adr] [name=criterios]", "tabela com pesos, retorno, risco e sharpe")
    jr.wait_for_function(
        "document.querySelector(\"[data-campo='criterios'] .spec-selo\").textContent === 'MS, editando'")
    ms.click("form[data-adr] [name=opcoes]")
    jr.wait_for_function(
        "document.querySelector(\"[data-campo='criterios'] .spec-selo\").textContent === 'MS, agora'")
    assert ("criterios", "tabela com pesos, retorno, risco e sharpe", "MS") in _gravado(ms)
    assert not _selo(jr, "titulo").is_visible()  # campo que ninguém editou não tem selo

    # Quem fecha a aba sai do cabeçalho.
    ms.close()
    jr.wait_for_function("document.querySelector('[data-spec-fichas]').dataset.quem === 'JR'", timeout=15000)


def test_sem_iniciais_na_url_a_tela_pede_antes_de_liberar_a_edicao(contexto, base):
    page = _editar(contexto, _spec(base, grupo="G03"))
    assert page.is_visible("[data-spec-iniciais]")
    assert page.get_attribute("form[data-adr] [name=contexto]", "readonly") is not None
    assert "Informe as iniciais" in page.inner_text("form[data-adr] .adr-estado")
    assert not page.is_visible(".adr-quem")  # nunca o campo de nome completo da Aula 02

    page.click("[data-spec-entrar]")  # vazio: continua pedindo
    assert page.get_attribute("form[data-adr] [name=contexto]", "readonly") is not None
    page.fill("#spec-iniciais", "j9r")  # só letras, em maiúsculas
    assert page.input_value("#spec-iniciais") == "JR"
    assert page.get_attribute("#spec-iniciais", "maxlength") == "3"
    page.fill("#spec-iniciais", "ab")
    page.press("#spec-iniciais", "Enter")
    page.wait_for_function("document.querySelector('form[data-adr] [name=contexto]').readOnly === false")
    assert not page.is_visible("[data-spec-iniciais]")
    assert page.inner_text("[data-spec-eu]") == "Você edita como AB"
    assert "a=AB" in page.url  # a recarga mantém as iniciais
    assert page.evaluate("Reveal.getIndices().h") == 0  # digitar não trocou de slide

    page.fill("form[data-adr] [name=opcoes]", "n menor que 1 levanta ValueError")
    page.click("form[data-adr] [name=decisao]")
    page.wait_for_function(
        "document.querySelector(\"[data-campo='opcoes'] .spec-selo\").textContent === 'AB, agora'")
    assert _gravado(page, grupo="G03") == [("opcoes", "n menor que 1 levanta ValueError", "AB")]

    page.reload(wait_until="load")
    page.wait_for_selector("form[data-adr][data-pronto='sim']")
    assert not page.is_visible("[data-spec-iniciais]")
    assert page.get_attribute("form[data-adr] [name=contexto]", "readonly") is None


def test_iniciais_do_portal_neste_navegador_entram_como_sugestao(contexto, base):
    page = _editar(contexto, _spec(base, grupo="G01"))
    page.evaluate("localStorage.setItem('inteli-simulador-eu:%s', JSON.stringify("
                  "{id: 'x', iniciais: 'LT', grupo: 'G01'}))" % SESSAO)
    page.reload(wait_until="load")
    page.wait_for_selector("form[data-adr][data-pronto='sim']")
    assert page.input_value("#spec-iniciais") == "LT"
    assert page.get_attribute("form[data-adr] [name=contexto]", "readonly") is not None  # ainda confirma
    outro = _editar(contexto, _spec(base, grupo="G04"))  # identidade de outro grupo não vale
    assert outro.input_value("#spec-iniciais") == ""


def test_token_errado_com_iniciais_fica_so_para_leitura(contexto, base):
    page = _editar(contexto, _spec(base, a="JR", token="errado"))
    assert page.get_attribute("form[data-adr] [name=decisao]", "readonly") is not None
    estado = page.inner_text("form[data-adr] .adr-estado")
    assert "sem permissão de edição" in estado and "Progresso do portal" in estado
    assert not page.is_visible("[data-spec-iniciais]") and not page.is_visible("[data-spec-eu]")
    page.wait_for_timeout(600)
    assert page.locator(".spec-ficha").count() == 0  # quem só lê não entra em "na spec agora"


def test_visao_somente_leitura_nao_tem_campo_e_acompanha_a_edicao(contexto, base):
    jr = _editar(contexto, _spec(base, a="JR"))
    jr.fill("form[data-adr] [name=titulo]", "simular(retornos, n, semente, rf)")
    jr.fill("form[data-adr] [name=decisao]", "aceite do G02")
    jr.click("form[data-adr] [name=contexto]")
    jr.wait_for_function("document.querySelector(\"[data-campo='decisao'] .spec-selo\").textContent === 'JR, agora'")

    ver = _ver(contexto, base)
    # Sem token, sem campo editável e sem o segundo slide do grupo.
    assert "t=" not in ver.url
    assert ver.locator("input, textarea, [contenteditable]").count() == 0
    assert ver.locator("form").count() == 0
    assert ver.locator("section#depois").count() == 0
    assert "Spec do turno 4: grupo G02" in ver.inner_text("#spec h2")
    assert ver.inner_text("[data-adr-cronometro]") == "Somente leitura"
    assert ver.locator(".spec-leitura-rotulo").all_inner_texts() == [
        "Função", "Entrada", "Saída", "Casos de borda", "Critério de aceite"]
    assert ver.inner_text("[data-campo='titulo'] .spec-leitura-texto") == "simular(retornos, n, semente, rf)"
    assert ver.inner_text("[data-campo='decisao'] .spec-leitura-texto") == "aceite do G02"
    assert ver.inner_text("[data-campo='criterios'] .spec-leitura-texto") == "Ainda em branco"
    assert _selo(ver, "decisao").text_content().startswith("JR, ")
    assert not _selo(ver, "criterios").is_visible()
    # Quem projeta vê quem está na spec, sem entrar na lista.
    ver.wait_for_function("document.querySelector('[data-spec-fichas]').dataset.quem === 'JR'")
    jr.wait_for_timeout(1200)
    assert jr.locator(".spec-ficha").all_inner_texts() == ["JR"]

    # A edição chega sozinha, com o selo de quem está no campo.
    jr.fill("form[data-adr] [name=criterios]", "tabela com pesos, retorno, risco e sharpe")
    ver.wait_for_function("document.querySelector(\"[data-campo='criterios'] .spec-leitura-texto\")"
                          ".textContent === 'tabela com pesos, retorno, risco e sharpe'", timeout=8000)
    assert _selo(ver, "criterios").text_content() == "JR, editando"
    assert ver.get_attribute("[data-campo='criterios']", "data-vivo") == "sim"

    # Atalhos para os outros grupos e para o outro turno, ainda em leitura.
    assert ver.locator("[data-spec-outros] a").all_inner_texts() == ["G01", "G02", "G03", "G04", "Turno 4", "Turno 5"]
    assert ver.locator("[data-spec-outros] a[aria-current='page']").all_inner_texts() == ["G02", "Turno 4"]
    ver.click("[data-spec-outros] a:has-text('Turno 5')")
    ver.wait_for_selector("[data-spec-leitura][data-pronto='sim']")
    assert "Spec do turno 5: grupo G02" in ver.inner_text("#spec h2")
    assert ver.inner_text("[data-campo='decisao'] .spec-leitura-texto") == "Ainda em branco"  # outra sessão
    assert ver.locator("input, textarea").count() == 0


def test_tela_de_spec_cabe_no_slide_com_a_barra_e_os_selos(contexto, base):
    page = _editar(contexto, _spec(base, a="MMM"))
    for campo in ("titulo", "contexto", "criterios", "opcoes", "decisao"):
        page.fill("form[data-adr] [name=%s]" % campo, "texto do campo %s" % campo)
    page.evaluate("document.activeElement.blur()")
    page.wait_for_function("document.querySelectorAll('.spec-selo:not([hidden])').length === 5")
    medidas = page.evaluate("""() => {
      const area = document.querySelector('.adr-area').getBoundingClientRect();
      const dentro = n => { const r = n.getBoundingClientRect(); return r.top >= area.top - 1 && r.bottom <= area.bottom + 1 && r.right <= area.right + 1; };
      const nos = [...document.querySelectorAll('.spec-barra, form[data-adr] [data-campo], .adr-rodape, .spec-selo')];
      // O selo não cobre o nome do campo (a dica ao lado pode encolher).
      const livre = [...document.querySelectorAll('form[data-adr] [data-campo]')].every(c => {
        const faixa = document.createRange(); faixa.selectNodeContents(c.querySelector('label').firstChild);
        return faixa.getBoundingClientRect().right <= c.querySelector('.spec-selo').getBoundingClientRect().left;
      });
      return { dentro: nos.every(dentro), livre: livre };
    }""")
    assert medidas == {"dentro": True, "livre": True}


def test_projetor_da_adr_ganha_selo_de_autoria_so_com_data_selos(contexto, base):
    """Extensão opcional de inteli-adr.js: o painel do projetor da Aula 02 não muda."""
    fixture = _ler("tools/tests/fixture_adr_professor.html")
    assert "data-selos" not in fixture
    gravar = """async () => {
        const dados = IntelIAula02Dados.criar();
        const token = (await dados.adrLinks('teste', 'm08-aula02-2026-11-05')).find(l => l.grupo === 'G04').token;
        await dados.adrSalvar('m08-aula02-2026-11-05', 'G04', token, 'decisao', 'decisão do G04', 'JR');
        await dados.adrSalvar('m08-aula02-2026-11-05', 'G04', token, 'contexto', 'contexto do G04', 'MS');
    }"""
    endereco = "%s/tools/tests/fixture_adr_professor.html?quiz-demo=1&quiz-chave=teste" % base
    sem = contexto.new_page()
    sem.goto(endereco, wait_until="load")
    sem.wait_for_selector("[data-adr-comite][data-pronto='sim']")
    sem.evaluate(gravar)
    sem.wait_for_function("document.querySelector('.adr-comite-decisao').textContent === 'decisão do G04'")
    assert sem.locator(".adr-comite-selo").count() == 0
    assert sem.locator(".adr-comite-detalhes dt").all_inner_texts() == ["Contexto"]

    contexto.route("**/fixture_adr_professor.html*", lambda rota: rota.fulfill(
        status=200, content_type="text/html; charset=utf-8",
        body=fixture.replace("<div data-adr-comite ", "<div data-adr-comite data-selos ")))
    com = contexto.new_page()
    com.goto(endereco, wait_until="load")
    com.wait_for_selector("[data-adr-comite][data-selos][data-pronto='sim']")
    assert com.text_content(".adr-comite-decisao") == "decisão do G04 (JR, agora)"
    assert com.text_content(".adr-comite-detalhes dt") == "Contexto (MS, agora)"
    assert com.get_attribute(".adr-comite-decisao .adr-comite-selo", "data-vivo") == "sim"
    assert com.locator(".adr-comite-titulo .adr-comite-selo").count() == 0  # título em branco não tem autor
