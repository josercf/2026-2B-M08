"""Os JSON dos widgets da Aula 05 repetem as medições travadas, sem número à mão."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula05 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def janela():
    return _json("aula05-janela-treino.json")


def test_janela_treino_tem_33_janelas_e_marca_a_divisao_principal(janela):
    assert len(janela["janelas"]) == 33
    assert janela["principal"] == 24
    principal = janela["janelas"][24]
    assert principal["treino"] == ["01/2023", "12/2024"]
    assert principal["teste"] == ["01/2025", "12/2025"]
    assert janela["ativos"] == m.carregar_retornos().columns.tolist()


def test_janela_principal_repete_prometido_entregue_e_drawdown(janela):
    o = janela["janelas"][24]["objetivos"]
    assert (round(o["max_sharpe"]["prometido"], 2), round(o["max_sharpe"]["entregue"], 2)) == (2.11, -0.32)
    assert (round(o["var_min"]["prometido"], 2), round(o["var_min"]["entregue"], 2)) == (1.17, 0.77)
    assert o["max_sharpe"]["drawdown_max"] == -0.0849
    assert o["max_sharpe"]["data_fundo"] == "08/04/2025"
    assert o["var_min"]["drawdown_max"] == -0.0475
    pesos = dict(zip(janela["ativos"], o["max_sharpe"]["pesos"]))
    assert pesos["IVVB11"] == 0.4151


@pytest.mark.parametrize("objetivo", m.OBJETIVOS)
def test_cada_janela_soma_1_e_traz_o_drawdown_do_teste(janela, objetivo):
    for i, j in enumerate(janela["janelas"]):
        o = j["objetivos"][objetivo]
        assert abs(sum(o["pesos"]) - 1) < 1e-3, (objetivo, i)
        assert min(o["drawdown"]) == o["drawdown_max"], (objetivo, i)
        assert (o["rotatividade"] is None) == (i == 0)


def test_resumo_do_json_bate_com_o_medido(janela):
    assert janela["resumo"]["max_sharpe"]["abaixo_do_prometido"] == 25
    assert janela["resumo"]["var_min"]["abaixo_do_prometido"] == 14
    assert janela["resumo"]["max_sharpe"]["rotatividade_mensal_mediana"] == 0.1191


def test_sensibilidade_repete_as_rotatividades_medidas():
    s = _json("aula05-sensibilidade.json")
    assert s["encolhimento"] == 0.0241
    assert s["erro_padrao_mediano"] == 0.1763
    assert s["perturbacao"] == 0.05
    ms = s["objetivos"]["max_sharpe"]
    assert ms["rotatividade"] == {"base": 0.0, "perturbado": 0.1975, "ledoit_wolf": 0.0191}
    assert s["objetivos"]["var_min"]["rotatividade"]["perturbado"] == 0.0
    petr4 = ms["ativos"].index("PETR4")
    assert (round(ms["base"][petr4], 2), round(ms["perturbado"][petr4], 2)) == (0.17, 0.27)


def test_json_gerado_e_o_mesmo_que_o_versionado():
    """Regerar o JSON a partir de dados/ não muda nada: ninguém editou o arquivo à mão."""
    import dados_widgets_aula05 as d
    assert _json("aula05-sensibilidade.json") == json.loads(json.dumps(d.sensibilidade()))
    assert _json("aula05-janela-treino.json") == json.loads(json.dumps(d.janela_treino()))


def test_janela_treino_inclui_24_10_2025_no_teste_da_divisao_principal(janela):
    """ADR-009: a lacuna de 24/10/2025 é preenchida, e o teste de 2025 tem 250 pregões."""
    o = janela["janelas"][24]["objetivos"]
    assert len(o["max_sharpe"]["drawdown"]) == 250
