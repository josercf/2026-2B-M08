"""Tratamento de ausência único do módulo (ADR-009).

Toda medição das Aulas 02 a 06 parte daqui, para o mesmo ativo ter o mesmo
retorno em todas as aulas e a matriz da Aula 03 ser a que o otimizador da Aula
04 consome.

- Preço: Adj Close de dados/precos_ajustados.csv.
- Lacuna isolada (ativo já cotado que fica sem cotação num pregão) é preenchida
  com o último preço (ffill). No snapshot de 17/09/2026 são três lacunas, todas
  em 24/10/2025 (BOVA11, IVVB11 e GOLD11). O retorno do dia preenchido é zero, e
  o pregão seguinte leva a variação dos dois dias.
- Nada é preenchido antes da primeira cotação: a GOLD11 segue sem retorno até
  11/12/2020.
- Métrica de um ativo usa a série inteira dele (retornos_por_ativo).
- Análise conjunta usa a janela comum dos ativos envolvidos
  (retornos_janela_comum). Com a GOLD11 na cesta, essa janela começa em
  14/12/2020 e deixa março de 2020 de fora; quem usa a janela comum declara
  início e número de retornos.
"""
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
PREGOES_ANO = 252


def precos_brutos():
    return pd.read_csv(os.path.join(DADOS, "precos_ajustados.csv"),
                       index_col="data", parse_dates=["data"])


TICKERS = list(precos_brutos().columns)


def precos_tratados(tickers=None):
    """Adj Close com as lacunas isoladas preenchidas, sem preencher o começo."""
    precos = precos_brutos()
    if tickers is not None:
        precos = precos[list(tickers)]
    # ffill nunca preenche antes do primeiro valor válido de cada coluna.
    return precos.ffill()


def lacunas_preenchidas():
    """Uma linha por (data, ticker) que o ffill preencheu."""
    brutos = precos_brutos()
    marcadas = (brutos.isna() & brutos.ffill().notna()).stack()
    marcadas = marcadas[marcadas]
    return pd.DataFrame({"ticker": marcadas.index.get_level_values(1)},
                        index=marcadas.index.get_level_values(0))


def retornos_por_ativo(tickers=None):
    """Retorno simples diário de cada ativo, NaN antes da primeira cotação."""
    return precos_tratados(tickers).pct_change(fill_method=None).iloc[1:]


def retornos_janela_comum(tickers=None, inicio=None, fim=None):
    """Retornos dos pregões em que todos os ativos pedidos têm retorno."""
    rets = retornos_por_ativo(tickers).loc[inicio:fim]
    return rets.dropna()


def volatilidade_anual(serie):
    return serie.dropna().std() * PREGOES_ANO ** 0.5
