"""Medições da Aula 03 sobre os CSVs de dados/.

Covariância e correlação da cesta, a curva de risco de dois ativos em função do
peso e da correlação, a correlação móvel em crise e o encolhimento de
Ledoit-Wolf. Todo número que o deck, o notebook, os widgets e as animações da
Aula 03 citam sai daqui e está travado em tools/tests/test_aula03.py.

Tratamento de ausências declarado, o mesmo da Aula 02 (tools/medidas_aula02.py)
para a matriz repetir a tabela de volatilidade daquela aula: retornos simples
diários do Adj Close preenchido para a frente por ativo (ffill), sem preencher
antes da primeira cotação. A GOLD11 entra só a partir de 11/12/2020. A matriz
da cesta usa, em cada par, os pregões em que os dois ativos têm retorno (o
padrão de DataFrame.corr e DataFrame.cov). Medidas de um par ou de uma carteira
leem essa mesma matriz, a que o A3 consome. A correlação móvel usa os pregões
em que os dois ativos têm retorno, e o Ledoit-Wolf, os pregões com os 15
ativos cotados.
"""
import os

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
PREGOES_ANO = 252
JANELA_MOVEL = 63
PARES_WIDGET = [("ITUB4", "BBDC4"), ("PETR4", "IVVB11"), ("BOVA11", "GOLD11")]
PARES_MOVEIS = [("ITUB4", "BBDC4"), ("PETR4", "IVVB11")]
BANCOS = ["ITUB4", "BBDC4", "BBAS3"]
MISTA = ["ITUB4", "PETR4", "IVVB11"]
EXCERTO = ["PETR4", "VALE3", "ITUB4", "IVVB11"]
JANELAS_LW = [63, 126, 252]


def carregar_ajustados():
    return pd.read_csv(os.path.join(DADOS, "precos_ajustados.csv"),
                       index_col="data", parse_dates=["data"])


def retornos():
    """Retornos simples diários do Adj Close preenchido para a frente por ativo."""
    return carregar_ajustados().ffill().pct_change(fill_method=None).iloc[1:]


# ---------------------------------------------------------------------------
# Risco de dois ativos: a fórmula
# ---------------------------------------------------------------------------

def risco_dois_ativos(peso, vol_a, vol_b, rho):
    """Desvio padrão da carteira com `peso` em A e o resto em B."""
    variancia = (peso ** 2 * vol_a ** 2 + (1 - peso) ** 2 * vol_b ** 2
                 + 2 * peso * (1 - peso) * rho * vol_a * vol_b)
    return float(np.sqrt(max(variancia, 0.0)))


def peso_variancia_minima(vol_a, vol_b, rho):
    """Peso em A que minimiza a variância, sem venda a descoberto (entre 0 e 1)."""
    denominador = vol_a ** 2 + vol_b ** 2 - 2 * rho * vol_a * vol_b
    if denominador == 0:
        return 0.5
    return float(min(1.0, max(0.0, (vol_b ** 2 - rho * vol_a * vol_b) / denominador)))


def peer_instruction():
    """Dois ativos de 30% de volatilidade, correlação 0,5, metade em cada."""
    return {
        "rho_05": risco_dois_ativos(0.5, 0.30, 0.30, 0.5),
        "rho_1": risco_dois_ativos(0.5, 0.30, 0.30, 1.0),
        "rho_0": risco_dois_ativos(0.5, 0.30, 0.30, 0.0),
        "rho_menos_1": risco_dois_ativos(0.5, 0.30, 0.30, -1.0),
    }


CORRELACOES_CURVA = [1.0, 0.5, 0.0, -0.5, -1.0]


def curva_por_correlacao(a="PETR4", b="IVVB11", rhos=None):
    """Para cada correlação, o peso de menor risco em A e o risco nesse peso.

    Volatilidades e retornos são os medidos na cesta; só a correlação varia.
    É a curva da animação aula03-curva-correlacao.
    """
    par = estatisticas_par(a, b)
    saida = {}
    for rho in (CORRELACOES_CURVA if rhos is None else rhos):
        w = peso_variancia_minima(par["vol_a"], par["vol_b"], rho)
        saida[rho] = {"peso_minimo": w,
                      "risco_minimo": risco_dois_ativos(w, par["vol_a"], par["vol_b"], rho),
                      "risco_meio_a_meio": risco_dois_ativos(0.5, par["vol_a"], par["vol_b"], rho)}
    return saida


