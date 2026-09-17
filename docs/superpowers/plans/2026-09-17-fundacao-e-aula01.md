# Fundação do acervo M08 e Aula 01: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Montar a fundação do acervo `josercf/2026-2B-M08` e construir a Aula 01 completa como padrão-ouro das outras cinco.

**Architecture:** Site estático no GitHub Pages, copiado da base do M03 (`canaldoovidio/2026-2A-M03`) com o cronômetro e a escolha da Formação GitLab. Dados reais versionados em `dados/`; medições travadas em pytest; animações MP4 geradas por matplotlib e widgets em JavaScript puro, ambos alimentados só por `dados/`. Validadores de marca, layout, links, widgets e mídia rodam localmente e no CI.

**Tech Stack:** HTML, CSS e JS puros; Reveal.js 5.1.0 por CDN; Python 3 (pandas, numpy, matplotlib, pytest, Playwright, nbconvert); ffmpeg e ffprobe; yfinance só na coleta; GitHub Actions e GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-17-modulo-08-admtech-computacao-design.md`

## Global Constraints

- Português do Brasil com acentuação completa em todo texto, inclusive comentário de código novo e mensagem de commit. Arquivos copiados do M03 mantêm os comentários originais.
- Proibido o caractere travessão U+2014 em qualquer arquivo. Em código, referir-se a ele como `chr(0x2014)`: o escape com barra invertida digitado num parâmetro de ferramenta é convertido no próprio caractere antes de chegar ao arquivo.
- Proibido emoji. Iconografia: Google Material Symbols.
- Cor só por token (`var(--inteli-*)`, `var(--seg-*)`) em HTML, CSS e JS; `tools/check_brand.py` reprova cor literal e `font-family` fora de `assets/css/inteli-brand.css`. Em Python, cor só por `paleta.cor("--token")`.
- Número em deck, material, notas, notebook, widget ou animação vem de `dados/` por código e está travado em teste. Nada digitado de memória.
- Regras de escrita do professor: título de slide analítico é frase completa com o achado e o número dentro; slide de referência tem título descritivo curto; proibido paralelismo negativo ("não é X, é Y"), antítese simétrica, escalada com dois-pontos ("não apenas X: Y") e título de listicle ("Os três erros que..."). Preferir tabela a grade de cartões.
- Data, horário, título, autoestudo ou peso ausente das fontes vira pendência registrada, nunca estimativa. Datas das aulas: "a confirmar na Adalove".
- Repositório: `josercf/2026-2B-M08`. `REPO_BLOB = "https://github.com/josercf/2026-2B-M08/blob/main/"`. URL bruta: `https://raw.githubusercontent.com/josercf/2026-2B-M08/main/`.
- Vídeo: MP4 H.264, `yuv420p`, 1280x720, 30 quadros por segundo, sem áudio, até 60 s e 3 MB, com pôster PNG 1280x720.
- Widget: `<div class="widget" data-widget="nome" data-fonte="../assets/data/arquivo.json">`, script em `assets/js/widgets/nome.js`, `data-pronto="sim"` ao montar.
- Deck: Reveal.js 5.1.0, `width: 1280, height: 720, center: false, margin: 0`.
- Notebook: badge do Colab na primeira célula; carga de dado com queda para a URL bruta; `M08_OFFLINE=1` desliga a rede; sem saída gravada.
- Commits em Conventional Commits, autor `José Romualdo <joseromualdo@outlook.com>` (já configurado no repositório), mensagem terminando com a linha `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- Ambiente local: `.venv` criado com `--system-site-packages`; testes e scripts rodam com `.venv/bin/python`.

## Caminhos usados nos comandos

```bash
REPO=/Users/joseromualdocostafilho/Projects/Inteli/Graduacao/2026.2/AD08-LBL/2026-2B-M08
M03=/Users/joseromualdocostafilho/Projects/Inteli/Graduacao/2026.2/2026-2A-M03
FG=/Users/joseromualdocostafilho/Projects/Inteli/Graduacao/2026.2/FormacaoGitLab
FONTES="/Users/joseromualdocostafilho/Projects/Inteli/Graduacao/2026.2/AD08-LBL/Inteli - Adm Tech - M08 - LBL"
```

Todos os comandos rodam a partir de `$REPO`, salvo indicação.

## Ordem e dependências

| Task | Depende de | Pode rodar em paralelo com |
|---|---|---|
| 1 Base e validadores | nada | 3, 4 |
| 2 Cronômetro e escolha | 1 | 3, 4 |
| 3 Paleta Python | nada | 1, 2, 4 |
| 4 Dados do case | .venv da Task 1 | 2, 3 |
| 5 Contrato de vídeo | 3 | 6 |
| 6 Runtime e validador de widgets | 1, 2, 4 | 5 |
| 7 Documentos de planejamento | nada de código | 5, 6 |
| 8 ADRs, CLAUDE.md, README, ANDAMENTO | 7 | 9 |
| 9 Portal | 1, 7 | 8 |
| 10 Agentes, CI e GitHub | 1 a 9 | nada |
| 11 Medições da Aula 01 | 4 | nada |
| 12 Animações da Aula 01 | 5, 11 | 13, 14 |
| 13 Widgets da Aula 01 | 6, 11 | 12, 14 |
| 14 Notebook da Aula 01 | 11 | 12, 13 |
| 15 Deck da Aula 01 | 12, 13, 14 | nada |
| 16 Material, referências, notas, portal | 15 | nada |

---

## Fase 1: Fundação

### Task 1: Base visual e validadores do M03 no repositório novo

**Files:**
- Create (cópia do M03): `assets/css/inteli-brand.css`, `assets/css/inteli-theme.css`, `assets/css/inteli-print.css`, `assets/css/inteli-material.css`, `assets/js/inteli-quiz.js`, `assets/js/inteli-zoom.js`, `assets/img/inteli-grafismo-graduacao.svg`, `assets/img/inteli-logo-mono.svg`, `assets/img/inteli-logo-negativa.svg`, `assets/img/inteli-logo-positiva.svg`, `aulas/_fixture-tema.html`, `tools/check_brand.py`, `tools/check_slides.py`, `tools/check_links.py`, `tools/tests/__init__.py`, `tools/tests/fixture_layout.html`, `tools/tests/fixture_sem_slides.html`, `tools/tests/test_assets_marca.py`, `tools/tests/test_check_brand.py`, `tools/tests/test_check_links.py`, `tools/tests/test_check_slides.py`, `pytest.ini`
- Create: `tools/tests/test_repo_m08.py`
- Modify: `.gitignore`, `tools/check_links.py`, `tools/check_brand.py`, `aulas/_fixture-tema.html`

**Interfaces:**
- Produces: `check_slides.porta_livre() -> int`; `check_slides.servir(porta) -> socketserver.TCPServer` (serve a raiz do repositório); `check_links.REPO_BLOB: str`; `check_links.IGNORAR: set`; `check_brand.IGNORAR: set`; `check_brand.varrer(raiz) -> list[dict]`.

- [ ] **Step 1: Criar o ambiente virtual**

```bash
cd $REPO
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -q yfinance httpx
.venv/bin/python -c "import yfinance, httpx, pandas, matplotlib, pytest, playwright, nbconvert; print('ambiente ok')"
.venv/bin/python -m playwright install chromium
```

Expected: `ambiente ok`.

- [ ] **Step 2: Substituir o `.gitignore`**

Conteúdo completo de `.gitignore`:

```gitignore
.DS_Store
__pycache__/
*.pyc
.ipynb_checkpoints/
.pytest_cache/
.venv/

# Planilhas exportadas da Adalove e da alocação de professores têm dado pessoal
# de aluno e de professor, e o repositório é publicado inteiro no GitHub Pages.
*.xlsx
*.xls

# A chave da OpenRouter da Aula 06 vive em variável de ambiente, nunca no git.
.env
.env.*

# Enunciado, tabela por RA e barema das ponderadas vivem na Adalove.
Ponderada*
ponderada*

# Saídas de execução dos notebooks.
saida/
```

- [ ] **Step 3: Escrever o teste que falha**

`tools/tests/test_repo_m08.py`:

```python
"""Adaptações da base do M03 para o repositório do M08."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_brand  # noqa: E402
import check_links  # noqa: E402


def test_link_do_notebook_aponta_para_o_repositorio_do_m08():
    assert check_links.REPO_BLOB == "https://github.com/josercf/2026-2B-M08/blob/main/"


def test_validadores_ignoram_ambiente_virtual_e_worktrees():
    for pasta in (".venv", ".claude"):
        assert pasta in check_brand.IGNORAR, pasta
        assert pasta in check_links.IGNORAR, pasta
```

- [ ] **Step 4: Copiar a base do M03**

```bash
cd $REPO
mkdir -p assets/css assets/js assets/img aulas tools/tests
cp $M03/assets/css/inteli-brand.css $M03/assets/css/inteli-theme.css $M03/assets/css/inteli-print.css $M03/assets/css/inteli-material.css assets/css/
cp $M03/assets/js/inteli-quiz.js $M03/assets/js/inteli-zoom.js assets/js/
cp $M03/assets/img/inteli-grafismo-graduacao.svg $M03/assets/img/inteli-logo-mono.svg $M03/assets/img/inteli-logo-negativa.svg $M03/assets/img/inteli-logo-positiva.svg assets/img/
cp $M03/aulas/_fixture-tema.html aulas/
cp $M03/tools/check_brand.py $M03/tools/check_slides.py $M03/tools/check_links.py tools/
cp $M03/tools/tests/__init__.py $M03/tools/tests/fixture_layout.html $M03/tools/tests/fixture_sem_slides.html $M03/tools/tests/test_assets_marca.py $M03/tools/tests/test_check_brand.py $M03/tools/tests/test_check_links.py $M03/tools/tests/test_check_slides.py tools/tests/
cp $M03/pytest.ini .
```

`assets/css/inteli-portal.css` e `assets/js/inteli-print.js` não vêm do M03: a Task 2 copia as versões da Formação GitLab.

- [ ] **Step 5: Rodar o teste novo e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_repo_m08.py -v`
Expected: FAIL nos dois testes (`REPO_BLOB` ainda aponta para `canaldoovidio/2026-2A-M03`; `.venv` ausente de `IGNORAR`).

- [ ] **Step 6: Adaptar os validadores e o fixture**

```bash
cd $REPO
.venv/bin/python - <<'EOF'
import re
def trocar(caminho, velho, novo):
    texto = open(caminho, encoding="utf-8").read()
    assert velho in texto, (caminho, velho)
    open(caminho, "w", encoding="utf-8").write(texto.replace(velho, novo))

trocar("tools/check_links.py",
       'REPO_BLOB = "https://github.com/canaldoovidio/2026-2A-M03/blob/main/"',
       'REPO_BLOB = "https://github.com/josercf/2026-2B-M08/blob/main/"')
trocar("tools/check_links.py",
       'IGNORAR = {".git", "node_modules", "__pycache__", ".ipynb_checkpoints"}',
       'IGNORAR = {".git", ".claude", ".venv", "node_modules", "__pycache__", ".ipynb_checkpoints"}')
trocar("tools/check_brand.py",
       'IGNORAR = {".git", ".claude", "node_modules", "__pycache__", ".ipynb_checkpoints"}',
       'IGNORAR = {".git", ".claude", ".venv", "node_modules", "__pycache__", ".ipynb_checkpoints"}')
trocar("aulas/_fixture-tema.html", "Módulo 03 IN &middot; Graduação", "Módulo 08 AdmTech &middot; Graduação")
texto = open("aulas/_fixture-tema.html", encoding="utf-8").read()
texto = texto.replace("Módulo 03 IN &middot; Aula 01", "Módulo 08 AdmTech &middot; Fixture do tema")
open("aulas/_fixture-tema.html", "w", encoding="utf-8").write(texto)
assert "03 IN" not in texto
print("adaptado")
EOF
```

Expected: `adaptado`.

- [ ] **Step 7: Rodar a suíte e os três validadores**

```bash
.venv/bin/python -m pytest tools/tests -v
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html
```

Expected: pytest todo verde; `Brandbook: paleta, tipografia, segmento e iconografia conferem.`; `Links: todos os alvos locais existem.`; `Todos os slides cabem em 1280x720, sem bloco sobreposto.`

- [ ] **Step 8: Commit**

```bash
git add .gitignore pytest.ini assets aulas tools
git commit -m "feat(base): tema, marca e validadores do M03 adaptados ao repositório do M08

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Cronômetro e escolha da Formação GitLab no tema

**Files:**
- Create (cópia da Formação GitLab): `assets/js/inteli-cronometro.js`, `assets/js/inteli-escolha.js`, `assets/js/inteli-print.js`, `assets/css/inteli-portal.css`
- Create: `tools/tests/test_componentes_ativos.py`
- Modify: `assets/css/inteli-theme.css` (anexar blocos), `aulas/_fixture-tema.html` (dois slides e dois scripts)

**Interfaces:**
- Consumes: `check_slides.porta_livre`, `check_slides.servir` (Task 1).
- Produces: markup `<div class="slide-title-area slide-title-area-cronometro">` com `<div class="cronometro" data-minutos="N">`; markup `.escolha-grid > .escolha > .escolha-item + ul.escolha-opcoes > li[data-correct]`; `window.IntelIEscolha.responder(escolha, opcao)`; slides do fixture com `id="cronometro"` e `id="escolha"`.

Por que a versão da Formação GitLab: `inteli-print.js` dela revela também o gabarito das escolhas no PDF, e `inteli-portal.css` dela troca `--seg-texto-suave` (2,04:1 de contraste) por `--seg-texto` em três pontos. Nos demais arquivos o M03 é mais recente.

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_componentes_ativos.py`:

```python
"""Estado depois da interação do cronômetro e da escolha, medido no navegador.

O check_slides.py mede o deck sem clicar em nada (inteli-deck-design, seção 8.4).
Este teste clica e compara getComputedStyle, porque classe de estado que perde
na especificidade muda o DOM e não muda a tela (seção 8.1).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def deck():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    with sync_api.sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1280, "height": 720})
        try:
            yield page, "http://127.0.0.1:%d/aulas/_fixture-tema.html" % porta
        finally:
            navegador.close()
    httpd.shutdown()


def _ir(deck, slide):
    # A query string força documento novo: sem ela, trocar só o hash mantém o
    # estado da interação do teste anterior.
    page, url = deck
    page.goto("%s?teste=%s#/%s" % (url, slide, slide), wait_until="load")
    page.wait_for_selector("section#%s.present" % slide)
    return page


def test_cronometro_conta_ate_zero_e_marca_esgotado(deck):
    page = _ir(deck, "cronometro")
    tempo = "#cronometro-fixture .cronometro-tempo"
    page.wait_for_selector(tempo)
    assert page.inner_text(tempo) == "00:03"
    page.click("#cronometro-fixture .cronometro-play")
    page.wait_for_function(
        "() => document.querySelector('#cronometro-fixture').classList.contains('esgotado')",
        timeout=8000,
    )
    assert page.inner_text(tempo) == "00:00"
    borda = page.eval_on_selector("#cronometro-fixture", "e => getComputedStyle(e).borderTopColor")
    assert borda == "rgb(255, 69, 69)"  # --seg-destaque


def test_escolha_errada_marca_a_errada_e_revela_a_certa(deck):
    page = _ir(deck, "escolha")
    opcoes = "#escolha-fixture .escolha-opcoes li"
    repouso = page.eval_on_selector(opcoes + ":nth-child(3)", "e => getComputedStyle(e).backgroundColor")
    page.click(opcoes + ":nth-child(1)")
    classes = page.eval_on_selector_all(opcoes, "els => els.map(e => e.className)")
    assert "errada" in classes[0]
    assert "revelada" in classes[2]
    revelada = page.eval_on_selector(opcoes + ":nth-child(3)", "e => getComputedStyle(e).backgroundColor")
    assert revelada != repouso


def test_escolha_certa_pinta_a_opcao(deck):
    page = _ir(deck, "escolha")
    opcoes = "#escolha-fixture-certa .escolha-opcoes li"
    repouso = page.eval_on_selector(opcoes + ":nth-child(2)", "e => getComputedStyle(e).backgroundColor")
    page.click(opcoes + ":nth-child(1)")
    assert "certa" in page.eval_on_selector(opcoes + ":nth-child(1)", "e => e.className")
    certa = page.eval_on_selector(opcoes + ":nth-child(1)", "e => getComputedStyle(e).backgroundColor")
    assert certa != repouso
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_componentes_ativos.py -v`
Expected: FAIL nos três (timeout em `section#cronometro.present`).

- [ ] **Step 3: Copiar os componentes e anexar o CSS**

```bash
cd $REPO
cp $FG/assets/js/inteli-cronometro.js $FG/assets/js/inteli-escolha.js $FG/assets/js/inteli-print.js assets/js/
cp $FG/assets/css/inteli-portal.css assets/css/
{
  printf '\n/* ==========================================================================\n'
  printf '   Componentes de metodologia ativa portados da Formação GitLab\n'
  printf '   (josercf/treinamento-gitlab) em 17/09/2026: cronômetro e escolha.\n'
  printf '   ========================================================================== */\n\n'
  awk '/Cronometro de atividade cronometrada/{p=1} /Caixa do prompt que a sala copia/{p=0} p' $FG/assets/css/inteli-theme.css
} >> assets/css/inteli-theme.css
grep -c "escolha-opcoes li.revelada" assets/css/inteli-theme.css
```

Expected: `1`.

- [ ] **Step 4: Acrescentar os dois slides e os scripts ao fixture**

Inserir antes de `<section class="end-slide">` em `aulas/_fixture-tema.html`:

```html
      <section class="content-slide" id="cronometro">
        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-positiva.svg" alt="Logo Inteli">
        <div class="slide-title-area slide-title-area-cronometro">
          <div>
            <div class="accent-bar"></div>
            <h2>Cronômetro de atividade</h2>
          </div>
          <div class="cronometro" id="cronometro-fixture" data-minutos="0.05"></div>
        </div>
        <p>O cronômetro mora dentro da faixa do título. Neste fixture ele tem três segundos, para
        <code>tools/tests/test_componentes_ativos.py</code> ver o estado esgotado sem esperar.</p>
        <div class="slide-footer">
          <p class="footer-bar">Módulo 08 AdmTech &middot; Fixture do tema</p>
          <p class="footer-page">6</p>
        </div>
      </section>

      <section class="content-slide" id="escolha">
        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-positiva.svg" alt="Logo Inteli">
        <div class="slide-title-area">
          <div class="accent-bar"></div>
          <h2>Classificação coletiva</h2>
        </div>
        <div class="escolha-grid">
          <div class="escolha" id="escolha-fixture">
            <p class="escolha-item">1. Volatilidade anual para o otimizador</p>
            <ul class="escolha-opcoes">
              <li>Negociado</li>
              <li>Close</li>
              <li data-correct="true">Adj Close</li>
            </ul>
          </div>
          <div class="escolha" id="escolha-fixture-certa">
            <p class="escolha-item">2. Preço exibido no pregão daquele dia</p>
            <ul class="escolha-opcoes">
              <li data-correct="true">Negociado</li>
              <li>Close</li>
              <li>Adj Close</li>
            </ul>
          </div>
        </div>
        <div class="slide-footer">
          <p class="footer-bar">Módulo 08 AdmTech &middot; Fixture do tema</p>
          <p class="footer-page">7</p>
        </div>
      </section>
```

Acrescentar depois de `<script src="../assets/js/inteli-print.js"></script>`:

```html
  <script src="../assets/js/inteli-cronometro.js"></script>
  <script src="../assets/js/inteli-escolha.js"></script>
```

- [ ] **Step 5: Rodar o teste e os validadores**

```bash
.venv/bin/python -m pytest tools/tests/test_componentes_ativos.py -v
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
```

Expected: 3 passed; os três validadores limpos.

- [ ] **Step 6: Provar que o teste de especificidade falha contra o bug**

```bash
cp assets/css/inteli-theme.css /tmp/tema-backup.css
sed -i '' 's/^\.escolha-opcoes li\.revelada {/.revelada {/' assets/css/inteli-theme.css
.venv/bin/python -m pytest tools/tests/test_componentes_ativos.py::test_escolha_errada_marca_a_errada_e_revela_a_certa -v
cp /tmp/tema-backup.css assets/css/inteli-theme.css
.venv/bin/python -m pytest tools/tests/test_componentes_ativos.py -v
```

Expected: a primeira execução FALHA em `assert revelada != repouso`; depois de restaurar, 3 passed. Registrar no relatório da task que a mutação foi vista falhando.

- [ ] **Step 7: Commit**

```bash
git add assets/js assets/css aulas/_fixture-tema.html tools/tests/test_componentes_ativos.py
git commit -m "feat(tema): cronômetro e escolha da Formação GitLab, com estado pós-clique testado

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Paleta dos tokens para scripts Python

**Files:**
- Create: `tools/paleta.py`, `tools/tests/test_paleta.py`

**Interfaces:**
- Produces: `paleta.tokens(caminho=BRAND) -> dict[str, str]` (token para valor final, `var()` resolvido); `paleta.cor(nome, caminho=BRAND) -> str` (hex em minúsculas; `KeyError` se o token não existe, `ValueError` se não é cor hex).

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_paleta.py`:

