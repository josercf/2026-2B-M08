"""Trava a Aula 04 em turnos (ADR-018): deck, tela de spec, material, referências e notas.

Estáticos: ordem do deck (daily, portal, painel, preparo, turnos, nuvens, quiz, A3), o
que cada slide de turno declara (função, onde roda, quem implementa, entrega), os
números citados do arquivo de cotações, a amarração que cita só o A3 e a ausência de
otimização como conteúdo do encontro. Navegador: a tela de spec no modo de memória
(?quiz-demo=1), com o painel de links e a visão de projetor do deck do professor.
"""
import json
import os
import re
import sys
import urllib.parse

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_brand  # noqa: E402
import check_slides  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula04.html")
SPEC = os.path.join(RAIZ, "aulas", "aula04-spec.html")
MATERIAL = os.path.join(RAIZ, "materiais", "aula04.html")
REFERENCIAS = os.path.join(RAIZ, "referencias", "aula04.html")
NOTAS = os.path.join(RAIZ, "docs", "notas-do-professor", "aula04.md")
PLANEJAMENTO = os.path.join(RAIZ, "PLANEJAMENTO_AULA_A_AULA.md")
AUTOESTUDOS = os.path.join(RAIZ, "docs", "autoestudos-por-semana.md")
COTACOES = os.path.join(RAIZ, "assets", "data", "aula04-cotacoes.json")
SESSAO = "m08-aula04-2026-11-18"
PORTAL = "https://josercf.github.io/2026-2B-M08/simulador/"

# Turno: (função, onde roda, quem implementa, comando ou função de conferência)
TURNOS = {
    1: ("retorno_do_dia(pesos, retornos_do_dia)", "Colab", "à mão e sem IA", "conferir_turno1"),
    2: ("metricas(pesos, retornos)", "Colab", "à mão e sem IA", "conferir_turno2"),
    3: ("sortear_pesos(k, rng)", "kit", "o agente", "python conferir.py 3"),
    4: ("simular(retornos, n, semente, rf)", "kit", "o agente", "python conferir.py 4"),
    5: ("posicionar(pesos, retornos, rf)", "kit", "o agente", "python conferir.py 5"),
}


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _sem_comentario(html):
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _secoes():
    """(id, html) de cada slide, na ordem do deck."""
    return re.findall(r'<section class="[^"]*" id="([\w-]+)"[^>]*>(.*?)</section>', _ler(DECK), flags=re.S)


def _secao(ident):
    return dict(_secoes())[ident]


def _aula(numero):
    texto = _ler(PLANEJAMENTO)
    return texto.split("### Aula %s - " % numero, 1)[1].split("\n### ", 1)[0]


def _autoestudos_semana_06():
    bloco = _ler(AUTOESTUDOS).split("## Semana 06", 1)[1].split("## Semana", 1)[0]
    return re.findall(r"^- (.+)$", bloco, flags=re.M)


def _milhar(n):
    return "{:,}".format(n).replace(",", ".")


def _data_br(iso):
    return "/".join(reversed(iso.split("-")))


# ------------------------------------------------------------------ deck

def test_rodapes_numerados_em_sequencia():
    secoes = _secoes()
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _ler(DECK))]
    assert numeros == [i + 1 for i, (_, s) in enumerate(secoes) if "footer-page" in s]
    assert len(numeros) >= 15


def test_deck_segue_a_ordem_dos_sete_blocos():
    ids = [i for i, _ in _secoes()]
    assert ids[:3] == ["capa", "agenda", "daily"]
    ordem = ["daily", "portal", "painel", "preparo", "preparo-sharpe", "anatomia", "adrs-kit",
             "turno1-codigo", "turno1", "turno2", "passagem", "turno3", "turno4", "specs-t4",
             "turno5", "specs-t5", "nuvens", "quiz-propriedades", "quiz-sorteada", "quiz-conferir",
             "a3", "referencias", "encerramento"]
    posicoes = [ids.index(i) for i in ordem]
    assert posicoes == sorted(posicoes)
    assert ids[-1] == "encerramento"


def test_capa_mantem_o_titulo_e_a_data_do_planejamento():
    capa = _texto(_secao("capa"))
    cabecalho = _aula("04").splitlines()[0]
    assert "Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz" in cabecalho
    assert "Da Nuvem à Fronteira" in capa and "Monte Carlo e Otimização de Markowitz" in capa
    assert "Data: 18/11/2026" in _aula("04") and "18/11/2026" in capa


