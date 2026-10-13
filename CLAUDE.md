# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) a trabalhar neste repositório.

> **Retomando o trabalho?** `docs/ANDAMENTO.md` tem o estado atual: o que está pronto, o que está
> em andamento e as pendências abertas.

## 1. O que é este repositório

Acervo de Computação do **LBL 08 AdmTech, Imersão no mercado financeiro** (Graduação Inteli, turma
2026-2B, Prof. José Romualdo). São 6 Encontros de Instrução nas semanas 1, 3, 5, 6, 8 e 9, um
artefato COM por sprint e duas atividades ponderadas de 3 pontos.

O repositório é um site estático de decks Reveal.js, materiais de apoio, páginas de referências e
notebooks, feito para publicar no GitHub Pages. O repositório remoto `josercf/2026-2B-M08` está
no GitHub e publica em <https://josercf.github.io/2026-2B-M08/>. O que se edita é HTML, CSS,
JavaScript puro, Markdown, notebooks Jupyter e os scripts Python de `tools/`. Não existe build,
bundler nem gerenciador de pacote de JavaScript na raiz.

A única dependência de execução é Python. O ambiente local é o `.venv`, criado com
`--system-site-packages`: `.venv/bin/python` tem Playwright para os validadores, matplotlib para as
animações, pandas para os dados e yfinance para a coleta.

## 2. Comandos

```bash
# Preview local (obrigatório servir por HTTP: os decks usam caminhos relativos para assets/)
python3 -m http.server 8000                 # a partir da raiz do repositório
# http://localhost:8000/                          portal com as seis instruções; botões ficam desabilitados até o artefato existir
# http://localhost:8000/aulas/_fixture-tema.html   deck de referência de cada classe do tema

# Suíte de testes (validadores, dados, mídia, widgets e planejamento)
.venv/bin/python -m pytest tools/tests -v

# Fidelidade à marca: cor, segmento, font-family, emoji, canto reto (GRA-01), ícone Sharp (ICO-01), pesos (TIP-04)
.venv/bin/python tools/check_brand.py

# Todo href e src local do acervo resolve para um arquivo existente
.venv/bin/python tools/check_links.py

# Layout dos decks: estouro de 1280x720, bloco sobreposto, título colidindo com a marca
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html
.venv/bin/python tools/check_slides.py --shots /tmp/shots aulas/_fixture-tema.html

# Widgets do deck: todos os declarados montam (data-pronto="sim") e o console fica sem erro
.venv/bin/python tools/check_widgets.py aulas/_fixture-tema.html

# Regerar o JSON do widget do fixture do tema, a partir de dados/
.venv/bin/python tools/dados_widgets_fixture.py

# Regerar o snapshot de dados/: precisa de rede e sobrescreve os oito CSVs versionados
.venv/bin/python tools/baixar_dados.py
```

Todo comando acima roda como está escrito.
O `baixar_dados.py` depende de provedor externo: em 17/09/2026, numa primeira tentativa, a API do
SGS respondeu HTTP 200 com página HTML em duas das quatro séries, o script parou em erro de JSON,
e a tentativa seguinte completou a coleta. Ele é chamado só quando a janela do case muda, e o
`dados/README.md`, seção 7, diz o que conferir antes de aceitar uma coleta nova.

Quando uma aula existir, o deck dela, de nome `aulas/aulaNN.html`, entra nos mesmos comandos do
`check_slides.py` e do `check_widgets.py`, ao lado do fixture, e abre no preview pela URL
equivalente, com `?print-pdf` para exportar o PDF. Cada aula traz também os scripts dela, que
nascem com ela: `tools/dados_widgets_aulaNN.py` para o JSON dos widgets e
`tools/animacoes_aulaNN.py` para as animações MP4 e os pôsteres, que precisa de ffmpeg. O notebook
da aula roda sem rede, como no CI, por
`M08_OFFLINE=1 jupyter nbconvert --to notebook --execute --output-dir /tmp/nb notebooks/aulaNN.ipynb`,
e o equivalente dentro do ambiente é `.venv/bin/python -m nbconvert`. O `docs/ANDAMENTO.md` diz
quais aulas já existem.

## 3. Arquitetura de conteúdo em três camadas

Alterar o conteúdo de uma aula costuma exigir tocar em mais de uma camada, nesta ordem de
dependência.

