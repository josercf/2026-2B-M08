# ADR-001: Janela dos dados do simulador

> Exemplo do professor: a ADR do seu A3 precisa tratar de uma decisão sua.

- **Data:** 17/11/2026
- **Status:** Aceita
- **Decisores:** Prof. José Romualdo

## Contexto

O simulador calcula retorno e risco a partir de cotações históricas. O resultado muda com três
escolhas: a data em que as cotações terminam, o tratamento de ativos que começaram a negociar em
datas diferentes e a quantidade de pregões usada na conta.

## Decisão

As cotações de `dados/precos.csv` vão de 02/01/2024 a 13/11/2026, toda conta com mais de um ativo
usa a janela comum dos ativos escolhidos, e o kit trabalha com dois períodos: os 9 pregões mais
recentes para conferir à mão e os 252 pregões mais recentes para a nuvem de carteiras.

## Motivações

- O corte em 13/11/2026 é o preço de referência da carteira que os grupos montaram na aula de
  Negócios.
- A janela comum mantém só os pregões em que todos os ativos da carteira têm cotação. Sem ela, a
  covariância entre dois ativos seria calculada com datas que um deles não tem.
- Nove pregões cabem em uma tabela que se confere com calculadora, o que permite comparar a
  função escrita à mão com o portal.
- 252 pregões equivalem a um ano de negociação, a mesma base usada para anualizar retorno e
  risco.

## Riscos conhecidos e mitigações

- Um ativo com início de negociação recente encurta a janela comum de toda a carteira.
  Mitigação: o portal de simulação informa quantos pregões a janela comum tem e limita o
  período oferecido a esse número.
- Retorno e risco anualizados a partir de 9 pregões variam muito de uma semana para outra.
  Mitigação: os 9 pregões servem apenas para conferir a conta, e nenhuma leitura analítica usa
  esse período.

## Consequências

- Positiva: qualquer dupla reproduz os mesmos números sem acesso à rede, porque o arquivo é fixo.
- Negativa: os números do kit deixam de acompanhar o mercado depois de 13/11/2026.
- Negativa: 252 pregões cobrem só o último ano, e o risco medido pode ser menor que o de um
  período mais longo, que inclua crises anteriores.
