# Notas do professor: Aula 02

Pontos cegos do retorno. 05/11/2026 (quinta), 14h, Semana 4, Sprint 2, aula 13 do módulo.
Redesenhada em 05/11/2026 (ADR-016).

Este arquivo é público, porque o repositório inteiro vai para o GitHub Pages. Por isso ele traz
só a logística. Veredito, número decisivo e erro comum de cada grupo ficam no gabarito, em
`Inteli - Adm Tech - M08 - LBL/aula02-gabarito/`, fora do git.

## Antes de entrar na sala

- Abrir `aulas/aula02.html` no navegador da sala com `?quiz-chave=<chave>` uma vez. A mesma chave
  do quiz da Aula 01 libera a moeda, gera os links e inicia o prazo.
- Ensaio sem tocar no banco da aula: `?sessao=m08-aula02-ensaio` em todas as páginas, ou
  `?quiz-demo=1` para rodar tudo na memória do navegador.
- Deixar o Slack aberto com os canais dos quatro grupos (G01 a G04).

## Ordem dos slides

| Slides | Bloco | O que fazer |
|---|---|---|
| 1 a 4 | abertura | agenda, resgate da Aula 01 e daily com cronômetro de 15 min |
| 5 | 1 | voto "vale jogar?" em duas rodadas, sem revelar nada |
| 6 | 1 | os celulares do quiz trocam sozinhos para a moeda; liberar uma rodada por vez; aba Trajetórias no fim |
| 7 | 1 | voto de cada aluno contra o saldo dele, sem nomes |
| 8 | 2 | case da SUZB3 projetado na lousa: um aluno por área, resposta só depois da discussão |
| 9 e 10 | 2 | o artigo em Python e a simulação com a cena dos 12 jogadores (palpite da mediana antes) |
| 11 | 2 | mesma média, três moedas: revelar uma linha por vez e só então a regra do capítulo 5 |
| 12 e 13 | 3 | BBDC4: promessa contra vivido, imposto da volatilidade e o retorno de quem aporta todo ano |
| 14 | 3 | o que cada grupo faz e entrega, com tempo |
| 15 | 4 e 5 | links do Slack e os 25 minutos do servidor, com marco aos 12 |
| 16 a 19 | 6 | ADR do grupo ao vivo e voto da sala; o veredito sai da fala do professor |
| 20 a 22 | 7 | o que vai para o A2, referências, encerramento |

## Moeda

- O jogo tem 10 rodadas, como no enunciado do voto. Teoria para a fala: média esperada de
  R$ 162,89 e mediana de R$ 59,05.
- Com uns 30 alunos, há cerca de uma chance em oito de a mediana da sala terminar acima de R$ 100 por
  sorte. Se acontecer, a aba Trajetórias e a simulação de 10.000 jogadores (slide 8) mostram o efeito
  sem depender da sorte da sala.
- A aba Trajetórias do slide mostra uma linha por aluno, rodada a rodada, com a média e a mediana.
- O botão Zerar pede um segundo clique, apaga o jogo e volta para a rodada 0; os celulares do quiz
  entram de novo sozinhos.
- Plano B sem rede: moeda física, saldo no papel e a tabela teórica acima.

## Links e prazo

- Com a chave no navegador, os quatro links aparecem sozinhos no slide 15. O token de cada grupo é
  fixo na sessão: abrir o slide de novo devolve os mesmos links.
- "Iniciar 25 minutos" grava o prazo no servidor; o relógio grande do slide é esse mesmo prazo, e o
  marco dos 12 minutos aparece nele. "+5 minutos" estende para todos.
- O prazo é do servidor e trava a ADR dos quatro grupos ao mesmo tempo. Para estender, digitar os
  minutos que faltam e clicar de novo em "Iniciar prazo".
- Plano B: se às 13h15 o banco ao vivo falhar no ensaio, a ADR vai para um documento
  compartilhado por grupo, com os mesmos seis campos.

## Depois da aula

- Cada grupo baixa a ADR em Markdown pelo deck e commita no repositório do A2.
- Para limpar o ensaio no banco: apagar as linhas da sessão `m08-aula02-ensaio` em `adr_campos`,
  `adr_prazos`, `adr_tokens`, `moeda_jogadas`, `moeda_jogadores` e `moeda_sessoes`.
