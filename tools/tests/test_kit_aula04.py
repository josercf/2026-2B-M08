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
    "docs/adrs/ADR-003-restricoes-da-otimizacao.md",
    "tests/test_turno1.py", "tests/test_turno2.py", "tests/test_turno3.py",
    "tests/test_turno4.py", "tests/test_turno5.py", "tests/test_turno6.py"])
TURNOS = range(1, 7)


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
                   "não baixe dados", "português do Brasil", "seis turnos",
                   "## Turno 6: otimização de Markowitz", "scipy.optimize.minimize", "SLSQP",
                   "Nunca devolva a melhor carteira sorteada", "resultado.success",
                   "tratar a melhor carteira simulada como a carteira ótima"):
        assert trecho in agents, trecho


def test_nenhum_arquivo_python_do_kit_acessa_a_rede():
    proibido = re.compile(r"^\s*(?:import|from)\s+(urllib|requests|yfinance|socket|http)\b", re.M)
    for nome in ESPERADOS:
        if nome.endswith(".py"):
            assert not proibido.search(_ler(*nome.split("/"))), nome


def test_conferir_usa_so_biblioteca_padrao_numpy_e_pandas():
    importados = set(re.findall(r"^\s*(?:import|from)\s+(\w+)", _ler("conferir.py"), re.M))
    assert importados == {"importlib", "os", "sys", "time", "numpy", "pandas"}


def test_spec_traz_cinco_campos_por_turno_e_deixa_so_os_turnos_4_e_5_em_branco():
    secoes = re.split(r"^## Turno ", _ler("SPEC.md"), flags=re.M)[1:]
    assert len(secoes) == 6
    campos = ("**Função:**", "**Entrada:**", "**Saída:**", "**Casos de borda:**",
              "**Critério de aceite:**")
    for secao in secoes:
        for campo in campos:
            assert secao.count(campo) == 1, campo
    for secao, funcao in zip(secoes, ("retorno_do_dia(pesos, retornos_do_dia)",
                                      "metricas(pesos, retornos)", "sortear_pesos(k, rng)",
                                      "simular(retornos, n, semente, rf)",
                                      "posicionar(pesos, retornos, rf)",
                                      "variancia_minima(retornos)")):
        assert funcao in secao

    def preenchido(secao, campo):
        return secao.split(campo)[1].split("**")[0].strip() != ""

    for secao in secoes[:3]:
        assert all(preenchido(secao, campo) for campo in campos)
    for secao in secoes[3:5]:
        assert not any(preenchido(secao, campo) for campo in campos[1:])
    assert "10.000 simulações em\nmenos de 10 segundos, com 2 a 20 ativos" in secoes[4]
    turno6 = secoes[5]
    assert turno6.startswith("6 (depois do encontro)")
    assert all(preenchido(turno6, campo) for campo in campos)
    turno6 = " ".join(turno6.split())
    for trecho in ("`maximo_sharpe(retornos, rf)`", "`fronteira(retornos, pontos=50)`",
                   "`w_<ticker>`", "`retorno` e `risco`", "sem venda a descoberto",
                   "cada peso entre 0 e 1", "soma dos pesos igual a 1",
                   "`scipy.optimize.minimize` com o método SLSQP", "partindo de pesos iguais",
                   "igualmente espaçados", "ordem crescente", "`ValueError`", "`RuntimeError`",
                   "`python conferir.py 6` imprime `TURNO 6: OK`",
                   "ADR-003-restricoes-da-otimizacao.md"):
        assert trecho in turno6, trecho


