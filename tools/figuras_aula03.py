"""Figuras estáticas do deck da Aula 03 (ADR-017), geradas de dados/ com a paleta do tema.

Uso: .venv/bin/python tools/figuras_aula03.py
Saída: assets/img/aula03-heatmap-cesta.png e assets/img/aula03-movel-bova-dolar.png
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

import medidas_aula03_lab as m  # noqa: E402
from midia import figura  # noqa: E402
from paleta import cor  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "img")


def heatmap():
    c = m.matriz_cesta()
    fig = figura()
    fig.set_size_inches(10, 10)
    eixo = fig.add_axes([0.12, 0.12, 0.86, 0.86])
    mapa = LinearSegmentedColormap.from_list("inteli", [cor("--seg-secundaria"), cor("--seg-base"), cor("--seg-primaria")])
    eixo.imshow(c.values, cmap=mapa, vmin=-1, vmax=1)
    n = len(c)
    eixo.set_xticks(range(n), c.columns, rotation=90, fontsize=16)
    eixo.set_yticks(range(n), c.columns, fontsize=16)
    for i in range(n):
        for j in range(n):
            v = c.values[i, j]
            eixo.text(j, i, ("%.2f" % v).replace(".", ","), ha="center", va="center", fontsize=12,
                      color=cor("--seg-base") if v > 0.55 else cor("--seg-texto"))
    from matplotlib.patches import Rectangle
    for a, b in (("ITUB4", "BBDC4"), ("RENT3", "GOLD11")):
        i, j = list(c.columns).index(a), list(c.columns).index(b)
        for x, y in ((j, i), (i, j)):
            eixo.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, fill=False, edgecolor=cor("--seg-destaque"), linewidth=3))
    for lado in eixo.spines.values():
        lado.set_visible(False)
    fig.savefig(os.path.join(SAIDA, "aula03-heatmap-cesta.png"), dpi=100)
    plt.close(fig)


def movel():
    precos, rets = m.movel_bova_dolar()
    fig = figura()
    eixo = fig.add_axes([0.12, 0.1, 0.86, 0.86])
    eixo.plot(precos.index, precos.values, color=cor("--seg-primaria"), linewidth=2.5, label="sobre os preços (como no vídeo)")
    eixo.plot(rets.index, rets.values, color=cor("--seg-secundaria"), linewidth=2.5, label="sobre os retornos diários")
    eixo.axhline(0, color=cor("--seg-borda"), linewidth=1)
    eixo.set_ylim(-1, 1)
    eixo.set_ylabel("correlação móvel, 252 pregões", fontsize=20)
    eixo.tick_params(labelsize=20)
    eixo.legend(loc="upper left", frameon=False, fontsize=20)
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    fig.savefig(os.path.join(SAIDA, "aula03-movel-bova-dolar.png"), dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    heatmap()
    movel()
    print("ok")
