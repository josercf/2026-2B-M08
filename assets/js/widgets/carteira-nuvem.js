// Carteira que vira nuvem (Aula 01, slide do parceiro). Animação em SVG de
// 13,2 segundos, em cinco tempos:
//   1. a carteira de peso igual (1/15) dos 15 ativos entra em cascata, como um
//      extrato, com a câmera próxima;
//   2. a câmera se afasta, os eixos de risco e retorno aparecem à direita e cada
//      linha da carteira voa até o ponto (volatilidade, retorno) do ativo;
//   3. o quadro aproxima da região da nuvem; o ativo que fica longe dela
//      (MGLU3, no snapshot) vira um marcador de borda com os números;
//   4. 2.000 das 10.000 carteiras sorteadas da Aula 04 surgem em ondas, a
//      partir da carteira de peso igual;
//   5. a fronteira eficiente de 50 pontos é traçada, com as carteiras de
//      variância mínima e de máximo Sharpe marcadas.
//
// O estado final é estável: é o que o validador, o PDF (?print-pdf) e quem tem
// prefers-reduced-motion veem. A animação dispara quando o slide fica present,
// recomeça ao voltar ao slide e pelo botão Repetir. Fora de um deck Reveal, ela
// toca uma vez ao montar.
//
// Tudo é função do tempo: aplicar(t) desenha o quadro do instante t, sem estado
// acumulado, e aplicar(FIM) é o estado final. Para teste, o elemento expõe
// elemento.carteiraNuvem = { ir: aplicar, tocar: tocar, fim: FIM }.
//
// Dados: tools/dados_widgets_aula01.py (assets/data/aula01-carteira.json), na
// janela comum dos 15 ativos (ADR-009). Nenhuma cor literal: api.cor('--seg-*').
(function () {
  'use strict';

  var SVG = 'http://www.w3.org/2000/svg';
  var contador = 0;

  // Carteira à esquerda, em coordenadas do SVG.
  var LISTA = {
    largura: 330, cabecalho: 34, linha: 23, total: 26,
    xBolinha: 13, xTicker: 28, xRet: 172, xVol: 254, xPeso: 326
  };
  var TAM = { linha: 15, cabecalho: 14, rotulo: 15, eixo: 15, nota: 14 };
  var RAIO = { ativo: 6, igual: 6.5, nuvem: 2.4, otima: 7.5 };
  var ONDAS = 5;

  // Linha do tempo, em segundos.
  var T = {
    cabecalho: 0.05, linhas: 0.25, passoLinha: 0.09, durLinha: 0.45,
    camera: 2.3, durCamera: 1.9,
    grafico: 2.7, durGrafico: 1.0,
    voo: 3.7, passoVoo: 0.08, durVoo: 1.3, igual: 5.0, assentar: 0.4,
    foco: 7.2, durFoco: 1.4,
    nuvem: 8.7, passoOnda: 0.4, durOnda: 1.0,
    fronteira: 10.8, durFronteira: 1.8, durMarcador: 0.35
  };
  var FIM = 13.2;

  function criar(nome, atributos, pai) {
    var no = document.createElementNS(SVG, nome);
    Object.keys(atributos || {}).forEach(function (k) {
      if (atributos[k] !== null && atributos[k] !== undefined) no.setAttribute(k, atributos[k]);
    });
    if (pai) pai.appendChild(no);
    return no;
  }

  function texto(pai, conteudo, atributos) {
    var t = criar('text', atributos, pai);
    t.textContent = conteudo;
    return t;
  }

  function pct(valor, casas) {
    var s = (valor * 100).toFixed(casas === undefined ? 2 : casas).replace('.', ',');
    return (s === '-0' ? '0' : s) + '%';
  }

  function milhar(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  function limitar(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function lerp(a, b, p) { return a + (b - a) * p; }
  function suave(p) { return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; }
  function saida(p) { return 1 - Math.pow(1 - p, 3); }
  function fase(t, inicio, duracao) { return limitar((t - inicio) / duracao, 0, 1); }

  // Largura de texto medida num SVG fora do slide: o slide fora de cena tem
  // display none e mede zero, e o body herda a mesma família do tema.
  var regua = null;
  function medir(conteudo, tamanho, peso) {
    if (!regua) {
      regua = criar('svg', { width: 10, height: 10, 'aria-hidden': 'true' });
      regua.style.position = 'absolute';
      regua.style.left = '-10000px';
      regua.style.top = '0';
      regua.style.visibility = 'hidden';
      document.body.appendChild(regua);
    }
    var t = texto(regua, conteudo, { 'font-size': tamanho, 'font-weight': peso });
    var w = t.getComputedTextLength();
    regua.removeChild(t);
    return w || conteudo.length * tamanho * 0.62;
  }

  function sobreposicao(a, b) {
    var w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
    var h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
    return w > 0 && h > 0 ? w * h : 0;
  }

  function areaFora(caixa, limite) {
    var dentro = sobreposicao(caixa, limite);
    return caixa.w * caixa.h - dentro;
  }

  // Posicionamento guloso de rótulos: para cada ponto, testa oito posições em
  // duas distâncias e fica com a de menor custo (sobreposição com rótulos já
  // postos, com pontos, com obstáculos fixos e saída do gráfico).
  function posicionar(itens, obstaculos, limite) {
    var postos = obstaculos.slice();
    var saidaPos = {};
    itens.forEach(function (item, ordem) {
      var w = item.w, h = item.h, r = item.r + 4;
      var melhor = null;
      [0, 10].forEach(function (d) {
        [
          [r + d, -h / 2], [-r - d - w, -h / 2], [-w / 2, -r - d - h], [-w / 2, r + d],
          [r * 0.7 + d, -r * 0.7 - d - h], [r * 0.7 + d, r * 0.7 + d],
          [-r * 0.7 - d - w, -r * 0.7 - d - h], [-r * 0.7 - d - w, r * 0.7 + d]
        ].forEach(function (c, preferencia) {
          var caixa = { x: item.x + c[0], y: item.y + c[1], w: w, h: h };
          var custo = preferencia * 0.5 + d * 0.8 + 40 * areaFora(caixa, limite);
          postos.forEach(function (o) { custo += (o.peso || 30) * sobreposicao(caixa, o); });
          itens.forEach(function (outro, k) {
            if (k === ordem) return;
            custo += 30 * sobreposicao(caixa, {
              x: outro.x - outro.r - 1, y: outro.y - outro.r - 1, w: 2 * outro.r + 2, h: 2 * outro.r + 2
            });
          });
          if (!melhor || custo < melhor.custo) {
            melhor = { custo: custo, dx: c[0], dy: c[1] + h / 2, caixa: caixa };
          }
        });
      });
      postos.push(melhor.caixa);
      saidaPos[item.chave] = melhor;
    });
    return saidaPos;
  }

  IntelIWidgets.registrar('carteira-nuvem', function (elemento, dados, api) {
    var L = Number(elemento.dataset.largura || 1160);
    var A = Number(elemento.dataset.altura || 470);
    var id = 'carteira-nuvem-' + (++contador);
    var cor = {
      base: api.cor('--seg-base'), superficie: api.cor('--seg-superficie'), borda: api.cor('--seg-borda'),
      primaria: api.cor('--seg-primaria'), secundaria: api.cor('--seg-secundaria'),
      destaque: api.cor('--seg-destaque'), texto: api.cor('--seg-texto'), suave: api.cor('--seg-texto-suave')
    };
    var ativos = dados.ativos;
    var n = ativos.length;
    var foraDoFoco = dados.quadro.fora;
    var quadroC = dados.quadro.completo;
    var quadroF = dados.quadro.foco;

    // Área do gráfico e câmera inicial, que enquadra só a carteira.
    var G = { esq: 470, dir: L - 22, topo: 14, base: A - 58 };
    var alturaLista = LISTA.cabecalho + n * LISTA.linha + LISTA.total;
    var escala0 = Math.min(1.3, (A - 10) / alturaLista);
    var camera0 = { s: escala0, x: L / 2 - escala0 * LISTA.largura / 2, y: (A - escala0 * alturaLista) / 2 };

    function vista(p) {
      return {
        x0: lerp(quadroC.x[0], quadroF.x[0], p), x1: lerp(quadroC.x[1], quadroF.x[1], p),
        y0: lerp(quadroC.y[0], quadroF.y[0], p), y1: lerp(quadroC.y[1], quadroF.y[1], p)
      };
    }
    function px(v, vi) { return G.esq + (G.dir - G.esq) * (v - vi.x0) / (vi.x1 - vi.x0); }
    function py(r, vi) { return G.base - (G.base - G.topo) * (r - vi.y0) / (vi.y1 - vi.y0); }
    var VC = vista(0), VF = vista(1);
    var limiteGrafico = { x: G.esq, y: G.topo, w: G.dir - G.esq, h: G.base - G.topo };

    // Estrutura: palco com o SVG e o botão Repetir.
    var palco = document.createElement('div');
    palco.className = 'carteira-palco';
    palco.style.width = L + 'px';
    var svg = criar('svg', {
      viewBox: '0 0 ' + L + ' ' + A, width: L, height: A, role: 'img',
      'aria-label': 'Carteira de peso igual com os ' + n + ' ativos da cesta, que viram pontos no plano ' +
        'risco e retorno, seguidos de ' + milhar(dados.nuvem.vol.length) + ' das ' +
        milhar(dados.nuvem.total) + ' carteiras sorteadas e da fronteira eficiente de ' +
        dados.fronteira.length + ' pontos.'
    });
    svg.setAttribute('class', 'carteira-svg');
    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'carteira-repetir';
    botao.textContent = 'Repetir';
    palco.appendChild(svg);
    palco.appendChild(botao);
    elemento.appendChild(palco);

    var defs = criar('defs', {}, svg);
    var recorte = criar('clipPath', { id: id + '-recorte' }, defs);
    criar('rect', { x: G.esq, y: G.topo, width: G.dir - G.esq, height: G.base - G.topo }, recorte);

    var cena = criar('g', {}, svg);
    var gLista = criar('g', {}, cena);
    var gGrafico = criar('g', {}, cena);
    var gGrade = criar('g', {}, gGrafico);
    var gNuvem = criar('g', { 'clip-path': 'url(#' + id + '-recorte)' }, gGrafico);
    var gFronteira = criar('g', { 'clip-path': 'url(#' + id + '-recorte)' }, gGrafico);
    var gLegenda = criar('g', {}, gGrafico);
    var gFantasmas = criar('g', {}, cena);
    var gPontos = criar('g', {}, cena);
    var gRotulos = criar('g', {}, cena);

    var halo = { stroke: cor.base, 'stroke-width': 4, 'stroke-linejoin': 'round', 'paint-order': 'stroke' };
    function comHalo(atributos) {
      Object.keys(halo).forEach(function (k) { atributos[k] = halo[k]; });
      return atributos;
    }

    // 1. Carteira: cabeçalho, 15 linhas, total e nota da janela.
    var cabecalho = criar('g', {}, gLista);
    criar('rect', { x: 0, y: 0, width: LISTA.largura, height: LISTA.cabecalho, fill: cor.superficie }, cabecalho);
    [['Ativo', LISTA.xTicker, 'start'], ['Ret. anual', LISTA.xRet, 'end'],
     ['Vol. anual', LISTA.xVol, 'end'], ['Peso', LISTA.xPeso, 'end']].forEach(function (c) {
      texto(cabecalho, c[0], {
        x: c[1], y: LISTA.cabecalho / 2, 'dominant-baseline': 'central', 'text-anchor': c[2],
        'font-size': TAM.cabecalho, 'font-weight': 600, fill: cor.texto
      });
    });

    function linhaDaCarteira(i) {
      return LISTA.cabecalho + i * LISTA.linha + LISTA.linha / 2;
    }

    var linhas = ativos.map(function (ativo, i) {
      var g = criar('g', {}, gLista);
      var y = linhaDaCarteira(i);
      criar('line', { x1: 0, x2: LISTA.largura, y1: y + LISTA.linha / 2, y2: y + LISTA.linha / 2,
        stroke: cor.borda, 'stroke-width': 1 }, g);
      criar('circle', { cx: LISTA.xBolinha, cy: y, r: 5, fill: cor.primaria }, g);
      [[ativo.ticker, LISTA.xTicker, 'start', 600], [pct(ativo.ret), LISTA.xRet, 'end', 300],
       [pct(ativo.vol), LISTA.xVol, 'end', 300], [pct(dados.peso), LISTA.xPeso, 'end', 300]].forEach(function (c) {
        texto(g, c[0], { x: c[1], y: y, 'dominant-baseline': 'central', 'text-anchor': c[2],
          'font-size': TAM.linha, 'font-weight': c[3], fill: cor.texto });
      });
      return g;
    });

    var yTotal = LISTA.cabecalho + n * LISTA.linha;
    var total = criar('g', {}, gLista);
    criar('line', { x1: 0, x2: LISTA.largura, y1: yTotal + 1, y2: yTotal + 1, stroke: cor.primaria,
      'stroke-width': 2 }, total);
    var yTotalTexto = yTotal + LISTA.total / 2 + 1;
    criar('circle', { cx: LISTA.xBolinha, cy: yTotalTexto, r: 5, fill: cor.base, stroke: cor.primaria,
      'stroke-width': 2.5 }, total);
    [['Carteira', LISTA.xTicker, 'start'], [pct(dados.igual.ret), LISTA.xRet, 'end'],
     [pct(dados.igual.vol), LISTA.xVol, 'end'], [pct(dados.peso * n, 0), LISTA.xPeso, 'end']].forEach(function (c) {
      texto(total, c[0], { x: c[1], y: yTotalTexto, 'dominant-baseline': 'central', 'text-anchor': c[2],
        'font-size': TAM.linha, 'font-weight': 700, fill: cor.texto });
    });

    var nota = criar('g', {}, gLista);
    texto(nota, 'Janela comum: ' + dados.janela.inicio + ' a ' + dados.janela.fim + ',', {
      x: 0, y: alturaLista + 26, 'font-size': TAM.nota, 'font-weight': 300, fill: cor.texto });
    texto(nota, milhar(dados.janela.retornos) + ' retornos diários por ativo', {
      x: 0, y: alturaLista + 46, 'font-size': TAM.nota, 'font-weight': 300, fill: cor.texto });

    // 2. Eixos: linhas e títulos fixos; marcas e grade refeitas a cada vista.
    criar('line', { x1: G.esq, x2: G.esq, y1: G.topo, y2: G.base, stroke: cor.borda, 'stroke-width': 1.5 }, gGrafico);
    criar('line', { x1: G.esq, x2: G.dir, y1: G.base, y2: G.base, stroke: cor.borda, 'stroke-width': 1.5 }, gGrafico);
    texto(gGrafico, 'Volatilidade anual (risco)', {
      x: (G.esq + G.dir) / 2, y: A - 6, 'text-anchor': 'middle', 'font-size': TAM.eixo, 'font-weight': 600,
      fill: cor.texto });
    texto(gGrafico, 'Retorno anual', {
      x: 0, y: 0, 'text-anchor': 'middle', 'font-size': TAM.eixo, 'font-weight': 600, fill: cor.texto,
      transform: 'translate(' + (G.esq - 58) + ',' + ((G.topo + G.base) / 2) + ') rotate(-90)' });

    var ultimaVista = null;
    function desenharGrade(vi, pFoco) {
      var chave = [vi.x0, vi.x1, vi.y0, vi.y1, pFoco].join('|');
      if (chave === ultimaVista) return;
      ultimaVista = chave;
      while (gGrade.firstChild) gGrade.removeChild(gGrade.firstChild);
      var passo = quadroF.passo;
      function marcas(a, b) {
        var lista = [];
        for (var k = Math.ceil(a / passo - 1e-6); k * passo <= b + 1e-6; k++) lista.push(k);
        return lista;
      }
      function opacidade(k) {
        // Múltiplos do passo do quadro completo ficam sempre; os intermediários
        // entram junto com a aproximação.
        var multiplo = Math.round(quadroC.passo / passo);
        return k % multiplo === 0 ? 1 : pFoco;
      }
      marcas(vi.x0, vi.x1).forEach(function (k) {
        var o = opacidade(k);
        if (o < 0.02) return;
        var x = px(k * passo, vi);
        if (x > G.esq + 1) {
          criar('line', { x1: x, x2: x, y1: G.topo, y2: G.base, stroke: cor.superficie, 'stroke-width': 1,
            opacity: o }, gGrade);
        }
        texto(gGrade, pct(k * passo, 0), { x: x, y: G.base + 24, 'text-anchor': 'middle',
          'font-size': TAM.eixo, 'font-weight': 300, fill: cor.texto, opacity: o });
      });
      marcas(vi.y0, vi.y1).forEach(function (k) {
        var o = opacidade(k);
        if (o < 0.02) return;
        var y = py(k * passo, vi);
        if (y < G.base - 1) {
          criar('line', { x1: G.esq, x2: G.dir, y1: y, y2: y, stroke: k === 0 ? cor.borda : cor.superficie,
            'stroke-width': 1, opacity: o }, gGrade);
        }
        texto(gGrade, pct(k * passo, 0), { x: G.esq - 10, y: y, 'text-anchor': 'end',
          'dominant-baseline': 'central', 'font-size': TAM.eixo, 'font-weight': 300, fill: cor.texto, opacity: o });
      });
    }

    // Legenda, no canto superior esquerdo do gráfico.
    var amostra = dados.nuvem.vol.length;
    var itensLegenda = [
      { simbolo: 'ativo', texto: 'Ativo da carteira', inicio: T.grafico + 0.4 },
      { simbolo: 'igual', texto: 'Carteira de peso igual (1/' + n + ')', inicio: T.igual + 0.6 },
      { simbolo: 'nuvem', texto: milhar(amostra) + ' de ' + milhar(dados.nuvem.total) + ' carteiras sorteadas',
        inicio: T.nuvem },
      { simbolo: 'fronteira', texto: 'Fronteira eficiente (' + dados.fronteira.length + ' pontos)',
        inicio: T.fronteira }
    ];
    var legX = G.esq + 16, legY = G.topo + 16, legPasso = 23, legLargura = 0;
    itensLegenda.forEach(function (item, i) {
      var g = criar('g', {}, gLegenda);
      var y = legY + i * legPasso;
      if (item.simbolo === 'ativo') criar('circle', { cx: legX + 7, cy: y, r: RAIO.ativo, fill: cor.primaria }, g);
      if (item.simbolo === 'igual') {
        criar('circle', { cx: legX + 7, cy: y, r: RAIO.igual - 1, fill: cor.base, stroke: cor.primaria,
          'stroke-width': 2.5 }, g);
      }
      if (item.simbolo === 'nuvem') {
        [[-4, 2], [0, -3], [4, 3], [6, -2], [-6, -1]].forEach(function (d) {
          criar('circle', { cx: legX + 7 + d[0], cy: y + d[1], r: RAIO.nuvem, fill: cor.secundaria }, g);
        });
      }
      if (item.simbolo === 'fronteira') {
        criar('line', { x1: legX - 2, x2: legX + 16, y1: y, y2: y, stroke: cor.destaque, 'stroke-width': 3.5 }, g);
      }
      texto(g, item.texto, { x: legX + 24, y: y, 'dominant-baseline': 'central', 'font-size': TAM.rotulo,
        'font-weight': 300, fill: cor.texto });
      legLargura = Math.max(legLargura, 24 + medir(item.texto, TAM.rotulo, 300));
      item.no = g;
    });
    var caixaLegenda = { x: legX - 6, y: legY - 14, w: legLargura + 12, h: itensLegenda.length * legPasso + 6,
      peso: 60 };
    var caixaBotao = { x: L - 110, y: 0, w: 110, h: 36, peso: 60 };

    // 3. Nuvem: ondas que nascem na carteira de peso igual.
    var centroNuvem = { x: px(dados.igual.vol, VF), y: py(dados.igual.ret, VF) };
    var ondas = [];
    for (var k = 0; k < ONDAS; k++) ondas.push(criar('g', {}, gNuvem));
    dados.nuvem.vol.forEach(function (v, i) {
      criar('circle', { cx: px(v, VF).toFixed(1), cy: py(dados.nuvem.ret[i], VF).toFixed(1), r: RAIO.nuvem,
        fill: cor.secundaria, 'fill-opacity': 0.75 }, ondas[Math.floor(i * ONDAS / amostra)]);
    });

    // 4. Fronteira, com pathLength 1 para o traçado por stroke-dashoffset.
    var pontosFronteira = dados.fronteira.map(function (p) { return [px(p[0], VF), py(p[1], VF)]; });
    var caminho = criar('path', {
      d: pontosFronteira.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); })
        .join(' '),
      fill: 'none', stroke: cor.destaque, 'stroke-width': 3.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round',
      pathLength: 1, 'stroke-dasharray': '1 1', 'stroke-dashoffset': 1
    }, gFronteira);
    caminho.setAttribute('class', 'carteira-fronteira');
    // Fração do traçado em que a fronteira passa pela carteira de máximo Sharpe.
    var acumulado = [0];
    for (var j = 1; j < pontosFronteira.length; j++) {
      acumulado.push(acumulado[j - 1] + Math.hypot(pontosFronteira[j][0] - pontosFronteira[j - 1][0],
        pontosFronteira[j][1] - pontosFronteira[j - 1][1]));
    }
    var comprimento = acumulado[acumulado.length - 1];
    function fracaoNaFronteira(p) {
      var melhor = 0, menor = Infinity;
      dados.fronteira.forEach(function (q, i) {
        var d = Math.hypot(q[0] - p.vol, q[1] - p.ret);
        if (d < menor) { menor = d; melhor = i; }
      });
      return acumulado[melhor] / comprimento;
    }

    // Pontos: os 15 ativos, a carteira de peso igual e as duas ótimas.
    var otimas = [
      { chave: 'variancia_minima', rotulo: 'Variância mínima', dados: dados.variancia_minima },
      { chave: 'maximo_sharpe', rotulo: 'Máximo Sharpe', dados: dados.maximo_sharpe }
    ].map(function (o) {
      o.x = px(o.dados.vol, VF);
      o.y = py(o.dados.ret, VF);
      o.inicio = T.fronteira + T.durFronteira * fracaoNaFronteira(o.dados);
      o.ponto = criar('circle', { cx: o.x, cy: o.y, r: RAIO.otima, fill: cor.destaque, stroke: cor.base,
        'stroke-width': 2.5, opacity: 0 }, gPontos);
      o.ponto.setAttribute('class', 'carteira-otima');
      o.rotulo = texto(gRotulos, o.rotulo, comHalo({ 'dominant-baseline': 'central', 'font-size': TAM.rotulo,
        'font-weight': 700, fill: cor.texto, opacity: 0 }));
      o.w = medir(o.rotulo.textContent, TAM.rotulo, 700);
      return o;
    });

    var moveis = ativos.map(function (ativo, i) {
      return { chave: ativo.ticker, rotulo: ativo.ticker, vol: ativo.vol, ret: ativo.ret,
        origem: { x: LISTA.xBolinha, y: linhaDaCarteira(i) }, inicio: T.voo + i * T.passoVoo,
        raio: RAIO.ativo, fora: foraDoFoco.indexOf(ativo.ticker) >= 0, peso: 600 };
    });
    moveis.push({ chave: 'igual', rotulo: 'Carteira 1/' + n, vol: dados.igual.vol, ret: dados.igual.ret,
      origem: { x: LISTA.xBolinha, y: yTotalTexto }, inicio: T.igual, raio: RAIO.igual, fora: false,
      igual: true, peso: 700 });
    moveis.forEach(function (m) {
      m.fantasma = criar('rect', { fill: cor.primaria, opacity: 0 }, gFantasmas);
      m.ponto = m.igual
        ? criar('circle', { r: RAIO.igual - 1, fill: cor.base, stroke: cor.primaria, 'stroke-width': 2.5 }, gPontos)
        : criar('circle', { r: RAIO.ativo, fill: cor.primaria, stroke: cor.base, 'stroke-width': 1.5 }, gPontos);
      m.ponto.setAttribute('class', m.igual ? 'carteira-igual' : 'carteira-ativo');
      m.ponto.setAttribute('data-ticker', m.chave);
      m.texto = texto(gRotulos, m.rotulo, comHalo({ 'dominant-baseline': 'central', 'font-size': TAM.rotulo,
        'font-weight': m.peso, fill: cor.texto }));
      m.texto.setAttribute('class', 'carteira-rotulo');
      m.w = medir(m.rotulo, TAM.rotulo, m.peso);
      m.c = { x: px(m.vol, VC), y: py(m.ret, VC) };
      m.f = { x: px(m.vol, VF), y: py(m.ret, VF) };
    });

    // Marcador de borda do ativo fora do foco: seta e nota com os números.
    var foraNotas = moveis.filter(function (m) { return m.fora; }).map(function (m, i) {
      var g = criar('g', { opacity: 0 }, gRotulos);
      var conteudo = m.rotulo + ' fora do quadro: retorno ' + pct(m.ret) + ', volatilidade ' + pct(m.vol);
      var xFim = G.dir - 34, y = G.base - 16 - i * 22;
      var t = texto(g, conteudo, comHalo({ x: xFim, y: y, 'text-anchor': 'end', 'dominant-baseline': 'central',
        'font-size': TAM.rotulo, 'font-weight': 600, fill: cor.texto }));
      t.setAttribute('class', 'carteira-fora');
      var seta = criar('path', { d: 'M0 -6 L10 0 L0 6 Z', fill: cor.primaria }, g);
      m.nota = { g: g, seta: seta, caixa: { x: xFim - medir(conteudo, TAM.rotulo, 600) - 4, y: y - 11,
        w: medir(conteudo, TAM.rotulo, 600) + 8, h: 22, peso: 60 } };
      return m.nota.caixa;
    });

    function posicaoNaBordaDe(p) {
      return { x: limitar(p.x, G.esq + 14, G.dir - 14), y: limitar(p.y, G.topo + 14, G.base - 14) };
    }

    // Rótulos: posição no quadro completo (só fica visível quem não colide) e
    // no foco. Ótimas primeiro, porque são as marcas de que a aula fala.
    var altura = TAM.rotulo + 3;
    function itensRotulo(vistaFoco) {
      var lista = [];
      if (vistaFoco) {
        otimas.forEach(function (o) {
          lista.push({ chave: o.chave, x: o.x, y: o.y, w: o.w, h: altura, r: RAIO.otima });
        });
      }
      moveis.forEach(function (m) {
        if (vistaFoco && m.fora) return;
        var p = vistaFoco ? m.f : m.c;
        lista.push({ chave: m.chave, x: p.x, y: p.y, w: m.w, h: altura, r: m.raio });
      });
      return lista;
    }
    var amostrasFronteira = pontosFronteira.filter(function (p, i) { return i % 2 === 0; }).map(function (p) {
      return { x: p[0] - 3, y: p[1] - 3, w: 6, h: 6, peso: 8 };
    });
    var posC = posicionar(itensRotulo(false), [caixaLegenda, caixaBotao], limiteGrafico);
    var posF = posicionar(itensRotulo(true), [caixaLegenda, caixaBotao].concat(foraNotas, amostrasFronteira),
      limiteGrafico);
    moveis.forEach(function (m) {
      // No quadro completo só fica o rótulo que cabe colado ao ponto (à
      // direita, à esquerda ou acima) sem encostar em nada.
      m.visivelC = posC[m.chave].custo <= 1;
      m.offC = posC[m.chave];
      m.offF = m.fora ? posC[m.chave] : posF[m.chave];
      m.texto.setAttribute('text-anchor', 'start');
    });
    otimas.forEach(function (o) {
      o.rotulo.setAttribute('x', (o.x + posF[o.chave].dx).toFixed(1));
      o.rotulo.setAttribute('y', (o.y + posF[o.chave].dy).toFixed(1));
    });

    function bezier(a, b, c, p) {
      var q = 1 - p;
      return { x: q * q * a.x + 2 * q * p * c.x + p * p * b.x, y: q * q * a.y + 2 * q * p * c.y + p * p * b.y };
    }

    // Desenha o instante t. Toda propriedade animada é reescrita a cada chamada.
    function aplicar(t) {
      // Câmera.
      var pc = suave(fase(t, T.camera, T.durCamera));
      cena.setAttribute('transform', 'translate(' + lerp(camera0.x, 0, pc).toFixed(2) + ',' +
        lerp(camera0.y, 0, pc).toFixed(2) + ') scale(' + lerp(camera0.s, 1, pc).toFixed(4) + ')');

      // Carteira.
      var pCab = saida(fase(t, T.cabecalho, T.durLinha));
      cabecalho.setAttribute('opacity', pCab);
      linhas.forEach(function (g, i) {
        var p = saida(fase(t, T.linhas + i * T.passoLinha, T.durLinha));
        g.setAttribute('opacity', p);
        g.setAttribute('transform', 'translate(' + ((1 - p) * -24).toFixed(1) + ',0)');
      });
      var pTot = saida(fase(t, T.linhas + n * T.passoLinha, T.durLinha));
      total.setAttribute('opacity', pTot);
      total.setAttribute('transform', 'translate(' + ((1 - pTot) * -24).toFixed(1) + ',0)');
      nota.setAttribute('opacity', fase(t, T.camera + 0.6, 0.8));

      // Gráfico e grade.
      gGrafico.setAttribute('opacity', saida(fase(t, T.grafico, T.durGrafico)));
      var pf = suave(fase(t, T.foco, T.durFoco));
      var vi = vista(pf);
      desenharGrade(vi, pf);
      itensLegenda.forEach(function (item) { item.no.setAttribute('opacity', fase(t, item.inicio, 0.6)); });

      // Voo de cada linha até o ponto do ativo.
      moveis.forEach(function (m) {
        var pv = fase(t, m.inicio, T.durVoo);
        var ev = suave(pv);
        var alvo = { x: px(m.vol, vi), y: py(m.ret, vi) };
        var noFoco = pf > 0 && m.fora;
        if (noFoco) alvo = posicaoNaBordaDe(alvo);
        var controle = { x: (m.origem.x + alvo.x) / 2, y: Math.max(G.topo, Math.min(m.origem.y, alvo.y) - 50) };
        var pos = pv < 1 ? bezier(m.origem, alvo, controle, ev) : alvo;
        var visivel = pv > 0 ? 1 : 0;
        m.ponto.setAttribute('cx', pos.x.toFixed(1));
        m.ponto.setAttribute('cy', pos.y.toFixed(1));
        m.ponto.setAttribute('opacity', visivel);

        // A linha da carteira encolhe até virar o ponto, no primeiro terço do voo.
        var ef = saida(limitar(pv * 2.2, 0, 1));
        var cx = lerp(LISTA.largura / 2, pos.x, ef), cy = lerp(m.origem.y, pos.y, ef);
        var w = lerp(LISTA.largura - 8, 2 * m.raio, ef), h = lerp(LISTA.linha - 3, 2 * m.raio, ef);
        m.fantasma.setAttribute('x', (cx - w / 2).toFixed(1));
        m.fantasma.setAttribute('y', (cy - h / 2).toFixed(1));
        m.fantasma.setAttribute('width', w.toFixed(1));
        m.fantasma.setAttribute('height', h.toFixed(1));
        m.fantasma.setAttribute('opacity', pv > 0 && pv < 1 ? (0.16 * (1 - ef)).toFixed(3) : 0);

        // Rótulo: aparece quando o ponto já saiu da carteira, assenta na
        // posição do quadro completo (some se ali colide), apaga durante a
        // aproximação e volta na posição do foco.
        var dx, dy, opacidade;
        if (t < T.foco + T.durFoco / 2) {
          var pa = suave(fase(t, m.inicio + T.durVoo, T.assentar));
          var voo = { dx: m.raio + 6, dy: 0 };
          dx = lerp(voo.dx, m.offC.dx, pa);
          dy = lerp(voo.dy, m.offC.dy, pa);
          opacidade = visivel * limitar((pv - 0.4) / 0.3, 0, 1) * lerp(1, m.visivelC ? 1 : 0, pa) *
            (1 - fase(t, T.foco, 0.35));
        } else {
          dx = m.offF.dx;
          dy = m.offF.dy;
          opacidade = m.fora ? 0 : fase(t, T.foco + T.durFoco - 0.25, 0.5);
        }
        m.texto.setAttribute('x', (pos.x + dx).toFixed(1));
        m.texto.setAttribute('y', (pos.y + dy).toFixed(1));
        m.texto.setAttribute('opacity', opacidade.toFixed(3));

        if (m.nota) {
          var real = { x: px(m.vol, vi), y: py(m.ret, vi) };
          var fora = noFoco && (real.x !== pos.x || real.y !== pos.y);
          var angulo = Math.atan2(real.y - pos.y, real.x - pos.x) * 180 / Math.PI;
          m.nota.seta.setAttribute('transform', 'translate(' + pos.x.toFixed(1) + ',' + pos.y.toFixed(1) +
            ') rotate(' + angulo.toFixed(1) + ') translate(' + (m.raio + 3) + ',0)');
          m.nota.seta.setAttribute('opacity', fora ? 1 : 0);
          m.nota.g.setAttribute('opacity', fase(t, T.foco + T.durFoco - 0.2, 0.6));
        }
      });

      // Nuvem em ondas.
      ondas.forEach(function (g, k) {
        var p = saida(fase(t, T.nuvem + k * T.passoOnda, T.durOnda));
        g.setAttribute('opacity', limitar(p * 1.8, 0, 1).toFixed(3));
        g.setAttribute('transform', p >= 1 ? '' : 'translate(' + centroNuvem.x.toFixed(1) + ',' +
          centroNuvem.y.toFixed(1) + ') scale(' + p.toFixed(4) + ') translate(' + (-centroNuvem.x).toFixed(1) +
          ',' + (-centroNuvem.y).toFixed(1) + ')');
      });

      // Fronteira e ótimas.
      var pFr = suave(fase(t, T.fronteira, T.durFronteira));
      caminho.setAttribute('stroke-dashoffset', (1 - pFr).toFixed(4));
      caminho.setAttribute('opacity', pFr > 0 ? 1 : 0);
      otimas.forEach(function (o) {
        var p = fase(t, o.inicio, T.durMarcador);
        var pulso = p < 1 ? 1 + 0.6 * Math.sin(Math.PI * p) : 1;
        o.ponto.setAttribute('opacity', p > 0 ? 1 : 0);
        o.ponto.setAttribute('r', (RAIO.otima * saida(p) * pulso).toFixed(2));
        o.rotulo.setAttribute('opacity', fase(t, o.inicio + 0.1, 0.4).toFixed(3));
      });

      // Em espera nada aparece, e visibility hidden (além de opacity 0) tira a
      // cena da medição do tools/check_slides.py: com a câmera próxima, os
      // elementos ainda transparentes passam da caixa do SVG.
      cena.setAttribute('visibility', t <= 0 ? 'hidden' : 'visible');
      elemento.dataset.fase = t >= FIM ? 'final' : (t <= 0 ? 'espera' : 'animando');
    }

    // Execução.
    var quadro = null;
    var semMovimento = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var impressao = /print-pdf/.test(window.location.search) ||
      document.documentElement.classList.contains('print-pdf');

    function parar() {
      if (quadro) cancelAnimationFrame(quadro);
      quadro = null;
    }

    function tocar() {
      parar();
      if (semMovimento || impressao) { aplicar(FIM); return; }
      var inicio = null;
      function passo(agora) {
        if (inicio === null) inicio = agora;
        var t = (agora - inicio) / 1000;
        aplicar(Math.min(t, FIM));
        quadro = t < FIM ? requestAnimationFrame(passo) : null;
      }
      aplicar(0);
      quadro = requestAnimationFrame(passo);
    }

    botao.addEventListener('click', tocar);
    elemento.carteiraNuvem = { ir: function (t) { parar(); aplicar(t); }, tocar: tocar, fim: FIM };

    var secao = elemento.closest('section');
    var reveal = window.Reveal && typeof window.Reveal.on === 'function' && secao ? window.Reveal : null;
    if (!reveal) {
      tocar();
      return;
    }
    if (semMovimento || impressao) aplicar(FIM); else aplicar(0);
    if (secao.classList.contains('present') && !impressao) tocar();
    reveal.on('slidechanged', function (evento) {
      if (evento.currentSlide === secao || secao.contains(evento.currentSlide)) {
        tocar();
      } else if (!semMovimento && !impressao) {
        parar();
        aplicar(0);
      }
    });
  });
})();
