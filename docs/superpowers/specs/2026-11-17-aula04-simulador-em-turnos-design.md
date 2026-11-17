# Aula 04 em turnos: do portal de simulação ao motor escrito pelos grupos

- **Data:** 17/11/2026
- **Status:** em revisão, aguardando aprovação do professor
- **Encontro:** Aula 04, 18/11/2026 (quarta), turma 2026-2B-T19, horário de relógio pendente (P1)
- **Substitui:** o formato da Aula 04 de 13/10/2026 ("Da Nuvem à Fronteira"), que passa a ser a versão v1

## 1. Intenção

A Aula 04 atual entrega o motor de Monte Carlo pronto no notebook, e as duas práticas em dupla
consistem em rodar células. O professor relatou na reunião docente de 16/11/2026 que os artefatos
dos grupos chegam com nota 9 a 10 e que, numa atividade de programação em sala, a turma ficou
muito abaixo disso. O diagnóstico dele é que os alunos de Administração não escrevem código sem
IA. Os próprios alunos pediram mais programação.

A aula nova faz os grupos construírem o motor do A3 durante a instrução, em fatias pequenas e
verificáveis, sem anunciar que aquilo é o artefato. A parte que o aluno escreve à mão é a
especificação e o teste; a implementação é escrita à mão nas duas primeiras fatias e por um agente
de codificação nas seguintes. O encontro treina o modo de trabalho da próxima sprint, em que os
grupos escrevem código e frontend.

Em 18/11 a aula recebe de 8 a 12 visitantes de uma faculdade de Rondônia (Administração, Ciências
Contábeis e Direito), que vêm observar a dinâmica do PBL. A orientação da coordenação é manter o
conteúdo previsto e mostrar a dinâmica.

## 2. Objetivos, fora de escopo e o que tornaria a aula um fracasso

**Objetivos**

1. Cada grupo sai do encontro com um módulo `simulador.py` próprio, com testes, que sorteia N
   carteiras e devolve retorno, risco e Índice de Sharpe de cada uma.
2. Cada aluno escreve à mão, sem IA, pelo menos um teste e o corpo de duas funções.
3. Cada grupo usa um agente de codificação a partir de uma spec e de um teste escritos pelo
   grupo, e confere o resultado pelo teste.
4. A aula parte da carteira que o grupo montou na aula de Negócios (5 ativos, R$ 100 mil, pesos
   iguais e pesos do Solver, preço de referência de 13/11/2026) e olha para os pregões anteriores
   a essa data.
5. Os visitantes veem alunos produzindo durante a maior parte do encontro.

**Fora de escopo**

- Otimização com SLSQP, carteira de variância mínima, de máximo Sharpe e fronteira eficiente.
  Saem do encontro (ver seção 9).
- Login com senha. A entrada é por nome e avatar, como no quiz ao vivo.
- Foto de aluno. O avatar usa iniciais e a cor do grupo.
- Frontend escrito pelos alunos. O portal é do professor.
- Nota. A aula não é ponderada.
- Comparação entre uniforme normalizado e Dirichlet (slides 12 a 14 da v1). Fica no material v1.

**O que tornaria a aula um fracasso mesmo funcionando**

- Aluno assistindo sem digitar por mais de um bloco.
- Falha de rede, do Supabase ou do provedor de cotações interrompendo a aula.
- Número do portal diferente do número que a função correta do aluno devolve.
- Nome ou dado de aluno gravado no repositório, que é publicado inteiro.
- Tom de espetáculo no material. Valem as convenções editoriais do `CLAUDE.md`, seção 9.

## 3. Restrições

- A aula é no dia seguinte à escrita deste documento. O que não ficar pronto e testado até a
  manhã de 18/11 é cortado na ordem da seção 10.
- Site estático, sem build. HTML, CSS, JavaScript puro, Python em `tools/`, notebooks.
- O CI roda os quatro validadores, a suíte pytest e os notebooks com `M08_OFFLINE=1`. O push em
  `main` publica no Pages.
- O encontro tem 15 minutos de daily e 105 minutos em sete blocos de 15, cada um fechado por uma
  interação nomeada (`tools/tests/test_planejamento.py`).
