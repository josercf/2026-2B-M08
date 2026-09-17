# Dados do case

## 1. O que é esta pasta

Snapshot dos dados do case, coletado em 17/09/2026 pelo script `tools/baixar_dados.py`, cobrindo a janela de 02/01/2019 a 31/08/2026. Notebooks, decks e testes leem os números apenas dos arquivos desta pasta; nenhum deles chama a rede para recalcular esses valores.

## 2. Arquivos

| Arquivo | Conteúdo | Fonte | Linhas | Colunas |
|---|---|---|---|---|
| `precos_ajustados.csv` | Preço de fechamento ajustado por desdobramentos, grupamentos, bonificações e proventos (Adj Close) | Yahoo Finance, via yfinance 1.7.0 | 1.908 | `data` e as 15 colunas de ticker listadas em A cesta de referência |
| `precos_fechamento.csv` | Preço de fechamento ajustado apenas por desdobramentos, grupamentos e bonificações (Close) | Yahoo Finance, via yfinance 1.7.0 | 1.908 | `data` e as 15 colunas de ticker |
| `eventos_desdobramento.csv` | Desdobramentos, grupamentos e bonificações em ações da cesta, no período | Yahoo Finance, via yfinance 1.7.0 | 15 | `ticker, data, fator` |
| `eventos_proventos.csv` | Dividendos e juros sobre capital próprio pagos pela cesta, no período | Yahoo Finance, via yfinance 1.7.0 | 499 | `ticker, data, valor` |
| `cdi_diario.csv` | Taxa DI over, divulgação diária (SGS 12) | Banco Central do Brasil, SGS, série 12 | 1.926 | `data, valor` |
| `selic_meta.csv` | Meta da taxa Selic definida pelo Copom (SGS 432) | Banco Central do Brasil, SGS, série 432 | 2.800 | `data, valor` |
| `ipca_mensal.csv` | Variação mensal do IPCA (SGS 433) | Banco Central do Brasil, SGS, série 433 | 92 | `data, valor` |
| `ptax_venda.csv` | Taxa de câmbio, dólar americano, venda, PTAX (SGS 1) | Banco Central do Brasil, SGS, série 1 | 1.926 | `data, valor` |

Nas duas tabelas de preço, célula vazia é ausência de cotação (ver seção 5).

Os links abaixo, um por série do Banco Central, foram conferidos em 17/09/2026 com `curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n"`, todos retornando código 200. Duas séries (12 e 433) não têm página própria no catálogo de dados abertos do Banco Central; para essas, o link registrado é o endpoint da API SGS que o script usa para baixar os valores.

| Série SGS | Arquivo | Link conferido | Origem do link |
|---|---|---|---|
| 12 | `cdi_diario.csv` | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=01/01/2019&dataFinal=31/08/2026` | Endpoint da API SGS usado pelo script |
| 432 | `selic_meta.csv` | `https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom` | Página do catálogo de dados abertos |
| 433 | `ipca_mensal.csv` | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2019&dataFinal=31/08/2026` | Endpoint da API SGS usado pelo script |
| 1 | `ptax_venda.csv` | `https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio---livre---dolar-americano-venda---diario` | Página do catálogo de dados abertos |

## 3. A cesta de referência

A cesta reúne 15 ativos negociados na B3: três bancos do mesmo setor para comparar pares diretos, três exportadoras sensíveis ao câmbio, três ETFs de índice para servir de referência de mercado (Ibovespa, S&P 500 em reais e ouro), e mais seis ativos que ampliam a cesta para outros setores.

| Ticker | Ativo | Grupo na cesta |
|---|---|---|
| PETR4 | Petrobras | Exportadora sensível ao câmbio (petróleo) |
| VALE3 | Vale | Exportadora sensível ao câmbio (minério de ferro) |
| SUZB3 | Suzano | Exportadora sensível ao câmbio (celulose) |
| ITUB4 | Itaú Unibanco | Banco |
| BBDC4 | Bradesco | Banco |
| BBAS3 | Banco do Brasil | Banco |
| ABEV3 | Ambev | Bens de consumo |
| WEGE3 | WEG | Bens de capital |
| EGIE3 | Engie Brasil | Geração de energia elétrica |
| RENT3 | Localiza | Aluguel de veículos |
| B3SA3 | B3 | Bolsa de valores |
| MGLU3 | Magazine Luiza | Varejo eletrônico |
| BOVA11 | ETF | Índice Ibovespa |
| IVVB11 | ETF | Índice S&P 500 em reais |
| GOLD11 | ETF | Ouro |

