"""Estrutura mínima das ADRs, pela diretiva global do professor."""
import glob
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADRS = sorted(glob.glob(os.path.join(RAIZ, "docs", "adrs", "ADR-*.md")))
SECOES = ["## Contexto", "## Decisão", "## Motivações", "## Riscos conhecidos",
          "## Consequências", "## ADRs relacionadas"]


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
