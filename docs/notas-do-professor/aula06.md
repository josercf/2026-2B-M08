# Notas do professor: Aula 06, Do Script ao Produto

Material interno de condução, não distribuído ao aluno. Aula 06, 16/12/2026 (quarta), Semana 10,
Sprint 5, Aula 43 do módulo na Adalove. Horário de relógio a confirmar (P1). Roteiro de origem:
`PLANEJAMENTO_AULA_A_AULA.md`, Aula 06. Todo número abaixo está travado em
`tools/tests/test_aula06.py`, medido por `tools/medidas_aula06.py` pela própria API de
`exemplos/aula06-api-carteira/`.

## Antes da aula

- Subir a API de exemplo na máquina do professor, a partir de `exemplos/aula06-api-carteira/backend/`:
  `fastapi dev main.py`, e abrir `http://127.0.0.1:8000/docs`. Sem `OPENROUTER_API_KEY` no
  ambiente, a rota de interpretação devolve 503, que é o caso mostrado no montador.
- Subir o frontend em outra janela, a partir de `frontend/`: `npm install` (precisa de rede na
  primeira vez) e `npm run dev`, em `http://localhost:5173`. Para mostrar o erro de CORS ao vivo,
  rodar a API com `FRONTEND_ORIGEM=http://localhost:9999` e clicar em Otimizar com o console aberto.
- Para a demonstração com o LLM de verdade, exportar a chave da coordenação só no terminal do
  backend. Nunca projetar o terminal com a chave visível.
- Conferir que os dois vídeos tocam no navegador da sala: o Chromium dos validadores não decodifica
  H.264, e nenhuma checagem automática toca o vídeo.

## Números da aula

| Medida | Valor |
|---|---|
| Pedido de referência | PETR4, VALE3, ITUB4, WEGE3 e IVVB11, de 01/01/2019 a 31/08/2026 |
| Retornos diários no pedido | 1.907, de 03/01/2019 a 31/08/2026 (ADR-009: lacuna da IVVB11 em 24/10/2025 preenchida, janela comum dos tickers pedidos) |
| CDI do período, taxa livre de risco | 9,51% ao ano |
| Máximo Sharpe | 51,64% IVVB11, 25,02% WEGE3, 23,33% PETR4; retorno 26,90%, volatilidade 19,13%, Sharpe 0,91 |
| Variância mínima | 61,65% IVVB11, 22,55% ITUB4, 10,94% WEGE3, 2,54% VALE3, 2,32% PETR4; retorno 21,04%, volatilidade 16,71% |
| Problemas de otimização por pedido novo | 52 (1 + 1 + 50 pontos da fronteira) |
| Cinco pedidos (A, A, B, A, B) | 260 sem cache, 104 com cache |
| Status do montador | 200, 404, 422 e 503 nas nove combinações |
| Texto com erros plantados | 12 números, 10 conferem, 2 acusados (17,13% e 30,00%); 0,16 passa |

## Daily (15 min)

Pedir a cada grupo: em que módulo estão o coletor, as métricas, o motor de Monte Carlo e o
otimizador. Grupo que responde "no notebook" ainda não tem o que a API importar; a tarefa da
semana começa por extrair funções para módulos. Confirmar em voz alta que a chave do LLM recebida
pela coordenação está fora do repositório: perguntar onde ela está agora.

## Bloco 1: resgate e Peer Instruction (slides 3 e 4)

Resgate em uma frase: a Aula 05 deixou pronto o teste fora da amostra das duas carteiras ótimas e
a medida de estabilidade dos pesos entre janelas.

**Gabarito do Peer Instruction:** "No servidor, em Python, e o navegador recebe JSON".

| Alternativa | Erro que revela | Contra-argumento |
|---|---|---|
| No navegador, em JavaScript | confundir velocidade de resposta com lugar do cálculo | reescrever A1, A2 e A4 em outra linguagem e mandar o histórico inteiro para cada gestor |
| Nos dois, para conferir | achar que redundância é verificação | dois otimizadores divergem no primeiro arredondamento, e o grupo mantém o dobro de código |
| No servidor, devolvendo imagem | pensar no gráfico como o produto | sem os números, a tela perde tabela de pesos, interatividade e CSV |

