# Notas do professor: Aula 02

Dados Financeiros: Do Preço ao Retorno. 05/11/2026 (quinta), Semana 4, Sprint 2, aula 13 do
módulo. Horário de relógio a confirmar na Adalove (P1).

Material de condução, não distribuído ao aluno. Todo número abaixo vem de
`tools/medidas_aula02.py` e está travado em `tools/tests/test_aula02.py`. Retornos do Adj Close
preenchido para a frente por ativo, a decisão do exemplo de ADR da Aula 01; a GOLD11 entra só a
partir de 11/12/2020.

## Antes de entrar na sala

- Abrir o deck por HTTP (`python3 -m http.server 8000` na raiz) e conferir que os dois widgets
  montam: retorno simples contra log no slide 10 e volatilidade em janela no slide 19.
- O widget do slide 10 abre em PETR4 com o log escondido. Só clicar em "Revelar log" depois de as
  duplas anotarem a previsão. O do slide 19 abre só com a janela de 252 pregões ligada; ligar 21 e
  63 depois da aposta da sala.
- Os dois vídeos tocam sem rede. O Chromium dos validadores não decodifica H.264; no navegador da
  sala, testar o play antes.
- A review da Sprint 2 é no dia seguinte, 06/11/2026. A daily vai trazer grupos ainda fechando o
  A1 e preocupados com o A2: o Bloco 7 diz em voz alta o que o A2 cobra e o que a P5 adia.

## Se a turma chega sem o pré-aula

Sinal: no primeiro voto do Peer Instruction, mais da metade marca -29,70%.

1. Não refazer o autoestudo em aula. Escrever no quadro ln(P_t / P_(t-1)) = ln(1 + r) e calcular
   ln(1 - 0,2970) com a sala, na calculadora do celular.
2. Tocar a animação `aula02-histograma-retornos` (24 s) antes do Bloco 4 em vez de depois, e pedir
   que as duplas observem só onde caem as barras coral.
3. Votar de novo. Se a maioria ainda errar, seguir para o Bloco 2: o widget do slide 10 é a mesma
   conta para oito pregões.
4. A animação `aula02-raiz-do-tempo` vira o apoio do Bloco 5 para quem não a viu; o slide 18 é o
   primeiro a cortar quando a turma fez o pré-aula.

## Bloco 1 (0 a 15): resgate e Peer Instruction

**Resgate.** "A Aula 01 deixou pronto o coletor parametrizado, com o Adj Close escolhido e a
decisão de ausências registrada em ADR." Perguntar a dois grupos o que o ADR deles decidiu. Quem
descartou as datas vai ter, hoje, março de 2020 fora da série e uma PETR4 menos volátil: anotar
para o desafio.

**Peer Instruction.** Em 09/03/2020 a PETR4 caiu 29,70% no retorno simples. Qual é o log?

| Alternativa | Correta | Erro que revela |
|---|---|---|
| -29,70% | não | acha que log e simples são a mesma coisa; vale só para movimento pequeno |
| -26,00% | não | calcula ln(1 + 0,2970) e troca o sinal: trata a queda como alta espelhada |
| -35,24% | sim | ln(1 - 0,2970) |
| -15,30% | não | usa log de base 10, o padrão da calculadora científica |

Critério de discussão em dupla: quem votou -35,24% defende com a fórmula, quem votou -26,00%
explica de onde tirou o número. Se a primeira votação passar de 70% de acerto, revelar direto; se
ficar abaixo de 30%, dar a fórmula e votar de novo; entre 30% e 70%, dois minutos de dupla.

## Bloco 2 (15 a 30): simples, log e a soma que erra

**Pergunta socrática.** "O retorno de dois pregões seguidos é a soma dos dois retornos?"
Resposta esperada: não; compõe pelo produto de (1 + r). Erro comum: somar percentuais.

**A soma da crise (slide 9).** 47 pregões da PETR4, 20/02 a 30/04/2020: soma dos simples
-34,19%, acumulado -40,92%, soma dos log -52,62%. A soma dos simples erra em 6,73 pontos.
Pergunta: "a soma dos log acertou?" Resposta: acertou o log do acumulado, ln(1 - 0,4092);
reportar -52,62% como perda é o segundo erro.

**Widget simples-log (slide 10), prever e observar.** Cada dupla anota a diferença na queda de
09/03/2020 e na alta de 13/03/2020 antes de revelar. Medido: queda com 5,54 pontos (-29,70%
contra -35,24%); alta de 22,22% contra 20,07%. Ponto a fixar: o log fica abaixo do simples nos
dois sentidos. Trocar para MGLU3 mostra altas de 25,14% (log 22,43%) em 16/11/2023.

## Bloco 3 (30 a 45): dupla no notebook, seções 2 e 3

Cronômetro de 12 minutos, troca de condutor aos 6. Circular perguntando:

- "Por que `fill_method=None`?" Resposta: a decisão de ausências é do ADR, não do padrão da
  biblioteca. Erro comum: tirar o argumento porque "dá na mesma" no pandas 3.0; no Colab com
  pandas 2.x o padrão preenche.
- "Por que a GOLD11 tem 1.423 retornos e os outros 1.907?" Resposta: estreia em 11/12/2020.

Respostas da seção 3: maior desvio diário MGLU3 (4,12%), menor GOLD11 (1,25%); média diária da
MGLU3 é -0,037%, e o retorno total dela na janela foi -90,26%.

