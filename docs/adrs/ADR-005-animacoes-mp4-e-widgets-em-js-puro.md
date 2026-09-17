# ADR-005: animações em MP4 e widgets em JavaScript puro

**Data:** 17/09/2026
**Status:** Aceita
**Decisores:** Prof. José Romualdo

## Contexto

A quinta decisão de 17/09/2026 é que a mídia do acervo é produzida por código, com animações
renderizadas sobre os dados reais e widgets interativos dentro do deck, sem vídeo de terceiros
embutido (design, seção 1). O objetivo 3 do design pede ao menos duas animações e ao menos um
widget por aula, todos alimentados por `dados/`.

Duas constraints do acervo restringem as opções. Cor só entra por token (`var(--inteli-*)`,
`var(--seg-*)` no navegador, `paleta.cor("--token")` em Python), e `tools/check_brand.py` reprova
cor literal e `font-family` fora de `assets/css/inteli-brand.css`. Número em deck, material,
notebook, widget ou animação vem de `dados/` por código e fica travado em teste.

O encontro depende dessa mídia em dois pontos: as animações do conceito central vivem na seção
"Preparação" do material, no pré-aula, e os widgets sustentam a técnica de prever, observar e
explicar dentro dos blocos de 15 minutos (ADR-004).

## Decisão

Animações são MP4 H.264 geradas por matplotlib sobre `dados/`, e widgets são JavaScript puro
alimentado por JSON gerado de `dados/`.

## Motivações

1. **A mídia herda a fonte única de número e de cor.** Os scripts `tools/animacoes_aulaNN.py` leem
   só `dados/` e pedem cor ao `tools/paleta.py`, que resolve os tokens de
   `assets/css/inteli-brand.css`. Os widgets leem as custom properties em tempo de execução por
   `getComputedStyle`, o que mantém o `check_brand.py` válido para o JavaScript.
2. **O vídeo toca sem rede.** O arquivo fica em `assets/video/`, é servido pelo próprio portal e
   dispensa provedor externo no horário da aula.
3. **O deck não tem build.** Widget em JavaScript puro desenhando em `<canvas>` ou SVG roda no
   deck autocontido, sem bundler e sem pacote de terceiros.
4. **O professor controla a reprodução.** O `<video controls muted playsinline>` com pôster permite
   parar no quadro em que a turma registra a previsão, que é a técnica de prever, observar e
   explicar da ADR-004.
5. **A verificação não depende de decodificar o vídeo.** O Chromium do Playwright, que é o
   navegador dos validadores, não decodifica H.264, e nenhuma verificação toca o vídeo: o contrato
   é conferido por `ffprobe`.

## O contrato de vídeo

| Item | Valor |
|---|---|
| Container e codec | MP4, H.264 |
| Formato de pixel | `yuv420p` |
| Resolução | 1280x720 |
| Quadros por segundo | 30 |
| Áudio | ausente |
| Duração | até 60 segundos |
| Tamanho | até 3 MB |
| Pôster | PNG 1280x720, do primeiro quadro significativo |

O contrato mora em `tools/midia.py`, que grava o MP4 por `matplotlib.animation.FFMpegWriter`
(`libx264`, `yuv420p`, `-an`, `-movflags +faststart`) e lê os metadados por `ffprobe`.
`tools/tests/test_midia.py` confere codec, resolução, formato de pixel, quadros por segundo,
duração e bytes de todo vídeo de `assets/video/`, exige que todo vídeo referenciado exista com
pôster e atributos, e reprova vídeo órfão. Um diretório de vídeo vazio com deck que referencia
vídeo reprova, porque nada medido nunca lê como sucesso.

## O contrato de widget

O markup é `<div class="widget" data-widget="nome" data-fonte="../assets/data/arquivo.json">`, com
o script em `assets/js/widgets/nome.js` e o JSON gerado por `tools/dados_widgets_aulaNN.py` a
partir de `dados/`. O runtime `assets/js/inteli-widgets.js` carrega a fonte, chama a função
registrada e grava `data-pronto="sim"` no elemento ao terminar; falha de carga ou de montagem grava
`data-pronto="erro"` e escreve no console.

Três regras valem para quem escreve um widget, e as duas primeiras vêm das constraints de marca:

1. Nenhuma cor literal. `api.cor('--seg-primaria')` lê a custom property do tema.
2. Nenhuma família tipográfica literal. `api.fonte(16, 600)` monta o `ctx.font` a partir de
   `--fonte-texto`.
3. Nenhuma medida de layout para desenhar. Slide fora de cena tem `display: none` e mede zero, por
   isso o canvas usa `data-largura` e `data-altura` do markup, e coordenada de ponteiro sai de
   `api.ponto(evento, canvas)`, porque o Reveal escala o slide com `transform`.

O runtime monta os widgets depois do evento `load` e de `document.fonts.ready`. O
`DOMContentLoaded` chegaria cedo demais, porque os arquivos de `assets/js/widgets/` são carregados
depois do runtime e precisam ter se registrado antes da montagem.

