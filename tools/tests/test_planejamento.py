"""Estrutura dos documentos de planejamento: seis aulas, sete blocos, amarrações."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TITULOS = {
    "01": "Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível",
    "02": "Dados Financeiros: Do Preço ao Retorno",
    "03": "Correlação, Covariância e o Argumento Matemático da Diversificação",
    "04": "Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz",
    "05": "Do Script ao Produto: API em FastAPI e Página Web",
    "06": "Validação, Robustez e Interpretação com LLM",
}


def _ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return fh.read()


def _secoes_de_aula(texto):
    partes = re.split(r"^### Aula (\d\d) - ", texto, flags=re.M)
    return {partes[i]: partes[i + 1] for i in range(1, len(partes), 2)}


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


def test_autoestudo_citado_no_planejamento_existe_no_arquivo_derivado():
    derivado = _ler("docs", "autoestudos-por-semana.md")
    oficiais = set(re.findall(r"^- (.+)$", derivado, flags=re.M))
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        antes = secao.split("Antes do encontro", 1)[1].split("Daily da equipe", 1)[0]
        citados = re.findall(r"^\s+Autoestudo: (.+?) \(\d+ min\)$", antes, flags=re.M)
        assert len(citados) == 2, numero
        for titulo in citados:
            assert titulo in oficiais, (numero, titulo)


def test_nenhum_documento_tem_travessao():
    for partes in (("PLANO_DE_ENSINO.md",), ("PLANEJAMENTO_AULA_A_AULA.md",),
                   ("docs", "autoestudos-por-semana.md"), ("docs", "revisao-planilha-2026-09-17.md")):
        assert chr(0x2014) not in _ler(*partes), partes
