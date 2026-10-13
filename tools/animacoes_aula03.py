"""Animações da Aula 03, a partir de dados/ via tools/medidas_aula03.py.

1. aula03-curva-correlacao (26 s): as carteiras de PETR4 com IVVB11 no plano
   risco-retorno, com as volatilidades e os retornos medidos na cesta. A
   correlação cai de +1 a -1 e a reta entre os dois ativos se curva para a
   esquerda; o ponto de menor risco é marcado a cada quadro. No fim, a curva da
   correlação medida entra tracejada. O pôster é o último quadro.
2. aula03-correlacao-movel (24 s): a correlação de 63 pregões de ITUB4 com BBDC4
   e de PETR4 com IVVB11 desenhada no tempo. No fim, março de 2020 é destacado
   com o pico de cada par. O pôster é o último quadro.

Tratamento de ausência da ADR-009 (tools/retornos.py): os dois pares são
medidos na janela comum dos dois ativos. Sem a GOLD11, essa janela tem 1.907
retornos desde 03/01/2019 e inclui março de 2020, de que as duas animações
dependem; main() confere isso antes de gravar.

Uso: .venv/bin/python tools/animacoes_aula03.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula03 as m  # noqa: E402
import retornos as r  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402

PAR_CURVA = ("PETR4", "IVVB11")


def _data_br(texto):
    return "/".join(reversed(texto.split("-")))


def curva_correlacao():
    a, b = PAR_CURVA
    par = m.estatisticas_par(a, b)
    pesos = np.linspace(0, 1, 201)
    retorno = pesos * par["ret_a"] + (1 - pesos) * par["ret_b"]

    def riscos(rho):
        return np.array([m.risco_dois_ativos(w, par["vol_a"], par["vol_b"], rho) for w in pesos])

    fig = figura()
    eixo = fig.add_axes([0.10, 0.27, 0.86, 0.66])
    eixo.set_xlim(-0.01, max(par["vol_a"], par["vol_b"]) * 1.12)
    faixa = par["ret_a"] - par["ret_b"]
    eixo.set_ylim(min(par["ret_a"], par["ret_b"]) - 0.12 * faixa, max(par["ret_a"], par["ret_b"]) + 0.12 * faixa)
    eixo.set_xlabel("Risco anual (volatilidade)")
    eixo.set_ylabel("Retorno médio anual")
    eixo.xaxis.set_major_formatter(lambda v, _: m.pct(v, 0))
    eixo.yaxis.set_major_formatter(lambda v, _: m.pct(v, 0))
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)

    eixo.plot(riscos(1.0), retorno, color=cor("--seg-borda"), linewidth=2)
    maior_vol = max(par["vol_a"], par["vol_b"])
    for ticker, vol, ret in ((a, par["vol_a"], par["ret_a"]), (b, par["vol_b"], par["ret_b"])):
        eixo.plot([vol], [ret], "o", color=cor("--seg-primaria"), markersize=11)
        # O ativo mais arriscado fica perto da borda direita: rótulo à esquerda
        # do ponto, senão o texto sai da figura (visto no pôster).
        direita = vol == maior_vol
        eixo.annotate("%s\n%s de risco" % (ticker, m.pct(vol)), xy=(vol, ret),
                      xytext=(-14 if direita else 12, -44 if direita else -8),
                      textcoords="offset points", fontsize=16, color=cor("--seg-texto"),
                      ha="right" if direita else "left")
    linha, = eixo.plot([], [], color=cor("--seg-primaria"), linewidth=3)
    medida, = eixo.plot([], [], color=cor("--seg-secundaria"), linewidth=3, linestyle="--")
    minimo, = eixo.plot([], [], "o", color=cor("--seg-destaque"), markersize=13)
    legenda = fig.text(0.08, 0.05, "", fontsize=18, color=cor("--seg-texto"))

    parado, descendo, final = 2 * FPS, 18 * FPS, 6 * FPS
    total = parado + descendo + final

    def desenhar(i):
        if i < parado + descendo:
            rho = 1.0 - 2.0 * max(0, i - parado) / (descendo - 1)
            rho = max(-1.0, rho)
            medida.set_data([], [])
            vols = riscos(rho)
            linha.set_data(vols, retorno)
            k = int(np.argmin(vols))
            minimo.set_data([vols[k]], [retorno[k]])
            w = m.peso_variancia_minima(par["vol_a"], par["vol_b"], rho)
            legenda.set_text("Correlação %s: o menor risco é %s, com %s em %s."
                             % (m.dec(rho), m.pct(m.risco_dois_ativos(w, par["vol_a"], par["vol_b"], rho)),
                                m.pct(w, 0), a))
        else:
            # Quadro final: só a curva medida (tracejada) e a reta de
            # correlação 1, com o ponto de menor risco da correlação medida.
            linha.set_data([], [])
            vols = riscos(par["rho"])
            medida.set_data(vols, retorno)
            k = int(np.argmin(vols))
            minimo.set_data([vols[k]], [retorno[k]])
            legenda.set_text("Correlação medida de %s com %s: %s. Menor risco %s, com %s em %s,\n"
                             "abaixo dos %s do ativo menos arriscado."
                             % (a, b, m.dec(par["rho"]), m.pct(par["risco_minimo"]),
                                m.pct(par["peso_minimo"]), a, m.pct(min(par["vol_a"], par["vol_b"]))))

    # Pôster no primeiro quadro, com correlação +1: o quadro final traz o peso de
    # menor risco medido, que é a previsão pedida no widget do Bloco 3.
    return gravar(fig, desenhar, total, "aula03-curva-correlacao", 0)


def correlacao_movel():
    series = {par: m.correlacao_movel(*par) for par in m.PARES_MOVEIS}
    resumos = {par: m.resumo_movel(*par) for par in m.PARES_MOVEIS}
    datas = sorted(set().union(*[s.index for s in series.values()]))
    datas = pd.DatetimeIndex(datas)

    fig = figura()
    eixo = fig.add_axes([0.09, 0.27, 0.88, 0.65])
    eixo.set_xlim(datas[0], datas[-1])
    eixo.set_ylim(-0.8, 1.05)
    eixo.axhline(0, color=cor("--seg-borda"), linewidth=1)
    eixo.set_ylabel("Correlação em 63 pregões")
    eixo.yaxis.set_major_formatter(lambda v, _: m.dec(v))
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    linhas = {}
    for (a, b), token in zip(m.PARES_MOVEIS, ("--seg-primaria", "--seg-secundaria")):
        linhas[(a, b)], = eixo.plot([], [], color=cor(token), linewidth=2.6, label="%s com %s" % (a, b))
    eixo.legend(loc="lower left", frameon=False)
    legenda = fig.text(0.09, 0.05, "", fontsize=19, color=cor("--seg-texto"))

    desenho, final = 18 * FPS, 6 * FPS
    total = desenho + final
    faixa_crise = eixo.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-03-31"),
                               color=cor("--seg-superficie"), zorder=0, visible=False)

    def desenhar(i):
        limite = datas[min(len(datas) - 1, int(len(datas) * (i + 1) / desenho))]
        for par, linha in linhas.items():
            trecho = series[par].loc[:limite]
            linha.set_data(trecho.index, trecho.values)
        faixa_crise.set_visible(i >= desenho)
        if i < desenho:
            legenda.set_text("")
        else:
            bancos, petro = resumos[m.PARES_MOVEIS[0]], resumos[m.PARES_MOVEIS[1]]
            a1, b1 = m.PARES_MOVEIS[0]
            a2, b2 = m.PARES_MOVEIS[1]
            legenda.set_text("%s com %s chega a %s em %s.\n"
                             "%s com %s sai de %s no fim de 2019 para %s no fim de março de 2020."
                             % (a1, b1, m.dec(bancos["maximo"]), _data_br(bancos["data_maximo"]),
                                a2, b2, m.dec(petro["fim_2019"]), m.dec(petro["fim_marco_2020"])))

    # Pôster no quadro em que a linha chega ao fim de 2019: o deck pede a
    # previsão sobre março de 2020 antes de o vídeo tocar.
    fim_2019 = int(np.searchsorted(datas, pd.Timestamp("2019-12-31"), side="right"))
    return gravar(fig, desenhar, total, "aula03-correlacao-movel", int(desenho * fim_2019 / len(datas)) - 1)


def janela_dos_pares():
    """Retornos e pregões de março de 2020 na janela comum de cada par animado."""
    saida = {}
    for par in [PAR_CURVA] + list(m.PARES_MOVEIS):
        rets = r.retornos_janela_comum(list(par))
        saida[par] = (len(rets), len(rets.loc["2020-03-01":"2020-03-31"]))
    return saida


def main():
    for par, (n, marco) in janela_dos_pares().items():
        if marco == 0:
            print("%s com %s: a janela comum perdeu março de 2020 (%d retornos)" % (par + (n,)))
            return 1
    for gerar in (curva_correlacao, correlacao_movel):
        mp4, _ = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
