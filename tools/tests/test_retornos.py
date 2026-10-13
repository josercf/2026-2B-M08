"""Trava o tratamento de ausência único do módulo (ADR-009), medido em 13/10/2026.

Uma regra só para as seis aulas: lacuna isolada é preenchida com o último
preço (ffill), nada é preenchido antes da primeira cotação do ativo, métrica de
um ativo usa a série inteira dele e análise conjunta usa a janela comum dos
ativos envolvidos.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import retornos as r  # noqa: E402


def test_so_tres_lacunas_isoladas_sao_preenchidas_todas_em_24_10_2025():
    preenchidas = r.lacunas_preenchidas()
    assert sorted(preenchidas.index.strftime("%Y-%m-%d").unique()) == ["2025-10-24"]
    assert sorted(preenchidas["ticker"]) == ["BOVA11", "GOLD11", "IVVB11"]


def test_nada_e_preenchido_antes_da_primeira_cotacao():
    precos = r.precos_tratados()
    assert precos["GOLD11"].first_valid_index().strftime("%Y-%m-%d") == "2020-12-11"
    assert int(precos["GOLD11"].isna().sum()) == 484


def test_lacuna_preenchida_vira_retorno_zero_e_o_pregao_seguinte_leva_os_dois_dias():
    rets = r.retornos_por_ativo()
    assert float(rets.loc["2025-10-24", "BOVA11"]) == 0.0


def test_metrica_de_um_ativo_usa_a_serie_inteira():
    rets = r.retornos_por_ativo()
    assert len(rets) == 1907
    assert int(rets["PETR4"].notna().sum()) == 1907
    assert round(float(r.volatilidade_anual(rets["PETR4"])), 4) == 0.3925


def test_janela_comum_da_cesta_inteira_comeca_depois_da_gold11_e_perde_marco_de_2020():
    comum = r.retornos_janela_comum()
    assert len(comum) == 1423
    assert comum.index[0].strftime("%Y-%m-%d") == "2020-12-14"
    assert comum.index[-1].strftime("%Y-%m-%d") == "2026-08-31"
    assert comum.loc["2020-03-01":"2020-03-31"].empty
    assert round(float(r.volatilidade_anual(comum["PETR4"])), 4) == 0.3340


def test_janela_comum_sem_gold11_mantem_marco_de_2020():
    sem_ouro = [t for t in r.TICKERS if t != "GOLD11"]
    comum = r.retornos_janela_comum(sem_ouro)
    assert len(comum) == 1907
    assert not comum.loc["2020-03-01":"2020-03-31"].empty


def test_janela_comum_respeita_recorte_de_datas():
    comum = r.retornos_janela_comum(["PETR4", "VALE3"], inicio="2025-01-01", fim="2025-12-31")
    assert comum.index[0].year == 2025 and comum.index[-1].year == 2025
    assert list(comum.columns) == ["PETR4", "VALE3"]
