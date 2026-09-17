# ADR-003: dados do case da B3 e do Banco Central versionados

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

Toda aula de Computação do módulo trabalha sobre preço de ativo e taxa de referência: a Aula 01
coleta e trata ausências, a Aula 02 converte preço em retorno, a Aula 03 monta a matriz de
covariância, a Aula 04 simula carteiras, a Aula 05 expõe métricas por API e a Aula 06 testa a
carteira fora da amostra. Os números de deck, material, notebook, widget e animação precisam sair
de uma fonte única e estável, porque a constraint do acervo proíbe número digitado de memória.

Uma coleta ao vivo em sala depende de rede, de disponibilidade do provedor e da data em que a aula
acontece, e o mesmo notebook devolveria números diferentes em dias diferentes. O parceiro do
projeto tem premissas descritas no LBL da Adalove, que ainda não foi lido (P4 do
`PLANO_DE_ENSINO.md`), e a cesta precisa existir antes disso para as aulas serem construídas.

## Decisão

Os dados do case são um snapshot versionado de 15 ativos da B3 pelo yfinance e de quatro séries do
SGS do Banco Central.

## Motivações

1. **Reprodutibilidade.** A janela vai de 02/01/2019 a 31/08/2026 e foi coletada em 17/09/2026,
   com 1.908 pregões nas duas tabelas de preço. Qualquer pessoa que rode os notebooks em qualquer
   dia obtém os mesmos números, e os números do deck ficam travados em
   `tools/tests/test_dados.py`.
2. **A janela cobre o que as ponderadas pedem.** Ela inclui o choque de março de 2020, o ciclo de
   alta da Selic de 2021 a 2023 e o período mais recente (design, seção 8).
3. **A cesta foi escolhida pelo que ela ensina.** Três bancos para comparar pares do mesmo setor,
   três exportadoras sensíveis ao câmbio, três ETFs de referência (Ibovespa, S&P 500 em reais e
   ouro) e mais seis ativos de outros setores. A GOLD11 tem primeira cotação em 11/12/2020, o que
   dá à Aula 01 um caso real de histórico curto (`dados/README.md`, seção 3).
4. **As séries do Banco Central entram porque o case pede.** O CDI (SGS 12) é a taxa livre de
   risco do Índice de Sharpe, a Selic meta (SGS 432) explica correlações do período, o IPCA
   (SGS 433) é a régua de retorno real e o PTAX de venda (SGS 1) liga as exportadoras ao câmbio
   (`PLANO_DE_ENSINO.md`, seção 2).
5. **As três visões de preço viram conteúdo.** O `Close` do Yahoo já vem dividido pelos fatores de
   desdobramento, grupamento e bonificação, então nenhuma queda diária da cesta é artefato de
   evento corporativo, e as maiores são choques reais (PETR4 com -29,70% em 09/03/2020, VALE3 com
   -24,56% em 28/01/2019). O `Adj Close` desconta também os proventos: no primeiro pregão da
   janela, o da PETR4 vale 26,13% do `Close`. O preço como foi negociado na época é reconstruído
   em aula multiplicando o `Close` pelos fatores posteriores de `eventos_desdobramento.csv`, e é
   nessa visão que o grupamento da MGLU3 (fator 0,1 em 27/05/2024) e o desdobramento da B3SA3
   (fator 3 em 17/05/2021) aparecem como saltos.
6. **As falhas do provedor são dado de aula.** BOVA11, IVVB11 e GOLD11 ficam sem cotação em
   24/10/2025, pregão normal da B3, e a GOLD11 acumula 485 pregões sem cotação, dos quais 484 são
   anteriores à primeira cotação do fundo. Descartar as datas com ausência mantém 1.423 dos 1.908
   pregões, tira março de 2020 da cesta inteira e derruba a volatilidade anual da PETR4 de 39,25%
   para 33,41%. O primeiro ADR pedido aos grupos é exatamente essa decisão de tratamento.

## O que está versionado

