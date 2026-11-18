"""Simulador de carteiras da Aula 04, construído em seis turnos.

Cada função corresponde a um turno do SPEC.md:

    turno 1  retorno_do_dia(pesos, retornos_do_dia)
    turno 2  metricas(pesos, retornos)
    turno 3  sortear_pesos(k, rng)
    turno 4  simular(retornos, n, semente, rf)
    turno 5  simular dentro do requisito de tempo e posicionar(pesos, retornos, rf)
    turno 6  variancia_minima(retornos), maximo_sharpe(retornos, rf) e
             fronteira(retornos, pontos=50)

Os turnos 1 e 2 vêm do notebook do Colab, escritos à mão. Os turnos 3 a 5 são
implementados nesta pasta, um por vez, com o agente de codificação. O turno 6
(otimização de Markowitz) é feito depois do encontro, do mesmo modo, e usa o
SciPy: quem implementa acrescenta a importação de scipy.optimize.minimize.

Em todo o arquivo, `retornos` é uma tabela (DataFrame do pandas) com uma linha
por pregão e uma coluna por ativo, em fração: 1,23% é 0.0123.
"""
import numpy as np
import pandas as pd

PREGOES_ANO = 252


# --- Turno 1 -----------------------------------------------------------------

def retorno_do_dia(pesos, retornos_do_dia):
    """Retorno da carteira em um pregão.

    pesos: o peso de cada ativo (soma 1).
    retornos_do_dia: o retorno de cada ativo no pregão, na mesma ordem.
    Devolve um número: a soma de cada peso vezes o retorno do ativo no pregão.
    """
    raise NotImplementedError("turno 1: cole aqui a função escrita no Colab")


# Solução de reserva do turno 1. Só descomente se o professor liberar.
# Para usar: apague a função acima e tire o "# " das linhas abaixo.
#
# def retorno_do_dia(pesos, retornos_do_dia):
#     """Retorno da carteira em um pregão."""
#     return sum(peso * retorno for peso, retorno in zip(pesos, retornos_do_dia))


# --- Turno 2 -----------------------------------------------------------------

def metricas(pesos, retornos):
    """Retorno anual e risco anual da carteira em N pregões.

    pesos: o peso de cada ativo, na ordem das colunas de `retornos`.
    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    Devolve dois números, nesta ordem: (retorno_anual, risco_anual).

    Retorno anual: média dos retornos diários da carteira vezes 252.
    Risco anual: desvio padrão amostral (ddof=1) dos retornos diários da
    carteira vezes a raiz de 252.
    """
    raise NotImplementedError("turno 2: cole aqui a função escrita no Colab")


# Solução de reserva do turno 2. Só descomente se o professor liberar.
# Para usar: apague a função acima e tire o "# " das linhas abaixo.
#
# def metricas(pesos, retornos):
#     """Retorno anual e risco anual da carteira em N pregões."""
#     diarios = [retorno_do_dia(pesos, linha) for linha in np.asarray(retornos, dtype=float)]
#     return np.mean(diarios) * PREGOES_ANO, np.std(diarios, ddof=1) * np.sqrt(PREGOES_ANO)


# --- Turno 3 -----------------------------------------------------------------

def sortear_pesos(k, rng):
    """Sorteia os pesos de uma carteira de k ativos.

    k: número de ativos da carteira.
    rng: gerador aleatório do NumPy, criado com np.random.default_rng(semente).
    Devolve um vetor do NumPy com k pesos não negativos que somam 1.

    A especificação completa está no SPEC.md, turno 3.
    """
    raise NotImplementedError("turno 3: sortear_pesos ainda não foi implementada")


# --- Turno 4 -----------------------------------------------------------------

def simular(retornos, n, semente, rf):
    """Sorteia n carteiras e calcula retorno, risco e Sharpe de cada uma.

    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    n: número de carteiras a sortear.
    semente: número inteiro que fixa o sorteio.
    rf: taxa livre de risco anual, em fração (o valor da aula está em dados/rf.txt).
    Devolve uma tabela (DataFrame) com uma linha por carteira e as colunas
    w_<ticker> (uma por ativo, na ordem das colunas de `retornos`), retorno,
    risco e sharpe, nesta ordem.

    A dupla completa a especificação no SPEC.md, turno 4, antes de implementar.
    """
    raise NotImplementedError("turno 4: simular ainda não foi implementada")


# --- Turno 5 -----------------------------------------------------------------

def posicionar(pesos, retornos, rf):
    """Calcula retorno, risco e Sharpe de uma carteira dada, para marcar na nuvem.

    pesos: o peso de cada ativo, na ordem das colunas de `retornos`.
    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    rf: taxa livre de risco anual, em fração.
    Devolve um dicionário com as chaves "retorno", "risco" e "sharpe".

    A dupla completa a especificação no SPEC.md, turno 5, antes de implementar.
    """
    raise NotImplementedError("turno 5: posicionar ainda não foi implementada")


# --- Turno 6 (depois do encontro) --------------------------------------------

def variancia_minima(retornos):
    """Pesos da carteira de menor risco anual.

    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    Devolve um vetor do NumPy com um peso por ativo, na ordem das colunas de
    `retornos`. Nenhum peso é negativo, cada peso fica entre 0 e 1 e a soma é 1.

    A otimização usa scipy.optimize.minimize com o método SLSQP, partindo de
    pesos iguais. A especificação completa está no SPEC.md, turno 6.
    """
    raise NotImplementedError("turno 6: variancia_minima ainda não foi implementada")


def maximo_sharpe(retornos, rf):
    """Pesos da carteira de maior Índice de Sharpe.

    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    rf: taxa livre de risco anual, em fração.
    Devolve um vetor do NumPy com um peso por ativo, com as mesmas restrições
    de variancia_minima.

    A especificação completa está no SPEC.md, turno 6.
    """
    raise NotImplementedError("turno 6: maximo_sharpe ainda não foi implementada")


def fronteira(retornos, pontos=50):
    """Fronteira eficiente: a carteira de menor risco para cada retorno alvo.

    retornos: tabela com uma linha por pregão e uma coluna por ativo.
    pontos: número de retornos alvo, igualmente espaçados do retorno da
    carteira de variância mínima até o maior retorno anual entre os ativos.
    Devolve uma tabela (DataFrame) com uma linha por retorno alvo, em ordem
    crescente de retorno, e as colunas w_<ticker> (uma por ativo, na ordem das
    colunas de `retornos`), retorno e risco, nesta ordem.

    A especificação completa está no SPEC.md, turno 6.
    """
    raise NotImplementedError("turno 6: fronteira ainda não foi implementada")
