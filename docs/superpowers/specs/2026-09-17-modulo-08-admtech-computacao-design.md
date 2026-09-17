# Design: acervo de Computação do Módulo 08 AdmTech (2026-2B)

**Data:** 17/09/2026
**Status:** Aprovado para construção em 17/09/2026
**Autor:** Prof. José Romualdo
**Módulo:** LBL 08 AdmTech, "Imersão no mercado financeiro", turma 2026-2B
**Repositório:** `git@github.com:josercf/2026-2B-M08.git`
**Portal:** <https://josercf.github.io/2026-2B-M08/>

---

## 1. Contexto

O Módulo 08 de AdmTech tem 10 semanas, 5 sprints e começa em 14/10/2026. O projeto do módulo é
uma ferramenta de simulação de carteira eficiente para um parceiro que precisa decidir onde
alocar excedentes de caixa. A parte de Computação tem **6 Encontros de Instrução**, nas semanas 1,
3, 5, 6, 8 e 9, **5 artefatos COM**, um por sprint, e **2 atividades ponderadas** de 3 pontos
cada.

A trilha foi revisada em junho de 2026 no documento `REVISAO-LBL08-COMPUTACAO.md` (16/06/2026),
que vive fora deste repositório, na pasta de trabalho do módulo. Em 17/09/2026 o professor decidiu
cinco mudanças, que este design incorpora:

1. **A parte web sobe para a Sprint 4.** O artefato A4 (semana 8) passa a ser o otimizador de
   Markowitz entregue dentro de uma aplicação web. O artefato A5 (semana 10) fica só com a
   interpretação da carteira por LLM.
2. **A aplicação web usa FastAPI e uma página HTML/JS.** O Streamlit sai do módulo.
3. **As instruções das semanas 8 e 9 trocam de conteúdo.** A semana 8 passa a ensinar a parte web.
   Validação e robustez do modelo descem para a semana 9, junto com a interpretação por LLM, e a
   Ponderada 2 acompanha esse conteúdo para a semana 9.
4. **As aulas seguem sala de aula invertida explícita**, com uso intenso de imagem, animação e
   notebooks prontos para o Colab.
5. **A mídia é produzida por código**: animações renderizadas sobre os dados reais e widgets
   interativos dentro do deck. Vídeo de terceiros não é embutido no deck.

## 2. Objetivos

1. Produzir o acervo das 6 instruções de Computação, com os quatro artefatos públicos por aula
   (deck, material de apoio, referências, notebook) e as notas do professor.
2. Estruturar cada aula em três tempos de sala invertida: antes, durante e depois do encontro.
3. Dar a cada aula ao menos duas animações geradas por código e ao menos um widget interativo no
   deck, todos alimentados pelos dados reais versionados em `dados/`.
4. Entregar notebooks que abrem no Colab pelo badge e executam do início ao fim sem edição.
5. Entregar o texto revisado dos artefatos A4 e A5, dos títulos e descrições das instruções 5 e 6
   e dos autoestudos das semanas 8 e 9, pronto para lançar na planilha e na Adalove.
6. Manter o acervo verificável por automação: marca, layout, links, mídia, dados e notebooks.

## 3. Não-objetivos

- Não construir o projeto dos grupos. O exemplo de API da Aula 05 é propositalmente parcial: expõe
  métricas de uma carteira com pesos dados e não contém o otimizador nem a fronteira, que são o
  núcleo avaliado do A4.
- Não versionar enunciado completo, tabela de carteiras por RA nem barema das ponderadas. Eles
  vivem na Adalove; o acervo cita as ponderadas por título e pontuação.
- Não produzir material de Negócios, Matemática, UX ou Liderança.
- Não alterar a planilha nem a Adalove. O repositório entrega o texto revisado; lançar é um passo
  separado, feito pelo professor ou com autorização explícita.

## 4. Fontes da verdade e pendências abertas

