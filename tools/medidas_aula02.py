"""Medições da Aula 02 sobre os CSVs de dados/.

Do preço ao retorno: retorno simples e logarítmico, média e desvio padrão
diários, caudas do histograma, anualização por 252 e por raiz de 252,
volatilidade em janela deslizante, a dispersão crescendo com a raiz do tempo e
a comparação da cesta com o CDI acumulado. Todo número que o deck, o notebook,
os widgets e as animações da Aula 02 citam sai daqui e está travado em
tools/tests/test_aula02.py.

Tratamento de ausência usado em toda a aula, salvo onde dito: Adj Close com
preenchimento para a frente por ativo (ffill), sem preencher antes da primeira
cotação. É a decisão do exemplo de ADR da Aula 01 e a regra do módulo
(ADR-009, tools/retornos.py); a GOLD11 entra só a partir
de 11/12/2020. O desafio do notebook inverte a decisão (descartar as datas com
ausência na cesta inteira), e descartar_contra_preencher() mede o efeito.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m1  # noqa: E402
import retornos  # noqa: E402

RAIZ = m1.RAIZ
DADOS = m1.DADOS
PREGOES_ANO = 252
JANELAS = (21, 63, 252)
DATA_QUEDA = "2020-03-09"
CRISE_INICIO, CRISE_FIM = "2020-02-20", "2020-04-30"
TICKER_CAUDAS = "PETR4"
TICKER_RAIZ = "BOVA11"
HORIZONTES_RAIZ = (1, 5, 21, 63)


def precos():
    """Adj Close da cesta, preenchido para a frente por ativo (ADR-009)."""
    return retornos.precos_tratados()


def retornos_simples(p=None):
    p = precos() if p is None else p
    return p.pct_change(fill_method=None).iloc[1:]


def retornos_log(p=None):
    p = precos() if p is None else p
    return np.log(p / p.shift(1)).iloc[1:]


def queda_petr4():
    """A queda da PETR4 em 09/03/2020 e as alternativas do Peer Instruction.

    Cada distrator é um erro de conta comum, calculado sobre o mesmo número:
    repetir o retorno simples, usar ln(1 + |r|) com o sinal trocado e usar o
    logaritmo de base 10.
    """
    simples = float(retornos_simples()["PETR4"].loc[DATA_QUEDA])
    return {
        "data": DATA_QUEDA,
        "simples": simples,
        "log": float(retornos_log()["PETR4"].loc[DATA_QUEDA]),
        "erro_repetir_simples": simples,
        "erro_simetrico": -math.log(1 + abs(simples)),
        "erro_log10": math.log10(1 + simples),
    }


def piores_quedas(n=5):
    """Pior retorno simples diário de cada ativo, com a data e o log correspondente."""
    r = retornos_simples()
    lg = retornos_log()
    return pd.DataFrame({"data": r.idxmin(), "simples": r.min(), "log": lg.min()})


def estatisticas_diarias():
    r = retornos_simples()
    return pd.DataFrame({"media": r.mean(), "desvio": r.std(), "n": r.count()})


def anualizadas():
    """Retorno anualizado (média diária x 252), volatilidade (desvio x raiz de 252),
    retorno log anualizado e retorno total entre a primeira e a última cotação."""
    p = precos()
    r = retornos_simples(p)
    lg = retornos_log(p)
    total = p.apply(lambda s: s.dropna().iloc[-1] / s.dropna().iloc[0] - 1)
    return pd.DataFrame({
        "retorno_anual": r.mean() * PREGOES_ANO,
        "vol_anual": r.std() * np.sqrt(PREGOES_ANO),
        "log_anual": lg.mean() * PREGOES_ANO,
        "total": total,
        "inicio": p.apply(lambda s: s.first_valid_index()),
    })


def carregar_cdi():
    serie = pd.read_csv(os.path.join(DADOS, "cdi_diario.csv"), index_col="data", parse_dates=["data"])
    return serie["valor"] / 100


def cdi(inicio=None):
    """CDI acumulado e anualizado (base 252) a partir de inicio, até o fim da janela.

    Capitaliza a taxa diária de cada dia útil de cdi_diario.csv.
    """
    taxa = carregar_cdi()
    if inicio is not None:
        taxa = taxa.loc[inicio:]
    acumulado = float((1 + taxa).prod() - 1)
    return {
        "acumulado": acumulado,
        "anual": (1 + acumulado) ** (PREGOES_ANO / len(taxa)) - 1,
        "dias": len(taxa),
    }


def abaixo_do_cdi():
    """Ativos cujo retorno total ficou abaixo do CDI acumulado no mesmo período.

    O período de cada ativo começa na primeira cotação dele (GOLD11 em
    11/12/2020), e o CDI é acumulado a partir da mesma data.
    """
    a = anualizadas()
    return sorted(t for t in a.index if a.loc[t, "total"] < cdi(a.loc[t, "inicio"])["acumulado"])


def caudas(ticker=TICKER_CAUDAS):
    """Peso das caudas: a pior queda em desvios padrão e os pregões além de 3 desvios
    contra o que a distribuição normal preveria para a mesma amostra."""
    r = retornos_simples()[ticker].dropna()
    z = (r - r.mean()) / r.std()
    alem = z[z.abs() > 3]
    prob_normal = math.erfc(3 / math.sqrt(2))
    return {
        "n": len(r),
        "desvio": float(r.std()),
        "pior": float(r.min()),
        "pior_data": r.idxmin().strftime("%Y-%m-%d"),
        "pior_em_desvios": float(z.min()),
        "alem_3": int(len(alem)),
        "alem_3_normal": prob_normal * len(r),
        "alem_3_marco_2020": int((alem.index.strftime("%Y-%m") == "2020-03").sum()),
        "curtose": float(r.kurt()),
    }


def janela_crise(ticker="PETR4"):
    """Retornos de 20/02/2020 a 30/04/2020: a soma dos simples erra o acumulado e a
    soma dos log acerta o log do acumulado."""
    r = retornos_simples()[ticker].loc[CRISE_INICIO:CRISE_FIM]
    lg = retornos_log()[ticker].loc[CRISE_INICIO:CRISE_FIM]
    return {
        "pregoes": len(r),
        "soma_simples": float(r.sum()),
        "acumulado": float((1 + r).prod() - 1),
        "soma_log": float(lg.sum()),
    }


def vol_movel(ticker, janela):
    """Volatilidade anualizada em janela deslizante de `janela` pregões."""
    return retornos_simples()[ticker].rolling(janela).std() * np.sqrt(PREGOES_ANO)


def picos_2020(ticker):
    """Pico de cada janela em 2020: valor e data. A janela curta reage primeiro e mais alto."""
    saida = {}
    for janela in JANELAS:
        v = vol_movel(ticker, janela).loc["2020-01-01":"2020-12-31"]
        saida[janela] = {"pico": float(v.max()), "data": v.idxmax().strftime("%Y-%m-%d")}
    return saida


def raiz_do_tempo(ticker=TICKER_RAIZ, horizontes=HORIZONTES_RAIZ):
    """Desvio do retorno log acumulado em h pregões (janelas sobrepostas) contra a
    previsão da raiz do tempo, desvio diário x raiz de h."""
    lg = retornos_log()[ticker].dropna()
    diario = float(lg.std())
    return {h: {"medido": float(lg.rolling(h).sum().dropna().std()), "previsto": diario * math.sqrt(h)}
            for h in horizontes}


def descartar_contra_preencher():
    """Desafio do notebook: volatilidade anual com a cesta inteira em dropna."""
    ajustado = m1.carregar_precos("precos_ajustados.csv")
    descartar = ajustado.dropna().pct_change().std() * np.sqrt(PREGOES_ANO)
    preencher = retornos_simples().std() * np.sqrt(PREGOES_ANO)
    return pd.DataFrame({"descartar": descartar, "preencher": preencher,
                         "diferenca": descartar - preencher})


def maiores_movimentos(ticker, n=8):
    """Os n pregões de maior variação absoluta do ativo, com o retorno simples e o log.

    Alimenta o widget simples-log: nas quedas o log fica abaixo do simples, e nas
    altas também, porque ln(1 + r) < r para todo r diferente de zero.
    """
    r = retornos_simples()[ticker].dropna()
    lg = retornos_log()[ticker].dropna()
    datas = r.abs().sort_values(ascending=False).index[:n]
    return pd.DataFrame({"simples": r.loc[datas], "log": lg.loc[datas]})


def erro_da_soma_simples(ticker="PETR4"):
    """Quanto a soma dos retornos simples erra o acumulado na janela da crise,
    em pontos percentuais (positivo: a soma subestima a queda)."""
    j = janela_crise(ticker)
    return j["soma_simples"] - j["acumulado"]


def conta_anualizacao(ticker="PETR4"):
    """A conta do quadro no Bloco 5: média e desvio diários, os dois fatores e o
    resultado, mais o erro comum de multiplicar o desvio por 252."""
    e = estatisticas_diarias().loc[ticker]
    media, desvio = float(e["media"]), float(e["desvio"])
    return {
        "media_diaria": media,
        "desvio_diario": desvio,
        "raiz_252": math.sqrt(PREGOES_ANO),
        "retorno_anual": media * PREGOES_ANO,
        "vol_anual": desvio * math.sqrt(PREGOES_ANO),
        "erro_desvio_vezes_252": desvio * PREGOES_ANO,
    }


def extremos_da_cesta():
    """Quem lidera e quem fecha a cesta em retorno total e em volatilidade."""
    a = anualizadas()
    return {
        "maior_total": a["total"].idxmax(),
        "menor_total": a["total"].idxmin(),
        "maior_vol": a["vol_anual"].idxmax(),
        "menor_vol": a["vol_anual"].idxmin(),
        "ranking_vol": list(a["vol_anual"].sort_values(ascending=False).index),
    }


def pct(valor, casas=2):
    """0.123456 -> "12,35%", no formato do deck."""
    return ("%.*f%%" % (casas, valor * 100)).replace(".", ",")


# ---- Aula 02 redesenhada em 05/11/2026 (spec 2026-11-05-aula02-pontos-cegos) ----

def moeda_teorica(rodadas=10):
    """Jogo da moeda: cara rende +50%, coroa rende -40%, saldo inicial de R$ 100.

    A média do saldo cresce 5% por rodada; a mediana (metade das jogadas em cara)
    multiplica 1,5 x 0,6 = 0,9 a cada par de rodadas.
    """
    aritmetica = 0.5 * 0.5 + 0.5 * (-0.4)
    variancia = 0.5 * (0.5 - aritmetica) ** 2 + 0.5 * (-0.4 - aritmetica) ** 2
    return {
        "rodadas": rodadas,
        "media": 100 * 1.05 ** rodadas,
        "mediana": 100 * (1.5 * 0.6) ** (rodadas / 2),
        "aritmetica": aritmetica,
        "geometrica": (1.5 * 0.6) ** 0.5 - 1,
        "variancia": variancia,
        "aproximacao": aritmetica - variancia / 2,
    }


def reais(valor):
    """162.889 -> "R$ 162,89" e 1028.265 -> "R$ 1.028,27", no formato do deck (meio para cima)."""
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(repr(float(valor))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    inteiro, centavos = ("%.2f" % q).split(".")
    return "R$ " + "{:,}".format(int(inteiro)).replace(",", ".") + "," + centavos


def ponte_bbdc4(ticker="BBDC4", anos=range(2020, 2026)):
    """Retorno anual de fim de ano a fim de ano: média aritmética contra geométrica."""
    s = precos()[ticker].dropna()
    fins = s.groupby(s.index.year).last()
    anuais = fins.pct_change().loc[list(anos)]
    return {
        "anuais": {int(a): float(v) for a, v in anuais.items()},
        "anos": [int(a) for a in anuais.index],
        "aritmetica": float(anuais.mean()),
        "geometrica": float((1 + anuais).prod() ** (1 / len(anuais)) - 1),
    }


def afirmacoes_grupos():
    """Números que os assessores citam nas afirmações dos grupos, como aparecem no deck.

    Só a afirmação: o que a confirma ou desmonta fica no gabarito fora do repositório.
    """
    close = m1.carregar_precos("precos_fechamento.csv")
    bbas3 = close["BBAS3"].dropna()
    mglu3 = close["MGLU3"].dropna()
    vol_petr4 = anualizadas().loc["PETR4", "vol_anual"]
    return {
        "bbas3_close": pct(abs(bbas3.iloc[-1] / bbas3.iloc[0] - 1), 1),
        # Truncado: o assessor arredonda para baixo (a queda medida é de 90,7%).
        "mglu3_queda": "%d%%" % int(abs(mglu3.iloc[-1] / mglu3.iloc[0] - 1) * 100),
        "petr4_vol": "%d%%" % int(vol_petr4 * 100),
    }


def caso_suzb3(ticker="SUZB3", dia1="2022-07-19", dia2="2022-07-20", aporte=1000):
    """Caso real para o slide da lousa: SUZB3 sobe 5,00% num pregão e cai 2,07% no seguinte."""
    # A turma calcula com as taxas como aparecem na tela, em duas casas.
    r = retornos_simples()[ticker]
    r1, r2 = round(float(r.loc[dia1]), 4), round(float(r.loc[dia2]), 4)
    fmt = lambda d: pd.Timestamp(d).strftime("%d/%m/%Y")
    return {
        "dia1": fmt(dia1), "dia2": fmt(dia2), "r1": r1, "r2": r2,
        "soma": r1 + r2, "composto": (1 + r1) * (1 + r2) - 1,
        "depois1": round(aporte * (1 + r1), 6), "depois2": round(aporte * (1 + r1) * (1 + r2), 6),
    }


def bodie_comparacao(altas=(0.10, 0.30, 0.50), media=0.05, rodadas=10):
    """Três moedas com a mesma média aritmética de 5% por rodada e oscilações diferentes.

    Cara rende `alta`, coroa rende 2 x media - alta. A média geométrica e a
    aproximação do capítulo 5 (aritmética menos metade da variância) caem quanto
    mais a moeda oscila; saldo10 é o que o jogador típico (5 caras e 5 coroas)
    tem depois de 10 rodadas, começando com R$ 100.
    """
    linhas = []
    for alta in altas:
        baixa = 2 * media - alta
        variancia = ((alta - media) ** 2 + (baixa - media) ** 2) / 2
        geometrica = ((1 + alta) * (1 + baixa)) ** 0.5 - 1
        linhas.append({
            "alta": alta, "baixa": baixa, "aritmetica": (alta + baixa) / 2,
            "variancia": variancia, "geometrica": geometrica,
            "aproximacao": media - variancia / 2,
            "saldo10": 100 * (1 + geometrica) ** rodadas,
        })
    return linhas


def ponte_profunda(ticker="BBDC4", anos=range(2020, 2026), aporte=100):
    """O BBDC4 de 2020 a 2025 em três leituras para o slide da ponte.

    promessa: R$ 100 crescendo pela média aritmética; vivido: R$ 100 comprados no
    fim de 2019 e mantidos; imposto: metade da variância anual (ddof=0) contra a
    distância medida entre as duas médias; aportes: R$ 100 no início de cada ano,
    com o saldo de fim de ano e a taxa interna de retorno (retorno ponderado pelo
    dinheiro, capítulo 5).
    """
    base = ponte_bbdc4(ticker, anos)
    r = pd.Series(base["anuais"])
    n = len(r)
    promessa = [100 * (1 + base["aritmetica"]) ** k for k in range(n + 1)]
    vivido = [100.0] + list(100 * (1 + r).cumprod())
    saldo, aportes = 0.0, []
    for i, ano in enumerate(r.index):
        saldo = (saldo + aporte) * (1 + r[ano])
        aportes.append({"ano": int(ano), "aportado": aporte * (i + 1), "saldo": saldo})
    fluxo = [-aporte] * n + [saldo]

    def vpl(taxa):
        return sum(c / (1 + taxa) ** k for k, c in enumerate(fluxo))

    baixo, alto = -0.9, 1.0
    for _ in range(200):
        meio = (baixo + alto) / 2
        if vpl(meio) > 0:
            baixo = meio
        else:
            alto = meio
    return dict(base, promessa=promessa, vivido=vivido,
                imposto_regra=float(r.var(ddof=0) / 2),
                imposto_medido=base["aritmetica"] - base["geometrica"],
                aportes=aportes, tir=meio)


def moeda_sorte_sala(jogadores=30, rodadas=10):
    """Chance de a mediana de uma sala terminar acima de R$ 100 no jogo da moeda.

    Um jogador termina acima de R$ 100 com 6 caras ou mais em 10 rodadas. Com 30
    jogadores, a mediana é a média do 15º e do 16º saldo; ela passa de R$ 100
    quando 15 ou mais jogadores terminam acima.
    """
    from math import comb
    p = sum(comb(rodadas, k) for k in range(6, rodadas + 1)) / 2 ** rodadas
    minimo = jogadores // 2
    chance = sum(comb(jogadores, x) * p ** x * (1 - p) ** (jogadores - x) for x in range(minimo, jogadores + 1))
    return {"p_jogador": p, "chance": chance}
