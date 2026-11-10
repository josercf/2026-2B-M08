"""Trava os números do deck da Aula 03 redesenhada em 10/11/2026 (ADR-017) contra tools/medidas_aula03_lab.py."""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula03_lab as m  # noqa: E402

RAIZ = m.RAIZ
DECK = os.path.join(RAIZ, "aulas", "aula03.html")
NOTEBOOK = os.path.join(RAIZ, "notebooks", "aula03.ipynb")


def _deck():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def test_celula_vazia_do_bova11():
    lac = m.lacuna_bova11()
    assert lac["ret_planilha_2410"] == -1.0
    assert lac["ret_certo_2410"] == 0.0
    assert m.pct(lac["ret_certo_2710"]) == "0,93%"
    assert m.pct(lac["vol_certa"]) == "23,41%"
    assert m.pct(lac["vol_planilha"]) == "43,26%"
    assert "de 23,41% a 43,26% de risco" in _deck()


def test_funcao_do_peer_instruction():
    assert round(m.risco_dois_ativos(0.5, 0.30, 0.30, 0.5), 4) == 0.2598
    assert round(m.risco_dois_ativos(0.5, 0.30, 0.20, 1.0), 4) == 0.25
    assert round(m.risco_dois_ativos(0.4, 0.30, 0.20, -1.0), 4) == 0.0


def test_retiradas_da_carteira_de_demonstracao():
    base, sem = m.retiradas_demo()
    assert m.pct(base) == "18,82%"
    esperado = {"BBAS3": "18,83%", "BBDC4": "18,37%", "VALE3": "20,04%", "WEGE3": "19,95%", "IVVB11": "21,03%"}
    assert {k: m.pct(v) for k, v in sem.items()} == esperado
    assert min(sem, key=sem.get) == "BBDC4" and max(sem, key=sem.get) == "IVVB11"
    deck = _deck()
    for ativo, valor in esperado.items():
        assert "<td>%s</td><td>%s</td>" % (ativo, valor) in deck


def test_carteira_de_demonstracao_fica_fora_das_carteiras_da_prova():
    # As dez carteiras da Ponderada 1 vivem fora do repositório; a de demonstração tem BBAS3 com 35%.
    assert m.CARTEIRA_DEMO["BBAS3"] == 0.35 and abs(sum(m.CARTEIRA_DEMO.values()) - 1) < 1e-12


def test_pares_extremos_da_cesta():
    rho, a, b = m.par_extremo(True)
    assert (a, b, m.dec(rho)) == ("ITUB4", "BBDC4", "0,72")
    rho, a, b = m.par_extremo(False)
    assert (a, b, m.dec(rho)) == ("RENT3", "GOLD11", "-0,22")


def test_bova11_e_dolar_trocam_de_sinal():
    r = m.resumo_bova_dolar()
    assert m.dec(r["corr_precos"]) == "0,26" and m.dec(r["corr_retornos"]) == "-0,36"
    assert m.dec(r["movel_ret_min"]) == "-0,62" and m.dec(r["movel_ret_max"]) == "-0,17"
    assert m.dec(r["movel_precos_min"]) == "-0,91" and m.dec(r["movel_precos_max"]) == "0,60"
    assert "entre -0,62 e -0,17" in _deck() and "de -0,91 a 0,60" in _deck()


def test_caca_ao_bug():
    b = m.caca_ao_bug()
    assert (m.pct(b["certa"]), m.pct(b["bug_365"]), m.pct(b["bug_sem_raiz"])) == ("39,25%", "47,24%", "623,12%")


def test_rodapes_em_sequencia_e_sem_travessao():
    deck = _deck()
    paginas = [int(p) for p in re.findall(r'<p class="footer-page">(\d+)</p>', deck)]
    assert paginas == list(range(2, 2 + len(paginas)))
    assert chr(0x2014) not in deck


def test_slide_de_preparacao_vem_antes_da_descricao_da_ponderada():
    deck = _deck()
    assert deck.index('id="preparacao"') < deck.index('id="ponderada"') < deck.index('id="prova"')


def test_notebook_sem_saida_e_com_badge():
    with open(NOTEBOOK, encoding="utf-8") as fh:
        nb = json.load(fh)
    assert "colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula03.ipynb" in "".join(nb["cells"][0]["source"])
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            assert not c.get("outputs")


def test_media_ponderada_da_demonstracao_do_assert():
    assert m.pct(m.media_ponderada_demo()) == "29,65%"
    assert "18,82% contra 29,65%" in _deck()


def test_deck_sem_peer_instruction_inexistente_e_com_nomes_do_notebook():
    deck = _deck()
    assert "Peer Instruction" not in deck
    with open(NOTEBOOK, encoding="utf-8") as fh:
        nb = fh.read()
    for nome in ("M1. A célula vazia do BOVA11", "M2. A primeira função", "M3. Uma função chamada cinco vezes",
                 "M4. Heatmap e correlação móvel", "M5. Caça ao bug com testes"):
        assert nome in deck and nome in nb, nome


def test_curva_do_slide_da_conta():
    rhos, risco = m.curva_risco_dois_ativos()
    por_rho = {round(float(r), 2): float(v) for r, v in zip(rhos, risco)}
    assert [m.pct(por_rho[k]) for k in (1.0, 0.5, 0.0, -1.0)] == ["30,00%", "25,98%", "21,21%", "0,00%"]
    deck = _deck()
    trecho = deck[deck.index('id="conta"'):deck.index('id="funcao"')]
    assert "aula03-conta-risco.png" in trecho and "25,98%" in trecho and "0,0675" in trecho
    assert os.path.exists(os.path.join(RAIZ, "assets", "img", "aula03-conta-risco.png"))


