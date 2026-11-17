"""Testes de aceite do professor para os cinco turnos do simulador.

Uso:
    python conferir.py        confere os cinco turnos
    python conferir.py 3      confere só o turno 3

Imprime "TURNO n: OK" quando o turno passa e sai com código 0. Quando falta
alguma coisa, imprime "TURNO n: AINDA NÃO" com a lista do que falta e sai com
código 1.

Este arquivo é do professor e não deve ser editado. Ele verifica propriedades
do resultado: soma dos pesos, formato da tabela, repetição com a mesma semente
e tempo. Nenhuma verificação depende do valor de um sorteio específico. Usa só
a biblioteca padrão, NumPy e pandas, e lê apenas os arquivos da pasta dados/.
"""
import importlib
import os
import sys
import time

import numpy as np
import pandas as pd

PASTA = os.path.dirname(os.path.abspath(__file__))
PREGOES_ANO = 252
EXATO = 1e-8
LIMITE_SEGUNDOS = 10.0


class Falta(Exception):
    """A função não pôde ser avaliada; a mensagem diz o que falta."""


# --- dados e referência -------------------------------------------------------

def carregar_precos():
    return pd.read_csv(os.path.join(PASTA, "dados", "precos.csv"), index_col="data")


def carregar_rf():
    with open(os.path.join(PASTA, "dados", "rf.txt"), encoding="utf-8") as arquivo:
        return float(arquivo.read().strip())


def tabela_de_retornos(precos, ativos, pregoes):
    """Retornos diários dos últimos `pregoes` pregões, na janela comum dos ativos."""
    comum = precos[list(ativos)].dropna()
    return comum.pct_change().iloc[1:].tail(pregoes)


def serie_da_carteira(pesos, retornos):
    """Referência do professor: a série diária da carteira, calculada com pandas."""
    return retornos.mul(np.asarray(pesos, dtype=float), axis=1).sum(axis=1)


def referencia_metricas(pesos, retornos):
    serie = serie_da_carteira(pesos, retornos)
    return (float(serie.mean() * PREGOES_ANO),
            float(serie.std(ddof=1) * np.sqrt(PREGOES_ANO)))


def pct(valor, casas=2):
    return ("%.*f%%" % (casas, 100 * float(valor))).replace(".", ",")


# --- chamada protegida ----------------------------------------------------------

def obter(modulo, nome):
    funcao = getattr(modulo, nome, None)
    if not callable(funcao):
        raise Falta("simulador.py não tem a função %s. Confira o nome e a assinatura no SPEC.md."
                    % nome)
    return funcao


def chamar(funcao, *argumentos):
    """Chama a função da dupla. Erro vira item da lista do que falta, sem traceback."""
    nome = getattr(funcao, "__name__", "a função")
    try:
        valor = funcao(*argumentos)
    except NotImplementedError:
        raise Falta("%s ainda não foi implementada: o corpo levanta NotImplementedError." % nome)
    except Exception as erro:
        raise Falta("%s parou com o erro %s: %s." % (nome, type(erro).__name__, erro))
    if valor is None:
        raise Falta("%s não devolveu nada. Falta o return com o resultado." % nome)
    return valor


def espera_erro(funcao, argumentos, descricao):
    """Devolve None se a função levanta ValueError, ou o texto do que falta."""
    nome = getattr(funcao, "__name__", "a função")
    try:
        funcao(*argumentos)
    except ValueError:
        return None
    except NotImplementedError:
        return "%s ainda não foi implementada: o corpo levanta NotImplementedError." % nome
    except Exception as erro:
        return ("%s: %s deve levantar ValueError com uma mensagem clara, e levantou %s."
                % (descricao, nome, type(erro).__name__))
    return ("%s: %s deve recusar essa entrada levantando ValueError, e devolveu um resultado."
            % (descricao, nome))


def numero(valor, nome):
    try:
        resultado = float(valor)
    except (TypeError, ValueError):
        raise Falta("%s devolveu %r, e o esperado é um número." % (nome, valor))
    if resultado != resultado:
        raise Falta("%s devolveu NaN (um valor que não é número)." % nome)
    return resultado


