# ADR-002: A4 com FastAPI e A5 só com LLM

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A trilha de Computação do módulo foi revisada em junho de 2026 no `REVISAO-LBL08-COMPUTACAO.md`
(16/06/2026), que vive na pasta de trabalho do módulo, fora deste repositório. Naquela versão, o
A4 da Sprint 4 era "Otimizador de Carteira com Fronteira Eficiente", o A5 da Sprint 5 era
"Simulador Interativo com Streamlit e Interpretação por LLM", a instrução da semana 8 ensinava
validação e robustez do modelo, a instrução da semana 9 ensinava o simulador em Streamlit com LLM
e a Ponderada 2 estava na semana 8.

Em 17/09/2026 o professor decidiu cinco mudanças, registradas no design (seção 1) e detalhadas em
`docs/revisao-planilha-2026-09-17.md`, seção 1. As três primeiras afetam as entregas avaliadas e as
duas últimas instruções, e ficam registradas nesta ADR; as outras duas estão nas ADRs 004 e 005. A
planilha e a Adalove ainda não foram atualizadas, e o texto pronto para lançar está em
`docs/revisao-planilha-2026-09-17.md`.

## Decisão

O A4 entrega o otimizador numa aplicação FastAPI com página HTML/JS, o A5 fica só com a
interpretação por LLM, as instruções 5 e 6 trocam de conteúdo e a Ponderada 2 vai para a semana 9.

## Motivações

1. **O gestor do parceiro opera o otimizador sem programar.** A pergunta do case da Aula 05 é
   como um gestor do parceiro, que não programa, opera o otimizador (design, seção 9). Subir a
   parte web para a Sprint 4 coloca a entrega avaliada no formato em que a decisão de alocação
   acontece.
2. **A chave do LLM fica no backend.** O conteúdo da Aula 05 fecha com segredo nunca no
   JavaScript do navegador, e o da Aula 06 trata a chave da OpenRouter em variável de ambiente,
   fora do git (design, seção 9). Uma aplicação com servidor próprio é o que permite ensinar isso;
   uma página estática que chamasse o provedor direto exporia a chave.
3. **FastAPI no lugar do Streamlit.** Com FastAPI e uma página HTML/JS, a turma aprende cliente e
   servidor, HTTP, JSON, validação de entrada e documentação automática, e a API importa os
   módulos dos artefatos anteriores sem copiar código (design, seção 9). O Streamlit sai do
   módulo.
4. **A ordem das instruções passa a seguir a ordem das entregas.** Com o A4 na semana 8, a
   instrução da semana 8 precisa ensinar a parte web. Validação, robustez e interpretação por LLM
   descem juntas para a semana 9, onde alimentam o A5 e a Ponderada 2 ao mesmo tempo.
5. **A Ponderada 2 acompanha o conteúdo que ela cobra.** O enunciado pergunta se a carteira ótima
   sobrevive fora da amostra, que é o conteúdo da parte 1 da instrução da semana 9.

## O que muda nas entregas

| Item | Antes (REVISAO de 16/06/2026) | Depois (17/09/2026) |
|---|---|---|
| A4 (Sprint 4) | Otimizador de Carteira com Fronteira Eficiente | Otimizador de Carteira com Fronteira Eficiente em Aplicação Web |
| A5 (Sprint 5) | Simulador Interativo com Streamlit e Interpretação por LLM | Interpretação da Carteira por LLM |
| Instrução 5 (semana 8) | validação e robustez do modelo | Do Script ao Produto: API em FastAPI e Página Web |
| Instrução 6 (semana 9) | simulador em Streamlit com interpretação por LLM | Validação, Robustez e Interpretação com LLM |
| Ponderada 2 (3 pontos) | semana 8 | semana 9 |

Os pesos citados do REVISAO seguem marcados "a confirmar na Adalove" (P2 do
`PLANO_DE_ENSINO.md`).

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| O A4 vence na mesma semana da instrução que ensina a parte web, e a folga real depende do dia da aula dentro da semana 8, ainda não lido (P6 e P3 do `PLANO_DE_ENSINO.md`) | pendência aberta com a coordenação; o `exemplos/api-carteira/` entra pronto e parcial, com endpoint de métricas para pesos dados, para o grupo estender em vez de começar do zero |
| A semana 8 concentra HTTP, FastAPI e HTML/JS em 105 minutos (design, seção 16) | os dois autoestudos da semana carregam HTTP, JSON e `fetch` antes do encontro (50 e 70 minutos, `docs/autoestudos-por-semana.md`), e o encontro fica com a integração; a sala invertida da ADR-004 é a mitigação estrutural dessa densidade |
| O `Case-Creditos-OpenRouter-M08-AdmTech.docx` (02/09/2026), já aprovado, cita Streamlit e a instrução 6 antiga (P7 do `PLANO_DE_ENSINO.md`) | atualizar o case com FastAPI e a instrução 6 nova antes da Sprint 5; o acervo não altera o documento aprovado por conta própria |
| Planilha e Adalove seguem com os títulos de junho até o lançamento | `docs/revisao-planilha-2026-09-17.md` traz título, descrição, autoestudos e as colunas E, F e G de A4 e A5 no formato das abas, prontos para lançar |
| O A5 perdeu o simulador interativo próprio e pode parecer uma entrega pequena para uma sprint | o barema segue com 65% na ferramenta, 15% em especificação e documentação e 20% nos ADRs, e a ferramenta do A5 passa a ser um endpoint de interpretação na aplicação da Sprint 4, com verificação automática de todo número citado pelo modelo, comparação de dois modelos em custo e painel na página, escopo descrito em `docs/revisao-planilha-2026-09-17.md`, seção 7 |

## Consequências

**Positivas**

- O arco das cinco sprints termina em decisão assistida, com o produto web entregue uma sprint
  antes do fecho.
- A Aula 06 fica com um único fio condutor, que é desconfiar do resultado do otimizador e depois
  explicá-lo sem inventar número.
- A Ponderada 2 passa a vencer na semana em que o conteúdo dela é ensinado.
- O exemplo da Aula 05 pode ser propositalmente parcial, porque o otimizador e a fronteira são o
  núcleo avaliado do A4 (design, seção 3).

**Negativas**

- A semana 8 ficou sendo a mais densa do módulo, com a mitigação registrada acima.
- Quatro documentos de origem ficam divergentes até o lançamento: a planilha, a Adalove, o REVISAO
  de junho e o case de créditos da OpenRouter.
- A turma precisa de HTML e JavaScript mínimos, conteúdo que o módulo não previa antes desta
  decisão, e isso entrou como carga de autoestudo na semana 8.

## ADRs relacionadas

- ADR-004, que é a mitigação estrutural da densidade da semana 8.
- ADR-006, que fixa a numeração `aula01` a `aula06` usada na tabela de troca das instruções.
