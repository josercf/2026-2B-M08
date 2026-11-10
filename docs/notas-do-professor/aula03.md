# Notas do professor: Aula 03

Do Excel ao Python: funções, gráficos e testes. 10/11/2026 (terça), 14h, Semana 5, Sprint 3,
aula 22 do módulo. Redesenhada em 10/11/2026 (ADR-017). A versão de 13/10/2026, sobre
correlação, covariância e Ledoit-Wolf, está em `aulas/aula03-v1.html` e `docs/notas-do-professor/aula03-v1.md`.

Este arquivo é público. Enunciado, carteiras, gabarito e corretor da Ponderada 1 ficam fora do git.

## Ordem dos slides

| Slides | Horário | O que fazer |
|---|---|---|
| 1 a 3 | 14h00 | capa, agenda e daily com cronômetro de 15 min |
| 4 | 14h15 | planilha desenhada: uma pergunta socrática por vez, duas ou três respostas da sala antes de revelar a próxima |
| 5 | | a aba de correlação e os cinco limites, revelados um a um e ligados às respostas da sala |
| 6 | | a sala propõe a linha de pandas antes de cada revelação |
| 7 | | M1 (3 min): o CSV no Sheets, coluna N, fórmula em Q3, linha 1699 |
| 8 | | a célula vazia passo a passo, com a pergunta para a sala no passo 5 antes da ADR-009 |
| 9 | | os três testes de unidade passo a passo; no notebook, trocar `ffill()` por `fillna(0)` reprova dois |
| 10 a 13 | 14h25 | anatomia da função (código passo a passo); M2 (5 min); M3 (6 min); a tabela das retiradas |
| 14 a 16 | 14h37 | heatmap da cesta, móvel BOVA11 e dólar sobre preços e retornos, M4 (5 min) |
| 17 a 19 | 14h45 | os asserts passo a passo, M5 (5 min), a tabela da caça ao bug e a ligação com `entregar()` |
| 20 a 22 | 14h55 | preparação, o que o aluno faz e entrega, dúvidas com o GitLab aberto (5 min) |
| 23 | 15h00 | cronômetro de 60 min da prova, com aviso aos 50 |

Respostas do slide 4: 105 fórmulas (15 x 14 / 2); o BOVA11 ficou sem cotação em 24/10/2025 e a
fórmula leu a célula vazia como zero, sem aviso; trocar a janela exige reescrever os intervalos;
nada na planilha garante que a referência foi arrastada certo.

## Respostas das perguntas dos microexercícios

- M1: a planilha mostra -100% em 24/10/2025 e `#DIV/0!` em 27/10; com o -100% na conta, a
  volatilidade anual do BOVA11 vai a 43,26%. Pela ADR-009, 23,41%.
- M2: com correlação -1, o risco zera com 40% no ativo de 30% (0,4 × 30% = 0,6 × 20%).
- M3: a retirada que mais reduz o risco é a da BBDC4 (18,82% para 18,37%); a que mais aumenta é a
  do IVVB11 (21,03%).
- M4: a linha dos retornos responde se o dólar protege a carteira. Sobre os preços, a correlação
  é 0,26 no período inteiro; sobre os retornos, -0,36.
- M5: `vol_b` (365 dias, 47,24%) reprova só na razão; `vol_c` (sem raiz, 623,12%) reprova nas
  duas. O 47,24% é o que passaria despercebido numa planilha.

## Antes de entrar na sala

- Conferir que os 23 arquivos da ponderada estão no repositório `t19/ponderada` do GitLab.
- Abrir o `aula03.ipynb` no Colab uma vez para confirmar que a carga dos dados responde.
- Plano B se o GitLab falhar: distribuir os arquivos pelo Slack, um por aluno.
