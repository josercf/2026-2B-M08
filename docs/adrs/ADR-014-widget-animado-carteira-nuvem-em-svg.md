# ADR-014: Widget animado carteira-nuvem em SVG, com quadro de foco calculado

**Data:** 20/10/2026
**Status:** Proposta
**Decisores:** Prof. José Romualdo

## Contexto

O professor pediu, para o slide do parceiro da Aula 01, uma animação que mostre à esquerda a
carteira de 15 ativos e, num movimento de câmera que se afasta, transforme cada ativo num ponto
do plano risco-retorno, monte a nuvem de carteiras e trace a fronteira de Markowitz. Os widgets
existentes (ADR-005) desenham em canvas e respondem a clique; nenhum anima sozinho.

Na janela comum dos 15 ativos (ADR-009, 1.423 retornos de 14/12/2020 a 31/08/2026), a MGLU3 tem
retorno anual de -42,83% e volatilidade de 67,68%. O quadro que contém os 15 ativos vai de 0% a
70% de volatilidade e de -50% a 40% de retorno, e nele a nuvem de carteiras ocupa só a faixa de
12% a 24% de volatilidade.

## Decisão

O widget `carteira-nuvem` desenha em SVG, como função pura do tempo, e usa dois quadros calculados
em `tools/dados_widgets_aula01.py`: o completo, com os 15 ativos, e o de foco, com a nuvem, a
fronteira e os ativos próximos, em que o ativo de fora vira um marcador de borda com os números.

## Motivações

- SVG mantém texto nítido no `?print-pdf` e deixa o teste medir cada rótulo pelo DOM
  (`getBoundingClientRect`), o que no canvas não é possível.
- `aplicar(t)` sem estado acumulado faz do estado final o mesmo quadro para o validador, o PDF,
  `prefers-reduced-motion` e o fim da animação.
- O quadro de foco sai de uma regra escrita no gerador (volatilidade acima de 1,5 vez a do fim
  da fronteira ou retorno mais de 10 pontos abaixo do menor da nuvem). Se o snapshot mudar, o
  quadro acompanha, e o teste confere o que fica dentro.
- A câmera que se afasta e depois aproxima mostra a MGLU3 longe da cesta antes de tirá-la do
  quadro, então nenhum dado some sem aviso.

## Riscos conhecidos

- Ativo novo de comportamento extremo muda o quadro de foco. Mitigação: `test_widget_carteira.py`
  confere que todo ativo fora da regra está dentro do foco e que a nuvem e a fronteira também.
- Rótulos de ativos próximos podem colidir. Mitigação: posicionamento guloso com a largura medida
  do texto e teste que reprova sobreposição de rótulos no estado final.
- Com a câmera próxima, elementos transparentes passam da caixa do SVG e o `check_slides.py`
  acusaria estouro. Mitigação: a cena fica com `visibility: hidden` enquanto espera, travado em
  teste.

## Consequências

- Positivas: o slide do parceiro ganha a narrativa visual do módulo inteiro com dados versionados,
  e o mesmo widget pode reaparecer na Aula 04 sem recálculo.
- Negativas: o widget depende do evento `slidechanged` do Reveal para tocar ao entrar no slide, e
  a subamostra de 2.000 das 10.000 carteiras soma cerca de 30 KB de JSON ao deck.

## ADRs relacionadas

- ADR-005 (animações MP4 e widgets em JS puro)
- ADR-009 (tratamento de ausência único com janela comum)
- ADR-011 (tema no brand kit vigente)
