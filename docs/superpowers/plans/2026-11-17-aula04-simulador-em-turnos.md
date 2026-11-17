# Aula 04 em turnos: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** entregar até a manhã de 18/11/2026 a Aula 04 em turnos: portal de simulação de carteiras
com painel de alunos, notebook dos turnos 1 e 2, kit dos turnos 3 a 5 para uso com agente, deck e
documentação, tudo testado.

**Architecture:** um arquivo de cotações gerado uma vez alimenta o portal (JSON) e o kit (CSV). A
conta do simulador existe em duas implementações com as mesmas definições, uma em JavaScript para o
portal e uma em Python como referência dos testes, e um teste de paridade compara as duas. O estado
compartilhado da sala fica em três tabelas novas `sim_*` no Supabase do quiz ao vivo, com modo em
memória para quando o banco não responde.

**Tech Stack:** HTML, CSS e JavaScript puro, Reveal.js do acervo, Python 3 com pandas e NumPy,
pytest, Playwright, Supabase (Postgres com RLS e funções `security definer`), yfinance.

**Spec:** `docs/superpowers/specs/2026-11-17-aula04-simulador-em-turnos-design.md`

## Global Constraints

- Convenções editoriais do `CLAUDE.md`, seção 9: pt-BR com acentuação completa, sem `chr(0x2014)`,
  sem emoji, cor só por token, canto reto, sem paralelismo negativo, antítese simétrica ou título
  de listicle. Tabela antes de cartões.
- Sessão: `m08-aula04-2026-11-18`. Grupos: `G01`, `G02`, `G03`, `G04` e `VIS` (visitante).
- Data de corte das cotações: `2026-11-13`. Início: `2024-01-02`.
- Definições numéricas da seção 5.4 da spec: retorno simples diário do preço ajustado; janela comum
  dos ativos escolhidos com a regra da ADR-009; retorno anual = média diária vezes 252; risco anual
  = desvio padrão amostral (`ddof=1`) vezes raiz de 252; Sharpe = (retorno menos `rf`) dividido
  pelo risco; sorteio uniforme normalizado.
- Períodos do portal, em pregões anteriores ao corte: 9, 21, 63, 126, 252. Simulações: 10, 100,
  1.000, 10.000. Ativos por carteira: de 2 a 5.
- Nenhum nome de aluno em arquivo do repositório nem em tabela com leitura pública. O banco guarda
  iniciais (1 a 3 letras) e grupo.
- SQL novo só cria objetos com prefixo `sim_`. Nada existente é alterado ou removido.
- `tools/medidas_aula04.py` e `assets/data/aula04-nuvem.json` continuam existindo.
- `.venv/bin/python -m pytest tools/tests` e os quatro validadores passam ao fim de cada tarefa.
- Commit e push só com autorização do professor.

## Review Focus

1. Ativo do grupo fora do arquivo de cotações: o portal mostra "ativo não encontrado no arquivo da
   aula" e mantém a carteira montada até ali. Teste na Tarefa 4.
2. Banco fora do ar ou lento em sala: entrar, montar e simular funcionam, e o painel cai para
   memória com aviso. Teste na Tarefa 4 com a URL do banco bloqueada no Playwright.
3. Ativo com início de negociação dentro da janela pedida: o período oferecido é limitado ao que a
   janela comum tem, e o portal informa quantos pregões existem. Testes nas Tarefas 2 e 4.
4. Aluno digita valor esperado com vírgula decimal ou em porcentagem no notebook ("12,3%"): o
   `conferir` aceita e compara com tolerância de 0,05 ponto percentual. Teste na Tarefa 5.
5. Agente altera os testes para passar: `conferir.py` do kit roda testes de aceite próprios, fora
   de `tests/`, e as instruções do agente proíbem editar `conferir.py`. Teste na Tarefa 6.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade | Tarefa |
