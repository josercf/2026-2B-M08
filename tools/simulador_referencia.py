"""Solução de referência do simulador da Aula 04 em turnos (ADR-018).

É a conta que o portal faz em JavaScript (assets/js/simulador-nucleo.js) e que
os grupos reconstroem nos cinco turnos. Serve de gabarito para os testes do
notebook, do kit e da paridade com o portal.

Definições:
- retorno diário simples do preço ajustado, na janela comum dos ativos;
- retorno da carteira no pregão: soma dos pesos vezes os retornos do pregão;
- retorno anual: média dos retornos diários da carteira vezes 252;
- risco anual: desvio padrão amostral (ddof=1) vezes raiz de 252;
- Sharpe: (retorno anual - taxa livre de risco) / risco anual;
- sorteio dos pesos: uniforme normalizado.
"""
import numpy as np
import pandas as pd

PREGOES_ANO = 252


def retornos(precos, ativos, pregoes):
    """Últimos `pregoes` retornos diários da janela comum dos ativos pedidos."""
    comum = precos[list(ativos)].dropna()
    tabela = comum.pct_change().iloc[1:]
    if pregoes < 2 or len(tabela) < pregoes:
        raise ValueError(
            f"a janela comum tem {len(tabela)} retornos e foram pedidos {pregoes}")
    return tabela.tail(pregoes)


def retorno_do_dia(pesos, retornos_do_dia):
    """Retorno da carteira em um pregão."""
    return float(np.dot(np.asarray(pesos, dtype=float),
                        np.asarray(retornos_do_dia, dtype=float)))


def metricas(pesos, retornos):
    """Retorno anual e risco anual da carteira em N pregões."""
    serie = np.asarray(retornos, dtype=float) @ np.asarray(pesos, dtype=float)
    return (float(serie.mean() * PREGOES_ANO),
            float(serie.std(ddof=1) * np.sqrt(PREGOES_ANO)))


def sortear_pesos(k, rng):
    """Vetor de k pesos não negativos que soma 1."""
    if k < 1:
        raise ValueError("a carteira precisa de pelo menos um ativo")
    bruto = rng.random(k)
    return bruto / bruto.sum()


def simular(retornos, n, semente, rf):
    """Tabela com n carteiras sorteadas: pesos, retorno, risco e Sharpe."""
    tabela = pd.DataFrame(retornos)
    if n < 0:
        raise ValueError("o número de simulações não pode ser negativo")
    k = tabela.shape[1]
    rng = np.random.default_rng(semente)
    pesos = rng.random((n, k))
    pesos /= pesos.sum(axis=1, keepdims=True)
    media = tabela.mean().to_numpy() * PREGOES_ANO
    cov = tabela.cov().to_numpy() * PREGOES_ANO
    retorno = pesos @ media
    risco = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
    saida = pd.DataFrame(pesos, columns=[f"w_{c}" for c in tabela.columns])
    saida["retorno"] = retorno
    saida["risco"] = risco
    saida["sharpe"] = (retorno - rf) / risco
    return saida


def posicionar(pesos, retornos, rf):
    """Retorno, risco e Sharpe de uma carteira dada, para marcar na nuvem."""
    pesos = np.asarray(pesos, dtype=float)
    if abs(pesos.sum() - 1) > 1e-6 or (pesos < 0).any():
        raise ValueError("os pesos precisam ser não negativos e somar 1")
    retorno, risco = metricas(pesos, retornos)
    return {"retorno": retorno, "risco": risco, "sharpe": (retorno - rf) / risco}
