# ADR-010: Validação da Aula 05 com anos disjuntos e custo de reotimização declarado

**Data:** 13/10/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A auditoria crítica de 13/10/2026 (`docs/auditorias/2026-10-13-auditoria-critica-materiais-aulas.md`)
apontou dois defeitos de método na Aula 05:

- **C-11.** O deck dizia que o máximo Sharpe entregou menos que prometeu "em 25 das 33 janelas". As
  33 janelas têm treino de 24 meses e teste de 12, deslocadas mês a mês: duas vizinhas compartilham
  11 dos 12 meses de teste, e os 33 testes somam 8.231 dias de pregão sobre só 915 dias distintos.
  A contagem soava como 33 experimentos independentes.
- **C-12.** O ADR de exemplo do deck decidia "reotimizar todo mês" sem custo de transação, embora
  82,60% do máximo Sharpe troque de ativo entre 2021-2022 e 2023-2024.

## Decisão

As 33 janelas continuam como leitura de regime, acompanhadas da sobreposição medida e da mesma
regra em anos de teste disjuntos (2023, 2024 e 2025), e toda frequência de reotimização é
apresentada com turnover e retorno líquido sob custo declarado de 0,10% do valor negociado.

## Motivações

- Três anos disjuntos são a evidência independente que a base comporta com treino de 24 meses. Ela
  é pequena, e o deck diz isso: o máximo Sharpe ficou abaixo do prometido em 2 dos 3 anos. Em todos
  os 12 meses possíveis de início dos blocos, ele fica abaixo em pelo menos 2 blocos.
- O custo de 0,10% sobre compras e vendas é uma premissa didática, sem fonte de mercado
  citada, que o aluno consegue trocar no notebook. Com ela, a
  reotimização mensal gira 156,87% ao ano e custa 0,31 ponto de retorno por ano (29,39% bruto,
  29,08% líquido, de 02/01/2023 a 31/08/2026).
- O ADR de exemplo vira hipótese condicionada ao custo, rotulada como exercício sem valor de
  recomendação prática, que é o que a evidência sustenta.

## Riscos conhecidos e mitigações

- **A premissa de 0,10% subestima o custo real** (spread, impacto de mercado, imposto). Mitigação:
  ela aparece no slide como premissa, e o notebook pede que a dupla a altere.
- **As diferenças de retorno bruto entre frequências vêm de um único período de 915 dias.**
  Mitigação: o slide declara isso, e nenhuma frequência é recomendada.
- **Três blocos disjuntos são pouca evidência.** Mitigação: o deck mostra as duas leituras juntas,
  e o quiz cobra por que 33 janelas não são 33 experimentos.

## Consequências

- Positivas: a conclusão do deck fica do tamanho da evidência; o aluno vê sobreposição, custo e
  turnover antes de escrever o ADR do A4.
- Negativas: o deck da Aula 05 passa de 27 para 29 slides, e o bloco correspondente fica mais
  denso.

## ADRs relacionadas

- ADR-009: tratamento de ausência e janela comum, usado em todas as medições.
- ADR-004: sala de aula invertida; o quiz final segue com três perguntas.
