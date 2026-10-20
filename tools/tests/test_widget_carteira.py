"""Widget carteira-nuvem do slide do parceiro da Aula 01.

Duas metades. A primeira confere que assets/data/aula01-carteira.json repete as
medições da Aula 04 (tools/medidas_aula04.py) na janela comum da ADR-009, sem
número à mão. A segunda abre tools/tests/fixture_carteira_nuvem.html no
Chromium e confere a animação: dispara com o slide present, termina no estado
final com os 15 ativos e a fronteira, nenhum texto sai da caixa do widget e
prefers-reduced-motion e ?print-pdf mostram o estado final de imediato.
"""
import json
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402
import dados_widgets_aula01 as d1  # noqa: E402
import dados_widgets_aula04 as d4  # noqa: E402
import medidas_aula04 as m4  # noqa: E402
import retornos  # noqa: E402

JSON = os.path.join(m4.RAIZ, "assets", "data", "aula01-carteira.json")
FIXTURE = "tools/tests/fixture_carteira_nuvem.html"


@pytest.fixture(scope="module")
def dados():
    with open(JSON, encoding="utf-8") as fh:
        return json.load(fh)


def _dentro(v, r, caixa):
    return caixa["x"][0] <= v <= caixa["x"][1] and caixa["y"][0] <= r <= caixa["y"][1]


# Dados ----------------------------------------------------------------------

def test_json_versionado_e_o_que_o_gerador_produz(dados):
    gerado = json.loads(json.dumps(d1.carteira(), ensure_ascii=False))
    assert gerado == dados


def test_janela_comum_dos_15_ativos(dados):
    assert dados["janela"] == {"inicio": "14/12/2020", "fim": "31/08/2026", "retornos": 1423}
    assert dados["janela"]["retornos"] == len(retornos.retornos_janela_comum())


def test_ativos_tem_retorno_e_volatilidade_da_mesma_janela_da_nuvem(dados):
    mu, vol = m4.retorno_esperado(), m4.volatilidade()
    assert [a["ticker"] for a in dados["ativos"]] == retornos.TICKERS
    assert len(dados["ativos"]) == 15
    for ativo in dados["ativos"]:
        assert ativo["ret"] == round(float(mu[ativo["ticker"]]), 4)
        assert ativo["vol"] == round(float(vol[ativo["ticker"]]), 4)
    # A volatilidade da PETR4 é a da janela comum (33,40%), não a da série inteira.
    petr4 = next(a for a in dados["ativos"] if a["ticker"] == "PETR4")
    assert petr4["vol"] == round(m4.custo_da_janela("PETR4")["janela_comum"], 4)


def test_carteira_de_peso_igual(dados):
    ret, vol, sharpe = m4.metricas(np.full(15, 1 / 15))
    assert dados["peso"] == round(1 / 15, 4)
    assert dados["igual"] == {"ret": round(ret, 4), "vol": round(vol, 4), "sharpe": round(sharpe, 4)}


def test_nuvem_e_subamostra_deterministica_da_nuvem_da_aula04(dados):
    n = m4.nuvem()
    indices = d1.amostra_nuvem()
    assert len(set(indices.tolist())) == d1.N_AMOSTRA_NUVEM == len(dados["nuvem"]["vol"])
    assert dados["nuvem"]["total"] == m4.N_CARTEIRAS == 10_000
    assert dados["nuvem"]["vol"] == [round(float(n["volatilidade"][i]), 4) for i in indices]
    assert dados["nuvem"]["ret"] == [round(float(n["retorno"][i]), 4) for i in indices]
    assert (d1.amostra_nuvem() == indices).all()


def test_fronteira_e_otimas_sao_as_da_aula04(dados):
    with open(os.path.join(m4.RAIZ, "assets", "data", "aula04-nuvem.json"), encoding="utf-8") as fh:
        aula04 = json.load(fh)
    assert len(dados["fronteira"]) == m4.N_FRONTEIRA == 50
    assert dados["fronteira"] == aula04["fronteira"]
    assert dados["variancia_minima"] == aula04["variancia_minima"]
    assert dados["maximo_sharpe"] == aula04["maximo_sharpe"]
    assert dados["variancia_minima"] == d4._ponto(m4.carteira(m4.variancia_minima()))


