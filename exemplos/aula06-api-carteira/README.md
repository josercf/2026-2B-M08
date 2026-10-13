# API e tela do simulador de carteira (exemplo da Aula 06)

Exemplo pronto e parcial da Aula 06, "Do Script ao Produto: React, FastAPI e Interpretação com
LLM". Mostra a separação que o A5 pede: `backend/` em FastAPI, que importa os módulos das sprints
anteriores e chama o LLM com a chave no servidor, e `frontend/` em React com Vite, que só chama a
API e desenha. Os números vêm do snapshot em `dados/` do acervo.

## Estrutura

| Pasta ou arquivo | Papel |
|---|---|
| `backend/carteira/dados.py` | coletor (A1) reduzido: Adj Close e CDI do snapshot, com a lacuna isolada preenchida pelo último preço (ADR-009) |
| `backend/carteira/metricas.py` | risco e retorno (A2): retornos diários na janela comum dos tickers pedidos e métricas anualizadas por 252 |
| `backend/carteira/otimizador.py` | otimizador (A4): variância mínima, máximo Sharpe e fronteira de 50 pontos |
| `backend/carteira/pipeline.py` | as três camadas numa função só, sem nada de FastAPI |
| `backend/main.py` | rotas, modelos Pydantic, cache, CORS e códigos de status |
| `backend/interpretacao.py` | prompt com os números reais, chamada à OpenRouter e verificador de números |
| `backend/tests/` | testes com `TestClient`, sem servidor e sem chave |
| `frontend/src/api.js` | todo o HTTP do frontend e a tradução de erro para o gestor |
| `frontend/src/App.jsx` e `Fronteira.jsx` | formulário, estados de carregamento e erro, tabela e gráfico em SVG |

## Contrato da API

| Rota | Entrada | Sucesso | Erros do contrato |
|---|---|---|---|
| `GET /ativos` | nenhuma | 200, lista de tickers da base | nenhum |
| `POST /carteiras/otimizar` | `tickers` (2 a 15, sem repetição), `inicio`, `fim`, `taxa_livre_risco` opcional | 200, início e fim da janela comum, número de retornos, métricas por ativo, as duas carteiras e a fronteira | 404 ticker fora da base; 422 entrada inválida ou janela comum com menos de 60 retornos |
| `POST /carteiras/interpretar` | o mesmo pedido | 200, prompt, texto, modelo e a verificação de cada número | 404 e 422 como acima; 503 sem chave no servidor; 502 falha do provedor |
| `POST /carteiras/exportar` | o mesmo pedido | 200, CSV com os pesos das duas carteiras | 404 e 422 como acima |

A documentação automática fica em `http://127.0.0.1:8000/docs` com o backend rodando.

## Como rodar

Backend, a partir de `backend/`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -v          # 21 testes, sem rede e sem chave
cp .env.example .env               # preencher OPENROUTER_API_KEY só para a interpretação
set -a && source .env && set +a    # exporta as variáveis para o processo
fastapi dev main.py                # http://127.0.0.1:8000/docs
```

Frontend, a partir de `frontend/`, com o backend rodando:

```bash
npm install
npm test                           # node --test src/api.test.js, sem navegador
npm run dev                        # http://localhost:5173
```

O `main.jsx` importa os tokens de cor e fonte de `assets/css/inteli-brand.css` do acervo, e por
isso o `vite.config.js` libera a leitura até a raiz do acervo. No repositório do grupo, troque
esse import pelo CSS do grupo.

## O que fica para o grupo

- Rota de métricas para pesos informados pelo gestor, com 422 para pesos que não somam 1
  (desafio do notebook da Aula 06).
- Teste fora da amostra e estabilidade dos pesos da Aula 05 expostos como rota.
- Escolha do modelo do LLM por custo, registrada em ADR com o custo medido por chamada.
- `SPEC.md` com este contrato antes de dividir o trabalho entre frontend e backend.

## Segredos

A chave da OpenRouter vive só na variável de ambiente `OPENROUTER_API_KEY` do processo do
backend. O `.env` está no `.gitignore` do acervo, e o frontend nunca recebe a chave: tudo o que
o navegador baixa, inclusive variável `VITE_*`, qualquer pessoa consegue ler.
