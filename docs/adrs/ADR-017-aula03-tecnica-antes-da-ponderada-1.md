# ADR-017: Aula 03 técnica de 40 minutos antes da Ponderada 1 aplicada em sala

**Data:** 10/11/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A Ponderada 1 (Diagnóstico de uma carteira herdada, 3 pontos) estava planejada como autoestudo de
120 minutos. O professor decidiu aplicá-la em sala, em 60 minutos, no mesmo encontro da Aula 03,
com um notebook por aluno gerado pelo RA. Sobram 40 minutos de aula depois da daily, e a versão de
13/10/2026 da Aula 03 tinha 27 slides de correlação, covariância e Ledoit-Wolf, expositiva demais
para esse tempo.

## Decisão

A Aula 03 passa a ser uma aula técnica de 40 minutos sobre funções em Python, comparação com o
Excel, gráficos e testes, com cinco microexercícios no notebook `aula03.ipynb` que usam as
mesmas operações da Ponderada 1, e um slide de preparação separado do slide que descreve a prova.

## Motivações

- A turma de Administração já usa planilha: mostrar onde ela falha (célula vazia vira zero,
  105 fórmulas para uma matriz, erro plausível que passa sem teste) justifica cada função escrita.
- O aluno chega à prova tendo executado cada operação cobrada, sem ver nenhuma carteira da prova.
- O `assert` antecipa a ideia de validação que a `entregar()` da prova aplica às respostas.

## Riscos conhecidos

- O deck antigo tem números travados em teste. Mitigação: ele fica em `aulas/aula03-v1.html`, fora
  do portal, com os testes apontando para ele.
- O material de apoio e as referências da Aula 03 continuam os da versão de 13/10. Mitigação: o
  conteúdo de correlação segue válido como leitura; o notebook do portal passa a ser o
  `aula03.ipynb`.
- Os números do deck novo podem divergir do dado. Mitigação: saem de `tools/medidas_aula03_lab.py`
  e estão travados em `tools/tests/test_aula03_lab.py`.

- O `PLANEJAMENTO_AULA_A_AULA.md` e o `docs/autoestudos-por-semana.md` ainda descrevem a Aula 03
  em sete blocos e a Ponderada 1 como autoestudo de 120 minutos. Pendência: atualizar os dois
  com o roteiro de 40 minutos e a prova em sala, junto do teste de planejamento.
- O horário de relógio (14h às 16h) vem da agenda do professor, e a pendência P1 continua aberta
  para as demais aulas.

## Consequências

- Positivas: aula curta e prática, alinhada à prova; o aluno escreve as funções em vez de lê-las.
- Negativas: Ledoit-Wolf e correlação em crise saem do encontro; a Aula 04 parte da matriz
  calculada no M4 e no notebook da versão anterior.

## ADRs relacionadas

- ADR-009 (tratamento de ausência), ADR-016 (formato da Aula 02 redesenhada).