|---|---|---|
| `tools/dados_aula04_simulador.py` | baixa cotações e CDI, grava JSON e CSV | 1 |
| `assets/data/aula04-cotacoes.json` | cotações para o portal | 1 |
| `exemplos/aula04-simulador/dados/precos.csv` | cotações para kit e notebook | 1 |
| `tools/simulador_referencia.py` | solução de referência em Python | 2 |
| `assets/js/simulador-nucleo.js` | a mesma conta em JavaScript, sem DOM | 2 |
| `exemplos/aula04-supabase/aula04.sql` | tabelas e funções `sim_*` | 3 |
| `assets/js/simulador-dados.js` | camada de dados da sala: Supabase ou memória | 3 |
| `simulador/index.html`, `assets/js/simulador-portal.js`, `assets/css/simulador.css` | portal | 4 |
| `notebooks/aula04.ipynb` | turnos 1 e 2 | 5 |
| `exemplos/aula04-simulador/**`, `tools/empacotar_kit_aula04.py`, `materiais/aula04-simulador.zip` | kit | 6 |
| `aulas/aula04.html`, `aulas/aula04-spec.html`, material, referências, notas | deck e apoio | 7 |
| `PLANEJAMENTO_AULA_A_AULA.md`, `docs/adrs/ADR-018-*.md`, `docs/ANDAMENTO.md` | planejamento | 8 |

---

### Task 1: Cotações da aula

**Files:**
- Create: `tools/dados_aula04_simulador.py`, `assets/data/aula04-cotacoes.json`,
  `exemplos/aula04-simulador/dados/precos.csv`, `tools/tests/test_dados_aula04_simulador.py`

**Interfaces:**
- Produces: JSON `{"corte": "2026-11-13", "inicio": "2024-01-02", "rf_anual": float,
  "datas": ["AAAA-MM-DD", ...], "precos": {"PETR4": [float | null, ...], ...}}`, preços com 4
  casas, `null` apenas antes da primeira cotação do ativo. CSV com coluna `data` e uma coluna por
  ticker, mesmas linhas, e a primeira linha de comentário ausente. `rf_anual` também em
  `exemplos/aula04-simulador/dados/rf.txt`, uma linha.
- Produces: `tools.dados_aula04_simulador.UNIVERSO: list[str]`, tickers sem o sufixo `.SA`.

- [ ] Escrever `test_dados_aula04_simulador.py`: última data igual a `2026-11-13`; primeira data
  maior ou igual a `2024-01-02`; PETR4, VALE3, ITUB4, BOVA11, IVVB11 e GOLD11 presentes; pelo menos
  100 tickers; nenhum `null` depois da primeira cotação de cada ativo; JSON e CSV com as mesmas
  datas e os mesmos tickers; `0.05 < rf_anual < 0.25`; arquivo JSON com menos de 3 MB.
- [ ] Rodar e ver falhar.
- [ ] Implementar o script: `UNIVERSO` com o IBrX-100, os três ETFs do acervo e os FIIs e BDRs mais
  negociados; `yfinance.download(..., auto_adjust=True)`; descarta ticker sem dado; preenche lacuna
  isolada com o último preço depois da primeira cotação; `rf_anual` pela série 12 do SGS nos 252
  pregões até o corte, com nova tentativa quando a resposta não for JSON.
- [ ] Rodar o script, rodar o teste e ver passar.

### Task 2: Conta do simulador em Python e em JavaScript

**Files:**
- Create: `tools/simulador_referencia.py`, `assets/js/simulador-nucleo.js`,
  `tools/tests/test_simulador_referencia.py`, `tools/tests/test_simulador_paridade.py`

**Interfaces:**
- Produces (Python):
  - `retornos(precos: pd.DataFrame, ativos: list[str], pregoes: int) -> pd.DataFrame`, as últimas
    `pregoes` linhas de retorno da janela comum; `ValueError` se a janela tiver menos que isso.
  - `retorno_do_dia(pesos, retornos_do_dia) -> float`
  - `metricas(pesos, retornos) -> tuple[float, float]`, retorno anual e risco anual.
  - `sortear_pesos(k: int, rng: np.random.Generator) -> np.ndarray`
  - `simular(retornos, n: int, semente: int, rf: float) -> pd.DataFrame`, colunas `w_<ticker>`,
    `retorno`, `risco`, `sharpe`.
  - `posicionar(pesos, retornos, rf: float) -> dict` com `retorno`, `risco`, `sharpe`.
