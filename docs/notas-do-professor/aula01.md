# Notas do professor: Aula 01

Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível. 20/10/2026 (terça), Semana 2,
Sprint 1, aula 5 do módulo. Horário de relógio a confirmar na Adalove (P1).

Material de condução, não distribuído ao aluno. Todo número abaixo vem de
`tools/medidas_aula01.py` e está travado em `tools/tests/test_aula01.py`. Primeira aula do módulo:
não há resgate de aula anterior, e a abertura apresenta o parceiro, a ferramenta e as cinco
entregas.

## Antes de entrar na sala

- Abrir o deck por HTTP (`python3 -m http.server 8000` na raiz) e conferir que os dois widgets
  montam: `tres-visoes` no slide 12 e `ausencias` no slide 20.
- O widget do slide 12 abre na B3SA3. A pergunta da WEGE3 é feita antes do clique no botão WEGE3.
- O pôster do vídeo do slide 10 para antes de 27/05/2024: a turma anota a previsão olhando o
  pôster, e só então o vídeo toca. O Chromium dos validadores não decodifica H.264; no navegador
  da sala, testar o play antes.
- Os slides 2 e 3 (apresentação e combinados) só existem nesta aula e consomem a folga da
  abertura. Se o tempo apertar, cortar primeiro o slide 22 (exemplo de ADR) e reduzir a segunda
  dupla para 8 minutos.
- A review da Sprint 1 e a entrega do A1 são três dias depois, na sexta, 23/10/2026. Dizer isso
  na daily e de novo no Bloco 7.

## Se a turma chega sem o pré-aula

Sinal: no primeiro voto do Peer Instruction, mais da metade marca 21 ou 31.

1. Não refazer o autoestudo em aula. Escrever no quadro `range(1, 31)` e perguntar quantos
   números ele gera: a sala chega em 30, e a convenção de excluir o limite final fica visível.
2. Mostrar a linha `fim_exclusivo` do slide 16 antes da hora, como a correção que o coletor faz.
3. Votar de novo. Se a maioria ainda errar, seguir: o slide 8 desmonta as três contas erradas.
4. Tocar a animação `aula01-mapa-ausencias` (20 s) no início do Bloco 5 em vez de só citá-la,
   pedindo que as duplas observem o bloco coral da GOLD11.

## Bloco 1 (0 a 15): o parceiro, as entregas e o Peer Instruction

**Abertura do case.** O parceiro precisa decidir onde alocar excedentes de caixa; a ferramenta
calcula a Fronteira Eficiente de Markowitz e explica o resultado. Pergunta disparada para a sala:
"de onde vem o número que o otimizador usa?" Resposta esperada: do histórico de preços que o A1
coleta hoje.

**Peer Instruction (slide 7).** `yf.download("PETR4.SA", start="2026-08-01", end="2026-08-31")`:
quantas linhas o DataFrame devolve?

| Alternativa | Correta | Erro que revela |
|---|---|---|
| 31 | não | conta dias corridos: não sabe que o DataFrame tem uma linha por pregão |
| 30 | não | sabe que o `end` é exclusivo, mas conta dias corridos |
| 21 | não | conta os 21 pregões de agosto de 2026 e trata o `end` como inclusivo |
| 20 | sim | 21 pregões menos 31/08/2026, segunda-feira com pregão, excluído pelo `end` |

Critério de discussão em dupla: quem votou 20 defende com as duas regras (uma linha por pregão,
fim exclusivo); quem votou 21 explica se sabia que o `end` exclui o dia. Se a primeira votação
passar de 70% de acerto, revelar direto; abaixo de 30%, dar as duas regras e votar de novo; entre
30% e 70%, dois minutos de dupla.

Pergunta socrática depois do slide 8: "o yfinance avisa que deixou 31/08 de fora?" Resposta: não;
a chamada termina sem aviso. Erro comum: confiar que a última linha é a data pedida sem conferir.
É o primeiro caso de teste do SPEC.md.

## Bloco 2 (15 a 30): três visões e a previsão da MGLU3

**Prever e observar (slide 10).** Com o vídeo parado no pôster, cada aluno anota no papel o que
acontece em 27/05/2024, data do grupamento de 10 para 1, com o negociado, o Close e o Adj Close.
Medido: o negociado vai de R$ 1,32 em 24/05/2024 para R$ 13,15 em 27/05/2024, alta de 896,21%; o
Close e o Adj Close seguem contínuos. Nos dois desdobramentos anteriores, o negociado cai
-86,74% (06/08/2019) e -75,31% (14/10/2020).

