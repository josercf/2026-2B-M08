# Plano de Ensino: Computação no Módulo 08 AdmTech, Imersão no mercado financeiro

Este documento e o `PLANEJAMENTO_AULA_A_AULA.md` são a fonte da verdade do acervo. Nenhum deck,
página de referências, material de apoio, notebook ou card do portal inventa data, título, escopo
ou peso de entrega: tudo desce destes dois arquivos, que por sua vez descem do
`REVISAO-LBL08-COMPUTACAO.md` (16/06/2026), das decisões registradas em 17/09/2026 e dos dados
versionados em `dados/`.

Datas, semanas, títulos e pesos foram conferidos em 13/10/2026 contra o export da Adalove da
turma 2026-2B-T19 (23 alunos em quatro grupos, G01 a G04, orientador Rafael Donaire). A planilha
fica fora do git, porque traz nomes de alunos. O export não traz horário de relógio, que segue a
confirmar. As lacunas restantes estão na seção 8.

## 1. Identificação

| Campo | Valor |
|---|---|
| Módulo | LBL 08 AdmTech, Imersão no mercado financeiro |
| Turma | 2026-2B-T19 |
| Professor de Computação | Prof. José Romualdo |
| Início | 14/10/2026 |
| Duração | 10 semanas, 5 sprints, 6 Encontros de Instrução de Computação |
| Parceiro do case | BTG Pactual, segundo as anotações dos checkpoints de 14/05, 29/06 e 19/08/2026; premissas a confirmar no LBL |

## 2. O case

O projeto do módulo é uma ferramenta de simulação de carteira eficiente para um parceiro que
precisa decidir onde alocar excedentes de caixa. A ferramenta calcula a Fronteira Eficiente de
Markowitz e apresenta o resultado a quem decide.

Premissas registradas no `REVISAO-LBL08-COMPUTACAO.md`:

1. A análise se sustenta em dados públicos e verificáveis, coletados pelo próprio grupo, com as
   decisões de tratamento documentadas.
2. A base é o histórico de preços dos ativos candidatos, convertido em retornos diários antes de
   qualquer conversa de alocação.
3. Selic, IPCA e CDI entram como referência: o CDI como taxa livre de risco no Índice de Sharpe, a
   Selic como ciclo que explica correlações do período e o IPCA como régua de retorno real.
4. Os gestores do parceiro definem a tolerância a risco, e o otimizador devolve a carteira ótima
   para o nível escolhido.

O arco das cinco sprints leva do dado bruto à decisão assistida: coleta (A1), risco e retorno por
ativo (A2), simulação de Monte Carlo (A3), otimização com a fronteira eficiente (A4) e o
simulador em React com API Python e interpretação por LLM (A5).

## 3. Dados

A pasta `dados/` guarda o snapshot do case, coletado em 17/09/2026, cobrindo 02/01/2019 a
31/08/2026. Decks, materiais, notebooks e testes leem os números apenas desses arquivos. O
contrato de cada arquivo, a cesta de 15 ativos da B3, os links conferidos das séries do Banco
Central e o procedimento de regeneração estão em `dados/README.md`.

**Três visões de preço.** O `Close` de `precos_fechamento.csv` já vem dividido pelos fatores de
desdobramento, grupamento e bonificação, por isso nenhum evento corporativo aparece como salto
nessa série. O `Adj Close` de `precos_ajustados.csv` desconta também os proventos pagos depois de
cada data: no primeiro pregão da janela, o Adj Close da PETR4 vale 26,13% do Close. O preço como
foi negociado na época não está versionado e é reconstruído em aula, multiplicando o Close pelos
fatores posteriores de `eventos_desdobramento.csv`; é nessa terceira visão que o grupamento da
MGLU3 (fator 0,1 em 27/05/2024) e o desdobramento da B3SA3 (fator 3 em 17/05/2021) aparecem como
saltos.

**Falhas reais do provedor.** BOVA11, IVVB11 e GOLD11 ficam sem cotação em 24/10/2025, pregão
normal da B3. GOLD11 acumula 485 pregões sem cotação na janela, dos quais 484 são anteriores à
primeira cotação do fundo, em 11/12/2020. Descartar as datas com ausência mantém 1.423 dos 1.908
pregões e tira março de 2020 da cesta inteira, o que derruba a volatilidade anual da PETR4 de
39,25% para 33,41%. Essas ausências são conteúdo da Aula 01 e o primeiro ADR pedido aos grupos.

