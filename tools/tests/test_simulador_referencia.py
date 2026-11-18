"""Solução de referência do simulador da Aula 04 em turnos."""
import os
import sys
import time

import numpy as np
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import simulador_referencia as sim  # noqa: E402

CSV = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados", "precos.csv")


@pytest.fixture(scope="module")
def precos():
    return pd.read_csv(CSV, index_col="data")


def test_carteira_de_um_ativo_devolve_o_retorno_e_o_risco_do_ativo(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 252)
    retorno, risco = sim.metricas([1.0, 0.0], rets)
    assert retorno == pytest.approx(rets["PETR4"].mean() * 252, abs=1e-12)
    assert risco == pytest.approx(rets["PETR4"].std() * 252 ** 0.5, abs=1e-12)


def test_pesos_iguais_conferem_com_a_serie_diaria_da_carteira(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 9)
    serie = 0.5 * rets["PETR4"] + 0.5 * rets["VALE3"]
    retorno, risco = sim.metricas([0.5, 0.5], rets)
    assert retorno == pytest.approx(serie.mean() * 252, abs=1e-12)
    assert risco == pytest.approx(serie.std(ddof=1) * 252 ** 0.5, abs=1e-12)
    assert sim.retorno_do_dia([0.5, 0.5], rets.iloc[0]) == pytest.approx(serie.iloc[0], abs=1e-15)


