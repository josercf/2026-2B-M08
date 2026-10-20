# ADR-012: Nuvem de palavras por voz com n8n e ElevenLabs Scribe

**Data:** 20/10/2026
**Status:** Proposta
**Decisores:** Prof. José Romualdo

## Contexto

O professor pediu, antes do slide do parceiro da Aula 01, um slide que pergunta à turma o que é o
projeto do módulo, com um botão que abre o microfone. O áudio vai a um fluxo do n8n, que extrai as
palavras, e a nuvem de palavras se monta no slide enquanto a turma fala. O pedido citou duas
opções de transcrição, ElevenLabs e "Whisper Flow".

Restrições do acervo que moldam a solução:

- O repositório é público e publicado inteiro no GitHub Pages: nenhuma chave de API e nenhuma URL
  de webhook podem ficar em arquivo versionado.
- O deck é HTML estático, sem build e sem servidor próprio. Quem guarda a chave da transcrição
  precisa ser um serviço fora do navegador.
- A marca pede canto reto, cor e família só por token, ícone do sprite Sharp e coral só como
  filete (ADR-011), conferidos pelo `check_brand.py`.

Comparação das opções de transcrição, com preço de tabela consultado em 20/10/2026:

| Critério | ElevenLabs Scribe v2 | OpenAI `gpt-4o-transcribe` / `gpt-4o-mini-transcribe` | OpenAI `whisper-1` | Wispr Flow |
|---|---|---|---|---|
| Preço por hora de áudio | US$ 0,22 (lote); US$ 0,39 em tempo real | cerca de US$ 0,36 / US$ 0,18 | cerca de US$ 0,36 | não publicado |
| Acesso por API | autosserviço, chave `xi-api-key` | autosserviço, chave Bearer | autosserviço | chave só pelo time enterprise; produto é app de ditado para desktop |
| WebM/Opus do `MediaRecorder` | aceito ("all major audio and video formats") | aceito (`webm` na lista) | aceito | a documentação converte para WAV PCM 16 kHz em base64 |
| Português | `language_code=por`; remoção de hesitações com `no_verbatim` | detecção automática ou parâmetro de idioma | idem | não documentado para este uso |
| Integração no n8n | HTTP Request multipart com credencial Header Auth | HTTP Request ou nó OpenAI | idem | HTTP Request com JSON em base64 |

"Whisper Flow" é o Wispr Flow, aplicativo de ditado para desktop. Ele tem documentação de API
(REST e WebSocket), mas a chave é concedida pelo time enterprise (`enterprise@wisprflow.ai`, segundo
a documentação de integração da PipesHub), sem cadastro de autosserviço e sem preço publicado.
Para um fluxo de servidor no n8n, a comparação útil é ElevenLabs Scribe contra os modelos de
transcrição da OpenAI.

## Decisão

O navegador grava trechos completos de 3,5 a 8 segundos e envia cada um, sem preflight de CORS, a
um webhook do n8n que transcreve na ElevenLabs Scribe v2, extrai os termos num nó Code em
JavaScript e devolve JSON; o deck acumula as contagens e desenha a nuvem em espiral.

## Motivações

- **ElevenLabs Scribe v2** custa US$ 0,22 por hora em lote, abaixo do `gpt-4o-transcribe` (cerca de
  US$ 0,36) e próximo do `gpt-4o-mini-transcribe` (cerca de US$ 0,18), aceita o WebM/Opus que o
  `MediaRecorder` do Chrome produz sem conversão, e tem `no_verbatim`, que tira "é", "hã" e
  repetições da transcrição antes da extração. A diferença de custo para uma rodada de 30 pessoas
  é de centavos; o que decide é o formato aceito sem conversão e a remoção de hesitações. O
  `gpt-4o-mini-transcribe` fica como alternativa documentada: trocar a URL, o cabeçalho e os nomes
  dos campos no nó HTTP Request.
- **n8n entre o navegador e a ElevenLabs** guarda a chave numa credencial, fora do repositório, e é
  o que o professor pediu. O mesmo fluxo serve de exemplo de integração para a turma.
- **Trechos completos em vez de `timeslice`**: com `start(timeslice)`, só o primeiro pedaço WebM
  traz o cabeçalho EBML, e os seguintes não decodificam sozinhos na API. Parar e reiniciar o
  gravador gera arquivos independentes. O corte espera uma pausa da fala (300 ms abaixo do limiar,
  depois de 3,5 s) e é forçado em 8 s, para não partir palavra ao meio na maioria dos cortes.