- `dados/` termina em 31/08/2026 e tem 15 ativos. A carteira dos grupos usa preço de 13/11/2026 e
  ativos escolhidos por eles.
- O Supabase do quiz ao vivo já está em produção. A chave do professor fica fora do git, e SQL
  novo é executado pelo professor.
- Os alunos têm Claude Code e Codex configurados (informação do professor, não verificada
  máquina a máquina).
- São quatro grupos (G01 a G04), como na Aula 02.

## 4. Abordagens consideradas

**Para a aula**

| Abordagem | Descrição | Avaliação |
|---|---|---|
| A. Notebook em níveis com placar | O grupo escreve o simulador em fatias no Colab, com `conferir` por fatia | Coloca o aluno para programar. Tem pouco impacto de abertura |
| B. Simulador jogável no navegador | O aluno monta carteira e simulação num portal, sem escrever código | Chama atenção. Sozinho, mantém o aluno sem programar |
| C. Programação ao vivo guiada | O professor escreve e a turma acompanha | Menor risco e menor atividade do aluno |

**Decisão do professor:** B como gancho de abertura, seguido de A. O portal é o produto pronto; os
turnos reconstroem o motor dele, e o número do portal é o valor esperado dos testes.

**Para a divisão entre mão e agente**

| Abordagem | Avaliação |
|---|---|
| Agente desde o turno 1 | Mais ritmo, sem evidência de que o aluno entende a conta |
| Turnos 1 e 2 à mão, agente a partir do 3 | Garante a conta entendida antes de delegar |

**Decisão do professor:** turnos 1 e 2 sem IA, com scaffold; agente a partir do turno 3.

**Para o ambiente dos turnos 3 a 5**

| Abordagem | Avaliação |
|---|---|
| Kit de repositório com agente no terminal | O agente lê a spec, roda o `pytest` e itera. O resultado sai como módulo `.py` com `SPEC.md`, formato cobrado no barema do A3. Custa uma troca de ambiente no meio da aula |
| Tudo no Colab | Menos atrito. O agente não executa os testes e o resultado continua sendo notebook |

**Decisão do professor:** kit de repositório com agente no terminal, porque na próxima sprint os
grupos escrevem código e frontend. O Colab fica como reserva para grupo com ambiente quebrado.

## 5. Desenho do encontro

### 5.1 Blocos

| Bloco | Minutos | Conteúdo | Interação que fecha o bloco |
|---|---|---|---|
| Daily | 15 | Requisito do A3 e estado dos grupos | padrão do módulo |
| 1 | 0 a 15 | Portal: cada aluno entra, escolhe ativos, período e número de simulações | painel de avatares no projetor, com a simulação de dois alunos aberta |
| 2 | 15 a 30 | Verificação do preparo e leitura da spec do simulador e das duas ADRs prontas | quiz ao vivo por QR code |
| 3 | 30 a 45 | Turnos 1 e 2, à mão, no Colab, em dupla | `conferir` dos dois turnos e marcação no placar |
| 4 | 45 a 60 | Turno 3, primeiro turno com agente, com spec pronta | `pytest` verde e marcação no placar |
| 5 | 60 a 75 | Turno 4, spec escrita pelo grupo na tela de spec | `pytest` verde, gráfico e marcação no placar |
| 6 | 75 a 90 | Turno 5, desempenho e posição da carteira do grupo na nuvem | `pytest` verde e marcação no placar |
| 7 | 90 a 105 | Nuvens dos quatro grupos no projetor, leitura da carteira de pesos iguais e da do Solver dentro da nuvem, amarração com o A3 | quiz ao vivo de três perguntas |

Pair programming é o formato dos blocos 3 a 6: piloto e copiloto trocam a cada turno.

### 5.2 Anatomia de um turno

1. Ler a spec do turno: função, entrada, saída, casos de borda, critério de aceite.
2. Escrever o teste à mão. Nos turnos 1 e 2 o valor esperado é o número que o portal mostrou
   para a carteira do aluno.