1. **Planejamento** (raiz do repositório e `docs/`)
   - `PLANO_DE_ENSINO.md`: o case, os dados, o cronograma das seis instruções, as entregas com
     peso citado e as pendências P1 a P7.
   - `PLANEJAMENTO_AULA_A_AULA.md`: roteiro de cada encontro em sete blocos de 15 minutos, com a
     interação nomeada que fecha cada bloco.
   - `docs/autoestudos-por-semana.md`: os dois autoestudos de cada semana de instrução, com título
     exato, tempo e origem.
   - `docs/superpowers/specs/2026-09-17-modulo-08-admtech-computacao-design.md`: o design do
     acervo, que é a origem das seis ADRs da fundação.
   - Os dois primeiros são a **fonte da verdade** para data, título, escopo, autoestudo e peso.
     Nenhum artefato inventa o que deveria vir deles.

2. **Metodologia** (skills globais, fora deste repositório)
   - `~/.claude/skills/inteli-course-design/SKILL.md`: estrutura do encontro de 2h, a regra dos 15
     minutos, a aprendizagem em espiral, o case do parceiro como espinha dorsal, a amarração
     aula/sprint/artefato/autoestudo e a anatomia dos quatro artefatos por aula.
   - `~/.claude/skills/inteli-deck-design/SKILL.md`: identidade visual, tipografia, grafismo
     isométrico, anatomia do deck Reveal.js e as armadilhas de layout já corrigidas. Ler antes de
     tocar em qualquer slide ou no tema.

3. **Materiais** (este repositório)
   - `index.html`: portal com um card por instrução, agrupado por sprint. Existe, com as seis
     instruções; os quatro botões de cada card ficam desabilitados até o artefato correspondente
     existir, e a task que constrói cada artefato habilita o botão dele (ver `docs/ANDAMENTO.md`).
   - `aulas/aulaNN.html`: um deck Reveal.js autocontido por aula, de `aula01` a `aula06`, ao lado
     do `aulas/_fixture-tema.html`, que é o deck de referência de cada classe do tema.
   - `materiais/`, `referencias/`, `notebooks/`, `docs/notas-do-professor/`: os demais artefatos
     por aula. `docs/ANDAMENTO.md` diz o que já existe.
   - `exemplos/aula06-api-carteira/`: o exemplo da Aula 06, com backend FastAPI e frontend React
     (ADR-008). Os testes dele rodam por `tools/tests/test_exemplo_aula06.py`.
   - `dados/`: o snapshot do case (ver seção 4 e `dados/README.md`).
   - `assets/{css,js,js/widgets,img,data}/`: tema, scripts, marca, JSON dos widgets
     e, em `assets/video/`, as animações.
   - `docs/adrs/`: as decisões não triviais, começando pelas seis da fundação.

O deck é inicializado com `width: 1280, height: 720, center: false, margin: 0`, e o tema fixa cada
`section` nesse tamanho: o conteúdo não rola, e o que não couber quebra o slide visualmente. A
anatomia completa está na `inteli-deck-design`, seção 7, e este arquivo não a repete.

## 4. O case e os dados

O projeto do módulo é uma ferramenta de simulação de carteira eficiente para um parceiro que
precisa decidir onde alocar excedentes de caixa. Ela calcula a Fronteira Eficiente de Markowitz e
apresenta o resultado a quem decide. O nome e as premissas do parceiro estão no LBL da Adalove, que
ainda não foi lido (P4).

`dados/` guarda o snapshot do case, coletado em 17/09/2026, na janela de 02/01/2019 a 31/08/2026.
Decks, materiais, notebooks, widgets, animações e testes leem número apenas desses arquivos.

| Arquivo | Conteúdo | Fonte | Linhas |
|---|---|---|---|
| `precos_ajustados.csv` | `Adj Close` de 15 ativos da B3 | Yahoo Finance via yfinance 1.7.0 | 1.908 |
| `precos_fechamento.csv` | `Close` dos mesmos 15 ativos | Yahoo Finance via yfinance 1.7.0 | 1.908 |
| `eventos_desdobramento.csv` | `ticker, data, fator` | Yahoo Finance via yfinance 1.7.0 | 15 |
| `eventos_proventos.csv` | `ticker, data, valor` | Yahoo Finance via yfinance 1.7.0 | 499 |
| `cdi_diario.csv` | taxa DI over diária | BCB SGS, série 12 | 1.926 |
| `selic_meta.csv` | meta da Selic do Copom | BCB SGS, série 432 | 2.800 |
| `ipca_mensal.csv` | variação mensal do IPCA | BCB SGS, série 433 | 92 |
| `ptax_venda.csv` | dólar americano, venda, PTAX | BCB SGS, série 1 | 1.926 |

