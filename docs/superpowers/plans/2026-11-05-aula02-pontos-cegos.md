# Aula 02 com pontos cegos, jogo da moeda e comitê do assessor: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar a Aula 02 por um encontro com jogo da moeda no celular, quatro decks de grupo com ADR online e prazo sincronizado, e um deck principal que conduz moeda, ponte com dado real e comitê, tudo publicado antes das 14h de 05/11/2026.

**Architecture:** Uma camada de dados nova (`inteli-aula02-dados.js`) com duas implementações, Supabase (funções `security definer` em `exemplos/aula02-supabase/aula02.sql`) e memória (`?quiz-demo=1`, localStorage e BroadcastChannel), no mesmo molde de `inteli-quiz-dados.js`. Dois componentes usam essa camada: `inteli-moeda.js` (slide e celular) e `inteli-adr.js` (deck do grupo e slide do comitê). Os decks de grupo saem de um gerador Python para que os quatro fiquem idênticos fora do conteúdo.

**Tech Stack:** Reveal.js 5.1.0, JavaScript puro, Supabase JS 2.45.4 (UMD), Postgres/PLpgSQL, Python 3 com pandas, pytest e Playwright.

**Spec:** `docs/superpowers/specs/2026-11-05-aula02-pontos-cegos-design.md`

## Global Constraints

- pt-BR com acentuação completa; `chr(0x2014)` proibido em todo arquivo; sem emoji; ícones Material Symbols Sharp pelo sprite (`tools/icones.py` regenera).
- Cor só por token (`var(--inteli-*)`, `var(--seg-*)`); canto reto; pesos 700/600/300 (ADR-011); `check_brand.py` passa.
- Pouco texto e fonte grande nos slides; nada de grade de cartões quando tabela ou prosa resolve; título analítico é frase com o número.
- Número de deck sai de `tools/medidas_aula02.py` e fica travado em teste. Número que desmonta afirmação de grupo **nunca** entra no repositório.
- Sessão da aula: `m08-aula02-2026-11-05`. Grupos: `G01` a `G04`.
- Chave do professor: a mesma do quiz (`localStorage['inteli-quiz-chave']`, `?quiz-chave=`), checada no banco por `quiz_chave_ok`.
- Modo de teste e ensaio: `?quiz-demo=1` liga a memória em todas as páginas novas; `?sessao=<s>` sobrescreve `data-sessao` em `inteli-moeda.js` e `inteli-adr.js` (ensaio em `m08-aula02-ensaio`).
- Comandos de verificação: `.venv/bin/python -m pytest tools/tests -q`, `check_brand.py`, `check_links.py`, `check_slides.py aulas/aula02*.html`, `check_widgets.py aulas/aula02.html`.
- Commits em Conventional Commits terminando com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. Dois colegas digitando no mesmo campo da ADR: quem está com o foco não perde o que digita quando chega a gravação do outro; o campo mostra o aviso de edição remota (teste na Task 3).
2. Prazo encerrado: gravação recusada pelo backend mesmo se o JS do aluno ignorar a trava, e o formulário vira somente leitura em todos os decks do grupo (teste na Task 1 e na Task 3).
3. Token errado ou ausente na URL do grupo: o deck abre em modo leitura com aviso, sem gravar (teste na Task 3).
4. Aluno que entra na moeda depois da rodada 4: joga as rodadas já liberadas em sequência e o histograma conta o saldo dele na rodada atual (teste na Task 2).
5. Recarregar o celular no meio da moeda: o aluno volta com o mesmo jogador e o mesmo saldo, sem jogar a mesma rodada duas vezes (teste na Task 2).

---

### Task 1: Banco e camada de dados da aula

**Files:**
- Create: `exemplos/aula02-supabase/aula02.sql`
- Create: `assets/js/inteli-aula02-dados.js`
- Create: `tools/tests/test_aula02_sql.py`

