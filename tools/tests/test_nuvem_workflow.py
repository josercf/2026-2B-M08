"""Workflow do n8n da nuvem de palavras (ADR-012) e a extração de termos.

O workflow.json é importado à mão no n8n do professor, então o que pode
quebrar sem aviso é: um nó trocado de ordem, a URL da ElevenLabs errada, uma
chave de API colada no arquivo (o repositório é público) ou o código do nó Code
divergir de extrair_termos.js, que é o arquivo testado aqui.

A extração roda em node. Sem node na máquina, o mesmo código roda no Chromium
do Playwright.
"""
import json
import os
import re
import shutil
import subprocess

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA = os.path.join(RAIZ, "exemplos", "aula01-nuvem-n8n")
WORKFLOW = os.path.join(PASTA, "workflow.json")
EXTRATOR = os.path.join(PASTA, "extrair_termos.js")


@pytest.fixture(scope="module")
def workflow():
    with open(WORKFLOW, encoding="utf-8") as fh:
        return json.load(fh)


def _no(workflow, tipo):
    nos = [n for n in workflow["nodes"] if n["type"] == tipo]
    assert len(nos) >= 1, tipo
    return nos[0]


def _caminho_principal(workflow):
    """Segue sempre a primeira saída a partir do Webhook."""
    por_nome = {n["name"]: n for n in workflow["nodes"]}
    atual = _no(workflow, "n8n-nodes-base.webhook")["name"]
    caminho = [por_nome[atual]["type"]]
    vistos = {atual}
    while atual in workflow["connections"]:
        saidas = workflow["connections"][atual]["main"]
        if not saidas or not saidas[0]:
            break
        atual = saidas[0][0]["node"]
        assert atual not in vistos, "ciclo em %s" % atual
        vistos.add(atual)
        caminho.append(por_nome[atual]["type"])
    return caminho


def test_caminho_webhook_elevenlabs_code_resposta(workflow):
    caminho = [t for t in _caminho_principal(workflow) if t != "n8n-nodes-base.if"]
    assert caminho == [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.httpRequest",
        "n8n-nodes-base.code",
        "n8n-nodes-base.respondToWebhook",
    ]


def test_webhook_responde_pelo_no_e_libera_as_origens_do_acervo(workflow):
    webhook = _no(workflow, "n8n-nodes-base.webhook")["parameters"]
    assert webhook["httpMethod"] == "POST"
    assert webhook["responseMode"] == "responseNode"
    origens = webhook["options"]["allowedOrigins"].split(",")
    assert "https://josercf.github.io" in origens
    assert "http://localhost:8000" in origens


def test_requisicao_para_a_elevenlabs(workflow):
    http = _no(workflow, "n8n-nodes-base.httpRequest")
    p = http["parameters"]
    assert p["method"] == "POST"
    assert p["url"] == "https://api.elevenlabs.io/v1/speech-to-text"
    assert p["contentType"] == "multipart-form-data"
    # A chave fica numa credencial Header Auth do n8n, nunca no parâmetro.
    assert p["authentication"] == "genericCredentialType"
    assert p["genericAuthType"] == "httpHeaderAuth"
    campos = {c["name"]: c for c in p["bodyParameters"]["parameters"]}
    assert campos["file"]["parameterType"] == "formBinaryData"
    assert campos["file"]["inputDataFieldName"] == "audio"
    assert campos["model_id"]["value"].startswith("scribe_")
    assert campos["language_code"]["value"] == "por"


def test_ramo_recusado_responde_403(workflow):
    se = _no(workflow, "n8n-nodes-base.if")["name"]
    falso = workflow["connections"][se]["main"][1][0]["node"]
    recusa = next(n for n in workflow["nodes"] if n["name"] == falso)
    assert recusa["type"] == "n8n-nodes-base.respondToWebhook"
    assert recusa["parameters"]["options"]["responseCode"] == 403


def test_nenhuma_chave_literal_no_workflow():
    with open(WORKFLOW, encoding="utf-8") as fh:
        texto = fh.read()
    assert re.search(r"sk_[A-Za-z0-9]{16,}", texto) is None         # chave da ElevenLabs
    assert re.search(r"sk-[A-Za-z0-9_-]{20,}", texto) is None        # chave da OpenAI
    assert re.search(r"\b[0-9a-f]{32,}\b", texto) is None
    assert '"xi-api-key"' not in texto and "xi-api-key:" not in texto
    dados = json.loads(texto)
    for no in dados["nodes"]:
        for cred in (no.get("credentials") or {}).values():
            assert cred.get("id", "").startswith("SELECIONE"), cred


