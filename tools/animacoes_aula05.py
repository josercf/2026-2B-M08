"""Animações da Aula 05, a partir de dados/ via tools/medidas_aula05.py.

1. aula05-janela-deslizante (37 s): a janela de treino de 24 meses desliza de mês
   em mês sobre a linha do tempo, e cada janela acrescenta uma barra com os pesos
   da carteira de máximo Sharpe otimizada nela. A legenda de cada quadro traz o
   Sharpe prometido no treino e o entregue nos 12 meses seguintes; o quadro final
   resume quantas janelas entregaram menos do que prometeram e a rotatividade
   mensal mediana. O pôster é o quadro da primeira janela.
2. aula05-drawdown-teste (26 s): as duas carteiras ótimas do treino 2023-2024
   aplicadas em 2025, com o patrimônio e a curva de drawdown se formando pregão a
   pregão ao lado do CDI. O quadro final marca o fundo de cada drawdown e compara
   o Sharpe prometido com o entregue. O pôster é o fim do primeiro trimestre.

Uso: .venv/bin/python tools/animacoes_aula05.py [janela-deslizante] [drawdown-teste]
"""
import os
import sys

import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula05 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402

# Cinco cores de peso do segmento Graduação para os cinco ativos de maior peso
# médio; o resto da cesta soma numa faixa só, em cinza claro.
TOKENS_ATIVOS = ["--seg-primaria", "--seg-secundaria", "--seg-destaque",
                 "--inteli-cinza-escuro", "--inteli-cinza-medio"]
TOKEN_DEMAIS = "--seg-superficie"


def _pct(valor, casas=2):
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",")


def _num(valor, casas=2):
    return ("%.*f" % (casas, valor)).replace(".", ",").replace("-", "−")


def _mes(ts):
    return ts.strftime("%m/%Y")


def _data_br(ts):
    return ts.strftime("%d/%m/%Y")


def _limpar_eixo(eixo, lados=("top", "right")):
    for lado in lados:
        eixo.spines[lado].set_visible(False)


