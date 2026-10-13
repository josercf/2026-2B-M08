"""Coletor (A1) reduzido ao que a API precisa: preços ajustados e CDI do snapshot.

Lê os CSVs de dados/ do acervo. Procura a pasta subindo a partir deste arquivo;
a variável M08_DADOS aponta outra pasta, e sem pasta local a leitura cai para a
URL bruta do repositório, a menos que M08_OFFLINE=1.
"""
import os

import numpy as np
import pandas as pd

URL_BRUTA = "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/"
PREGOES_ANO = 252


class TickerDesconhecido(LookupError):
    """Um ou mais tickers pedidos não existem na base."""

    def __init__(self, tickers):
        self.tickers = list(tickers)
        super().__init__("ticker fora da base: " + ", ".join(self.tickers))


class PeriodoSemDados(ValueError):
    """O período pedido deixa menos pregões do que o cálculo precisa."""


def _pasta_dados():
    if os.environ.get("M08_DADOS"):
        return os.environ["M08_DADOS"]
    pasta = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidata = os.path.join(pasta, "dados")
        if os.path.exists(os.path.join(candidata, "precos_ajustados.csv")):
            return candidata
        pasta = os.path.dirname(pasta)
    return None


def ler_csv(nome, **kwargs):
    pasta = _pasta_dados()
    if pasta:
        return pd.read_csv(os.path.join(pasta, nome), **kwargs)
    if os.environ.get("M08_OFFLINE") == "1":
        raise FileNotFoundError("dados/ não encontrado e M08_OFFLINE=1 desliga a rede")
    return pd.read_csv(URL_BRUTA + nome, **kwargs)


def tickers_disponiveis():
    return list(ler_csv("precos_ajustados.csv", nrows=0).columns.drop("data"))


def precos(tickers):
    """Adj Close dos tickers na série inteira, com as lacunas isoladas preenchidas.

    Tratamento de ausência do módulo (ADR-009 do acervo): a lacuna isolada,
    pregão sem cotação de um ativo que já era negociado, recebe o último preço
    (ffill). O ffill nunca preenche antes da primeira cotação: a GOLD11 segue
    sem preço até 11/12/2020. O recorte de datas fica para depois dos retornos,
    em metricas.retornos, que usa a janela comum dos tickers pedidos.
    """
    tabela = ler_csv("precos_ajustados.csv", index_col="data", parse_dates=["data"])
    fora = [t for t in tickers if t not in tabela.columns]
    if fora:
        raise TickerDesconhecido(fora)
    return tabela[list(tickers)].ffill()


def taxa_livre_risco(inicio, fim):
    """CDI acumulado no período, anualizado por 252 pregões (SGS 12, em % ao dia).

    O pipeline passa a primeira e a última data da janela comum, para a taxa
    cobrir os mesmos pregões dos retornos.
    """
    cdi = ler_csv("cdi_diario.csv", index_col="data", parse_dates=["data"])["valor"]
    recorte = cdi.loc[inicio:fim] / 100
    return float(np.prod(1 + recorte) ** (PREGOES_ANO / len(recorte)) - 1)
