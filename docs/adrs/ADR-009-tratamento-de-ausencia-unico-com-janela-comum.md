# ADR-009: Tratamento de ausência único, com janela comum na análise conjunta

**Data:** 13/10/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

As Aulas 02 a 06 foram construídas em paralelo em 13/10/2026, e cada uma escolheu sozinha como
tratar as datas sem cotação. A Aula 02 preenchia as lacunas com o último preço (ffill) e calculava
cada ativo na série inteira. A Aula 03 fazia o mesmo e montava a matriz de covariância par a par,
cada par na própria janela. A Aula 04 descartava as datas com ausência na cesta inteira (dropna
sobre preço, 1.422 retornos). A Aula 05 descartava as datas e começava o estudo em 04/01/2021. O
exemplo da Aula 06 descartava as datas no subconjunto de ativos pedido.

Cada aula declarava a própria escolha, e nenhum número estava errado. O efeito para a turma, porém,
era ver a volatilidade do mesmo ativo mudar de uma aula para a outra sem que a diferença fosse o
assunto da aula, e a matriz construída na Aula 03 não ser a que o otimizador da Aula 04 consome,
embora o roteiro diga que o A3 consome a matriz montada na Aula 03.

Medido em 13/10/2026 sobre o snapshot de 17/09/2026:

| Medida | Valor |
|---|---|
| Lacunas isoladas (ativo já cotado sem cotação num pregão) | 3, todas em 24/10/2025: BOVA11, IVVB11 e GOLD11 |
| Pregões da GOLD11 sem cotação antes da primeira cotação (11/12/2020) | 484 |
| Retornos da série inteira (1.908 pregões) | 1.907 |
| Retornos na janela comum dos 15 ativos | 1.423, de 14/12/2020 a 31/08/2026 |
| Retornos na janela comum dos 14 ativos sem a GOLD11 | 1.907, com março de 2020 |
| Volatilidade anual da PETR4, série inteira e janela comum dos 15 | 39,25% e 33,40% |

## Decisão

O módulo inteiro usa um tratamento só, implementado em `tools/retornos.py`: lacuna isolada é
preenchida com o último preço, nada é preenchido antes da primeira cotação, métrica de um ativo
usa a série inteira dele e análise conjunta usa a janela comum dos ativos envolvidos, com início e
número de retornos declarados no slide.

## Motivações

1. **Espiral.** A Aula 01 ensina os três tratamentos e o exemplo de ADR dela escolhe preencher. As
   aulas seguintes passam a usar a decisão que a turma registrou no A1, em vez de trocá-la sem
   aviso.
2. **Uma matriz só.** A matriz de covariância da Aula 03 é a mesma que entra no otimizador da Aula
   04, no estudo fora da amostra da Aula 05 e na API da Aula 06, como o roteiro pede.
3. **Preencher afeta três pregões.** Com só três lacunas isoladas, o preenchimento muda pouco os
   números; o que pesa é a janela, e ela passa a ser declarada.
4. **O custo da janela comum vira conteúdo.** Com a GOLD11 na cesta, a janela comum perde março de
   2020, exatamente o efeito que a Aula 01 mostra ao descartar datas. As Aulas 03 e 04 mostram esse
   custo com o número medido, e a turma decide no próprio ADR se o ativo de histórico curto vale a
   perda do período de estresse.
5. **Matriz positiva semidefinida.** A covariância par a par, com cada par numa janela diferente,
   não garante matriz positiva semidefinida, e o otimizador pode falhar ou devolver variância
   negativa. A janela comum garante.

## Riscos conhecidos

- **Otimizador estimado sem o choque de 2020.** Na janela comum dos 15 ativos, a volatilidade sai
  menor que a da série inteira (PETR4 de 39,25% para 33,40%). Mitigação: a Aula 04 declara a
  janela e o custo no slide, e a Aula 05 testa a carteira fora da amostra.
- **Retorno zero no dia preenchido.** O ffill cria retorno zero em 24/10/2025 e joga a variação dos
  dois dias no pregão seguinte. Mitigação: o efeito é medido na Aula 01 e afeta três pregões.
- **Snapshot novo com mais lacunas.** Uma coleta futura pode trazer lacunas longas, que o ffill
  esconderia. Mitigação: `tools/tests/test_retornos.py` trava as três lacunas, e qualquer mudança
  reprova o teste antes de chegar aos decks.

## Consequências

**Positivas:** o mesmo ativo tem o mesmo retorno em todas as aulas; a matriz da Aula 03 alimenta as
Aulas 04 a 06; um módulo só concentra a regra e o teste dela.

**Negativas:** as medições, os testes, os widgets, as animações, os decks, os materiais e os
notebooks das Aulas 03 a 06 precisam ser medidos de novo, e os números que mudarem precisam ser
trocados em todos os artefatos da aula.

## ADRs relacionadas

- ADR-003: dados do case versionados.
- ADR-008: exemplo da Aula 06 em duas camadas, medido pela API.
