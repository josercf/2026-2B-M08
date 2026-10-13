# Notas do professor: Aula 05, Validação e Robustez do Modelo

Artefato interno de condução, não distribuído ao aluno. Aula de 01/12/2026 (terça), Semana 8,
Sprint 4, Aula 38 do módulo na Adalove; horário de relógio a confirmar (P1). Todo número abaixo vem
de `tools/medidas_aula05.py` e está travado em `tools/tests/test_aula05.py`. Amostra: tratamento de
ausência do módulo (ADR-009, `tools/retornos.py`), retornos do Adj Close na janela comum dos 15
ativos, 1.412 retornos de 04/01/2021 a 31/08/2026, com a lacuna de 24/10/2025 preenchida pelo preço
anterior (retorno zero em BOVA11, IVVB11 e GOLD11 nesse dia); anualização por 252, CDI das datas de
cada janela como taxa livre de risco. Divisão principal: treino 2023 e 2024 (499 pregões), teste
2025 (250 pregões).

## Antes do encontro

- Abrir o deck por HTTP (`python3 -m http.server 8000` na raiz) e conferir que os dois widgets
  montam e que os dois vídeos tocam no navegador da sala.
- Não distribuir o PDF exportado pelo botão do deck: ele revela o gabarito do Peer Instruction, do
  quiz final e da escolha coletiva.
- A Aula 04 usa a janela comum dos 15 ativos, que começa em 14/12/2020 (ADR-009); esta aula
  começa em 04/01/2021 para que as janelas caiam em anos e meses civis inteiros. Se um grupo estranhar que os pesos não batem com os
  da Aula 04, a resposta é exatamente o assunto do dia: outra janela, outros pesos.
- A Ponderada 2 é individual e vence nesta semana. Nada da aula usa a cesta nem os perfis da
  Ponderada; o exemplo é sempre a cesta de referência. Responder dúvidas de método, nunca de número
  da cesta individual.

## Daily (15 min)

Pergunta a cada equipe: qual janela de dados vocês usaram para calcular a fronteira do A4? Equipe
que não sabe dizer as datas sai da daily com essa tarefa, porque o Bloco 4 separa essa janela em
treino e teste.

## Bloco 1: resgate e Peer Instruction de abertura

Resgate (slide 3): "A Aula 04 deixou prontas as duas carteiras ótimas e a fronteira de 50 pontos.
Elas foram escolhidas olhando só para o passado. O que garante que funcionam no ano seguinte?"
Deixar duas ou três respostas sem corrigir e passar ao slide 4.

Pergunta do slide 5: a carteira de máximo Sharpe otimizada em 2023 e 2024 promete Sharpe 2,11.
Aplicada em 2025, o que ela entrega?

| Alternativa | Correta | Erro que revela |
|---|---|---|
| Perto de 2,11: os pesos são ótimos | não | trata "ótimo" como propriedade da carteira, e não da janela em que foi calculada |
| Menos, mas acima de 1 | não | intuição certa de que piora, sem dimensionar o erro do retorno esperado |
| Sharpe negativo: rende menos que o CDI | sim (-0,32) | |
| Mais, porque o CDI subiu | não | inverte o papel do CDI no Sharpe: CDI maior diminui o numerador |

Critério de discussão: entre 30% e 70% de acerto na primeira votação, dois minutos em dupla e nova
votação. Abaixo de 30%, tocar o final da animação do drawdown (slide 8, últimos 6 segundos) antes da
dupla. Acima de 70%, revelar e ir ao slide 6. Na revelação: acumulado de 10,96% contra 14,26% do
CDI; CDI de 12,00% no treino e 14,32% no teste.

**Turma sem pré-aula.** Se mais da metade não viu as animações, adiantar o slide 8 (animação do
drawdown, 26 segundos) para antes da votação, com a previsão escrita do próprio slide 8. O Peer
Instruction passa a medir a leitura do vídeo, e o Bloco 2 começa direto no slide 7.

## Bloco 2: o otimizador converge para o passado

Interação: pergunta disparada do slide 9, "que parte do resultado da Aula 04 o grupo ainda não
tinha testado?". Resposta esperada: retorno, Sharpe e pesos das duas carteiras foram calculados e
avaliados na mesma janela; nada foi medido fora dela.