def test_daily_tem_tres_perguntas_e_cronometro_de_15_minutos():
    daily = _secao("daily")
    assert daily.count('class="daily-numero"') == 3
    assert re.search(r'class="cronometro[^"]*"[^>]*data-minutos="15"', daily)
    assert "19/11" in _texto(daily)


def test_agenda_segue_o_padrao_enxuto_e_o_deck_nao_inventa_horario_de_relogio():
    agenda = _secao("agenda")
    assert "<tr><th>Bloco</th><th>Tema</th></tr>" in agenda
    assert re.findall(r"<tr><td>([^<]+)</td><td>", agenda) == ["Daily", "1", "2", "3", "4", "5", "6", "7"]
    temas = dict(re.findall(r"<tr><td>([^<]+)</td><td>([^<]+)</td></tr>", agenda))
    assert "Portal" in temas["1"] and "quiz" in temas["2"] and "quiz" in temas["7"]
    for bloco, turno in (("3", "Turnos 1 e 2"), ("4", "Turno 3"), ("5", "Turno 4"), ("6", "Turno 5")):
        assert turno in temas[bloco], bloco
    # Horário de relógio segue pendente (P1): só o prazo do A3 tem hora no deck.
    assert not re.search(r"\b\d{1,2}h\d{2}\b", _texto(_sem_comentario(_ler(DECK))).replace("23h59", ""))


def test_slide_do_portal_tem_qr_code_endereco_e_o_que_o_aluno_faz():
    portal = _secao("portal")
    assert 'data-qr="%s"' % PORTAL in portal
    assert 'href="%s"' % PORTAL in portal
    texto = _texto(portal)
    for trecho in ("iniciais", "G01 a G04", "Visitante", "2 a 5", "aula de Negócios", "9 pregões"):
        assert trecho in texto, trecho
    assert portal.count('class="pn"') == 4


def test_numeros_do_arquivo_de_cotacoes_sao_os_citados():
    dados = json.loads(_ler(COTACOES))
    frase = "%d ativos e %d pregões, de %s a %s" % (len(dados["precos"]), len(dados["datas"]),
                                                    _data_br(dados["datas"][0]), _data_br(dados["datas"][-1]))
    assert frase == "162 ativos e 718 pregões, de 02/01/2024 a 13/11/2026"
    assert frase in _texto(_secao("portal"))
    assert frase in _texto(_ler(MATERIAL))
    assert frase in _ler(NOTAS)


def test_painel_do_portal_aparece_no_bloco_1_e_no_bloco_7_com_a_previsao():
    for ident in ("painel", "nuvens"):
        secao = _secao(ident)
        assert 'data-src="../simulador/?painel=1"' in secao, ident
        assert 'href="../simulador/?painel=1"' in secao, ident
    previsao = _texto(_secao("painel"))
    assert "prevê" in previsao and "pesos iguais" in previsao
    nuvens = _texto(_secao("nuvens"))
    assert "pesos iguais" in nuvens and "Solver" in nuvens


def test_quiz_ao_vivo_nos_blocos_2_e_7():
    perguntas = {}
    for ident, secao in _secoes():
        for atributos in re.findall(r"<div class=\"quiz-vivo[^\"]*\" data-quiz-vivo([^>]*)>", secao):
            assert 'data-sessao="%s"' % SESSAO in atributos, ident
            pergunta = re.search(r'data-pergunta="([\w-]+)"', atributos).group(1)
            correta = int(re.search(r'data-correta="(\d)"', atributos).group(1))
            opcoes = re.findall(r"<li>(.*?)</li>", secao.split('class="quiz-vivo-opcoes"', 1)[1].split("</ol>", 1)[0])
            assert len(opcoes) == 3 and correta < len(opcoes), ident
            enunciado = re.search(r'data-enunciado="([^"]+)"', atributos).group(1)
            assert enunciado in secao.split("quiz-vivo-enunciado", 1)[1], ident
            perguntas[ident] = (pergunta, opcoes[correta])
    assert list(perguntas) == ["preparo", "preparo-sharpe", "quiz-propriedades", "quiz-sorteada", "quiz-conferir"]
    assert len({p for p, _ in perguntas.values()}) == 5
    assert perguntas["preparo"][1] == "para os pesos somarem 1"
    assert perguntas["preparo-sharpe"][1] == "0,60"
    assert "NumPy" in perguntas["quiz-propriedades"][1]
    assert "melhor entre as sorteadas" in perguntas["quiz-sorteada"][1]
    assert "conferir.py" in perguntas["quiz-conferir"][1]
    # Gabarito espalhado: a resposta certa não fica sempre na mesma posição.
    corretas = re.findall(r'data-quiz-vivo[^>]*data-correta="(\d)"', _ler(DECK))
    assert len(set(corretas)) == 3


