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

As datas e os horários das aulas dependem da Adalove da turma, que ainda não foi lida. Toda data
aparece como "a confirmar na Adalove" no acervo, e o mesmo vale para os pesos das entregas, que
estão citados da revisão de junho de 2026. O `PLANO_DE_ENSINO.md` lista essas pendências de P1 a
P7.

## O parceiro do case

O projeto do módulo é uma ferramenta de simulação de carteira eficiente para um parceiro que
precisa decidir onde alocar excedentes de caixa. A ferramenta calcula a Fronteira Eficiente de
Markowitz e apresenta o resultado a quem decide.

O nome e as premissas do parceiro estão descritos no LBL da Adalove, que ainda não foi lido, e por
isso aparecem como "a confirmar". Até lá, as aulas trabalham sobre uma cesta de referência de 15
ativos negociados na B3, com séries do Banco Central como taxas de referência. O snapshot está
versionado em `dados/`, com o detalhamento em `dados/README.md`.

## As seis instruções de Computação

Fonte oficial: `PLANO_DE_ENSINO.md` e `PLANEJAMENTO_AULA_A_AULA.md`. Divergência de data ou de
título entre esta tabela e a Adalove é erro deste README.

| Acervo | Data | Semana | Sprint | Instrução | Entrega que a aula alimenta |
|---|---|---|---|---|---|
| aula01 | a confirmar na Adalove | 1 | 1 | Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível | A1 Coletor e Processador de Dados de Mercado |
| aula02 | a confirmar na Adalove | 3 | 2 | Dados Financeiros: Do Preço ao Retorno | A2 Módulo de Análise de Risco e Retorno Individual |
| aula03 | a confirmar na Adalove | 5 | 3 | Correlação, Covariância e o Argumento Matemático da Diversificação | A3 Motor de Simulação de Monte Carlo e Ponderada 1 |
| aula04 | a confirmar na Adalove | 6 | 3 | Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz | A3 e a base matemática do A4 |
| aula05 | a confirmar na Adalove | 8 | 4 | Do Script ao Produto: API em FastAPI e Página Web | A4 Otimizador de Carteira com Fronteira Eficiente em Aplicação Web |
| aula06 | a confirmar na Adalove | 9 | 5 | Validação, Robustez e Interpretação com LLM | A5 Interpretação da Carteira por LLM e Ponderada 2 |

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
├── index.html                     portal com um card por instrução, agrupado por sprint
├── README.md                      este documento, para o aluno
├── CLAUDE.md                      guia de quem edita o acervo
├── PLANO_DE_ENSINO.md             case, dados, cronograma, entregas e pendências (fonte da verdade)
├── PLANEJAMENTO_AULA_A_AULA.md    roteiro em sete blocos de cada encontro (fonte da verdade)
├── aulas/                         um deck Reveal.js por aula (aulaNN.html)
├── materiais/                     material de apoio, com preparação pré-aula e aprofundamento
├── referencias/                   autoestudos da semana e leitura complementar, por aula
├── notebooks/                     laboratório executável de cada aula, com badge do Colab
├── exemplos/api-carteira/         API mínima e página da Aula 05
├── dados/                         snapshot da B3 e séries do Banco Central, com README próprio
├── assets/                        CSS, JS, imagens, vídeos e JSON compartilhados pelos decks
└── docs/
    ├── autoestudos-por-semana.md  autoestudos e instruções por semana, com título exato
    ├── adrs/                      decisões de arquitetura do acervo
    └── ANDAMENTO.md               o que está pronto, o que está em andamento e o que falta
```

As pastas `materiais/`, `referencias/`, `notebooks/` e `exemplos/` nascem conforme cada aula é
construída, e nem toda aula tem os quatro artefatos publicados ainda. O estado atual está em
`docs/ANDAMENTO.md`.

## Portal

O endereço do portal é <https://josercf.github.io/2026-2B-M08/>. A publicação no GitHub Pages
ainda não está configurada (ver `docs/ANDAMENTO.md`). Para abrir o acervo localmente, sirva a raiz
do repositório por HTTP, porque os decks usam caminhos relativos para `assets/`:

```bash
python3 -m http.server 8000
```