| Arquivo | Conteúdo | Fonte | Linhas |
|---|---|---|---|
| `dados/precos_ajustados.csv` | `Adj Close` dos 15 ativos | Yahoo Finance via yfinance 1.7.0 | 1.908 |
| `dados/precos_fechamento.csv` | `Close` dos mesmos 15 ativos | Yahoo Finance via yfinance 1.7.0 | 1.908 |
| `dados/eventos_desdobramento.csv` | desdobramento, grupamento e bonificação: `ticker, data, fator` | Yahoo Finance via yfinance 1.7.0 | 15 |
| `dados/eventos_proventos.csv` | proventos por ação: `ticker, data, valor` | Yahoo Finance via yfinance 1.7.0 | 499 |
| `dados/cdi_diario.csv` | taxa DI over, divulgação diária | BCB SGS, série 12 | 1.926 |
| `dados/selic_meta.csv` | meta da Selic definida pelo Copom | BCB SGS, série 432 | 2.800 |
| `dados/ipca_mensal.csv` | variação mensal do IPCA | BCB SGS, série 433 | 92 |
| `dados/ptax_venda.csv` | dólar americano, venda, PTAX | BCB SGS, série 1 | 1.926 |

O contrato de coluna, os links conferidos de cada série, a classificação dos 15 eventos
corporativos e o procedimento de regeneração estão em `dados/README.md`. A regeneração roda por
`tools/baixar_dados.py`, que é o único arquivo do acervo que chama a rede para esses dados.

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Os termos de uso do Yahoo Finance restringem a redistribuição do dado bruto | o snapshot é pequeno, tem finalidade educacional e mantém a atribuição ao Yahoo Finance e ao yfinance; se a redistribuição precisar de licença mais formal, a fonte de preços passa a ser a série histórica oficial da B3 (COTAHIST), com o mesmo contrato de coluna, e só `tools/baixar_dados.py` muda |
| O Yahoo pode bloquear ou mudar a API do provedor | nenhum notebook e nenhum teste depende da coleta ao vivo; a coleta aparece nas Aulas 01 e 02 com tempo limite e queda para o snapshot, e `M08_OFFLINE=1` desliga a rede |
| O provedor revisa histórico, e um valor travado em teste passa a divergir | `dados/README.md`, seção 7, manda investigar a divergência antes de alterar o número do teste e registrar o que mudou com a data da nova coleta |
| A cesta de 15 ativos pode não ser a do parceiro, cujas premissas estão no LBL não lido (P4) | a cesta está declarada como referência das aulas até o LBL ser lido, e o contrato de coluna permite trocar os tickers sem mexer no código dos notebooks |
| Aula sem rede, ou Colab sem acesso ao repositório | os notebooks carregam `../dados/` quando existe e caem para a URL bruta do repositório no Colab |
| Célula vazia preenchida em silêncio por um notebook esconde a ausência real do provedor | as ausências estão travadas em `tools/tests/test_dados.py`, e o tratamento é decisão registrada em ADR pelo grupo |

## Consequências

**Positivas**

- Todo número do acervo tem origem em arquivo versionado, conferível com `git log`, e a suíte de
  teste reprova divergência.
- A aula acontece sem rede, o que remove a dependência de infraestrutura no horário do encontro.
- As ausências e os eventos corporativos reais dão conteúdo que dado sintético não daria, com
  impacto numérico medido para a turma discutir.
- Os notebooks abrem no Colab pelo badge e executam do início ao fim sem edição.

**Negativas**

- O snapshot envelhece, e atualizar a janela exige nova coleta, nova medição e revisão dos números
  travados em teste.
- Os CSVs de preço somam 1.908 linhas por arquivo dentro do git, o que aumenta o repositório.
- A cesta é provisória enquanto o LBL do parceiro não for lido.
- Nenhuma das duas tabelas versionadas traz o preço como foi negociado na época, que precisa ser
  reconstruído em aula a cada notebook que dependa dele.

## ADRs relacionadas

- ADR-005, cujas animações e widgets leem apenas `dados/`.
- ADR-002, porque o A5 verifica os números citados pelo LLM contra os mesmos dados.
