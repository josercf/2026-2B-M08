"""Testes do turno 6: variancia_minima, maximo_sharpe e fronteira.

Rode com:  python -m pytest tests/test_turno6.py -q

O primeiro teste é um exemplo completo. O segundo é da dupla: escreva o assert
à mão, antes de implementar a função, e rode para ver o teste falhar.
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA)

import simulador  # noqa: E402

ATIVOS = ["PETR4", "VALE3", "ITUB4", "WEGE3", "ABEV3"]


def carregar_retornos(ativos, pregoes):
    """Retornos diários dos últimos `pregoes` pregões de dados/precos.csv, na janela comum."""
    precos = pd.read_csv(os.path.join(PASTA, "dados", "precos.csv"), index_col="data")
    return precos[ativos].dropna().pct_change().iloc[1:].tail(pregoes)


def carregar_rf():
    """Taxa livre de risco anual da aula, em fração, lida de dados/rf.txt."""
    with open(os.path.join(PASTA, "dados", "rf.txt"), encoding="utf-8") as arquivo:
        return float(arquivo.read().strip())


def test_exemplo_variancia_minima_soma_um_e_tem_risco_menor_que_pesos_iguais():
    retornos = carregar_retornos(ATIVOS, 252)
    pesos = simulador.variancia_minima(retornos)
    assert len(pesos) == 5
    assert abs(sum(pesos) - 1) < 0.000001
    assert min(pesos) > -0.000001 and max(pesos) < 1.000001
    _, risco_da_otima = simulador.metricas(pesos, retornos)
    _, risco_de_pesos_iguais = simulador.metricas([0.2] * 5, retornos)
    assert risco_da_otima < risco_de_pesos_iguais


def test_da_dupla_nenhuma_carteira_sorteada_supera_o_sharpe_da_otima():
    retornos = carregar_retornos(ATIVOS, 252)
    rf = carregar_rf()
    nuvem = simulador.simular(retornos, 10_000, 42, rf)
    retorno, risco = simulador.metricas(simulador.maximo_sharpe(retornos, rf), retornos)
    sharpe_da_otima = (retorno - rf) / risco
    # ESCREVA AQUI: afirme que o maior Sharpe entre as 10.000 carteiras sorteadas não passa
    # do Sharpe da carteira ótima, com folga de 0,0001 para o arredondamento do otimizador.
    # Pista de escrita: nuvem["sharpe"].max() devolve o maior Sharpe da coluna.
    assert False, "escreva o assert deste teste e apague esta linha"
