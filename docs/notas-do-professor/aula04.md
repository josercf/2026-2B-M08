# Notas do professor: Aula 04

Da Nuvem à Fronteira: Monte Carlo e Otimização de Markowitz, no formato em turnos. 18/11/2026
(quarta), Semana 6, Sprint 3, aula 28 do módulo. Horário de relógio pendente (P1): este roteiro usa
minutos contados a partir do fim da daily. Redesenhada em 17/11/2026 (ADR-018). A versão de
13/10/2026, com o motor pronto, o SLSQP e a fronteira, está em `aulas/aula04-v1.html`,
`materiais/aula04-v1.html`, `notebooks/aula04-v1.ipynb` e `docs/notas-do-professor/aula04-v1.md`.

Este arquivo é público. Nenhum nome de aluno entra aqui, no portal ou na tela de spec: o banco
guarda iniciais e grupo.

## Antes do encontro

| Item | Como conferir |
|---|---|
| Chave do professor no navegador do projetor | abrir `aulas/aula04.html?quiz-chave=<chave>` uma vez; a chave serve ao quiz ao vivo |
| Portal respondendo | abrir `simulador/` e `simulador/?painel=1&telao=1`, que é o endereço embutido nos slides 5 e 18; se o banco não responder, o portal avisa e segue em memória |
| Spec dos grupos | nenhum link é enviado: cada grupo abre a tela de spec pelo portal, na tela Progresso, botão "Abrir a spec do grupo" dos turnos 4 e 5. Conferir antes do encontro que os dois botões abrem a tela |
| Documentos do kit nos slides | no slide 11, clicar em ADR-001: o arquivo abre sobre o slide e fecha com Esc. Os slides leem `exemplos/aula04-simulador/` em tempo de execução |
| Kit baixado pelos grupos | pedir no dia anterior que cada dupla rode `python checar_ambiente.py` |
| Lista dos ativos dos grupos | não há lista prévia; o arquivo da aula tem 162 ativos e 718 pregões, de 02/01/2024 a 13/11/2026 |

## Roteiro por bloco

| Bloco | Minutos | Slides | O que fazer |
|---|---|---|---|
| Daily | 15 | 1 a 3 | capa, agenda e daily com cronômetro; cada grupo diz o estado do motor e o tempo de execução medido |
| 1 | 0 a 15 | 4 e 5 | QR code do portal; cada aluno entra, monta a carteira do grupo e para na montagem; painel da sala em modo telão; previsão falada, com a mão levantada; simulação; abrir no painel a simulação de dois alunos |
| 2 | 15 a 30 | 6 a 9 | duas perguntas de quiz ao vivo (sessão `m08-aula04-2026-11-18`, perguntas `preparo-normalizar` e `preparo-sharpe`); anúncio da atividade, com a tabela dos turnos e o ciclo de um turno; leitura em dupla da ADR-001 e da ADR-002 do kit |
| 3 | 30 a 45 | 10 a 12 | código do turno 1 linha a linha (3 min), turno 1 (5 min), turno 2 (7 min) |
| 4 | 45 a 60 | 13 e 14 | passagem para o kit (5 min) e turno 3 (8 min); 2 minutos de marcação e debrief |
| 5 | 60 a 75 | 15 e 16 | turno 4 (13 min); projetar a spec de um grupo no slide 16, que mostra em cada campo as iniciais de quem editou por último e há quanto tempo |
| 6 | 75 a 90 | 17 | turno 5 (12 min); 3 minutos de debrief; para projetar uma spec, voltar ao slide 16 e escolher Turno 5 |
| 7 | 90 a 105 | 18 a 24 | nuvens dos grupos no painel, demonstração da fronteira (6 a 8 min), quiz de duas perguntas (`fecho-sorteada` e `fecho-conferir`), A3 com o turno 6, referências e encerramento |

