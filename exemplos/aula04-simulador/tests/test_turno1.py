"""Testes do turno 1: retorno_do_dia.

Rode com:  python -m pytest tests/test_turno1.py -q

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


def test_exemplo_carteira_de_um_ativo_devolve_o_retorno_do_ativo():
    retornos = carregar_retornos(["PETR4", "VALE3"], 9)
    primeiro_pregao = retornos.iloc[0].to_numpy()
    resultado = simulador.retorno_do_dia([1.0, 0.0], primeiro_pregao)
    assert resultado == pytest.approx(primeiro_pregao[0])


def test_da_dupla_pesos_iguais_no_primeiro_pregao():
    retornos = carregar_retornos(["PETR4", "VALE3"], 9)
    primeiro_pregao = retornos.iloc[0].to_numpy()
    resultado = simulador.retorno_do_dia([0.5, 0.5], primeiro_pregao)
    # ESCREVA AQUI: afirme que `resultado` é o retorno da carteira PETR4 e VALE3 com pesos
    # iguais no primeiro pregão. Use o valor que o portal mostrou, em fração, com
    # pytest.approx(valor, abs=0.0005).
    assert False, "escreva o assert deste teste e apague esta linha"
