# Revisão para a planilha: Computação no LBL 08 AdmTech (2026-2B), 17/09/2026

Complemento do `REVISAO-LBL08-COMPUTACAO.md` (16/06/2026), no mesmo formato e com o mesmo mapa de
preenchimento. Traz apenas o que mudou nas decisões de 17/09/2026 e está pronto para lançar:

- Aba "Instruções Computação": título e descrição das instruções 5 e 6, e os dois autoestudos de
  cada uma nas colunas A a I.
- Aba "Artefatos": linhas com D = COM dos artefatos A4 e A5, colunas E (título), F (descrição
  completa) e G (entregáveis e critérios).

As instruções 1 a 4 e os artefatos A1 a A3 seguem como estão no REVISAO de junho. Lançar na
planilha e na Adalove é um passo separado, feito pelo professor.

## 1. O que muda em relação à revisão de 16/06

| # | Decisão de 17/09/2026 | Efeito na planilha |
|---|---|---|
| 1 | A parte web sobe para a Sprint 4. O A4 (semana 8) passa a ser o otimizador de Markowitz entregue dentro de uma aplicação web, e o A5 (semana 10) fica só com a interpretação da carteira por LLM. | colunas E, F e G de A4 e A5 reescritas (seções 6 e 7) |
| 2 | A aplicação web usa FastAPI e uma página HTML/JS. O Streamlit sai do módulo. | descrição da instrução 5, texto de A4 e de A5, e o case de créditos OpenRouter (seção 8) |
| 3 | As instruções das semanas 8 e 9 trocam de conteúdo: a semana 8 passa a ensinar a parte web, validação e robustez descem para a semana 9 junto com a interpretação por LLM, e a Ponderada 2 acompanha esse conteúdo para a semana 9. | título e descrição das instruções 5 e 6 (seções 2 e 3) e os quatro autoestudos (seções 4 e 5) |
| 4 | As aulas seguem sala de aula invertida explícita, com uso intenso de imagem, animação e notebooks prontos para o Colab. | carga e formato dos autoestudos das semanas 8 e 9 |
| 5 | A mídia é produzida por código, com animações renderizadas sobre os dados reais e widgets interativos dentro do deck. Vídeo de terceiros não é embutido no deck. | vídeo entra como complemento no campo Objetivo do autoestudo, com link |

## 2. Instrução 5 (semana 8, aula 38)

**Título do encontro:** Do Script ao Produto: API em FastAPI e Página Web

**Descrição:** O otimizador sai do notebook e vira produto: cliente e servidor, HTTP e JSON, uma
API em FastAPI com validação de entrada e documentação automática, e uma página HTML que consome a
API com fetch e desenha a fronteira com Plotly.js. A aula integra os módulos das sprints anteriores
sem copiar código e prepara o A4.

## 3. Instrução 6 (semana 9, aula 43)

**Título do encontro:** Validação, Robustez e Interpretação com LLM

**Descrição:** Primeiro, desconfiar do próprio otimizador: divisão temporal entre treino e teste,
backtest fora da amostra, drawdown e instabilidade dos pesos entre janelas. Depois, o LLM como
componente do produto: chamada no backend pela OpenRouter, prompt com os números reais, verificação
automática de cada número citado e custo por token. Alimenta o A5 e a Ponderada 2.

## 4. Autoestudos da semana 8

Os nove campos seguem as colunas da aba "Instruções Computação". O campo Semana usa a numeração
sequencial da aba, em que a instrução 5 é a semana 5.

Os dois links foram abertos em 17/09/2026 com
`curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n"`, e o que está registrado abaixo é a
URL final com código 200. As quatro páginas citadas existem em português, conferido pelo título
devolvido pelo servidor.

**Autoestudo 5.1**

- Semana: 5 | Aula: 38 | Tipo de Card: Autoestudo
- Título do Recurso: HTTP e JSON na prática: o que acontece entre a página e o servidor
- Objetivo: Chegar à aula sabendo ler uma requisição HTTP (método, URL, parâmetros de consulta e código de status) e consumir JSON com `fetch`. A página "Uma visão geral do HTTP" cobre a anatomia da requisição e da resposta; a página "Usando Fetch" mostra a chamada no navegador e o tratamento do JSON devolvido, em https://developer.mozilla.org/pt-BR/docs/Web/API/Fetch_API/Using_Fetch . O ponto é reconhecer as partes de uma requisição antes de escrever a primeira rota na aula.
- Tempo estimado: 50 min
- Referência Bibliográfica: MDN WEB DOCS. Uma visão geral do HTTP. Mozilla, 2026. Disponível em: https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Guides/Overview . Acesso em: 17 set. 2026. MDN WEB DOCS. Usando Fetch. Mozilla, 2026. Disponível em: https://developer.mozilla.org/pt-BR/docs/Web/API/Fetch_API/Using_Fetch . Acesso em: 17 set. 2026.
- Link: https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Guides/Overview
- Qtde. Pontos: sem pontos

