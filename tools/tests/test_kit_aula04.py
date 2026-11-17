"""Kit do simulador da Aula 04 (exemplos/aula04-simulador) e o zip de materiais/.

Tudo roda em cópia temporária do kit: a pasta versionada nunca é alterada.
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import empacotar_kit_aula04 as pacote  # noqa: E402

KIT = os.path.join(RAIZ, "exemplos", "aula04-simulador")
REFERENCIA = os.path.join(RAIZ, "tools", "simulador_referencia.py")
ESPERADOS = sorted([
    "AGENTS.md", "CLAUDE.md", "README.md", "SPEC.md", "checar_ambiente.py", "conferir.py",
    "requirements.txt", "simulador.py", "dados/precos.csv", "dados/rf.txt",
    "docs/adrs/ADR-001-janela-dos-dados.md", "docs/adrs/ADR-002-sorteio-dos-pesos.md",
    "tests/test_turno1.py", "tests/test_turno2.py", "tests/test_turno3.py",
    "tests/test_turno4.py", "tests/test_turno5.py"])


def _ler(*partes):
    with open(os.path.join(KIT, *partes), encoding="utf-8") as fh:
        return fh.read()


def _copia(destino, simulador=None):
    shutil.copytree(KIT, destino, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    if simulador is not None:
        with open(os.path.join(destino, "simulador.py"), "w", encoding="utf-8") as fh:
            fh.write(simulador)
    return destino


def _rodar(pasta, *argumentos):
    return subprocess.run([sys.executable, *argumentos], cwd=pasta, capture_output=True,
                          text=True, encoding="utf-8")


def _referencia():
    with open(REFERENCIA, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def kit_resolvido(tmp_path_factory):
    return _copia(tmp_path_factory.mktemp("resolvido") / "kit", _referencia())


@pytest.fixture(scope="module")
def kit_original(tmp_path_factory):
    return _copia(tmp_path_factory.mktemp("original") / "kit")


# --- conteúdo -------------------------------------------------------------------

def test_kit_tem_exatamente_os_arquivos_previstos():
    assert pacote.arquivos_do_kit() == ESPERADOS


def test_zip_tem_exatamente_os_arquivos_da_pasta_e_esta_em_dia():
    with zipfile.ZipFile(pacote.ZIP) as z:
        nomes = z.namelist()
        assert z.testzip() is None
    assert nomes == ["aula04-simulador/" + nome for nome in ESPERADOS]
    assert not any("__pycache__" in nome or nome.endswith(".pyc") for nome in nomes)
    assert pacote.conteudo_do_zip() == pacote.conteudo_esperado()
    assert pacote.em_dia()


def test_empacotar_e_deterministico_e_ignora_pycache(tmp_path):
    copia = _copia(tmp_path / "kit")
    os.makedirs(copia / "__pycache__")
    (copia / "__pycache__" / "simulador.cpython-311.pyc").write_bytes(b"x")
    (copia / ".DS_Store").write_bytes(b"x")
    a, b = tmp_path / "a.zip", tmp_path / "b.zip"
    pacote.empacotar(str(copia), str(a))
    os.utime(copia / "SPEC.md", (0, 0))
    pacote.empacotar(str(copia), str(b))
    assert a.read_bytes() == b.read_bytes()
    with zipfile.ZipFile(a) as z:
        assert z.namelist() == ["aula04-simulador/" + nome for nome in ESPERADOS]
        assert {info.date_time for info in z.infolist()} == {pacote.DATA_FIXA}
    (copia / "SPEC.md").write_text("mudou", encoding="utf-8")
    assert not pacote.em_dia(str(copia), str(a))


def test_instrucoes_do_agente_sao_iguais_nos_dois_nomes_e_protegem_o_aceite():
    agents = _ler("AGENTS.md")
    assert agents == _ler("CLAUDE.md")
    assert "Nunca edite `conferir.py`" in agents
    assert "Nunca apague, pule, comente ou enfraqueça um teste de `tests/`" in agents
    for trecho in ("SPEC.md", "python -m pytest tests -q", "python conferir.py <N>",
                   "apenas a função do turno pedido", "resumo de três linhas",
                   "não baixe dados", "português do Brasil"):
        assert trecho in agents, trecho


def test_nenhum_arquivo_python_do_kit_acessa_a_rede():
    proibido = re.compile(r"^\s*(?:import|from)\s+(urllib|requests|yfinance|socket|http)\b", re.M)
    for nome in ESPERADOS:
        if nome.endswith(".py"):
            assert not proibido.search(_ler(*nome.split("/"))), nome


def test_conferir_usa_so_biblioteca_padrao_numpy_e_pandas():
    importados = set(re.findall(r"^\s*(?:import|from)\s+(\w+)", _ler("conferir.py"), re.M))
    assert importados == {"importlib", "os", "sys", "time", "numpy", "pandas"}


def test_spec_traz_cinco_campos_por_turno_e_deixa_os_turnos_4_e_5_em_branco():
    secoes = re.split(r"^## Turno ", _ler("SPEC.md"), flags=re.M)[1:]
    assert len(secoes) == 5
    campos = ("**Função:**", "**Entrada:**", "**Saída:**", "**Casos de borda:**",
              "**Critério de aceite:**")
    for secao in secoes:
        for campo in campos:
            assert secao.count(campo) == 1, campo
    for secao, funcao in zip(secoes, ("retorno_do_dia(pesos, retornos_do_dia)",
                                      "metricas(pesos, retornos)", "sortear_pesos(k, rng)",
                                      "simular(retornos, n, semente, rf)",
                                      "posicionar(pesos, retornos, rf)")):
        assert funcao in secao

    def preenchido(secao, campo):
        return secao.split(campo)[1].split("**")[0].strip() != ""

    for secao in secoes[:3]:
        assert all(preenchido(secao, campo) for campo in campos)
    for secao in secoes[3:]:
        assert not any(preenchido(secao, campo) for campo in campos[1:])
    assert "10.000 simulações em\nmenos de 10 segundos, com 2 a 20 ativos" in secoes[4]


def test_simulador_do_kit_traz_cinco_funcoes_vazias_e_a_reserva_comentada():
    fonte = _ler("simulador.py")
    for assinatura in ("def retorno_do_dia(pesos, retornos_do_dia):", "def metricas(pesos, retornos):",
                       "def sortear_pesos(k, rng):", "def simular(retornos, n, semente, rf):",
                       "def posicionar(pesos, retornos, rf):"):
        assert re.search(r"^" + re.escape(assinatura), fonte, re.M), assinatura
    assert fonte.count("raise NotImplementedError") == 5
    assert fonte.count("Só descomente se o professor liberar") == 2
    assert "# def retorno_do_dia(pesos, retornos_do_dia):" in fonte
    assert "# def metricas(pesos, retornos):" in fonte
    sem_comentario = "\n".join(l for l in fonte.splitlines() if not l.lstrip().startswith("#"))
    assert "return" not in re.sub(r'""".*?"""', "", sem_comentario, flags=re.S)


def test_reserva_comentada_passa_nos_turnos_1_e_2_quando_liberada(tmp_path):
    fonte = _ler("simulador.py")
    for nome in ("retorno_do_dia", "metricas"):
        vazia = re.search(r"^def %s\(.*?\n    raise NotImplementedError\(.*?\)\n" % nome,
                          fonte, re.M | re.S).group(0)
        fonte = fonte.replace(vazia, "")
    fonte = re.sub(r"^# (def |    )", r"\1", fonte, flags=re.M)
    kit = _copia(tmp_path / "kit", fonte)
    for turno in ("1", "2"):
        r = _rodar(kit, "conferir.py", turno)
        assert r.returncode == 0 and "TURNO %s: OK" % turno in r.stdout, r.stdout + r.stderr


def test_cada_arquivo_de_teste_tem_um_exemplo_completo_e_um_assert_em_branco():
    for n in range(1, 6):
        fonte = _ler("tests", "test_turno%d.py" % n)
        assert len(re.findall(r"^def test_exemplo_", fonte, re.M)) == 1
        assert len(re.findall(r"^def test_da_dupla_", fonte, re.M)) == 1
        da_dupla = fonte.split("def test_da_dupla_")[1]
        assert "# ESCREVA AQUI: afirme que" in da_dupla
        assert len(re.findall(r"^    assert ", da_dupla, re.M)) == 1
        assert 'assert False, "escreva o assert deste teste e apague esta linha"' in da_dupla
        assert 'os.path.join(PASTA, "dados", "precos.csv")' in fonte
        assert "os.path.abspath(__file__)" in fonte


def test_adrs_de_exemplo_tem_a_estrutura_e_o_aviso():
    for nome, trechos in (
            ("ADR-001-janela-dos-dados.md", ("13/11/2026", "janela comum", "9 pregões", "252 pregões")),
            ("ADR-002-sorteio-dos-pesos.md", ("uniforme normalizado", "perto de pesos iguais",
                                              "concentrada em um único ativo"))):
        adr = _ler("docs", "adrs", nome)
        assert "Exemplo do professor: a ADR do seu A3 precisa tratar de uma decisão sua." in adr
        for parte in ("**Data:**", "**Status:**", "**Decisores:**", "## Contexto", "## Decisão",
                      "## Motivações", "## Riscos conhecidos", "## Consequências"):
            assert parte in adr, parte
        for trecho in trechos:
            assert trecho in adr, trecho


def test_texto_do_kit_sem_travessao_e_requirements_com_os_quatro_pacotes():
    for nome in ESPERADOS:
        if not nome.startswith("dados/"):
            assert chr(0x2014) not in _ler(*nome.split("/")), nome
    assert _ler("requirements.txt").split() == ["numpy", "pandas", "matplotlib", "pytest"]


def test_readme_diz_o_que_a_dupla_faz_e_entrega():
    readme = _ler("README.md")
    for trecho in ("O que a dupla entrega", "python checar_ambiente.py", "escrita no Colab",
                   "python conferir.py 3", "Implemente o turno 3 deste kit", "AGENTS.md"):
        assert trecho in readme, trecho


# --- comportamento ----------------------------------------------------------------

def test_com_a_referencia_o_conferir_passa_nos_cinco_turnos(kit_resolvido):
    r = _rodar(kit_resolvido, "conferir.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split("\n")[:5] == ["TURNO %d: OK" % n for n in range(1, 6)]
    for n in range(1, 6):
        um = _rodar(kit_resolvido, "conferir.py", str(n))
        assert um.returncode == 0 and um.stdout.strip() == "TURNO %d: OK" % n


def test_com_a_referencia_os_testes_de_exemplo_passam(kit_resolvido):
    r = _rodar(kit_resolvido, "-m", "pytest", "tests", "-q", "-k", "exemplo",
               "-p", "no:cacheprovider")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "5 passed, 5 deselected" in r.stdout


def test_teste_da_dupla_falha_ate_o_assert_ser_escrito(kit_resolvido):
    r = _rodar(kit_resolvido, "-m", "pytest", "tests", "-q", "-k", "da_dupla",
               "-p", "no:cacheprovider")
    assert r.returncode == 1
    assert "5 failed, 5 deselected" in r.stdout
    assert "escreva o assert deste teste" in r.stdout


def test_com_o_simulador_original_o_conferir_falha_nos_cinco_sem_traceback(kit_original):
    r = _rodar(kit_original, "conferir.py")
    assert r.returncode == 1
    assert "Traceback" not in r.stdout + r.stderr and r.stderr == ""
    for n in range(1, 6):
        assert "TURNO %d: AINDA NÃO" % n in r.stdout
        um = _rodar(kit_original, "conferir.py", str(n))
        assert um.returncode == 1 and "ainda não foi implementada" in um.stdout
        assert "Traceback" not in um.stdout + um.stderr
    assert "OK" not in r.stdout


def test_argumento_invalido_mostra_o_uso(kit_original):
    r = _rodar(kit_original, "conferir.py", "9")
    assert r.returncode == 2 and "Uso: python conferir.py" in r.stdout


def test_checar_ambiente_aprova_este_ambiente_e_acusa_dado_ausente(kit_original, tmp_path):
    r = _rodar(kit_original, "checar_ambiente.py")
    assert r.returncode == 0 and "AMBIENTE: OK" in r.stdout
    for pacote_ in ("numpy", "pandas", "matplotlib", "pytest"):
        assert "OK     %s" % pacote_ in r.stdout
    sem_dado = _copia(tmp_path / "kit")
    os.remove(sem_dado / "dados" / "rf.txt")
    r = _rodar(sem_dado, "checar_ambiente.py")
    assert r.returncode == 1 and "FALTA  dados/rf.txt" in r.stdout


def _com_erro(tmp_path, certo, errado):
    fonte = _referencia()
    assert certo in fonte
    return _copia(tmp_path / "kit", fonte.replace(certo, errado))


def test_pesos_que_nao_somam_um_sao_reprovados_com_o_motivo(tmp_path):
    kit = _com_erro(tmp_path, "return bruto / bruto.sum()", "return bruto")
    r = _rodar(kit, "conferir.py", "3")
    assert r.returncode == 1 and "TURNO 3: AINDA NÃO" in r.stdout
    assert "precisam somar 1" in r.stdout and "Traceback" not in r.stdout + r.stderr


def test_simular_que_ignora_a_semente_e_reprovado_com_o_motivo(tmp_path):
    kit = _com_erro(tmp_path, "rng = np.random.default_rng(semente)", "rng = np.random.default_rng()")
    r = _rodar(kit, "conferir.py", "4")
    assert r.returncode == 1 and "TURNO 4: AINDA NÃO" in r.stdout
    assert "mesma semente devolveram tabelas diferentes" in r.stdout


def test_semente_fixa_no_codigo_e_reprovada(tmp_path):
    kit = _com_erro(tmp_path, "rng = np.random.default_rng(semente)", "rng = np.random.default_rng(1)")
    r = _rodar(kit, "conferir.py", "4")
    assert r.returncode == 1 and "As sementes 7 e 8 devolveram a mesma tabela" in r.stdout


def test_sorteio_que_ignora_o_gerador_e_reprovado(tmp_path):
    kit = _com_erro(tmp_path, "bruto = rng.random(k)", "bruto = np.ones(k)")
    r = _rodar(kit, "conferir.py", "3")
    assert r.returncode == 1 and "argumento rng" in r.stdout


def test_risco_com_desvio_populacional_e_reprovado_no_turno_2(tmp_path):
    kit = _com_erro(tmp_path, "serie.std(ddof=1)", "serie.std(ddof=0)")
    r = _rodar(kit, "conferir.py", "2")
    assert r.returncode == 1 and "desvio padrão populacional" in r.stdout


def test_erro_de_sintaxe_no_simulador_nao_gera_traceback(tmp_path):
    kit = _copia(tmp_path / "kit", "def retorno_do_dia(:\n")
    r = _rodar(kit, "conferir.py")
    assert r.returncode == 1 and "simulador.py não pôde ser carregado" in r.stdout
    assert "Traceback" not in r.stdout + r.stderr


def test_agente_que_enfraquece_tests_nao_muda_o_resultado_do_conferir(tmp_path):
    """Review Focus 5: o aceite do professor não depende de tests/ nem do pytest."""
    kit = _copia(tmp_path / "kit")
    for n in range(1, 6):
        (kit / "tests" / ("test_turno%d.py" % n)).write_text("def test_ok():\n    assert True\n",
                                                            encoding="utf-8")
    (kit / "pytest.ini").write_text("[pytest]\naddopts = --co\n", encoding="utf-8")
    assert _rodar(kit, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider").returncode == 0
    r = _rodar(kit, "conferir.py")
    assert r.returncode == 1 and r.stdout.count("AINDA NÃO") == 5
