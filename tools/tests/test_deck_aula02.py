"""Trava a estrutura do deck da Aula 02 e amarra os números dele às medições.

Cada número central do deck é formatado aqui a partir de tools/medidas_aula02.py
e procurado no HTML: se a medição mudar, o deck reprova até ser atualizado.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula02 as m  # noqa: E402

DECK = os.path.join(m.RAIZ, "aulas", "aula02.html")


def _html():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _secoes():
    return re.findall(r"<section\b(.*?)</section>", _html(), flags=re.S)


def test_rodapes_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _html())]
    esperados = [i + 1 for i, s in enumerate(_secoes()) if "footer-page" in s]
    assert numeros == esperados


def test_primeira_interacao_e_peer_instruction_sobre_o_preparo():
    secoes = _secoes()
    primeiro_quiz = next(i for i, s in enumerate(secoes) if "quiz-options" in s)
    assert 'id="preparo"' in secoes[primeiro_quiz]
    assert "Votar de novo" in secoes[primeiro_quiz]
    assert 'id="resgate"' in "".join(secoes[:primeiro_quiz])


def test_peer_instruction_usa_as_alternativas_medidas():
    q = m.queda_petr4()
    preparo = next(s for s in _secoes() if 'id="preparo"' in s)
    certa = re.search(r'data-correct="true".*?>([^<]+)</li>', preparo, re.S).group(1)
    assert certa == m.pct(q["log"])
    for chave in ("erro_repetir_simples", "erro_simetrico", "erro_log10"):
        assert ">%s</li>" % m.pct(q[chave]) in preparo, chave


def test_numeros_centrais_do_deck_saem_das_medicoes():
    html = _html()
    j = m.janela_crise()
    c = m.conta_anualizacao()
    cdi = m.cdi()
    caudas = m.caudas()
    for numero in (m.pct(j["soma_simples"]), m.pct(j["acumulado"]), m.pct(j["soma_log"]),
                   m.pct(c["vol_anual"]), m.pct(c["retorno_anual"]), m.pct(c["erro_desvio_vezes_252"]),
                   m.pct(cdi["acumulado"]), m.pct(cdi["anual"]),
                   m.pct(m.cdi("2020-12-11")["acumulado"])):
        assert numero in html, numero
    assert ("%.2f" % abs(caudas["pior_em_desvios"])).replace(".", ",") in html
    assert ("%.2f pontos" % (m.erro_da_soma_simples() * 100)).replace(".", ",") in html


def test_tabela_da_cesta_repete_as_metricas_anualizadas():
    cesta = next(s for s in _secoes() if 'id="cesta"' in s)
    a = m.anualizadas()
    for ticker in a.index:
        linha = re.search(r"<td>%s\*?</td>(.*?)</tr>" % ticker, cesta, re.S).group(1)
        valores = re.findall(r"<td>([^<]+)</td>", linha)
        assert valores == [m.pct(a.loc[ticker, "retorno_anual"]), m.pct(a.loc[ticker, "vol_anual"]),
                           m.pct(a.loc[ticker, "total"])], ticker
    assert len(m.abaixo_do_cdi()) == 9 and "Nove dos 15" in cesta


def test_widgets_e_videos_da_aula_estao_no_deck():
    html = _html()
    for widget in ("simples-log", "vol-janela"):
        assert 'data-widget="%s"' % widget in html
        assert "../assets/js/widgets/%s.js" % widget in html
    for video in ("aula02-histograma-retornos", "aula02-raiz-do-tempo"):
        assert "../assets/video/%s.mp4" % video in html


def test_amarracao_cita_o_peso_do_plano_de_ensino():
    a2 = next(s for s in _secoes() if 'id="a2"' in s)
    assert "A2 vale 3 pontos" in a2
    assert "06/11/2026" in a2
    assert "P5" in next(s for s in _secoes() if 'id="p5"' in s)


def test_sem_travessao_no_deck():
    assert chr(0x2014) not in _html()


MATERIAL = os.path.join(m.RAIZ, "materiais", "aula02.html")
REFERENCIAS = os.path.join(m.RAIZ, "referencias", "aula02.html")
AUTOESTUDOS = ("Risco e retorno: passado e prólogo (70 min)",
               "Análise de uma ação em Python na prática (45 min)")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def test_autoestudos_sao_os_da_semana_4_com_titulo_exato():
    fonte = _ler(os.path.join(m.RAIZ, "docs", "autoestudos-por-semana.md"))
    semana = fonte.split("## Semana 04", 1)[1].split("## Semana", 1)[0]
    for titulo in AUTOESTUDOS:
        assert "- " + titulo.rsplit(" (", 1)[0] in semana, titulo
        assert titulo in _ler(MATERIAL), titulo
        assert titulo in _ler(REFERENCIAS), titulo


def test_material_abre_pela_preparacao_com_animacoes_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, re.S)
    assert secoes[0][0] == "preparacao"
    preparacao = secoes[0][1]
    for video in ("aula02-histograma-retornos", "aula02-raiz-do-tempo"):
        assert "../assets/video/%s.mp4" % video in preparacao
    assert preparacao.count("<details>") == 5
    assert chr(0x2014) not in html


def test_referencias_tem_as_duas_secoes_fixas_na_ordem():
    html = _ler(REFERENCIAS)
    assert html.index('id="autoestudos"') < html.index('id="complementar"')
    assert chr(0x2014) not in html


def test_numeros_do_material_saem_das_medicoes():
    html = _ler(MATERIAL)
    a = m.anualizadas()
    raiz = m.raiz_do_tempo(horizontes=(21, 63, 126, 252))
    picos = m.picos_2020("PETR4")
    numeros = [m.pct(a.loc["PETR4", "log_anual"]), m.pct(a.loc["MGLU3", "log_anual"]),
               m.pct(a.loc["MGLU3", "retorno_anual"]), m.pct(a.loc["BOVA11", "total"]),
               m.pct(m.cdi()["acumulado"]), m.pct(m.cdi("2020-12-11")["acumulado"]),
               m.pct(picos[21]["pico"]), m.pct(picos[63]["pico"]), m.pct(picos[252]["pico"])]
    numeros += [m.pct(raiz[h][k]) for h in raiz for k in ("medido", "previsto")]
    for numero in numeros:
        assert numero in html, numero
    corrido = " ".join(html.split())
    assert ", ".join(m.abaixo_do_cdi()[:-1]) + " e " + m.abaixo_do_cdi()[-1] in corrido
    # Sete anos e meio de amostra cabem em sete janelas anuais sem sobreposição.
    assert m.retornos_simples()["BOVA11"].count() // m.PREGOES_ANO == 7
