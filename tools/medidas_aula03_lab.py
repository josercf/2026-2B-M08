"""Medições do deck da Aula 03 redesenhada em 10/11/2026 (ADR-017): Excel contra Python,
funções, gráficos e testes. Todo número do deck sai daqui e fica travado em
tools/tests/test_aula03_lab.py. O tratamento de ausência é o da ADR-009 (tools/retornos.py).
"""
import os

import numpy as np
import pandas as pd

import retornos as rt

RAIZ = rt.RAIZ
PREGOES_ANO = rt.PREGOES_ANO

# Carteira de demonstração: a mesma do notebook de treino da Ponderada 1, nenhuma da prova.
CARTEIRA_DEMO = {"BBAS3": 0.35, "BBDC4": 0.25, "VALE3": 0.15, "WEGE3": 0.15, "IVVB11": 0.10}
INICIO_DEMO, FIM_DEMO = "2022-01-01", "2023-12-31"


def pct(valor, casas=2):
    return ("{:." + str(casas) + "f}").format(100 * valor).replace(".", ",") + "%"


def dec(valor, casas=2):
    return ("{:." + str(casas) + "f}").format(valor).replace(".", ",")


# ---------------------------------------------------------------- Excel contra pandas
def lacuna_bova11():
    """O que a planilha faz com a célula vazia do BOVA11 em 24/10/2025.

    Uma fórmula =B3/B2-1 arrastada trata a célula vazia como zero: o retorno de 24/10 vira -100%
    e o de 27/10 vira #DIV/0!. O pandas marca a lacuna como NaN e a ADR-009 a preenche com o
    último preço, o que dá retorno zero em 24/10 e leva a variação dos dois dias para 27/10.
    """
    bruto = rt.precos_brutos()["BOVA11"]
    trecho = bruto.loc["2025-10-21":"2025-10-28"]
    certo = rt.retornos_por_ativo(["BOVA11"])["BOVA11"]
    # Imitação da planilha: vazio vira zero; a divisão por zero vira erro e sai da conta.
    planilha = bruto.fillna(0)
    r_planilha = (planilha / planilha.shift(1) - 1).replace([np.inf, -np.inf], np.nan).iloc[1:]
    return {
        "precos": trecho,
        "ret_planilha_2410": float(r_planilha.loc["2025-10-24"]),
        "ret_certo_2410": float(certo.loc["2025-10-24"]),
        "ret_certo_2710": float(certo.loc["2025-10-27"]),
        "vol_certa": float(rt.volatilidade_anual(certo)),
        "vol_planilha": float(r_planilha.dropna().std() * PREGOES_ANO ** 0.5),
    }


# ---------------------------------------------------------------- funções
def risco_dois_ativos(peso, vol_a, vol_b, rho):
    var = peso ** 2 * vol_a ** 2 + (1 - peso) ** 2 * vol_b ** 2 + 2 * peso * (1 - peso) * rho * vol_a * vol_b
    return float(np.sqrt(max(var, 0.0)))


def curva_risco_dois_ativos(passos=201):
    """Risco de dois ativos de 30% com metade em cada, para a correlação de -1 a 1 (slide #conta)."""
    rhos = np.linspace(-1.0, 1.0, passos)
    return rhos, np.array([risco_dois_ativos(0.5, 0.30, 0.30, r) for r in rhos])


def vol_carteira(retornos, pesos):
    w = np.array([pesos[c] for c in retornos.columns])
    return float(np.sqrt(w @ (retornos.cov().values * PREGOES_ANO) @ w))


def retornos_demo(ativos=None):
    return rt.retornos_janela_comum(list(ativos or CARTEIRA_DEMO), INICIO_DEMO, FIM_DEMO)


def retiradas_demo():
    """Volatilidade da carteira de demonstração e de cada carteira sem um ativo."""
    base = vol_carteira(retornos_demo(), CARTEIRA_DEMO)
    sem = {}
    for ativo in CARTEIRA_DEMO:
        resto = {k: v for k, v in CARTEIRA_DEMO.items() if k != ativo}
        total = sum(resto.values())
        resto = {k: v / total for k, v in resto.items()}
        sem[ativo] = vol_carteira(retornos_demo(resto), resto)
    return base, sem


def media_ponderada_demo():
    """Soma de peso x volatilidade anual de cada ativo, na mesma janela comum da carteira."""
    r = retornos_demo()
    vol = r.std() * np.sqrt(PREGOES_ANO)
    return float(sum(CARTEIRA_DEMO[a] * vol[a] for a in CARTEIRA_DEMO))


# ---------------------------------------------------------------- gráficos
def matriz_cesta():
    return rt.retornos_janela_comum().corr()


def par_extremo(maior=True):
    c = matriz_cesta()
    cols = list(c.columns)
    pares = [(c.loc[a, b], a, b) for i, a in enumerate(cols) for b in cols[i + 1:]]
    return max(pares) if maior else min(pares)


def bova_dolar():
    fe = pd.read_csv(os.path.join(rt.DADOS, "precos_fechamento.csv"), index_col="data", parse_dates=["data"])
    ptax = pd.read_csv(os.path.join(rt.DADOS, "ptax_venda.csv"), index_col="data", parse_dates=["data"])["valor"]
    t = pd.concat([fe["BOVA11"], ptax], axis=1, sort=True).dropna()
    t.columns = ["BOVA11", "DOLAR"]
    return t


def movel_bova_dolar(janela=252):
    t = bova_dolar()
    precos = t["BOVA11"].rolling(janela).corr(t["DOLAR"]).dropna()
    r = t.pct_change().dropna()
    rets = r["BOVA11"].rolling(janela).corr(r["DOLAR"]).dropna()
    return precos, rets


def resumo_bova_dolar():
    t = bova_dolar()
    r = t.pct_change().dropna()
    precos, rets = movel_bova_dolar()
    return {
        "corr_precos": float(t["BOVA11"].corr(t["DOLAR"])),
        "corr_retornos": float(r["BOVA11"].corr(r["DOLAR"])),
        "movel_precos_min": float(precos.min()), "movel_precos_max": float(precos.max()),
        "movel_ret_min": float(rets.min()), "movel_ret_max": float(rets.max()),
        "inicio": t.index[0].strftime("%d/%m/%Y"), "fim": t.index[-1].strftime("%d/%m/%Y"),
        "n": len(t),
    }


# ---------------------------------------------------------------- testes (caça ao bug)
def vol_anual_certa(r):
    return r.std() * np.sqrt(252)


def vol_anual_bug_365(r):
    return r.std() * np.sqrt(365)


def vol_anual_bug_sem_raiz(r):
    return r.std() * 252


def caca_ao_bug():
    """Volatilidade anual da PETR4 (série inteira) pela função certa e pelas duas com defeito."""
    r = rt.retornos_por_ativo(["PETR4"])["PETR4"].dropna()
    return {
        "certa": float(vol_anual_certa(r)),
        "bug_365": float(vol_anual_bug_365(r)),
        "bug_sem_raiz": float(vol_anual_bug_sem_raiz(r)),
    }


if __name__ == "__main__":
    print(lacuna_bova11())
    print("PI", risco_dois_ativos(0.5, 0.30, 0.30, 0.5))
    print("retiradas", retiradas_demo())
    print("par max", par_extremo(True), "par min", par_extremo(False))
    print(resumo_bova_dolar())
    print(caca_ao_bug())
