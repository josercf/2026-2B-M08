# Andamento do acervo

Estado atual do repositório, para quem estiver retomando o trabalho. Fonte: o plano
`docs/superpowers/plans/2026-09-17-fundacao-e-aula01.md`, de 16 tarefas, que cobre a fundação do
acervo e a Aula 01 como padrão-ouro das cinco aulas restantes. O design que originou o plano está
em `docs/superpowers/specs/2026-09-17-modulo-08-admtech-computacao-design.md`.

Suíte de testes em 17/09/2026: **96 testes passando e 3 ignorados**, de 99 coletados. Os três
ignorados são as parametrizações de vídeo de `tools/tests/test_midia.py`, que ficam vazias até as
animações da Aula 01 existirem. Para conferir a contagem em qualquer momento:

```bash
.venv/bin/python -m pytest tools/tests -q
```

## Pronto

**Base visual e validadores** (`assets/css/`, `assets/img/`, `assets/js/`, `aulas/_fixture-tema.html`,
`tools/check_brand.py`, `tools/check_slides.py`, `tools/check_links.py`). Tokens da marca, tema do
deck, CSS de impressão, estilo das páginas de leitura, portal, logo em três versões, grafismo
isométrico, quiz, zoom e exportação em PDF, mais os três validadores e a suíte de teste deles. O
`check_links.py` aponta para `josercf/2026-2B-M08` e os dois validadores ignoram `.venv`. Origem
arquivo por arquivo na ADR-001.

**Cronômetro e escolha da Formação GitLab** (`assets/js/inteli-cronometro.js`,
`assets/js/inteli-escolha.js`, blocos de `assets/css/inteli-theme.css`,
`assets/css/inteli-portal.css` com o contraste corrigido, `assets/js/inteli-print.js` revelando
também o gabarito da escolha). O `tools/tests/test_componentes_ativos.py` mede o estado pós-clique
por `getComputedStyle`, e a mutação que rebaixa a especificidade de `.escolha-opcoes li.revelada`
foi vista reprovando esse teste.

**Paleta para scripts Python** (`tools/paleta.py`). Resolve os tokens de
`assets/css/inteli-brand.css`, com `var(--outro)` encadeado, para figuras e animações pedirem cor
por nome.

**Dados do case versionados** (`dados/`, `tools/baixar_dados.py`, `dados/README.md`,
`tools/tests/test_dados.py`). Snapshot coletado em 17/09/2026, na janela de 02/01/2019 a
31/08/2026, com os números abaixo travados em `tools/tests/test_dados.py`.

| Item medido | Valor |
|---|---|
| Ativos da cesta de referência (B3) | 15 |
| Pregões em cada tabela de preço | 1.908 |
| Séries do Banco Central (SGS 12, 432, 433 e 1) | 4 |
| Eventos de desdobramento, grupamento e bonificação | 15 |
| Proventos registrados | 499 |
| `Adj Close` da PETR4 no primeiro pregão, em relação ao `Close` | 26,13% |
| Pregões sem cotação da GOLD11, dos quais 484 antes da primeira cotação (11/12/2020) | 485 |
| ETFs sem cotação em 24/10/2025, pregão normal da B3 | BOVA11, IVVB11 e GOLD11 |

Descartar as datas com ausência mantém 1.423 dos 1.908 pregões, tira março de 2020 da cesta
inteira e derruba a volatilidade anual da PETR4 de 39,25% para 33,41%. Esses três números vêm do
design, seção 8, e do `PLANO_DE_ENSINO.md`, seção 3, e nenhum teste os trava ainda: quem vai
travá-los é a task de medição da Aula 01.

**Contrato de vídeo das animações** (`tools/midia.py`, `tools/tests/test_midia.py`). MP4 H.264,
`yuv420p`, 1280x720, 30 quadros por segundo, sem áudio, até 60 segundos e 3 MB, com pôster PNG.
`figura()` monta a figura 1280x720 com o tema, `gravar()` escreve o MP4 e o pôster, `metadados()`
lê por `ffprobe` e `violacoes()` compara com o contrato. O teste reprova vídeo fora do contrato,
vídeo órfão e vídeo referenciado que não existe.

**Runtime e validador de widgets** (`assets/js/inteli-widgets.js`,
`assets/js/widgets/barras-horizontais.js`, `tools/check_widgets.py`,
`tools/dados_widgets_fixture.py`, `assets/data/_fixture-pregoes.json`, o slide de widget do fixture
do tema, `tools/tests/test_check_widgets.py`, `tools/tests/test_servidor.py`). O validador exige
`data-pronto="sim"` em todo widget declarado e zero erro de console, e reprova deck com widget
declarado e nenhum medido. O servidor local dos validadores passou a `ThreadingTCPServer` por causa
da preconexão especulativa do Chromium, com regressão própria.

