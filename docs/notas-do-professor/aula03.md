# Notas do professor: Aula 03

Correlação, Covariância e o Argumento Matemático da Diversificação. 10/11/2026 (terça), Semana 5,
Sprint 3, aula 22 do módulo. Horário de relógio a confirmar na Adalove (P1).

Material de condução, não distribuído ao aluno. Todo número abaixo vem de
`tools/medidas_aula03.py` e está travado em `tools/tests/test_aula03.py`. Retornos simples
diários do Adj Close preenchido para a frente por ativo, o mesmo tratamento da Aula 02; nenhuma
carteira da Ponderada 1 aparece na aula.

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
29,36%, BBDC4 34,09%, IVVB11 20,15%.

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
palpites antes de passar o cursor. Resposta: ITUB4 com BBDC4, 0,80. Palpites comuns: PETR4 com
VALE3 (0,41, por serem as duas maiores da bolsa) e BBAS3 com BOVA11 (0,76, segundo lugar entre os
pares citados).

| Pergunta quando a sala trava | Resposta esperada | Erro comum |
|---|---|---|
| A covariância de PETR4 com VALE3 é 0,0570. É alta? | Não dá para dizer sem as volatilidades; a correlação, 0,41, responde | ler covariância como se tivesse escala fixa |
| Por que a diagonal do heatmap é 1? | Todo ativo tem correlação 1 consigo mesmo | achar que é dado faltante |
| Por que a GOLD11 aparece com pares negativos? | O ouro tende a subir quando a bolsa cai; os dez pares mais negativos têm GOLD11 | ler correlação negativa como erro de dado |

## Bloco 3 (30 a 45): peso e correlação no widget

**Prever e observar.** Cada dupla anota o peso em PETR4 que dá o menor risco do par PETR4 e
IVVB11, antes de mover o controle. Resposta: 17,12% em PETR4, com risco de 18,85%, abaixo dos
20,15% do IVVB11 sozinho.

