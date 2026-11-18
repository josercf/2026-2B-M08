# Kit do simulador de carteiras (Aula 04)

A dupla usa este kit nos turnos 3, 4 e 5 da aula. Os turnos 1 e 2 vêm do notebook do Colab. O
turno 6, a otimização de Markowitz, é feito depois do encontro e está descrito no fim deste
arquivo.

O que a dupla entrega ao fim da aula: esta pasta dentro do repositório do grupo, com
`python conferir.py` imprimindo `OK` nos turnos concluídos, o `SPEC.md` dos turnos 4 e 5
preenchido e os testes `test_da_dupla_*` escritos.

## Conteúdo

| Arquivo | Para que serve | Quem edita |
|---|---|---|
| `SPEC.md` | especificação dos seis turnos | a dupla preenche os turnos 4 e 5 |
| `simulador.py` | as funções do simulador | a dupla (turnos 1 e 2) e o agente (turnos 3 a 6) |
| `tests/test_turno1.py` a `test_turno6.py` | um teste de exemplo e um teste da dupla por turno | a dupla escreve o assert do teste dela |
| `conferir.py` | teste de aceite do professor | ninguém |
| `checar_ambiente.py` | confere Python e pacotes | ninguém |
| `dados/precos.csv`, `dados/rf.txt` | cotações até 13/11/2026 e taxa livre de risco anual | ninguém |
| `AGENTS.md`, `CLAUDE.md` | instruções que o Codex e o Claude Code leem sozinhos | ninguém |
| `docs/adrs/` | três ADRs de exemplo do professor | ninguém |

## Preparação (uma vez, no início do bloco 4)

1. Copie a pasta `aula04-simulador` para dentro do repositório do grupo.
2. Abra um terminal dentro da pasta e rode:

   ```
   python checar_ambiente.py
   ```

   Se a resposta começar com `AMBIENTE: OK`, siga. Se faltar pacote, rode o comando que a
   mensagem mostra. O SciPy só é usado no turno 6: sem ele, a resposta é
   `AMBIENTE: OK para os turnos 1 a 5`, e a instalação pode ficar para depois do encontro. Se o problema continuar, junte-se a outra dupla do seu grupo.
3. Abra `simulador.py`. Cole a função `retorno_do_dia` escrita no Colab no lugar da
   `retorno_do_dia` vazia, e a `metricas` do Colab no lugar da `metricas` vazia. As duas estão
   no arquivo `simulador.py` que o notebook gravou.
4. Rode:

   ```
   python conferir.py 1
   python conferir.py 2
   ```

   As duas respostas precisam ser `OK`. Se a dupla não fechou esses turnos no Colab, avise o
   professor: o `simulador.py` do kit traz uma solução de reserva comentada, que só é
   descomentada com a liberação dele.

## Roteiro de um turno com o agente (turnos 3, 4 e 5)

1. **Ler a spec.** Abra o `SPEC.md` na seção do turno. No turno 3 a seção está pronta. Nos
   turnos 4 e 5, preencha os quatro campos em branco com o que a dupla escreveu na tela de spec.
2. **Escrever o teste.** Abra `tests/test_turno<N>.py`, leia o comentário `ESCREVA AQUI` do teste
   `test_da_dupla_*`, escreva o assert à mão e apague a linha `assert False`.
3. **Ver falhar.** Rode `python -m pytest tests/test_turno<N>.py -q`. Os dois testes falham,
   porque a função ainda levanta `NotImplementedError`.
4. **Pedir a implementação.** Abra o Claude Code ou o Codex dentro desta pasta e faça o pedido.
   Exemplo para o turno 3:

   ```
   Implemente o turno 3 deste kit. Leia a seção "Turno 3" do SPEC.md e siga as regras do
   AGENTS.md. Rode python -m pytest tests -q e python conferir.py 3. Pare quando o turno 3
   passar e resuma em três linhas o que você fez.
   ```

5. **Ver passar.** Rode você mesmo, no terminal:

   ```
   python -m pytest tests/test_turno<N>.py -q
   python conferir.py <N>
   ```