**Autoestudo 5.2**

- Semana: 5 | Aula: 38 | Tipo de Card: Autoestudo
- Título do Recurso: Primeira API com FastAPI: rotas, parâmetros e validação
- Objetivo: Seguir os capítulos "Primeiros Passos" e "Parâmetros de Consulta" do tutorial oficial em português, o segundo em https://fastapi.tiangolo.com/pt/tutorial/query-params/ , e subir uma rota GET que devolve JSON, testada na documentação automática em `/docs`. Trocar o exemplo do tutorial por um cálculo da cesta do grupo, para chegar à aula com o ambiente pronto e uma rota própria funcionando.
- Tempo estimado: 70 min
- Referência Bibliográfica: FASTAPI. Primeiros Passos. Documentação oficial do FastAPI em português. Disponível em: https://fastapi.tiangolo.com/pt/tutorial/first-steps/ . Acesso em: 17 set. 2026. FASTAPI. Parâmetros de Consulta. Disponível em: https://fastapi.tiangolo.com/pt/tutorial/query-params/ . Acesso em: 17 set. 2026.
- Link: https://fastapi.tiangolo.com/pt/tutorial/first-steps/
- Qtde. Pontos: sem pontos

## 5. Autoestudos da semana 9

O campo Semana usa a numeração sequencial da aba, em que a instrução 6 é a semana 6. O autoestudo
6.1 é o 5.1 de junho, movido para esta semana e ampliado com o capítulo de limitações de LLM. O
autoestudo 6.2 é a Ponderada 2, movida da semana 8, com a referência inalterada.

**Autoestudo 6.1**

- Semana: 6 | Aula: 43 | Tipo de Card: Autoestudo
- Título do Recurso: Os limites do otimizador e do LLM: premissas, sensibilidade e alucinação
- Objetivo: Entender por que uma carteira ótima no papel pode falhar na prática e por que um texto gerado por LLM pode citar um número que não existe. Os capítulos de Lachtermacher tratam de programação não linear e de otimização aplicada, com atenção às premissas e à sensibilidade das soluções; o cap. 12 de Hirota cobre as limitações conhecidas dos modelos de linguagem, inclusive alucinação, em https://integrada.minhabiblioteca.com.br/reader/books/9786587019635 . Complemento prático em vídeo: "Aula 12 - Simulação de Monte Carlo e Drawdowns", do canal Outspoken Market (20min18), em https://www.youtube.com/watch?v=jJ6mZuI28kQ , que mostra como medir a perda máxima de uma estratégia.
- Tempo estimado: 90 min
- Referência Bibliográfica: LACHTERMACHER, G. Pesquisa operacional na tomada de decisões. 5. ed. Rio de Janeiro: LTC, 2016. cap. 7 (p. 153) e cap. 8 (p. 171). HIROTA, F. ChatGPT e inteligência artificial: uso e aplicações na era digital. São Paulo: Actual, 2023. cap. 12 (p. 174).
- Link: https://integrada.minhabiblioteca.com.br/reader/books/9788521630494
- Qtde. Pontos: sem pontos

**Autoestudo 6.2 (Ponderada 2)**

- Semana: 6 | Aula: 43 | Tipo de Card: Autoestudo
- Título do Recurso: Atividade Ponderada 2: A carteira ótima sobrevive fora da amostra?
- Objetivo: Otimizar uma carteira numa janela de treino, testá-la fora da amostra, medir a instabilidade dos pesos e recomendar ao comitê qual carteira indicar para o perfil de cliente recebido, dizendo quanto confiar no modelo. Enunciado completo e barema na seção 4 do `REVISAO-LBL08-COMPUTACAO.md`.
- Tempo estimado: 120 min
- Referência Bibliográfica: BODIE, Z.; KANE, A.; MARCUS, A. Fundamentos de investimentos. 9. ed. Porto Alegre: AMGH, 2014. cap. 6, p. 148 (risco de estimação e diversificação eficiente).
- Link: https://integrada.minhabiblioteca.com.br/reader/books/9788580553789
- Qtde. Pontos: 3

## 6. Artefato A4 (Sprint 4, 2 pontos)

**Coluna E (título):** Otimizador de Carteira com Fronteira Eficiente em Aplicação Web

**Coluna F (descrição):**

Contexto e propósito: O coração matemático da ferramenta chega a quem decide. A Sprint 3 mostrou o
espaço de possibilidades e a Sprint 4 entrega a carteira ótima dentro de uma aplicação que um
gestor do parceiro opera sem abrir código. É a entrega que materializa a Teoria de Markowitz nos
limites de tolerância a risco definidos pelos gestores, em um produto que se pode demonstrar numa
reunião.

