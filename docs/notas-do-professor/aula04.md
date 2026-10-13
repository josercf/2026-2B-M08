# Notas do professor: Aula 04, Da Nuvem à Fronteira

Artefato interno de condução, não distribuído ao aluno. Aula de 18/11/2026 (quarta), Semana 6,
Sprint 3, Aula 28 do módulo na Adalove; horário de relógio a confirmar (P1). Todo número abaixo vem
de `tools/medidas_aula04.py` e está travado em `tools/tests/test_aula04.py`. Amostra: Adj Close com
o tratamento de ausência da ADR-009 (`tools/retornos.py`), janela comum dos 15 ativos, 1.423
retornos diários de 14/12/2020 a 31/08/2026, anualização por 252, CDI acumulado na janela (11,30%
ao ano), semente 42.

## Antes do encontro

- Abrir o deck por HTTP (`python3 -m http.server 8000` na raiz) e conferir que os dois widgets
  montam e que os três vídeos tocam no navegador da sala.
- Não distribuir o PDF exportado pelo botão do deck: ele revela o gabarito dos dois quizzes.
- A matriz desta aula é a da Aula 03, na mesma janela comum dos 15 ativos (ADR-009). O pregão de
  24/10/2025 entra com retorno zero preenchido em BOVA11, IVVB11 e GOLD11, como no ADR da Aula 01.
  Se um grupo perguntar por que a volatilidade da PETR4 é 33,40% aqui e 39,25% na Aula 02, a
  resposta está no slide 3 e na seção 2 do material: a Aula 02 mede cada ativo na série inteira, e a
  janela comum com a GOLD11 começa em 14/12/2020 e perde março de 2020. Pergunta para o ADR do
  grupo: a GOLD11 vale a perda do período de estresse?

## Daily (15 min)

Pergunta a cada equipe: quanto tempo o motor de vocês leva para 10.000 carteiras? O requisito do A3
é menos de 10 segundos. Equipe que não mediu ainda sai da daily com essa tarefa para o Bloco 3.

## Bloco 1: Peer Instruction de abertura

Pergunta: entre 10.000 carteiras sorteadas, a de maior Índice de Sharpe é a carteira ótima?

| Alternativa | Correta | Erro que revela |
|---|---|---|
| Sim: 10.000 sorteios cobrem todas as alocações | não | confunde quantidade de pontos com cobertura do espaço de pesos |
| Sim, a menos de arredondamento | não | supõe que a nuvem chega à borda; a melhor sorteada tem 0,41 e a ótima 0,92 |
| Depende da semente: outra semente passa da ótima | não | não entendeu que a ótima é o máximo sobre todas as carteiras possíveis |
| Não: é só a melhor entre as sorteadas e fica abaixo da ótima | sim | |

Critério de discussão: se a primeira votação tiver entre 30% e 70% de acerto, discussão em dupla
por dois minutos e nova votação. Abaixo de 30%, retomar a animação da nuvem por 1 minuto antes da
dupla. Acima de 70%, revelar e passar ao slide 5. Na revelação, apontar duas colunas do slide 5:
ativos com peso (15 contra 3) e maior peso (18,17% contra 44,31%).

**Turma sem pré-aula.** Se mais da metade não viu as animações, tocar a animação da nuvem do slide
11 logo depois do slide 3 (22 segundos) e só então votar. O Bloco 4 continua com o widget.

## Bloco 2: forma vetorial e o triângulo

Interação: previsão antes de arrastar o vértice. Cada dupla anota onde o ponto cai no plano com
100% em PETR4 e onde fica o maior Sharpe.

- Pergunta socrática: "Por que a carteira de pesos iguais tem Sharpe negativo se a PETR4 rende
  37,53% ao ano?" Resposta esperada: o Sharpe da carteira é calculado sobre o retorno da carteira
  (8,34%), que fica abaixo do CDI de 11,30%; oito dos 15 ativos rendem abaixo do CDI e a MGLU3 tem
  retorno esperado de -42,83%. Erro comum: achar que o Sharpe da carteira é a média dos Sharpes
  dos ativos.
