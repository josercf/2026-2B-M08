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
