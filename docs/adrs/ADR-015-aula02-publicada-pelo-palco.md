# ADR-015: Aula 02 publicada pela exportação estática do Palco

**Data:** 21/10/2026
**Status:** Proposta
**Decisores:** Prof. José Romualdo

## Contexto

O Palco é o estúdio de apresentações do professor (repositório `palco`). Na etapa 1 ele importou o deck
`aulas/aula02.html` para o catálogo, em 28 slides, e exporta uma página estática que não depende de rede
nem de caminho absoluto. A Aula 02 acontece em 05/11/2026 e o site é servido em
`https://josercf.github.io/2026-2B-M08/`, portanto a página exportada precisa funcionar sob o subcaminho
`/2026-2B-M08/palco/aula02/`.

## Decisão

A pasta `palco/aula02/` recebe a exportação do Palco e o botão Slides da Aula 02 no `index.html` aponta para
ela; o `aulas/aula02.html` original permanece intacto como reserva.

## Motivações

- A exportação passou pelos três portões do Palco antes de ser gravada: regras de marca, layout em 1280x720 e
  slides ausentes.
- O teste `tools/exportar/test/aula02.spec.ts` do Palco compara o texto visível do original e do exportado
  slide a slide, e todo número do original aparece no exportado. O mesmo teste confere 28 seções, os widgets
  `simples-log` e `vol-janela` com `data-pronto="sim"` e zero resposta 4xx sob o subcaminho.
- Manter o deck original dá caminho de volta imediato se a página exportada falhar em sala.

## Riscos conhecidos

- Diferenças de fidelidade entre o original e o importado. O quiz final do original tinha três perguntas num
  slide, com retorno local por clique. Na versão exportada cada pergunta é um slide próprio com o quiz ao vivo
  do Palco (QR para `aluno.html`, placar, abrir e encerrar rodada, revelar), sobre o mesmo projeto Supabase da
  Aula 01 e a sessão `m08-aula02-2026-11-05`; o Palco mantém uma rodada aberta por slide, o que impede três
  quizzes juntos. A apresentação passa de 28 para 30 slides. O retorno por opção do original fica nas notas do
  apresentador. O quiz de preparo (slide 5) já era ao vivo no original e segue assim. O bloco de escolha de
  risco (slide 22) segue clicável (Sustentada e Não sustentada marcam certa ou errada e mostram a certa), em
  uma versão 2 do slide; a versão 1 guarda o resultado da importação.
- Quatro slides (histograma, raiz do tempo, cesta e preparo) usam a variante `compacta` do formato do Palco:
  tabela, vídeo e QR menores só neles, sem alterar o padrão dos demais decks do catálogo.
- A chave do professor é digitada em sala e gravada só no navegador; nenhum arquivo do repositório a contém.
- `check_brand.py` não varre `palco/`, porque a pasta guarda CSS e JS minificados do player. Mitigação: a marca é
  validada pelas regras do Palco na exportação.
- A exportação é regerada no repositório `palco`; editar `palco/aula02/` à mão é perdido na próxima exportação.
  Mitigação: a pasta tem o marcador `.palco-exportacao`, e o Palco recusa sobrescrever pasta sem ele.
- A chave publicável do Supabase do quiz está no JavaScript exportado, como já está no deck original. A chave do
  professor nunca é gravada.

## Consequências

- Positivas: a Aula 02 sai de uma fonte única (o catálogo do Palco), com a mesma página servida em
  qualquer subcaminho.
- Negativas: o repositório passa a guardar cerca de 1,7 MB de saída gerada, e correção de conteúdo da Aula 02
  passa a exigir regerar a exportação.

## ADRs relacionadas

- ADR-005 (animações MP4 e widgets em JS puro)
- ADR-011 (tema no brand kit vigente)
- ADR-013 (abertura animada, agenda enxuta e esteira de artefatos)
