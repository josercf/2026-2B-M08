"""Testes do turno 5: requisito de tempo de simular e posicionar.

Rode com:  python -m pytest tests/test_turno5.py -q

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

import time  # noqa: E402


def test_exemplo_dez_mil_simulacoes_com_cinco_ativos_em_menos_de_dez_segundos():
    retornos = carregar_retornos(["PETR4", "VALE3", "ITUB4", "WEGE3", "ABEV3"], 252)
    inicio = time.perf_counter()
    tabela = simulador.simular(retornos, 10_000, 42, carregar_rf())
    duracao = time.perf_counter() - inicio
    assert len(tabela) == 10_000
    assert duracao < 10


def test_da_dupla_posicionar_recusa_pesos_que_nao_somam_um():
    retornos = carregar_retornos(["PETR4", "VALE3"], 63)
    # ESCREVA AQUI: afirme que posicionar levanta ValueError quando os pesos somam 1,1.
    # Pista de escrita:
    #     with pytest.raises(ValueError):
    #         simulador.posicionar([0.5, 0.6], retornos, carregar_rf())
    assert False, "escreva o assert deste teste e apague esta linha"