- **Lote por trecho em vez de tempo real por WebSocket**: o Scribe v2 Realtime custa US$ 0,39 por
  hora e exige token de uso único emitido por um servidor e uma conexão aberta pelo navegador. Para
  uma rodada de respostas curtas, 2 a 3 segundos de atraso por trecho são suficientes.
- **Token como campo do formulário, sem cabeçalho próprio**: `multipart/form-data` sem cabeçalho
  extra é requisição simples de CORS. Um cabeçalho `X-Nuvem-Token` exigiria resposta ao `OPTIONS`
  de preflight, e a opção "Allowed Origins (CORS)" do Webhook do n8n cobre só requisições sem
  preflight, segundo a documentação do nó. O token é conferido por um nó IF, que responde 403.
- **Extração no nó Code com lista de compostos** é determinística, gratuita e testável: o código é
  o arquivo `extrair_termos.js`, testado em node, e o teste reprova se o nó divergir dele. Um nó
  de LLM reconheceria compostos fora da lista, ao custo de uma segunda chamada paga por trecho e
  de saída não determinística; fica documentado no README como alternativa.
- **Desenho no navegador**: espiral arquimediana achatada na proporção do palco, com colisão por
  retângulo e varredura em grade quando a espiral falha. Cada termo tenta primeiro o centro que já
  ocupava, e a escala só diminui, para a nuvem crescer sem que os termos antigos pulem de lugar.
  Tamanho pela raiz da frequência, de 22 a 84 px, com no máximo 60 termos visíveis. Os três termos
  de maior peso usam a fonte de título pela classe `.nuvem-t1`, declarada em `inteli-brand.css`.

## Riscos conhecidos e mitigações

- **URL do webhook exposta permitiria gastar créditos da ElevenLabs.** A URL e o token ficam só no
  `localStorage` do navegador do professor (chaves `inteli-nuvem-webhook` e `inteli-nuvem-token`,
  gravadas pelo campo de configuração ou por `?nuvem=`), o path do webhook é trocado por uma
  sequência aleatória na importação e o nó IF recusa pedido sem token. `test_nuvem_workflow.py`
  reprova chave literal no `workflow.json`.
- **Rede da sala ou n8n fora do ar no meio da aula.** O envio tem fila, dois pedidos em paralelo e
  tempo limite de 30 s; a falha vira aviso no slide e a gravação continua. O campo de texto e a API
  `IntelINuvem.adicionar` mantêm a atividade sem voz. `test_nuvem.py` simula HTTP 500.
- **Palavra cortada entre dois trechos.** O corte na pausa reduz a ocorrência; fala contínua de
  mais de 8 segundos ainda pode cortar uma palavra, que sai como termo truncado ou some.
- **Microfone aberto além da atividade.** Sair do slide desliga o microfone, com teste.
- **Nome dos campos da API muda.** A documentação da ElevenLabs consultada em 20/10/2026 mostra
  `scribe_v2` nos exemplos e não menciona mais `scribe_v1`. O teste exige só o prefixo `scribe_`, e
  o README manda conferir o `curl` antes da aula.
- **Nuvem perdida ao recarregar.** O estado vive na memória da página. Fica registrado como
  limitação; persistir em `sessionStorage` é a extensão natural se isso acontecer em aula.
- **Opção de CORS do Webhook com nome interno diferente em versões antigas do n8n.** O README
  manda conferir o campo "Allowed Origins (CORS)" depois da importação.

## Consequências

- Positivas: o slide funciona com qualquer n8n (nuvem ou auto-hospedado) sem segredo no
  repositório; o componente é reaproveitável em qualquer deck com
  `<div class="nuvem" data-largura data-altura>`; a extração e o desenho têm teste automatizado,
  inclusive o fluxo completo com microfone falso e webhook simulado.
- Negativas: a atividade depende de três serviços em sala (n8n, ElevenLabs e rede), e por isso o
  campo de texto existe. `inteli-brand.css` ganhou a classe `.nuvem-t1` na lista de elementos com
  fonte de título, e `tools/icones.py` ganhou cinco ícones montados por JavaScript (`mic`, `stop`,
  `check`, `delete_sweep`, `settings`).
- Fica fora desta ADR: a inclusão do slide no `aulas/aula01.html` e a revisão do tempo do Bloco 1
  no `PLANEJAMENTO_AULA_A_AULA.md`, que a abertura com a nuvem consome.

## ADRs relacionadas

- ADR-004: a nuvem é uma interação de abertura do bloco, na linha da sala de aula invertida.
- ADR-005: o componente segue a regra dos widgets de medir pelo `data-largura` e `data-altura` do
  markup, porque slide fora de cena mede zero.
- ADR-011: canto reto, ícones do sprite Sharp e pesos do `TIP-04`.