**Interfaces:**
- Consumes: `quiz_chave_ok(text)` e a extensão `pgcrypto` de `exemplos/quiz-supabase/quiz.sql`.
- Produces, no SQL (todas `security definer`, `grant execute` para `anon, authenticated`, salvo indicado):
  - Tabelas: `adr_tokens(sessao text, grupo text, token text, primary key(sessao, grupo))` sem política de leitura; `adr_prazos(sessao text primary key, fim timestamptz)` leitura pública; `adr_campos(sessao, grupo, campo, texto, atualizado_em, autor text, primary key(sessao, grupo, campo))` leitura pública; `moeda_sessoes(sessao text primary key, rodada int not null default 0)` leitura pública; `moeda_jogadores(id uuid pk, sessao, apelido, criado_em)` sem leitura pública; `moeda_jogadas(sessao, jogador uuid, rodada int, cara boolean, saldo numeric(12,2), primary key(jogador, rodada))` leitura pública.
  - `adr_links(p_chave text, p_sessao text) returns table(grupo text, token text)`: cria token aleatório (16 hex) para G01 a G04 se faltar e devolve os existentes.
  - `adr_prazo(p_chave text, p_sessao text, p_minutos int) returns timestamptz`: grava `fim = now() + minutos`.
  - `adr_agora(p_sessao text) returns table(agora timestamptz, fim timestamptz)`: relógio do servidor para sincronizar o cronômetro.
  - `adr_salvar(p_sessao, p_grupo, p_token, p_campo, p_texto, p_autor) returns timestamptz`: recusa (`raise exception`) token inválido, campo fora de `titulo, contexto, criterios, opcoes, decisao, impacto`, texto acima de 4.000 caracteres e `now() > fim`; sem prazo definido, aceita.
  - `moeda_liberar(p_chave, p_sessao, p_rodada int)`: rodada de 0 a 10.
  - `moeda_entrar(p_sessao, p_apelido) returns uuid`.
  - `moeda_jogar(p_sessao, p_jogador uuid, p_rodada int) returns table(cara boolean, saldo numeric)`: exige `p_rodada <= rodada liberada`, exige a rodada anterior jogada (ou `p_rodada = 1`), sorteia no servidor com `random() < 0.5`, aplica +50% ou -40% sobre o saldo anterior (R$ 100 na rodada 1) e é idempotente: repetir a mesma rodada devolve a jogada gravada.
  - Realtime: `adr_campos`, `adr_prazos`, `moeda_sessoes`, `moeda_jogadas` na publicação `supabase_realtime`.
- Produces, no JS: `window.IntelIAula02Dados.criar()` devolve backend com
  `adrLinks(chave, sessao) -> Promise<[{grupo, token}]>`,
  `adrPrazo(chave, sessao, minutos) -> Promise<fimISO>`,
  `adrAgora(sessao) -> Promise<{agora, fim}>`,
  `adrSalvar(sessao, grupo, token, campo, texto, autor) -> Promise<atualizadoISO>` (rejeita com Error nas recusas acima),
  `adrCampos(sessao, grupo?) -> Promise<[{grupo, campo, texto, atualizado_em, autor}]>`,
  `moedaLiberar(chave, sessao, rodada)`, `moedaRodada(sessao) -> Promise<int>`,
  `moedaEntrar(sessao, apelido) -> Promise<id>`, `moedaJogar(sessao, jogador, rodada) -> Promise<{cara, saldo}>`,
  `moedaJogadas(sessao) -> Promise<[{jogador, rodada, cara, saldo}]>`,
  `ouvir(sessao, aoMudar) -> cancelar` (realtime mais vigia de 4 s, como no quiz).
  A versão memória reproduz as mesmas recusas (token, campo, prazo, rodada não liberada) e usa a chave `inteli-aula02-demo` do localStorage; em memória a chave do professor é aceita se não vazia.

- [ ] **Step 1: Teste do SQL por texto.** `test_aula02_sql.py`: `test_funcoes_de_escrita_sao_security_definer_e_tabelas_tem_rls` (toda `create table` tem `enable row level security`; toda `create or replace function` tem `security definer set search_path`); `test_funcoes_de_professor_checam_a_chave` (`adr_links`, `adr_prazo`, `moeda_liberar` contêm `quiz_chave_ok(p_chave)`); `test_adr_salvar_recusa_prazo_token_e_campo` (corpo contém `now() >`, comparação com `adr_tokens` e a lista dos seis campos); `test_moeda_sorteia_no_servidor` (`random()` em `moeda_jogar`, `1.5` e `0.6`); `test_sql_nao_cria_nada_fora_dos_prefixos` (todo objeto criado começa com `adr_` ou `moeda_`).
- [ ] **Step 2:** `.venv/bin/python -m pytest tools/tests/test_aula02_sql.py -v` falha (arquivo não existe).
- [ ] **Step 3:** Escrever `aula02.sql` (idempotente: `if not exists`, `create or replace`, `drop policy if exists`) e `inteli-aula02-dados.js`.
- [ ] **Step 4:** Teste passa. A camada JS é exercida pelos testes Playwright das Tasks 2 e 3.
- [ ] **Step 5:** Commit `feat(aula02): banco e camada de dados da moeda e da ADR online`.

