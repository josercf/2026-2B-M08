# Instruções para o agente de codificação

Este kit é uma atividade de aula. Uma dupla de alunos de Administração constrói um simulador de
carteiras em seis turnos e pede a você a implementação de um turno por vez. Responda sempre em
português do Brasil.

## Como trabalhar

1. Leia a seção do turno pedido em `SPEC.md` e a docstring da função em `simulador.py`.
2. Se algum campo da seção estiver em branco (Entrada, Saída, Casos de borda ou Critério de
   aceite), pare e peça à dupla para preencher. A especificação é escrita pela dupla.
3. Abra `tests/test_turno<N>.py`. O teste `test_da_dupla_*` é escrito à mão pela dupla. Se ele
   ainda termina com `assert False, "escreva o assert deste teste e apague esta linha"`, pare e
   peça à dupla para escrever o assert. Não escreva esse assert por ela.
4. Implemente em `simulador.py` apenas a função do turno pedido. Não implemente turnos
   seguintes, mesmo que pareça simples. O turno 6 tem três funções, e as três fazem parte dele.
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
- Use apenas a biblioteca padrão, NumPy, pandas e matplotlib. No turno 6, use também o SciPy
  (`scipy.optimize.minimize`). Não instale pacote novo: se o SciPy faltar, pare e mostre à dupla
  o comando que `python checar_ambiente.py` imprime.
- Não descomente as soluções de reserva dos turnos 1 e 2 em `simulador.py`. Só a dupla faz
  isso, e só com a liberação do professor.
- Escreva comentários, docstrings e mensagens de erro em português do Brasil, com acentuação.

## Turno 6: otimização de Markowitz

O turno 6 é feito depois do encontro e implementa `variancia_minima`, `maximo_sharpe` e
`fronteira`. Além das regras acima:

- As carteiras ótimas saem de `scipy.optimize.minimize` com o método SLSQP, com pesos iguais como
  ponto inicial, `bounds` de 0 a 1 em cada peso e a restrição de soma 1 em `constraints`.
- Nunca devolva a melhor carteira sorteada por `simular` como carteira ótima, nem monte a
  fronteira com carteiras sorteadas. O `conferir.py` reprova esse atalho, que é o erro que o barema
  do A3 chama de tratar a melhor carteira simulada como a carteira ótima.
- Confira `resultado.success` depois de cada chamada do `minimize`. Se a otimização não
  convergir, levante `RuntimeError` com a mensagem do otimizador. Não devolva pesos de uma
  otimização que falhou.
- Na fronteira, cada retorno alvo tem a sua restrição de igualdade. Se a restrição for criada
  com `lambda` dentro do laço, fixe o alvo em um argumento padrão do `lambda`. O `README.md`
  explica o motivo.
- O gráfico do A4 (fronteira sobre a nuvem) fica em um script separado, `grafico_fronteira.py`,
  e só é escrito quando a dupla pedir, depois que `python conferir.py 6` passar.
