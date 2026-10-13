"""Trava os achados da Aula 03, medidos em 13/10/2026 sobre dados/.

Se um valor divergir depois de uma nova coleta, o provedor mudou o histórico:
investigar e registrar em dados/README.md antes de atualizar o número aqui, no
deck, no notebook, nos widgets e nas animações.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula03 as m  # noqa: E402


def _r(valor, casas=4):
    return round(float(valor), casas)


# ---------------------------------------------------------------- fórmula

def test_peer_instruction_dois_ativos_de_30_por_cento_com_correlacao_meio():
    pi = m.peer_instruction()
    assert _r(pi["rho_05"]) == 0.2598
    assert _r(pi["rho_1"]) == 0.3
    assert _r(pi["rho_0"]) == 0.2121
    assert _r(pi["rho_menos_1"]) == 0.0


def test_correlacao_um_devolve_a_media_ponderada_das_volatilidades():
    for w in (0.0, 0.25, 0.6, 1.0):
        assert abs(m.risco_dois_ativos(w, 0.4, 0.2, 1.0) - (0.4 * w + 0.2 * (1 - w))) < 1e-12


def test_peso_de_variancia_minima_fica_entre_zero_e_um():
    assert m.peso_variancia_minima(0.3, 0.3, 0.5) == 0.5
    assert m.peso_variancia_minima(0.2, 0.4, 1.0) == 1.0
    assert 0.0 <= m.peso_variancia_minima(0.4, 0.2, 0.9) <= 1.0


# ---------------------------------------------------------------- matriz

def test_retornos_preenchem_para_a_frente_como_na_aula_02():
    rets = m.retornos()
    assert len(rets) == 1907
    contagem = rets.count()
    assert int(contagem["PETR4"]) == 1907
    assert int(contagem["BOVA11"]) == 1907
    assert int(contagem["GOLD11"]) == 1423
    assert rets.loc["2025-10-24", "BOVA11"] == 0.0


def test_volatilidade_e_retorno_repetem_a_tabela_da_aula_02():
    cov = m.matriz_covariancia_anual()
    media = m.retornos().mean() * m.PREGOES_ANO
    assert _r(np.sqrt(cov.loc["BOVA11", "BOVA11"])) == 0.2341
    assert _r(np.sqrt(cov.loc["GOLD11", "GOLD11"])) == 0.1980
    assert _r(media["IVVB11"]) == 0.2182
    assert _r(media["PETR4"]) == 0.3394


def test_matriz_tem_105_pares_e_media_0_2983():
    pares = m.pares_ordenados()
    assert len(pares) == 105
    assert _r(pares.mean()) == 0.2983


def test_par_mais_e_menos_correlacionado_da_cesta():
    pares = m.pares_ordenados()
    assert pares.index[-1] == ("ITUB4", "BBDC4")
    assert _r(pares.iloc[-1]) == 0.8034
    assert pares.index[0] == ("RENT3", "GOLD11")
    assert _r(pares.iloc[0]) == -0.2156


def test_os_dez_pares_mais_negativos_sao_todos_com_gold11():
    pares = m.pares_ordenados()
    assert all("GOLD11" in par for par in pares.index[:10])


@pytest.mark.parametrize("a,b,rho", [
    ("ITUB4", "BBDC4", 0.8034),
    ("BBAS3", "BOVA11", 0.7617),
    ("ITUB4", "BBAS3", 0.7122),
    ("PETR4", "VALE3", 0.4093),
    ("VALE3", "SUZB3", 0.2715),
    ("PETR4", "IVVB11", 0.1397),
    ("ITUB4", "IVVB11", 0.0835),
    ("BOVA11", "GOLD11", -0.2078),
])
def test_correlacoes_citadas_no_deck(a, b, rho):
    c = m.matriz_correlacao()
    assert _r(c.loc[a, b]) == rho
    assert _r(c.loc[b, a]) == rho


@pytest.mark.parametrize("a,b,cov", [
    ("PETR4", "PETR4", 0.1541),
    ("VALE3", "VALE3", 0.1259),
    ("ITUB4", "ITUB4", 0.0862),
    ("IVVB11", "IVVB11", 0.0406),
    ("PETR4", "VALE3", 0.0570),
    ("PETR4", "ITUB4", 0.0525),
    ("PETR4", "IVVB11", 0.0110),
    ("VALE3", "ITUB4", 0.0346),
    ("VALE3", "IVVB11", 0.0200),
    ("ITUB4", "IVVB11", 0.0049),
])
def test_covariancia_anualizada_do_excerto(a, b, cov):
    assert _r(m.matriz_covariancia_anual().loc[a, b]) == cov


def test_diagonal_da_covariancia_anual_e_a_volatilidade_ao_quadrado():
    cov = m.matriz_covariancia_anual()
    assert _r(np.sqrt(cov.loc["PETR4", "PETR4"])) == 0.3925
    assert _r(np.sqrt(cov.loc["IVVB11", "IVVB11"])) == 0.2015


def test_matriz_de_covariancia_da_cesta_e_positiva_definida():
    autovalores = np.linalg.eigvalsh(m.matriz_covariancia_anual().to_numpy())
    assert autovalores.min() > 0


def test_correlacao_media_sobe_em_marco_de_2020():
    c = m.correlacao_media_marco_2020()
    assert c["pregoes_marco_2020"] == 22
    assert _r(c["janela"]) == 0.3588
    assert _r(c["marco_2020"]) == 0.7365


# ---------------------------------------------------------------- curva da animação

def test_curva_de_petr4_com_ivvb11_conforme_a_correlacao_cai():
    curva = {rho: {k: _r(v) for k, v in d.items()} for rho, d in m.curva_por_correlacao().items()}
    assert curva == {
        1.0: {"peso_minimo": 0.0, "risco_minimo": 0.2015, "risco_meio_a_meio": 0.297},
        0.5: {"peso_minimo": 0.009, "risco_minimo": 0.2014, "risco_meio_a_meio": 0.2616},
        0.0: {"peso_minimo": 0.2085, "risco_minimo": 0.1792, "risco_meio_a_meio": 0.2206},
        -0.5: {"peso_minimo": 0.2927, "risco_minimo": 0.1309, "risco_meio_a_meio": 0.17},
        -1.0: {"peso_minimo": 0.3392, "risco_minimo": 0.0, "risco_meio_a_meio": 0.0955},
    }


def test_formatacao_pt_br():
    assert m.pct(0.259807) == "25,98%"
    assert m.pct(-0.6111, 1) == "\u221261,1%"
    assert m.dec(-0.2156) == "\u22120,22"
    assert _r(m.autoverificacao()) == 0.1803
    assert m.pct(m.autoverificacao()) == "18,03%"
    assert m.dec(0.8034) == "0,80"


# ---------------------------------------------------------------- pares

@pytest.mark.parametrize("a,b,esperado", [
    ("ITUB4", "BBDC4", {"vol_a": 0.2936, "vol_b": 0.3409, "rho": 0.8034,
                        "peso_minimo": 0.8614, "risco_minimo": 0.2922, "risco_meio_a_meio": 0.3013}),
    ("PETR4", "IVVB11", {"vol_a": 0.3925, "vol_b": 0.2015, "rho": 0.1397,
                         "peso_minimo": 0.1712, "risco_minimo": 0.1885, "risco_meio_a_meio": 0.2328}),
    ("BOVA11", "GOLD11", {"vol_a": 0.2341, "vol_b": 0.1980, "rho": -0.2078,
                          "peso_minimo": 0.4311, "risco_minimo": 0.1347, "risco_meio_a_meio": 0.1367}),
])
def test_curva_de_risco_dos_pares_do_widget(a, b, esperado):
    par = m.estatisticas_par(a, b)
    for chave, valor in esperado.items():
        assert _r(par[chave]) == valor, chave


def test_retorno_anual_do_par_da_animacao():
    par = m.estatisticas_par("PETR4", "IVVB11")
    assert _r(par["ret_a"]) == 0.3394
    assert _r(par["ret_b"]) == 0.2182


def test_risco_minimo_de_petr4_e_ivvb11_fica_abaixo_dos_dois_ativos():
    par = m.estatisticas_par("PETR4", "IVVB11")
    assert par["risco_minimo"] < min(par["vol_a"], par["vol_b"])


@pytest.mark.parametrize("tickers,vol,media,reducao", [
    (["ITUB4", "BBDC4", "BBAS3"], 0.2964, 0.3261, 0.0911),
    (["ITUB4", "PETR4", "IVVB11"], 0.2154, 0.2958, 0.2718),
])
def test_carteira_de_bancos_contra_carteira_mista(tickers, vol, media, reducao):
    c = m.carteira_igual(tickers)
    assert _r(c["vol"]) == vol
    assert _r(c["media_vols"]) == media
    assert _r(c["reducao"]) == reducao


# ---------------------------------------------------------------- correlação móvel

@pytest.mark.parametrize("a,b,esperado", [
    ("ITUB4", "BBDC4", {"minimo": 0.3404, "data_minimo": "2025-06-04", "maximo": 0.9693,
                        "data_maximo": "2020-03-25", "fim_2019": 0.8156, "fim_marco_2020": 0.9645}),
    ("PETR4", "IVVB11", {"minimo": -0.6111, "data_minimo": "2026-06-03", "maximo": 0.8592,
                         "data_maximo": "2020-03-16", "fim_2019": 0.0085, "fim_marco_2020": 0.7747}),
])
def test_correlacao_movel_de_63_pregoes(a, b, esperado):
    resumo = m.resumo_movel(a, b)
    for chave, valor in esperado.items():
        atual = resumo[chave]
        assert (atual if isinstance(valor, str) else _r(atual)) == valor, chave


# ---------------------------------------------------------------- Ledoit-Wolf

def test_amostra_com_os_15_ativos_cotados():
    assert m.amostra_completa() == {"pregoes": 1423, "inicio": "2020-12-14"}


def test_encolhimento_cresce_quando_a_janela_encurta():
    lw = m.encolhimento_por_janela()
    assert {n: _r(v["intensidade"]) for n, v in lw.items()} == {
        63: 0.1072, 126: 0.0546, 252: 0.0345, 1423: 0.0089}
    assert lw[63]["inicio"] == "2026-06-03"
    assert lw[126]["inicio"] == "2026-03-03"
    assert lw[252]["inicio"] == "2025-08-28"


def test_ledoit_wolf_em_numpy_coincide_com_o_scikit_learn():
    covariance = pytest.importorskip("sklearn.covariance")
    trecho = m.retornos().dropna().iloc[-63:].to_numpy()
    nossa, intensidade = m.ledoit_wolf(trecho)
    deles, intensidade_deles = covariance.ledoit_wolf(trecho)
    assert abs(intensidade - intensidade_deles) < 1e-12
    assert np.abs(nossa - deles).max() < 1e-15


# ---------------------------------------------------------------- resgate e escolha

def test_tabela_de_resgate_repete_a_aula_02():
    t = {k: {c: _r(v) for c, v in d.items()} for k, d in m.tabela_resgate().items()}
    assert t == {"PETR4": {"ret": 0.3394, "vol": 0.3925}, "ITUB4": {"ret": 0.129, "vol": 0.2936},
                 "BBDC4": {"ret": 0.0702, "vol": 0.3409}, "IVVB11": {"ret": 0.2182, "vol": 0.2015}}


def test_escolha_coletiva_classifica_os_oito_pares_pela_regua():
    classes = [(a, b, _r(rho, 2), classe) for a, b, rho, classe in m.escolha_coletiva()]
    assert classes == [
        ("ITUB4", "BBDC4", 0.8, "concentra"), ("BBAS3", "BOVA11", 0.76, "concentra"),
        ("ITUB4", "BBAS3", 0.71, "concentra"), ("PETR4", "VALE3", 0.41, "intermediário"),
        ("VALE3", "SUZB3", 0.27, "diversifica"), ("PETR4", "IVVB11", 0.14, "diversifica"),
        ("ITUB4", "IVVB11", 0.08, "diversifica"), ("BOVA11", "GOLD11", -0.21, "diversifica"),
    ]


def test_regua_nas_bordas():
    assert m.classificar(0.60) == "concentra"
    assert m.classificar(0.5999) == "intermediário"
    assert m.classificar(0.30) == "intermediário"
    assert m.classificar(0.2999) == "diversifica"


def test_erros_comuns_citados_nas_notas_do_professor():
    # Correlação anualizada por engano passa de 1; volatilidade sem o fator 252 fica diária.
    assert int(m.matriz_correlacao().loc["ITUB4", "BBDC4"] * m.PREGOES_ANO) == 202
    diaria = np.sqrt(m.matriz_covariancia_anual().loc["PETR4", "PETR4"] / m.PREGOES_ANO)
    assert m.pct(diaria) == "2,47%"
