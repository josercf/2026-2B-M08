# Auditoria crítica dos materiais de aula — Módulo 08 AdmTech

**Data da auditoria:** 13/10/2026  
**Escopo:** portal, plano de ensino, planejamento aula a aula, 6 decks Reveal.js, 160 slides, 6 materiais de apoio, 6 notebooks, referências, mídias, widgets e exemplo de aplicação da Aula 06.  
**Parecer:** **NÃO APROVADO PARA USO EM SALA SEM CORREÇÕES CRÍTICAS.**

O acervo tem uma base técnica acima da média: dados versionados, números reproduzíveis, narrativa cumulativa, atividades aplicadas, widgets, notebooks e uma conexão explícita entre aula e artefato avaliado. Entretanto, a qualidade do conteúdo não compensa quatro bloqueios: premissas do parceiro ainda não confirmadas; conteúdo cobrado antes de ser ensinado; não conformidade visual sistêmica com o brand kit vigente; e atividades incompatíveis com o tempo declarado. Há ainda dois riscos conceituais relevantes: a amostragem de pesos da Aula 04 induz uma conclusão incompleta sobre Monte Carlo e a “verificação” da LLM na Aula 06 é apresentada com força maior do que o algoritmo realmente oferece.

## 1. Método e limites da auditoria

Foram executadas quatro camadas de revisão:

1. Leitura integral dos documentos de planejamento e das seis trilhas de aula.
2. Revisão individual das 160 seções de slide, incluindo texto, exemplo, dado, atividade, resposta, dependência e tempo de execução.
3. Inspeção no Google Chrome do portal publicado e de amostras representativas dos principais tipos de slide: capa, professor, combinados, agenda, quiz com feedback, código com tabela, widget e nota de rodapé. O conteúdo de todos os slides foi auditado individualmente; a inspeção visual no navegador foi dirigida às tipologias e aos slides de maior risco, não a 160 capturas independentes.
4. Execução dos validadores e testes disponíveis no repositório.

O portal publicado abriu corretamente em `https://josercf.github.io/2026-2B-M08/`. O quiz da Aula 01 respondeu ao clique e exibiu feedback sem estouro aparente. A revisão no navegador confirmou problemas sistêmicos que o validador atual não detecta: cantos arredondados, cápsulas, círculos com conteúdo, tipografia fora dos pesos vigentes e excesso de densidade em agendas e slides técnicos.

Resultados técnicos:

- `tools/check_brand.py`: aprovado, mas com cobertura insuficiente para o brand kit vigente.
- `tools/check_links.py`: aprovado.
- suíte `pytest`: **497 aprovados, 6 falhas e 44 erros**. As 6 falhas e os 44 erros concentram-se em testes que tentam abrir servidor local ou navegador e foram afetados pelas restrições do ambiente a `bind(127.0.0.1, porta)` e ao lançamento de Chromium automatizado. Portanto, não são evidência de defeito do material nem de aprovação visual.
- `check_slides.py` e `check_widgets.py`: não concluídos pelo mesmo bloqueio de porta local.

## 2. Parecer executivo

| Dimensão | Nota / 5 | Parecer |
|---|---:|---|
| Coerência curricular | 2,5 | A progressão é boa, mas o A2 cobra correlação/covariância antes da aula que ensina o tema. |
| Correção e profundidade conceitual | 3,4 | Forte em dados e otimização; insuficiente em viés de amostragem, custos, independência das janelas e limites da LLM. |
| Clareza dos exemplos | 3,8 | Números reais e comparações concretas são um ponto forte; faltam mais intuição visual e explicitação de premissas. |
| Atividades e aprendizagem ativa | 2,4 | Boas intenções, mas diversas tarefas de 8–12 min exigem 20–40 min para execução e reflexão reais. |
| Carga de autoestudo | 2,2 | Em semanas críticas ultrapassa duas ou três horas antes de vídeos, animações e questionários. |
| Design visual e projeção | 2,1 | Consistente internamente, porém denso e incompatível com normas vigentes de forma, ícone e tipografia. |
| Avaliação e critérios | 3,6 | Rubricas e entregáveis estão explícitos; há pendências de peso, duplicidade, datas e alinhamento. |
| Engenharia e reprodutibilidade | 4,2 | Dados versionados, notebooks, testes e fallback local são excelentes práticas. |
| Governança para publicação | 1,8 | Parceiro, LBL, horários, duplicidade do A4 e case de OpenRouter ainda estão pendentes. |

### Decisão de auditoria

O material pode virar um curso excelente, mas **não deve ser considerado “pronto”**. O mínimo para liberação é resolver os achados C-01 a C-08. O professor conseguiria ministrar as aulas atuais, mas dependeria de improvisar cortes, explicar ressalvas que não estão nos slides e administrar inconsistências curriculares diante de uma turma capaz de detectá-las.

## 3. Achados críticos e orientação corretiva

### C-01 — O caso do parceiro está apoiado em premissas não confirmadas

**Evidência.** O plano informa que BTG Pactual, setor, premissas e cesta de 15 ativos aguardam leitura do LBL; o próprio plano classifica isso como P4.  
**Risco.** A turma pode receber um caso apresentado como real, mas construído sobre hipótese interna. Isso compromete credibilidade, alinhamento com o parceiro e avaliação dos artefatos.  
**Orientação.** Antes da Aula 01, ler o LBL oficial; registrar fonte, problema, usuário, restrições, ativos e critério de sucesso; marcar explicitamente o que é requisito do parceiro e o que é decisão didática.  
**Critério de aceite.** Nenhuma capa, exemplo, rubrica ou atividade atribui ao parceiro uma afirmação sem fonte identificada.

### C-02 — O A2 cobra conteúdo antes de ele ser ensinado

**Evidência.** O A2, associado à Aula 02, cobra matriz de correlação e covariância; o conceito é ensinado formalmente apenas na Aula 03. O material tenta remediar isso com uma antecipação mínima.  
**Risco.** O curso avalia autonomia de pesquisa como se fosse domínio já ensinado, e a Aula 03 chega depois da necessidade avaliativa.  
**Orientação.** Escolher uma única solução institucional: mover esses critérios para o A3; antecipar 30–45 min do tema para a Aula 02; ou transformar a parte do A2 em diagnóstico não pontuado. Não deixar a correção depender de aviso oral.  
**Critério de aceite.** A matriz de alinhamento mostra, para cada critério avaliativo, a aula anterior em que o conteúdo foi modelado e praticado.

