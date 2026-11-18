"""Trava a Aula 04 em turnos (ADR-018): deck, tela de spec, material, referências e notas.

Estáticos: ordem do deck (daily, portal, painel, preparo, turnos, nuvens, fronteira,
quiz, A3), o que cada slide de atividade responde (o que, onde, como e pronto quando),
os números citados do arquivo de cotações e do JSON da nuvem, a amarração com o A3 e
com o turno 6 e a checagem fora da área visível. Navegador: os documentos do kit
abertos no slide (sobreposição e painel fixo), a ampulheta dos slides de atividade, a
demonstração da fronteira e a tela de spec no modo de memória (?quiz-demo=1), com a
visão de projetor do deck do professor.
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
NUVEM = os.path.join(RAIZ, "assets", "data", "aula04-nuvem.json")
KIT = os.path.join(RAIZ, "exemplos", "aula04-simulador")
ATIVIDADES = ("turno1", "turno2", "passagem", "turno3", "turno4", "turno5")
SESSAO = "m08-aula04-2026-11-18"
PORTAL = "https://josercf.github.io/2026-2B-M08/simulador/"

# Turno: (função, onde roda, quem implementa, comando ou função de conferência)
TURNOS = {
    1: ("retorno_do_dia(pesos, retornos_do_dia)", "Colab", "à mão, sem IA", "conferir_turno1"),
    2: ("metricas(pesos, retornos)", "Colab", "à mão, sem IA", "conferir_turno2"),
    3: ("sortear_pesos(k, rng)", "kit", "ao agente", "python conferir.py 3"),
    4: ("simular(retornos, n, semente, rf)", "kit", "ao agente", "python conferir.py 4"),
    5: ("posicionar(pesos, retornos, rf)", "kit", "ao agente", "python conferir.py 5"),
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


def _visivel(secao):
    """Texto do slide sem as notas do apresentador."""
    return _texto(re.sub(r"<aside class=\"notes[^>]*>.*?</aside>", "", secao, flags=re.S))


def _notas(secao):
    return _texto(" ".join(re.findall(r"<aside class=\"notes[^>]*>(.*?)</aside>", secao, flags=re.S)))


def _parte(secao, classe):
    """Texto do bloco de primeiro nível do slide de atividade com a classe dada."""
    m = re.search(r'<div class="%s[^"]*">(.*?)\n          <div class="at-|<div class="%s[^"]*">(.*?)\n        </div>' % (classe, classe),
                  secao, flags=re.S)
    assert m, classe
    return _texto(m.group(1) or m.group(2))


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
    assert ids == ["capa", "agenda", "daily", "portal", "painel", "preparo", "preparo-sharpe", "anatomia",
                   "adrs-kit", "turno1-codigo", "turno1", "turno2", "passagem", "turno3", "turno4",
                   "specs-projetor", "turno5", "nuvens", "fronteira", "quiz-sorteada", "quiz-conferir",
                   "a3", "referencias", "encerramento"]


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


def test_painel_do_portal_ocupa_o_slide_em_modo_telao_e_a_previsao_e_falada():
    endereco = "../simulador/?painel=1&amp;telao=1"
    for ident in ("painel", "nuvens"):
        secao = _secao(ident)
        assert 'class="content-slide slide-telao"' in _ler(DECK).split('id="%s"' % ident)[0].rsplit("<section", 1)[1]
        assert 'data-src="%s"' % endereco in secao, ident
        assert 'href="%s" target="_blank" rel="noopener"' % endereco in secao, ident
    painel = _secao("painel")
    # Retorno do professor (17/11/2026): a previsão sai da área visível e vira pergunta falada.
    assert "pergunta-previsao" not in painel
    assert "prevê" not in _visivel(painel) and "1.000 carteiras" not in _visivel(painel)
    notas = _notas(painel)
    assert "Prever e observar" in notas and "pesos iguais" in notas and "1.000 carteiras sorteadas" in notas
    nuvens = _visivel(_secao("nuvens"))
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
    # Fechamento com duas perguntas: a demonstração da fronteira ocupa o tempo da terceira.
    assert list(perguntas) == ["preparo", "preparo-sharpe", "quiz-sorteada", "quiz-conferir"]
    assert len({p for p, _ in perguntas.values()}) == 4
    assert perguntas["preparo"][1] == "para os pesos somarem 1"
    assert perguntas["preparo-sharpe"][1] == "0,60"
    assert "melhor entre as sorteadas" in perguntas["quiz-sorteada"][1]
    assert "otimização" in perguntas["quiz-sorteada"][1]
    assert "não é a carteira ótima" in _texto(_secao("quiz-sorteada"))
    assert "Quiz 1 de 2" in _secao("quiz-sorteada") and "Quiz 2 de 2" in _secao("quiz-conferir")
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


def test_anatomia_anuncia_a_atividade_com_tabela_dos_turnos_e_ciclo_em_cinco_verbos():
    anatomia = _secao("anatomia")
    assert re.findall(r"<th>(.*?)</th>", anatomia) == ["Turno", "O que se constrói", "Onde", "Quem implementa"]
    linhas = re.findall(r"<tr><td>(\d)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", anatomia)
    assert [n for n, _, _, _ in linhas] == ["1", "2", "3", "4", "5", "6"]
    funcoes = {n: _texto(f) for n, f, _, _ in linhas}
    for n, nome in (("1", "retorno_do_dia"), ("2", "metricas"), ("3", "sortear_pesos"), ("4", "simular"),
                    ("5", "posicionar"), ("6", "variancia_minima"), ("6", "maximo_sharpe"), ("6", "fronteira")):
        assert nome in funcoes[n], (n, nome)
    onde = {n: o for n, _, o, _ in linhas}
    assert onde["1"] == onde["2"] == "Colab" and all("kit" in onde[n] for n in "3456")
    quem = {n: q for n, _, _, q in linhas}
    assert "à mão" in quem["1"] and "agente" in quem["3"] and "depois do encontro" in quem["6"]
    assert "motor do simulador que acabou de usar no portal" in _visivel(anatomia)
    ciclo = re.findall(r'<li><span class="pn">(\d)</span>([^<]+)</li>', anatomia)
    assert [n for n, _ in ciclo] == ["1", "2", "3", "4", "5"]
    for (_, texto), verbo in zip(ciclo, ("Ler a spec", "Escrever o teste", "Ver falhar", "Implementar", "Ver passar e marcar")):
        assert texto.startswith(verbo), texto
    # Os cinco campos da spec saem do slide e ficam no SPEC.md, aberto pelo botão.
    assert "Casos de borda" not in _visivel(anatomia)
    assert 'data-documento="../exemplos/aula04-simulador/SPEC.md"' in anatomia
    spec = _ler(os.path.join(KIT, "SPEC.md"))
    assert "Cada turno tem cinco campos: Função, Entrada, Saída, Casos de borda e Critério de aceite." in spec


def test_adrs_do_kit_aparecem_como_exemplo_com_o_turno_que_sustentam():
    secao = _secao("adrs-kit")
    texto = _texto(secao)
    assert "exemplo" in texto and "individual" in texto
    linhas = re.findall(r"<tr><td>(ADR-00\d)</td><td>.*?</td><td>(.*?)</td><td>(.*?)</td></tr>", secao)
    assert [(a, s) for a, s, _ in linhas] == [("ADR-001", "turnos 1 e 2"), ("ADR-002", "turno 3"),
                                              ("ADR-003", "turno 6, depois do encontro")]
    for (_, _, celula), nome in zip(linhas, ("ADR-001-janela-dos-dados.md", "ADR-002-sorteio-dos-pesos.md",
                                             "ADR-003-restricoes-da-otimizacao.md")):
        assert 'class="doc-abrir" data-documento="../exemplos/aula04-simulador/docs/adrs/%s"' % nome in celula
    for nome in ("ADR-001-janela-dos-dados.md", "ADR-002-sorteio-dos-pesos.md"):
        assert os.path.isfile(os.path.join(KIT, "docs", "adrs", nome)), nome
    adr1 = _ler(os.path.join(KIT, "docs", "adrs", "ADR-001-janela-dos-dados.md"))
    for trecho in ("13/11/2026", "janela comum", "9 pregões", "252"):
        assert trecho in adr1 and trecho in texto, trecho


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
def test_cada_turno_responde_o_que_onde_como_e_pronto_quando(turno):
    funcao, onde, quem, conferencia = TURNOS[turno]
    secao = _secao("turno%d" % turno)
    assert re.search(r'class="cronometro" id="cronometro-turno%d" data-minutos="\d+" data-ampulheta' % turno, secao)
    assert re.findall(r'<span class="at-rotulo">(.*?)</span>', secao) == ["O que", "Onde", "Como", "Pronto quando"]
    oque = _parte(secao, "at-oque")
    assert funcao in oque and quem in oque
    assert onde in _parte(secao, "at-onde")
    pronto = _parte(secao, "at-pronto")
    assert conferencia in pronto
    assert "imprime" in pronto
    if turno >= 2:
        assert "no portal" in pronto and "marcad" in pronto
    titulo = re.search(r"<h2>(.*?)</h2>", secao).group(1)
    assert "Turno %d" % turno in titulo and len(titulo) <= 40
    # Cada passo aparece em um clique; a extensão fica visível desde o início.
    passos = re.findall(r"<li\b([^>]*)>", secao.split('<ol class="exercise-steps">', 1)[1].split("</ol>", 1)[0])
    assert [p.strip() for p in passos if "passo-extensao" not in p] == ['class="fragment"'] * 4


@pytest.mark.parametrize("ident", ATIVIDADES)
def test_slide_de_atividade_tem_ampulheta_apoio_e_checagem_fora_da_area_visivel(ident):
    secao = _secao(ident)
    assert re.search(r'class="cronometro" id="cronometro-%s" data-minutos="\d+" data-ampulheta' % ident, secao)
    assert "data-ampulheta-espera" in secao
    # Retorno do professor: checagem e debrief são deixa de condução, fora do slide.
    assert "faixa-nota" not in secao
    visivel = _visivel(secao)
    assert "Checagem aos" not in visivel and "Debrief" not in visivel
    notas = re.search(r'<aside class="notes checagem-pratica">(.*?)</aside>', secao, flags=re.S).group(1)
    assert re.search(r"Checagem aos \d+ min:", notas) and "Debrief:" in notas
    # Todo acesso que sai do slide abre em nova aba.
    acessos = re.findall(r'<a class="at-acesso"([^>]*)>', secao)
    for atributos in acessos:
        assert 'target="_blank"' in atributos and 'rel="noopener"' in atributos, atributos
    assert acessos or 'class="doc-abrir"' in secao


def test_cada_turno_abre_o_documento_que_o_sustenta():
    def documentos(ident):
        return re.findall(r'data-documento="\.\./exemplos/aula04-simulador/([^"]+)"', _secao(ident))
    adr1, adr2 = "docs/adrs/ADR-001-janela-dos-dados.md", "docs/adrs/ADR-002-sorteio-dos-pesos.md"
    assert documentos("turno1") == [adr1] and documentos("turno2") == [adr1]
    assert sorted(set(documentos("passagem"))) == ["AGENTS.md", "SPEC.md"]
    assert documentos("turno3") == ["SPEC.md", "AGENTS.md", adr2]
    assert documentos("turno4") == ["SPEC.md", "AGENTS.md"] and documentos("turno5") == ["SPEC.md", "AGENTS.md"]
    for ident in ATIVIDADES + ("anatomia", "adrs-kit"):
        for caminho in documentos(ident):
            if "ADR-003" not in caminho:
                assert os.path.isfile(os.path.join(KIT, caminho)), caminho


def test_ferramentas_do_python_usam_outros_dados_e_nao_entregam_a_solucao():
    def codigo(ident):
        bruto = _secao(ident).split('<pre class="at-codigo"><code>', 1)[1].split("</code></pre>", 1)[0]
        return re.sub(r"<[^>]+>", "", bruto).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    for ident in ("turno1", "turno2"):
        assert "Ferramentas do Python para este turno" in _secao(ident)
    t1 = codigo("turno1")
    for ferramenta in ("zip(", "sum(", "np.dot("):
        assert ferramenta in t1, ferramenta
    t2 = codigo("turno2")
    for ferramenta in (" @ ", ".mean()", ".std(ddof=1)", "** 0.5", "252", "return min(lista), max(lista)"):
        assert ferramenta in t2, ferramenta
    t3 = codigo("turno3")
    for ferramenta in ("assert abs(sum(", "assert all(", "default_rng(7)", "assert list(a) == list(b)"):
        assert ferramenta in t3, ferramenta
    assert "Proibição" in _secao("turno3") and "conferir.py" in _parte(_secao("turno3"), "at-apoio")
    # Os exemplos usam outros dados: nenhuma variável da tarefa aparece neles.
    for ident in ("turno1", "turno2", "turno3", "turno4", "turno5"):
        for nome in ("pesos", "retornos", "sortear_pesos", "simular(", "posicionar", "retorno_do_dia", "metricas"):
            assert nome not in codigo(ident), (ident, nome)
    # Cada bloco roda como está escrito e dá o resultado do comentário.
    import numpy as np
    import pandas as pd
    for ident in ("turno1", "turno2", "turno3", "turno4", "turno5"):
        exec(compile(codigo(ident), ident, "exec"), {"np": np, "pd": pd})
    ambiente = {"np": np, "pd": pd}
    exec(codigo("turno1"), ambiente)
    assert sum(q * p for q, p in zip(ambiente["qtd"], ambiente["preco"])) == 17.0 == np.dot(ambiente["qtd"], ambiente["preco"])
    exec(codigo("turno2"), ambiente)
    assert list(ambiente["m"]) == [7.0, 6.0, 5.0] and ambiente["m"].mean() == 6.0 and ambiente["m"].std(ddof=1) == 1.0
    assert (ambiente["menor"], ambiente["maior"]) == (2, 9)


def test_turnos_a_mao_ficam_no_colab_e_os_demais_no_kit_com_agente():
    colab = 'href="https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula04.ipynb" target="_blank"'
    for turno in (1, 2):
        secao = _secao("turno%d" % turno)
        assert "sem IA" in _texto(secao) and "agente" not in _texto(secao), turno
        assert colab in secao, turno
    for turno in (3, 4, 5):
        texto = _texto(_secao("turno%d" % turno))
        assert "agente" in texto and "Colab" not in texto, turno
    # A spec do grupo abre pelo portal, na tela Progresso, sem link distribuído.
    for turno in (4, 5):
        secao = _secao("turno%d" % turno)
        assert 'href="../simulador/#progresso" target="_blank"' in secao
        # O nome do botão é o da tela Progresso do portal.
        assert "Portal: Progresso, botão Abrir a spec do grupo" in _texto(secao)
        assert "no turno %d, cliquem em Abrir a spec do grupo" % turno in _texto(secao)
        assert ">Abrir a spec do grupo</a>" in _ler(os.path.join(RAIZ, "simulador", "index.html"))
        assert "Slack" not in _texto(secao) and "link" not in _visivel(secao)
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
        assert os.path.isfile(os.path.join(KIT, arquivo)), arquivo
    # Instruções linha a linha, com os comandos em blocos copiáveis.
    lista = secao.split('<ol class="exercise-steps">', 1)[1].split("</ol>", 1)[0]
    assert lista.count('<li class="fragment">') == 4
    assert re.findall(r'<button type="button" class="copiar" data-copiar="([^"]+)"', lista) == [
        "python checar_ambiente.py", "python conferir.py 1", "python conferir.py 2",
        "Leia o SPEC.md e o AGENTS.md e diga o que o turno 3 pede, sem escrever código."]
    # A coluna da direita mostra o SPEC.md e o AGENTS.md abertos, em duas abas.
    painel = secao.split('data-documento-abas', 1)[1].split('<div class="doc-fixo-corpo">', 1)[0]
    assert re.findall(r'<button type="button" data-documento="[^"]+/(\w+\.md)"', painel) == ["SPEC.md", "AGENTS.md"]


def test_deck_do_professor_projeta_as_specs_sem_distribuir_link():
    deck = _sem_comentario(_ler(DECK))
    # Retorno do professor: nenhum link de spec é distribuído por slide.
    assert "data-adr-links" not in deck and "aula04-spec.html" not in deck and "?t=" not in deck
    ids = [i for i, _ in _secoes()]
    assert not [i for i in ids if i.startswith("specs-t") or "links" in i]
    projetor = _secao("specs-projetor")
    paineis = re.findall(r'data-adr-comite data-sessao="%s-t(\d)" data-grupo="(G0\d)" data-turno="(\d)" data-selos' % SESSAO,
                         projetor)
    assert sorted(paineis) == sorted((str(t), "G0%d" % g, str(t)) for t in (4, 5) for g in range(1, 5))
    rotulos = json.loads(re.search(r"data-rotulos='([^']+)'", projetor).group(1))
    assert rotulos == {"contexto": "Entrada", "criterios": "Saída", "opcoes": "Casos de borda"}


def test_amarracao_cita_o_a3_com_peso_e_prazo_da_fonte_e_o_turno_6_como_base_do_a4():
    secao = _secao("a3")
    a3 = _texto(secao)
    plano = _aula("04")
    assert "A3 Motor de Simulação de Monte Carlo, peso 3" in a3
    assert "A3 Motor de Simulação de Monte Carlo (peso 3)" in plano
    for data in ("19/11/2026", "20/11/2026, 23h59"):
        assert data in a3 and data in plano, data
    assert "decisão sua" in a3 and "exemplo" in a3
    pesos = [int(p) for p in re.findall(r"<td>(\d+)%</td>", secao)]
    assert pesos == [30, 10, 10, 15, 15, 20] and sum(pesos) == 100
    # Turno 6, depois do encontro: base do A4, sem prazo, porque o planejamento não traz a data de entrega.
    visivel = _visivel(secao)
    assert "Depois do encontro" in visivel
    assert "O turno 6 do kit é a base do A4, Otimizador de Carteira com Fronteira Eficiente" in visivel
    assert "A4 Otimizador de Carteira com Fronteira Eficiente (peso 3)" in plano
    assert "fronteira sobreposta à nuvem" in visivel
    assert len(re.findall(r"\d\d/\d\d/\d{4}", visivel)) == 3  # só as datas do A3 (título, review e entrega)
    for nome in ("variancia_minima(retornos)", "maximo_sharpe(retornos, rf)", "fronteira(retornos, pontos=50)",
                 "python conferir.py 6", "TURNO 6: OK"):
        assert nome in _notas(secao), nome
    assert re.findall(r'data-documento="\.\./exemplos/aula04-simulador/([^"]+)"', secao) == [
        "SPEC.md", "docs/adrs/ADR-003-restricoes-da-otimizacao.md"]


def test_fronteira_e_demonstrada_no_bloco_7_com_os_numeros_do_json():
    secao = _secao("fronteira")
    assert ('<div class="widget" data-widget="aula04-nuvem" data-fonte="../assets/data/aula04-nuvem.json"'
            in secao)
    dados = json.loads(_ler(NUVEM))
    melhor = ("%.2f" % max(dados["sharpe"])).replace(".", ",")
    otima = ("%.2f" % dados["maximo_sharpe"]["sharpe"]).replace(".", ",")
    assert (melhor, otima) == ("0,41", "0,92")
    titulo = re.search(r"<h2>(.*?)</h2>", secao).group(1)
    assert melhor in titulo and otima in titulo
    assert len(dados["sharpe"]) == 10000 and dados["passos"] == [10, 100, 1000, 10000]
    visivel = _visivel(secao)
    janela = dados["janela"]
    assert "%s retornos de %s a %s" % (_milhar(janela["retornos"]), janela["inicio"], janela["fim"]) in visivel
    assert "15 ativos do acervo" in visivel and "sem os ativos dos grupos" in visivel
    # Nenhuma sorteada passa da fronteira (a medida está travada em tools/tests/test_aula04.py).
    assert "Nenhuma das 10.000 sorteadas passa da fronteira" in visivel
    assert "sem sortear" in visivel
    assert max(dados["sharpe"]) < dados["maximo_sharpe"]["sharpe"]
    notas = _notas(secao)
    for passo in ("6 a 8 minutos", "10, 100, 1.000 e 10.000", "Ótimas e fronteira", "turno 6"):
        assert passo in notas, passo
    for n, leitura in dados["leituras"].items():
        assert re.search(r"sorteadas: (-?\d,\d\d)", leitura).group(1) in notas, n
    # O material e as notas do professor citam os mesmos dois números.
    depois = _texto(_ler(MATERIAL).split('id="depois"', 1)[1].split("</section>", 1)[0])
    assert "Índice de Sharpe %s" % melhor in depois and "chega a %s" % otima in depois
    assert "python conferir.py 6" in depois and "TURNO 6: OK" in depois
    demonstracao = _ler(NOTAS).split("**Demonstração da fronteira", 1)[1].split("\n\n", 1)[0]
    assert melhor in demonstracao and otima in demonstracao and "1.423 retornos" in demonstracao


def test_otimizacao_e_demonstrada_e_a_implementacao_fica_para_o_turno_6():
    visivel = " ".join(_visivel(s) for _, s in _secoes())
    # O encontro demonstra a fronteira e não ensina o otimizador: SLSQP e scipy só nas notas.
    for termo in ("SLSQP", "scipy", "otimizar("):
        assert termo not in visivel, termo
    assert "scipy.optimize.minimize" in _notas(_secao("a3"))
    assert "depois do encontro" in _visivel(_secao("anatomia"))


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
                   "inteli-aula02-dados.js", "aula04-turnos.js", "aula04-documento.js", "inteli-widgets.js",
                   "widgets/aula04-nuvem.js", "inteli-tela-cheia.js", "inteli-print.js"):
        assert "../assets/js/%s" % script in deck, script
    for folha in ("aula04-turnos.css", "aula04-atividade.css"):
        assert "../assets/css/%s" % folha in deck, folha


# ------------------------------------------------- material, referências, notas

def test_artefatos_novos_sem_travessao_e_sem_emoji():
    for caminho in (DECK, SPEC, MATERIAL, REFERENCIAS, NOTAS,
                    os.path.join(RAIZ, "assets", "js", "aula04-turnos.js"),
                    os.path.join(RAIZ, "assets", "js", "aula04-spec.js"),
                    os.path.join(RAIZ, "assets", "js", "aula04-documento.js"),
                    os.path.join(RAIZ, "assets", "css", "aula04-atividade.css"),
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
        for termo in ("Obrigatório", "Checagem aos", "Debrief", "Erros comuns", "Contingência"):
            assert termo in bloco, (turno, termo)
        # O número do slide citado nas notas é o do deck.
        slide = int(re.match(r"slide (\d+)", bloco).group(1))
        assert [i for i, _ in _secoes()][slide - 1] == "turno%d" % turno
    assert "**Turno 6 (depois do encontro)" in notas and "python conferir.py 6" in notas
    assert "Demonstração da fronteira" in notas
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


def _deck(contexto, base, slide):
    page = contexto.new_page()
    page.goto("%s/aulas/aula04.html?quiz-demo=1&quiz-chave=teste#/%s" % (base, slide), wait_until="load")
    page.wait_for_function("() => window.Reveal && Reveal.isReady()")
    page.wait_for_selector("section#%s.present" % slide)
    return page


def _ir(page, slide):
    page.evaluate("id => Reveal.slide(Reveal.getSlides().findIndex(s => s.id === id))", slide)
    page.wait_for_selector("section#%s.present" % slide)


def _abrir(page, slide, indice=0):
    botao = page.locator("section#%s .doc-abrir" % slide).nth(indice)
    botao.click()
    page.wait_for_selector(".doc-popup:not([hidden]) .doc-popup-corpo:not([data-estado=carregando])")
    return botao


def _plano(markdown):
    """Texto de um trecho de Markdown como aparece na tela: sem crase, sem asterisco, em uma linha."""
    return re.sub(r"\s+", " ", markdown.replace("`", "").replace("**", "")).strip()


def test_spec_do_grupo_aparece_no_projetor_com_os_rotulos_da_spec(sala):
    contexto, base, _ = sala
    prof = _deck(contexto, base, "agenda")
    # O grupo escreve pela tela de spec, aberta no portal (tools/tests/test_spec_aula04.py). Aqui
    # o texto entra direto no banco em memória, e o teste cobre só a visão do projetor.
    prof.evaluate("""async sessao => {
        const dados = IntelIAula02Dados.criar();
        const token = (await dados.adrLinks('teste', sessao)).find(l => l.grupo === 'G03').token;
        await dados.adrSalvar(sessao, 'G03', token, 'titulo', 'simular(retornos, n, semente, rf)', 'JR');
        await dados.adrSalvar(sessao, 'G03', token, 'contexto', 'tabela de retornos do G03', 'JR');
        await dados.adrSalvar(sessao, 'G03', token, 'decisao', 'aceite do G03 ao vivo', 'JR');
    }""", "%s-t4" % SESSAO)
    _ir(prof, "specs-projetor")
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
    rotulos = [t.split("(")[0].strip() for t in painel.locator("dt").all_inner_texts()]
    assert "Entrada" in rotulos and "Contexto" not in rotulos
    # Selo de quem está editando (data-selos): iniciais e há quanto tempo, em cada campo escrito.
    selos = painel.locator(".adr-comite-selo")
    assert selos.count() == 3
    assert re.fullmatch(r"\(JR, (agora|há \d+ s)\)", selos.first.inner_text().strip())
    assert selos.first.get_attribute("data-vivo") in ("sim", "nao")
    assert painel.locator("dt .adr-comite-selo").evaluate("e => getComputedStyle(e).fontSize") >= "16px"
    recente = prof.evaluate("""() => { const s = document.querySelector('#specs-projetor [data-grupo=G03][data-turno="4"] .adr-comite-selo');
        const antes = s.dataset.vivo; s.dataset.vivo = 'sim'; const vivo = getComputedStyle(s).backgroundColor;
        s.dataset.vivo = 'nao'; const parado = getComputedStyle(s).backgroundColor; s.dataset.vivo = antes; return vivo !== parado; }""")
    assert recente   # edição recente tem destaque próprio
    # Painel sem texto não ganha selo.
    assert prof.locator("section#specs-projetor [data-grupo=G01][data-turno='4'] .adr-comite-selo").count() == 0
    # Link da visão somente leitura do grupo em projeção, sem token.
    ver = prof.locator("section#specs-projetor [data-spec-ver]")
    assert ver.get_attribute("href") == "aula04-spec.html?g=G03&turno=4&ver=1&quiz-demo=1"
    assert ver.get_attribute("target") == "_blank"
    # A spec do turno 5 é outra sessão: o texto do turno 4 não aparece nela.
    prof.click("section#specs-projetor [data-spec-abas] button[data-turno='5']")
    outro = prof.locator("section#specs-projetor [data-adr-comite]:not([hidden])")
    assert (outro.get_attribute("data-grupo"), outro.get_attribute("data-turno")) == ("G03", "5")
    assert ver.get_attribute("href") == "aula04-spec.html?g=G03&turno=5&ver=1&quiz-demo=1"
    assert "aceite do G03 ao vivo" not in outro.inner_text()


def test_adr_001_abre_em_sobreposicao_com_o_conteudo_real_e_fecha_por_esc_clique_fora_e_botao(sala):
    contexto, base, erros = sala
    page = _deck(contexto, base, "turno1")
    assert page.locator(".doc-popup:not([hidden])").count() == 0
    botao = _abrir(page, "turno1")
    popup = page.locator(".doc-popup")
    corpo = page.locator(".doc-popup-corpo")
    assert corpo.get_attribute("data-estado") == "pronto"
    assert page.locator(".doc-popup-janela").get_attribute("role") == "dialog"
    assert page.locator(".doc-popup-nome").inner_text() == "docs/adrs/ADR-001-janela-dos-dados.md"
    # O conteúdo é o do arquivo do kit, convertido do Markdown.
    fonte = _ler(os.path.join(KIT, "docs", "adrs", "ADR-001-janela-dos-dados.md"))
    assert corpo.locator("h1").inner_text() == fonte.splitlines()[0].lstrip("# ")
    assert corpo.locator("h2").all_inner_texts() == re.findall(r"^## (.+)$", fonte, flags=re.M)
    texto = re.sub(r"\s+", " ", corpo.inner_text())
    decisao = _plano(fonte.split("## Decisão", 1)[1].split("## ", 1)[0])
    assert decisao.startswith("As cotações de dados/precos.csv vão de 02/01/2024 a 13/11/2026") and decisao in texto
    assert corpo.locator("ul li").count() == len(re.findall(r"^- ", fonte, flags=re.M))
    assert corpo.locator("li strong").first.inner_text() == "Data:"
    assert corpo.locator("code").first.inner_text() == "dados/precos.csv"
    assert corpo.locator("blockquote").count() == 1
    assert "**" not in texto and "##" not in texto
    # Rolagem interna: o arquivo é mais alto que a janela e rola dentro dela.
    assert corpo.evaluate("e => e.scrollHeight > e.clientHeight && getComputedStyle(e).overflowY === 'auto'")
    assert page.evaluate("document.documentElement.scrollHeight <= window.innerHeight")

    # Com o documento aberto, nenhuma tecla navega o deck.
    antes = page.evaluate("JSON.stringify(Reveal.getIndices())")
    for tecla in ("ArrowRight", "Space", "PageDown", "ArrowDown", "n", "End"):
        page.keyboard.press(tecla)
    assert page.evaluate("JSON.stringify(Reveal.getIndices())") == antes
    assert popup.is_visible()
    assert corpo.evaluate("e => e.scrollTop") > 0   # as teclas de rolagem rolam o documento

    # Esc fecha e devolve o foco ao botão que abriu.
    page.keyboard.press("Escape")
    assert not popup.is_visible()
    assert botao.evaluate("e => e === document.activeElement")
    assert page.evaluate("JSON.stringify(Reveal.getIndices())") == antes
    # Clique fora da janela fecha; clique dentro dela, não.
    _abrir(page, "turno1")
    corpo.click(position={"x": 40, "y": 40})
    assert popup.is_visible()
    page.mouse.click(6, 360)
    assert not popup.is_visible()
    assert botao.evaluate("e => e === document.activeElement")
    # O botão Fechar fecha.
    _abrir(page, "turno1")
    page.click(".doc-popup-fechar")
    assert not popup.is_visible()
    # Fechado, o teclado volta a ser do deck.
    page.locator("body").press("ArrowRight")
    assert page.evaluate("JSON.stringify(Reveal.getIndices())") != antes
    assert not erros


def test_spec_md_abre_no_bloco_do_turno_e_agents_md_mantem_a_lista_numerada(sala):
    contexto, base, erros = sala
    page = _deck(contexto, base, "turno3")
    _abrir(page, "turno3", 0)
    corpo = page.locator(".doc-popup-corpo")
    assert page.locator(".doc-popup-nome").inner_text() == "SPEC.md"
    spec = _ler(os.path.join(KIT, "SPEC.md"))
    assert corpo.locator("h1").inner_text() == spec.splitlines()[0].lstrip("# ")
    assert corpo.locator("h2").all_inner_texts() == re.findall(r"^## (.+)$", spec, flags=re.M)
    texto = re.sub(r"\s+", " ", corpo.inner_text())
    assert "Cada turno tem cinco campos: Função, Entrada, Saída, Casos de borda e Critério de aceite." in texto
    assert "Função: sortear_pesos(k, rng)" in texto
    # data-secao="Turno 3": a janela abre rolada até o bloco do turno.
    topo = corpo.evaluate("""e => { const h = [...e.querySelectorAll('h2')].find(x => x.textContent.startsWith('Turno 3'));
        return h.getBoundingClientRect().top - e.getBoundingClientRect().top; }""")
    assert 0 <= topo < 60 and corpo.evaluate("e => e.scrollTop") > 0
    page.keyboard.press("Escape")

    _abrir(page, "turno3", 1)
    assert page.locator(".doc-popup-nome").inner_text() == "AGENTS.md"
    agents = _ler(os.path.join(KIT, "AGENTS.md"))
    assert corpo.locator("ol > li").count() == len(re.findall(r"^\d+\. ", agents, flags=re.M))
    assert corpo.locator("ul > li").count() == len(re.findall(r"^- ", agents, flags=re.M))
    assert "Nunca edite conferir.py. Ele é o teste de aceite do professor." in re.sub(r"\s+", " ", corpo.inner_text())
    assert not erros


def test_falha_do_fetch_mostra_mensagem_e_link_para_o_arquivo(sala):
    contexto, base, _ = sala
    contexto.route("**/ADR-002-sorteio-dos-pesos.md", lambda rota: rota.abort())
    page = _deck(contexto, base, "turno3")
    _abrir(page, "turno3", 2)
    corpo = page.locator(".doc-popup-corpo")
    assert corpo.get_attribute("data-estado") == "erro"
    assert "ADR-002-sorteio-dos-pesos.md não carregou" in corpo.inner_text()
    link = corpo.locator("a")
    assert link.get_attribute("href") == "../exemplos/aula04-simulador/docs/adrs/ADR-002-sorteio-dos-pesos.md"
    assert link.get_attribute("target") == "_blank"
    page.keyboard.press("Escape")
    assert not page.locator(".doc-popup").is_visible()


def test_conversor_de_markdown_cobre_tabela_bloco_de_codigo_e_lista_com_continuacao(sala):
    contexto, base, _ = sala
    page = _deck(contexto, base, "agenda")
    fonte = "\n".join([
        "# Título", "", "Parágrafo em", "duas linhas com **negrito** e `a < b`.", "",
        "- item um", "  continua aqui", "- item dois", "",
        "1. primeiro", "2. segundo", "",
        "| Para | Use |", "|---|---|", "| média | `np.mean` |", "",
        "```", "x = 1 < 2", "**cru**", "```", "", "> citação", ""])
    html = page.evaluate("fonte => Aula04Documento.markdown(fonte)", fonte)
    assert "<h1>Título</h1>" in html
    assert "<p>Parágrafo em duas linhas com <strong>negrito</strong> e <code>a &lt; b</code>.</p>" in html
    assert "<ul><li>item um continua aqui</li><li>item dois</li></ul>" in html
    assert "<ol><li>primeiro</li><li>segundo</li></ol>" in html
    assert "<table><thead><tr><th>Para</th><th>Use</th></tr></thead><tbody><tr><td>média</td><td><code>np.mean</code></td></tr></tbody></table>" in html
    assert "<pre><code>x = 1 &lt; 2\n**cru**</code></pre>" in html
    assert "<blockquote><p>citação</p></blockquote>" in html
    # Marcação do arquivo nunca vira elemento da página.
    assert "<script>" not in page.evaluate("Aula04Documento.markdown('<script>alert(1)</script>')")


def test_passagem_revela_linha_a_linha_e_mostra_spec_e_agents_em_abas(sala):
    contexto, base, erros = sala
    contexto.grant_permissions(["clipboard-read", "clipboard-write"])
    page = _deck(contexto, base, "passagem")
    passos = page.locator("section#passagem .exercise-steps li.fragment")
    assert passos.count() == 4 and page.locator("section#passagem li.fragment.visible").count() == 0
    for n in range(1, 5):
        page.keyboard.press("ArrowRight")
        page.wait_for_function("n => document.querySelectorAll('section#passagem li.fragment.visible').length === n", arg=n)
        assert page.locator("section#passagem.present").count() == 1
    page.wait_for_function("getComputedStyle(document.querySelectorAll('section#passagem li.fragment')[3]).visibility === 'visible'")
    # Comando em bloco copiável.
    botao = page.locator("section#passagem button.copiar").nth(1)
    botao.click()
    page.wait_for_function("document.querySelectorAll('section#passagem button.copiar')[1].dataset.copiado === 'sim'")
    assert page.evaluate("navigator.clipboard.readText()") == "python conferir.py 1"

    # Painel fixo: o SPEC.md aberto, e o AGENTS.md na segunda aba.
    page.wait_for_selector("section#passagem .doc-fixo[data-pronto='sim']")
    corpo = page.locator("section#passagem .doc-fixo-corpo")
    abas = page.locator("section#passagem .doc-fixo-barra button[data-nome]:not(.doc-abrir)")
    assert abas.all_inner_texts() == ["SPEC.md", "AGENTS.md"]
    assert abas.nth(0).get_attribute("aria-pressed") == "true"
    assert corpo.locator("h1").inner_text() == "Especificação do simulador de carteiras"
    assert corpo.evaluate("e => e.scrollHeight > e.clientHeight && getComputedStyle(e).overflowY === 'auto'")
    abas.nth(1).click()
    page.wait_for_function("(document.querySelector('section#passagem .doc-fixo-corpo h1') || {textContent: ''}).textContent.includes('agente')")
    assert corpo.locator("h1").inner_text() == "Instruções para o agente de codificação"
    assert abas.nth(1).get_attribute("aria-pressed") == "true" and abas.nth(0).get_attribute("aria-pressed") == "false"
    # Ampliar abre na sobreposição o arquivo da aba em uso.
    page.click("section#passagem .doc-fixo-ampliar")
    page.wait_for_selector(".doc-popup:not([hidden]) .doc-popup-corpo[data-estado=pronto]")
    assert page.locator(".doc-popup-nome").inner_text() == "AGENTS.md"
    assert not erros


def _caixa(page, seletor):
    return page.locator(seletor).first.bounding_box()


def _cruzam(a, b):
    return not (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
                or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])


@pytest.mark.parametrize("ident", ATIVIDADES)
def test_ampulheta_nasce_no_play_sem_cobrir_o_conteudo_do_slide(sala, ident):
    contexto, base, erros = sala
    page = _deck(contexto, base, ident)
    raiz = "section#%s " % ident
    # As notas, com a checagem e o debrief, não aparecem no slide.
    assert not page.locator(raiz + "aside.notes.checagem-pratica").is_visible()
    assert page.locator(raiz + ".faixa-nota").count() == 0
    espera = _caixa(page, raiz + "[data-ampulheta-espera]")
    assert page.locator(raiz + ".ampulheta").count() == 0
    conteudo = {s: _caixa(page, raiz + s) for s in (".at-oque", ".at-onde", ".at-como", ".at-pronto",
                                                    ".at-apoio, " + raiz + ".doc-fixo")}
    page.evaluate("() => { while (Reveal.availableFragments().next) Reveal.nextFragment(); }")
    page.click(raiz + ".cronometro-play")
    page.wait_for_selector(raiz + ".ampulheta.ampulheta-visivel")
    assert page.locator(raiz.strip() + ".com-ampulheta").count() == 1
    page.wait_for_timeout(300)
    ampulheta = _caixa(page, raiz + ".ampulheta")
    # A ampulheta do cronômetro ocupa o lugar da ampulheta em espera, e o layout não muda.
    for lado in ("x", "y", "width"):
        assert abs(ampulheta[lado] - espera[lado]) <= 3, (lado, ampulheta, espera)
    assert page.locator(raiz + "[data-ampulheta-espera]").evaluate("e => getComputedStyle(e).visibility") == "hidden"
    for seletor, antes in conteudo.items():
        depois = _caixa(page, raiz + seletor)
        assert depois == antes, seletor
        assert not _cruzam(ampulheta, depois), seletor
    assert ampulheta["y"] + ampulheta["height"] <= 648 and ampulheta["x"] + ampulheta["width"] <= 1224
    # Nada da lista de passos sai da coluna dela (medido com todos os passos revelados).
    sobra = page.evaluate("""raiz => { const c = document.querySelector(raiz + '.at-como');
        const l = c.querySelector('ol'); return c.getBoundingClientRect().bottom - l.getBoundingClientRect().bottom; }""", raiz)
    assert sobra >= 0, sobra
    assert not erros


def test_acessos_dos_turnos_abrem_em_nova_aba(sala):
    contexto, base, _ = sala
    page = _deck(contexto, base, "turno1")
    alvos = page.evaluate("[...document.querySelectorAll('section[data-atividade] a')].map(a => a.target + '|' + a.rel)")
    assert alvos and set(alvos) == {"_blank|noopener"}
    with contexto.expect_page() as nova:
        page.click("section#turno1 a.at-acesso:has-text('Portal')")
    assert nova.value.url.split("?")[0].split("#")[0].endswith("/simulador/")
    assert page.locator("section#turno1.present").count() == 1
    _ir(page, "turno4")
    assert page.locator("section#turno4 a.at-acesso").get_attribute("href") == "../simulador/#progresso"
    # Nenhum link de spec é distribuído pelo deck.
    assert page.locator("[data-adr-links], a[href*='aula04-spec']:not([href*='ver=1']), a[href*='t=']").count() == 0


def test_demonstracao_da_fronteira_monta_o_widget_e_liga_as_otimas(sala):
    contexto, base, erros = sala
    page = _deck(contexto, base, "fronteira")
    page.wait_for_selector("section#fronteira .widget[data-pronto='sim']")
    botoes = page.locator("section#fronteira .widget button")
    assert botoes.all_inner_texts() == ["10 sorteios", "100 sorteios", "1.000 sorteios", "10.000 sorteios",
                                        "Ótimas e fronteira"]
    dados = json.loads(_ler(NUVEM))
    widget = page.locator("section#fronteira .widget")
    for indice, passo in enumerate(dados["passos"]):
        botoes.nth(indice).click()
        page.wait_for_function("t => document.querySelector('section#fronteira .widget').innerText.includes(t)",
                               arg=dados["leituras"][str(passo)])
    botoes.nth(4).click()
    page.wait_for_function("t => document.querySelector('section#fronteira .widget').innerText.includes(t)",
                           arg=dados["leitura_otimas"])
    # Com as duas leituras na tela, o widget e a faixa continuam dentro da área útil.
    faixa = _caixa(page, "section#fronteira .faixa-nota")
    assert faixa["y"] + faixa["height"] <= 650
    caixa = widget.bounding_box()
    assert caixa["y"] + caixa["height"] <= faixa["y"] + 1
    assert not erros


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


def test_painel_embutido_so_carrega_quando_o_slide_aparece_e_ocupa_a_area_util(sala):
    contexto, base, _ = sala
    page = contexto.new_page()
    page.goto("%s/aulas/aula04.html?quiz-demo=1#/agenda" % base, wait_until="load")
    page.wait_for_function("() => window.Reveal && Reveal.isReady()")
    assert page.locator("section#painel iframe").get_attribute("src") is None
    page.evaluate("Reveal.slide(Reveal.getSlides().findIndex(s => s.id === 'painel'))")
    page.wait_for_function(
        "document.querySelector('section#painel iframe').getAttribute('src') === '../simulador/?painel=1&telao=1'")
    # Retorno do professor: o painel ocupa a área útil inteira, da linha do título ao rodapé.
    caixa = page.locator("section#painel iframe").bounding_box()
    assert caixa["width"] >= 1160 and caixa["height"] >= 500
    assert caixa["y"] + caixa["height"] <= 650
    assert page.locator("section#painel .pergunta-previsao").count() == 0
    assert not page.locator("section#painel aside.notes").is_visible()
