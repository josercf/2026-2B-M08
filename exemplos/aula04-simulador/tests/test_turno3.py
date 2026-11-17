"""Testes do turno 3: sortear_pesos.

Rode com:  python -m pytest tests/test_turno3.py -q

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


def test_exemplo_pesos_sorteados_somam_um():
    pesos = simulador.sortear_pesos(5, np.random.default_rng(42))
    assert len(pesos) == 5
    assert sum(pesos) == pytest.approx(1.0)


def test_da_dupla_nenhum_peso_e_negativo():
    pesos = simulador.sortear_pesos(20, np.random.default_rng(42))
    # ESCREVA AQUI: afirme que nenhum dos 20 pesos é negativo.
    # Pista de escrita: all(condição for peso in pesos) é verdadeiro quando a condição
    # vale para todos os pesos.
    assert False, "escreva o assert deste teste e apague esta linha"
