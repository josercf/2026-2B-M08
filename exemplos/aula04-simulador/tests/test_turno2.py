"""Testes do turno 2: metricas.

Rode com:  python -m pytest tests/test_turno2.py -q

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


def carregar_retornos(ativos, pregoes):
    """Retornos diários dos últimos `pregoes` pregões de dados/precos.csv, na janela comum."""
    precos = pd.read_csv(os.path.join(PASTA, "dados", "precos.csv"), index_col="data")
    return precos[ativos].dropna().pct_change().iloc[1:].tail(pregoes)


def carregar_rf():
    """Taxa livre de risco anual da aula, em fração, lida de dados/rf.txt."""
    with open(os.path.join(PASTA, "dados", "rf.txt"), encoding="utf-8") as arquivo:
        return float(arquivo.read().strip())


def test_exemplo_carteira_de_um_ativo_tem_o_retorno_e_o_risco_do_ativo():
    retornos = carregar_retornos(["PETR4", "VALE3"], 9)
    retorno, risco = simulador.metricas([1.0, 0.0], retornos)
    assert retorno == pytest.approx(retornos["PETR4"].mean() * 252)
    assert risco == pytest.approx(retornos["PETR4"].std(ddof=1) * np.sqrt(252))


def test_da_dupla_pesos_iguais_em_nove_pregoes():
    retornos = carregar_retornos(["PETR4", "VALE3"], 9)
    retorno, risco = simulador.metricas([0.5, 0.5], retornos)
    # ESCREVA AQUI: afirme que `retorno` e `risco` são o retorno anual e o risco anual que o
    # portal mostrou para PETR4 e VALE3 com pesos iguais em 9 pregões. Use um assert para
    # cada valor, em fração, com pytest.approx(valor, abs=0.0005).
    assert False, "escreva o assert deste teste e apague esta linha"
