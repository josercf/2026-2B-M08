# ADR-001: base do M03 com componentes da Formação GitLab

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

O acervo de Computação do Módulo 08 AdmTech precisa de tema de deck, tokens de marca, CSS de
impressão, validadores e suíte de teste desde o primeiro dia, para que a Aula 01 seja construída
sobre uma base já verificada. Escrever esse conjunto do zero repetiria as armadilhas de layout já
corrigidas em acervos anteriores e documentadas na skill `inteli-deck-design`, seção 8.

Dois acervos do professor têm partes do conjunto, e nenhum dos dois tem o conjunto completo
(design, seção 12):

| Acervo | O que existe apenas nele |
|---|---|
| `canaldoovidio/2026-2A-M03` | correções de 04/09 e 08/09/2026 (título sobre a marca no PDF, lista longa de referências) e a tradução do link do notebook no validador de links |
| `josercf/treinamento-gitlab` (Formação GitLab) | `inteli-cronometro.js`, `inteli-escolha.js`, os blocos de tema e de impressão que estilizam os dois, e a versão do portal com o contraste corrigido |

## Decisão

O acervo parte da base do M03 e incorpora o cronômetro e a escolha da Formação GitLab.

## Motivações

1. O M03 é o acervo com as correções mais recentes de layout, de impressão e de validação de link
   (design, seção 12), e as correções de 04/09 e 08/09/2026 valem igual aqui, porque o tema e o
   CSS de impressão são os mesmos.
2. A Formação GitLab tem os dois componentes que sustentam três das cinco técnicas de metodologia
   ativa da seção 6 do design: o cronômetro visível em "pensar, discutir em dupla, compartilhar" e
   na programação em dupla, e a escolha coletiva de vários itens num mesmo slide. O M03 não tem
   nenhum dos dois.
3. A versão da Formação GitLab do `inteli-portal.css` substitui `--seg-texto-suave`, que mede
   2,03:1 de contraste sobre o branco de `--seg-base`, por `--seg-texto` em três pontos do portal,
   acima do mínimo da WCAG.
4. O `inteli-print.js` da Formação GitLab revela na impressão o gabarito das `.escolha` e dos
   quizzes; a versão do M03 revela apenas o dos quizzes.

## Registro da cópia, arquivo por arquivo

Esta seção também é o registro de um ajuste de escopo. O `assets/js/inteli-print.js` e o
`assets/css/inteli-portal.css` foram copiados do M03 na primeira etapa da fundação, porque o
`aulas/_fixture-tema.html` referencia o script de impressão e o `tools/check_links.py` reprova
referência a arquivo ausente. Na etapa seguinte, os dois foram substituídos pelas versões da
Formação GitLab. A origem final dos dois é a Formação GitLab.

| Arquivo | Origem final | Observação |
|---|---|---|
| `assets/css/inteli-brand.css` | M03 | tokens de cor e tipografia, idêntico |
| `assets/css/inteli-material.css` | M03 | estilo das páginas de leitura, idêntico |
| `assets/css/inteli-print.css` | M03 | idêntico |
| `assets/css/inteli-theme.css` | M03 mais Formação GitLab | base do M03, com o bloco de cronômetro e escolha anexado da Formação GitLab e, depois, o bloco de widget e vídeo escrito neste acervo |
| `assets/css/inteli-portal.css` | Formação GitLab | copiado do M03 primeiro, substituído depois pela versão com o contraste corrigido; o comentário teve o valor medido acertado de 2,04:1 para 2,03:1 |
| `assets/img/inteli-logo-positiva.svg`, `inteli-logo-negativa.svg`, `inteli-logo-mono.svg`, `inteli-grafismo-graduacao.svg` | M03 | marca e grafismo, idênticos |
| `assets/js/inteli-quiz.js` | M03 | idêntico |
| `assets/js/inteli-zoom.js` | M03 | idêntico |
| `assets/js/inteli-print.js` | Formação GitLab | copiado do M03 primeiro, substituído depois pela versão que revela também o gabarito da escolha |
| `assets/js/inteli-cronometro.js` | Formação GitLab | novo no acervo |
| `assets/js/inteli-escolha.js` | Formação GitLab | novo no acervo |
| `aulas/_fixture-tema.html` | M03 | adaptado: "Módulo 03 IN" virou "Módulo 08 AdmTech" em cinco pontos, e o fixture ganhou os slides de cronômetro, escolha e widget deste acervo |
| `tools/check_brand.py` | M03 | adaptado: `.venv` acrescentado a `IGNORAR` |
| `tools/check_links.py` | M03 | adaptado: `REPO_BLOB` para `https://github.com/josercf/2026-2B-M08/blob/main/` e `.claude` e `.venv` acrescentados a `IGNORAR` |
| `tools/check_slides.py` | M03 | copiado idêntico e, depois, com o servidor local passado a `ThreadingTCPServer` (ADR-005) |
| `pytest.ini` | M03 | idêntico |
| `tools/tests/__init__.py`, `test_assets_marca.py`, `test_check_brand.py`, `test_check_links.py`, `test_check_slides.py`, `fixture_layout.html`, `fixture_sem_slides.html` | M03 | idênticos |

Os demais arquivos de `tools/` e de `tools/tests/` foram escritos neste acervo.

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Correção feita no M03 depois de 17/09/2026 não chega sozinha a este acervo | a tabela acima nomeia a origem de cada arquivo, o que permite comparar com `diff` contra o M03 e portar a correção deliberadamente |
| Fundir o CSS de dois temas pode deixar uma classe de estado perdendo a guerra de especificidade, mudando o DOM sem mudar a tela | `tools/tests/test_componentes_ativos.py` mede `getComputedStyle` depois do clique; a mutação que rebaixa a especificidade de `.escolha-opcoes li.revelada` foi vista reprovando esse teste |
| Uma cópia futura a partir do M03 pode sobrescrever os dois arquivos cuja origem final é a Formação GitLab | nenhum teste trava hoje o conteúdo de `inteli-print.js` e de `inteli-portal.css`; a verificação é manual e o registro é esta ADR |
| O tema herdado carrega as armadilhas de layout do acervo de origem | as seis armadilhas herdadas estão listadas no `CLAUDE.md` deste repositório, com a causa raiz de cada uma na skill `inteli-deck-design`, seção 8 |

## Consequências

**Positivas**

- Os validadores de marca, de layout e de link chegaram acompanhados da suíte de teste deles, que
  passou na primeira etapa da fundação, antes de qualquer conteúdo do M08 ser escrito.
- As cinco técnicas de metodologia ativa da seção 6 do design têm componente de deck desde o
  começo, sem etapa de implementação de componente dentro da construção da Aula 01.
- A fidelidade à marca continua conferida por `tools/check_brand.py` com os mesmos tokens do M03,
  que a skill `inteli-deck-design` documenta.

**Negativas**

- O acervo tem duas origens para o mesmo arquivo em dois casos, o que exige o registro acima para
  não regredir.
- O `assets/css/inteli-theme.css` cresceu por anexação de blocos de duas origens, com o risco de
  especificidade que a tabela de riscos trata.
- Correções futuras dos acervos de origem não se propagam automaticamente, e cada porte é uma
  decisão manual.

## ADRs relacionadas

- ADR-004, que depende do cronômetro e da escolha para sustentar as técnicas dos três tempos.
- ADR-005, cujos widgets e animações leem as cores dos tokens herdados do M03 e cujo validador
  reaproveita o servidor local do `tools/check_slides.py`.
