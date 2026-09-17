"""Trava os achados da Aula 01, medidos em 17/09/2026 sobre dados/.

Se um valor divergir depois de uma nova coleta, o provedor mudou o histórico:
investigar e registrar em dados/README.md antes de atualizar o número aqui, no
deck, no material, nas notas, nos widgets e nas animações.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula01 as m  # noqa: E402


def _variacao_no_dia(serie, dia):
    return round(float(serie.dropna().pct_change().loc[dia]), 4)


def test_negociado_de_b3sa3_cai_67_por_cento_no_desdobramento():
    visoes = m.tres_visoes("B3SA3")
    assert round(float(visoes.loc["2021-05-14", "negociado"]), 2) == 53.55
    assert round(float(visoes.loc["2021-05-17", "negociado"]), 2) == 17.58
    data, variacao = m.maior_variacao_diaria(visoes["negociado"])
    assert data.strftime("%Y-%m-%d") == "2021-05-17"
    assert round(variacao, 4) == -0.6717
    assert _variacao_no_dia(visoes["fechamento"], "2021-05-17") == -0.0151


def test_negociado_de_mglu3_sobe_896_por_cento_no_grupamento():
    visoes = m.tres_visoes("MGLU3")
    assert round(float(visoes.loc["2019-01-02", "negociado"]), 2) == 173.96
    assert round(float(visoes.loc["2024-05-24", "negociado"]), 2) == 1.32
    assert round(float(visoes.loc["2024-05-27", "negociado"]), 2) == 13.15
    data, variacao = m.maior_variacao_diaria(visoes["negociado"])
    assert data.strftime("%Y-%m-%d") == "2024-05-27"
    assert round(variacao, 4) == 8.9621
    assert _variacao_no_dia(visoes["negociado"], "2019-08-06") == -0.8674
    assert _variacao_no_dia(visoes["negociado"], "2020-10-14") == -0.7531


@pytest.mark.parametrize("ticker,dia,variacao", [
    ("WEGE3", "2021-04-28", -0.5069),
    ("BBAS3", "2024-04-16", -0.5057),
    ("EGIE3", "2025-11-27", -0.2851),
])
def test_desdobramento_vira_queda_falsa_no_negociado(ticker, dia, variacao):
    assert _variacao_no_dia(m.preco_negociado(ticker), dia) == variacao


def test_close_do_yahoo_nao_salta_em_nenhum_dos_15_eventos():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    eventos = m.carregar_desdobramentos()
    assert len(eventos) == 15
    for ticker, data in zip(eventos["ticker"], eventos["data"]):
        variacao = fechamento[ticker].dropna().pct_change().loc[data]
        assert abs(variacao) < 0.07, (ticker, data, variacao)


def test_negociado_coincide_com_close_depois_do_ultimo_evento():
    visoes = m.tres_visoes("MGLU3").loc["2026-01-02":]
    assert (visoes["negociado"] - visoes["fechamento"]).abs().max() < 1e-9


@pytest.mark.parametrize("ticker,preco,total", [
    ("PETR4", 0.8712, 6.1600),
    ("VALE3", 0.5238, 1.8986),
    ("BBAS3", -0.1465, 0.4209),
    ("ITUB4", 0.2102, 0.9120),
    ("BOVA11", 0.9884, 0.9884),
    ("IVVB11", 3.4703, 3.4703),
])
def test_proventos_separam_retorno_de_preco_e_retorno_total(ticker, preco, total):
    visoes = m.tres_visoes(ticker)
    assert round(m.retorno_no_periodo(visoes["fechamento"]), 4) == preco
    assert round(m.retorno_no_periodo(visoes["ajustado"]), 4) == total


def test_ausencias_reais_do_provedor():
    ausentes = m.ausencias()
    assert ausentes[ausentes > 0].to_dict() == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}


def test_descartar_datas_mantem_1423_pregoes_a_partir_de_dezembro_de_2020():
    c = m.comparar_tratamentos()
    assert c["pregoes_total"] == 1908
    assert c["pregoes_descartar"] == 1423
    assert c["pregoes_preencher"] == 1908
    assert c["inicio_descartar"] == "2020-12-11"


@pytest.mark.parametrize("ticker,descartar,preencher", [
    ("BOVA11", 0.1851, 0.2341),
    ("IVVB11", 0.1767, 0.2015),
    ("GOLD11", 0.1980, 0.1980),
    ("PETR4", 0.3341, 0.3925),
    ("VALE3", 0.2977, 0.3549),
    ("MGLU3", 0.6775, 0.6541),
])
def test_volatilidade_anual_sob_cada_tratamento(ticker, descartar, preencher):
    c = m.comparar_tratamentos()
    assert round(float(c["vol_descartar"][ticker]), 4) == descartar
    assert round(float(c["vol_preencher"][ticker]), 4) == preencher


def test_preencher_cria_retorno_zero_e_acumula_no_pregao_seguinte():
    retorno = m.comparar_tratamentos()["retorno_bova11_preenchido"]
    assert retorno["2025-10-24"] == 0.0
    assert round(retorno["2025-10-27"], 6) == 0.009252
