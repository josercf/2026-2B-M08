"""Medições da Aula 02 sobre os CSVs de dados/.

Do preço ao retorno: retorno simples e logarítmico, média e desvio padrão
diários, caudas do histograma, anualização por 252 e por raiz de 252,
volatilidade em janela deslizante, a dispersão crescendo com a raiz do tempo e
a comparação da cesta com o CDI acumulado. Todo número que o deck, o notebook,
os widgets e as animações da Aula 02 citam sai daqui e está travado em
tools/tests/test_aula02.py.

Tratamento de ausência usado em toda a aula, salvo onde dito: Adj Close com
preenchimento para a frente por ativo (ffill), sem preencher antes da primeira
cotação. É a decisão do exemplo de ADR da Aula 01; a GOLD11 entra só a partir
de 11/12/2020. O desafio do notebook inverte a decisão (descartar as datas com
ausência na cesta inteira), e descartar_contra_preencher() mede o efeito.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m1  # noqa: E402

RAIZ = m1.RAIZ
DADOS = m1.DADOS
PREGOES_ANO = 252
JANELAS = (21, 63, 252)
DATA_QUEDA = "2020-03-09"
CRISE_INICIO, CRISE_FIM = "2020-02-20", "2020-04-30"
TICKER_CAUDAS = "PETR4"
TICKER_RAIZ = "BOVA11"
HORIZONTES_RAIZ = (1, 5, 21, 63)


def precos():
    """Adj Close da cesta, preenchido para a frente por ativo (ver docstring do módulo)."""
    return m1.carregar_precos("precos_ajustados.csv").ffill()


def retornos_simples(p=None):
    p = precos() if p is None else p
    return p.pct_change(fill_method=None).iloc[1:]


def retornos_log(p=None):
    p = precos() if p is None else p
    return np.log(p / p.shift(1)).iloc[1:]


def queda_petr4():
    """A queda da PETR4 em 09/03/2020 e as alternativas do Peer Instruction.

    Cada distrator é um erro de conta comum, calculado sobre o mesmo número:
    repetir o retorno simples, usar ln(1 + |r|) com o sinal trocado e usar o
    logaritmo de base 10.
    """
    simples = float(retornos_simples()["PETR4"].loc[DATA_QUEDA])
    return {
        "data": DATA_QUEDA,
        "simples": simples,
        "log": float(retornos_log()["PETR4"].loc[DATA_QUEDA]),
        "erro_repetir_simples": simples,
        "erro_simetrico": -math.log(1 + abs(simples)),
        "erro_log10": math.log10(1 + simples),
    }


def piores_quedas(n=5):
    """Pior retorno simples diário de cada ativo, com a data e o log correspondente."""
    r = retornos_simples()
    lg = retornos_log()
    return pd.DataFrame({"data": r.idxmin(), "simples": r.min(), "log": lg.min()})


def estatisticas_diarias():
    r = retornos_simples()
    return pd.DataFrame({"media": r.mean(), "desvio": r.std(), "n": r.count()})


def anualizadas():
    """Retorno anualizado (média diária x 252), volatilidade (desvio x raiz de 252),
    retorno log anualizado e retorno total entre a primeira e a última cotação."""
    p = precos()
    r = retornos_simples(p)
    lg = retornos_log(p)
    total = p.apply(lambda s: s.dropna().iloc[-1] / s.dropna().iloc[0] - 1)
    return pd.DataFrame({
        "retorno_anual": r.mean() * PREGOES_ANO,
        "vol_anual": r.std() * np.sqrt(PREGOES_ANO),
        "log_anual": lg.mean() * PREGOES_ANO,
        "total": total,
        "inicio": p.apply(lambda s: s.first_valid_index()),
    })


def carregar_cdi():
    serie = pd.read_csv(os.path.join(DADOS, "cdi_diario.csv"), index_col="data", parse_dates=["data"])
    return serie["valor"] / 100


def cdi(inicio=None):
    """CDI acumulado e anualizado (base 252) a partir de inicio, até o fim da janela.

    Capitaliza a taxa diária de cada dia útil de cdi_diario.csv.
    """
    taxa = carregar_cdi()
    if inicio is not None:
        taxa = taxa.loc[inicio:]
    acumulado = float((1 + taxa).prod() - 1)
    return {
        "acumulado": acumulado,
        "anual": (1 + acumulado) ** (PREGOES_ANO / len(taxa)) - 1,
        "dias": len(taxa),
    }


def abaixo_do_cdi():
    """Ativos cujo retorno total ficou abaixo do CDI acumulado no mesmo período.

    O período de cada ativo começa na primeira cotação dele (GOLD11 em
    11/12/2020), e o CDI é acumulado a partir da mesma data.
    """
    a = anualizadas()
    return sorted(t for t in a.index if a.loc[t, "total"] < cdi(a.loc[t, "inicio"])["acumulado"])


def caudas(ticker=TICKER_CAUDAS):
    """Peso das caudas: a pior queda em desvios padrão e os pregões além de 3 desvios
    contra o que a distribuição normal preveria para a mesma amostra."""
    r = retornos_simples()[ticker].dropna()
    z = (r - r.mean()) / r.std()
    alem = z[z.abs() > 3]
    prob_normal = math.erfc(3 / math.sqrt(2))
    return {
        "n": len(r),
        "desvio": float(r.std()),
        "pior": float(r.min()),
        "pior_data": r.idxmin().strftime("%Y-%m-%d"),
        "pior_em_desvios": float(z.min()),
        "alem_3": int(len(alem)),
        "alem_3_normal": prob_normal * len(r),
        "alem_3_marco_2020": int((alem.index.strftime("%Y-%m") == "2020-03").sum()),
        "curtose": float(r.kurt()),
    }


def janela_crise(ticker="PETR4"):
    """Retornos de 20/02/2020 a 30/04/2020: a soma dos simples erra o acumulado e a
    soma dos log acerta o log do acumulado."""
    r = retornos_simples()[ticker].loc[CRISE_INICIO:CRISE_FIM]
    lg = retornos_log()[ticker].loc[CRISE_INICIO:CRISE_FIM]
    return {
        "pregoes": len(r),
        "soma_simples": float(r.sum()),
        "acumulado": float((1 + r).prod() - 1),
        "soma_log": float(lg.sum()),
    }


def vol_movel(ticker, janela):
    """Volatilidade anualizada em janela deslizante de `janela` pregões."""
    return retornos_simples()[ticker].rolling(janela).std() * np.sqrt(PREGOES_ANO)


def picos_2020(ticker):
    """Pico de cada janela em 2020: valor e data. A janela curta reage primeiro e mais alto."""
    saida = {}
    for janela in JANELAS:
        v = vol_movel(ticker, janela).loc["2020-01-01":"2020-12-31"]
        saida[janela] = {"pico": float(v.max()), "data": v.idxmax().strftime("%Y-%m-%d")}
    return saida


def raiz_do_tempo(ticker=TICKER_RAIZ, horizontes=HORIZONTES_RAIZ):
    """Desvio do retorno log acumulado em h pregões (janelas sobrepostas) contra a
    previsão da raiz do tempo, desvio diário x raiz de h."""
    lg = retornos_log()[ticker].dropna()
    diario = float(lg.std())
    return {h: {"medido": float(lg.rolling(h).sum().dropna().std()), "previsto": diario * math.sqrt(h)}
            for h in horizontes}


def descartar_contra_preencher():
    """Desafio do notebook: volatilidade anual com a cesta inteira em dropna."""
    ajustado = m1.carregar_precos("precos_ajustados.csv")
    descartar = ajustado.dropna().pct_change().std() * np.sqrt(PREGOES_ANO)
    preencher = retornos_simples().std() * np.sqrt(PREGOES_ANO)
    return pd.DataFrame({"descartar": descartar, "preencher": preencher,
                         "diferenca": descartar - preencher})


def maiores_movimentos(ticker, n=8):
    """Os n pregões de maior variação absoluta do ativo, com o retorno simples e o log.

    Alimenta o widget simples-log: nas quedas o log fica abaixo do simples, e nas
    altas também, porque ln(1 + r) < r para todo r diferente de zero.
    """
    r = retornos_simples()[ticker].dropna()
    lg = retornos_log()[ticker].dropna()
    datas = r.abs().sort_values(ascending=False).index[:n]
    return pd.DataFrame({"simples": r.loc[datas], "log": lg.loc[datas]})


def erro_da_soma_simples(ticker="PETR4"):
    """Quanto a soma dos retornos simples erra o acumulado na janela da crise,
    em pontos percentuais (positivo: a soma subestima a queda)."""
    j = janela_crise(ticker)
    return j["soma_simples"] - j["acumulado"]


def conta_anualizacao(ticker="PETR4"):
    """A conta do quadro no Bloco 5: média e desvio diários, os dois fatores e o
    resultado, mais o erro comum de multiplicar o desvio por 252."""
    e = estatisticas_diarias().loc[ticker]
    media, desvio = float(e["media"]), float(e["desvio"])
    return {
        "media_diaria": media,
        "desvio_diario": desvio,
        "raiz_252": math.sqrt(PREGOES_ANO),
        "retorno_anual": media * PREGOES_ANO,
        "vol_anual": desvio * math.sqrt(PREGOES_ANO),
        "erro_desvio_vezes_252": desvio * PREGOES_ANO,
    }


def extremos_da_cesta():
    """Quem lidera e quem fecha a cesta em retorno total e em volatilidade."""
    a = anualizadas()
    return {
        "maior_total": a["total"].idxmax(),
        "menor_total": a["total"].idxmin(),
        "maior_vol": a["vol_anual"].idxmax(),
        "menor_vol": a["vol_anual"].idxmin(),
        "ranking_vol": list(a["vol_anual"].sort_values(ascending=False).index),
    }


def pct(valor, casas=2):
    """0.123456 -> "12,35%", no formato do deck."""
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",")
