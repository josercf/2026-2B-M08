# Planejamento Aula a Aula: Computação no Módulo 08 AdmTech

Roteiro dos 6 Encontros de Instrução de Computação do Prof. José Romualdo, no formato Inteli. Este
documento e o `PLANO_DE_ENSINO.md` são a fonte da verdade do acervo: nenhum deck, material, página
de referências ou notebook inventa data, título, escopo ou autoestudo. Os autoestudos citados
abaixo têm título exato conferido contra `docs/autoestudos-por-semana.md`.

**Estrutura do encontro, igual nas seis aulas:**

- Autoestudo, feito pelo aluno antes da aula, na Adalove: os dois autoestudos da semana, as
  animações da seção "Preparação" do material de apoio e uma autoverificação de cinco perguntas
  sem nota.
- Daily da equipe, 15 minutos: o que fiz, o que vou fazer, impedimentos.
- Metodologia ativa, 105 minutos em sete blocos de 15 minutos. Nenhum bloco passa de 15 minutos
  sem interação direta dos alunos: cada bloco abaixo fecha em uma interação nomeada (Peer
  Instruction, prever e observar, pensar e compartilhar, dupla no notebook, escolha coletiva, quiz
  ou pergunta disparada) antes de abrir o seguinte.

Os horários de relógio dependem da Adalove (pendência P1 do plano de ensino). Por isso os blocos
aparecem em minutos corridos, de 0 a 105, contados do fim da daily, e nenhuma hora de relógio
aparece no acervo.

---

### Aula 01 - Semana 1 - Aquisição de Dados de Mercado: Coleta Confiável e Reproduzível  (Sprint 1)

Data: a confirmar na Adalove (pendência P1). Aula 5 do módulo na planilha.
Entrega que alimenta: A1 Coletor e Processador de Dados de Mercado (3, a confirmar na Adalove).
O que a aula anterior deixou pronto: primeira aula do módulo; a abertura apresenta o parceiro e a ferramenta.
O que esta aula deixa pronto: coletor parametrizado por tickers e datas, com preço ajustado e ausências tratadas e documentadas.

Antes do encontro
  Autoestudo: Coleta de dados financeiros e DataFrames com Pandas (70 min)
  Autoestudo: Cotações do Yahoo Finance no Colab, do jeito reaproveitável (35 min)
  Preparação no material de apoio: animações `aula01-tres-visoes-mglu3` e `aula01-mapa-ausencias`
    e autoverificação de cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. Primeira daily do módulo: cada equipe confirma acesso
  ao Colab, ao repositório do grupo e à pasta `dados/` do acervo antes de seguir.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Abertura do módulo: o parceiro, a ferramenta de simulação de carteira
    eficiente e as cinco entregas por sprint, de A1 a A5. Fecha em Peer Instruction: "No primeiro
    pregão de 2019, quanto o Adj Close da PETR4 vale em relação ao Close?", com as opções 100%,
    86%, 52% e 26%. Cada distrator é a razão real de outro ativo da cesta (BOVA11, SUZB3 e VALE3),
    e a certa é 26,13%. Votar, discutir em dupla, votar de novo.
  Bloco 2 (15 a 30 min)  As três visões de preço (negociado, ajustado por desdobramento, ajustado
    por proventos) e o que cada uma responde. Antes de tocar a animação, a turma prevê e registra
    no papel o que acontece com as três linhas da MGLU3 em 27/05/2024, data do grupamento de fator
    0,1. Pergunta disparada: qual das três visões responde quanto R$ 1.000 aplicados em 2019
    viraram.
  Bloco 3 (30 a 45 min)  Widget `tres-visoes` com B3SA3 e WEGE3: no desdobramento de 17/05/2021, o
    preço negociado da B3SA3 cai 67,17% e o Close cai 1,51%. Escolha coletiva de quatro perguntas
    de negócio contra as três visões, uma visão apontada por pergunta. Fecha na PETR4, com retorno
    de preço de 87,12% e retorno total de 616,00% na janela do snapshot.
  Bloco 4 (45 a 60 min)  Dupla no notebook, seções 1 e 2: a função `coletar`, parametrizada por
    tickers e datas, com tempo limite e queda para o snapshot de `dados/`. Cronômetro de 12
    minutos, condutor e navegador trocando na metade.
  Bloco 5 (60 a 75 min)  Animação do mapa de ausências e widget `ausencias`: BOVA11, IVVB11 e
    GOLD11 sem cotação em 24/10/2025, pregão normal da B3, e GOLD11 com 484 pregões vazios antes
    da primeira cotação, em 11/12/2020. Descartar as datas com ausência mantém 1.423 dos 1.908
    pregões e tira março de 2020 da cesta inteira. Pergunta disparada: que número o grupo registra
    no ADR.
  Bloco 6 (75 a 90 min)  Dupla no notebook, seções 3 e 4: relatório de ausências por ativo, escolha
    do tratamento e primeiro ADR com o impacto numérico da decisão, que leva a volatilidade anual
    da PETR4 de 39,25% para 33,41%. Cronômetro de 12 minutos.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 1: o A1
    (3, a confirmar na Adalove), o SPEC.md escrito antes de codar, o ADR individual valendo 20% da
    nota do artefato, a review da Sprint 1 com data a confirmar, e o que a Aula 02 vai pedir
    (retornos calculados a partir do Adj Close já tratado).