- Pergunta socrática: "Por que a volatilidade prevista acertou e o retorno previsto errou?"
  Resposta esperada: a volatilidade de dois anos de retornos diários é estimada com muito mais
  precisão do que a média; o otimizador de máximo Sharpe ainda escolhe justamente os ativos cuja
  média saiu alta por acaso (Michaud, referência 5). Erro comum: atribuir tudo a "o mercado mudou",
  que é verdade e não explica por que a variância mínima errou menos.
- Pergunta socrática: "Se sortearmos 30% dos dias de 2023 a 2025 para teste, o resultado melhora ou
  piora?" Resposta: o número do notebook sobe e deixa de representar o que o comitê vai ver, porque
  o treino passa a conhecer dias posteriores ao teste. Erro comum: achar que sorteio é mais "científico" do que corte no
  tempo.
- Slide 8: antes de tocar, cada dupla anota em que mês cada carteira atinge a maior queda e qual cai mais (resposta: máximo Sharpe, -8,49% em 08/04/2025; variância mínima, -4,75% em 13/08/2025). Conferir as
  previsões ao fim, antes de ir ao slide 9.

## Bloco 3: widget da janela de treino

Interação: previsão antes de mover o controle. Cada dupla escreve um número: quanto da carteira de
máximo Sharpe troca de ativo quando a janela anda um mês.

- Começar na primeira janela (PETR4 76,5%, VALE3 23,5%) e andar uma janela por vez nas cinco
  primeiras, lendo a frase de baixo. Depois pular para a divisão principal (janela 25 de 33, treino
  01/2023 a 12/2024).
- Trocar para variância mínima e repetir: a marca coral (peso da janela anterior) fica quase em
  cima da barra.
- Resposta da previsão (slide 11): mediana de 11,91% ao mês no máximo Sharpe, máximo de 32,32%;
  3,23% e 7,88% na variância mínima. Em 25 das 33 janelas o máximo Sharpe entregou menos do que
  prometeu; a variância mínima, em 14.
- Pergunta socrática: "A variância mínima entregou mais do que prometeu na mediana (0,21 contra
  0,70). Isso quer dizer que ela é melhor?" Resposta esperada: quer dizer que a promessa dela é mais
  conservadora e depende menos do retorno estimado; melhor depende do perfil do cliente. Erro comum:
  escolher a carteira pelo Sharpe entregue de um único período.
- Slide 11, sobreposição: duas janelas vizinhas compartilham 11 dos 12 meses de teste (91,60% dos
  pregões, na mediana), e um mesmo pregão entra no teste de até 12 janelas; os 8.231 pregões de
  teste somados são 915 distintos. Pergunta socrática: "25 em 33 são 33 confirmações?" Resposta
  esperada: não, porque janelas vizinhas medem quase o mesmo período. Erro comum: ler a contagem
  como 33 experimentos e superestimar a evidência.
- Slide 12, anos disjuntos: com a mesma regra de treino cabem três anos de teste sem sobreposição
  (janelas 1, 13 e 25: 2023, 2024 e 2025). O máximo Sharpe entregou menos que prometeu em 2 de 3
  (0,67 contra 1,59 em 2023, 1,39 contra -0,25 em 2024, 2,11 contra -0,32 em 2025); a variância
  mínima, em 1 de 3. Nas 12 escolhas de mês de partida dos blocos, o máximo Sharpe fica abaixo em
  pelo menos 2 blocos em todas. Fechar com a frase: a base comporta três experimentos
  independentes, e o ADR do grupo diz isso.
- O drawdown à direita muda com a janela de teste. Perguntar em que janela aparece o fundo mais
  profundo e o que aconteceu no mercado naquele período.

## Bloco 4: backtest em dupla (12 min)

Interação: programação em dupla no notebook, seções 1 a 3, troca de papel aos 6 minutos.

Prática em camadas (slide 14, cronômetro de 12 minutos):

- **Obrigatório.** Rodar as seções 1 a 3, que já vêm escritas, e ler a tabela de esperado contra
  realizado; conferir o drawdown de -8,49% do máximo Sharpe; depois da troca de papel, auditar o
  desenho da seção 3: algum dado de 2025 entra na estimativa (look-ahead)? O CDI do teste é o
  comparador adequado? A dupla executa e audita, sem escrever código novo.
- **Extensão.** Seção 4: medir a sobreposição das 33 janelas e dizer quantos experimentos
  independentes elas contêm (o slide 12 tem a resposta).
- **Checagem aos 6 minutos.** Na volta pela sala: a tabela de esperado contra realizado está na
  tela e a dupla conferiu o drawdown. Dupla sem a tabela nesse ponto recebe ajuda antes da troca.
