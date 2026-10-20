"""Trava a abertura da Aula 01 revisada em 20/10/2026 e a agenda das seis aulas.

O professor pediu, em 20/10/2026: foto com a família e formação completa no
perfil; combinados animados; agenda só com bloco e tema, sem minutos, sem a
interação de fechamento e sem a nota de horário de relógio, em todas as aulas;
e a esteira dos artefatos com um slide comum e um slide por artefato. Os pesos
de cada artefato vêm do PLANO_DE_ENSINO.md (Adalove) e os critérios próprios
somam 65%, a parte da ferramenta no barema de todo artefato.
"""
import os
import re

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula01.html")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _secoes(caminho=DECK):
    return re.findall(r"<section\b(.*?)</section>", _ler(caminho), flags=re.S)


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace("&middot;", "·")


def _secao(id_):
    return next(s for s in _secoes() if 'id="%s"' % id_ in s)


# --- perfil do professor ---------------------------------------------------

def test_perfil_tem_a_foto_com_a_familia():
    perfil = _secao("professor")
    assert 'src="../assets/img/professor-familia.jpg"' in perfil
    assert os.path.getsize(os.path.join(RAIZ, "assets", "img", "professor-familia.jpg")) < 400_000
    assert re.search(r'<img src="../assets/img/professor-familia.jpg" alt="[^"]{20,}"', perfil)


def test_perfil_traz_a_formacao_e_a_docencia_informadas_pelo_professor():
    texto = _texto(_secao("professor"))
    for trecho in ("Doutorando em Administração, Uninove", "Mestrado em Gestão de Projetos, Uninove",
                   "MBA em Digital Transformation, MIT", "Pós-graduação em Governança de TI, Uninove",
                   "Análise de Sistemas, Uninove", "FIAP", "Uninove e no Mackenzie",
                   "Professor orientador e instrutor de Computação", "Inteli Exec",
                   "adoção de IA nas organizações", "Pós e no MBA"):
        assert trecho in texto, trecho


# --- combinados ------------------------------------------------------------

def test_combinados_viram_linha_do_tempo_animada_com_os_mesmos_prazos():
    combinados = _secao("combinados")
    assert '<ol class="semana">' in combinados
    assert combinados.count('class="semana-marco"') == 3
    texto = _texto(combinados)
    for trecho in ("Participação", "Autoestudo em sala", "Autoestudo para casa", "Artefato da sprint",
                   "IA liberada", "20% de cada artefato"):
        assert trecho in texto, trecho


# --- agenda, nas seis aulas ------------------------------------------------

@pytest.mark.parametrize("n", range(1, 7))
def test_agenda_mostra_bloco_e_tema_sem_minutos_nem_nota_de_horario(n):
    deck = os.path.join(RAIZ, "aulas", "aula%02d.html" % n)
    agenda = next(s for s in _secoes(deck) if 'id="agenda"' in s)
    assert "<tr><th>Bloco</th><th>Tema</th></tr>" in agenda
    assert re.findall(r"<tr><td>([^<]+)</td><td>", agenda) == ["Daily", "1", "2", "3", "4", "5", "6", "7"]
    for removido in ("Minutos", "Intervalo (min)", "Interação que fecha", "Horários de relógio"):
        assert removido not in agenda, removido


# --- esteira e slides por artefato -----------------------------------------

def _pesos_do_plano():
    plano = _ler(os.path.join(RAIZ, "PLANO_DE_ENSINO.md"))
    return {a: (sprint, int(peso)) for a, sprint, peso in
            re.findall(r"^\| (A\d) \| ([^|]+?) \| [^|]+ \| (\d) \|", plano, re.M)}


def test_esteira_vem_logo_depois_do_parceiro_e_abre_um_slide_por_artefato():
    ids = [re.search(r'id="([^"]+)"', s).group(1) if 'id="' in s else None for s in _secoes()]
    i = ids.index("parceiro")
    assert ids[i + 1:i + 9] == ["entregas", "entregas-comum", "framework", "artefato-a1", "artefato-a2",
                                "artefato-a3", "artefato-a4", "artefato-a5"]
    assert ids[i + 9] == "preparo"


def test_estacoes_da_esteira_citam_sprint_e_peso_do_plano():
    esteira = _texto(_secao("entregas"))
    for artefato, (sprint, peso) in _pesos_do_plano().items():
        rotulo = ("Sprints %s" if " e " in sprint else "Sprint %s") % sprint
        assert "%s · peso %d" % (rotulo, peso) in esteira, artefato
    assert esteira.count("review") == 5


