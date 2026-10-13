"""Análise de risco e retorno (A2): retornos diários e métricas anualizadas por 252."""
import numpy as np

PREGOES_ANO = 252


def retornos(precos, inicio=None, fim=None):
    """Retornos diários na janela comum dos ativos, entre inicio e fim (ADR-009).

    O retorno é calculado na série inteira, sem preencher nada (fill_method=None),
    e só depois recortado: o primeiro retorno do período compara o primeiro
    pregão dele com o pregão anterior. O dropna final deixa só os pregões em que
    todos os ativos têm retorno, a janela comum. Com a GOLD11 no pedido, ela
    começa em 14/12/2020, e a API devolve início, fim e número de retornos para
    o gestor ver a janela usada.
    """
    return precos.pct_change(fill_method=None).iloc[1:].loc[inicio:fim].dropna()


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