# --- turno 1 --------------------------------------------------------------------

def turno1(sim, precos, rf):
    faltas = []
    funcao = obter(sim, "retorno_do_dia")
    retornos = tabela_de_retornos(precos, ["PETR4", "VALE3", "ITUB4"], 9)
    casos = [("pesos de 50%, 30% e 20%", [0.5, 0.3, 0.2]),
             ("carteira só de PETR4", [1.0, 0.0, 0.0])]
    for descricao, pesos in casos:
        serie = serie_da_carteira(pesos, retornos)
        for posicao in (0, len(retornos) - 1):
            linha = retornos.iloc[posicao].to_numpy()
            valor = numero(chamar(funcao, np.array(pesos), linha), "retorno_do_dia")
            esperado = float(serie.iloc[posicao])
            if abs(valor - esperado) > EXATO:
                if abs(valor - linha.sum()) <= EXATO:
                    motivo = " O que veio é a soma dos retornos, sem os pesos."
                elif abs(valor - linha.mean()) <= EXATO:
                    motivo = " O que veio é a média simples dos retornos, sem os pesos."
                else:
                    motivo = ""
                faltas.append(
                    "Com %s, no pregão de %s, retorno_do_dia devolveu %s e o esperado é %s.%s "
                    "O retorno da carteira no pregão é a soma de cada peso vezes o retorno do "
                    "ativo naquele dia." % (descricao, retornos.index[posicao], pct(valor, 4),
                                            pct(esperado, 4), motivo))
                break
    return faltas


# --- turno 2 --------------------------------------------------------------------

def turno2(sim, precos, rf):
    faltas = []
    funcao = obter(sim, "metricas")
    retornos = tabela_de_retornos(precos, ["PETR4", "VALE3", "ITUB4"], 63)
    casos = [("pesos de 50%, 30% e 20%", [0.5, 0.3, 0.2]),
             ("carteira só de VALE3", [0.0, 1.0, 0.0])]
    for descricao, pesos in casos:
        valor = chamar(funcao, np.array(pesos), retornos)
        try:
            retorno, risco = valor
        except (TypeError, ValueError):
            raise Falta("metricas devolveu %r, e o esperado são dois números, nesta ordem: "
                        "retorno anual e risco anual." % (valor,))
        retorno = numero(retorno, "metricas (retorno anual)")
        risco = numero(risco, "metricas (risco anual)")
        serie = serie_da_carteira(pesos, retornos)
        ref_retorno, ref_risco = referencia_metricas(pesos, retornos)
        if abs(retorno - ref_retorno) > EXATO:
            if abs(retorno - serie.mean()) <= EXATO:
                motivo = "O que veio é a média diária: falta multiplicar por 252."
            else:
                motivo = "A definição é a média dos retornos diários da carteira vezes 252."
            faltas.append("Com %s, o retorno anual veio %s e o esperado é %s. %s"
                          % (descricao, pct(retorno), pct(ref_retorno), motivo))
        if abs(risco - ref_risco) > EXATO:
            if abs(risco - serie.std(ddof=0) * np.sqrt(PREGOES_ANO)) <= EXATO:
                motivo = ("O que veio é o desvio padrão populacional. A definição pede o "
                          "amostral: use ddof=1.")
            elif abs(risco - serie.std(ddof=1)) <= EXATO:
                motivo = "O que veio é o desvio padrão diário: falta multiplicar pela raiz de 252."
            elif abs(risco - serie.std(ddof=1) * PREGOES_ANO) <= EXATO:
                motivo = "O risco anualiza pela raiz de 252, e o que veio foi multiplicado por 252."
            else:
                motivo = ("A definição é o desvio padrão amostral (ddof=1) dos retornos diários "
                          "da carteira vezes a raiz de 252.")
            faltas.append("Com %s, o risco anual veio %s e o esperado é %s. %s"
                          % (descricao, pct(risco), pct(ref_risco), motivo))
        if faltas:
            break
    return faltas


# --- turno 3 --------------------------------------------------------------------