@pytest.mark.parametrize("artefato", ["A1", "A2", "A3", "A4", "A5"])
def test_slide_do_artefato_tem_criterios_que_somam_65_e_o_peso_do_plano(artefato):
    secao = _secao("artefato-%s" % artefato.lower())
    criterios = re.search(r'<table class="tabela-leitura tabela-criterios.*?</table>', secao, re.S).group(0)
    pesos = [int(p) for p in re.findall(r"<td>(\d+)%</td>", criterios)]
    assert sum(pesos[:-1]) == 65 and pesos[-1] == 35
    sprint, peso = _pesos_do_plano()[artefato]
    assert "peso %d." % peso in _texto(secao)
    atual = re.findall(r'<li class="estacao estacao-atual">.*?<span>(A\d)</span>', secao)
    assert atual == [artefato]
    for rotulo in ("Recebe", "Entrega", "Fora do escopo"):
        assert rotulo in _texto(secao), rotulo


def test_barema_comum_soma_100():
    comum = _secao("entregas-comum")
    barra = [int(p) for p in re.findall(r'style="--peso: (\d+)"', comum)]
    assert barra == [65, 15, 20]
    assert "individual" in _texto(comum)


# --- animação: estado final visível, e direto com movimento reduzido -------

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def servidor():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import check_slides
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    yield "http://127.0.0.1:%d/aulas/aula01.html" % porta
    httpd.shutdown()


def _opacidades(page, id_):
    return page.eval_on_selector_all(
        "section#%s .entrada" % id_, "els => els.map(e => Number(getComputedStyle(e).opacity))")


@pytest.mark.parametrize("id_", ["professor", "combinados", "entregas", "artefato-a3"])
def test_entradas_terminam_visiveis(servidor, id_):
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1280, "height": 720})
        page.goto("%s?t=%s#/%s" % (servidor, id_, id_), wait_until="load")
        page.wait_for_selector("section#%s.present" % id_)
        page.wait_for_timeout(3500)
        opacidades = _opacidades(page, id_)
        navegador.close()
    assert opacidades and all(o == 1 for o in opacidades)


def test_movimento_reduzido_mostra_o_estado_final_de_imediato(servidor):
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        page.goto("%s?t=rm#/combinados" % servidor, wait_until="load")
        page.wait_for_selector("section#combinados.present")
        opacidades = _opacidades(page, "combinados")
        navegador.close()
    assert opacidades and all(o == 1 for o in opacidades)


# --- nuvem antes do parceiro e ordem do Bloco 2 ------------------------------

def _ids():
    return [re.search(r'id="([^"]+)"', s.split(">")[0]).group(1) if 'id="' in s.split(">")[0] else None
            for s in _secoes()]


def test_nuvem_abre_o_case_antes_do_parceiro():
    ids = _ids()
    assert ids.index("o-que-e-o-projeto") + 1 == ids.index("parceiro")
    assert 'data-widget="carteira-nuvem"' in _secao("parceiro")


def test_termos_e_codigo_vem_antes_da_previsao_e_do_widget():
    """Pedido de 20/10/2026: explicar os termos antes da animação da MGLU3 e
    introduzir o widget da B3SA3 pelo código que o aluno vai rodar."""
    ids = _ids()
    assert ids[ids.index("eventos"):ids.index("widget-visoes") + 1] == [
        "eventos", "visoes", "mglu3", "reconstruir", "widget-visoes"]


def test_eventos_usa_exemplo_generico_sem_entregar_a_previsao():
    eventos = _texto(_secao("eventos"))
    assert "MGLU3" not in eventos and "1,32" not in eventos and "896" not in eventos


def test_codigo_da_reconstrucao_e_o_do_notebook():
    import html as html_mod
    import json
    nb = json.load(open(os.path.join(RAIZ, "notebooks", "aula01.ipynb"), encoding="utf-8"))
    celula = next("".join(c["source"]) for c in nb["cells"] if "def preco_negociado" in "".join(c["source"]))
    funcao_nb = celula[celula.index("def preco_negociado"):celula.index("return serie * fator")]
    linhas = re.findall(r'<span class="cl" data-n="\d+"><span class="cl-n">\d+</span>(.*?)</span>(?=<span class="cl"|</code>)',
                        _secao("reconstruir"), re.S)
    codigo = "\n".join(html_mod.unescape(re.sub(r"<[^>]+>", "", l)).rstrip() for l in linhas)
    assert funcao_nb in codigo
    assert 'ler_csv("eventos_desdobramento.csv", parse_dates=["data"])' in codigo
    assert "2021-05-17, fator 3.0" in _secao("reconstruir")
    assert "B3SA3,2021-05-17,3.0" in _ler(os.path.join(RAIZ, "dados", "eventos_desdobramento.csv"))