```python
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paleta import cor, tokens  # noqa: E402


def test_token_da_paleta_devolve_o_hex_oficial():
    assert cor("--inteli-roxo") == "#2e2640"
    assert cor("--inteli-coral") == "#ff4545"


def test_token_de_segmento_resolve_var():
    assert cor("--seg-primaria") == "#2e2640"
    assert cor("--seg-secundaria") == "#89cea5"
    assert cor("--seg-destaque") == "#ff4545"
    assert cor("--seg-base") == "#ffffff"


def test_cor_de_outro_segmento_nao_existe_no_acervo():
    with pytest.raises(KeyError):
        cor("--inteli-lilas")


def test_token_que_nao_e_cor_e_recusado():
    with pytest.raises(ValueError):
        cor("--escala-texto")


def test_referencia_circular_e_recusada(tmp_path):
    css = tmp_path / "brand.css"
    css.write_text(":root { --a: var(--b); --b: var(--a); }", encoding="utf-8")
    with pytest.raises(ValueError):
        tokens(str(css))


def test_comentario_nao_vira_token(tmp_path):
    css = tmp_path / "brand.css"
    css.write_text("/* --falso: #000000; */ :root { --verdadeiro: #ffffff; }", encoding="utf-8")
    assert tokens(str(css)) == {"--verdadeiro": "#ffffff"}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_paleta.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'paleta'`.

- [ ] **Step 3: Implementar**

`tools/paleta.py`:

```python
"""Tokens de cor de assets/css/inteli-brand.css, para scripts Python.

Figuras e animações do acervo não declaram hex: pedem o token pelo nome, por
exemplo cor("--seg-primaria"). A paleta tem uma fonte só, a mesma que o tema do
deck consome e que o tools/check_brand.py protege.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(RAIZ, "assets", "css", "inteli-brand.css")

_COMENTARIO = re.compile(r"/\*.*?\*/", re.S)
_DECLARACAO = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
_VAR = re.compile(r"var\((--[a-z0-9-]+)\)")
_HEX = re.compile(r"#[0-9a-fA-F]{6}")


def tokens(caminho=BRAND):
    """Dicionário token -> valor final, com var(--outro) resolvido."""
    with open(caminho, encoding="utf-8") as fh:
        texto = _COMENTARIO.sub("", fh.read())
    brutos = {nome: valor.strip() for nome, valor in _DECLARACAO.findall(texto)}

    def resolver(nome, trilha):
        if nome in trilha:
            raise ValueError("referência circular: %s" % " -> ".join(trilha + (nome,)))
        valor = brutos[nome]
        referencia = _VAR.fullmatch(valor)
        return resolver(referencia.group(1), trilha + (nome,)) if referencia else valor

    return {nome: resolver(nome, ()) for nome in brutos}


def cor(nome, caminho=BRAND):
    """Hex de um token de cor, em minúsculas: cor("--seg-primaria") -> "#2e2640"."""
    valor = tokens(caminho)[nome]
    if not _HEX.fullmatch(valor):
        raise ValueError("%s não é cor hex: %r" % (nome, valor))
    return valor.lower()
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_paleta.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/paleta.py tools/tests/test_paleta.py
git commit -m "feat(tools): paleta lida dos tokens da marca para scripts Python

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 4: Dados do case versionados e travados

**Files:**
- Create: `tools/baixar_dados.py`, `tools/tests/test_dados.py`, `dados/README.md`
- Create (gerados): `dados/precos_ajustados.csv`, `dados/precos_fechamento.csv`, `dados/eventos_desdobramento.csv`, `dados/eventos_proventos.csv`, `dados/cdi_diario.csv`, `dados/selic_meta.csv`, `dados/ipca_mensal.csv`, `dados/ptax_venda.csv`

**Interfaces:**
- Produces: os oito CSVs com o contrato abaixo, consumidos por todas as tasks seguintes.
  - Preços: `data` (AAAA-MM-DD) e uma coluna por ticker, na ordem `PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3, WEGE3, EGIE3, SUZB3, RENT3, B3SA3, MGLU3, BOVA11, IVVB11, GOLD11`; célula vazia é ausência.
  - Eventos: `ticker, data, fator` e `ticker, data, valor`.
  - Banco Central: `data, valor`.

Os valores travados nos testes foram medidos num ensaio de 17/09/2026 com o mesmo código, yfinance 1.7.0. Se a coleta real divergir, o provedor mudou o histórico: investigar e registrar em `dados/README.md` antes de mexer em número de teste.

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_dados.py`:

```python
"""Trava o contrato e os fatos medidos dos dados do case em dados/."""
import csv
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "dados")
TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3",
           "SUZB3", "RENT3", "B3SA3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"]
PRECOS = ["precos_ajustados.csv", "precos_fechamento.csv"]
# arquivo: (linhas, primeira data, primeiro valor, última data, último valor)
SERIES_BCB = {
    "cdi_diario.csv": (1926, "2019-01-02", 0.02462, "2026-08-31", 0.05166),
    "selic_meta.csv": (2800, "2019-01-01", 6.5, "2026-08-31", 14.0),
    "ipca_mensal.csv": (92, "2019-01-01", 0.32, "2026-08-01", -0.32),
    "ptax_venda.csv": (1926, "2019-01-02", 3.8595, "2026-08-31", 5.1816),
}


def _ler(nome):
    with open(os.path.join(DADOS, nome), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("arquivo", PRECOS)
def test_precos_seguem_o_contrato_e_a_janela(arquivo):
    linhas = _ler(arquivo)
    assert list(linhas[0].keys()) == ["data"] + TICKERS
    datas = [linha["data"] for linha in linhas]
    assert len(datas) == 1908
    assert (datas[0], datas[-1]) == ("2019-01-02", "2026-08-31")
    assert datas == sorted(set(datas))


def test_as_duas_tabelas_de_preco_tem_as_mesmas_datas():
    assert [l["data"] for l in _ler(PRECOS[0])] == [l["data"] for l in _ler(PRECOS[1])]


@pytest.mark.parametrize("arquivo", PRECOS)
def test_todo_preco_presente_e_positivo(arquivo):
    for linha in _ler(arquivo):
        for ticker in TICKERS:
            if linha[ticker] != "":
                assert float(linha[ticker]) > 0, (arquivo, linha["data"], ticker)


def test_ausencias_reais_do_provedor():
    linhas = _ler("precos_fechamento.csv")
    vazios = {t: [l["data"] for l in linhas if l[t] == ""] for t in TICKERS}
    assert {t: len(v) for t, v in vazios.items() if v} == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}
    assert vazios["BOVA11"] == ["2025-10-24"]
    assert vazios["IVVB11"] == ["2025-10-24"]
    assert vazios["GOLD11"][-1] == "2025-10-24"
    assert vazios["GOLD11"][-2] < "2020-12-11"
    assert next(l["data"] for l in linhas if l["GOLD11"] != "") == "2020-12-11"


def test_ausencia_e_igual_nas_duas_tabelas():
    ajustado, fechamento = _ler(PRECOS[0]), _ler(PRECOS[1])
    for ticker in TICKERS:
        assert ([l["data"] for l in ajustado if l[ticker] == ""]
                == [l["data"] for l in fechamento if l[ticker] == ""]), ticker


def test_adj_close_da_petr4_desconta_proventos():
    ajustado, fechamento = _ler(PRECOS[0])[0], _ler(PRECOS[1])[0]
    assert round(float(ajustado["PETR4"]) / float(fechamento["PETR4"]), 4) == 0.2613
    for etf in ("BOVA11", "IVVB11"):
        assert float(ajustado[etf]) == pytest.approx(float(fechamento[etf]), rel=1e-9)


def test_eventos_de_desdobramento_do_periodo():
    linhas = _ler("eventos_desdobramento.csv")
    assert list(linhas[0].keys()) == ["ticker", "data", "fator"]
    eventos = {(l["ticker"], l["data"]): float(l["fator"]) for l in linhas}
    assert len(eventos) == 15
    assert eventos[("B3SA3", "2021-05-17")] == 3.0
    assert eventos[("WEGE3", "2021-04-28")] == 2.0
    assert eventos[("BBAS3", "2024-04-16")] == 2.0
    assert eventos[("MGLU3", "2024-05-27")] == pytest.approx(0.1)


def test_proventos_tem_contrato_e_volume_medido():
    linhas = _ler("eventos_proventos.csv")
    assert list(linhas[0].keys()) == ["ticker", "data", "valor"]
    assert len(linhas) == 499
    assert all(l["ticker"] in TICKERS and float(l["valor"]) > 0 for l in linhas)


@pytest.mark.parametrize("arquivo", sorted(SERIES_BCB))
def test_series_do_banco_central(arquivo):
    n, d0, v0, d1, v1 = SERIES_BCB[arquivo]
    linhas = _ler(arquivo)
    assert list(linhas[0].keys()) == ["data", "valor"]
    datas = [linha["data"] for linha in linhas]
    assert datas == sorted(set(datas))
    assert len(linhas) == n
    assert (datas[0], datas[-1]) == (d0, d1)
    assert float(linhas[0]["valor"]) == pytest.approx(v0)
    assert float(linhas[-1]["valor"]) == pytest.approx(v1)


def test_readme_documenta_cada_arquivo():
    with open(os.path.join(DADOS, "README.md"), encoding="utf-8") as fh:
        texto = fh.read()
    for nome in sorted(os.listdir(DADOS)):
        if nome.endswith(".csv"):
            assert nome in texto, nome
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_dados.py -v`
Expected: FAIL com `FileNotFoundError` em `dados/`.

- [ ] **Step 3: Implementar o coletor**

`tools/baixar_dados.py`:

```python
#!/usr/bin/env python3
"""
Baixa os dados do case para dados/: preços e eventos corporativos da cesta de
referência (Yahoo Finance, pelo yfinance) e quatro séries do Banco Central (SGS).

Precisa de rede e do yfinance, que fica fora da stack de validação: rodar com
.venv/bin/python. Notebooks e testes nunca chamam este script, eles leem os CSVs
versionados. Rodar de novo só quando a janela mudar, e atualizar a data da
coleta em dados/README.md.

Uso:
    .venv/bin/python tools/baixar_dados.py
"""
import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")

INICIO = "2019-01-01"
FIM = "2026-08-31"
TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3",
           "SUZB3", "RENT3", "B3SA3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"]
SERIES_BCB = {"cdi_diario": 12, "selic_meta": 432, "ipca_mensal": 433, "ptax_venda": 1}
URL_SGS = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
           "?formato=json&dataInicial={inicio}&dataFinal={fim}")


def _gravar(arquivo, cabecalho, linhas):
    with open(os.path.join(DADOS, arquivo), "w", newline="", encoding="utf-8") as fh:
        escritor = csv.writer(fh)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def _data_br(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def baixar_precos():
    import yfinance as yf

    # O yfinance trata "end" como exclusivo: pedir o dia seguinte ao FIM.
    fim_exclusivo = (datetime.strptime(FIM, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    bruto = yf.download([t + ".SA" for t in TICKERS], start=INICIO, end=fim_exclusivo,
                        auto_adjust=False, progress=False, group_by="column", threads=False)
    for coluna, arquivo in (("Adj Close", "precos_ajustados.csv"), ("Close", "precos_fechamento.csv")):
        tabela = bruto[coluna].copy()
        tabela.columns = [c.removesuffix(".SA") for c in tabela.columns]
        tabela = tabela[TICKERS].dropna(how="all")
        tabela.index = tabela.index.strftime("%Y-%m-%d")
        tabela.index.name = "data"
        tabela.to_csv(os.path.join(DADOS, arquivo), float_format="%.6f")


def baixar_eventos():
    import yfinance as yf

    desdobramentos, proventos = [], []
    for ticker in TICKERS:
        ativo = yf.Ticker(ticker + ".SA")
        for serie, destino in ((ativo.splits, desdobramentos), (ativo.dividends, proventos)):
            for quando, valor in serie.items():
                dia = quando.strftime("%Y-%m-%d")
                if INICIO <= dia <= FIM:
                    destino.append((ticker, dia, round(float(valor), 8)))
    _gravar("eventos_desdobramento.csv", ["ticker", "data", "fator"],
            sorted(desdobramentos, key=lambda r: (r[1], r[0])))
    _gravar("eventos_proventos.csv", ["ticker", "data", "valor"],
            sorted(proventos, key=lambda r: (r[1], r[0])))


def baixar_bcb():
    for nome, codigo in SERIES_BCB.items():
        url = URL_SGS.format(codigo=codigo, inicio=_data_br(INICIO), fim=_data_br(FIM))
        pedido = urllib.request.Request(url, headers={"User-Agent": "acervo-2026-2B-M08"})
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            registros = json.load(resposta)
        linhas = [(datetime.strptime(r["data"], "%d/%m/%Y").strftime("%Y-%m-%d"), r["valor"])
                  for r in registros]
        _gravar(nome + ".csv", ["data", "valor"], linhas)


def main():
    os.makedirs(DADOS, exist_ok=True)
    baixar_precos()
    baixar_eventos()
    baixar_bcb()
    for nome in sorted(os.listdir(DADOS)):
        if nome.endswith(".csv"):
            with open(os.path.join(DADOS, nome), encoding="utf-8") as fh:
                print("%-28s %5d linhas" % (nome, sum(1 for _ in fh) - 1))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Coletar**

Run: `.venv/bin/python tools/baixar_dados.py`
Expected, linha a linha: `cdi_diario.csv 1926`, `eventos_desdobramento.csv 15`, `eventos_proventos.csv 499`, `ipca_mensal.csv 92`, `precos_ajustados.csv 1908`, `precos_fechamento.csv 1908`, `ptax_venda.csv 1926`, `selic_meta.csv 2800`.

- [ ] **Step 5: Escrever `dados/README.md`**

Seções obrigatórias, nesta ordem, com os números abaixo (todos medidos):

1. **O que é esta pasta.** Snapshot do case, coletado em 17/09/2026 por `tools/baixar_dados.py`, janela de 02/01/2019 a 31/08/2026. Notebooks e testes leem só daqui.
2. **Arquivos.** Tabela com os oito CSVs: conteúdo, fonte (Yahoo Finance via yfinance 1.7.0; BCB SGS séries 12, 432, 433 e 1, com link `https://dadosabertos.bcb.gov.br/dataset/<código>` conferido antes de publicar), linhas e contrato de colunas.
3. **A cesta de referência.** Os 15 tickers, com o motivo de cada grupo (bancos do mesmo setor, exportadoras sensíveis ao câmbio, ETFs de índice, de S&P 500 em reais e de ouro).
4. **Três visões de preço.** `Close` do Yahoo já dividido pelos fatores de desdobramento; `Adj Close` desconta também proventos; o preço negociado na data é reconstruído multiplicando o `Close` pelos fatores dos eventos posteriores. Exemplo medido: no primeiro pregão da janela, o `Adj Close` da PETR4 vale 26,13% do `Close`.
5. **Falhas reais do provedor.** BOVA11, IVVB11 e GOLD11 sem cotação em 24/10/2025; GOLD11 com 484 pregões vazios antes de 11/12/2020.
6. **Eventos corporativos.** Os 15 eventos do período; fator menor que 1 é grupamento; fator inteiro maior que 1 é desdobramento; fator fracionário maior que 1 é tratado como bonificação em ações, classificação inferida do fator e não informada pelo provedor.
7. **Como regenerar.** Comando, necessidade de rede e do yfinance, e a regra de investigar antes de alterar número de teste.
8. **Termos de uso.** Os termos do Yahoo restringem redistribuição; o snapshot é pequeno, educacional e atribuído; a troca pelas séries históricas da B3 (COTAHIST) é a mitigação registrada na ADR-003.

- [ ] **Step 6: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_dados.py -v`
Expected: todos passam. Se algum valor divergir, parar e reportar a divergência com o valor obtido, sem editar o teste.

- [ ] **Step 7: Commit**

```bash
git add tools/baixar_dados.py tools/tests/test_dados.py dados
git commit -m "feat(dados): cesta de 15 ativos da B3 e quatro séries do Banco Central, com fatos travados

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Contrato de vídeo e gerador de animações

**Files:**
- Create: `tools/midia.py`, `tools/tests/test_midia.py`

**Interfaces:**
- Consumes: `paleta.cor` (Task 3).
- Produces: `midia.LARGURA=1280`, `midia.ALTURA=720`, `midia.FPS=30`, `midia.VIDEO` (caminho de `assets/video`), `midia.IMG` (caminho de `assets/img`); `midia.figura() -> matplotlib.figure.Figure` (1280x720, tema aplicado); `midia.gravar(fig, desenhar, n_quadros, nome, quadro_poster) -> (mp4, poster)` onde `desenhar(i)` atualiza a figura para o quadro `i` e os arquivos saem em `assets/video/<nome>.mp4` e `assets/img/<nome>-poster.png`; `midia.metadados(caminho) -> dict` com `codec, largura, altura, pix_fmt, fps, duracao, bytes, tem_audio`; `midia.violacoes(meta) -> list[str]` (vazia quando conforme).

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_midia.py`:

```python
"""Contrato das animações: arquivo, pôster, codec, tamanho, duração e uso.

Mede por ffprobe, sem tocar o vídeo: o Chromium do Playwright não tem H.264.
"""
import glob
import os
import re
import struct
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import midia  # noqa: E402

PAGINAS = sorted(glob.glob(os.path.join(midia.RAIZ, "aulas", "*.html"))
                 + glob.glob(os.path.join(midia.RAIZ, "materiais", "*.html")))
TAG_VIDEO = re.compile(r"<video\b.*?</video>", re.S)
SRC = re.compile(r'\bsrc\s*=\s*"([^"]+)"')
POSTER = re.compile(r'\bposter\s*=\s*"([^"]+)"')


def _tags():
    for pagina in PAGINAS:
        with open(pagina, encoding="utf-8") as fh:
            for tag in TAG_VIDEO.findall(fh.read()):
                yield pagina, tag


def _resolver(pagina, alvo):
    return os.path.normpath(os.path.join(os.path.dirname(pagina), alvo))


def _dimensoes_png(caminho):
    with open(caminho, "rb") as fh:
        cabecalho = fh.read(24)
    assert cabecalho[:8] == b"\x89PNG\r\n\x1a\n", "%s não é PNG" % caminho
    return struct.unpack(">II", cabecalho[16:24])


TAGS = list(_tags())
VIDEOS = sorted(glob.glob(os.path.join(midia.VIDEO, "*.mp4")))


@pytest.mark.parametrize("pagina,tag", TAGS,
                         ids=["%s-%d" % (os.path.basename(p), i) for i, (p, _) in enumerate(TAGS)])
def test_video_referenciado_existe_tem_poster_e_atributos(pagina, tag):
    fontes = SRC.findall(tag)
    assert fontes, "<video> sem <source src> em %s" % pagina
    for fonte in fontes:
        assert os.path.isfile(_resolver(pagina, fonte)), fonte
    posters = POSTER.findall(tag)
    assert posters, "<video> sem poster em %s" % pagina
    assert _dimensoes_png(_resolver(pagina, posters[0])) == (midia.LARGURA, midia.ALTURA)
    abertura = tag.split(">", 1)[0]
    for atributo in ("controls", "muted", "playsinline"):
        assert re.search(r"\b%s\b" % atributo, abertura), atributo


@pytest.mark.parametrize("video", VIDEOS, ids=os.path.basename)
def test_video_cumpre_o_contrato(video):
    assert midia.violacoes(midia.metadados(video)) == []


@pytest.mark.parametrize("video", VIDEOS, ids=os.path.basename)
def test_video_nao_esta_orfao(video):
    usados = {_resolver(p, s) for p, t in TAGS for s in SRC.findall(t)}
    assert os.path.normpath(video) in usados, "nenhuma página usa %s" % video


def test_gravar_produz_video_conforme(tmp_path, monkeypatch):
    monkeypatch.setattr(midia, "VIDEO", str(tmp_path))
    monkeypatch.setattr(midia, "IMG", str(tmp_path))
    fig = midia.figura()
    eixo = fig.add_subplot()
    eixo.set_xlim(0, 30)
    eixo.set_ylim(0, 30)
    ponto, = eixo.plot([0], [0], "o")

    def desenhar(i):
        ponto.set_data([i], [i])

    mp4, poster = midia.gravar(fig, desenhar, 30, "ensaio", 29)
    assert midia.violacoes(midia.metadados(mp4)) == []
    assert _dimensoes_png(poster) == (1280, 720)


def test_violacoes_acusa_video_fora_do_contrato(tmp_path):
    saida = str(tmp_path / "fora.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
                    "-f", "lavfi", "-i", "sine=frequency=440", "-t", "1",
                    "-c:v", "libx264", "-pix_fmt", "yuv444p", "-c:a", "aac", saida], check=True)
    erros = " | ".join(midia.violacoes(midia.metadados(saida)))
    for trecho in ("640x360", "yuv444p", "25/1", "áudio"):
        assert trecho in erros, trecho
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_midia.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'midia'`.

- [ ] **Step 3: Implementar**

`tools/midia.py`:

```python
"""Contrato e gravação das animações do acervo.

Toda animação é um MP4 H.264 em yuv420p, 1280x720, 30 quadros por segundo, sem
áudio, com até 60 segundos e 3 MB, acompanhado de um pôster PNG do mesmo
tamanho. O contrato mora aqui e é conferido por tools/tests/test_midia.py com
ffprobe, sem tocar o vídeo.
"""
import json
import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation, font_manager  # noqa: E402

from paleta import cor  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.path.join(RAIZ, "assets", "video")
IMG = os.path.join(RAIZ, "assets", "img")

LARGURA, ALTURA, DPI, FPS = 1280, 720, 100, 30
LIMITE_SEGUNDOS = 60
LIMITE_BYTES = 3 * 1024 * 1024


def _fonte_texto():
    """Manrope quando instalada; DejaVu Sans, que vem com o matplotlib, se não."""
    nomes = {fonte.name for fonte in font_manager.fontManager.ttflist}
    return "Manrope" if "Manrope" in nomes else "DejaVu Sans"