### Task 2: Jogo da moeda (celular e slide)

**Files:**
- Create: `aulas/aula02-moeda.html` (página do aluno, 390 px de largura útil)
- Create: `assets/js/inteli-moeda.js`, `assets/css/inteli-moeda.css`
- Create: `tools/tests/test_moeda.py`
- Modify: `tools/medidas_aula02.py` (acrescentar `moeda_teorica(rodadas=10) -> dict` com `media = 100 * 1.05**n` e `mediana = 100 * (1.5 * 0.6)**(n/2)`), `tools/tests/test_aula02.py`

**Interfaces:**
- Consumes: Task 1 (`moeda*`, `ouvir`).
- Produces: markup do slide `<div class="moeda-sala" data-moeda data-sessao="m08-aula02-2026-11-05" data-rodadas="10"></div>`; o componente monta QR para `aula02-moeda.html?s=<sessao>` (com `&quiz-demo=1` se o deck estiver em demo), contador de jogadores, rodada atual, botão "Liberar rodada N" (só com chave), histograma de saldos em canvas com média, mediana e linha de R$ 100, e grava `data-pronto="sim"` no elemento quando monta.
  Celular: apelido, depois botão "Jogar rodada N" quando houver rodada liberada não jogada, animação curta de cara ou coroa, saldo em destaque e histórico das rodadas. Identidade em `localStorage['inteli-moeda-<sessao>']`.

- [ ] **Step 1: Testes que falham.** `test_aula02.py::test_moeda_teorica` com `media == pytest.approx(162.89, abs=0.01)` e `mediana == pytest.approx(59.05, abs=0.01)`. `test_moeda.py` (Playwright, `?quiz-demo=1&quiz-chave=teste`, fixture `sala` igual à de `test_quiz_vivo.py`): `test_tres_jogadores_dez_rodadas_e_slide_mostra_media_e_mediana` (slide libera 1 a 10, cada celular joga; o slide mostra 3 jogadores e os valores de média e mediana iguais aos calculados dos saldos lidos dos celulares); `test_saldo_aplica_mais_50_ou_menos_40` (cada saldo do histórico é o anterior vezes 1,5 ou 0,6); `test_atrasado_joga_rodadas_liberadas_em_sequencia` (entra com rodada 4 liberada, joga 1 a 4, slide conta o saldo dele na rodada 4); `test_recarregar_mantem_jogador_e_nao_rejoga` (reload após rodada 2 mostra o mesmo saldo e o botão da rodada 3 só depois de liberada); `test_sem_chave_nao_ha_botao_de_liberar`.
- [ ] **Step 2:** Rodar `pytest tools/tests/test_moeda.py tools/tests/test_aula02.py::test_moeda_teorica -v`: falha.
- [ ] **Step 3:** Implementar. Histograma: faixas fixas em escala log de saldo (R$ 0,60 a R$ 5.800), para não pular a cada rodada.
- [ ] **Step 4:** Testes passam; `check_brand.py` e `check_links.py` passam.
- [ ] **Step 5:** Commit `feat(aula02): jogo da moeda no celular com histograma ao vivo`.

### Task 3: ADR online e decks dos grupos

**Files:**
- Create: `assets/js/inteli-adr.js`, `assets/css/inteli-adr.css`
- Create: `tools/gerar_decks_grupos_aula02.py` (gera `aulas/aula02-g01.html` a `aula02-g04.html`)
- Create: os quatro decks gerados
- Create: `tools/tests/test_adr_grupos.py`

