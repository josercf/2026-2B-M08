# Kit do simulador de carteiras (Aula 04)

A dupla usa este kit nos turnos 3, 4 e 5 da aula. Os turnos 1 e 2 vêm do notebook do Colab.

O que a dupla entrega ao fim da aula: esta pasta dentro do repositório do grupo, com
`python conferir.py` imprimindo `OK` nos turnos concluídos, o `SPEC.md` dos turnos 4 e 5
preenchido e os testes `test_da_dupla_*` escritos.

## Conteúdo

| Arquivo | Para que serve | Quem edita |
|---|---|---|
| `SPEC.md` | especificação dos cinco turnos | a dupla preenche os turnos 4 e 5 |
| `simulador.py` | as cinco funções do simulador | a dupla (turnos 1 e 2) e o agente (turnos 3 a 5) |
| `tests/test_turno1.py` a `test_turno5.py` | um teste de exemplo e um teste da dupla por turno | a dupla escreve o assert do teste dela |
| `conferir.py` | teste de aceite do professor | ninguém |
| `checar_ambiente.py` | confere Python e pacotes | ninguém |
| `dados/precos.csv`, `dados/rf.txt` | cotações até 13/11/2026 e taxa livre de risco anual | ninguém |
| `AGENTS.md`, `CLAUDE.md` | instruções que o Codex e o Claude Code leem sozinhos | ninguém |
| `docs/adrs/` | duas ADRs de exemplo do professor | ninguém |

## Preparação (uma vez, no início do bloco 4)

1. Copie a pasta `aula04-simulador` para dentro do repositório do grupo.
2. Abra um terminal dentro da pasta e rode:

   ```
   python checar_ambiente.py
   ```

   Se a resposta for `AMBIENTE: OK`, siga. Se faltar pacote, rode o comando que a mensagem
   mostra. Se o problema continuar, junte-se a outra dupla do seu grupo.
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

## Comandos

| Comando | O que faz |
|---|---|
| `python checar_ambiente.py` | confere Python 3.10 ou mais novo, NumPy, pandas, matplotlib e pytest |
| `python -m pytest tests -q` | roda os testes de todos os turnos |
| `python -m pytest tests/test_turno3.py -q` | roda os testes de um turno |
| `python conferir.py 3` | teste de aceite do professor para um turno |
| `python conferir.py` | teste de aceite dos cinco turnos |

O kit não acessa a rede. Todos os números saem de `dados/precos.csv` e `dados/rf.txt`.
