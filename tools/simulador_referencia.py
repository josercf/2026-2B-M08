"""Solução de referência do simulador da Aula 04 em turnos (ADR-018).

É a conta que o portal faz em JavaScript (assets/js/simulador-nucleo.js) e que
os grupos reconstroem nos cinco turnos do encontro, mais a otimização de
Markowitz do turno 6, feito depois do encontro. Serve de gabarito para os testes
do notebook, do kit e da paridade com o portal.

Definições:
- retorno diário simples do preço ajustado, na janela comum dos ativos;
- retorno da carteira no pregão: soma dos pesos vezes os retornos do pregão;
- retorno anual: média dos retornos diários da carteira vezes 252;
- risco anual: desvio padrão amostral (ddof=1) vezes raiz de 252;
- Sharpe: (retorno anual - taxa livre de risco) / risco anual;
- sorteio dos pesos: uniforme normalizado;
- otimização (turno 6): scipy.optimize.minimize com SLSQP, pesos entre 0 e 1
  (sem venda a descoberto) e soma 1, partindo de pesos iguais. É a mesma
  abordagem de tools/medidas_aula04.py.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize

PREGOES_ANO = 252
TOLERANCIA = 1e-12   # ftol do SLSQP: o padrão (1e-6) para antes do ótimo da variância


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


# --- Turno 6: otimização de Markowitz ----------------------------------------

def _momentos(retornos):
    """Tabela, vetor de retornos anuais e matriz de covariância anual dos ativos."""
    tabela = pd.DataFrame(retornos)
    return (tabela, tabela.mean().to_numpy() * PREGOES_ANO,
            tabela.cov().to_numpy() * PREGOES_ANO)


def _otimizar(objetivo, k, restricoes=(), x0=None):
    """Minimiza `objetivo` nos pesos, com soma 1 e cada peso entre 0 e 1."""
    restricoes = [{"type": "eq", "fun": lambda w: w.sum() - 1}] + list(restricoes)
    x0 = np.full(k, 1 / k) if x0 is None else np.asarray(x0, dtype=float)
    resultado = minimize(objetivo, x0, method="SLSQP", bounds=[(0, 1)] * k,
                         constraints=restricoes,
                         options={"ftol": TOLERANCIA, "maxiter": 500})
    if not resultado.success:
        raise RuntimeError("o otimizador SLSQP não convergiu: %s" % resultado.message)
    pesos = np.clip(resultado.x, 0, 1)   # tira o resíduo numérico fora dos limites
    return pesos / pesos.sum()


def variancia_minima(retornos):
    """Pesos da carteira de menor risco anual, sem venda a descoberto."""
    _, _, cov = _momentos(retornos)
    return _otimizar(lambda w: w @ cov @ w, len(cov))


def maximo_sharpe(retornos, rf):
    """Pesos da carteira de maior Índice de Sharpe, sem venda a descoberto."""
    _, media, cov = _momentos(retornos)
    return _otimizar(lambda w: -(w @ media - rf) / np.sqrt(w @ cov @ w), len(media))


def fronteira(retornos, pontos=50):
    """Fronteira eficiente: a carteira de menor risco para cada retorno alvo.

    Os alvos são igualmente espaçados, do retorno da carteira de variância
    mínima até o maior retorno anual entre os ativos. Cada otimização parte dos
    pesos do alvo anterior.
    """
    if pontos < 2:
        raise ValueError("a fronteira precisa de pelo menos dois pontos")
    tabela, media, cov = _momentos(retornos)
    k = len(media)
    x0 = variancia_minima(tabela)
    alvos = np.linspace(x0 @ media, media.max(), pontos)
    linhas = []
    for alvo in alvos:
        x0 = _otimizar(lambda w: w @ cov @ w, k,
                       [{"type": "eq", "fun": lambda w, a=alvo: w @ media - a}], x0=x0)
        linhas.append(x0)
    saida = pd.DataFrame(np.array(linhas), columns=[f"w_{c}" for c in tabela.columns])
    saida["retorno"] = alvos
    saida["risco"] = [float(np.sqrt(w @ cov @ w)) for w in linhas]
    return saida