- No widget, "Só PETR4" leva o ponto para 33,40% de volatilidade e 37,53% de retorno. Pergunta:
  "e se eu tirar um pouco da PETR4 e pôr no GOLD11, a volatilidade sobe ou desce?" Resposta: desce,
  porque a correlação entre os dois é -0,13. Erro comum: imaginar a volatilidade da mistura como
  média ponderada das volatilidades.
- "Mostrar ótimo" só depois das previsões anotadas.

## Bloco 3: o motor (dupla, 12 min)

Interação: programação em dupla no notebook, seções 1 a 3, troca de papel aos 6 minutos. As
células já vêm prontas: a dupla roda, mede e lê o código, sem escrever o motor do zero.

- **Obrigatório:** rodar as seções 1 a 3; anotar o tempo das 10.000 carteiras e quantas ficam
  abaixo do CDI; depois da troca, o navegador aponta em `sortear` a linha que faz os pesos somarem
  1 (`pesos /= pesos.sum(axis=1, keepdims=True)`) e a que calcula a variância sem laço (`einsum`);
  comparar o tempo com o requisito do A3, menos de 10 segundos.
- **Extensão:** escrever o laço `for w in pesos: w @ cov @ w` e conferir com `np.allclose` que ele
  bate com o `einsum`.
- **Checagem aos 6 minutos**, junto com a troca de papel: tempo e contagem abaixo do CDI anotados.
  Dupla que não chegou à seção 3 usa "Executar anteriores" na célula do motor.
- **Debrief**, ao fim do cronômetro: a turma compara os tempos medidos e a contagem abaixo do CDI
  entre as duplas; contagem diferente de 8.851 aponta semente ou janela alterada (ver abaixo).
- **Contingência:** se o Colab ou a rede falharem, o professor projeta o notebook executado na
  própria máquina, que roda sem rede a partir de `dados/`, e a dupla faz a leitura de `sortear`
  pelo código do slide 9.

- Quando a sala trava em `einsum`: pedir que escrevam o laço `for w in pesos: w @ cov @ w` e
  comparem o resultado com `np.allclose`. Resposta esperada: os dois batem, e a forma `einsum` faz
  a mesma conta para as 10.000 linhas sem laço.
- Pergunta: "por que dividir pela soma da linha e não por 15?" Resposta: dividir por 15 não garante
  soma 1 com números sorteados entre 0 e 1. Erro comum: normalizar a matriz inteira em vez de cada
  linha (`keepdims=True` faltando).
- O notebook imprime 8.851 carteiras abaixo do CDI. Se uma dupla tiver outro número, a semente ou a
  amostra mudou: conferir `semente=42` e a janela (1.423 retornos, a partir de 14/12/2020).

## Bloco 4: sorteio progressivo

Interação: pergunta disparada "quantos sorteios faltariam para a melhor sorteada encostar na
ótima?".

- Mover o widget de 10 a 10.000: -0,10, 0,15, 0,28 e 0,41.
- Resposta esperada depois do slide 13: um milhão chega a 0,60, ainda longe de 0,92. O motor da
  aula soma 15 números Uniform(0,1) e divide pela soma, distribuição que acumula os pesos perto de
  1/15: o maior peso entre as 10.000 sorteadas é 24,61%, e a ótima põe 44,31% na PETR4 e zera 12
  ativos.
- Slide 14: com a mesma semente e os mesmos 10.000 sorteios, a Dirichlet(1), uniforme no simplex,
  chega a 0,64 (acima do milhão do motor da aula) e a Dirichlet(0,2), que favorece vértices, a 0,85.
  No trio PETR4, IVVB11 e GOLD11 as três chegam a 0,92. Fechar com os três fatores: distribuição dos
  pesos, dimensão e ausência de objetivo no sorteio. Nenhuma distribuição chega a 0,92 com 15
  ativos, e o A4 resolve a carteira por otimização.
- Erro comum: concluir que basta trocar para Dirichlet(0,2). A melhor dela tem 1,90 ativos
  efetivos, mais concentrada que a ótima (2,82), e continua abaixo de 0,92.
- Erro comum: propor "mais sorteios" ou "outra semente" como solução. Devolver a pergunta do
  barema do A3: por que a simulação não substitui a otimização?

## Bloco 5: SLSQP

Interação: previsão no quadro, antes de rodar o otimizador, de qual carteira concentra mais peso
num único ativo. Anotar a contagem de votos no quadro.

