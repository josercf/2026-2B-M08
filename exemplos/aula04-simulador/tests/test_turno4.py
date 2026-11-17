"""Testes do turno 4: simular.

Rode com:  python -m pytest tests/test_turno4.py -q

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


def test_exemplo_tabela_tem_uma_linha_por_carteira_e_as_colunas_da_spec():
    retornos = carregar_retornos(["PETR4", "VALE3", "ITUB4"], 126)
    tabela = simulador.simular(retornos, 100, 42, carregar_rf())
    assert len(tabela) == 100
    assert list(tabela.columns) == ["w_PETR4", "w_VALE3", "w_ITUB4", "retorno", "risco", "sharpe"]


def test_da_dupla_mesma_semente_devolve_a_mesma_tabela():
    retornos = carregar_retornos(["PETR4", "VALE3", "ITUB4"], 126)
    primeira = simulador.simular(retornos, 100, 42, carregar_rf())
    segunda = simulador.simular(retornos, 100, 42, carregar_rf())
    # ESCREVA AQUI: afirme que as duas tabelas são iguais, porque a semente é a mesma.
    # Pista de escrita: primeira.equals(segunda) devolve True quando as tabelas são iguais.
    assert False, "escreva o assert deste teste e apague esta linha"