- **Debrief (3 minutos finais do bloco).** Cada dupla relata o problema de desenho que procurou e
  um número do A4 do grupo ainda não testado fora da amostra. Look-ahead: os pesos usam só
  `retornos.loc["2023":"2024"]`, e o teste começa depois do último dia do treino. Benchmark: o
  CDI das datas do teste é a taxa livre do Sharpe realizado, e o comitê compara a carteira com ele.
- **Contingência.** Se o Colab ou a rede falharem, a dupla segue a auditoria pelo código do slide
  13 e pela tabela do slide 9, com o professor projetando a saída da seção 3 do notebook já
  executado.

- Ponto de travamento comum: `retornos_teste @ w` com `w` numa ordem de ativos diferente da ordem
  das colunas. O notebook usa a mesma ordem de `retornos.columns`; quem montou pesos à mão por
  dicionário precisa reindexar.
- Segundo travamento: CDI e cesta com calendários diferentes. O `reindex` pelas datas da cesta
  alinha as duas séries, e uma data da cesta ausente do CDI daria `NaN` no Sharpe. A lacuna de
  24/10/2025 fica na cesta com retorno zero nos três ETFs (ADR-009), e o CDI tem essa data.
- Conferência rápida na sala: máximo Sharpe com drawdown de -8,49% em 08/04/2025.

## Bloco 5: sensibilidade da fronteira

Interação: previsão antes do clique no widget do slide 16. Cada dupla escolhe entre "retorno
perturbado em 5 p.p." e "Ledoit-Wolf". Registrar a contagem no quadro.

- Resultado (slide 17): o retorno perturbado troca 19,75% do máximo Sharpe e 0,00% da variância
  mínima; Ledoit-Wolf troca 1,91% e 1,81%. A PETR4 sobe de 17% para 27%.
- Pergunta socrática: "Por que a variância mínima não se mexe com o retorno perturbado?" Resposta:
  a função objetivo dela é só `w @ cov @ w`; o retorno esperado não entra. Erro comum: achar que
  toda carteira da fronteira depende do retorno esperado da mesma forma.
- Pergunta socrática: "5 p.p. é muito?" Resposta: o erro padrão mediano da média anual de um ativo
  com dois anos de dados é 17,63%; 5 p.p. é bem menos do que a incerteza que já existe. Erro comum:
  tratar o retorno médio histórico como dado, e não como estimativa.
- Pergunta socrática: "Então Ledoit-Wolf não serve?" Resposta: com 499 pregões e 15 ativos o
  encolhimento ótimo é 2,41%, e a amostral já é estável; com janela curta e muitos ativos o
  encolhimento cresce. O ADR do grupo cita o encolhimento medido na própria janela. O exemplo de
  ADR do REVISAO, com Ledoit-Wolf estabilizando os pesos, é um caso de janela curta.

## Bloco 6: estabilidade, ADR e escolha coletiva

Animação do slide 18: antes de tocar, cada dupla responde se o ativo de maior peso na primeira
janela continua no topo na última. Resposta: não; a PETR4 começa com 76,52% e perde espaço para
BBAS3, GOLD11 e IVVB11.

Slide 19: definir carteira trocada no quadro com um exemplo de dois ativos (60/40 para 40/60 troca
20%). Entre 2021-2022 e 2023-2024: 82,60% no máximo Sharpe e 33,23% na variância mínima.

Slide 20, custo da reotimização. Começar pela premissa, que é hipótese de aula, sem dado de
corretora: 0,10% sobre o valor negociado (compras mais vendas), sem custo na compra inicial, pesos
constantes entre reotimizações, de 02/01/2023 a 31/08/2026 (915 pregões). Reotimizar o máximo
Sharpe todo mês troca 156,87% da carteira por ano (13,25% por reotimização, na média) e custa 0,31
p.p. ao ano: retorno anual de 29,39% bruto e 29,08% líquido, Sharpe de 0,92 para 0,90. Trimestral:
87,50% ao ano, 0,18 p.p., 25,93% e 25,76%. Anual: 48,54% ao ano, 0,10 p.p., 20,77% e 20,68%.

- Pergunta socrática: "Então reotimizar todo mês é melhor?" Resposta esperada: a tabela não
  sustenta isso; a diferença de retorno bruto vem de um único caminho de 915 pregões, e outro
  período pode inverter a ordem. Erro comum: ler o retorno bruto da simulação como previsão.
