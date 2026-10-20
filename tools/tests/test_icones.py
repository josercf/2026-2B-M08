"""Todo ícone do acervo sai do sprite Sharp do brand kit (ICO-01 e ICO-05).

A auditoria de 13/10/2026 (C-05) achou a fonte Material Symbols Outlined por
CDN. O tools/icones.py trocou os spans por <svg><use> e gerou o sprite; este
teste garante que nenhum nome referenciado fica sem símbolo, o que deixaria o
ícone vazio na tela sem nenhum erro no console.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import icones  # noqa: E402

RAIZ = icones.RAIZ


def _simbolos():
    with open(icones.SPRITE, encoding="utf-8") as fh:
        return set(re.findall(r'<symbol id="([a-z0-9_]+)"', fh.read()))


def test_todo_icone_das_paginas_existe_no_sprite():
    assert set(icones.nomes_usados()) - _simbolos() == set()


def test_icones_montados_por_js_existem_no_sprite_e_estao_declarados():
    usados = set()
    for nome in ("inteli-print.js", "inteli-cronometro.js", "inteli-nuvem.js"):
        with open(os.path.join(RAIZ, "assets", "js", nome), encoding="utf-8") as fh:
            usados.update(re.findall(r"(?:criarIcone|trocarIcone)\((?:icone, )?'([a-z0-9_]+)'\)", fh.read()))
    assert usados and usados <= set(icones.ICONES_JS) <= _simbolos()


def test_nenhuma_pagina_usa_a_fonte_de_icone():
    for caminho in icones.paginas():
        with open(caminho, encoding="utf-8") as fh:
            assert "material-symbols" not in fh.read(), caminho


def test_href_do_sprite_resolve_a_partir_de_cada_pagina():
    for caminho in icones.paginas():
        with open(caminho, encoding="utf-8") as fh:
            for href in set(re.findall(r'href="([^"#]*icones\.svg)#', fh.read())):
                alvo = os.path.normpath(os.path.join(os.path.dirname(caminho), href))
                assert alvo == icones.SPRITE, (caminho, href)


def test_reescrita_e_idempotente(tmp_path, monkeypatch):
    pagina = tmp_path / "aulas" / "x.html"
    pagina.parent.mkdir()
    pagina.write_text('<p><span class="material-symbols-outlined" aria-hidden="true">insights</span></p>',
                      encoding="utf-8")
    monkeypatch.setattr(icones, "RAIZ", str(tmp_path))
    assert icones.reescrever(str(pagina)) == 1
    assert icones.reescrever(str(pagina)) == 0
    texto = pagina.read_text(encoding="utf-8")
    assert 'href="../assets/icons/icones.svg#query_stats"' in texto