Previsões típicas: 0% ("o IVVB11 é menos arriscado, então tudo nele") e 50% ("meio a meio sempre
diversifica"). As duas revelam o mesmo erro, ignorar a correlação. Pedir que a dupla que disse 0%
mova o peso de 0% para 10% e leia o risco caindo.

Depois, trocar para ITUB4 e BBDC4: o menor risco é 29,22% com 86,14% em ITUB4, a 0,14 ponto
percentual do ITUB4 sozinho (29,36%). E BOVA11 com GOLD11: 13,47% com 43,11% em BOVA11.

**Pergunta socrática.** "Se a correlação de PETR4 com IVVB11 fosse 1, quanto vocês colocariam em
PETR4?" Resposta: nada; com correlação 1 o menor risco é o IVVB11 sozinho, 20,15%. Mova o
controle de correlação até 1 para mostrar.

## Bloco 4 (45 a 60): dupla no notebook

Seções 1, 3 e 4. Cronômetro de 12 minutos, troca de papel aos 6.

| Pergunta quando a dupla trava | Resposta esperada | Erro comum |
|---|---|---|
| A raiz da diagonal da PETR4 deu 2,47%. O que houve? | Faltou multiplicar por 252: essa é a volatilidade diária | anualizar só a correlação, ou esquecer o fator |
| A correlação deu 202 entre ITUB4 e BBDC4. | A correlação foi multiplicada por 252; correlação não se anualiza | aplicar o fator nas duas matrizes no mesmo passo |
| A matriz deu 225 pares e média estranha. | O `stack()` da versão do pandas manteve os NaN do triângulo de baixo; acrescentar `.dropna()` | contar a diagonal e os dois triângulos |
| Por que a GOLD11 tem menos pregões? | Estreia em 11/12/2020; o `ffill` não preenche antes da primeira cotação | preencher para trás com `bfill` |

Fechamento: cada dupla diz em uma linha onde a matriz entra no motor do A3 (na variância de cada
carteira sorteada, `w @ cov @ w`).

## Bloco 5 (60 a 75): correlação em crise e Ledoit-Wolf

**Prever.** Antes da animação, as duplas anotam o que acontece com as duas linhas em março de
2020. Resultado: ITUB4 com BBDC4 chega a 0,97 em 25/03/2020; PETR4 com IVVB11 sai de 0,01 no fim
de 2019 para 0,77 no fim de março de 2020. A correlação média dos pares vai de 0,36 na janela
inteira para 0,74 nos 22 pregões de março de 2020 (14 ativos, sem GOLD11).

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

Régua declarada no slide (convenção didática da aula): ρ a partir de 0,60 concentra, de 0,30 a
0,60 é intermediário, abaixo de 0,30 diversifica.

| Item | Par | ρ | Gabarito | Comentário falado |
|---|---|---|---|---|
| 1 | ITUB4 e BBDC4 | 0,80 | concentra | mesmo setor, mesmo risco de juros e crédito |
| 2 | BBAS3 e BOVA11 | 0,76 | concentra | o ETF carrega os bancos no índice |
| 3 | ITUB4 e BBAS3 | 0,71 | concentra | banco público e privado no mesmo ciclo |
| 4 | PETR4 e VALE3 | 0,41 | intermediário | duas commodities, ciclos distintos; a sala costuma dizer "concentra" |
| 5 | VALE3 e SUZB3 | 0,27 | diversifica | perto da borda; discutir que a régua é convenção |
| 6 | PETR4 e IVVB11 | 0,14 | diversifica | o par do widget |
| 7 | ITUB4 e IVVB11 | 0,08 | diversifica | bolsa americana em reais |
| 8 | BOVA11 e GOLD11 | −0,21 | diversifica | correlação negativa |

**Pensar e compartilhar.** Uma carteira só de bancos (ITUB4, BBDC4 e BBAS3 em partes iguais) tem
29,64% de volatilidade contra 32,61% de média das volatilidades: redução de 9,11%. Trocando dois
bancos por PETR4 e IVVB11, a redução vai a 27,18% (21,54% contra 29,58%). Resposta esperada às
trocas: um ativo com correlação baixa com os bancos, como IVVB11 (0,08 com ITUB4) ou GOLD11. Erro
comum: contar ativos ("três empresas, três riscos") em vez de medir correlação.

Nenhuma carteira da Ponderada 1 é usada aqui. Se um aluno perguntar pela própria carteira,
responder que o diagnóstico é individual e o método é o desta aula.

## Bloco 7 (90 a 105): quiz e amarração

| Pergunta | Correta | Distratores e o que revelam |
|---|---|---|
| ITUB4 e BBDC4 têm correlação 0,80 | os dois tendem a subir e cair nos mesmos dias | "sobe 0,80% quando o outro sobe 1%" confunde com beta; "80% dos dias com o mesmo sinal" confunde com contagem |
| Anualizar a covariância diária | multiplicar por 252 | raiz de 252 vale para o desvio padrão; anualizar a correlação é erro |
| Encolhimento de 10,72% com 63 pregões e 0,89% com 1.423 | menos pregões, estimativa mais ruidosa | "a crise de 2020 está nos 63 pregões" (começam em 03/06/2026); "percentual fixo" |

Amarração, com os pesos do `PLANO_DE_ENSINO.md`, seção 5: A3 Motor de Simulação de Monte Carlo,
peso 3, review da Sprint 3 em 19/11/2026 e entrega até sexta, 20/11/2026, 23h59; Ponderada 1,
peso 3, carteira individualizada pelo último dígito do RA e parecer situado no período analisado.
O A3 consome a matriz de covariância anualizada montada hoje. Na Aula 04, em 18/11/2026, a matriz
alimenta as 10.000 carteiras do motor.

Atenção: o roteiro do Bloco 7 no `PLANEJAMENTO_AULA_A_AULA.md` ainda diz "A3 (2, a confirmar na
Adalove)". O deck segue o `PLANO_DE_ENSINO.md`, seção 5, que registra peso 3.