| Fonte | Papel | Estado em 17/09/2026 |
|---|---|---|
| Adalove, LBL 08 AdmTech 2026-2B | datas, horários, autoestudos, pesos oficiais | não lida |
| Planilha "Revisão LBL 8 AdmTech - 2026-2B" (Google Sheets, privada) | organização das aulas (aba gid 3721376), artefatos, instruções | não lida: HTTP 401 sem sessão |
| Planilha de alocação de professores, coluna de ADM | dias das instruções do professor | não lida |
| `REVISAO-LBL08-COMPUTACAO.md` (16/06/2026) | instruções, autoestudos, artefatos, ponderadas | lida, base provisória |
| `Case-Creditos-OpenRouter-M08-AdmTech.docx` (02/09/2026) | créditos de LLM para a Sprint 5 | lido |
| Decisões de 17/09/2026 | reorganização de A4, A5 e das instruções 5 e 6 | ADR-002 |

Regra herdada da skill `inteli-course-design`: nenhum artefato inventa data, horário, título,
autoestudo ou peso. Enquanto a Adalove e as planilhas não forem lidas:

- **Datas e horários** ficam como pendência explícita nos documentos de planejamento, no portal e
  nos decks. O roteiro usa a estrutura padrão de 2h (autoestudo, daily de 15 minutos, 105 minutos
  em sete blocos) com blocos relativos, sem hora de relógio.
- **Pesos dos artefatos** são citados do REVISAO, que os leu da planilha em junho: A1 3, A2 sem
  peso na planilha, A3 2, A4 2, A5 1, Ponderadas 1 e 2 com 3 cada. Todos marcados "a confirmar na
  Adalove".
- **Autoestudos** das semanas 1, 3, 5 e 6 vêm do REVISAO. Os das semanas 8 e 9 são proposta nova
  (seção 10) e ficam marcados "a lançar".

Pendências de conteúdo registradas para a coordenação, sem mudança unilateral neste acervo:

1. O A2 (Sprint 2, semana 4) cobra matriz de correlação e de covariância, que a Instrução 3 só
   ensina na semana 5.
2. O A4 vence na mesma semana da instrução que ensina a parte web. A folga real depende do dia da
   aula dentro da semana 8, que ainda não foi lido.
3. O case de créditos OpenRouter ainda cita Streamlit na Instrução 6.
4. O parceiro do projeto tem nome e premissas descritos no LBL da Adalove, sem TAPI. A cesta de
   ativos da seção 8 é a referência das aulas até essas premissas serem lidas.

## 5. Mapa das instruções, sprints e entregas

Numeração do acervo: `aula01` a `aula06` são as instruções 1 a 6 de Computação, na ordem em que
acontecem. A planilha numera as aulas do módulo inteiro (5, 13, 22, 28, 38 e 43 na aba
"Organização de Aula"); o portal mostra os dois números para não haver ambiguidade (ADR-006).

| Acervo | Semana | Sprint | Instrução | Entrega que a aula alimenta |
|---|---|---|---|---|
| aula01 | 1 | 1 | Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível | A1 Coletor e Processador de Dados de Mercado (3) |
| aula02 | 3 | 2 | Dados Financeiros: Do Preço ao Retorno | A2 Módulo de Análise de Risco e Retorno Individual (sem peso) |
| aula03 | 5 | 3 | Correlação, Covariância e o Argumento Matemático da Diversificação | A3 Motor de Simulação de Monte Carlo (2) e Ponderada 1 (3) |
| aula04 | 6 | 3 | Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz | A3 (2) e a base matemática do A4 |
| aula05 | 8 | 4 | Do Script ao Produto: API em FastAPI e Página Web (título novo) | A4 Otimizador de Carteira com Fronteira Eficiente em Aplicação Web (2) |
| aula06 | 9 | 5 | Validação, Robustez e Interpretação com LLM (título novo) | A5 Interpretação da Carteira por LLM (1) e Ponderada 2 (3) |

A espiral do módulo, que cada aula resgata na abertura:

| Aula | O que a aula deixa pronto para a seguinte |
|---|---|
| 01 | coletor parametrizado por tickers e datas, com preço ajustado e ausências tratadas e documentadas |
| 02 | retornos diários, métricas anualizadas por 252 e a comparação de risco entre os ativos da cesta |
| 03 | matriz de covariância anualizada e a curva de risco de dois ativos em função da correlação |
| 04 | nuvem de 10.000 carteiras, carteiras de variância mínima e de máximo Sharpe e a fronteira de 50 pontos |
| 05 | API FastAPI que devolve métricas de carteira em JSON e página que desenha o resultado |
| 06 | fecho do módulo: teste fora da amostra e interpretação verificada por LLM |

## 6. Sala de aula invertida em três tempos

Cada aula é desenhada em três tempos. O encontro pressupõe o primeiro tempo feito e começa
medindo se ele foi feito.

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

A regra dos 15 minutos da `inteli-course-design` continua valendo sem exceção: todo bloco fecha
com interação direta dos alunos.

## 7. Mídia: animações geradas por código e widgets no deck

### 7.1 Animações

- **Ferramenta:** `matplotlib.animation.FuncAnimation` com escrita por ffmpeg. Codec H.264,
  `yuv420p`, 1280x720, 30 quadros por segundo, sem áudio, no máximo 60 segundos e 3 MB por clipe.
- **Scripts:** `tools/animacoes_aulaNN.py`, um por aula, lendo só `dados/`. As cores vêm dos
  tokens de `assets/css/inteli-brand.css`, lidos por `tools/paleta.py`, nunca de hex literal.
- **Saída:** `assets/video/aulaNN-<assunto>.mp4` e o pôster `assets/img/aulaNN-<assunto>-poster.png`
  (primeiro quadro significativo).
- **Uso:** `<video controls muted playsinline preload="metadata" poster="...">` no deck e na seção
  "Preparação" do material de apoio. O vídeo toca sem rede.
- **Verificação:** `tools/tests/test_midia.py` confere, por ffprobe, codec, resolução, duração e
  tamanho de todo vídeo em `assets/video/`, que todo vídeo referenciado existe e que nenhum vídeo
  fica órfão. Um diretório de vídeo vazio com decks que referenciam vídeo reprova (nada medido
  nunca lê como sucesso).

### 7.2 Widgets

- **Tecnologia:** JavaScript puro, sem biblioteca, desenhando em `<canvas>` ou SVG. Cores lidas em
  tempo de execução das custom properties do tema (`getComputedStyle`), para o `check_brand.py`
  continuar valendo.
- **Dados:** JSON pré-calculado em `assets/data/aulaNN-<assunto>.json` por
  `tools/dados_widgets_aulaNN.py`, a partir de `dados/`. Nenhum número de widget é digitado à mão.
- **Contrato de markup:** `<div class="widget" data-widget="<nome>" data-fonte="../assets/data/..."></div>`,
  com o script em `assets/js/widgets/<nome>.js`. Ao terminar de montar, o widget grava
  `data-pronto="sim"` no próprio elemento.
- **Verificação:** `tools/check_widgets.py` abre cada deck no Chromium do Playwright, conta os
  widgets declarados, exige `data-pronto="sim"` em todos e zero erro de console. Deck com widget
  declarado e zero widget medido reprova.
- **Reveal.js:** fragments e `data-auto-animate` são permitidos. O `revisor-slides` revela todos e
  confere o layout pós-interação, porque `check_slides.py` é cego a esse estado.

## 8. Dados do case

| Arquivo | Conteúdo | Fonte |
|---|---|---|
| `dados/precos_ajustados.csv` | fechamento ajustado por proventos e desdobramentos, 15 ativos | Yahoo Finance via yfinance 1.7.0 |
| `dados/precos_brutos.csv` | fechamento sem ajuste, os mesmos 15 ativos | Yahoo Finance via yfinance 1.7.0 |
| `dados/cdi_diario.csv` | CDI, taxa diária em % | BCB SGS, série 12 |
| `dados/selic_meta.csv` | meta da Selic, % a.a. | BCB SGS, série 432 |
| `dados/ipca_mensal.csv` | IPCA, variação mensal em % | BCB SGS, série 433 |
| `dados/ptax_venda.csv` | dólar PTAX, venda | BCB SGS, série 1 |

