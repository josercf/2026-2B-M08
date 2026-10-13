"""Material de apoio e referências da Aula 05: preparação, números medidos e autoestudos.

Os números são formatados aqui a partir de tools/medidas_aula05.py; os títulos e
tempos dos autoestudos vêm de docs/autoestudos-por-semana.md, Semana 08.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula05 as m  # noqa: E402

MATERIAL = os.path.join(m.RAIZ, "materiais", "aula05.html")
REFERENCIAS = os.path.join(m.RAIZ, "referencias", "aula05.html")
AUTOESTUDOS = os.path.join(m.RAIZ, "docs", "autoestudos-por-semana.md")


def _ler(caminho):
    return open(caminho, encoding="utf-8").read()


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _pct(valor):
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def _autoestudos_semana_08():
    linhas = [l for l in _ler(AUTOESTUDOS).splitlines() if l.startswith("| 08 |")]
    return [(c[3], c[4]) for c in (list(map(str.strip, l.strip("|").split("|"))) for l in linhas)]


def test_preparacao_e_a_primeira_secao_com_duas_animacoes_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, re.S)
    assert secoes[0][0] == "preparacao"
    preparo = secoes[0][1]
    assert "aula05-drawdown-teste.mp4" in preparo and "aula05-janela-deslizante.mp4" in preparo
    autoverificacao = preparo.split("1.3 Autoverificação")[1]
    assert autoverificacao.count("<details>") == 5


def test_autoestudos_da_semana_08_com_titulo_e_tempo_exatos():
    autoestudos = _autoestudos_semana_08()
    assert len(autoestudos) == 2
    material = _texto(_ler(MATERIAL))
    referencias = _texto(_ler(REFERENCIAS))
    for titulo, tempo in autoestudos:
        assert "%s (%s)" % (titulo, tempo) in referencias, titulo
        assert "%s (%s)" % (titulo, tempo) in material, titulo


def test_referencias_tem_as_duas_secoes_fixas_na_ordem():
    html = _ler(REFERENCIAS)
    assert html.index('id="autoestudos"') < html.index('id="complementar"')


def test_numeros_do_material_vem_das_medicoes():
    p = m.principal()
    s = m.sensibilidade()
    e = m.estabilidade_duas_janelas()
    r = m.resumo_deslizante()
    ms, vm = p["max_sharpe"], p["var_min"]
    esperados = [
        _pct(ms["realizado"]["retorno_acumulado"]), _pct(vm["realizado"]["retorno_acumulado"]),
        _pct(m.cdi_acumulado_no_teste()), _pct(ms["realizado"]["drawdown_max"]),
        _pct(vm["realizado"]["drawdown_max"]), _pct(ms["esperado"]["retorno"]),
        _pct(ms["realizado"]["retorno"]), _pct(vm["esperado"]["retorno"]), _pct(vm["realizado"]["retorno"]),
        _pct(p["rf_treino"]), _pct(ms["realizado"]["rf"]), _pct(s["erro_padrao_mediano"]),
        _pct(s["encolhimento"]), _pct(s["max_sharpe"]["rotatividade_perturbado"]),
        _pct(s["max_sharpe"]["rotatividade_ledoit_wolf"]), _pct(s["var_min"]["rotatividade_ledoit_wolf"]),
        _pct(e["max_sharpe"]["rotatividade"]), _pct(e["var_min"]["rotatividade"]),
        _pct(e["max_sharpe"]["a"]["PETR4"]), _pct(r["max_sharpe"]["rotatividade_mensal_mediana"]),
        _pct(r["var_min"]["rotatividade_mensal_maxima"]),
        "%d das %d janelas" % (r["max_sharpe"]["abaixo_do_prometido"], r["janelas"]),
    ]
    for ticker, peso in [m.maiores_pesos(w, 1)[0] for w in m.tres_janelas()]:
        esperados.append(_pct(peso))
    texto = _texto(_ler(MATERIAL))
    assert [v for v in esperados if v not in texto] == []


def test_secao_da_amostra_declara_a_janela_comum_da_adr_009():
    retornos = m.carregar_retornos()
    n = "{:,}".format(len(retornos)).replace(",", ".")
    texto = _texto(_ler(MATERIAL))
    assert "ADR-009" in texto
    assert "são %s retornos diários, de %s a %s" % (n, retornos.index[0].strftime("%d/%m/%Y"),
                                                    retornos.index[-1].strftime("%d/%m/%Y")) in texto
    assert "descartada" not in _ler(MATERIAL)


def test_paginas_sem_travessao():
    for caminho in (MATERIAL, REFERENCIAS):
        assert chr(0x2014) not in _ler(caminho)
