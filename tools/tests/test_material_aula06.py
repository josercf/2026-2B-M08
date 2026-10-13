"""Material e referências da Aula 06: preparação no topo, autoestudos literais e números medidos."""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MATERIAL = os.path.join(RAIZ, "materiais", "aula06.html")
REFERENCIAS = os.path.join(RAIZ, "referencias", "aula06.html")


def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _autoestudos_da_semana_10():
    texto = _ler(os.path.join(RAIZ, "docs", "autoestudos-por-semana.md"))
    secao = texto.split("## Semana 10")[1].split("## ")[0]
    titulos = re.findall(r"^- (.+)$", secao, re.M)
    tempos = {t: re.search(r"\| 10 \| 6 \| 43 \| %s \| (\d+ min)" % re.escape(t), texto).group(1)
              for t in titulos}
    return tempos


def test_material_abre_pela_preparacao_com_autoestudos_videos_e_cinco_perguntas():
    html = _ler(MATERIAL)
    secoes = re.findall(r'<section class="doc-secao" id="([^"]+)"', html)
    assert secoes[0] == "preparacao"
    preparacao = html.split('id="preparacao"')[1].split("</section>")[0]
    for titulo, tempo in _autoestudos_da_semana_10().items():
        assert "%s</strong> (%s)" % (titulo, tempo) in preparacao
    assert preparacao.count("<video ") == 2
    assert preparacao.count("<details>") == 5


def test_referencias_tem_as_duas_secoes_fixas_com_autoestudos_literais():
    html = _ler(REFERENCIAS)
    assert re.findall(r'<section class="doc-secao" id="([^"]+)"', html) == ["autoestudos", "complementar"]
    for titulo, tempo in _autoestudos_da_semana_10().items():
        assert "<strong>%s</strong> (%s" % (titulo, tempo) in html


@pytest.mark.parametrize("caminho", [MATERIAL, REFERENCIAS], ids=os.path.basename)
def test_sem_travessao_nem_emoji(caminho):
    html = _ler(caminho)
    assert chr(0x2014) not in html
    assert not re.search("[\U0001F000-\U0001FAFF]", html)


def test_numeros_do_material_conferem_com_as_medicoes():
    pytest.importorskip("fastapi")
    pytest.importorskip("scipy")
    import medidas_aula06 as m

    texto = _texto(_ler(MATERIAL))
    c = m.contexto()
    br = lambda x: ("%.2f" % x).replace(".", ",")
    s = c["maximo_sharpe"]
    for ticker, peso in s["pesos_pct"].items():
        assert "%s%% em %s" % (br(peso), ticker) in texto
    assert "retorno anual de %s%%, volatilidade de %s%% e Sharpe de %s" % (
        br(s["retorno_anual_pct"]), br(s["volatilidade_anual_pct"]), br(s["sharpe"])) in texto
    assert "{:,}".format(c["pregoes"]).replace(",", ".") + " retornos diários" in texto
    assert "de %s a %s" % tuple("/".join(reversed(d.split("-")))
                                for d in (c["inicio_janela"], c["fim_janela"])) in texto
    com_ouro = m.cliente().post("/carteiras/otimizar", json=dict(
        m.PEDIDO, tickers=["PETR4", "BOVA11", "GOLD11"])).json()
    assert "com a GOLD11 no pedido, ela começa em %s" % "/".join(
        reversed(com_ouro["inicio_janela"].split("-"))) in texto
    assert "de %s%% ao ano" % br(c["taxa_livre_risco_pct"]) in texto
    sem, com = m.problemas_por_pedido(False), m.problemas_por_pedido(True)
    assert "sem cache, %d; com cache, %d" % (sum(sem), sum(com)) in texto
    assert "resolvem %d problemas" % sem[0] in texto
    verificacao = m.verificacao_do_texto()
    conferem = sum(v["confere"] for v in verificacao)
    assert "confere %d de %d números e acusa %d" % (conferem, len(verificacao), len(verificacao) - conferem) in texto
    assert "os %d tickers da base" % len(m.requisicoes()[0]["resposta"]) in texto


def test_numeros_das_notas_do_professor_conferem_com_as_medicoes():
    pytest.importorskip("fastapi")
    pytest.importorskip("scipy")
    import medidas_aula06 as m

    notas = _ler(os.path.join(RAIZ, "docs", "notas-do-professor", "aula06.md"))
    c = m.contexto()
    br = lambda x: ("%.2f" % x).replace(".", ",")
    data = lambda iso: "/".join(reversed(iso.split("-")))
    assert "| %s, de %s a %s (ADR-009" % ("{:,}".format(c["pregoes"]).replace(",", "."),
                                          data(c["inicio_janela"]), data(c["fim_janela"])) in notas
    assert "| %s%% ao ano |" % br(c["taxa_livre_risco_pct"]) in notas
    for nome in ("maximo_sharpe", "variancia_minima"):
        carteira = c[nome]
        linha = [l for l in notas.splitlines()
                 if l.startswith("| %s |" % ("Máximo Sharpe" if nome == "maximo_sharpe" else "Variância mínima"))][0]
        for ticker, peso in carteira["pesos_pct"].items():
            assert "%s%% %s" % (br(peso), ticker) in linha
        assert "retorno %s%%" % br(carteira["retorno_anual_pct"]) in linha
        assert "volatilidade %s%%" % br(carteira["volatilidade_anual_pct"]) in linha
