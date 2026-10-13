"""Trava o deck da Aula 06 contra as medições, o plano de ensino e o roteiro.

Os números do deck são digitados no HTML, então este teste confere cada um
contra tools/medidas_aula06.py: se a API de exemplo ou dados/ mudarem, o deck
reprova aqui em vez de mostrar número velho na sala.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "aula06.html")


def _html():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _secoes():
    return re.findall(r"<section\b(.*?)</section>", _html(), flags=re.S)


def _texto(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def _br(valor):
    return ("%.2f" % valor).replace(".", ",")


def test_rodapes_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _html())]
    esperados = [i + 1 for i, s in enumerate(_secoes()) if "footer-page" in s]
    assert numeros == esperados


def test_sem_travessao_e_sem_emoji():
    html = _html()
    assert chr(0x2014) not in html
    assert not re.search("[\U0001F000-\U0001FAFF]", html)


def test_abre_com_resgate_da_aula_05_e_peer_instruction():
    secoes = _secoes()
    assert 'class="cover-slide"' in secoes[0]
    assert 'id="resgate"' in secoes[2]
    assert "teste fora da amostra" in _texto(secoes[2])
    assert 'class="quiz-slide" id="preparo"' in secoes[3]
    assert "Votar de novo" in _texto(secoes[3])


def test_peso_do_a5_e_review_vem_do_plano_de_ensino():
    with open(os.path.join(RAIZ, "PLANO_DE_ENSINO.md"), encoding="utf-8") as fh:
        plano = fh.read()
    linha = re.search(r"^\| A5 \| 5 \| [^|]+\| (\d+) \| review em (\d\d/\d\d/\d{4})", plano, re.M)
    peso, review = linha.groups()
    a5 = _texto([s for s in _secoes() if 'id="a5"' in s][0])
    assert "A5 vale %s pontos" % peso in a5
    assert review in a5


def test_sete_blocos_da_agenda_com_as_interacoes_do_roteiro():
    agenda = _texto([s for s in _secoes() if 'id="agenda"' in s][0])
    for trecho in ("Peer Instruction", "previsão do status no montador",
                   "que erro para um ticker que não existe", "dupla no notebook",
                   "escolha coletiva", "que número conferir por código", "quiz de três perguntas"):
        assert trecho in agenda, trecho


@pytest.fixture(scope="module")
def medidas():
    pytest.importorskip("fastapi")
    pytest.importorskip("scipy")
    import medidas_aula06 as m

    return m


def test_numeros_do_prompt_conferem_com_a_api(medidas):
    c = medidas.contexto()
    prompt = _html().split('id="prompt"')[1].split("</section>")[0]
    sharpe = c["maximo_sharpe"]
    for ticker, peso in sharpe["pesos_pct"].items():
        assert '"%s": %s' % (ticker, peso) in prompt
    assert '"retorno_anual_pct": %s' % sharpe["retorno_anual_pct"] in prompt
    assert '"volatilidade_anual_pct": %s' % sharpe["volatilidade_anual_pct"] in prompt
    assert '"sharpe": %s' % sharpe["sharpe"] in prompt
    assert '"taxa_livre_risco_pct": %s' % c["taxa_livre_risco_pct"] in prompt
    assert '"pregoes": %d' % c["pregoes"] in prompt
    assert '"inicio_janela": "%s"' % c["inicio_janela"] in prompt


def test_titulos_com_numero_conferem_com_as_medicoes(medidas):
    html = _texto(_html())
    r = medidas.resultado()
    sem = medidas.problemas_por_pedido(com_cache=False)
    com = medidas.problemas_por_pedido(com_cache=True)
    assert "O pedido volta com %d pares da fronteira" % len(r["fronteira"]) in html
    assert "O cache reduz %d problemas de otimização a %d" % (sum(sem), sum(com)) in html
    assert "cada pedido novo calcula %d carteiras" % sem[0] in html
    assert "Nove requisições" in html and len(medidas.requisicoes()) == 9
    assert len(set(medidas.status_por_caso().values())) == 4  # "quatro status"


def test_tabela_do_ativo_trocado_confere_com_o_verificador(medidas):
    _, erros = medidas.texto_com_erros()
    verificacao = medidas.verificacao_do_texto()
    trecho = _texto([s for s in _secoes() if 'id="ativo-trocado"' in s][0])
    nao = [v for v in verificacao if not v["confere"]]
    assert "acusa %d dos %d erros plantados" % (len(nao), len(erros)) in trecho
    passam = len(verificacao) - len(nao)
    assert "%d dos %d números passam na verificação de presença, e %d estão certos" % (
        passam, len(verificacao), passam - (len(erros) - len(nao))) in trecho
    for erro in erros:
        assert erro["trecho"] in trecho
    c = medidas.contexto()
    vale = [a for a in c["ativos"] if a["ticker"] == "VALE3"][0]
    assert "VALE3 tem %s" % _br(vale["correlacao_media"]) in trecho
    assert _br(c["maximo_sharpe"]["volatilidade_anual_pct"]) + "%" in trecho


def test_widgets_e_videos_declarados():
    html = _html()
    assert 'data-widget="montador-requisicao"' in html
    assert 'data-widget="verificador-numeros"' in html
    for nome in ("aula06-requisicao", "aula06-cache"):
        assert "../assets/video/%s.mp4" % nome in html
        assert "../assets/img/%s-poster.png" % nome in html


def test_json_dos_widgets_existe_e_e_valido():
    for nome in ("aula06-requisicoes.json", "aula06-verificador.json"):
        with open(os.path.join(RAIZ, "assets", "data", nome), encoding="utf-8") as fh:
            assert json.load(fh)


def test_404_e_422_aparecem_como_escolha_de_contrato():
    # Auditoria de 13/10/2026, C-15: o ticker vem no corpo do POST, então 422
    # também é defensável. O deck pede justificativa pelo contrato e não
    # apresenta o 404 como resposta universal.
    erros = _texto([s for s in _secoes() if 'id="erros"' in s][0])
    assert "por que 404 em vez de 422" not in erros
    assert "justifica pelo contrato" in erros
    assert "422 também é defensável" in erros and "SPEC.md" in erros


def test_checagem_de_numeros_nao_promete_verificacao_factual():
    # Auditoria de 13/10/2026, C-13: o algoritmo confere presença no JSON e
    # deixa passar número certo no ativo errado. Nenhum texto do deck pode
    # prometer verificação de cada número.
    html = _texto(_html())
    assert "verificação de cada número" not in html
    assert "checagem de presença de cada número" in html
    trocado = _texto([s for s in _secoes() if 'id="ativo-trocado"' in s][0])
    assert "sem conferir ativo, unidade nem período" in trocado
