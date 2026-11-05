"""Trava a estrutura do deck da Aula 02 (redesenhada em 05/11/2026) e amarra os números às medições.

Cada número central do deck é formatado aqui a partir de tools/medidas_aula02.py
e procurado no HTML: se a medição mudar, o deck reprova até ser atualizado. O
deck não traz o veredito de nenhum grupo; o gabarito vive fora do repositório.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula02 as m  # noqa: E402

DECK = os.path.join(m.RAIZ, "aulas", "aula02.html")
SEQUENCIA = ["capa", "agenda", "resgate", "daily", "vale-jogar", "moeda", "artigo", "simulacao", "bodie",
             "ponte", "comite", "links", "investigacao", "comite-g01", "comite-g02", "comite-g03",
             "comite-g04", "a2", "referencias", "encerramento"]


def _html():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _secoes():
    return re.findall(r"<section\b(.*?)</section>", _html(), flags=re.S)


def _secao(sid):
    return next(s for s in _secoes() if 'id="%s"' % sid in s)


def test_rodapes_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _html())]
    esperados = [i + 1 for i, s in enumerate(_secoes()) if "footer-page" in s]
    assert numeros == esperados


def test_sequencia_de_slides():
    ids = [re.search(r'id="([^"]+)"', s).group(1) for s in _secoes()]
    assert ids == SEQUENCIA


def test_ponte_e_moeda_saem_das_medicoes():
    p = m.ponte_bbdc4()
    ponte = _secao("ponte")
    assert m.pct(p["aritmetica"]) in ponte and m.pct(p["geometrica"]) in ponte
    for ano, valor in p["anuais"].items():
        assert m.pct(valor) in ponte, ano
    notas = _secao("moeda")
    for rodadas in (10, 20):
        t = m.moeda_teorica(rodadas)
        assert m.reais(t["media"]) in notas and m.reais(t["mediana"]) in notas, rodadas
    simulacao = _secao("simulacao")
    assert m.reais(m.moeda_teorica()["mediana"]) in simulacao
    t = m.moeda_teorica()
    bodie = _secao("bodie")
    for chave in ("aritmetica", "geometrica", "aproximacao"):
        assert m.pct(t[chave], 1) in bodie, chave
    assert m.pct(t["variancia"]) in bodie


def test_afirmacoes_do_comite_saem_das_medicoes():
    comite = _secao("comite")
    a = m.afirmacoes_grupos()
    for numero in (a["bbas3_close"], a["mglu3_queda"], a["petr4_vol"]):
        assert numero in comite, numero


def test_votos_do_comite_nao_tem_correta():
    for g in ("g01", "g02", "g03", "g04"):
        s = _secao("comite-" + g)
        assert "data-quiz-vivo" in s and 'data-adr-comite' in s, g
        assert "data-correta" not in s and 'data-correct="true"' not in s, g
        assert 'data-grupo="%s"' % g.upper() in s, g


def test_deck_nao_traz_veredito_dos_grupos():
    texto = re.sub(r"<[^>]+>", " ", _html()).lower()
    # "Sustentada" e "Enganosa" só como opções de voto, uma vez por grupo.
    assert texto.count("sustentada") == 4 and texto.count("enganosa") == 4


def test_componentes_novos_declarados():
    html = _html()
    for js in ("inteli-aula02-dados.js", "inteli-moeda.js", "inteli-adr.js", "inteli-quiz-vivo.js",
               "inteli-codigo.js", "inteli-cronometro.js"):
        assert "../assets/js/%s" % js in html, js
    for css in ("inteli-moeda.css", "inteli-adr.css", "inteli-quiz-vivo.css"):
        assert "../assets/css/%s" % css in html, css
    assert 'data-aluno="../quiz/moeda.html"' in html


def test_amarracao_cita_o_peso_do_plano_de_ensino():
    a2 = _secao("a2")
    assert "A2 vale 3 pontos" in a2
    assert "06/11/2026" in a2


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