# --- calendário do end exclusivo ---------------------------------------------

def test_calendario_marca_os_pregoes_do_snapshot():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import medidas_aula01 as m
    secao = _secao("fim-exclusivo")
    dias = re.findall(r'<span class="cal-dia[^"]*" data-dia="(\d+)" data-pregao="(sim|nao)">', secao)
    esperado = [(str(d["dia"]), "sim" if d["pregao"] else "nao") for d in m.calendario_do_mes()]
    assert dias == esperado
    vazios = secao.count('class="cal-vazio"')
    assert vazios == m.calendario_do_mes()[0]["dia_da_semana"]
    medida = m.linhas_com_fim_exclusivo()
    finais = [int(v) for v in re.findall(r'data-final="(\d+)"', secao)]
    assert finais == [medida["dias_corridos"], medida["dias_corridos_fim_exclusivo"],
                      medida["pregoes_inclusivo"], medida["pregoes_fim_exclusivo"]]
    assert secao.count("contagem-certa") == 1


def _ir_calendario(servidor, **opcoes):
    p = sync_api.sync_playwright().start()
    navegador = p.chromium.launch()
    page = navegador.new_page(viewport={"width": 1280, "height": 720}, **opcoes)
    erros = []
    page.on("console", lambda msg: msg.type == "error" and erros.append(msg.text))
    return p, navegador, page, erros


def test_cada_clique_conta_no_calendario_e_explica(servidor):
    p, navegador, page, erros = _ir_calendario(servidor)
    try:
        page.goto("%s?t=cal#/fim-exclusivo" % servidor, wait_until="load")
        page.wait_for_selector("section#fim-exclusivo.present [data-calendario][data-pronto='sim']")
        valores = "section#fim-exclusivo .contagem-valor"
        assert page.eval_on_selector_all(valores, "els => els.map(e => e.textContent)") == ["?"] * 4
        botoes = page.query_selector_all("section#fim-exclusivo .contagem")
        trilhos = []
        for botao in botoes:
            botao.click()
            page.wait_for_function("b => b.classList.contains('contagem-revelada')", arg=botao, timeout=6000)
            trilhos.append(len(botao.query_selector_all(".trilho-marca")))
        assert trilhos == [31, 30, 21, 20]
        assert page.eval_on_selector_all(valores, "els => els.map(e => e.textContent)") == ["31", "30", "21", "20"]
        excluido = page.eval_on_selector("section#fim-exclusivo .cal-end", "e => e.classList.contains('cal-excluido')")
        assert excluido
        explica = page.inner_text("section#fim-exclusivo .calendario-explica")
        assert "segunda-feira, 31/08" in explica
        # o voo não deixa resto na camada
        assert page.eval_on_selector_all("section#fim-exclusivo .calendario-voo", "els => els.length") == 0
        assert erros == []
    finally:
        navegador.close()
        p.stop()


def test_calendario_com_movimento_reduzido_conta_sem_voo(servidor):
    p, navegador, page, erros = _ir_calendario(servidor, reduced_motion="reduce")
    try:
        page.goto("%s?t=calrm#/fim-exclusivo" % servidor, wait_until="load")
        page.wait_for_selector("section#fim-exclusivo [data-calendario][data-pronto='sim']")
        botao = page.query_selector("section#fim-exclusivo .contagem-certa")
        botao.click()
        assert "contagem-revelada" in botao.get_attribute("class")
        assert botao.query_selector(".contagem-valor").inner_text() == "20"
    finally:
        navegador.close()
        p.stop()


# --- coletor em três visões (20/10/2026) -------------------------------------

def _funcao_coletar_do_notebook():
    import json
    nb = json.load(open(os.path.join(RAIZ, "notebooks", "aula01.ipynb"), encoding="utf-8"))
    celula = next("".join(c["source"]) for c in nb["cells"] if "def coletar" in "".join(c["source"]))
    inicio = celula.index("def coletar")
    fim = celula.index('"snapshot de dados/")') + len('"snapshot de dados/")')
    return celula[inicio:fim].split("\n")


def test_coletor_tem_tres_visoes_em_sequencia():
    ids = _ids()
    i = ids.index("coletar")
    assert ids[i:i + 6] == ["coletar", "coletar-codigo", "coletar-revisao",
                            "adr-linha", "adr-agentes", "pratica-coletor"]


