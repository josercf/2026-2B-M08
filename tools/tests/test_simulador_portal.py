"""Portal de simulação da Aula 04 em turnos (simulador/index.html, ADR-018).

Os testes rodam em ?demo=1: a sala fica em memória (localStorage e
BroadcastChannel) e a identidade de cada participante fica no sessionStorage da
aba, então duas abas do mesmo contexto são dois alunos na mesma sala.

O número que o aluno lê no portal vira valor esperado do teste que ele escreve
nos turnos 1 e 2. Por isso a conferência é feita contra tools/simulador_referencia.py,
lendo o valor dos atributos data-* e não do texto formatado.
"""
import json
import os
import sys
import time

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_slides  # noqa: E402
import simulador_referencia as sim  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

CSV = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados", "precos.csv")
JSON = os.path.join(RAIZ, "assets", "data", "aula04-cotacoes.json")
PERIODOS = [9, 21, 63, 126, 252]
# Recurso bloqueado de propósito no teste do banco fora do ar: o navegador
# registra a falha de rede no console, e ela não é erro do portal.
FALHA_DE_REDE = "Failed to load resource"


@pytest.fixture(scope="module")
def precos():
    return pd.read_csv(CSV, index_col="data")


@pytest.fixture(scope="module")
def cotacoes():
    with open(JSON, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def servidor():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    yield "http://127.0.0.1:%d/simulador/index.html" % porta
    httpd.shutdown()


@pytest.fixture(scope="module")
def navegador():
    with sync_api.sync_playwright() as p:
        nav = p.chromium.launch()
        yield nav
        nav.close()


def _contexto(navegador, largura=1280, altura=720):
    contexto = navegador.new_context(viewport={"width": largura, "height": altura},
                                     reduced_motion="reduce")
    erros = []
    contexto.on("weberror", lambda e: erros.append(str(e.error)))
    contexto.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    return contexto, erros


@pytest.fixture
def sala(navegador, servidor):
    """Contexto novo por teste, em ?demo=1. Ao final, o console não pode ter erro."""
    contexto, erros = _contexto(navegador)
    try:
        yield contexto, servidor + "?demo=1"
        assert erros == []
    finally:
        contexto.close()


def _abrir(contexto, url, limpar=True):
    page = contexto.new_page()
    page.goto(url, wait_until="load")
    if limpar:
        page.evaluate("localStorage.clear(); sessionStorage.clear()")
        page.reload(wait_until="load")
    page.wait_for_selector("body[data-sala]")
    return page


def _entrar(page, iniciais="AB", grupo="G01"):
    page.wait_for_selector(".tela-entrar:not([hidden])")
    page.fill("#iniciais", iniciais)
    page.click(".grupo-opcao[data-grupo='%s']" % grupo)
    page.click("#entrar-botao")
    page.wait_for_selector(".tela-montar:not([hidden])")


def _adicionar(page, ticker):
    page.fill("#busca", ticker)
    page.press("#busca", "Enter")


def _montar(page, ativos, pregoes):
    for ticker in ativos:
        _adicionar(page, ticker)
    page.click(".tela-montar .periodos button[data-pregoes='%d']" % pregoes)
    page.wait_for_selector("#montar-resultado:not([hidden])")


def _ativos(page):
    return page.eval_on_selector_all("#ativos .ativo", "nos => nos.map(n => n.dataset.ticker)")


def _numero(page, seletor, atributo="valor"):
    return float(page.get_attribute(seletor, "data-" + atributo))


def _destaque(page, raiz, carteira):
    linha = "%s tr[data-carteira='%s']" % (raiz, carteira)
    return {campo: _numero(page, linha, campo) for campo in ("retorno", "risco", "sharpe")}


def _simular(page, n):
    page.click(".sim-nav a[data-nav='simular']")
    page.wait_for_selector(".tela-simular:not([hidden])")
    page.click(".quantidades button[data-n='%d']" % n)
    page.wait_for_selector("#simular-nuvem .nuvem-tela[data-pronto='sim'][data-n='%d']" % n)


def _pesos(page, valores):
    for ticker, valor in valores.items():
        page.fill("input[data-peso='%s']" % ticker, valor)
    page.click("#form-pesos button[type='submit']")


# ------------------------------------------------------------------ entrar

def test_entrar_com_iniciais_e_grupo_mostra_o_avatar_e_sobrevive_a_recarga(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    page.click("#entrar-botao")
    assert page.inner_text("#entrar-erro") == "Informe de 1 a 3 letras."
    page.fill("#iniciais", "j9r")  # só letras, em maiúsculas
    assert page.input_value("#iniciais") == "JR"
    _entrar(page, "jr", "G02")
    assert page.inner_text("#eu-avatar") == "JR"
    assert page.get_attribute("#eu-avatar", "data-grupo") == "G02"
    _adicionar(page, "PETR4")
    page.reload(wait_until="load")
    page.wait_for_selector(".tela-montar:not([hidden])")
    assert page.inner_text("#eu-avatar") == "JR" and _ativos(page) == ["PETR4"]


# ------------------------------------------------------------------ montar

def test_retorno_e_risco_de_petr4_e_vale3_em_9_pregoes_sao_os_da_referencia(sala, precos):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    _montar(page, ["PETR4", "VALE3"], 9)

    rets = sim.retornos(precos, ["PETR4", "VALE3"], 9)
    retorno, risco = sim.metricas([0.5, 0.5], rets)
    assert _numero(page, "#m-retorno") == pytest.approx(retorno, abs=1e-9)
    assert _numero(page, "#m-risco") == pytest.approx(risco, abs=1e-9)
    final = 100000 * float((1 + rets.to_numpy() @ [0.5, 0.5]).prod())
    assert _numero(page, "#m-final") == pytest.approx(final, abs=1e-6)

    # Tabela dos 9 pregões: retorno de cada ativo e o da carteira, pregão a pregão.
    assert page.is_visible("#bloco-diaria")
    linhas = page.eval_on_selector_all(
        "#tabela-diaria tbody tr",
        "trs => trs.map(tr => [tr.dataset.data].concat("
        "Array.from(tr.querySelectorAll('td')).map(td => Number(td.dataset.valor))))")
    assert [linha[0] for linha in linhas] == list(rets.index)
    for linha, (_, esperado) in zip(linhas, rets.iterrows()):
        assert linha[1:3] == pytest.approx(list(esperado), abs=1e-12)
        assert linha[3] == pytest.approx(sim.retorno_do_dia([0.5, 0.5], esperado), abs=1e-12)

    # Leitura para o aluno: porcentagem com 2 casas e, sob pedido, decimal com 6.
    assert page.inner_text("#m-retorno") == ("%.2f%%" % (retorno * 100)).replace(".", ",")
    assert not page.is_visible("#m-retorno-dec")
    page.click("label.chave")
    assert page.inner_text("#m-retorno-dec") == "%.6f" % retorno
    assert page.inner_text("#tabela-diaria tbody tr:first-child td[data-ativo='carteira'] .em-decimal") == \
        "%.6f" % sim.retorno_do_dia([0.5, 0.5], rets.iloc[0])

    # Fora de 9 pregões a tabela diária some.
    page.click(".tela-montar .periodos button[data-pregoes='21']")
    assert not page.is_visible("#bloco-diaria")
    retorno21, _ = sim.metricas([0.5, 0.5], sim.retornos(precos, ["PETR4", "VALE3"], 21))
    assert _numero(page, "#m-retorno") == pytest.approx(retorno21, abs=1e-9)


def test_var_de_um_dia_a_95_por_cento_aparece_com_os_dois_metodos_e_em_reais(sala, precos):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    _montar(page, ["PETR4", "VALE3"], 252)

    historico, parametrico = sim.valor_em_risco(
        [0.5, 0.5], sim.retornos(precos, ["PETR4", "VALE3"], 252))
    assert _numero(page, "#m-var-hist") == pytest.approx(historico, abs=1e-9)
    assert _numero(page, "#m-var-param") == pytest.approx(parametrico, abs=1e-9)
    assert page.inner_text("#m-var-hist") == ("%.2f%%" % (historico * 100)).replace(".", ",")
    assert _numero(page, "#m-var-hist-reais") == pytest.approx(historico * 100000, abs=1e-4)
    assert "R$" in page.inner_text("#m-var-param-reais")

    # Com 9 pregões o percentil é pouco estável, e a tela avisa.
    page.click(".tela-montar .periodos button[data-pregoes='9']")
    hist9, _ = sim.valor_em_risco([0.5, 0.5], sim.retornos(precos, ["PETR4", "VALE3"], 9))
    assert _numero(page, "#m-var-hist") == pytest.approx(hist9, abs=1e-9)
    assert "pouco estável" in page.inner_text("#m-var-nota")
    page.click(".tela-montar .periodos button[data-pregoes='252']")
    assert "pouco estável" not in page.inner_text("#m-var-nota")


def test_ticker_inexistente_avisa_e_mantem_a_carteira(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    _adicionar(page, "PETR4")
    _adicionar(page, "XXXX9")
    assert "ativo não encontrado no arquivo da aula" in page.inner_text("#busca-erro")
    assert _ativos(page) == ["PETR4"]
    _adicionar(page, "PETR4")
    assert "já está na carteira" in page.inner_text("#busca-erro")
    _adicionar(page, "vale3")
    assert page.inner_text("#busca-erro") == "" and _ativos(page) == ["PETR4", "VALE3"]
    for ticker in ("ITUB4", "WEGE3", "BBAS3", "BOVA11"):  # o sexto é recusado
        _adicionar(page, ticker)
    assert _ativos(page) == ["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"]
    assert "até 5 ativos" in page.inner_text("#busca-erro")


def test_busca_sugere_tickers_do_arquivo(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    page.fill("#busca", "PET")
    page.wait_for_selector("#sugestoes:not([hidden])")
    assert page.eval_on_selector_all("#sugestoes li", "nos => nos.map(n => n.textContent)") == ["PETR3", "PETR4"]
    page.press("#busca", "ArrowDown")
    page.press("#busca", "ArrowDown")
    page.press("#busca", "Enter")
    assert _ativos(page) == ["PETR4"]


def test_ativo_de_inicio_tardio_informa_a_janela_comum(sala, cotacoes):
    """No arquivo real, o ativo mais novo ainda deixa os cinco períodos disponíveis."""
    contexto, url = sala
    contagem = {t: sum(v is not None for v in serie) for t, serie in cotacoes["precos"].items()}
    tardio = min(contagem, key=contagem.get)
    disponiveis = contagem[tardio] - 1
    assert disponiveis < len(cotacoes["datas"]) - 1
    page = _abrir(contexto, url)
    _entrar(page)
    _adicionar(page, "PETR4")
    assert _numero(page, "#m-janela", "disponiveis") == len(cotacoes["datas"]) - 1
    _adicionar(page, tardio)
    assert _numero(page, "#m-janela", "disponiveis") == disponiveis
    assert "%d pregões" % disponiveis in page.inner_text("#m-janela")
    assert "cotação desde" in page.inner_text("#ativos .ativo[data-ticker='%s']" % tardio)
    bloqueados = page.eval_on_selector_all(
        ".tela-montar .periodos button:disabled", "nos => nos.map(n => Number(n.dataset.pregoes))")
    assert bloqueados == [p for p in PERIODOS if p > disponiveis]


def test_janela_comum_curta_limita_os_periodos_oferecidos(sala, cotacoes, precos):
    """Review Focus 3. O arquivo de hoje não tem ativo com menos de 252 pregões,
    então o teste serve ao portal uma cópia em que a VALE3 começa 100 pregões
    antes do corte."""
    contexto, url = sala
    curto = json.loads(json.dumps(cotacoes))
    total = len(curto["datas"])
    curto["precos"]["VALE3"] = [None] * (total - 101) + curto["precos"]["VALE3"][total - 101:]
    contexto.route("**/aula04-cotacoes.json", lambda rota: rota.fulfill(
        status=200, content_type="application/json", body=json.dumps(curto)))
    page = _abrir(contexto, url)
    _entrar(page)
    _adicionar(page, "PETR4")
    assert page.get_attribute(".tela-montar .periodos button[data-pregoes='252']", "aria-pressed") == "true"
    _adicionar(page, "VALE3")
    assert _numero(page, "#m-janela", "disponiveis") == 100
    assert "100 pregões" in page.inner_text("#m-janela")
    bloqueados = page.eval_on_selector_all(
        ".tela-montar .periodos button:disabled", "nos => nos.map(n => Number(n.dataset.pregoes))")
    assert bloqueados == [126, 252]
    # O período escolhido cai para o maior que cabe, e a conta segue a referência.
    assert page.get_attribute(".tela-montar .periodos button[data-pregoes='63']", "aria-pressed") == "true"
    retorno, risco = sim.metricas([0.5, 0.5], sim.retornos(precos, ["PETR4", "VALE3"], 63))
    assert _numero(page, "#m-retorno") == pytest.approx(retorno, abs=1e-9)
    assert _numero(page, "#m-risco") == pytest.approx(risco, abs=1e-9)
    # A tela Simular oferece os mesmos períodos.
    _simular(page, 100)
    assert page.eval_on_selector_all(
        ".tela-simular .periodos button:disabled", "nos => nos.map(n => Number(n.dataset.pregoes))") == [126, 252]


# ----------------------------------------------------------------- simular

def test_dez_mil_carteiras_desenham_a_nuvem_em_menos_de_dois_segundos(sala, cotacoes):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    _montar(page, ["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"], 252)
    page.click(".sim-nav a[data-nav='simular']")
    page.wait_for_selector("#simular-nuvem .nuvem-tela[data-pronto='sim'][data-n='1000']")
    inicio = time.monotonic()
    page.click(".quantidades button[data-n='10000']")
    page.wait_for_selector("#simular-nuvem .nuvem-tela[data-pronto='sim'][data-n='10000']")
    assert time.monotonic() - inicio < 2
    assert _numero(page, "#simular-nuvem .nuvem-tela", "ms") < 2000

    # A nuvem foi de fato desenhada: o canvas tem pontos além do fundo.
    cores = page.evaluate(
        "() => { const c = document.querySelector('#simular-nuvem .nuvem-tela');"
        " const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;"
        " const vistas = new Set(); for (let i = 0; i < d.length; i += 4 * 97)"
        " vistas.add(d[i] + ',' + d[i + 1] + ',' + d[i + 2]); return vistas.size; }")
    assert cores > 20

    # Semente gravada e mostrada; o sorteio novo troca a semente e a nuvem.
    semente = page.get_attribute("#simular-nuvem .nuvem-tela", "data-semente")
    assert page.inner_text("#semente") == semente
    melhor = _destaque(page, "#simular-nuvem", "melhor")
    assert melhor["sharpe"] == pytest.approx((melhor["retorno"] - cotacoes["rf_anual"]) / melhor["risco"], abs=1e-9)
    assert "maior Sharpe" in page.inner_text("#simular-nuvem .leitura")
    page.click("#novo-sorteio")
    page.wait_for_function(
        "s => document.querySelector('#simular-nuvem .nuvem-tela').dataset.semente !== s", arg=semente)
    assert _destaque(page, "#simular-nuvem", "melhor") != melhor
    assert "252" in page.inner_text("#nota-periodo") and "9 pregões" in page.inner_text("#nota-periodo")


def test_pesos_proprios_marcam_a_carteira_e_soma_diferente_de_100_e_recusada(sala, precos, cotacoes):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page)
    _montar(page, ["PETR4", "VALE3"], 252)
    _simular(page, 1000)

    _pesos(page, {"PETR4": "30", "VALE3": "80"})
    assert "110,00%" in page.inner_text("#pesos-erro")
    assert page.locator("#simular-nuvem tr[data-carteira='proprios']").count() == 0
    _pesos(page, {"PETR4": "-20", "VALE3": "120"})
    assert "negativos" in page.inner_text("#pesos-erro")
    assert page.locator("#simular-nuvem tr[data-carteira='proprios']").count() == 0

    _pesos(page, {"PETR4": "20", "VALE3": "80"})
    page.wait_for_selector("#simular-nuvem tr[data-carteira='proprios']")
    assert page.inner_text("#pesos-erro") == ""
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 252)
    esperado = sim.posicionar([0.2, 0.8], rets, cotacoes["rf_anual"])
    marcado = _destaque(page, "#simular-nuvem", "proprios")
    for campo in ("retorno", "risco", "sharpe"):
        assert marcado[campo] == pytest.approx(esperado[campo], abs=1e-9)
    assert page.is_visible("#simular-nuvem .legenda-proprios")

    # Pesos iguais também seguem a referência, e a vírgula decimal é aceita.
    iguais = _destaque(page, "#simular-nuvem", "iguais")
    assert iguais["retorno"] == pytest.approx(sim.posicionar([0.5, 0.5], rets, cotacoes["rf_anual"])["retorno"], abs=1e-9)
    _pesos(page, {"PETR4": "12,5", "VALE3": "87,5%"})
    page.wait_for_function(
        "() => Math.abs(Number(document.querySelector(\"#simular-nuvem tr[data-carteira='proprios']\")"
        ".dataset.retorno) - %r) < 1e-9" % sim.posicionar([0.125, 0.875], rets, cotacoes["rf_anual"])["retorno"])

    page.click("#pesos-limpar")
    page.wait_for_selector("#simular-nuvem tr[data-carteira='proprios']", state="detached")


# ------------------------------------------------------------------ painel

def test_segundo_participante_aparece_no_painel_e_a_simulacao_dele_abre_igual(sala):
    contexto, url = sala
    primeira = _abrir(contexto, url)
    _entrar(primeira, "AB", "G01")
    _montar(primeira, ["PETR4", "VALE3"], 252)

    segunda = _abrir(contexto, url, limpar=False)
    _entrar(segunda, "CD", "G03")
    _montar(segunda, ["ITUB4", "WEGE3", "BBAS3"], 126)
    _simular(segunda, 100)
    _pesos(segunda, {"ITUB4": "50", "WEGE3": "25", "BBAS3": "25"})
    segunda.wait_for_selector("#simular-nuvem tr[data-carteira='proprios']")
    salvo = segunda.get_attribute("body", "data-salvo")
    segunda.wait_for_function("s => document.body.dataset.salvo !== s", arg=salvo)
    semente = segunda.get_attribute("#simular-nuvem .nuvem-tela", "data-semente")
    la = {c: _destaque(segunda, "#simular-nuvem", c) for c in ("melhor", "iguais", "proprios")}

    primeira.click(".sim-nav a[data-nav='painel']")
    primeira.wait_for_selector(".painel-linha[data-grupo='G03'] .painel-avatar[data-carteira='sim']")
    assert primeira.inner_text(".painel-linha[data-grupo='G01'] .painel-avatar") == "AB"
    avatar = primeira.locator(".painel-linha[data-grupo='G03'] .painel-avatar")
    assert avatar.inner_text() == "CD" and avatar.get_attribute("data-grupo") == "G03"
    identificador = avatar.get_attribute("data-id")
    avatar.click()
    primeira.wait_for_selector("#ver-nuvem .nuvem-tela[data-pronto='sim']")
    assert primeira.evaluate("location.hash") == "#ver=" + identificador
    assert primeira.get_attribute("#ver-nuvem .nuvem-tela", "data-semente") == semente
    assert primeira.get_attribute("#ver-nuvem .nuvem-tela", "data-n") == "100"
    assert "ITUB4, WEGE3, BBAS3" in primeira.inner_text("#ver-parametros")
    assert "126 pregões" in primeira.inner_text("#ver-parametros")
    # Mesmos ativos, período, n e semente: a nuvem recalculada é a mesma.
    aqui = {c: _destaque(primeira, "#ver-nuvem", c) for c in ("melhor", "iguais", "proprios")}
    assert aqui == la

    # O endereço da simulação abre direto, inclusive para quem não entrou.
    visita = _abrir(contexto, url + "#ver=" + identificador, limpar=False)
    visita.wait_for_selector("#ver-nuvem .nuvem-tela[data-pronto='sim']")
    assert _destaque(visita, "#ver-nuvem", "melhor") == la["melhor"]
    visita.goto(url + "#ver=nao-existe")
    visita.reload(wait_until="load")
    visita.wait_for_selector("#ver-vazio:not([hidden])")
    assert "não encontrado" in visita.inner_text("#ver-vazio-titulo")


def test_marcar_turno_atualiza_o_placar_do_grupo(sala):
    contexto, url = sala
    aluno = _abrir(contexto, url)
    _entrar(aluno, "EF", "G02")
    projetor = _abrir(contexto, url.replace("?demo=1", "?demo=1&painel=1"), limpar=False)
    projetor.wait_for_selector(".tela-painel:not([hidden])")
    celula = ".placar-celula[data-grupo='G02'][data-turno='%d'][data-contagem='%d']"
    projetor.wait_for_selector(celula % (1, 0))

    aluno.click(".sim-nav a[data-nav='progresso']")
    aluno.click("#turnos li:nth-child(1) label")
    aluno.click("#turnos li:nth-child(2) label")
    assert aluno.is_checked("input[data-turno='1']")
    projetor.wait_for_selector(celula % (1, 1))  # o painel atualiza sozinho
    projetor.wait_for_selector(celula % (2, 1))
    assert projetor.get_attribute(".placar-celula[data-grupo='G01'][data-turno='1']", "data-contagem") == "0"
    assert projetor.get_attribute(".placar-celula[data-grupo='G02'][data-turno='3']", "data-contagem") == "0"

    aluno.click("#turnos li:nth-child(1) label")  # desmarcar
    projetor.wait_for_selector(celula % (1, 0))
    aluno.reload(wait_until="load")
    aluno.wait_for_selector(".tela-progresso:not([hidden])")
    assert not aluno.is_checked("input[data-turno='1']") and aluno.is_checked("input[data-turno='2']")

    # Visitante entra no painel e fica fora do placar.
    visitante = _abrir(contexto, url, limpar=False)
    _entrar(visitante, "ZZ", "VIS")
    projetor.wait_for_selector(".painel-linha[data-grupo='VIS'] .painel-avatar")
    assert projetor.locator(".painel-linha[data-grupo='VIS'] .placar-celula").count() == 0


# ----------------------------------------------------------- banco fora do ar

def test_banco_fora_do_ar_nao_impede_entrar_montar_e_simular(navegador, servidor, precos):
    """Review Focus 2: sem ?demo=1 e com o Supabase inalcançável, a sala cai para memória."""
    contexto, erros = _contexto(navegador)
    try:
        contexto.route("**/*supabase*", lambda rota: rota.abort())
        page = _abrir(contexto, servidor)
        assert page.get_attribute("body", "data-sala") == "memoria"
        assert page.is_visible("#aviso") and "Sala sem conexão com o banco" in page.inner_text("#aviso")
        _entrar(page, "GH", "G04")
        _montar(page, ["PETR4", "VALE3"], 9)
        retorno, risco = sim.metricas([0.5, 0.5], sim.retornos(precos, ["PETR4", "VALE3"], 9))
        assert _numero(page, "#m-retorno") == pytest.approx(retorno, abs=1e-9)
        assert _numero(page, "#m-risco") == pytest.approx(risco, abs=1e-9)
        _simular(page, 10000)
        assert page.is_visible("#aviso")
        page.click(".sim-nav a[data-nav='painel']")
        page.wait_for_selector(".painel-linha[data-grupo='G04'] .painel-avatar[data-carteira='sim']")

        # Sem ?demo=1 a identidade fica no localStorage: a pessoa volta sem entrar de novo.
        page.reload(wait_until="load")
        page.wait_for_selector(".tela-painel:not([hidden])")
        assert page.inner_text("#eu-avatar") == "GH"
        page.click(".sim-nav a[data-nav='montar']")
        page.wait_for_selector("#montar-resultado:not([hidden])")
        assert _ativos(page) == ["PETR4", "VALE3"]
        assert [e for e in erros if FALHA_DE_REDE not in e] == []
    finally:
        contexto.close()


def test_arquivo_de_cotacoes_indisponivel_mostra_erro_com_nova_tentativa(navegador, servidor):
    contexto, erros = _contexto(navegador)
    try:
        falhar = {"sim": True}

        def rota_cotacoes(rota):
            if falhar["sim"]:
                rota.fulfill(status=503, body="fora do ar")
            else:
                rota.continue_()

        contexto.route("**/aula04-cotacoes.json", rota_cotacoes)
        page = contexto.new_page()
        page.goto(servidor + "?demo=1", wait_until="load")
        page.wait_for_selector(".tela-erro:not([hidden])")
        assert "503" in page.inner_text("#erro-detalhe")
        falhar["sim"] = False
        page.click("#tentar")
        page.wait_for_selector(".tela-entrar:not([hidden])")
        assert [e for e in erros if FALHA_DE_REDE not in e] == []
    finally:
        contexto.close()


# -------------------------------------------------------------------- celular

def test_em_390_por_844_nenhuma_tela_estoura_a_largura(navegador, servidor):
    contexto, erros = _contexto(navegador, 390, 844)
    try:
        url = servidor + "?demo=1"
        page = _abrir(contexto, url)

        def cabe(tela):
            largura = page.evaluate("document.documentElement.scrollWidth")
            assert largura <= 390, (tela, largura)

        cabe("entrar")
        _entrar(page, "MMM", "G03")
        cabe("montar vazio")
        _montar(page, ["PETR4", "VALE3", "ITUB4", "GOLD11", "IVVB11"], 9)
        page.click("label.chave")
        cabe("montar")
        _simular(page, 10000)
        _pesos(page, {"PETR4": "20", "VALE3": "20", "ITUB4": "20", "GOLD11": "20", "IVVB11": "20"})
        page.wait_for_selector("#simular-nuvem tr[data-carteira='proprios']")
        cabe("simular")
        page.click(".sim-nav a[data-nav='progresso']")
        page.click("#turnos li:nth-child(5) label")
        cabe("progresso")
        page.click(".sim-nav a[data-nav='painel']")
        page.wait_for_selector(".painel-avatar[data-carteira='sim']")
        cabe("painel")
        page.click(".painel-avatar")
        page.wait_for_selector("#ver-nuvem .nuvem-tela[data-pronto='sim']")
        cabe("ver")
        assert erros == []
    finally:
        contexto.close()


# ---------------------------------------------------------------------- telão

SESSAO = "m08-aula04-2026-11-18"
TELAO = "?demo=1&painel=1&telao=1"


def _semear(page, grupos, carteira_de=()):
    """Grava uma sala em memória: {grupo: quantidade}. `carteira_de` lista os ids com carteira."""
    sala = {"participantes": [], "carteiras": [], "turnos": []}
    for grupo, quantidade in grupos.items():
        for i in range(quantidade):
            pid = "m%s%02d" % (grupo.lower(), i)
            sala["participantes"].append({"id": pid, "iniciais": "%s%s" % (chr(65 + i % 26), chr(66 + i % 25)), "grupo": grupo})
            if pid in carteira_de:
                sala["carteiras"].append({"participante": pid, "ativos": ["PETR4", "VALE3", "ITUB4"], "pregoes": 252,
                                          "n": 1000, "semente": 77, "pesos": None})
    page.evaluate("s => localStorage.setItem('inteli-simulador-demo:%s', JSON.stringify(s))" % SESSAO, sala)


def _caixas(page, seletor):
    return page.eval_on_selector_all(
        seletor, "nos => nos.map(n => { const r = n.getBoundingClientRect();"
        " return {topo: r.top, base: r.bottom, esq: r.left, dir: r.right}; })")


def test_telao_mostra_os_cinco_blocos_sem_rolagem_em_1170_por_520_com_8_avatares(navegador, servidor):
    contexto, erros = _contexto(navegador, 1170, 520)
    try:
        page = _abrir(contexto, servidor + "?demo=1")
        _semear(page, {"G01": 8, "G02": 3, "G03": 1})
        page.goto(servidor + TELAO, wait_until="load")
        page.wait_for_selector(".painel-linha[data-grupo='G01'] .painel-avatar")

        # Só o painel: sem barra de navegação, sem rodapé e sem pedir entrada.
        assert not page.is_visible(".sim-topo") and not page.is_visible(".sim-rodape")
        assert not page.is_visible(".tela-entrar") and not page.is_visible(".tela-painel .tela-cabeca")
        assert page.evaluate("document.documentElement.scrollHeight") <= 520
        assert page.evaluate("document.documentElement.scrollWidth") <= 1170

        # Os quatro grupos e os visitantes, inteiros dentro da janela.
        assert page.eval_on_selector_all(".painel-linha", "nos => nos.map(n => n.dataset.grupo)") == \
            ["G01", "G02", "G03", "G04", "VIS"]
        for linha in _caixas(page, ".painel-linha"):
            assert linha["topo"] >= 0 and linha["base"] <= 520.5 and linha["base"] - linha["topo"] >= 60, linha

        # Oito avatares em uma linha só, com pelo menos 48px, sem invadir o placar.
        avatares = _caixas(page, ".painel-linha[data-grupo='G01'] .painel-avatar")
        placar = _caixas(page, ".painel-linha[data-grupo='G01'] .placar")[0]
        assert len(avatares) == 8 and len({round(a["topo"]) for a in avatares}) == 1
        assert all(a["dir"] - a["esq"] >= 48 and a["dir"] <= placar["esq"] for a in avatares)
        assert page.get_attribute(".painel-linha[data-grupo='G01']", "data-densidade") == "1"

        # Contagem de pessoas em destaque e atualização automática.
        assert page.inner_text("#telao-pessoas") == "12"
        assert page.evaluate("parseFloat(getComputedStyle(document.querySelector('#telao-pessoas')).fontSize)") >= 40
        aluno = _abrir(contexto, servidor + "?demo=1", limpar=False)
        _entrar(aluno, "ZZ", "G04")
        page.wait_for_function("document.querySelector('#telao-pessoas').textContent === '13'")
        page.wait_for_selector(".painel-linha[data-grupo='G04'] .painel-avatar")
        assert erros == []
    finally:
        contexto.close()


def test_telao_com_mais_de_10_no_grupo_reduz_o_avatar_e_cabe_na_linha(navegador, servidor):
    contexto, erros = _contexto(navegador, 1170, 520)
    try:
        page = _abrir(contexto, servidor + "?demo=1")
        _semear(page, {"G02": 17, "VIS": 4})
        page.goto(servidor + TELAO, wait_until="load")
        page.wait_for_selector(".painel-linha[data-grupo='G02'][data-densidade='2'] .painel-avatar")
        linha = _caixas(page, ".painel-linha[data-grupo='G02']")[0]
        avatares = _caixas(page, ".painel-linha[data-grupo='G02'] .painel-avatar")
        assert len(avatares) == 17
        assert all(a["topo"] >= linha["topo"] and a["base"] <= linha["base"] for a in avatares)
        assert len({round(a["topo"]) for a in avatares}) == 2  # duas linhas de avatares
        assert page.evaluate("document.documentElement.scrollHeight") <= 520
        assert erros == []
    finally:
        contexto.close()


@pytest.mark.parametrize("largura,altura", [(1170, 520), (1920, 1080)])
def test_avatar_no_telao_abre_a_simulacao_em_tela_inteira_e_volta_ao_painel(navegador, servidor, largura, altura):
    contexto, erros = _contexto(navegador, largura, altura)
    try:
        page = _abrir(contexto, servidor + "?demo=1")
        _semear(page, {"G01": 8, "G03": 2}, carteira_de=("mg0102",))
        page.goto(servidor + TELAO, wait_until="load")
        page.click(".painel-avatar[data-id='mg0102']")
        page.wait_for_selector("#ver-nuvem .nuvem-tela[data-pronto='sim']")
        assert page.evaluate("location.hash") == "#ver=mg0102"
        assert not page.is_visible(".sim-topo") and not page.is_visible(".sim-rodape")
        assert page.evaluate("document.documentElement.scrollHeight") <= altura

        # Nuvem grande: ocupa a altura livre abaixo da faixa e mais da metade da largura.
        nuvem = _caixas(page, "#ver-nuvem .nuvem-tela")[0]
        assert nuvem["base"] - nuvem["topo"] >= altura * 0.7 and nuvem["dir"] - nuvem["esq"] >= largura * 0.55
        assert nuvem["base"] <= altura + 0.5
        # Leitura em texto e os três números, inteiros dentro da janela.
        assert "maior Sharpe" in page.inner_text("#ver-nuvem .leitura")
        for seletor in ("#ver-nuvem .leitura", "#ver-numeros", "#ver-nuvem .legenda"):
            caixa = _caixas(page, seletor)[0]
            assert caixa["topo"] >= 0 and caixa["base"] <= altura + 0.5 and caixa["dir"] <= largura + 0.5, seletor
        assert page.locator("#ver-numeros dt").all_inner_texts() == ["Maior Sharpe", "Retorno anual", "Risco anual"]
        assert "Simulação de" in page.inner_text("#ver-titulo")

        page.click(".voltar a")
        page.wait_for_selector(".tela-painel:not([hidden]) .painel-linha[data-grupo='G01'] .painel-avatar")
        assert page.evaluate("location.hash") == "#painel"
        # Quem ainda não montou carteira abre o aviso, com o caminho de volta.
        page.click(".painel-avatar[data-id='mg0100']")
        page.wait_for_selector("#ver-vazio:not([hidden])")
        assert page.is_visible(".voltar a")
        # Endereço de outra tela não sai do painel.
        page.goto(servidor + TELAO + "#montar", wait_until="load")
        page.wait_for_selector(".tela-painel:not([hidden])")
        assert erros == []
    finally:
        contexto.close()


def test_painel_sem_telao_continua_com_a_barra_de_navegacao(sala):
    contexto, url = sala
    page = _abrir(contexto, url.replace("?demo=1", "?demo=1&painel=1"))
    page.wait_for_selector(".tela-painel:not([hidden])")
    assert page.is_visible(".sim-topo") and page.is_visible(".sim-rodape")
    assert not page.is_visible(".telao-cabeca")
    assert "sim-telao" not in page.get_attribute("body", "class")
    assert page.is_visible("#painel-vazio")  # sala vazia, como antes


# ---------------------------------------------------------- spec do grupo

def _consulta(url):
    import urllib.parse
    partes = urllib.parse.urlparse(url)
    return partes.path, {k: v[0] for k, v in urllib.parse.parse_qs(partes.query).items()}


def test_botao_da_spec_no_progresso_abre_a_tela_do_grupo_em_nova_aba(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page, "JR", "G02")
    page.click(".sim-nav a[data-nav='progresso']")
    page.wait_for_selector("#spec-t4[data-estado='pronto']")
    page.wait_for_selector("#spec-t5[data-estado='pronto']")
    assert page.locator(".turno-spec").count() == 2  # só os turnos 4 e 5
    assert page.inner_text("#spec-t4").strip() == "Abrir a spec do grupo"
    assert page.get_attribute("#spec-t4", "target") == "_blank"
    _, t5 = _consulta(page.get_attribute("#spec-t5", "href"))
    assert (t5["g"], t5["turno"], t5["a"]) == ("G02", "5", "JR")

    with contexto.expect_page() as nova:
        page.click("#spec-t4")
    spec = nova.value
    spec.wait_for_selector("form[data-adr][data-pronto='sim']")
    caminho, consulta = _consulta(spec.url)
    assert caminho == "/aulas/aula04-spec.html"
    assert (consulta["g"], consulta["turno"], consulta["a"]) == ("G02", "4", "JR")
    # Sala em memória: token fixo de demonstração e o parâmetro que a tela de spec aceita.
    assert consulta["t"] == "demo-aula04" and consulta["quiz-demo"] == "1"
    assert "Spec do turno 4: grupo G02" in spec.inner_text("#spec h2")
    assert spec.get_attribute("form[data-adr]", "data-iniciais") == "JR"
    assert spec.get_attribute("form[data-adr] [name=contexto]", "readonly") is None
    # A tela Progresso continua onde estava, e marcar o turno não depende do atalho.
    assert page.is_visible(".tela-progresso")
    page.click("#turnos li:nth-child(4) > label")
    assert page.is_checked("input[data-turno='4']")


def test_visitante_ve_o_botao_da_spec_desabilitado_com_a_explicacao(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page, "ZZ", "VIS")
    page.click(".sim-nav a[data-nav='progresso']")
    for turno in (4, 5):
        botao = "#spec-t%d" % turno
        page.wait_for_selector(botao + "[data-estado='visitante']")
        assert page.get_attribute(botao, "aria-disabled") == "true"
        assert page.get_attribute(botao, "href") is None
        assert "Visitante não edita a spec do grupo" in page.inner_text(botao + "-nota")
    page.click("#spec-t4")
    page.wait_for_timeout(300)
    assert len(contexto.pages) == 1  # nenhuma aba nova


def test_painel_tem_atalho_da_spec_somente_leitura_de_cada_grupo(sala):
    contexto, url = sala
    page = _abrir(contexto, url)
    _entrar(page, "AB", "G03")
    for endereco in (url.replace("?demo=1", "?demo=1&painel=1"), url.replace("?demo=1", TELAO)):
        painel = _abrir(contexto, endereco, limpar=False)
        painel.wait_for_selector(".painel-linha[data-grupo='G03'] .painel-avatar")
        for grupo in ("G01", "G02", "G03", "G04"):
            links = painel.locator(".painel-linha[data-grupo='%s'] .painel-specs a" % grupo)
            assert links.all_inner_texts() == ["Spec T4", "Spec T5"]
            for i, turno in enumerate(("4", "5")):
                caminho, consulta = _consulta(links.nth(i).get_attribute("href"))
                assert caminho.endswith("/aulas/aula04-spec.html")
                assert (consulta["g"], consulta["turno"], consulta["ver"]) == (grupo, turno, "1")
                assert "t" not in consulta and "a" not in consulta  # leitura não leva token
                assert links.nth(i).get_attribute("target") == "_blank"
        assert painel.locator(".painel-linha[data-grupo='VIS'] .painel-specs").count() == 0
        painel.close()

    painel = _abrir(contexto, url.replace("?demo=1", TELAO), limpar=False)
    with contexto.expect_page() as nova:
        painel.click(".painel-linha[data-grupo='G03'] .painel-specs a[data-turno='5']")
    leitura = nova.value
    leitura.wait_for_selector("[data-spec-leitura][data-pronto='sim']")
    assert "Spec do turno 5: grupo G03" in leitura.inner_text("#spec h2")
    assert leitura.locator("input, textarea").count() == 0


# Biblioteca do Supabase de mentira: a sala fica no modo "supabase" sem rede. As
# funções sim_entrar, sim_salvar e sim_marcar respondem; sim_spec_link devolve o
# erro do PostgREST para função inexistente até window.__specNoBanco virar true.
SUPABASE_FALSO = """
window.__sala = { participantes: [], carteiras: [], turnos: [] };
window.supabase = { createClient: function () {
  var s = window.__sala;
  function ok(data) { return Promise.resolve({ data: data, error: null }); }
  return {
    rpc: function (nome, a) {
      if (nome === 'sim_entrar') {
        var id = '0000000' + s.participantes.length + '-aaaa-4bbb-8ccc-000000000000';
        s.participantes.push({ id: id, sessao: a.p_sessao, iniciais: a.p_iniciais, grupo: a.p_grupo, criado_em: String(Date.now()) });
        return ok(id);
      }
      if (nome === 'sim_spec_link') {
        if (!window.__specNoBanco) {
          return Promise.resolve({ data: null, error: { message:
            'Could not find the function public.sim_spec_link(p_participante, p_turno) in the schema cache' } });
        }
        var p = s.participantes.filter(function (x) { return x.id === a.p_participante; })[0];
        return ok({ grupo: p.grupo, sessao: p.sessao + '-t' + a.p_turno, turno: a.p_turno, token: 'tok' + a.p_turno });
      }
      if (nome === 'sim_marcar') { s.turnos.push({ participante: a.p_participante, turno: a.p_turno }); return ok(true); }
      return ok(null);
    },
    from: function (tabela) {
      var linhas = s[tabela.replace('sim_', '')] || [];
      return { select: function () { return { eq: function () { return ok(linhas); } }; } };
    }
  };
} };
"""


def test_erro_do_rpc_da_spec_pede_o_professor_e_nao_derruba_a_sala(navegador, servidor):
    contexto, erros = _contexto(navegador)
    try:
        contexto.route("**/supabase.js", lambda rota: rota.fulfill(
            status=200, content_type="application/javascript", body=SUPABASE_FALSO))
        page = _abrir(contexto, servidor)
        assert page.get_attribute("body", "data-sala") == "supabase"
        _entrar(page, "JR", "G01")
        page.click(".sim-nav a[data-nav='progresso']")
        page.wait_for_selector("#spec-t4[data-estado='erro']")
        page.wait_for_selector("#spec-t5[data-estado='erro']")
        nota = page.inner_text("#spec-t4-nota")
        assert "ainda não está ativo no banco" in nota and "Chame o professor" in nota
        assert page.get_attribute("#spec-t4", "href") is None

        # A sala segue no banco: sem aviso de queda, turno marcado no banco e painel lido dele.
        assert not page.is_visible("#aviso")
        page.click("#turnos li:nth-child(1) label")
        page.wait_for_function("document.body.dataset.marcado === '1'")
        assert page.evaluate("window.__sala.turnos.length") == 1
        page.click(".sim-nav a[data-nav='painel']")
        page.wait_for_selector(".placar-celula[data-grupo='G01'][data-turno='1'][data-contagem='1']")
        assert not page.is_visible("#aviso")
        assert "quiz-demo" not in page.get_attribute(".painel-linha[data-grupo='G01'] .painel-specs a", "href")

        # Com a função aplicada no banco, o clique refaz o pedido e o atalho fica pronto.
        page.click(".sim-nav a[data-nav='progresso']")
        page.wait_for_selector("#spec-t4[data-estado='erro']")
        page.evaluate("window.__specNoBanco = true")
        page.click("#spec-t4")
        page.wait_for_selector("#spec-t4[data-estado='pronto']")
        _, consulta = _consulta(page.get_attribute("#spec-t4", "href"))
        assert consulta == {"g": "G01", "t": "tok4", "turno": "4", "a": "JR"}  # sem quiz-demo
        assert erros == []
    finally:
        contexto.close()