def test_quadros_contem_o_que_desenham(dados):
    completo, foco = dados["quadro"]["completo"], dados["quadro"]["foco"]
    assert dados["quadro"]["fora"] == ["MGLU3"]
    for ativo in dados["ativos"]:
        assert _dentro(ativo["vol"], ativo["ret"], completo), ativo
        assert _dentro(ativo["vol"], ativo["ret"], foco) == (ativo["ticker"] not in dados["quadro"]["fora"]), ativo
    for v, r in zip(dados["nuvem"]["vol"], dados["nuvem"]["ret"]):
        assert _dentro(v, r, foco)
    for v, r in dados["fronteira"]:
        assert _dentro(v, r, foco)
    # Folga: nenhum ponto encosta na borda do foco.
    for ativo in dados["ativos"]:
        if ativo["ticker"] not in dados["quadro"]["fora"]:
            assert foco["x"][1] - ativo["vol"] >= d1.FOLGA_QUADRO - 1e-9


# Navegador ------------------------------------------------------------------

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def navegador():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        nav = p.chromium.launch()
        try:
            yield nav, "http://127.0.0.1:%d/%s" % (porta, FIXTURE)
        finally:
            nav.close()
    httpd.shutdown()


def _abrir(navegador, sufixo="#/carteira", reduzir=False):
    nav, url = navegador
    contexto = nav.new_context(viewport={"width": 1280, "height": 720},
                               reduced_motion="reduce" if reduzir else "no-preference")
    pagina = contexto.new_page()
    erros = []
    pagina.on("console", lambda msg: erros.append(msg.text) if msg.type == "error" else None)
    pagina.on("pageerror", lambda exc: erros.append(str(exc)))
    pagina.goto(url + sufixo, wait_until="load")
    pagina.wait_for_selector("[data-widget=carteira-nuvem][data-pronto]", state="attached")
    return pagina, erros


# Nulo-seguro: no ?print-pdf o Reveal reorganiza os slides em páginas logo
# depois do load, e por um instante a consulta pode não achar o elemento.
# Em forma de expressão: os testes concatenam " === 'final'" ao fim.
FASE = "() => (document.querySelector('[data-widget=carteira-nuvem]') || {dataset: {}}).dataset.fase"

# Retângulos dos textos visíveis (opacidade efetiva acima de 0,05) e do SVG.
MEDIR_TEXTOS = """() => {
  const svg = document.querySelector('.carteira-svg');
  const caixa = svg.getBoundingClientRect();
  const escala = caixa.width / svg.viewBox.baseVal.width;
  const visivel = (el) => {
    for (let e = el; e && e !== svg; e = e.parentNode) {
      if (Number(e.getAttribute('opacity') ?? 1) < 0.05) return false;
    }
    return true;
  };
  return {
    svg: {x: caixa.left, y: caixa.top, r: caixa.right, b: caixa.bottom},
    escala,
    textos: [...svg.querySelectorAll('text')].filter(visivel).map(t => {
      const r = t.getBoundingClientRect();
      return {texto: t.textContent, classe: t.getAttribute('class'), x: r.left, y: r.top, r: r.right, b: r.bottom,
              tamanho: Number(t.getAttribute('font-size'))};
    })
  };
}"""


def test_animacao_dispara_no_slide_e_termina_no_estado_final(navegador):
    pagina, erros = _abrir(navegador)
    try:
        assert pagina.get_attribute("[data-widget=carteira-nuvem]", "data-pronto") == "sim"
        assert pagina.evaluate(FASE) in ("animando", "final")
        pagina.wait_for_function(FASE + " === 'final'", timeout=20000)
        assert pagina.locator(".carteira-ativo").count() == 15
        assert pagina.locator(".carteira-igual").count() == 1
        assert pagina.eval_on_selector(".carteira-fronteira", "e => e.getAttribute('stroke-dashoffset')") == "0.0000"
        assert pagina.eval_on_selector(".carteira-fronteira", "e => e.getAttribute('d').split('L').length") == 50
        assert pagina.eval_on_selector_all(".carteira-otima", "es => es.map(e => e.getAttribute('opacity'))") == ["1", "1"]
        assert pagina.eval_on_selector_all(".carteira-ativo", "es => es.every(e => e.getAttribute('opacity') === '1')")
        assert erros == []
    finally:
        pagina.context.close()