### C-03 — Datas, horários e entregas ainda não formam um contrato confiável

**Evidência.** Horários seguem “a confirmar”; o A4 aparece com mesmo título e peso nas Sprints 3 e 4; a revisão do A3 está marcada para 19/11 e a entrega para 20/11 às 23h59; o dia real de algumas aulas depende de planilha ainda não lida.  
**Risco.** O deck comunica precisão onde a governança ainda é incerta. Alunos exigentes interpretarão isso como falha de coordenação.  
**Orientação.** Publicar uma tabela única, com versão e data, contendo aula, instrução, sprint, artefato, peso, prazo, revisão e responsável. Remover datas provisórias dos slides até confirmação.  
**Critério de aceite.** Plano, portal, decks e Adalove exibem a mesma informação, sem duplicidade ou ressalva oral.

### C-04 — O sistema visual reprova no brand kit vigente

**Evidência.** Há `border-radius` de 6 a 999 px em cartões, quiz, perfil, cronômetro, botões, materiais e portal; círculos carregam número e controle; sombras marcam estados. A norma vigente GRA-01 exige cantos retos e proíbe círculos carregando conteúdo.  
**Risco.** A inconsistência é sistêmica, não cosmética. Corrigir slide a slide será caro e continuará gerando regressões.  
**Orientação.** Corrigir os componentes-base: remover arredondamento e pílulas; substituir círculos numerados por formas retangulares do sistema; usar filetes, blocos ortogonais e cor plana; remover sombras como indicador de estado.  
**Critério de aceite.** Busca por `border-radius` e `box-shadow` nos CSS não encontra exceções não justificadas; inspeção visual confirma hierarquia sem “cards de aplicativo”.

### C-05 — Iconografia e pesos tipográficos estão desatualizados

**Evidência.** O projeto carrega `Material Symbols Outlined` via CDN. A norma atual pede Material Symbols Sharp, preferencialmente SVG vetorial. Títulos usam peso 500 e corpo tende a 400; o kit vigente define títulos 700, subtítulos 600 e corpo Manrope Light 300.  
**Risco.** O validador declara conformidade porque testa regras antigas e cria falsa sensação de aprovação.  
**Orientação.** Atualizar tokens e componentes; substituir a fonte remota por SVGs Sharp versionados; estabelecer matriz de pesos por função e teste automatizado correspondente.  
**Critério de aceite.** Nenhum uso de `material-symbols-outlined`; títulos, subtítulos e corpo seguem TIP-04; o `check_brand.py` falha deliberadamente diante de uma fixture fora do padrão.

### C-06 — A densidade de projeção é excessiva

**Evidência.** Agendas chegam a oito linhas e mais de 160 palavras; slides combinam código, tabela, conclusão e nota; textos de 14–16 px são usados em elementos densos. O slide `aula03#/covariancia`, visto no Chrome, exige ler código, matriz e ressalva ao mesmo tempo.  
**Risco.** O aluno alterna entre ouvir, copiar e decodificar uma tela que funciona melhor como apostila. Em sala, o fundo da turma perderá legibilidade.  
**Orientação.** Uma ideia principal por slide; dividir código e resultado; usar revelação progressiva; mover ressalvas longas para notas/material; manter corpo projetado em tamanho equivalente a pelo menos 17–18 pt e código realmente necessário.  
**Critério de aceite.** Cada slide pode ser compreendido em 10 segundos sem fala; nenhum slide tem mais de dois objetos cognitivos primários.

### C-07 — As atividades não cabem no tempo declarado

**Evidência.** Há práticas de 8–12 min que pedem abrir notebook, localizar seção, carregar dados, executar, alterar parâmetros, depurar, comparar, discutir e produzir ADR ou texto.  
**Risco.** O professor terminará fazendo demonstração, os alunos mais rápidos dominarão a dupla e a reflexão será cortada. A promessa de aprendizagem ativa vira preenchimento apressado.  
**Orientação.** Para cada atividade, separar **obrigatório / extensão / depois da aula**; fornecer célula inicial pronta; definir checkpoint observável aos 4 e 8 min; prever solução de contingência; reservar 3–5 min para debrief.  
**Critério de aceite.** Ensaio com aluno representativo conclui a parte obrigatória em 70% do tempo reservado, deixando margem para instrução e falha técnica.

### C-08 — A carga de autoestudo não está calibrada

**Evidência.** Semanas como Aula 03 e Aula 05 somam 190–200 min de leituras e materiais antes de vídeos, animações, quiz e trabalho de sprint.  
**Risco.** A preparação compete com as entregas do próprio módulo; quem não consegue cumprir chega à aula já excluído da dinâmica invertida.  
**Orientação.** Definir trilha mínima de 30–45 min, trilha recomendada de até 90 min e aprofundamento opcional. Abrir a aula com recuperação suficiente para quem fez apenas o mínimo.  
**Critério de aceite.** Cada item tem duração medida, prioridade e evidência de aprendizagem; a soma obrigatória semanal não excede o teto acordado com a coordenação.

### C-09 — A Aula 04 ensina Monte Carlo com uma distribuição de pesos enviesada

**Evidência.** O notebook sorteia pesos `Uniform(0,1)` e normaliza pela soma. Isso **não** gera distribuição uniforme no simplex e subamostra regiões de alta concentração. Os slides atribuem o afastamento da ótima principalmente à quantidade de sorteios e à concentração rara.  
**Risco.** O aluno conclui que “Monte Carlo precisa de milhões” sem perceber que o gerador escolhido já impõe um viés geométrico. A comparação com SLSQP fica pedagogicamente injusta.  
**Orientação.** Ensinar três casos: pesos uniformes normalizados atuais; `Dirichlet(alpha=1)` para uniformidade no simplex; `Dirichlet(alpha<1)` para explorar vértices. Mostrar que amostragem, dimensionalidade e objetivo explicam o resultado, e que otimização continua necessária.  
**Critério de aceite.** O deck nomeia a distribuição, mede cobertura/concentração e a atividade compara pelo menos dois esquemas com a mesma semente e orçamento.