def test_sharpe_do_quiz_bate_com_a_conta():
    enunciado = _texto(_secao("preparo-sharpe"))
    retorno, risco, rf = (int(n) for n in re.search(
        r"rende (\d+)% ao ano, com risco de (\d+)% ao ano, e a taxa livre de risco é (\d+)%", enunciado).groups())
    assert ("%.2f" % ((retorno - rf) / risco)).replace(".", ",") == "0,60"


def test_preparo_cita_os_dois_autoestudos_da_semana_6():
    titulos = _autoestudos_semana_06()
    assert len(titulos) == 2
    deck = _ler(DECK)
    for titulo in titulos:
        assert titulo in deck, titulo
        assert "Autoestudo: %s" % titulo in _aula("04")


def test_anatomia_do_turno_tem_cinco_passos_e_os_cinco_campos_da_spec():
    anatomia = _secao("anatomia")
    assert anatomia.count('class="pn"') == 5
    texto = _texto(anatomia)
    for campo in ("Função", "Entrada", "Saída", "Casos de borda", "Critério de aceite"):
        assert campo in texto, campo
    for passo in ("Ler a spec", "Escrever o teste à mão", "ver o teste falhar", "Implementar", "marcar o turno"):
        assert passo in texto, passo


def test_adrs_do_kit_aparecem_como_exemplo():
    texto = _texto(_secao("adrs-kit"))
    assert "ADR-001" in texto and "ADR-002" in texto
    assert "exemplo" in texto and "individual" in texto
    for nome in ("ADR-001-janela-dos-dados.md", "ADR-002-sorteio-dos-pesos.md"):
        assert os.path.isfile(os.path.join(RAIZ, "exemplos", "aula04-simulador", "docs", "adrs", nome)), nome


def test_turno_1_mostra_funcao_e_teste_linha_a_linha_sem_entregar_o_corpo():
    secao = _secao("turno1-codigo")
    assert "data-codigo-passos" in secao
    codigo = _texto(secao.split('<pre class="codigo-linhas">', 1)[1].split("</pre>", 1)[0])
    assert "def retorno_do_dia(pesos, retornos_do_dia):" in codigo
    assert "def test_" in codigo and "assert abs(r - 0.005)" in codigo
    assert "return None" in codigo
    for pista in ("np.dot", "sum(", " @ ", "zip("):
        assert pista not in codigo, pista
    passos = re.findall(r'class="fragment codigo-passo" data-linhas="([\d,]+)"', secao)
    linhas = len(re.findall(r'<span class="cl" data-n="\d+">', secao))
    assert len(passos) >= 5
    assert all(1 <= int(n) <= linhas for p in passos for n in p.split(","))
    # O exemplo do teste sai de cabeça: 0,5 x 2% + 0,5 x (-1%) = 0,5%.
    assert abs(0.5 * 0.02 + 0.5 * -0.01 - 0.005) < 1e-12


@pytest.mark.parametrize("turno", sorted(TURNOS))
def test_cada_turno_diz_funcao_onde_quem_implementa_e_entrega(turno):
    funcao, onde, quem, conferencia = TURNOS[turno]
    secao = _secao("turno%d" % turno)
    assert re.search(r'class="cronometro" id="cronometro-turno%d" data-minutos="\d+"' % turno, secao)
    cabecalho = re.findall(r"<th>(.*?)</th>", secao)
    assert cabecalho == ["Função", "Onde", "Quem implementa", "Entrega"]
    celulas = [_texto(c) for c in re.findall(r"<td>(.*?)</td>", secao, flags=re.S)]
    assert len(celulas) == 4
    assert funcao in celulas[0]
    assert onde in celulas[1]
    assert quem in celulas[2]
    assert conferencia in celulas[3]
    assert "Turno %d" % turno in re.search(r"<h2>(.*?)</h2>", secao).group(1)


def test_turnos_a_mao_ficam_no_colab_e_os_demais_no_kit_com_agente():
    for turno in (1, 2):
        texto = _texto(_secao("turno%d" % turno))
        assert "sem IA" in texto and "agente" not in texto, turno
    for turno in (3, 4, 5):
        texto = _texto(_secao("turno%d" % turno))
        assert "agente" in texto and "Colab" not in texto, turno
    assert "colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula04.ipynb" in _secao("turno1")
    assert "tela de spec" in _texto(_secao("turno4")) and "tela de spec" in _texto(_secao("turno5"))
    assert "10.000 simulações" in _texto(_secao("turno5")) and "menos de 10 segundos" in _texto(_secao("turno5"))