Depois do encontro
  Desafio do notebook: rodar o coletor do zero em máquina limpa, com a rede desligada por
    `M08_OFFLINE=1`, e conferir que o resultado bate com o da aula.
  Avanço do A1: SPEC.md com as interfaces do coletor e o plano de testes, relatório descritivo por
    ativo e o ADR de tratamento de ausências assinado por cada aluno.
  Leitura complementar: seções 4 e 5 de `dados/README.md`, com as três visões de preço e as falhas
    do provedor medidas no snapshot.

### Aula 02 - Semana 3 - Dados Financeiros: Do Preço ao Retorno  (Sprint 2)

Data: a confirmar na Adalove (pendência P1). Aula 13 do módulo na planilha.
Entrega que alimenta: A2 Módulo de Análise de Risco e Retorno Individual (sem peso na planilha, a confirmar na Adalove).
O que a aula anterior deixou pronto: a Aula 01 deixou pronto o coletor parametrizado, com o Adj Close escolhido e a decisão de ausências registrada em ADR.
O que esta aula deixa pronto: retornos diários, métricas anualizadas por 252 e a comparação de risco entre os ativos da cesta.

Antes do encontro
  Autoestudo: Risco e retorno: passado e prólogo (70 min)
  Autoestudo: Análise de uma ação em Python na prática (45 min)
  Preparação no material de apoio: animação do histograma de retornos diários se formando, com
    março de 2020 surgindo nas caudas; animação da dispersão crescendo com a raiz do tempo;
    autoverificação de cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. A equipe traz o estado do A1 e o que o ADR de
  ausências decidiu, porque o retorno calculado hoje herda essa decisão.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Resgate do coletor da Aula 01 e Peer Instruction sobre a queda de 29,70%
    da PETR4 em 09/03/2020: qual é o retorno logarítmico correspondente. As opções e o valor exato
    saem da medição da própria aula. Votar, discutir em dupla, votar de novo.
  Bloco 2 (15 a 30 min)  Retorno simples e retorno logarítmico: definição, quando cada um se soma
    e o que acontece em quedas grandes. A turma prevê a diferença entre os dois na queda do bloco
    anterior antes de o widget revelar as duas séries lado a lado.
  Bloco 3 (30 a 45 min)  Dupla no notebook: `pct_change`, `np.log`, média e desvio padrão diários
    de cada ativo da cesta. Cronômetro de 12 minutos, condutor e navegador trocando na metade.
  Bloco 4 (45 a 60 min)  Histograma dos retornos e o peso das caudas, com março de 2020 destacado.
    O desvio padrão como medida de risco e o que ele deixa de fora. Pergunta disparada: o desvio
    padrão diz qual foi a pior queda do período.
  Bloco 5 (60 a 75 min)  Anualização: fator 252 no retorno e raiz de 252 na volatilidade, com a
    conta feita no quadro. Widget de volatilidade anualizada em janela deslizante de 21, 63 e 252
    pregões; a turma prevê qual janela reage primeiro a uma crise antes de mover o controle.
  Bloco 6 (75 a 90 min)  Dupla no notebook: tabela de retorno e volatilidade anualizados da cesta,
    com o CDI acumulado do período como referência. Fecha em escolha coletiva, com a sala julgando
    afirmações sobre risco como sustentadas ou não pelos números da tabela.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 2: o A2
    (sem peso na planilha, a confirmar na Adalove), as funções reutilizáveis que o A3 vai importar
    e a pendência P5, dita em voz alta: o A2 cobra matriz de correlação e de covariância, que a
    Aula 03 só ensina na semana 5, e o material de apoio antecipa o mínimo necessário.

