"""Nuvem de palavras ao vivo por voz (ADR-012), medida no navegador.

O check_slides.py mede o deck sem clicar em nada, e a nuvem só existe depois
de interação (inteli-deck-design, seção 8.4). Estes testes montam o fixture
tools/tests/fixture_nuvem.html, alimentam a nuvem pela API, pelo campo de texto
e pelo fluxo de envio com o webhook simulado, e medem o resultado com
getBoundingClientRect.

O microfone é o falso do Chromium (--use-fake-device-for-media-stream), que
toca um bipe periódico: alto o bastante para o trecho passar do limiar de fala
e ser enviado. O webhook do n8n é simulado por page.route.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")

SLIDE = "o-que-e-o-projeto"
WEBHOOK = "https://n8n.exemplo.test/webhook/nuvem-teste"

QUARENTA = [
    ("fronteira eficiente", 6), ("carteira", 5), ("risco", 5), ("retorno", 4), ("Markowitz", 4),
    ("simulador", 3), ("dados de mercado", 3), ("excedente de caixa", 3), ("parceiro", 3), ("CDI", 2),
    ("Selic", 2), ("IPCA", 2), ("volatilidade", 2), ("correlação", 2), ("diversificação", 2),
    ("otimizador", 2), ("gestor", 1), ("decisão", 1), ("B3", 1), ("ações", 1),
    ("renda fixa", 1), ("yfinance", 1), ("notebook", 1), ("Python", 1), ("dashboard", 1),
    ("API", 1), ("React", 1), ("FastAPI", 1), ("preço ajustado", 1), ("proventos", 1),
    ("desdobramento", 1), ("série histórica", 1), ("taxa livre de risco", 1), ("liquidez", 1),
    ("investimento", 1), ("benchmark", 1), ("covariância", 1), ("Sharpe", 1), ("alocação", 1),
    ("previsão", 1),
]

# Registra cada chamada a getUserMedia antes de qualquer script da página.
ESPIAO_MICROFONE = """
window.__pedidosMicrofone = 0;
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  const original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
  navigator.mediaDevices.getUserMedia = (c) => { window.__pedidosMicrofone++; return original(c); };
}
"""


@pytest.fixture(scope="module")
def ambiente():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch(args=[
            "--use-fake-device-for-media-stream",
            "--use-fake-ui-for-media-stream",
            "--autoplay-policy=no-user-gesture-required",
        ])
        try:
            yield navegador, "http://127.0.0.1:%d/tools/tests/fixture_nuvem.html" % porta
        finally:
            navegador.close()
    httpd.shutdown()


@pytest.fixture
def pagina(ambiente):
    """Contexto novo por teste: localStorage limpo e permissão de microfone."""
    navegador, url = ambiente
    contexto = navegador.new_context(viewport={"width": 1280, "height": 720},
                                     permissions=["microphone"], reduced_motion="reduce")
    page = contexto.new_page()
    page.add_init_script(ESPIAO_MICROFONE)
    erros = []
    page.on("pageerror", lambda e: erros.append(str(e)))
    page.on("console", lambda m: m.type == "error" and erros.append(m.text))
    page.erros = erros

    def ir(query=""):
        page.goto("%s%s#/%s" % (url, query, SLIDE), wait_until="load")
        page.wait_for_selector("section#%s.present .nuvem[data-pronto='sim']" % SLIDE)
        page.evaluate("document.fonts.ready")
        return page

    page.ir = ir
    yield page
    contexto.close()


def _retangulos(page):
    return page.evaluate("""() => {
      const area = document.querySelector('#nuvem-projeto .nuvem-area').getBoundingClientRect();
      const termos = [...document.querySelectorAll('#nuvem-projeto .nuvem-termo')].map(e => {
        const r = e.getBoundingClientRect();
        return {texto: e.textContent, l: r.left, t: r.top, r: r.right, b: r.bottom,
                fonte: parseFloat(e.style.fontSize)};
      });
      return {area: {l: area.left, t: area.top, r: area.right, b: area.bottom}, termos: termos};
    }""")


def _adicionar(page, termos):
    page.evaluate("t => IntelINuvem.adicionar(t.map(x => ({texto: x[0], peso: x[1]})))", termos)
    page.wait_for_function("n => document.querySelectorAll('#nuvem-projeto .nuvem-termo').length >= n",
                           arg=min(len(termos), 60))
    # Com reduced_motion não há transição: a posição final vale no quadro seguinte.
    page.wait_for_timeout(100)


def test_monta_sem_erro_de_console_e_com_estado_vazio(pagina):
    page = pagina.ir()
    assert page.erros == []
    assert page.evaluate("IntelINuvem.estado().termos.length") == 0
    assert page.is_visible("#nuvem-projeto .nuvem-vazio")
    assert page.inner_text("#nuvem-projeto .nuvem-mic-rotulo") == "Ouvir a turma"
    # Ícones do sprite: o <use> aponta para um símbolo que existe.
    href = page.get_attribute("#nuvem-projeto .nuvem-mic use", "href")
    assert href.endswith("assets/icons/icones.svg#mic")


def test_quarenta_termos_cabem_sem_sobreposicao_e_dentro_do_palco(pagina):
    page = pagina.ir()
    _adicionar(page, QUARENTA)
    medida = _retangulos(page)
    termos, area = medida["termos"], medida["area"]
    assert len(termos) == len(QUARENTA)
    assert {t["texto"] for t in termos} == {t[0] for t in QUARENTA}
    for t in termos:
        assert t["l"] >= area["l"] - 0.5 and t["r"] <= area["r"] + 0.5, t
        assert t["t"] >= area["t"] - 0.5 and t["b"] <= area["b"] + 0.5, t
        assert t["r"] <= 1280 and t["b"] <= 720, t
    for i, a in enumerate(termos):
        for b in termos[i + 1:]:
            horizontal = min(a["r"], b["r"]) - max(a["l"], b["l"])
            vertical = min(a["b"], b["b"]) - max(a["t"], b["t"])
            assert horizontal <= 0.5 or vertical <= 0.5, (a["texto"], b["texto"])
    # O mais citado é o maior e leva o filete coral; os menores ficam acima do piso.
    maior = max(termos, key=lambda t: t["fonte"])
    assert maior["texto"] == "fronteira eficiente"
    assert page.inner_text("#nuvem-projeto .nuvem-lider") == "fronteira eficiente"
    assert min(t["fonte"] for t in termos) >= 15
    assert page.erros == []


def test_limite_de_sessenta_termos_visiveis(pagina):
    page = pagina.ir()
    page.evaluate("""() => { const l = []; for (let i = 0; i < 75; i++) l.push({texto: 'termo' + i, peso: 1 + (i % 3)});
                            IntelINuvem.adicionar(l); }""")
    page.wait_for_timeout(200)
    estado = page.evaluate("IntelINuvem.estado()")
    assert len(estado["termos"]) == 75
    visiveis = page.locator("#nuvem-projeto .nuvem-termo").count()
    assert 0 < visiveis <= 60


def test_repetir_um_termo_aumenta_o_tamanho(pagina):
    page = pagina.ir()
    _adicionar(page, [("carteira", 1), ("risco", 3), ("retorno", 1), ("parceiro", 2)])
    seletor = "#nuvem-projeto .nuvem-termo[data-peso]"

    def tamanho(texto):
        return page.evaluate("""t => { const e = [...document.querySelectorAll('#nuvem-projeto .nuvem-termo')]
                                   .find(x => x.textContent === t); return parseFloat(e.style.fontSize); }""", texto)

    antes = tamanho("carteira")
    page.evaluate("IntelINuvem.adicionar(['carteira', 'carteira', 'Carteira'])")
    page.wait_for_timeout(150)
    assert page.locator(seletor).count() == 4
    assert page.evaluate("IntelINuvem.estado().termos[0]") == {"texto": "carteira", "peso": 4, "visivel": True}
    assert tamanho("carteira") > antes


def test_limpar_zera_a_nuvem(pagina):
    page = pagina.ir()
    _adicionar(page, QUARENTA[:10])
    page.click("#nuvem-projeto .nuvem-limpar")
    page.wait_for_timeout(100)
    assert page.evaluate("IntelINuvem.estado().termos") == []
    assert page.locator("#nuvem-projeto .nuvem-termo").count() == 0
    assert page.inner_text("#nuvem-projeto .nuvem-contagem") == ""


def test_campo_de_texto_adiciona_com_enter_e_nao_avanca_o_slide(pagina):
    page = pagina.ir()
    campo = "#nuvem-projeto .nuvem-entrada"
    page.click(campo)
    page.keyboard.type("fronteira eficiente")     # o espaço não pode avançar o deck
    page.keyboard.press("ArrowRight")
    page.keyboard.press("Enter")
    page.keyboard.type("risco, retorno")
    page.keyboard.press("Enter")
    page.wait_for_timeout(150)
    textos = sorted(t["texto"] for t in page.evaluate("IntelINuvem.estado().termos"))
    assert textos == ["fronteira eficiente", "retorno", "risco"]
    assert page.input_value(campo) == ""
    assert page.evaluate("Reveal.getIndices().h") == 1
    assert page.is_visible("section#%s.present" % SLIDE)


def test_sem_url_o_microfone_abre_a_configuracao_e_nao_pede_permissao(pagina):
    page = pagina.ir()
    page.click("#nuvem-projeto .nuvem-mic")
    page.wait_for_selector("#nuvem-projeto.nuvem-configurando .nuvem-config", state="visible")
    assert page.evaluate("window.__pedidosMicrofone") == 0
    assert page.evaluate("IntelINuvem.estado().gravando") is False
    # URL inválida não é aceita e continua sem pedir o microfone.
    page.fill("#nuvem-projeto .nuvem-config input[type=url]", "ftp://qualquer")
    page.click("#nuvem-projeto .nuvem-salvar")
    assert "inválida" in page.inner_text("#nuvem-projeto .nuvem-status")
    assert page.evaluate("window.__pedidosMicrofone") == 0
    assert page.evaluate("localStorage.getItem('inteli-nuvem-webhook')") is None


def _simular_webhook(page, pedidos, status=200, corpo=None):
    corpo = corpo or {
        "transcricao": "É um simulador de carteira eficiente para o parceiro",
        "termos": [{"texto": "simulador", "peso": 1}, {"texto": "carteira eficiente", "peso": 2}],
    }

    def responder(route):
        req = route.request
        pedidos.append({"metodo": req.method, "tipo": req.headers.get("content-type", ""),
                        "corpo": req.post_data_buffer or b""})
        route.fulfill(status=status, content_type="application/json",
                      headers={"Access-Control-Allow-Origin": "*"}, body=json.dumps(corpo))

    page.route(WEBHOOK, responder)


def test_fluxo_de_envio_com_webhook_simulado(pagina):
    pedidos = []
    _simular_webhook(pagina, pedidos)
    page = pagina.ir("?nuvem=%s&nuvem-token=segredo-de-teste" % WEBHOOK)
    assert page.evaluate("localStorage.getItem('inteli-nuvem-webhook')") == WEBHOOK

    page.click("#nuvem-projeto .nuvem-mic")
    page.wait_for_function("IntelINuvem.estado().gravando === true", timeout=5000)
    assert page.evaluate("window.__pedidosMicrofone") == 1
    assert "nuvem-gravando" in page.get_attribute("#nuvem-projeto", "class")

    page.wait_for_function(
        "IntelINuvem.estado().termos.some(t => t.texto === 'carteira eficiente')", timeout=20000)
    page.click("#nuvem-projeto .nuvem-mic")
    page.wait_for_function("IntelINuvem.estado().gravando === false")

    assert pedidos, "nenhum POST chegou ao webhook"
    primeiro = pedidos[0]
    assert primeiro["metodo"] == "POST"
    assert primeiro["tipo"].startswith("multipart/form-data")
    assert b'name="audio"; filename="trecho-1.' in primeiro["corpo"]
    assert b"Content-Type: audio/" in primeiro["corpo"]
    assert b'name="token"' in primeiro["corpo"] and b"segredo-de-teste" in primeiro["corpo"]
    # Cada trecho é um arquivo completo: o WebM começa pelo cabeçalho EBML.
    assert b"\x1a\x45\xdf\xa3" in primeiro["corpo"]

    assert "simulador de carteira" in page.inner_text("#nuvem-projeto .nuvem-frase")
    assert page.locator("#nuvem-projeto .nuvem-termo").count() >= 2
    assert page.erros == []


def test_falha_do_webhook_vira_aviso_e_a_gravacao_continua(pagina):
    pedidos = []
    _simular_webhook(pagina, pedidos, status=500, corpo={"erro": "falha simulada"})
    page = pagina.ir("?nuvem=%s" % WEBHOOK)
    page.click("#nuvem-projeto .nuvem-mic")
    page.wait_for_selector("#nuvem-projeto .nuvem-status.nuvem-aviso", timeout=20000)
    assert "HTTP 500" in page.inner_text("#nuvem-projeto .nuvem-status")
    assert page.evaluate("IntelINuvem.estado().gravando") is True
    erros_de_pagina = [e for e in page.erros if "500" not in e]
    assert erros_de_pagina == []
    page.click("#nuvem-projeto .nuvem-mic")


def test_sair_do_slide_desliga_o_microfone(pagina):
    pedidos = []
    _simular_webhook(pagina, pedidos)
    page = pagina.ir("?nuvem=%s" % WEBHOOK)
    page.click("#nuvem-projeto .nuvem-mic")
    page.wait_for_function("IntelINuvem.estado().gravando === true", timeout=5000)
    page.evaluate("Reveal.next()")
    page.wait_for_function("IntelINuvem.estado().gravando === false", timeout=5000)