- Produces (JavaScript, `window.SimuladorNucleo`): `retornos(cotacoes, ativos, pregoes)` devolvendo
  `{datas, linhas}`, `pregoesDisponiveis(cotacoes, ativos)`, `retornoDoDia(pesos, linha)`,
  `metricas(pesos, linhas)` devolvendo `{retorno, risco}`, `gerador(semente)` (mulberry32),
  `sortearPesos(k, gerador)`, `simular(linhas, n, semente, rf)` devolvendo vetores `retorno`,
  `risco`, `sharpe` e `pesos`, `posicionar(pesos, linhas, rf)`.

- [ ] Testes da referência: carteira de um ativo devolve o retorno e o risco do ativo; pesos iguais
  em dois ativos conferem com a conta feita por série diária; `sortear_pesos` soma 1 com tolerância
  `1e-12`, sem negativo, formato `(k,)`; `simular` com a mesma semente devolve a mesma tabela;
  10.000 simulações com 2, 5 e 20 ativos em menos de 10 s cada; `retornos` com `pregoes` maior que
  a janela levanta `ValueError`; ativo que começa dentro da janela reduz a janela comum.
- [ ] Rodar e ver falhar; implementar; ver passar.
- [ ] Teste de paridade com Playwright: página mínima carrega `simulador-nucleo.js` e o JSON; para
  seis carteiras fixas (2 a 5 ativos, períodos 9 e 252) `metricas` do JavaScript e do Python
  diferem em menos de `1e-9`; `gerador` com a mesma semente devolve a mesma sequência em duas
  chamadas.
- [ ] Rodar e ver falhar; implementar o núcleo em JavaScript; ver passar.

### Task 3: Banco da sala

**Files:**
- Create: `exemplos/aula04-supabase/aula04.sql`, `assets/js/simulador-dados.js`,
  `tools/tests/test_simulador_sql.py`

**Interfaces:**
- Produces (SQL): tabelas `sim_participantes(id, sessao, iniciais, grupo, criado_em)`,
  `sim_carteiras(participante, sessao, ativos text[], pregoes, n, semente, pesos jsonb,
  atualizado_em)`, `sim_turnos(participante, sessao, turno, feito_em)`, as três com leitura
  pública. Funções `sim_entrar(p_sessao text, p_iniciais text, p_grupo text) returns uuid`,
  `sim_salvar(p_participante uuid, p_ativos text[], p_pregoes int, p_n int, p_semente int,
  p_pesos jsonb) returns timestamptz`, `sim_marcar(p_participante uuid, p_turno int,
  p_feito boolean) returns boolean`. Validação no servidor: iniciais de 1 a 3 letras, grupo na
  lista, 2 a 5 ativos, período e `n` nas listas das Global Constraints, turno de 1 a 5.
- Produces (JavaScript, `window.SimuladorDados.abrir(sessao)`): objeto com `tipo` (`supabase` ou
  `memoria`), `entrar(iniciais, grupo)`, `salvar(participante, simulacao)`,
  `marcar(participante, turno, feito)`, `sala()` devolvendo participantes com carteira e turnos,
  `assinar(callback)`. Segue o padrão de `assets/js/inteli-quiz-dados.js`, inclusive a queda para
  memória com `?demo=1` ou sem configuração.

- [ ] Teste estático do SQL: só cria objetos `sim_*`; nenhum `drop table`, `alter table` fora de
  `enable row level security`, nem `delete`; toda tabela tem RLS ligado; nenhuma coluna `nome`.
- [ ] Escrever o SQL, idempotente.
- [ ] Aplicar no projeto `m08-quiz` pelo CLI do Supabase a partir de `AD08-LBL/` e conferir as
  três funções com uma sessão de teste `m08-aula04-teste`.
- [ ] Implementar `simulador-dados.js`; o teste de comportamento dele entra na Tarefa 4.

### Task 4: Portal de simulação

