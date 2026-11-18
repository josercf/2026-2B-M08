# Especificação do simulador de carteiras

Cada turno tem cinco campos: Função, Entrada, Saída, Casos de borda e Critério de aceite. Os
turnos 1, 2 e 3 já estão preenchidos. O turno 3 é o modelo de escrita. Os turnos 4 e 5 a dupla
preenche antes de pedir a implementação ao agente. O turno 6 é feito depois do encontro e já vem
preenchido.

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

## Turno 6 (depois do encontro)

**Função:** `variancia_minima(retornos)`, `maximo_sharpe(retornos, rf)` e
`fronteira(retornos, pontos=50)`

**Entrada:** `retornos`, a tabela de N pregões, com uma coluna por ativo; `rf`, a taxa livre de
risco anual, em fração (o valor da aula está em `dados/rf.txt`); `pontos`, número inteiro de
retornos alvo da fronteira, 50 quando não é informado.

**Saída:**

- `variancia_minima` devolve um vetor do NumPy com um peso por ativo, na ordem das colunas de
  `retornos`: os pesos da carteira de menor risco anual.
- `maximo_sharpe` devolve um vetor do NumPy no mesmo formato: os pesos da carteira de maior
  Índice de Sharpe, que é o retorno anual menos `rf`, dividido pelo risco anual.
- `fronteira` devolve uma tabela (DataFrame) com uma linha por retorno alvo e as colunas
  `w_<ticker>` (uma por ativo, na ordem das colunas de `retornos`), `retorno` e `risco`, nesta
  ordem. Os retornos alvo são igualmente espaçados, do retorno da carteira de variância mínima
  até o maior retorno anual entre os ativos, em ordem crescente. Cada linha traz a carteira de
  menor risco anual que entrega o retorno alvo, com o retorno anual e o risco anual dela.
- Restrições das três funções: nenhum peso negativo (sem venda a descoberto), cada peso entre 0
  e 1, soma dos pesos igual a 1 (ver `docs/adrs/ADR-003-restricoes-da-otimizacao.md`).
- Retorno anual e risco anual seguem as definições do turno 2.
- A otimização usa `scipy.optimize.minimize` com o método SLSQP, partindo de pesos iguais. Na
  fronteira, cada otimização parte dos pesos encontrados para o alvo anterior.

**Casos de borda:**

- Tabela com um ativo só: `variancia_minima` e `maximo_sharpe` devolvem o vetor `[1.0]`.
- `pontos` menor que 2 levanta `ValueError` com mensagem que explica o motivo.
- Otimização que não converge (o resultado do `minimize` com `success` falso) levanta
  `RuntimeError` com a mensagem do otimizador. Nenhuma função devolve pesos de uma otimização
  que falhou.
- O último ponto da fronteira é a carteira com todo o peso no ativo de maior retorno anual.

**Critério de aceite:** `python conferir.py 6` imprime `TURNO 6: OK`, e os dois testes de
`tests/test_turno6.py` passam, incluindo o teste escrito pela dupla. O `conferir.py` verifica
propriedades: os pesos somam 1 e ficam entre 0 e 1; nenhuma de 10.000 carteiras sorteadas tem
risco menor que o da variância mínima nem Sharpe maior que o do máximo Sharpe; nenhuma mistura
de uma carteira ótima com outra carteira é melhor que a ótima; a fronteira tem uma linha por
alvo, começa na variância mínima, termina no ativo de maior retorno e, em cada ponto, nenhuma
carteira sorteada com retorno maior ou igual tem risco menor. As tolerâncias são 0,002 ponto
percentual no risco e 0,0001 no Sharpe.