def _pesos(valor, k, origem):
    """Converte para vetor e devolve (vetor, faltas de formato, soma e sinal)."""
    faltas = []
    try:
        pesos = np.asarray(valor, dtype=float)
    except (TypeError, ValueError):
        raise Falta("%s devolveu %r, e o esperado é um vetor de números." % (origem, valor))
    if pesos.shape != (k,):
        raise Falta("%s devolveu um resultado de formato %s, e o esperado é um vetor com %d "
                    "pesos, um por ativo." % (origem, pesos.shape, k))
    if (pesos < 0).any():
        faltas.append("%s devolveu peso negativo (%.4f). Nenhum peso pode ser menor que zero: "
                      "a carteira não vende a descoberto." % (origem, pesos.min()))
    if abs(pesos.sum() - 1) > 1e-9:
        faltas.append("%s devolveu pesos que somam %.4f, e os pesos de uma carteira precisam "
                      "somar 1. Divida cada número sorteado pela soma de todos."
                      % (origem, pesos.sum()))
    return pesos, faltas


def turno3(sim, precos, rf):
    faltas = []
    funcao = obter(sim, "sortear_pesos")
    for k in (2, 5, 20):
        origem = "sortear_pesos(%d, rng)" % k
        pesos, problemas = _pesos(chamar(funcao, k, np.random.default_rng(42)), k, origem)
        if problemas:
            return problemas
        de_novo, _ = _pesos(chamar(funcao, k, np.random.default_rng(42)), k, origem)
        outra, _ = _pesos(chamar(funcao, k, np.random.default_rng(43)), k, origem)
        if not np.allclose(pesos, de_novo, atol=1e-12):
            faltas.append("%s devolveu pesos diferentes em duas chamadas com geradores de mesma "
                          "semente. O sorteio precisa sair do gerador recebido no argumento rng, "
                          "e de nenhum outro." % origem)
            break
        if np.allclose(pesos, outra, atol=1e-12):
            faltas.append("%s devolveu os mesmos pesos com sementes diferentes. Os pesos "
                          "precisam ser sorteados com o gerador recebido no argumento rng." % origem)
            break
    if not faltas:
        gerador = np.random.default_rng(7)
        primeira = np.asarray(chamar(funcao, 5, gerador), dtype=float)
        segunda = np.asarray(chamar(funcao, 5, gerador), dtype=float)
        if np.allclose(primeira, segunda, atol=1e-12):
            faltas.append("Duas chamadas seguidas com o mesmo gerador devolveram os mesmos pesos. "
                          "Cada chamada precisa consumir números novos do rng.")
    um, problemas = _pesos(chamar(funcao, 1, np.random.default_rng(1)), 1, "sortear_pesos(1, rng)")
    faltas.extend(problemas)
    recusa = espera_erro(funcao, (0, np.random.default_rng(1)), "Caso de borda k = 0 (SPEC.md)")
    if recusa:
        faltas.append(recusa)
    return faltas


# --- turno 4 --------------------------------------------------------------------

def _tabela(valor, retornos, n, origem):
    """Confere o formato da tabela devolvida por simular. Devolve (tabela, colunas de peso)."""
    if not isinstance(valor, pd.DataFrame):
        raise Falta("%s devolveu %s, e o esperado é uma tabela (DataFrame do pandas)."
                    % (origem, type(valor).__name__))
    colunas_peso = ["w_%s" % ativo for ativo in retornos.columns]
    esperadas = colunas_peso + ["retorno", "risco", "sharpe"]
    if list(valor.columns) != esperadas:
        raise Falta("%s devolveu as colunas %s, e o esperado é %s, nesta ordem."
                    % (origem, list(valor.columns), esperadas))
    if len(valor) != n:
        raise Falta("%s devolveu %d linhas, e o esperado é uma linha por carteira sorteada: %d."
                    % (origem, len(valor), n))
    return valor, colunas_peso


