# Notas do professor: Aula 03

Correlação, Covariância e o Argumento Matemático da Diversificação. 10/11/2026 (terça), Semana 5,
Sprint 3, aula 22 do módulo. Horário de relógio a confirmar na Adalove (P1).

Material de condução, não distribuído ao aluno. Todo número abaixo vem de
`tools/medidas_aula03.py` e está travado em `tools/tests/test_aula03.py`. Tratamento de ausência
da ADR-009 (`tools/retornos.py`): a matriz da cesta usa a janela comum dos 15 ativos (1.423
retornos, de 14/12/2020 a 31/08/2026), a mesma que o otimizador da Aula 04 consome; par ou
subconjunto usa a janela comum dos ativos envolvidos; medida de um ativo usa a série inteira dele,
a da Aula 02. Nenhuma carteira da Ponderada 1 aparece na aula.

## Antes de entrar na sala

- Abrir o deck por HTTP (`python3 -m http.server 8000` na raiz) e conferir que os dois widgets
  montam: heatmap no slide 8 e peso e correlação no slide 11.
- O widget do slide 11 abre em PETR4 e IVVB11 com o peso de menor risco escondido. Só clicar em
  "Revelar o menor risco" depois de as duplas anotarem a previsão.
- Os dois vídeos tocam sem rede. O Chromium dos validadores não decodifica H.264; no navegador da
  sala, testar o play antes.

## Se a turma chega sem o pré-aula

Sinal: no primeiro voto do Peer Instruction, mais da metade marca "exatamente em 30%".

1. Não refazer o autoestudo em aula. Tocar a animação `aula03-curva-correlacao` (26 s) no slide
   10 antes de revelar o quiz, e pedir que as duplas observem só a posição do ponto de menor risco.
2. Fazer a conta do slide 5 no quadro, termo a termo: 0,0225 + 0,0225 + 0,0225.
3. Votar de novo. Se a maioria ainda errar, seguir para o Bloco 2 e retomar a fórmula no widget
   do Bloco 3, que é a mesma conta com números reais.
4. Lembrar que a Ponderada 1 é um dos autoestudos da semana: quem não fez a preparação tende a
   chegar sem ter aberto o enunciado.

## Bloco 1 (0 a 15): resgate e Peer Instruction

**Resgate.** "A Aula 02 deixou pronta a tabela de retorno e volatilidade anualizados da cesta,
com o CDI como referência." A tabela do slide 3 repete quatro linhas dela: PETR4 39,25%, ITUB4
29,36%, BBDC4 34,09%, IVVB11 20,15%, cada ativo na série inteira dele.

**Peer Instruction.** Dois ativos de 30% de volatilidade, correlação 0,5, metade em cada.

| Alternativa | Correta | Erro que revela |
|---|---|---|
| abaixo de 30% | sim, 25,98% | |
| exatamente em 30% | não | supor que o risco da carteira é a média das volatilidades, o que só vale com correlação 1 |
| acima de 30% | não | somar riscos como se a carteira fosse a soma dos dois ativos, ou confundir com alavancagem |

Critério de discussão: quem votou certo precisa defender com o termo cruzado da fórmula; a frase
genérica "diversificar reduz risco" não basta. Se o primeiro voto ficar entre 30% e 70% de acerto, a discussão em
dupla rende; acima de 70%, revelar direto; abaixo de 30%, seguir o roteiro da seção anterior.

## Bloco 2 (15 a 30): covariância, correlação e o heatmap

**Pergunta disparada:** qual par da cesta a sala aposta como o mais correlacionado? Recolher três
palpites antes de passar o cursor. Resposta: ITUB4 com BBDC4, 0,72 na janela comum dos 15 ativos.
Palpites comuns: PETR4 com VALE3 (0,21, embora sejam as duas maiores da bolsa) e BBAS3 com BOVA11
(0,65, segundo lugar entre os pares citados).