def test_simulador_do_kit_traz_as_funcoes_vazias_dos_seis_turnos_e_a_reserva_comentada():
    fonte = _ler("simulador.py")
    for assinatura in ("def retorno_do_dia(pesos, retornos_do_dia):", "def metricas(pesos, retornos):",
                       "def sortear_pesos(k, rng):", "def simular(retornos, n, semente, rf):",
                       "def posicionar(pesos, retornos, rf):",
                       "def variancia_minima(retornos):", "def maximo_sharpe(retornos, rf):",
                       "def fronteira(retornos, pontos=50):"):
        assert re.search(r"^" + re.escape(assinatura), fonte, re.M), assinatura
    assert fonte.count("raise NotImplementedError") == 8
    # O SciPy só entra no turno 6: o arquivo do kit carrega sem ele durante o encontro.
    assert not re.search(r"^\s*(?:import|from)\s+scipy", fonte, re.M)
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
    for n in TURNOS:
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
                                              "concentrada em um único ativo")),
            ("ADR-003-restricoes-da-otimizacao.md", (
                "sem venda a descoberto", "cada peso entre\n0 e 1", "Não há teto de peso por ativo",
                "concentrar o peso em poucos ativos", "converge para o passado da janela"))):
        adr = _ler("docs", "adrs", nome)
        # As duas primeiras sustentam os turnos do A3; a terceira, o turno 6, base do A4.
        artefato = "A4" if nome.startswith("ADR-003") else "A3"
        assert "Exemplo do professor: a ADR do seu %s precisa tratar de uma decisão sua." % artefato in adr
        for parte in ("**Data:**", "**Status:**", "**Decisores:**", "## Contexto", "## Decisão",
                      "## Motivações", "## Riscos conhecidos", "## Consequências"):
            assert parte in adr, parte
        for trecho in trechos:
            assert trecho in adr, trecho


def test_texto_do_kit_sem_travessao_e_requirements_com_os_cinco_pacotes():
    for nome in ESPERADOS:
        if not nome.startswith("dados/"):
            assert chr(0x2014) not in _ler(*nome.split("/")), nome
    assert _ler("requirements.txt").split() == ["numpy", "pandas", "matplotlib", "pytest", "scipy"]


def test_readme_diz_o_que_a_dupla_faz_e_entrega():
    readme = _ler("README.md")
    for trecho in ("O que a dupla entrega", "python checar_ambiente.py", "escrita no Colab",
                   "python conferir.py 3", "Implemente o turno 3 deste kit", "AGENTS.md"):
        assert trecho in readme, trecho


def test_readme_descreve_o_turno_6_a_entrega_e_a_ligacao_com_o_a4():
    readme = _ler("README.md")
    assert "## Depois do encontro: turno 6, a otimização de Markowitz" in readme
    secao = readme.split("## Depois do encontro: turno 6, a otimização de Markowitz")[1]
    secao = secao.split("\n## Comandos")[0]
    for trecho in ("O que a dupla faz", "O que a dupla entrega", "Implemente o turno 6 deste kit",
                   "python conferir.py 6", "tests/test_turno6.py", "A4", "grafico_fronteira.py",
                   "fronteira desenhada sobre a nuvem", "variância mínima", "máximo Sharpe",
                   "carteira do Solver da aula de Negócios", "melhor carteira sorteada",
                   "ADR-003-restricoes-da-otimizacao.md"):
        assert trecho in secao, trecho


def _blocos_python(texto):
    return re.findall(r"^```python\n(.*?)^```\n+Saída:\n+```\n(.*?)^```", texto, re.M | re.S)


def test_bloco_de_ferramentas_ensina_o_minimize_com_exemplos_que_rodam(tmp_path):
    readme = _ler("README.md")
    assert "### Ferramentas do Python para este turno" in readme
    bloco = readme.split("### Ferramentas do Python para este turno")[1].split("\n## ")[0]
    for trecho in ("scipy.optimize.minimize", "`bounds`", "`constraints`", "ponto inicial",
                   "função objetivo", "`resultado.success`", "`resultado.x`", '"ftol"',
                   "lambda x, a=alvo:"):
        assert trecho in bloco, trecho
    # O exemplo trata de outro problema: nada de carteira, Sharpe ou covariância resolvidos.
    for proibido in ("sharpe", "cov(", "retornos", "pesos"):
        assert not any(proibido in codigo for codigo, _ in _blocos_python(bloco)), proibido
    exemplos = _blocos_python(bloco)
    assert len(exemplos) == 2
    for posicao, (codigo, saida) in enumerate(exemplos):
        arquivo = tmp_path / ("exemplo%d.py" % posicao)
        arquivo.write_text(codigo, encoding="utf-8")
        r = _rodar(tmp_path, str(arquivo))
        assert r.returncode == 0, r.stderr
        assert r.stdout == saida, r.stdout


# --- comportamento ----------------------------------------------------------------

