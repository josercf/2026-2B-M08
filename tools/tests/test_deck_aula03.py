"""Trava a estrutura dos artefatos públicos da Aula 03.

Deck: rodapés em sequência, abertura por Peer Instruction logo depois do resgate,
amarração com o peso e o prazo do PLANO_DE_ENSINO.md. Material: a seção
"Preparação" no topo, com os dois autoestudos da semana 5, as duas animações e
cinco perguntas. Referências: os autoestudos copiados de
docs/autoestudos-por-semana.md, e a seção de leitura complementar presente.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula03 as m  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula03.html")
MATERIAL = os.path.join(RAIZ, "materiais", "aula03.html")
REFERENCIAS = os.path.join(RAIZ, "referencias", "aula03.html")
NOTAS = os.path.join(RAIZ, "docs", "notas-do-professor", "aula03.md")
AUTOESTUDOS = os.path.join(RAIZ, "docs", "autoestudos-por-semana.md")
NOTEBOOK = os.path.join(RAIZ, "notebooks", "aula03.ipynb")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _autoestudos_semana_05():
    bloco = _ler(AUTOESTUDOS).split("## Semana 05", 1)[1].split("## Semana", 1)[0]
    return re.findall(r"^- (.+)$", bloco, flags=re.M)


def test_rodapes_numerados_em_sequencia():
    html = _ler(DECK)
    secoes = re.findall(r"<section\b(.*?)</section>", html, flags=re.S)
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', html)]
    assert numeros == [i + 1 for i, s in enumerate(secoes) if "footer-page" in s]


def test_deck_abre_pelo_resgate_e_pelo_peer_instruction():
    secoes = re.findall(r"<section\b(.*?)</section>", _ler(DECK), flags=re.S)
    assert 'id="resgate"' in secoes[2]
    assert 'id="preparo"' in secoes[3] and "quiz-options" in secoes[3]
    assert "25,98%" in secoes[4]


def test_amarracao_cita_peso_e_prazo_do_plano():
    a3 = _texto(re.search(r'id="a3">(.*?)</section>', _ler(DECK), flags=re.S).group(1))
    assert "A3 Motor de Simulação de Monte Carlo 3" in a3
    assert "Ponderada 1: Diagnóstico de uma carteira herdada 3" in a3
    assert "19/11/2026" in a3 and "20/11/2026, 23h59" in a3


def test_material_abre_pela_preparacao_com_autoestudos_animacoes_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)">(.*?)</section>', html, flags=re.S)
    assert secoes[0][0] == "preparacao"
    preparacao = secoes[0][1]
    for titulo in _autoestudos_semana_05():
        assert titulo in preparacao, titulo
    assert "aula03-curva-correlacao.mp4" in preparacao
    assert "aula03-correlacao-movel.mp4" in preparacao
    assert preparacao.count("<details>") == 5


def test_referencias_copiam_os_autoestudos_e_tem_leitura_complementar():
    html = _ler(REFERENCIAS)
    autoestudos = re.search(r'id="autoestudos">(.*?)</section>', html, flags=re.S).group(1)
    titulos = _autoestudos_semana_05()
    assert len(titulos) == 2
    for titulo in titulos:
        assert titulo in autoestudos, titulo
    assert 'id="complementar"' in html


def test_sem_travessao_nos_artefatos_da_aula():
    for caminho in (DECK, MATERIAL, REFERENCIAS, NOTAS):
        assert chr(0x2014) not in _ler(caminho), caminho


def _secao(html, ident):
    return re.search(r'<section[^>]*id="%s">(.*?)</section>' % ident, html, flags=re.S).group(1)


def _data_br(iso):
    return "/".join(reversed(iso.split("-")))


def _milhar(n):
    return "{:,}".format(n).replace(",", ".")


def test_slide_do_custo_da_janela_comum_cita_os_numeros_medidos():
    custo = m.custo_janela_comum()
    secao = _secao(_ler(DECK), "custo-janela")
    titulo = re.search(r"<h2>(.*?)</h2>", secao).group(1)
    assert titulo == "A janela comum com a GOLD11 leva a PETR4 de %s a %s" % (
        m.pct(custo["serie"]["vol_petr4"]), m.pct(custo["comum"]["vol_petr4"]))
    texto = _texto(secao)
    for lado in ("serie", "comum"):
        assert _data_br(custo[lado]["inicio"]) in texto
        assert _milhar(custo[lado]["retornos"]) in texto
        assert m.dec(custo[lado]["rho_petr4_ivvb11"]) in texto
    assert "%d retornos" % custo["fora"] in texto
    assert "Aula 01" in texto and "ADR" in texto


def test_custo_da_janela_comum_vem_logo_depois_da_matriz_anualizada():
    secoes = re.findall(r"<section\b(.*?)</section>", _ler(DECK), flags=re.S)
    ids = [re.search(r'id="([^"]+)"', s).group(1) if 'id="' in s.split(">", 1)[0] else None for s in secoes]
    assert ids.index("custo-janela") == ids.index("covariancia") + 1


def test_matriz_do_deck_e_a_da_janela_comum_dos_15_ativos():
    html = _ler(DECK)
    janela = m.janela_cesta()
    declaracao = "%s retornos, %s a %s" % (_milhar(janela["retornos"]), _data_br(janela["inicio"]),
                                          _data_br(janela["fim"]))
    assert declaracao in _ler(DECK)
    pares = m.pares_ordenados()
    assert "têm a maior correlação, %s" % m.dec(pares.iloc[-1]) in _secao(html, "pares")
    assert "<strong>%s</strong>" % m.dec(pares.mean()) in _secao(html, "pares")
    cov = m.matriz_covariancia_anual()
    excerto = _texto(_secao(html, "covariancia"))
    for a in m.EXCERTO:
        linha = " ".join(m.dec(cov.loc[a, b], 4) for b in m.EXCERTO)
        assert "%s %s" % (a, linha) in excerto, a
    assert "%s, é %s ao quadrado" % (m.dec(cov.loc["PETR4", "PETR4"], 4),
                                     m.pct(cov.loc["PETR4", "PETR4"] ** 0.5)) in excerto


def test_escolha_coletiva_do_deck_repete_a_matriz_e_a_regua():
    secao = _secao(_ler(DECK), "escolha-pares")
    assert "<h2>Classificação exploratória de pares</h2>" in secao
    assert "Heurística exploratória desta aula, sem valor de regra de decisão" in secao
    itens = re.findall(r'<p class="escolha-item">(\d+)\. (\w+) e (\w+), ρ = ([^<]+)</p>\s*'
                       r'<ul class="escolha-opcoes">(.*?)</ul>', secao, flags=re.S)
    rotulo = {"concentra": "Concentra", "intermediário": "Intermediário", "diversifica": "Diversifica"}
    lidos = sorted((int(n), a, b, rho, re.search(r'<li data-correct="true">(\w+)</li>', ops).group(1))
                   for n, a, b, rho, ops in itens)
    esperados = [(i + 1, a, b, m.dec(rho), rotulo[classe])
                 for i, (a, b, rho, classe) in enumerate(m.escolha_coletiva())]
    assert lidos == esperados
    assert {e[4] for e in esperados} == set(rotulo.values())


def _milhar(n):
    return "{:,}".format(n).replace(",", ".")


def test_reducao_50_50_dos_pares_vem_logo_depois_da_escolha_e_repete_a_medicao():
    html = _ler(DECK)
    ordem = re.findall(r'<section[^>]*id="([\w-]+)"', html)
    assert ordem[ordem.index("escolha-pares") + 1] == "reducao-pares"
    secao = _secao(html, "reducao-pares")
    dados = m.reducao_pares_escolha()
    reducoes = [d["reducao"] for d in dados]
    assert "<h2>A carteira 50/50 corta de %s a %s do risco</h2>" % (
        m.pct(min(reducoes)), m.pct(max(reducoes))) in secao
    linhas = re.findall(r"<tr><td>(\w+) e (\w+)</td>((?:<td>[^<]*</td>)+)</tr>", secao)
    lidas = [(a, b, re.findall(r"<td>([^<]*)</td>", resto)) for a, b, resto in linhas]
    esperadas = [(d["a"], d["b"], [m.dec(d["rho_cesta"]), m.dec(d["rho_par"]),
                                   "%s, %s" % (_data_br(d["inicio"]), _milhar(d["retornos"])),
                                   "%s e %s" % (m.pct(d["vol_a"]), m.pct(d["vol_b"])),
                                   m.pct(d["media_vols"]), m.pct(d["vol_carteira"]),
                                   m.dec(100 * d["reducao_pp"]), m.pct(d["reducao"])])
                 for d in dados]
    assert lidas == esperadas
    texto = _texto(secao)
    assert "Pesos de 50% em cada ativo" in texto
    mudam = [d for d in dados if d["classe_cesta"] != d["classe_par"]]
    assert [(d["a"], d["b"]) for d in mudam] == [("PETR4", "BOVA11"), ("PETR4", "VALE3")]
    for d in mudam:
        assert "%s e %s sobe a %s" % (d["a"], d["b"], m.dec(d["rho_par"])) in texto or \
            "%s e %s a %s" % (d["a"], d["b"], m.dec(d["rho_par"])) in texto


def test_regua_aparece_como_heuristica_no_material_e_nas_notas():
    material = _texto(_ler(MATERIAL))
    notas = _ler(NOTAS)
    assert "heurística exploratória" in material and "heurística exploratória" in notas
    assert "convenção didática" not in notas
    for d in m.reducao_pares_escolha():
        assert m.pct(d["reducao"]) in material, (d["a"], d["b"])
        assert m.pct(d["reducao"]) in notas, (d["a"], d["b"])


def test_notebook_mede_a_reducao_50_50_dos_pares_da_escolha():
    nb = json.loads(_ler(NOTEBOOK))
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    assert all(not c.get("outputs") for c in nb["cells"] if c["cell_type"] == "code")
    for a, b in m.PARES_ESCOLHA:
        assert '("%s", "%s")' % (a, b) in codigo


def test_material_traz_o_custo_da_janela_comum():
    custo = m.custo_janela_comum()
    texto = _texto(_ler(MATERIAL))
    assert "O custo da janela comum" in texto
    assert m.pct(custo["serie"]["vol_petr4"]) in texto and m.pct(custo["comum"]["vol_petr4"]) in texto
    assert "ADR-009" in texto


def test_notebook_implementa_a_adr_009_sem_importar_tools():
    nb = json.loads(_ler(NOTEBOOK))
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    texto = "\n".join("".join(c["source"]) for c in nb["cells"])
    assert "ADR-009" in texto
    assert "def janela_comum" in codigo and "comum.cov()" in codigo
    assert "import retornos" not in codigo and "tools" not in codigo