- Gabarito: máximo Sharpe, com 44,31% na PETR4, contra 26,78% no IVVB11, o maior peso da variância
  mínima. A variância mínima tem 10 ativos com peso; o máximo Sharpe, 3.
- Pergunta socrática: "a soma 1 impede venda a descoberto?" Resposta: não; -50% num ativo e 150% em
  outro também somam 1. Quem impede são os limites de 0 a 1.
- Na animação do trio, o primeiro passo vai ao vértice da PETR4 (Sharpe 0,79). Pergunta: "por que o
  otimizador passa do ponto e volta?" Resposta: o passo segue a direção que mais melhora o Sharpe no
  ponto de partida; os passos seguintes corrigem. Parada em 10 iterações, Sharpe 0,92, igual ao da
  cesta inteira, porque os outros 12 ativos ficam com peso zero na ótima.
- Erro comum a antecipar: usar `resultado.x` sem conferir `resultado.success`.

## Bloco 6: a fronteira (dupla, 12 min)

Interação: dupla no notebook, seções 4 e 5, já prontas, e a frase sobre o perfil de investidor. O
solucionador é fornecido; o trabalho da dupla é interpretar restrições ativas e pontos dominados.

- **Obrigatório:** rodar as seções 1 a 5 e conferir `success` nas duas otimizações; na tabela de
  pesos, apontar os ativos com peso zero no máximo Sharpe, onde o limite inferior está ativo (o
  máximo Sharpe zera 12 dos 15 ativos); depois da troca, escolher no gráfico da seção 5 uma sorteada e o ponto da
  fronteira que tem mais retorno com a mesma volatilidade; escrever a frase do perfil.
- **Extensão:** seção 6, completar `maximo_sharpe_com_teto` e comparar os pesos com os da seção 4.
  É o desafio do notebook que o planejamento põe depois do encontro.
- **Checagem aos 6 minutos**, junto com a troca de papel: a tabela das duas ótimas está na tela, com
  os ativos de peso zero apontados.
- **Debrief**, ao fim do cronômetro: duas duplas leem a frase do perfil, e a sala responde se
  alguma sorteada passa da fronteira.
- **Contingência:** se o ambiente falhar, a dupla trabalha sobre a tabela do slide 18 e o vídeo da
  fronteira do slide 19, e o professor projeta o notebook executado na própria máquina, que roda
  sem rede a partir de `dados/`.

- Resposta esperada para a frase: a variância mínima (9,67% de volatilidade, 14,10% de retorno)
  serve a quem prioriza preservar o excedente de caixa; o máximo Sharpe (15,91% e 25,96%) serve a
  quem aceita mais oscilação em troca de retorno por unidade de risco.
- Pergunta: "alguma sorteada passa da fronteira?" Resposta: nenhuma, e o teste da aula confere isso
  para as 10.000. Se o gráfico de uma dupla mostrar pontos acima da curva, os eixos estão trocados
  (retorno no eixo x).
- Pergunta socrática para fechar: "a PETR4 vai continuar rendendo 37,53% ao ano?" É a ponte para a
  Aula 05: o otimizador converge para o passado.

## Bloco 7: quiz e amarração

Gabarito do quiz de verificação:

1. Por que o sorteio não encontra a ótima? **A distribuição dos pesos quase nunca concentra.**
   Uniform(0,1) dividido pela soma nunca passa de 24,61% num ativo; a Dirichlet(0,2) chega a 0,85
   com os mesmos 10.000 sorteios, e nenhuma distribuição chega a 0,92 com 15 ativos.
2. O que impede venda a descoberto no SLSQP? **Os limites de 0 a 1.**
3. Qual ótima tem a menor volatilidade? **Variância mínima**, 9,67%, abaixo da menor sorteada
   (11,87%).

Amarração: A3 vale 3 pontos (PLANO_DE_ENSINO.md, seção 5), review da Sprint 3 em 19/11/2026 e
entrega na sexta, 20/11/2026, 23h59, por decisão do professor. O A4 vale 3 pontos e aparece nas
Sprints 3 e 4 na Adalove (P2, em aberto com a coordenação). Próxima instrução: Aula 05, 01/12/2026,
Validação e Robustez do Modelo.