### C-10 — A régua de correlação vira regra decisória sem fundamento suficiente

**Evidência.** A Aula 03 classifica pares com limiares como ≥0,60 “concentra” e <0,30 “diversifica”.  
**Risco.** Correlação sozinha não determina redução de risco: pesos e volatilidades importam; a correlação também é instável e dependente da janela.  
**Orientação.** Rotular os limiares como heurística exploratória, nunca como regra universal. Para cada par, calcular o risco da carteira com pesos explícitos e comparar à média ponderada dos riscos individuais.  
**Critério de aceite.** Nenhuma conclusão “diversifica/concentra” aparece sem peso, volatilidade, janela e medida de redução de risco.

### C-11 — A validação da Aula 05 superestima 33 janelas sobrepostas

**Evidência.** São apresentadas 33 janelas móveis com treino de 24 meses e teste de 12 meses, deslocadas mês a mês. Esses testes compartilham grande parte dos mesmos retornos.  
**Risco.** “25 de 33” soa como 33 observações independentes, quando a evidência tem forte dependência temporal.  
**Orientação.** Explicitar sobreposição; complementar com blocos não sobrepostos, walk-forward com rebalanceamento definido ou bootstrap em blocos. Reportar distribuição e duração dos regimes, não apenas contagem.  
**Critério de aceite.** O aluno consegue explicar por que 33 janelas não equivalem a 33 experimentos independentes.

### C-12 — O ADR prescreve reotimização mensal sem custo de transação

**Evidência.** O material admite “sem custo de transação”, mas o exemplo de ADR recomenda reotimizar todo mês apesar de alta troca de pesos.  
**Risco.** A recomendação pode piorar o resultado líquido e confunde estabilidade estatística com política operacional.  
**Orientação.** Incluir turnover, custo por operação, slippage, impostos simplificados, limite por ativo e liquidez. Comparar mensal, trimestral e gatilho por desvio.  
**Critério de aceite.** Toda recomendação de rebalanceamento apresenta resultado líquido e turnover, ou é claramente rotulada como exercício sem recomendação prática.

### C-13 — O “verificador de números” da LLM não verifica fatos

**Evidência.** O algoritmo verifica presença/aproximação numérica. O próprio exemplo mostra que um número correto associado ao ativo errado pode passar. Ainda assim, a API e o deck falam em “verificação de cada número”.  
**Risco.** A turma pode confundir correspondência lexical com grounding, consistência semântica ou segurança contra alucinação.  
**Orientação.** Renomear para “checagem de presença numérica”; usar saída estruturada com campo, ativo, unidade, período e valor; validar cada afirmação contra o JSON fonte; separar validação determinística de avaliação textual.  
**Critério de aceite.** Um número correto atribuído ao ativo, unidade ou período errado reprova automaticamente.

### C-14 — A Aula 06 tenta ensinar produto, API, frontend e LLM em uma sessão

**Evidência.** Em 105 min entram contrato HTTP, Pydantic, FastAPI, cache, testes, React, proxy, CORS, segredo, prompt, provedor e verificação.  
**Risco.** A aula vira tour tecnológico e não deixa competência transferível clara.  
**Orientação.** Escolher objetivo central: “transformar um módulo em API testável”. Entregar o frontend pronto como consumidor; deixar LLM como extensão ou segunda instrução.  
**Critério de aceite.** Ao final, todo aluno implementa e testa uma rota; frontend e LLM não são pré-requisitos para o objetivo principal.

### C-15 — Semântica HTTP é ensinada como certeza onde há escolha de contrato

**Evidência.** Ticker inexistente recebe 404 e o deck pergunta “por que 404 em vez de 422?”. Como o ticker está no corpo de um `POST`, 422 também é uma decisão defensável para falha de domínio/validação.  
**Risco.** O aluno memoriza um código sem entender recursos, representação e convenção da API.  
**Orientação.** Apresentar 404 e 422 como alternativas de design; adotar um padrão documentado com exemplos de erro estáveis.  
**Critério de aceite.** O aluno justifica a escolha pelo contrato, não por uma regra absoluta.

## 4. Auditoria slide a slide

Legenda: **C** = crítico; **R** = revisar; **A** = aprovado com ajuste pequeno. Os achados sistêmicos de marca, tipografia e densidade aplicam-se a todos os slides e não são repetidos em cada linha.

