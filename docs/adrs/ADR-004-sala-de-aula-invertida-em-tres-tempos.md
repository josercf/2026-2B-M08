# ADR-004: sala de aula invertida em três tempos

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

O Encontro de Instrução do Inteli tem 2 horas, divididas em autoestudo prévio na Adalove, daily da
equipe de 15 minutos e 105 minutos de metodologia ativa em sete blocos de até 15 minutos
(`inteli-course-design`, seção 1). O conteúdo de cada uma das seis instruções de Computação deste
módulo soma exposição conceitual, demonstração sobre dado real e prática no notebook, e os 105
minutos não cabem as três coisas: a semana 8, por exemplo, tem HTTP, FastAPI e HTML/JS no mesmo
encontro (design, seção 16).

A quarta decisão de 17/09/2026 é que as aulas seguem sala de aula invertida explícita, com uso
intenso de imagem, animação e notebooks prontos para o Colab (design, seção 1). O autoestudo já
existe na Adalove como carga reservada, e o encontro já pressupõe que ele foi feito
(`inteli-course-design`, seção 1), sem nada no acervo que verifique isso.

## Decisão

Toda aula é desenhada em três tempos de sala invertida, e o encontro abre medindo o preparo.

## Motivações

1. **O tempo do encontro passa a ser gasto no que exige a presença do professor.** A exposição
   conceitual desce para o pré-aula, e os 105 minutos ficam com demonstração sobre dado real,
   prática em dupla e discussão de decisão de negócio.
2. **O preparo deixa de ser suposição.** A abertura do encontro é uma Peer Instruction sobre o
   conteúdo pré-aula, com distratores construídos a partir de números reais da cesta, o que dá ao
   professor uma medida imediata de quantos chegaram preparados.
3. **A densidade da semana 8 tem onde ser resolvida.** Os dois autoestudos da semana carregam
   HTTP, JSON e `fetch` antes do encontro, e o encontro fica com a integração (design, seção 16, e
   ADR-002).
4. **A mídia produzida por código tem para onde ir.** As animações do conceito central vivem na
   seção "Preparação" do material de apoio, e o aluno as assiste antes da aula, quantas vezes
   quiser (ADR-005).

## Os três tempos

| Tempo | Onde vive no acervo | Conteúdo |
|---|---|---|
| Antes (pré-aula) | autoestudos na Adalove e seção "Preparação" do material de apoio | os dois autoestudos da semana, duas a três animações curtas do conceito central e uma autoverificação de cinco perguntas sem nota |
| Durante (encontro) | deck e notebook | verificação do preparo por Peer Instruction, blocos de até 15 minutos alternando demonstração com widget, prática em dupla e discussão com dado real, cronômetro visível nas atividades |
| Depois (pós-aula) | material de apoio, notebook e slide de amarração | avanço do artefato da sprint, desafio do notebook e leitura complementar |

Técnicas de metodologia ativa adotadas, cada uma com o componente do deck que a sustenta:

| Técnica | Uso no encontro | Componente |
|---|---|---|
| Peer Instruction (votar, discutir em dupla, votar de novo) | abertura, sobre o conteúdo pré-aula | `inteli-quiz.js` |
| Prever, observar, explicar | antes de mover um widget ou tocar uma animação, a turma registra a previsão | widgets de `assets/js/widgets/` e `<video>` |
| Pensar, discutir em dupla, compartilhar | leitura de gráfico real e decisão de negócio | `inteli-cronometro.js` |
| Programação em dupla (condutor e navegador) | prática no notebook | slide `exercise-slide` com `inteli-cronometro.js` |
| Classificação coletiva | vários itens julgados pela sala num mesmo slide | `inteli-escolha.js` |

A regra dos 15 minutos da `inteli-course-design` continua valendo sem exceção: todo bloco do
roteiro fecha em uma interação nomeada antes de abrir o seguinte, e isso está travado em
`tools/tests/test_planejamento.py`.

## Carga de cada tempo

O encontro segue em 2 horas, com 15 minutos de daily e 105 minutos em sete blocos, e a decisão não
acrescenta minuto ao encontro. O pré-aula usa a carga que a Adalove já reserva como autoestudo,
citada em `docs/autoestudos-por-semana.md`:

| Semana da instrução | Soma dos dois autoestudos | Observação |
|---|---|---|
| 1 | 105 min | 70 e 35 |
| 3 | 115 min | 70 e 45 |
| 5 | 200 min | 80 mais a Ponderada 1, de 120 |
| 6 | 135 min | 65 e 70 |
| 8 | 120 min | 50 e 70, proposta de 17/09/2026 a lançar |
| 9 | 210 min | 90 mais a Ponderada 2, de 120, proposta de 17/09/2026 a lançar |

O que a sala invertida acrescenta ao pré-aula fica dentro dessa carga: cada animação tem no máximo
60 segundos pelo contrato de vídeo (ADR-005) e a autoverificação tem cinco perguntas sem nota.

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| A turma chega sem fazer o pré-aula, e o encontro perde a base que ele pressupõe | a Peer Instruction de abertura mede isso nos primeiros minutos; o material de apoio traz a seção "Preparação" com as animações, que cobrem o conceito central em até três minutos de vídeo somados, por causa do teto de 60 segundos por clipe |
| A carga real dos autoestudos depende da Adalove, ainda não lida (P1 do `PLANO_DE_ENSINO.md`), e os das semanas 8 e 9 são proposta a lançar | os tempos acima estão citados com a origem, e a tabela de `docs/autoestudos-por-semana.md` marca cada item como REVISAO de junho ou proposta de 17/09/2026 |
| Duas semanas somam mais de três horas de pré-aula porque a ponderada da sprint entra como card de autoestudo | cada ponderada vale 3 pontos, tem 120 minutos reservados na tabela e é entrega avaliada; descontada ela, o preparo de leitura das semanas 5 e 9 fica em 80 e 90 minutos |
| A prática em dupla estoura o bloco de 15 minutos e come o bloco seguinte | o cronômetro fica visível no slide de exercício, com o tempo declarado no roteiro do `PLANEJAMENTO_AULA_A_AULA.md` |
| Animação assistida em casa não garante compreensão | a técnica de prever, observar e explicar é aplicada de novo no encontro, com o widget do mesmo conceito, e o professor vê a previsão da turma antes de mostrar o resultado |

## Consequências

**Positivas**

- Os 105 minutos ficam com o que precisa do professor na sala, o que é a mitigação estrutural da
  densidade da semana 8 registrada na ADR-002.
- Cada aula tem um lugar definido para a mídia gerada por código, sem disputar tempo de encontro.
- O preparo passa a ser medido, com dado imediato para o professor decidir onde acelerar.
- O roteiro das seis aulas fica verificável: os sete blocos e as interações nomeadas estão
  travados em `tools/tests/test_planejamento.py`.

**Negativas**

- O acervo passa a depender do lançamento correto dos autoestudos na Adalove, que é um passo fora
  deste repositório.
- Cada aula precisa produzir material de preparação além dos quatro artefatos, o que aumenta o
  custo de construção.
- A qualidade do encontro fica sensível ao preparo da turma, e a mitigação disponível é diagnóstica
  na abertura.

## ADRs relacionadas

- ADR-002, cuja densidade da semana 8 esta decisão mitiga.
- ADR-005, que produz as animações do pré-aula e os widgets do encontro.
- ADR-001, que trouxe o cronômetro e a escolha usados por três das cinco técnicas.