def pct(valor, casas=2):
    """Porcentagem em pt-BR, com sinal de menos U+2212: 0.25981 -> "25,98%"."""
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",").replace("-", "\u2212")


def dec(valor, casas=2):
    """Decimal em pt-BR, com sinal de menos U+2212: 0.8034 -> "0,80"."""
    return ("%.*f" % (casas, valor)).replace(".", ",").replace("-", "\u2212")


def autoverificacao():
    """Pergunta 1 da autoverificação: 30% e 20% de volatilidade, correlação 0, metade em cada.

    Variação do Peer Instruction de abertura, com o mesmo raciocínio e outro
    número, para o preparo não entregar a resposta do voto em sala.
    """
    return risco_dois_ativos(0.5, 0.30, 0.20, 0.0)


# ---------------------------------------------------------------------------
# Matrizes da cesta
# ---------------------------------------------------------------------------

def matriz_correlacao():
    return retornos().corr()


def matriz_covariancia_anual():
    return retornos().cov() * PREGOES_ANO


def pares_ordenados():
    """Série (ativo_a, ativo_b) -> correlação, dos 105 pares, em ordem crescente."""
    c = matriz_correlacao()
    acima = np.triu(np.ones(c.shape, dtype=bool), 1)
    return c.where(acima).stack().dropna().sort_values()


def correlacao_media(rets):
    c = rets.corr()
    acima = np.triu(np.ones(c.shape, dtype=bool), 1)
    return float(c.where(acima).stack().dropna().mean())


def correlacao_media_marco_2020():
    """Média dos pares sem o GOLD11, que só tem cotação a partir de 11/12/2020."""
    sem_gold = retornos().drop(columns="GOLD11")
    return {
        "janela": correlacao_media(sem_gold),
        "marco_2020": correlacao_media(sem_gold.loc["2020-03"]),
        "pregoes_marco_2020": int(len(sem_gold.loc["2020-03"])),
    }


# ---------------------------------------------------------------------------
# Pares e carteiras
# ---------------------------------------------------------------------------

def estatisticas_par(a, b):
    """Volatilidade, retorno anual e correlação de um par, lidos da matriz da cesta.

    Mesma fonte que o A3 consome: volatilidade da diagonal da covariância
    anualizada, correlação da matriz par a par e retorno médio anual de cada
    ativo no seu próprio histórico.
    """
    cov = matriz_covariancia_anual()
    media = retornos().mean() * PREGOES_ANO
    vol_a, vol_b = float(np.sqrt(cov.loc[a, a])), float(np.sqrt(cov.loc[b, b]))
    rho = float(matriz_correlacao().loc[a, b])
    w = peso_variancia_minima(vol_a, vol_b, rho)
    return {
        "pregoes": int(retornos()[[a, b]].dropna().shape[0]),
        "vol_a": vol_a, "vol_b": vol_b,
        "ret_a": float(media[a]), "ret_b": float(media[b]),
        "rho": rho,
        "peso_minimo": w,
        "risco_minimo": risco_dois_ativos(w, vol_a, vol_b, rho),
        "risco_meio_a_meio": risco_dois_ativos(0.5, vol_a, vol_b, rho),
    }


def carteira_igual(tickers):
    """Carteira de pesos iguais: volatilidade contra a média das volatilidades.

    Usa a covariância anualizada da cesta, a mesma matriz que o A3 consome.
    """
    cov = matriz_covariancia_anual().loc[tickers, tickers].to_numpy()
    w = np.full(len(tickers), 1 / len(tickers))
    vol = float(np.sqrt(w @ cov @ w))
    media_vols = float(w @ np.sqrt(np.diag(cov)))
    return {"vol": vol, "media_vols": media_vols, "reducao": 1 - vol / media_vols}


# ---------------------------------------------------------------------------
# Correlação móvel
# ---------------------------------------------------------------------------