def test_com_a_referencia_o_conferir_passa_nos_seis_turnos(kit_resolvido):
    r = _rodar(kit_resolvido, "conferir.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split("\n")[:6] == ["TURNO %d: OK" % n for n in TURNOS]
    for n in TURNOS:
        um = _rodar(kit_resolvido, "conferir.py", str(n))
        assert um.returncode == 0 and um.stdout.strip() == "TURNO %d: OK" % n


def test_com_a_referencia_os_testes_de_exemplo_passam(kit_resolvido):
    r = _rodar(kit_resolvido, "-m", "pytest", "tests", "-q", "-k", "exemplo",
               "-p", "no:cacheprovider")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "6 passed, 6 deselected" in r.stdout


def test_teste_da_dupla_falha_ate_o_assert_ser_escrito(kit_resolvido):
    r = _rodar(kit_resolvido, "-m", "pytest", "tests", "-q", "-k", "da_dupla",
               "-p", "no:cacheprovider")
    assert r.returncode == 1
    assert "6 failed, 6 deselected" in r.stdout
    assert "escreva o assert deste teste" in r.stdout


def test_com_o_simulador_original_o_conferir_falha_nos_seis_sem_traceback(kit_original):
    r = _rodar(kit_original, "conferir.py")
    assert r.returncode == 1
    assert "Traceback" not in r.stdout + r.stderr and r.stderr == ""
    for n in TURNOS:
        assert "TURNO %d: AINDA NÃO" % n in r.stdout
        um = _rodar(kit_original, "conferir.py", str(n))
        assert um.returncode == 1 and "ainda não foi implementada" in um.stdout
        assert "Traceback" not in um.stdout + um.stderr
    assert "OK" not in r.stdout


def test_argumento_invalido_mostra_o_uso(kit_original):
    r = _rodar(kit_original, "conferir.py", "9")
    assert r.returncode == 2 and "Uso: python conferir.py" in r.stdout
    assert "turno de 1 a 6" in r.stdout


def test_checar_ambiente_aprova_este_ambiente_e_acusa_dado_ausente(kit_original, tmp_path):
    r = _rodar(kit_original, "checar_ambiente.py")
    assert r.returncode == 0 and "AMBIENTE: OK" in r.stdout
    assert r.stdout.strip().endswith("AMBIENTE: OK")
    for pacote_ in ("numpy", "pandas", "matplotlib", "pytest", "scipy"):
        assert "OK     %s" % pacote_ in r.stdout
    sem_dado = _copia(tmp_path / "kit")
    os.remove(sem_dado / "dados" / "rf.txt")
    r = _rodar(sem_dado, "checar_ambiente.py")
    assert r.returncode == 1 and "FALTA  dados/rf.txt" in r.stdout


def test_sem_scipy_o_ambiente_serve_para_os_turnos_1_a_5_e_avisa_do_turno_6(tmp_path):
    """Quem instalou o kit antes do turno 6 existir não fica barrado no encontro."""
    kit = _copia(tmp_path / "kit", _referencia().split("# --- Turno 6")[0].replace(
        "from scipy.optimize import minimize\n", ""))
    (kit / "scipy.py").write_text('raise ImportError("sem scipy")\n', encoding="utf-8")
    r = _rodar(kit, "checar_ambiente.py")
    assert r.returncode == 0, r.stdout
    assert "FALTA  scipy (usado só no turno 6)" in r.stdout
    assert "AMBIENTE: OK para os turnos 1 a 5" in r.stdout
    assert "-m pip install scipy" in r.stdout
    for turno in range(1, 6):
        um = _rodar(kit, "conferir.py", str(turno))
        assert um.returncode == 0 and "TURNO %d: OK" % turno in um.stdout, um.stdout + um.stderr
    seis = _rodar(kit, "conferir.py", "6")
    assert seis.returncode == 1 and "simulador.py não tem a função variancia_minima" in seis.stdout
    assert "Traceback" not in seis.stdout + seis.stderr


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
    for n in TURNOS:
        (kit / "tests" / ("test_turno%d.py" % n)).write_text("def test_ok():\n    assert True\n",
                                                            encoding="utf-8")
    (kit / "pytest.ini").write_text("[pytest]\naddopts = --co\n", encoding="utf-8")
    assert _rodar(kit, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider").returncode == 0
    r = _rodar(kit, "conferir.py")
    assert r.returncode == 1 and r.stdout.count("AINDA NÃO") == 6


# --- turno 6: implementações erradas típicas ------------------------------------

def _turno6(tmp_path, trocas=(), acrescimo=""):
    """Roda conferir.py 6 sobre a referência com trechos trocados ou funções sobrepostas."""
    fonte = _referencia()
    for certo, errado in trocas:
        assert fonte.count(certo) == 1, certo
        fonte = fonte.replace(certo, errado)
    r = _rodar(_copia(tmp_path / "kit", fonte + acrescimo), "conferir.py", "6")
    assert r.returncode == 1 and "TURNO 6: AINDA NÃO" in r.stdout, r.stdout + r.stderr
    assert "Traceback" not in r.stdout + r.stderr
    return r.stdout


MELHOR_SORTEADA = '''

def variancia_minima(retornos):
    tabela = simular(retornos, %(n)d, 42, 0.1)
    return tabela.iloc[tabela["risco"].argmin(), :retornos.shape[1]].to_numpy()


def maximo_sharpe(retornos, rf):
    tabela = simular(retornos, %(n)d, 42, rf)
    return tabela.iloc[tabela["sharpe"].argmax(), :retornos.shape[1]].to_numpy()
'''

FRONTEIRA_ERRADA = '''

def _tabela_da_fronteira(retornos, linhas):
    _, media, cov = _momentos(retornos)
    linhas = np.array(linhas)
    saida = pd.DataFrame(linhas, columns=[f"w_{c}" for c in retornos.columns])
    saida["retorno"] = linhas @ media
    saida["risco"] = np.sqrt(np.einsum("ij,jk,ik->i", linhas, cov, linhas))
    return saida


def fronteira(retornos, pontos=50):
    if pontos < 2:
        raise ValueError("a fronteira precisa de pelo menos dois pontos")
    _, media, cov = _momentos(retornos)
    minima = variancia_minima(retornos)
    alvos = np.linspace(minima @ media, media.max(), pontos)
%s
'''

LAMBDA_NO_LACO = FRONTEIRA_ERRADA % '''    restricoes = []
    for alvo in alvos:
        restricoes.append([{"type": "eq", "fun": lambda w: w @ media - alvo}])
    return _tabela_da_fronteira(retornos, [
        _otimizar(lambda w: w @ cov @ w, len(media), restricao) for restricao in restricoes])'''

RETA_NOS_PESOS = FRONTEIRA_ERRADA % '''    ultimo = np.eye(len(media))[media.argmax()]
    return _tabela_da_fronteira(retornos, [
        (1 - t) * minima + t * ultimo for t in np.linspace(0, 1, pontos)])'''

NUVEM_NO_LUGAR_DA_FRONTEIRA = FRONTEIRA_ERRADA % '''    nuvem = simular(retornos, 10_000, 42, 0.1)
    linhas = []
    for alvo in alvos:
        acima = nuvem[nuvem["retorno"] >= alvo]
        linhas.append(acima.iloc[acima["risco"].argmin(), :len(media)].to_numpy()
                      if len(acima) else np.eye(len(media))[media.argmax()])
    saida = _tabela_da_fronteira(retornos, linhas)
    saida["retorno"] = alvos
    return saida'''


def test_otimizacao_que_devolve_pesos_iguais_e_reprovada_com_o_motivo(tmp_path):
    saida = _turno6(tmp_path, [("pesos = np.clip(resultado.x, 0, 1)", "pesos = np.clip(x0, 0, 1)")])
    assert "variancia_minima com 2 ativos devolveu pesos iguais (50,0% em cada ativo)" in saida
    assert "ponto inicial" in saida and "tem risco anual de" in saida
    assert "atributo x do resultado" in saida


def test_otimizacao_sem_a_restricao_de_soma_um_e_reprovada_com_o_motivo(tmp_path):
    saida = _turno6(tmp_path, [
        ('restricoes = [{"type": "eq", "fun": lambda w: w.sum() - 1}] + list(restricoes)',
         "restricoes = list(restricoes)"),
        ("return pesos / pesos.sum()", "return pesos")])
    assert "devolveu pesos que somam" in saida and "precisam somar 1" in saida
    assert 'restrição de igualdade (type "eq")' in saida


def test_otimizacao_sem_limites_e_reprovada_por_peso_negativo(tmp_path):
    saida = _turno6(tmp_path, [
        ('bounds=[(0, 1)] * k,', "bounds=None,"),
        ("pesos = np.clip(resultado.x, 0, 1)", "pesos = resultado.x")])
    assert "devolveu peso fora do intervalo de 0 a 1" in saida and "bounds" in saida


@pytest.mark.parametrize("n", [10_000, 200_000])
def test_melhor_carteira_sorteada_no_lugar_da_otima_e_reprovada_com_o_motivo(tmp_path, n):
    """O erro que o barema do A3 chama de tratar a melhor carteira simulada como a ótima."""
    saida = _turno6(tmp_path, acrescimo=MELHOR_SORTEADA % {"n": n})
    for funcao in ("variancia_minima", "maximo_sharpe"):
        assert "%s com 5 ativos não devolveu a carteira ótima" % funcao in saida
    assert "devolver a melhor carteira sorteada da tabela de simular no lugar de otimizar" in saida
    assert "tem Sharpe de" in saida and "tem risco anual de" in saida


def test_tolerancia_padrao_com_variancia_diaria_e_reprovada_com_a_pista_do_ftol(tmp_path):
    saida = _turno6(tmp_path, [
        ("tabela.cov().to_numpy() * PREGOES_ANO)", "tabela.cov().to_numpy())"),
        ('options={"ftol": TOLERANCIA, "maxiter": 500})', "options={})")])
    assert "devolveu pesos iguais" in saida and '"ftol"' in saida and "variância anual" in saida


def test_fronteira_com_lambda_que_enxerga_o_ultimo_alvo_e_reprovada_com_o_motivo(tmp_path):
    saida = _turno6(tmp_path, acrescimo=LAMBDA_NO_LACO)
    assert "Todas as linhas de fronteira(retornos) têm o mesmo retorno" in saida
    assert "lambda dentro do laço" in saida and "README" in saida


def test_fronteira_que_nao_minimiza_o_risco_de_cada_alvo_e_reprovada_com_o_motivo(tmp_path):
    saida = _turno6(tmp_path, acrescimo=RETA_NOS_PESOS)
    assert re.search(r"\d+ dos 50 pontos de fronteira\(retornos\) não estão na fronteira", saida)
    assert "rende pelo menos esse retorno com risco de" in saida
    assert "uma otimização por alvo" in saida


def test_fronteira_montada_com_carteiras_sorteadas_e_reprovada(tmp_path):
    saida = _turno6(tmp_path, acrescimo=NUVEM_NO_LUGAR_DA_FRONTEIRA)
    assert "os pesos não atingiram o alvo" in saida


def test_fronteira_com_numero_errado_de_pontos_ou_sem_recusar_um_ponto_e_reprovada(tmp_path):
    saida = _turno6(tmp_path, [("alvos = np.linspace(x0 @ media, media.max(), pontos)",
                                "alvos = np.linspace(x0 @ media, media.max(), 50)")])
    assert "fronteira(retornos, 12) devolveu 50 linhas" in saida
    (tmp_path / "outro").mkdir()
    saida = _turno6(tmp_path / "outro", [("    if pontos < 2:\n        raise ValueError("
                                          '"a fronteira precisa de pelo menos dois pontos")\n', "")])
    assert "Caso de borda pontos = 1" in saida


def test_solucao_com_a_tolerancia_padrao_do_slsqp_sobre_a_variancia_anual_passa(tmp_path):
    """O aceite não exige o ftol da referência: a folga declarada cobre a tolerância padrão."""
    fonte = _referencia()
    certo = 'options={"ftol": TOLERANCIA, "maxiter": 500})'
    assert fonte.count(certo) == 1
    kit = _copia(tmp_path / "kit", fonte.replace(certo, "options={})"))
    r = _rodar(kit, "conferir.py", "6")
    assert r.returncode == 0 and r.stdout.strip() == "TURNO 6: OK", r.stdout + r.stderr


def test_conferir_o_turno_6_leva_menos_de_dez_segundos(kit_resolvido):
    import time
    inicio = time.perf_counter()
    r = _rodar(kit_resolvido, "conferir.py", "6")
    assert r.returncode == 0 and time.perf_counter() - inicio < 10