| Pergunta quando a sala trava | Resposta esperada | Erro comum |
|---|---|---|
| A covariância de PETR4 com VALE3 é 0,0212. É alta? | Não dá para dizer sem as volatilidades; a correlação, 0,21, responde | ler covariância como se tivesse escala fixa |
| Por que a diagonal do heatmap é 1? | Todo ativo tem correlação 1 consigo mesmo | achar que é dado faltante |
| Por que a GOLD11 e o IVVB11 aparecem com pares negativos? | O ouro tende a subir quando a bolsa cai, e o IVVB11 sobe em reais com o dólar; os 21 pares negativos têm um dos dois | ler correlação negativa como erro de dado |
| Por que o cursor mostra 1.423 pregões em todo par? | A matriz usa a janela comum dos 15 ativos, que começa em 14/12/2020 por causa da GOLD11 | achar que faltam dados nos outros ativos |

## Bloco 3 (30 a 45): peso e correlação no widget

**Prever e observar.** Cada dupla anota o peso em PETR4 que dá o menor risco do par PETR4 e
IVVB11, antes de mover o controle. Resposta: 17,12% em PETR4, com risco de 18,85%, abaixo dos
20,15% do IVVB11 sozinho.

Previsões típicas: 0% ("o IVVB11 é menos arriscado, então tudo nele") e 50% ("meio a meio sempre
diversifica"). As duas revelam o mesmo erro, ignorar a correlação. Pedir que a dupla que disse 0%
mova o peso de 0% para 10% e leia o risco caindo.

Depois, trocar para ITUB4 e BBDC4: o menor risco é 29,22% com 86,14% em ITUB4, a 0,14 ponto
percentual do ITUB4 sozinho (29,36%). E BOVA11 com GOLD11: 12,03% com 52,79% em BOVA11.

Cada par do widget é medido na janela comum dos dois ativos: 1.907 retornos desde 03/01/2019, ou
1.423 desde 14/12/2020 no par com a GOLD11. Se alguém notar que ITUB4 e BBDC4 têm 0,80 no widget e
0,72 no heatmap, a resposta é a janela: a do par inclui março de 2020, e a da matriz não. É a deixa
para o slide 15.

**Pergunta socrática.** "Se a correlação de PETR4 com IVVB11 fosse 1, quanto vocês colocariam em
PETR4?" Resposta: nada; com correlação 1 o menor risco é o IVVB11 sozinho, 20,15%. Mova o
controle de correlação até 1 para mostrar.

## Bloco 4 (45 a 60): custo da janela comum e dupla no notebook

**Custo da janela comum (slide 15, dois minutos antes da dupla).** A diagonal do slide 14 dá 33,40%
para a PETR4, e a Aula 02 deu 39,25%. A diferença é a janela: com a GOLD11, a matriz começa em
14/12/2020, deixa de fora 484 retornos e perde os 22 pregões de março de 2020. A correlação de PETR4
com IVVB11 cai de 0,14 (janela do par) para −0,09 (janela comum dos 15). Ligar com a Aula 01: é o
mesmo efeito de descartar datas que a turma mediu ao tratar ausências. Sem a GOLD11, a janela comum
dos 14 volta a 1.907 retornos, com março de 2020. Pergunta para a sala: "o parceiro ganha mais com o
ouro na cesta ou com o choque de 2020 na matriz?" Não há resposta certa; o que se cobra é o ADR do
estimador de covariância registrar a escolha com estes números.

**Dupla no notebook.** Seções 1, 3 e 4. Cronômetro de 12 minutos, troca de papel aos 6.

| Pergunta quando a dupla trava | Resposta esperada | Erro comum |
|---|---|---|
| A raiz da diagonal da PETR4 deu 2,10%. O que houve? | Faltou multiplicar por 252: essa é a volatilidade diária | anualizar só a correlação, ou esquecer o fator |
| A raiz da diagonal da PETR4 deu 39,25%, e não 33,40%. | A matriz saiu de `retornos.cov()` sem `dropna()`: cada par ficou na própria janela | pular a janela comum da ADR-009 |
| A correlação deu 181 entre ITUB4 e BBDC4. | A correlação foi multiplicada por 252; correlação não se anualiza | aplicar o fator nas duas matrizes no mesmo passo |
| A matriz deu 225 pares e média estranha. | O `stack()` da versão do pandas manteve os NaN do triângulo de baixo; acrescentar `.dropna()` | contar a diagonal e os dois triângulos |
| Por que a GOLD11 tem menos pregões? | Estreia em 11/12/2020; o `ffill` não preenche antes da primeira cotação, e a janela comum começa no primeiro retorno dela | preencher para trás com `bfill` |

Fechamento: cada dupla diz em uma linha onde a matriz entra no motor do A3 (na variância de cada
carteira sorteada, `w @ cov @ w`).

## Bloco 5 (60 a 75): correlação em crise e Ledoit-Wolf

**Prever.** Antes da animação, as duplas anotam o que acontece com as duas linhas em março de
2020. Resultado: ITUB4 com BBDC4 chega a 0,97 em 25/03/2020; PETR4 com IVVB11 sai de 0,01 no fim
de 2019 para 0,77 no fim de março de 2020. A correlação média dos pares vai de 0,36 na janela
inteira para 0,74 nos 22 pregões de março de 2020, na janela comum dos 14 ativos sem a GOLD11
(1.907 retornos); com a GOLD11, março de 2020 não estaria na janela.

**Pergunta disparada:** o que uma correlação que sobe na crise faz com a diversificação prometida
ao parceiro? Resposta esperada: a redução de risco calculada com a correlação média encolhe no
momento em que o parceiro mais precisa dela; o parecer precisa citar a correlação em crise ao lado
da média. Erro comum: concluir que diversificar "não funciona". Contra-argumento com número: mesmo
em março de 2020, a correlação média de 0,74 ainda é menor que 1.

**Ledoit-Wolf, em três minutos.** 15 ativos, 120 números estimados. Encolhimento de 10,72% com 63
pregões, 5,46% com 126, 3,45% com 252 e 0,89% com 1.423. Pergunta: "por que encolher mais com
menos dados?" Resposta: menos observações por número estimado, mais ruído. Se o tempo apertar,
este slide vira fala.

## Bloco 6 (75 a 90): escolha coletiva e carteira só de bancos

Régua declarada no slide 21 como heurística exploratória da aula, sem valor de regra de decisão:
ρ a partir de 0,60 concentra, de 0,30 a 0,60 é intermediário, abaixo de 0,30 diversifica. Os
limiares organizam a discussão; quem decide a redução de risco é a conta com peso, volatilidade e
correlação, e a correlação muda com a janela. O gabarito abaixo é o da heurística sobre a matriz
da cesta, e o slide 22 confere cada par com a carteira 50/50.

| Item | Par | ρ | Gabarito pela heurística | Comentário falado |
|---|---|---|---|---|
| 1 | ITUB4 e BBDC4 | 0,72 | concentra | mesmo setor, mesmo risco de juros e crédito |
| 2 | BBAS3 e BOVA11 | 0,65 | concentra | o ETF carrega os bancos no índice |
| 3 | ITUB4 e BBAS3 | 0,61 | concentra | perto da borda de 0,60; discutir que o limiar é arbitrário |
| 4 | PETR4 e BOVA11 | 0,53 | intermediário | a Petrobras pesa no índice, ao lado de dezenas de outras ações |
| 5 | PETR4 e VALE3 | 0,21 | diversifica | duas commodities, ciclos distintos; a sala costuma dizer "concentra" |
| 6 | ITUB4 e IVVB11 | −0,08 | diversifica | bolsa americana em reais |
| 7 | PETR4 e IVVB11 | −0,09 | diversifica | o par do widget, que na janela do par tem 0,14 |
| 8 | BOVA11 e GOLD11 | −0,21 | diversifica | correlação negativa |

As correlações são as da matriz da cesta, na janela comum dos 15 ativos (1.423 retornos desde
14/12/2020).

**Revelação com a carteira 50/50 (slide 22).** Pesos de 50% em cada ativo, medidos na janela
comum do par (ADR-009). A redução compara a volatilidade anual da carteira com a média ponderada
das duas volatilidades.

| Par | ρ na cesta | ρ no par | Janela do par (início, retornos) | Volatilidades | Média ponderada | Carteira | Redução |
|---|---|---|---|---|---|---|---|
| ITUB4 e BBDC4 | 0,72 | 0,80 | 03/01/2019, 1.907 | 29,36% e 34,09% | 31,72% | 30,13% | 1,59 p.p. (5,01%) |
| BBAS3 e BOVA11 | 0,65 | 0,76 | 03/01/2019, 1.907 | 34,39% e 23,41% | 28,90% | 27,19% | 1,71 p.p. (5,92%) |
| ITUB4 e BBAS3 | 0,61 | 0,71 | 03/01/2019, 1.907 | 29,36% e 34,39% | 31,87% | 29,51% | 2,37 p.p. (7,43%) |
| PETR4 e BOVA11 | 0,53 | 0,69 | 03/01/2019, 1.907 | 39,25% e 23,41% | 31,33% | 28,94% | 2,39 p.p. (7,63%) |
| PETR4 e VALE3 | 0,21 | 0,41 | 03/01/2019, 1.907 | 39,25% e 35,49% | 37,37% | 31,39% | 5,98 p.p. (16,01%) |
| ITUB4 e IVVB11 | −0,08 | 0,08 | 03/01/2019, 1.907 | 29,36% e 20,15% | 24,75% | 18,48% | 6,27 p.p. (25,33%) |
| PETR4 e IVVB11 | −0,09 | 0,14 | 03/01/2019, 1.907 | 39,25% e 20,15% | 29,70% | 23,28% | 6,42 p.p. (21,62%) |
| BOVA11 e GOLD11 | −0,21 | −0,21 | 14/12/2020, 1.423 | 18,50% e 19,80% | 19,15% | 12,06% | 7,09 p.p. (37,01%) |

Pontos para a fala: (1) na janela do par, PETR4 e BOVA11 sobe de 0,53 para 0,69 e PETR4 e VALE3 de
0,21 para 0,41, e os dois trocariam de classe pela heurística; (2) PETR4 com IVVB11 corta 6,42 p.p.
e 21,62% da média, e ITUB4 com IVVB11 corta 6,27 p.p. e 25,33%; a ordem dos dois pares depende da
medida escolhida, porque a volatilidade da PETR4 eleva a média ponderada; (3) a maior redução,
37,01%, vem do único par com correlação negativa nas duas janelas. Erro comum: tratar o limiar de
0,30 como critério de aprovação de um par no parecer do A3.

**Pensar e compartilhar.** Uma carteira só de bancos (ITUB4, BBDC4 e BBAS3 em partes iguais) tem
29,64% de volatilidade contra 32,61% de média das volatilidades: redução de 9,11%. Trocando dois
bancos por PETR4 e IVVB11, a redução vai a 27,18% (21,54% contra 29,58%). As duas carteiras são
medidas na janela comum dos três ativos, 1.907 retornos desde 03/01/2019. Resposta esperada às
trocas: um ativo com correlação baixa com os bancos, como IVVB11 (−0,08 com ITUB4 na matriz) ou
GOLD11. Erro
comum: contar ativos ("três empresas, três riscos") em vez de medir correlação.

Nenhuma carteira da Ponderada 1 é usada aqui. Se um aluno perguntar pela própria carteira,
responder que o diagnóstico é individual e o método é o desta aula.

## Bloco 7 (90 a 105): quiz e amarração

| Pergunta | Correta | Distratores e o que revelam |
|---|---|---|
| ITUB4 e BBDC4 têm correlação 0,72 | os dois tendem a subir e cair nos mesmos dias | "sobe 0,72% quando o outro sobe 1%" confunde com beta; "72% dos dias com o mesmo sinal" confunde com contagem |
| Anualizar a covariância diária | multiplicar por 252 | raiz de 252 vale para o desvio padrão; anualizar a correlação é erro |
| Encolhimento de 10,72% com 63 pregões e 0,89% com 1.423 | menos pregões, estimativa mais ruidosa | "a crise de 2020 está nos 63 pregões" (começam em 03/06/2026); "percentual fixo" |

Amarração, com os pesos do `PLANO_DE_ENSINO.md`, seção 5: A3 Motor de Simulação de Monte Carlo,
peso 3, review da Sprint 3 em 19/11/2026 e entrega até sexta, 20/11/2026, 23h59; Ponderada 1,
peso 3, carteira individualizada pelo último dígito do RA e parecer situado no período analisado.
O A3 consome a matriz de covariância anualizada montada hoje, na janela comum dos 15 ativos. Na Aula 04, em 18/11/2026, a matriz
alimenta as 10.000 carteiras do motor.

Atenção: o roteiro do Bloco 7 no `PLANEJAMENTO_AULA_A_AULA.md` ainda diz "A3 (2, a confirmar na
Adalove)". O deck segue o `PLANO_DE_ENSINO.md`, seção 5, que registra peso 3.