- Pergunta socrática: "O que mudaria a conta?" Resposta: o custo real da corretora do parceiro,
  imposto sobre ganho de capital nas vendas e o tamanho do lote, nenhum deles medido aqui.

Slide 21, ADR de exemplo: é exercício com a cesta de referência, sem valor de recomendação
prática. A decisão aparece como hipótese condicionada ao custo, com a carteira trocada por ano e o
retorno líquido. O ADR do grupo que propuser frequência de reotimização segue o mesmo formato.

Dupla de 8 minutos (slide 22), troca de papel aos 4 minutos. A seção 6 do notebook repete o
widget do Bloco 5 e fica para casa.

- **Obrigatório.** Seção 5: rodar a carteira trocada entre os treinos de 2021 e 2022 e de 2023 e
  2024. Distribuir os cenários pelo número da dupla: ímpares leem o máximo Sharpe (82,60%), pares a
  variância mínima (33,23%). Depois da troca, o novo condutor escreve uma recomendação condicionada
  de duas linhas, no formato "recomendamos ... se ...", com a carteira trocada medida, e lê para a
  dupla vizinha, que leu a outra carteira. O ADR completo fica para depois da aula.
- **Extensão.** Depois da aula, para o A4: o ADR completo no modelo do curso, com o custo da
  reotimização do slide 20.
- **Checagem aos 4 minutos.** A carteira trocada da carteira da dupla está anotada. Critério para a
  recomendação lida em voz alta: cita o número medido e diz a condição sob a qual o comitê pode usar
  os pesos.
- **Debrief.** A escolha coletiva do slide seguinte, com duplas das duas carteiras na mesma sala.
- **Contingência.** Se o notebook não rodar, a dupla escreve a recomendação com o número do slide
  19, projetado pelo professor.

Escolha coletiva (slide 23, 4 minutos). Gabarito e o número que sustenta cada resposta:

| Recomendação | Gabarito | Número que sustenta |
|---|---|---|
| 1. O máximo Sharpe entrega Sharpe perto de 2 fora da amostra | não sustentada | -0,32 em 2025; mediana de 0,53 nas 33 janelas |
| 2. A variância mínima rendeu mais que o CDI em 2025 | sustentada | 22,83% contra 14,26% |
| 3. Os pesos de máximo Sharpe podem ficar um ano sem revisão | não sustentada | 11,91% trocados por mês na mediana; 82,60% entre biênios |
| 4. No máximo Sharpe, a volatilidade prevista errou menos que o retorno previsto | sustentada | 9,51% contra 10,35% na volatilidade; 32,05% contra 11,02% no retorno (na variância mínima é o contrário: 20,77% contra 21,12% no retorno, 7,46% contra 8,81% na volatilidade) |

Na recomendação 2, provocar: "sustentada para 2025; o que as 33 janelas dizem?" A variância mínima
teve Sharpe negativo em 5 das 33, lembrando que as janelas se sobrepõem. Um ano é um ponto, e a base
inteira comporta três anos de teste independentes; o comitê precisa saber disso.

Na recomendação 3, o número que sustenta é a troca de pesos. A frequência de revisão que substitui o
"um ano sem revisão" continua sendo hipótese: o slide 20 mostra a carteira trocada e o custo de cada
frequência, sem eleger uma.

## Bloco 7: quiz e amarração

Quiz de três perguntas (slide 24):

1. Vizinhas dividem 11 dos 12 meses de teste. Erro comum: "o treino de cada janela contém o teste";
   o teste sempre começa depois do último dia do treino. Na revelação: sem sobreposição cabem 3 anos
   de teste, e o máximo Sharpe ficou abaixo do prometido em 2.
2. 0,00%. Erro comum: 19,75%, que é o efeito no máximo Sharpe; quem marca isso não separou as duas
   carteiras.
3. Maior queda desde um pico. Erro comum: perda no ano; a carteira acumulou 10,96%.

Amarração: A4 vale 3 pontos (PLANO_DE_ENSINO.md, seção 5), entrega até sexta, 04/12/2026, 23h59,
review no mesmo dia. A observação do A4 pede que a instabilidade dos pesos seja comunicada ao
parceiro: o ADR da janela e do estimador é onde isso entra. Ponderada 2 vale 3 pontos, individual,
cesta e perfil pelo último dígito do RA; enunciado e barema na Adalove.

## Se o tempo apertar

Cortar primeiro o slide 13 (o código está no notebook) e reduzir a escolha coletiva para os itens 1
e 4. Não cortar o Bloco 5: a sensibilidade é o argumento técnico do ADR.
