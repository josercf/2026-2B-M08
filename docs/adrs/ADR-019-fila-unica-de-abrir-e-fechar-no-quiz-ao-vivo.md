# ADR-019: Fila única de abrir e fechar rodada no quiz ao vivo e reabertura de slide já visitado

- **Data:** 17/11/2026
- **Status:** aceita
- **Decisores:** Prof. José Romualdo

## Contexto

Na Aula 03, em 10/11/2026, 15 alunos entraram no quiz pelo QR code e nenhum voto foi registrado
nas duas perguntas de verificação do preparo. Nas Aulas 01 e 02 o mesmo componente registrou de
10 a 22 votos por pergunta. A investigação de 17/11/2026 reproduziu dois defeitos em modo de
memória:

1. Slide de quiz já visitado não reabria a votação. A votação só abria com o slide na fase
   `parada`; sair do slide deixava a fase em `encerrada`, e voltar a ele não fazia nada. Com
   `data-rodadas="1"` e sem `data-correta`, o slide também não mostrava botão. O banco registra as
   duas rodadas da Aula 03 abertas pela primeira vez às 12h51, uma hora e meia antes da aula, o
   que é coerente com um ensaio que percorreu o deck.
2. Corrida entre fechar e abrir em slides de quiz seguidos, formato introduzido na Aula 03. A
   função `quiz_fechar` fecha todas as rodadas abertas da sessão. Na troca de slide, o `fechar`
   do slide que sai e o `abrir` do slide que entra saíam ao mesmo tempo, e quando o `fechar`
   chegava depois ele derrubava a rodada recém-aberta. O banco registra as duas rodadas fechadas
   com 6 ms de diferença.

A Aula 04 usa quizzes seguidos nos blocos 2 e 7, com `data-rodadas="1"`.

## Decisão

As chamadas de abrir e fechar rodada de todos os componentes da página passam por uma fila única
em `assets/js/inteli-quiz-dados.js`, com os fechamentos antes das aberturas, e o slide de quiz
reabre a votação ao ser revisitado.

## Motivações

- A fila elimina a corrida sem alterar o SQL em produção na véspera de uma aula.
- Reabrir sozinho quando a rodada encerrada tem zero voto cobre o caso do ensaio antes da aula,
  que é o que a evidência indica ter acontecido.
- Com votos, o resultado permanece na tela e a reabertura é uma ação explícita do professor
  (botão "Reabrir votação"), para não apagar da tela um resultado já discutido.

## Riscos conhecidos

- `quiz_fechar` continua fechando a sessão inteira. Duas abas do deck abertas com a chave do
  professor ainda se atrapalham. Mitigação: o slide detecta o fechamento externo, avisa e oferece
  "Reabrir votação". A correção definitiva é fechar por pergunta no SQL, ainda não escrita.
- Voto dado na sessão real durante o ensaio conta como voto, e nesse caso o slide não reabre
  sozinho na aula. Mitigação: ensaiar com `?quiz-demo=1`.
- A fila só foi exercitada em memória, com latência simulada por `?quiz-demo-atraso=`. Abrir e
  fechar no banco real exige a chave do professor. Mitigação: roteiro de teste no site publicado,
  registrado nas notas do professor da Aula 04.
- Requisição que não responde seguraria a fila. Mitigação: a fila libera depois de 8 segundos.

## Consequências

- Positivas: dois slides de quiz seguidos funcionam nas duas ordens de chegada; ensaiar o deck
  antes da aula deixa de inutilizar o quiz; sete testes de regressão em
  `tools/tests/test_quiz_vivo.py`, com prefixo `test_aula03_`.
- Negativas: abrir e fechar ficam serializados, então uma troca rápida de slides pode levar
  alguns décimos de segundo a mais para refletir no celular; a interface ganha um botão.

## ADRs relacionadas

- ADR-004 (sala de aula invertida, verificação do preparo), ADR-016 (Aula 02 com ADR online e
  jogo da moeda no mesmo banco), ADR-017 (Aula 03 com a verificação em dois slides), ADR-018
  (Aula 04 em turnos).
