"""Animações da Aula 02, a partir de dados/ via tools/medidas_aula02.py.

1. aula02-histograma-retornos (24 s): o histograma dos retornos diários da PETR4
   se formando pregão a pregão, em ordem cronológica. Os pregões de março de 2020
   entram em coral e vão parar nas caudas; os pregões além de 3 desvios ganham uma
   marca na faixa abaixo do eixo. No fim, a curva normal com a mesma média e o
   mesmo desvio entra por cima, e a legenda compara as caudas medidas com as que
   a normal preveria. O pôster é um quadro anterior a março de 2020.
2. aula02-raiz-do-tempo (22 s): o desvio padrão do retorno logarítmico acumulado
   do BOVA11 em horizontes de 1 a 63 pregões, ponto a ponto, contra a curva do
   desvio diário multiplicado pela raiz do horizonte. É a justificativa da raiz de
   252 na anualização. O pôster mostra só o primeiro ponto.

Uso: .venv/bin/python tools/animacoes_aula02.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula02 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402

HORIZONTE_MAX = 63
LARGURA_CLASSE = 0.005


def _virgula(numero, casas=1):
    return ("%.*f" % (casas, numero)).replace(".", ",")


def _data_br(timestamp):
    return timestamp.strftime("%d/%m/%Y")


def histograma_retornos():
    ticker = m.TICKER_CAUDAS
    r = m.retornos_simples()[ticker].dropna()
    c = m.caudas(ticker)
    media, desvio = float(r.mean()), c["desvio"]
    marco = r.index.strftime("%Y-%m") == "2020-03"
    bordas = np.arange(math.floor(r.min() / LARGURA_CLASSE) * LARGURA_CLASSE,
                       r.max() + LARGURA_CLASSE, LARGURA_CLASSE)
    centros = (bordas[:-1] + bordas[1:]) / 2
    contagem_final, _ = np.histogram(r, bordas)

    fig = figura()
    eixo = fig.add_axes([0.08, 0.37, 0.89, 0.54])
    faixa = fig.add_axes([0.08, 0.29, 0.89, 0.05], sharex=eixo)
    eixo.set_xlim(bordas[0], bordas[-1])
    eixo.set_ylim(0, contagem_final.max() * 1.12)
    eixo.set_ylabel("pregões por classe de 0,5%")
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    eixo.tick_params(labelbottom=False)
    faixa.set_ylim(0, 1)
    faixa.set_yticks([])
    for lado in ("top", "right", "left"):
        faixa.spines[lado].set_visible(False)
    ticks = np.arange(-0.30, 0.25, 0.05)
    faixa.set_xticks(ticks)
    faixa.set_xticklabels(["%d%%" % round(t * 100) for t in ticks])
    for limite in (media - 3 * desvio, media + 3 * desvio):
        eixo.axvline(limite, color=cor("--seg-texto"), linewidth=1.2, linestyle="--")
    eixo.text(media + 3 * desvio, contagem_final.max() * 1.05, "  3 desvios", fontsize=15)

    barras_outros = eixo.bar(centros, np.zeros(len(centros)), width=LARGURA_CLASSE * 0.92,
                             color=cor("--seg-primaria"), label="demais pregões")
    barras_marco = eixo.bar(centros, np.zeros(len(centros)), width=LARGURA_CLASSE * 0.92,
                            color=cor("--seg-destaque"), label="março de 2020")
    eixo.legend(loc="upper left", frameon=False)
    relogio = fig.text(0.97, 0.93, "", fontsize=20, ha="right", color=cor("--seg-texto"))
    legenda = fig.text(0.08, 0.12, "", fontsize=19, color=cor("--seg-texto"))
    alem = np.abs((r.values - media) / desvio) > 3

    quadros_formacao = 18 * FPS
    total = quadros_formacao + 6 * FPS
    estado = {"marcados": 0, "curva": None, "marcas": []}

    def desenhar(i):
        k = max(1, int(round(len(r) * min(i + 1, quadros_formacao) / quadros_formacao)))
        outros, _ = np.histogram(r.values[:k][~marco[:k]], bordas)
        do_marco, _ = np.histogram(r.values[:k][marco[:k]], bordas)
        for barra, altura in zip(barras_outros, outros):
            barra.set_height(altura)
        for barra, base, altura in zip(barras_marco, outros, do_marco):
            barra.set_y(base)
            barra.set_height(altura)
        # O pôster é desenhado depois da gravação, num quadro anterior: as marcas e
        # a curva acumuladas precisam sair para o pôster mostrar só aquele quadro.
        if k < estado["marcados"]:
            for marca in estado["marcas"]:
                marca.remove()
            estado["marcas"], estado["marcados"] = [], 0
        for j in range(estado["marcados"], k):
            if alem[j]:
                estado["marcas"] += faixa.plot([r.values[j]] * 2, [0.1, 0.9], linewidth=2.2,
                                               color=cor("--seg-destaque") if marco[j] else cor("--seg-primaria"))
        estado["marcados"] = k
        if i < quadros_formacao and estado["curva"] is not None:
            estado["curva"].remove()
            estado["curva"] = None
            eixo.legend(loc="upper left", frameon=False)
            legenda.set_text("")
        relogio.set_text("%s: %s pregões" % (_data_br(r.index[k - 1]), "{:,}".format(k).replace(",", ".")))
        if i >= quadros_formacao and estado["curva"] is None:
            x = np.linspace(bordas[0], bordas[-1], 600)
            normal = len(r) * LARGURA_CLASSE * np.exp(-0.5 * ((x - media) / desvio) ** 2) / (desvio * math.sqrt(2 * math.pi))
            estado["curva"], = eixo.plot(x, normal, color=cor("--seg-secundaria"), linewidth=3,
                                         label="normal, mesma média e desvio")
            eixo.legend(loc="upper left", frameon=False)
            legenda.set_text("%d pregões além de 3 desvios, contra %s previstos pela normal; %d em março de 2020.\n"
                             "Pior queda: %s em %s, a %s desvios da média."
                             % (c["alem_3"], _virgula(c["alem_3_normal"]), c["alem_3_marco_2020"],
                                m.pct(c["pior"]), "/".join(reversed(c["pior_data"].split("-"))),
                                _virgula(abs(c["pior_em_desvios"]), 2)))

    # Pôster antes de março de 2020 entrar: o pôster não entrega a resposta da
    # previsão que o deck pede antes de tocar (achado da revisão do deck).
    return gravar(fig, desenhar, total, "aula02-histograma-retornos", int(quadros_formacao * 0.12))


def raiz_do_tempo():
    horizontes = list(range(1, HORIZONTE_MAX + 1))
    medidas = m.raiz_do_tempo(horizontes=horizontes)
    diario = medidas[1]["medido"]
    medido = np.array([medidas[h]["medido"] for h in horizontes])
    previsto = np.array([medidas[h]["previsto"] for h in horizontes])

    fig = figura()
    eixo = fig.add_axes([0.10, 0.38, 0.84, 0.55])
    eixo.set_xlim(0, HORIZONTE_MAX + 2)
    eixo.set_ylim(0, max(medido.max(), previsto.max()) * 1.18)
    eixo.set_xlabel("horizonte, em pregões")
    eixo.set_ylabel("desvio do retorno acumulado")
    eixo.yaxis.set_major_formatter(lambda v, _: "%d%%" % round(v * 100))
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    eixo.plot(horizontes, previsto, color=cor("--seg-primaria"), linewidth=2.6, linestyle="--",
              label="desvio diário do log x raiz do horizonte")
    pontos, = eixo.plot([], [], "o", color=cor("--seg-destaque"), markersize=7,
                        label="medido no retorno log do %s" % m.TICKER_RAIZ)
    # Legenda embaixo à direita: no alto à esquerda ela cobria o rótulo "um
    # mês" (visto no pôster), e a curva passa longe do canto inferior direito.
    eixo.legend(loc="lower right", frameon=False)
    for h, rotulo in ((21, "um mês"), (63, "um trimestre")):
        eixo.axvline(h, color=cor("--seg-borda"), linewidth=1.5)
        eixo.text(h - 0.6, eixo.get_ylim()[1] * 0.98, rotulo, fontsize=15, va="top", ha="right")
    legenda = fig.text(0.10, 0.12, "", fontsize=19, color=cor("--seg-texto"))

    por_ponto = 9
    quadros_pontos = len(horizontes) * por_ponto
    total = quadros_pontos + 4 * FPS

    def desenhar(i):
        k = min(len(horizontes), i // por_ponto + 1)
        pontos.set_data(horizontes[:k], medido[:k])
        h = horizontes[k - 1]
        legenda.set_text("%d %s: %s%% medido, %s%% previsto por %s%% x raiz de %d."
                         % (h, "pregão" if h == 1 else "pregões", _virgula(medido[k - 1] * 100, 2), _virgula(previsto[k - 1] * 100, 2),
                            _virgula(diario * 100, 2), h))
        if i >= quadros_pontos:
            legenda.set_text("O risco cresce com a raiz do tempo: em %d pregões, %s%% medido contra %s%% previsto.\n"
                             "Por isso a volatilidade anual multiplica o desvio diário por raiz de 252."
                             % (HORIZONTE_MAX, _virgula(medido[-1] * 100, 2), _virgula(previsto[-1] * 100, 2)))

    # Pôster com só o primeiro ponto medido, pelo mesmo motivo do histograma.
    return gravar(fig, desenhar, total, "aula02-raiz-do-tempo", 0)


def main():
    for gerar in (histograma_retornos, raiz_do_tempo):
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
