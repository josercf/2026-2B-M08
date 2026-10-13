"""Pipeline único: preços (A1), métricas (A2) e otimização (A4) numa chamada.

É esta função que a API expõe. Ela devolve um dicionário simples, sem nada de
FastAPI, para poder ser chamada também de notebook, teste ou script.
"""
from carteira import dados, metricas, otimizador


def calcular(tickers, inicio, fim, taxa_livre_risco=None):
    precos = dados.precos(list(tickers))
    ret = metricas.retornos(precos, inicio, fim)
    if len(ret) < 60:
        raise dados.PeriodoSemDados(
            "a janela comum tem %d retornos com todos os ativos; o mínimo é 60" % len(ret))
    inicio_janela, fim_janela = ret.index[0].date().isoformat(), ret.index[-1].date().isoformat()
    mu = metricas.retorno_anual(ret).values
    cov = metricas.covariancia_anual(ret).values
    rf = dados.taxa_livre_risco(inicio_janela, fim_janela) if taxa_livre_risco is None else taxa_livre_risco
    minima = otimizador.variancia_minima(mu, cov)
    sharpe = otimizador.maximo_sharpe(mu, cov, rf)
    vol, corr = metricas.volatilidade_anual(ret), metricas.correlacao_media(ret)

    def carteira(pesos):
        return {"pesos": {t: float(p) for t, p in zip(tickers, pesos)},
                **otimizador.metricas_carteira(pesos, mu, cov, rf)}

    return {
        "tickers": list(tickers),
        "inicio_janela": inicio_janela,
        "fim_janela": fim_janela,
        "pregoes": len(ret),
        "taxa_livre_risco": rf,
        "ativos": [{"ticker": t, "retorno": float(mu[i]), "volatilidade": float(vol[t]),
                    "correlacao_media": float(corr[t])} for i, t in enumerate(tickers)],
        "variancia_minima": carteira(minima),
        "maximo_sharpe": carteira(sharpe),
        "fronteira": otimizador.fronteira(mu, cov, minima),
    }