6. **Ler e marcar.** Leia o resumo do agente e a função que ele escreveu. Um integrante da dupla
   explica ao outro, em voz alta, o que a função faz. Depois marque o turno no placar do portal.

Se o `conferir.py` responder `AINDA NÃO`, copie a lista do que falta e entregue ao agente como
novo pedido.

## Gráfico dos turnos 4 e 5

A saída do turno 4 inclui o gráfico de risco e retorno das carteiras sorteadas, e a do turno 5
inclui a carteira da dupla marcada sobre a nuvem. O `conferir.py` não verifica imagem. Depois
que o turno passar, peça ao agente um script `grafico.py` que usa `simular` e `posicionar`,
desenha a nuvem com matplotlib e grava `nuvem.png` nesta pasta. A dupla mostra a figura ao
professor.

## Depois do encontro: turno 6, a otimização de Markowitz

O encontro termina com a demonstração da fronteira eficiente. O turno 6 é a implementação dela
pela dupla, e é a base do artefato A4 (Otimizador de Carteira com Fronteira Eficiente).

O que a dupla faz:

1. Roda `python checar_ambiente.py`. Se a linha do `scipy` vier com `FALTA`, instala com o
   comando que a mensagem mostra.
2. Lê a seção "Turno 6" do `SPEC.md`, que já vem preenchida, e a
   `docs/adrs/ADR-003-restricoes-da-otimizacao.md`.
3. Lê o bloco "Ferramentas do Python para este turno", logo abaixo, e roda os dois exemplos.
4. Abre `tests/test_turno6.py`, escreve à mão o assert do teste `test_da_dupla_*` e apaga a
   linha `assert False`.
5. Roda `python -m pytest tests/test_turno6.py -q` e vê os dois testes falharem.
6. Pede a implementação ao agente. Exemplo de pedido:

   ```
   Implemente o turno 6 deste kit: variancia_minima, maximo_sharpe e fronteira. Leia a seção
   "Turno 6" do SPEC.md e siga as regras do AGENTS.md. Use scipy.optimize.minimize com o
   método SLSQP e confira resultado.success em cada otimização. Rode python -m pytest tests -q
   e python conferir.py 6. Pare quando o turno 6 passar e resuma em três linhas o que você
   fez, dizendo qual função objetivo cada uma das três funções minimiza.
   ```

7. Roda `python -m pytest tests/test_turno6.py -q` e `python conferir.py 6` no terminal. Se a
   resposta for `AINDA NÃO`, entrega a lista do que falta ao agente como novo pedido.
8. Lê as três funções. Um integrante explica ao outro qual é a função objetivo de cada uma,
   quais são as restrições e por que a fronteira roda uma otimização por retorno alvo.
9. Pede ao agente um script `grafico_fronteira.py` que usa `simular`, `fronteira`,
   `variancia_minima`, `maximo_sharpe` e `posicionar`, e grava `fronteira.png` com:
   - a nuvem de 10.000 carteiras do turno 4;
   - a linha da fronteira desenhada sobre a nuvem;
   - a carteira de variância mínima e a de máximo Sharpe marcadas;
   - a carteira do Solver da aula de Negócios marcada com `posicionar`, para comparar com as
     duas ótimas.

O que a dupla entrega no repositório do grupo:

- `simulador.py` com as três funções, e `python conferir.py 6` imprimindo `TURNO 6: OK`;
- `tests/test_turno6.py` com o teste da dupla escrito e passando;
- `grafico_fronteira.py` e `fronteira.png`;
- a leitura do gráfico no A4: os pesos das duas carteiras ótimas, a distância entre a carteira
  do Solver e a fronteira (em risco, para o mesmo retorno) e a diferença entre a melhor
  carteira sorteada e a carteira de máximo Sharpe.

O `conferir.py` reprova a função que devolve a melhor carteira sorteada no lugar da ótima. A
carteira ótima fica na borda da região ocupada pela nuvem do turno 4, e o sorteio raramente
chega a essa borda.

