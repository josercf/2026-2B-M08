# Módulo 08 AdmTech, Imersão no mercado financeiro

Acervo de Computação do módulo, com os decks, materiais de apoio, páginas de referências e
notebooks dos seis Encontros de Instrução. Este documento é para o aluno; quem for editar o
repositório começa pelo `CLAUDE.md`.

## O módulo

| Campo | Valor |
|---|---|
| Módulo | LBL 08 AdmTech, Imersão no mercado financeiro |
| Turma | 2026-2B |
| Professor de Computação | Prof. José Romualdo |
| Início | 14/10/2026 |
| Duração | 10 semanas, 5 sprints, 6 Encontros de Instrução de Computação |
| Entregas de Computação | 5 artefatos COM, um por sprint, e 2 atividades ponderadas de 3 pontos |

Datas, semanas e pesos foram conferidos em 13/10/2026 contra a Adalove da turma 2026-2B-T19. O
horário de relógio das aulas segue a confirmar. O `PLANO_DE_ENSINO.md` lista as pendências de P1 a
P7.

## O parceiro do case

O projeto do módulo é uma ferramenta de simulação de carteira eficiente para um parceiro que
precisa decidir onde alocar excedentes de caixa. A ferramenta calcula a Fronteira Eficiente de
Markowitz e apresenta o resultado a quem decide.

O parceiro é o BTG Pactual, segundo as anotações dos checkpoints de planejamento do módulo. As
premissas detalhadas estão no LBL da Adalove, ainda não lido. Até lá, as aulas trabalham sobre uma cesta de referência de 15
ativos negociados na B3, com séries do Banco Central como taxas de referência. O snapshot está
versionado em `dados/`, com o detalhamento em `dados/README.md`.

## As seis instruções de Computação

Fonte oficial: `PLANO_DE_ENSINO.md` e `PLANEJAMENTO_AULA_A_AULA.md`. Divergência de data ou de
título entre esta tabela e a Adalove é erro deste README.

| Acervo | Data | Semana | Sprint | Instrução | Entrega que a aula alimenta |
|---|---|---|---|---|---|
| aula01 | 20/10/2026 | 2 | 1 | Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível | A1 Coletor e Processador de Dados de Mercado |
| aula02 | 05/11/2026 | 4 | 2 | Dados Financeiros: Do Preço ao Retorno | A2 Módulo de Análise de Risco e Retorno Individual |
| aula03 | 10/11/2026 | 5 | 3 | Correlação, Covariância e o Argumento Matemático da Diversificação | A3 Motor de Simulação de Monte Carlo e Ponderada 1 |
| aula04 | 18/11/2026 | 6 | 3 | Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz | A3 e a base matemática do A4 |
| aula05 | 01/12/2026 | 8 | 4 | Validação e Robustez do Modelo | A4 Otimizador de Carteira com Fronteira Eficiente e Ponderada 2 |
| aula06 | 16/12/2026 | 10 | 5 | Do Script ao Produto: React, FastAPI e Interpretação com LLM | A5 Simulador Interativo integrado à interface e Interpretação por LLM |

Os pesos de cada entrega, com a marca de confirmação, estão no `PLANO_DE_ENSINO.md`, seção 5. A
numeração `aula01` a `aula06` é a do acervo; a planilha do módulo numera as mesmas aulas como 5,
13, 22, 28, 38 e 43, e o portal mostra os dois números.

## Como cada aula funciona

O encontro pressupõe o preparo feito. Antes da aula, você faz os dois autoestudos da semana na
Adalove, assiste às animações curtas da seção "Preparação" do material de apoio e responde uma
autoverificação de cinco perguntas sem nota. O encontro tem 2 horas: 15 minutos de daily da equipe
e 105 minutos em sete blocos de até 15 minutos, começando por uma votação sobre o conteúdo do
preparo e alternando demonstração sobre dado real, widget interativo no deck e prática em dupla no
notebook. Depois da aula, o material de apoio, o notebook e o slide de amarração indicam o que
avança no artefato da sprint, o desafio do notebook e a leitura complementar.

## Estrutura de pastas

```
.
├── index.html                     portal com um card por instrução, por sprint (a construir)
├── README.md                      este documento, para o aluno
├── CLAUDE.md                      guia de quem edita o acervo
├── PLANO_DE_ENSINO.md             case, dados, cronograma, entregas e pendências (fonte da verdade)
├── PLANEJAMENTO_AULA_A_AULA.md    roteiro em sete blocos de cada encontro (fonte da verdade)
├── aulas/                         um deck Reveal.js por aula (aula01 a aula06)
├── materiais/                     material de apoio, com preparação pré-aula
├── referencias/                   autoestudos da semana e leitura complementar
├── notebooks/                     laboratório executável de cada aula, com badge do Colab
├── exemplos/aula06-api-carteira/  API FastAPI e interface React da Aula 06
├── dados/                         snapshot da B3 e séries do Banco Central, com README próprio
├── assets/                        CSS, JS, imagens e JSON dos decks, com os vídeos em assets/video
└── docs/
    ├── autoestudos-por-semana.md  autoestudos e instruções por semana, com título exato
    ├── adrs/                      decisões de arquitetura do acervo
    └── ANDAMENTO.md               o que está pronto, o que está em andamento e o que falta
```

O portal `index.html` e as pastas `materiais/`, `referencias/`, `notebooks/` e `exemplos/` ainda
não existem, e `aulas/` tem por enquanto apenas o deck de referência do tema
(`_fixture-tema.html`). Eles nascem conforme cada aula é construída, e nem toda aula vai ter os
quatro artefatos publicados ao mesmo tempo. O estado atual está em `docs/ANDAMENTO.md`.

## Portal

O endereço do portal é <https://josercf.github.io/2026-2B-M08/>. A publicação no GitHub Pages
ainda não está configurada (ver `docs/ANDAMENTO.md`). Para abrir o acervo localmente, sirva a raiz
do repositório por HTTP, porque os decks usam caminhos relativos para `assets/`:

```bash
python3 -m http.server 8000
```