def figura():
    """Figura 1280x720 com fundo, tinta e fonte do tema."""
    plt.rcParams.update({
        "font.family": _fonte_texto(),
        "font.size": 18,
        "text.color": cor("--seg-texto"),
        "axes.labelcolor": cor("--seg-texto"),
        "axes.edgecolor": cor("--seg-borda"),
        "xtick.color": cor("--seg-texto"),
        "ytick.color": cor("--seg-texto"),
        "axes.facecolor": cor("--seg-base"),
        "figure.facecolor": cor("--seg-base"),
        "savefig.facecolor": cor("--seg-base"),
    })
    return plt.figure(figsize=(LARGURA / DPI, ALTURA / DPI), dpi=DPI)


def gravar(fig, desenhar, n_quadros, nome, quadro_poster):
    """Grava assets/video/<nome>.mp4 e assets/img/<nome>-poster.png.

    desenhar(i) atualiza a figura para o quadro i. O pôster é o quadro
    quadro_poster, escolhido para mostrar o conceito inteiro; use o último
    quadro quando a animação acumula elementos.
    """
    os.makedirs(VIDEO, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    mp4 = os.path.join(VIDEO, nome + ".mp4")
    poster = os.path.join(IMG, nome + "-poster.png")
    escritor = animation.FFMpegWriter(
        fps=FPS, codec="libx264",
        extra_args=["-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow",
                    "-movflags", "+faststart", "-an"],
    )
    animacao = animation.FuncAnimation(fig, desenhar, frames=n_quadros, blit=False)
    animacao.save(mp4, writer=escritor, dpi=DPI)
    desenhar(quadro_poster)
    fig.savefig(poster, dpi=DPI)
    plt.close(fig)
    return mp4, poster


def metadados(caminho):
    """Codec, tamanho, formato de pixel, taxa, duração, bytes e áudio, por ffprobe."""
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,pix_fmt,avg_frame_rate:format=duration,size",
         "-of", "json", caminho],
        capture_output=True, text=True, check=True,
    )
    dados = json.loads(saida.stdout)
    videos = [s for s in dados["streams"] if s["codec_type"] == "video"]
    if not videos:
        raise ValueError("%s não tem trilha de vídeo" % caminho)
    video = videos[0]
    return {
        "codec": video["codec_name"],
        "largura": video["width"],
        "altura": video["height"],
        "pix_fmt": video.get("pix_fmt"),
        "fps": video["avg_frame_rate"],
        "duracao": float(dados["format"]["duration"]),
        "bytes": int(dados["format"]["size"]),
        "tem_audio": any(s["codec_type"] == "audio" for s in dados["streams"]),
    }


def violacoes(meta):
    """Quebras do contrato. Lista vazia significa vídeo conforme."""
    erros = []
    if meta["codec"] != "h264":
        erros.append("codec %s, o contrato pede h264" % meta["codec"])
    if (meta["largura"], meta["altura"]) != (LARGURA, ALTURA):
        erros.append("%dx%d, o contrato pede %dx%d"
                     % (meta["largura"], meta["altura"], LARGURA, ALTURA))
    if meta["pix_fmt"] != "yuv420p":
        erros.append("pix_fmt %s, o contrato pede yuv420p" % meta["pix_fmt"])
    if meta["fps"] != "%d/1" % FPS:
        erros.append("taxa %s, o contrato pede %d/1" % (meta["fps"], FPS))
    if meta["duracao"] > LIMITE_SEGUNDOS + 0.5:
        erros.append("%.1f s, o limite é %d s" % (meta["duracao"], LIMITE_SEGUNDOS))
    if meta["bytes"] > LIMITE_BYTES:
        erros.append("%d bytes, o limite é %d" % (meta["bytes"], LIMITE_BYTES))
    if meta["tem_audio"]:
        erros.append("tem trilha de áudio, o contrato pede vídeo mudo")
    return erros
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_midia.py -v`
Expected: `test_gravar_produz_video_conforme` e `test_violacoes_acusa_video_fora_do_contrato` passam; os três testes parametrizados aparecem como `SKIPPED (got empty parameter set)`, porque ainda não há vídeo nem página com vídeo.

- [ ] **Step 5: Commit**

```bash
git add tools/midia.py tools/tests/test_midia.py
git commit -m "feat(midia): contrato de vídeo das animações conferido por ffprobe

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 6: Runtime e validador de widgets

**Files:**
- Create: `assets/js/inteli-widgets.js`, `assets/js/widgets/barras-horizontais.js`, `tools/check_widgets.py`, `tools/dados_widgets_fixture.py`, `assets/data/_fixture-pregoes.json` (gerado), `tools/tests/test_check_widgets.py`, `tools/tests/fixture_widget_ok.html`, `tools/tests/fixture_widget_erro.html`, `tools/tests/fixture_widget_sem_registro.html`, `tools/tests/fixture_widget_fonte_quebrada.html`, `tools/tests/fixture_widget_removido.html`
- Modify: `assets/css/inteli-theme.css` (blocos `.widget` e `.video-slide`), `aulas/_fixture-tema.html` (slide `id="widget"` e scripts)

**Interfaces:**
- Consumes: `check_slides.porta_livre`, `check_slides.servir` (Task 1); `dados/precos_fechamento.csv` (Task 4).
- Produces:
  - JS: `window.IntelIWidgets.registrar(nome, montar)`, onde `montar(elemento, dados, api)` pode devolver Promise; `api.cor(token) -> string`; `api.fonte(tamanho, peso) -> string` para `ctx.font`; `api.ponto(evento, canvas) -> {x, y}` em coordenadas do canvas; `IntelIWidgets.iniciar() -> Promise`.
  - Estados: `data-pronto="sim"` ou `data-pronto="erro"` no elemento.
  - CSS: `.widget`, `.widget canvas`, `.widget-controles`, `.widget-controles button`, `.widget-controles button.ativo`, `.widget-leitura`, `.widget-tabela`, `.video-slide`.
  - Python: `check_widgets.declarados(caminho) -> int`; `check_widgets.checar(caminhos, porta) -> list[dict]` com `deck, declarados, medidos, problemas`; `check_widgets.main(argv) -> int`; `check_widgets._descobrir() -> list[str]`.
  - JSON genérico de barras: `{"titulo": str, "unidade": str, "itens": [{"rotulo": str, "valor": number}]}`.

- [ ] **Step 1: Escrever as páginas de teste**

`tools/tests/fixture_widget_ok.html`:

```html
<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Widget que monta</title></head>
<body>
  <div class="widget" data-widget="ok-teste"></div>
  <script src="../../assets/js/inteli-widgets.js"></script>
  <script>
    IntelIWidgets.registrar('ok-teste', function (elemento) {
      elemento.textContent = 'montado';
    });
  </script>
</body>
</html>
```

`tools/tests/fixture_widget_erro.html`: igual ao anterior, com `data-widget="erro-teste"` e o registro

```html
  <script>
    IntelIWidgets.registrar('erro-teste', function () {
      throw new Error('falha proposital');
    });
  </script>
```

`tools/tests/fixture_widget_sem_registro.html`: `<div class="widget" data-widget="inexistente"></div>` e só o `<script src="../../assets/js/inteli-widgets.js"></script>`, sem registro.

`tools/tests/fixture_widget_fonte_quebrada.html`: `<div class="widget" data-widget="ok-teste" data-fonte="nao-existe.json"></div>`, o runtime e o mesmo registro `ok-teste` da primeira página.

`tools/tests/fixture_widget_removido.html`:

```html
<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Widget declarado e removido antes da medição</title></head>
<body>
  <div class="widget" data-widget="ok-teste"></div>
  <script>document.querySelector('[data-widget]').remove();</script>
  <script src="../../assets/js/inteli-widgets.js"></script>
</body>
</html>
```

- [ ] **Step 2: Escrever o teste que falha**

`tools/tests/test_check_widgets.py`:

```python
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("playwright.sync_api")

import check_slides  # noqa: E402
import check_widgets  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def porta():
    numero = check_slides.porta_livre()
    httpd = check_slides.servir(numero)
    yield numero
    httpd.shutdown()


def _checar(porta, nome):
    [resultado] = check_widgets.checar([os.path.join(AQUI, nome)], porta)
    return resultado


def test_widget_que_monta_passa(porta):
    r = _checar(porta, "fixture_widget_ok.html")
    assert (r["declarados"], r["medidos"]) == (1, 1)
    assert r["problemas"] == []


def test_widget_que_lanca_erro_reprova(porta):
    problemas = " | ".join(_checar(porta, "fixture_widget_erro.html")["problemas"])
    assert "não montou" in problemas
    assert "falha proposital" in problemas


def test_widget_sem_registro_reprova(porta):
    assert any("não montou" in p for p in _checar(porta, "fixture_widget_sem_registro.html")["problemas"])


def test_fonte_de_dados_inexistente_reprova(porta):
    assert any("não montou" in p for p in _checar(porta, "fixture_widget_fonte_quebrada.html")["problemas"])


def test_widget_declarado_e_nao_medido_reprova(porta):
    r = _checar(porta, "fixture_widget_removido.html")
    assert (r["declarados"], r["medidos"]) == (1, 0)
    assert any("nenhum para medir" in p for p in r["problemas"])


def test_main_sem_deck_reprova(monkeypatch):
    monkeypatch.setattr(check_widgets, "_descobrir", lambda: [])
    assert check_widgets.main([]) == 1


def test_main_com_deck_inexistente_reprova():
    assert check_widgets.main(["aulas/nao-existe.html"]) == 1


def test_fixture_do_tema_monta_o_widget_de_demonstracao():
    assert check_widgets.main([os.path.join(check_widgets.RAIZ, "aulas", "_fixture-tema.html")]) == 0
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_check_widgets.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'check_widgets'`.

- [ ] **Step 4: Implementar o runtime**

`assets/js/inteli-widgets.js`:

```js
// Runtime dos widgets interativos dos decks.
//
// Contrato de markup, no deck:
//   <div class="widget" data-widget="tres-visoes"
//        data-fonte="../assets/data/aula01-tres-visoes.json"></div>
//   <script src="../assets/js/inteli-widgets.js"></script>
//   <script src="../assets/js/widgets/tres-visoes.js"></script>
//
// Cada arquivo de assets/js/widgets/ chama
//   IntelIWidgets.registrar('nome', function (elemento, dados, api) { ... })
// e a função pode devolver uma Promise. Depois do evento load e das fontes, este
// arquivo carrega o JSON de data-fonte, chama a função e grava data-pronto="sim".
// Falha de carga ou de montagem grava data-pronto="erro" e escreve no console, e
// o tools/check_widgets.py reprova as duas coisas.
//
// Regras para quem escreve um widget:
// - nenhuma cor literal: api.cor('--seg-primaria') lê a custom property do tema,
//   e o tools/check_brand.py continua valendo para o JS;
// - nenhuma família tipográfica literal: api.fonte(16, 600) monta o ctx.font a
//   partir de --fonte-texto;
// - nenhuma medida de layout para desenhar: slide fora de cena tem display none e
//   mede zero. O canvas usa data-largura e data-altura do markup;
// - coordenada de ponteiro sempre por api.ponto(evento, canvas), porque o Reveal
//   escala o slide com transform.
(function () {
  'use strict';

  var registro = {};

  function cor(nome) {
    return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  }

  function fonte(tamanho, peso) {
    var familia = getComputedStyle(document.documentElement).getPropertyValue('--fonte-texto').trim();
    return (peso || 400) + ' ' + tamanho + 'px ' + familia;
  }

  function ponto(evento, canvas) {
    var caixa = canvas.getBoundingClientRect();
    return {
      x: (evento.clientX - caixa.left) * (canvas.width / caixa.width),
      y: (evento.clientY - caixa.top) * (canvas.height / caixa.height)
    };
  }

  function carregar(endereco) {
    if (!endereco) return Promise.resolve(null);
    return fetch(endereco).then(function (resposta) {
      if (!resposta.ok) {
        throw new Error('HTTP ' + resposta.status + ' ao carregar ' + endereco);
      }
      return resposta.json();
    });
  }

  function montar(elemento) {
    var nome = elemento.dataset.widget;
    var funcao = registro[nome];
    if (!funcao) {
      elemento.dataset.pronto = 'erro';
      console.error('widget sem registro: ' + nome);
      return Promise.resolve();
    }
    return carregar(elemento.dataset.fonte)
      .then(function (dados) {
        return funcao(elemento, dados, { cor: cor, fonte: fonte, ponto: ponto });
      })
      .then(function () {
        elemento.dataset.pronto = 'sim';
      })
      .catch(function (erro) {
        elemento.dataset.pronto = 'erro';
        console.error('widget ' + nome + ': ' + (erro && erro.message ? erro.message : erro));
      });
  }

  function iniciar() {
    var elementos = document.querySelectorAll('[data-widget]');
    return Promise.all(Array.prototype.map.call(elementos, montar));
  }

  window.IntelIWidgets = {
    registrar: function (nome, funcao) { registro[nome] = funcao; },
    cor: cor,
    fonte: fonte,
    ponto: ponto,
    iniciar: iniciar
  };

  // load, e não DOMContentLoaded: os scripts de assets/js/widgets/ vêm depois
  // deste e precisam ter se registrado antes da montagem. document.fonts.ready
  // evita desenhar texto de canvas com a fonte de reserva.
  function aguardarFontes() {
    return document.fonts ? document.fonts.ready : Promise.resolve();
  }
  if (document.readyState === 'complete') {
    aguardarFontes().then(iniciar);
  } else {
    window.addEventListener('load', function () { aguardarFontes().then(iniciar); });
  }
})();
```

- [ ] **Step 5: Implementar o validador**

`tools/check_widgets.py`:

```python
#!/usr/bin/env python3
"""
Valida os widgets interativos dos decks.

Para cada deck: conta no HTML os elementos com data-widget, abre a página no
Chromium do Playwright, espera cada widget terminar de montar e reprova se algum
não gravou data-pronto="sim", se houve erro de console ou exceção na página, ou
se o HTML declara widget e a página não tem nenhum para medir. Nada medido nunca
lê como sucesso: sem deck, ou com zero widget medido no total, o código de saída
é 1.

Uso:
    python3 tools/check_widgets.py aulas/_fixture-tema.html aulas/aula01.html
    python3 tools/check_widgets.py                # todos os aulas/aula*.html
"""
import glob
import os
import re
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_slides import porta_livre, servir  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECLARACAO = re.compile(r"\bdata-widget\s*=")
ESPERA_MS = 15000
JS_PRONTOS = "() => [...document.querySelectorAll('[data-widget]')].every(e => e.dataset.pronto)"
JS_ESTADOS = ("() => [...document.querySelectorAll('[data-widget]')]"
              ".map(e => ({nome: e.dataset.widget, pronto: e.dataset.pronto || null}))")


def declarados(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return len(DECLARACAO.findall(fh.read()))


def _medir(navegador, url):
    pagina = navegador.new_page(viewport={"width": 1280, "height": 720})
    erros = []
    pagina.on("console", lambda msg: erros.append(msg.text) if msg.type == "error" else None)
    pagina.on("pageerror", lambda exc: erros.append(str(exc)))
    try:
        resposta = pagina.goto(url, wait_until="load")
        if resposta is None or not resposta.ok:
            return None, ["página não carregou: %s" % (resposta.status if resposta else "sem resposta")]
        try:
            pagina.wait_for_function(JS_PRONTOS, timeout=ESPERA_MS)
        except Exception:
            erros.append("tempo esgotado esperando os widgets montarem")
        return pagina.evaluate(JS_ESTADOS), erros
    finally:
        pagina.close()


def checar(caminhos, porta):
    resultados = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        try:
            for caminho in caminhos:
                rel = os.path.relpath(os.path.abspath(caminho), RAIZ).replace(os.sep, "/")
                n_declarados = declarados(caminho)
                estados, erros = _medir(navegador, "http://127.0.0.1:%d/%s" % (porta, rel))
                problemas = list(erros)
                if estados is not None:
                    if n_declarados and not estados:
                        problemas.append("HTML declara %d widget(s) e a página não tem nenhum para medir"
                                         % n_declarados)
                    for estado in estados:
                        if estado["pronto"] != "sim":
                            problemas.append("widget %s não montou (data-pronto=%s)"
                                             % (estado["nome"], estado["pronto"]))
                resultados.append({"deck": rel, "declarados": n_declarados,
                                   "medidos": len(estados or []), "problemas": problemas})
        finally:
            navegador.close()
    return resultados


def _descobrir():
    return sorted(glob.glob(os.path.join(RAIZ, "aulas", "aula*.html")))


def main(argv=None):
    caminhos = list(sys.argv[1:] if argv is None else argv) or _descobrir()
    if not caminhos:
        print("ERRO: nenhum deck encontrado, nada foi medido.")
        return 1
    inexistentes = [c for c in caminhos if not os.path.isfile(c)]
    if inexistentes:
        print("ERRO: deck inexistente: %s" % ", ".join(inexistentes))
        return 1
    porta = porta_livre()
    httpd = servir(porta)
    try:
        resultados = checar(caminhos, porta)
    finally:
        httpd.shutdown()
    falhou = False
    for resultado in resultados:
        for problema in resultado["problemas"]:
            print("%s  %s" % (resultado["deck"], problema))
            falhou = True
    medidos = sum(r["medidos"] for r in resultados)
    if falhou:
        return 1
    if medidos == 0:
        print("ERRO: nenhum widget medido em %d deck(s), nada foi validado." % len(resultados))
        return 1
    print("Widgets: %d montado(s) em %d deck(s), sem erro de console." % (medidos, len(resultados)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Implementar o widget genérico e o JSON do fixture**

`assets/js/widgets/barras-horizontais.js`:

```js
// Barras horizontais com rótulo e valor. Widget genérico, usado no fixture do
// tema e disponível para as aulas. JSON: {titulo, unidade, itens: [{rotulo, valor}]}.
(function () {
  'use strict';

  IntelIWidgets.registrar('barras-horizontais', function (elemento, dados, api) {
    var canvas = document.createElement('canvas');
    canvas.width = Number(elemento.dataset.largura || 720);
    canvas.height = Number(elemento.dataset.altura || 360);
    elemento.appendChild(canvas);

    var ctx = canvas.getContext('2d');
    var itens = dados.itens;
    var maximo = Math.max.apply(null, itens.map(function (item) { return item.valor; }));
    var esquerda = 120;
    var direita = 150;
    var faixa = (canvas.height - 16) / itens.length;

    ctx.fillStyle = api.cor('--seg-base');
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = api.fonte(14, 600);
    ctx.textBaseline = 'middle';
    itens.forEach(function (item, i) {
      var y = 8 + i * faixa;
      var largura = (canvas.width - esquerda - direita) * item.valor / maximo;
      ctx.fillStyle = api.cor('--seg-secundaria');
      ctx.fillRect(esquerda, y + 3, largura, faixa - 6);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.textAlign = 'right';
      ctx.fillText(item.rotulo, esquerda - 10, y + faixa / 2);
      ctx.textAlign = 'left';
      ctx.fillText(item.valor.toLocaleString('pt-BR') + ' ' + dados.unidade, esquerda + largura + 8, y + faixa / 2);
    });
  });
})();
```

`tools/dados_widgets_fixture.py`:

```python
"""JSON do widget de demonstração do fixture do tema: pregões com cotação por ativo.

Uso: .venv/bin/python tools/dados_widgets_fixture.py
"""
import json
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    fechamento = pd.read_csv(os.path.join(RAIZ, "dados", "precos_fechamento.csv"), index_col="data")
    contagem = fechamento.notna().sum()
    dados = {
        "titulo": "Pregões com cotação de 02/01/2019 a 31/08/2026",
        "unidade": "pregões",
        "itens": [{"rotulo": t, "valor": int(contagem[t])} for t in fechamento.columns],
    }
    destino = os.path.join(RAIZ, "assets", "data", "_fixture-pregoes.json")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("gravado:", os.path.relpath(destino, RAIZ))


if __name__ == "__main__":
    main()
```

Run: `.venv/bin/python tools/dados_widgets_fixture.py`
Expected: `gravado: assets/data/_fixture-pregoes.json`.

- [ ] **Step 7: CSS do widget e do vídeo**

Anexar ao fim de `assets/css/inteli-theme.css`:

```css
/* ==========================================================================
   Widgets interativos (assets/js/inteli-widgets.js) e vídeo de animação.
   ========================================================================== */

/* O canvas tem width e height declarados no markup; a caixa só centraliza e
   nunca passa da largura útil do slide. */