def test_estado_final_tem_todo_texto_dentro_da_caixa_e_legivel(navegador):
    pagina, erros = _abrir(navegador)
    try:
        pagina.evaluate("() => { const e = document.querySelector('[data-widget=carteira-nuvem]');"
                        " e.carteiraNuvem.ir(e.carteiraNuvem.fim); }")
        medida = pagina.evaluate(MEDIR_TEXTOS)
        svg, textos = medida["svg"], medida["textos"]
        assert len(textos) > 40
        for t in textos:
            assert t["tamanho"] >= 14, t
            assert t["x"] >= svg["x"] - 0.5 and t["r"] <= svg["r"] + 0.5, t
            assert t["y"] >= svg["y"] - 0.5 and t["b"] <= svg["b"] + 0.5, t
            assert t["b"] <= 720 and t["r"] <= 1280, t
        # Os 15 tickers menos o que fica fora do foco, mais a carteira de peso igual.
        rotulos = [t for t in textos if t["classe"] == "carteira-rotulo"]
        assert sorted(t["texto"] for t in rotulos) == sorted(
            ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3", "SUZB3", "RENT3",
             "B3SA3", "BOVA11", "IVVB11", "GOLD11", "Carteira 1/15"])
        assert any(t["classe"] == "carteira-fora" and "MGLU3" in t["texto"] for t in textos)
        # Nenhum rótulo de ponto encosta em outro.
        marcas = rotulos + [t for t in textos if t["texto"] in ("Variância mínima", "Máximo Sharpe")]
        for i, a in enumerate(marcas):
            for b in marcas[i + 1:]:
                largura = min(a["r"], b["r"]) - max(a["x"], b["x"])
                altura = min(a["b"], b["b"]) - max(a["y"], b["y"])
                assert largura <= 0.5 or altura <= 0.5, (a["texto"], b["texto"])
        assert erros == []
    finally:
        pagina.context.close()


def test_fixture_cabe_no_slide_pelo_check_slides(navegador):
    """O validador de layout mede o deck no carregamento, com o widget em espera."""
    nav, url = navegador
    pagina = nav.new_page(viewport={"width": 1280, "height": 720})
    try:
        assert check_slides.checar(pagina, url, "fixture") == 0
    finally:
        pagina.close()


def test_reduced_motion_mostra_o_estado_final_de_imediato(navegador):
    pagina, erros = _abrir(navegador, reduzir=True)
    try:
        assert pagina.evaluate(FASE) == "final"
        assert pagina.eval_on_selector(".carteira-fronteira", "e => e.getAttribute('stroke-dashoffset')") == "0.0000"
        # O botão Repetir também não anima.
        pagina.click(".carteira-repetir")
        assert pagina.evaluate(FASE) == "final"
        assert erros == []
    finally:
        pagina.context.close()


def test_print_pdf_mostra_o_estado_final(navegador):
    pagina, erros = _abrir(navegador, sufixo="?print-pdf#/carteira")
    try:
        pagina.wait_for_function(FASE + " === 'final'", timeout=5000)
        assert pagina.evaluate("() => document.documentElement.classList.contains('print-pdf')")
        assert erros == []
    finally:
        pagina.context.close()


def test_sair_e_voltar_ao_slide_repete_e_o_botao_repete(navegador):
    pagina, erros = _abrir(navegador, sufixo="#/antes")
    try:
        assert pagina.evaluate(FASE) == "espera"
        # Em espera a cena fica com visibility hidden: com a câmera próxima, os
        # elementos transparentes passam da caixa do SVG, e o check_slides.py
        # (que mede todo slide sem clicar) acusava estouro.
        assert pagina.eval_on_selector(".carteira-svg > g", "g => getComputedStyle(g).visibility") == "hidden"
        pagina.evaluate("() => Reveal.slide(1)")
        pagina.wait_for_function(FASE + " === 'animando'", timeout=5000)
        pagina.evaluate("() => Reveal.slide(0)")
        assert pagina.evaluate(FASE) == "espera"
        pagina.evaluate("() => Reveal.slide(1)")
        pagina.wait_for_function(FASE + " === 'animando'", timeout=5000)
        pagina.evaluate("() => { const e = document.querySelector('[data-widget=carteira-nuvem]');"
                        " e.carteiraNuvem.ir(e.carteiraNuvem.fim); }")
        assert pagina.evaluate(FASE) == "final"
        pagina.click(".carteira-repetir")
        pagina.wait_for_function(FASE + " === 'animando'", timeout=5000)
        assert erros == []
    finally:
        pagina.context.close()
