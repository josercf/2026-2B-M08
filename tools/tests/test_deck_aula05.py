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


def _secao(secao_id):
    return [s for s in _secoes() if 'id="%s"' % secao_id in s][0]


def _texto(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def _milhar(n):
    return "{:,}".format(n).replace(",", ".")


def test_resumo_das_janelas_declara_a_sobreposicao_medida():
    """C-11: o slide das 33 janelas diz quanto do teste duas vizinhas compartilham."""
    s = m.sobreposicao_deslizante()
    texto = _texto(_secao("resumo-janelas"))
    assert "%d dos %d meses de teste" % (s["meses_compartilhados"], s["meses_de_teste"]) in texto
    assert "%s dos pregões, na mediana" % _pct(s["fracao_compartilhada_mediana"]) in texto
    assert "até %d janelas" % s["janelas_por_pregao_maximo"] in texto
    assert "%s pregões de teste somados são %s pregões distintos" % (
        _milhar(s["pregoes_testados_somados"]), _milhar(s["pregoes_testados_distintos"])) in texto


def test_slide_dos_anos_disjuntos_trava_cada_bloco():
    d = m.blocos_disjuntos()
    secao = _secao("janelas-disjuntas")
    texto = _texto(secao)
    for b in d["blocos"]:
        celulas = [b["teste"][0].strftime("%Y"),
                   "%s a %s" % (b["treino"][0].strftime("%m/%Y"), b["treino"][1].strftime("%m/%Y"))]
        celulas += [_num(b[o][k]) for o in m.OBJETIVOS for k in ("prometido", "entregue")]
        linha = re.search(r"<tr><td>%s</td>(.*?)</tr>" % celulas[0], secao, re.S).group(0)
        assert [re.sub(r"<[^>]+>", "", c) for c in re.findall(r"<td[^>]*>(.*?)</td>", linha)] == celulas
    assert "falhou em %d de %d" % (d["max_sharpe"]["abaixo_do_prometido"], d["n"]) in texto
    assert "%d de %d anos" % (d["max_sharpe"]["abaixo_do_prometido"], d["n"]) in texto
    assert "%d de %d anos" % (d["var_min"]["abaixo_do_prometido"], d["n"]) in texto
    partidas = m.blocos_disjuntos_todas_as_partidas()
    minimo = min(p["max_sharpe"]["abaixo_do_prometido"] for p in partidas)
    assert "Nas %d escolhas possíveis" % len(partidas) in texto
    assert "em pelo menos %d blocos em todas" % minimo in texto
    assert "Por que 33 janelas não equivalem a 33 experimentos" in texto


def test_slide_de_custo_trava_a_tabela_e_declara_a_premissa():
    """C-12: carteira trocada e retorno líquido de cada frequência, com a premissa de custo."""
    c = m.custo_da_reotimizacao()["max_sharpe"]
    secao = _secao("custo-reotimizacao")
    texto = _texto(secao)
    for nome, _ in m.FREQUENCIAS:
        f = c[nome]
        celulas = [nome.capitalize(), str(f["reotimizacoes"]), _pct(f["trocada_media"]),
                   _pct(f["trocada_por_ano"]), ("%.2f p.p." % (100 * f["custo_por_ano"])).replace(".", ",", 1),
                   _pct(f["bruto"]["retorno"]), _pct(f["liquido"]["retorno"])]
        linha = re.search(r"<tr[^>]*><td>%s</td>(.*?)</tr>" % celulas[0], secao, re.S).group(0)
        assert re.findall(r"<td>(.*?)</td>", linha) == celulas
    mensal = c["mensal"]
    assert "troca %s ao ano" % _pct(mensal["trocada_por_ano"]) in texto
    assert "custo tira %s p.p. por ano" % _num(100 * mensal["custo_por_ano"]) in texto
    assert "Sharpe passa de %s para %s" % (_num(mensal["bruto"]["sharpe"]), _num(mensal["liquido"]["sharpe"])) in texto
    assert "caminho de %d pregões" % mensal["pregoes"] in texto
    assert "custo de %s sobre o valor negociado" % _pct(m.CUSTO_OPERACAO) in texto
    assert "teste de %s a %s" % (mensal["inicio"].strftime("%d/%m/%Y"), mensal["fim"].strftime("%d/%m/%Y")) in texto


def test_adr_de_exemplo_e_hipotese_condicionada_com_carteira_trocada_e_liquido():
    c = m.custo_da_reotimizacao()["max_sharpe"]["mensal"]
    texto = _texto(_secao("adr"))
    assert "hipótese a validar" in texto
    assert "Decisão condicionada" in texto
    assert "se o custo for até %s" % _pct(m.CUSTO_OPERACAO) in texto
    assert "%s da carteira trocada por ano" % _pct(c["trocada_por_ano"]) in texto
    assert "%s bruto" % _pct(c["bruto"]["retorno"]) in texto
    assert "%s líquido" % _pct(c["liquido"]["retorno"]) in texto
    assert "sem valor de recomendação prática" in texto
    assert "Reotimizar todo mês, treino de 24 meses.\n" not in _html()


def test_quiz_final_pergunta_sobre_a_sobreposicao():
    s = m.sobreposicao_deslizante()
    texto = _texto(_secao("quiz-final"))
    assert "Por que as 33 janelas não equivalem a 33 testes?" in texto
    assert "%d dos %d meses de teste" % (s["meses_compartilhados"], s["meses_de_teste"]) in texto
    d = m.blocos_disjuntos()
    assert ("sem sobreposição cabem %d anos de teste, e o máximo Sharpe ficou abaixo do prometido em %d."
            % (d["n"], d["max_sharpe"]["abaixo_do_prometido"])) in _secao("quiz-final")
    assert len(re.findall(r'class="quiz-question"', _secao("quiz-final"))) == 3
