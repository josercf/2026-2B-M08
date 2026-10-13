"""Trava o deck da Aula 05 contra as medições e contra o planejamento.

Cada número citado no deck é formatado aqui a partir de tools/medidas_aula05.py
e precisa aparecer no HTML: se uma coleta nova mudar o número, o teste reprova
antes do deck ficar desatualizado. Peso das entregas citado do
PLANO_DE_ENSINO.md, seção 5.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula05 as m  # noqa: E402

RAIZ = m.RAIZ
DECK = os.path.join(RAIZ, "aulas", "aula05.html")


def _html():
    return open(DECK, encoding="utf-8").read()


def _secoes():
    return re.findall(r"<section\b(.*?)</section>", _html(), flags=re.S)


def _pct(valor, casas=2):
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",")


def _num(valor):
    return ("%.2f" % valor).replace(".", ",")


@pytest.fixture(scope="module")
def numeros():
    p = m.principal()
    e = m.estabilidade_duas_janelas()
    s = m.sensibilidade()
    r = m.resumo_deslizante()
    ms, vm = p["max_sharpe"], p["var_min"]
    valores = [
        _num(ms["esperado"]["sharpe"]), _num(ms["realizado"]["sharpe"]),
        _num(vm["esperado"]["sharpe"]), _num(vm["realizado"]["sharpe"]),
        _pct(ms["esperado"]["retorno"]), _pct(ms["esperado"]["vol"]),
        _pct(ms["realizado"]["retorno"]), _pct(ms["realizado"]["vol"]),
        _pct(vm["esperado"]["retorno"]), _pct(vm["esperado"]["vol"]),
        _pct(vm["realizado"]["retorno"]), _pct(vm["realizado"]["vol"]),
        _pct(ms["realizado"]["drawdown_max"]), _pct(vm["realizado"]["drawdown_max"]),
        _pct(ms["realizado"]["retorno_acumulado"]), _pct(m.cdi_acumulado_no_teste()),
        _pct(p["rf_treino"]), _pct(ms["realizado"]["rf"]),
        ms["realizado"]["data_fundo"].strftime("%d/%m/%Y"),
        vm["realizado"]["data_fundo"].strftime("%d/%m/%Y"),
        str(p["pregoes_treino"]), str(p["pregoes_teste"]),
        _pct(e["max_sharpe"]["rotatividade"]), _pct(e["var_min"]["rotatividade"]),
        _pct(s["max_sharpe"]["rotatividade_perturbado"]), _pct(s["max_sharpe"]["rotatividade_ledoit_wolf"]),
        _pct(s["var_min"]["rotatividade_ledoit_wolf"]), _pct(s["encolhimento"]),
        _pct(s["erro_padrao_mediano"]),
        _num(r["max_sharpe"]["sharpe_prometido_mediano"]), _num(r["max_sharpe"]["sharpe_entregue_mediano"]),
        _num(r["var_min"]["sharpe_prometido_mediano"]), _num(r["var_min"]["sharpe_entregue_mediano"]),
        _pct(r["max_sharpe"]["rotatividade_mensal_mediana"]), _pct(r["var_min"]["rotatividade_mensal_mediana"]),
        _pct(r["max_sharpe"]["rotatividade_mensal_maxima"]), _pct(r["var_min"]["rotatividade_mensal_maxima"]),
    ]
    for t, w in m.maiores_pesos(dict(zip(p["ativos"], ms["pesos"]))):
        valores.append("%s %s" % (t, _pct(w)))
    for t, w in m.maiores_pesos(dict(zip(p["ativos"], vm["pesos"]))):
        valores.append("%s %s" % (t, _pct(w)))
    for t, w in m.maiores_pesos(e["max_sharpe"]["a"]):
        valores.append("%s %s" % (t, _pct(w)))
    return valores


def test_todo_numero_medido_aparece_no_deck(numeros):
    html = _html()
    faltando = [v for v in numeros if v not in html]
    assert faltando == []


def test_slide_de_treino_e_teste_declara_a_amostra_da_adr_009():
    """Início e número de retornos da janela comum, como a ADR-009 pede."""
    retornos = m.carregar_retornos()
    n = "{:,}".format(len(retornos)).replace(",", ".")
    secao = [s for s in _secoes() if 'id="treino-teste"' in s][0]
    assert "ADR-009" in secao
    assert "desde %s: %s retornos até %s" % (retornos.index[0].strftime("%d/%m/%Y"), n,
                                             retornos.index[-1].strftime("%d/%m/%Y")) in secao
    assert "24/10/2025" in secao and "retorno deles nesse dia é zero" in secao
    assert "sai da cesta inteira" not in _html()


def test_contagens_das_janelas_deslizantes_no_titulo():
    r = m.resumo_deslizante()
    assert "Em %d das 33 janelas o máximo Sharpe" % r["max_sharpe"]["abaixo_do_prometido"] in _html()


def test_peso_das_entregas_citado_do_plano_de_ensino():
    plano = open(os.path.join(RAIZ, "PLANO_DE_ENSINO.md"), encoding="utf-8").read()
    assert re.search(r"\| A4 \| 3 e 4 \| Otimizador de Carteira com Fronteira Eficiente \| 3 \|", plano)
    assert re.search(r"\| Ponderada 2 \| 4 \| .* \| 3 \|", plano)
    texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", _html()))
    assert "A4 vale 3 pontos" in texto
    assert "Individual, 3 pontos" in texto


def test_abre_pelo_resgate_e_pela_verificacao_do_preparo():
    secoes = _secoes()
    assert 'class="cover-slide"' in secoes[0]
    assert 'id="agenda"' in secoes[1]
    assert 'id="resgate"' in secoes[2]
    preparo = [i for i, s in enumerate(secoes) if 'id="preparo"' in s]
    assert preparo and preparo[0] <= 5
    assert 'class="quiz-slide"' in secoes[preparo[0]]


def test_rodapes_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _html())]
    esperados = [i + 1 for i, s in enumerate(_secoes()) if "footer-page" in s]
    assert numeros == esperados


def test_referencias_citadas_existem_na_lista():
    html = _html()
    citadas = {int(n) for n in re.findall(r"\[(\d+)\]", html)}
    listadas = {int(n) for n in re.findall(r'<li id="ref-(\d+)">', html)}
    assert citadas <= listadas
    assert listadas == set(range(1, len(listadas) + 1))


def test_sem_travessao_no_deck():
    assert chr(0x2014) not in _html()