- **Janela:** 02/01/2019 a 31/08/2026, coletada em 17/09/2026. Cobre o choque de março de 2020, o
  ciclo de alta da Selic de 2021 a 2023 e o período mais recente, que as ponderadas pedem para
  contextualizar.
- **Cesta de referência das aulas (15 ativos):** PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3, WEGE3,
  EGIE3, SUZB3, RENT3, B3SA3, MGLU3, BOVA11, IVVB11 e GOLD11. Tem pares do mesmo setor (bancos),
  exportadoras sensíveis ao câmbio, ETFs de índice, de S&P 500 em reais e de ouro, e um ativo com
  histórico mais curto (GOLD11, 1.423 pregões contra 1.908 dos demais), que vira conteúdo de
  tratamento de ausências na Aula 01.
- **Contrato:** primeira coluna `data` (AAAA-MM-DD), uma coluna por ticker sem o sufixo `.SA`;
  séries do BCB com `data` e `valor`. Documentado em `dados/README.md`, regenerado por
  `tools/baixar_dados.py` e travado por `tools/tests/test_dados.py`.
- **Notebooks:** carregam `../dados/` quando existe e caem para a URL bruta do repositório no
  Colab. A coleta ao vivo pelo yfinance aparece nas Aulas 01 e 02 com tempo limite e queda para o
  snapshot; a variável `M08_OFFLINE=1` desliga a rede no CI.
- **Risco conhecido:** os termos do Yahoo restringem redistribuição. O snapshot é educacional,
  pequeno e atribuído; a troca pelas séries históricas da B3 (COTAHIST) fica registrada como
  mitigação na ADR-003.

## 9. Escopo de cada aula

Cada linha abaixo é o escopo mínimo. O roteiro minuto a minuto vive em
`PLANEJAMENTO_AULA_A_AULA.md`, que é escrito a partir desta seção.

### Aula 01: Aquisição de Dados de Mercado (semana 1, Sprint 1)

- **Pergunta do case:** os dados que vão sustentar a recomendação ao parceiro são confiáveis?
- **Conteúdo:** coletor parametrizado com yfinance; preço bruto e preço ajustado; desdobramento e
  grupamento aparecendo como falso colapso no preço bruto; ausências e calendário de pregões;
  reprodutibilidade (snapshot, requirements, execução do zero); SPEC.md e ADR como disciplina de
  projeto.
- **Animações:** o falso colapso do preço bruto no evento corporativo; o mapa de ausências se
  formando conforme os ativos entram na coleta.
- **Widgets:** alternância entre preço bruto e ajustado com zoom no evento; escolha entre descartar
  datas e preencher para a frente, mostrando pregões perdidos e o desvio padrão resultante.
- **Autoestudos (REVISAO):** "Coleta de dados financeiros e DataFrames com Pandas"; "Cotações do
  Yahoo Finance no Colab, do jeito reaproveitável".

### Aula 02: Do Preço ao Retorno (semana 3, Sprint 2)

- **Pergunta do case:** qual ativo da cesta oscila mais, e quanto isso custa ao parceiro?
- **Conteúdo:** retorno simples e logarítmico; `pct_change`; média, variância e desvio padrão;
  anualização por 252 e por raiz de 252; histograma e caudas; o CDI como referência de retorno sem
  risco.
- **Animações:** histograma de retornos diários se formando dia a dia, com março de 2020 surgindo
  nas caudas; a dispersão crescendo com raiz do tempo.
- **Widgets:** volatilidade anualizada em janela deslizante de 21, 63 ou 252 pregões; retorno
  simples contra logarítmico em quedas grandes.
- **Autoestudos (REVISAO):** "Risco e retorno: passado e prólogo"; "Análise de uma ação em Python na
  prática".

### Aula 03: Correlação e Diversificação (semana 5, Sprint 3)

- **Pergunta do case:** a carteira do parceiro diversifica de verdade ou repete o mesmo risco?
- **Conteúdo:** covariância e correlação; matriz e heatmap; correlação móvel e sua mudança em
  crise; risco de dois ativos em função do peso e da correlação; covariância anualizada;
  introdução ao encolhimento de Ledoit-Wolf.
