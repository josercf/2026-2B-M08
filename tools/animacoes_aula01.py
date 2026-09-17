"""Animações da Aula 01, a partir de dados/ via tools/medidas_aula01.py.

1. aula01-tres-visoes-mglu3 (24 s): as três visões de preço da MGLU3 desenhadas
   no tempo, em escala logarítmica, com cada evento corporativo rotulado quando a
   linha chega nele. O pôster é o último quadro.
2. aula01-mapa-ausencias (20 s): a matriz de pregões por ativo preenchida ativo a
   ativo; no fim, o bloco vazio do GOLD11 e o pregão de 24/10/2025 destacados, e
   o número de pregões que o dropna mantém. O pôster é o último quadro.

Uso: .venv/bin/python tools/animacoes_aula01.py
"""
import os
import sys

import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _data_br(timestamp):
    return timestamp.strftime("%d/%m/%Y")


def descrever_evento(fator):
    if fator < 1:
        return "grupamento de %d para 1" % round(1 / fator)
    if float(fator).is_integer():
        return "desdobramento de %d para 1" % fator
    return "bonificação de %s%% em ações" % ("%g" % round((fator - 1) * 100, 2)).replace(".", ",")


def tres_visoes_mglu3():
    visoes = m.tres_visoes("MGLU3")
    eventos = m.carregar_desdobramentos()
    eventos = eventos[eventos["ticker"] == "MGLU3"].reset_index(drop=True)

    fig = figura()
    eixo = fig.add_axes([0.09, 0.12, 0.87, 0.80])
    eixo.set_yscale("log")
    eixo.set_xlim(visoes.index[0], visoes.index[-1])
    eixo.set_ylim(visoes.min().min() * 0.6, visoes.max().max() * 2.2)
    eixo.set_ylabel("R$ por ação, escala logarítmica")
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)

    linhas = {}
    for chave, token, rotulo in (("negociado", "--seg-destaque", "Negociado na data"),
                                 ("fechamento", "--seg-primaria", "Close do Yahoo"),
                                 ("ajustado", "--seg-secundaria", "Adj Close do Yahoo")):
        linhas[chave], = eixo.plot([], [], color=cor(token), linewidth=2.6, label=rotulo)
    eixo.legend(loc="upper right", frameon=False)

    datas = visoes.index
    quadros_desenho = 20 * FPS
    total = quadros_desenho + 4 * FPS
    rotulados = set()

    def desenhar(i):
        k = max(2, int(round(len(datas) * min(i + 1, quadros_desenho) / quadros_desenho)))
        for chave, linha in linhas.items():
            linha.set_data(datas[:k], visoes[chave].values[:k])
        for n, (data, fator) in enumerate(zip(eventos["data"], eventos["fator"])):
            if data <= datas[k - 1] and data not in rotulados:
                rotulados.add(data)
                # Evento perto do fim da série: deslocar para a esquerda, senão o
                # rótulo sai pela borda direita da figura (visto no pôster).
                perto_da_borda = (data - datas[0]) > 0.85 * (datas[-1] - datas[0])
                deslocamento = (-14 if perto_da_borda else 14, 40 if n % 2 == 0 else -56)
                eixo.annotate("%s\n%s" % (_data_br(data), descrever_evento(fator)),
                              xy=(data, visoes.loc[data, "negociado"]), xytext=deslocamento,
                              textcoords="offset points", fontsize=15, color=cor("--seg-texto"),
                              ha="right" if perto_da_borda else "left",
                              arrowprops={"arrowstyle": "-", "color": cor("--seg-borda")},
                              # Fundo opaco: sem ele, a linha da série cruza por
                              # trás do texto e o rótulo fica ilegível (visto no
                              # pôster, no evento de 06/08/2019).
                              bbox={"boxstyle": "round,pad=0.35", "facecolor": cor("--seg-base"),
                                    "edgecolor": "none"})

    return gravar(fig, desenhar, total, "aula01-tres-visoes-mglu3", total - 1)


def mapa_ausencias():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    presente = fechamento.notna().to_numpy().T.astype(float)
    n_ativos, n_pregoes = presente.shape
    tratamentos = m.comparar_tratamentos()

    mapa_de_cor = ListedColormap([cor("--seg-destaque"), cor("--seg-secundaria")])
    mapa_de_cor.set_bad(cor("--seg-base"))

    fig = figura()
    eixo = fig.add_axes([0.10, 0.24, 0.87, 0.68])
    visivel = np.full(presente.shape, np.nan)
    imagem = eixo.imshow(visivel, aspect="auto", cmap=mapa_de_cor, vmin=0, vmax=1,
                         interpolation="nearest")
    eixo.set_yticks(range(n_ativos))
    eixo.set_yticklabels(fechamento.columns, fontsize=14)
    anos = sorted(set(fechamento.index.year))
    eixo.set_xticks([int(np.argmax(fechamento.index.year == ano)) for ano in anos])
    eixo.set_xticklabels([str(ano) for ano in anos])
    for lado in ("top", "right", "left", "bottom"):
        eixo.spines[lado].set_visible(False)
    legenda = fig.text(0.10, 0.06, "", fontsize=19, color=cor("--seg-texto"))

    gold = list(fechamento.columns).index("GOLD11")
    primeiro_gold = int(np.argmax(presente[gold] == 1))
    dia_falha = list(fechamento.index.strftime("%Y-%m-%d")).index("2025-10-24")
    por_ativo = FPS
    quadros_ativos = n_ativos * por_ativo
    total = quadros_ativos + 5 * FPS
    estado = {"destacado": False}

    def desenhar(i):
        linhas = min(n_ativos, i // por_ativo + 1)
        visivel[:linhas] = presente[:linhas]
        imagem.set_data(visivel)
        if i >= quadros_ativos and not estado["destacado"]:
            estado["destacado"] = True
            eixo.add_patch(Rectangle((-0.5, gold - 0.5), primeiro_gold, 1, fill=False,
                                     edgecolor=cor("--seg-primaria"), linewidth=2.5))
            eixo.axvline(dia_falha, color=cor("--seg-primaria"), linewidth=2, linestyle="--")
            legenda.set_text("GOLD11: %d pregões sem cotação antes de %s.\n"
                             "BOVA11, IVVB11 e GOLD11: sem cotação em 24/10/2025."
                             % (primeiro_gold, _data_br(fechamento.index[primeiro_gold])))
        if i >= quadros_ativos + 3 * FPS:
            legenda.set_text("Descartar as datas com ausência mantém %s dos %s pregões\n"
                             "e começa a série da cesta inteira em %s."
                             % (_milhar(tratamentos["pregoes_descartar"]),
                                _milhar(tratamentos["pregoes_total"]),
                                "/".join(reversed(tratamentos["inicio_descartar"].split("-")))))

    return gravar(fig, desenhar, total, "aula01-mapa-ausencias", total - 1)


def main():
    for gerar in (tres_visoes_mglu3, mapa_ausencias):
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
