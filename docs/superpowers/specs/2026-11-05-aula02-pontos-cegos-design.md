# Aula 02 redesenhada: pontos cegos do retorno, jogo da moeda e comitê do assessor

- Data: 05/11/2026, 10h. Aula às 14h do mesmo dia (turma 2026-2B-T19, grupos G01 a G04).
- Aprovado em conversa pelo Prof. José Romualdo em 05/11/2026.
- Substitui o roteiro da Aula 02 em `PLANEJAMENTO_AULA_A_AULA.md` e o deck atual `aulas/aula02.html`
  (o deck atual fica no histórico do git). Encerra a ADR-015 (Palco) para esta aula: o professor não
  está usando o Palco, e o botão Slides do portal volta para `aulas/aula02.html`.

## 1. Intenção

A versão atual da Aula 02 é expositiva e genérica: muito conteúdo (retorno simples, log, histograma,
anualização, janela deslizante) com pouca profundidade, e quase nenhuma ponte com os dois autoestudos
da semana ("Risco e retorno: passado e prólogo", cap. 5 de Bodie, Kane e Marcus; "Análise de uma ação
em Python na prática", artigo do Turing Talks com o exemplo de +5% e -2% virando 2,9%).

A aula nova é de computação para alunos de administração: mostra como código sobre dado real sustenta
ou derruba uma afirmação de investimento. O fio é **pontos cegos**: afirmações que soam corretas e
levam a uma decisão errada. Menos conteúdo, mais profundidade, dinâmicas que a Aula 01 não usou.

## 2. Objetivos, não objetivos e antiobjetivos

Objetivos
- A turma vive o ponto cego da média aritmética contra a geométrica antes de ver a fórmula (jogo da moeda).
- Cada grupo desmonta (ou confirma) uma afirmação de assessor com código sobre o snapshot `dados/` e
  registra a decisão numa ADR preenchida em conjunto, online, dentro do próprio deck do grupo, com prazo.
- Cada veredito vira uma decisão de projeto do A2 (review em 06/11/2026).

Não objetivos
- Retorno logarítmico, volatilidade em janela deslizante e o widget `vol-janela` saem desta aula.
- Anualização entra só como ferramenta usada pelo G03, não como bloco expositivo.
- Nada de Palco.

Antiobjetivos (falha mesmo que funcione)
- Gabarito, veredito esperado ou número que desmonta uma afirmação publicado no repositório (o GitHub
  Pages expõe o repositório inteiro, inclusive `docs/notas-do-professor/` e `tools/tests/`).
- Repetir a nuvem de palavras por voz da Aula 01.
- Slide com muito texto, fonte pequena ou grade de cartões mecânica. Pouco texto, fonte grande,
  composição livre usando a área.
- Vazar a resposta de um grupo no deck principal antes da defesa.

## 3. Restrições

- Tudo pronto, publicado e ensaiado antes das 14h de 05/11/2026.
- HTML Reveal.js puro, no molde da Aula 01 (`aulas/aula01.html`): mesmos CSS e JS de `assets/`,
  validadores `check_brand.py`, `check_slides.py`, `check_links.py`, `check_widgets.py` passando, testes
  em `tools/tests` passando (`.venv/bin/python -m pytest tools/tests -q`).
- Convenções do repositório: pt-BR acentuado, sem em dash, sem emoji, Material Symbols, títulos descritivos
  ou action titles conforme o `CLAUDE.md` global.
- Backend ao vivo: o mesmo projeto Supabase do quiz (`assets/js/inteli-quiz-config.js`), no padrão de
  `exemplos/quiz-supabase/quiz.sql`: tabelas com RLS, escrita só por funções `security definer`, ações de
  professor protegidas pela chave do professor (`quiz_chave_ok`), realtime pela publicação
  `supabase_realtime`. Aplicar o SQL no projeto de produção exige confirmação do professor antes.
- Publicação: push em `main` dispara o Pages. Push só com autorização do professor.

## 4. Sequência do encontro (105 min de metodologia ativa, depois da daily)

| Bloco | Tempo | Conteúdo | Interação que fecha |
|---|---|---|---|
| 1 | 0 a 15 | Quiz ao vivo existente: "Cara rende +50%, coroa rende -40%. Vale jogar 10 rodadas?" Depois, jogo da moeda no celular (seção 5) | voto antes; histograma ao vivo depois |
| 2 | 15 a 30 | Python linha a linha (`inteli-codigo.js`): +5% e -2% do artigo com `(1 + r).cumprod()`; simulação de 10.000 jogadores com média e mediana; a regra do Bodie (geométrica ~ aritmética - metade da variância) | turma prevê a mediana antes de rodar |
| 3 | 30 a 45 | Ponte com o dado real: BBDC4, 2020 a 2025, média aritmética anual +4,81% e geométrica -0,42%. Apresentação do comitê de investimentos do BTG e envio dos links no Slack | cada grupo lê sua afirmação em voz alta |
| 4 e 5 | 45 a 75 | Grupos investigam no notebook (20 min) e preenchem a ADR (5 min), com prazo sincronizado e trava | marco do cronômetro aos 12 min |
| 6 | 75 a 95 | Comitê: slide que projeta as quatro ADRs ao vivo; cada grupo defende em 3 min; sala vota sustentada ou enganosa no quiz ao vivo | voto da sala |
| 7 | 95 a 105 | Amarração com o A2: cada veredito vira decisão da função de risco e retorno (qual média, qual preço, qual referência); ADR do grupo no repositório | review do A2 em 06/11 |

Números da ponte do Bloco 3 (anos-calendário completos 2020 a 2025, `precos_ajustados.csv`, fim de ano a
fim de ano): BBDC4 aritmética 4,81% e geométrica -0,42%. Calcular por script versionado
(`tools/medidas_aula02.py` pode ser reescrito) e travar em teste, porque a ponte é pública e não é resposta
de nenhum grupo.

## 5. Jogo da moeda

- Página do aluno `aulas/aula02-moeda.html`, aberta por QR no slide do Bloco 1. O aluno entra com apelido
  (reaproveitar `quiz_entrar` da sessão, ou cadastro próprio equivalente).
- Cada celular sorteia a **própria** moeda. Se o professor jogasse uma moeda única, todos teriam o mesmo
  saldo e o ponto cego sumiria.
- Todos começam com R$ 100. O professor libera cada rodada pelo slide (ação com chave do professor); o
  celular mostra o botão de jogar, anima o resultado, aplica +50% ou -40% e grava o saldo daquela rodada.
  Dez rodadas.
- O slide mostra ao vivo: número de jogadores, rodada atual, histograma dos saldos, **média** e **mediana**
  marcadas, e a linha dos R$ 100. Referência teórica para a fala (não precisa estar no slide): após 10
  rodadas, média esperada ~ R$ 163 e mediana ~ R$ 59.
- Aluno que entra atrasado joga as rodadas já liberadas em sequência.
- Plano B sem rede: moeda física e saldo no papel; o slide mostra a tabela teórica.

## 6. Exercício dos grupos: o pitch do assessor

Um deck por grupo, com link próprio enviado no Slack:
`aulas/aula02-g01.html` a `aulas/aula02-g04.html`, com `?t=<token>` na URL.

| Grupo | Afirmação do assessor (vai no deck) |
|---|---|
| G01 | "O BBAS3 deu prejuízo de 14,7% entre 2019 e 2026" |
| G02 | "A MGLU3 caiu 90% desde 2019. Uma alta de 90% devolve o cliente ao zero a zero" |
| G03 | "A PETR4 tem volatilidade de 39% ao ano, então o pior que acontece em um ano é perder 39%" |
| G04 | "A WEGE3 ganhou da renda fixa no período" |

O ponto cego de cada frase e o veredito esperado ficam só no gabarito privado (seção 8). Nem toda
frase precisa ser enganosa: o comitê não pode aprender que o assessor sempre mente.

Cada deck de grupo tem poucos slides, fonte grande:
1. A afirmação do assessor e o papel do grupo (analistas do comitê do BTG).
2. O dado e o ponto de partida: link do notebook de grupos (no GitHub, com badge do Colab, conforme a skill
   de curso) e a seção do grupo.
3. A ADR online com cronômetro sincronizado.
4. O veredito que o grupo vai defender (campo da própria ADR, destacado).

Notebook `notebooks/aula02-grupos.ipynb`: carga do snapshot (local, com queda para a URL bruta do
repositório no Colab), uma seção por grupo com a afirmação e células vazias. Sem respostas, sem números
que desmontam a afirmação. O notebook atual `notebooks/aula02.ipynb` pode ser substituído pelo da aula nova
(Bloco 2) ou mantido; decisão do construtor, desde que o portal aponte para o que a aula usa.

## 7. ADR online

- Campos, enxutos a partir de `Inteli - Adm Tech - M08 - LBL/adr-template-admtech-m08.md`: título,
  contexto e problema, critérios de decisão, opções consideradas, decisão (veredito: sustentada ou
  enganosa, e por quê), impacto numérico no caso do grupo.
- Edição simultânea por todos do grupo. Cada campo salva sozinho (debounce) e recebe as mudanças dos
  colegas em tempo real; o campo em foco não é sobrescrito enquanto a pessoa digita (último a gravar vence
  por campo, com aviso visível de edição remota).
- Acesso: token por grupo gerado na hora pela chave do professor (função de professor), guardado só como
  hash no banco, nunca no repositório. O professor obtém os quatro links prontos para colar no Slack.
- Prazo: o professor inicia o prazo pelo deck principal (por exemplo 25 min); todos os decks de grupo
  mostram o mesmo cronômetro a partir do horário do servidor; depois do fim, a função de gravação recusa
  escrita e o formulário fica somente leitura. O professor pode estender o prazo.
- Leitura pública das ADRs da sessão (vão ao projetor).
- Slide do comitê no deck principal: as quatro ADRs ao vivo, uma por vez ou lado a lado em fonte legível,
  e o quiz ao vivo de voto por grupo **sem `data-correta` no HTML** (o veredito sai da fala do professor).
- Exportar cada ADR como Markdown no formato do template (botão no deck do grupo), para o grupo commitar
  no próprio repositório como ADR do A2.

## 8. Gabarito e material do professor fora do repositório

- `Inteli - Adm Tech - M08 - LBL/` (não versionado) recebe: gabarito por grupo (números, veredito, erro
  comum), script que mede esses números sobre o snapshot e teste que trava os números, mais uma checagem
  que varre o repositório público e falha se algum número do gabarito aparecer lá.
- `docs/notas-do-professor/aula02.md` (público) é reescrito só com logística (ordem dos slides, como
  gerar links, plano B), sem respostas.

## 9. Decidido pelo professor, decidido por mim e deixado ao construtor

Pelo professor: aula interativa e dinâmica; nada da nuvem por voz; jogo da moeda e pitch do assessor;
prazo nos grupos; respostas fora do repositório; um deck por grupo com link no Slack; ADR preenchida em
conjunto, online, no slide; HTML direto, sem Palco; sequência da seção 4.

Por mim (o professor pode vetar): moeda individual no celular; afirmações da seção 6 e vereditos do gabarito privado; token por grupo; prazo sincronizado com trava; campos da ADR; ponte BBDC4 no Bloco 3;
substituir o deck no mesmo endereço; ADR-016 do acervo registrando a troca e encerrando a ADR-015 para a
Aula 02; atualizar `PLANEJAMENTO_AULA_A_AULA.md` e o portal.

Ao construtor: nomes de tabelas e funções SQL, estrutura do JS, layout dos slides dentro das regras de
marca, formato do histograma, quantos slides no deck principal, como os testes cobrem o realtime (por
exemplo, um cliente Supabase falso injetado na página nos testes Playwright).

## 9.1 Respostas da revisão do construtor (05/11/2026)

- Autorizado pelo professor: aplicar o SQL novo (prefixos `adr_` e `moeda_`, só adição) no projeto Supabase
  do quiz por volta das 11h30, e push em `main` por etapas a partir de cerca de 12h30, sem nova confirmação.
- Plano B decidido: se às 13h15 o backend ao vivo falhar no ensaio, ADR em Google Docs e moeda física.
- Por mim: `materiais/aula02.html` e `referencias/aula02.html` ficam como estão (leitura complementar do A2);
  `palco/aula02/` fica no repositório; ADR-015 passa a "Substituída pela ADR-016"; o botão Slides do portal
  volta para `aulas/aula02.html`.

## 10. Prioridade se o tempo apertar

1. Decks de grupo com ADR online, prazo e tokens (o coração da aula).
2. Deck principal com Blocos 2, 3, 6 e 7.
3. Jogo da moeda no celular (plano B físico existe).