**Interfaces:**
- Consumes: Task 1 (`adr*`, `ouvir`); `inteli-cronometro.js` só como referência visual (o cronômetro do grupo é do `inteli-adr.js`, porque segue o `fim` do servidor).
- Produces:
  - Markup do formulário: `<form class="adr-online" data-adr data-sessao="m08-aula02-2026-11-05" data-grupo="G02">` com `textarea[name=titulo|contexto|criterios|opcoes|decisao|impacto]`; o componente lê `?t=` da URL, mostra o cronômetro sincronizado por `adrAgora` (diferença entre relógio do servidor e local), salva cada campo 800 ms depois da última tecla, aplica mudanças remotas só nos campos sem foco, mostra "editado por outra pessoa" no campo com foco quando o remoto muda, trava tudo com `readonly` depois do `fim`, e tem botão "Baixar ADR em Markdown" no formato de `adr-template-admtech-m08.md` (campos ausentes ficam com a linha do template). Sem token válido: somente leitura e aviso "link sem permissão de edição".
  - Markup do painel do comitê, usado na Task 5: `<div class="adr-comite" data-adr-comite data-sessao="..." data-grupo="G01"></div>` (ADR de um grupo, ao vivo, fonte grande, decisão em destaque) e `<div class="adr-links" data-adr-links data-sessao="..."></div>` (com chave: botão que chama `adrLinks` e mostra as quatro URLs completas com `?t=` e botão copiar; e controle "Iniciar prazo de N min" que chama `adrPrazo`).
  - Gerador: `CONTEUDO = {"G01": {...}, ...}` com afirmação, ativo, ponto de partida no notebook (âncora da seção do grupo) e papel; `gerar() -> dict[caminho, html]`; `main()` grava. Quatro slides por deck, conforme seção 6 da spec. Afirmações exatamente:
    - G01: "O BBAS3 deu prejuízo de 14,7% entre 2019 e 2026."
    - G02: "A MGLU3 caiu 90% desde 2019. Uma alta de 90% devolve o cliente ao zero a zero."
    - G03: "A PETR4 tem volatilidade de 39% ao ano, então o pior que acontece em um ano é perder 39%."
    - G04: "A WEGE3 ganhou da renda fixa no período."
    Os números das afirmações vêm de `medidas_aula02` (Close do BBAS3 arredondado a uma casa, queda da MGLU3 em inteiro, volatilidade anual da PETR4 em inteiro), nunca digitados.

- [ ] **Step 1: Testes que falham** (`test_adr_grupos.py`):
  `test_decks_gerados_estao_atualizados` (`gerar()` igual ao disco);
  `test_afirmacoes_saem_das_medicoes`;
  `test_decks_nao_trazem_veredito` (nenhum deck contém "enganosa" ou "sustentada" fora do rótulo do campo de decisão);
  Playwright em `?quiz-demo=1`: `test_dois_colegas_veem_a_edicao_um_do_outro`; `test_campo_com_foco_nao_e_sobrescrito_e_mostra_aviso`; `test_prazo_encerrado_trava_formulario_e_backend_recusa` (prazo de 0 min pelo `adr-links`, `textarea` com `readonly`, chamada direta a `adrSalvar` rejeita); `test_token_errado_abre_somente_leitura`; `test_markdown_baixado_segue_o_template` (contém `# ADR`, `## Contexto e problema`, `## Decisão` e o texto digitado); `test_painel_comite_mostra_o_texto_ao_vivo`.
- [ ] **Step 2:** Rodar: falha.
- [ ] **Step 3:** Implementar componente, CSS (texto de campo a 22 px ou mais no deck 1280x720) e gerador; rodar o gerador.
- [ ] **Step 4:** Testes passam; `check_slides.py aulas/aula02-g0*.html`, `check_brand.py`, `check_links.py` passam.
- [ ] **Step 5:** Commit `feat(aula02): decks dos quatro grupos com ADR online e prazo sincronizado`.

### Task 4: Notebook da aula e medições públicas

**Files:**
- Modify (reescrever): `notebooks/aula02.ipynb`
- Modify: `tools/medidas_aula02.py` (acrescentar `ponte_bbdc4() -> dict` com `aritmetica`, `geometrica`, `anos` sobre fins de ano 2020 a 2025 de `precos_ajustados.csv` pela regra de `tools/retornos.py`; `afirmacoes_grupos() -> dict` com os números das afirmações), `tools/tests/test_aula02.py`

