# ADR-007: Ordem do REVISAO de 13/10 com React no A5

**Data:** 13/10/2026
**Status:** Aceita. Substitui a ADR-002.
**Decisores:** Prof. José Romualdo

## Contexto

A ADR-002 (17/09/2026) trocou o conteúdo das instruções 5 e 6: a semana 8 passaria a ensinar
FastAPI com página HTML/JS para o A4, e a semana 9 juntaria validação, robustez e interpretação
por LLM, com a Ponderada 2. Essa troca nunca foi lançada na planilha nem na Adalove.

Em 13/10/2026, véspera do início do módulo, o `REVISAO-LBL08-COMPUTACAO.md` foi revisado pelo
professor. A versão revisada mantém a ordem de junho (validação e robustez na semana 8, produto na
semana 9) e troca o Streamlit por uma aplicação em duas camadas: FastAPI no backend e React (Vite)
no frontend, com a chamada ao LLM feita no servidor. O professor confirmou em 13/10/2026 que vale
a ordem do REVISAO revisado.

## Decisão

As instruções 5 e 6 seguem o REVISAO de 13/10/2026: semana 8 com Validação e Robustez do Modelo e
a Ponderada 2, semana 9 com React, FastAPI e interpretação por LLM, alimentando o A5.

## Motivações

1. **Uma única fonte.** O REVISAO é o documento que vai para a planilha e para a Adalove. Manter o
   acervo com a ordem da ADR-002 deixaria o portal e os decks divergentes do que a turma lê na
   Adalove.
2. **O A4 volta a ser o otimizador.** Sem a parte web, a Sprint 4 concentra o núcleo matemático
   (variância mínima, máximo Sharpe, fronteira de 50 pontos) e a aula da semana 8 ensina a
   desconfiar dele antes da entrega, que é o que o A4 pede na observação sobre pesos instáveis.
3. **React e FastAPI no fim.** A reunião de checkpoint de 19/08/2026 registrou o protótipo em Figma
   na semana 6, o início da codificação da interface na semana 8 e o simulador integrado com
   interpretação por LLM como entrega final; a ordem do REVISAO acompanha esse calendário.
4. **A chave do LLM continua no servidor.** O motivo técnico da ADR-002 para ter backend próprio
   segue valendo: a aplicação do A5 tem FastAPI, e a chave fica em variável de ambiente no backend.

## O que muda no acervo

| Item | ADR-002 (17/09/2026) | Esta ADR (13/10/2026) |
|---|---|---|
| Aula 05 (semana 8) | Do Script ao Produto: API em FastAPI e Página Web | Validação e Robustez do Modelo |
| Aula 06 (semana 9) | Validação, Robustez e Interpretação com LLM | Do Script ao Produto: React, FastAPI e Interpretação com LLM |
| A4 (Sprint 4) | Otimizador de Carteira com Fronteira Eficiente em Aplicação Web | Otimizador de Carteira com Fronteira Eficiente |
| A5 (Sprint 5) | Interpretação da Carteira por LLM | Simulador Interativo em React com API Python e Interpretação por LLM |
| Ponderada 2 | semana 9 | semana 8 |
| Autoestudos da semana 8 | HTTP e JSON; Primeira API com FastAPI | Os limites do otimizador; Ponderada 2 |
| Autoestudos da semana 9 | Os limites do otimizador e do LLM; Ponderada 2 | React e FastAPI; LLMs com senso crítico |

Arquivos atualizados: `PLANO_DE_ENSINO.md`, `PLANEJAMENTO_AULA_A_AULA.md` (Aulas 05 e 06),
`docs/autoestudos-por-semana.md`, `index.html`, `README.md` e `tools/tests/test_planejamento.py`.

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| A semana 9 concentra FastAPI, React e LLM em 105 minutos, e a turma não teve React no módulo | o autoestudo 6.1 pede as duas pontas funcionando em separado antes do encontro, e a aula fica com a ligação entre elas; o exemplo do acervo entra pronto e parcial |
| O A5 vence logo depois da única aula de React e FastAPI | o contrato da API no SPEC.md, exigido pelo barema do A5, deixa front e back trabalharem em paralelo desde o início da Sprint 5 |
| O `Case-Creditos-OpenRouter-M08-AdmTech.docx` ainda cita Streamlit (P7) | atualizar o case para React e FastAPI antes da Sprint 5 |
| O texto da pendência P6 foi escrito para a ordem da ADR-002 | a P6 continua aberta: o A4 e a Ponderada 2 vencem perto da Aula 05, e a folga depende do dia da aula na semana 8 (P3) |

## Consequências

**Positivas**

- Portal, planejamento, autoestudos e REVISAO passam a contar a mesma ordem.
- A Ponderada 2 vence na semana em que o teste fora da amostra é ensinado.
- O A4 fica com o otimizador, sem dividir a sprint com a primeira experiência web da turma.

**Negativas**

- O `docs/revisao-planilha-2026-09-17.md` deixa de valer para as semanas 8 e 9 e fica como
  histórico.
- A semana 9 vira a mais densa do módulo.

## ADRs relacionadas

- ADR-002, substituída por esta.
- ADR-004, a sala invertida que carrega React e FastAPI para o autoestudo da semana 9.
- ADR-006, a numeração `aula01` a `aula06`.