`tools/check_widgets.py` abre cada deck no Chromium do Playwright, conta os widgets declarados,
exige `data-pronto="sim"` em todos e zero erro de console. Deck com widget declarado e zero widget
medido reprova.

## Servidor local do validador de widgets

O validador serve as páginas do repositório por HTTP em `127.0.0.1`, porque os decks usam caminhos
relativos para `assets/`. Com um servidor de uma única thread (`socketserver.TCPServer`), 1 de 6
execuções de `tools/check_widgets.py` falhou com `net::ERR_SOCKET_NOT_CONNECTED` num recurso
aleatório da página, sem relação com o conteúdo servido. A causa é a conexão especulativa de
preconexão que o Chromium abre e às vezes não usa: o servidor de uma thread aceita essa conexão
ociosa e fica preso dentro do `readline()` dela, e nenhuma outra requisição é atendida até ela
fechar.

Por isso `check_slides.servir()`, usado pelos dois validadores de deck, passou a
`socketserver.ThreadingTCPServer` com `daemon_threads`. A regressão está em
`tools/tests/test_servidor.py`, que abre uma conexão TCP crua sem mandar byte nenhum e exige que a
próxima requisição real responda 200, reproduzindo o travamento de forma determinística em vez de
depender de sorte de agendamento.

## Alternativas descartadas

| Alternativa | Por que não entrou |
|---|---|
| Manim para as animações | o design fixa `matplotlib.animation.FuncAnimation` com escrita por ffmpeg (seção 7.1), e matplotlib já é a ferramenta das figuras das aulas (`tools/graficos_aulaNN.py`, design seção 11), com um caminho único de cor por `tools/paleta.py`; uma segunda ferramenta de renderização precisaria repetir essa ligação com os tokens e entraria como dependência nova, sem requisito registrado que a peça |
| GIF animado | fica fora do contrato de vídeo, que exige H.264 em `yuv420p` conferido por `ffprobe`, e fica sem os controles de `<video>` que o professor usa para parar no quadro da previsão |
| Biblioteca de gráficos dentro do deck | o design pede JavaScript puro, sem biblioteca, com cor lida em tempo de execução do tema, para o `check_brand.py` continuar valendo (seção 7.2); biblioteca de terceiros traz paleta própria em cor literal e peso de pacote num deck que não tem build. A decisão vale para o deck: a página do produto da Aula 05 usa Plotly.js, e isso é conteúdo ensinado à turma (design, seção 9) |

## Riscos conhecidos

| Risco | Mitigação |
|---|---|
| Vídeo pesado inflando o git | teto de 3 MB por clipe, com teste que reprova acima disso |
| Chromium do Playwright sem H.264, o que impede validar tocando o vídeo | nenhum validador depende de reprodução; o contrato é medido por `ffprobe` |
| Widget que mede o layout desenha em zero, porque slide fora de cena tem `display: none` | tamanho declarado em `data-largura` e `data-altura`; `tools/check_widgets.py` exige `data-pronto="sim"`, que não aparece quando a montagem falha |
| Widget registrado depois da montagem não monta | o runtime espera o evento `load` e `document.fonts.ready` antes de montar |
| `ffmpeg` ausente na máquina ou no CI, e nenhuma animação gerada | o teste de mídia reprova diretório de vídeo vazio com deck que referencia vídeo; o workflow `validate.yml` previsto no design (seção 13) instala ffmpeg e Chromium, e ainda não existe no repositório (ver `docs/ANDAMENTO.md`) |
| Validador de widget intermitente por conexão ociosa do navegador | servidor com uma thread por conexão e a regressão de `tools/tests/test_servidor.py` |
| Animação e widget saem de `dados/` e podem divergir do número do deck | as medições de cada aula são travadas em teste antes de o deck ser escrito, e deck, animação e widget citam o mesmo valor medido |

## Consequências

**Positivas**

- Toda animação e todo widget é regenerável a partir de `dados/`, e a mudança de um número no
  snapshot propaga por código.
- A fidelidade à marca vale também na mídia, porque cor e fonte saem dos mesmos tokens do tema.
- A aula funciona sem rede, incluindo o vídeo.
- O deck segue autocontido, sem bundler e sem dependência de pacote de terceiros.

**Negativas**

- Produzir mídia por código custa mais tempo de construção do que capturar tela ou reaproveitar
  vídeo de terceiros.
- O acervo passa a depender de ffmpeg para gerar e de ffprobe para verificar.
- Cada widget novo é código próprio, sem biblioteca para encurtar o caminho, e precisa respeitar as
  três regras de escrita.
- O pôster PNG dobra o número de arquivos de mídia por animação.

## ADRs relacionadas

- ADR-003, que é a única fonte de número das animações e dos widgets.
- ADR-004, que define onde a animação e o widget entram nos três tempos.
- ADR-001, que trouxe os tokens de marca e o servidor local reaproveitado pelo validador.
