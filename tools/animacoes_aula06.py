"""Animações da Aula 06, a partir de tools/medidas_aula06.py.

1. aula06-requisicao (24 s): o pedido sai do componente React, passa pela
   validação da FastAPI e pelos módulos das sprints, que resolvem os problemas
   de otimização, e volta como JSON; no fim, o gráfico da fronteira é desenhado
   com os 50 pares da resposta. O pôster é o último quadro.
2. aula06-cache (21 s): cinco gestores pedem a mesma sequência de consultas a
   duas APIs, uma sem cache e outra com cache, e a barra de cada uma acumula os
   problemas de otimização resolvidos. O pôster é o último quadro.

Uso: .venv/bin/python tools/animacoes_aula06.py
"""
import os
import sys

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula06 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402


def _br(valor, casas=2):
    return ("%.*f" % (casas, valor)).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _caixa(fig, x, y, largura, altura, titulo, subtitulo):
    caixa = FancyBboxPatch((x, y), largura, altura, boxstyle="round,pad=0.008,rounding_size=0.015",
                           transform=fig.transFigure, facecolor=cor("--seg-superficie"),
                           edgecolor=cor("--seg-borda"), linewidth=2)
    fig.patches.append(caixa)
    fig.text(x + largura / 2, y + altura * 0.64, titulo, ha="center", va="center",
             fontsize=20, fontweight="bold", color=cor("--seg-texto"))
    fig.text(x + largura / 2, y + altura * 0.30, subtitulo, ha="center", va="center",
             fontsize=15, color=cor("--seg-texto"))
    return caixa