3. Rodar e ver o teste falhar.
4. Implementar: a dupla nos turnos 1 e 2, o agente nos turnos 3 a 5.
5. Rodar, ver passar e marcar o turno no placar.

### 5.3 Os cinco turnos

| Turno | Função | Entrada | Saída | Onde | Quem implementa |
|---|---|---|---|---|---|
| 1 | `retorno_do_dia` | pesos e retornos dos ativos em um pregão | retorno da carteira no pregão | Colab | dupla, à mão |
| 2 | `metricas` | pesos e tabela de retornos de N pregões | retorno anual e risco anual | Colab | dupla, à mão |
| 3 | `sortear_pesos` | número de ativos e gerador com semente | vetor de pesos não negativos que soma 1 | kit | agente |
| 4 | `simular` | tabela de retornos, número de simulações, semente, taxa livre de risco | tabela com pesos, retorno, risco e Sharpe de cada carteira, e gráfico de risco e retorno | kit | agente |
| 5 | `simular` com requisito de tempo e `posicionar` | o mesmo, com 2 a 20 ativos, e uma carteira dada | 10.000 simulações em menos de 10 s; a carteira dada marcada sobre a nuvem | kit | agente |

Scaffold dos turnos 1 e 2: a célula traz assinatura, docstring e a célula de teste com o valor
esperado em branco. O aluno escreve o valor esperado e até três linhas de corpo.

A última célula do notebook grava as duas funções em `simulador.py`, que o grupo leva para o kit.
O kit já traz um `simulador.py` com as duas funções resolvidas comentadas como reserva, para o
grupo que não fechar o bloco 3 não ficar parado.

A spec do turno 3 vem preenchida como modelo. As dos turnos 4 e 5 o grupo completa na tela de
spec e copia para o `SPEC.md` do kit.

### 5.4 Definições numéricas, iguais no portal e no Python

- Retorno diário simples do preço ajustado.
- Análise conjunta em janela comum dos ativos escolhidos, com a regra de ausência da ADR-009.
- Retorno da carteira no pregão: soma dos pesos vezes os retornos do pregão.
- Retorno anual: média dos retornos diários da carteira vezes 252.
- Risco anual: desvio padrão amostral (`ddof=1`) dos retornos diários da carteira vezes raiz
  de 252.
- Sharpe: retorno anual menos taxa livre de risco, dividido pelo risco anual. A taxa é parâmetro
  da função, e o valor da aula vem do arquivo de dados da aula.
- Sorteio dos pesos: uniforme normalizado, como no capítulo 9 do Caetano e na v1. A segunda ADR
  pronta registra essa escolha e a consequência medida na auditoria C-09.

O gerador aleatório do navegador e o do NumPy produzem sequências diferentes. Por isso o portal
serve de valor esperado apenas para os turnos 1 e 2, que são determinísticos. Os testes dos
turnos 3 a 5 verificam propriedades: soma 1, não negatividade, formato, reprodutibilidade com a
mesma semente, tempo e limites de retorno e risco.

## 6. Peças a construir

### 6.1 Dados da aula

- Script novo em `tools/` que baixa preço ajustado dos papéis do Ibovespa e dos ETFs do acervo,
  de janeiro de 2024 a 13/11/2026, e grava um JSON para o portal e um CSV para o kit e o
  notebook. A data de corte é 13/11/2026, a referência da atividade de Negócios.
- Esses arquivos ficam separados de `dados/`. O snapshot do case não muda.
- A taxa livre de risco da janela entra no mesmo arquivo. Se a série do CDI não vier, o valor é
  registrado como pendência e o Sharpe do turno 4 usa parâmetro informado em sala.
- Teste trava formato, janela, ausência de valor nulo dentro da janela comum e a lista de
  tickers.

### 6.2 Portal de simulação

Página estática nova, com link no deck e QR code.

1. Entrada: nome, grupo e avatar de iniciais, pela função `quiz_entrar` já existente.
2. Montagem: de 2 a 5 ativos e período em pregões anteriores a 13/11/2026 (9, 21, 63, 126, 252).
   Mostra retorno e risco da carteira de pesos iguais e a evolução de R$ 100 mil.
