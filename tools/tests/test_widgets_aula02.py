"""Os JSON dos widgets da Aula 02 repetem as medições travadas, sem número à mão."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula02 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def test_simples_log_tem_oito_movimentos_por_ativo():
    dados = _json("aula02-simples-log.json")
    assert sorted(dados["tickers"]) == ["BOVA11", "MGLU3", "PETR4"]
    for ticker, serie in dados["tickers"].items():
        assert len(serie["movimentos"]) == 8, ticker
        for mov in serie["movimentos"]:
            assert mov["log"] < mov["simples"], (ticker, mov)


def test_simples_log_repete_a_queda_da_petr4():
    petr4 = _json("aula02-simples-log.json")["tickers"]["PETR4"]
    assert petr4["movimentos"][0] == {"data": "2020-03-09", "simples": -0.297, "log": -0.3524}
    for trecho in ("09/03/2020", "-29,70%", "-35,24%", "5,54 pontos"):
        assert trecho in petr4["leitura"], trecho


def test_vol_janela_alinha_series_as_datas_e_repete_os_picos():
    dados = _json("aula02-vol-janela.json")
    assert dados["janelas"] == [21, 63, 252]
    assert len(dados["datas"]) == 1907
    for ticker, bloco in dados["tickers"].items():
        for janela in ("21", "63", "252"):
            assert len(bloco["series"][janela]) == 1907, (ticker, janela)
    bova = dados["tickers"]["BOVA11"]
    assert bova["vol_total"] == 0.2341
    i = dados["datas"].index("2020-04-06")
    assert bova["series"]["21"][i] == 1.2444
    assert bova["leituras"]["21"] == "21 pregões: pico de 124,44% em 06/04/2020"
    assert dados["tickers"]["PETR4"]["leituras"]["252"] == "252 pregões: pico de 67,97% em 23/12/2020"