**Critério de discussão:** se o primeiro voto passar de 70% na certa, revelar e seguir. Entre 30%
e 70%, dois minutos de dupla e novo voto. Abaixo de 30%, a turma não fez o autoestudo 6.1: tocar a
animação da requisição na sala (24 s) antes do segundo voto.

**Turma sem pré-aula.** Se a maioria não tem React nem FastAPI rodando, não instalar nada em sala:
o Bloco 4 usa só o notebook no Colab, que não precisa de Node nem de servidor. O frontend fica como
demonstração do professor no Bloco 5, e o `npm install` vira tarefa da semana.

## Bloco 2: cliente, servidor e o contrato (slides 6 a 8)

Antes de tocar a animação, cada um anota em qual caixa um pedido com ticker repetido para.
Resposta: no servidor, na validação; nenhum problema de otimização é resolvido.

Montador: para cada combinação, a dupla anota o status antes de clicar em Enviar. Ordem sugerida:
pedido de referência em `/carteiras/otimizar` (200), ticker que não existe (404), um ticker só
(422), pedido de referência em `/carteiras/interpretar` (503).

| Pergunta quando a sala trava | Resposta esperada | Erro comum que revela |
|---|---|---|
| Por que `/carteiras/interpretar` com o pedido válido devolve 503 e não 200? | o servidor de gravação não tinha a chave; o cálculo funcionou e só a camada de texto falhou | achar que erro do LLM invalida os números |
| Por que GET em `/ativos` e POST em `/carteiras/otimizar`? | um só lê a lista; o outro recebe um corpo com o pedido | achar que POST é "para gravar" e não serve para cálculo |
| O que o SPEC.md ganha com essa tabela? | frontend e backend testam contra o mesmo combinado em paralelo | dividir o trabalho e só juntar na véspera da review |

## Bloco 3: FastAPI ao vivo (slides 10 a 12)

Abrir o `/docs` da API rodando e mostrar que os campos do formulário vêm do modelo Pydantic. Na
animação do cache, a turma prevê quantos problemas o servidor com cache resolve nos cinco pedidos;
resposta: 104. Quem responde 52 esqueceu que a consulta B, com janela desde 2021, é outra consulta.

**Pergunta disparada:** que erro a API deve devolver para um ticker que não existe? Não há resposta
universal: 404 (recurso fora da base) e 422 (entrada inválida, porque o ticker vem no corpo) são
escolhas defensáveis. Vale a dupla que justifica pelo contrato. O exemplo adota 404, com o ticker na
mensagem, para separar pedido mal formado de recurso que falta, e registra a escolha no `SPEC.md`.
Segundo erro comum: 500, que diz ao gestor que o servidor quebrou.

## Bloco 4: dupla no notebook (slide 13, 12 min)

Seções 1 a 4 do notebook, com as células prontas: o 200 e o 422 já vêm escritos e servem de
teste fornecido. Aos 6 minutos, troca de condutor. O caso do ticker inexistente tem
`status_esperado = None` de propósito: a dupla escreve o status antes de rodar.

- **Obrigatório.** Rodar as seções 1 a 4 e ver passar o 200 e o 422; ler o `loc` do 422. Cada dupla
  recebe um caminho e escreve um caso dele: 200 com dois tickers da cesta, 422 com início depois
  do fim (o `model_validator` recusa) ou erro de domínio com `XPTO3` (célula c). Distribuir os três
  caminhos em rodízio pelo número da dupla, para que cada um tenha ao menos uma dupla.
- **Extensão.** Escrever os outros dois caminhos e anotar os três no plano de testes do SPEC.md.
- **Checagem aos 6 minutos.** A seção 4 passou e o caso do caminho da dupla está escrito, ainda sem
  rodar. Dupla com erro de importação nesse ponto recebe ajuda antes da troca.
