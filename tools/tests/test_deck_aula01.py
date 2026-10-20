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


# Números, Peer Instruction, ordem dos blocos e artefatos de apoio da Aula 01, amarrados a
# tools/medidas_aula01.py: se a medição mudar, o deck, o material ou as notas reprovam.
import json  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula01 as m  # noqa: E402

MATERIAL = os.path.join(RAIZ, "materiais", "aula01.html")
REFERENCIAS = os.path.join(RAIZ, "referencias", "aula01.html")
NOTAS = os.path.join(RAIZ, "docs", "notas-do-professor", "aula01.md")
NOTEBOOK = os.path.join(RAIZ, "notebooks", "aula01.ipynb")
PLANEJAMENTO = os.path.join(RAIZ, "PLANEJAMENTO_AULA_A_AULA.md")
AUTOESTUDOS = ("Coleta de dados financeiros e DataFrames com Pandas (70 min)",
               "Cotações do Yahoo Finance no Colab, do jeito reaproveitável (35 min)")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _pct(valor):
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def _secao(id_):
    return next(s for s in _secoes() if 'id="%s"' % id_ in s)


def test_peer_instruction_de_abertura_usa_as_alternativas_medidas():
    """A pergunta mede o end exclusivo do yfinance, preparado pelos dois autoestudos.
    Cada distrator é uma conta errada medida no snapshot ou no calendário."""
    medida = m.linhas_com_fim_exclusivo()
    secoes = _secoes()
    primeiro_quiz = next(i for i, s in enumerate(secoes) if "quiz-options" in s)
    preparo = secoes[primeiro_quiz]
    assert 'id="preparo"' in preparo and "Votar de novo" in preparo
    assert 'start="2026-08-01", end="2026-08-31"' in preparo
    opcoes = re.findall(r'data-correct="(true|false)".*?>([^<]+)</li>', preparo, re.S)
    assert opcoes == [("false", str(medida["dias_corridos"])),
                      ("false", str(medida["dias_corridos_fim_exclusivo"])),
                      ("false", str(medida["pregoes_inclusivo"])),
                      ("true", str(medida["pregoes_fim_exclusivo"]))]
    resposta = _texto(_secao("fim-exclusivo"))
    assert "devolve %d dos %d pregões" % (medida["pregoes_fim_exclusivo"], medida["pregoes_inclusivo"]) in resposta
    # A explicação da alternativa certa mora no data-explica do calendário animado.
    assert "segunda-feira, 31/08" in _secao("fim-exclusivo") and medida["dia_da_semana_do_fim"] == 0


def test_peer_instruction_do_planejamento_e_o_do_deck():
    secao = _ler(PLANEJAMENTO).split("### Aula 01 - ", 1)[1].split("### Aula 02 - ", 1)[0]
    bloco1 = " ".join(secao.split("Bloco 1 (0 a 15 min)", 1)[1].split("Bloco 2 (15 a 30 min)", 1)[0].split())
    medida = m.linhas_com_fim_exclusivo()
    assert "Peer Instruction" in bloco1
    assert "com as opções %d, %d, %d e %d" % (medida["dias_corridos"], medida["dias_corridos_fim_exclusivo"],
                                               medida["pregoes_inclusivo"], medida["pregoes_fim_exclusivo"]) in bloco1
    assert "a certa é %d" % medida["pregoes_fim_exclusivo"] in bloco1
    depois = " ".join(secao.split("Depois do encontro", 1)[1].split())
    for trecho in ("máquina limpa", "M08_OFFLINE=1", "cesta e a janela do grupo", "SPEC.md"):
        assert trecho in depois, trecho


def _bloco_do_slide(n):
    """Bloco do roteiro de cada slide, lido do comentário de cabeçalho do deck."""
    for linha in re.findall(r"Bloco (\d) \(\d+ a \d+\)\s+slides? (\d+) (?:a|e) (\d+)", _ler(DECK)):
        if int(linha[1]) <= n <= int(linha[2]):
            return int(linha[0])
    return None