def test_minutos_dos_turnos_cabem_nos_blocos_de_15():
    minutos = {i: int(re.search(r'class="cronometro" id="[\w-]+" data-minutos="(\d+)"', s).group(1))
               for i, s in _secoes() if i in ("turno1", "turno2", "passagem", "turno3", "turno4", "turno5")}
    assert minutos["turno1"] + minutos["turno2"] <= 15
    assert minutos["passagem"] + minutos["turno3"] <= 15
    assert minutos["turno4"] <= 15 and minutos["turno5"] <= 15


def test_passagem_para_o_kit_lista_zip_ambiente_funcoes_e_primeiro_pedido():
    secao = _secao("passagem")
    assert 'href="../materiais/aula04-simulador.zip"' in secao
    texto = _texto(secao)
    for trecho in ("python checar_ambiente.py", "simulador.py", "python conferir.py 1", "python conferir.py 2",
                   "AGENTS.md", "SPEC.md", "sem escrever código", "mesmo grupo"):
        assert trecho in texto, trecho
    for arquivo in ("checar_ambiente.py", "conferir.py", "AGENTS.md", "SPEC.md", "simulador.py"):
        assert os.path.isfile(os.path.join(RAIZ, "exemplos", "aula04-simulador", arquivo)), arquivo


def test_deck_do_professor_tem_links_prazo_e_projetor_das_duas_sessoes_de_spec():
    for turno in (4, 5):
        secao = _secao("specs-t%d" % turno)
        assert 'data-adr-links data-sessao="%s-t%d"' % (SESSAO, turno) in secao
        assert 'data-pagina="aula04-spec.html?g={grupo}&amp;turno=%d"' % turno in secao
        assert re.search(r'data-minutos="\d+"', secao)
    projetor = _secao("specs-projetor")
    paineis = re.findall(r'data-adr-comite data-sessao="%s-t(\d)" data-grupo="(G0\d)" data-turno="(\d)"' % SESSAO,
                         projetor)
    assert sorted(paineis) == sorted((str(t), "G0%d" % g, str(t)) for t in (4, 5) for g in range(1, 5))
    rotulos = json.loads(re.search(r"data-rotulos='([^']+)'", projetor).group(1))
    assert rotulos == {"contexto": "Entrada", "criterios": "Saída", "opcoes": "Casos de borda"}


def test_amarracao_cita_so_o_a3_com_peso_e_prazo_da_fonte():
    a3 = _texto(_secao("a3"))
    plano = _aula("04")
    assert "A3 Motor de Simulação de Monte Carlo, peso 3" in a3
    assert "A3 Motor de Simulação de Monte Carlo (peso 3)" in plano
    for data in ("19/11/2026", "20/11/2026, 23h59"):
        assert data in a3 and data in plano, data
    assert "A4" not in a3
    assert "decisão sua" in a3 and "exemplo" in a3
    pesos = [int(p) for p in re.findall(r"<td>(\d+)%</td>", _secao("a3"))]
    assert pesos == [30, 10, 10, 15, 15, 20] and sum(pesos) == 100


def test_otimizacao_nao_e_conteudo_do_encontro():
    texto = _texto(_sem_comentario(_ler(DECK)))
    for termo in ("SLSQP", "variância mínima", "máximo Sharpe", "scipy", "otimizar("):
        assert termo not in texto, termo
    # "fronteira" só aparece no título do encontro e no título do autoestudo.
    resto = texto.replace("Da Nuvem à Fronteira", "").replace("Da nuvem à fronteira eficiente de Markowitz", "")
    assert "ronteira" not in resto
    assert "A4" not in texto


def test_encerramento_cita_a_data_e_o_titulo_da_aula_05_do_planejamento():
    aula05 = _aula("05")
    titulo = re.match(r"Semana \d+ - (.+?)\s+\(Sprint", aula05.splitlines()[0]).group(1)
    data = re.search(r"Data: (\d\d/\d\d/\d{4})", aula05).group(1)
    fim = _texto(_secao("encerramento"))
    assert "Até %s" % data in fim and "Aula 05: %s" % titulo in fim


def test_referencias_do_deck_sao_numeradas_e_citadas():
    refs = re.findall(r'<li id="ref-(\d)">', _secao("referencias"))
    assert refs == [str(i) for i in range(1, len(refs) + 1)] and len(refs) >= 5
    citadas = {n for rodape in re.findall(r'<p class="footer-bar">(.*?)</p>', _ler(DECK)) for n in re.findall(r"\[(\d)\]", rodape)}
    assert citadas and citadas <= set(refs)


