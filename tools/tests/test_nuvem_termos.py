"""Extração e agrupamento dos termos da nuvem por voz (assets/js/inteli-nuvem-termos.js).

Pedido de 20/10/2026, depois da primeira aula: a nuvem mostrava muletas e verbos
da fala e partia "Gisele Bündchen" em duas palavras. As funções são puras e
rodam no node.
"""
import json
import os
import shutil
import subprocess

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULO = os.path.join(RAIZ, "assets", "js", "inteli-nuvem-termos.js")

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node ausente")


def _js(expressao):
    codigo = "const T = require(%s); console.log(JSON.stringify(%s));" % (json.dumps(MODULO), expressao)
    return json.loads(subprocess.run(["node", "-e", codigo], capture_output=True, text=True, check=True).stdout)


def _textos(frase):
    return [t["texto"] for t in _js("T.extrair(%s)" % json.dumps(frase))]


def test_fala_da_primeira_aula_perde_muletas_e_verbos():
    frase = ("Olha, cara, legal! Vamos falar, achei bacana, gostei bastante. Ele colocou, "
             "começou assistindo e jogando. Hoje agora, hein, cadê o exemplo?")
    assert _textos(frase) == []


def test_nome_proprio_fica_junto():
    assert "Gisele Bündchen" in _textos("A Gisele Bündchen apareceu no telão")
    assert "gisele" not in [t.lower() for t in _textos("A Gisele Bündchen apareceu")]


def test_vocabulario_do_modulo_passa_e_composto_fica_inteiro():
    textos = _textos("Uma carteira eficiente na fronteira eficiente de Markowitz, com risco e retorno "
                     "para o excedente de caixa do parceiro, com latência baixa e estratégia")
    for termo in ("carteira eficiente", "fronteira eficiente", "excedente de caixa", "risco",
                  "retorno", "parceiro", "markowitz", "latência", "estratégia"):
        assert termo in textos, termo


def test_plural_acento_e_caixa_somam_no_mesmo_termo():
    termos = _js('T.extrair("As ações subiram. Uma ação. AÇÕES.")')
    assert termos == [{"texto": "ações", "peso": 3}]
    assert _js('T.chave("Carteiras")') == _js('T.chave("carteira")')


def test_variacao_de_transcricao_e_agrupada_e_palavra_curta_nao():
    assert _js('T.parecidos("Bündchen", "Bunchen")') is True
    assert _js('T.parecidos("risco", "rico")') is False
    assert _js('T.parecidos("carteira", "cadeira")') is False


def test_so_nome_proprio_absorve_palavra_solta():
    assert _js('T.ehNome("Gisele Bündchen")') is True
    assert _js('T.ehNome("Banco do Brasil")') is True
    assert _js('T.ehNome("taxa livre de risco")') is False
    assert _js('T.parecidos("termo1", "termo2")') is False