Piloto e copiloto trocam a cada turno. Nos turnos 1 e 2 cada aluno escreve no próprio notebook e o
colega da dupla revisa. Nos turnos 3 a 5 há um kit por dupla, de duas a três duplas por grupo.

Os slides de atividade (turnos 1 a 5 e passagem) têm a mesma estrutura: O que, Onde, Como e Pronto
quando. Os passos aparecem um por clique, a coluna da direita traz o apoio do turno e a ampulheta
aparece quando o cronômetro é iniciado. A checagem intermediária e a pergunta de debrief são deixa
de condução: ficam nas notas do apresentador de cada slide e nesta seção, fora da área projetada. O
aluno vê no slide o critério de pronto.

**Previsão do bloco 1 (slide 5).**
Pergunta falada, sem texto no slide, antes de liberar a simulação: entre 1.000 carteiras sorteadas
com os seus ativos, a de pesos iguais cai na borda de menor risco, no meio da nuvem ou na borda de
maior risco? Contar as mãos, anotar no quadro e liberar: Simular, com 10, 100, 1.000 e 10.000
carteiras.

## Práticas

**Turno 1 (slide 11, 5 min).**
Obrigatório: preencher `ATIVOS` e `PREGOES = 9`, escrever o valor esperado lido no portal, ver o
teste falhar e escrever o corpo de `retorno_do_dia`.
Checagem aos 3 min: o teste já falhou uma vez.
Debrief: que conta a função faz com os dois vetores?
Apoio no slide: `zip`, `sum` e `np.dot` com os dados de uma compra, e a ADR-001 em sobreposição.
O que observar: aluno que escreve o corpo antes do valor esperado; aluno que copia o número do
colega em vez de ler o da própria carteira.
Erros comuns: valor esperado em porcentagem quando a função devolve fração (o `conferir` aceita
`0.123`, `12.3` e `"12,3%"`); carteira do notebook diferente da do portal; soma dos retornos sem
multiplicar pelos pesos.
Contingência: quem travar por mais de 2 minutos usa a pergunta do slide 10, sobre o peso zero e o
peso 1.

**Turno 2 (slide 12, 7 min).**
Obrigatório: escrever os dois valores esperados, implementar `metricas`, rodar `conferir_turno2`,
gravar `simulador.py` e marcar os turnos 1 e 2 no portal.
Checagem aos 4 min: os dois valores esperados escritos e o teste falhando.
Debrief: o que muda no risco anual se `PREGOES` passar de 9 para 21?
Apoio no slide: `@`, `.mean()`, `.std(ddof=1)`, `** 0.5` e uma função que devolve dois valores,
com uma tabela de notas.
O que observar: se a dupla conversa sobre a conta ou só sobre a sintaxe.
Erros comuns: desvio padrão populacional no lugar do amostral (`ddof=1`); multiplicar o risco por
252 em vez da raiz de 252; anualizar cada ativo e só depois aplicar os pesos.
Contingência: quem não fechar usa as duas funções que vêm comentadas no `simulador.py` do kit, com
a liberação do professor, e segue para o bloco 4.

**Passagem para o kit (slide 13, 5 min).**
Obrigatório: descompactar o kit, rodar `checar_ambiente.py`, colar as duas funções, rodar
`conferir.py 1` e `conferir.py 2` e fazer o primeiro pedido de leitura ao agente.
Checagem aos 3 min: `checar_ambiente.py` sem erro.
Debrief: dupla sem agente funcionando se junta a outra dupla do mesmo grupo.
Apoio no slide: o `SPEC.md` e o `AGENTS.md` abertos em duas abas, e os comandos em blocos copiáveis.
Erros comuns: kit descompactado fora do repositório do grupo; terminal aberto em outra pasta;
Python anterior ao 3.10.
Contingência: dupla sem agente funcionando se junta a outra dupla do mesmo grupo. Não consertar
ambiente em aula.

