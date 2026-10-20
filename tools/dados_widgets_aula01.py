"""JSON dos widgets da Aula 01, a partir de tools/medidas_aula01.py.

Uso: .venv/bin/python tools/dados_widgets_aula01.py
Saída: assets/data/aula01-tres-visoes.json, assets/data/aula01-ausencias.json e
assets/data/aula01-carteira.json

O aula01-carteira.json alimenta o widget carteira-nuvem do slide do parceiro: a
carteira de peso igual dos 15 ativos, uma subamostra da nuvem de 10.000
carteiras e a fronteira de 50 pontos da Aula 04. Tudo na janela comum dos 15
ativos (ADR-009), lida de tools/retornos.py por tools/medidas_aula04.py, para os
pontos dos ativos ficarem coerentes com a nuvem e com a fronteira.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import dados_widgets_aula04 as w4  # noqa: E402
import medidas_aula01 as m  # noqa: E402
import medidas_aula04 as m4  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
TICKERS_VISOES = ["MGLU3", "B3SA3", "WEGE3", "BBAS3", "PETR4"]
ATIVOS_AUSENCIAS = ["BOVA11", "IVVB11", "GOLD11", "PETR4", "VALE3"]
# Subamostra da nuvem da Aula 04 que o widget carteira-nuvem desenha: 2.000 das
# 10.000 carteiras, escolhidas sem reposição por um gerador de semente fixa. A
# ordem do sorteio é a ordem das ondas da animação.
N_AMOSTRA_NUVEM = 2_000
SEMENTE_AMOSTRA = 2026
# Quadro do gráfico. O completo contém os 15 ativos; o foco contém a nuvem, a
# fronteira e os ativos que não ficam longe dela. Ativo fica fora do foco quando
# a volatilidade passa de 1,5 vez a do fim da fronteira ou o retorno fica mais
# de 10 pontos abaixo do menor retorno da nuvem.
FOLGA_QUADRO = 0.02
PASSO_COMPLETO = 0.10
PASSO_FOCO = 0.05


def _pct(valor):
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _lista(itens):
    """Junta nomes em prosa: "A", "A e B" ou "A, B e C". Nenhuma lista digitada."""
    if len(itens) == 1:
        return itens[0]
    return ", ".join(itens[:-1]) + " e " + itens[-1]


def _serie(valores):
    return [None if math.isnan(x) else round(float(x), 2) for x in valores]


def tres_visoes():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    eventos = m.carregar_desdobramentos()
    saida = {"datas": [d.strftime("%Y-%m-%d") for d in fechamento.index], "tickers": {}}
    for ticker in TICKERS_VISOES:
        visoes = m.tres_visoes(ticker).reindex(fechamento.index)
        if ticker == "PETR4":
            leitura = ("PETR4 não tem evento de desdobramento no período. A distância entre Close "
                       "e Adj Close são os proventos: retorno de preço de %s e retorno total de %s."
                       % (_pct(m.retorno_no_periodo(visoes["fechamento"])),
                          _pct(m.retorno_no_periodo(visoes["ajustado"]))))
        else:
            data, variacao = m.maior_variacao_diaria(visoes["negociado"])
            no_close = visoes["fechamento"].dropna().pct_change().loc[data]
            leitura = ("%s em %s: o preço negociado varia %s e o Close do Yahoo, %s."
                       % (ticker, data.strftime("%d/%m/%Y"), _pct(variacao), _pct(no_close)))
        do_ticker = eventos[eventos["ticker"] == ticker]
        saida["tickers"][ticker] = {
            "negociado": _serie(visoes["negociado"]),
            "fechamento": _serie(visoes["fechamento"]),
            "ajustado": _serie(visoes["ajustado"]),
            "eventos": [{"data": d.strftime("%Y-%m-%d"), "fator": float(f)}
                        for d, f in zip(do_ticker["data"], do_ticker["fator"])],
            "leitura": leitura,
        }
    return saida


def ausencias():
    c = m.comparar_tratamentos()
    ausentes = m.ausencias()
    inicio = "/".join(reversed(c["inicio_descartar"].split("-")))
    data_falha = m.data_ausencia_compartilhada().strftime("%d/%m/%Y")
    etfs_falha = _lista(list(c["retorno_etfs_preenchido"]))
    return {
        "pregoes_total": c["pregoes_total"],
        "ativos": ATIVOS_AUSENCIAS,
        "ausentes": {t: int(ausentes[t]) for t in ausentes.index if ausentes[t] > 0},
        "descartar": {
            "pregoes": c["pregoes_descartar"],
            "vol": {t: round(float(c["vol_descartar"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Descartar mantém %s dos %s pregões e começa a cesta em %s, "
                        "sem março de 2020." % (_milhar(c["pregoes_descartar"]),
                                                 _milhar(c["pregoes_total"]), inicio)),
        },
        "preencher": {
            "pregoes": c["pregoes_preencher"],
            "vol": {t: round(float(c["vol_preencher"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Preencher mantém os %s pregões e dá retorno zero para %s em %s; "
                        "o pregão seguinte acumula os dois dias."
                        % (_milhar(c["pregoes_preencher"]), etfs_falha, data_falha)),
        },
    }


def _caixa(xs, ys, passo):
    """Menor caixa em múltiplos de passo que contém os pontos com FOLGA_QUADRO."""
    def fora(valor, sinal):
        # round antes de floor e ceil: 0,40 / 0,05 dá 8,000000000000002 em ponto flutuante.
        multiplo = round(valor / passo, 9)
        return round((math.floor(multiplo) if sinal < 0 else math.ceil(multiplo)) * passo, 4)
    return {"x": [fora(min(xs) - FOLGA_QUADRO, -1), fora(max(xs) + FOLGA_QUADRO, 1)],
            "y": [fora(min(ys) - FOLGA_QUADRO, -1), fora(max(ys) + FOLGA_QUADRO, 1)],
            "passo": passo}


def amostra_nuvem():
    """Índices da subamostra da nuvem, na ordem em que o widget os revela."""
    gerador = np.random.default_rng(SEMENTE_AMOSTRA)
    return gerador.choice(m4.N_CARTEIRAS, N_AMOSTRA_NUVEM, replace=False)


def carteira():
    mu = m4.retorno_esperado()
    vol = m4.volatilidade()
    tickers = list(mu.index)
    n = m4.nuvem()
    f = m4.fronteira()
    igual = np.full(len(tickers), 1 / len(tickers))
    ret_igual, vol_igual, sharpe_igual = m4.metricas(igual)
    indices = amostra_nuvem()

    vol_fronteira = float(f["volatilidade"].max())
    ret_nuvem = float(n["retorno"].min())
    fora = [t for t in tickers if vol[t] > 1.5 * vol_fronteira or mu[t] < ret_nuvem - 0.10]
    dentro = [t for t in tickers if t not in fora]
    foco = _caixa(list(n["volatilidade"]) + list(f["volatilidade"]) + [vol[t] for t in dentro],
                  list(n["retorno"]) + list(f["retorno"]) + [mu[t] for t in dentro], PASSO_FOCO)
    completo = _caixa(list(vol), list(mu), PASSO_COMPLETO)
    # O quadro completo parte da volatilidade zero: é a vista de câmera afastada.
    completo["x"][0] = 0.0

    return {
        "janela": w4.janela(),
        "rf": round(m4.taxa_livre_de_risco(), 4),
        "peso": round(1 / len(tickers), 4),
        "ativos": [{"ticker": t, "ret": round(float(mu[t]), 4), "vol": round(float(vol[t]), 4)}
                   for t in tickers],
        "igual": {"ret": round(ret_igual, 4), "vol": round(vol_igual, 4), "sharpe": round(sharpe_igual, 4)},
        "nuvem": {
            "total": m4.N_CARTEIRAS,
            "vol": [round(float(n["volatilidade"][i]), 4) for i in indices],
            "ret": [round(float(n["retorno"][i]), 4) for i in indices],
        },
        "fronteira": [[round(float(v), 4), round(float(r), 4)]
                      for v, r in zip(f["volatilidade"], f["retorno"])],
        "variancia_minima": w4._ponto(m4.carteira(m4.variancia_minima())),
        "maximo_sharpe": w4._ponto(m4.carteira(m4.maximo_sharpe())),
        "quadro": {"completo": completo, "foco": foco, "fora": fora},
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula01-tres-visoes.json", tres_visoes()), ("aula01-ausencias.json", ausencias()),
                        ("aula01-carteira.json", carteira())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
