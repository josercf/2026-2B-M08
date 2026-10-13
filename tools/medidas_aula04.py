"""Medições da Aula 04 sobre os CSVs de dados/.

Retorno esperado e covariância anualizados da cesta de 15 ativos, o CDI como
taxa livre de risco, a nuvem de 10.000 carteiras sorteadas com semente fixa, a
melhor carteira sorteada contra a ótima, as carteiras de variância mínima e de
máximo Sharpe resolvidas por SLSQP, a fronteira de 50 pontos e o caminho do
SLSQP no triângulo de pesos de três ativos, e a comparação de três distribuições
de pesos no mesmo orçamento de sorteios (uniforme normalizado, Dirichlet(1) e
Dirichlet(0,2)). Todo número que o deck, o notebook,
os widgets e as animações da Aula 04 citam sai daqui e está travado em
tools/tests/test_aula04.py.

Tratamento de ausência: o único do módulo (ADR-009), de tools/retornos.py. A
lacuna isolada de 24/10/2025 (BOVA11, IVVB11 e GOLD11) é preenchida com o último
preço, nada é preenchido antes da primeira cotação, e a cesta usa a janela
comum dos 15 ativos: 1.423 retornos de 14/12/2020 a 31/08/2026, a mesma janela
da matriz da Aula 03. Com a GOLD11 na cesta, a janela perde março de 2020, e
custo_da_janela() mede o efeito na PETR4. Anualização por 252 pregões, como na
Aula 02.
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import minimize

import retornos as tratamento

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
LIMITE_CONCENTRACAO = 0.25  # carteira com algum peso acima disso conta como concentrada
# Distribuições de pesos comparadas: None é o motor da aula (Uniform(0,1) dividido
# pela soma); um número é o alfa de uma Dirichlet simétrica. Dirichlet(1) é a
# uniforme no simplex; alfa abaixo de 1 empurra os sorteios para vértices e arestas.
ESQUEMAS = (("uniforme_normalizado", None), ("dirichlet_1", 1.0), ("dirichlet_02", 0.2))


def retornos():
    """Retornos diários simples da cesta na janela comum dos 15 ativos (ADR-009)."""
    return tratamento.retornos_janela_comum()


def custo_da_janela(ticker="PETR4"):
    """Volatilidade anual do ativo na série inteira e na janela comum da cesta.

    A série inteira é a medida da Aula 02; a janela comum é a da matriz que o
    otimizador consome. A diferença é o custo de pôr a GOLD11 na cesta.
    """
    inteira = tratamento.retornos_por_ativo()[ticker]
    comum = retornos()[ticker]
    return {"serie_inteira": float(tratamento.volatilidade_anual(inteira)),
            "janela_comum": float(tratamento.volatilidade_anual(comum)),
            "retornos_serie_inteira": int(inteira.notna().sum()),
            "retornos_janela_comum": len(comum)}


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
    """Motor vetorizado: n carteiras com pesos Uniform(0,1) divididos pela soma.

    Devolve (pesos, retorno, volatilidade, sharpe) em arrays NumPy, sem laço
    por carteira.
    """
    mu = retorno_esperado().values if mu is None else mu
    cov = covariancia().values if cov is None else cov
    rf = taxa_livre_de_risco() if rf is None else rf
    pesos = pesos_sorteados(np.random.default_rng(semente), n, len(mu))
    ret = pesos @ mu
    vol = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
    return pesos, ret, vol, (ret - rf) / vol


def pesos_sorteados(gerador, n, k, alfa=None):
    """n linhas de k pesos não negativos que somam 1.

    alfa=None reproduz o motor da aula: Uniform(0,1) dividido pela soma da
    linha, que não é uniforme no simplex e acumula as carteiras perto de 1/k.
    Com alfa, sorteia de uma Dirichlet simétrica: alfa=1 é a uniforme no
    simplex, alfa<1 favorece carteiras concentradas.
    """
    if alfa is None:
        pesos = gerador.random((n, k))
        return pesos / pesos.sum(axis=1, keepdims=True)
    return gerador.dirichlet(np.full(k, float(alfa)), n)


def ativos_efetivos(pesos):
    """Número efetivo de ativos, 1 / soma(w²), de cada linha."""
    pesos = np.atleast_2d(np.asarray(pesos, dtype=float))
    return 1 / (pesos ** 2).sum(axis=1)


def comparar_esquemas(n=N_CARTEIRAS, semente=SEMENTE, mu=None, cov=None, rf=None):
    """Mesma semente e mesmo orçamento de n sorteios para cada distribuição de pesos.

    Para cada esquema de ESQUEMAS: melhor Sharpe, maior peso da melhor carteira,
    maior peso entre as n, mediana do número efetivo de ativos, número efetivo
    da melhor, fração de carteiras com algum peso acima de 25% e quantas rendem
    abaixo do CDI.
    """
    mu = retorno_esperado().values if mu is None else mu
    cov = covariancia().values if cov is None else cov
    rf = taxa_livre_de_risco() if rf is None else rf
    saida = {}
    for nome, alfa in ESQUEMAS:
        pesos = pesos_sorteados(np.random.default_rng(semente), n, len(mu), alfa)
        vol = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
        sharpe = (pesos @ mu - rf) / vol
        melhor = int(np.argmax(sharpe))
        efetivos = ativos_efetivos(pesos)
        saida[nome] = {
            "alfa": alfa,
            "melhor_sharpe": float(sharpe[melhor]),
            "melhor_maior_peso": float(pesos[melhor].max()),
            "maior_peso": float(pesos.max()),
            "ativos_efetivos_mediana": float(np.median(efetivos)),
            "ativos_efetivos_melhor": float(efetivos[melhor]),
            "fracao_concentrada": float((pesos.max(axis=1) > LIMITE_CONCENTRACAO).mean()),
            "abaixo_do_cdi": int((sharpe < 0).sum()),
        }
    return saida


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
            pesos = pesos_sorteados(gerador, lote, len(mu))
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