def test_funcao_do_notebook_cabe_em_79_colunas():
    """O slide linha a linha mostra a função inteira sem cortar: ela é
    formatada no notebook, que é a fonte, e não só no slide."""
    assert max(len(linha) for linha in _funcao_coletar_do_notebook()) <= 79


def test_codigo_linha_a_linha_e_a_funcao_do_notebook():
    import html as html_mod
    secao = _secao("coletar-codigo")
    linhas = re.findall(r'<span class="cl" data-n="(\d+)"><span class="cl-n">\d+</span>(.*?)</span>(?=<span class="cl"|</code>)', secao, re.S)
    texto = [html_mod.unescape(re.sub(r"<[^>]+>", "", corpo)) for _, corpo in linhas]
    esperado = [linha if linha else " " for linha in _funcao_coletar_do_notebook()]
    assert [int(n) for n, _ in linhas] == list(range(1, len(esperado) + 1))
    assert texto == esperado


def test_passos_do_codigo_cobrem_linhas_existentes_em_ordem():
    secao = _secao("coletar-codigo")
    total = len(_funcao_coletar_do_notebook())
    passos = re.findall(r'class="fragment codigo-passo" data-linhas="([\d-]+)"', secao)
    assert len(passos) == 10
    inicios = []
    for passo in passos:
        de, _, ate = passo.partition("-")
        de, ate = int(de), int(ate or de)
        assert 1 <= de <= ate <= total
        inicios.append(de)
    assert inicios == sorted(inicios)


def test_revisao_cita_trechos_reais_da_funcao():
    import html as html_mod
    secao = _secao("coletar-revisao")
    funcao = _funcao_coletar_do_notebook()
    itens = re.findall(r'<span class="revisao-ref">linhas? (\d+)[^<]*</span>.*?<code>(.*?)</code>', secao, re.S)
    assert len(itens) == 8
    for numero, trecho in itens:
        assert html_mod.unescape(trecho).split("\n")[0] == funcao[int(numero) - 1].strip(), numero
    assert secao.count('class="revisao-item') == 8


def test_codigo_linha_a_linha_destaca_e_desliza_no_navegador(servidor):
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1280, "height": 720})
        erros = []
        page.on("console", lambda msg: msg.type == "error" and erros.append(msg.text))
        page.goto("%s?t=cod#/coletar-codigo" % servidor, wait_until="load")
        page.wait_for_selector("section#coletar-codigo.present [data-codigo-passos][data-pronto='sim']")
        sel = "section#coletar-codigo"
        assert page.eval_on_selector_all(sel + " .cl-destaque", "els => els.length") == 0
        for _ in range(6):
            page.keyboard.press("ArrowRight")
        page.wait_for_timeout(800)
        destacadas = page.eval_on_selector_all(sel + " .cl-destaque", "els => els.map(e => Number(e.dataset.n))")
        assert destacadas == list(range(12, 22))
        assert page.inner_text(sel + " .codigo-contador") == "6 DE 10" or \
            page.eval_on_selector(sel + " .codigo-contador", "e => e.textContent") == "6 de 10"
        # o trecho destacado fica dentro da janela visível
        dentro = page.evaluate("""() => {
            const j = document.querySelector('section#coletar-codigo .codigo-janela').getBoundingClientRect();
            return [...document.querySelectorAll('section#coletar-codigo .cl-destaque')].every(l => {
                const r = l.getBoundingClientRect();
                return r.top >= j.top - 1 && r.bottom <= j.bottom + 1;
            });
        }""")
        navegador.close()
    assert dentro and erros == []


def test_framework_do_modulo_em_cinco_etapas_depois_do_barema():
    """Pedido de 20/10/2026: especificar, ADR, plano de testes, implementar e
    testes funcionais, nessa ordem, para usar com ADRs e spec-driven development."""
    ids = _ids()
    assert ids.index("framework") == ids.index("entregas-comum") + 1
    secao = _secao("framework")
    nomes = re.findall(r'<p class="fw-nome">([^<]+)</p>', secao)
    assert nomes == ["Especificar", "Decidir", "Planejar os testes", "Implementar", "Validar"]
    artefatos = re.findall(r'<p class="fw-artefato">([^<]+)</p>', secao)
    assert artefatos[0] == "SPEC.md" and "/docs/adr/" in artefatos[1] and "testes" in artefatos[2]
    assert "testes funcionais" in artefatos[4]