**Files:**
- Create: `simulador/index.html`, `assets/js/simulador-portal.js`, `assets/css/simulador.css`,
  `tools/tests/test_simulador_portal.py`
- Modify: `index.html` (link do portal no card da Aula 04)

**Interfaces:**
- Consumes: `SimuladorNucleo`, `SimuladorDados`, `assets/data/aula04-cotacoes.json`.
- Produces: URL `simulador/` com as telas `#entrar`, `#montar`, `#simular`, `#painel`,
  `#progresso` e `#ver=<id>`; `?demo=1` força memória; `?painel=1` abre direto no painel, para o
  projetor.

Telas: entrada (iniciais e grupo); montagem (busca de ticker, lista de 2 a 5 ativos, período,
retorno e risco da carteira de pesos iguais, evolução de R$ 100 mil, tabela dos retornos diários
quando o período é 9); simulação (quantidade, nuvem de risco e retorno em canvas, campo de pesos
próprios que somam 100% e marca a carteira na nuvem, aviso de que 9 pregões são instáveis para a
nuvem); painel (grade de avatares por grupo, clique abre a simulação da pessoa, placar de turnos
por grupo); progresso (cinco caixas de turno para a dupla marcar).

- [ ] Testes com Playwright em `?demo=1`: entrar com iniciais e grupo; montar com PETR4 e VALE3 em
  9 pregões e ver retorno e risco iguais aos da referência em Python; simular 10.000 e ver a nuvem
  desenhada em menos de 2 s; informar pesos próprios e ver o marcador; abrir o painel e a
  simulação de um segundo participante criado no mesmo modo de memória; marcar um turno e ver o
  placar; nenhum erro de console.
- [ ] Testes do Review Focus 1, 2 e 3.
- [ ] Implementar; rodar `check_brand.py` e `check_links.py`.

### Task 5: Notebook dos turnos 1 e 2

**Files:**
- Rename: `notebooks/aula04.ipynb` para `notebooks/aula04-v1.ipynb`
- Create: `notebooks/aula04.ipynb`, `tools/tests/test_notebook_aula04_turnos.py`

**Interfaces:**
- Consumes: `exemplos/aula04-simulador/dados/precos.csv`, `tools/simulador_referencia.py` (só no
  teste).
- Produces: notebook com as células `ATIVOS`, `PREGOES`, turno 1 (`retorno_do_dia`), turno 2
  (`metricas`), `conferir_turno1(esperado, funcao)`, `conferir_turno2(esperado_retorno,
  esperado_risco, funcao)` e a célula final que grava `simulador.py`.

- [ ] Testes: o notebook executa com `M08_OFFLINE=1` e respostas vazias sem erro e imprime
  "AINDA NÃO"; com as funções da referência injetadas imprime "OK" nos dois turnos; valor esperado
  aceito como `0.123`, `12.3`, `"12,3%"`; nenhuma saída gravada; badge do Colab na primeira célula;
  o `simulador.py` gerado importa e passa nos testes de aceite dos turnos 1 e 2.
- [ ] Implementar seguindo o padrão `conferir` de `notebooks/aula03.ipynb`.

### Task 6: Kit do simulador

**Files:**
- Create: `exemplos/aula04-simulador/{README.md,SPEC.md,AGENTS.md,CLAUDE.md,simulador.py,
  conferir.py,checar_ambiente.py,requirements.txt}`, `exemplos/aula04-simulador/tests/
  test_turno{1,2,3,4,5}.py`, `exemplos/aula04-simulador/docs/adrs/ADR-001-janela-dos-dados.md`,
  `ADR-002-sorteio-dos-pesos.md`, `tools/empacotar_kit_aula04.py`,
  `materiais/aula04-simulador.zip`, `tools/tests/test_kit_aula04.py`

**Interfaces:**
- Consumes: assinaturas da Tarefa 2 (Python). O `SPEC.md` usa os cinco campos da tela de spec:
  função, entrada, saída, casos de borda, critério de aceite.
- Produces: `python conferir.py <turno>` devolve código 0 e imprime "TURNO n: OK" quando o turno
  passa, e código 1 com a lista do que falta quando não passa; `python checar_ambiente.py` confere
  Python 3.10 ou mais novo, pandas, NumPy, matplotlib e pytest.