def requisicao():
    r = m.resultado()
    c = m.contexto()
    problemas = m.problemas_por_pedido(com_cache=False)[0]
    fig = figura()

    caixas = [
        (0.03, "Navegador", "componente React, fetch"),
        (0.365, "Servidor", "FastAPI valida com Pydantic"),
        (0.70, "Módulos das sprints", "carteira.pipeline: A1, A2, A4"),
    ]
    largura, altura, base = 0.27, 0.15, 0.78
    patches = [_caixa(fig, x, base, largura, altura, t, s) for x, t, s in caixas]
    centros = [x + largura / 2 for x, _, _ in caixas]
    for a, b in ((0, 1), (1, 2)):
        fig.add_artist(_seta(fig, centros[a] + largura / 2 + 0.005, centros[b] - largura / 2 - 0.005))

    envelope = fig.text(0, 0, "", ha="center", va="center", fontsize=18, color=cor("--seg-texto"),
                        family="monospace",
                        bbox={"boxstyle": "round,pad=0.4", "facecolor": cor("--seg-base"),
                              "edgecolor": cor("--seg-primaria"), "linewidth": 2})
    status = fig.text(0.5, 0.715, "", ha="center", fontsize=17, color=cor("--seg-texto"))

    eixo = fig.add_axes([0.09, 0.14, 0.86, 0.42])
    eixo.set_xlim(0, max(a["volatilidade"] for a in r["ativos"]) * 1.12)
    eixo.set_ylim(0, max(a["retorno"] for a in r["ativos"]) * 1.15)
    eixo.set_xlabel("volatilidade anual")
    eixo.set_ylabel("retorno anual")
    eixo.xaxis.set_major_formatter(lambda v, _: "%d%%" % round(100 * v))
    eixo.yaxis.set_major_formatter(lambda v, _: "%d%%" % round(100 * v))
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    eixo.set_visible(False)
    curva, = eixo.plot([], [], color=cor("--seg-primaria"), linewidth=3)
    estado = {"marcado": False}

    seg = FPS
    fases = {"ida": (0, 5 * seg), "valida": (5 * seg, 7 * seg), "ida2": (7 * seg, 9 * seg),
             "calcula": (9 * seg, 12 * seg), "volta": (12 * seg, 16 * seg), "grafico": (16 * seg, 22 * seg)}
    total = 24 * seg
    pedido = 'POST /carteiras/otimizar\n{"tickers": [%d ativos],\n "inicio": "2019-01-01"}' % len(r["tickers"])
    resposta = ('200 OK\n{"pregoes": %d,\n "maximo_sharpe": {...},\n "fronteira": [%d pares]}'
                % (r["pregoes"], len(r["fronteira"])))
    y_envelope = 0.50

    def entre(i, fase):
        a, b = fases[fase]
        return min(1.0, max(0.0, (i - a) / (b - a)))

    def realcar(indice):
        for k, p in enumerate(patches):
            p.set_edgecolor(cor("--seg-primaria") if k == indice else cor("--seg-borda"))
            p.set_linewidth(4 if k == indice else 2)

    def desenhar(i):
        if i < fases["valida"][1]:
            t = entre(i, "ida")
            envelope.set_position((centros[0] + (centros[1] - centros[0]) * t, y_envelope))
            envelope.set_text(pedido)
            realcar(0 if t < 1 else 1)
            status.set_text("" if t < 1 else "Pydantic: 2 a 15 tickers, sem repetição, início antes do fim")
        elif i < fases["ida2"][1]:
            t = entre(i, "ida2")
            envelope.set_position((centros[1] + (centros[2] - centros[1]) * t, y_envelope))
            realcar(1 if t < 1 else 2)
            status.set_text("pedido válido: a rota chama pipeline.calcular, sem copiar código")
        elif i < fases["calcula"][1]:
            t = entre(i, "calcula")
            envelope.set_position((centros[2], y_envelope))
            envelope.set_text("SLSQP\n%d de %d problemas" % (round(problemas * t), problemas))
            realcar(2)
            status.set_text("variância mínima, máximo Sharpe e %d pontos da fronteira" % len(r["fronteira"]))
        elif i < fases["volta"][1]:
            t = entre(i, "volta")
            envelope.set_text(resposta)
            envelope.set_position((centros[2] + (centros[0] - centros[2]) * t, y_envelope))
            realcar(0 if t >= 1 else None)
            status.set_text("o navegador recebe o JSON e desenha o gráfico")
        else:
            t = entre(i, "grafico")
            envelope.set_text("")
            realcar(0)
            eixo.set_visible(True)
            k = max(2, round(len(r["fronteira"]) * t))
            curva.set_data([p[0] for p in r["fronteira"][:k]], [p[1] for p in r["fronteira"][:k]])
            if t >= 1 and not estado["marcado"]:
                estado["marcado"] = True
                for a in r["ativos"]:
                    eixo.scatter(a["volatilidade"], a["retorno"], s=60, color=cor("--seg-borda"), zorder=3)
                    eixo.annotate(a["ticker"], (a["volatilidade"], a["retorno"]), xytext=(8, -4),
                                  textcoords="offset points", fontsize=14)
                for chave, nome, dx, dy, ha in (("variancia_minima", "Variância mínima", -12, -26, "right"),
                                                ("maximo_sharpe", "Máximo Sharpe", -12, 12, "right")):
                    p = r[chave]
                    eixo.scatter(p["volatilidade"], p["retorno"], s=180, color=cor("--seg-secundaria"),
                                 edgecolor=cor("--seg-primaria"), linewidth=2, zorder=4)
                    eixo.annotate("%s: %s%% de risco" % (nome, _br(100 * p["volatilidade"])),
                                  (p["volatilidade"], p["retorno"]), xytext=(dx, dy),
                                  textcoords="offset points", fontsize=15, fontweight="bold", ha=ha)
                status.set_text("Máximo Sharpe: %s%% de retorno anual, %s%% de volatilidade, Sharpe %s"
                                % (_br(c["maximo_sharpe"]["retorno_anual_pct"]),
                                   _br(c["maximo_sharpe"]["volatilidade_anual_pct"]),
                                   _br(c["maximo_sharpe"]["sharpe"])))

    return gravar(fig, desenhar, total, "aula06-requisicao", total - 1)


def _seta(fig, x0, x1):
    from matplotlib.patches import FancyArrowPatch

    return FancyArrowPatch((x0, 0.855), (x1, 0.855), transform=fig.transFigure,
                           arrowstyle="<|-|>", mutation_scale=22, color=cor("--seg-primaria"),
                           linewidth=2.5)


