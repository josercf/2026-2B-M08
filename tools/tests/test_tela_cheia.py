"""Trava o botão de tela cheia dos decks: script em todos os decks, ícones no sprite e estilo no tema."""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula03_lab as m  # noqa: E402

RAIZ = m.RAIZ


def _ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return fh.read()


def test_todo_deck_carrega_o_botao_de_tela_cheia():
    decks = sorted(glob.glob(os.path.join(RAIZ, "aulas", "*.html")))
    assert decks
    for deck in decks:
        with open(deck, encoding="utf-8") as fh:
            assert "inteli-tela-cheia.js" in fh.read(), os.path.basename(deck)


def test_botao_usa_a_api_de_tela_cheia_e_os_icones_do_sprite():
    js = _ler("assets", "js", "inteli-tela-cheia.js")
    assert "requestFullscreen" in js and "exitFullscreen" in js and "fullscreenEnabled" in js
    sprite = _ler("assets", "icons", "icones.svg")
    for nome in re.findall(r"'(fullscreen(?:_exit)?)'", js):
        assert 'id="%s"' % nome in sprite, nome


def test_estilo_do_botao_no_tema_com_canto_reto_e_sem_impressao():
    css = _ler("assets", "css", "inteli-theme.css")
    bloco = css[css.index(".tela-cheia {"):]
    assert "border-radius: 0" in bloco.split("}")[0]
    assert "@media print { .tela-cheia { display: none; } }" in css
