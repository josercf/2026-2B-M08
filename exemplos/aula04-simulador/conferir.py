"""Testes de aceite do professor para os seis turnos do simulador.

Uso:
    python conferir.py        confere os seis turnos
    python conferir.py 3      confere só o turno 3

Imprime "TURNO n: OK" quando o turno passa e sai com código 0. Quando falta
alguma coisa, imprime "TURNO n: AINDA NÃO" com a lista do que falta e sai com
código 1.

Este arquivo é do professor e não deve ser editado. Ele verifica propriedades
do resultado: soma dos pesos, formato da tabela, repetição com a mesma semente
e tempo. Nenhuma verificação depende do valor de um sorteio específico. Usa só
a biblioteca padrão, NumPy e pandas, e lê apenas os arquivos da pasta dados/.

O turno 6 (otimização) também é conferido por propriedades, sem SciPy: uma
carteira ótima não pode ser melhorada por nenhuma carteira candidata nem por
uma mistura dela com uma candidata. As candidatas são 10.000 carteiras
sorteadas aqui dentro, mais as carteiras de um ativo só.
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
# Tolerâncias do turno 6. O otimizador é numérico, então a conferência aceita
# resíduo pequeno: 0,000001 na soma e nos limites dos pesos, 0,002 ponto
# percentual no risco e no retorno, 0,0001 no Sharpe.
TOL_PESO = 1e-6
TOL_RISCO = 2e-5
TOL_SHARPE = 1e-4
CANDIDATAS = 10_000
FRACOES = (1.0, 0.2, 0.05, 0.01)   # parte da carteira trocada pela candidata


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


# --- turno 6 --------------------------------------------------------------------

CAUSAS = ("Causas comuns: devolver a melhor carteira sorteada da tabela de simular no lugar "
          "de otimizar (a melhor carteira sorteada ainda pode ser melhorada, como a mistura "
          "acima mostra); parar o SLSQP cedo, com a tolerância padrão (aperte com o parâmetro "
          "options do minimize, chave \"ftol\"); ou minimizar uma função diferente da pedida.")


def _candidatas(retornos):
    """Carteiras de comparação: 10.000 sorteadas mais as de um ativo só.

    Devolve (pesos, nomes, retorno anual dos ativos, covariância anual, variância
    de cada candidata, retorno de cada candidata).
    """
    k = retornos.shape[1]
    rng = np.random.default_rng(2026)
    sorteadas = rng.random((CANDIDATAS, k))
    sorteadas /= sorteadas.sum(axis=1, keepdims=True)
    pesos = np.vstack([sorteadas, np.eye(k)])
    nomes = ["uma carteira sorteada"] * CANDIDATAS + ["a carteira só de %s" % ativo
                                                      for ativo in retornos.columns]
    media = retornos.mean().to_numpy() * PREGOES_ANO
    cov = retornos.cov().to_numpy() * PREGOES_ANO
    variancias = np.einsum("ij,jk,ik->i", pesos, cov, pesos)
    return pesos, nomes, media, cov, variancias, pesos @ media


def _melhor_mistura(pesos, candidatas, rf=None, retorno_minimo=None):
    """Procura uma mistura de `pesos` com uma candidata que seja melhor que `pesos`.

    Com rf, melhor é ter Sharpe maior; sem rf, é ter risco menor. Com
    retorno_minimo, só entram misturas que rendem pelo menos esse retorno.
    Devolve None ou (ganho, fração, nome da candidata, valor atual, valor da mistura).
    """
    matriz, nomes, media, cov, variancias, retornos_cand = candidatas
    variancia = float(pesos @ cov @ pesos)
    retorno = float(pesos @ media)
    cruzada = matriz @ (cov @ pesos)
    atual = (retorno - rf) / np.sqrt(variancia) if rf is not None else np.sqrt(variancia)
    achado = None
    for fracao in FRACOES:
        var_mix = ((1 - fracao) ** 2 * variancia + 2 * fracao * (1 - fracao) * cruzada
                   + fracao ** 2 * variancias)
        risco_mix = np.sqrt(np.maximum(var_mix, 0))
        ret_mix = (1 - fracao) * retorno + fracao * retornos_cand
        if rf is not None:
            ganho = (ret_mix - rf) / np.maximum(risco_mix, 1e-300) - atual
            valor_mix = atual + ganho
        else:
            ganho = atual - risco_mix
            valor_mix = risco_mix
        if retorno_minimo is not None:
            ganho = np.where(ret_mix >= retorno_minimo - 1e-9, ganho, -np.inf)
        posicao = int(np.argmax(ganho))
        if achado is None or ganho[posicao] > achado[0]:
            achado = (float(ganho[posicao]), fracao, nomes[posicao], float(atual),
                      float(valor_mix[posicao]))
    limite = TOL_SHARPE if rf is not None else TOL_RISCO
    return achado if achado[0] > limite else None


def _descrever_mistura(achado):
    _, fracao, nome, _, _ = achado
    if fracao >= 1:
        return nome[0].upper() + nome[1:]
    return ("Uma mistura de %s da carteira devolvida com %s de %s"
            % (pct(1 - fracao, 0), pct(fracao, 0), nome.replace("a carteira só de ", "")
               if nome.startswith("a carteira só") else nome))


def _pesos_otimos(valor, k, origem):
    """Converte o resultado de uma otimização em vetor e confere soma e limites."""
    try:
        pesos = np.asarray(valor, dtype=float)
    except (TypeError, ValueError):
        raise Falta("%s devolveu %r, e o esperado é um vetor de números." % (origem, valor))
    if pesos.shape != (k,):
        raise Falta("%s devolveu um resultado de formato %s, e o esperado é um vetor do NumPy "
                    "com %d pesos, um por ativo, na ordem das colunas de retornos. Se a função "
                    "devolve o objeto do minimize, o vetor de pesos está no atributo x dele."
                    % (origem, pesos.shape, k))
    if np.isnan(pesos).any():
        raise Falta("%s devolveu NaN (um valor que não é número) entre os pesos." % origem)
    faltas = []
    if abs(pesos.sum() - 1) > TOL_PESO:
        faltas.append("%s devolveu pesos que somam %.4f, e os pesos de uma carteira precisam "
                      "somar 1. O otimizador só respeita a soma se ela entrar em constraints: "
                      "uma restrição de igualdade (type \"eq\") cuja função devolve zero quando "
                      "a soma dos pesos é 1." % (origem, pesos.sum()))
    if pesos.min() < -TOL_PESO or pesos.max() > 1 + TOL_PESO:
        faltas.append("%s devolveu peso fora do intervalo de 0 a 1 (menor %.4f, maior %.4f). A "
                      "carteira não vende a descoberto: passe ao minimize o argumento bounds, "
                      "com um par (mínimo, máximo) por ativo." % (origem, pesos.min(), pesos.max()))
    return pesos, faltas


def _conferir_otima(pesos, candidatas, origem, rf=None):
    """Lista do que falta para `pesos` ser a carteira ótima (risco sem rf, Sharpe com rf)."""
    k = len(pesos)
    achado = _melhor_mistura(pesos, candidatas, rf)
    if achado is None:
        return []
    _, _, _, atual, novo = achado
    if rf is None:
        medida = "tem risco anual de %s, menor que os %s" % (pct(novo, 3), pct(atual, 3))
        nome = "a de menor risco"
    else:
        medida = ("tem Sharpe de %.4f, maior que o %.4f" % (novo, atual)).replace(".", ",")
        nome = "a de maior Sharpe"
    if k > 1 and np.allclose(pesos, 1.0 / k, atol=1e-6):
        return ["%s devolveu pesos iguais (%s em cada ativo), que são o ponto inicial da "
                "otimização, e essa carteira não é %s. %s %s da carteira devolvida. Confira se "
                "o minimize foi chamado e se a função devolve os pesos encontrados por ele (o "
                "atributo x do resultado). Se o minimize foi chamado e os pesos não saíram do "
                "ponto inicial, a função objetivo tem valores muito pequenos (variância diária, "
                "por exemplo) e o SLSQP parou na tolerância padrão: use a variância anual e "
                "aperte a chave \"ftol\" do parâmetro options."
                % (origem, pct(1.0 / k, 1), nome, _descrever_mistura(achado), medida)]
    return ["%s não devolveu a carteira ótima. %s %s da carteira devolvida, com as mesmas "
            "restrições. %s" % (origem, _descrever_mistura(achado), medida, CAUSAS)]


def _fronteira(valor, retornos, pontos, origem):
    """Confere o formato da tabela da fronteira. Devolve (tabela, matriz de pesos)."""
    if not isinstance(valor, pd.DataFrame):
        raise Falta("%s devolveu %s, e o esperado é uma tabela (DataFrame do pandas)."
                    % (origem, type(valor).__name__))
    colunas_peso = ["w_%s" % ativo for ativo in retornos.columns]
    esperadas = colunas_peso + ["retorno", "risco"]
    if list(valor.columns) != esperadas:
        raise Falta("%s devolveu as colunas %s, e o esperado é %s, nesta ordem."
                    % (origem, list(valor.columns), esperadas))
    if len(valor) != pontos:
        raise Falta("%s devolveu %d linhas, e o esperado é uma linha por retorno alvo: %d."
                    % (origem, len(valor), pontos))
    try:
        numeros = valor.to_numpy(dtype=float)
    except (TypeError, ValueError):
        raise Falta("%s devolveu uma tabela com valor que não é número." % origem)
    if np.isnan(numeros).any():
        raise Falta("%s devolveu uma tabela com NaN (um valor que não é número)." % origem)
    return valor, numeros[:, :len(colunas_peso)]


def _conferir_fronteira(tabela, pesos, retornos, candidatas, origem):
    faltas = []
    _, _, media, cov, _, _ = candidatas
    pontos = len(tabela)
    somas = pesos.sum(axis=1)
    if np.abs(somas - 1).max() > TOL_PESO:
        linha = int(np.abs(somas - 1).argmax())
        faltas.append("Na linha %d de %s os pesos somam %.4f, e os pesos de cada linha precisam "
                      "somar 1. A restrição de soma 1 continua valendo em cada ponto da "
                      "fronteira, ao lado da restrição do retorno alvo: constraints aceita uma "
                      "lista com as duas." % (linha, origem, somas[linha]))
    if pesos.min() < -TOL_PESO or pesos.max() > 1 + TOL_PESO:
        faltas.append("%s tem peso fora do intervalo de 0 a 1 (menor %.4f, maior %.4f). Passe "
                      "bounds ao minimize em cada ponto da fronteira."
                      % (origem, pesos.min(), pesos.max()))
    if faltas:
        return faltas
    retorno = tabela["retorno"].to_numpy(dtype=float)
    risco = tabela["risco"].to_numpy(dtype=float)
    ref_retorno = pesos @ media
    ref_risco = np.sqrt(np.einsum("ij,jk,ik->i", pesos, cov, pesos))
    if np.abs(retorno - ref_retorno).max() > TOL_RISCO:
        linha = int(np.abs(retorno - ref_retorno).argmax())
        faltas.append("Na linha %d de %s a coluna retorno vale %s e o retorno anual dos pesos "
                      "dessa linha é %s. Se a coluna guarda o retorno alvo, os pesos não "
                      "atingiram o alvo: confira a restrição de igualdade do retorno e se a "
                      "otimização convergiu (resultado.success)."
                      % (linha, origem, pct(retorno[linha], 3), pct(ref_retorno[linha], 3)))
    if np.abs(risco - ref_risco).max() > TOL_RISCO:
        linha = int(np.abs(risco - ref_risco).argmax())
        faltas.append("Na linha %d de %s a coluna risco vale %s e o risco anual dos pesos dessa "
                      "linha é %s. Use a definição do turno 2: desvio padrão amostral (ddof=1) "
                      "vezes a raiz de 252. A variância que o otimizador minimiza é o quadrado "
                      "do risco." % (linha, origem, pct(risco[linha], 3), pct(ref_risco[linha], 3)))
    if faltas:
        return faltas
    passos = np.diff(retorno)
    if (passos <= 0).any():
        if np.abs(passos).max() <= TOL_RISCO:
            faltas.append("Todas as linhas de %s têm o mesmo retorno (%s). Sintoma comum: a "
                          "restrição do retorno alvo foi criada com lambda dentro do laço e "
                          "todas enxergam o último alvo. O README mostra como fixar o valor de "
                          "cada volta do laço em um argumento padrão do lambda."
                          % (origem, pct(retorno[0])))
        else:
            linha = int(np.argmax(passos <= 0)) + 1
            faltas.append("A coluna retorno de %s precisa estar em ordem crescente, e a linha "
                          "%d (%s) não é maior que a anterior (%s). Cada linha vem de uma "
                          "otimização própria, com um retorno alvo maior que o da linha anterior."
                          % (origem, linha, pct(retorno[linha], 3), pct(retorno[linha - 1], 3)))
        return faltas
    achado = _melhor_mistura(pesos[0], candidatas)
    if achado is not None:
        faltas.append("O primeiro ponto de %s precisa ser a carteira de variância mínima, e ele "
                      "tem risco anual de %s. %s tem risco de %s. O primeiro retorno alvo é o "
                      "retorno da carteira que variancia_minima devolve."
                      % (origem, pct(achado[3], 3), _descrever_mistura(achado), pct(achado[4], 3)))
    if abs(retorno[-1] - media.max()) > TOL_RISCO:
        faltas.append("O último ponto de %s tem retorno de %s, e o esperado é o maior retorno "
                      "anual entre os ativos: %s, de %s."
                      % (origem, pct(retorno[-1], 3), pct(media.max(), 3),
                         retornos.columns[int(media.argmax())]))
    if faltas:
        return faltas
    if np.abs(passos - passos.mean()).max() > TOL_RISCO:
        faltas.append("Os retornos alvo de %s precisam ser igualmente espaçados entre o primeiro "
                      "(%s) e o último (%s), e o maior passo é %s para um passo médio de %s. O "
                      "NumPy tem uma função que devolve números igualmente espaçados entre dois "
                      "extremos." % (origem, pct(retorno[0]), pct(retorno[-1]),
                                     pct(passos.max(), 3), pct(passos.mean(), 3)))
        return faltas
    piores = []
    for linha in range(pontos):
        achado = _melhor_mistura(pesos[linha], candidatas, retorno_minimo=retorno[linha])
        if achado is not None:
            piores.append((linha, achado))
    if piores:
        linha, achado = max(piores, key=lambda item: item[1][0])
        faltas.append("%d dos %d pontos de %s não estão na fronteira. Na linha %d, com retorno "
                      "de %s, a carteira devolvida tem risco de %s. %s rende pelo menos esse "
                      "retorno com risco de %s. Cada ponto da fronteira é a carteira de menor "
                      "risco para o retorno alvo: uma otimização por alvo, com a restrição de "
                      "soma 1 e a restrição do retorno. Montar a fronteira com as melhores "
                      "carteiras sorteadas deixa os pontos acima do risco mínimo."
                      % (len(piores), pontos, origem, linha, pct(retorno[linha]),
                         pct(achado[3], 3), _descrever_mistura(achado), pct(achado[4], 3)))
    return faltas


def turno6(sim, precos, rf):
    faltas = []
    minima = obter(sim, "variancia_minima")
    sharpe = obter(sim, "maximo_sharpe")
    fronteira = obter(sim, "fronteira")
    completos = list(precos.dropna(axis=1).columns)
    cinco = ["PETR4", "VALE3", "ITUB4", "WEGE3", "ABEV3"]
    cestas = [("2 ativos", ["PETR4", "VALE3"]), ("5 ativos", cinco),
              ("15 ativos", completos[:15])]
    for descricao, ativos in cestas:
        retornos = tabela_de_retornos(precos, ativos, 252)
        candidatas = _candidatas(retornos)
        k = len(ativos)
        for funcao, argumentos, taxa in ((minima, (retornos,), None), (sharpe, (retornos, rf), rf)):
            origem = "%s com %s" % (funcao.__name__, descricao)
            pesos, problemas = _pesos_otimos(chamar(funcao, *argumentos), k, origem)
            faltas.extend(problemas or _conferir_otima(pesos, candidatas, origem, taxa))
        if faltas:
            return faltas
    um = tabela_de_retornos(precos, ["PETR4"], 63)
    for funcao, argumentos in ((minima, (um,)), (sharpe, (um, rf))):
        origem = "Caso de borda de um ativo só: %s" % funcao.__name__
        pesos, problemas = _pesos_otimos(chamar(funcao, *argumentos), 1, origem)
        faltas.extend(problemas)
    retornos = tabela_de_retornos(precos, cinco, 252)
    candidatas = _candidatas(retornos)
    for pontos, argumentos in ((50, (retornos,)), (12, (retornos, 12))):
        origem = ("fronteira(retornos)" if pontos == 50 else "fronteira(retornos, 12)")
        tabela, pesos = _fronteira(chamar(fronteira, *argumentos), retornos, pontos, origem)
        problemas = _conferir_fronteira(tabela, pesos, retornos, candidatas, origem)
        faltas.extend(problemas)
        if problemas:
            return faltas
    recusa = espera_erro(fronteira, (retornos, 1), "Caso de borda pontos = 1 (SPEC.md)")
    if recusa:
        faltas.append(recusa)
    return faltas


TURNOS = {1: turno1, 2: turno2, 3: turno3, 4: turno4, 5: turno5, 6: turno6}


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
    if len(argumentos) == 1 and argumentos[0] in ("1", "2", "3", "4", "5", "6"):
        return conferir([int(argumentos[0])])
    print("Uso: python conferir.py [turno]   (turno de 1 a 6; sem argumento, confere os seis)")
    return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
