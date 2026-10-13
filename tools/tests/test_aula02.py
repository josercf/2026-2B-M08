"""Trava os achados da Aula 02, medidos em 13/10/2026 sobre dados/.

Tratamento de ausência: Adj Close preenchido para a frente por ativo, salvo no
teste do desafio, que mede a decisão invertida. Se um valor divergir depois de
uma nova coleta, o provedor mudou o histórico: investigar e registrar em
dados/README.md antes de atualizar o número aqui, no deck, no notebook, nos
widgets e nas animações.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula02 as m  # noqa: E402


def r4(x):
    return round(float(x), 4)


def test_queda_da_petr4_em_09_03_2020_e_as_alternativas_do_peer_instruction():
    q = m.queda_petr4()
    assert r4(q["simples"]) == -0.2970
    assert r4(q["log"]) == -0.3524
    assert r4(q["erro_simetrico"]) == -0.2600
    assert r4(q["erro_log10"]) == -0.1530
    assert len({r4(q[k]) for k in ("log", "erro_repetir_simples", "erro_simetrico", "erro_log10")}) == 4


def test_a_queda_da_petr4_e_a_pior_da_cesta():
    piores = m.piores_quedas()
    assert piores["simples"].idxmin() == "PETR4"
    assert piores.loc["PETR4", "data"].strftime("%Y-%m-%d") == "2020-03-09"
    assert r4(piores.loc["VALE3", "simples"]) == -0.2456
    assert piores.loc["VALE3", "data"].strftime("%Y-%m-%d") == "2019-01-28"
    # Dez dos 15 piores dias caem em março de 2020.
    assert int((piores["data"].dt.strftime("%Y-%m") == "2020-03").sum()) == 10


@pytest.mark.parametrize("ticker,media,desvio,n", [
    ("PETR4", 0.00135, 0.02473, 1907),
    ("MGLU3", -0.00037, 0.04120, 1907),
    ("BOVA11", 0.00047, 0.01475, 1907),
    ("IVVB11", 0.00087, 0.01269, 1907),
    ("GOLD11", 0.00069, 0.01247, 1423),
])
def test_media_e_desvio_diarios(ticker, media, desvio, n):
    e = m.estatisticas_diarias().loc[ticker]
    assert round(float(e["media"]), 5) == media
    assert round(float(e["desvio"]), 5) == desvio
    assert int(e["n"]) == n


@pytest.mark.parametrize("ticker,retorno,vol,log,total", [
    ("PETR4", 0.3394, 0.3925, 0.2601, 6.1600),
    ("VALE3", 0.2039, 0.3549, 0.1406, 1.8986),
    ("ITUB4", 0.1290, 0.2936, 0.0856, 0.9120),
    ("BBDC4", 0.0702, 0.3409, 0.0118, 0.0936),
    ("BBAS3", 0.1059, 0.3439, 0.0464, 0.4209),
    ("ABEV3", 0.0737, 0.2834, 0.0336, 0.2893),
    ("WEGE3", 0.3083, 0.3513, 0.2462, 5.4447),
    ("EGIE3", 0.1055, 0.2365, 0.0776, 0.7987),
    ("SUZB3", 0.1005, 0.3467, 0.0405, 0.3587),
    ("RENT3", 0.1447, 0.4381, 0.0488, 0.4466),
    ("B3SA3", 0.1887, 0.3924, 0.1118, 1.3312),
    ("MGLU3", -0.0945, 0.6541, -0.3078, -0.9026),
    ("BOVA11", 0.1185, 0.2341, 0.0908, 0.9884),
    ("IVVB11", 0.2182, 0.2015, 0.1979, 3.4703),
    ("GOLD11", 0.1746, 0.1980, 0.1549, 1.3980),
])
def test_metricas_anualizadas_da_cesta(ticker, retorno, vol, log, total):
    a = m.anualizadas().loc[ticker]
    assert r4(a["retorno_anual"]) == retorno
    assert r4(a["vol_anual"]) == vol
    assert r4(a["log_anual"]) == log
    assert r4(a["total"]) == total


def test_mglu3_oscila_mais_e_gold11_menos():
    vol = m.anualizadas()["vol_anual"]
    assert vol.idxmax() == "MGLU3"
    assert vol.idxmin() == "GOLD11"
    assert round(float(vol["MGLU3"] / vol["GOLD11"]), 1) == 3.3


def test_cdi_acumulado_e_anualizado_na_janela():
    c = m.cdi()
    assert c["dias"] == 1926
    assert r4(c["acumulado"]) == 1.0017
    assert r4(c["anual"]) == 0.0951
    assert r4(m.cdi("2020-12-11")["acumulado"]) == 0.8404


def test_nove_ativos_rendem_menos_que_o_cdi():
    assert m.abaixo_do_cdi() == ["ABEV3", "BBAS3", "BBDC4", "BOVA11", "EGIE3",
                                 "ITUB4", "MGLU3", "RENT3", "SUZB3"]


def test_caudas_da_petr4():
    c = m.caudas()
    assert c["n"] == 1907
    assert c["pior_data"] == "2020-03-09"
    assert round(c["pior_em_desvios"], 2) == -12.06
    assert c["alem_3"] == 26
    assert round(c["alem_3_normal"], 1) == 5.1
    assert c["alem_3_marco_2020"] == 12
    assert round(c["curtose"], 1) == 21.9


def test_soma_dos_log_acerta_o_acumulado_na_crise():
    j = m.janela_crise()
    assert j["pregoes"] == 47
    assert r4(j["soma_simples"]) == -0.3419
    assert r4(j["acumulado"]) == -0.4092
    assert r4(j["soma_log"]) == -0.5262
    import math
    assert abs(j["soma_log"] - math.log(1 + j["acumulado"])) < 1e-12


@pytest.mark.parametrize("ticker,janela,pico,data", [
    ("BOVA11", 21, 1.2444, "2020-04-06"),
    ("BOVA11", 63, 0.7896, "2020-05-27"),
    ("BOVA11", 252, 0.4381, "2020-12-23"),
    ("PETR4", 21, 1.9365, "2020-04-02"),
    ("PETR4", 63, 1.2115, "2020-05-25"),
    ("PETR4", 252, 0.6797, "2020-12-23"),
])
def test_janela_curta_reage_primeiro_e_mais_alto(ticker, janela, pico, data):
    p = m.picos_2020(ticker)[janela]
    assert r4(p["pico"]) == pico
    assert p["data"] == data


@pytest.mark.parametrize("h,medido,previsto", [
    (1, 0.0149, 0.0149),
    (5, 0.0310, 0.0333),
    (21, 0.0698, 0.0681),
    (63, 0.1180, 0.1180),
])
def test_dispersao_cresce_com_a_raiz_do_tempo_no_bova11(h, medido, previsto):
    r = m.raiz_do_tempo()[h]
    assert r4(r["medido"]) == medido
    assert r4(r["previsto"]) == previsto


@pytest.mark.parametrize("ticker,descartar,preencher", [
    ("PETR4", 0.3341, 0.3925),
    ("BBAS3", 0.2762, 0.3439),
    ("MGLU3", 0.6775, 0.6541),
    ("GOLD11", 0.1980, 0.1980),
])
def test_desafio_inverter_a_decisao_de_ausencias(ticker, descartar, preencher):
    d = m.descartar_contra_preencher().loc[ticker]
    assert r4(d["descartar"]) == descartar
    assert r4(d["preencher"]) == preencher


def test_so_a_mglu3_ganha_volatilidade_ao_descartar():
    d = m.descartar_contra_preencher()
    assert list(d.index[d["diferenca"] > 0.001]) == ["MGLU3"]
    assert d["diferenca"].idxmin() == "BBAS3"


def test_formato_pct():
    assert m.pct(-0.352367) == "-35,24%"


def test_queda_da_petr4_separa_log_e_simples_em_5_54_pontos():
    q = m.queda_petr4()
    assert r4(q["simples"] - q["log"]) == 0.0554


@pytest.mark.parametrize("ticker,data,simples,log", [
    ("PETR4", "2020-03-09", -0.2970, -0.3524),
    ("PETR4", "2020-03-13", 0.2222, 0.2007),
    ("BOVA11", "2020-03-12", -0.1457, -0.1575),
    ("MGLU3", "2023-11-16", 0.2514, 0.2243),
    ("MGLU3", "2023-05-16", -0.2283, -0.2592),
])
def test_maiores_movimentos_do_widget_simples_log(ticker, data, simples, log):
    mov = m.maiores_movimentos(ticker)
    assert len(mov) == 8
    linha = mov.loc[data]
    assert r4(linha["simples"]) == simples
    assert r4(linha["log"]) == log


def test_log_fica_abaixo_do_simples_em_todo_movimento_grande():
    for ticker in ("PETR4", "BOVA11", "MGLU3"):
        mov = m.maiores_movimentos(ticker)
        assert (mov["log"] < mov["simples"]).all(), ticker


def test_soma_dos_simples_subestima_a_queda_da_crise_em_6_73_pontos():
    assert r4(m.erro_da_soma_simples()) == 0.0673


def test_conta_da_anualizacao_da_petr4():
    c = m.conta_anualizacao()
    assert round(c["media_diaria"], 6) == 0.001347
    assert round(c["desvio_diario"], 6) == 0.024727
    assert round(c["raiz_252"], 2) == 15.87
    assert r4(c["retorno_anual"]) == 0.3394
    assert r4(c["vol_anual"]) == 0.3925
    assert r4(c["erro_desvio_vezes_252"]) == 6.2312


def test_extremos_da_cesta():
    e = m.extremos_da_cesta()
    assert e["maior_total"] == "PETR4"
    assert e["menor_total"] == "MGLU3"
    assert e["maior_vol"] == "MGLU3"
    assert e["menor_vol"] == "GOLD11"
    assert e["ranking_vol"][:3] == ["MGLU3", "RENT3", "PETR4"]


@pytest.mark.parametrize("h,medido,previsto", [
    (126, 0.1268, 0.1669),
    (252, 0.1570, 0.2361),
])
def test_raiz_do_tempo_superestima_horizontes_longos(h, medido, previsto):
    r = m.raiz_do_tempo(horizontes=(h,))[h]
    assert r4(r["medido"]) == medido
    assert r4(r["previsto"]) == previsto
