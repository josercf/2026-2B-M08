"""Otimizador (A4): variância mínima, máximo Sharpe e fronteira de 50 pontos.

SLSQP do SciPy, pesos somando 1 e nenhum negativo (sem venda a descoberto).
PROBLEMAS_RESOLVIDOS conta cada chamada ao SLSQP: é o que o cache da API evita.
"""
import numpy as np
from scipy.optimize import minimize

PONTOS_FRONTEIRA = 50
PROBLEMAS_RESOLVIDOS = 0


def _resolver(objetivo, n, restricoes=()):
    global PROBLEMAS_RESOLVIDOS
    PROBLEMAS_RESOLVIDOS += 1
    inicial = np.full(n, 1.0 / n)
    resultado = minimize(
        objetivo, inicial, method="SLSQP", bounds=[(0.0, 1.0)] * n,
        constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}, *restricoes],
        options={"ftol": 1e-12, "maxiter": 500},
    )
    if not resultado.success:
        raise RuntimeError("SLSQP não convergiu: " + resultado.message)
    pesos = np.clip(resultado.x, 0.0, None)
    return pesos / pesos.sum()


def metricas_carteira(pesos, mu, cov, rf):
    retorno = float(pesos @ mu)
    vol = float(np.sqrt(pesos @ cov @ pesos))
    return {"retorno": retorno, "volatilidade": vol, "sharpe": (retorno - rf) / vol}


def variancia_minima(mu, cov):
    return _resolver(lambda w: w @ cov @ w, len(mu))


def maximo_sharpe(mu, cov, rf):
    return _resolver(lambda w: -(w @ mu - rf) / np.sqrt(w @ cov @ w), len(mu))


def fronteira(mu, cov, base, pontos=PONTOS_FRONTEIRA):
    """Volatilidade mínima para cada retorno alvo, da variância mínima ao maior retorno.

    base são os pesos da carteira de variância mínima, já calculados por quem chama.
    """
    alvos = np.linspace(float(base @ mu), float(np.max(mu)), pontos)
    curva = []
    for alvo in alvos:
        restricao = {"type": "eq", "fun": lambda w, a=alvo: w @ mu - a}
        pesos = _resolver(lambda w: w @ cov @ w, len(mu), (restricao,))
        curva.append((float(np.sqrt(pesos @ cov @ pesos)), float(alvo)))
    return curva
