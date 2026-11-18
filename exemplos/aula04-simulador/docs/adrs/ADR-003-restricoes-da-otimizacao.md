# ADR-003: Restrições da otimização de carteiras

> Exemplo do professor: a ADR do seu A4 precisa tratar de uma decisão sua.

- **Data:** 17/11/2026
- **Status:** Aceita
- **Decisores:** Prof. José Romualdo

## Contexto

O turno 6 calcula a carteira de variância mínima, a de máximo Sharpe e a fronteira eficiente. O
resultado de uma otimização depende das restrições impostas aos pesos: a mesma cesta de ativos
gera carteiras diferentes com e sem venda a descoberto, e com e sem teto de peso por ativo.

## Decisão

A otimização usa três restrições: nenhum peso negativo (sem venda a descoberto), cada peso entre
0 e 1, e soma dos pesos igual a 1. Não há teto de peso por ativo.

## Motivações

- São as restrições das carteiras sorteadas nos turnos 3 e 4. Com as mesmas restrições, a
  fronteira e a nuvem podem ser desenhadas no mesmo gráfico e comparadas.
- A carteira do Solver da aula de Negócios entra no mesmo gráfico. Antes de comparar, a dupla
  confere se o Solver foi configurado com as mesmas restrições.
- O método SLSQP do SciPy recebe as três diretamente, em `bounds` e `constraints`.

## Riscos conhecidos e mitigações

- Sem teto por ativo, a carteira ótima tende a concentrar o peso em poucos ativos.
  Mitigação: o A4 informa os pesos das duas carteiras ótimas e quantos ativos recebem peso.
- O otimizador converge para o passado da janela: os pesos ótimos refletem os retornos e as
  covariâncias dos pregões usados, e mudam quando a janela muda.
  Mitigação: a janela é declarada (ADR-001), e a aula 05 trata da validação fora da amostra.

## Consequências

- Positiva: a comparação entre a nuvem e a fronteira usa uma regra só.
- Negativa: a carteira de máximo Sharpe pode ficar concentrada em um ou dois ativos, o que um
  gestor com limite de exposição por ativo não aceitaria.
- Negativa: incluir um teto de peso por ativo muda a fronteira e exige nova ADR.

## ADRs relacionadas

- ADR-001: Janela dos dados do simulador.
- ADR-002: Sorteio dos pesos das carteiras.