Erro comum: prever que as três linhas saltam juntas. Pergunta socrática: "o valor da empresa
mudou dez vezes de um pregão para o outro?" Resposta esperada: o grupamento dividiu a empresa em
dez vezes menos ações, sem mudar o valor dela.

**Pergunta disparada (slide 11).** Qual das três visões responde quanto R$ 1.000 aplicados em
2019 viraram? Resposta: o Adj Close, se a pergunta incluir os proventos reinvestidos; o Close, se
for só o preço. A ambiguidade é proposital: exigir que o aluno pergunte "com ou sem proventos?".

## Bloco 3 (30 a 45): widget, escolha coletiva e PETR4

**Widget `tres-visoes` (slide 12).** B3SA3 em 17/05/2021: negociado -67,17%, Close -1,51%. Antes
do clique na WEGE3, cada dupla prevê as duas quedas de 28/04/2021. Medido: negociado -50,69%; o
Close não salta (nenhum dos 15 eventos da cesta move o Close mais de 7% no dia). A legenda do
canvas mostra só as linhas ligadas; desligar o negociado ajuda a ver Close e Adj Close.

**Escolha coletiva (slide 13), gabarito.**

| Pergunta de negócio | Visão | Por quê |
|---|---|---|
| Quanto R$ 1.000 em PETR4 em 2019 viraram, com proventos | Adj Close | desconta os proventos reinvestidos |
| Preço na tela do home broker em 14/05/2021 | Negociado | único que reproduz a tela do dia |
| Volatilidade anual para o otimizador | Adj Close | retorno total, sem salto de evento |
| Valor de mercado da empresa naquele dia | Negociado | preço do dia vezes as ações daquele dia |

**Fecho na PETR4 (slide 14).** Retorno de preço de 87,12% e retorno total de 616,00% na janela.
No primeiro pregão de 2019, o Adj Close vale 26,13% do Close. Pergunta: "a BBAS3 perdeu dinheiro
na janela?" Resposta: no preço, -14,65%; com proventos, +42,09%.

## Bloco 4 (45 a 60): dupla no notebook, seções 1 e 2

Cronômetro de 12 minutos, troca de condutor aos 6 (slide 17). A prática está em camadas:

- **Obrigatório:** abrir o notebook, conferir a cesta e a janela da seção 1, rodar `coletar` e
  anotar a origem impressa; depois da troca, o novo condutor roda de novo com `M08_OFFLINE=1` e
  compara as duas rodadas.
- **Extensão:** uma linha sobre o que mudaria no coletor para a cesta do grupo. Quem não chegar
  nela leva para o SPEC.md do A1.
- **Checagem aos 6 min:** cada dupla tem a origem da primeira rodada anotada. Dupla que ainda não
  rodou a seção 2 nesse ponto recebe ajuda antes da troca de papel.
- **Debrief, nos minutos finais do bloco:** duas duplas dizem a origem das duas rodadas e se o
  resultado bateu.
- **Contingência:** sem rede, o coletor cai para o snapshot e a aula segue igual. Se o Colab não
  abrir para uma dupla, ela acompanha a dupla vizinha; se não abrir para a sala, o professor
  projeta o notebook rodando localmente e as duplas anotam a origem impressa na projeção.

Circular perguntando:

- "Qual origem o coletor imprimiu?" Na sala com rede: `yfinance, ao vivo`. Com
  `M08_OFFLINE=1`: `snapshot de dados/`. Erro comum: não saber de onde veio o número.
- "O que acontece se o yfinance não estiver instalado?" Resposta: a exceção é capturada, o nome
  dela é impresso e o coletor lê o snapshot.
- "Por que somar um dia ao fim?" Resposta: o `end` exclusivo do Peer Instruction.

Se a rede da sala falhar, o coletor cai para o snapshot e a aula segue igual.

## Bloco 5 (60 a 75): ausências reais do provedor

Animação `aula01-mapa-ausencias` e widget `ausencias`. Números: BOVA11, IVVB11 e GOLD11 sem
cotação em 24/10/2025; GOLD11 com 485 ausências, 484 antes da primeira cotação, em 11/12/2020.
Descartar mantém 1.423 dos 1.908 pregões e começa a cesta em 11/12/2020.