def test_titulos_sem_listicle_e_sem_paralelismo():
    titulos = [re.search(r"<h[12]>(.*?)</h[12]>", s).group(1) for _, s in _secoes()]
    assert len(titulos) == len(_secoes())
    for titulo in titulos:
        assert not re.match(r"(As|Os) (duas|dois|três|quatro|cinco|seis|sete|\d+) ", titulo), titulo
        assert not re.search(r"não é .+, é |não apenas", titulo), titulo


def test_deck_carrega_os_componentes_do_padrao_da_aula_03():
    deck = _ler(DECK)
    for script in ("inteli-codigo.js", "inteli-quiz-vivo.js", "inteli-cronometro.js", "inteli-adr.js",
                   "inteli-aula02-dados.js", "aula04-turnos.js", "inteli-tela-cheia.js", "inteli-print.js"):
        assert "../assets/js/%s" % script in deck, script


# ------------------------------------------------- material, referências, notas

def test_artefatos_novos_sem_travessao_e_sem_emoji():
    for caminho in (DECK, SPEC, MATERIAL, REFERENCIAS, NOTAS,
                    os.path.join(RAIZ, "assets", "js", "aula04-turnos.js"),
                    os.path.join(RAIZ, "assets", "js", "aula04-spec.js"),
                    os.path.join(RAIZ, "assets", "css", "aula04-turnos.css")):
        texto = _ler(caminho)
        assert chr(0x2014) not in texto, caminho
        assert check_brand.EMOJI.search(texto) is None, caminho


def test_material_abre_pela_preparacao_com_os_autoestudos_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, flags=re.S)
    assert secoes[0][0] == "preparacao"
    preparacao = secoes[0][1]
    for titulo, minutos in re.findall(r"Autoestudo: (.+) \((\d+) min\)", _aula("04")):
        linha = re.search(r"<tr><td>[^<]+</td><td>Autoestudo: %s</td><td>(\d+) min</td>" % re.escape(titulo), preparacao)
        assert linha and linha.group(1) == minutos, titulo
    assert 'id="trilha-minima"' in preparacao
    assert preparacao.count("<details>") == 5


def test_material_tem_o_roteiro_dos_turnos_os_links_e_a_leitura_v1():
    html = _ler(MATERIAL)
    turnos = html.split('id="turnos"', 1)[1].split("</section>", 1)[0]
    for funcao, _, _, conferencia in TURNOS.values():
        assert funcao in _texto(turnos), funcao
        assert conferencia in _texto(turnos), conferencia
    for link in ('href="../simulador/"', 'href="aula04-simulador.zip"',
                 "colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula04.ipynb"):
        assert link in html, link
    depois = html.split('id="depois"', 1)[1].split("</section>", 1)[0]
    assert 'href="aula04-v1.html"' in depois
    assert "notebooks/aula04-v1.ipynb" in depois
    texto = _texto(depois)
    assert "19/11/2026" in texto and "20/11/2026, 23h59" in texto and "3 pontos" in texto
    assert "otimização" in texto and "Aula 05" in texto


def test_referencias_copiam_os_autoestudos_e_tem_leitura_complementar():
    html = _ler(REFERENCIAS)
    autoestudos = re.search(r'id="autoestudos">(.*?)</section>', html, flags=re.S).group(1)
    for titulo in _autoestudos_semana_06():
        assert titulo in autoestudos, titulo
    complementar = re.search(r'id="complementar">(.*?)</section>', html, flags=re.S).group(1)
    assert '<ol class="doc-referencias">' in complementar
    assert "aula04-v1.html" in complementar


def test_notas_do_professor_cobrem_blocos_turnos_e_contingencias():
    notas = _ler(NOTAS)
    for faixa in ("0 a 15", "15 a 30", "30 a 45", "45 a 60", "60 a 75", "75 a 90", "90 a 105"):
        assert "| %s |" % faixa in notas, faixa
    for turno in range(1, 6):
        bloco = notas.split("**Turno %d (" % turno, 1)[1].split("\n\n", 1)[0]
        for termo in ("Obrigatório", "Checagem aos", "Erros comuns", "Contingência"):
            assert termo in bloco, (turno, termo)
    contingencias = notas.split("## Contingências", 1)[1].split("\n## ", 1)[0]
    for trecho in ("?demo=1", "Ativo do grupo ausente do arquivo", "outra dupla do mesmo grupo",
                   "ordem de corte: turno 5, depois a tela de spec"):
        assert trecho in contingencias, trecho
    visitantes = notas.split("## Visitantes na sala", 1)[1].split("\n## ", 1)[0]
    assert '"Visitante"' in visitantes and "fora do placar" in visitantes