## Bloco 4 (45 a 60): histograma e caudas

Prever antes da animação: onde caem os pregões de março de 2020. Depois do vídeo, a pergunta
disparada: **"o desvio padrão diz qual foi a pior queda do período?"**

Resposta esperada: não. O desvio diário da PETR4 é 2,47%, e a pior queda, -29,70%, fica a 12,06
desvios da média. A normal com o mesmo desvio prevê 5,1 pregões além de 3 desvios; houve 26, 12
deles em março de 2020. Curtose em excesso de 21,9. Erro comum: "três desvios cobrem 99,7%, então
a pior queda é cerca de 3 desvios", que é a regra da normal aplicada a um dado de caudas pesadas.

Pergunta de aprofundamento, se a sala estiver rápida: "se o otimizador só enxerga o desvio, o que
ele deixa de ver?" Resposta: a forma das caudas. A Aula 05 retoma com o drawdown.

## Bloco 5 (60 a 75): anualização e janela deslizante

**Conta no quadro (slide 17).** PETR4: média diária 0,1347% x 252 = 33,94%; desvio 2,4727% x
raiz de 252 (15,87) = 39,25%. Pedir que alguém faça desvio x 252 em voz alta: 623,12%. Pergunta:
"uma ação que oscila 623% ao ano?" A sala percebe o absurdo antes da explicação.

**Por que a raiz.** Variância soma em pregões independentes; desvio é a raiz da variância.
Animação do BOVA11: 63 pregões, 11,80% medido contra 11,80% previsto. Pergunta socrática: "a
regra vale para um ano?" Resposta honesta: aproxima pior, 15,70% medido contra 23,61% previsto
em 252 pregões, porque há só sete janelas anuais sem sobreposição e a independência é premissa.
O padrão de mercado continua sendo raiz de 252, e o ADR registra a premissa.

**Widget vol-janela (slide 19), prever e observar.** Aposta: qual janela reage primeiro e qual
sobe mais. Medido no BOVA11 em 2020: 21 pregões, 124,44% em 06/04; 63 pregões, 78,96% em 27/05;
252 pregões, 43,81% em 23/12. Na PETR4: 193,65%, 121,15% e 67,97%. Erro comum: achar que a janela
longa é "mais certa"; ela só é mais lenta.

## Bloco 6 (75 a 90): a cesta contra o CDI

Dupla no notebook, seções 5 e 6, cronômetro de 12 minutos. CDI acumulado na janela: 100,17%, ou
9,51% ao ano; desde 11/12/2020, para a GOLD11, 84,04%.

**Escolha coletiva (slide 22), gabarito.**

| Afirmação | Gabarito | Número que decide |
|---|---|---|
| A MGLU3 é o ativo de maior risco da cesta | sustentada | volatilidade anual de 65,41%, a maior |
| Na cesta, quem oscila mais rende mais | não sustentada | a MGLU3 tem a maior volatilidade e o menor retorno total, -90,26% |
| O BOVA11 rendeu mais que o CDI na janela | não sustentada | 98,84% contra 100,17% |
| A PETR4 entregou o maior retorno total da cesta | sustentada | 616,00%, acima dos 544,47% da WEGE3 |

Nove dos 15 ativos ficaram abaixo do CDI: ABEV3, BBAS3, BBDC4, BOVA11, EGIE3, ITUB4, MGLU3, RENT3
e SUZB3. Pergunta socrática para fechar: "então risco não paga?" Resposta: a relação entre risco
e prêmio do autoestudo vale para carteiras diversificadas em prazos longos; uma ação individual
em sete anos e meio pode contrariá-la. É o gancho da Aula 03.

## Bloco 7 (90 a 105): quiz e amarração

Quiz de três perguntas (slide 23), gabarito: -40,92%; 39,25%; 21 pregões.

Amarração, em voz alta:

- O A2 vale 3 pontos, entrega até sexta, 06/11/2026, 23h59, com review no mesmo dia.
- O barema: corretude 30%, visualizações 15%, leitura analítica 15%, reutilização 5%,
  especificação 15%, ADRs 20% (individual).
- **P5.** O A2 cobra matriz de correlação com heatmap e covariância anualizada, que a Aula 03 só
  ensina em 10/11/2026. O mínimo para 06/11 está na seção 9 do material e na seção 7 do notebook:
  `cov() * 252` e `corr()`. A pendência está em decisão com a coordenação; não prometer que o item
  sai do barema.

## Gabarito do desafio do notebook (não distribuir)

Volatilidade anual com a cesta inteira em `dropna` contra o preenchimento para a frente:

| Ativo | Descartar | Preencher |
|---|---|---|
| PETR4 | 33,41% | 39,25% |
| BBAS3 | 27,62% | 34,39% |
| MGLU3 | 67,75% | 65,41% |
| GOLD11 | 19,80% | 19,80% |

A BBAS3 é o ativo que mais perde volatilidade ao descartar; a MGLU3 é o único que ganha, porque os
pregões de 2019 e 2020 que o `dropna` remove eram, para ela, menos dispersos que os seguintes. A GOLD11 não muda, porque a série dela começa na
mesma data em que o `dropna` começa a cesta. Quem acertar a MGLU3 com a explicação merece nota de
participação.