## 4. Três visões de preço

1. **Close** (`precos_fechamento.csv`). Preço de fechamento já dividido pelos fatores de desdobramento, grupamento e bonificação; um evento desse tipo não aparece como salto na série.
2. **Adj Close** (`precos_ajustados.csv`). Além dos mesmos fatores, desconta também os proventos (dividendos e juros sobre capital próprio) pagos depois de cada data.
3. **Preço negociado**. Reconstruído a partir do Close, multiplicado pelos fatores dos eventos de desdobramento posteriores à data. Não está entre os arquivos desta pasta: cada notebook das aulas seguintes recalcula essa série a partir de `precos_fechamento.csv` e `eventos_desdobramento.csv`.

Exemplo medido, travado em `test_adj_close_da_petr4_desconta_proventos`: no primeiro pregão da janela (02/01/2019), o Adj Close da PETR4 vale 26,13% do Close, proporção que acumula todos os proventos pagos entre essa data e 31/08/2026. Em BOVA11 e IVVB11, o Adj Close é igual ao Close nesta amostra, sem provento registrado pelo provedor para as duas ETFs no período.

## 5. Falhas reais do provedor

As ausências abaixo vêm do provedor, ficam marcadas com célula vazia nas duas tabelas de preço e estão travadas nos testes; nenhum notebook deve preenchê-las sem registrar a decisão em ADR.

- BOVA11 e IVVB11 ficam sem cotação em 24/10/2025, a mesma data nas duas séries.
- GOLD11 acumula 485 pregões sem cotação na janela. A primeira cotação do fundo aparece em 11/12/2020, o que deixa 484 pregões vazios antes dessa data; o pregão de 24/10/2025 completa as 485 ausências, compartilhado com BOVA11 e IVVB11.

## 6. Eventos corporativos

`eventos_desdobramento.csv` registra os 15 eventos de desdobramento, grupamento ou bonificação em ações da cesta na janela, com o contrato `ticker, data, fator`. O yfinance não informa o tipo do evento; a classificação abaixo é inferida do valor do fator.

| Fator | Classificação | Eventos na janela | Exemplo |
|---|---|---|---|
| Menor que 1 | Grupamento | 1 | MGLU3, 27/05/2024, fator 0,1 |
| Inteiro maior que 1 | Desdobramento | 5 | B3SA3, 17/05/2021, fator 3; WEGE3, 28/04/2021, fator 2; BBAS3, 16/04/2024, fator 2 |
| Fracionário maior que 1 | Bonificação em ações | 9 | BBDC4, 01/04/2019, fator 1,2 |

`eventos_proventos.csv` registra os proventos pagos pela cesta na janela, com o contrato `ticker, data, valor`: 499 pagamentos, todos com valor positivo.

## 7. Como regenerar

Rodar `.venv/bin/python tools/baixar_dados.py` a partir da raiz do repositório. O script precisa de rede e do pacote yfinance, por isso roda só com o interpretador do `.venv` (a stack de validação não carrega yfinance). Notebooks e testes nunca chamam este script: eles leem os CSVs já versionados nesta pasta.

Rodar de novo só quando a janela do case mudar, e atualizar a data da coleta na seção 1. Se um valor travado em `tools/tests/test_dados.py` divergir depois de uma nova coleta, a causa provável é revisão de histórico pelo provedor: investigar antes de alterar o número do teste, e registrar o que mudou nesta seção com a data da nova coleta.

## 8. Termos de uso

Os termos de uso do Yahoo Finance restringem a redistribuição dos dados brutos. O snapshot desta pasta é pequeno, tem finalidade educacional e mantém a atribuição ao Yahoo Finance e ao yfinance como fonte. A mitigação de longo prazo, para o caso de a redistribuição precisar de licença mais formal, é trocar a fonte de preços pelas séries históricas oficiais da B3 (COTAHIST); a decisão está registrada na ADR-003.