**Interfaces:**
- Produces: `ponte_bbdc4()["aritmetica"] == approx(0.0481, abs=5e-5)` e `["geometrica"] == approx(-0.0042, abs=5e-5)`; `afirmacoes_grupos()` com `bbas3_close` (-0,147), `mglu3_queda` (0,90), `petr4_vol` (0,39) arredondados como nas afirmações.
- Notebook: badge do Colab, carga com queda para a URL bruta e `M08_OFFLINE`; Parte A (Bloco 2): +5% e -2% com `(1 + r).cumprod()`, jogo da moeda simulado para 10.000 jogadores com `np.random.default_rng(2026)` (média, mediana, fração abaixo de R$ 100), média aritmética contra geométrica e a regra da metade da variância; Parte B: uma seção por grupo com âncora `#g01` a `#g04`, a afirmação, o dado sugerido e células vazias com comentário de partida. Sem nenhum número que responda a afirmação.

- [ ] **Step 1:** Testes `test_ponte_bbdc4` e `test_afirmacoes_grupos` em `test_aula02.py`; em `test_notebooks.py` nada muda (o contrato já cobre). Acrescentar `test_notebook_aula02_tem_secao_por_grupo_sem_veredito` em `test_aula02.py`.
- [ ] **Step 2:** Rodar: falha.
- [ ] **Step 3:** Implementar medições e notebook.
- [ ] **Step 4:** Testes passam e `M08_OFFLINE=1 .venv/bin/python -m nbconvert --to notebook --execute --output-dir /tmp/nb notebooks/aula02.ipynb` termina sem erro.
- [ ] **Step 5:** Commit `feat(aula02): notebook com moeda simulada e seções dos grupos`.

### Task 5: Deck principal

**Files:**
- Modify (reescrever): `aulas/aula02.html`
- Modify (reescrever): `tools/tests/test_deck_aula02.py` (mantém os testes de material e referências, que seguem válidos)
- Delete: `tools/tests/test_praticas_aula02.py` (testava as práticas do deck antigo)
- Modify: `assets/data` e `tools/dados_widgets_aula02.py` só se algum teste de widget passar a falhar; os JSON continuam servindo ao material.

**Interfaces:**
- Consumes: Tasks 2, 3 e 4 (`data-moeda`, `data-adr-links`, `data-adr-comite`, `ponte_bbdc4`, `moeda_teorica`); `inteli-quiz-vivo.js` para os votos (sem `data-correta` nos votos do comitê); `inteli-codigo.js` para o código linha a linha; `inteli-cronometro.js` na daily.
- Sequência de slides (ids fixos, travados no teste): `capa`, `agenda`, `resgate` (a Aula 01 deixou pronto o coletor com Adj Close e a ADR de ausências), `daily`, `vale-jogar` (quiz vivo, 2 rodadas, sem correta), `moeda`, `artigo` (código linha a linha +5% e -2%), `simulacao` (código linha a linha dos 10.000 jogadores, com a turma prevendo a mediana antes), `bodie` (a regra da metade da variância, um exemplo), `ponte` (título "O BBDC4 rendeu 4,81% ao ano na média e quem segurou perdeu 0,42% ao ano"), `comite` (papel do comitê do BTG e regras), `links` (`data-adr-links`), `investigacao` (prazo e roteiro de 20 + 5 min, marco aos 12 min), `comite-g01` a `comite-g04` (ADR ao vivo e voto da sala no quiz vivo, 1 rodada), `a2` (cada veredito vira decisão da função do A2, review em 06/11/2026), `referencias`, `encerramento`.
- Fala e números no `<aside class="notes">` sem veredito.

- [ ] **Step 1: Testes que falham** (`test_deck_aula02.py`): `test_rodapes_numerados_em_sequencia` (mantido); `test_sequencia_de_slides` (ids na ordem acima); `test_ponte_e_moeda_saem_das_medicoes` (`4,81%`, `-0,42%` formatados por `m.pct`; média e mediana teóricas formatadas em reais aparecem nas notas do slide `moeda`); `test_votos_do_comite_nao_tem_correta` (nenhum `data-correta` nas seções `comite-g0N`); `test_deck_nao_traz_veredito_dos_grupos` (nenhuma das palavras "enganosa", "sustentada" ligada a um grupo fora das opções de voto); `test_componentes_novos_declarados` (scripts `inteli-aula02-dados.js`, `inteli-moeda.js`, `inteli-adr.js` e os CSS).
- [ ] **Step 2:** Rodar: falha.
- [ ] **Step 3:** Escrever o deck no molde de `aulas/aula01.html` (mesmo `<head>`, inicialização Reveal e rodapé), com pouco texto e fonte grande.
- [ ] **Step 4:** Testes passam; `check_slides.py aulas/aula02.html`, `check_widgets.py aulas/aula02.html`, `check_brand.py`, `check_links.py` passam. Abrir em `?quiz-demo=1&quiz-chave=teste` e conferir à mão moeda, links e comitê.
- [ ] **Step 5:** Commit `feat(aula02): deck principal com moeda, ponte do BBDC4 e comitê`.