### Aula 01 — Do dado bruto à decisão auditável (28 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | A | Boa promessa e hierarquia. Reduzir elementos decorativos concorrentes e explicitar o resultado observável da aula. |
| 2 | professor | R | Painel muito grande e arredondado, com espaço morto. Usar composição ortogonal, bio em três linhas e foco em por que o professor é relevante ao caso. |
| 3 | combinados | R | Contrato útil, mas excessivamente administrativo. Transformar em quatro princípios acionáveis e mover detalhes para o portal. |
| 4 | agenda | R | Oito linhas e alta densidade antes de gerar curiosidade. Substituir por três atos: problema, investigação e decisão. |
| 5 | parceiro | C | Parceiro e premissas ainda não confirmados no LBL. Não apresentar hipótese como briefing oficial. |
| 6 | entregas | C | Dependências avaliativas herdam incertezas de A2/A4. Mostrar apenas entregas confirmadas e linkar matriz viva de avaliação. |
| 7 | preparo | R | A preparação é extensa e mistura obrigatório com complementar. Marcar mínimo, recomendado e aprofundamento. |
| 8 | fim-exclusivo | A | Bom gatilho conceitual. Acrescentar uma microdecisão: “qual preço usaria e qual risco aceitaria?”. |
| 9 | section | A | Divisor claro, mas consome tela. Manter apenas se houver mudança real de objetivo; usar tempo e pergunta-guia. |
| 10 | mglu3 | A | Exemplo forte e memorável. Explicitar fonte, data do evento e diferença entre retorno econômico e salto mecânico. |
| 11 | visoes | A | Boa comparação entre Close, Adjusted Close e total return. Destacar visualmente uma única conclusão por vez. |
| 12 | widget-visoes | A | Interatividade pertinente. Incluir instrução de 20 segundos, estado inicial e pergunta que exija previsão antes do clique. |
| 13 | escolha-visoes | R | A escolha favorece resposta correta por redação. Tornar distratores conceitualmente plausíveis e pedir justificativa em uma frase. |
| 14 | proventos | A | Exemplo necessário. Incluir fórmula mínima e um caso em que o dado ajustado não atende à pergunta de negócio. |
| 15 | section | A | Transição válida para coleta. Trocar rótulo genérico por uma pergunta operacional sobre rastreabilidade. |
| 16 | coletar | R | Pipeline útil, porém abstrato. Mostrar entrada, transformação, saída e log de proveniência num único fluxo visual. |
| 17 | pratica-coletor | R | Em 12 min há dependência de ambiente e rede. Entregar célula pronta, fallback obrigatório e checkpoint aos 5 min. |
| 18 | section | A | Transição para ausências é coerente. Antecipar a pergunta “ausência é erro, informação ou calendário?”. |
| 19 | mapa-ausencias | A | Visualiza o problema real. Separar feriado local, falha de fonte e ativo sem negociação. |
| 20 | widget-ausencias | A | Excelente para consequência de imputação. Pedir previsão do viés antes de alternar o tratamento. |
| 21 | volatilidade | R | O número é elucidativo, mas pode sugerir causalidade única. Explicitar janela, anualização e que o efeito depende do tratamento. |
| 22 | adr | A | Boa conexão entre técnica e decisão. Mostrar também uma alternativa rejeitada e sua consequência. |
| 23 | pratica-ausencias | C | Diagnóstico, dois tratamentos, comparação e ADR não cabem no tempo. Tornar um tratamento obrigatório e outro extensão. |
| 24 | quiz-final | A | Verifica pontos-chave. Acrescentar uma questão de transferência, não apenas recordação do caso visto. |
| 25 | notebook | R | Índice útil, porém detalhado demais para projeção. Mostrar só rota mínima e deixar mapa completo no material. |
| 26 | a1 | C | Rubrica depende de briefing ainda provisório. Revisar após confirmação do LBL e explicitar evidência mínima por critério. |
| 27 | referencias | A | Referências existem e são rastreáveis. Diferenciar fonte de dado, documentação técnica e leitura conceitual. |
| 28 | end | A | Encerramento limpo. Trocar despedida genérica por “saída da aula” com artefato e próxima decisão. |

### Aula 02 — Do preço ao retorno e ao risco (28 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | A | Tema claro. Formular o conflito central: um ativo “subiu” dependendo de qual retorno e janela? |
| 2 | agenda | R | Agenda muito operacional. Resumir em preço → retorno → distribuição → risco → decisão. |
| 3 | resgate | A | Boa recuperação. Usar uma pergunta de baixa latência que exponha confusão entre preço ajustado e retorno. |
| 4 | case | C | O A2 inclui conteúdo ainda não ensinado. Exibir no slide a solução institucional, não uma ressalva oral. |
| 5 | preparo | R | Carga alta. Definir trecho indispensável e resultado esperado do pré-estudo. |
| 6 | queda | A | Exemplo concreto. Contrastar queda percentual simples com soma de retornos para desmontar intuição errada. |
| 7 | section | A | Boa transição. Dar título conceitual, não apenas nome de seção. |
| 8 | definicoes | R | Duas fórmulas e propriedades podem sobrecarregar. Usar linha do tempo de dois preços e revelar uma fórmula por vez. |
| 9 | crise | A | Caso autêntico. Indicar datas, fonte e por que o log-retorno facilita composição, sem vendê-lo como “melhor” universal. |
| 10 | widget-simples-log | A | Widget pertinente. Pedir previsão de quando a diferença importa materialmente. |
| 11 | pandas | R | Código projetado tende a virar leitura passiva. Destacar três linhas essenciais e mover boilerplate ao notebook. |
| 12 | pratica-retornos | R | Tarefas demais para 12 min. Fixar um ativo e uma pergunta; deixar comparação ampla como extensão. |
| 13 | section | A | Transição correta para distribuição. Ancorar com “média esconde cauda?”. |
| 14 | histograma | A | Visual adequado. Incluir eixo, unidade, período, tamanho amostral e marcação do evento extremo. |
| 15 | caudas | R | Evitar simplificar normalidade como teste binário. Comparar quantis empíricos e normais e discutir implicação de decisão. |
| 16 | section | A | Mudança para anualização é válida. Conectar a pergunta de negócio antes da fórmula. |
| 17 | conta | A | Exemplo numérico é didático. Deixar clara a convenção de 252 pregões e sua natureza aproximada. |
| 18 | raiz-do-tempo | R | A raiz do tempo requer independência/estacionariedade aproximadas. Explicitar hipóteses e quando falha. |
| 19 | widget-janela | A | Excelente para mostrar sensibilidade. Acrescentar comparação de regime e não só valor final. |
| 20 | cesta | R | Tabela de 15 ativos é consulta, não slide. Projetar ranking/intervalo e deixar tabela completa no material. |
| 21 | pratica-cesta | C | Calcular tabela inteira, comparar CDI e julgar em 12 min é irreal. Distribuir ativos entre grupos e fazer síntese coletiva. |
| 22 | escolha-risco | R | A decisão é boa, mas o enunciado precisa declarar horizonte, tolerância e objetivo; risco sem contexto não é decisão. |
| 23 | quiz-final | A | Cobre fundamentos. Incluir hipótese da anualização e um erro de agregação temporal. |
| 24 | notebook | R | Reduzir índice projetado; mostrar caminho mínimo e checkpoints de saída. |
| 25 | a2 | C | Não pode cobrar matriz formal antes da Aula 03. Corrigir alinhamento e rubrica antes de publicar. |
| 26 | p5 | C | É evidência explícita de falha curricular. Este slide não resolve o problema; precisa ser substituído por decisão confirmada. |
| 27 | referencias | A | Boa base. Adicionar referência específica para hipóteses de volatilidade anualizada e caudas. |
| 28 | end | A | Fechamento adequado. Encerrar com a tabela/figura que o aluno deve conseguir produzir sozinho. |