Fatos do snapshot que o material usa e que `tools/tests/test_dados.py` trava:

- **Três visões de preço.** O `Close` já vem dividido pelos fatores de desdobramento, grupamento e
  bonificação. O `Adj Close` desconta também os proventos: no primeiro pregão da janela, o da
  PETR4 vale 26,13% do `Close`. O preço como foi negociado na época é reconstruído em aula,
  multiplicando o `Close` pelos fatores posteriores de `eventos_desdobramento.csv`.
- **Ausências reais do provedor.** BOVA11, IVVB11 e GOLD11 ficam sem cotação em 24/10/2025, pregão
  normal da B3. A GOLD11 acumula 485 pregões sem cotação, dos quais 484 são anteriores à primeira
  cotação do fundo, em 11/12/2020.

Tratamento de ausência do módulo (ADR-009, `tools/retornos.py`, travado em
`tools/tests/test_retornos.py`):

- **Uma regra para as seis aulas.** Lacuna isolada é preenchida com o último preço (são três, todas
  em 24/10/2025), nada é preenchido antes da primeira cotação, métrica de um ativo usa a série
  inteira dele e análise conjunta usa a janela comum dos ativos envolvidos. Toda medição das Aulas
  02 a 06 importa `tools/retornos.py`; notebook repete a regra em poucas linhas, sem importar
  `tools/`.
- **Custo da janela comum.** Com a GOLD11, a janela comum dos 15 ativos tem 1.423 retornos, de
  14/12/2020 a 31/08/2026, e perde março de 2020: a volatilidade anual da PETR4 vai de 39,25% para
  33,40%. A Aula 01 mede o efeito de descartar as datas sobre o preço (1.423 dos 1.908 pregões e
  33,41%, travados em `tools/tests/test_aula01.py`); a diferença de 0,01 ponto vem de a janela
  comum preencher 24/10/2025 em vez de descartar.

O contrato de coluna, os links conferidos das séries do Banco Central, a classificação dos 15
eventos corporativos e o procedimento de regeneração estão em `dados/README.md`. A decisão está na
ADR-003.

## 5. Sala de aula invertida

Toda aula é desenhada em três tempos, e o encontro abre medindo o preparo (ADR-004).

| Tempo | Onde vive no acervo | Conteúdo |
|---|---|---|
| Antes | autoestudos na Adalove e seção "Preparação" do material de apoio | os dois autoestudos da semana, duas a três animações curtas do conceito central e uma autoverificação de cinco perguntas sem nota |
| Durante | deck e notebook | verificação do preparo por Peer Instruction, blocos de até 15 minutos alternando demonstração com widget, prática em dupla e discussão com dado real, cronômetro visível nas atividades |
| Depois | material de apoio, notebook e slide de amarração | avanço do artefato da sprint, desafio do notebook e leitura complementar |

O encontro segue em 2 horas: 15 minutos de daily e 105 minutos em sete blocos. A regra dos 15
minutos vale sem exceção, e cada bloco fecha em uma interação nomeada, travada em
`tools/tests/test_planejamento.py`. As cinco técnicas adotadas e o componente de deck de cada uma
estão na ADR-004 e no `PLANO_DE_ENSINO.md`, seção 7.

## 6. Mídia

**Contrato de vídeo** (ADR-005, implementado em `tools/midia.py`): MP4 H.264, `yuv420p`, 1280x720,
30 quadros por segundo, sem áudio, até 60 segundos e 3 MB, com pôster PNG 1280x720. Saída em
`assets/video/aulaNN-<assunto>.mp4` e `assets/img/aulaNN-<assunto>-poster.png`. No deck e no
material, `<video controls muted playsinline preload="metadata" poster="...">`. Conferido por
`ffprobe` em `tools/tests/test_midia.py`, que também reprova vídeo órfão e vídeo referenciado que
não existe.

**Contrato de widget** (ADR-005, runtime em `assets/js/inteli-widgets.js`):

```html
<div class="widget" data-widget="nome" data-fonte="../assets/data/arquivo.json"></div>
<script src="../assets/js/inteli-widgets.js"></script>
<script src="../assets/js/widgets/nome.js"></script>
```

