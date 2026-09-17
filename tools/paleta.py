"""Tokens de cor de assets/css/inteli-brand.css, para scripts Python.

Figuras e animações do acervo não declaram hex: pedem o token pelo nome, por
exemplo cor("--seg-primaria"). A paleta tem uma fonte só, a mesma que o tema do
deck consome e que o tools/check_brand.py protege.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(RAIZ, "assets", "css", "inteli-brand.css")

_COMENTARIO = re.compile(r"/\*.*?\*/", re.S)
_DECLARACAO = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
_VAR = re.compile(r"var\((--[a-z0-9-]+)\)")
_HEX = re.compile(r"#[0-9a-fA-F]{6}")


def tokens(caminho=BRAND):
    """Dicionário token -> valor final, com var(--outro) resolvido."""
    with open(caminho, encoding="utf-8") as fh:
        texto = _COMENTARIO.sub("", fh.read())
    brutos = {nome: valor.strip() for nome, valor in _DECLARACAO.findall(texto)}

    def resolver(nome, trilha):
        if nome in trilha:
            raise ValueError("referência circular: %s" % " -> ".join(trilha + (nome,)))
        valor = brutos[nome]
        referencia = _VAR.fullmatch(valor)
        return resolver(referencia.group(1), trilha + (nome,)) if referencia else valor

    return {nome: resolver(nome, ()) for nome in brutos}


def cor(nome, caminho=BRAND):
    """Hex de um token de cor, em minúsculas: cor("--seg-primaria") -> "#2e2640"."""
    valor = tokens(caminho)[nome]
    if not _HEX.fullmatch(valor):
        raise ValueError("%s não é cor hex: %r" % (nome, valor))
    return valor.lower()