**Documentos de planejamento** (`PLANO_DE_ENSINO.md`, `PLANEJAMENTO_AULA_A_AULA.md`,
`docs/autoestudos-por-semana.md`, `docs/revisao-planilha-2026-09-17.md`,
`tools/tests/test_planejamento.py`). As seis aulas com título exato, os sete blocos de 15 minutos
por aula com a interação nomeada que fecha cada bloco, os 12 autoestudos com título exato e tempo,
e o texto das instruções 5 e 6, dos autoestudos das semanas 8 e 9 e das colunas E, F e G de A4 e A5
pronto para lançar na planilha.

**Decisões da fundação e guias do repositório** (`docs/adrs/ADR-001` a `ADR-006`, `CLAUDE.md`,
`README.md`, este arquivo, `tools/tests/test_adrs.py`).

| ADR | Decisão |
|---|---|
| 001 | O acervo parte da base do M03 e incorpora o cronômetro e a escolha da Formação GitLab |
| 002 | O A4 entrega o otimizador numa aplicação FastAPI com página HTML/JS, o A5 fica só com a interpretação por LLM, as instruções 5 e 6 trocam de conteúdo e a Ponderada 2 vai para a semana 9 |
| 003 | Os dados do case são um snapshot versionado de 15 ativos da B3 pelo yfinance e de quatro séries do SGS do Banco Central |
| 004 | Toda aula é desenhada em três tempos de sala invertida, e o encontro abre medindo o preparo |
| 005 | Animações são MP4 H.264 geradas por matplotlib sobre `dados/`, e widgets são JavaScript puro alimentado por JSON gerado de `dados/` |
| 006 | Os arquivos das instruções de Computação se chamam `aula01` a `aula06`, na ordem em que acontecem |

## Em andamento

| Etapa | Escopo | Estado |
|---|---|---|
| Portal | `index.html` com um card por instrução, agrupado por sprint, com os dois números de cada aula e o estado de confirmação de data e peso | a fazer |
| Automação e publicação | agentes `construtor-aulas` e `revisor-slides`, hook `PostToolUse`, `.github/workflows/validate.yml`, `.github/workflows/static.yml` e o repositório `josercf/2026-2B-M08` no GitHub | a fazer; nada disso existe hoje, e o acervo roda inteiro em local |
| Aula 01, padrão-ouro | medições travadas em teste, duas animações, os widgets, o notebook, o deck, o material, as referências, as notas do professor e a ADR de escopo da aula | a fazer |

As Aulas 02 a 06 só começam depois da Aula 01 revisada, porque ela é o padrão que elas copiam
(design, seção 15).

## Pendências abertas

As quatro primeiras são fontes oficiais que ainda não foram lidas. As três últimas são pendências
de conteúdo levantadas em 17/09/2026, que dependem da coordenação e não foram alteradas
unilateralmente no acervo. O texto completo, com efeito e forma de fechamento de cada uma, está no
`PLANO_DE_ENSINO.md`, seção 8, e as quatro da coordenação também em
`docs/revisao-planilha-2026-09-17.md`, seção 8.

| # | Pendência | Efeito imediato |
|---|---|---|
| P1 | Adalove do LBL 08 AdmTech 2026-2B, com datas, horários, autoestudos e pesos oficiais, não lida | toda data aparece como "a confirmar na Adalove" e o roteiro usa blocos relativos, sem hora de relógio |
| P2 | Planilha "Revisão LBL 8 AdmTech - 2026-2B" não lida, HTTP 401 sem sessão | pesos dos artefatos e numeração das aulas do módulo citados da revisão de junho de 2026 |
| P3 | Planilha de alocação de professores, coluna de ADM, não lida | o dia da semana de cada instrução é desconhecido, o que também define a folga real do A4 |
| P4 | LBL do parceiro não lido, e o projeto não tem TAPI | nome, setor e premissas sem citação direta, e a cesta de 15 ativos da B3 como referência das aulas |
| P5 | O A2 cobra matriz de correlação e de covariância, que a Instrução 3 só ensina na semana 5 | a Aula 02 avisa a turma e o material antecipa o mínimo necessário |
| P6 | O A4 vence na mesma semana da instrução que ensina a parte web | a folga real depende do dia da aula na semana 8, ainda não lido (P3) |
| P7 | O case de créditos OpenRouter (02/09/2026) ainda cita Streamlit e a Instrução 6 antiga | o documento aprovado descreve um produto que o módulo não vai mais construir |