O script de `assets/js/widgets/nome.js` chama `IntelIWidgets.registrar('nome', funcao)`, e o
runtime grava `data-pronto="sim"` no elemento ao terminar de montar, ou `data-pronto="erro"` com
mensagem no console. Cor vem de `api.cor('--seg-primaria')`, fonte de `api.fonte(16, 600)` e
coordenada de ponteiro de `api.ponto(evento, canvas)`.

Arquivos de referência: `assets/js/widgets/barras-horizontais.js` (widget genérico em canvas),
`tools/dados_widgets_fixture.py` (gerador do JSON a partir de `dados/`),
`aulas/_fixture-tema.html` (slide de demonstração), `tools/midia.py` (contrato e gravação) e
`tools/paleta.py` (tokens de cor para Python).

## 7. Armadilhas conhecidas

Herdadas do acervo de origem e ainda válidas:

- **Slide que estoura os 720px não aparece em `scrollHeight`.** A `section` tem altura fixa, e esse
  valor volta 720 mesmo com conteúdo vazando. Medir com `tools/check_slides.py`, que compara o
  retângulo de cada descendente com a área útil.
- **A capa usa `conic-gradient`, com SVG recortado descartado.** Trocar de técnica reintroduz um
  bug de empilhamento no Chrome headless, que é o navegador dos validadores.
- **Classe de estado (quiz respondido, fragment revelado, escolha revelada) precisa vencer a
  especificidade da regra base do componente.** Sem isso o DOM muda e a tela fica igual.
- **`tools/check_slides.py` é cego a estado pós-interação.** Ele mede com `page.goto` e nunca clica
  em nada. Responder o quiz, revelar fragments e mover o widget é verificação manual.
- **Screenshot de `?print-pdf` não valida impressão.** Aquilo só aciona o layout empilhado do
  Reveal por JavaScript. Gerar o PDF de verdade antes de validar.
- **Passar no macOS não garante passar no Ubuntu do CI.** As métricas de fonte do Linux são
  diferentes, e o mesmo parágrafo ocupa mais linhas lá. Um slide com menos de cerca de 80px de
  folga vertical no macOS é candidato a reprovar no CI.
- **O repositório é publicado inteiro no GitHub Pages.** Planilha da Adalove, enunciado de
  ponderada e `.env` estão no `.gitignore` de propósito.

Deste módulo:

- **O `Close` do Yahoo já vem ajustado por desdobramento.** Nenhuma queda diária da cesta é
  artefato de evento corporativo, e o grupamento da MGLU3 ou o desdobramento da B3SA3 só aparecem
  como salto na visão de preço negociado, reconstruída a partir de `eventos_desdobramento.csv`.
- **O Chromium do Playwright não decodifica H.264.** Nenhuma verificação toca o vídeo; o contrato
  é medido por `ffprobe`.
- **Widget que mede o layout para desenhar desenha em zero.** Slide fora de cena tem
  `display: none` e mede zero em largura e altura. O canvas usa `data-largura` e `data-altura` do
  markup.
- **Widget precisa estar registrado antes do evento `load`.** O runtime monta depois de `load` e de
  `document.fonts.ready`; quem se registra depois disso encontra a montagem já feita, e o elemento
  fica com `data-pronto="erro"` e "widget sem registro" no console.
- **A janela comum com a GOLD11 tira março de 2020 de todos os ativos.** Medição conjunta que
  inclui a GOLD11 começa em 14/12/2020. Qualquer número de deck que dependa da janela declara
  início e número de retornos (ADR-009), e medição nova sai de `tools/retornos.py`, nunca de um
  `ffill` ou `dropna` escrito à mão.
- **Servidor de teste de uma única thread trava com o Chromium.** A preconexão especulativa do
  navegador fica aberta e muda, e um `TCPServer` de uma thread para de atender. Os validadores
  usam `ThreadingTCPServer`, com a regressão em `tools/tests/test_servidor.py`.

A causa raiz das armadilhas de layout está na `inteli-deck-design`, seção 8, e as de verificação na
`inteli-course-design`, seção 8.

## 8. Automação

Em funcionamento hoje:

| Ferramenta | O que faz |
|---|---|
| `tools/check_brand.py` | varre o acervo procurando cor literal fora do arquivo de tokens, cor fora da paleta, cor de outro segmento, `font-family` fora dos tokens e emoji |
| `tools/check_slides.py` | abre cada deck em 1280x720 no Playwright e reporta estouro, bloco sobreposto e título colidindo com a marca |
| `tools/check_links.py` | confere que todo `href` e `src` local resolve para um arquivo existente, sem tocar link externo |
| `tools/check_widgets.py` | abre cada deck, conta os widgets declarados, exige `data-pronto="sim"` em todos e zero erro de console |
| `tools/tests/` | suíte pytest dos validadores, dos dados, da mídia, dos componentes e do planejamento |

Em funcionamento agora:

| Ferramenta | O que faz |
|---|---|
| Hook `PostToolUse` em `.claude/settings.json` | dispara `check_slides.py` e `check_brand.py` ao editar `aulas/*.html` |
| Agente `construtor-aulas` em `.claude/agents/construtor-aulas.md` | constrói uma aula inteira, incluindo animações, widgets e a seção "Preparação" do material |
| Agente `revisor-slides` em `.claude/agents/revisor-slides.md` | revisa um deck, incluindo vídeo, widget depois de interação, fragments revelados e a abertura por verificação do preparo |
| `.github/workflows/validate.yml` | instala ffmpeg e Chromium, roda os quatro validadores, a suíte pytest e os notebooks com `M08_OFFLINE=1`, e exige árvore de trabalho limpa |
| `.github/workflows/static.yml` | publica no GitHub Pages a cada push em `main` |

## 9. Convenções editoriais

Valem para deck, material de apoio, referências, notebook, portal, ADR e documento de
planejamento. Detalhadas na `inteli-course-design`, seção 7.

- Português do Brasil com **acentuação completa**, inclusive em comentário de código novo e em
  mensagem de commit. Arquivo copiado do acervo de origem mantém os comentários originais.
- **O travessão U+2014 é proibido.** Usar dois-pontos, vírgula, parênteses ou hífen. Em código,
  referir-se a ele como `chr(0x2014)`.
- **Emoji é proibido.** A iconografia é o Material Symbols Sharp do `inteli-brand-kit`, servido pelo
  sprite `assets/icons/icones.svg`: `<svg class="icone" aria-hidden="true"><use
  href="../assets/icons/icones.svg#nome"></use></svg>`. Ícone novo entra na página e o sprite é
  regenerado por `.venv/bin/python tools/icones.py` (ADR-011).
- **Marca pelo `inteli-brand-kit` vigente** (ADR-011), que vence a `inteli-deck-design` onde as duas
  divergem: canto reto em todo container (`GRA-01`), título em peso 700, subtítulo e label 600,
  corpo 300 e destaque 700 (`TIP-04`). O `check_brand.py` reprova raio, ícone Outlined e peso fora
  dessa tabela.
- **Cor só por token**: `var(--inteli-*)` e `var(--seg-*)` em HTML, CSS e JS, `paleta.cor("--token")`
  em Python.
- **Número vem de `dados/` por código e fica travado em teste.** Nada digitado de memória.
- **Data, horário, título, autoestudo e peso são citados da fonte.** O que falta vira pendência
  registrada, nunca estimativa. As datas das aulas vêm da Adalove, lida em 13/10/2026; o horário
  de relógio segue pendente (P1).
- **Título de slide analítico é frase completa com o achado e o número dentro.** Slide de
  referência tem título descritivo curto.
- **Proibido** paralelismo negativo ("não é X, é Y"), antítese simétrica, escalada com dois-pontos
  ("não apenas X: Y") e título de listicle ("Os três erros que..."). Tabela é preferível a grade de
  cartões.
- Referências são numeradas na página de referências de cada aula.
- Notebook tem badge do Colab na primeira célula, carga de dado com queda para a URL bruta,
  `M08_OFFLINE=1` desligando a rede e nenhuma saída gravada.

## 10. Commits e push

O autor já está configurado no repositório como `José Romualdo <joseromualdo@outlook.com>`.
Commits em Conventional Commits, com a mensagem terminando na linha de coautoria:

```bash
git commit -m "feat(aula01): deck da Aula 01

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

O repositório está no GitHub em `git@github.com-josercf:josercf/2026-2B-M08.git`, que usa o host
do `~/.ssh/config` que autentica como `josercf`. O remoto está configurado como `origin` e a
branch `main` está sincronizada com o repositório remoto. O portal publica em
<https://josercf.github.io/2026-2B-M08/> via `.github/workflows/static.yml`, e `REPO_BLOB` em
`tools/check_links.py` é `https://github.com/josercf/2026-2B-M08/blob/main/`.
