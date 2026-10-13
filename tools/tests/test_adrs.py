"""Estrutura mínima das ADRs, pela diretiva global do professor, e as duas
proibições de caractere nos documentos escritos na fundação."""
import glob
import os
import re
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_brand  # noqa: E402

ADRS = sorted(glob.glob(os.path.join(RAIZ, "docs", "adrs", "ADR-*.md")))
SECOES = ["## Contexto", "## Decisão", "## Motivações", "## Riscos conhecidos",
          "## Consequências", "## ADRs relacionadas"]
# O check_brand.py varre só .html, .css e .js, então nenhum Markdown do acervo
# passa pela regra de emoji dele. Estes três guias são Markdown e a proibição
# vale igual neles, junto com a do travessão. A definição de emoji vem do
# próprio validador, para o acervo não ter uma segunda lista de blocos Unicode.
GUIAS = ["CLAUDE.md", "README.md", os.path.join("docs", "ANDAMENTO.md")]
DOCUMENTOS = [os.path.join(RAIZ, guia) for guia in GUIAS] + ADRS


def test_as_seis_adrs_da_fundacao_existem_em_sequencia():
    numeros = [int(re.search(r"ADR-(\d{3})-", os.path.basename(a)).group(1)) for a in ADRS]
    assert numeros[:6] == [1, 2, 3, 4, 5, 6]
    assert numeros == list(range(1, len(numeros) + 1))


def test_cada_adr_tem_cabecalho_e_secoes():
    assert ADRS, "nenhuma ADR encontrada"
    for caminho in ADRS:
        texto = open(caminho, encoding="utf-8").read()
        for campo in ("**Data:**", "**Status:**", "**Decisores:**"):
            assert campo in texto, (os.path.basename(caminho), campo)
        posicoes = [texto.find(s) for s in SECOES]
        assert -1 not in posicoes, (os.path.basename(caminho), posicoes)
        assert posicoes == sorted(posicoes), os.path.basename(caminho)
        assert chr(0x2014) not in texto, os.path.basename(caminho)


@pytest.mark.parametrize("caminho", DOCUMENTOS, ids=lambda c: os.path.basename(c))
def test_documento_da_fundacao_sem_travessao_e_sem_emoji(caminho):
    assert len(DOCUMENTOS) >= len(GUIAS) + 6, len(DOCUMENTOS)
    texto = open(caminho, encoding="utf-8").read()
    nome = os.path.basename(caminho)
    assert chr(0x2014) not in texto, nome
    assert check_brand.EMOJI.search(texto) is None, (nome, check_brand.EMOJI.findall(texto))