Depois do encontro
  Desafio do notebook: repetir as métricas anualizadas com a decisão de ausências invertida e medir
    quanto a volatilidade de cada ativo muda.
  Avanço do A2: SPEC.md com as interfaces do módulo de métricas, histogramas por ativo e leitura
    escrita comparando a cesta, mais o ADR da anualização.
  Leitura complementar: seção do autoestudo de risco e retorno sobre prêmio de risco, retomada com
    os números da cesta.

### Aula 03 - Semana 5 - Correlação, Covariância e o Argumento Matemático da Diversificação  (Sprint 3)

Data: a confirmar na Adalove (pendência P1). Aula 22 do módulo na planilha.
Entrega que alimenta: A3 Motor de Simulação de Monte Carlo (2, a confirmar na Adalove) e Ponderada 1 (3, a confirmar na Adalove).
O que a aula anterior deixou pronto: a Aula 02 deixou pronta a tabela de retorno e volatilidade anualizados da cesta, com o CDI como referência.
O que esta aula deixa pronto: matriz de covariância anualizada e a curva de risco de dois ativos em função da correlação.

Antes do encontro
  Autoestudo: Diversificação eficiente: a matemática de não colocar todos os ovos na mesma cesta (80 min)
  Autoestudo: Atividade Ponderada 1: Diagnóstico de uma carteira herdada (120 min)
  Preparação no material de apoio: animação da curva de dois ativos se curvando enquanto a
    correlação cai de +1 a -1; animação da correlação móvel de ITUB4 com BBDC4 contra a de PETR4
    com IVVB11; autoverificação de cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. A equipe traz o estado do A2 e as dúvidas de
  correlação que apareceram ao escrever a leitura analítica pedida no artefato.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Resgate da tabela de volatilidade da Aula 02 e Peer Instruction: dois
    ativos com 30% de volatilidade cada, correlação de 0,5 e metade do dinheiro em cada. A
    volatilidade da carteira fica abaixo de 30%, exatamente em 30% ou acima de 30%. Votar,
    discutir em dupla, votar de novo.
  Bloco 2 (15 a 30 min)  Covariância e correlação: definição, unidade e por que a correlação
    circula mais do que a covariância. Heatmap da matriz real da cesta projetado, com leitura do
    par ao passar o cursor. Pergunta disparada: qual par da cesta a sala aposta como o mais
    correlacionado.
  Bloco 3 (30 a 45 min)  Widget de correlação e peso sobre dois ativos reais da cesta. A turma
    prevê e registra qual peso dá o menor risco antes de mover o controle, e compara a previsão
    com a curva medida.
  Bloco 4 (45 a 60 min)  Dupla no notebook: matriz de correlação e matriz de covariância anualizada
    da cesta, a partir dos retornos da Aula 02. Cronômetro de 12 minutos, condutor e navegador
    trocando na metade.
  Bloco 5 (60 a 75 min)  Correlação móvel e o que acontece com ela em crise, com a animação da
    preparação retomada sobre os dados. Introdução ao encolhimento de Ledoit-Wolf como resposta à
    instabilidade da covariância amostral. Pergunta disparada: o que uma correlação que sobe na
    crise faz com a diversificação prometida ao parceiro.
  Bloco 6 (75 a 90 min)  Escolha coletiva: pares da cesta classificados entre os que concentram
    risco e os que diversificam, com o número da matriz na tela. Fecha em pensar e compartilhar
    sobre uma carteira formada só de bancos. Nenhuma carteira da Ponderada 1 aparece nesta aula.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 3: o A3
    (2, a confirmar na Adalove), que consome a matriz de covariância montada hoje, e a Ponderada 1
    (3, a confirmar na Adalove), com carteira individualizada pelo último dígito do RA e parecer
    situado no período analisado.

