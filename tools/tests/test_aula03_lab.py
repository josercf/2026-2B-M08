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
