"""Estrutura dos documentos de planejamento: seis aulas, sete blocos, amarrações."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TITULOS = {
    "01": "Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível",
    "02": "Dados Financeiros: Do Preço ao Retorno",
    "03": "Correlação, Covariância e o Argumento Matemático da Diversificação",
    "04": "Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz",
    "05": "Validação e Robustez do Modelo",
    "06": "Do Script ao Produto: React, FastAPI e Interpretação com LLM",
}
# As sete interações que a abertura do roteiro licencia, cada uma com as formas
# que a nomeiam no texto de um bloco. A abertura e este dicionário são conferidos
# um contra o outro, para a regra dos 15 minutos não poder ser afrouxada de um
# lado só.
INTERACOES = {
    "Peer Instruction": r"Peer Instruction",
    "prever e observar": r"prev[êe]\b|prevendo\b|prever\b",
    "pensar e compartilhar": r"pensar e compartilhar",
    "dupla no notebook": r"[Dd]upla no notebook",
    "escolha coletiva": r"[Ee]scolha coletiva",
    "quiz": r"[Qq]uiz",
    "pergunta disparada": r"[Pp]ergunta disparada",
}
BLOCOS_ESPERADOS = 42


def _ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return fh.read()


def _secoes_de_aula(texto):
    partes = re.split(r"^### Aula (\d\d) - ", texto, flags=re.M)
    return {partes[i]: partes[i + 1] for i in range(1, len(partes), 2)}


def _blocos_de_aula(secao):
    """Cada bloco da aula como (rótulo, texto do bloco até o bloco seguinte)."""
    corpo = secao.split("Metodologia ativa", 1)[1].split("Depois do encontro", 1)[0]
    partes = re.split(r"^\s+(Bloco \d) \(\d+ a \d+ min\)", corpo, flags=re.M)
    return [(partes[i], partes[i + 1]) for i in range(1, len(partes), 2)]


def _interacoes_declaradas_na_abertura(texto):
    abertura = " ".join(texto.split("### Aula", 1)[0].split())
    achado = re.search(r"interação nomeada \(([^)]+)\)", abertura)
    assert achado, "a abertura não declara a lista de interações nomeadas"
    return [nome.strip() for nome in re.split(r", | ou ", achado.group(1))]


def _autoestudos_por_semana():
    """Títulos oficiais de cada semana do arquivo derivado, por número de semana."""
    por_semana = {}
    for parte in re.split(r"^## ", _ler("docs", "autoestudos-por-semana.md"), flags=re.M):
        linhas = parte.splitlines()
        if not linhas:
            continue
        cabecalho = re.fullmatch(r"Semana (\d\d)", linhas[0].strip())
        if cabecalho:
            por_semana[cabecalho.group(1)] = set(re.findall(r"^- (.+)$", parte, flags=re.M))
    return por_semana


def _pendencias(*partes):
    """Número e texto de cada linha de pendência da tabela do documento."""
    return {achado.group(1): achado.group(2)
            for achado in re.finditer(r"^\| (P\d) \| (.+?) \|", _ler(*partes), flags=re.M)}


def test_planejamento_tem_as_seis_aulas_com_titulo_exato():
    secoes = _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md"))
    assert sorted(secoes) == sorted(TITULOS)
    for numero, titulo in TITULOS.items():
        assert titulo in secoes[numero].splitlines()[0], numero


def test_cada_aula_tem_sete_blocos_de_quinze_minutos():
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        blocos = re.findall(r"^\s+Bloco (\d) \((\d+) a (\d+) min\)", secao, flags=re.M)
        assert [int(b[0]) for b in blocos] == list(range(1, 8)), numero
        for _, inicio, fim in blocos:
            assert int(fim) - int(inicio) == 15, (numero, inicio, fim)


def test_cada_aula_declara_as_amarracoes():
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        for rotulo in ("Data:", "Entrega que alimenta:", "O que a aula anterior deixou pronto:",
                       "O que esta aula deixa pronto:", "Antes do encontro", "Daily da equipe",
                       "Metodologia ativa", "Depois do encontro"):
            assert rotulo in secao, (numero, rotulo)


def test_cada_bloco_fecha_em_interacao_nomeada():
    """A regra dos 15 minutos: bloco sem interação nomeada reprova o documento."""
    texto = _ler("PLANEJAMENTO_AULA_A_AULA.md")
    assert sorted(_interacoes_declaradas_na_abertura(texto)) == sorted(INTERACOES)
    medidos = 0
    for numero, secao in _secoes_de_aula(texto).items():
        for rotulo, corpo in _blocos_de_aula(secao):
            nomeadas = [nome for nome, forma in INTERACOES.items() if re.search(forma, corpo)]
            assert nomeadas, (numero, rotulo, " ".join(corpo.split())[:120])
            medidos += 1
    assert medidos == BLOCOS_ESPERADOS, medidos


def test_autoestudo_citado_no_planejamento_e_o_da_semana_da_aula():
    por_semana = _autoestudos_por_semana()
    assert sorted(por_semana) == ["02", "04", "05", "06", "08", "10"]
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        semana = re.match(r"Semana (\d+) - ", secao.splitlines()[0]).group(1).zfill(2)
        antes = secao.split("Antes do encontro", 1)[1].split("Daily da equipe", 1)[0]
        citados = re.findall(r"^\s+Autoestudo: (.+?) \(\d+ min\)$", antes, flags=re.M)
        assert len(citados) == 2, numero
        oficiais = por_semana[semana]
        assert len(oficiais) == 2, semana
        assert set(citados) == oficiais, (numero, semana, sorted(citados), sorted(oficiais))


def test_pendencias_batem_entre_o_plano_e_a_revisao():
    """Numeração e texto das pendências não podem divergir entre os documentos."""
    plano = _pendencias("PLANO_DE_ENSINO.md")
    revisao = _pendencias("docs", "revisao-planilha-2026-09-17.md")
    assert sorted(plano) == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    compartilhadas = sorted(set(plano) & set(revisao))
    assert compartilhadas == ["P4", "P5", "P6", "P7"]
    for numero in compartilhadas:
        assert plano[numero] == revisao[numero], numero
    citadas = set()
    for partes in (("PLANEJAMENTO_AULA_A_AULA.md",), ("PLANO_DE_ENSINO.md",),
                   ("docs", "revisao-planilha-2026-09-17.md")):
        citadas |= set(re.findall(r"\bP\d\b", _ler(*partes)))
    assert citadas, "nenhum documento cita pendência"
    assert citadas <= set(plano), sorted(citadas - set(plano))


def test_nenhum_documento_tem_travessao():
    for partes in (("PLANO_DE_ENSINO.md",), ("PLANEJAMENTO_AULA_A_AULA.md",),
                   ("docs", "autoestudos-por-semana.md"), ("docs", "revisao-planilha-2026-09-17.md")):
        assert chr(0x2014) not in _ler(*partes), partes
