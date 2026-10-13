"""Medições da Aula 05 (Validação e Robustez do Modelo) sobre os CSVs de dados/.

O otimizador da Aula 04 (SLSQP, pesos que somam 1, sem venda a descoberto)
rodado numa janela de treino e testado fora da amostra: esperado contra
realizado, drawdown no período de teste, estabilidade dos pesos entre janelas e
sensibilidade da carteira ao retorno esperado e ao estimador de covariância.
Todo número que o deck, o notebook, os widgets e as animações da Aula 05 citam
sai daqui e está travado em tools/tests/test_aula05.py.

Decisões declaradas (valem para todo número da aula):

- Preço e ausências: tratamento único do módulo (ADR-009), de tools/retornos.py.
  Adj Close de precos_ajustados.csv, os 15 ativos da cesta de referência; lacuna
  isolada preenchida com o último preço (ffill), nada preenchido antes da
  primeira cotação, e a análise conjunta na janela comum dos 15 ativos
  (retornos_janela_comum).
- Período do estudo: de 04/01/2021, primeiro pregão de 2021, a 31/08/2026. A
  janela comum dos 15 ativos começa em 14/12/2020, por causa do GOLD11; começar
  em 2021 é escolha de desenho do estudo, que deixa as janelas em anos civis
  inteiros. São 1.412 retornos, de 04/01/2021 a 31/08/2026; o primeiro mede a
  variação desde o último pregão de 2020.
- Dentro do período há uma data com lacuna, 24/10/2025 (BOVA11, IVVB11 e GOLD11
  sem cotação). Ela fica na amostra com o preço do dia anterior: retorno zero
  nesses três ETFs nesse dia, e o pregão seguinte leva a variação dos dois dias.
- Retorno e risco anualizados por 252 pregões: média aritmética diária vezes
  252 e desvio-padrão diário vezes raiz de 252, iguais no treino e no teste para
  que esperado e realizado sejam comparáveis.
- Taxa livre de risco: CDI diário (SGS 12) composto nas datas da própria janela
  e anualizado por 252.
- No teste, os pesos ficam constantes (rebalanceamento diário implícito no
  produto retornos @ pesos). O drawdown é medido sobre o patrimônio acumulado
  dessa carteira, a partir de 1 no primeiro pregão do teste.
- Divisão principal: treino de 02/01/2023 a 30/12/2024 (24 meses) e teste no
  último ano civil completo da janela, 2025.
- Janelas deslizantes: treino de 24 meses e teste nos 12 meses seguintes, com
  passo de um mês, do treino iniciado em 01/2021 ao iniciado em 09/2023.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import retornos  # noqa: E402

RAIZ = retornos.RAIZ
DADOS = retornos.DADOS
PREGOES_ANO = retornos.PREGOES_ANO

INICIO_ESTUDO = "2021-01-01"
TREINO = ("2023-01-01", "2024-12-31")
TESTE = ("2025-01-01", "2025-12-31")
MESES_TREINO = 24
MESES_TESTE = 12
# Perturbação do bloco 5: cada retorno esperado anual sobe ou desce 5 pontos
# percentuais, com o sinal sorteado por semente fixa.
PERTURBACAO = 0.05
SEMENTE = 8
# Duas janelas de treino sem sobreposição, para a medida de estabilidade.
JANELA_A = ("2021-01-01", "2022-12-31")
JANELA_B = ("2023-01-01", "2024-12-31")
# Três janelas do desafio do notebook, contíguas, de 12 meses cada.
TRES_JANELAS = (("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"),
                ("2024-01-01", "2024-12-31"))

OBJETIVOS = ("max_sharpe", "var_min")


def carregar_retornos():
    """Retornos diários dos 15 ativos na janela comum, de 04/01/2021 a 31/08/2026 (ADR-009)."""
    return retornos.retornos_janela_comum(inicio=INICIO_ESTUDO)


def datas_preenchidas():
    """Pregões do período do estudo em que algum ativo teve a lacuna preenchida."""
    lacunas = retornos.lacunas_preenchidas()
    return sorted(set(lacunas.loc[INICIO_ESTUDO:].index))


def carregar_cdi():
    """CDI diário como fração (o CSV traz a taxa em %)."""
    cdi = pd.read_csv(os.path.join(DADOS, "cdi_diario.csv"), index_col="data", parse_dates=["data"])
    return cdi["valor"] / 100


def cdi_anual(datas):
    """CDI composto nas datas dadas e anualizado por 252 pregões."""
    taxas = carregar_cdi().reindex(datas)
    if taxas.isna().any():
        raise ValueError("CDI ausente em %d datas" % int(taxas.isna().sum()))
    return float((1 + taxas).prod() ** (PREGOES_ANO / len(taxas)) - 1)


def ledoit_wolf(retornos):
    """Covariância diária encolhida de Ledoit e Wolf (2004), alvo mu * identidade.

    Mesma conta do sklearn.covariance.LedoitWolf (dados centrados, covariância
    empírica dividida por n), escrita em numpy para não exigir o scikit-learn.
    Devolve (covariância, intensidade do encolhimento).
    """
    x = np.asarray(retornos, dtype=float)
    x = x - x.mean(axis=0)
    n, p = x.shape
    emp = x.T @ x / n
    mu = np.trace(emp) / p
    delta = ((emp - mu * np.eye(p)) ** 2).sum() / p
    x2 = x ** 2
    beta_bar = ((x2.T @ x2) / n - emp ** 2).sum() / (p * n)
    beta = min(beta_bar, delta)
    encolhimento = 0.0 if delta == 0 else beta / delta
    return encolhimento * mu * np.eye(p) + (1 - encolhimento) * emp, encolhimento


def estimar(retornos, estimador="amostral"):
    """(retorno esperado anual, covariância anual) a partir de retornos diários."""
    mu = retornos.mean().to_numpy() * PREGOES_ANO
    if estimador == "amostral":
        cov = retornos.cov().to_numpy() * PREGOES_ANO
    elif estimador == "ledoit-wolf":
        cov = ledoit_wolf(retornos.to_numpy())[0] * PREGOES_ANO
    else:
        raise ValueError(estimador)
    return mu, cov


def otimizar(mu, cov, rf, objetivo):
    """Pesos ótimos por SLSQP: soma 1, cada peso entre 0 e 1 (sem venda a descoberto)."""
    n = len(mu)
    if objetivo == "var_min":
        def custo(w):
            return w @ cov @ w
    elif objetivo == "max_sharpe":
        def custo(w):
            return -(w @ mu - rf) / np.sqrt(w @ cov @ w)
    else:
        raise ValueError(objetivo)
    # Tolerância apertada primeiro. Em algumas janelas o SLSQP para com
    # "Positive directional derivative for linesearch" já em cima do ótimo, por
    # pedir precisão maior do que a busca consegue; a tolerância seguinte resolve.
    for tolerancia in (1e-12, 1e-10, 1e-8):
        resultado = minimize(custo, np.full(n, 1 / n), method="SLSQP", bounds=[(0, 1)] * n,
                             constraints=({"type": "eq", "fun": lambda w: w.sum() - 1},),
                             options={"ftol": tolerancia, "maxiter": 1000})
        if resultado.success:
            w = np.clip(resultado.x, 0, None)
            return w / w.sum()
    raise RuntimeError(resultado.message)


def esperado(w, mu, cov, rf):
    retorno = float(w @ mu)
    vol = float(np.sqrt(w @ cov @ w))
    return {"retorno": retorno, "vol": vol, "sharpe": (retorno - rf) / vol}


def realizado(w, retornos_teste):
    """Métricas fora da amostra da carteira de pesos constantes."""
    diario = pd.Series(retornos_teste.to_numpy() @ w, index=retornos_teste.index)
    retorno = float(diario.mean() * PREGOES_ANO)
    vol = float(diario.std() * np.sqrt(PREGOES_ANO))
    rf = cdi_anual(retornos_teste.index)
    patrimonio = (1 + diario).cumprod()
    queda = patrimonio / patrimonio.cummax() - 1
    return {
        "retorno": retorno,
        "vol": vol,
        "sharpe": (retorno - rf) / vol,
        "rf": rf,
        "retorno_acumulado": float(patrimonio.iloc[-1] - 1),
        "drawdown_max": float(queda.min()),
        "data_fundo": queda.idxmin(),
        "patrimonio": patrimonio,
        "drawdown": queda,
    }


def backtest(treino, teste, estimador="amostral"):
    """Otimiza as duas carteiras no treino e mede as duas no teste."""
    retornos = carregar_retornos()
    r_treino = retornos.loc[treino[0]:treino[1]]
    r_teste = retornos.loc[teste[0]:teste[1]]
    mu, cov = estimar(r_treino, estimador)
    rf = cdi_anual(r_treino.index)
    saida = {"ativos": list(retornos.columns), "rf_treino": rf,
             "pregoes_treino": len(r_treino), "pregoes_teste": len(r_teste)}
    for objetivo in OBJETIVOS:
        w = otimizar(mu, cov, rf, objetivo)
        saida[objetivo] = {"pesos": w, "esperado": esperado(w, mu, cov, rf),
                           "realizado": realizado(w, r_teste)}
    return saida


def principal():
    """Divisão principal da aula: treino 2023 e 2024, teste 2025."""
    return backtest(TREINO, TESTE)


def rotatividade(w1, w2):
    """Fração da carteira que precisa trocar de mãos para ir de w1 a w2."""
    return float(0.5 * np.abs(np.asarray(w1) - np.asarray(w2)).sum())


def _fim_do_mes(inicio, meses):
    return (pd.Timestamp(inicio) + pd.DateOffset(months=meses)) - pd.Timedelta(days=1)


def janelas_deslizantes():
    """Treino de 24 meses e teste nos 12 seguintes, deslizando de mês em mês.

    Para quando o teste passaria do último pregão do snapshot.
    """
    ultimo = carregar_retornos().index[-1]
    janelas = []
    inicio = pd.Timestamp(INICIO_ESTUDO)
    while True:
        fim_treino = _fim_do_mes(inicio, MESES_TREINO)
        inicio_teste = fim_treino + pd.Timedelta(days=1)
        fim_teste = _fim_do_mes(inicio_teste, MESES_TESTE)
        if fim_teste > ultimo + pd.offsets.MonthEnd(0):
            break
        janelas.append(((inicio, fim_treino), (inicio_teste, fim_teste)))
        inicio = inicio + pd.DateOffset(months=1)
    return janelas


def resultados_deslizantes():
    """Backtest de cada janela deslizante, na ordem do tempo."""
    return [dict(backtest(treino, teste), treino=treino, teste=teste)
            for treino, teste in janelas_deslizantes()]


def resumo_deslizante(resultados=None):
    """Quantas janelas entregaram menos Sharpe do que prometeram, e a rotatividade mês a mês."""
    resultados = resultados if resultados is not None else resultados_deslizantes()
    resumo = {"janelas": len(resultados)}
    for objetivo in OBJETIVOS:
        prometido = np.array([r[objetivo]["esperado"]["sharpe"] for r in resultados])
        entregue = np.array([r[objetivo]["realizado"]["sharpe"] for r in resultados])
        pesos = [r[objetivo]["pesos"] for r in resultados]
        giro = [rotatividade(a, b) for a, b in zip(pesos[:-1], pesos[1:])]
        resumo[objetivo] = {
            "abaixo_do_prometido": int((entregue < prometido).sum()),
            "abaixo_do_cdi": int((entregue < 0).sum()),
            "sharpe_prometido_mediano": float(np.median(prometido)),
            "sharpe_entregue_mediano": float(np.median(entregue)),
            "rotatividade_mensal_mediana": float(np.median(giro)),
            "rotatividade_mensal_maxima": float(np.max(giro)),
        }
    return resumo


def pesos_na_janela(janela, objetivo, estimador="amostral"):
    retornos = carregar_retornos().loc[janela[0]:janela[1]]
    mu, cov = estimar(retornos, estimador)
    return otimizar(mu, cov, cdi_anual(retornos.index), objetivo)


def estabilidade_duas_janelas():
    """Pesos das duas carteiras em 2021-2022 contra 2023-2024, e a rotatividade entre elas."""
    ativos = list(carregar_retornos().columns)
    saida = {}
    for objetivo in OBJETIVOS:
        a = pesos_na_janela(JANELA_A, objetivo)
        b = pesos_na_janela(JANELA_B, objetivo)
        saida[objetivo] = {"a": dict(zip(ativos, a)), "b": dict(zip(ativos, b)),
                           "rotatividade": rotatividade(a, b)}
    return saida


def tres_janelas():
    """Pesos de máximo Sharpe em três anos civis seguidos (desafio do notebook)."""
    ativos = list(carregar_retornos().columns)
    return [dict(zip(ativos, pesos_na_janela(j, "max_sharpe"))) for j in TRES_JANELAS]


def sinais_perturbacao(n):
    return np.random.default_rng(SEMENTE).choice([-1.0, 1.0], n)


def sensibilidade():
    """Na janela de treino principal: retorno esperado perturbado contra Ledoit-Wolf."""
    retornos = carregar_retornos().loc[TREINO[0]:TREINO[1]]
    ativos = list(retornos.columns)
    mu, cov = estimar(retornos)
    _, cov_lw = estimar(retornos, "ledoit-wolf")
    rf = cdi_anual(retornos.index)
    mu_perturbado = mu + PERTURBACAO * sinais_perturbacao(len(mu))
    anos = len(retornos) / PREGOES_ANO
    erro_padrao = np.sqrt(np.diag(cov)) / np.sqrt(anos)
    saida = {"ativos": ativos,
             "encolhimento": ledoit_wolf(retornos.to_numpy())[1],
             "erro_padrao_mediano": float(np.median(erro_padrao)),
             "erro_padrao": dict(zip(ativos, erro_padrao))}
    for objetivo in OBJETIVOS:
        base = otimizar(mu, cov, rf, objetivo)
        perturbado = otimizar(mu_perturbado, cov, rf, objetivo)
        lw = otimizar(mu, cov_lw, rf, objetivo)
        saida[objetivo] = {
            "base": dict(zip(ativos, base)),
            "perturbado": dict(zip(ativos, perturbado)),
            "ledoit_wolf": dict(zip(ativos, lw)),
            "rotatividade_perturbado": rotatividade(base, perturbado),
            "rotatividade_ledoit_wolf": rotatividade(base, lw),
        }
    return saida


def maiores_pesos(pesos, k=4, minimo=0.005):
    """Os k maiores pesos acima do mínimo, do maior para o menor."""
    itens = sorted(pesos.items(), key=lambda par: -par[1])
    return [(t, float(w)) for t, w in itens[:k] if w > minimo]


def cdi_no_periodo(inicio, fim):
    """Patrimônio do CDI composto em todas as datas do SGS 12 entre inicio e fim, inclusive.

    Começa em 1 antes do primeiro dia, como a carteira no teste. Usa todas as
    datas do CDI entre inicio e fim.
    """
    taxas = carregar_cdi().loc[inicio:fim]
    return (1 + taxas).cumprod()


def cdi_acumulado_no_teste(teste=TESTE):
    """CDI acumulado entre o primeiro e o último pregão do teste da divisão principal."""
    datas = carregar_retornos().loc[teste[0]:teste[1]].index
    return float(cdi_no_periodo(datas[0], datas[-1]).iloc[-1] - 1)


def ativos_destaque(resultados, objetivo, k=5):
    """Os k ativos de maior peso médio entre as janelas deslizantes, do maior para o menor."""
    ativos = resultados[0]["ativos"]
    media = np.mean([r[objetivo]["pesos"] for r in resultados], axis=0)
    ordem = np.argsort(-media)[:k]
    return [(ativos[i], float(media[i])) for i in ordem]


def janela_da_divisao_principal(resultados):
    """Posição, entre as janelas deslizantes, da janela igual à divisão principal."""
    for i, r in enumerate(resultados):
        if r["treino"][0] == pd.Timestamp(TREINO[0]):
            return i
    raise ValueError("divisão principal fora das janelas deslizantes")
