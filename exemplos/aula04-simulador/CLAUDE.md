# Instruções para o agente de codificação

Este kit é uma atividade de aula. Uma dupla de alunos de Administração constrói um simulador de
carteiras em cinco turnos e pede a você a implementação de um turno por vez. Responda sempre em
português do Brasil.

## Como trabalhar

1. Leia a seção do turno pedido em `SPEC.md` e a docstring da função em `simulador.py`.
2. Se algum campo da seção estiver em branco (Entrada, Saída, Casos de borda ou Critério de
   aceite), pare e peça à dupla para preencher. A especificação é escrita pela dupla.
3. Abra `tests/test_turno<N>.py`. O teste `test_da_dupla_*` é escrito à mão pela dupla. Se ele
   ainda termina com `assert False, "escreva o assert deste teste e apague esta linha"`, pare e
   peça à dupla para escrever o assert. Não escreva esse assert por ela.
4. Implemente em `simulador.py` apenas a função do turno pedido. Não implemente turnos
   seguintes, mesmo que pareça simples.
5. Rode `python -m pytest tests -q` e `python conferir.py <N>`.
6. O turno termina quando `python conferir.py <N>` imprime `TURNO <N>: OK` e os testes de
   `tests/test_turno<N>.py` e dos turnos anteriores passam. Falha em teste de turno seguinte é
   esperada, porque a função dele ainda não existe.
7. Pare e escreva um resumo de três linhas para a dupla ler: o que a função faz, qual caso de
   borda foi tratado e o resultado dos dois comandos.

## Regras

- Nunca edite `conferir.py`. Ele é o teste de aceite do professor.
- Nunca apague, pule, comente ou enfraqueça um teste de `tests/`. Se um teste parecer errado,
  explique o motivo à dupla e espere a decisão dela.
- Não altere a pasta `dados/` e não baixe dados. O kit funciona sem rede, só com
  `dados/precos.csv` e `dados/rf.txt`.
- Não mude a assinatura das funções de `simulador.py`.
- Use apenas a biblioteca padrão, NumPy, pandas e matplotlib. Não instale pacote novo.
- Não descomente as soluções de reserva dos turnos 1 e 2 em `simulador.py`. Só a dupla faz
  isso, e só com a liberação do professor.
- Escreva comentários, docstrings e mensagens de erro em português do Brasil, com acentuação.