def test_proventos_da_petr4_ficam_no_bloco_3_como_o_roteiro_diz():
    secoes = _secoes()
    indice = next(i for i, s in enumerate(secoes) if 'id="proventos"' in s)
    assert _bloco_do_slide(indice + 1) == 3
    assert indice > next(i for i, s in enumerate(secoes) if 'id="escolha-visoes"' in s)
    visoes = m.tres_visoes("PETR4")
    proventos = _secao("proventos")
    for numero in (_pct(m.retorno_no_periodo(visoes["fechamento"])),
                   _pct(m.retorno_no_periodo(visoes["ajustado"])),
                   _pct(m.razao_ajustado_fechamento("PETR4"))):
        assert numero in proventos, numero
    assert "87,12%" in proventos and "616,00%" in proventos
    assert "616,00%" not in "".join(secoes[:indice - 4])


def test_slide_da_mglu3_nao_entrega_a_resposta_da_previsao():
    """O título e o pôster do slide da animação ficam antes do grupamento de 27/05/2024."""
    mglu3 = _secao("mglu3")
    titulo = re.search(r"<h2>(.*?)</h2>", mglu3).group(1)
    data, variacao = m.maior_variacao_diaria(m.tres_visoes("MGLU3")["negociado"])
    assert data.strftime("%d/%m/%Y") in titulo
    assert _pct(variacao) not in mglu3 and "896" not in mglu3
    assert "Antes de tocar" in mglu3


def test_adr_de_exemplo_e_marcado_como_exemplo():
    adr = _texto(_secao("adr"))
    assert "Exemplo" in adr and "(exemplo)" in adr
    assert "próprio coletor" in adr


def test_entrega_e_review_do_a1_no_mesmo_dia():
    a1 = _texto(_secao("a1"))
    assert "A1 vale 3 pontos" in a1
    assert "Review da Sprint 1 e entrega do A1 no mesmo dia: sexta, 23/10/2026" in a1


def test_desafio_do_notebook_junta_maquina_limpa_e_cesta_do_grupo():
    notebook = _texto(_secao("notebook"))
    assert "M08_OFFLINE=1" in notebook and "cesta do grupo" in notebook and "SPEC.md" in notebook
    nb = json.loads(_ler(NOTEBOOK))
    desafio = "".join("".join(c["source"]) for c in nb["cells"]
                      if "".join(c["source"]).startswith("## 6. Desafio") or "TICKERS_GRUPO" in "".join(c["source"])
                      or 'os.environ["M08_OFFLINE"] = "1"' in "".join(c["source"]))
    for trecho in ("Colab novo", 'os.environ["M08_OFFLINE"] = "1"', "1.908 pregões", "TICKERS_GRUPO"):
        assert trecho in desafio, trecho
    assert m.comparar_tratamentos()["pregoes_total"] == 1908


def test_autoestudos_sao_os_da_semana_2_com_titulo_exato():
    fonte = _ler(os.path.join(RAIZ, "docs", "autoestudos-por-semana.md"))
    semana = fonte.split("## Semana 02", 1)[1].split("## Semana", 1)[0]
    tabela = fonte.split("## Tempo", 1)[1]
    for titulo in AUTOESTUDOS:
        nome, tempo = titulo.rsplit(" (", 1)
        assert "- " + nome in semana, titulo
        assert "| 02 | 1 | 5 | %s | %s |" % (nome, tempo.rstrip(")")) in tabela, titulo
        assert titulo in _ler(MATERIAL), titulo
        assert titulo in _ler(REFERENCIAS), titulo


def test_material_abre_pela_preparacao_com_animacoes_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, re.S)
    assert secoes[0][0] == "preparacao"
    preparacao = secoes[0][1]
    assert preparacao.index("Autoestudos da semana") < preparacao.index("<video")
    for video in ("aula01-tres-visoes-mglu3", "aula01-mapa-ausencias"):
        assert "../assets/video/%s.mp4" % video in preparacao
        assert "../assets/img/%s-poster.png" % video in preparacao
    assert preparacao.count("<details>") == 5
    assert preparacao.count("Resposta comentada") == 5
    assert chr(0x2014) not in html


