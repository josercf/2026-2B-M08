#!/usr/bin/env python3
"""
Baixa os dados do case para dados/: preços e eventos corporativos da cesta de
referência (Yahoo Finance, pelo yfinance) e quatro séries do Banco Central (SGS).

Precisa de rede e do yfinance, que fica fora da stack de validação: rodar com
.venv/bin/python. Notebooks e testes nunca chamam este script, eles leem os CSVs
versionados. Rodar de novo só quando a janela mudar, e atualizar a data da
coleta em dados/README.md.

Uso:
    .venv/bin/python tools/baixar_dados.py
"""
import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")

INICIO = "2019-01-01"
FIM = "2026-08-31"
TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3",
           "SUZB3", "RENT3", "B3SA3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"]
SERIES_BCB = {"cdi_diario": 12, "selic_meta": 432, "ipca_mensal": 433, "ptax_venda": 1}
URL_SGS = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
           "?formato=json&dataInicial={inicio}&dataFinal={fim}")


def _gravar(arquivo, cabecalho, linhas):
    with open(os.path.join(DADOS, arquivo), "w", newline="", encoding="utf-8") as fh:
        escritor = csv.writer(fh)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def _data_br(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def baixar_precos():
    import yfinance as yf

    # O yfinance trata "end" como exclusivo: pedir o dia seguinte ao FIM.
    fim_exclusivo = (datetime.strptime(FIM, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    bruto = yf.download([t + ".SA" for t in TICKERS], start=INICIO, end=fim_exclusivo,
                        auto_adjust=False, progress=False, group_by="column", threads=False)
    for coluna, arquivo in (("Adj Close", "precos_ajustados.csv"), ("Close", "precos_fechamento.csv")):
        tabela = bruto[coluna].copy()
        tabela.columns = [c.removesuffix(".SA") for c in tabela.columns]
        tabela = tabela[TICKERS].dropna(how="all")
        tabela.index = tabela.index.strftime("%Y-%m-%d")
        tabela.index.name = "data"
        tabela.to_csv(os.path.join(DADOS, arquivo), float_format="%.6f")


def baixar_eventos():
    import yfinance as yf

    desdobramentos, proventos = [], []
    for ticker in TICKERS:
        ativo = yf.Ticker(ticker + ".SA")
        for serie, destino in ((ativo.splits, desdobramentos), (ativo.dividends, proventos)):
            for quando, valor in serie.items():
                dia = quando.strftime("%Y-%m-%d")
                if INICIO <= dia <= FIM:
                    destino.append((ticker, dia, round(float(valor), 8)))
    _gravar("eventos_desdobramento.csv", ["ticker", "data", "fator"],
            sorted(desdobramentos, key=lambda r: (r[1], r[0])))
    _gravar("eventos_proventos.csv", ["ticker", "data", "valor"],
            sorted(proventos, key=lambda r: (r[1], r[0])))


def baixar_bcb():
    for nome, codigo in SERIES_BCB.items():
        url = URL_SGS.format(codigo=codigo, inicio=_data_br(INICIO), fim=_data_br(FIM))
        pedido = urllib.request.Request(url, headers={"User-Agent": "acervo-2026-2B-M08"})
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            registros = json.load(resposta)
        linhas = [(datetime.strptime(r["data"], "%d/%m/%Y").strftime("%Y-%m-%d"), r["valor"])
                  for r in registros]
        _gravar(nome + ".csv", ["data", "valor"], linhas)


def main():
    os.makedirs(DADOS, exist_ok=True)
    baixar_precos()
    baixar_eventos()
    baixar_bcb()
    for nome in sorted(os.listdir(DADOS)):
        if nome.endswith(".csv"):
            with open(os.path.join(DADOS, nome), encoding="utf-8") as fh:
                print("%-28s %5d linhas" % (nome, sum(1 for _ in fh) - 1))


if __name__ == "__main__":
    main()
