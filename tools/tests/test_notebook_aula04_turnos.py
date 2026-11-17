"""Notebook dos turnos 1 e 2 da Aula 04 (notebooks/aula04.ipynb).

Executa o notebook de verdade, sem rede, em uma cópia temporária: com as
respostas vazias, com as funções da referência injetadas e com erros típicos
de aluno. O `simulador.py` que a última célula grava é conferido pelo
`conferir.py` do kit.
"""
import json
import os
import shutil
import subprocess
import sys

import nbformat
import pandas as pd
import pytest
from nbclient import NotebookClient

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import simulador_referencia as sim  # noqa: E402

NOTEBOOK = os.path.join(RAIZ, "notebooks", "aula04.ipynb")
KIT = os.path.join(RAIZ, "exemplos", "aula04-simulador")
CSV = os.path.join(KIT, "dados", "precos.csv")

CORPO_TURNO1 = "    return sum(p * r for p, r in zip(pesos, retornos_do_dia))\n"
CORPO_TURNO2 = ("    diarios = [retorno_do_dia(pesos, linha) for linha in retornos.values]\n"
                "    return np.mean(diarios) * 252, np.std(diarios, ddof=1) * np.sqrt(252)\n")


def _bruto():
    with open(NOTEBOOK, encoding="utf-8") as fh:
        return json.load(fh)


def _referencia(ativos=("PETR4", "VALE3"), pregoes=9):
    precos = pd.read_csv(CSV, index_col="data")
    rets = sim.retornos(precos, list(ativos), pregoes)
    pesos = [1 / len(ativos)] * len(ativos)
    retorno, risco = sim.metricas(pesos, rets)
    return sim.retorno_do_dia(pesos, rets.iloc[0]), retorno, risco


def _executar(tmp_path, trocas=None, extras=(), acrescimos=None):
    """Roda o notebook numa cópia, com M08_OFFLINE=1. Devolve {id da célula: texto impresso}.

    trocas: {id: função que recebe a fonte e devolve a fonte nova}.
    acrescimos: {id: texto acrescentado ao fim da célula}.
    extras: células de código acrescentadas ao fim, com id extra-0, extra-1...
    """
    pasta = tmp_path / "notebooks"
    pasta.mkdir(parents=True, exist_ok=True)
    dados = tmp_path / "exemplos" / "aula04-simulador" / "dados"
    dados.mkdir(parents=True, exist_ok=True)
    shutil.copy(CSV, dados / "precos.csv")
    nb = nbformat.read(NOTEBOOK, as_version=4)
    for celula in nb.cells:
        if trocas and celula.id in trocas:
            celula.source = trocas[celula.id](celula.source)
        if acrescimos and celula.id in acrescimos:
            celula.source += "\n" + acrescimos[celula.id]
    for i, fonte in enumerate(extras):
        celula = nbformat.v4.new_code_cell(fonte)
        celula.id = "extra-%d" % i
        nb.cells.append(celula)
    antes = os.environ.get("M08_OFFLINE")
    os.environ["M08_OFFLINE"] = "1"
    try:
        NotebookClient(nb, timeout=120, kernel_name="python3",
                       resources={"metadata": {"path": str(pasta)}}).execute()
    finally:
        if antes is None:
            del os.environ["M08_OFFLINE"]
        else:
            os.environ["M08_OFFLINE"] = antes
    saidas = {}
    for celula in nb.cells:
        if celula.cell_type != "code":
            continue
        assert not any(s.output_type == "error" for s in celula.outputs), celula.id
        saidas[celula.id] = "".join(s.get("text", "") for s in celula.outputs
                                    if s.output_type == "stream")
    return saidas


def _resolver(esperado1, esperado_retorno, esperado_risco):
    return {
        "aula04-10": lambda f: f.replace("ESPERADO_TURNO1 = None", "ESPERADO_TURNO1 = %r" % (esperado1,)),
        "aula04-14": lambda f: f.replace("ESPERADO_RETORNO_ANUAL = None",
                                         "ESPERADO_RETORNO_ANUAL = %r" % (esperado_retorno,))
                                .replace("ESPERADO_RISCO_ANUAL = None",
                                         "ESPERADO_RISCO_ANUAL = %r" % (esperado_risco,)),
    }


