"""Os JSON dos widgets da Aula 03 repetem as medições travadas, sem número à mão."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dados_widgets_aula03 as gerador  # noqa: E402
import medidas_aula03 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def test_json_versionado_igual_ao_gerado():
    assert _json("aula03-heatmap.json") == json.loads(json.dumps(gerador.heatmap()))
    assert _json("aula03-correlacao-peso.json") == json.loads(json.dumps(gerador.correlacao_peso()))


def test_heatmap_tem_matriz_simetrica_de_15_ativos_com_diagonal_um():
    dados = _json("aula03-heatmap.json")
    n = len(dados["tickers"])
    assert n == 15
    for i in range(n):
        assert dados["correlacao"][i][i] == 1.0
        for j in range(n):
            assert dados["correlacao"][i][j] == dados["correlacao"][j][i]
    i, j = dados["tickers"].index("ITUB4"), dados["tickers"].index("BBDC4")
    assert dados["correlacao"][i][j] == 0.7207
    # Matriz da cesta na janela comum dos 15 ativos (ADR-009): todo par tem 1.423 pregões.
    assert {p for linha in dados["pregoes"] for p in linha} == {1423}
    # A leitura inicial não entrega a resposta da pergunta disparada.
    assert dados["leitura"] == "Passe o cursor sobre uma célula."


def test_correlacao_peso_tem_os_tres_pares_medidos():
    pares = _json("aula03-correlacao-peso.json")["pares"]
    assert [(p["a"], p["b"]) for p in pares] == m.PARES_WIDGET
    petr = pares[1]
    assert (petr["rho"], petr["peso_minimo"], petr["risco_minimo"]) == (0.1397, 0.1712, 0.1885)
    assert "18,85%" in petr["medido"] and "17,12% em PETR4" in petr["medido"]
    assert "1.907 pregões desde 03/01/2019" in petr["medido"]
    ouro = pares[2]
    assert (ouro["pregoes"], ouro["inicio"]) == (1423, "2020-12-14")
    assert (ouro["vol_a"], ouro["peso_minimo"], ouro["risco_minimo"]) == (0.185, 0.5279, 0.1203)
    assert "1.423 pregões desde 14/12/2020" in ouro["medido"]