Depois do encontro
  Desafio do notebook: recalcular a matriz de correlação em duas janelas distintas e medir quanto
    cada par se move entre elas.
  Avanço do A3: SPEC.md do motor de simulação, matriz de covariância anualizada exportada para o
    motor e o ADR do estimador de covariância.
  Leitura complementar: capítulo de diversificação eficiente do autoestudo da semana, relido com a
    matriz da própria cesta do grupo.

### Aula 04 - Semana 6 - Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz  (Sprint 3)

Data: a confirmar na Adalove (pendência P1). Aula 28 do módulo na planilha.
Entrega que alimenta: A3 Motor de Simulação de Monte Carlo (2, a confirmar na Adalove) e a base matemática do A4.
O que a aula anterior deixou pronto: a Aula 03 deixou pronta a matriz de covariância anualizada da cesta e a curva de risco de dois ativos em função da correlação.
O que esta aula deixa pronto: nuvem de 10.000 carteiras, carteiras de variância mínima e de máximo Sharpe e a fronteira de 50 pontos.

Antes do encontro
  Autoestudo: Carteiras e simulação de Monte Carlo com Python (65 min)
  Autoestudo: Da nuvem à fronteira eficiente de Markowitz (70 min)
  Preparação no material de apoio: animação da nuvem de Monte Carlo acumulando pontos; animação da
    fronteira traçada sobre a nuvem; animação do SLSQP caminhando até o ótimo no triângulo de pesos
    de três ativos; autoverificação de cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. A equipe traz o estado do motor de simulação e o tempo
  de execução que já mediu, porque o requisito do A3 é rodar 10.000 carteiras em menos de 10
  segundos.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Resgate da covariância da Aula 03 e Peer Instruction: entre 10.000
    carteiras sorteadas, a de maior Índice de Sharpe é a carteira ótima. Votar, discutir em dupla,
    votar de novo.
  Bloco 2 (15 a 30 min)  Pesos, retorno e variância em forma vetorial, e o Índice de Sharpe com o
    CDI no lugar da taxa livre de risco. Widget do triângulo de pesos de três ativos, com a turma
    prevendo onde o ponto cai no plano risco-retorno antes de arrastar o vértice.
  Bloco 3 (30 a 45 min)  Dupla no notebook: motor vetorizado que sorteia 10.000 carteiras com pesos
    normalizados e devolve retorno, volatilidade e Sharpe de cada uma em menos de 10 segundos.
    Cronômetro de 12 minutos, condutor e navegador trocando na metade.
  Bloco 4 (45 a 60 min)  Widget de sorteio progressivo: a melhor carteira sorteada comparada com a
    ótima, conforme o número de sorteios cresce. Pergunta disparada: quantos sorteios faltariam
    para a melhor sorteada encostar na ótima.
  Bloco 5 (60 a 75 min)  Otimização com restrições: função objetivo, soma dos pesos igual a 1,
    limites sem venda a descoberto e `scipy.optimize.minimize` com SLSQP. Variância mínima e máximo
    Sharpe resolvidos ao vivo, com a animação do SLSQP retomada quadro a quadro. Antes de rodar o
    otimizador, a turma prevê qual das duas carteiras vai concentrar mais peso num único ativo, e a
    previsão fica no quadro para ser comparada com o resultado na tela.
  Bloco 6 (75 a 90 min)  Dupla no notebook: otimizador das duas carteiras e fronteira de 50 pontos
    de retorno alvo desenhada sobre a nuvem do bloco 3. Cronômetro de 12 minutos.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 3: o A3
    (2, a confirmar na Adalove), fechado com a nuvem e a leitura escrita de por que a simulação não
    substitui a otimização, e a prévia do A4 na Sprint 4, que leva este otimizador para dentro de
    uma aplicação web.

Depois do encontro
  Desafio do notebook: repetir a otimização com uma restrição de peso máximo por ativo e comparar
    os pesos resultantes com os da aula.
  Avanço do A3 e prévia do A4: gráfico integrando nuvem, fronteira e os dois pontos ótimos, tabela
    comparativa das duas carteiras e o ADR das restrições da otimização.
  Leitura complementar: seção do autoestudo sobre a fronteira como borda da nuvem, relida com o
    gráfico do próprio grupo.