### Aula 03 — Correlação, covariância e diversificação (28 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | A | Promessa relevante. Incluir a tensão: correlação observada não é propriedade fixa. |
| 2 | agenda | R | Oito passos fragmentam a narrativa. Agrupar em medir, interpretar e decidir. |
| 3 | resgate | A | Bom elo com volatilidade. Fazer o aluno calcular verbalmente o risco de dois ativos antes da fórmula. |
| 4 | preparo | R | Carga de pré-estudo muito alta. Definir trilha mínima de 45 min e questões diagnósticas. |
| 5 | conta | A | Exemplo de dois ativos é forte. Mostrar decomposição visual das parcelas própria e cruzada. |
| 6 | section | A | Transição pertinente. Usar “o que a correlação não diz?” como pergunta-guia. |
| 7 | definicoes | R | Covariância, correlação, unidade e interpretação no mesmo slide. Dividir em duas telas e usar unidades explícitas. |
| 8 | heatmap | A | Bom uso de matriz real. Ordenar ativos por classe/setor ou clustering para tornar padrão visível. |
| 9 | pares | R | Rankings são úteis, mas pedem explicação econômica e cautela com data mining. Solicitar hipótese antes de revelar. |
| 10 | animacao-curva | A | Ótima intuição. Fixar volatilidades e pesos visivelmente para evitar atribuir todo efeito só à correlação. |
| 11 | widget-peso | A | Interação central à aula. Incluir marcador da média ponderada de riscos como referência. |
| 12 | tres-pares | A | Comparação elucidativa. Exibir também a redução percentual de risco, não apenas correlação. |
| 13 | section | A | Boa passagem à matriz. Relacionar dimensão 15×15 ao número de parâmetros estimados. |
| 14 | covariancia | R | Código, matriz e conclusão competem; no Chrome o slide é legível, mas denso. Separar construção e leitura da diagonal. |
| 15 | custo-janela | A | Excelente consequência concreta da janela comum. Explicitar que comparabilidade é comprada com perda de histórico. |
| 16 | pratica-matriz | C | Carregar, calcular, plotar, trocar par e interpretar não cabe no tempo. Fornecer matriz pronta e focar em leitura/decisão. |
| 17 | section | A | Transição válida para instabilidade. Formular hipótese: “a correlação sobe justamente quando precisamos dela?”. |
| 18 | animacao-movel | A | Excelente visual temporal. Acrescentar janela, frequência e intervalo de datas sempre visíveis. |
| 19 | crise | R | Média 0,36 versus 0,74 é convincente, mas uma janela/evento não prova lei geral. Rotular como evidência do caso. |
| 20 | ledoit-wolf | R | Introduz shrinkage rapidamente. Explicar alvo, trade-off viés-variância e por que intensidade cai com mais dados. |
| 21 | escolha-pares | C | Limiar de correlação é heurístico e insuficiente para dizer “diversifica”. Pedir cálculo de risco com pesos e volatilidades. |
| 22 | so-bancos | R | Boa provocação, mas “só bancos” mistura setor, fator e concentração. Explicitar qual hipótese está sendo testada. |
| 23 | bancos | A | Resultado forte. Mostrar pesos usados e decompor quanto vem de correlação versus volatilidade. |
| 24 | quiz-final | R | Evitar premiar memorização dos limiares arbitrários. Avaliar leitura de matriz e efeito conjunto de peso/correlação. |
| 25 | notebook | R | O mapa é completo, mas projetivamente denso. Destacar apenas células indispensáveis à prática. |
| 26 | a3 | R | Boa conexão com o motor. Incluir testes de forma, simetria, diagonal e semidefinição positiva. |
| 27 | referencias | A | Referências adequadas. Acrescentar fonte primária/introdutória de Ledoit–Wolf e instabilidade de correlação. |
| 28 | end | A | Encerramento coerente. Terminar com o artefato produzido e a pergunta que abre Monte Carlo. |

### Aula 04 — Monte Carlo e fronteira eficiente (24 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | A | Tema forte. Antecipar que sorteio e otimização respondem perguntas diferentes. |
| 2 | agenda | R | Reduzir de sequência operacional para explorar, otimizar e comparar. |
| 3 | resgate | A | Os 135 parâmetros tornam o problema concreto. Explicar contagem e relação com erro de estimação. |
| 4 | preparo | R | Preparação extensa e técnica. Oferecer notebook executado e pergunta mínima para quem teve falha de ambiente. |
| 5 | sorteada-contra-otima | C | Comparação numérica forte, mas omite o viés do gerador de pesos. Acrescentar distribuição de amostragem antes da conclusão. |
| 6 | section | A | Boa transição ao espaço de carteiras. Usar visual do simplex para três ativos. |
| 7 | forma-vetorial | R | Fórmula matricial pode virar ritual. Mapear cada termo a uma decisão e a uma dimensão verificável. |
| 8 | widget-triangulo | A | Excelente ponte geométrica. Contrastar pontos uniformes no simplex com pesos uniformes normalizados. |
| 9 | motor | C | `uniform + normalize` não é uniforme no simplex. Ensinar Dirichlet e explicitar por que o método atual evita cantos. |
| 10 | pratica-motor | C | Ler código linha a linha, medir, alterar e testar em poucos minutos é inviável. Dar esqueleto e dividir papéis/checkpoints. |
| 11 | video-nuvem | A | Animação ajuda. Incluir legenda de cor, taxa livre de risco e quantidade de pontos. |
| 12 | widget-nuvem | A | Bom para exploração. Permitir alternar esquema de amostragem, não apenas número de sorteios. |
| 13 | milhao | C | “Um milhão ainda não chega” é efeito conjunto de dimensão e amostragem enviesada. Reescrever conclusão e comparar Dirichlet. |
| 14 | section | A | Passagem à otimização é lógica. Explicitar que SLSQP também depende de objetivo, restrições e inicialização. |
| 15 | slsqp | R | Código correto em espírito, mas falta discutir ótimos locais, sucesso, tolerância e múltiplos inícios. |
| 16 | video-slsqp | A | Boa visualização. Mostrar restrições ativas ao chegar ao ótimo. |
| 17 | duas-otimas | R | Carteiras extremas são elucidativas, porém economicamente frágeis. Incluir concentração, turnover e sensibilidade. |
| 18 | video-fronteira | A | Forte síntese visual. Diferenciar fronteira possível, eficiente e pontos dominados. |
| 19 | pratica-fronteira | C | Duas otimizações, 50 pontos, gráfico e interpretação não cabem. Entregar funções prontas e focar no diagnóstico. |
| 20 | quiz-final | R | Questão sobre sorteio reforça explicação incompleta. Incluir distribuição dos pesos como parte da resposta correta. |
| 21 | notebook | R | Completo, mas denso. Exibir rota mínima e testes esperados. |
| 22 | a3-a4 | C | A4 ainda tem duplicidade de sprint não resolvida. Não publicar rubrica definitiva antes da coordenação. |
| 23 | referencias | A | Boa documentação técnica. Acrescentar referência sobre amostragem no simplex e limitações de Markowitz. |
| 24 | end | A | Encerramento adequado. Fechar com comparação honesta: exploração, otimização e validação são etapas complementares. |