3. Simulação: 10, 100, 1.000 ou 10.000 carteiras sorteadas, nuvem de risco e retorno, campo para
   informar pesos próprios (os do Solver) e marcar essa carteira na nuvem.
4. Painel: grade de avatares de quem entrou na sessão. Clicar num avatar abre a simulação
   daquela pessoa.

O banco guarda apenas os parâmetros de cada simulação (ativos, período, quantidade, semente e
pesos próprios). A nuvem é recalculada no navegador de quem abre, com gerador com semente, e por
isso sai idêntica. A simulação roda sem servidor. Com `?demo=1`, ou se o banco não responder, o
painel funciona em memória.

Os nove pregões servem aos turnos 1 e 2, porque cabem numa tabela conferível à mão. A nuvem usa
252 pregões por padrão, porque risco medido em nove pregões é instável; o portal avisa isso ao
lado do seletor.

### 6.3 Tela de spec

Reaproveita os três componentes da ADR online da Aula 02 (`inteli-adr.js`): formulário do grupo
com link por token, painel de links e prazo do professor, visão do projetor. Campos: função,
entrada, saída, casos de borda, critério de aceite. Botão novo "Copiar como SPEC.md".

### 6.4 Placar dos turnos

Quatro grupos por cinco turnos, no deck do professor. O grupo marca o próprio turno na tela de
spec, com o token do grupo, depois de ver o teste passar. É declaração do grupo, conferida pelo
professor na circulação.

### 6.5 Notebook dos turnos 1 e 2

Substitui `notebooks/aula04.ipynb`. Segue o contrato de notebook do `CLAUDE.md`: badge do Colab,
carga com queda para URL bruta, `M08_OFFLINE=1`, sem saída gravada. Usa o padrão `conferir` da
Aula 03. Executa no CI com as células de resposta vazias sem quebrar.

### 6.6 Kit do simulador

Pasta em `exemplos/` e um `.zip` gerado a partir dela, baixável pelo portal. O grupo descompacta
dentro do repositório do grupo.

Conteúdo: `SPEC.md`, `simulador.py`, `tests/` com um teste de exemplo e um teste em branco por
turno, `conferir.py` com os testes de aceite do professor, duas ADRs prontas (janela dos dados e
sorteio dos pesos), `dados/` com o CSV da aula, `requirements.txt`, um verificador de ambiente e
um arquivo de instruções para o agente (ler a spec, não alterar os testes, rodar `pytest`,
parar quando passar), nos nomes que Claude Code e Codex leem.

O kit não baixa nada em aula.

### 6.7 Deck, material, referências e notas do professor

- Deck novo em `aulas/aula04.html`, curto, no padrão das Aulas 02 e 03: daily, QR code do portal,
  quiz ao vivo, código linha a linha com `inteli-codigo.js`, um slide por turno, placar,
  fechamento.
- A versão atual passa a `aulas/aula04-v1.html` e `notebooks/aula04-v1.ipynb`, como foi feito com
  a Aula 03, com os testes dela apontando para os arquivos v1.
- Material de apoio, referências e notas do professor atualizados para o formato novo. O material
  aponta o conteúdo de otimização da v1 como leitura posterior.

### 6.8 Planejamento e decisões

- `PLANEJAMENTO_AULA_A_AULA.md`: blocos da Aula 04 reescritos conforme a seção 5.1.
- ADR nova, a 018, registrando a troca de formato e a saída da otimização do encontro.
- `docs/ANDAMENTO.md` atualizado.

## 7. Verificação

- Suíte pytest para o script de dados, o kit (a solução de referência passa em todos os testes
  de aceite; o kit vazio falha em todos), o notebook e o deck.
- Paridade numérica: para um conjunto de carteiras, o portal aberto no Playwright e o Python
  devolvem retorno e risco iguais dentro de tolerância de arredondamento.
- Requisito de tempo medido com 2, 5 e 20 ativos.
- `check_brand.py`, `check_slides.py`, `check_links.py` e `check_widgets.py` nos arquivos novos.
- Portal exercitado no Playwright em modo de memória: entrar, montar, simular, abrir a simulação
  de outro participante.