**Turno 3 (slide 14, 8 min).**
Obrigatório: ler a spec modelo, escrever o `assert` do teste da dupla, ver falhar, pedir a
implementação ao agente e rodar `conferir.py 3`.
Checagem aos 4 min: o `assert` da dupla escrito e falhando.
Debrief: que propriedades o teste verifica, já que o portal não dá o número?
Apoio no slide: o que entra no pedido ao agente (turno, spec, proibição), `assert` de propriedade
com outros dados, e `SPEC.md`, `AGENTS.md` e ADR-002 em sobreposição.
O que observar: dupla que pede ao agente para escrever o `assert`; o `AGENTS.md` manda o agente
recusar.
Erros comuns: `assert` que compara com um vetor fixo, que só passa com uma semente; pedido ao
agente sem citar o turno, e o agente implementa os turnos seguintes.
Contingência: se o agente alterar um teste, mostrar que `conferir.py` continua reprovando e pedir
que a dupla desfaça a alteração.

**Turno 4 (slide 15, 13 min).**
Obrigatório: preencher a spec na tela do grupo, aberta pelo portal (tela Progresso, botão "Abrir a
spec do grupo"), copiar para o `SPEC.md`, escrever o `assert`,
pedir `simular` ao agente, rodar `conferir.py 4` e gerar o gráfico.
Checagem aos 6 min: a spec está no `SPEC.md` e o teste falha.
Debrief: que caso de borda o grupo escreveu?
O que observar: critério de aceite escrito como frase vaga ("funciona"); perguntar qual teste
reprova quando a função está errada.
Erros comuns: saída sem dizer as colunas da tabela; caso de borda ausente para `n` igual a zero ou
para um ativo só; Sharpe com a taxa livre de risco fixa dentro da função.
Contingência: se a tela de spec falhar, o grupo escreve direto no `SPEC.md` do kit, nos mesmos
cinco campos.

**Turno 5 (slide 17, 12 min).**
Obrigatório: escrever o requisito de tempo na spec, escrever o teste de tempo e o de `posicionar`,
pedir a implementação e rodar `conferir.py 5`; marcar os pesos do Solver na nuvem do portal.
Checagem aos 6 min: os dois testes escritos e falhando.
Debrief: a carteira do Solver caiu dentro ou na borda da nuvem?
O que observar: se o grupo mede o tempo ou confia na resposta do agente.
Erros comuns: teste de tempo com 100 simulações no lugar de 10.000; pesos do Solver informados em
porcentagem que não soma 100.
Contingência: é o primeiro turno a cortar. Se o bloco 5 atrasar, o turno 5 vira tarefa da sprint e
o bloco 6 fecha o turno 4.

**Demonstração da fronteira (slide 19, 6 a 8 min).**
Quem conduz: o professor, no widget da nuvem. Os dados são os da cesta de 15 ativos do acervo, com
1.423 retornos de 14/12/2020 a 31/08/2026. Os ativos dos grupos ficam fora do gráfico; dizer isso
antes de clicar.
Roteiro: clicar 10, 100, 1.000 e 10.000 sorteios e ler o melhor Sharpe de cada passo (-0,10, 0,15,
0,28 e 0,41); perguntar onde está a melhor carteira e quantos sorteios faltam para chegar nela;
ligar "Ótimas e fronteira" e mostrar a carteira de máximo Sharpe, com 0,92, e a de variância
mínima, com volatilidade de 9,67%.
O que a turma observa: nenhuma das 10.000 sorteadas passa da fronteira, e a otimização chega à
carteira ótima sem sortear.
Fechamento: a implementação é o turno 6 do kit, depois do encontro.

**Turno 6 (depois do encontro).**
Funções: `variancia_minima(retornos)`, `maximo_sharpe(retornos, rf)` e
`fronteira(retornos, pontos=50)`, com `scipy.optimize.minimize` (SLSQP) e pesos entre 0 e 1
somando 1.
Aceite: `python conferir.py 6` imprime `TURNO 6: OK`.
Apoio: a spec do turno 6 já vem preenchida no `SPEC.md`, os testes estão em `tests/test_turno6.py`
e a ADR-003 do kit registra as restrições da otimização. O slide 22 abre o `SPEC.md` e a ADR-003.
Amarração: o turno 6 é a base do A4, Otimizador de Carteira com Fronteira Eficiente, que exige a
fronteira sobreposta à nuvem. A Aula 05 parte do turno 6.

## Perguntas para quando a sala trava

| Pergunta | Resposta esperada | Erro que ela revela |
|---|---|---|
| Se o peso de um ativo for zero, quanto ele contribui para o retorno do dia? | nada; com peso 1, o retorno é o do próprio ativo | somar retornos sem os pesos |
| Por que ver o teste falhar antes de implementar? | um teste que nunca falhou pode não testar nada | tratar o teste como formalidade |
| O portal dá o número do turno 3? | não: o sorteio do navegador e o do NumPy geram sequências diferentes | esperar valor fixo de função aleatória |
| O que o teste de `sortear_pesos` pode afirmar sem conhecer o sorteio? | soma 1, nenhum negativo, formato, mesma semente devolve o mesmo vetor | teste que só passa com uma semente |
| A melhor carteira entre as 10.000 é a ótima? | é a melhor entre as sorteadas; a do Solver pode ficar fora da nuvem | confundir simulação com otimização |

## Contingências

| Situação | O que fazer |
|---|---|
| Banco fora do ar ou lento | o portal avisa e segue em memória; para forçar, abrir `simulador/?demo=1`. O painel e o placar ficam locais, e a marcação dos turnos vai para o quadro. O quiz ao vivo vira votação com a mão levantada, e a tela de spec é substituída pelo `SPEC.md` do kit |
| Ativo do grupo ausente do arquivo | o portal mostra "ativo não encontrado no arquivo da aula" e mantém a carteira montada; o grupo troca por outro do mesmo setor e anota a troca |
| Ativo com início de negociação dentro da janela | o portal limita o período ao que a janela comum tem e informa quantos pregões existem; o grupo escolhe um período menor ou troca o ativo |
| Dupla sem agente funcionando | junta-se a outra dupla do mesmo grupo; não há segundo notebook para os turnos 3 a 5 |
| Tela de spec fora do ar | a spec é escrita direto no `SPEC.md` do kit, nos mesmos cinco campos; o botão do portal, na tela Progresso, abre a tela de novo |
| Documento do kit não abre no slide | a sobreposição mostra o aviso e o link do arquivo; abrir em outra aba ou direto na pasta do kit |
| Encontro atrasado | ordem de corte: turno 5, depois a tela de spec; o núcleo é o portal, os turnos 1 e 2 e os turnos 3 e 4 no kit |

## Visitantes na sala

Em 18/11 a turma recebe de 8 a 12 visitantes de uma faculdade de Rondônia, que vêm observar a
dinâmica do PBL. A orientação da coordenação é manter o conteúdo previsto.

- Na abertura, dizer em uma frase o que os visitantes vão ver: grupos construindo, em turnos, o
  motor do artefato da sprint.
- Visitantes entram no portal pelo mesmo QR code e escolhem "Visitante". Ficam fora do placar e do
  relatório de participação.
- Na daily e nos turnos, os visitantes circulam e observam uma dupla por vez, sem intervir no
  código. Perguntas aos alunos ficam para os debriefs.
- No bloco 7, convidar um visitante a escolher qual nuvem abrir no painel.
- O PDF exportado pelo botão do deck revela o gabarito dos quizzes e não é distribuído.

## Depois do encontro

- A fronteira foi demonstrada no bloco 7, e a implementação da otimização é o turno 6 do kit, feito
  depois do encontro. A Aula 05 e o A4 partem do turno 6. O material v1 segue como leitura de apoio.
- O A3 (peso 3) tem review em 19/11/2026 e entrega em 20/11/2026, 23h59. A ADR individual trata de
  decisão do próprio aluno; as ADRs do kit são exemplo.