### Aula 05 — Validação e robustez do modelo (27 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | A | Tema essencial e madura a narrativa. Explicitar que “ótimo” é condicional à amostra e às premissas. |
| 2 | agenda | R | Simplificar para promessa, teste, instabilidade e decisão. |
| 3 | resgate | A | Boa conexão com a fronteira. Pedir previsão sobre qual carteira degrada mais fora da amostra. |
| 4 | promessa | A | Excelente contraste esperado versus realizado. Manter unidades, período e regra de rebalanceamento visíveis. |
| 5 | preparo | R | Autoestudo excessivo. Separar obrigação, referência e extensão. |
| 6 | section | A | Transição clara. Introduzir vazamento de dados antes do desenho treino/teste. |
| 7 | treino-teste | A | Fundamento bem escolhido. Mostrar linha do tempo e proibir explicitamente uso do teste na calibração. |
| 8 | animacao-drawdown | A | Visual relevante. Definir drawdown e seu pico de referência antes da animação. |
| 9 | esperado-realizado | A | Comparação poderosa. Acrescentar retorno líquido e benchmark para evitar leitura isolada do Sharpe. |
| 10 | widget-janela | A | Interação adequada. Pedir que a dupla explique mudança de regime, não só mova a janela. |
| 11 | resumo-janelas | C | “25 de 33” pode sugerir independência. Marcar sobreposição e complementar com blocos não sobrepostos. |
| 12 | backtest-codigo | R | Código projetado deve enfatizar fronteira temporal, rebalanceamento e prevenção de look-ahead. |
| 13 | pratica-backtest | C | Rodar backtest, comparar duas carteiras e interpretar em 12 min é apertado. Pré-calcular e focar em auditoria do desenho. |
| 14 | section | A | Boa mudança para sensibilidade. Formular “qual entrada move a decisão?”. |
| 15 | widget-sensibilidade | A | Excelente conexão entre erro de entrada e peso. Incluir custo/turnover gerado pela perturbação. |
| 16 | sensibilidade | A | Números ajudam. Distinguir sensibilidade local, cenário e erro de estimação. |
| 17 | animacao-janela | A | Boa percepção de instabilidade. Adicionar benchmark de pesos constantes. |
| 18 | estabilidade | R | Troca de pesos é evidência importante, mas não basta para recomendar frequência. Incluir turnover e custo. |
| 19 | adr | C | Recomenda reotimização mensal sem resultado líquido. Reescrever como hipótese a testar, não decisão pronta. |
| 20 | pratica-estabilidade | C | Perturbar, trocar estimador, medir, interpretar e escrever ADR em 8 min é inviável. Dividir entre grupos e fazer plenária. |
| 21 | escolha-comite | R | Boa atividade decisória. Dar restrições do comitê: liquidez, limite por ativo, custo e horizonte. |
| 22 | quiz-final | A | Bom fechamento, desde que inclua sobreposição e custo de rebalanceamento. |
| 23 | notebook | R | Mostrar somente células usadas em sala e rotular extensões. |
| 24 | a4 | C | Rubrica deve cobrar robustez líquida, não apenas otimização e gráfico. Resolver duplicidade da entrega. |
| 25 | ponderada2 | R | Tornar explícita a diferença entre evidência técnica, decisão e comunicação executiva. |
| 26 | referencias | A | Base adequada. Incluir referência de backtest overfitting e custos de transação. |
| 27 | end | A | Fechamento forte. Terminar com “o que faria você rejeitar o modelo?”. |

### Aula 06 — Do script ao produto: API, React e LLM (25 slides)

