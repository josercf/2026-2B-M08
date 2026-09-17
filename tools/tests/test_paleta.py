import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paleta import cor, tokens  # noqa: E402


def test_token_da_paleta_devolve_o_hex_oficial():
    assert cor("--inteli-roxo") == "#2e2640"
    assert cor("--inteli-coral") == "#ff4545"


def test_token_de_segmento_resolve_var():
    assert cor("--seg-primaria") == "#2e2640"
    assert cor("--seg-secundaria") == "#89cea5"
    assert cor("--seg-destaque") == "#ff4545"
    assert cor("--seg-base") == "#ffffff"


def test_cor_de_outro_segmento_nao_existe_no_acervo():
    with pytest.raises(KeyError):
        cor("--inteli-lilas")


def test_token_que_nao_e_cor_e_recusado():
    with pytest.raises(ValueError):
        cor("--escala-texto")


def test_referencia_circular_e_recusada(tmp_path):
    css = tmp_path / "brand.css"
    css.write_text(":root { --a: var(--b); --b: var(--a); }", encoding="utf-8")
    with pytest.raises(ValueError):
        tokens(str(css))


def test_comentario_nao_vira_token(tmp_path):
    css = tmp_path / "brand.css"
    css.write_text("/* --falso: #000000; */ :root { --verdadeiro: #ffffff; }", encoding="utf-8")
    assert tokens(str(css)) == {"--verdadeiro": "#ffffff"}