**Pergunta disparada (slide 20): que número o grupo registra no ADR?** Resposta esperada: a
volatilidade anual sob cada tratamento, com o número antes e depois (PETR4 39,25% preenchendo e
33,41% descartando). Erro comum: registrar só "1.423 pregões", que mede o tamanho da amostra e não
o efeito no risco.

## Bloco 6 (75 a 90): descartar ou preencher e o primeiro ADR

**Slide 21.** Volatilidade anual, descartar contra preencher: PETR4 33,41% e 39,25%; VALE3 29,77%
e 35,49%; BOVA11 18,51% e 23,41%; IVVB11 17,67% e 20,15%; MGLU3 67,75% e 65,41%. Preencher cria
retorno zero em 24/10/2025 e acumula no pregão seguinte: 0,93% no BOVA11, 1,72% no IVVB11 e
-3,37% na GOLD11.

Pergunta socrática: "por que a MGLU3 fica mais volátil quando descartamos datas?" Resposta: os
pregões de 2019 e 2020 que saem eram, para ela, menos dispersos que os seguintes. Quem acertar
com a explicação merece nota de participação.

**Slide 22, exemplo de ADR.** Dizer em voz alta que é um exemplo. Ele decide preencher, que é o
tratamento das Aulas 02 a 06 (ADR-009 do acervo); o grupo decide o dele com os números do próprio
coletor, e um ADR que decide descartar é válido quando cita o custo. Não induzir a turma a copiar
o exemplo.

**Dupla (slide 23).** Cronômetro de 12 minutos, troca de condutor aos 6. A prática está em
camadas, e o ADR completo sai da aula como tarefa do A1:

- **Obrigatório:** rodar o relatório de ausências da seção 4, rodar a comparação dos tratamentos e
  anotar a volatilidade anual da PETR4 sob cada um; depois da troca, o novo condutor escreve a
  decisão da dupla em uma frase, com o número antes e depois.
- **Extensão:** comparar as três visões de preço de um ativo com evento corporativo (seção 3) e
  completar o ADR com contexto e alternativa rejeitada. A segunda extensão é a saída pós-aula para
  o ADR individual do A1.
- **Checagem aos 6 min:** os dois valores da PETR4 estão anotados. Dupla sem os números nesse
  ponto ainda não rodou a célula da comparação.
- **Debrief, nos minutos finais do bloco:** duas duplas com decisões opostas leem a frase em voz
  alta. Critério: a frase cita um número medido? Se não cita, a dupla reescreve antes de sair.
- **Contingência:** se o notebook não rodar, a dupla escreve a frase com os números da PETR4 do
  slide 21, que são os mesmos da célula.

## Bloco 7 (90 a 105): quiz e amarração

Quiz de três perguntas (slide 24), gabarito: desdobramento (o Close cai só 1,51%); `dropna` na
cesta; Adj Close.

Amarração, em voz alta:

- O A1 vale 3 pontos. A review da Sprint 1 e a entrega do A1 são no mesmo dia, sexta,
  23/10/2026, com entrega até 23h59.
- O barema: pipeline 25%, tratamento 20%, relatório descritivo 10%, reprodutibilidade 10%,
  especificação 15%, ADRs 20% (individual).
- A Aula 02, em 05/11/2026, calcula os retornos a partir do Adj Close já tratado pelo coletor.

## Gabarito do desafio do notebook (não distribuir)

- **Parte a.** Num Colab novo, com `M08_OFFLINE=1`, a célula imprime `origem: snapshot de dados/`
  e `pregões: 1908 de 2019-01-02 a 2026-08-31`. Se a origem sair `yfinance, ao vivo`, a variável
  foi definida depois da chamada.
- **Parte b.** Com ticker fora da cesta e `M08_OFFLINE=1`, o snapshot não tem a coluna e a célula
  falha com `KeyError`. É o comportamento esperado: o grupo roda com a rede ligada e registra a
  origem no SPEC.md.
- **Parte c.** Um caso aceitável por rodada, com entrada, resultado esperado e origem do número.
  Exemplo de caso que pega o `end` exclusivo: "a última data devolvida é a data final pedida,
  quando ela é pregão".
