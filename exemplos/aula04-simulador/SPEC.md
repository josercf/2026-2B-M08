# Especificação do simulador de carteiras

Cada turno tem cinco campos: Função, Entrada, Saída, Casos de borda e Critério de aceite. Os
turnos 1, 2 e 3 já estão preenchidos. O turno 3 é o modelo de escrita. Os turnos 4 e 5 a dupla
preenche antes de pedir a implementação ao agente.

Definições usadas em todos os turnos:

- `retornos` é uma tabela (DataFrame do pandas) com uma linha por pregão e uma coluna por ativo,
  em fração: 1,23% é `0.0123`.
- Os pesos seguem a ordem das colunas de `retornos`.
- Um ano tem 252 pregões.

## Turno 1

**Função:** `retorno_do_dia(pesos, retornos_do_dia)`

**Entrada:** `pesos`, com o peso de cada ativo, somando 1; `retornos_do_dia`, com o retorno de
cada ativo em um pregão, na mesma ordem.

**Saída:** um número, o retorno da carteira no pregão: a soma de cada peso vezes o retorno do
ativo naquele dia.

**Casos de borda:** carteira com peso 1 em um ativo e 0 nos outros devolve o retorno desse ativo.

**Critério de aceite:** `python conferir.py 1` imprime `TURNO 1: OK`, e o teste da dupla em
`tests/test_turno1.py` passa com o valor lido no portal, com tolerância de 0,05 ponto percentual.

## Turno 2

**Função:** `metricas(pesos, retornos)`

**Entrada:** `pesos`, com o peso de cada ativo; `retornos`, a tabela de N pregões.

**Saída:** dois números, nesta ordem: retorno anual e risco anual. O retorno anual é a média dos
retornos diários da carteira vezes 252. O risco anual é o desvio padrão amostral (`ddof=1`) dos
retornos diários da carteira vezes a raiz de 252.

**Casos de borda:** carteira com peso 1 em um ativo devolve o retorno anual e o risco anual desse
ativo.

**Critério de aceite:** `python conferir.py 2` imprime `TURNO 2: OK`, e o teste da dupla em
`tests/test_turno2.py` passa com os dois valores lidos no portal, com tolerância de 0,05 ponto
percentual.

## Turno 3 (modelo)

**Função:** `sortear_pesos(k, rng)`

**Entrada:** `k`, número inteiro de ativos da carteira; `rng`, gerador aleatório do NumPy criado
com `np.random.default_rng(semente)`.

**Saída:** um vetor do NumPy com `k` pesos. Nenhum peso é negativo e a soma é 1. O sorteio é
uniforme normalizado: `k` números sorteados entre 0 e 1 pelo `rng`, cada um dividido pela soma
de todos (ver `docs/adrs/ADR-002-sorteio-dos-pesos.md`).

**Casos de borda:**

- `k = 1` devolve o vetor `[1.0]`.
- `k` menor que 1 levanta `ValueError` com mensagem que explica o motivo.
- Dois geradores criados com a mesma semente devolvem os mesmos pesos.
- Duas chamadas seguidas com o mesmo gerador devolvem pesos diferentes.

**Critério de aceite:** `python conferir.py 3` imprime `TURNO 3: OK`, e os dois testes de
`tests/test_turno3.py` passam, incluindo o teste escrito pela dupla.

## Turno 4

**Função:** `simular(retornos, n, semente, rf)`

**Entrada:**

**Saída:**

**Casos de borda:**

**Critério de aceite:**

## Turno 5

**Função:** `simular(retornos, n, semente, rf)`, com requisito de tempo: 10.000 simulações em
menos de 10 segundos, com 2 a 20 ativos; e `posicionar(pesos, retornos, rf)`

**Entrada:**

**Saída:**

**Casos de borda:**

**Critério de aceite:**
