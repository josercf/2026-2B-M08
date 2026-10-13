"""Trava os achados da Aula 05, medidos em 13/10/2026 sobre dados/.

As decisões de período, tratamento de ausência (ADR-009, tools/retornos.py), anualização e taxa livre de
risco estão no cabeçalho de tools/medidas_aula05.py. Se um valor divergir depois
de uma nova coleta, o provedor mudou o histórico: investigar e registrar em
dados/README.md antes de atualizar o número aqui, no deck, no notebook, nos
widgets e nas animações.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula05 as m  # noqa: E402


@pytest.fixture(scope="module")
def principal():
    return m.principal()


@pytest.fixture(scope="module")
def deslizantes():
    return m.resultados_deslizantes()


@pytest.fixture(scope="module")
def sensibilidade():
    return m.sensibilidade()


def _r(valor, casas=4):
    return round(float(valor), casas)


def test_periodo_comeca_em_2021_na_janela_comum_e_preenche_24_10_2025():
    """ADR-009: a base é retornos_janela_comum; a lacuna de 24/10/2025 vira retorno zero."""
    retornos = m.carregar_retornos()
    assert retornos.shape == (1412, 15)
    assert retornos.index[0].strftime("%Y-%m-%d") == "2021-01-04"
    assert retornos.index[-1].strftime("%Y-%m-%d") == "2026-08-31"
    assert not retornos.isna().any().any()
    assert [d.strftime("%Y-%m-%d") for d in m.datas_preenchidas()] == ["2025-10-24"]
    dia = retornos.loc["2025-10-24"]
    assert [t for t in retornos.columns if dia[t] == 0.0] == ["BOVA11", "IVVB11", "GOLD11"]


def test_base_e_a_janela_comum_do_modulo():
    import retornos as base
    comum = base.retornos_janela_comum(inicio=m.INICIO_ESTUDO)
    assert m.carregar_retornos().equals(comum)


def test_ledoit_wolf_em_numpy_igual_ao_sklearn():
    covariance = pytest.importorskip("sklearn.covariance")
    retornos = m.carregar_retornos().loc[m.TREINO[0]:m.TREINO[1]].to_numpy()
    nosso, encolhimento = m.ledoit_wolf(retornos)
    referencia = covariance.LedoitWolf().fit(retornos)
    assert abs(encolhimento - referencia.shrinkage_) < 1e-12
    assert np.abs(nosso - referencia.covariance_).max() < 1e-15


@pytest.mark.parametrize("objetivo", m.OBJETIVOS)
def test_otimizador_respeita_soma_1_e_sem_venda_a_descoberto(principal, objetivo):
    pesos = principal[objetivo]["pesos"]
    assert abs(pesos.sum() - 1) < 1e-9
    assert (pesos >= 0).all()


def test_janela_principal_tem_499_pregoes_de_treino_e_250_de_teste(principal):
    assert principal["pregoes_treino"] == 499
    assert principal["pregoes_teste"] == 250
    assert _r(principal["rf_treino"]) == 0.1200
    assert _r(principal["max_sharpe"]["realizado"]["rf"]) == 0.1432


@pytest.mark.parametrize("objetivo,retorno,vol,sharpe", [
    ("max_sharpe", 0.3205, 0.0951, 2.11),
    ("var_min", 0.2077, 0.0746, 1.17),
])
def test_esperado_no_treino(principal, objetivo, retorno, vol, sharpe):
    e = principal[objetivo]["esperado"]
    assert (_r(e["retorno"]), _r(e["vol"]), _r(e["sharpe"], 2)) == (retorno, vol, sharpe)


@pytest.mark.parametrize("objetivo,retorno,vol,sharpe,acumulado,drawdown,fundo", [
    ("max_sharpe", 0.1102, 0.1035, -0.32, 0.1096, -0.0849, "2025-04-08"),
    ("var_min", 0.2112, 0.0881, 0.77, 0.2283, -0.0475, "2025-08-13"),
])
def test_realizado_em_2025(principal, objetivo, retorno, vol, sharpe, acumulado, drawdown, fundo):
    r = principal[objetivo]["realizado"]
    assert _r(r["retorno"]) == retorno
    assert _r(r["vol"]) == vol
    assert _r(r["sharpe"], 2) == sharpe
    assert _r(r["retorno_acumulado"]) == acumulado
    assert _r(r["drawdown_max"]) == drawdown
    assert r["data_fundo"].strftime("%Y-%m-%d") == fundo


@pytest.mark.parametrize("objetivo,esperados", [
    ("max_sharpe", [("IVVB11", 0.4151), ("GOLD11", 0.2106), ("PETR4", 0.1740), ("BBAS3", 0.1681)]),
    ("var_min", [("IVVB11", 0.2744), ("GOLD11", 0.2258), ("EGIE3", 0.1612), ("BBAS3", 0.0824)]),
])
def test_maiores_pesos_da_janela_principal(principal, objetivo, esperados):
    pesos = dict(zip(principal["ativos"], principal[objetivo]["pesos"]))
    assert [(t, _r(w)) for t, w in m.maiores_pesos(pesos)] == esperados


def test_33_janelas_deslizantes_de_2021_a_2026(deslizantes):
    assert len(deslizantes) == 33
    primeira, ultima = deslizantes[0], deslizantes[-1]
    assert primeira["treino"][0].strftime("%Y-%m-%d") == "2021-01-01"
    assert primeira["teste"][1].strftime("%Y-%m-%d") == "2023-12-31"
    assert ultima["treino"][0].strftime("%Y-%m-%d") == "2023-09-01"
    assert ultima["teste"][1].strftime("%Y-%m-%d") == "2026-08-31"


@pytest.mark.parametrize("objetivo,abaixo,abaixo_cdi,prometido,entregue,giro,giro_max", [
    ("max_sharpe", 25, 9, 1.35, 0.53, 0.1191, 0.3232),
    ("var_min", 14, 5, 0.21, 0.70, 0.0323, 0.0788),
])
def test_resumo_das_janelas_deslizantes(deslizantes, objetivo, abaixo, abaixo_cdi,
                                         prometido, entregue, giro, giro_max):
    r = m.resumo_deslizante(deslizantes)[objetivo]
    assert r["abaixo_do_prometido"] == abaixo
    assert r["abaixo_do_cdi"] == abaixo_cdi
    assert _r(r["sharpe_prometido_mediano"], 2) == prometido
    assert _r(r["sharpe_entregue_mediano"], 2) == entregue
    assert _r(r["rotatividade_mensal_mediana"]) == giro
    assert _r(r["rotatividade_mensal_maxima"]) == giro_max


def test_rotatividade_entre_2021_2022_e_2023_2024():
    e = m.estabilidade_duas_janelas()
    assert _r(e["max_sharpe"]["rotatividade"]) == 0.8260
    assert _r(e["var_min"]["rotatividade"]) == 0.3323
    assert [(t, _r(w)) for t, w in m.maiores_pesos(e["max_sharpe"]["a"])] == [
        ("PETR4", 0.7652), ("VALE3", 0.2348)]
    assert _r(e["max_sharpe"]["a"]["IVVB11"]) == 0 and _r(e["max_sharpe"]["a"]["GOLD11"]) == 0
    assert [(t, _r(w)) for t, w in m.maiores_pesos(e["var_min"]["a"])][:2] == [
        ("GOLD11", 0.3591), ("EGIE3", 0.2706)]


def test_maior_peso_de_maximo_sharpe_em_tres_anos_seguidos():
    maiores = [m.maiores_pesos(w, 1)[0] for w in m.tres_janelas()]
    assert [(t, _r(w)) for t, w in maiores] == [("BBAS3", 0.3584), ("BBAS3", 0.3071), ("IVVB11", 0.5256)]


def test_sensibilidade_retorno_perturbado_contra_ledoit_wolf(sensibilidade):
    s = sensibilidade
    assert _r(s["encolhimento"]) == 0.0241
    assert _r(s["erro_padrao_mediano"]) == 0.1763
    assert _r(s["max_sharpe"]["rotatividade_perturbado"]) == 0.1975
    assert _r(s["max_sharpe"]["rotatividade_ledoit_wolf"]) == 0.0191
    assert _r(s["var_min"]["rotatividade_perturbado"]) == 0.0
    assert _r(s["var_min"]["rotatividade_ledoit_wolf"]) == 0.0181


def test_perturbacao_tem_sinal_fixo_por_semente():
    assert m.sinais_perturbacao(15).tolist() == [1, -1, -1, 1, -1, -1, 1, 1, 1, 1, -1, -1, 1, -1, -1]


def test_retorno_perturbado_leva_petr4_de_17_para_27_por_cento(sensibilidade):
    s = sensibilidade["max_sharpe"]
    assert _r(s["base"]["PETR4"], 2) == 0.17
    assert _r(s["perturbado"]["PETR4"], 2) == 0.27


def test_cdi_acumulado_em_2025_fica_entre_as_duas_carteiras(principal):
    cdi = m.cdi_acumulado_no_teste()
    assert _r(cdi) == 0.1426
    assert principal["max_sharpe"]["realizado"]["retorno_acumulado"] < cdi
    assert principal["var_min"]["realizado"]["retorno_acumulado"] > cdi


def test_ativos_de_maior_peso_medio_nas_janelas(deslizantes):
    assert [(t, _r(w)) for t, w in m.ativos_destaque(deslizantes, "max_sharpe")] == [
        ("PETR4", 0.3816), ("BBAS3", 0.2051), ("GOLD11", 0.1661), ("IVVB11", 0.1356), ("ITUB4", 0.0684)]
    assert [t for t, _ in m.ativos_destaque(deslizantes, "var_min")] == [
        "GOLD11", "EGIE3", "IVVB11", "ABEV3", "BBAS3"]


def test_divisao_principal_e_a_janela_25_de_33(deslizantes):
    i = m.janela_da_divisao_principal(deslizantes)
    assert i == 24
    p = m.principal()
    assert np.allclose(deslizantes[i]["max_sharpe"]["pesos"], p["max_sharpe"]["pesos"])


def test_datas_de_inicio_e_fim_do_treino_e_do_teste():
    r = m.carregar_retornos()
    treino = r.loc[m.TREINO[0]:m.TREINO[1]].index
    teste = r.loc[m.TESTE[0]:m.TESTE[1]].index
    assert [d.strftime("%d/%m/%Y") for d in (treino[0], treino[-1], teste[0], teste[-1])] == [
        "02/01/2023", "30/12/2024", "02/01/2025", "30/12/2025"]


def test_notebook_repete_a_regra_da_adr_009_sem_importar_tools():
    """O notebook roda no Colab: reimplementa o tratamento em poucas linhas, citando a ADR-009."""
    import json
    nb = json.load(open(os.path.join(m.RAIZ, "notebooks", "aula05.ipynb"), encoding="utf-8"))
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    assert "ADR-009" in codigo
    assert 'precos.ffill().pct_change(fill_method=None).loc["2021-01-01":].dropna()' in codigo
    assert "precos.dropna()" not in codigo
    assert "import retornos" not in codigo and "medidas_aula05" not in codigo


def test_janelas_vizinhas_compartilham_11_dos_12_meses_de_teste(deslizantes):
    """C-11: as 33 janelas se sobrepõem e não são 33 experimentos independentes."""
    s = m.sobreposicao_deslizante(deslizantes)
    assert (s["meses_compartilhados"], s["meses_de_teste"]) == (11, 12)
    assert _r(s["fracao_compartilhada_mediana"]) == 0.9160
    assert _r(s["fracao_compartilhada_minima"]) == 0.9076
    assert _r(s["fracao_compartilhada_maxima"]) == 0.9274
    assert s["janelas_por_pregao_maximo"] == 12
    assert s["pregoes_testados_distintos"] == 915
    assert s["pregoes_testados_somados"] == 8231


def test_tres_anos_de_teste_sem_sobreposicao(deslizantes):
    """Janelas 0, 12 e 24: testes em 2023, 2024 e 2025, mesma regra de treino de 24 meses."""
    d = m.blocos_disjuntos(deslizantes)
    assert d["n"] == 3
    assert [b["teste"][0].strftime("%Y-%m-%d") for b in d["blocos"]] == ["2023-01-01", "2024-01-01", "2025-01-01"]
    assert [b["treino"][0].strftime("%Y-%m-%d") for b in d["blocos"]] == ["2021-01-01", "2022-01-01", "2023-01-01"]
    for a, b in zip(d["blocos"][:-1], d["blocos"][1:]):
        assert a["teste"][1] < b["teste"][0]
    assert [(_r(b["max_sharpe"]["prometido"], 2), _r(b["max_sharpe"]["entregue"], 2)) for b in d["blocos"]] == [
        (0.67, 1.59), (1.39, -0.25), (2.11, -0.32)]
    assert [(_r(b["var_min"]["prometido"], 2), _r(b["var_min"]["entregue"], 2)) for b in d["blocos"]] == [
        (-0.70, 0.41), (-0.29, 1.09), (1.17, 0.77)]
    assert d["max_sharpe"]["abaixo_do_prometido"] == 2
    assert d["var_min"]["abaixo_do_prometido"] == 1


def test_em_todo_mes_de_partida_o_maximo_sharpe_falha_em_ao_menos_dois_blocos(deslizantes):
    partidas = m.blocos_disjuntos_todas_as_partidas(deslizantes)
    assert len(partidas) == 12
    assert [p["n"] for p in partidas] == [3] * 9 + [2] * 3
    assert min(p["max_sharpe"]["abaixo_do_prometido"] for p in partidas) == 2


@pytest.fixture(scope="module")
def custo():
    return m.custo_da_reotimizacao()


@pytest.mark.parametrize("frequencia,reot,media,ano,custo_ano,bruto,liquido,sh_bruto,sh_liquido", [
    ("mensal", 44, 0.1325, 1.5687, 0.0031, 0.2939, 0.2908, 0.92, 0.90),
    ("trimestral", 15, 0.2269, 0.8750, 0.0018, 0.2593, 0.2576, 0.73, 0.72),
    ("anual", 4, 0.5875, 0.4854, 0.0010, 0.2077, 0.2068, 0.41, 0.41),
])
def test_custo_da_reotimizacao_do_maximo_sharpe(custo, frequencia, reot, media, ano, custo_ano,
                                                 bruto, liquido, sh_bruto, sh_liquido):
    """C-12: carteira trocada e custo hipotético de 0,10% por operação, de 01/2023 a 08/2026."""
    c = custo["max_sharpe"][frequencia]
    assert c["reotimizacoes"] == reot
    assert _r(c["trocada_media"]) == media
    assert _r(c["trocada_por_ano"]) == ano
    assert _r(c["custo_por_ano"]) == custo_ano
    assert _r(c["bruto"]["retorno"]) == bruto
    assert _r(c["liquido"]["retorno"]) == liquido
    assert _r(c["bruto"]["sharpe"], 2) == sh_bruto
    assert _r(c["liquido"]["sharpe"], 2) == sh_liquido
    assert c["pregoes"] == 915
    assert (c["inicio"].strftime("%d/%m/%Y"), c["fim"].strftime("%d/%m/%Y")) == ("02/01/2023", "31/08/2026")
    assert _r(c["rf"]) == 0.1308


def test_custo_da_reotimizacao_da_variancia_minima(custo):
    c = custo["var_min"]
    assert [_r(c[f]["trocada_por_ano"]) for f in ("mensal", "trimestral", "anual")] == [0.4179, 0.2775, 0.1395]
    assert [_r(c[f]["custo_por_ano"]) for f in ("mensal", "trimestral", "anual")] == [0.0008, 0.0006, 0.0003]


def test_custo_zero_devolve_o_retorno_bruto():
    c = m.reotimizacao_com_custo(12, "max_sharpe", custo=0.0)
    assert c["custo_por_ano"] == 0.0
    assert c["liquido"]["retorno"] == c["bruto"]["retorno"]


def test_custo_por_ano_e_custo_vezes_o_dobro_da_carteira_trocada(custo):
    """Valor negociado = soma de |Δw| = 2 x carteira trocada; custo = 0,10% do negociado."""
    for objetivo in m.OBJETIVOS:
        for nome, _ in m.FREQUENCIAS:
            c = custo[objetivo][nome]
            assert abs(c["custo_por_ano"] - m.CUSTO_OPERACAO * 2 * c["trocada_por_ano"]) < 1e-12


def test_reotimizacao_mensal_usa_os_treinos_das_janelas_deslizantes(deslizantes):
    """Cada reotimização mensal até 09/2025 coincide com o treino de uma das 33 janelas."""
    c = m.reotimizacao_com_custo(1, "max_sharpe", custo=0.0)
    assert len(c["pesos"]) == 44
    for k, r in enumerate(deslizantes):
        assert np.allclose(c["pesos"][k], r["max_sharpe"]["pesos"], atol=1e-10), k
    anual = m.reotimizacao_com_custo(12, "max_sharpe", custo=0.0)
    assert [np.allclose(anual["pesos"][i], deslizantes[12 * i]["max_sharpe"]["pesos"], atol=1e-10)
            for i in range(3)] == [True] * 3


def test_notebook_mede_sobreposicao_e_custo_com_a_premissa_declarada():
    import json
    nb = json.load(open(os.path.join(m.RAIZ, "notebooks", "aula05.ipynb"), encoding="utf-8"))
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    texto = "\n".join("".join(c["source"]) for c in nb["cells"])
    assert "CUSTO = %s" % m.CUSTO_OPERACAO in codigo
    assert "treinos[::%d]" % m.PASSO_DISJUNTO in codigo
    assert 'pd.date_range("%s"' % m.INICIO_REOTIMIZACAO in codigo
    assert "premissa declarada" in texto and "hipótese condicionada" in texto
