"""Toda prática cronometrada separa missão obrigatória, extensão e checagem.

A auditoria de 13/10/2026 (C-07) mediu práticas de 8 a 12 minutos que pediam
abrir notebook, carregar dado, executar, comparar, discutir e escrever ADR.
O componente do tema (aulas/_fixture-tema.html, slide "Exercício") deixa a
missão obrigatória sem rótulo, marca a extensão com .passo-extensao e põe a
checagem intermediária e o debrief numa .faixa-nota.checagem-pratica. O C-08
pede a trilha mínima de preparo na seção "Preparação" de cada material.
"""
import glob
import os
import re

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECKS = sorted(glob.glob(os.path.join(RAIZ, "aulas", "aula0*.html")))

# Passos obrigatórios que cabem no tempo: acima disso a prática volta a ser
# lista de laboratório.
MAX_OBRIGATORIOS = 4


def _texto(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def _praticas():
    for deck in DECKS:
        with open(deck, encoding="utf-8") as fh:
            html = fh.read()
        for m in re.finditer(r'<section class="exercise-slide" id="([^"]+)"(.*?)</section>', html, re.S):
            minutos = re.search(r'data-minutos="([\d.]+)"', m.group(2))
            if minutos:
                yield os.path.basename(deck), m.group(1), float(minutos.group(1)), m.group(2)


PRATICAS = list(_praticas())


def test_ha_praticas_cronometradas():
    assert len(PRATICAS) == 11


@pytest.mark.parametrize("deck,pid,minutos,corpo", PRATICAS, ids=[p[0] + "#" + p[1] for p in PRATICAS])
def test_pratica_em_camadas(deck, pid, minutos, corpo):
    lista = re.search(r'<ol class="exercise-steps[^"]*">(.*?)</ol>', corpo, re.S).group(1)
    itens = re.findall(r"<li\b([^>]*)>", lista)
    extensoes = [i for i in itens if "passo-extensao" in i]
    obrigatorios = len(itens) - len(extensoes)
    assert 1 <= obrigatorios <= MAX_OBRIGATORIOS, (obrigatorios, pid)
    if minutos > 8:
        assert extensoes, "prática de %s min sem extensão" % minutos
    for item in re.findall(r'<li class="passo-extensao">(.*?)</li>', lista, re.S):
        assert '<span class="rotulo-extensao">Extensão</span>' in item

    faixa = re.search(r'<div class="faixa-nota checagem-pratica">(.*?)</div>', corpo, re.S)
    assert faixa, "sem checagem intermediária"
    checagem = _texto(faixa.group(1))
    n = int(re.search(r"Checagem aos (\d+) min", checagem).group(1))
    assert 0 < n < minutos
    assert "Debrief:" in checagem


@pytest.mark.parametrize("n", range(1, 7))
def test_material_declara_trilha_minima_na_preparacao(n):
    with open(os.path.join(RAIZ, "materiais", "aula%02d.html" % n), encoding="utf-8") as fh:
        html = fh.read()
    preparacao = html.split('id="preparacao"')[1].split('<section class="doc-secao"')[0]
    assert 'id="trilha-minima"' in preparacao
    trilha = _texto(preparacao.split('id="trilha-minima"')[1])
    assert re.search(r"\d+ min", trilha)