def cache():
    sem = m.problemas_por_pedido(com_cache=False)
    com = m.problemas_por_pedido(com_cache=True)
    sequencia = m.SEQUENCIA_CACHE
    descricao = {"A": "%s a %s" % (m.PEDIDO["inicio"][:4], m.PEDIDO["fim"][:4]),
                 "B": "%s a %s" % (m.PEDIDO_2021["inicio"][:4], m.PEDIDO_2021["fim"][:4])}

    fig = figura()
    fig.text(0.06, 0.90, "Cinco gestores, os mesmos %d ativos, duas janelas de dados"
             % len(m.PEDIDO["tickers"]), fontsize=24, fontweight="bold", color=cor("--seg-texto"))
    fig.text(0.06, 0.83, "Consulta A: %s.   Consulta B: %s." % (descricao["A"], descricao["B"]),
             fontsize=18, color=cor("--seg-texto"))
    pedidos_txt = fig.text(0.06, 0.77, "", fontsize=18, color=cor("--seg-texto"))
    eixo = fig.add_axes([0.20, 0.40, 0.74, 0.32])
    eixo.set_xlim(0, sum(sem) * 1.08)
    eixo.set_ylim(-0.75, 1.5)
    eixo.set_yticks([1, 0])
    eixo.set_yticklabels(["Sem cache", "Com cache"], fontsize=19)
    eixo.set_xlabel("problemas de otimização resolvidos (chamadas ao SLSQP), acumulados")
    for lado in ("top", "right", "left"):
        eixo.spines[lado].set_visible(False)
    servidos = eixo.text(0, -0.55, "", ha="left", va="center", fontsize=16, color=cor("--seg-texto"))
    # Acima de 0.12: a barra de controles do <video> cobre a faixa de baixo do quadro.
    legenda = fig.text(0.06, 0.14, "", fontsize=19, color=cor("--seg-texto"))

    por_pedido = 3 * FPS
    total = len(sequencia) * por_pedido + 6 * FPS
    feitos = {"n": 0}

    def desenhar(i):
        n = min(len(sequencia), i // por_pedido + 1)
        if n < feitos["n"]:
            # Pôster pedido depois da animação inteira: apagar as barras e redesenhar
            # só até o quadro pedido, senão o pôster mostraria a resposta final.
            for artista in list(eixo.patches) + [t for t in eixo.texts if t is not servidos]:
                artista.remove()
            legenda.set_text("")
            feitos["n"] = 0
        while feitos["n"] < n:
            k = feitos["n"]
            for y, contagem, token in ((1, sem, "--seg-primaria"), (0, com, "--seg-secundaria")):
                if contagem[k]:
                    inicio = sum(contagem[:k])
                    eixo.barh(y, contagem[k], left=inicio, height=0.55, color=cor(token),
                              edgecolor=cor("--seg-base"), linewidth=2)
                    eixo.text(inicio + contagem[k] / 2, y, "%d" % contagem[k], ha="center", va="center",
                              fontsize=16, color=cor("--seg-base") if token == "--seg-primaria"
                              else cor("--seg-texto"))
            feitos["n"] += 1
        pedidos_txt.set_text("Pedidos que chegaram: " + ", ".join(
            "%d (%s)" % (j + 1, sequencia[j]) for j in range(n)))
        do_cache = [str(j + 1) for j in range(n) if com[j] == 0]
        rotulo = "pedido " if len(do_cache) == 1 else "pedidos "
        lista = do_cache[0] if len(do_cache) == 1 else ", ".join(do_cache[:-1]) + " e " + (do_cache[-1] if do_cache else "")
        servidos.set_text("Com cache, sem nenhum cálculo: " + rotulo + lista if do_cache else "")
        if i >= len(sequencia) * por_pedido:
            legenda.set_text("Sem cache: %d pedidos, %s problemas resolvidos.\n"
                             "Com cache: %s, só na primeira vez de cada consulta."
                             % (len(sem), _milhar(sum(sem)), _milhar(sum(com))))

    # Pôster no fim do primeiro pedido: o quadro final responderia à previsão do slide.
    return gravar(fig, desenhar, total, "aula06-cache", por_pedido - 1)


def main():
    for gerar in (requisicao, cache):
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