- [ ] Testes: com `tools/simulador_referencia.py` copiado sobre `simulador.py`, `conferir.py` passa
  nos cinco turnos; com o `simulador.py` do kit, falha nos cinco; o `.zip` contém exatamente os
  arquivos da pasta e está em dia; `AGENTS.md` e `CLAUDE.md` têm o mesmo conteúdo e proíbem editar
  `conferir.py`; nenhum arquivo do kit acessa a rede.
- [ ] Implementar. `tests/test_turnoN.py` traz um teste de exemplo completo e um teste com o
  `assert` em branco para o aluno escrever. A spec do turno 3 vem preenchida; as dos turnos 4 e 5
  trazem só o nome da função e os campos vazios.

### Task 7: Deck, tela de spec e material de apoio

**Files:**
- Rename para `-v1`: `aulas/aula04.html`, `materiais/aula04.html`, `referencias/aula04.html`,
  `docs/notas-do-professor/aula04.md`
- Modify: `tools/tests/test_aula04.py` (caminhos `-v1`), `index.html`
- Create: `aulas/aula04.html`, `aulas/aula04-spec.html`, `materiais/aula04.html`,
  `referencias/aula04.html`, `docs/notas-do-professor/aula04.md`,
  `tools/tests/test_deck_aula04_turnos.py`

**Interfaces:**
- Consumes: URL do portal e `?painel=1` (Tarefa 4), nomes das funções dos turnos (Tarefa 2),
  `conferir.py` (Tarefa 6), componentes `inteli-quiz-vivo`, `inteli-codigo`, `inteli-cronometro`,
  `inteli-adr`.
- Produces: `aulas/aula04-spec.html?g=G0n&t=<token>&turno=4|5`, que reaproveita `inteli-adr.js`
  com a sessão `m08-aula04-2026-11-18-t4` ou `-t5` e os campos mapeados nos nomes aceitos por
  `adr_salvar` (`titulo` para função, `contexto` para entrada, `criterios` para saída, `opcoes`
  para casos de borda, `decisao` para aceite), com o botão "Copiar como SPEC.md".

- [ ] Ler `inteli-course-design` e `inteli-deck-design` antes de escrever slide.
- [ ] Testes do deck: slide de daily; QR code do portal; um slide por turno com função, onde roda e
  quem implementa; slides de quiz ao vivo nos blocos 2 e 7; slide do painel com `?painel=1`;
  amarração que cita só o A3 e diz que a ADR do A3 trata de decisão do aluno; sem menção a SLSQP
  como conteúdo do encontro.
- [ ] Implementar deck, tela de spec, material, referências e notas; rodar os quatro validadores
  no deck novo e no v1.

### Task 8: Planejamento, ADR e andamento

**Files:**
- Modify: `PLANEJAMENTO_AULA_A_AULA.md` (Aula 04), `docs/ANDAMENTO.md`, `PLANO_DE_ENSINO.md` onde
  citar o conteúdo da Aula 04
- Create: `docs/adrs/ADR-018-aula04-em-turnos-com-portal-e-agente.md`

- [ ] Reescrever os sete blocos com as interações aceitas por `test_planejamento.py` e o título
  mantido: bloco 1 prever e observar, bloco 2 quiz, blocos 3 a 6 dupla no notebook, bloco 7 quiz.
- [ ] Escrever a ADR-018 na estrutura do `CLAUDE.md` global e registrar a pendência nova sobre a
  otimização que a Aula 05 e o A4 esperam.
- [ ] Rodar a suíte inteira e os validadores.

---

## Ordem de execução

Tarefas 1, 2 e 3 em sequência, porque fixam as interfaces. Depois, em paralelo e em arquivos
disjuntos: Tarefa 4; Tarefas 5 e 6 juntas; Tarefas 7 e 8 juntas. Ao fim, suíte completa,
validadores, revisão do conjunto e pedido de autorização para commit e push.

Ordem de corte, da spec: painel de avatares, placar automático, turno 5, tela de spec.