- **Debrief (3 minutos finais do bloco).** Uma dupla por caminho mostra o status obtido. No `XPTO3`,
  confrontar o status escolhido com o contrato do slide 12: o exemplo devolve 404, e 422 também é
  defensável se o contrato disser.
- **Contingência.** Se o Colab falhar ou o `fastapi` não importar, a dupla escreve o caso no papel,
  com o status esperado, e o professor roda os três caminhos no notebook projetado.

| Pergunta | Resposta esperada | Erro comum |
|---|---|---|
| O que o `TestClient` evita? | subir servidor e abrir porta; o teste roda no CI e no Colab | achar que testar API exige Postman ou servidor no ar |
| O que o `loc` do 422 diz? | `["body", "tickers"]`: o campo do corpo que falhou | ler só o código e ignorar o corpo |
| Por que o assert da soma dos pesos usa tolerância? | ponto flutuante: a soma é 1 a menos de 1e-9 | comparar float com `==` |

## Bloco 5: o componente React (slides 15 e 16)

Mostrar o frontend rodando, digitar `XPTO3` e ler a mensagem traduzida. Depois desligar o CORS
(variável `FRONTEND_ORIGEM` errada) e mostrar o erro no console: a API registra 200 no terminal e
o navegador descarta a resposta.

**Gabarito da escolha coletiva:**

| Item | Destino | Comentário falado |
|---|---|---|
| A chave do LLM | Servidor | tudo o que o navegador baixa é público, inclusive variável `VITE_*` |
| O cálculo da fronteira | Servidor | é o Python das sprints, testado; o navegador recebe JSON |
| O gráfico da fronteira | Navegador | desenhar é conversão de número em pixel, e a interatividade é do navegador |
| A validação da entrada | Nos dois | no navegador para ajudar o gestor; no servidor porque o navegador pode ser contornado |

O item 4 costuma dividir a sala. A pergunta que destrava: "se alguém chamar a API pelo `/docs`,
sem a tela, quem valida?".

## Bloco 6: o LLM no backend (slides 18 a 20)

O texto do widget é exercício, escrito pelo acervo com três erros plantados, e o slide diz isso.
Não apresentar como saída de modelo.

Sequência: a sala lê e marca à mão os números suspeitos; depois "Conferir por código"; depois
"Revelar erros plantados".

**Pergunta disparada:** que número desse texto o grupo consegue conferir por código? Resposta: todo
número que veio do JSON do prompt, por presença. O 0,16 confere por presença e está errado, porque
pertence ao IVVB11; a origem devolvida pelo verificador entrega o erro a quem lê.

| Pergunta | Resposta esperada | Erro comum |
|---|---|---|
| Por que o 30,00% é erro mesmo se o modelo "achar" provável? | o JSON não tem retorno futuro, e o prompt proíbe prometer | aceitar número plausível sem fonte |
| Como pegar o ativo trocado por código? | exigir o mesmo ticker na frase e na origem | achar que a verificação de presença basta |
| O que muda ao trocar o modelo? | custo por token e texto; o verificador continua igual | escolher modelo sem medir custo por chamada |

## Bloco 7: quiz e amarração (slides 21 a 23)

**Gabarito do quiz:** 1. 422; 2. ambiente do backend; 3. o número existe em outro ativo.

Amarração: o A5 vale 2 pontos (`PLANO_DE_ENSINO.md`, seção 5), com review da Sprint 5 em
18/12/2026, que fecha o módulo. Reforçar `/backend` e `/frontend` separados, contrato da API no
SPEC.md antes de dividir o trabalho, cache, exportação em CSV e `.env.example` sem chave.

O roteiro do `PLANEJAMENTO_AULA_A_AULA.md` ainda cita o A5 com peso 1 "a confirmar"; o deck segue o
peso 2 do plano de ensino, conferido na Adalove em 13/10/2026.