.widget {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.widget canvas {
  max-width: 100%;
  height: auto;
}

.widget-controles {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.widget-controles button {
  font: inherit;
  font-size: var(--escala-complementar);
  padding: 6px 14px;
  border: 1px solid var(--seg-borda);
  border-radius: 999px;
  background: var(--seg-base);
  color: var(--seg-texto);
  cursor: pointer;
}

/* Seletor composto de propósito: a regra base acima tem especificidade (0,1,1)
   e a classe sozinha perderia o empate (inteli-deck-design, seção 8.1). */
.widget-controles button.ativo {
  background: var(--seg-primaria);
  border-color: var(--seg-primaria);
  color: var(--seg-base);
}

.widget-leitura {
  margin: 0;
  font-size: var(--escala-texto);
  text-align: center;
}

.widget-tabela {
  border-collapse: collapse;
  font-size: var(--escala-texto);
}

.widget-tabela th,
.widget-tabela td {
  padding: 6px 18px;
  border-bottom: 1px solid var(--seg-borda);
  text-align: left;
}

/* max-height além de max-width: a altura depende da proporção, que o CSS não
   conhece (inteli-deck-design, seção 8.8). */
.video-slide {
  display: block;
  max-width: 100%;
  max-height: 460px;
  margin: 0 auto;
  border-radius: 10px;
  background: var(--seg-superficie);
}
```

- [ ] **Step 8: Slide de demonstração no fixture**

Inserir antes de `<section class="end-slide">` em `aulas/_fixture-tema.html`:

```html
      <section class="content-slide" id="widget">
        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-positiva.svg" alt="Logo Inteli">
        <div class="slide-title-area">
          <div class="accent-bar"></div>
          <h2>Widget interativo</h2>
        </div>
        <div class="widget" data-widget="barras-horizontais"
             data-fonte="../assets/data/_fixture-pregoes.json" data-largura="760" data-altura="440"></div>
        <div class="slide-footer">
          <p class="footer-bar">Módulo 08 AdmTech &middot; Fixture do tema</p>
          <p class="footer-page">8</p>
        </div>
      </section>
```

Acrescentar depois de `<script src="../assets/js/inteli-escolha.js"></script>`:

```html
  <script src="../assets/js/inteli-widgets.js"></script>
  <script src="../assets/js/widgets/barras-horizontais.js"></script>
```

- [ ] **Step 9: Rodar os testes e os validadores**

```bash
.venv/bin/python -m pytest tools/tests/test_check_widgets.py -v
.venv/bin/python tools/check_widgets.py aulas/_fixture-tema.html
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
.venv/bin/python -m pytest tools/tests -v
```

Expected: 8 passed no arquivo novo; `Widgets: 1 montado(s) em 1 deck(s), sem erro de console.`; demais validadores limpos; suíte inteira verde.

- [ ] **Step 10: Commit**

```bash
git add assets tools aulas/_fixture-tema.html
git commit -m "feat(widgets): runtime, widget de barras e validador que reprova widget não medido

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 7: Documentos de planejamento e revisão para a planilha

**Files:**
- Create: `PLANO_DE_ENSINO.md`, `PLANEJAMENTO_AULA_A_AULA.md`, `docs/autoestudos-por-semana.md`, `docs/revisao-planilha-2026-09-17.md`, `tools/tests/test_planejamento.py`

**Interfaces:**
- Consumes: spec, seções 4 a 10; `$FONTES/REVISAO-LBL08-COMPUTACAO.md` (títulos exatos dos autoestudos, textos dos artefatos A1 a A3, ponderadas); `$FONTES/Case-Creditos-OpenRouter-M08-AdmTech.docx` (custos, lido com `textutil -convert txt -stdout`).
- Produces: fonte da verdade para todas as tasks de aula. Cada aula em `PLANEJAMENTO_AULA_A_AULA.md` abre com o cabeçalho `### Aula NN - Semana S - Título  (Sprint X)`; cada autoestudo em `docs/autoestudos-por-semana.md` é uma linha `- Título exato`.

Esta task é de texto. O revisor da task confere as três fontes contra o resultado, linha a linha.

- [ ] **Step 1: Escrever o teste estrutural que falha**

`tools/tests/test_planejamento.py`:

```python
"""Estrutura dos documentos de planejamento: seis aulas, sete blocos, amarrações."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TITULOS = {
    "01": "Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível",
    "02": "Dados Financeiros: Do Preço ao Retorno",
    "03": "Correlação, Covariância e o Argumento Matemático da Diversificação",
    "04": "Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz",
    "05": "Do Script ao Produto: API em FastAPI e Página Web",
    "06": "Validação, Robustez e Interpretação com LLM",
}


def _ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as fh:
        return fh.read()


def _secoes_de_aula(texto):
    partes = re.split(r"^### Aula (\d\d) - ", texto, flags=re.M)
    return {partes[i]: partes[i + 1] for i in range(1, len(partes), 2)}


def test_planejamento_tem_as_seis_aulas_com_titulo_exato():
    secoes = _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md"))
    assert sorted(secoes) == sorted(TITULOS)
    for numero, titulo in TITULOS.items():
        assert titulo in secoes[numero].splitlines()[0], numero


def test_cada_aula_tem_sete_blocos_de_quinze_minutos():
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        blocos = re.findall(r"^\s+Bloco (\d) \((\d+) a (\d+) min\)", secao, flags=re.M)
        assert [int(b[0]) for b in blocos] == list(range(1, 8)), numero
        for _, inicio, fim in blocos:
            assert int(fim) - int(inicio) == 15, (numero, inicio, fim)


def test_cada_aula_declara_as_amarracoes():
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        for rotulo in ("Data:", "Entrega que alimenta:", "O que a aula anterior deixou pronto:",
                       "O que esta aula deixa pronto:", "Antes do encontro", "Daily da equipe",
                       "Metodologia ativa", "Depois do encontro"):
            assert rotulo in secao, (numero, rotulo)


def test_autoestudo_citado_no_planejamento_existe_no_arquivo_derivado():
    derivado = _ler("docs", "autoestudos-por-semana.md")
    oficiais = set(re.findall(r"^- (.+)$", derivado, flags=re.M))
    for numero, secao in _secoes_de_aula(_ler("PLANEJAMENTO_AULA_A_AULA.md")).items():
        antes = secao.split("Antes do encontro", 1)[1].split("Daily da equipe", 1)[0]
        citados = re.findall(r"^\s+Autoestudo: (.+?) \(\d+ min\)$", antes, flags=re.M)
        assert len(citados) == 2, numero
        for titulo in citados:
            assert titulo in oficiais, (numero, titulo)


def test_nenhum_documento_tem_travessao():
    for partes in (("PLANO_DE_ENSINO.md",), ("PLANEJAMENTO_AULA_A_AULA.md",),
                   ("docs", "autoestudos-por-semana.md"), ("docs", "revisao-planilha-2026-09-17.md")):
        assert chr(0x2014) not in _ler(*partes), partes
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_planejamento.py -v`
Expected: FAIL com `FileNotFoundError`.

- [ ] **Step 3: Escrever `docs/autoestudos-por-semana.md`**

Cabeçalho declarando a origem: "Derivado do `REVISAO-LBL08-COMPUTACAO.md` (16/06/2026) e das decisões de 17/09/2026, enquanto a Adalove da turma 2026-2B não é lida. Semanas 8 e 9 são proposta a lançar." Uma seção por semana de instrução (`## Semana 01`, `03`, `05`, `06`, `08`, `09`), cada uma com `**Encontro de Instrução**` (título exato e "data a confirmar") e `**Autoestudos**` com uma linha `- Título` por item. Títulos exatos:

| Semana | Autoestudos |
|---|---|
| 01 | Coleta de dados financeiros e DataFrames com Pandas; Cotações do Yahoo Finance no Colab, do jeito reaproveitável |
| 03 | Risco e retorno: passado e prólogo; Análise de uma ação em Python na prática |
| 05 | Diversificação eficiente: a matemática de não colocar todos os ovos na mesma cesta; Atividade Ponderada 1: Diagnóstico de uma carteira herdada |
| 06 | Carteiras e simulação de Monte Carlo com Python; Da nuvem à fronteira eficiente de Markowitz |
| 08 | HTTP e JSON na prática: o que acontece entre a página e o servidor; Primeira API com FastAPI: rotas, parâmetros e validação |
| 09 | Os limites do otimizador e do LLM: premissas, sensibilidade e alucinação; Atividade Ponderada 2: A carteira ótima sobrevive fora da amostra? |

- [ ] **Step 4: Escrever `PLANO_DE_ENSINO.md`**

Seções, nesta ordem:

1. **Identificação**: tabela com Módulo (LBL 08 AdmTech, Imersão no mercado financeiro), Turma (2026-2B), Professor de Computação (Prof. José Romualdo), Início (14/10/2026), Duração (10 semanas, 5 sprints, 6 Encontros de Instrução de Computação), Parceiro ("descrito no LBL da Adalove; nome e premissas a confirmar").
2. **O case**: a ferramenta de simulação de carteira eficiente e as premissas registradas no REVISAO (dados públicos verificáveis, histórico de preços, Selic, IPCA e CDI, gestores definindo a tolerância a risco).
3. **Dados**: resumo de `dados/README.md` com as três visões de preço e as falhas do provedor, apontando para o README.
4. **Cronograma**: tabela da spec, seção 5, com a coluna Data preenchida com "a confirmar na Adalove" e a coluna Aula do módulo (5, 13, 22, 28, 38, 43).
5. **Entregas**: tabela A1 a A5 e Ponderadas 1 e 2, com peso citado do REVISAO e a marca "a confirmar na Adalove"; A4 e A5 com os títulos novos.
6. **Espiral**: tabela da spec, seção 5.
7. **Sala de aula invertida**: as duas tabelas da spec, seção 6.
8. **Pendências abertas**: as quatro fontes não lidas e as quatro pendências de conteúdo da spec, seção 4, numeradas P1 a P8.

- [ ] **Step 5: Escrever `PLANEJAMENTO_AULA_A_AULA.md`**

Abertura igual à do M03: o documento e o plano de ensino são a fonte da verdade; estrutura do encontro (autoestudo, daily de 15 minutos, 105 minutos em sete blocos, nenhum bloco sem interação) com horários "a confirmar na Adalove". Para cada aula, este formato exato (as linhas de bloco e de autoestudo são lidas pelo teste do Step 1):

```text
### Aula 01 - Semana 1 - Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível  (Sprint 1)

Data: a confirmar na Adalove (pendência P1). Aula 5 do módulo na planilha.
Entrega que alimenta: A1 Coletor e Processador de Dados de Mercado (3, a confirmar na Adalove).
O que a aula anterior deixou pronto: primeira aula do módulo; a abertura apresenta o parceiro e a ferramenta.
O que esta aula deixa pronto: coletor parametrizado por tickers e datas, com preço ajustado e ausências tratadas e documentadas.

Antes do encontro
  Autoestudo: Coleta de dados financeiros e DataFrames com Pandas (70 min)
  Autoestudo: Cotações do Yahoo Finance no Colab, do jeito reaproveitável (35 min)
  Preparação no material de apoio: animações ... e autoverificação de cinco perguntas

Daily da equipe (15 min)
  ...

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  ...
  ...
  Bloco 7 (90 a 105 min)  ...

Depois do encontro
  ...
```

Conteúdo obrigatório de cada bloco. Todo bloco termina numa interação nomeada (Peer Instruction, prever e observar, pensar e compartilhar, dupla no notebook, escolha coletiva ou quiz). Os números da Aula 01 são os medidos no ensaio de 17/09/2026 e travados na Task 11.

**Aula 01, Semana 1, Sprint 1.** Preparação: animações `aula01-tres-visoes-mglu3` e `aula01-mapa-ausencias`.
- Bloco 1: abertura do módulo (parceiro, ferramenta, A1 a A5 por sprint) e Peer Instruction: "No primeiro pregão de 2019, quanto o Adj Close da PETR4 vale em relação ao Close?" Opções 100%, 86%, 52% e 26%; cada distrator é a razão real de outro ativo da cesta (BOVA11, SUZB3 e VALE3); a certa é 26,13%.
- Bloco 2: as três visões de preço; a turma prevê o que acontece com as três linhas da MGLU3 em 27/05/2024 antes de tocar a animação; pergunta disparada: qual visão responde quanto R$ 1.000 aplicados em 2019 viraram.
- Bloco 3: widget `tres-visoes` com B3SA3 (negociado cai 67,17% em 17/05/2021, Close cai 1,51%) e WEGE3; escolha coletiva de quatro perguntas de negócio contra as três visões; PETR4 com retorno de preço de 87,12% e retorno total de 616,00%.
- Bloco 4: dupla no notebook, seções 1 e 2: função `coletar` com queda para o snapshot; cronômetro de 12 minutos.
- Bloco 5: animação do mapa de ausências e widget `ausencias`: BOVA11, IVVB11 e GOLD11 sem cotação em 24/10/2025; GOLD11 com 484 pregões vazios antes de 11/12/2020; descartar mantém 1.423 dos 1.908 pregões e tira março de 2020 da cesta; pergunta disparada: que número o grupo registra no ADR.
- Bloco 6: dupla no notebook, seções 3 e 4: relatório de ausências, escolha do tratamento e primeiro ADR com o impacto numérico (volatilidade anual da PETR4 de 39,25% para 33,41%); cronômetro de 12 minutos.
- Bloco 7: quiz de verificação de três perguntas e amarração: A1 (3, a confirmar), SPEC.md antes de codar, ADR individual valendo 20%, review da Sprint 1 com data a confirmar, e o que a Aula 02 vai pedir (retornos a partir do Adj Close tratado).

**Aula 02, Semana 3, Sprint 2.** Resgate: "a Aula 01 deixou pronto o coletor parametrizado, com o Adj Close escolhido e a decisão de ausências registrada em ADR". Preparação: histograma de retornos diários se formando; dispersão crescendo com a raiz do tempo.
- Bloco 1: Peer Instruction sobre a queda de 29,70% da PETR4 em 09/03/2020 e o retorno logarítmico correspondente.
- Bloco 2: retorno simples e logarítmico; widget comparando os dois em quedas grandes; prever antes de revelar.
- Bloco 3: dupla no notebook: `pct_change`, `np.log`, média e desvio diários da cesta; cronômetro.
- Bloco 4: histograma e caudas, março de 2020; desvio padrão como medida de risco; pergunta disparada: o desvio padrão diz a pior queda?
- Bloco 5: anualização por 252 e por raiz de 252; widget de volatilidade em janela de 21, 63 e 252 pregões.
- Bloco 6: dupla: métricas anualizadas da cesta e o CDI do período como referência; escolha coletiva de afirmações sobre risco.
- Bloco 7: quiz e amarração com o A2; a pendência P5 (correlação cobrada no A2 antes da Aula 03) é dita em voz alta.

**Aula 03, Semana 5, Sprint 3.** Resgate: "a Aula 02 deixou pronta a tabela de retorno e volatilidade anualizados da cesta, com o CDI como referência". Preparação: curva de dois ativos se curvando com a correlação; correlação móvel de ITUB4 com BBDC4 e de PETR4 com IVVB11.
- Bloco 1: Peer Instruction: dois ativos com 30% de volatilidade cada, correlação 0,5 e metade em cada; a carteira fica abaixo, em ou acima de 30%?
- Bloco 2: covariância e correlação; heatmap real da cesta.
- Bloco 3: widget de correlação e peso sobre dois ativos reais; prever o peso de menor risco antes de mover.
- Bloco 4: dupla: matriz de correlação e covariância anualizada da cesta; cronômetro.
- Bloco 5: correlação móvel em crise e introdução ao encolhimento de Ledoit-Wolf.
- Bloco 6: escolha coletiva: pares que concentram e pares que diversificam; pensar e compartilhar sobre uma carteira só de bancos. Nenhuma carteira da Ponderada 1 aparece.
- Bloco 7: quiz e amarração com o A3 e a Ponderada 1 (3).

**Aula 04, Semana 6, Sprint 3.** Resgate: "a Aula 03 deixou pronta a matriz de covariância anualizada da cesta e a curva de risco de dois ativos em função da correlação". Preparação: nuvem de Monte Carlo acumulando; fronteira sobre a nuvem; SLSQP no triângulo de pesos.
- Bloco 1: Peer Instruction: a carteira de maior Sharpe entre 10.000 sorteadas é a ótima?
- Bloco 2: pesos, retorno e variância vetoriais, Sharpe com o CDI; widget do triângulo de pesos de três ativos.
- Bloco 3: dupla: motor vetorizado de 10.000 carteiras em menos de 10 segundos; cronômetro.
- Bloco 4: widget de sorteio progressivo: melhor sorteada contra ótima.
- Bloco 5: otimização com restrições, `scipy.optimize.minimize` com SLSQP, variância mínima e máximo Sharpe; animação do SLSQP.
- Bloco 6: dupla: otimizador e fronteira de 50 pontos sobre a nuvem.
- Bloco 7: quiz e amarração com o A3 (2) e prévia do A4 na Sprint 4.

**Aula 05, Semana 8, Sprint 4.** Resgate: "a Aula 04 deixou prontas as carteiras de variância mínima e de máximo Sharpe e a fronteira de 50 pontos, calculadas num notebook". Preparação: requisição e resposta entre navegador e API; tempo de resposta com e sem cache.
- Bloco 1: Peer Instruction: o gestor digita tickers numa página; o otimizador roda no navegador ou no servidor?
- Bloco 2: cliente e servidor, GET, parâmetros de consulta, códigos de status e JSON; widget montador de URL com `fetch` real contra JSON gravado da API de exemplo.
- Bloco 3: FastAPI ao vivo: rota com tipos, validação e `/docs`, importando o módulo do otimizador sem copiar.
- Bloco 4: dupla no notebook: API testada com `TestClient`, status 200 e 422; cronômetro.
- Bloco 5: página HTML com `fetch` e Plotly.js; arquivos estáticos servidos pela API.
- Bloco 6: dupla: `exemplos/api-carteira/` rodando e página estendida; escolha coletiva: chave de API, cálculo, gráfico e validação ficam no navegador, no servidor ou em nenhum dos dois.
- Bloco 7: quiz e amarração com o A4 (2): otimizador dentro da API, fronteira na página, SPEC.md com contratos dos endpoints.

**Aula 06, Semana 9, Sprint 5.** Resgate: "a Aula 05 deixou pronta a API FastAPI que devolve métricas de carteira em JSON e a página que desenha o resultado". Preparação: janela de treino deslizando e pesos mudando; curva de drawdown se formando.
- Bloco 1: Peer Instruction: a carteira de máximo Sharpe otimizada num período entrega o Sharpe prometido no período seguinte?
- Bloco 2: treino e teste temporais, backtest fora da amostra, esperado contra realizado.
- Bloco 3: widget da janela de treino com pesos ótimos pré-calculados; prever quanto os pesos mudam; drawdown.
- Bloco 4: dupla no notebook: backtest e estabilidade dos pesos; cronômetro.
- Bloco 5: o LLM como componente: OpenRouter, chave no backend, prompt com números reais, resposta estruturada, custo por chamada citado do case de créditos (cenário realista de cerca de US$ 0,002 por chamada).
- Bloco 6: widget verificador sobre um texto com erros plantados e declarados como exercício; dupla: prompt, chamada opcional e verificador automático no notebook.
- Bloco 7: quiz e amarração com o A5 (1) e a Ponderada 2 (3); fechamento do módulo com a review da Sprint 5, data a confirmar.

Os valores numéricos das Aulas 02 a 06 não entram agora: cada aula mede os seus na própria task de medições, e o planejamento é atualizado com eles.

- [ ] **Step 6: Escrever `docs/revisao-planilha-2026-09-17.md`**

Formato do REVISAO de junho, com estas seções:

1. **O que muda em relação à revisão de 16/06**: as cinco decisões da spec, seção 1.
2. **Instrução 5 (semana 8, aula 38)**: título "Do Script ao Produto: API em FastAPI e Página Web" e descrição: "O otimizador sai do notebook e vira produto: cliente e servidor, HTTP e JSON, uma API em FastAPI com validação de entrada e documentação automática, e uma página HTML que consome a API com fetch e desenha a fronteira com Plotly.js. A aula integra os módulos das sprints anteriores sem copiar código e prepara o A4."
3. **Instrução 6 (semana 9, aula 43)**: título "Validação, Robustez e Interpretação com LLM" e descrição: "Primeiro, desconfiar do próprio otimizador: divisão temporal entre treino e teste, backtest fora da amostra, drawdown e instabilidade dos pesos entre janelas. Depois, o LLM como componente do produto: chamada no backend pela OpenRouter, prompt com os números reais, verificação automática de cada número citado e custo por token. Alimenta o A5 e a Ponderada 2."
4. **Autoestudos da semana 8**, nos nove campos da planilha (Semana 5, Aula 38, Tipo de Card Autoestudo, Título, Objetivo, Tempo, Referência ABNT, Link, Pontos):
   - 5.1 "HTTP e JSON na prática: o que acontece entre a página e o servidor", 50 min, sem pontos. Objetivo: chegar à aula lendo uma requisição HTTP (método, URL, parâmetros de consulta, código de status) e consumindo JSON com `fetch`. Referências: MDN Web Docs em português, "Visão geral do HTTP" e "Usando a Fetch API".
   - 5.2 "Primeira API com FastAPI: rotas, parâmetros e validação", 70 min, sem pontos. Objetivo: seguir os capítulos "Primeiros passos" e "Parâmetros de consulta" do tutorial oficial em português e subir uma rota GET que devolve JSON, testada em `/docs`, trocando o exemplo do tutorial por um cálculo da cesta. Referência: documentação oficial do FastAPI em português.
   - Antes de gravar cada link, abrir com `curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n" URL` e usar a URL final com código 200. Se a página em português não existir, usar a em inglês e dizer isso no campo Objetivo.
5. **Autoestudos da semana 9**:
   - 6.1 "Os limites do otimizador e do LLM: premissas, sensibilidade e alucinação", 90 min, sem pontos. Referências copiadas do REVISAO: LACHTERMACHER (2016), cap. 7 (p. 153) e cap. 8 (p. 171), e HIROTA (2023), cap. 12 (p. 174); complemento em vídeo "Aula 12 - Simulação de Monte Carlo e Drawdowns", Outspoken Market, 20min18. Link: o do Lachtermacher na Minha Biblioteca.
   - 6.2 "Atividade Ponderada 2: A carteira ótima sobrevive fora da amostra?", 120 min, 3 pontos, com a referência do REVISAO, movida da semana 8.
6. **Artefato A4 (Sprint 4, 2 pontos)**, colunas E, F e G:
   - E: "Otimizador de Carteira com Fronteira Eficiente em Aplicação Web".
   - F, no padrão Business Diagnosis and Discovery do REVISAO: contexto (o coração matemático da ferramenta chega a quem decide, numa aplicação que um gestor opera sem abrir código); o que é (otimização SLSQP exposta por API FastAPI e consumida por página HTML/JS que desenha a fronteira sobre a nuvem de Monte Carlo); o que é esperado (variância mínima e máximo Sharpe com pesos, retorno, volatilidade e Sharpe; fronteira de 50 pontos; endpoints documentados em `/docs`; validação de entrada com erro claro para ticker inválido e período sem dados; página com formulário, gráfico com nuvem, fronteira e os dois ótimos, e tabela de pesos; API importando os módulos anteriores sem copiar código; soma dos pesos igual a 1, sem venda a descoberto; convergência abaixo de 5 segundos para até 15 ativos); o que não é esperado (deploy público com autenticação, interpretação por LLM, design visual elaborado, venda a descoberto, alavancagem, custos de transação, modelos além de média-variância); objetivos de aprendizagem; formato de entrega (repositório com a aplicação, `uvicorn` documentado no README, SPEC.md com contratos dos endpoints e plano de testes com `TestClient`, ADRs); observação importante (o otimizador converge para o passado, e uma entrada inválida sem mensagem clara derruba a confiança do parceiro antes do gráfico aparecer).
   - G: Corretude da otimização (25%); API documentada, validada e testada (15%); Página e fronteira (15%); Integração sem cópia de código (10%); Especificação e documentação (15%); ADRs, componente individual (20%). Soma 100%.
7. **Artefato A5 (Sprint 5, 1 ponto)**, colunas E, F e G:
   - E: "Interpretação da Carteira por LLM".
   - F: contexto (a ferramenta calcula e mostra, e falta explicar em português sem inventar número); o que é (endpoint da API da Sprint 4 que envia à OpenRouter os resultados reais e devolve texto verificado, exibido na página); o que é esperado (chamada no backend com chave em variável de ambiente, fora do JavaScript e do git; prompt com pesos, retorno, volatilidade, Sharpe, período e resultado fora da amostra quando houver, pedindo limitações declaradas; resposta estruturada; verificação automática de todo número citado, com tolerância declarada, e texto reprovado sinalizado na página; tokens e custo por chamada registrados; comparação de dois modelos em qualidade e custo; falha do provedor tratada sem derrubar a aplicação); o que não é esperado (chatbot, recomendação automática sem ressalvas, ajuste fino, RAG); objetivos de aprendizagem; formato de entrega (endpoint e painel na aplicação, SPEC.md com o prompt versionado e o plano de testes do verificador, README, ADRs); observação importante (a credibilidade da ferramenta depende de o texto ser verificável contra os números na tela).
   - G: Integração segura (15%); Prompt e contexto (15%); Verificação automática com testes (20%); Custo e escolha de modelo (15%); Especificação e documentação (15%); ADRs, componente individual (20%). Soma 100%.
8. **Pendências para a coordenação**: P5 a P8 do plano de ensino, incluindo a atualização do case de créditos OpenRouter, que ainda cita Streamlit.

Rodar a skill `humanizer` sobre o texto das seções 2 a 7 antes do commit, mantendo os números e os títulos exatos.

- [ ] **Step 7: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_planejamento.py -v`
Expected: 5 passed.

- [ ] **Step 8: Commit**

```bash
git add PLANO_DE_ENSINO.md PLANEJAMENTO_AULA_A_AULA.md docs/autoestudos-por-semana.md docs/revisao-planilha-2026-09-17.md tools/tests/test_planejamento.py
git commit -m "docs(planejamento): plano de ensino, roteiro das seis aulas e revisão para a planilha

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 8: ADRs da fundação, CLAUDE.md, README e ANDAMENTO

**Files:**
- Create: `docs/adrs/ADR-001-base-do-m03-com-componentes-da-formacao-gitlab.md`, `docs/adrs/ADR-002-a4-com-fastapi-e-a5-so-com-llm.md`, `docs/adrs/ADR-003-dados-do-case-b3-e-bcb-versionados.md`, `docs/adrs/ADR-004-sala-de-aula-invertida-em-tres-tempos.md`, `docs/adrs/ADR-005-animacoes-mp4-e-widgets-em-js-puro.md`, `docs/adrs/ADR-006-numeracao-aula01-a-aula06.md`, `CLAUDE.md`, `README.md`, `docs/ANDAMENTO.md`, `tools/tests/test_adrs.py`

**Interfaces:**
- Consumes: spec; `PLANO_DE_ENSINO.md` (Task 7); `$M03/CLAUDE.md` e `$M03/README.md` como modelo de forma.
- Produces: ADRs numeradas que as tasks de aula citam; `CLAUDE.md` com os comandos do acervo.

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_adrs.py`:

```python
"""Estrutura mínima das ADRs, pela diretiva global do professor."""
import glob
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADRS = sorted(glob.glob(os.path.join(RAIZ, "docs", "adrs", "ADR-*.md")))
SECOES = ["## Contexto", "## Decisão", "## Motivações", "## Riscos conhecidos",
          "## Consequências", "## ADRs relacionadas"]


def test_as_seis_adrs_da_fundacao_existem_em_sequencia():
    numeros = [int(re.search(r"ADR-(\d{3})-", os.path.basename(a)).group(1)) for a in ADRS]
    assert numeros[:6] == [1, 2, 3, 4, 5, 6]
    assert numeros == list(range(1, len(numeros) + 1))


def test_cada_adr_tem_cabecalho_e_secoes():
    assert ADRS, "nenhuma ADR encontrada"
    for caminho in ADRS:
        texto = open(caminho, encoding="utf-8").read()
        for campo in ("**Data:**", "**Status:**", "**Decisores:**"):
            assert campo in texto, (os.path.basename(caminho), campo)
        posicoes = [texto.find(s) for s in SECOES]
        assert -1 not in posicoes, (os.path.basename(caminho), posicoes)
        assert posicoes == sorted(posicoes), os.path.basename(caminho)
        assert chr(0x2014) not in texto, os.path.basename(caminho)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_adrs.py -v`
Expected: FAIL com `nenhuma ADR encontrada` e lista de números vazia.

- [ ] **Step 3: Escrever as seis ADRs**

Modelo de cada arquivo:

```markdown
# ADR-00N: título descritivo

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto
## Decisão
Uma frase.
## Motivações
## Riscos conhecidos
Tabela Risco | Mitigação.
## Consequências
Positivas e negativas, em listas separadas.
## ADRs relacionadas
```

Conteúdo obrigatório:

| ADR | Decisão em uma frase | Pontos que precisam aparecer |
|---|---|---|
| 001 | O acervo parte da base do M03 e incorpora o cronômetro e a escolha da Formação GitLab. | M03 tem as correções de 04/09 e 08/09/2026 e a tradução de URL do `check_links.py`; a Formação GitLab tem os dois componentes e o contraste do portal; nenhuma das duas bases contém a outra; o que foi copiado de cada uma, arquivo por arquivo |
| 002 | O A4 entrega o otimizador numa aplicação FastAPI com página HTML/JS, o A5 fica só com a interpretação por LLM, as instruções 5 e 6 trocam de conteúdo e a Ponderada 2 vai para a semana 9. | decisão do professor em 17/09/2026; Streamlit sai do módulo; chave de LLM no backend; riscos P6 (A4 vence na semana da aula) e densidade da semana 8; case OpenRouter a atualizar; ADR-004 como mitigação da densidade |
| 003 | Os dados do case são um snapshot versionado de 15 ativos da B3 pelo yfinance e de quatro séries do SGS do Banco Central. | janela e data da coleta; `Close` já ajustado por desdobramento e a reconstrução do negociado; falhas reais em 24/10/2025; termos do Yahoo e a troca por COTAHIST como mitigação; notebooks nunca dependem de rede em aula |
| 004 | Toda aula é desenhada em três tempos de sala invertida, e o encontro abre medindo o preparo. | tabela dos três tempos e das técnicas da spec, seção 6; a regra dos 15 minutos continua; carga do autoestudo dentro de 2h |
| 005 | Animações são MP4 H.264 geradas por matplotlib sobre `dados/`, e widgets são JavaScript puro alimentado por JSON gerado de `dados/`. | contrato de vídeo; ausência de H.264 no Chromium do Playwright e verificação por ffprobe; widgets sem cor literal e sem medir layout; alternativas descartadas (Manim, GIF, biblioteca de gráficos no deck) com o motivo |
| 006 | Os arquivos das instruções de Computação se chamam `aula01` a `aula06`, na ordem em que acontecem. | a planilha numera as aulas do módulo inteiro (5, 13, 22, 28, 38, 43); o portal mostra os dois números |

- [ ] **Step 4: Escrever `CLAUDE.md`**

Adaptar `$M03/CLAUDE.md` com estas seções:

1. **O que é este repositório**: acervo de Computação do LBL 08 AdmTech 2026-2B; site estático no GitHub Pages; o que se edita.
2. **Comandos**, num bloco `bash`: preview (`python3 -m http.server 8000`), `.venv/bin/python -m pytest tools/tests -v`, `check_brand.py`, `check_links.py`, `check_slides.py aulas/_fixture-tema.html aulas/aulaNN.html`, `check_widgets.py aulas/_fixture-tema.html aulas/aulaNN.html`, `baixar_dados.py` (rede), `dados_widgets_aulaNN.py`, `animacoes_aulaNN.py`, execução de notebook com `M08_OFFLINE=1 jupyter nbconvert --to notebook --execute --output-dir /tmp/nb notebooks/aulaNN.ipynb`.
3. **Arquitetura de conteúdo em três camadas**: planejamento (os dois documentos e a spec), metodologia (skills `inteli-course-design` e `inteli-deck-design`), materiais.
4. **O case e os dados**: resumo de `dados/README.md`.
5. **Sala de aula invertida**: resumo da ADR-004.
6. **Mídia**: contrato de vídeo e contrato de widget, com os arquivos de referência.
7. **Armadilhas conhecidas**: as do M03 que continuam valendo (estouro invisível de 720px, capa em `conic-gradient`, especificidade de estado, validador cego a interação, PDF de verdade, métricas de fonte do Ubuntu) e as novas: `Close` do Yahoo já ajustado por desdobramento; Chromium do Playwright sem H.264; widget que mede layout desenha em zero; widget registrado antes do evento `load`; `dropna` na cesta tira março de 2020 de todos os ativos.
8. **Automação**: validadores, hook, agentes, CI.
9. **Convenções editoriais**: as da spec e as regras de escrita do professor.
10. **Commits e push**: autor configurado, linha `Co-Authored-By`, remoto `git@github.com-josercf:josercf/2026-2B-M08.git`.

- [ ] **Step 5: Escrever `README.md` e `docs/ANDAMENTO.md`**

`README.md`, para o aluno, no formato do `$M03/README.md`: o módulo (tabela com datas "a confirmar"), o parceiro ("a confirmar"), as seis instruções com semana, sprint e entrega, a sala invertida em um parágrafo, estrutura de pastas e o endereço do portal `https://josercf.github.io/2026-2B-M08/`.

`docs/ANDAMENTO.md`: seções **Pronto** (Tasks 1 a 8 concluídas, com os números medidos dos dados), **Em andamento** (Tasks 9 e 10, Aula 01) e **Pendências abertas** (P1 a P8 do plano de ensino).

- [ ] **Step 6: Rodar e ver passar**

```bash
.venv/bin/python -m pytest tools/tests/test_adrs.py -v
grep -rn $'\u2014' CLAUDE.md README.md docs/ && echo "ACHOU TRAVESSÃO" || echo "sem travessão"
```

Expected: 2 passed; `sem travessão`.

- [ ] **Step 7: Commit**

```bash
git add docs/adrs CLAUDE.md README.md docs/ANDAMENTO.md tools/tests/test_adrs.py
git commit -m "docs(adr): seis decisões da fundação, guia do repositório e andamento

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Portal

**Files:**
- Create: `index.html`, `tools/tests/test_portal.py`

**Interfaces:**
- Consumes: `assets/css/inteli-portal.css` (Task 2), `PLANO_DE_ENSINO.md` (Task 7).
- Produces: um `<article class="card-aula" id="aula-NN">` por instrução, com os quatro botões `Slides`, `Material`, `Referências`, `Notebook` desabilitados (`<a class="botao" aria-disabled="true">`, sem `href`) até a aula existir.

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_portal.py`:

```python
"""O portal lista as seis instruções e só habilita botão de artefato que existe."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_BLOB = "https://github.com/josercf/2026-2B-M08/blob/main/"


def _portal():
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as fh:
        return fh.read()


def _cards(html):
    return dict(re.findall(r'<article class="card-aula" id="aula-(\d\d)">(.*?)</article>', html, re.S))


def test_portal_tem_as_seis_instrucoes_em_cinco_sprints():
    html = _portal()
    assert sorted(_cards(html)) == ["01", "02", "03", "04", "05", "06"]
    assert len(re.findall(r'<section class="sprint-block"', html)) == 5


def test_botao_habilitado_aponta_para_arquivo_existente_e_desabilitado_nao_tem_href():
    for numero, card in _cards(_portal()).items():
        botoes = re.findall(r"<a class=\"botao\"([^>]*)>", card)
        assert len(botoes) == 4, numero
        for atributos in botoes:
            href = re.search(r'href="([^"]+)"', atributos)
            if 'aria-disabled="true"' in atributos:
                assert href is None, (numero, atributos)
                continue
            alvo = href.group(1)
            if alvo.startswith(REPO_BLOB):
                alvo = alvo[len(REPO_BLOB):]
            assert os.path.isfile(os.path.join(RAIZ, alvo)), (numero, alvo)


def test_artefato_existente_tem_botao_habilitado():
    cards = _cards(_portal())
    for numero, card in cards.items():
        for pasta, extensao in (("aulas", "html"), ("materiais", "html"),
                                ("referencias", "html"), ("notebooks", "ipynb")):
            caminho = "%s/aula%s.%s" % (pasta, numero, extensao)
            if os.path.isfile(os.path.join(RAIZ, caminho)):
                assert caminho in card, (numero, caminho)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_portal.py -v`
Expected: FAIL com `FileNotFoundError` em `index.html`.

- [ ] **Step 3: Escrever `index.html`**

Estrutura do `$M03/index.html`, com:

- `<title>Módulo 08 AdmTech &middot; Computação</title>`; `meta description` com o módulo e as seis instruções.
- Cabeçalho: eyebrow `LBL 08 AdmTech &middot; 2026-2B &middot; Computação`; `h1` "Módulo 08 AdmTech, Imersão no mercado financeiro"; `dl` com Professor de Computação (Prof. José Romualdo), Parceiro do case ("a confirmar na Adalove"), Início (14/10/2026), Duração (10 semanas &middot; 5 sprints &middot; 6 Encontros de Instrução de Computação).
- Cinco `<section class="sprint-block" aria-labelledby="sprint-N-titulo">`, com `p.sprint-datas` "datas a confirmar" e `p.sprint-entrega` citando o artefato COM da sprint e o peso com "(a confirmar)".
- Cards de aula na sprint certa: Sprint 1 aula 01; Sprint 2 aula 02; Sprint 3 aulas 03 e 04; Sprint 4 aula 05; Sprint 5 aula 06. Markup:

```html
          <article class="card-aula" id="aula-01">
            <div class="card-cabecalho">
              <span class="card-badge">INSTRUÇÃO 1</span>
              <p class="card-data">Semana 1 &middot; aula 5 do módulo &middot; data a confirmar</p>
            </div>
            <h3>Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível</h3>
            <p class="card-resumo">Coletor parametrizado, as três visões de preço e as ausências reais do provedor, sobre a cesta de 15 ativos da B3.</p>
            <div class="card-botoes">
              <a class="botao" aria-disabled="true"><span class="material-symbols-outlined" aria-hidden="true">slideshow</span>Slides</a>
              <a class="botao" aria-disabled="true"><span class="material-symbols-outlined" aria-hidden="true">menu_book</span>Material</a>
              <a class="botao" aria-disabled="true"><span class="material-symbols-outlined" aria-hidden="true">link</span>Referências</a>
              <a class="botao" aria-disabled="true"><span class="material-symbols-outlined" aria-hidden="true">code</span>Notebook</a>
            </div>
          </article>
```

- Cards de contexto (`card-contexto`) para cada entrega COM ("Entrega COM", título e peso com "a confirmar") e para as ponderadas na Sprint 3 (Ponderada 1) e na Sprint 5 (Ponderada 2).
- Resumos das aulas 02 a 06 tirados do escopo da spec, seção 9, em uma frase cada.

- [ ] **Step 4: Rodar e ver passar**

```bash
.venv/bin/python -m pytest tools/tests/test_portal.py -v
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
```

Expected: 3 passed; validadores limpos.

- [ ] **Step 5: Commit**

```bash
git add index.html tools/tests/test_portal.py
git commit -m "feat(portal): seis instruções em cinco sprints, com botões desabilitados até cada aula existir

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 10: Agentes, hook, CI e publicação no GitHub

**Files:**
- Create: `.claude/agents/construtor-aulas.md`, `.claude/agents/revisor-slides.md`, `.claude/settings.json`, `.github/workflows/validate.yml`, `.github/workflows/static.yml`, `requirements-ci.txt`, `.nojekyll`

**Interfaces:**
- Consumes: tudo das Tasks 1 a 9.
- Produces: repositório público `josercf/2026-2B-M08` com CI verde e Pages publicado; agentes usados na Fase 2 e no plano das Aulas 02 a 06.

- [ ] **Step 1: Hook e workflow de publicação**

```bash
mkdir -p .claude/agents .github/workflows
cp $M03/.claude/settings.json .claude/settings.json
cp $M03/.github/workflows/static.yml .github/workflows/static.yml
touch .nojekyll
```

Trocar no comentário do topo de `static.yml` a frase "Turma.xlsx e o TAPI estao no .gitignore por isso." por "As planilhas exportadas e os segredos estao no .gitignore por isso."

- [ ] **Step 2: `requirements-ci.txt`**

```text
# Dependências da validação do acervo (.github/workflows/validate.yml).
# Sem versão fixada: os notebooks rodam no Colab, que atualiza os pacotes sozinho.
#
# Validadores
playwright        # tools/check_slides.py e tools/check_widgets.py
pytest            # tools/tests/
#
# Execução dos notebooks
nbconvert
jupyter
ipykernel
#
# Notebooks, medições, animações e JSON dos widgets
pandas
numpy
matplotlib
```

Cada aula que precisar de biblioteca nova (scipy na Aula 04, fastapi, httpx e uvicorn na Aula 05, scikit-learn na Aula 03) acrescenta a linha com o motivo na própria task.

- [ ] **Step 3: `validate.yml`**

```yaml
# Portão do acervo: nada de material quebrado entra em main.
name: Validar o acervo

on:
  push:
  pull_request:

jobs:
  validar:
    runs-on: ubuntu-latest
    env:
      M08_OFFLINE: "1"

    steps:
      - name: Clonar o repositório
        uses: actions/checkout@v4

      - name: Preparar o Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar ffmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Instalar dependências
        run: |
          python3 -m pip install --upgrade pip
          python3 -m pip install -r requirements-ci.txt

      - name: Instalar o Chromium do Playwright
        run: python3 -m playwright install --with-deps chromium

      - name: Fidelidade ao brandbook
        run: python3 tools/check_brand.py

      - name: Links locais
        run: python3 tools/check_links.py

      # O fixture do tema entra sempre na lista: garante ao menos um deck e um
      # widget medidos antes da primeira aula. Nada medido nunca lê como sucesso.
      - name: Layout dos decks
        run: python3 tools/check_slides.py aulas/_fixture-tema.html $(ls aulas/aula*.html 2>/dev/null)

      - name: Widgets dos decks
        run: python3 tools/check_widgets.py aulas/_fixture-tema.html $(ls aulas/aula*.html 2>/dev/null)

      - name: Suíte de testes
        run: python3 -m pytest tools/tests/ -v

      # Sem --inplace: a saída gravada no notebook entregaria o desafio resolvido.
      - name: Executar os notebooks
        run: |
          if [ -n "$(ls -A notebooks/*.ipynb 2>/dev/null)" ]; then
            jupyter nbconvert --to notebook --execute \
              --output-dir "${RUNNER_TEMP}/notebooks-executados" \
              notebooks/*.ipynb
          else
            echo "nenhum notebook em notebooks/: nada a executar"
          fi

      - name: A árvore de trabalho precisa continuar limpa
        run: |
          git diff --exit-code
          test -z "$(git status --porcelain)" || { git status --porcelain; exit 1; }
```

- [ ] **Step 4: Os dois agentes**

`.claude/agents/construtor-aulas.md`: partir de `$M03/.claude/agents/construtor-aulas.md` e manter a estrutura (frontmatter com `name`, `description`, `tools: Bash, Read, Write, Edit, Grep, Glob`, `model: opus`; seções de leitura obrigatória, artefatos, dados, validação, checklist e relatório). Mudanças obrigatórias:

1. Descrição e contexto: Módulo 08 AdmTech, Computação, Prof. José Romualdo, case da ferramenta de carteira eficiente.
2. Leitura obrigatória acrescenta: a spec, `dados/README.md`, as ADRs 003 a 005 e o plano da aula em `docs/superpowers/plans/`.
3. Artefatos: os quatro do M03 mais `docs/notas-do-professor/aulaNN.md`, `tools/medidas_aulaNN.py` com `tools/tests/test_aulaNN.py`, `tools/animacoes_aulaNN.py` (duas ou mais animações), `tools/dados_widgets_aulaNN.py` com os widgets em `assets/js/widgets/`.
4. Seção nova "Sala de aula invertida": seção "Preparação" no topo do material com as animações e a autoverificação de cinco perguntas; Bloco 1 do deck abre com Peer Instruction sobre o conteúdo pré-aula.
5. Seção de dados reescrita: só `dados/`; os números vêm de `medidas_aulaNN.py` e estão travados no teste antes do primeiro slide; nenhuma carteira de ponderada aparece.
6. Links: notebook pelo GitHub (`https://github.com/josercf/2026-2B-M08/blob/main/notebooks/aulaNN.ipynb`); badge do Colab (`https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aulaNN.ipynb`); URL bruta de dados (`https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/`).
7. Validação obrigatória: pytest inteiro, `check_brand.py`, `check_links.py`, `check_slides.py aulas/aulaNN.html`, `check_widgets.py aulas/aulaNN.html`, execução do notebook com `M08_OFFLINE=1`, e o agente `revisor-slides`.
8. Regras de escrita do professor copiadas das Global Constraints deste plano.

`.claude/agents/revisor-slides.md`: partir de `$M03/.claude/agents/revisor-slides.md` e manter as seções 1 a 6. Mudanças obrigatórias:

1. Contexto do M08 no lugar do 03 IN, com `dados/` e `tools/tests/test_aulaNN.py` como referência de número.
2. Seção 1 roda também `python3 tools/check_widgets.py aulas/aulaNN.html`.
3. Seção 3 ganha "3.6 Vídeo": pôster presente e significativo, `controls muted playsinline`, a animação comunica o conceito do slide, texto da animação legível a 1280x720.
4. Seção 3 ganha "3.7 Widget depois de interação": clicar em cada controle, conferir que o canvas redesenha, que a leitura muda e que nada sai dos 1280x720.
5. Seção 4 ganha: Bloco 1 abre com Peer Instruction sobre a preparação; título de slide analítico com achado e número; ausência de paralelismo, antítese simétrica, escalada com dois-pontos e título de listicle.

- [ ] **Step 5: Validar localmente tudo junto**

```bash
.venv/bin/python -m pytest tools/tests -v
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html
.venv/bin/python tools/check_widgets.py aulas/_fixture-tema.html
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "settings ok"
```

Expected: tudo verde e `settings ok`.

- [ ] **Step 6: Commit**

```bash
git add .claude .github requirements-ci.txt .nojekyll
git commit -m "ci: validação do acervo, publicação no Pages, hook e agentes do M08

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Criar o repositório, publicar e conferir o CI**

```bash
gh repo create josercf/2026-2B-M08 --public --description "Acervo de Computação do Módulo 08 AdmTech (Inteli, 2026-2B): decks, materiais, referências e notebooks"
git remote add origin git@github.com-josercf:josercf/2026-2B-M08.git
git push -u origin main
gh api --method POST repos/josercf/2026-2B-M08/pages -f build_type=workflow
gh run list --repo josercf/2026-2B-M08 --limit 4
```

Esperar os dois workflows terminarem (`gh run watch <id> --repo josercf/2026-2B-M08 --exit-status`). Expected: "Validar o acervo" e "Publicar no GitHub Pages" com `success`; `curl -s -o /dev/null -w "%{http_code}" https://josercf.github.io/2026-2B-M08/` devolve `200`. Se o CI falhar, ler o log (`gh run view <id> --log-failed`), corrigir na raiz e empurrar de novo; não desligar passo do workflow.

---
## Fase 2: Aula 01, padrão-ouro

### Task 11: Medições da Aula 01 travadas em teste

**Files:**
- Create: `tools/medidas_aula01.py`, `tools/tests/test_aula01.py`

**Interfaces:**
- Consumes: CSVs de `dados/` (Task 4).
- Produces:
  - `carregar_precos(arquivo) -> DataFrame` (índice `data` em datetime, colunas por ticker)
  - `carregar_desdobramentos() -> DataFrame` (`ticker`, `data` em datetime, `fator`)
  - `preco_negociado(ticker) -> Series`
  - `tres_visoes(ticker) -> DataFrame` com colunas `negociado`, `fechamento`, `ajustado`
  - `maior_variacao_diaria(serie) -> (Timestamp, float)`
  - `retorno_no_periodo(serie) -> float`
  - `ausencias() -> Series` (pregões vazios por ticker, no Close)
  - `volatilidade_anual(precos) -> Series`
  - `comparar_tratamentos() -> dict` com `pregoes_total`, `pregoes_descartar`, `pregoes_preencher`, `inicio_descartar` (str AAAA-MM-DD), `vol_descartar` (Series), `vol_preencher` (Series), `retorno_bova11_preenchido` (dict `{"2025-10-24": float, "2025-10-27": float}`)

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_aula01.py`:

```python
"""Trava os achados da Aula 01, medidos em 17/09/2026 sobre dados/.

Se um valor divergir depois de uma nova coleta, o provedor mudou o histórico:
investigar e registrar em dados/README.md antes de atualizar o número aqui, no
deck, no material, nas notas, nos widgets e nas animações.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula01 as m  # noqa: E402


def _variacao_no_dia(serie, dia):
    return round(float(serie.dropna().pct_change().loc[dia]), 4)


def test_negociado_de_b3sa3_cai_67_por_cento_no_desdobramento():
    visoes = m.tres_visoes("B3SA3")
    assert round(float(visoes.loc["2021-05-14", "negociado"]), 2) == 53.55
    assert round(float(visoes.loc["2021-05-17", "negociado"]), 2) == 17.58
    data, variacao = m.maior_variacao_diaria(visoes["negociado"])
    assert data.strftime("%Y-%m-%d") == "2021-05-17"
    assert round(variacao, 4) == -0.6717
    assert _variacao_no_dia(visoes["fechamento"], "2021-05-17") == -0.0151


def test_negociado_de_mglu3_sobe_896_por_cento_no_grupamento():
    visoes = m.tres_visoes("MGLU3")
    assert round(float(visoes.loc["2019-01-02", "negociado"]), 2) == 173.96
    assert round(float(visoes.loc["2024-05-24", "negociado"]), 2) == 1.32
    assert round(float(visoes.loc["2024-05-27", "negociado"]), 2) == 13.15
    data, variacao = m.maior_variacao_diaria(visoes["negociado"])
    assert data.strftime("%Y-%m-%d") == "2024-05-27"
    assert round(variacao, 4) == 8.9621
    assert _variacao_no_dia(visoes["negociado"], "2019-08-06") == -0.8674
    assert _variacao_no_dia(visoes["negociado"], "2020-10-14") == -0.7531


@pytest.mark.parametrize("ticker,dia,variacao", [
    ("WEGE3", "2021-04-28", -0.5069),
    ("BBAS3", "2024-04-16", -0.5057),
    ("EGIE3", "2025-11-27", -0.2851),
])
def test_desdobramento_vira_queda_falsa_no_negociado(ticker, dia, variacao):
    assert _variacao_no_dia(m.preco_negociado(ticker), dia) == variacao


def test_close_do_yahoo_nao_salta_em_nenhum_dos_15_eventos():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    eventos = m.carregar_desdobramentos()
    assert len(eventos) == 15
    for ticker, data in zip(eventos["ticker"], eventos["data"]):
        variacao = fechamento[ticker].dropna().pct_change().loc[data]
        assert abs(variacao) < 0.07, (ticker, data, variacao)


def test_negociado_coincide_com_close_depois_do_ultimo_evento():
    visoes = m.tres_visoes("MGLU3").loc["2026-01-02":]
    assert (visoes["negociado"] - visoes["fechamento"]).abs().max() < 1e-9


@pytest.mark.parametrize("ticker,preco,total", [
    ("PETR4", 0.8712, 6.1600),
    ("VALE3", 0.5238, 1.8986),
    ("BBAS3", -0.1465, 0.4209),
    ("ITUB4", 0.2102, 0.9120),
    ("BOVA11", 0.9884, 0.9884),
    ("IVVB11", 3.4703, 3.4703),
])
def test_proventos_separam_retorno_de_preco_e_retorno_total(ticker, preco, total):
    visoes = m.tres_visoes(ticker)
    assert round(m.retorno_no_periodo(visoes["fechamento"]), 4) == preco
    assert round(m.retorno_no_periodo(visoes["ajustado"]), 4) == total


def test_ausencias_reais_do_provedor():
    ausentes = m.ausencias()
    assert ausentes[ausentes > 0].to_dict() == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}


def test_descartar_datas_mantem_1423_pregoes_a_partir_de_dezembro_de_2020():
    c = m.comparar_tratamentos()
    assert c["pregoes_total"] == 1908
    assert c["pregoes_descartar"] == 1423
    assert c["pregoes_preencher"] == 1908
    assert c["inicio_descartar"] == "2020-12-11"


@pytest.mark.parametrize("ticker,descartar,preencher", [
    ("BOVA11", 0.1851, 0.2341),
    ("IVVB11", 0.1767, 0.2015),
    ("GOLD11", 0.1980, 0.1980),
    ("PETR4", 0.3341, 0.3925),
    ("VALE3", 0.2977, 0.3549),
    ("MGLU3", 0.6775, 0.6541),
])
def test_volatilidade_anual_sob_cada_tratamento(ticker, descartar, preencher):
    c = m.comparar_tratamentos()
    assert round(float(c["vol_descartar"][ticker]), 4) == descartar
    assert round(float(c["vol_preencher"][ticker]), 4) == preencher


def test_preencher_cria_retorno_zero_e_acumula_no_pregao_seguinte():
    retorno = m.comparar_tratamentos()["retorno_bova11_preenchido"]
    assert retorno["2025-10-24"] == 0.0
    assert round(retorno["2025-10-27"], 6) == 0.009252
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_aula01.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'medidas_aula01'`.

- [ ] **Step 3: Implementar**

`tools/medidas_aula01.py`:

```python
"""Medições da Aula 01 sobre os CSVs de dados/.

As três visões de preço (negociado, Close e Adj Close), os saltos que os eventos
corporativos provocam no preço negociado, o peso dos proventos no retorno e o
efeito de descartar ou preencher ausências. Todo número que o deck, o material,
as notas, os widgets e as animações da Aula 01 citam sai daqui e está travado em
tools/tests/test_aula01.py.
"""
import os

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
PREGOES_ANO = 252


def carregar_precos(arquivo):
    """precos_fechamento.csv ou precos_ajustados.csv, com índice de datas."""
    return pd.read_csv(os.path.join(DADOS, arquivo), index_col="data", parse_dates=["data"])


def carregar_desdobramentos():
    return pd.read_csv(os.path.join(DADOS, "eventos_desdobramento.csv"), parse_dates=["data"])


def preco_negociado(ticker):
    """Preço como foi negociado na data.

    O Close do Yahoo vem dividido pelos fatores de todos os eventos posteriores à
    data. Multiplicar de volta por esses fatores devolve o preço da tela do
    pregão daquele dia.
    """
    fechamento = carregar_precos("precos_fechamento.csv")[ticker].dropna()
    eventos = carregar_desdobramentos()
    eventos = eventos[eventos["ticker"] == ticker]
    fator = np.ones(len(fechamento))
    for data, f in zip(eventos["data"], eventos["fator"]):
        fator = fator * np.where(fechamento.index < data, f, 1.0)
    return fechamento * fator


def tres_visoes(ticker):
    """DataFrame com as colunas negociado, fechamento e ajustado de um ativo."""
    return pd.DataFrame({
        "negociado": preco_negociado(ticker),
        "fechamento": carregar_precos("precos_fechamento.csv")[ticker].dropna(),
        "ajustado": carregar_precos("precos_ajustados.csv")[ticker].dropna(),
    })


def maior_variacao_diaria(serie):
    """(data, variação) da maior variação diária em valor absoluto."""
    variacao = serie.dropna().pct_change().dropna()
    data = variacao.abs().idxmax()
    return data, float(variacao[data])


def retorno_no_periodo(serie):
    """Retorno entre o primeiro e o último valor presentes."""
    presentes = serie.dropna()
    return float(presentes.iloc[-1] / presentes.iloc[0] - 1)


def ausencias():
    """Pregões sem cotação por ativo, no Close."""
    return carregar_precos("precos_fechamento.csv").isna().sum()


def volatilidade_anual(precos):
    return precos.pct_change(fill_method=None).std() * np.sqrt(PREGOES_ANO)


def comparar_tratamentos():
    """Descartar datas com ausência (dropna) contra preencher para a frente (ffill)."""
    ajustado = carregar_precos("precos_ajustados.csv")
    descartar = ajustado.dropna()
    preencher = ajustado.ffill()
    retorno_preenchido = preencher["BOVA11"].pct_change(fill_method=None)
    return {
        "pregoes_total": len(ajustado),
        "pregoes_descartar": len(descartar),
        "pregoes_preencher": len(preencher.dropna(how="all")),
        "inicio_descartar": descartar.index[0].strftime("%Y-%m-%d"),
        "vol_descartar": volatilidade_anual(descartar),
        "vol_preencher": volatilidade_anual(preencher),
        "retorno_bova11_preenchido": {
            dia: float(retorno_preenchido.loc[dia]) for dia in ("2025-10-24", "2025-10-27")
        },
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_aula01.py -v`
Expected: todos passam. Divergência em qualquer número: parar e reportar o valor obtido, sem editar o teste.

- [ ] **Step 5: Provar que o teste pega o erro de data do evento**

```bash
cp tools/medidas_aula01.py /tmp/medidas-backup.py
sed -i '' 's/fechamento.index < data/fechamento.index <= data/' tools/medidas_aula01.py
.venv/bin/python -m pytest tools/tests/test_aula01.py -k "b3sa3 or mglu3" -v
cp /tmp/medidas-backup.py tools/medidas_aula01.py
.venv/bin/python -m pytest tools/tests/test_aula01.py -v
```

Expected: com `<=`, os testes de B3SA3 e MGLU3 FALHAM (o fator passa a valer no próprio dia do evento); restaurado, tudo passa. Registrar a mutação vista falhando no relatório.

- [ ] **Step 6: Commit**

```bash
git add tools/medidas_aula01.py tools/tests/test_aula01.py
git commit -m "test(aula01): trava as três visões de preço, os proventos e o efeito do dropna

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 12: Animações da Aula 01

**Files:**
- Create: `tools/animacoes_aula01.py`
- Create (gerados): `assets/video/aula01-tres-visoes-mglu3.mp4`, `assets/img/aula01-tres-visoes-mglu3-poster.png`, `assets/video/aula01-mapa-ausencias.mp4`, `assets/img/aula01-mapa-ausencias-poster.png`

**Interfaces:**
- Consumes: `midia.figura`, `midia.gravar`, `midia.FPS`, `midia.metadados`, `midia.violacoes` (Task 5); `paleta.cor` (Task 3); `medidas_aula01` (Task 11).
- Produces: os dois vídeos e pôsteres, referenciados pelo deck (Task 15) e pelo material (Task 16). Enquanto nenhuma página os referencia, `test_video_nao_esta_orfao` reprova: esta task commita os vídeos e a Task 15 os referencia, e o pytest inteiro só precisa estar verde ao fim da Task 15.

- [ ] **Step 1: Implementar**

`tools/animacoes_aula01.py`:

```python
"""Animações da Aula 01, a partir de dados/ via tools/medidas_aula01.py.

1. aula01-tres-visoes-mglu3 (24 s): as três visões de preço da MGLU3 desenhadas
   no tempo, em escala logarítmica, com cada evento corporativo rotulado quando a
   linha chega nele. O pôster é o último quadro.
2. aula01-mapa-ausencias (20 s): a matriz de pregões por ativo preenchida ativo a
   ativo; no fim, o bloco vazio do GOLD11 e o pregão de 24/10/2025 destacados, e
   o número de pregões que o dropna mantém. O pôster é o último quadro.

Uso: .venv/bin/python tools/animacoes_aula01.py
"""
import os
import sys

import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m  # noqa: E402
from midia import FPS, figura, gravar, metadados, violacoes  # noqa: E402
from paleta import cor  # noqa: E402


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _data_br(timestamp):
    return timestamp.strftime("%d/%m/%Y")


def descrever_evento(fator):
    if fator < 1:
        return "grupamento de %d para 1" % round(1 / fator)
    if float(fator).is_integer():
        return "desdobramento de %d para 1" % fator
    return "bonificação de %s%% em ações" % ("%g" % round((fator - 1) * 100, 2)).replace(".", ",")


def tres_visoes_mglu3():
    visoes = m.tres_visoes("MGLU3")
    eventos = m.carregar_desdobramentos()
    eventos = eventos[eventos["ticker"] == "MGLU3"].reset_index(drop=True)

    fig = figura()
    eixo = fig.add_axes([0.09, 0.12, 0.87, 0.80])
    eixo.set_yscale("log")
    eixo.set_xlim(visoes.index[0], visoes.index[-1])
    eixo.set_ylim(visoes.min().min() * 0.6, visoes.max().max() * 2.2)
    eixo.set_ylabel("R$ por ação, escala logarítmica")
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)

    linhas = {}
    for chave, token, rotulo in (("negociado", "--seg-destaque", "Negociado na data"),
                                 ("fechamento", "--seg-primaria", "Close do Yahoo"),
                                 ("ajustado", "--seg-secundaria", "Adj Close do Yahoo")):
        linhas[chave], = eixo.plot([], [], color=cor(token), linewidth=2.6, label=rotulo)
    eixo.legend(loc="upper right", frameon=False)

    datas = visoes.index
    quadros_desenho = 20 * FPS
    total = quadros_desenho + 4 * FPS
    rotulados = set()

    def desenhar(i):
        k = max(2, int(round(len(datas) * min(i + 1, quadros_desenho) / quadros_desenho)))
        for chave, linha in linhas.items():
            linha.set_data(datas[:k], visoes[chave].values[:k])
        for n, (data, fator) in enumerate(zip(eventos["data"], eventos["fator"])):
            if data <= datas[k - 1] and data not in rotulados:
                rotulados.add(data)
                deslocamento = (14, 40) if n % 2 == 0 else (14, -56)
                eixo.annotate("%s\n%s" % (_data_br(data), descrever_evento(fator)),
                              xy=(data, visoes.loc[data, "negociado"]), xytext=deslocamento,
                              textcoords="offset points", fontsize=15, color=cor("--seg-texto"),
                              arrowprops={"arrowstyle": "-", "color": cor("--seg-borda")})

    return gravar(fig, desenhar, total, "aula01-tres-visoes-mglu3", total - 1)


def mapa_ausencias():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    presente = fechamento.notna().to_numpy().T.astype(float)
    n_ativos, n_pregoes = presente.shape
    tratamentos = m.comparar_tratamentos()

    mapa_de_cor = ListedColormap([cor("--seg-destaque"), cor("--seg-secundaria")])
    mapa_de_cor.set_bad(cor("--seg-base"))

    fig = figura()
    eixo = fig.add_axes([0.10, 0.24, 0.87, 0.68])
    visivel = np.full(presente.shape, np.nan)
    imagem = eixo.imshow(visivel, aspect="auto", cmap=mapa_de_cor, vmin=0, vmax=1,
                         interpolation="nearest")
    eixo.set_yticks(range(n_ativos))
    eixo.set_yticklabels(fechamento.columns, fontsize=14)
    anos = sorted(set(fechamento.index.year))
    eixo.set_xticks([int(np.argmax(fechamento.index.year == ano)) for ano in anos])
    eixo.set_xticklabels([str(ano) for ano in anos])
    for lado in ("top", "right", "left", "bottom"):
        eixo.spines[lado].set_visible(False)
    legenda = fig.text(0.10, 0.06, "", fontsize=19, color=cor("--seg-texto"))

    gold = list(fechamento.columns).index("GOLD11")
    primeiro_gold = int(np.argmax(presente[gold] == 1))
    dia_falha = list(fechamento.index.strftime("%Y-%m-%d")).index("2025-10-24")
    por_ativo = FPS
    quadros_ativos = n_ativos * por_ativo
    total = quadros_ativos + 5 * FPS
    estado = {"destacado": False}

    def desenhar(i):
        linhas = min(n_ativos, i // por_ativo + 1)
        visivel[:linhas] = presente[:linhas]
        imagem.set_data(visivel)
        if i >= quadros_ativos and not estado["destacado"]:
            estado["destacado"] = True
            eixo.add_patch(Rectangle((-0.5, gold - 0.5), primeiro_gold, 1, fill=False,
                                     edgecolor=cor("--seg-primaria"), linewidth=2.5))
            eixo.axvline(dia_falha, color=cor("--seg-primaria"), linewidth=2, linestyle="--")
            legenda.set_text("GOLD11: %d pregões sem cotação antes de %s.\n"
                             "BOVA11, IVVB11 e GOLD11: sem cotação em 24/10/2025."
                             % (primeiro_gold, _data_br(fechamento.index[primeiro_gold])))
        if i >= quadros_ativos + 3 * FPS:
            legenda.set_text("Descartar as datas com ausência mantém %s dos %s pregões\n"
                             "e começa a série da cesta inteira em %s."
                             % (_milhar(tratamentos["pregoes_descartar"]),
                                _milhar(tratamentos["pregoes_total"]),
                                "/".join(reversed(tratamentos["inicio_descartar"].split("-")))))

    return gravar(fig, desenhar, total, "aula01-mapa-ausencias", total - 1)


def main():
    for gerar in (tres_visoes_mglu3, mapa_ausencias):
        mp4, poster = gerar()
        erros = violacoes(metadados(mp4))
        print("%s  %s" % (os.path.basename(mp4), "conforme" if not erros else "; ".join(erros)))
        if erros:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Gerar e conferir o contrato**

Run: `.venv/bin/python tools/animacoes_aula01.py`
Expected: `aula01-tres-visoes-mglu3.mp4  conforme` e `aula01-mapa-ausencias.mp4  conforme`.

- [ ] **Step 3: Conferir as imagens a olho**

Abrir os dois pôsteres com a ferramenta Read e conferir: texto legível, rótulos de evento sem sobreposição, legenda dentro da figura, nenhuma cor fora do tema. Extrair um quadro do meio de cada vídeo e conferir também:

```bash
ffmpeg -v error -ss 10 -i assets/video/aula01-tres-visoes-mglu3.mp4 -frames:v 1 /tmp/tres-visoes-10s.png
ffmpeg -v error -ss 8 -i assets/video/aula01-mapa-ausencias.mp4 -frames:v 1 /tmp/mapa-8s.png
```

Se um rótulo sobrepuser outro ou sair da figura, ajustar deslocamento ou limites e gerar de novo. Registrar no relatório o que foi visto.

- [ ] **Step 4: Commit**

```bash
git add tools/animacoes_aula01.py assets/video assets/img/aula01-*-poster.png
git commit -m "feat(aula01): animações das três visões de preço e do mapa de ausências

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 13: Widgets da Aula 01

**Files:**
- Create: `tools/dados_widgets_aula01.py`, `assets/js/widgets/tres-visoes.js`, `assets/js/widgets/ausencias.js`, `tools/tests/test_widgets_aula01.py`
- Create (gerados): `assets/data/aula01-tres-visoes.json`, `assets/data/aula01-ausencias.json`

**Interfaces:**
- Consumes: `medidas_aula01` (Task 11); runtime `IntelIWidgets` e CSS `.widget*` (Task 6).
- Produces:
  - `aula01-tres-visoes.json`: `{"datas": [str], "tickers": {TICKER: {"negociado": [num|null], "fechamento": [...], "ajustado": [...], "eventos": [{"data": str, "fator": num}], "leitura": str}}}` para MGLU3, B3SA3, WEGE3, BBAS3 e PETR4; séries alinhadas a `datas`.
  - `aula01-ausencias.json`: `{"pregoes_total": int, "ativos": [str], "ausentes": {TICKER: int}, "descartar": {"pregoes": int, "vol": {TICKER: num}, "leitura": str}, "preencher": {...}}`.
  - Widgets `tres-visoes` (atributos `data-largura`, `data-altura`, `data-inicial`) e `ausencias` (atributo `data-inicial`: `descartar` ou `preencher`).

- [ ] **Step 1: Escrever o teste que falha**

`tools/tests/test_widgets_aula01.py`:

```python
"""Os JSON dos widgets da Aula 01 repetem as medições travadas, sem número à mão."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula01 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def test_tres_visoes_tem_os_cinco_ativos_alinhados_as_datas():
    dados = _json("aula01-tres-visoes.json")
    assert len(dados["datas"]) == 1908
    assert sorted(dados["tickers"]) == ["B3SA3", "BBAS3", "MGLU3", "PETR4", "WEGE3"]
    for ticker, serie in dados["tickers"].items():
        for chave in ("negociado", "fechamento", "ajustado"):
            assert len(serie[chave]) == 1908, (ticker, chave)
        assert serie["leitura"]


def test_tres_visoes_repete_o_salto_medido_de_b3sa3():
    dados = _json("aula01-tres-visoes.json")
    i = dados["datas"].index("2021-05-17")
    b3 = dados["tickers"]["B3SA3"]
    assert (b3["negociado"][i - 1], b3["negociado"][i]) == (53.55, 17.58)
    assert "-67,17%" in b3["leitura"]
    assert "-1,51%" in b3["leitura"]


def test_leitura_da_petr4_cita_os_retornos_medidos():
    leitura = _json("aula01-tres-visoes.json")["tickers"]["PETR4"]["leitura"]
    assert "87,12%" in leitura
    assert "616,00%" in leitura


def test_ausencias_repete_os_tratamentos_medidos():
    dados = _json("aula01-ausencias.json")
    c = m.comparar_tratamentos()
    assert dados["pregoes_total"] == 1908
    assert dados["ausentes"] == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}
    assert dados["descartar"]["pregoes"] == 1423
    assert dados["preencher"]["pregoes"] == 1908
    for ativo in dados["ativos"]:
        assert dados["descartar"]["vol"][ativo] == round(float(c["vol_descartar"][ativo]), 4)
        assert dados["preencher"]["vol"][ativo] == round(float(c["vol_preencher"][ativo]), 4)
    assert "1.423" in dados["descartar"]["leitura"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_widgets_aula01.py -v`
Expected: FAIL com `FileNotFoundError` em `assets/data/aula01-tres-visoes.json`.

- [ ] **Step 3: Implementar o gerador dos JSON**

`tools/dados_widgets_aula01.py`:

```python
"""JSON dos widgets da Aula 01, a partir de tools/medidas_aula01.py.

Uso: .venv/bin/python tools/dados_widgets_aula01.py
Saída: assets/data/aula01-tres-visoes.json e assets/data/aula01-ausencias.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula01 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
TICKERS_VISOES = ["MGLU3", "B3SA3", "WEGE3", "BBAS3", "PETR4"]
ATIVOS_AUSENCIAS = ["BOVA11", "IVVB11", "GOLD11", "PETR4", "VALE3"]


def _pct(valor):
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _serie(valores):
    return [None if math.isnan(x) else round(float(x), 2) for x in valores]


def tres_visoes():
    fechamento = m.carregar_precos("precos_fechamento.csv")
    eventos = m.carregar_desdobramentos()
    saida = {"datas": [d.strftime("%Y-%m-%d") for d in fechamento.index], "tickers": {}}
    for ticker in TICKERS_VISOES:
        visoes = m.tres_visoes(ticker).reindex(fechamento.index)
        if ticker == "PETR4":
            leitura = ("PETR4 não tem evento de desdobramento no período. A distância entre Close "
                       "e Adj Close são os proventos: retorno de preço de %s e retorno total de %s."
                       % (_pct(m.retorno_no_periodo(visoes["fechamento"])),
                          _pct(m.retorno_no_periodo(visoes["ajustado"]))))
        else:
            data, variacao = m.maior_variacao_diaria(visoes["negociado"])
            no_close = visoes["fechamento"].dropna().pct_change().loc[data]
            leitura = ("%s em %s: o preço negociado varia %s e o Close do Yahoo, %s."
                       % (ticker, data.strftime("%d/%m/%Y"), _pct(variacao), _pct(no_close)))
        do_ticker = eventos[eventos["ticker"] == ticker]
        saida["tickers"][ticker] = {
            "negociado": _serie(visoes["negociado"]),
            "fechamento": _serie(visoes["fechamento"]),
            "ajustado": _serie(visoes["ajustado"]),
            "eventos": [{"data": d.strftime("%Y-%m-%d"), "fator": float(f)}
                        for d, f in zip(do_ticker["data"], do_ticker["fator"])],
            "leitura": leitura,
        }
    return saida


def ausencias():
    c = m.comparar_tratamentos()
    ausentes = m.ausencias()
    inicio = "/".join(reversed(c["inicio_descartar"].split("-")))
    return {
        "pregoes_total": c["pregoes_total"],
        "ativos": ATIVOS_AUSENCIAS,
        "ausentes": {t: int(ausentes[t]) for t in ausentes.index if ausentes[t] > 0},
        "descartar": {
            "pregoes": c["pregoes_descartar"],
            "vol": {t: round(float(c["vol_descartar"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Descartar mantém %s dos %s pregões e começa a cesta em %s, "
                        "sem março de 2020." % (_milhar(c["pregoes_descartar"]),
                                                 _milhar(c["pregoes_total"]), inicio)),
        },
        "preencher": {
            "pregoes": c["pregoes_preencher"],
            "vol": {t: round(float(c["vol_preencher"][t]), 4) for t in ATIVOS_AUSENCIAS},
            "leitura": ("Preencher mantém os %s pregões e dá retorno zero aos três ETFs em "
                        "24/10/2025; o pregão seguinte acumula os dois dias."
                        % _milhar(c["pregoes_preencher"])),
        },
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula01-tres-visoes.json", tres_visoes()), ("aula01-ausencias.json", ausencias())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
```

Run: `.venv/bin/python tools/dados_widgets_aula01.py`
Expected: dois arquivos gravados; `aula01-tres-visoes.json` abaixo de 400 KB.

- [ ] **Step 4: Rodar o teste dos JSON e ver passar**

Run: `.venv/bin/python -m pytest tools/tests/test_widgets_aula01.py -v`
Expected: 4 passed.

- [ ] **Step 5: Implementar os dois widgets**

`assets/js/widgets/tres-visoes.js`:

```js
// Três visões de preço de um ativo: negociado na data, Close do Yahoo (ajustado
// por desdobramento) e Adj Close (ajustado também por proventos). Botões escolhem
// o ativo, ligam ou desligam cada visão e alternam a escala logarítmica. Eventos
// corporativos aparecem como linhas tracejadas. Dados: tools/dados_widgets_aula01.py.
(function () {
  'use strict';

  var VISOES = [
    { chave: 'negociado', rotulo: 'Negociado', token: '--seg-destaque' },
    { chave: 'fechamento', rotulo: 'Close', token: '--seg-primaria' },
    { chave: 'ajustado', rotulo: 'Adj Close', token: '--seg-secundaria' }
  ];

  IntelIWidgets.registrar('tres-visoes', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 330);
    var tickers = Object.keys(dados.tickers);
    var estado = {
      ticker: elemento.dataset.inicial || tickers[0],
      ligadas: { negociado: true, fechamento: true, ajustado: true },
      log: true
    };

    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controles);
    elemento.appendChild(canvas);
    elemento.appendChild(leitura);

    function botao(texto, aoClicar) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = texto;
      b.addEventListener('click', aoClicar);
      controles.appendChild(b);
      return b;
    }

    var botoesTicker = tickers.map(function (t) {
      return botao(t, function () { estado.ticker = t; desenhar(); });
    });
    var botoesVisao = VISOES.map(function (v) {
      return botao(v.rotulo, function () { estado.ligadas[v.chave] = !estado.ligadas[v.chave]; desenhar(); });
    });
    var botaoLog = botao('Escala log', function () { estado.log = !estado.log; desenhar(); });

    function desenhar() {
      botoesTicker.forEach(function (b, i) { b.classList.toggle('ativo', tickers[i] === estado.ticker); });
      botoesVisao.forEach(function (b, i) { b.classList.toggle('ativo', estado.ligadas[VISOES[i].chave]); });
      botaoLog.classList.toggle('ativo', estado.log);

      var serie = dados.tickers[estado.ticker];
      var ctx = canvas.getContext('2d');
      var margem = { esquerda: 80, direita: 16, topo: 12, base: 34 };
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);

      var valores = [];
      VISOES.forEach(function (v) {
        if (!estado.ligadas[v.chave]) return;
        serie[v.chave].forEach(function (x) { if (x !== null) valores.push(x); });
      });
      if (!valores.length) {
        leitura.textContent = 'Ligue ao menos uma visão.';
        return;
      }
      var escala = estado.log ? Math.log : function (x) { return x; };
      var minimo = escala(Math.min.apply(null, valores));
      var maximo = escala(Math.max.apply(null, valores));
      var n = dados.datas.length;
      function px(i) { return margem.esquerda + (largura - margem.esquerda - margem.direita) * i / (n - 1); }
      function py(v) {
        return altura - margem.base - (altura - margem.topo - margem.base) * (escala(v) - minimo) / ((maximo - minimo) || 1);
      }

      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, margem.topo);
      ctx.lineTo(margem.esquerda, altura - margem.base);
      ctx.lineTo(largura - margem.direita, altura - margem.base);
      ctx.stroke();

      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(14, 400);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      var extremos = [Math.min.apply(null, valores), Math.max.apply(null, valores)];
      extremos.forEach(function (v) {
        ctx.fillText('R$ ' + v.toFixed(2).replace('.', ','), margem.esquerda - 8, py(v));
      });
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      var anoAnterior = '';
      dados.datas.forEach(function (d, i) {
        var ano = d.slice(0, 4);
        if (ano !== anoAnterior) {
          ctx.fillText(ano, px(i), altura - margem.base + 8);
          anoAnterior = ano;
        }
      });

      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = api.cor('--seg-borda');
      serie.eventos.forEach(function (evento) {
        var i = dados.datas.indexOf(evento.data);
        if (i < 0) return;
        ctx.beginPath();
        ctx.moveTo(px(i), margem.topo);
        ctx.lineTo(px(i), altura - margem.base);
        ctx.stroke();
      });
      ctx.setLineDash([]);

      VISOES.forEach(function (v) {
        if (!estado.ligadas[v.chave]) return;
        ctx.strokeStyle = api.cor(v.token);
        ctx.lineWidth = 2;
        ctx.beginPath();
        var aberto = false;
        serie[v.chave].forEach(function (x, i) {
          if (x === null) { aberto = false; return; }
          if (aberto) { ctx.lineTo(px(i), py(x)); } else { ctx.moveTo(px(i), py(x)); aberto = true; }
        });
        ctx.stroke();
      });

      leitura.textContent = serie.leitura;
    }

    desenhar();
  });
})();
```

`assets/js/widgets/ausencias.js`:

```js
// Descartar datas com ausência ou preencher para a frente: para cada tratamento,
// quantos pregões sobram e a volatilidade anual de cada ativo afetado. Dados:
// tools/dados_widgets_aula01.py.
(function () {
  'use strict';

  var OPCOES = [
    { chave: 'descartar', rotulo: 'Descartar datas (dropna)' },
    { chave: 'preencher', rotulo: 'Preencher para a frente (ffill)' }
  ];

  function porcentagem(valor) {
    return (valor * 100).toFixed(2).replace('.', ',') + '%';
  }

  IntelIWidgets.registrar('ausencias', function (elemento, dados) {
    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var tabela = document.createElement('table');
    tabela.className = 'widget-tabela';
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controles);
    elemento.appendChild(tabela);
    elemento.appendChild(leitura);

    var botoes = OPCOES.map(function (opcao) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = opcao.rotulo;
      b.addEventListener('click', function () { mostrar(opcao.chave); });
      controles.appendChild(b);
      return b;
    });

    function mostrar(chave) {
      botoes.forEach(function (b, i) { b.classList.toggle('ativo', OPCOES[i].chave === chave); });
      var tratamento = dados[chave];
      tabela.textContent = '';
      var cabecalho = tabela.insertRow();
      ['Ativo', 'Volatilidade anual'].forEach(function (texto) {
        var th = document.createElement('th');
        th.textContent = texto;
        cabecalho.appendChild(th);
      });
      dados.ativos.forEach(function (ativo) {
        var linha = tabela.insertRow();
        linha.insertCell().textContent = ativo;
        linha.insertCell().textContent = porcentagem(tratamento.vol[ativo]);
      });
      leitura.textContent = tratamento.leitura;
    }

    mostrar(elemento.dataset.inicial || 'descartar');
  });
})();
```

- [ ] **Step 6: Validar os widgets numa página de ensaio**

O servidor do validador serve só a raiz do repositório, então a página de ensaio fica versionada em `tools/tests/fixture_widgets_aula01.html` e carrega os dois widgets com os JSON reais:

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Ensaio dos widgets da Aula 01</title>
  <link rel="stylesheet" href="../../assets/css/inteli-brand.css">
  <link rel="stylesheet" href="../../assets/css/inteli-theme.css">
</head>
<body>
  <div class="widget" data-widget="tres-visoes" data-fonte="../../assets/data/aula01-tres-visoes.json"
       data-largura="1000" data-altura="330" data-inicial="B3SA3"></div>
  <div class="widget" data-widget="ausencias" data-fonte="../../assets/data/aula01-ausencias.json"
       data-inicial="descartar"></div>
  <script src="../../assets/js/inteli-widgets.js"></script>
  <script src="../../assets/js/widgets/tres-visoes.js"></script>
  <script src="../../assets/js/widgets/ausencias.js"></script>
</body>
</html>
```

Acrescentar a `tools/tests/test_check_widgets.py`:

```python
def test_widgets_da_aula01_montam_com_os_dados_reais(porta):
    r = _checar(porta, "fixture_widgets_aula01.html")
    assert (r["declarados"], r["medidos"]) == (2, 2)
    assert r["problemas"] == []
```

```bash
.venv/bin/python -m pytest tools/tests/test_check_widgets.py tools/tests/test_widgets_aula01.py -v
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
```

Expected: tudo verde.

- [ ] **Step 7: Conferir a interação no navegador**

Com `python3 -m http.server 8000` na raiz, abrir `http://localhost:8000/tools/tests/fixture_widgets_aula01.html` no navegador embutido, clicar em cada ticker, desligar e ligar cada visão, alternar a escala e os dois tratamentos. Conferir que o gráfico redesenha, que a leitura muda e que não há erro no console. Registrar no relatório.

- [ ] **Step 8: Commit**

```bash
git add tools/dados_widgets_aula01.py assets/data/aula01-*.json assets/js/widgets/tres-visoes.js assets/js/widgets/ausencias.js tools/tests/test_widgets_aula01.py tools/tests/fixture_widgets_aula01.html tools/tests/test_check_widgets.py
git commit -m "feat(aula01): widgets das três visões de preço e dos tratamentos de ausência

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 14: Notebook da Aula 01

**Files:**
- Create: `notebooks/aula01.ipynb`, `tools/tests/test_notebooks.py`

**Interfaces:**
- Consumes: CSVs de `dados/` (Task 4); os números de `tools/tests/test_aula01.py` (Task 11), que o notebook reproduz.
- Produces: `notebooks/aula01.ipynb`, citado pelo deck (Task 15), pelo material e pelo portal (Task 16). Funções definidas no notebook e reusadas pelos alunos no A1: `ler_csv(nome, **kwargs)`, `coletar(tickers, inicio, fim)`, `preco_negociado(fechamento, eventos, ticker)`.

- [ ] **Step 1: Escrever o teste estrutural que falha**

`tools/tests/test_notebooks.py`:

```python
"""Estrutura comum dos notebooks: badge do Colab, carga com queda para a URL bruta e nenhuma saída gravada."""
import glob
import json
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTEBOOKS = sorted(glob.glob(os.path.join(RAIZ, "notebooks", "aula*.ipynb")))
COLAB = "https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/%s"
BRUTA = "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/"


def test_existe_ao_menos_um_notebook():
    assert NOTEBOOKS, "nenhum notebook em notebooks/"


@pytest.mark.parametrize("caminho", NOTEBOOKS, ids=os.path.basename)
def test_notebook_segue_o_contrato(caminho):
    with open(caminho, encoding="utf-8") as fh:
        nb = json.load(fh)
    primeira = "".join(nb["cells"][0]["source"])
    assert nb["cells"][0]["cell_type"] == "markdown"
    assert COLAB % os.path.basename(caminho) in primeira
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    assert BRUTA in codigo
    assert "M08_OFFLINE" in codigo
    for celula in nb["cells"]:
        if celula["cell_type"] == "code":
            assert celula.get("outputs") == [], "saída gravada em %s" % os.path.basename(caminho)
            assert celula.get("execution_count") is None
    texto = json.dumps(nb, ensure_ascii=False)
    assert chr(0x2014) not in texto
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/bin/python -m pytest tools/tests/test_notebooks.py -v`
Expected: FAIL em `test_existe_ao_menos_um_notebook`.

- [ ] **Step 3: Montar o notebook com nbformat**

Montar com um script descartável em `/tmp/gerar_aula01.py` que usa `nbformat.v4.new_notebook`, `new_markdown_cell` e `new_code_cell`, com `metadata` igual à do M03 (`kernelspec` python3) e grava `notebooks/aula01.ipynb`. Só o `.ipynb` é commitado. Células, nesta ordem:

1. **Markdown**: `# Aula 01 - Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível`; linha "Módulo 08 AdmTech, Computação · Semana 1 · Sprint 1 · Prof. José Romualdo"; badge `[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula01.ipynb)`; seção "O que este notebook é": laboratório da Aula 01, que alimenta o A1; roda no Colab ou local; sem rede, lê o snapshot de `dados/`.
2. **Markdown**: `## 1. A cesta e onde os dados moram`, com os 15 tickers e a janela.
3. **Código**:

```python
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DADOS_LOCAL = os.path.join("..", "dados")
DADOS_BRUTOS = "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/"
TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3",
           "SUZB3", "RENT3", "B3SA3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"]
INICIO, FIM = "2019-01-01", "2026-08-31"


def ler_csv(nome, **kwargs):
    """Lê um CSV de dados/: do disco quando o repositório está clonado, da URL bruta no Colab."""
    local = os.path.join(DADOS_LOCAL, nome)
    return pd.read_csv(local if os.path.exists(local) else DADOS_BRUTOS + nome, **kwargs)
```

4. **Markdown**: `## 2. Um coletor que outra pessoa consegue rodar`: por que parametrizar tickers e datas; por que ter queda para o snapshot; `yfinance` trata o fim como exclusivo.
5. **Código**:

```python
def coletar(tickers, inicio, fim):
    """Close e Adj Close dos tickers entre inicio e fim, inclusive.

    Tenta o yfinance ao vivo; sem rede, sem yfinance ou com M08_OFFLINE=1, lê o
    snapshot versionado em dados/. Devolve (fechamento, ajustado, origem).
    """
    if os.environ.get("M08_OFFLINE") != "1":
        try:
            import yfinance as yf

            fim_exclusivo = (pd.Timestamp(fim) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            bruto = yf.download([t + ".SA" for t in tickers], start=inicio, end=fim_exclusivo,
                                auto_adjust=False, progress=False, group_by="column",
                                threads=False, timeout=20)
            if not bruto.empty:
                renomear = lambda coluna: coluna.removesuffix(".SA")
                fechamento = bruto["Close"].rename(columns=renomear)[tickers]
                ajustado = bruto["Adj Close"].rename(columns=renomear)[tickers]
                return fechamento, ajustado, "yfinance, ao vivo"
        except Exception as erro:
            print("coleta ao vivo falhou, seguindo com o snapshot:", type(erro).__name__)
    fechamento = ler_csv("precos_fechamento.csv", index_col="data", parse_dates=["data"])
    ajustado = ler_csv("precos_ajustados.csv", index_col="data", parse_dates=["data"])
    return fechamento.loc[inicio:fim, tickers], ajustado.loc[inicio:fim, tickers], "snapshot de dados/"


fechamento, ajustado, origem = coletar(TICKERS, INICIO, FIM)
print("origem:", origem)
print("pregões:", len(fechamento), "de", fechamento.index[0].date(), "a", fechamento.index[-1].date())
```

6. **Markdown**: `## 3. Três visões do mesmo preço`: negociado, Close e Adj Close, e a pergunta que cada uma responde.
7. **Código**:

```python
eventos = ler_csv("eventos_desdobramento.csv", parse_dates=["data"])


def preco_negociado(fechamento, eventos, ticker):
    """Close multiplicado pelos fatores dos eventos posteriores a cada data."""
    serie = fechamento[ticker].dropna()
    fator = np.ones(len(serie))
    do_ticker = eventos[eventos["ticker"] == ticker]
    for data, f in zip(do_ticker["data"], do_ticker["fator"]):
        fator = fator * np.where(serie.index < data, f, 1.0)
    return serie * fator


visoes = pd.DataFrame({
    "negociado": preco_negociado(fechamento, eventos, "MGLU3"),
    "Close": fechamento["MGLU3"],
    "Adj Close": ajustado["MGLU3"],
})
eixo = visoes.plot(logy=True, figsize=(11, 4), title="MGLU3: três visões de preço")
eixo.set_ylabel("R$ por ação (escala log)")
plt.show()
```

8. **Código**:

```python
for ticker in ["B3SA3", "MGLU3"]:
    negociado = preco_negociado(fechamento, eventos, ticker).pct_change().dropna()
    close = fechamento[ticker].dropna().pct_change().dropna()
    dia = negociado.abs().idxmax()
    print("%s em %s: negociado %+.2f%%, Close %+.2f%%" % (ticker, dia.date(), 100 * negociado[dia], 100 * close[dia]))
```

9. **Markdown**: "Pergunta para a dupla": qual visão responde a cada uma das quatro perguntas do slide de escolha, com a resposta escondida num `<details>`.
10. **Código**:

```python
for ticker in ["PETR4", "BBAS3", "BOVA11"]:
    preco = fechamento[ticker].dropna()
    total = ajustado[ticker].dropna()
    print("%s: retorno de preço %+.2f%%, retorno total %+.2f%%"
          % (ticker, 100 * (preco.iloc[-1] / preco.iloc[0] - 1), 100 * (total.iloc[-1] / total.iloc[0] - 1)))
```

11. **Markdown**: `## 4. Ausências reais do provedor`.
12. **Código**:

```python
vazios = fechamento.isna().sum()
print(vazios[vazios > 0])
print("primeira cotação do GOLD11:", fechamento["GOLD11"].first_valid_index().date())
print("ativos sem cotação em 24/10/2025:", list(fechamento.columns[fechamento.loc["2025-10-24"].isna()]))
```

13. **Código**:

```python
def volatilidade_anual(precos):
    return precos.pct_change(fill_method=None).std() * np.sqrt(252)


descartar = ajustado.dropna()
preencher = ajustado.ffill()
comparacao = pd.DataFrame({
    "descartar (dropna)": volatilidade_anual(descartar),
    "preencher (ffill)": volatilidade_anual(preencher),
}).loc[["BOVA11", "IVVB11", "GOLD11", "PETR4", "VALE3"]]
print("pregões mantidos: dropna %d, ffill %d, de %d" % (len(descartar), len(preencher), len(ajustado)))
print("a série do dropna começa em", descartar.index[0].date())
(100 * comparacao).round(2)
```

14. **Markdown**: `## 5. Registre a decisão`: link do modelo de ADR (`https://gist.github.com/josercf/fc714afe20773401dc9d56f65174b441`); o ADR do grupo precisa citar o número que muda com a escolha, medido na célula anterior.
15. **Markdown**: `## 6. Desafio para o A1`: (a) trocar a cesta pelos tickers do grupo e rodar `coletar`; (b) escrever no SPEC.md três casos de teste com resultado esperado, sendo um com os dados do grupo; (c) completar a célula seguinte.
16. **Código**:

```python
# Verificações mínimas de reprodutibilidade. Acrescente as do SPEC.md do grupo.
assert fechamento.index.is_monotonic_increasing, "datas fora de ordem"
assert not fechamento.index.duplicated().any(), "data repetida"
assert (fechamento.min() > 0).all(), "preço não positivo"  # min() ignora as ausências
print("verificações ok")
```

- [ ] **Step 4: Executar sem rede e com rede**

```bash
mkdir -p /tmp/nb
M08_OFFLINE=1 .venv/bin/jupyter nbconvert --to notebook --execute --output-dir /tmp/nb notebooks/aula01.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir /tmp/nb-rede notebooks/aula01.ipynb
.venv/bin/python -m pytest tools/tests/test_notebooks.py -v
```

Expected: as duas execuções terminam sem erro; na offline, a saída da célula 5 diz `origem: snapshot de dados/` e `pregões: 1908`; os números impressos nas células 8, 10, 12 e 13 batem com `tools/tests/test_aula01.py` (B3SA3 -67,17% e -1,51%; PETR4 +87,12% e +616,00%; 1.423 pregões; PETR4 33,41% e 39,25%). O teste estrutural passa. O arquivo em `notebooks/` continua sem saída.

- [ ] **Step 5: Commit**

```bash
git add notebooks/aula01.ipynb tools/tests/test_notebooks.py
git commit -m "feat(aula01): notebook com coletor reproduzível, três visões de preço e ausências

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 15: Deck da Aula 01

**Files:**
- Create: `aulas/aula01.html`

**Interfaces:**
- Consumes: `aulas/_fixture-tema.html` (markup de cada classe); vídeos e pôsteres (Task 12); widgets e JSON (Task 13); notebook (Task 14); `PLANEJAMENTO_AULA_A_AULA.md`, Aula 01 (Task 7); números de `tools/tests/test_aula01.py` (Task 11).
- Produces: o deck que o portal e o material citam.

Executor recomendado: agente `construtor-aulas`, com leitura das skills `inteli-course-design` e `inteli-deck-design` e desta task inteira antes da primeira linha.

- [ ] **Step 1: Escrever o deck**

Cabeçalho e rodapé técnico copiados de `aulas/_fixture-tema.html` (CSS de Reveal, marca, tema e impressão; `Reveal.initialize` com `width: 1280, height: 720, center: false, margin: 0, hash: true, slideNumber: false, transition: 'fade'`). Scripts no fim, nesta ordem: `inteli-quiz.js`, `inteli-zoom.js`, `inteli-print.js`, `inteli-cronometro.js`, `inteli-escolha.js`, `inteli-widgets.js`, `widgets/tres-visoes.js`, `widgets/ausencias.js`. Comentário HTML no topo com a divisão dos 105 minutos por bloco e os slides de cada bloco. Rodapé de cada slide: `Módulo 08 AdmTech &middot; Aula 01 &middot; Sprint 1` e número sequencial.

Slides, nesta ordem. Os títulos analíticos abaixo são a redação de partida; o `check_slides.py` decide a largura, e ao reprovar encurta-se mantendo o número.

| # | Classe | Título | Conteúdo obrigatório |
|---|---|---|---|
| 1 | `cover-slide` | Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível | eyebrow `Módulo 08 AdmTech &middot; Computação &middot; Semana 1`; subtítulo com a Sprint 1 |
| 2 | `content-slide` | Agenda do encontro | tabela dos sete blocos com duração de 15 minutos e o tema de cada um; nota "horários a confirmar na Adalove" |
| 3 | `content-slide` | O parceiro precisa decidir onde alocar o excedente de caixa | abertura do módulo no lugar do resgate (primeira aula): a ferramenta de carteira eficiente e o que cada sprint entrega |
| 4 | `content-slide` | Entregas de Computação por sprint | tabela A1 a A5 com sprint, entrega e peso "a confirmar", destacando o A1 |
| 5 | `quiz-slide` | Verificação do preparo | Peer Instruction em dois tempos (votar, discutir em dupla, votar de novo): "No primeiro pregão de 2019, quanto o Adj Close da PETR4 vale em relação ao Close?" Opções 100%, 86%, 52% e 26%; certa 26%; mensagens de feedback citando que 100% é o BOVA11, 86% o SUZB3 e 52% a VALE3 |
| 6 | `content-slide` | Proventos fazem o Adj Close da PETR4 valer 26% do Close em 2019 | tabela retorno de preço contra retorno total: PETR4 87,12% e 616,00%; VALE3 52,38% e 189,86%; BBAS3 -14,65% e 42,09%; BOVA11 98,84% nos dois |
| 7 | `section-slide` | Três visões do mesmo preço | |
| 8 | `content-slide` | O grupamento da MGLU3 aparece como alta de 896% no preço negociado | vídeo `aula01-tres-visoes-mglu3` com pôster; instrução "prever antes de tocar": o que acontece com cada linha em 27/05/2024 |
| 9 | `content-slide` | Três visões de preço e a pergunta que cada uma responde | tabela: visão, como é obtida, pergunta de negócio que responde |
| 10 | `content-slide` | O desdobramento da B3SA3 derruba o preço negociado em 67,17% | widget `tres-visoes` com `data-inicial="B3SA3"`, `data-largura="1000"`, `data-altura="300"`; pergunta disparada: e a WEGE3 em 28/04/2021? |
| 11 | `content-slide` com cronômetro | Qual visão responde a cada pergunta | escolha coletiva com quatro itens e as opções Negociado, Close e Adj Close: quanto R$ 1.000 em PETR4 em 2019 viraram com proventos (Adj Close); preço na tela do home broker em 14/05/2021 (Negociado); volatilidade anual para o otimizador (Adj Close); valor de mercado da empresa no dia (Negociado); cronômetro de 4 minutos |
| 12 | `section-slide` | Um coletor que outra pessoa consegue rodar | |
| 13 | `content-slide` | A função coletar cai para o snapshot quando a rede falha | código de `coletar` com `code-compact`, no máximo 18 linhas, e três marcas: parâmetros, queda para o snapshot, fim exclusivo do yfinance |
| 14 | `exercise-slide` com cronômetro | Prática em dupla: o coletor | `exercise-steps` para as seções 1 e 2 do notebook, condutor e navegador; cronômetro de 12 minutos; link do Colab |
| 15 | `section-slide` | Ausências reais do provedor | |
| 16 | `content-slide` | Três ETFs ficaram sem cotação em 24/10/2025 | vídeo `aula01-mapa-ausencias` com pôster; GOLD11 com 484 pregões vazios antes de 11/12/2020 |
| 17 | `content-slide` | Descartar datas mantém 1.423 dos 1.908 pregões | widget `ausencias` com `data-inicial="descartar"`; pergunta disparada: o que sumiu da série junto com esses pregões? |
| 18 | `content-slide` | Descartar datas tira março de 2020 e baixa a volatilidade da PETR4 para 33,41% | tabela das volatilidades dos cinco ativos sob os dois tratamentos; o retorno zero do BOVA11 em 24/10/2025 e os 0,93% acumulados em 27/10/2025 com o preenchimento |
| 19 | `content-slide` | O ADR registra a decisão com o número que ela muda | exemplo de ADR curto sobre o tratamento de ausências citando 39,25% e 33,41%; link do modelo no gist |
| 20 | `exercise-slide` com cronômetro | Prática em dupla: ausências e o primeiro ADR | seções 3 e 4 do notebook; cronômetro de 12 minutos |
| 21 | `quiz-slide` | Quiz de verificação | três perguntas: a variação de 17/05/2021 na B3SA3 (desdobramento de 3 para 1, com os distratores queda de mercado, erro do provedor e proventos); qual tratamento tira março de 2020 da PETR4 (dropna na cesta inteira); qual coluna usar para volatilidade (Adj Close) |
| 22 | `exercise-slide` | Notebook da aula | link do notebook no GitHub e badge do Colab; o que cada seção entrega; o desafio do A1 |
| 23 | `content-slide` | Artefato A1 da Sprint 1 | entrega, peso 3 "a confirmar na Adalove", SPEC.md antes de codar, ADR individual com 20% da nota, review com data a confirmar, e o que a Aula 02 vai pedir |
| 24 | `content-slide` | Referências | lista numerada das fontes citadas com `[N]` nos slides: `dados/README.md`, os dois autoestudos, a documentação do yfinance, a do pandas sobre dados ausentes, as páginas do SGS do Banco Central, o modelo de ADR e o MADR |
| 25 | `end-slide` | Até a Semana 3 | Aula 02: Dados Financeiros, Do Preço ao Retorno; Prof. José Romualdo |

Markup de vídeo:

```html
<video class="video-slide" controls muted playsinline preload="metadata"
       poster="../assets/img/aula01-tres-visoes-mglu3-poster.png">
  <source src="../assets/video/aula01-tres-visoes-mglu3.mp4" type="video/mp4">
</video>
```

- [ ] **Step 2: Validar**

```bash
.venv/bin/python tools/check_slides.py aulas/aula01.html
.venv/bin/python tools/check_widgets.py aulas/aula01.html
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
.venv/bin/python -m pytest tools/tests -v
grep -o '<p class="footer-page">[0-9]*</p>' aulas/aula01.html
```

Expected: layout sem estouro, sobreposição ou título no logo; `Widgets: 2 montado(s) em 1 deck(s)`; marca e links limpos; pytest inteiro verde, agora com os vídeos referenciados; rodapés em sequência.

- [ ] **Step 3: Conferir o estado depois da interação**

No navegador embutido, com `python3 -m http.server 8000`: responder os dois quizzes, clicar nas quatro escolhas, tocar os dois vídeos, operar os dois widgets e disparar os cronômetros. Conferir que nada sai dos 1280x720 e que as cores de estado aparecem. Registrar no relatório.

- [ ] **Step 4: Revisão**

Acionar o agente `revisor-slides` sobre `aulas/aula01.html`. Corrigir todo achado de layout, marca, número e regra de escrita antes do commit.

- [ ] **Step 5: Commit**

```bash
git add aulas/aula01.html
git commit -m "feat(aula01): deck com verificação do preparo, vídeos, widgets e escolha coletiva

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---
### Task 16: Material, referências, notas, ADR e portal da Aula 01

**Files:**
- Create: `materiais/aula01.html`, `referencias/aula01.html`, `docs/notas-do-professor/aula01.md`, `docs/adrs/ADR-007-escopo-da-aula-01.md`
- Modify: `index.html` (card `aula-01`), `docs/ANDAMENTO.md`, `PLANEJAMENTO_AULA_A_AULA.md` (só se a construção mudou algum bloco)

**Interfaces:**
- Consumes: tudo das Tasks 11 a 15; `$M03/materiais/aula12.html` e `$M03/referencias/aula12.html` como modelo de marcação (`doc`, `doc-header`, `doc-toc`, `doc-conteudo`, `doc-secao`, `doc-nota`, `doc-referencias`, `doc-porque`).
- Produces: a Aula 01 completa e publicada, padrão-ouro das Aulas 02 a 06.

- [ ] **Step 1: Material de apoio**

`materiais/aula01.html`, com `inteli-brand.css` e `inteli-material.css`, TOC lateral e estas seções:

1. **Preparação antes do encontro** (sala invertida, primeiro tempo): tempo total dentro de 2h; os dois autoestudos com título exato; o vídeo `aula01-tres-visoes-mglu3` com três perguntas para responder assistindo; o vídeo `aula01-mapa-ausencias` com duas perguntas; autoverificação de cinco perguntas com resposta comentada dentro de `<details>` (razão Adj Close sobre Close da PETR4; por que o Close não salta em 17/05/2021; o que é o preço negociado; quantos pregões o dropna mantém; que número um ADR sobre ausências precisa citar).
2. **O que o parceiro precisa dos dados**.
3. **Três visões de preço e a pergunta que cada uma responde**: tabela e o caso MGLU3.
4. **Como o preço negociado é reconstruído**: a fórmula, o exemplo B3SA3 de 14/05/2021 (R$ 53,55) e 17/05/2021 (R$ 17,58), e o erro `<=` no lugar de `<` explicado como o erro mais provável de quem implementa.
5. **Proventos e retorno total**: PETR4, VALE3, BBAS3 (preço cai 14,65% e retorno total sobe 42,09%) e os ETFs sem distribuição.
6. **Ausências reais do provedor**: GOLD11 e 24/10/2025.
7. **Descartar ou preencher**: o que cada escolha faz com a janela e com a volatilidade, com a tabela dos cinco ativos e o efeito de março de 2020.
8. **Reprodutibilidade**: coleta ao vivo com queda para o snapshot e o fim exclusivo do yfinance.
9. **O que o grupo entrega no A1**: SPEC.md antes do código, ADR individual com número, README.
10. **Escopo das conclusões**: janela de 02/01/2019 a 31/08/2026, cesta de referência, classificação dos eventos inferida do fator.

Todo número desta página está em `tools/tests/test_aula01.py`. Comentário HTML no topo dizendo isso.

- [ ] **Step 2: Referências**

`referencias/aula01.html`, com as duas seções fixas:

1. **Autoestudos da semana**: os dois títulos exatos de `docs/autoestudos-por-semana.md`, Semana 01, com referência bibliográfica e link copiados do REVISAO, e um parágrafo dizendo que a lista é provisória até a Adalove da turma 2026-2B ser lida.
2. **Leitura complementar do professor**, numerada: documentação do yfinance; guia do pandas sobre dados ausentes; páginas das séries 12, 432, 433 e 1 no portal de dados abertos do Banco Central; página de ajuda do Yahoo sobre preço ajustado; MADR; o modelo de ADR do curso no gist. Cada link é conferido antes de entrar com `curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n" URL`, e só entra a URL final com código 200.

- [ ] **Step 3: Notas do professor**

`docs/notas-do-professor/aula01.md`, no formato do `$M03/docs/notas-do-professor/aula12.md`: onde está o peso da aula (o slide 18, com o dropna tirando março de 2020); checkpoint de abertura (Colab abrindo e autoestudo feito); para cada um dos sete blocos, as perguntas socráticas com resposta esperada e erro comum; ordem de corte se o tempo apertar (cortar primeiro o slide 19, depois reduzir a segunda prática para 8 minutos); os números que a turma precisa sair sabendo.

- [ ] **Step 4: ADR-007**

`docs/adrs/ADR-007-escopo-da-aula-01.md`, no modelo da Task 8. Decisão: "A Aula 01 ensina coleta a partir de três visões de preço e das ausências reais do provedor, com o preço negociado reconstruído dos eventos do Yahoo." Contexto: o `Close` do Yahoo já vem ajustado, então o falso colapso previsto na spec só aparece no preço reconstruído. Motivações, riscos (classificação de evento inferida; a coleta ao vivo pode divergir do snapshot) e consequências. Relacionadas: 003, 004, 005.

- [ ] **Step 5: Portal e andamento**

No card `aula-01` de `index.html`, trocar os quatro botões desabilitados por:

```html
              <a class="botao" href="aulas/aula01.html"><span class="material-symbols-outlined" aria-hidden="true">slideshow</span>Slides</a>
              <a class="botao" href="materiais/aula01.html"><span class="material-symbols-outlined" aria-hidden="true">menu_book</span>Material</a>
              <a class="botao" href="referencias/aula01.html"><span class="material-symbols-outlined" aria-hidden="true">link</span>Referências</a>
              <a class="botao" href="https://github.com/josercf/2026-2B-M08/blob/main/notebooks/aula01.ipynb" target="_blank" rel="noopener"><span class="material-symbols-outlined" aria-hidden="true">code</span>Notebook</a>
```

Em `docs/ANDAMENTO.md`, mover a Aula 01 para **Pronto** com os achados medidos e registrar o que a construção revelou.

- [ ] **Step 6: Validação completa**

```bash
.venv/bin/python -m pytest tools/tests -v
.venv/bin/python tools/check_brand.py
.venv/bin/python tools/check_links.py
.venv/bin/python tools/check_slides.py aulas/_fixture-tema.html aulas/aula01.html
.venv/bin/python tools/check_widgets.py aulas/_fixture-tema.html aulas/aula01.html
M08_OFFLINE=1 .venv/bin/jupyter nbconvert --to notebook --execute --output-dir /tmp/nb notebooks/aula01.ipynb
grep -rln $'\u2014' --include=*.html --include=*.md --include=*.py --include=*.js --include=*.css . | grep -v "^./.venv" && echo "ACHOU TRAVESSÃO" || echo "sem travessão"
```

Expected: tudo verde e `sem travessão`. Conferir responsividade do material e das referências em 390px de largura pelo navegador embutido, comparando `document.documentElement.scrollWidth` com `clientWidth`.

- [ ] **Step 7: Commit e publicação**

```bash
git add materiais/aula01.html referencias/aula01.html docs/notas-do-professor/aula01.md docs/adrs/ADR-007-escopo-da-aula-01.md index.html docs/ANDAMENTO.md PLANEJAMENTO_AULA_A_AULA.md
git commit -m "feat(aula01): material com preparação pré-aula, referências, notas e portal

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push origin main
```

Esperar os dois workflows com `gh run watch <id> --repo josercf/2026-2B-M08 --exit-status`. Expected: `success` nos dois e `https://josercf.github.io/2026-2B-M08/aulas/aula01.html` respondendo 200.

---

## Depois deste plano

Com a Aula 01 publicada e revisada pelo professor, escrever `docs/superpowers/plans/AAAA-MM-DD-aulas-02-a-06.md` no mesmo formato das Tasks 11 a 16, uma aula por vez, com as medições de cada aula feitas antes do primeiro slide e o `PLANEJAMENTO_AULA_A_AULA.md` atualizado com os números delas.