## 4. Cronograma das seis instruções de Computação

Datas e semanas da Adalove da turma 2026-2B-T19. Horário de relógio a confirmar (o export não
traz). A coluna Aula do módulo é a numeração da aba "Organização de Aula" da planilha, citada do
`REVISAO-LBL08-COMPUTACAO.md`.

| Acervo | Data | Semana | Aula do módulo | Sprint | Instrução | Entrega que a aula alimenta (peso da Adalove) |
|---|---|---|---|---|---|---|
| aula01 | 20/10/2026 (terça) | 2 | 5 | 1 | Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível | A1 Coletor e Processador de Dados de Mercado (3) |
| aula02 | 05/11/2026 (quinta) | 4 | 13 | 2 | Dados Financeiros: Do Preço ao Retorno | A2 Módulo de Análise de Risco e Retorno Individual (3) |
| aula03 | 10/11/2026 (terça) | 5 | 22 | 3 | Correlação, Covariância e o Argumento Matemático da Diversificação | A3 Motor de Simulação de Monte Carlo (3) e Ponderada 1 (3) |
| aula04 | 18/11/2026 (quarta) | 6 | 28 | 3 | Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz | A3 (3) e A4 Otimizador de Carteira com Fronteira Eficiente (3) |
| aula05 | 01/12/2026 (terça) | 8 | 38 | 4 | Validação e Robustez do Modelo | A4 Otimizador de Carteira com Fronteira Eficiente (3) e Ponderada 2 (3) |
| aula06 | 16/12/2026 (quarta) | 10 | 43 | 5 | Do Script ao Produto: React, FastAPI e Interpretação com LLM | A5 Simulador Interativo integrado à interface e Interpretação por LLM (2) |

Sprints, plannings e reviews na Adalove: Sprint 1 de 14/10 a 23/10 (review em 23/10, sexta);
Sprint 2 com planning em 26/10 e review em 06/11 (sexta); Sprint 3 com planning em 09/11 e review
em 19/11 (quinta, véspera do feriado de 20/11); Sprint 4 com planning em 23/11 e review em 04/12
(sexta); Sprint 5 com planning em 07/12 e review em 18/12 (sexta). A prova do módulo é em
11/12/2026, com peso 20.

A ordem das instruções 5 e 6 segue o `REVISAO-LBL08-COMPUTACAO.md` revisado em 13/10/2026, que
substitui a troca decidida em 17/09/2026 (ADR-007), e é a mesma da Adalove.

## 5. Entregas avaliadas e pesos

Pesos citados da Adalove da turma 2026-2B-T19. Cada barema soma 100%, com 65% na ferramenta, 15% em
Especificação e documentação (nota de grupo) e 20% nos ADRs (nota individual), conforme o
`REVISAO-LBL08-COMPUTACAO.md`.

| Entrega | Sprint | Título na Adalove | Peso | Observação |
|---|---|---|---|---|
| A1 | 1 | Coletor e Processador de Dados de Mercado | 3 | review em 23/10/2026 |
| A2 | 2 | Módulo de Análise de Risco e Retorno Individual | 3 | review em 06/11/2026 |
| A3 | 3 | Motor de Simulação de Monte Carlo | 3 | review em 19/11/2026 (quinta); entrega mantida na sexta 20/11/2026, 23h59, por decisão do professor em 13/10/2026 |
| A4 | 3 e 4 | Otimizador de Carteira com Fronteira Eficiente | 3 | a Adalove lista o mesmo título, com peso 3, nas Sprints 3 e 4: confirmar com a coordenação se são duas entregas |
| A5 | 5 | Simulador Interativo integrado à interface e Interpretação por LLM | 2 | review em 18/12/2026; o REVISAO de 13/10 chama de "Simulador Interativo em React com API Python e Interpretação por LLM" |
| Ponderada 1 | 3 | Atividade Ponderada 1: Diagnóstico de uma carteira herdada | 3 | autoestudo da semana 5 |
| Ponderada 2 | 4 | Atividade Ponderada 2: A carteira ótima sobrevive fora da amostra? | 3 | autoestudo da semana 8 |