def test_codigo_do_no_code_e_o_arquivo_testado(workflow):
    code = _no(workflow, "n8n-nodes-base.code")
    with open(EXTRATOR, encoding="utf-8") as fh:
        assert code["parameters"]["jsCode"] == fh.read()


def test_workflow_e_readme_sem_travessao_e_sem_emoji():
    import sys
    sys.path.insert(0, os.path.join(RAIZ, "tools"))
    import check_brand
    for nome in ("workflow.json", "extrair_termos.js", "README.md"):
        with open(os.path.join(PASTA, nome), encoding="utf-8") as fh:
            texto = fh.read()
        assert chr(0x2014) not in texto, nome
        assert check_brand.EMOJI.search(texto) is None, nome


# ------------------------------------------------------------ extração de termos

CASOS = r"""
const m = CARREGAR();
const termos = (t) => m.extrairTermos(t);
const mapa = (t) => Object.fromEntries(termos(t).map(x => [x.texto, x.peso]));
// Execução como nó Code: $input global, return no topo.
const comoNo = (texto) => {
  const fn = new Function('$input', CODIGO);
  return fn({ all: () => [{ json: { text: texto } }] });
};
return {
  composto: mapa('A ferramenta calcula a Fronteira Eficiente. A fronteira eficiente orienta o gestor.'),
  semAcento: mapa('Faz analise de risco da carteira'),
  stopwords: termos('é uma coisa que a gente faz para o parceiro, né, tipo assim'),
  parRepetido: mapa('simulador financeiro rápido, um simulador financeiro'),
  siglas: mapa('Usa dados da B3 e IA com o CDI'),
  eventos: mapa('[risos] carteira (música) carteira carteira'),
  vazio: termos(''),
  nulo: termos(null),
  ordem: termos('risco retorno retorno carteira carteira carteira').map(x => x.texto),
  no: comoNo('O simulador de carteira eficiente do parceiro'),
};
"""


def _rodar_casos():
    with open(EXTRATOR, encoding="utf-8") as fh:
        codigo = fh.read()
    if shutil.which("node"):
        script = (
            "const fs = require('fs');\n"
            "const CODIGO = fs.readFileSync(%s, 'utf8');\n"
            "const CARREGAR = () => require(%s);\n"
            "const r = (() => {%s})();\n"
            "process.stdout.write(JSON.stringify(r));\n"
        ) % (json.dumps(EXTRATOR), json.dumps(EXTRATOR), CASOS)
        saida = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60, check=True)
        return json.loads(saida.stdout)
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page()
        resultado = page.evaluate(
            """([codigo, casos]) => {
                 const CODIGO = codigo;
                 const CARREGAR = () => { const module = {exports: {}};
                   new Function('module', '$input', codigo)(module, undefined); return module.exports; };
                 return new Function('CODIGO', 'CARREGAR', casos)(CODIGO, CARREGAR);
               }""", [codigo, CASOS])
        navegador.close()
        return resultado


@pytest.fixture(scope="module")
def casos():
    return _rodar_casos()


def test_composto_conta_como_um_termo(casos):
    assert casos["composto"]["fronteira eficiente"] == 2
    assert "fronteira" not in casos["composto"] and "eficiente" not in casos["composto"]
    assert casos["composto"]["ferramenta"] == 1 and casos["composto"]["gestor"] == 1


def test_composto_casa_sem_acento_e_sai_com_acento(casos):
    assert casos["semAcento"] == {"análise de risco": 1, "carteira": 1}


def test_stopwords_e_muletas_da_fala_saem(casos):
    assert [t["texto"] for t in casos["stopwords"]] == ["parceiro"]


def test_par_repetido_vira_composto(casos):
    assert casos["parRepetido"] == {"simulador financeiro": 2, "rápido": 1}


def test_siglas_curtas_ficam_em_caixa_alta(casos):
    assert casos["siglas"] == {"B3": 1, "IA": 1, "CDI": 1, "dados": 1}


def test_eventos_de_audio_sao_descartados(casos):
    assert casos["eventos"] == {"carteira": 3}


def test_texto_vazio_devolve_lista_vazia(casos):
    assert casos["vazio"] == [] and casos["nulo"] == []


def test_ordem_por_peso(casos):
    assert casos["ordem"] == ["carteira", "retorno", "risco"]


def test_saida_do_no_code_no_formato_do_webhook(casos):
    assert casos["no"] == [{"json": {
        "transcricao": "O simulador de carteira eficiente do parceiro",
        "termos": [{"texto": "carteira eficiente", "peso": 1}, {"texto": "parceiro", "peso": 1},
                   {"texto": "simulador", "peso": 1}],
    }}]