## 8. O que depende do professor

1. Executar no Supabase o SQL novo, se a tabela de simulações e o placar exigirem.
2. Autorizar commit e push, que publicam no Pages.
3. Avisar os grupos, antes da aula, para trazerem uma máquina com agente funcionando e rodarem o
   verificador de ambiente do kit.
4. Ensaiar o bloco 1 com o projetor.

## 9. Consequências e pendências abertas

- A otimização com SLSQP e a fronteira saem do encontro. O A4 e a Aula 05 dependem delas: a
  Aula 05 reutiliza a função `otimizar`. Pendência nova a registrar: decidir se a otimização vira
  autoestudo com o material v1, abertura da Aula 05 ou encontro extra. Esta entrega não resolve.
- A pendência P2 (A4 listado nas Sprints 3 e 4) continua aberta. O slide de amarração cita só o
  A3.
- A solução de referência do motor fica no repositório público, como já ficava na v1.
- O acervo ganha um segundo conjunto de cotações, fora de `dados/`.

## 10. Ordem de corte se o prazo apertar

1. Painel de avatares (o portal individual permanece).
2. Placar automático (vira marcação à mão no quadro).
3. Turno 5 (vira tarefa da sprint).
4. Tela de spec online (a spec vai em arquivo no kit).

Núcleo que não se corta: portal individual, notebook dos turnos 1 e 2, kit com os turnos 3 e 4,
deck e testes.

## 11. Decisões tomadas por quem escreveu este documento

Não foram pedidas pelo professor e podem ser revistas:

- Avatar de iniciais, sem foto.
- Entrada sem senha, pelo mesmo mecanismo do quiz.
- Universo de ativos igual ao Ibovespa mais os ETFs do acervo, com corte em 13/11/2026.
- Nove pregões para os turnos à mão e 252 para a nuvem.
- Banco guarda parâmetros, e a nuvem é recalculada no navegador.
- Kit distribuído como `.zip` para dentro do repositório do grupo, em vez de repositório modelo
  separado.
- Placar por declaração do grupo.
- Versão atual preservada como v1.

## 12. O que fica para quem implementa

Nomes de arquivos e de sessão, esquema exato das tabelas, layout das telas dentro do tema,
biblioteca de gráfico do portal (canvas próprio, como os widgets), lista final de tickers,
redação dos slides e das ADRs prontas, e o conteúdo das perguntas dos dois quizzes.

## 13. Ajustes após a revisão independente

Respondidos pelo próprio repositório:

- **Interações do planejamento.** `test_planejamento.py` aceita apenas sete interações nomeadas
  (Peer Instruction, prever e observar, pensar e compartilhar, dupla no notebook, escolha
  coletiva, quiz, pergunta disparada) e trava o título "Da Nuvem à Fronteira: Monte Carlo e
  Otimização de Markowitz". Os blocos da seção 5.1 são redigidos no planejamento com essas
  interações: bloco 1 em prever e observar, bloco 2 em quiz, blocos 3 a 6 em dupla no notebook
  (o kit conta como a prática em dupla), bloco 7 em quiz. O título do encontro é mantido.
- **Versão v1.** Deck, notebook, material, referências e notas do professor atuais viram `-v1`, e
  `test_aula04.py` passa a apontar para eles, como na ADR-017. `tools/medidas_aula04.py` e
  `assets/data/aula04-nuvem.json` continuam existindo, porque `test_widget_carteira.py` depende
  deles.
- **`conferir` dos turnos 1 e 2.** O valor esperado é digitado pelo aluno a partir do portal. O
  notebook calcula a referência com os ativos e o período informados pelo aluno e compara as
  duas coisas: o valor digitado e o retorno da função.
- **Convenções.** ADR-018 é o próximo número. A sessão segue o padrão `m08-aula04-2026-11-18`. A
  chave do professor é a mesma do quiz.
