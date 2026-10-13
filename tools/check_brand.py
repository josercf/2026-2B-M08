#!/usr/bin/env python3
"""
Valida a fidelidade ao Brandbook Inteli 2025.

Oito regras. As cinco primeiras citam a pagina do Brandbook Inteli 2025; as
tres ultimas citam o codigo do inteli-brand-kit (norma de 12/08/2026), que
a auditoria de 13/10/2026 mostrou que este validador ainda nao conferia:

1. cor-fora-da-paleta   p.66  hex declarado no brand que nao esta na paleta oficial
2. cor-literal          p.66  cor literal declarada fora do arquivo de tokens
3. fonte-fora-do-brand  p.69  font-family declarado fora do arquivo de tokens
4. cor-de-outro-segmento p.68 lilas e verde escuro sao de Escolas e Exec/Pos
5. emoji                p.88  a iconografia da marca e o Material Symbols
6. canto-arredondado    GRA-01  todo container tem canto reto; circulo so para dado
7. icone-fora-do-kit    ICO-01  Material Symbols Sharp do kit, nunca Outlined por CDN
8. peso-tipografico     TIP-04  titulo 700, subtitulo e label 600, corpo 300, destaque 700

Uso:
    python3 tools/check_brand.py
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join("assets", "css", "inteli-brand.css")

PALETA = {
    "#2e2640", "#ff4545", "#90a5e5", "#89cea5", "#066d73",
    "#b2b6bf", "#caced6", "#e6eaeb", "#ffffff",
}
# p.68: pertencem a Escolas e a Exec/Pos, nao a Graduacao
OUTRO_SEGMENTO = {"#90a5e5", "#066d73"}

EXTENSOES = (".html", ".css", ".js")
# .claude guarda worktrees de agente (.claude/worktrees/NOME/), que sao copias
# inteiras do repositorio. Sem ignorar, a copia do inteli-brand.css que vive la
# dentro nao casa com o caminho canonico do arquivo de tokens, e o validador
# acusa cada cor e cada font-family dela como violacao. Sao 12 falsos positivos
# por worktree, e ruido treina quem le a ignorar o validador.
IGNORAR = {".git", ".claude", ".venv", "node_modules", "__pycache__", ".ipynb_checkpoints"}

# Valor de declaracao CSS: tudo entre o ":" e o ";" ou o fim do bloco.
# Escanear hex solto daria falso positivo em href="#dados", cujas letras sao
# todas digitos hexadecimais validos.
DECLARACAO = re.compile(r"(?:^|[;{\"'])\s*[-a-zA-Z]+\s*:\s*([^;{}\"']*)")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FONT_FAMILY = re.compile(r"font-family\s*:")
# Blocos de emoji e simbolos pictograficos. As setas (U+2190 a U+21FF) ficam
# de fora de proposito: sao tipografia, nao emoji, e aparecem em textos como
# "Sprint 1 -> Sprint 2".
# GRA-01: qualquer raio diferente de zero. "0", "0px" e "0%" passam.
RAIO = re.compile(r"border-radius\s*:(?!\s*0(?:px|%)?\s*(?:[;\"'}]|$))\s*([^;\"'}]+)")
# ICO-01: a fonte de icone Outlined (ou Rounded) por CDN e a classe que a ativa.
ICONE_FORA = re.compile(r"material-symbols-(?:outlined|rounded)|Material\+Symbols|Material Symbols (?:Outlined|Rounded)")
# TIP-04: cada peso tem uma funcao. 300 corpo, 600 subtitulo e label, 700
# titulo e destaque. Vale para CSS e para a fonte de canvas dos widgets.
PESOS = {"300", "600", "700", "bold"}
PESO_CSS = re.compile(r"font-weight\s*:\s*([a-z0-9]+)")
PESO_CANVAS = re.compile(r"fonte\(\s*\d+\s*,\s*(\d+)\s*\)")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")


def _normalizar(hexa):
    """Expande #abc para #aabbcc e baixa a caixa, para comparar com a paleta."""
    h = hexa.lower()
    if len(h) == 4:
        return "#" + "".join(c * 2 for c in h[1:])
    return h


def _arquivos(raiz):
    for pasta, subs, nomes in os.walk(raiz):
        subs[:] = [s for s in subs if s not in IGNORAR]
        for nome in sorted(nomes):
            if nome.endswith(EXTENSOES):
                caminho = os.path.join(pasta, nome)
                yield caminho, os.path.relpath(caminho, raiz)


def varrer(raiz):
    """Devolve a lista de achados. Lista vazia significa acervo fiel ao brandbook."""
    achados = []
    for caminho, rel in _arquivos(raiz):
        eh_brand = rel.replace(os.sep, "/") == BRAND.replace(os.sep, "/")
        with open(caminho, encoding="utf-8") as fh:
            linhas = fh.read().splitlines()

        for n, linha in enumerate(linhas, start=1):
            for valor in DECLARACAO.findall(linha):
                for bruto in HEX.findall(valor):
                    hexa = _normalizar(bruto)
                    if hexa in OUTRO_SEGMENTO:
                        achados.append({
                            "arquivo": rel, "linha": n,
                            "regra": "cor-de-outro-segmento",
                            "detalhe": "%s e do segmento Escolas ou Exec/Pos (p.68)" % bruto,
                        })
                    elif eh_brand and hexa not in PALETA:
                        achados.append({
                            "arquivo": rel, "linha": n,
                            "regra": "cor-fora-da-paleta",
                            "detalhe": "%s nao esta na paleta oficial (p.66)" % bruto,
                        })
                    elif not eh_brand:
                        achados.append({
                            "arquivo": rel, "linha": n,
                            "regra": "cor-literal",
                            "detalhe": "%s deveria vir de var(--inteli-*)" % bruto,
                        })

            if not eh_brand and FONT_FAMILY.search(linha):
                achados.append({
                    "arquivo": rel, "linha": n,
                    "regra": "fonte-fora-do-brand",
                    "detalhe": "font-family so pode ser declarado em %s" % BRAND,
                })

            raio = RAIO.search(linha)
            if raio:
                achados.append({
                    "arquivo": rel, "linha": n, "regra": "canto-arredondado",
                    "detalhe": "border-radius %s: cantos retos em tudo (GRA-01)" % raio.group(1).strip(),
                })

            if ICONE_FORA.search(linha):
                achados.append({
                    "arquivo": rel, "linha": n, "regra": "icone-fora-do-kit",
                    "detalhe": "icone sai do sprite Sharp de assets/icons (ICO-01, tools/icones.py)",
                })

            for peso in PESO_CSS.findall(linha) + PESO_CANVAS.findall(linha):
                if peso not in PESOS:
                    achados.append({
                        "arquivo": rel, "linha": n, "regra": "peso-tipografico",
                        "detalhe": "peso %s fora de 300/600/700 (TIP-04)" % peso,
                    })

            achado_emoji = EMOJI.search(linha)
            if achado_emoji:
                achados.append({
                    "arquivo": rel, "linha": n, "regra": "emoji",
                    "detalhe": "%r: a iconografia da marca e o Material Symbols (p.88)"
                               % achado_emoji.group(0),
                })

    return achados


def main():
    achados = varrer(RAIZ)
    if not achados:
        print("Brandbook: paleta, tipografia, segmento e iconografia conferem.")
        return 0
    for a in achados:
        print("%s:%d  %s  %s" % (a["arquivo"], a["linha"], a["regra"], a["detalhe"]))
    print("\n%d violacao(oes) do brandbook." % len(achados))
    return 1


if __name__ == "__main__":
    sys.exit(main())
