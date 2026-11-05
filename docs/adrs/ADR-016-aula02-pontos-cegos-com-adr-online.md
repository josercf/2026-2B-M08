# ADR-016: Aula 02 redesenhada em pontos cegos, com moeda no celular e ADR online por grupo

**Data:** 05/11/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A versão da Aula 02 de 13/10/2026 cobria retorno simples e logarítmico, histograma, anualização e
volatilidade em janela deslizante em 28 slides. O professor avaliou que ela ficou expositiva e
genérica, com pouca ligação com os dois autoestudos da semana (capítulo 5 de Bodie, Kane e Marcus e
o artigo do Turing Talks sobre análise de uma ação em Python). A ADR-015 publicava essa versão pelo
Palco, que o professor não está usando.

## Decisão

A Aula 02 passa a ser conduzida em `aulas/aula02.html`, organizada em pontos cegos do retorno: jogo
da moeda no celular, a mesma conta em Python, a ponte com o BBDC4 e um comitê em que cada grupo
checa a frase de um assessor e registra a decisão numa ADR online, com prazo dado pelo servidor.

## Motivações

- A moeda (+50% ou -40%) faz a turma viver a distância entre média aritmética e geométrica antes da
  fórmula, que é o argumento central do capítulo 5 e o exemplo de +5% e -2% do artigo.
- A frase do assessor põe o aluno de administração no papel de quem decide com dado, que é o
  objetivo do módulo.
- A ADR online coletiva treina o registro de decisão que o A2 já cobra.

## Riscos conhecidos

- O banco ao vivo falhar em sala. Mitigação: as páginas funcionam em memória com `?quiz-demo=1`, e o
  plano B é moeda física e ADR em documento compartilhado.
- Com uns 30 alunos e 10 rodadas, a mediana da sala pode ficar acima de R$ 100 por sorte (perto de
  uma chance em oito). Mitigação: o jogo aceita até 20 rodadas.
- O gabarito vazar pelo repositório público. Mitigação: veredito e números que desmontam as frases
  ficam fora do git, com uma varredura que reprova se algum deles aparecer no acervo.
- Token de grupo exposto no projetor. Mitigação: o painel de links borra os endereços.

## Consequências

- Positivas: menos conteúdo e mais tempo de prática; os autoestudos aparecem na aula; cada grupo sai
  com uma ADR para o A2.
- Negativas: retorno logarítmico e janela deslizante saem do encontro e ficam só no material de
  apoio; o acervo ganha duas tabelas de banco por sessão (`adr_*` e `moeda_*`, em
  `exemplos/aula02-supabase/aula02.sql`).

## ADRs relacionadas

- ADR-004 (sala de aula invertida), ADR-015 (substituída por esta), ADR-009 (tratamento de ausência
  usado nas medições).
