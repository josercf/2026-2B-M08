"""Trava as práticas em camadas e a trilha mínima da Aula 01 (C-07 e C-08).

Cada prática com cronômetro tem no máximo quatro passos obrigatórios, uma ou
duas extensões no fim da lista, troca de condutor e uma checagem antes do fim do
cronômetro. A trilha mínima do material repete os tempos dos autoestudos da
Adalove e a soma sai deles.
"""
import os
import re

import pytest

AULA = "aula01"
PRATICAS = ("pratica-coletor", "pratica-ausencias")
INDISPENSAVEL = ("Cotações do Yahoo Finance no Colab, do jeito reaproveitável",)
RECOMENDADO = ("Coleta de dados financeiros e DataFrames com Pandas",)
SEMANA = "02"

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return fh.read()


def _texto(html):
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def _pratica(sid):
    html = _ler("aulas", AULA + ".html")
    return re.search(r'<section class="exercise-slide" id="%s">(.*?)</section>' % sid, html, re.S).group(1)


def _tempos_adalove():
    tabela = _ler("docs", "autoestudos-por-semana.md").split("## Tempo", 1)[1]
    return {nome: int(t) for sem, nome, t in re.findall(r"\| (\d\d) \| \d \| \d+ \| ([^|]+?) \| (\d+) min \|", tabela)
            if sem == SEMANA}


@pytest.mark.parametrize("sid", PRATICAS)
def test_pratica_tem_obrigatorio_curto_extensao_no_fim_e_checagem(sid):
    secao = _pratica(sid)
    minutos = int(re.search(r'data-minutos="(\d+)"', secao).group(1))
    lista = re.search(r'<ol class="exercise-steps">(.*?)</ol>', secao, re.S).group(1)
    # data-marco marca o item do alarme do cronômetro (troca de papel) e não muda o tipo do passo.
    passos = re.findall(r"<li( class=\"passo-extensao\")?(?: data-marco=\"[^\"]+\")?>", lista)
    obrigatorios = [p for p in passos if not p]
    extensoes = [p for p in passos if p]
    assert 3 <= len(obrigatorios) <= 4, sid
    assert 1 <= len(extensoes) <= 2, sid
    assert passos[-len(extensoes):] == extensoes, "extensão fora do fim da lista"
    assert lista.count('<span class="rotulo-extensao">Extensão</span>') == len(extensoes)
    assert "troquem de papel" in _texto(lista)
    faixa = secao.split('<div class="faixa-nota checagem-pratica">', 1)[1]
    assert secao.index("</ol>") < secao.index("checagem-pratica")
    assert "icones.svg#schedule" in faixa
    checagem = int(re.search(r"Checagem aos (\d+) min:", faixa).group(1))
    assert minutos / 3 <= checagem <= 2 * minutos / 3, (checagem, minutos)
    assert "Debrief:" in faixa
    assert chr(0x2014) not in secao


def test_notas_descrevem_as_camadas_de_cada_pratica():
    notas = _ler("docs", "notas-do-professor", AULA + ".md")
    assert notas.count("**Obrigatório:**") == len(PRATICAS)
    assert notas.count("**Extensão:**") == len(PRATICAS)
    assert notas.count("**Checagem aos 6 min:**") == len(PRATICAS)
    assert notas.count("**Contingência:**") == len(PRATICAS)
    assert chr(0x2014) not in notas


def test_trilha_minima_repete_os_tempos_da_adalove_e_soma_certo():
    html = _ler("materiais", AULA + ".html")
    preparacao = re.search(r'<section class="doc-secao" id="preparacao">(.*?)</section>', html, re.S).group(1)
    trilha = _texto(preparacao.split('id="trilha-minima"', 1)[1].split("Autoestudos da semana", 1)[0])
    tempos = _tempos_adalove()
    assert set(INDISPENSAVEL) | set(RECOMENDADO) == set(tempos)
    for nome in INDISPENSAVEL:
        assert "Indispensável Autoestudo: %s %d min" % (nome, tempos[nome]) in trilha, nome
    for nome in RECOMENDADO:
        assert "Recomendado Autoestudo: %s %d min" % (nome, tempos[nome]) in trilha, nome
    minimo = sum(tempos[n] for n in INDISPENSAVEL)
    assert "A trilha indispensável soma %d min de autoestudo" % minimo in trilha
    assert "a soma de autoestudo chega a %d min" % sum(tempos.values()) in trilha
    assert "não há Atividade Ponderada" in trilha
    assert "Aprofundamento" in trilha