def test_portal_do_acervo_aponta_para_os_artefatos_novos():
    card = re.search(r'<article class="card-aula" id="aula-04">(.*?)</article>', _ler(os.path.join(RAIZ, "index.html")),
                     flags=re.S).group(1)
    for href in ("aulas/aula04.html", "materiais/aula04.html", "referencias/aula04.html",
                 "https://github.com/josercf/2026-2B-M08/blob/main/notebooks/aula04.ipynb"):
        assert 'href="%s"' % href in card, href
    assert "SLSQP" not in card and "-v1" not in card


def test_versao_anterior_preservada_com_links_entre_os_arquivos_v1():
    for partes in (("aulas", "aula04-v1.html"), ("materiais", "aula04-v1.html"),
                   ("referencias", "aula04-v1.html"), ("docs", "notas-do-professor", "aula04-v1.md")):
        assert os.path.isfile(os.path.join(RAIZ, *partes)), partes
    material = _ler(os.path.join(RAIZ, "materiais", "aula04-v1.html"))
    assert "../aulas/aula04-v1.html" in material and "../referencias/aula04-v1.html" in material
    assert "../aulas/aula04.html" not in material


def test_tela_de_spec_mapeia_os_cinco_campos_nos_nomes_que_o_banco_aceita():
    html = _ler(SPEC)
    campos = re.findall(r'<label for="[\w-]+">([^<]+) <small>.*?</small></label>\s*<(?:input|textarea)[^>]*name="(\w+)"',
                        html, flags=re.S)
    assert campos == [("Função", "titulo"), ("Entrada", "contexto"), ("Saída", "criterios"),
                      ("Casos de borda", "opcoes"), ("Critério de aceite", "decisao")]
    aceitos = re.search(r"var CAMPOS = \[([^\]]+)\]", _ler(os.path.join(RAIZ, "assets", "js", "inteli-aula02-dados.js")))
    aceitos = re.findall(r"'(\w+)'", aceitos.group(1))
    assert {nome for _, nome in campos} <= set(aceitos)
    assert "Copiar como SPEC.md" in html
    # O script da spec roda antes do componente, para gravar grupo e sessão no formulário.
    assert html.index('src="../assets/js/aula04-spec.js"') < html.index('src="../assets/js/inteli-adr.js"')
    assert "inteli-tela-cheia.js" in html


# ------------------------------------------------------------ navegador

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture
def sala():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        erros = []
        contexto.on("weberror", lambda e: erros.append(str(e.error)))
        try:
            yield contexto, "http://127.0.0.1:%d" % porta, erros
        finally:
            navegador.close()
    httpd.shutdown()


def _professor(contexto, base, slide="specs-t4"):
    page = contexto.new_page()
    page.goto("%s/aulas/aula04.html?quiz-demo=1&quiz-chave=teste#/%s" % (base, slide), wait_until="load")
    page.wait_for_selector("section#%s.present [data-adr-links][data-pronto='sim']" % slide)
    page.wait_for_selector("section#%s .adr-link-url" % slide)
    return page


def _link(professor, slide, grupo):
    return professor.locator("section#%s [data-grupo='%s'] .adr-link-url" % (slide, grupo)).inner_text()


def _grupo(contexto, url):
    page = contexto.new_page()
    page.goto(url, wait_until="load")
    page.wait_for_selector("form[data-adr][data-pronto='sim']")
    return page


def test_links_do_professor_abrem_a_tela_de_spec_do_grupo_e_do_turno(sala):
    contexto, base, erros = sala
    prof = _professor(contexto, base)
    url = _link(prof, "specs-t4", "G02")
    consulta = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert "/aulas/aula04-spec.html?" in url
    assert consulta["g"] == ["G02"] and consulta["turno"] == ["4"] and consulta["t"][0]
    assert consulta["quiz-demo"] == ["1"]
    g = _grupo(contexto, url)
    form = g.locator("form[data-adr]")
    assert form.get_attribute("data-grupo") == "G02"
    assert form.get_attribute("data-sessao") == "%s-t4" % SESSAO
    assert "Spec do turno 4: grupo G02" in g.locator("#spec h2").inner_text()
    # O grupo edita sem informar nome: o autor gravado é o código do grupo.
    assert g.locator("form[data-adr] [name=contexto]").get_attribute("readonly") is None
    assert not g.locator(".adr-quem").is_visible()
    g.fill("form[data-adr] [name=contexto]", "retornos: DataFrame de N pregões")
    g.wait_for_timeout(1200)
    linhas = g.evaluate("IntelIAula02Dados.criar().adrCampos('%s-t4', 'G02')" % SESSAO)
    assert [(l["campo"], l["texto"], l["autor"]) for l in linhas] == [
        ("contexto", "retornos: DataFrame de N pregões", "Grupo G02")]
    assert not erros


