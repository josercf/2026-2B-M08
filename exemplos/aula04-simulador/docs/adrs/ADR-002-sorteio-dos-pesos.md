# ADR-002: Sorteio dos pesos das carteiras

> Exemplo do professor: a ADR do seu A3 precisa tratar de uma decisão sua.

- **Data:** 17/11/2026
- **Status:** Aceita
- **Decisores:** Prof. José Romualdo

## Contexto

A simulação de Monte Carlo sorteia milhares de carteiras. Cada carteira é um vetor de pesos não
negativos que soma 1, e existe mais de uma forma de sortear esse vetor. A forma escolhida define
quais regiões do gráfico de risco e retorno a nuvem cobre.

## Decisão

Os pesos são sorteados pelo método uniforme normalizado: `k` números entre 0 e 1, cada um
dividido pela soma de todos.

## Motivações

- A regra cabe em duas linhas e pode ser conferida à mão, o que permite à dupla revisar o código
  escrito pelo agente.
- É o método do material de referência da disciplina e o mesmo que o portal de simulação usa.
- A soma 1 e a ausência de peso negativo saem da própria construção, sem etapa de correção.

## Riscos conhecidos e mitigações

- O método concentra as carteiras perto de pesos iguais e raramente sorteia uma carteira
  concentrada em um único ativo. O efeito cresce com o número de ativos.
  Mitigação: a função `posicionar` permite marcar sobre a nuvem uma carteira concentrada
  escolhida pela dupla, e a leitura do gráfico declara essa limitação.

## Consequências

- Positiva: implementação curta, reproduzível com semente e rápida em NumPy.
- Negativa: as bordas da nuvem ficam pouco povoadas, e a melhor carteira sorteada tende a ficar
  abaixo da melhor carteira possível.
- Negativa: comparar esta nuvem com a de outro método de sorteio exige declarar o método usado
  em cada uma.
