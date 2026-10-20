"""Ícones do acervo: Material Symbols Sharp do brand kit, servidos num sprite SVG.

O brand kit do Inteli (ICO-01 e ICO-05, 12/08/2026) pede Material Symbols Sharp,
peso 400, a partir dos SVGs vendorados no próprio kit, e proíbe a fonte
Outlined por CDN. Este script faz as duas coisas que a troca exige:

1. reescreve cada <span class="material-symbols-outlined">nome</span> das
   páginas em <svg class="icone"><use href=".../assets/icons/icones.svg#nome">;
2. gera assets/icons/icones.svg com um <symbol> por nome usado, copiado do kit.

O sprite fica versionado, então o CI e o GitHub Pages não dependem do kit. Os
scripts de assets/js que montam ícone em tempo de execução declaram os nomes em
ICONES_JS, para que o sprite os inclua.

Uso: .venv/bin/python tools/icones.py   (idempotente)
"""
import glob
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.environ.get(
    "INTELI_ICONES_KIT",
    os.path.expanduser("~/.claude/skills/inteli-brand-kit/assets/icons/sharp"),
)
SPRITE = os.path.join(RAIZ, "assets", "icons", "icones.svg")

# Nome do Google Icons que não existe no kit e o substituto escolhido.
SUBSTITUTOS = {"insights": "query_stats"}

# Ícones montados por JavaScript (inteli-print.js, inteli-cronometro.js e inteli-nuvem.js).
ICONES_JS = ["picture_as_pdf", "play_arrow", "pause", "replay",
              "mic", "stop", "check", "delete_sweep", "settings"]

PAGINAS = ["index.html", "aulas/*.html", "materiais/*.html", "referencias/*.html", "quiz/*.html"]

SPAN = re.compile(
    r'<span class="material-symbols-outlined"(?: aria-hidden="true")?>([a-z0-9_]+)</span>'
)
USO = re.compile(r'icones\.svg#([a-z0-9_]+)')
PATH = re.compile(r'<path d="([^"]+)"')


def paginas():
    for padrao in PAGINAS:
        for caminho in sorted(glob.glob(os.path.join(RAIZ, padrao))):
            yield caminho


def _href(caminho, nome):
    profundidade = os.path.relpath(caminho, RAIZ).count(os.sep)
    return "../" * profundidade + "assets/icons/icones.svg#" + nome


def reescrever(caminho):
    """Troca os spans de ícone da página por <svg><use>. Devolve quantos trocou."""
    with open(caminho, encoding="utf-8") as fh:
        html = fh.read()

    def troca(casamento):
        nome = SUBSTITUTOS.get(casamento.group(1), casamento.group(1))
        return '<svg class="icone" aria-hidden="true"><use href="%s"></use></svg>' % _href(caminho, nome)

    novo, n = SPAN.subn(troca, html)
    if n:
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(novo)
    return n


def nomes_usados():
    nomes = set(ICONES_JS)
    for caminho in paginas():
        with open(caminho, encoding="utf-8") as fh:
            nomes.update(USO.findall(fh.read()))
    return sorted(nomes)


def gerar_sprite(nomes):
    simbolos = []
    for nome in nomes:
        with open(os.path.join(KIT, nome + ".svg"), encoding="utf-8") as fh:
            caminho = PATH.search(fh.read()).group(1)
        simbolos.append('  <symbol id="%s" viewBox="0 -960 960 960"><path d="%s"/></symbol>' % (nome, caminho))
    os.makedirs(os.path.dirname(SPRITE), exist_ok=True)
    with open(SPRITE, "w", encoding="utf-8") as fh:
        fh.write(
            '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n'
            "  <!-- Material Symbols Sharp, peso 400, FILL 0, copiados do inteli-brand-kit.\n"
            "       Copyright Google LLC, Apache License 2.0 (assets/icons/LICENSE).\n"
            "       Gerado por tools/icones.py: não editar à mão. -->\n"
            + "\n".join(simbolos) + "\n</svg>\n"
        )


def main():
    total = sum(reescrever(c) for c in paginas())
    nomes = nomes_usados()
    gerar_sprite(nomes)
    print("%d spans reescritos; sprite com %d ícones em %s" % (total, len(nomes), os.path.relpath(SPRITE, RAIZ)))


if __name__ == "__main__":
    sys.exit(main())