def test_copiar_como_spec_md_segue_o_formato_do_kit(sala):
    contexto, base, _ = sala
    g = _grupo(contexto, _link(_professor(contexto, base), "specs-t4", "G01"))
    g.fill("form[data-adr] [name=contexto]", "retornos, n, semente e rf")
    g.fill("form[data-adr] [name=criterios]", "tabela com pesos, retorno, risco e sharpe")
    g.fill("form[data-adr] [name=opcoes]", "n menor que 1 levanta ValueError")
    g.fill("form[data-adr] [name=decisao]", "python conferir.py 4 imprime TURNO 4: OK")
    g.click(".spec-copiar")
    md = g.locator(".spec-saida").input_value()
    assert md == g.evaluate("IntelISpecAula04.markdown()")
    assert md.splitlines()[0] == "## Turno 4"
    # Função em branco: vale a assinatura do turno, como no SPEC.md do kit.
    assert "**Função:** `simular(retornos, n, semente, rf)`" in md
    assert "**Entrada:** retornos, n, semente e rf" in md
    assert "**Saída:** tabela com pesos, retorno, risco e sharpe" in md
    assert "**Casos de borda:** n menor que 1 levanta ValueError" in md
    assert "**Critério de aceite:** python conferir.py 4 imprime TURNO 4: OK" in md
    # Os mesmos cinco rótulos, na mesma ordem, do bloco do turno 4 no SPEC.md do kit.
    kit = _ler(os.path.join(RAIZ, "exemplos", "aula04-simulador", "SPEC.md"))
    bloco = kit.split("## Turno 4", 1)[1].split("\n## ", 1)[0]
    assert re.findall(r"^\*\*(.+?):\*\*", bloco, flags=re.M) == re.findall(r"^\*\*(.+?):\*\*", md, flags=re.M)
    assert "`simular(retornos, n, semente, rf)`" in bloco


def test_spec_do_grupo_aparece_no_projetor_com_os_rotulos_da_spec(sala):
    contexto, base, _ = sala
    prof = _professor(contexto, base)
    g = _grupo(contexto, _link(prof, "specs-t4", "G03"))
    g.fill("form[data-adr] [name=titulo]", "simular(retornos, n, semente, rf)")
    g.fill("form[data-adr] [name=contexto]", "tabela de retornos do G03")
    g.fill("form[data-adr] [name=decisao]", "aceite do G03 ao vivo")
    prof.evaluate("Reveal.slide(Reveal.getSlides().findIndex(s => s.id === 'specs-projetor'))")
    prof.wait_for_selector("section#specs-projetor.present [data-adr-comite][data-pronto='sim']")
    visiveis = prof.locator("section#specs-projetor [data-adr-comite]:not([hidden])")
    assert visiveis.count() == 1 and visiveis.get_attribute("data-grupo") == "G01"
    assert "Spec do grupo G01" in visiveis.locator(".adr-comite-titulo").inner_text()
    assert "Critério de aceite ainda em branco" in visiveis.locator(".adr-comite-decisao").inner_text()
    prof.click("section#specs-projetor [data-spec-abas] button[data-grupo=G03]")
    painel = prof.locator("section#specs-projetor [data-adr-comite]:not([hidden])")
    assert painel.count() == 1
    assert (painel.get_attribute("data-grupo"), painel.get_attribute("data-turno")) == ("G03", "4")
    prof.wait_for_function(
        "document.querySelector('#specs-projetor [data-adr-comite][data-turno=\"4\"][data-grupo=G03] "
        ".adr-comite-decisao').textContent.includes('aceite do G03 ao vivo')", timeout=5000)
    assert "Entrada" in painel.locator("dt").all_inner_texts()
    assert "Contexto" not in painel.locator("dt").all_inner_texts()
    # A spec do turno 5 é outra sessão: o texto do turno 4 não aparece nela.
    prof.click("section#specs-projetor [data-spec-abas] button[data-turno='5']")
    outro = prof.locator("section#specs-projetor [data-adr-comite]:not([hidden])")
    assert (outro.get_attribute("data-grupo"), outro.get_attribute("data-turno")) == ("G03", "5")
    assert "aceite do G03 ao vivo" not in outro.inner_text()


