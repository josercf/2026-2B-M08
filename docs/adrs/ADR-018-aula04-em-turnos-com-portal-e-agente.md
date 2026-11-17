# ADR-018: Aula 04 em turnos, com portal de simulação e agente de codificação

**Data:** 17/11/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A Aula 04 de 13/10/2026 entregava o motor de Monte Carlo pronto no notebook, e as duas práticas em
dupla consistiam em rodar células. Na reunião docente de 16/11/2026 o professor relatou que os
artefatos dos grupos chegam com nota de 9 a 10 e que, numa atividade de programação em sala, a
turma ficou muito abaixo disso. O diagnóstico dele é que os alunos de Administração não escrevem
código sem IA. Os próprios alunos pediram mais programação.

Na próxima sprint os grupos escrevem código e frontend, com agente de codificação. Em 18/11/2026 a
aula recebe de 8 a 12 visitantes de uma faculdade de Rondônia, que vêm observar a dinâmica do PBL,
e a orientação da coordenação é manter o conteúdo previsto e mostrar a dinâmica.

O desenho completo, com as abordagens consideradas, está em
`docs/superpowers/specs/2026-11-17-aula04-simulador-em-turnos-design.md`.

## Decisão

A Aula 04 passa a ser conduzida em cinco turnos, nos quais cada grupo constrói o próprio
`simulador.py` a partir de um portal de simulação que serve de valor esperado, com os turnos 1 e 2
escritos à mão no Colab e os turnos 3 a 5 implementados por agente de codificação a partir de spec
e teste escritos pelo grupo, e a otimização com SLSQP e a fronteira eficiente saem do encontro.

## Motivações

- O aluno digita nos blocos 1 e 3 a 6, em fatias pequenas que se conferem por teste.
- A parte escrita à mão é a especificação e o teste, que continuam sendo do aluno quando a
  implementação passa ao agente. Os turnos 1 e 2 garantem que a conta foi entendida antes de ser
  delegada.
- O portal mostra o produto pronto e dá o número que o teste do aluno precisa reproduzir nos
  turnos 1 e 2, com a carteira que o grupo montou na aula de Negócios.
- O resultado sai como módulo `.py` com `SPEC.md` e testes, que é o formato cobrado no barema do A3.
- O kit com agente no terminal treina o modo de trabalho da sprint seguinte.

## Riscos conhecidos e mitigações

- **Banco fora do ar ou rede lenta em sala.** O portal cai para memória, com aviso, e aceita
  `?demo=1`. O kit não baixa nada. A spec pode ser escrita direto no `SPEC.md`.
- **Ativo de grupo fora do arquivo de cotações.** O universo foi ampliado para 162 ativos, o portal
  informa a ausência e o grupo troca o ativo por outro do mesmo setor.
- **Dupla sem agente funcionando.** O verificador de ambiente roda no início do bloco 4, e a dupla
  se junta a outra do mesmo grupo. Não há contagem verificada de máquinas com agente.
- **Agente altera os testes para passar.** O `conferir.py` roda testes de aceite fora de `tests/`,
  e as instruções do agente proíbem editá-lo.
- **Número do portal diferente do número da função correta.** As duas implementações, em
  JavaScript e em Python, seguem as mesmas definições e têm teste de paridade.
- **Nome de aluno em repositório ou tabela pública.** O portal guarda iniciais e grupo, e a tela de
  spec grava o código do grupo como autor.
- **Tempo curto para cinco turnos.** Ordem de corte definida: turno 5, depois a tela de spec.
- **Números do deck anterior travados em teste.** A versão de 13/10/2026 fica em arquivos `-v1`,
  com `tools/tests/test_aula04.py` apontando para eles, como na ADR-017.

## Consequências

- Positivas: cada grupo sai com um motor próprio e testado, que é a base do A3; cada aluno escreve
  ao menos um teste e duas funções à mão; os visitantes veem alunos produzindo na maior parte do
  encontro.
- Negativas: a otimização com SLSQP, as carteiras de variância mínima e de máximo Sharpe e a
  fronteira deixam de ser trabalhadas em encontro. A Aula 05 reutiliza a função `otimizar` e o A4
  depende desse conteúdo. Pendência aberta: decidir se ele vira autoestudo com o material v1,
  abertura da Aula 05 ou encontro extra. Esta ADR não resolve.
- Negativas: a seção da Aula 05 no `PLANEJAMENTO_AULA_A_AULA.md` ainda descreve o que a Aula 04
  anterior deixava pronto, e precisa ser revista junto com a decisão acima.
- Negativas: o acervo ganha um segundo conjunto de cotações, fora de `dados/`, e a comparação
  entre uniforme normalizado e Dirichlet fica só no material v1.
- Negativas: `assets/js/inteli-adr.js` ganhou três atributos opcionais (`data-pagina` no painel
  de links, `data-rotulos` e os textos de espera na visão de projetor) para servir à tela de spec.

## ADRs relacionadas

- ADR-004 (sala de aula invertida em três tempos), ADR-005 (animações e widgets), ADR-009
  (tratamento de ausência único com janela comum), ADR-017 (Aula 03 técnica, com a versão anterior
  preservada como `-v1`).
