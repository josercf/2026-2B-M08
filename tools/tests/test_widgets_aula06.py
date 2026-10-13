"""Os JSON dos widgets da Aula 06 repetem o que a API de exemplo devolve, sem número à mão."""
import json
import os
import sys

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("scipy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dados_widgets_aula06 as gerador  # noqa: E402
import medidas_aula06 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def test_json_gravado_e_igual_ao_que_o_gerador_produz_hoje():
    """JSON velho no repositório reprova: regere com tools/dados_widgets_aula06.py."""
    assert _json("aula06-requisicoes.json") == json.loads(json.dumps(gerador.requisicoes(), ensure_ascii=False))
    assert _json("aula06-verificador.json") == json.loads(json.dumps(gerador.verificador(), ensure_ascii=False))


def test_montador_tem_nove_casos_com_os_status_medidos():
    dados = _json("aula06-requisicoes.json")
    status = m.status_por_caso()
    assert len(dados["casos"]) == 9
    for caso in dados["casos"]:
        rota, corpo = caso["chave"].split("|")
        assert caso["status"] == status["%s %s" % (rota, corpo)]
        assert caso["resposta"]


def test_montador_mostra_a_fronteira_encurtada_e_diz_quantos_pares_faltam():
    caso = [c for c in _json("aula06-requisicoes.json")["casos"]
            if c["chave"] == "POST /carteiras/otimizar|valido"][0]
    assert '"pregoes": 1906' in caso["resposta"]
    assert "mais 48 pares" in caso["resposta"]


def test_verificador_declara_o_exercicio_e_repete_a_verificacao():
    dados = _json("aula06-verificador.json")
    assert "Nenhum modelo o gerou" in dados["aviso"]
    assert [n["trecho"] for n in dados["numeros"] if not n["confere"]] == ["17,13%", "30,00%"]
    assert len(dados["numeros"]) == 12
    assert "10 de 12" in dados["leitura"]
    for numero in dados["numeros"]:
        assert numero["trecho"] in dados["texto"]