def janela_deslizante():
    resultados = m.resultados_deslizantes()
    resumo = m.resumo_deslizante(resultados)["max_sharpe"]
    ativos = resultados[0]["ativos"]
    destaque = [t for t, _ in m.ativos_destaque(resultados, "max_sharpe")]
    indices = [ativos.index(t) for t in destaque]
    pesos = np.array([r["max_sharpe"]["pesos"] for r in resultados])
    camadas = [pesos[:, i] for i in indices] + [1 - pesos[:, indices].sum(axis=1)]
    rotulos = destaque + ["demais 10 ativos"]
    tokens = TOKENS_ATIVOS + [TOKEN_DEMAIS]
    n = len(resultados)
    inicio = resultados[0]["treino"][0]
    fim = resultados[-1]["teste"][1]

    fig = figura()
    titulo = fig.text(0.06, 0.95, "Máximo Sharpe: pesos ótimos em cada janela de treino de 24 meses",
                      fontsize=22, color=cor("--seg-texto"), weight="bold")
    linha_tempo = fig.add_axes([0.06, 0.66, 0.74, 0.08])
    linha_tempo.set_xlim(inicio, fim)
    linha_tempo.set_ylim(0, 1)
    linha_tempo.set_yticks([])
    _limpar_eixo(linha_tempo, ("top", "right", "left"))
    treino_ret = Rectangle((0, 0.1), 0, 0.8, facecolor=cor("--seg-superficie"),
                           edgecolor=cor("--seg-primaria"), linewidth=2)
    teste_ret = Rectangle((0, 0.1), 0, 0.8, facecolor=cor("--seg-destaque"), edgecolor="none")
    linha_tempo.add_patch(treino_ret)
    linha_tempo.add_patch(teste_ret)
    rotulo_treino = linha_tempo.text(0, 0.5, "treino", ha="center", va="center", fontsize=15)
    rotulo_teste = linha_tempo.text(0, 0.5, "teste", ha="center", va="center", fontsize=15,
                                    color=cor("--seg-base"))

    barras = fig.add_axes([0.06, 0.20, 0.74, 0.38])
    barras.set_xlim(-0.6, n - 0.4)
    barras.set_ylim(0, 1)
    barras.set_yticks([0, 0.25, 0.5, 0.75, 1])
    barras.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    marcas = list(range(0, n, 4))
    barras.set_xticks(marcas)
    barras.set_xticklabels([_mes(resultados[i]["treino"][0]) for i in marcas], fontsize=13)
    barras.set_xlabel("início da janela de treino", fontsize=15)
    _limpar_eixo(barras)
    retangulos = []
    for i in range(n):
        base = 0.0
        pilha = []
        for camada, token in zip(camadas, tokens):
            r = Rectangle((i - 0.38, base), 0.76, camada[i], facecolor=cor(token),
                          edgecolor=cor("--seg-borda") if token == TOKEN_DEMAIS else "none",
                          linewidth=0.8, visible=False)
            barras.add_patch(r)
            pilha.append(r)
            base += camada[i]
        retangulos.append(pilha)
    for rotulo, token in zip(rotulos, tokens):
        barras.bar([0], [0], color=cor(token), label=rotulo,
                   edgecolor=cor("--seg-borda") if token == TOKEN_DEMAIS else "none")
    barras.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=15)
    legenda = fig.text(0.06, 0.885, "", fontsize=17, color=cor("--seg-texto"), va="top")

    por_janela = FPS
    quadros_janelas = n * por_janela
    total = quadros_janelas + 4 * FPS

    def desenhar(i):
        k = min(n - 1, i // por_janela)
        r = resultados[k]
        (ti, tf), (si, sf) = r["treino"], r["teste"]
        treino_ret.set_x(ti)
        treino_ret.set_width(tf - ti)
        teste_ret.set_x(si)
        teste_ret.set_width(sf - si)
        rotulo_treino.set_x(ti + (tf - ti) / 2)
        rotulo_teste.set_x(si + (sf - si) / 2)
        for j, pilha in enumerate(retangulos):
            for ret in pilha:
                ret.set_visible(j <= k)
        if i < quadros_janelas:
            legenda.set_text("Treino de %s a %s, teste de %s a %s.\n"
                             "Sharpe prometido no treino: %s. Entregue no teste: %s."
                             % (_mes(ti), _mes(tf), _mes(si), _mes(sf),
                                _num(r["max_sharpe"]["esperado"]["sharpe"]),
                                _num(r["max_sharpe"]["realizado"]["sharpe"])))
        else:
            legenda.set_text("Em %d das %d janelas o Sharpe entregue ficou abaixo do prometido.\n"
                             "Carteira trocada de um mês para o seguinte, mediana: %s."
                             % (resumo["abaixo_do_prometido"], n,
                                _pct(resumo["rotatividade_mensal_mediana"])))
        titulo.set_text("Máximo Sharpe: pesos ótimos em cada janela de treino de 24 meses")

    # Pôster no quadro da primeira janela: o final responderia à previsão do deck.
    return gravar(fig, desenhar, total, "aula05-janela-deslizante", por_janela // 2)


def drawdown_teste():
    p = m.principal()
    datas = p["max_sharpe"]["realizado"]["patrimonio"].index
    cdi = m.cdi_no_periodo(datas[0], datas[-1]).reindex(datas, method="ffill")
    series = [("max_sharpe", "Máximo Sharpe", "--seg-primaria"),
              ("var_min", "Variância mínima", "--seg-secundaria")]

    fig = figura()
    fig.text(0.07, 0.95, "Carteiras ótimas de 2023-2024 aplicadas em 2025, pregão a pregão",
             fontsize=22, color=cor("--seg-texto"), weight="bold")
    topo = fig.add_axes([0.08, 0.48, 0.88, 0.30])
    base = fig.add_axes([0.08, 0.17, 0.88, 0.25], sharex=topo)
    patrimonios = [p[c]["realizado"]["patrimonio"] for c, _, _ in series] + [cdi]
    topo.set_ylim(min(s.min() for s in patrimonios) - 0.02, max(s.max() for s in patrimonios) + 0.03)
    topo.set_xlim(datas[0], datas[-1])
    topo.set_ylabel(r"R\$ por R\$ 1 aplicado", fontsize=15)
    topo.tick_params(labelbottom=False)
    fundo = min(p[c]["realizado"]["drawdown_max"] for c, _, _ in series)
    base.set_ylim(fundo * 1.35, 0.005)
    base.set_ylabel("drawdown", fontsize=15)
    base.yaxis.set_major_formatter(lambda v, _: _pct(v, 0))
    base.xaxis.set_major_formatter(lambda v, _: "")
    meses = [d for d in datas if d.day <= 7 and (d.month - 1) % 2 == 0]
    vistos = []
    for d in meses:
        if not vistos or vistos[-1].month != d.month:
            vistos.append(d)
    base.set_xticks(vistos)
    base.set_xticklabels([d.strftime("%m/%Y") for d in vistos], fontsize=13)
    for eixo in (topo, base):
        _limpar_eixo(eixo)

    linhas = {}
    for chave, rotulo, token in series:
        linhas[chave], = topo.plot([], [], color=cor(token), linewidth=2.6, label=rotulo)
        linhas[chave + "_dd"], = base.plot([], [], color=cor(token), linewidth=2.2)
    linhas["cdi"], = topo.plot([], [], color=cor("--seg-destaque"), linewidth=2.2,
                               linestyle="--", label="CDI")
    topo.legend(loc="upper left", frameon=False, fontsize=15)
    preenchidos = []
    legenda = fig.text(0.07, 0.885, "", fontsize=17, color=cor("--seg-texto"), va="top")

    quadros_desenho = 20 * FPS
    total = quadros_desenho + 6 * FPS
    estado = {"marcado": False}
    marcas = []

    def desenhar(i):
        k = max(2, int(round(len(datas) * min(i + 1, quadros_desenho) / quadros_desenho)))
        for chave, _, token in series:
            r = p[chave]["realizado"]
            linhas[chave].set_data(datas[:k], r["patrimonio"].values[:k])
            linhas[chave + "_dd"].set_data(datas[:k], r["drawdown"].values[:k])
        linhas["cdi"].set_data(datas[:k], cdi.values[:k])
        while preenchidos:
            preenchidos.pop().remove()
        for chave, _, token in series:
            preenchidos.append(base.fill_between(datas[:k], p[chave]["realizado"]["drawdown"].values[:k],
                                                 0, color=cor(token), alpha=0.25, linewidth=0))
        # As marcas do fundo só aparecem no fim; o pôster é um quadro anterior
        # e é desenhado depois da gravação, então a visibilidade segue o quadro.
        for marca in marcas:
            marca.set_visible(i >= quadros_desenho)
        if i < quadros_desenho:
            legenda.set_text("Até %s. A curva de baixo mede a queda desde o último pico do patrimônio."
                             % _data_br(datas[k - 1]))
            return
        if not estado["marcado"]:
            estado["marcado"] = True
            for n, (chave, rotulo, token) in enumerate(series):
                r = p[chave]["realizado"]
                marcas.extend(base.plot([r["data_fundo"]], [r["drawdown_max"]], "o", color=cor(token), markersize=9))
                marcas.append(base.annotate("%s em %s" % (_pct(r["drawdown_max"]), _data_br(r["data_fundo"])),
                              xy=(r["data_fundo"], r["drawdown_max"]),
                              xytext=(12, -6 if n == 0 else -22), textcoords="offset points",
                              fontsize=15, color=cor("--seg-texto"),
                              bbox={"boxstyle": "round,pad=0.25", "facecolor": cor("--seg-base"),
                                    "edgecolor": "none"}))
        ms, vm = p["max_sharpe"], p["var_min"]
        legenda.set_text("Sharpe prometido no treino contra entregue em 2025: máximo Sharpe %s contra %s,\n"
                         "variância mínima %s contra %s. Em 2025 o CDI acumulou %s; as carteiras, %s e %s."
                         % (_num(ms["esperado"]["sharpe"]), _num(ms["realizado"]["sharpe"]),
                            _num(vm["esperado"]["sharpe"]), _num(vm["realizado"]["sharpe"]),
                            _pct(m.cdi_acumulado_no_teste()),
                            _pct(ms["realizado"]["retorno_acumulado"]),
                            _pct(vm["realizado"]["retorno_acumulado"])))

    # Pôster com o primeiro trimestre: o final responderia à previsão do deck.
    return gravar(fig, desenhar, total, "aula05-drawdown-teste", quadros_desenho // 4)


def main(nomes=None):
    geradores = {"janela-deslizante": janela_deslizante, "drawdown-teste": drawdown_teste}
    for nome, gerar in geradores.items():
        if nomes and nome not in nomes:
            continue
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