@pytest.fixture(scope="module")
def vazio(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("vazio")
    return pasta, _executar(pasta)


@pytest.fixture(scope="module")
def resolvido(tmp_path_factory):
    """Funções corretas, valores do portal digitados, e chamadas extras com formatos e erros."""
    dia, retorno, risco = _referencia()
    pasta = tmp_path_factory.mktemp("resolvido")
    extras = [
        # 0: formatos aceitos no turno 1 (Review Focus 4)
        "for _v in (%r, %r, '%s', '%s', ' %s %%'):\n    conferir_turno1(_v, retorno_do_dia)\n" % (
            dia, 100 * dia, ("%.2f%%" % (100 * dia)).replace(".", ","),
            ("%.2f" % (100 * dia)).replace(".", ","), ("%.2f" % (100 * dia)).replace(".", ",")),
        # 1: formatos aceitos no turno 2, inclusive fração com módulo maior que 1,5
        "conferir_turno2(%r, %r, metricas)\n"
        "conferir_turno2(%r, %r, metricas)\n"
        "conferir_turno2('%s', '%s', metricas)\n" % (
            retorno, risco, 100 * retorno, 100 * risco,
            ("%.2f%%" % (100 * retorno)).replace(".", ","),
            ("%.2f" % (100 * risco)).replace(".", ",")),
        # 2: tolerância de 0,05 ponto percentual: 0,04 passa, 0,06 não
        "conferir_turno1(%r, retorno_do_dia)\nprint('---')\nconferir_turno1(%r, retorno_do_dia)\n" % (
            dia + 0.0004, dia + 0.0006),
        # 3: valor lido errado no portal, com a função certa
        "conferir_turno1('9,99%', retorno_do_dia)\n",
        # 4: valor que não é número
        "conferir_turno1('abc', retorno_do_dia)\n",
        # 5: função que esquece os pesos
        "conferir_turno1(%r, lambda pesos, r: sum(r))\n" % dia,
        # 6: função que levanta erro qualquer e função com NotImplementedError
        "def _quebra(pesos, r):\n    return pesos[99]\n"
        "def _nao(pesos, r):\n    raise NotImplementedError\n"
        "conferir_turno1(%r, _quebra)\nprint('---')\nconferir_turno1(%r, _nao)\n" % (dia, dia),
        # 7: risco com desvio populacional
        "conferir_turno2(%r, %r, lambda p, t: ((t.values @ p).mean() * 252, "
        "(t.values @ p).std() * 252 ** 0.5))\n" % (retorno, risco),
        # 8: retorno sem anualizar e saída que não é um par
        "conferir_turno2(%r, %r, lambda p, t: ((t.values @ p).mean(), "
        "(t.values @ p).std(ddof=1) * 252 ** 0.5))\nprint('---')\n"
        "conferir_turno2(%r, %r, lambda p, t: 0.1)\n" % (retorno, risco, retorno, risco),
        # 9: carteira inválida não derruba a conferência
        "ATIVOS = ['PETR4', 'NAOEXISTE3']\nconferir_turno1(%r, retorno_do_dia)\n"
        "conferir_turno2(%r, %r, metricas)\n" % (dia, retorno, risco),
    ]
    saidas = _executar(
        pasta,
        trocas=_resolver("%.2f%%" % (100 * dia), ("%.2f%%" % (100 * retorno)).replace(".", ","),
                         ("%.2f" % (100 * risco)).replace(".", ",")),
        acrescimos={"aula04-08": CORPO_TURNO1, "aula04-12": CORPO_TURNO2},
        extras=extras)
    return pasta, saidas


# --- contrato -----------------------------------------------------------------

def test_badge_do_colab_na_primeira_celula_e_nenhuma_saida_gravada():
    nb = _bruto()
    primeira = nb["cells"][0]
    assert primeira["cell_type"] == "markdown"
    assert ("https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/"
            "notebooks/aula04.ipynb") in "".join(primeira["source"])
    for celula in nb["cells"]:
        if celula["cell_type"] == "code":
            assert celula["outputs"] == [] and celula["execution_count"] is None


def test_carga_do_disco_com_queda_para_a_url_bruta_e_sem_importar_tools():
    codigo = "\n".join("".join(c["source"]) for c in _bruto()["cells"] if c["cell_type"] == "code")
    assert 'os.path.join("..", "exemplos", "aula04-simulador", "dados", "precos.csv")' in codigo
    assert "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/" in codigo
    assert "exemplos/aula04-simulador/dados/precos.csv" in codigo
    assert "M08_OFFLINE" in codigo
    assert "simulador_referencia" not in codigo and "tools" not in codigo
    assert "sys.path" not in codigo


def test_texto_sem_travessao_e_com_a_carteira_padrao():
    texto = json.dumps(_bruto(), ensure_ascii=False)
    assert chr(0x2014) not in texto
    assert 'ATIVOS = [\\"PETR4\\", \\"VALE3\\"]' in texto
    assert "PREGOES = 9" in texto


def test_conferencia_do_professor_fica_em_celula_recolhida():
    celulas = {c["id"]: c for c in _bruto()["cells"]}
    conferencia = celulas["aula04-04"]
    assert conferencia["metadata"]["jupyter"]["source_hidden"] is True
    assert conferencia["metadata"]["cellView"] == "form"
    fonte = "".join(conferencia["source"])
    assert fonte.startswith("#@title Conferência do professor")
    assert "def conferir_turno1(esperado, funcao)" in fonte
    assert "def conferir_turno2(esperado_retorno, esperado_risco, funcao)" in fonte


def test_scaffold_traz_assinatura_e_docstring_sem_a_solucao():
    celulas = {c["id"]: "".join(c["source"]) for c in _bruto()["cells"]}
    assert "def retorno_do_dia(pesos, retornos_do_dia):" in celulas["aula04-08"]
    assert "def metricas(pesos, retornos):" in celulas["aula04-12"]
    for ident in ("aula04-08", "aula04-12"):
        assert "return " not in celulas[ident].replace("começando com return", "")
    for trecho in ("vezes 252", "ddof=1", "raiz de 252"):
        assert trecho in celulas["aula04-12"]


# --- execução com respostas vazias ----------------------------------------------

def test_executa_sem_rede_com_respostas_vazias_e_diz_ainda_nao(vazio):
    pasta, saidas = vazio
    for ident, turno in (("aula04-10", 1), ("aula04-14", 2)):
        assert "TURNO %d: AINDA NÃO" % turno in saidas[ident]
        assert "em branco" in saidas[ident]
        assert "ainda não devolve nada" in saidas[ident]
        assert "Pista:" in saidas[ident]
        assert "OK" not in saidas[ident].replace("[ok]", "")
    assert "soma de cada peso vezes o retorno do ativo" in saidas["aula04-10"]


def test_respostas_vazias_nao_gravam_simulador_py(vazio):
    pasta, saidas = vazio
    assert "AINDA NÃO" in saidas["aula04-16"]
    assert not (pasta / "notebooks" / "simulador.py").exists()


# --- execução com as funções prontas ---------------------------------------------

def test_funcoes_corretas_e_valores_do_portal_dao_ok_nos_dois_turnos(resolvido):
    _, saidas = resolvido
    assert saidas["aula04-10"].startswith("TURNO 1: OK")
    assert saidas["aula04-14"].startswith("TURNO 2: OK")
    assert "[falta]" not in saidas["aula04-10"] + saidas["aula04-14"]


def test_referencia_do_notebook_e_a_mesma_de_tools(resolvido):
    """O OK acima saiu de valores calculados por tools/simulador_referencia.py."""
    dia, retorno, risco = _referencia()
    assert abs(dia) > 1e-4 and abs(retorno) > 1.5 and risco > 0.05


def test_valor_esperado_aceita_fracao_porcentagem_virgula_e_simbolo(resolvido):
    _, saidas = resolvido
    assert saidas["extra-0"].count("TURNO 1: OK") == 5
    assert saidas["extra-1"].count("TURNO 2: OK") == 3
    assert "AINDA NÃO" not in saidas["extra-0"] + saidas["extra-1"]


def test_tolerancia_e_de_cinco_centesimos_de_ponto_percentual(resolvido):
    _, saidas = resolvido
    dentro, fora = saidas["extra-2"].split("---")
    assert "TURNO 1: OK" in dentro
    assert "TURNO 1: AINDA NÃO" in fora and "[falta] Valor digitado" in fora


def test_erro_de_leitura_do_portal_e_nomeado_com_o_que_veio_e_o_esperado(resolvido):
    _, saidas = resolvido
    dia = _referencia()[0]
    texto = saidas["extra-3"]
    assert "TURNO 1: AINDA NÃO" in texto
    assert "[falta] Valor digitado: veio 9,9900%" in texto
    assert ("%.4f%%" % (100 * dia)).replace(".", ",") in texto
    assert "[ok]    Função" in texto
    assert "não consegui ler 'abc'" in saidas["extra-4"]


def test_funcao_errada_recebe_diagnostico_sem_a_linha_pronta(resolvido):
    _, saidas = resolvido
    assert "TURNO 1: AINDA NÃO" in saidas["extra-5"]
    assert "sem os pesos" in saidas["extra-5"] and "Pista:" in saidas["extra-5"]
    quebra, vazia = saidas["extra-6"].split("---")
    assert "IndexError" in quebra and "AINDA NÃO" in quebra
    assert "ainda não devolve nada" in vazia
    assert "desvio padrão populacional" in saidas["extra-7"] and "ddof=1" in saidas["extra-7"]
    media, par = saidas["extra-8"].split("---")
    assert "falta multiplicar por 252" in media
    assert "dois números" in par
    for texto in saidas.values():
        assert "zip(pesos" not in texto and "np.dot" not in texto


def test_carteira_invalida_nao_levanta_excecao(resolvido):
    _, saidas = resolvido
    assert saidas["extra-9"].count("AINDA NÃO") == 2
    assert "NAOEXISTE3" in saidas["extra-9"]


def test_simulador_py_gravado_importa_e_passa_no_aceite_dos_turnos_1_e_2(resolvido, tmp_path):
    pasta, saidas = resolvido
    gravado = pasta / "notebooks" / "simulador.py"
    assert "simulador.py gravado" in saidas["aula04-16"]
    assert gravado.exists()
    destino = tmp_path / "kit"
    shutil.copytree(KIT, destino, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copy(gravado, destino / "simulador.py")
    for turno in ("1", "2"):
        r = subprocess.run([sys.executable, "conferir.py", turno], cwd=destino,
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stdout + r.stderr
        assert "TURNO %s: OK" % turno in r.stdout
    r = subprocess.run([sys.executable, "conferir.py", "3"], cwd=destino,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1 and "Traceback" not in r.stdout + r.stderr