def correlacao_movel(a, b, janela=JANELA_MOVEL):
    rets = retornos()[[a, b]].dropna()
    return rets[a].rolling(janela).corr(rets[b]).dropna()


def resumo_movel(a, b, janela=JANELA_MOVEL):
    movel = correlacao_movel(a, b, janela)
    return {
        "minimo": float(movel.min()), "data_minimo": movel.idxmin().strftime("%Y-%m-%d"),
        "maximo": float(movel.max()), "data_maximo": movel.idxmax().strftime("%Y-%m-%d"),
        "fim_2019": float(movel.loc[:"2019-12-31"].iloc[-1]),
        "fim_marco_2020": float(movel.loc[:"2020-03-31"].iloc[-1]),
    }


# ---------------------------------------------------------------------------
# Ledoit-Wolf
# ---------------------------------------------------------------------------

def ledoit_wolf(matriz):
    """Encolhimento de Ledoit-Wolf (2004) para o alvo mu * I.

    Mesma estimativa do sklearn.covariance.LedoitWolf, escrita em NumPy para o
    notebook rodar sem scikit-learn. Devolve (covariância encolhida diária,
    intensidade do encolhimento entre 0 e 1).
    """
    x = np.asarray(matriz, dtype=float)
    n, p = x.shape
    x = x - x.mean(axis=0)
    amostral = x.T @ x / n
    mu = np.trace(amostral) / p
    alvo = mu * np.eye(p)
    d2 = np.sum((amostral - alvo) ** 2)
    normas = np.sum(x ** 2, axis=1)
    quadratica = np.einsum("ij,jk,ik->i", x, amostral, x)
    b2_barra = np.sum(normas ** 2 - 2 * quadratica + np.sum(amostral ** 2)) / n ** 2
    intensidade = min(b2_barra, d2) / d2
    return intensidade * alvo + (1 - intensidade) * amostral, float(intensidade)


def encolhimento_por_janela():
    """Intensidade do Ledoit-Wolf nos últimos 63, 126 e 252 pregões e na amostra comum."""
    completos = retornos().dropna()
    saida = {}
    for n in JANELAS_LW + [len(completos)]:
        trecho = completos.iloc[-n:]
        saida[n] = {"intensidade": ledoit_wolf(trecho.to_numpy())[1],
                    "inicio": trecho.index[0].strftime("%Y-%m-%d")}
    return saida


def amostra_completa():
    completos = retornos().dropna()
    return {"pregoes": int(len(completos)), "inicio": completos.index[0].strftime("%Y-%m-%d")}


# ---------------------------------------------------------------------------
# Resgate da Aula 02 e régua da escolha coletiva
# ---------------------------------------------------------------------------

RESGATE = ["PETR4", "ITUB4", "BBDC4", "IVVB11"]

# Régua da classificação coletiva do Bloco 6: convenção didática desta aula,
# declarada no slide.
REGUA_CONCENTRA = 0.60
REGUA_DIVERSIFICA = 0.30
PARES_ESCOLHA = [("ITUB4", "BBDC4"), ("BBAS3", "BOVA11"), ("ITUB4", "BBAS3"), ("PETR4", "VALE3"),
                 ("VALE3", "SUZB3"), ("PETR4", "IVVB11"), ("ITUB4", "IVVB11"), ("BOVA11", "GOLD11")]


def tabela_resgate():
    """Retorno médio anual e volatilidade anual dos ativos do slide de resgate."""
    cov = matriz_covariancia_anual()
    media = retornos().mean() * PREGOES_ANO
    return {t: {"ret": float(media[t]), "vol": float(np.sqrt(cov.loc[t, t]))} for t in RESGATE}


def classificar(rho):
    if rho >= REGUA_CONCENTRA:
        return "concentra"
    if rho >= REGUA_DIVERSIFICA:
        return "intermediário"
    return "diversifica"


def escolha_coletiva():
    """Os oito pares do Bloco 6 com a correlação medida e a classe pela régua."""
    c = matriz_correlacao()
    return [(a, b, float(c.loc[a, b]), classificar(float(c.loc[a, b]))) for a, b in PARES_ESCOLHA]