def test_retornos_devolve_os_ultimos_pregoes_ate_o_corte(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3", "ITUB4"], 9)
    assert rets.shape == (9, 3)
    assert rets.index[-1] == "2026-11-13"


def test_pedir_mais_pregoes_do_que_a_janela_tem_e_erro(precos):
    with pytest.raises(ValueError, match="janela comum"):
        sim.retornos(precos, ["PETR4", "VALE3"], 5000)


def test_ativo_que_comeca_depois_encurta_a_janela_comum(precos):
    tardio = precos.notna().sum().idxmin()
    cotacoes = int(precos[tardio].notna().sum())
    assert cotacoes < len(precos)
    assert len(sim.retornos(precos, ["PETR4", tardio], cotacoes - 1)) == cotacoes - 1
    with pytest.raises(ValueError):
        sim.retornos(precos, ["PETR4", tardio], cotacoes)


@pytest.mark.parametrize("k", [2, 5, 20])
def test_pesos_sorteados_somam_um_e_nao_sao_negativos(k):
    pesos = sim.sortear_pesos(k, np.random.default_rng(42))
    assert pesos.shape == (k,)
    assert abs(pesos.sum() - 1) < 1e-12
    assert (pesos >= 0).all()


def test_mesma_semente_devolve_a_mesma_tabela(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3", "ITUB4"], 252)
    a = sim.simular(rets, 500, 7, 0.14)
    b = sim.simular(rets, 500, 7, 0.14)
    c = sim.simular(rets, 500, 8, 0.14)
    pd.testing.assert_frame_equal(a, b)
    assert not a["retorno"].equals(c["retorno"])
    assert list(a.columns) == ["w_PETR4", "w_VALE3", "w_ITUB4", "retorno", "risco", "sharpe"]
    assert np.allclose(a[["w_PETR4", "w_VALE3", "w_ITUB4"]].sum(axis=1), 1)


def test_tabela_da_simulacao_confere_com_metricas_linha_a_linha(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3", "WEGE3"], 126)
    tabela = sim.simular(rets, 50, 3, 0.14)
    for _, linha in tabela.iterrows():
        retorno, risco = sim.metricas(linha[:3].to_numpy(), rets)
        assert linha["retorno"] == pytest.approx(retorno, abs=1e-10)
        assert linha["risco"] == pytest.approx(risco, abs=1e-10)
        assert linha["sharpe"] == pytest.approx((retorno - 0.14) / risco, abs=1e-9)


def test_zero_simulacoes_devolve_tabela_vazia_com_as_colunas(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 63)
    tabela = sim.simular(rets, 0, 1, 0.14)
    assert len(tabela) == 0
    assert list(tabela.columns) == ["w_PETR4", "w_VALE3", "retorno", "risco", "sharpe"]


@pytest.mark.parametrize("k", [2, 5, 20])
def test_dez_mil_simulacoes_em_menos_de_dez_segundos(precos, k):
    ativos = list(precos.dropna(axis=1).columns[:k])
    rets = sim.retornos(precos, ativos, 252)
    inicio = time.perf_counter()
    tabela = sim.simular(rets, 10_000, 42, 0.14)
    assert time.perf_counter() - inicio < 10
    assert len(tabela) == 10_000


def test_posicionar_recusa_pesos_que_nao_somam_um(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 63)
    ponto = sim.posicionar([0.2, 0.8], rets, 0.14)
    retorno, risco = sim.metricas([0.2, 0.8], rets)
    assert ponto == pytest.approx({"retorno": retorno, "risco": risco,
                                   "sharpe": (retorno - 0.14) / risco})
    with pytest.raises(ValueError):
        sim.posicionar([0.5, 0.6], rets, 0.14)
    with pytest.raises(ValueError):
        sim.posicionar([1.5, -0.5], rets, 0.14)


# --- turno 6: otimização de Markowitz ------------------------------------------

RF = 0.14
# Tolerâncias numéricas do turno 6: o SLSQP roda com ftol de 1e-12, e a nuvem
# pode encostar na ótima (com 2 ativos ela cobre a reta inteira dos pesos).
TOL_PESO = 1e-9
TOL_RISCO = 1e-8
TOL_SHARPE = 1e-6
CESTAS = {2: ["ITUB4", "WEGE3"], 5: ["PETR4", "VALE3", "ITUB4", "WEGE3", "ABEV3"]}


def _cesta(precos, k):
    ativos = CESTAS.get(k) or list(precos.dropna(axis=1).columns[:k])
    return sim.retornos(precos, ativos, 252)


def _pesos_validos(pesos, k):
    pesos = np.asarray(pesos)
    assert pesos.shape == (k,)
    assert abs(pesos.sum() - 1) < TOL_PESO
    assert pesos.min() >= 0 and pesos.max() <= 1


@pytest.mark.parametrize("k", [2, 5, 15])
def test_pesos_das_carteiras_otimas_somam_um_e_ficam_entre_zero_e_um(precos, k):
    rets = _cesta(precos, k)
    _pesos_validos(sim.variancia_minima(rets), k)
    _pesos_validos(sim.maximo_sharpe(rets, RF), k)


@pytest.mark.parametrize("k", [2, 5, 15])
def test_nenhuma_das_dez_mil_carteiras_sorteadas_supera_as_otimas(precos, k):
    rets = _cesta(precos, k)
    nuvem = sim.simular(rets, 10_000, 42, RF)
    minima = sim.posicionar(sim.variancia_minima(rets), rets, RF)
    sharpe = sim.posicionar(sim.maximo_sharpe(rets, RF), rets, RF)
    assert nuvem["risco"].min() >= minima["risco"] - TOL_RISCO
    assert nuvem["sharpe"].max() <= sharpe["sharpe"] + TOL_SHARPE
    assert minima["risco"] <= sharpe["risco"] + TOL_RISCO
    assert sharpe["sharpe"] >= minima["sharpe"] - TOL_SHARPE


@pytest.mark.parametrize("k", [2, 5, 15])
def test_fronteira_tem_cinquenta_pontos_retorno_crescente_e_domina_a_nuvem(precos, k):
    rets = _cesta(precos, k)
    fronteira = sim.fronteira(rets)
    assert len(fronteira) == 50
    assert list(fronteira.columns) == ["w_%s" % c for c in rets.columns] + ["retorno", "risco"]
    assert (np.diff(fronteira["retorno"]) > 0).all()
    assert (np.diff(fronteira["risco"]) > -TOL_RISCO).all()
    nuvem = sim.simular(rets, 10_000, 42, RF)
    for _, ponto in fronteira.iterrows():
        _pesos_validos(ponto.iloc[:k].to_numpy(), k)
        retorno, risco = sim.metricas(ponto.iloc[:k].to_numpy(), rets)
        assert ponto["retorno"] == pytest.approx(retorno, abs=1e-9)
        assert ponto["risco"] == pytest.approx(risco, abs=1e-9)
        acima = nuvem[nuvem["retorno"] >= ponto["retorno"]]
        assert acima.empty or acima["risco"].min() >= ponto["risco"] - TOL_RISCO


def test_fronteira_comeca_na_variancia_minima_e_termina_no_ativo_de_maior_retorno(precos):
    rets = _cesta(precos, 5)
    fronteira = sim.fronteira(rets)
    minima = sim.variancia_minima(rets)
    retorno, risco = sim.metricas(minima, rets)
    assert fronteira["retorno"].iloc[0] == pytest.approx(retorno, abs=1e-9)
    assert fronteira["risco"].iloc[0] == pytest.approx(risco, abs=1e-7)
    assert np.allclose(fronteira.iloc[0, :5].to_numpy(), minima, atol=1e-4)
    medias = rets.mean() * 252
    assert fronteira["retorno"].iloc[-1] == pytest.approx(medias.max(), abs=1e-12)
    assert fronteira["w_%s" % medias.idxmax()].iloc[-1] == pytest.approx(1, abs=1e-6)
    assert np.allclose(np.diff(fronteira["retorno"], 2), 0, atol=1e-12)


def test_fronteira_aceita_outro_numero_de_pontos_e_recusa_menos_de_dois(precos):
    rets = _cesta(precos, 5)
    assert len(sim.fronteira(rets, pontos=12)) == 12
    assert len(sim.fronteira(rets, 2)) == 2
    with pytest.raises(ValueError, match="dois pontos"):
        sim.fronteira(rets, 1)


def test_ativo_de_retorno_dominante_recebe_todo_o_peso_no_maximo_sharpe():
    rng = np.random.default_rng(0)
    ruido = rng.normal(0, 0.01, (252, 4))
    ruido -= ruido.mean(axis=0)
    rets = pd.DataFrame(ruido + np.array([-0.0005, 0.002, -0.0005, -0.0005]),
                        columns=["A", "B", "C", "D"])
    pesos = sim.maximo_sharpe(rets, 0.10)
    _pesos_validos(pesos, 4)
    assert pesos[1] > 0.99
    assert sim.variancia_minima(rets).max() < 0.5


def test_carteira_de_um_ativo_so_recebe_peso_um(precos):
    rets = sim.retornos(precos, ["PETR4"], 63)
    assert sim.variancia_minima(rets) == pytest.approx([1.0])
    assert sim.maximo_sharpe(rets, RF) == pytest.approx([1.0])


def test_otimizacao_que_nao_converge_levanta_erro(precos, monkeypatch):
    class Falhou:
        success, message, x = False, "limite de iterações", np.array([0.5, 0.5])

    monkeypatch.setattr(sim, "minimize", lambda *a, **k: Falhou())
    with pytest.raises(RuntimeError, match="não convergiu: limite de iterações"):
        sim.variancia_minima(_cesta(precos, 2))


def test_fronteira_de_cinquenta_pontos_com_cinco_ativos_em_menos_de_dez_segundos(precos):
    rets = _cesta(precos, 5)
    inicio = time.perf_counter()
    fronteira = sim.fronteira(rets)
    assert time.perf_counter() - inicio < 10
    assert len(fronteira) == 50


# ------------------------------------------------------------ valor em risco

def test_var_historico_e_parametrico_de_uma_serie_conhecida():
    # Série de um ativo com média zero: percentil 5% por interpolação linear
    # em (n - 1) x 0,05 = 0,2, ou seja -0,04 + 0,2 x 0,02 = -0,036.
    serie = np.array([[-0.04], [-0.02], [0.01], [0.02], [0.03]])
    historico, parametrico = sim.valor_em_risco([1.0], serie)
    assert historico == pytest.approx(0.036, abs=1e-12)
    desvio = np.sqrt(0.0034 / 4)
    assert parametrico == pytest.approx(1.6448536269514722 * desvio, abs=1e-12)


def test_var_e_perda_positiva_e_a_carteira_so_com_ganhos_tem_var_negativo():
    ganhos = np.array([[0.01], [0.02], [0.03], [0.04], [0.05]])
    historico, parametrico = sim.valor_em_risco([1.0], ganhos)
    assert historico < 0 and parametrico < 0


def test_var_da_carteira_usa_a_serie_diaria_ponderada(precos):
    rets = sim.retornos(precos, ["PETR4", "VALE3"], 252)
    serie = 0.3 * rets["PETR4"] + 0.7 * rets["VALE3"]
    historico, parametrico = sim.valor_em_risco([0.3, 0.7], rets)
    assert historico == pytest.approx(-np.percentile(serie, 5), abs=1e-12)
    assert parametrico == pytest.approx(1.6448536269514722 * serie.std(ddof=1) - serie.mean(),
                                        abs=1e-12)
