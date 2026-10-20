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
    """Descartar datas com ausência (dropna) contra preencher para a frente (ffill).

    O preenchimento para a frente copia o preço do pregão anterior para a data
    ausente, o que dá retorno zero nela e faz o pregão seguinte acumular os dois
    dias. BOVA11, IVVB11 e GOLD11 (data_ausencia_compartilhada) são os três
    ativos em que isso acontece dentro da janela coletada, e o retorno de cada
    um nas duas datas fica travado por ticker, nunca por uma data digitada.
    """
    ajustado = carregar_precos("precos_ajustados.csv")
    descartar = ajustado.dropna()
    preencher = ajustado.ffill()
    data_falha = data_ausencia_compartilhada()
    data_seguinte = ajustado.index[ajustado.index.get_loc(data_falha) + 1]
    retorno_etfs_preenchido = {
        ticker: {
            data.strftime("%Y-%m-%d"): float(preencher[ticker].pct_change(fill_method=None).loc[data])
            for data in (data_falha, data_seguinte)
        }
        for ticker in ("BOVA11", "IVVB11", "GOLD11")
    }
    return {
        "pregoes_total": len(ajustado),
        "pregoes_descartar": len(descartar),
        "pregoes_preencher": len(preencher.dropna(how="all")),
        "inicio_descartar": descartar.index[0].strftime("%Y-%m-%d"),
        "vol_descartar": volatilidade_anual(descartar),
        "vol_preencher": volatilidade_anual(preencher),
        "retorno_etfs_preenchido": retorno_etfs_preenchido,
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


def razao_ajustado_fechamento(ticker):
    """Adj Close dividido pelo Close no primeiro pregão da janela.

    Mede quanto dos proventos pagos depois daquela data foi descontado do preço
    antigo: quanto menor a razão, maior o peso dos proventos no retorno total.
    """
    ajustado = carregar_precos("precos_ajustados.csv")[ticker].dropna()
    fechamento = carregar_precos("precos_fechamento.csv")[ticker].dropna()
    return float(ajustado.iloc[0] / fechamento.iloc[0])


def linhas_com_fim_exclusivo(inicio="2026-08-01", fim="2026-08-31"):
    """Alternativas do Peer Instruction de abertura sobre o end do yfinance.

    yf.download(start=inicio, end=fim) devolve uma linha por pregão de inicio
    até o dia anterior a fim, porque o end é exclusivo. Os pregões vêm do
    snapshot (que é a própria saída do yfinance) e os dias corridos, do
    calendário. Cada alternativa errada corresponde a um erro comum:
    contar dias corridos, contar dias corridos com o fim exclusivo, ou contar
    os pregões esquecendo que o end exclui o último dia.
    """
    pregoes = carregar_precos("precos_fechamento.csv").index
    fim_ts = pd.Timestamp(fim)
    return {
        "dias_corridos": len(pd.date_range(inicio, fim)),
        "dias_corridos_fim_exclusivo": len(pd.date_range(inicio, fim_ts - pd.Timedelta(days=1))),
        "pregoes_inclusivo": int(((pregoes >= inicio) & (pregoes <= fim_ts)).sum()),
        "pregoes_fim_exclusivo": int(((pregoes >= inicio) & (pregoes < fim_ts)).sum()),
        "fim_e_pregao": bool(fim_ts in pregoes),
        "dia_da_semana_do_fim": fim_ts.dayofweek,
    }


def calendario_do_mes(inicio="2026-08-01", fim="2026-08-31"):
    """Dias do mês do Peer Instruction, com a marca de pregão, para o calendário do deck.

    Cada dia corrido vira um quadrado do calendário animado do slide do end
    exclusivo; pregão é a data que existe no snapshot, que é a própria saída do
    yfinance. Devolve dia, dia da semana (0 é segunda) e se houve pregão.
    """
    pregoes = set(carregar_precos("precos_fechamento.csv").index)
    return [{"dia": d.day, "dia_da_semana": d.dayofweek, "pregao": d in pregoes}
            for d in pd.date_range(inicio, fim)]
