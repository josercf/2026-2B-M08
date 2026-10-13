"""Medições da Aula 04 sobre os CSVs de dados/.

Retorno esperado e covariância anualizados da cesta de 15 ativos, o CDI como
taxa livre de risco, a nuvem de 10.000 carteiras sorteadas com semente fixa, a
melhor carteira sorteada contra a ótima, as carteiras de variância mínima e de
máximo Sharpe resolvidas por SLSQP, a fronteira de 50 pontos e o caminho do
SLSQP no triângulo de pesos de três ativos. Todo número que o deck, o notebook,
os widgets e as animações da Aula 04 citam sai daqui e está travado em
tools/tests/test_aula04.py.

Tratamento de ausências declarado: Adj Close com as datas de ausência
descartadas na cesta inteira (dropna), o tratamento "descartar" da Aula 01. A
amostra começa em 11/12/2020, primeira cotação do GOLD11, e os retornos diários
vão de 14/12/2020 a 31/08/2026. Anualização por 252 pregões, como na Aula 02.
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import minimize

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
PREGOES_ANO = 252
SEMENTE = 42
N_CARTEIRAS = 10_000
N_FRONTEIRA = 50
SORTEIOS_PROGRESSIVOS = (10, 100, 1_000, 10_000, 100_000, 1_000_000)
TRIO = ("PETR4", "IVVB11", "GOLD11")
TOLERANCIA = 1e-12
MINIMO_PESO = 1e-4  # peso abaixo disso conta como fora da carteira


def precos():
    """Adj Close da cesta com as datas de ausência descartadas."""
    ajustado = pd.read_csv(os.path.join(DADOS, "precos_ajustados.csv"),
                           index_col="data", parse_dates=["data"])
    return ajustado.dropna()


def retornos():
    """Retornos diários simples da cesta, sobre os preços com ausências descartadas."""
    return precos().pct_change().dropna()


def retorno_esperado():
    """Média diária vezes 252, por ativo."""
    return retornos().mean() * PREGOES_ANO


def covariancia():
    """Matriz de covariância diária vezes 252."""
    return retornos().cov() * PREGOES_ANO


def volatilidade():
    return pd.Series(np.sqrt(np.diag(covariancia())), index=covariancia().index)


def taxa_livre_de_risco():
    """CDI acumulado na janela dos retornos, anualizado por 252 dias úteis."""
    r = retornos()
    cdi = pd.read_csv(os.path.join(DADOS, "cdi_diario.csv"), index_col="data",
                      parse_dates=["data"])["valor"]
    janela = cdi.loc[r.index[0]:r.index[-1]]
    return float((1 + janela / 100).prod() ** (PREGOES_ANO / len(janela)) - 1)


def sharpe_por_ativo():
    return (retorno_esperado() - taxa_livre_de_risco()) / volatilidade()


def parametros_do_modelo(n):
    """Médias, variâncias e covariâncias distintas que o modelo estima para n ativos."""
    return n + n * (n + 1) // 2


def metricas(pesos, mu=None, cov=None, rf=None):
    """(retorno, volatilidade, Sharpe) de uma carteira, em forma vetorial."""
    mu = retorno_esperado().values if mu is None else mu
    cov = covariancia().values if cov is None else cov
    rf = taxa_livre_de_risco() if rf is None else rf
    w = np.asarray(pesos, dtype=float)
    ret = float(w @ mu)
    vol = float(np.sqrt(w @ cov @ w))
    return ret, vol, (ret - rf) / vol


def sortear(n, semente=SEMENTE, mu=None, cov=None, rf=None):
    """Motor vetorizado: n carteiras com pesos uniformes normalizados.

    Devolve (pesos, retorno, volatilidade, sharpe) em arrays NumPy, sem laço
    por carteira.
    """
    mu = retorno_esperado().values if mu is None else mu
    cov = covariancia().values if cov is None else cov
    rf = taxa_livre_de_risco() if rf is None else rf
    gerador = np.random.default_rng(semente)
    pesos = gerador.random((n, len(mu)))
    pesos /= pesos.sum(axis=1, keepdims=True)
    ret = pesos @ mu
    vol = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
    return pesos, ret, vol, (ret - rf) / vol


def nuvem():
    """A nuvem de 10.000 carteiras da aula e o resumo dela."""
    pesos, ret, vol, sharpe = sortear(N_CARTEIRAS)
    melhor = int(np.argmax(sharpe))
    return {
        "pesos": pesos, "retorno": ret, "volatilidade": vol, "sharpe": sharpe,
        "melhor": melhor,
        "melhor_sharpe": float(sharpe[melhor]),
        "melhor_retorno": float(ret[melhor]),
        "melhor_volatilidade": float(vol[melhor]),
        "melhor_maior_peso": float(pesos[melhor].max()),
        "maior_peso_da_nuvem": float(pesos.max()),
        "menor_volatilidade": float(vol.min()),
        "maior_retorno": float(ret.max()),
        "maior_volatilidade": float(vol.max()),
        "abaixo_do_cdi": int((sharpe < 0).sum()),
    }


def melhor_por_sorteios(tamanhos=SORTEIOS_PROGRESSIVOS, semente=SEMENTE):
    """Melhor Sharpe entre os N primeiros sorteios, para cada N.

    Um único gerador, em lotes de até 100.000: os N primeiros sorteios de cada
    tamanho são os mesmos, então a curva só pode subir.
    """
    mu, cov, rf = retorno_esperado().values, covariancia().values, taxa_livre_de_risco()
    gerador = np.random.default_rng(semente)
    saida, melhor, feitos = {}, -np.inf, 0
    for alvo in sorted(tamanhos):
        while feitos < alvo:
            lote = min(100_000, alvo - feitos)
            pesos = gerador.random((lote, len(mu)))
            pesos /= pesos.sum(axis=1, keepdims=True)
            vol = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
            melhor = max(melhor, float(((pesos @ mu - rf) / vol).max()))
            feitos += lote
        saida[alvo] = melhor
    return saida


def _otimizar(objetivo, n, restricoes=(), x0=None, callback=None):
    restricoes = [{"type": "eq", "fun": lambda w: w.sum() - 1}] + list(restricoes)
    x0 = np.full(n, 1 / n) if x0 is None else np.asarray(x0, dtype=float)
    resultado = minimize(objetivo, x0, method="SLSQP", bounds=[(0, 1)] * n,
                         constraints=restricoes, callback=callback,
                         options={"ftol": TOLERANCIA, "maxiter": 500})
    if not resultado.success:
        raise RuntimeError("SLSQP não convergiu: %s" % resultado.message)
    return resultado


def variancia_minima():
    cov = covariancia().values
    return _otimizar(lambda w: w @ cov @ w, len(cov)).x


def maximo_sharpe(mu=None, cov=None, rf=None, x0=None, callback=None):
    mu = retorno_esperado().values if mu is None else mu
    cov = covariancia().values if cov is None else cov
    rf = taxa_livre_de_risco() if rf is None else rf
    return _otimizar(lambda w: -(w @ mu - rf) / np.sqrt(w @ cov @ w), len(mu),
                     x0=x0, callback=callback).x


def carteira(pesos):
    """Resumo de uma carteira ótima: métricas e pesos acima do mínimo."""
    tickers = list(covariancia().index)
    ret, vol, sharpe = metricas(pesos)
    composicao = {t: float(w) for t, w in zip(tickers, pesos) if w > MINIMO_PESO}
    maior = max(composicao, key=composicao.get)
    return {"retorno": ret, "volatilidade": vol, "sharpe": sharpe,
            "pesos": composicao, "ativos": len(composicao),
            "maior_ativo": maior, "maior_peso": composicao[maior]}


def fronteira():
    """50 pontos de retorno alvo, da variância mínima ao ativo de maior retorno.

    Cada ponto é a carteira de menor volatilidade que entrega aquele retorno,
    sem venda a descoberto.
    """
    mu, cov = retorno_esperado().values, covariancia().values
    ret_minimo = metricas(variancia_minima())[0]
    alvos = np.linspace(ret_minimo, mu.max(), N_FRONTEIRA)
    pontos = []
    x0 = None
    for alvo in alvos:
        resultado = _otimizar(lambda w: w @ cov @ w, len(mu),
                              [{"type": "eq", "fun": lambda w, a=alvo: w @ mu - a}], x0=x0)
        x0 = resultado.x
        pontos.append((float(alvo), float(np.sqrt(resultado.x @ cov @ resultado.x))))
    return pd.DataFrame(pontos, columns=["retorno", "volatilidade"])


def trio():
    """Médias e covariância dos três ativos do triângulo de pesos."""
    mu = retorno_esperado()[list(TRIO)].values
    cov = covariancia().loc[list(TRIO), list(TRIO)].values
    return mu, cov


def correlacao_trio():
    """Matriz de correlação dos três ativos do triângulo de pesos."""
    return retornos()[list(TRIO)].corr()


def caminho_slsqp_trio(x0=(0.1, 0.8, 0.1)):
    """Pesos do SLSQP a cada iteração, maximizando o Sharpe só com o trio.

    Parte de 10% PETR4, 80% IVVB11 e 10% GOLD11, longe do ótimo, para o
    caminho ter passos visíveis no triângulo.
    """
    mu, cov = trio()
    passos = [np.asarray(x0, dtype=float)]
    final = maximo_sharpe(mu, cov, x0=x0, callback=lambda xk: passos.append(xk.copy()))
    return np.array(passos), final