- **Animações:** a curva risco-retorno de dois ativos se curvando enquanto a correlação cai de +1
  a -1; a correlação móvel de ITUB4 com BBDC4 contra a de PETR4 com IVVB11.
- **Widgets:** controle de correlação e peso sobre o desvio padrão real de dois ativos, com a
  correlação medida marcada; heatmap com leitura do par ao passar o cursor.
- **Autoestudos (REVISAO):** "Diversificação eficiente: a matemática de não colocar todos os ovos
  na mesma cesta"; "Atividade Ponderada 1: Diagnóstico de uma carteira herdada" (3 pontos).

### Aula 04: Monte Carlo e Markowitz (semana 6, Sprint 3)

- **Pergunta do case:** entre todas as alocações possíveis, qual o parceiro deveria considerar?
- **Conteúdo:** pesos, retorno e variância em forma vetorial; Índice de Sharpe com o CDI; 10.000
  carteiras vetorizadas em NumPy; `scipy.optimize.minimize` com SLSQP; variância mínima, máximo
  Sharpe e fronteira de 50 pontos; a melhor carteira sorteada contra a ótima.
- **Animações:** a nuvem de Monte Carlo acumulando pontos; a fronteira traçada sobre a nuvem; o
  SLSQP caminhando até o ótimo no triângulo de pesos de três ativos.
- **Widgets:** sorteio progressivo de carteiras com a melhor sorteada contra a ótima; triângulo de
  pesos de três ativos que move o ponto no plano risco-retorno.
- **Autoestudos (REVISAO):** "Carteiras e simulação de Monte Carlo com Python"; "Da nuvem à
  fronteira eficiente de Markowitz".

### Aula 05: API em FastAPI e Página Web (semana 8, Sprint 4)

- **Pergunta do case:** como um gestor do parceiro, que não programa, opera o otimizador?
- **Conteúdo:** cliente e servidor; HTTP (GET, parâmetros de consulta, códigos de status); JSON;
  FastAPI (rotas, tipos, validação, documentação automática em `/docs`); a API importa os módulos
  dos artefatos anteriores sem copiar código; página HTML com `fetch` e Plotly.js; erros de entrada
  (ticker inválido, pesos que não somam 1); cache; segredo nunca no JavaScript do navegador, que
  prepara a Aula 06.
- **Animações:** a requisição saindo do navegador, passando pela API e pelo cálculo e voltando como
  JSON até o gráfico; o tempo de resposta com e sem cache.
- **Widgets:** montador de URL que dispara `fetch` de verdade contra um JSON estático do acervo e
  mostra requisição e resposta; inspetor do JSON devolvido.
- **Notebook:** API definida no próprio notebook e testada com `TestClient`, sem servidor; servidor
  opcional com uvicorn e o proxy de porta do Colab.
- **Exemplo:** `exemplos/api-carteira/`, API mínima com um endpoint de métricas para pesos dados e
  a página que desenha o ponto, sem otimizador.
- **Autoestudos (propostos, a lançar):** seção 10.

### Aula 06: Validação, Robustez e LLM (semana 9, Sprint 5)

- **Pergunta do case:** quanto o parceiro pode confiar na carteira recomendada, e como explicar isso
  em português sem inventar número?
- **Conteúdo, parte 1:** o otimizador converge para o passado; divisão temporal treino e teste;
  backtest fora da amostra; drawdown; instabilidade dos pesos entre janelas.
- **Conteúdo, parte 2:** o LLM como componente do produto; OpenRouter com API compatível com a da
  OpenAI; chave no backend, em variável de ambiente e fora do git; prompt com os números reais como
  contexto; resposta estruturada; verificação automática de todo número citado pelo modelo; custo
  por token e escolha de modelo; limitações declaradas no texto.
- **Animações:** a janela de treino deslizando e os pesos ótimos mudando; a curva de drawdown se
  formando no período de teste.
- **Widgets:** controle da janela de treino com os pesos ótimos pré-calculados e o retorno realizado
  fora da amostra; verificador de números sobre um texto de interpretação com erros plantados e
  declarados como exercício.
