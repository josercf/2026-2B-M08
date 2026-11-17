"""O portal (JavaScript) e a referência (Python) fazem a mesma conta.

O número que o aluno lê no portal é o valor esperado do teste que ele escreve
nos turnos 1 e 2, então as duas implementações não podem divergir.
"""
import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_slides  # noqa: E402
import simulador_referencia as sim  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

CSV = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados", "precos.csv")
CARTEIRAS = [
    (["PETR4", "VALE3"], [0.5, 0.5], 9),
    (["PETR4", "VALE3"], [0.2, 0.8], 252),
    (["ITUB4", "WEGE3", "BOVA11"], [1 / 3, 1 / 3, 1 / 3], 21),
    (["ITUB4", "WEGE3", "GOLD11", "IVVB11"], [0.1, 0.2, 0.3, 0.4], 63),
    (["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"], [0.2] * 5, 126),
    (["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"], [0.05, 0.15, 0.25, 0.35, 0.2], 252),
]


@pytest.fixture(scope="module")
def pagina():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page()
        page.goto("http://127.0.0.1:%d/tools/tests/fixture_simulador_nucleo.html" % porta,
                  wait_until="load")
        page.wait_for_selector("body[data-pronto='sim']", state="attached")
        try:
            yield page
        finally:
            navegador.close()
    httpd.shutdown()


@pytest.fixture(scope="module")
def precos():
    return pd.read_csv(CSV, index_col="data")


@pytest.mark.parametrize("ativos,pesos,pregoes", CARTEIRAS)
def test_metricas_do_portal_sao_as_da_referencia(pagina, precos, ativos, pesos, pregoes):
    js = pagina.evaluate(
        "([a, w, n]) => { const r = SimuladorNucleo.retornos(cotacoes, a, n);"
        " const m = SimuladorNucleo.metricas(w, r.linhas);"
        " return [m.retorno, m.risco, r.datas[0], r.datas.length,"
        " SimuladorNucleo.retornoDoDia(w, r.linhas[0])]; }",
        [ativos, pesos, pregoes])
    rets = sim.retornos(precos, ativos, pregoes)
    retorno, risco = sim.metricas(pesos, rets)
    # O arquivo guarda quatro casas, igual nos dois lados; sobra só o erro de ponto flutuante.
    assert js[0] == pytest.approx(retorno, abs=1e-9)
    assert js[1] == pytest.approx(risco, abs=1e-9)
    assert js[2] == rets.index[0] and js[3] == pregoes
    assert js[4] == pytest.approx(sim.retorno_do_dia(pesos, rets.iloc[0]), abs=1e-12)


def test_simulacao_do_portal_confere_com_metricas_e_repete_com_a_semente(pagina, precos):
    ativos = ["PETR4", "VALE3", "ITUB4"]
    js = pagina.evaluate(
        "([a]) => { const r = SimuladorNucleo.retornos(cotacoes, a, 252);"
        " const s1 = SimuladorNucleo.simular(r.linhas, 200, 42, 0.14);"
        " const s2 = SimuladorNucleo.simular(r.linhas, 200, 42, 0.14);"
        " const s3 = SimuladorNucleo.simular(r.linhas, 200, 43, 0.14);"
        " return { pesos: s1.pesos, retorno: Array.from(s1.retorno), risco: Array.from(s1.risco),"
        " sharpe: Array.from(s1.sharpe), igual: Array.from(s2.retorno).join() === Array.from(s1.retorno).join(),"
        " outra: Array.from(s3.retorno).join() !== Array.from(s1.retorno).join() }; }",
        [ativos])
    assert js["igual"] and js["outra"]
    rets = sim.retornos(precos, ativos, 252)
    for pesos, retorno, risco, sharpe in zip(js["pesos"], js["retorno"], js["risco"], js["sharpe"]):
        assert abs(sum(pesos) - 1) < 1e-12 and min(pesos) >= 0
        esperado_ret, esperado_risco = sim.metricas(pesos, rets)
        assert retorno == pytest.approx(esperado_ret, abs=1e-9)
        assert risco == pytest.approx(esperado_risco, abs=1e-9)
        assert sharpe == pytest.approx((esperado_ret - 0.14) / esperado_risco, abs=1e-8)


def test_portal_informa_a_janela_disponivel_e_recusa_periodo_maior(pagina, precos):
    tardio = precos.notna().sum().idxmin()
    cotacoes = int(precos[tardio].notna().sum())
    assert pagina.evaluate("([a]) => SimuladorNucleo.pregoesDisponiveis(cotacoes, a)",
                           [["PETR4", tardio]]) == cotacoes - 1
    assert pagina.evaluate("() => SimuladorNucleo.pregoesDisponiveis(cotacoes, ['PETR4', 'XXXX9'])") == 0
    erro = pagina.evaluate(
        "([a, n]) => { try { SimuladorNucleo.retornos(cotacoes, a, n); return ''; }"
        " catch (e) { return e.message; } }", [["PETR4", tardio], cotacoes])
    assert "janela comum" in erro


def test_dez_mil_carteiras_de_cinco_ativos_saem_em_menos_de_dois_segundos(pagina):
    ms = pagina.evaluate(
        "() => { const r = SimuladorNucleo.retornos(cotacoes, ['PETR4','VALE3','ITUB4','WEGE3','BBAS3'], 252);"
        " const t = performance.now(); SimuladorNucleo.simular(r.linhas, 10000, 1, 0.14);"
        " return performance.now() - t; }")
    assert ms < 2000
