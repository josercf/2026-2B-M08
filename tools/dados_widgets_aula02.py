"""JSON dos widgets da Aula 02, a partir de tools/medidas_aula02.py.

Uso: .venv/bin/python tools/dados_widgets_aula02.py
Saída: assets/data/aula02-simples-log.json e assets/data/aula02-vol-janela.json

Nenhum número é digitado aqui: as séries, os picos e as frases de leitura saem
das funções de medidas_aula02.py, que tools/tests/test_aula02.py trava.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula02 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
TICKERS_SIMPLES_LOG = ["PETR4", "BOVA11", "MGLU3"]
TICKERS_VOL = ["BOVA11", "PETR4"]


def _data_br(texto):
    return "/".join(reversed(texto.split("-")))


def _pontos(valor):
    return ("%.2f" % (valor * 100)).replace(".", ",")


def simples_log():
    saida = {"tickers": {}}
    for ticker in TICKERS_SIMPLES_LOG:
        mov = m.maiores_movimentos(ticker)
        primeiro = mov.index[0]
        s, lg = float(mov.iloc[0]["simples"]), float(mov.iloc[0]["log"])
        saida["tickers"][ticker] = {
            "movimentos": [{"data": d.strftime("%Y-%m-%d"),
                            "simples": round(float(linha["simples"]), 4),
                            "log": round(float(linha["log"]), 4)}
                           for d, linha in mov.iterrows()],
            "leitura": ("%s em %s: simples %s, log %s. O log fica %s pontos abaixo."
                        % (ticker, primeiro.strftime("%d/%m/%Y"), m.pct(s), m.pct(lg),
                           _pontos(s - lg))),
        }
    return saida


def _serie(valores):
    return [None if math.isnan(x) else round(float(x), 4) for x in valores]


def vol_janela():
    r = m.retornos_simples()
    a = m.anualizadas()
    saida = {"datas": [d.strftime("%Y-%m-%d") for d in r.index], "janelas": list(m.JANELAS),
             "tickers": {}}
    for ticker in TICKERS_VOL:
        picos = m.picos_2020(ticker)
        saida["tickers"][ticker] = {
            "vol_total": round(float(a.loc[ticker, "vol_anual"]), 4),
            "series": {str(j): _serie(m.vol_movel(ticker, j)) for j in m.JANELAS},
            "leituras": {str(j): "%d pregões: pico de %s em %s" % (j, m.pct(picos[j]["pico"]),
                                                                    _data_br(picos[j]["data"]))
                         for j in m.JANELAS},
        }
    return saida


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula02-simples-log.json", simples_log()),
                        ("aula02-vol-janela.json", vol_janela())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