- **Notebook:** backtest, estabilidade dos pesos, montagem do prompt, chamada opcional à OpenRouter
  (pulada sem chave) e o verificador de números.
- **Autoestudos (propostos, a lançar):** seção 10, com a Ponderada 2 (3 pontos) movida para esta
  semana.

## 10. Revisão para a planilha e a Adalove

Arquivo `docs/revisao-planilha-2026-09-17.md`, no formato do REVISAO de junho, com:

1. Título e descrição novos das instruções 5 (semana 8) e 6 (semana 9).
2. Os dois autoestudos da semana 8, curados para FastAPI, HTTP e `fetch`, com links abertos e
   conferidos (documentação do FastAPI em português e MDN em português).
3. Os dois autoestudos da semana 9: o 5.1 de junho ("Os limites do otimizador") movido e ampliado
   com o capítulo de limitações de LLM, e a Ponderada 2 movida da semana 8.
4. Colunas E, F e G reescritas dos artefatos A4 e A5, no padrão "Business Diagnosis and Discovery"
   do REVISAO, mantendo SPEC.md, ADRs individuais e README como componentes do barema.

## 11. Arquitetura do repositório

```
2026-2B-M08/
├── index.html                      portal: cards por instrução, agrupados por sprint
├── README.md                       para o aluno
├── CLAUDE.md                       para quem edita o acervo
├── PLANO_DE_ENSINO.md              fonte da verdade: case, dados, cronograma, entregas, pendências
├── PLANEJAMENTO_AULA_A_AULA.md     fonte da verdade: roteiro em sete blocos das 6 instruções
├── aulas/aula01..06.html           decks Reveal.js (e _fixture-tema.html)
├── materiais/aula01..06.html       preparação pré-aula e aprofundamento, com TOC lateral
├── referencias/aula01..06.html     autoestudos da semana e leitura complementar
├── notebooks/aula01..06.ipynb      laboratório executável, com badge do Colab
├── exemplos/api-carteira/          API mínima e página da Aula 05
├── dados/                          snapshot da B3 e séries do BCB, com README
├── assets/
│   ├── css/                        inteli-brand, theme, print, material, portal
│   ├── js/                         quiz, zoom, print, cronometro, escolha
│   ├── js/widgets/                 um arquivo por widget
│   ├── img/                        marca, grafismo, figuras e pôsteres
│   ├── video/                      animações MP4
│   └── data/                       JSON dos widgets
├── tools/
│   ├── check_brand.py, check_slides.py, check_links.py, check_widgets.py
│   ├── baixar_dados.py, paleta.py
│   ├── animacoes_aulaNN.py, dados_widgets_aulaNN.py, graficos_aulaNN.py
│   └── tests/
├── docs/
│   ├── ANDAMENTO.md
│   ├── autoestudos-por-semana.md
│   ├── revisao-planilha-2026-09-17.md
│   ├── notas-do-professor/aula01..06.md
│   ├── adrs/
│   └── superpowers/{specs,plans}/
├── .claude/{agents,settings.json}
└── .github/workflows/{validate.yml,static.yml}
```

## 12. Base reaproveitada

| Origem | O que vem | Adaptação |
|---|---|---|
| `canaldoovidio/2026-2A-M03` | tokens, tema, CSS de impressão, material e portal; `inteli-quiz.js`, `inteli-zoom.js`, `inteli-print.js`; marca e grafismo; `check_brand.py`, `check_slides.py`, `check_links.py` e seus testes; workflows; agentes; hook | URL do repositório no `check_links.py`, agentes reescritos para o M08, `requirements-ci.txt` do novo stack |
| `josercf/treinamento-gitlab` (Formação GitLab) | `inteli-cronometro.js`, `inteli-escolha.js` e os blocos de CSS de tema e de impressão que os estilizam | fundidos ao tema do M03, que tem as correções mais recentes |

O M03 é a base porque traz as correções de 04/09 e 08/09/2026 (título sobre a marca no PDF, lista
longa de referências) e a tradução do link do notebook no validador de links. A Formação GitLab
contribui só os componentes de metodologia ativa que o M03 não tem.

## 13. Agentes e automação

