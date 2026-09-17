"""JSON dos widgets da Aula 01, a partir de tools/medidas_aula01.py.

Uso: .venv/bin/python tools/dados_widgets_aula01.py
Saída: assets/data/aula01-tres-visoes.json e assets/data/aula01-ausencias.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
TICKERS_VISOES = ["MGLU3", "B3SA3", "WEGE3", "BBAS3", "PETR4"]
ATIVOS_AUSENCIAS = ["BOVA11", "IVVB11", "GOLD11", "PETR4", "VALE3"]


def _pct(valor):
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _serie(valores):
    return [None if math.isnan(x) else round(float(x), 2) for x in valores]


def tres_visoes():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    eventos = m.carregar_desdobramentos()
    saida = {"datas": [d.strftime("%Y-%m-%d") for d in fechamento.index], "tickers": {}}
    for ticker in TICKERS_VISOES:
        visoes = m.tres_visoes(ticker).reindex(fechamento.index)
        if ticker == "PETR4":
            leitura = ("PETR4 não tem evento de desdobramento no período. A distância entre Close "
                       "e Adj Close são os proventos: retorno de preço de %s e retorno total de %s."
                       % (_pct(m.retorno_no_periodo(visoes["fechamento"])),
                          _pct(m.retorno_no_periodo(visoes["ajustado"]))))
        else:
            data, variacao = m.maior_variacao_diaria(visoes["negociado"])
            no_close = visoes["fechamento"].dropna().pct_change().loc[data]
            leitura = ("%s em %s: o preço negociado varia %s e o Close do Yahoo, %s."
                       % (ticker, data.strftime("%d/%m/%Y"), _pct(variacao), _pct(no_close)))
        do_ticker = eventos[eventos["ticker"] == ticker]
        saida["tickers"][ticker] = {
            "negociado": _serie(visoes["negociado"]),
            "fechamento": _serie(visoes["fechamento"]),
            "ajustado": _serie(visoes["ajustado"]),
            "eventos": [{"data": d.strftime("%Y-%m-%d"), "fator": float(f)}
                        for d, f in zip(do_ticker["data"], do_ticker["fator"])],
            "leitura": leitura,
        }
    return saida


def ausencias():
    c = m.comparar_tratamentos()
    ausentes = m.ausencias()
    inicio = "/".join(reversed(c["inicio_descartar"].split("-")))
    return {
        "pregoes_total": c["pregoes_total"],
        "ativos": ATIVOS_AUSENCIAS,
        "ausentes": {t: int(ausentes[t]) for t in ausentes.index if ausentes[t] > 0},
        "descartar": {
            "pregoes": c["pregoes_descartar"],
            "vol": {t: round(float(c["vol_descartar"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Descartar mantém %s dos %s pregões e começa a cesta em %s, "
                        "sem março de 2020." % (_milhar(c["pregoes_descartar"]),
                                                 _milhar(c["pregoes_total"]), inicio)),
        },
        "preencher": {
            "pregoes": c["pregoes_preencher"],
            "vol": {t: round(float(c["vol_preencher"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Preencher mantém os %s pregões e dá retorno zero aos três ETFs em "
                        "24/10/2025; o pregão seguinte acumula os dois dias."
                        % _milhar(c["pregoes_preencher"])),
        },
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula01-tres-visoes.json", tres_visoes()), ("aula01-ausencias.json", ausencias())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