def test_numeros_do_material_saem_das_medicoes():
    html = _ler(MATERIAL)
    c = m.comparar_tratamentos()
    pi = m.linhas_com_fim_exclusivo()
    mglu3 = m.tres_visoes("MGLU3")["negociado"]
    b3 = m.tres_visoes("B3SA3")
    numeros = [_pct(m.maior_variacao_diaria(mglu3)[1]),
               _pct(mglu3.pct_change().loc["2019-08-06"]), _pct(mglu3.pct_change().loc["2020-10-14"]),
               _pct(m.maior_variacao_diaria(b3["negociado"])[1]),
               _pct(b3["fechamento"].dropna().pct_change().loc["2021-05-17"])]
    for ticker, dia in (("WEGE3", "2021-04-28"), ("BBAS3", "2024-04-16"), ("EGIE3", "2025-11-27")):
        numeros.append(_pct(m.preco_negociado(ticker).pct_change().loc[dia]))
    for ticker in ("PETR4", "VALE3", "ITUB4", "BBAS3", "BOVA11", "IVVB11"):
        visoes = m.tres_visoes(ticker)
        numeros += [_pct(m.retorno_no_periodo(visoes["fechamento"])),
                    _pct(m.retorno_no_periodo(visoes["ajustado"])),
                    _pct(m.razao_ajustado_fechamento(ticker))]
    for ticker in ("PETR4", "VALE3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"):
        numeros += [_pct(c["vol_descartar"][ticker]), _pct(c["vol_preencher"][ticker])]
    for ticker in ("BOVA11", "IVVB11", "GOLD11"):
        numeros.append(_pct(c["retorno_etfs_preenchido"][ticker]["2025-10-27"]))
    for numero in numeros:
        assert numero in html, numero
    ausentes = m.ausencias()
    corrido = " ".join(re.sub(r"<[^>]+>", " ", html).split())
    assert "%d células vazias" % ausentes.sum() in corrido
    assert "%d pregões sem cotação" % ausentes["GOLD11"] in corrido
    assert "1.423 dos 1.908" in corrido and c["pregoes_descartar"] == 1423
    assert "R$ 1,32 em 24/05/2024 para R$ 13,15 em 27/05/2024" in corrido
    pregoes = m.carregar_precos("precos_fechamento.csv").loc["2026-08-01":"2026-08-30"].index
    assert "pregões de %s a %s" % (pregoes[0].strftime("%d/%m"), pregoes[-1].strftime("%d/%m/%Y")) in corrido
    assert len(pregoes) == pi["pregoes_fim_exclusivo"]
    assert "A review da Sprint 1 e a entrega do A1 caem no mesmo dia, sexta, 23/10/2026" in corrido


def test_referencias_seguem_a_numeracao_do_deck():
    html = _ler(REFERENCIAS)
    assert html.index('id="autoestudos"') < html.index('id="complementar"')
    deck = _secao("referencias")
    ids_deck = re.findall(r'<li id="(ref-\d+)">', deck)
    complementar = html.split('id="complementar"', 1)[1]
    assert re.findall(r'<li id="(ref-\d+)">', complementar) == ids_deck
    for ref in ids_deck:
        link_deck = re.search(r'<li id="%s">.*?href="([^"]+)"' % ref, deck, re.S)
        link_pagina = re.search(r'<li id="%s">.*?href="([^"]+)"' % ref, complementar, re.S)
        assert link_deck.group(1) == link_pagina.group(1), ref
    citadas = set(re.findall(r"\[(\d+)\]", _ler(DECK)))
    assert citadas <= {r.split("-")[1] for r in ids_deck}, citadas
    assert chr(0x2014) not in html


def test_notas_cobrem_os_sete_blocos_e_o_gabarito_do_peer_instruction():
    notas = _ler(NOTAS)
    for bloco in range(1, 8):
        assert "## Bloco %d " % bloco in notas, bloco
    pi = m.linhas_com_fim_exclusivo()
    for alternativa in ("dias_corridos", "dias_corridos_fim_exclusivo", "pregoes_inclusivo"):
        assert "| %d | não |" % pi[alternativa] in notas, alternativa
    assert "| %d | sim |" % pi["pregoes_fim_exclusivo"] in notas
    assert "Se a turma chega sem o pré-aula" in notas
    assert chr(0x2014) not in notas