def test_turno_5_usa_outra_sessao_e_outro_link(sala):
    contexto, base, _ = sala
    prof4 = _professor(contexto, base, "specs-t4")
    prof5 = _professor(contexto, base, "specs-t5")
    url4, url5 = _link(prof4, "specs-t4", "G04"), _link(prof5, "specs-t5", "G04")
    assert "turno=4" in url4 and "turno=5" in url5
    g = _grupo(contexto, url5)
    assert g.locator("form[data-adr]").get_attribute("data-sessao") == "%s-t5" % SESSAO
    assert "Spec do turno 5: grupo G04" in g.locator("#spec h2").inner_text()
    g.click(".spec-copiar")
    md = g.locator(".spec-saida").input_value()
    assert md.splitlines()[0] == "## Turno 5" and "posicionar(pesos, retornos, rf)" in md
    # O token do turno 4 não edita a spec do turno 5.
    token4 = urllib.parse.parse_qs(urllib.parse.urlparse(url4).query)["t"][0]
    intruso = _grupo(contexto, "%s/aulas/aula04-spec.html?g=G04&t=%s&turno=5&quiz-demo=1" % (base, token4))
    assert intruso.locator("form[data-adr] [name=contexto]").get_attribute("readonly") is not None


def test_token_errado_abre_a_spec_somente_para_leitura(sala):
    contexto, base, _ = sala
    _professor(contexto, base)
    g = _grupo(contexto, "%s/aulas/aula04-spec.html?g=G01&t=errado&turno=4&quiz-demo=1" % base)
    assert g.locator("form[data-adr] [name=decisao]").get_attribute("readonly") is not None
    assert "sem permissão de edição" in g.locator("form[data-adr] .adr-estado").inner_text()


def test_prazo_encerrado_trava_a_spec(sala):
    contexto, base, _ = sala
    prof = _professor(contexto, base)
    g = _grupo(contexto, _link(prof, "specs-t4", "G02"))
    g.fill("form[data-adr] [name=decisao]", "antes do prazo")
    g.wait_for_timeout(1200)
    prof.eval_on_selector("section#specs-t4 .adr-minutos", "e => { e.value = '0'; }")
    prof.click("section#specs-t4 .adr-iniciar")
    g.wait_for_selector("form[data-adr].adr-travado", timeout=5000)
    assert g.locator("form[data-adr] [name=decisao]").input_value() == "antes do prazo"
    # Travada, a spec ainda pode ser copiada para o SPEC.md.
    g.click(".spec-copiar")
    assert "**Critério de aceite:** antes do prazo" in g.locator(".spec-saida").input_value()


def test_endereco_sem_grupo_mostra_o_aviso_e_nao_monta_o_formulario(sala):
    contexto, base, erros = sala
    page = contexto.new_page()
    page.goto("%s/aulas/aula04-spec.html?quiz-demo=1" % base, wait_until="load")
    page.wait_for_selector("[data-spec-aviso]", state="visible")
    assert not page.locator("form[data-spec]").is_visible()
    assert page.locator("form[data-spec]").get_attribute("data-pronto") is None
    assert not erros


def test_qr_code_do_portal_e_desenhado_ou_cai_para_o_endereco(sala):
    contexto, base, erros = sala
    page = contexto.new_page()
    page.goto("%s/aulas/aula04.html?quiz-demo=1#/portal" % base, wait_until="load")
    page.wait_for_selector("section#portal [data-qr][data-pronto]")
    pronto = page.locator("section#portal [data-qr]").get_attribute("data-pronto")
    if pronto == "sim":
        assert page.locator("section#portal [data-qr] svg path.qr-modulo").count() == 1
    else:  # sem a biblioteca do QR (rede bloqueada), o endereço aparece em texto
        assert pronto == "texto" and PORTAL in page.locator("section#portal [data-qr]").inner_text()
    assert not erros


def test_painel_embutido_so_carrega_quando_o_slide_aparece(sala):
    contexto, base, _ = sala
    page = contexto.new_page()
    page.goto("%s/aulas/aula04.html?quiz-demo=1#/agenda" % base, wait_until="load")
    page.wait_for_function("() => window.Reveal && Reveal.isReady()")
    assert page.locator("section#painel iframe").get_attribute("src") is None
    page.evaluate("Reveal.slide(Reveal.getSlides().findIndex(s => s.id === 'painel'))")
    page.wait_for_function("document.querySelector('section#painel iframe').getAttribute('src') === '../simulador/?painel=1'")