- **Barema do A3.** Está em `../Inteli - Adm Tech - M08 - LBL/REVISAO-LBL08-COMPUTACAO.md`,
  linhas 328 a 368: corretude 30%, desempenho 10% (2 a 20 ativos, 10.000 simulações em menos de
  10 s), gráfico 10%, leitura analítica 15%, especificação 15%, ADRs 20%. As assinaturas e os
  campos do `SPEC.md` seguem esse barema.

Decididos por quem escreveu, a rever pelo professor:

- **Identidade no painel.** A tabela nova guarda iniciais e grupo, sem o nome, porque a chave
  pública permite leitura por qualquer pessoa que conheça a sessão.
- **Visitantes.** O portal tem a opção "Visitante", fora do placar e do relatório de
  participação.
- **ADRs prontas.** São do professor e documentam decisões do kit (janela dos dados e sorteio dos
  pesos), marcadas como exemplo. A ADR individual do A3, que vale 20%, precisa tratar de decisão
  do próprio aluno, e o slide de amarração diz isso.
- **Reserva dos turnos 3 a 5.** Não há segundo notebook. A dupla sem agente funcionando se junta
  a outra dupla do mesmo grupo. A instrução fica nas notas do professor.

## 14. Respostas do professor em 17/11/2026 e o que foi verificado

- **Ativos dos grupos.** O professor não tem a lista. O universo do portal é ampliado para o
  IBrX-100, os ETFs do acervo e os FIIs e BDRs mais negociados, para reduzir a chance de um ativo
  de grupo ficar de fora. O portal mostra uma mensagem clara quando o ticker procurado não
  existe no arquivo, e o grupo substitui o ativo por outro do mesmo setor. O risco permanece e
  fica nas notas do professor.
- **Supabase.** O professor autorizou o uso. O CLI do Supabase está instalado e autenticado nesta
  máquina, com o projeto `m08-quiz` (o mesmo do quiz ao vivo) vinculado em `AD08-LBL/supabase`. O
  SQL novo é aplicado por ele e fica versionado em `exemplos/`, como os anteriores. Só entram
  tabelas e funções novas; nada do que existe é alterado ou removido. Com isso o painel de
  avatares e o placar automático permanecem no escopo.
- **Tamanho da turma.** A lista local da T19 tem 23 alunos em quatro grupos (6, 6, 6 e 5).
- **Unidade de trabalho.** Turnos 1 e 2 em notebook individual, com o colega ao lado como
  revisor. Turnos 3 a 5 em dupla, um kit por dupla, o que dá de duas a três duplas por grupo. O
  placar mostra duplas concluídas por grupo e por turno.
- **Agentes.** O professor informa que os alunos já têm Claude Code e Codex configurados. Não há
  contagem verificada. O verificador de ambiente do kit roda no início do bloco 4, e a dupla sem
  agente se junta a outra do mesmo grupo.
- **Horário.** Segue pendente (P1). A Aula 03 foi das 14h às 16h segundo a ADR-017, e o prazo de
  construção assume o mesmo horário.

## 15. Acréscimos durante a implementação (17/11/2026)

- **Padrão visual do portal.** O professor pediu que o frontend do simulador seja bonito, útil e
  chame a atenção, e que sirva de referência para as entregas dos grupos, que escrevem frontend
  na próxima sprint. O portal é tratado como produto de referência: hierarquia clara, gráficos
  legíveis, estados de vazio, carregamento e erro resolvidos, responsivo do celular ao projetor,
  dentro da identidade Inteli do acervo.
- **Aplicação do SQL.** Aplicado em 17/11/2026 no projeto `m08-quiz` pelo CLI do Supabase, depois
  de trocar de rede (a rede em uso bloqueava as portas do Postgres). Conferido pela API pública
  com uma sessão de teste, removida em seguida: as três tabelas `sim_*` existem, entrar, salvar e
  marcar funcionam, grupo inválido e pesos que não somam 1 são recusados, escrita direta em
  tabela devolve 401, e as 64 linhas de `quiz_participantes` continuam lá.
- **Cotações.** O arquivo final tem 162 ativos e 718 pregões, de 02/01/2024 a 13/11/2026.
  Dezoito tickers do universo pedido ficaram de fora por falta de dado no provedor, em geral por
  troca de código de negociação.
