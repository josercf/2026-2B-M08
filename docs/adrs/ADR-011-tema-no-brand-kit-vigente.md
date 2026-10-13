# ADR-011: Tema do acervo migrado para o inteli-brand-kit vigente

**Data:** 13/10/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

O tema foi escrito a partir da skill `inteli-deck-design`, que cita o Brandbook Inteli 2025 e pede
título em Azurio Medium (peso 500) e ícones Material Symbols Outlined por CDN. O
`inteli-brand-kit`, cuja norma é de 12/08/2026 e que vence o guia de formato quando os dois
divergem, pede outra coisa. A auditoria de 13/10/2026 (C-04 e C-05) mediu a divergência:

- 29 declarações de `border-radius` no CSS, 6 delas fazendo círculo ou pílula, mais o raio inline
  dos vídeos nos materiais. O `GRA-01` pede canto reto em todo container e proíbe círculo que
  carrega conteúdo.
- 136 ícones Outlined vindos da fonte por CDN. O `ICO-01` e o `ICO-05` pedem o SVG Sharp, peso
  400, do próprio kit.
- Título em peso 500, corpo em 400 e widgets com fonte de canvas em 400. O `TIP-04` fixa título
  700, subtítulo e label 600, corpo 300 e destaque 700.

O `check_brand.py` aprovava tudo isso porque conferia só as regras do Brandbook.

## Decisão

O tema segue o `inteli-brand-kit`: cantos retos em todo componente, ícones de um sprite Sharp
versionado em `assets/icons/icones.svg` e pesos do `TIP-04`, com o `check_brand.py` reprovando
qualquer desvio dessas três regras.

## Motivações

- A correção nos componentes-base (`inteli-theme.css`, `inteli-material.css`,
  `inteli-portal.css`) vale para os sete decks, os materiais, as referências e o portal de uma
  vez. Corrigir slide a slide geraria regressão.
- O sprite com `<use>` mantém uma cópia de cada ícone e evita colar o path em cada página.
  `tools/icones.py` reescreve as páginas e regenera o sprite a partir do kit. O sprite fica
  versionado, então o CI e o Pages não dependem do kit.
- A regra no validador, com fixture que reprova de propósito (`test_check_brand.py`), impede que
  a divergência volte.

## Riscos conhecidos e mitigações

- **O título em 700 alarga a linha e passou por baixo do logo em 13 slides.** A escala do título
  caiu de 44px para 40px, que ainda atende o `TIP-03` (título pelo menos 4px acima do corpo de
  18px), e o `h2` da área de título reserva 96px à direita para o logo. A medição antes e depois
  mostrou que nenhum slide perto do limite ganhou altura.
- **Manrope Light (300) projetada é mais fina.** O piso de 18px no texto de leitura continua
  travado em `test_tema_legibilidade.py`. Se o teste de projeção em sala mostrar perda de leitura,
  o `TIP-01` (legibilidade) prevalece sobre o peso, e a mudança volta para esta ADR.
- **Ícone referenciado sem símbolo no sprite sai vazio, sem erro.** `test_icones.py` confere cada
  nome usado em página e em script contra o sprite.
- **O `insights` não existe no kit.** Ele foi trocado por `query_stats`, registrado em
  `SUBSTITUTOS` no `tools/icones.py`.

## Consequências

- Positivas: o acervo passa no kit vigente, e o validador deixa de dar aprovação falsa.
- Negativas: o cronômetro deixou o Space Mono (o `TIP-06` restringe a monoespaçada ao código) e
  usa Manrope com algarismos tabulares.
- Fica fora desta ADR: o `COR-04`, que restringe o coral a elemento acionável. O coral também
  aparece como marca de dado nos widgets e nas animações MP4, e tirá-lo de lá exige regenerar os
  vídeos. Fica registrado como pendência.

## ADRs relacionadas

- ADR-001: base do tema herdada do M03 e da formação GitLab.
- ADR-005: contrato de widget; a fonte de canvas `api.fonte()` passa a ter 300 como padrão.