### Aula 05 - Semana 8 - Do Script ao Produto: API em FastAPI e Página Web  (Sprint 4)

Data: a confirmar na Adalove (pendência P1). Aula 38 do módulo na planilha.
Entrega que alimenta: A4 Otimizador de Carteira com Fronteira Eficiente em Aplicação Web (2, a confirmar na Adalove).
O que a aula anterior deixou pronto: a Aula 04 deixou prontas as carteiras de variância mínima e de máximo Sharpe e a fronteira de 50 pontos, calculadas num notebook.
O que esta aula deixa pronto: API FastAPI que devolve métricas de carteira em JSON e página que desenha o resultado.

Antes do encontro
  Autoestudo: HTTP e JSON na prática: o que acontece entre a página e o servidor (50 min)
  Autoestudo: Primeira API com FastAPI: rotas, parâmetros e validação (70 min)
  Preparação no material de apoio: animação da requisição saindo do navegador, passando pela API e
    pelo cálculo e voltando como JSON até o gráfico; animação do tempo de resposta com e sem cache;
    autoverificação de cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. A equipe traz o estado do otimizador da Sprint 3 e diz
  em que módulo ele está, porque a API de hoje vai importar esse módulo sem copiar código.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Resgate da fronteira da Aula 04 e Peer Instruction: um gestor do parceiro
    digita tickers numa página, e o otimizador roda no navegador ou no servidor. Votar, discutir em
    dupla, votar de novo.
  Bloco 2 (15 a 30 min)  Cliente e servidor, método GET, parâmetros de consulta, códigos de status
    e JSON. Widget montador de URL que dispara `fetch` de verdade contra o JSON gravado da API de
    exemplo do acervo e mostra requisição e resposta. A turma prevê o código de status de cada URL
    montada antes de disparar.
  Bloco 3 (30 a 45 min)  FastAPI ao vivo: rota com tipos anotados, validação de entrada e
    documentação automática em `/docs`, importando o módulo do otimizador da Sprint 3 sem copiar
    código. Pergunta disparada: que erro a API deve devolver para um ticker que não existe.
  Bloco 4 (45 a 60 min)  Dupla no notebook: a mesma API testada com `TestClient`, sem subir
    servidor, com um caso de sucesso (status 200) e um caso de entrada inválida (status 422).
    Cronômetro de 12 minutos, condutor e navegador trocando na metade.
  Bloco 5 (60 a 75 min)  Página HTML que consome a API com `fetch` e desenha a fronteira com
    Plotly.js, servida como arquivo estático pela própria API. Pergunta disparada: onde fica o
    cálculo quando a página só desenha.
  Bloco 6 (75 a 90 min)  Dupla: subir `exemplos/api-carteira/` e estender a página com um campo
    novo. Fecha em escolha coletiva, com a sala decidindo se a chave de API, o cálculo, o gráfico e
    a validação ficam no navegador, no servidor ou em nenhum dos dois.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 4: o A4
    (2, a confirmar na Adalove), com o otimizador dentro da API, a fronteira desenhada na página e
    o SPEC.md trazendo os contratos dos endpoints e o plano de testes com `TestClient`. A folga
    entre esta aula e a entrega do A4 depende do dia da aula na semana 8 (pendência P6).

Depois do encontro
  Desafio do notebook: acrescentar um endpoint de métricas para pesos informados pelo usuário e
    testar o caso de pesos que não somam 1.
  Avanço do A4: aplicação no repositório do grupo com `uvicorn` documentado no README, contratos
    dos endpoints no SPEC.md e o ADR da fronteira entre navegador e servidor.
  Leitura complementar: capítulos de parâmetros de consulta e de validação do tutorial oficial do
    FastAPI, citados no autoestudo da semana.

### Aula 06 - Semana 9 - Validação, Robustez e Interpretação com LLM  (Sprint 5)