def turno4(sim, precos, rf):
    faltas = []
    funcao = obter(sim, "simular")
    retornos = tabela_de_retornos(precos, ["PETR4", "VALE3", "ITUB4", "WEGE3"], 126)
    n = 200
    origem = "simular(retornos, %d, 7, rf)" % n
    tabela, colunas_peso = _tabela(chamar(funcao, retornos, n, 7, rf), retornos, n, origem)
    pesos = tabela[colunas_peso].to_numpy(dtype=float)
    if (pesos < 0).any():
        faltas.append("%s sorteou peso negativo (%.4f). Nenhum peso pode ser menor que zero."
                      % (origem, pesos.min()))
    somas = pesos.sum(axis=1)
    if np.abs(somas - 1).max() > 1e-9:
        pior = somas[np.abs(somas - 1).argmax()]
        faltas.append("%s tem carteira cujos pesos somam %.4f, e os pesos de cada linha precisam "
                      "somar 1." % (origem, pior))
    if faltas:
        return faltas
    if len(np.unique(pesos.round(12), axis=0)) < n:
        faltas.append("%s repetiu carteiras: cada linha precisa de um sorteio novo de pesos."
                      % origem)
    for posicao in (0, n // 2, n - 1):
        ref_retorno, ref_risco = referencia_metricas(pesos[posicao], retornos)
        linha = tabela.iloc[posicao]
        if abs(float(linha["retorno"]) - ref_retorno) > EXATO:
            faltas.append("Na linha %d, a coluna retorno vale %s e o retorno anual desses pesos é "
                          "%s. Use a definição do turno 2: média diária da carteira vezes 252."
                          % (posicao, pct(linha["retorno"]), pct(ref_retorno)))
            break
        if abs(float(linha["risco"]) - ref_risco) > EXATO:
            faltas.append("Na linha %d, a coluna risco vale %s e o risco anual desses pesos é %s. "
                          "Use a definição do turno 2: desvio padrão amostral (ddof=1) vezes a "
                          "raiz de 252." % (posicao, pct(linha["risco"]), pct(ref_risco)))
            break
        ref_sharpe = (ref_retorno - rf) / ref_risco
        if abs(float(linha["sharpe"]) - ref_sharpe) > 1e-6:
            faltas.append("Na linha %d, a coluna sharpe vale %.4f e o esperado é %.4f. O Sharpe é "
                          "o retorno anual menos a taxa livre de risco (rf), dividido pelo risco "
                          "anual." % (posicao, float(linha["sharpe"]), ref_sharpe))
            break
    de_novo, _ = _tabela(chamar(funcao, retornos, n, 7, rf), retornos, n, origem)
    if not np.allclose(tabela.to_numpy(dtype=float), de_novo.to_numpy(dtype=float), atol=1e-12):
        faltas.append("Duas chamadas com a mesma semente devolveram tabelas diferentes. A semente "
                      "recebida precisa criar o gerador do sorteio, com "
                      "np.random.default_rng(semente), para o resultado poder ser repetido.")
    else:
        outra, _ = _tabela(chamar(funcao, retornos, n, 8, rf), retornos, n,
                           "simular(retornos, %d, 8, rf)" % n)
        if np.allclose(tabela.to_numpy(dtype=float), outra.to_numpy(dtype=float), atol=1e-12):
            faltas.append("As sementes 7 e 8 devolveram a mesma tabela. O sorteio precisa "
                          "depender da semente recebida. Uma semente fixa no código impede isso.")
    vazia, _ = _tabela(chamar(funcao, retornos, 0, 7, rf), retornos, 0,
                       "Caso de borda n = 0: simular(retornos, 0, 7, rf)")
    return faltas


# --- turno 5 --------------------------------------------------------------------

def _tempo(funcao, retornos, n, rf):
    inicio = time.perf_counter()
    tabela = chamar(funcao, retornos, n, 42, rf)
    return time.perf_counter() - inicio, tabela


def turno5(sim, precos, rf):
    faltas = []
    simular = obter(sim, "simular")
    completos = list(precos.dropna(axis=1).columns)
    for k in (2, 20):
        retornos = tabela_de_retornos(precos, completos[:k], 252)
        previa, _ = _tempo(simular, retornos, 1000, rf)
        if previa > LIMITE_SEGUNDOS / 2:
            faltas.append("Com %d ativos, 1.000 simulações levaram %.1f s; nesse ritmo, 10.000 "
                          "passam de 10 s. Sorteie todas as carteiras de uma vez, em uma matriz, "
                          "e calcule retorno e risco com operações do NumPy, sem laço em Python."
                          % (k, previa))
            break
        duracao, tabela = _tempo(simular, retornos, 10_000, rf)
        _tabela(tabela, retornos, 10_000, "simular com %d ativos e 10.000 simulações" % k)
        if duracao >= LIMITE_SEGUNDOS:
            faltas.append("Com %d ativos, 10.000 simulações levaram %.1f s, e o requisito é menos "
                          "de 10 s. Troque o laço em Python por operações do NumPy sobre a matriz "
                          "de pesos." % (k, duracao))
            break
    posicionar = obter(sim, "posicionar")
    retornos = tabela_de_retornos(precos, ["PETR4", "VALE3", "ITUB4"], 63)
    pesos = [0.2, 0.5, 0.3]
    ponto = chamar(posicionar, np.array(pesos), retornos, rf)
    if not isinstance(ponto, dict) or set(ponto) != {"retorno", "risco", "sharpe"}:
        raise Falta("posicionar devolveu %r, e o esperado é um dicionário com as chaves "
                    "\"retorno\", \"risco\" e \"sharpe\"." % (ponto,))
    ref_retorno, ref_risco = referencia_metricas(pesos, retornos)
    referencia = {"retorno": ref_retorno, "risco": ref_risco,
                  "sharpe": (ref_retorno - rf) / ref_risco}
    for chave in ("retorno", "risco", "sharpe"):
        valor = numero(ponto[chave], "posicionar (%s)" % chave)
        if abs(valor - referencia[chave]) > 1e-6:
            faltas.append("posicionar devolveu %s = %.4f e o esperado é %.4f. A carteira dada usa "
                          "as mesmas definições do turno 2 e o Sharpe do turno 4."
                          % (chave, valor, referencia[chave]))
    for descricao, ruins in (("Pesos que somam 1,1", [0.5, 0.3, 0.3]),
                             ("Peso negativo", [1.2, -0.2, 0.0])):
        recusa = espera_erro(posicionar, (np.array(ruins), retornos, rf), descricao)
        if recusa:
            faltas.append(recusa)
    return faltas


TURNOS = {1: turno1, 2: turno2, 3: turno3, 4: turno4, 5: turno5}


def conferir(turnos):
    """Confere os turnos pedidos. Devolve o código de saída: 0 se todos passam, 1 se não."""
    try:
        precos = carregar_precos()
        rf = carregar_rf()
    except OSError as erro:
        print("Não encontrei os dados da aula: %s" % erro)
        print("A pasta dados/ precisa ficar ao lado de conferir.py, com precos.csv e rf.txt.")
        return 1
    sys.path.insert(0, PASTA)
    sys.dont_write_bytecode = True   # não deixa __pycache__ na pasta do grupo
    try:
        sim = importlib.import_module("simulador")
    except Exception as erro:
        print("simulador.py não pôde ser carregado: %s: %s" % (type(erro).__name__, erro))
        print("Corrija esse erro antes de conferir. Se for erro de sintaxe, a mensagem acima "
              "diz a linha.")
        return 1
    codigo = 0
    for turno in turnos:
        try:
            faltas = TURNOS[turno](sim, precos, rf)
        except Falta as falta:
            faltas = [str(falta)]
        except Exception as erro:
            faltas = ["O resultado não pôde ser avaliado (%s: %s). Confira no SPEC.md o formato "
                      "da saída deste turno." % (type(erro).__name__, erro)]
        if faltas:
            codigo = 1
            print("TURNO %d: AINDA NÃO" % turno)
            for falta in faltas:
                print("  - " + falta)
        else:
            print("TURNO %d: OK" % turno)
    return codigo


def main(argumentos):
    if not argumentos:
        return conferir(sorted(TURNOS))
    if len(argumentos) == 1 and argumentos[0] in ("1", "2", "3", "4", "5"):
        return conferir([int(argumentos[0])])
    print("Uso: python conferir.py [turno]   (turno de 1 a 5; sem argumento, confere os cinco)")
    return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