| # | ID | Parecer | Crítica e orientação |
|---:|---|:---:|---|
| 1 | capa | R | Promessa ampla demais. Eleger API testável como objetivo principal e tratar React/LLM como camadas consumidoras. |
| 2 | agenda | C | Escopo incompatível com 105 min. Cortar uma camada ou dividir em duas aulas. |
| 3 | resgate | A | Boa ponte do módulo para produto. Explicitar quais funções já são estáveis e reutilizadas. |
| 4 | preparo | R | Setup de múltiplas tecnologias aumenta falha operacional. Fornecer ambiente verificado e respostas de contingência. |
| 5 | section | A | Boa transição a contrato. Começar pelo consumidor e pelo JSON esperado. |
| 6 | requisicao | A | Exemplo concreto. Marcar campos obrigatórios, opcionais, tipos e invariantes. |
| 7 | contrato | R | Tabela clara, mas a semântica 404/422 é apresentada como definitiva. Explicar que é decisão documentada. |
| 8 | montador | A | Widget útil. Incluir payload inválido e mostrar exatamente qual camada rejeita. |
| 9 | section | A | Transição correta. Definir objetivo observável: uma rota, três casos e contrato OpenAPI. |
| 10 | fastapi | R | Código ao vivo pode consumir o bloco. Entregar base pronta e implementar apenas validação/handler central. |
| 11 | cache | R | Bom exemplo de desempenho, mas falta chave canônica, invalidação e limite de validade. Mostrar que ordem dos tickers afeta cache. |
| 12 | erros | C | 404 versus 422 não tem resposta universal. Fazer debate de contrato e padronizar corpo de erro. |
| 13 | pratica-testclient | C | Construir e testar API em 12 min é irreal para primeiro contato. Dar testes e pedir implementação de um caso. |
| 14 | section | A | Mudança para frontend é clara, mas deveria ser extensão, não novo objetivo obrigatório. |
| 15 | react | R | Arquitetura útil, porém superficial. Mostrar fluxo de estado, loading, erro e sucesso em diagrama. |
| 16 | escolha-camada | A | Excelente pergunta de responsabilidade. Incluir segurança e custo como critérios, além de UX. |
| 17 | section | R | Nova mudança de objetivo aos 75 min. Se LLM permanecer, tratá-la como consumidor opcional da API. |
| 18 | prompt | R | Bom uso de dados reais. Exigir unidade, período, proibição de previsão e formato estruturado de saída. |
| 19 | verificador | C | Nome e mensagem superestimam o algoritmo. Renomear e validar tuplas semânticas, não presença de números. |
| 20 | ativo-trocado | A | Excelente contraexemplo dos limites atuais. Ele deveria anteceder qualquer afirmação de “verificação”. |
| 21 | quiz-final | R | Ajustar questão HTTP e avaliar separação entre validação determinística e interpretação generativa. |
| 22 | notebook | R | A trilha completa é longa. Destacar missão mínima: contrato, rota e três testes. |
| 23 | a5 | C | O case antigo ainda cita Streamlit/OpenRouter em configuração divergente. Atualizar antes da Sprint 5. |
| 24 | referencias | A | Boa base técnica. Acrescentar documentação de segurança, contratos de erro e limites de validação de LLM. |
| 25 | end | A | Fechamento adequado. Terminar com a arquitetura final e o conjunto de evidências de qualidade. |

## 5. Auditoria das atividades

| Aula / atividade | Diagnóstico | Orientação operacional |
|---|---|---|
| 01 — coletor | Viável apenas com ambiente e fallback previamente prontos. | Célula inicial executada; objetivo obrigatório: produzir um arquivo e registrar origem/horário. |
| 01 — ausências e ADR | Sobrecarregada para 12 min. | Um tratamento por dupla; comparação em plenária; ADR como saída pós-aula. |
| 02 — retornos | Muitos cálculos e decisões simultâneas. | Um ativo por grupo; juntar resultados num quadro coletivo. |
| 02 — cesta | Tabela de 15 ativos e julgamento não cabem. | Dividir cesta, fornecer agregador e reservar 5 min ao debrief. |
| 03 — matriz | Montagem, heatmap, troca de par e interpretação excedem o tempo. | Matriz pronta; cada dupla audita uma propriedade e um par. |
| 03 — bancos | Boa decisão aplicada, mas precisa de pesos e risco explícitos. | Comparar duas carteiras com o mesmo orçamento de risco. |
| 04 — motor | Leitura linha a linha e benchmarking competem. | Função incompleta com três lacunas; teste de forma e soma dos pesos já fornecido. |
| 04 — fronteira | Duas otimizações e 50 pontos são trabalho de laboratório. | Fornecer solucionadores; aluno interpreta restrições ativas e pontos dominados. |
| 05 — backtest | Execução técnica toma o tempo da crítica metodológica. | Entregar resultados e pedir caça a look-ahead, sobreposição e benchmark inadequado. |
| 05 — estabilidade/ADR | Quatro tarefas em oito minutos. | Distribuir cenários entre grupos; produzir uma recomendação condicionada, não ADR completo. |
| 06 — TestClient | Primeira API completa em 12 min é improvável. | Fornecer testes; cada dupla implementa um caminho: 200, 422 ou erro de domínio. |
| 06 — LLM | Mistura prompt, chamada externa, falha de provedor e validação. | Rodar offline com resposta gravada; extensão opcional usa provedor real. |

Padrão recomendado para todas as práticas:

- **Antes:** previsão individual de 30–60 segundos.
- **Durante:** missão obrigatória curta, checkpoint intermediário e extensão.
- **Depois:** debrief com resposta, erro comum e conexão com o artefato.
- **Contingência:** saída pré-computada e screenshot para falha de rede/ambiente.

## 6. Auditoria dos exemplos e da profundidade

### Exemplos que devem ser preservados

- MGLU3/B3SA3 para mostrar como eventos corporativos quebram leitura ingênua de preço.
- GOLD11 reduzindo a janela comum e alterando a volatilidade observada.
- Correlação ITUB4/BBDC4 em regime de crise versus janela completa.
- Nuvem de carteiras versus solução de otimização.
- Prometido em treino versus entregue em teste.
- Número correto associado ao ativo errado na interpretação por LLM.

Esses exemplos funcionam porque têm número, contraste e consequência decisória. O padrão deve ser replicado.

### Exemplos que precisam ser corrigidos

1. **Monte Carlo:** separar insuficiência de amostras de viés da distribuição de pesos.
2. **Correlação:** não converter limiar em recomendação sem pesos, volatilidades e janela.
3. **Raiz do tempo:** declarar hipóteses; não apresentar anualização como identidade universal.
4. **Janelas móveis:** declarar dependência entre testes sobrepostos.
5. **Reotimização mensal:** incluir custos e turnover antes de recomendar.
6. **HTTP 404/422:** apresentar convenção de contrato, não verdade absoluta.
7. **Verificador da LLM:** distinguir presença numérica, correspondência semântica e correção factual.

### Profundidade faltante para uma turma forte

- Incerteza de estimação em retorno esperado e por que ela domina Markowitz.
- Condicionamento/semidefinição positiva da matriz de covariância.
- Restrições realistas: teto por ativo, liquidez, lote, turnover e custo.
- Comparação com baselines: pesos iguais, BOVA11, CDI e carteira estática.
- Risco de backtest overfitting e múltiplas tentativas.
- Intervalos de confiança ou análise de sensibilidade, não apenas ponto estimado.
- Contratos de API versionados, observabilidade e modelo de ameaça mínimo.
- Limites e avaliação de qualidade de uma camada generativa.

## 7. Materiais de apoio, notebooks e referências

