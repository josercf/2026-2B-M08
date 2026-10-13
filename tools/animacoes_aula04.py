"""Animações da Aula 04 (legendas no topo do quadro, porque a barra de
controles do <video> cobre a faixa de baixo).

Animações da Aula 04, a partir de dados/ via tools/medidas_aula04.py.

1. aula04-nuvem-monte-carlo (22 s): as 10.000 carteiras sorteadas entrando no
   plano risco-retorno em lotes crescentes (10, 100, 1.000 e 10.000), verdes
   acima do CDI e cinza abaixo, com a melhor sorteada até o momento em coral.
   O pôster é o último quadro.
2. aula04-fronteira (20 s): a nuvem completa em cinza, a fronteira de 50 pontos
   traçada da variância mínima até a PETR4 e, no fim, as duas carteiras ótimas
   marcadas ao lado da melhor sorteada. O pôster é o último quadro.
3. aula04-slsqp-triangulo (22 s): o caminho do SLSQP maximizando o Sharpe de
   PETR4, IVVB11 e GOLD11, um passo por vez, no triângulo de pesos e no plano
   risco-retorno do trio. O pôster é o último quadro.

Uso: .venv/bin/python tools/animacoes_aula04.py
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula04 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402


def _pct(valor, casas=2):
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",")


def _num(valor):
    return ("%.2f" % valor).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _figura():
    """Figura do contrato com texto 1,3 vez maior: o vídeo aparece a cerca de 58%
    do tamanho no slide, e o texto de 18 pt do tema cairia abaixo do piso."""
    fig = figura()
    plt.rcParams.update({"font.size": 23, "xtick.labelsize": 21, "ytick.labelsize": 21})
    return fig


def _eixo_risco_retorno(fig, caixa, xlim, ylim):
    eixo = fig.add_axes(caixa)
    eixo.set_xlim(*xlim)
    eixo.set_ylim(*ylim)
    eixo.set_xlabel("volatilidade anual")
    eixo.set_ylabel("retorno anual")
    eixo.xaxis.set_major_formatter(lambda v, _: _pct(v, 0))
    eixo.yaxis.set_major_formatter(lambda v, _: _pct(v, 0))
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    return eixo


def nuvem_monte_carlo():
    n = m.nuvem()
    rf = m.taxa_livre_de_risco()
    vol, ret, sharpe = n["volatilidade"], n["retorno"], n["sharpe"]
    cores = np.where(sharpe >= 0, cor("--seg-secundaria"), cor("--seg-texto-suave"))

    fig = _figura()
    eixo = _eixo_risco_retorno(fig, [0.13, 0.13, 0.83, 0.64], (0.10, 0.26), (-0.03, 0.20))
    eixo.axhline(rf, color=cor("--seg-primaria"), linestyle="--", linewidth=1.8)
    eixo.text(0.258, rf + 0.004, "CDI %s" % _pct(rf), ha="right", va="bottom",
              color=cor("--seg-primaria"), fontsize=21)
    pontos = eixo.scatter([], [], s=8, linewidths=0)
    melhor, = eixo.plot([], [], "o", markersize=13, color=cor("--seg-destaque"),
                        markeredgecolor=cor("--seg-base"), markeredgewidth=2)
    legenda = fig.text(0.10, 0.975, "", fontsize=24, va="top", color=cor("--seg-texto"))

    # Quatro patamares de 4,5 s cada, com crescimento suave dentro do patamar,
    # e 4 s parados no fim para a leitura final.
    patamares = (10, 100, 1_000, 10_000)
    por_patamar = int(4.5 * FPS)
    total = len(patamares) * por_patamar + 4 * FPS

    def quantos(i):
        k = min(i // por_patamar, len(patamares) - 1)
        anterior = patamares[k - 1] if k else 0
        fracao = min(1.0, (i - k * por_patamar + 1) / (0.6 * por_patamar))
        return max(1, int(anterior + (patamares[k] - anterior) * fracao))

    def desenhar(i):
        q = quantos(i)
        pontos.set_offsets(np.column_stack([vol[:q], ret[:q]]))
        pontos.set_color(cores[:q])
        pontos.set_sizes([40 if q <= 100 else (16 if q <= 1_000 else 7)])
        b = int(np.argmax(sharpe[:q]))
        melhor.set_data([vol[b]], [ret[b]])
        abaixo = int((sharpe[:q] < 0).sum())
        texto = ("%s carteiras sorteadas: %s abaixo do CDI.\n"
                 "Melhor Sharpe até aqui (ponto coral): %s."
                 % (_milhar(q), _milhar(abaixo), _num(sharpe[b])))
        legenda.set_text(texto)

    # Pôster antes da revelação: só os 10 primeiros sorteios, para não
    # entregar a resposta da previsão pedida no slide (revisão de 13/10/2026).
    return gravar(fig, desenhar, total, "aula04-nuvem-monte-carlo", por_patamar - 1)


def fronteira():
    n = m.nuvem()
    f = m.fronteira()
    mv = m.carteira(m.variancia_minima())
    ms = m.carteira(m.maximo_sharpe())

    fig = _figura()
    eixo = _eixo_risco_retorno(fig, [0.13, 0.13, 0.83, 0.64], (0.08, 0.36), (-0.03, 0.40))
    eixo.scatter(n["volatilidade"], n["retorno"], s=5, linewidths=0, color=cor("--seg-borda"))
    linha, = eixo.plot([], [], color=cor("--seg-primaria"), linewidth=3.2)
    marcas = []
    legenda = fig.text(0.10, 0.975, "", fontsize=24, va="top", color=cor("--seg-texto"))

    quadros_linha = 12 * FPS
    total = quadros_linha + 8 * FPS
    estado = {"marcado": False}

    def desenhar(i):
        k = max(1, int(round(len(f) * min(i + 1, quadros_linha) / quadros_linha)))
        linha.set_data(f["volatilidade"].values[:k], f["retorno"].values[:k])
        legenda.set_text("Fronteira: %d de 50 pontos de retorno alvo, cada um a carteira\n"
                         "de menor volatilidade para aquele retorno, sem venda a descoberto." % k)
        if i >= quadros_linha and not estado["marcado"]:
            estado["marcado"] = True
            for carteira, token, rotulo, desloc in (
                    (mv, "--seg-secundaria", "Variância mínima", (14, -34)),
                    (ms, "--seg-destaque", "Máximo Sharpe", (-14, 18))):
                marcas.append(eixo.plot([carteira["volatilidade"]], [carteira["retorno"]], "o",
                                        markersize=14, color=cor(token),
                                        markeredgecolor=cor("--seg-primaria"),
                                        markeredgewidth=2)[0])
                eixo.annotate(rotulo, xy=(carteira["volatilidade"], carteira["retorno"]),
                              xytext=desloc, textcoords="offset points",
                              ha="left" if desloc[0] > 0 else "right",
                              fontsize=21, color=cor("--seg-texto"),
                              # Fundo opaco: o rótulo da variância mínima cai
                              # sobre a borda da nuvem (visto no pôster).
                              bbox={"boxstyle": "round,pad=0.25",
                                    "facecolor": cor("--seg-base"), "edgecolor": "none"})
            b = n["melhor"]
            eixo.plot([n["volatilidade"][b]], [n["retorno"][b]], "o", markersize=11,
                      color=cor("--seg-primaria"))
            eixo.annotate("Melhor sorteada", xy=(n["volatilidade"][b], n["retorno"][b]),
                          xytext=(18, -6), textcoords="offset points", fontsize=21,
                          color=cor("--seg-texto"))
        if i >= quadros_linha:
            legenda.set_text("Variância mínima: volatilidade %s e retorno %s, em %d ativos.\n"
                             "Máximo Sharpe: %s, contra %s da melhor das 10.000 sorteadas."
                             % (_pct(mv["volatilidade"]), _pct(mv["retorno"]), mv["ativos"],
                                _num(ms["sharpe"]), _num(n["melhor_sharpe"])))

    return gravar(fig, desenhar, total, "aula04-fronteira", total - 1)


def slsqp_triangulo():
    passos, final = m.caminho_slsqp_trio()
    mu, cov = m.trio()
    rf = m.taxa_livre_de_risco()
    metricas = np.array([m.metricas(w, mu, cov, rf) for w in passos])

    fig = _figura()
    # Triângulo à esquerda, em coordenadas próprias.
    tri = fig.add_axes([0.02, 0.06, 0.38, 0.72])
    tri.set_xlim(-0.12, 1.12)
    tri.set_ylim(-0.14, 1.0)
    tri.set_aspect("equal")
    tri.axis("off")
    vertices = np.array([[0.5, np.sqrt(3) / 2], [0.0, 0.0], [1.0, 0.0]])
    tri.add_patch(Polygon(vertices, closed=True, facecolor=cor("--seg-superficie"),
                          edgecolor=cor("--seg-primaria"), linewidth=2))
    for (x, y), rotulo, va in zip(vertices, m.TRIO, ("bottom", "top", "top")):
        tri.text(x, y + (0.03 if va == "bottom" else -0.04), rotulo, ha="center", va=va,
                 fontsize=22, fontweight="bold", color=cor("--seg-texto"))

    def tela(w):
        return w @ vertices

    caminho_tri, = tri.plot([], [], "-o", color=cor("--seg-destaque"), linewidth=2, markersize=7)

    # Plano risco-retorno do trio à direita, com todas as carteiras do trio em cinza.
    grade = [(a, b, 1 - a - b) for a in np.linspace(0, 1, 41) for b in np.linspace(0, 1, 41)
             if a + b <= 1 + 1e-9]
    grade = np.array([[max(0.0, x) for x in w] for w in grade])
    gm = np.array([m.metricas(w, mu, cov, rf) for w in grade])
    plano = _eixo_risco_retorno(fig, [0.54, 0.13, 0.43, 0.64], (0.08, 0.36), (0.12, 0.40))
    plano.scatter(gm[:, 1], gm[:, 0], s=10, linewidths=0, color=cor("--seg-borda"))
    caminho_plano, = plano.plot([], [], "-o", color=cor("--seg-destaque"), linewidth=2,
                                markersize=7)
    legenda = fig.text(0.05, 0.975, "", fontsize=24, va="top", color=cor("--seg-texto"))

    por_passo = int(1.6 * FPS)
    total = len(passos) * por_passo + 4 * FPS

    def desenhar(i):
        k = min(len(passos), i // por_passo + 1)
        xy = np.array([tela(w) for w in passos[:k]])
        caminho_tri.set_data(xy[:, 0], xy[:, 1])
        caminho_plano.set_data(metricas[:k, 1], metricas[:k, 0])
        w = passos[k - 1]
        if i >= len(passos) * por_passo:
            legenda.set_text("Ótimo do trio em %d iterações: %s.\nSharpe %s, o mesmo da cesta de 15 ativos."
                             % (len(passos) - 1,
                                ", ".join("%s %s" % (t, _pct(p)) for t, p in zip(m.TRIO, final)),
                                _num(metricas[-1, 2])))
        else:
            legenda.set_text("%s: %s.\nSharpe %s."
                             % ("Ponto de partida" if k == 1 else "Iteração %d" % (k - 1),
                                ", ".join("%s %s" % (t, _pct(p, 0)) for t, p in zip(m.TRIO, w)),
                                _num(metricas[k - 1, 2])))

    # Pôster no ponto de partida: o caminho e o ótimo ficam para o vídeo.
    return gravar(fig, desenhar, total, "aula04-slsqp-triangulo", 0)


def main():
    for gerar in (nuvem_monte_carlo, fronteira, slsqp_triangulo):
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
