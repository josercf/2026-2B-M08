"""O portal lista as seis instruções e só habilita botão de artefato que existe."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_BLOB = "https://github.com/josercf/2026-2B-M08/blob/main/"


def _portal():
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as fh:
        return fh.read()


def _cards(html):
    return dict(re.findall(r'<article class="card-aula" id="aula-(\d\d)">(.*?)</article>', html, re.S))


def test_portal_tem_as_seis_instrucoes_em_cinco_sprints():
    html = _portal()
    assert sorted(_cards(html)) == ["01", "02", "03", "04", "05", "06"]
    assert len(re.findall(r'<section class="sprint-block"', html)) == 5


def test_botao_habilitado_aponta_para_arquivo_existente_e_desabilitado_nao_tem_href():
    for numero, card in _cards(_portal()).items():
        botoes = re.findall(r"<a class=\"botao\"([^>]*)>", card)
        assert len(botoes) == 4, numero
        for atributos in botoes:
            href = re.search(r'href="([^"]+)"', atributos)
            if 'aria-disabled="true"' in atributos:
                assert href is None, (numero, atributos)
                continue
            alvo = href.group(1)
            if alvo.startswith(REPO_BLOB):
                alvo = alvo[len(REPO_BLOB):]
            assert os.path.isfile(os.path.join(RAIZ, alvo)), (numero, alvo)


def test_artefato_existente_tem_botao_habilitado():
    cards = _cards(_portal())
    for numero, card in cards.items():
        for pasta, extensao in (("aulas", "html"), ("materiais", "html"),
                                ("referencias", "html"), ("notebooks", "ipynb")):
            caminho = "%s/aula%s.%s" % (pasta, numero, extensao)
            if os.path.isfile(os.path.join(RAIZ, caminho)):
                assert caminho in card, (numero, caminho)
