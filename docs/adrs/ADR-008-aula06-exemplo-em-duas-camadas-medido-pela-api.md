# ADR-008: Aula 06 medida pela própria API de exemplo em duas camadas

**Data:** 13/10/2026
**Status:** Proposta
**Decisores:** Prof. José Romualdo

## Contexto

A Aula 06 (16/12/2026, Semana 10, Sprint 5) ensina React, FastAPI e interpretação por LLM e
alimenta o A5, que pede `/backend` e `/frontend` separados, cache da consulta, exportação em CSV
e um texto de LLM verificável contra os números da tela (ADR-007 e `REVISAO-LBL08-COMPUTACAO.md`,
Artefato 5). O acervo exige que todo número de aula venha de `dados/` por código e fique travado
em teste. Três pontos do roteiro não tinham forma definida: de onde vêm os números de uma aula
sobre uma API, como medir o "tempo de resposta com e sem cache" da animação pedida na Preparação,
e o que é o "texto de interpretação com erros plantados" do Bloco 6.

## Decisão

Os números da Aula 06 são medidos pela própria API de `exemplos/aula06-api-carteira/`, chamada
com `TestClient`; o efeito do cache é medido em problemas de otimização resolvidos, e o texto com
erros plantados é gerado por código a partir da resposta da API e conferido pelo verificador de
presença que a própria API usa.

## Motivações

1. **A medição usa o mesmo caminho da API.** `tools/medidas_aula06.py` carrega o `main.py` do exemplo e
   mede o que ele devolve. Se o exemplo mudar, o deck, o material, o notebook e os widgets
   reprovam juntos em `tools/tests/test_aula06.py`, `test_deck_aula06.py` e `test_material_aula06.py`.
2. **Tempo de relógio não trava em teste.** O tempo de resposta varia com a máquina e com a carga.
   A contagem de chamadas ao SLSQP é determinística (52 por pedido novo; 260 sem cache e 104 com
   cache na sequência A, A, B, A, B) e mede o que demora num pedido.
3. **Erro plantado tem que ser conhecido de antemão.** Um texto gerado por um LLM de verdade muda a
   cada chamada e não pode ser travado em teste. O texto do exercício é escrito por código com os
   números reais e três erros de tipos diferentes (valor alterado, promessa inventada e ativo
   trocado), declarado como exercício em todo lugar em que aparece.
4. **A limitação da verificação vira conteúdo.** A verificação de presença acusa 2 dos 3 erros e
   aprova o ativo trocado, devolvendo a origem do número. Isso ensina o que o código confere e o
   que continua exigindo leitura humana.
5. **Frontend sem cor literal.** O `main.jsx` importa `assets/css/inteli-brand.css`, e o
   `vite.config.js` libera a leitura até a raiz do acervo, para o `tools/check_brand.py` continuar
   valendo dentro de `exemplos/`.

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| A suíte do acervo passa a depender de `fastapi`, `httpx` e `scipy`, que não estão em `requirements-ci.txt` | os testes da Aula 06 usam `pytest.importorskip`; acrescentar os três pacotes ao `requirements-ci.txt` para o CI medir de fato |
| Os testes do frontend dependem de `node` | `node --test` sem dependência; o teste é pulado quando o `node` não existe, e o runner do GitHub tem `node` |
| O `.gitignore` do acervo ignora `.env.*`, o que também ignora os `.env.example` do exemplo | acrescentar `!.env.example` ao `.gitignore`; `tools/tests/test_exemplo_aula06.py` confere que o arquivo existe com a chave vazia |
| `npm install` cria `node_modules/` dentro de `exemplos/` | acrescentar `node_modules/` e `dist/` ao `.gitignore` |
| Contagem de problemas pode ser lida como tempo exato | a animação e o material dizem "problemas de otimização resolvidos", nunca segundos |

## Consequências

**Positivas**

- Deck, material, notebook, widgets e animações citam números que a API de exemplo devolve hoje,
  travados em teste.
- O exemplo tem 16 testes de backend e 8 de frontend, rodados pela suíte do acervo.
- O exercício do Bloco 6 é reprodutível e tem gabarito fixo.

**Negativas**

- A suíte do acervo fica mais lenta: o backend do exemplo roda em subprocesso.
- O tempo real de resposta com e sem cache não aparece em nenhum artefato.

## ADRs relacionadas

- ADR-003, os dados versionados de onde a API lê.
- ADR-005, o contrato das animações e dos widgets.
- ADR-007, que pôs React, FastAPI e LLM na Aula 06 e no A5.
