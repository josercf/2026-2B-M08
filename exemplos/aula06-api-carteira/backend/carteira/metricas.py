"""Análise de risco e retorno (A2): retornos diários e métricas anualizadas por 252."""
import numpy as np

PREGOES_ANO = 252


def retornos(precos):
    return precos.pct_change().dropna()


def retorno_anual(ret):
    return ret.mean() * PREGOES_ANO


def volatilidade_anual(ret):
    return ret.std() * np.sqrt(PREGOES_ANO)


def covariancia_anual(ret):
    return ret.cov() * PREGOES_ANO


def correlacao_media(ret):
    """Correlação média de cada ativo com os demais (diagonal fora)."""
    corr = ret.corr()
    n = len(corr)
    return (corr.sum() - 1) / (n - 1)