Prazos combinados pelo professor em 13/10/2026: autoestudo feito em sala até o fim da instrução;
autoestudo para casa e artefato até sexta, 23h59. A nota de participação é concedida pelo
professor a contribuições relevantes, aderentes ao módulo e ao problema do parceiro.

O A4 entrega o otimizador em módulo Python e o A5 entrega a aplicação em duas camadas, com FastAPI no
backend e React no frontend. O Streamlit saiu do módulo. A decisão está na ADR-007, que substitui a
ADR-002.

## 6. A espiral: o que cada aula deixa pronto para a próxima

Toda aula abre resgatando, em uma frase, o que a anterior deixou pronto. O resgate vira a pergunta
de abertura do primeiro bloco.

| Aula | O que a aula deixa pronto para a seguinte |
|---|---|
| 01 | coletor parametrizado por tickers e datas, com preço ajustado e ausências tratadas e documentadas |
| 02 | retornos diários, métricas anualizadas por 252 e a comparação de risco entre os ativos da cesta |
| 03 | matriz de covariância anualizada e a curva de risco de dois ativos em função da correlação |
| 04 | nuvem de 10.000 carteiras, carteiras de variância mínima e de máximo Sharpe e a fronteira de 50 pontos |
| 05 | teste fora da amostra das duas carteiras ótimas, estabilidade dos pesos entre janelas e drawdown |
| 06 | fecho do módulo: a ferramenta em React sobre a API FastAPI, com interpretação por LLM conferida contra os números |

## 7. Sala de aula invertida em três tempos

Cada aula é desenhada em três tempos. O encontro pressupõe o primeiro tempo feito e começa medindo
se ele foi feito.

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

A regra dos 15 minutos da skill `inteli-course-design` vale sem exceção: todo bloco do roteiro
fecha com interação direta dos alunos.

## 8. Pendências abertas

P1 e P2 vêm da leitura da Adalove em 13/10/2026; P3 e P4 são fontes ainda não lidas. De P5 a P7, as pendências de
conteúdo levantadas em 17/09/2026, que dependem da coordenação e não foram alteradas
unilateralmente neste acervo. O texto da coluna Pendência é o mesmo em
`docs/revisao-planilha-2026-09-17.md`, seção 8, para as quatro que a coordenação precisa responder
(P4 a P7).

| # | Pendência | Efeito no acervo | Como fecha |
|---|---|---|---|
| P1 | Horário de relógio das instruções: o export da Adalove lido em 13/10/2026 traz datas, semanas, autoestudos e pesos, sem horário | o roteiro usa blocos relativos, sem hora de relógio | ler o horário na Adalove ou no calendário da turma |
| P2 | A Adalove lista "Otimizador de Carteira com Fronteira Eficiente" com peso 3 nas Sprints 3 e 4 | o acervo trata o A4 como entrega das Sprints 3 e 4 até a coordenação esclarecer | confirmar com a coordenação se é uma entrega em duas etapas ou duplicidade |
| P3 | Planilha de alocação de professores, coluna de ADM, não lida | o dia da semana de cada instrução do professor é desconhecido, o que também define a folga real do A4 | ler a coluna de ADM e registrar os dias |
| P4 | O parceiro tem nome e premissas descritos no LBL da Adalove, o projeto não tem TAPI, e o LBL não foi lido | nome, setor e premissas ficam sem citação direta, e a cesta de 15 ativos da B3 documentada em `dados/README.md` é a referência das aulas até lá | ler o LBL, registrar as premissas com a fonte e trocar a cesta pelos ativos do parceiro, se as premissas pedirem |
| P5 | O A2 (Sprint 2, semana 4) cobra matriz de correlação e de covariância, que a Instrução 3 só ensina na semana 5 | a Aula 02 avisa a turma em voz alta e o material de apoio antecipa o mínimo necessário | decidir com a coordenação entre mover o item do A2 ou antecipar o conteúdo |
| P6 | O A4 vence na mesma semana da instrução que ensina a parte web | a folga real depende do dia da aula dentro da semana 8, ainda não lido (P3) | confirmar o dia e, se necessário, negociar a data de entrega |
| P7 | O case de créditos OpenRouter (02/09/2026) ainda cita Streamlit e a Instrução 6 antiga | o documento aprovado descreve um produto que o módulo não vai mais construir | atualizar o case com FastAPI e a Instrução 6 nova antes da Sprint 5 |
