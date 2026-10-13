"""Trava a estrutura dos artefatos públicos da Aula 03.

Deck: rodapés em sequência, abertura por Peer Instruction logo depois do resgate,
amarração com o peso e o prazo do PLANO_DE_ENSINO.md. Material: a seção
"Preparação" no topo, com os dois autoestudos da semana 5, as duas animações e
cinco perguntas. Referências: os autoestudos copiados de
docs/autoestudos-por-semana.md, e a seção de leitura complementar presente.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula03.html")
MATERIAL = os.path.join(RAIZ, "materiais", "aula03.html")
REFERENCIAS = os.path.join(RAIZ, "referencias", "aula03.html")
NOTAS = os.path.join(RAIZ, "docs", "notas-do-professor", "aula03.md")
AUTOESTUDOS = os.path.join(RAIZ, "docs", "autoestudos-por-semana.md")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _autoestudos_semana_05():
    bloco = _ler(AUTOESTUDOS).split("## Semana 05", 1)[1].split("## Semana", 1)[0]
    return re.findall(r"^- (.+)$", bloco, flags=re.M)


def test_rodapes_numerados_em_sequencia():
    html = _ler(DECK)
    secoes = re.findall(r"<section\b(.*?)</section>", html, flags=re.S)
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', html)]
    assert numeros == [i + 1 for i, s in enumerate(secoes) if "footer-page" in s]


def test_deck_abre_pelo_resgate_e_pelo_peer_instruction():
    secoes = re.findall(r"<section\b(.*?)</section>", _ler(DECK), flags=re.S)
    assert 'id="resgate"' in secoes[2]
    assert 'id="preparo"' in secoes[3] and "quiz-options" in secoes[3]
    assert "25,98%" in secoes[4]


def test_amarracao_cita_peso_e_prazo_do_plano():
    a3 = _texto(re.search(r'id="a3">(.*?)</section>', _ler(DECK), flags=re.S).group(1))
    assert "A3 Motor de Simulação de Monte Carlo 3" in a3
    assert "Ponderada 1: Diagnóstico de uma carteira herdada 3" in a3
    assert "19/11/2026" in a3 and "20/11/2026, 23h59" in a3


def test_material_abre_pela_preparacao_com_autoestudos_animacoes_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, flags=re.S)
    assert secoes[0][0] == "preparacao"
    preparacao = secoes[0][1]
    for titulo in _autoestudos_semana_05():
        assert titulo in preparacao, titulo
    assert "aula03-curva-correlacao.mp4" in preparacao
    assert "aula03-correlacao-movel.mp4" in preparacao
    assert preparacao.count("<details>") == 5


def test_referencias_copiam_os_autoestudos_e_tem_leitura_complementar():
    html = _ler(REFERENCIAS)
    autoestudos = re.search(r'id="autoestudos">(.*?)</section>', html, flags=re.S).group(1)
    titulos = _autoestudos_semana_05()
    assert len(titulos) == 2
    for titulo in titulos:
        assert titulo in autoestudos, titulo
    assert 'id="complementar"' in html


def test_sem_travessao_nos_artefatos_da_aula():
    for caminho in (DECK, MATERIAL, REFERENCIAS, NOTAS):
        assert chr(0x2014) not in _ler(caminho), caminho
