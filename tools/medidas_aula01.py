"""Medições da Aula 01 sobre os CSVs de dados/.

As três visões de preço (negociado, Close e Adj Close), os saltos que os eventos
corporativos provocam no preço negociado, o peso dos proventos no retorno e o
efeito de descartar ou preencher ausências. Todo número que o deck, o material,
as notas, os widgets e as animações da Aula 01 citam sai daqui e está travado em
tools/tests/test_aula01.py.
"""
import os

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
PREGOES_ANO = 252


def carregar_precos(arquivo):
    """precos_fechamento.csv ou precos_ajustados.csv, com índice de datas."""
    return pd.read_csv(os.path.join(DADOS, arquivo), index_col="data", parse_dates=["data"])


def carregar_desdobramentos():
    return pd.read_csv(os.path.join(DADOS, "eventos_desdobramento.csv"), parse_dates=["data"])


def preco_negociado(ticker):
    """Preço como foi negociado na data.

    O Close do Yahoo vem dividido pelos fatores de todos os eventos posteriores à
    data. Multiplicar de volta por esses fatores devolve o preço da tela do
    pregão daquele dia.
    """
    fechamento = carregar_precos("precos_fechamento.csv")[ticker].dropna()
    eventos = carregar_desdobramentos()
    eventos = eventos[eventos["ticker"] == ticker]
    fator = np.ones(len(fechamento))
    for data, f in zip(eventos["data"], eventos["fator"]):
        fator = fator * np.where(fechamento.index < data, f, 1.0)
    return fechamento * fator


def tres_visoes(ticker):
    """DataFrame com as colunas negociado, fechamento e ajustado de um ativo."""
    return pd.DataFrame({
        "negociado": preco_negociado(ticker),
        "fechamento": carregar_precos("precos_fechamento.csv")[ticker].dropna(),
        "ajustado": carregar_precos("precos_ajustados.csv")[ticker].dropna(),
    })


def maior_variacao_diaria(serie):
    """(data, variação) da maior variação diária em valor absoluto."""
    variacao = serie.dropna().pct_change().dropna()
    data = variacao.abs().idxmax()
    return data, float(variacao[data])


def retorno_no_periodo(serie):
    """Retorno entre o primeiro e o último valor presentes."""
    presentes = serie.dropna()
    return float(presentes.iloc[-1] / presentes.iloc[0] - 1)


def ausencias():
    """Pregões sem cotação por ativo, no Close."""
    return carregar_precos("precos_fechamento.csv").isna().sum()


def volatilidade_anual(precos):
    return precos.pct_change(fill_method=None).std() * np.sqrt(PREGOES_ANO)


def comparar_tratamentos():
    """Descartar datas com ausência (dropna) contra preencher para a frente (ffill)."""
    ajustado = carregar_precos("precos_ajustados.csv")
    descartar = ajustado.dropna()
    preencher = ajustado.ffill()
    retorno_preenchido = preencher["BOVA11"].pct_change(fill_method=None)
    return {
        "pregoes_total": len(ajustado),
        "pregoes_descartar": len(descartar),
        "pregoes_preencher": len(preencher.dropna(how="all")),
        "inicio_descartar": descartar.index[0].strftime("%Y-%m-%d"),
        "vol_descartar": volatilidade_anual(descartar),
        "vol_preencher": volatilidade_anual(preencher),
        "retorno_bova11_preenchido": {
            dia: float(retorno_preenchido.loc[dia]) for dia in ("2025-10-24", "2025-10-27")
        },
    }


def data_ausencia_compartilhada():
    """Data em que BOVA11, IVVB11 e GOLD11 ficam simultaneamente sem cotação no Close.

    Ausência real do provedor (dados/README.md), não falha de leitura. Dentro da
    janela coletada as três faltam juntas em um único pregão; a animação do mapa
    de ausências usa esta função tanto para a linha tracejada quanto para a
    legenda, para as duas nunca desalinharem entre si.
    """
    fechamento = carregar_precos("precos_fechamento.csv")
    compartilhada = fechamento[["BOVA11", "IVVB11", "GOLD11"]].isna().all(axis=1)
    return compartilhada[compartilhada].index[0]
