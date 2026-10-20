# Nuvem de palavras por voz com n8n (Aula 01)

Fluxo do slide "O que é o projeto deste módulo?", que entra na Aula 01 antes do slide do parceiro.
O professor clica no microfone, cada pessoa responde em uma frase em voz alta, e os termos ditos
entram numa nuvem de palavras no próprio slide enquanto a turma fala. A decisão e as alternativas
avaliadas estão na ADR-012.

| Arquivo | Papel |
|---|---|
| `workflow.json` | workflow importável do n8n: Webhook, conferência de token, ElevenLabs, extração de termos e resposta |
| `extrair_termos.js` | o código do nó Code "Extrair termos", idêntico ao que está dentro do `workflow.json` |
| `../../assets/js/inteli-nuvem.js` | componente do deck: microfone, corte dos trechos, fila de envio e desenho da nuvem |
| `../../assets/css/inteli-nuvem.css` | aparência do slide e da nuvem, só com tokens da marca |
| `../../tools/tests/test_nuvem.py` | testes no navegador, com microfone falso do Chromium e webhook simulado |
| `../../tools/tests/test_nuvem_workflow.py` | testes do `workflow.json` e da extração de termos |

## Fluxo

```mermaid
sequenceDiagram
    participant P as Navegador (slide)
    participant W as n8n: Webhook
    participant I as n8n: Conferir token
    participant E as ElevenLabs Speech-to-Text
    participant C as n8n: Extrair termos
    P->>P: getUserMedia e MediaRecorder; corta um trecho de 3,5 a 8 s na pausa da fala
    P->>W: POST multipart (audio = trecho WebM/Opus completo, token)
    W->>I: body.token e binário "audio"
    alt token certo e áudio presente
        I->>E: POST /v1/speech-to-text (file, model_id=scribe_v2, language_code=por, no_verbatim=true)
        E-->>C: { text: "..." }
        C-->>P: 200 { transcricao, termos: [{ texto, peso }] }
    else token errado ou sem áudio
        I-->>P: 403 { erro }
    end
    P->>P: soma os pesos, refaz a espiral e anima os termos novos
```

Em texto: o navegador grava trechos curtos e completos, envia cada um ao webhook sem parar de
gravar, e cada resposta acrescenta termos à nuvem. Um trecho leva, em média, a duração do áudio
mais 1 a 2 segundos de transcrição até aparecer no slide.

Detalhes que importam:

- **Cada trecho é um arquivo completo.** Com `MediaRecorder.start(timeslice)`, só o primeiro pedaço
  WebM traz o cabeçalho, e os seguintes não decodificam sozinhos. O componente para e reinicia o
  gravador a cada trecho. O corte espera uma pausa de 300 ms depois de 3,5 s de gravação, para não
  partir uma palavra ao meio, e é forçado em 8 s.
- **Trecho em silêncio não é enviado.** O componente mede o nível do microfone e descarta o trecho
  que não passou do limiar de fala, o que corta custo quando ninguém está falando.
- **Sem preflight de CORS.** O POST é `multipart/form-data` sem cabeçalho próprio, que o navegador
  trata como requisição simples, e o token vai como campo do formulário. Um cabeçalho como
  `X-Nuvem-Token` obrigaria o n8n a responder o `OPTIONS` de preflight, e a opção
  "Allowed Origins (CORS)" do Webhook cobre só requisições sem preflight.
- **Até dois envios em paralelo**, com tempo limite de 30 s. Falha de rede ou HTTP de erro vira
  aviso discreto no slide, e a gravação continua.
- **Sair do slide desliga o microfone.**

## Importação, passo a passo

1. **Credencial da ElevenLabs.** Em `elevenlabs.io`, crie uma chave de API com permissão de
   Speech to Text. No n8n, em Credentials, crie uma credencial do tipo **Header Auth** com nome
   `ElevenLabs xi-api-key`, campo Name `xi-api-key` e Value igual à chave.
2. **Importar.** No n8n, Workflows, Import from File, escolha `workflow.json`.
3. **Nó "ElevenLabs Speech-to-Text".** Em Credential for Header Auth, selecione a credencial do
   passo 1. O arquivo traz só um marcador (`SELECIONE-A-CREDENCIAL`), nunca a chave.
4. **Nó "Receber áudio" (Webhook).** Troque o Path `nuvem-m08-TROQUE-POR-UM-CAMINHO-ALEATORIO`
   por uma sequência aleatória longa (por exemplo, a saída de `python3 -c "import secrets;
   print(secrets.token_urlsafe(18))"`). Confira em Options, Allowed Origins (CORS):
   `https://josercf.github.io,http://localhost:8000,http://127.0.0.1:8000`.
