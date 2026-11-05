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
| 6 | 1 | QR da moeda; liberar uma rodada por vez e esperar a maioria jogar |
| 7 a 9 | 2 | o artigo em Python, a simulação (a turma anota o palpite da mediana antes) e a tabela do Bodie |
| 10 e 11 | 3 | BBDC4 e as quatro frases do comitê |
| 12 | 3 | gerar os links, copiar para o Slack, iniciar o prazo de 25 min |
| 13 | 4 e 5 | cronômetro da sala; checagem aos 12 min |
| 14 a 17 | 6 | ADR do grupo ao vivo e voto da sala; o veredito sai da fala do professor |
| 18 a 20 | 7 | o que vai para o A2, referências, encerramento |

## Moeda

- Teoria para a fala: 10 rodadas dão média esperada de R$ 162,89 e mediana de R$ 59,05; 20 rodadas
  dão R$ 265,33 e R$ 34,87.
- Se na rodada 10 a mediana da sala ainda estiver acima de R$ 100, seguir até a 20.
- O botão Zerar volta a rodada para 0 e permite jogar de novo do começo com novos apelidos.
- Plano B sem rede: moeda física, saldo no papel e a tabela teórica acima.

## Links e prazo

- "Gerar os links dos grupos" cria um token por grupo e devolve sempre os mesmos, então gerar de
  novo não invalida o link já enviado.
- Os endereços aparecem borrados no projetor; passar o mouse para ler, ou usar "Copiar os quatro
  para o Slack".
- O prazo é do servidor e trava a ADR dos quatro grupos ao mesmo tempo. Para estender, digitar os
  minutos que faltam e clicar de novo em "Iniciar prazo".
- Plano B: se às 13h15 o banco ao vivo falhar no ensaio, a ADR vai para um documento
  compartilhado por grupo, com os mesmos seis campos.

## Depois da aula

- Cada grupo baixa a ADR em Markdown pelo deck e commita no repositório do A2.
- Para limpar o ensaio no banco: apagar as linhas da sessão `m08-aula02-ensaio` em `adr_campos`,
  `adr_prazos`, `adr_tokens`, `moeda_jogadas`, `moeda_jogadores` e `moeda_sessoes`.
