"""Trava o conteúdo de abertura do deck da Aula 01, a primeira do módulo.

A apresentação do professor e os combinados de participação e entregas só
existem neste deck, logo depois da capa. Os prazos vêm do professor
(13/10/2026): autoestudo em sala até o fim da instrução, autoestudo para casa
e artefato na sexta às 23h59.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula01.html")


def _secoes():
    html = open(DECK, encoding="utf-8").read()
    return re.findall(r"<section\b(.*?)</section>", html, flags=re.S)


def _texto(secao):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", secao))


def test_apresentacao_e_combinados_vem_logo_depois_da_capa():
    secoes = _secoes()
    assert 'class="cover-slide"' in secoes[0]
    assert 'id="professor"' in secoes[1]
    assert 'id="combinados"' in secoes[2]


def test_combinados_trazem_os_prazos_definidos_pelo_professor():
    texto = _texto(_secoes()[2])
    assert "Participação" in texto
    assert "até o fim da instrução" in texto
    assert texto.count("sexta, 23h59") == 2


def test_rodapes_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', open(DECK, encoding="utf-8").read())]
    secoes = _secoes()
    esperados = [i + 1 for i, s in enumerate(secoes) if "footer-page" in s]
    assert numeros == esperados


def test_sem_travessao_no_deck():
    assert chr(0x2014) not in open(DECK, encoding="utf-8").read()
