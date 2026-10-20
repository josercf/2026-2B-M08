# ADR-013: Abertura animada da Aula 01, agenda enxuta nas seis aulas e esteira de artefatos

**Data:** 20/10/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

Na revisão do deck da Aula 01 em 20/10/2026, o professor apontou quatro problemas na abertura:

- o perfil tinha um monograma no lugar da foto e uma formação incompleta, montada a partir de uma
  fonte pública de 2018;
- os combinados estavam certos no conteúdo e mecânicos na forma, uma tabela de cinco linhas;
- a agenda repetia na tela os minutos de cada bloco, a interação que fecha o bloco e a nota de
  horário de relógio pendente, que são informação de roteiro e não de turma;
- as cinco entregas apareciam numa trilha única, sem mostrar que cada artefato consome o anterior
  e sem espaço para o detalhe de cada um.

A agenda com quatro colunas e a nota de horário existia nas seis aulas, com a mesma estrutura.

## Decisão

A abertura da Aula 01 passa a ter animação de entrada e uma esteira de artefatos com um slide
comum e um slide por artefato, e a agenda das seis aulas mostra só bloco e tema.

Em detalhe:

1. **Perfil.** Foto do professor com a família (`assets/img/professor-familia.jpg`, 1100 px de
   largura) e a formação e a docência informadas por ele em 20/10/2026.
2. **Combinados.** Linha do tempo da semana com três marcos (durante o encontro, fim da instrução,
   sexta-feira), desenhada ao entrar no slide, e a faixa de uso de IA embaixo.
3. **Agenda.** Colunas Bloco e Tema. Minutos, interação de fechamento e horário continuam no
   `PLANEJAMENTO_AULA_A_AULA.md`, travados em `tools/tests/test_planejamento.py`, e nos
   comentários de cabeçalho de cada deck.
4. **Artefatos.** O artefato ganha um selo, o ícone `deployed_code` do kit (um cubo isométrico)
   com o código A1 a A5. A esteira mostra as cinco estações e o que passa de uma para a outra; o
   slide comum mostra o barema 65/15/20; cada artefato tem um slide com o que recebe, o que é, o
   que entrega, os critérios próprios que somam 65% e o que fica fora do escopo.
5. **Bloco 2 desenhado.** Um slide de eventos corporativos com exemplo genérico vem antes das
   três visões, que viram um esquema animado; a animação da MGLU3 vem depois dos termos; um slide
   com a função `preco_negociado` do notebook introduz o widget da B3SA3. O slide do end exclusivo
   vira um calendário de agosto de 2026, lido do snapshot, em que cada alternativa conta os dias e
   os faz voar até a linha dela (`assets/js/inteli-calendario.js`).
6. **Coletor em três visões.** O slide do coletor vira três: o fluxo de decisão para quem não lê
   código, a função linha a linha com a janela que desliza a cada fragment
   (`assets/js/inteli-codigo.js`) e a revisão de código com quatro pontos a manter e quatro a
   revisar. A função do notebook foi formatada em até 79 colunas, sem mudar o comportamento, para
   caber inteira no slide; o `check_slides.py` passou a descontar o que um ancestral com
   `overflow` recorta.
7. **Animação.** Classe `.entrada` com atraso por `--atraso`, só no slide presente. O estado de
   repouso é o visível, então slide fora de cena, validador de layout e PDF veem o estado final.

## Motivações

- A turma lê o slide de agenda para saber o que vem, e minutos contados a partir da daily sem
  horário de relógio confundem mais do que orientam.
- Mostrar o que cada artefato recebe e entrega torna explícita a dependência entre sprints, que é
  o argumento do A1: nenhuma análise das próximas sprints é melhor do que os dados coletados nele.
- A aula é de computação: o slide que introduz o widget mostra o código que o aluno roda no
  notebook, e o teste trava que os dois textos são iguais.
- O ícone `deployed_code` já está no kit Sharp e repete a geometria de três faces do grafismo, o
  que dispensa desenhar um ícone próprio. Se a Adalove tiver um ícone de artefato que o professor
  prefira, a troca é um nome no sprite.
- Animar por CSS, sem biblioteca, mantém o acervo sem build e sem dependência nova.

## Riscos conhecidos

- **Tempo do Bloco 1.** A abertura ganhou sete slides (esteira, barema comum e cinco artefatos)
  além da nuvem de palavras. Mitigação: os slides de artefato são de referência, para passar em
  cerca de um minuto cada; o comentário de cabeçalho do deck registra o que cortar primeiro.
- **Animação escondendo conteúdo no PDF ou no validador.** Mitigação: animação só em
  `section.present`, desligada em `html.print-pdf` e em `prefers-reduced-motion`, com
  `tools/tests/test_abertura_aula01.py` conferindo a opacidade final no navegador e com movimento
  reduzido.
- **Foto pessoal publicada.** O repositório inteiro vai para o GitHub Pages, e a foto mostra
  familiares. Mitigação: a publicação foi pedida pelo próprio professor; remover a foto é apagar o
  arquivo e a `figure` do slide.
- **Critérios de barema digitados.** Os pesos dos critérios vêm do
  `REVISAO-LBL08-COMPUTACAO.md`, que fica fora do repositório. Mitigação: o teste confere que os
  critérios de cada artefato somam 65% e que sprint e peso batem com o `PLANO_DE_ENSINO.md`.

## Consequências

Positivas:

- A agenda das seis aulas fica com o mesmo formato, mais curto e legível do fundo da sala.
- O professor tem um slide por artefato para voltar a ele na abertura de cada sprint.

Negativas:

- A Aula 01 passa de 28 para 39 slides, e os números de slide citados nas notas do professor
  mudaram.
- O roteiro de cada bloco deixa de aparecer na tela; quem conduz a aula consulta o planejamento ou
  as notas.

## ADRs relacionadas

- ADR-004, sala de aula invertida em três tempos: a interação que fecha cada bloco continua
  obrigatória no roteiro.
- ADR-011, tema no brand kit vigente: canto reto, ícone Sharp e pesos do `TIP-04` valem para os
  componentes novos.
- ADR-012, nuvem de palavras por voz com n8n: o slide que antecede o parceiro na mesma abertura.