A ADR do A4 trata de uma decisão da dupla sobre a otimização: a janela dos dados, um teto de
peso por ativo ou a taxa livre de risco, por exemplo. A ADR-003 do kit é um exemplo de
estrutura.

### Ferramentas do Python para este turno

`scipy.optimize.minimize` procura os valores de um vetor que tornam uma função a menor possível.
Ela recebe:

| Argumento | O que é |
|---|---|
| função objetivo | função que recebe o vetor e devolve um número, o valor a minimizar |
| ponto inicial | vetor de onde a busca parte |
| `method="SLSQP"` | método de busca que aceita limites e restrições |
| `bounds` | lista com um par (mínimo, máximo) por posição do vetor |
| `constraints` | lista de dicionários; `{"type": "eq", "fun": f}` exige `f(vetor) == 0` |
| `options` | ajustes do método; `{"ftol": 1e-12}` faz a busca parar só bem perto do mínimo |

O exemplo abaixo trata de um problema diferente do turno: dividir 10 unidades entre três
posições, com a menor soma de quadrados possível, e com a primeira posição limitada a 2.

```python
import numpy as np
from scipy.optimize import minimize


def soma_dos_quadrados(x):
    return x[0] ** 2 + x[1] ** 2 + x[2] ** 2


inicio = np.array([10.0, 0.0, 0.0])
limites = [(0, 2), (0, 10), (0, 10)]
restricoes = [{"type": "eq", "fun": lambda x: x.sum() - 10}]

resultado = minimize(soma_dos_quadrados, inicio, method="SLSQP",
                     bounds=limites, constraints=restricoes,
                     options={"ftol": 1e-12})

print(resultado.success)
print(resultado.x.round(4))
print(round(resultado.fun, 4))
```

Saída:

```
True
[2. 4. 4.]
36.0
```

Leitura do resultado:

- `resultado.success` diz se a busca convergiu. Com `False`, `resultado.x` não tem validade e
  `resultado.message` traz o motivo.
- `resultado.x` é o vetor encontrado, e `resultado.fun` é o valor da função objetivo nele.
- Sem o limite da primeira posição, a resposta seria 10/3 em cada uma. O limite levou a
  primeira posição a 2 e a restrição de soma distribuiu o restante.
- `minimize` só minimiza. Para encontrar o maior valor de uma função, minimiza-se a função com
  o sinal trocado.
- A tolerância padrão do SLSQP (`ftol` de 0,000001) é larga para funções de valores pequenos,
  como a variância de retornos diários: a busca pode parar no ponto inicial. Por isso o
  exemplo passa `options={"ftol": 1e-12}`.

Armadilha do `lambda` dentro de laço. Um `lambda` consulta a variável do laço no momento em que
é chamado. Se as funções são criadas no laço e chamadas depois que ele termina, todas enxergam
o último valor:

```python
errado = []
certo = []
for alvo in (10, 20, 30):
    errado.append(lambda x: x - alvo)
    certo.append(lambda x, a=alvo: x - a)

print([f(0) for f in errado])
print([f(0) for f in certo])
```

Saída:

```
[-30, -30, -30]
[-10, -20, -30]
```

O argumento padrão `a=alvo` guarda o valor de `alvo` no momento em que o `lambda` é criado. Em
um laço que cria uma restrição por volta, a forma `lambda x, a=alvo: ...` funciona tanto quando
a restrição é usada na mesma volta quanto quando é guardada para depois.

## Comandos

| Comando | O que faz |
|---|---|
| `python checar_ambiente.py` | confere Python 3.10 ou mais novo, NumPy, pandas, matplotlib, pytest e SciPy (turno 6) |
| `python -m pytest tests -q` | roda os testes de todos os turnos |
| `python -m pytest tests/test_turno3.py -q` | roda os testes de um turno |
| `python conferir.py 3` | teste de aceite do professor para um turno |
| `python conferir.py 6` | teste de aceite do turno 6, depois do encontro |
| `python conferir.py` | teste de aceite dos seis turnos |

O kit não acessa a rede. Todos os números saem de `dados/precos.csv` e `dados/rf.txt`.