Cada material de apoio tem aproximadamente 2,2 a 2,7 mil palavras e cinco respostas expansíveis. A estrutura é consistente e útil para estudo autônomo, mas o volume somado ao notebook, vídeos e atividades produz sobrecarga.

**Pontos fortes**

- Notebooks equilibram explicação e código, com 17 a 24 células.
- Dados locais evitam depender integralmente da rede.
- As aulas reutilizam a mesma base e constroem progressão real.
- Há posters para vídeos e referências por aula.
- ADRs conectam escolha técnica, evidência e consequência.

**Correções recomendadas**

- Abrir cada material com “em 45 minutos você precisa conseguir…”.
- Identificar trechos como essencial, recomendado ou aprofundamento.
- Colocar estimativa medida por seção, não apenas global.
- Incluir gabarito de raciocínio, não só resultado numérico.
- Em notebooks, adicionar testes rápidos imediatamente após funções críticas.
- Congelar versões de dependências e registrar versão da base dentro da saída.
- Garantir acessibilidade: alternativa textual de gráficos, foco por teclado, contraste e rótulo dos widgets.
- Separar “fonte primária”, “documentação” e “leitura adicional” nas referências.

## 8. Auditoria visual e de marca

### Parecer: reprovado

O projeto é visualmente coerente consigo mesmo, mas não com a norma vigente. A origem é sistêmica: o CSS comum implementa linguagem de produto digital arredondada, enquanto o brand kit atual pede geometria ortogonal e composição editorial.

| Norma | Situação | Evidência / correção |
|---|---|---|
| GRA-01 | Reprovada | Cartões, quizzes, perfil, botões e materiais usam cantos arredondados; há círculos com número e controle. Remover raios e redesenhar componentes. |
| GRA-07 | Reprovada | O sistema recorrente é de cards/pílulas, não grafismo institucional. Usar filetes, retângulos, respiro e hierarquia tipográfica. |
| ICO-01 / ICO-05 | Reprovada | `Material Symbols Outlined` via CDN. Migrar para Sharp em SVG versionado. |
| TIP-04 | Reprovada | Título 500, corpo 400; norma vigente pede 700/600/300 por função. Atualizar tokens. |
| COR-04 | Revisar | Coral aparece em erro/alerta e filetes. Reservar coral ao papel previsto para Graduação e documentar cores funcionais. |
| LOG-01 a LOG-04 | Aprovada em amostra | Logos positivo/negativo parecem usados no fundo adequado e sem deformação. Revalidar todas as exportações PDF. |
| FOT-01 a FOT-04 | Não aplicável | O acervo praticamente não usa fotografia. Se for adicionada, seguir o tratamento do kit. |
| Acessibilidade | Revisar | Texto complementar e código ficam pequenos; estados não devem depender apenas de cor. |

### Direção visual recomendada

- Capa: manter grafismo e alto contraste, com menos elementos concorrentes.
- Conteúdo: fundo branco predominante, uma afirmação forte, uma evidência visual e uma conclusão.
- Fórmula: destacar variável que muda e resultado que responde à pergunta.
- Código: no máximo 8–12 linhas projetadas; restante no notebook.
- Tabela: mostrar apenas linhas/colunas necessárias à decisão; usar gráfico quando a pergunta for comparação.
- Atividade: instrução curta, tempo, entrega e critério de sucesso; sem card arredondado.
- Agenda: três atos, não cronograma administrativo completo.

## 9. Plano de correção priorizado

### P0 — bloqueadores antes de publicar

1. Confirmar LBL, parceiro, briefing e cesta.
2. Resolver o desalinhamento A2 versus Aula 03.
3. Resolver duplicidade/peso/prazo do A4 e atualizar a fonte única de calendário.
4. Corrigir o ensino de amostragem no simplex na Aula 04.
5. Renomear e limitar a checagem de números da Aula 06.
6. Replanejar atividades críticas para caber no tempo.
7. Migrar componentes globais para GRA-01, ICO-01/05 e TIP-04.
8. Atualizar o case Streamlit/OpenRouter para a arquitetura realmente ensinada.

### P1 — qualidade pedagógica

1. Reduzir agendas e índices projetados.
2. Quebrar slides com código + tabela + conclusão.
3. Introduzir custos, turnover, restrições e baselines.
4. Explicitar hipóteses de anualização, sobreposição de janelas e instabilidade.
5. Recalibrar autoestudo em trilhas mínima/recomendada/aprofundamento.
6. Adicionar debrief e critérios observáveis a todas as práticas.

### P2 — acabamento e sustentação

1. Atualizar `check_brand.py` para as regras vigentes.
2. Rodar inspeção visual em ambiente que permita servidor local e exportar PDF.
3. Executar teste de projeção em sala real, inclusive fundo da sala.
4. Fazer ensaio cronometrado com um aluno ou monitor.
5. Incluir checklist de publicação por aula.

## 10. Portão de qualidade para liberação

Uma aula só deve ser marcada como pronta quando:

- problema, exemplo e atividade respondem ao mesmo objetivo de aprendizagem;
- todo critério avaliado já foi ensinado e praticado;
- números, período, unidade, fonte e premissas estão visíveis;
- a atividade obrigatória cabe em 70% do tempo reservado em ensaio;
- há contingência offline;
- nenhuma conclusão é mais forte do que a evidência;
- o slide passa na norma visual vigente e em projeção real;
- links, widgets, notebook e PDF foram testados;
- datas, pesos e parceiros estão confirmados em fonte institucional.

## 11. Conclusão

O acervo não sofre de falta de trabalho; sofre de **excesso de ambição por tela e por minuto**, somado a pendências de governança que deveriam ter sido resolvidas antes de virar conteúdo publicado. A recomendação não é simplificar intelectualmente. É fazer o oposto: retirar administração e decoração da projeção para abrir espaço àquilo que uma turma forte cobrará — hipótese, limite, contraprova, comparação justa e consequência decisória.

Com os bloqueadores corrigidos, o material tem potencial para ficar excelente. Sem eles, os alunos mais atentos encontrarão rapidamente inconsistências de calendário, marca, método estatístico e promessa tecnológica, e essas falhas poderão reduzir a confiança justamente nos pontos em que o curso tenta ensinar rigor.