O que é: Uma otimização SLSQP exposta por uma API em FastAPI e consumida por uma página HTML/JS que
desenha a Fronteira Eficiente sobre a nuvem de Monte Carlo da sprint anterior.

O que é esperado:

Carteira de variância mínima global e carteira de máximo Índice de Sharpe, cada uma com pesos,
retorno esperado, volatilidade e Sharpe. Fronteira Eficiente traçada com 50 pontos de retorno alvo.
Endpoints documentados automaticamente em /docs. Validação de entrada com mensagem clara para
ticker inválido e para período sem dados. Página com formulário, gráfico integrando nuvem,
fronteira e os dois pontos ótimos, e tabela de pesos. A API importa os módulos dos artefatos
anteriores sem copiar código. Restrições respeitadas: pesos somam 1 e nenhum é negativo (sem short
selling). Convergência em menos de 5 segundos para carteiras de até 15 ativos.

O que não é esperado:

Deploy público com autenticação e controle de acesso. Interpretação por LLM, que é o artefato da
Sprint 5. Design visual elaborado, com a exigência limitada a uma página legível e operável. Short
selling, alavancagem ou custos de transação. Modelos além de média-variância (Black-Litterman,
paridade de risco).

Objetivos de aprendizagem: Formular um problema de otimização com função objetivo, restrições e
limites e resolvê-lo com o SciPy; expor um cálculo Python por uma API HTTP com contrato explícito;
validar entrada de usuário no servidor; consumir a API no navegador e desenhar o resultado;
interpretar os pesos ótimos como decisão de alocação.

Formato de entrega: Repositório do grupo com a aplicação rodando, o comando `uvicorn` documentado
no README, SPEC.md com os contratos dos endpoints e o plano de testes com `TestClient`, e ADRs em
/docs/adr/. Demonstração funcional na review da sprint.

Critérios de avaliação: detalhados na coluna de entregáveis, com pesos por dimensão.

Observação importante: O otimizador converge para o passado, e os pesos ótimos valem para a janela
histórica escolhida. O produto acrescenta um risco novo. Uma entrada inválida sem mensagem clara
derruba a confiança do parceiro antes de o gráfico aparecer na tela. Testem períodos diferentes,
observem a instabilidade dos pesos e tratem a validação de entrada como parte da entrega.

**Coluna G (entregáveis e critérios):**

Entregáveis: SPEC.md com contratos dos endpoints e plano de testes; otimizador com SLSQP dentro da
API; API em FastAPI com validação e /docs; página HTML/JS com formulário, gráfico e tabela de
pesos; testes com `TestClient`; README com o comando de execução; ADRs em /docs/adr/.

Corretude da otimização (25%): as duas carteiras ótimas corretas, restrições de soma 1 e não
negatividade respeitadas, convergência em menos de 5 segundos para até 15 ativos.

API documentada, validada e testada (15%): endpoints com tipos anotados e documentação em /docs,
entrada inválida respondida com código de status e mensagem claros, testes com `TestClient`
cobrindo caso de sucesso e caso de erro.

Página e fronteira (15%): formulário operável por quem não programa, gráfico integrando nuvem,
fronteira de 50 pontos e os dois ótimos, e tabela de pesos legível.

Integração sem cópia de código (10%): a API importa os módulos das sprints anteriores, sem
duplicar cálculo.

Especificação e documentação (15%): SPEC.md escrito antes de codar (objetivo, escopo, contratos dos
endpoints e plano de testes com casos-limite e um caso com os dados do grupo); README com
instruções de execução; docstrings nas funções principais.

ADRs, componente individual (20%): cada aluno registra, no formato do gist da seção 6 do REVISAO de
junho, as decisões que tomou nesta sprint (por exemplo, a fronteira entre navegador e servidor, o
contrato dos endpoints, as restrições da otimização). Avaliado aluno a aluno pela autoria dos
commits.

## 7. Artefato A5 (Sprint 5, 1 ponto)

**Coluna E (título):** Interpretação da Carteira por LLM

**Coluna F (descrição):**

Contexto e propósito: A ferramenta já calcula e já mostra. O que falta é explicar o resultado em
português, para um gestor, sem inventar número. Esta entrega fecha o ciclo do módulo, do dado bruto
à decisão assistida, e acrescenta ao produto a camada que o parceiro vai ler antes de decidir.

O que é: Um endpoint da API da Sprint 4 que envia à OpenRouter os resultados reais da otimização e
devolve um texto verificado, exibido na página da aplicação.

O que é esperado:

Chamada ao modelo feita no backend, com a chave em variável de ambiente, fora do JavaScript e fora
do git. Prompt montado com os números reais: pesos, retorno, volatilidade, Sharpe, período
analisado e o resultado fora da amostra quando houver, pedindo ao modelo que declare as limitações
da leitura. Resposta estruturada, para a aplicação separar o texto dos números citados. Verificação
automática de todo número citado pelo modelo, com tolerância declarada, e sinalização na página
quando o texto for reprovado. Tokens consumidos e custo por chamada registrados. Comparação de dois
modelos em qualidade da leitura e em custo. Falha do provedor tratada sem derrubar a aplicação.

O que não é esperado:

Chatbot ou conversa livre com o usuário. Recomendação de investimento automatizada sem ressalvas: o
texto é apoio à decisão e declara suas limitações. Ajuste fino de modelo. Recuperação aumentada por
busca (RAG).

Objetivos de aprendizagem: Integrar uma API de LLM a um software próprio, com segredo fora do
cliente; escrever e versionar um prompt que recebe dados reais como contexto; tratar e verificar a
saída de um modelo por código; raciocinar sobre custo por token e escolha de modelo como decisão de
produto.

Formato de entrega: Endpoint de interpretação e painel na aplicação do grupo, SPEC.md com o prompt
versionado e o plano de testes do verificador, README com as variáveis de ambiente necessárias, e
ADRs em /docs/adr/. Demonstração funcional na review da sprint.

Critérios de avaliação: detalhados na coluna de entregáveis, com pesos por dimensão.

Observação importante: A credibilidade da ferramenta depende de o texto ser verificável contra os
números na tela. Uma interpretação genérica ou alucinada durante a demonstração derruba a confiança
do parceiro em todo o trabalho das sprints anteriores. Tratem o prompt e o verificador como parte
do produto, testados tanto quanto o resto do código.

**Coluna G (entregáveis e critérios):**

Entregáveis: SPEC.md com o prompt versionado e o plano de testes do verificador; endpoint de
interpretação na API; painel na página exibindo o texto e o resultado da verificação; registro de
tokens e custo por chamada; comparação de dois modelos; README com as variáveis de ambiente; ADRs
em /docs/adr/.

Integração segura (15%): chamada no backend, chave em variável de ambiente, ausente do JavaScript e
do histórico do git, e falha do provedor tratada sem derrubar a aplicação.

Prompt e contexto (15%): o prompt recebe os números reais da otimização e o período analisado, pede
limitações declaradas e está versionado no repositório.

Verificação automática com testes (20%): todo número citado pelo modelo é conferido por código
contra o resultado da otimização, com tolerância declarada, texto reprovado sinalizado na página e
testes cobrindo um caso aprovado e um caso reprovado.

Custo e escolha de modelo (15%): tokens e custo por chamada registrados, com dois modelos
comparados em qualidade e custo e a escolha justificada.

Especificação e documentação (15%): SPEC.md escrito antes de codar (objetivo, escopo, contrato do
endpoint e plano de testes com casos-limite e um caso com os dados do grupo); README com as
variáveis de ambiente e instruções de execução; docstrings nas funções principais.

ADRs, componente individual (20%): cada aluno registra, no formato do gist da seção 6 do REVISAO de
junho, as decisões que tomou nesta sprint (por exemplo, desenho do prompt, escolha do modelo,
tolerância do verificador). Avaliado aluno a aluno pela autoria dos commits.

## 8. Pendências para a coordenação

Numeração do `PLANO_DE_ENSINO.md`, seção 8. As pendências P1 a P4 são fontes oficiais ainda não
lidas e se resolvem com acesso; as quatro abaixo dependem de decisão.

| # | Pendência | O que pedimos |
|---|---|---|
| P5 | O A2 (Sprint 2, semana 4) cobra matriz de correlação e de covariância, que a Instrução 3 só ensina na semana 5. | Decidir entre mover esse item do A2 para o A3 ou aceitar que a semana 4 chegue com o conteúdo antecipado pelo material de apoio. |
| P6 | O A4 vence na mesma semana da instrução que ensina a parte web. | Confirmar o dia da instrução da semana 8 na planilha de alocação e, se a folga ficar menor que dois dias, negociar a data de entrega. |
| P7 | O case de créditos OpenRouter (02/09/2026) ainda cita Streamlit e o título antigo da Instrução 6. | Atualizar o case com FastAPI, com o título "Validação, Robustez e Interpretação com LLM" e com o A5 novo. O dimensionamento aprovado continua válido: cerca de 2.800 tokens por chamada, cerca de US$ 0,002 por chamada no cenário realista, 4.000 chamadas na turma, US$ 10 provisionados e teto de US$ 20. |
| P8 | O parceiro tem nome e premissas descritos no LBL da Adalove, e o projeto não tem TAPI. | Confirmar as premissas do parceiro. Até lá, a cesta de 15 ativos da B3 documentada em `dados/README.md` é a referência das aulas. |