Data: a confirmar na Adalove (pendência P1). Aula 43 do módulo na planilha.
Entrega que alimenta: A5 Interpretação da Carteira por LLM (1, a confirmar na Adalove) e Ponderada 2 (3, a confirmar na Adalove).
O que a aula anterior deixou pronto: a Aula 05 deixou pronta a API FastAPI que devolve métricas de carteira em JSON e a página que desenha o resultado.
O que esta aula deixa pronto: fecho do módulo, com teste fora da amostra e interpretação verificada por LLM.

Antes do encontro
  Autoestudo: Os limites do otimizador e do LLM: premissas, sensibilidade e alucinação (90 min)
  Autoestudo: Atividade Ponderada 2: A carteira ótima sobrevive fora da amostra? (120 min)
  Preparação no material de apoio: animação da janela de treino deslizando e dos pesos ótimos
    mudando; animação da curva de drawdown se formando no período de teste; autoverificação de
    cinco perguntas sem nota.

Daily da equipe (15 min)
  O que fiz, o que vou fazer, impedimentos. A equipe traz o estado da aplicação da Sprint 4 e
  confirma que a chave da OpenRouter recebida pela coordenação está fora do repositório.

Metodologia ativa (105 min)
  Bloco 1 (0 a 15 min)  Resgate da API da Aula 05 e Peer Instruction: a carteira de máximo Sharpe
    otimizada num período entrega o Sharpe prometido no período seguinte. Votar, discutir em dupla,
    votar de novo.
  Bloco 2 (15 a 30 min)  Divisão temporal entre treino e teste, backtest fora da amostra e a
    comparação entre esperado e realizado. Pergunta disparada: que parte do resultado da Aula 04 o
    grupo ainda não tinha testado.
  Bloco 3 (30 a 45 min)  Widget da janela de treino com pesos ótimos pré-calculados. A turma prevê
    quanto os pesos mudam ao deslizar a janela antes de mover o controle, e lê a curva de drawdown
    que acompanha.
  Bloco 4 (45 a 60 min)  Dupla no notebook: backtest fora da amostra e medida de estabilidade dos
    pesos entre duas janelas de treino. Cronômetro de 12 minutos, condutor e navegador trocando na
    metade.
  Bloco 5 (60 a 75 min)  O LLM como componente do produto: chamada à OpenRouter pelo backend, chave
    em variável de ambiente, prompt montado com os números reais da carteira e resposta
    estruturada. O custo por chamada é citado do case de créditos aprovado, que estima cerca de
    US$ 0,002 por chamada no cenário realista. Pergunta disparada: que número desse texto o grupo
    consegue conferir por código.
  Bloco 6 (75 a 90 min)  Widget verificador sobre um texto de interpretação com erros plantados,
    declarados como exercício, e a sala apontando cada número errado. Dupla no notebook: montagem
    do prompt, chamada opcional à OpenRouter (pulada sem chave) e o verificador automático rodando
    sobre a resposta.
  Bloco 7 (90 a 105 min)  Quiz de verificação de três perguntas e amarração com a Sprint 5: o A5
    (1, a confirmar na Adalove), a Ponderada 2 (3, a confirmar na Adalove), com cesta e perfil de
    cliente individualizados pelo último dígito do RA, e o fechamento do módulo na review da Sprint
    5, com data a confirmar na Adalove.

Depois do encontro
  Desafio do notebook: reotimizar em três janelas e registrar quanto cada peso varia, com a leitura
    escrita do que isso significa para a recomendação ao comitê.
  Avanço do A5: endpoint de interpretação e painel na aplicação, prompt versionado no SPEC.md,
    plano de testes do verificador e o ADR da escolha de modelo com o custo medido.
  Leitura complementar: capítulo de limitações de LLM do autoestudo da semana, relido contra o
    texto que a própria ferramenta do grupo gerou.

---

Os valores numéricos das Aulas 02 a 06 não entram agora: cada aula mede os seus na própria task de
medições, e este planejamento é atualizado com eles. Os números da Aula 01 vêm do ensaio de
17/09/2026, e a task de medições da Aula 01 é que vai travá-los em teste. Até lá, sete deles ficam
sem cobertura de teste: 1.423 pregões, 39,25%, 33,41%, 67,17%, 1,51%, 87,12% e 616,00%. O único já
travado em `tools/tests/test_dados.py` é a razão de 26,13% entre o Adj Close e o Close da PETR4.
