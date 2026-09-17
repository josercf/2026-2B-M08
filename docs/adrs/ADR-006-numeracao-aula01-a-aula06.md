# ADR-006: numeração de aula01 a aula06

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

O módulo tem 10 semanas e aulas de várias disciplinas. A aba "Organização de Aula" da planilha
"Revisão LBL 8 AdmTech - 2026-2B" numera as aulas do módulo inteiro, e as seis instruções de
Computação caem nos números 5, 13, 22, 28, 38 e 43, citados do `REVISAO-LBL08-COMPUTACAO.md`
(16/06/2026). As seis instruções ficam nas semanas 1, 3, 5, 6, 8 e 9 do módulo.

O acervo precisa de um nome de arquivo por aula para o deck, o material, as referências, o
notebook, as notas do professor, as animações, os widgets e os scripts de medição. Usar a
numeração da planilha daria `aula05`, `aula13`, `aula22`, `aula28`, `aula38` e `aula43`, com cinco
buracos grandes e sem dizer qual é a primeira instrução de Computação. Usar só a numeração do
acervo, sem mostrar a da planilha, criaria ambiguidade quando o professor, a coordenação e o aluno
falarem da mesma aula olhando fontes diferentes.

## Decisão

Os arquivos das instruções de Computação se chamam `aula01` a `aula06`, na ordem em que acontecem.

## Motivações

1. **Sequência sem buraco.** A numeração `aula01` a `aula06` é contígua, o que torna previsível o
   nome de todo artefato derivado: `aulas/aula01.html`, `materiais/aula01.html`,
   `referencias/aula01.html`, `notebooks/aula01.ipynb`, `docs/notas-do-professor/aula01.md`,
   `tools/animacoes_aula01.py`, `tools/dados_widgets_aula01.py` e os JSON de
   `assets/data/aula01-*.json`.
2. **A ordem do arquivo é a ordem da espiral.** Cada aula abre resgatando o que a anterior deixou
   pronto (`inteli-course-design`, seção 3), e a sequência do nome é a sequência do resgate.
3. **A numeração da planilha continua visível.** O portal mostra os dois números, e o
   `PLANO_DE_ENSINO.md`, seção 4, tem a coluna "Aula do módulo" com 5, 13, 22, 28, 38 e 43 ao lado
   da coluna "Acervo". A `docs/revisao-planilha-2026-09-17.md` usa os números da planilha nos
   campos que vão ser lançados, porque é o que a aba espera.
4. **Os validadores dependem do padrão.** O `tools/check_widgets.py` descobre os decks por
   `aulas/aula*.html`, e o mesmo padrão vale para o hook e para os testes.

## Correspondência entre as duas numerações

| Acervo | Semana | Aula do módulo na planilha | Sprint |
|---|---|---|---|
| aula01 | 1 | 5 | 1 |
| aula02 | 3 | 13 | 2 |
| aula03 | 5 | 22 | 3 |
| aula04 | 6 | 28 | 3 |
| aula05 | 8 | 38 | 4 |
| aula06 | 9 | 43 | 5 |

A coluna "Aula do módulo" é citada do `REVISAO-LBL08-COMPUTACAO.md` e fica marcada "a confirmar"
enquanto a planilha não for lida com sessão autenticada (P2 do `PLANO_DE_ENSINO.md`).

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Duas numerações para a mesma aula confundem professor, coordenação e aluno | o portal, o plano de ensino e o roteiro aula a aula mostram os dois números lado a lado, sempre na mesma ordem |
| A planilha pode mudar a numeração do módulo quando for lida (P2) | a numeração do acervo não depende dela; só a coluna "Aula do módulo" precisa de atualização, em três arquivos de planejamento |
| Uma instrução de Computação pode ser acrescentada ou remanejada de semana | a sequência do acervo é renumerada por ordem de ocorrência, e o registro desta ADR diz o que isso implica em nome de arquivo |
| Referência cruzada errada entre aulas passa despercebida | `tools/check_links.py` reprova link local que não resolve, e `tools/tests/test_planejamento.py` confere as seis aulas com título exato |

## Consequências

**Positivas**

- Todo artefato de uma aula tem nome derivável do número dela, o que os agentes e os validadores
  assumem.
- A leitura do repositório dá a ordem das instruções de Computação sem precisar da planilha.
- O aluno encontra a aula pelo número do acervo no portal e pelo número do módulo na Adalove.

**Negativas**

- O acervo carrega duas numerações para a mesma aula, e todo documento de planejamento precisa
  manter as duas.
- Quem vem da planilha precisa traduzir o número antes de achar o arquivo.

## ADRs relacionadas

- ADR-002, que trocou o conteúdo das instruções 5 e 6 sem mudar a numeração dos arquivos.
- ADR-004, cujos três tempos são descritos por aula usando esta numeração.