### Task 6: Planejamento, portal, ADR e notas públicas

**Files:**
- Modify: `PLANEJAMENTO_AULA_A_AULA.md` (seção da Aula 02 com os sete blocos da spec, seção 4, no formato que `test_planejamento.py` exige)
- Modify: `index.html` (Slides da Aula 02 volta para `aulas/aula02.html`), `tools/tests/test_portal.py` (remover a exceção do Palco)
- Create: `docs/adrs/ADR-016-aula02-pontos-cegos-com-adr-online.md`; Modify: `docs/adrs/ADR-015-*.md` (Status: Substituída pela ADR-016)
- Modify (reescrever): `docs/notas-do-professor/aula02.md` (logística: ordem dos slides, gerar links, iniciar prazo, plano B; sem números de veredito)
- Modify: `docs/ANDAMENTO.md` (linha da Aula 02)

- [ ] **Step 1:** Atualizar documentos; `test_adrs.py` e `test_planejamento.py` guiam o formato.
- [ ] **Step 2:** `.venv/bin/python -m pytest tools/tests -q` inteiro passa; os quatro validadores passam.
- [ ] **Step 3:** Commit `docs(aula02): planejamento, portal, ADR-016 e notas da aula redesenhada`.

### Task 7: Gabarito privado e varredura de vazamento

**Files (fora do git):**
- Create: `../Inteli - Adm Tech - M08 - LBL/aula02-gabarito/medir_gabarito.py`, `gabarito.md`, `test_gabarito.py`

**Interfaces:**
- `medir_gabarito.py` lê `2026-2B-M08/dados/` e devolve, por grupo, os números que decidem o veredito (lista no próprio script, fora do git).
- `gabarito.md`: veredito, número decisivo, erro comum e pergunta socrática por grupo.
- `test_gabarito.py`: trava os números e `test_nada_do_gabarito_no_repositorio_publico` (varre `aulas/aula02*.html`, `notebooks/aula02.ipynb`, `docs/notas-do-professor/aula02.md`, `tools/*aula02*.py`, `tools/gerar_decks_grupos_aula02.py` procurando cada número formatado com vírgula).

- [ ] **Step 1:** Escrever teste, ver falhar, implementar, ver passar.
- [ ] **Step 2:** Sem commit (pasta não versionada).

### Task 8: Banco em produção, publicação e ensaio

- [ ] **Step 1 (≈ 11h30, autorizado):** aplicar `exemplos/aula02-supabase/aula02.sql` no projeto `tvgwzoalacvcscrmndjs` pela ferramenta de migração do Supabase; conferir com `execute_sql` em transação com `rollback`: `adr_links` com chave errada falha, `moeda_jogar` sem rodada liberada falha, e `get_advisors` sem alerta novo de segurança.
- [ ] **Step 2 (≈ 12h30, autorizado):** `git push origin main`; conferir o workflow `validate.yml` verde e as páginas no Pages: `aulas/aula02.html`, `aulas/aula02-moeda.html`, `aulas/aula02-g01.html`.
- [ ] **Step 3:** Ensaio no endereço real com dois navegadores: gerar links, editar a ADR de dois lados, iniciar prazo de 1 min e ver a trava, jogar três rodadas da moeda. Limpar as linhas do ensaio (`delete` só da sessão de ensaio `m08-aula02-ensaio`; o ensaio usa essa sessão via `?sessao=`, que os três componentes aceitam como sobrescrita de `data-sessao`).
- [ ] **Step 4:** Entregar ao professor os quatro links prontos para o Slack e o lembrete do plano B (13h15).

## Prioridade se o tempo apertar

Tasks 1 e 3 primeiro; depois 5 sem o slide `moeda`; depois 2; 4, 6 e 7 em paralelo ao ensaio.