def test_verificacao_do_preparo_em_dois_slides_com_qr():
    deck = _deck()
    assert deck.index('id="daily"') < deck.index('id="preparo"') < deck.index('id="preparo-conversa"') < deck.index('id="planilha"')
    primeiro = deck[deck.index('id="preparo"'):deck.index('id="preparo-conversa"')]
    segundo = deck[deck.index('id="preparo-conversa"'):deck.index('id="planilha"')]
    assert 'data-pergunta="preparo-risco"' in primeiro and "data-correta" not in primeiro
    assert 'data-pergunta="preparo-risco-2"' in segundo and 'data-correta="0"' in segundo
    assert "abaixo de 30%</li>" in segundo.split("<li>")[1] + "</li>" or "<li>abaixo de 30%</li>" in segundo
    for trecho in (primeiro, segundo):
        assert 'data-sessao="m08-aula03-2026-11-10"' in trecho and "data-quiz-vivo" in trecho
    for script in ("qrcode.js", "inteli-quiz-config.js", "inteli-quiz-dados.js", "inteli-quiz-vivo.js"):
        assert script in deck
    assert "inteli-quiz-vivo.css" in deck


def test_numeros_das_cenas_da_planilha():
    j = m.janela_24_meses_na_planilha()
    assert (j["primeira"], j["ultima"], j["linhas"], j["total"]) == (1412, 1909, 498, 1908)
    assert (j["inicio"], j["fim"]) == ("2024-09-01", "2026-08-31")
    certa, errada = m.correlacao_com_referencia_deslocada()
    assert (m.dec(certa), m.dec(errada)) == ("0,23", "-0,03")
    deck = _deck()
    trecho = deck[deck.index('id="planilha"'):deck.index('id="limites-planilha"')]
    for texto in ("$C$1412:$C$1909", "498 linhas", "da 1412 à 1909", "210 intervalos", "-0,03", "0,23", "105 fórmulas", "1.908 linhas"):
        assert texto in trecho, texto


def test_planilha_tem_quatro_perguntas_com_resposta_e_script_das_cenas():
    deck = _deck()
    trecho = deck[deck.index('id="planilha"'):deck.index('id="limites-planilha"')]
    assert trecho.count('class="fragment pergunta"') == 4 and trecho.count('class="fragment resposta"') == 4
    for cena in ("cena-precos", "cena-grade", "cena-janela", "cena-referencia"):
        assert cena in trecho
    assert trecho.count('<i class="t"') == 105
    assert "inteli-planilha-cena.js" in deck
    assert os.path.exists(os.path.join(RAIZ, "assets", "js", "inteli-planilha-cena.js"))
    recap = deck[deck.index('id="limites-planilha"'):deck.index('id="excel-pandas"')]
    assert "O que precisaria existir para esses cinco limites sumirem?" in recap


def test_slides_de_aaa_e_tdd_vem_antes_dos_tres_testes_da_celula_vazia():
    deck = _deck()
    assert deck.index('id="celula-vazia"') < deck.index('id="aaa"') < deck.index('id="tdd"') < deck.index('id="testes-unidade"') < deck.index('id="conta"')
    aaa = deck[deck.index('id="aaa"'):deck.index('id="tdd"')]
    for texto in ("Arrange", "Act", "Assert", "# Arrange", "# Act", "# Assert"):
        assert texto in aaa, texto
    assert aaa.count('class="fragment codigo-passo"') == 4
    tdd = deck[deck.index('id="tdd"'):deck.index('id="testes-unidade"')]
    for texto in ("Vermelho", "Verde", "Refatorar"):
        assert texto in tdd, texto
    assert tdd.count('<li class="fragment">') == 3 and "passos-cena" in tdd
    with open(os.path.join(RAIZ, "assets", "js", "inteli-planilha-cena.js"), encoding="utf-8") as fh:
        assert ".passos-cena" in fh.read()


TESTES_DO_SLIDE = '''
def test_retorno_de_um_pregao_normal():
    r = retornos(pd.Series([100.0, 110.0]))
    assert round(r.iloc[1], 4) == 0.10

def test_lacuna_vale_zero_e_o_dia_seguinte_acumula():
    r = retornos(pd.Series([100.0, None, 110.0]))
    assert r.iloc[1] == 0 and round(r.iloc[2], 4) == 0.10

def test_antes_da_primeira_cotacao_nao_inventa_preco():
    r = retornos(pd.Series([None, 100.0, 110.0]))
    assert pd.isna(r.iloc[1])
'''


def _rodar_testes_do_slide(regra):
    import pandas as pd
    ns = {"pd": pd, "retornos": regra}
    exec(TESTES_DO_SLIDE, ns)
    falhas = 0
    for nome in [n for n in ns if n.startswith("test_")]:
        try:
            ns[nome]()
        except AssertionError:
            falhas += 1
    return falhas


def test_os_tres_testes_do_slide_passam_com_ffill_e_dois_reprovam_com_fillna_zero():
    import numpy as np
    assert _rodar_testes_do_slide(lambda p: p.ffill().pct_change(fill_method=None)) == 0
    # A troca literal que o slide descreve: fillna(0) no lugar de ffill().
    assert _rodar_testes_do_slide(lambda p: p.fillna(0).pct_change(fill_method=None)) == 2
    deck = _deck()
    for linha in ("def test_retorno_de_um_pregao_normal():", "def test_lacuna_vale_zero_e_o_dia_seguinte_acumula():",
                  "def test_antes_da_primeira_cotacao_nao_inventa_preco():"):
        assert linha in deck