- **`construtor-aulas`**: constrói uma aula inteira. Além do que o agente do M03 faz, produz as
  animações, os widgets e a seção "Preparação" do material, e segue a seção 6 deste design.
- **`revisor-slides`**: revisa um deck. Além do escopo do M03, confere vídeo (pôster, controles,
  duração), widgets depois de interação, fragments revelados e a abertura por verificação do
  preparo.
- **Hook `PostToolUse`**: `check_slides.py` e `check_brand.py` ao editar `aulas/*.html`, igual ao
  M03.
- **`validate.yml`**: ffmpeg e Chromium instalados; `check_brand.py`, `check_links.py`,
  `check_slides.py`, `check_widgets.py`, pytest e execução dos notebooks com `M08_OFFLINE=1`; árvore
  de trabalho limpa ao final.
- **`static.yml`**: publicação no GitHub Pages a cada push em `main`.

## 14. ADRs da fundação

| ADR | Decisão |
|---|---|
| 001 | Base do acervo copiada do M03, com cronômetro e escolha da Formação GitLab |
| 002 | A4 com otimizador em aplicação FastAPI e HTML/JS, A5 só com LLM, troca das instruções 5 e 6 e Ponderada 2 na semana 9 |
| 003 | Dados do case: cesta de 15 ativos da B3 via yfinance e séries do BCB, versionados |
| 004 | Sala de aula invertida em três tempos |
| 005 | Animações em MP4 geradas por matplotlib e widgets em JavaScript puro |
| 006 | Numeração `aula01` a `aula06` para as instruções de Computação |

ADRs de escopo de cada aula são escritas pelo `construtor-aulas` quando a construção da aula exigir
uma decisão não trivial, como no M03.

## 15. Faseamento

| Fase | Escopo |
|---|---|
| 1. Fundação | base copiada e fundida, dados, documentos de planejamento, revisão para a planilha, portal, validadores novos com testes, agentes, CI, ADRs 001 a 006, repositório no GitHub |
| 2. Padrão-ouro | Aula 01 completa, com animações e widgets, revisada |
| 3. Aulas 02 a 06 | construídas em paralelo pelo `construtor-aulas`, uma por agente, cada uma seguida do `revisor-slides` |
| 4. Fechamento | espiral conferida entre aulas, CI verde, portal publicado, pendências de data aplicadas quando a Adalove for lida |

## 16. Riscos

| Risco | Mitigação |
|---|---|
| Datas e horários não lidos | pendência explícita e estrutura em blocos relativos; atualização concentrada quando a Adalove for lida |
| Yahoo bloquear ou mudar a API | snapshot versionado; notebooks caem para o snapshot |
| Vídeo pesado no git | teto de 3 MB por clipe e teste que reprova acima disso |
| Chromium do Playwright sem H.264 | nenhum validador depende de tocar o vídeo; a verificação usa ffprobe |
| FastAPI não expõe página no Colab sem proxy | notebook testa com `TestClient`; servidor pelo proxy de porta do Colab é opcional; exemplo local em VS Code |
| Notebook da Aula 06 sem chave de LLM no CI | chamada pulada sem `OPENROUTER_API_KEY`, prompt e verificador executam do mesmo jeito |
| Semana 8 densa: HTTP, FastAPI e HTML/JS em 105 minutos | pré-aula carrega HTTP e JSON; o encontro foca em integração; exemplo parcial pronto para estender |

## 17. Critérios de aceite

1. As 6 aulas têm deck, material, referências, notebook e notas do professor, e todos os links do
   portal resolvem.
2. `check_brand.py`, `check_links.py`, `check_slides.py`, `check_widgets.py`, a suíte pytest e a
   execução dos notebooks passam no CI.
3. Cada aula tem ao menos duas animações e um widget, todos alimentados por `dados/`.
4. Cada aula declara sprint, entrega, autoestudos e o estado de confirmação de data e peso.
5. Nenhum emoji, nenhum travessão, português com acentuação completa.
6. `docs/revisao-planilha-2026-09-17.md` pronto para lançar.
7. ADRs 001 a 006 escritas.