5. **Nó "Conferir token" (IF).** Troque `TROQUE-ESTE-TOKEN` por um token seu. Para dispensar o
   token, apague a primeira condição e mantenha a do áudio.
6. **Ativar** o workflow e copiar a **Production URL** do Webhook.
7. **No deck**, abra a Aula 01 uma vez com
   `?nuvem=<Production URL>&nuvem-token=<token>` antes do `#`, por exemplo
   `https://josercf.github.io/2026-2B-M08/aulas/aula01.html?nuvem=https%3A%2F%2F...&nuvem-token=...`.
   O componente grava as duas chaves no `localStorage` do navegador, e as aberturas seguintes não
   precisam do parâmetro. Sem isso, o primeiro clique no microfone abre o campo de configuração no
   próprio slide.

Chaves do `localStorage`, por origem (o GitHub Pages e o `localhost:8000` guardam cada um a sua):

| Chave | Conteúdo |
|---|---|
| `inteli-nuvem-webhook` | URL de produção do webhook |
| `inteli-nuvem-token` | token conferido pelo nó IF (opcional) |

O repositório é público e publicado no GitHub Pages inteiro: a URL do webhook e o token nunca
entram em arquivo versionado.

## Teste antes da aula

1. Com o workflow ativo, rode no terminal, a partir de um áudio curto qualquer em português:

   ```bash
   curl -s -F "audio=@frase.webm" -F "token=SEU-TOKEN" "https://SEU-N8N/webhook/SEU-PATH"
   ```

   A resposta esperada é `{"transcricao": "...", "termos": [{"texto": "...", "peso": 1}]}`.
2. Abra o slide pelo endereço publicado (o microfone exige HTTPS ou `localhost`), clique no
   microfone, autorize e fale uma frase. O medidor de nível acende, e o primeiro termo aparece em
   poucos segundos.
3. Contingência: o campo "Digitar um termo e Enter" aceita vários termos separados por vírgula, e
   no console do navegador `IntelINuvem.adicionar(['carteira', 'risco'])` faz o mesmo.

## Extração de termos

O nó Code normaliza a transcrição (caixa baixa, NFC, sem pontuação, sem eventos de áudio como
`[risos]`), casa primeiro os termos compostos do vocabulário do módulo ("fronteira eficiente",
"excedente de caixa", "taxa livre de risco"), sem exigir acento, e depois conta as palavras
soltas fora de uma lista de stopwords do português falado, que inclui muletas como "né", "tipo" e
"aí". Um par de palavras que se repete no mesmo trecho vira composto. Siglas curtas do domínio
(B3, CDI, IA, API) passam pelo filtro de tamanho e saem em caixa alta. "Projeto" e "módulo" estão
nas stopwords porque repetem a pergunta do slide.

Para alterar a extração, edite `extrair_termos.js`, rode
`.venv/bin/python -m pytest tools/tests/test_nuvem_workflow.py` e copie o arquivo inteiro para o
campo JavaScript do nó Code (o teste reprova se os dois divergirem).

Alternativa com LLM: trocar o nó Code por um nó de modelo de linguagem (Basic LLM Chain ou
Information Extractor do n8n) com a instrução "devolva os termos de conteúdo da frase, juntando
termos compostos, em JSON". Ele reconhece compostos fora da lista ("simulação de cenários",
"painel para o gestor") e normaliza flexões, ao custo de uma segunda chamada paga por trecho, de
0,5 a 2 segundos a mais de latência e saída não determinística. A lista de compostos cobre o
vocabulário que a Aula 01 introduz, então o nó Code ficou como padrão.

## Custo aproximado

Preços de tabela consultados em 20/10/2026 (conferir antes de usar):

| Item | Preço | Uma rodada de 30 pessoas |
|---|---|---|
| ElevenLabs Scribe v2, por API | US$ 0,22 por hora de áudio | cerca de 5 minutos de áudio útil, menos de US$ 0,02 |
| n8n Cloud | cada trecho é uma execução | 40 a 80 execuções por rodada |
| n8n auto-hospedado | sem custo por execução | idem |

O plano por assinatura da ElevenLabs desconta créditos por minuto de transcrição, então o custo
real depende do plano da conta. O descarte dos trechos em silêncio reduz o volume enviado.

## Limitações conhecidas

- A fronteira entre dois trechos pode cortar uma palavra quando a pessoa fala sem pausa por mais de
  8 segundos.
- A nuvem vive na memória da página: recarregar o deck zera a nuvem.
- O microfone exige contexto seguro (HTTPS ou `localhost`). Pelo `file://`, o botão avisa e o
  campo de texto continua funcionando.
- Com mais de 60 termos, só os 60 mais citados aparecem. Com muitos termos longos e de peso igual,
  a espiral pode deixar alguns de fora antes de chegar a 60.
