// Três visões de preço em volta de um evento corporativo, em SVG animado.
// Substitui o vídeo do slide da MGLU3 (Aula 01): antes do play, as linhas param
// na véspera do evento, para a turma prever; o play desenha o resto no tempo,
// para no dia do evento com o marcador e mostra a variação de cada linha.
//
// Markup:
//   <div class="widget" data-widget="visoes-evento" data-fonte="../assets/data/aula01-tres-visoes.json"
//        data-ticker="MGLU3" data-evento="2024-05-27" data-inicio="2023-12-01" data-fim="2024-09-30"
//        data-rotulo-evento="grupamento de 10 para 1" data-largura="1168" data-altura="400"></div>
// Dados: aula01-tres-visoes.json (tools/dados_widgets_aula01.py), nada digitado.
// Cor só por api.cor; nenhum número da variação fica no markup do deck.
(function () {
  'use strict';

  var SVG = 'http://www.w3.org/2000/svg';
  var SERIES = [
    { chave: 'negociado', nome: 'Negociado', cor: '--seg-destaque', largura: 4 },
    { chave: 'fechamento', nome: 'Close', cor: '--seg-primaria', largura: 5 },
    { chave: 'ajustado', nome: 'Adj Close', cor: '--seg-secundaria', largura: 5 }
  ];

  function no(tag, atributos, pai) {
    var e = document.createElementNS(SVG, tag);
    Object.keys(atributos || {}).forEach(function (k) { e.setAttribute(k, atributos[k]); });
    if (pai) pai.appendChild(e);
    return e;
  }

  function pct(v) {
    return (v >= 0 ? '+' : '') + (v * 100).toFixed(2).replace('.', ',') + '%';
  }

  function dataBr(iso) {
    var p = iso.split('-');
    return p[2] + '/' + p[1] + '/' + p[0];
  }

  IntelIWidgets.registrar('visoes-evento', function (elemento, dados, api) {
    var W = Number(elemento.dataset.largura || 1168);
    var H = Number(elemento.dataset.altura || 400);
    var ticker = elemento.dataset.ticker;
    var serieTicker = dados.tickers[ticker];
    var datas = dados.datas;
    var i0 = datas.findIndex(function (d) { return d >= elemento.dataset.inicio; });
    var i1 = datas.length - 1 - datas.slice().reverse().findIndex(function (d) { return d <= elemento.dataset.fim; });
    var iEvento = datas.indexOf(elemento.dataset.evento);
    var janela = datas.slice(i0, i1 + 1);
    var valores = SERIES.map(function (s) { return serieTicker[s.chave].slice(i0, i1 + 1); });

    var M = { esq: 70, dir: 170, topo: 20, base: 44 };
    var minimo = Infinity;
    var maximo = -Infinity;
    valores.forEach(function (l) {
      l.forEach(function (v) { if (v > 0) { minimo = Math.min(minimo, v); maximo = Math.max(maximo, v); } });
    });
    var lmin = Math.log10(minimo * 0.85);
    var lmax = Math.log10(maximo * 1.15);
    function x(i) { return M.esq + (i / (janela.length - 1)) * (W - M.esq - M.dir); }
    function y(v) { return M.topo + (1 - (Math.log10(v) - lmin) / (lmax - lmin)) * (H - M.topo - M.base); }

    elemento.innerHTML = '';
    var svg = no('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img',
      'aria-label': 'Três visões de preço da ' + ticker + ' em volta de ' + dataBr(elemento.dataset.evento) });
    elemento.appendChild(svg);
    function texto(t, atr, pai) {
      var e = no('text', Object.assign({ 'font-size': 14, 'font-weight': 600, fill: api.cor('--seg-texto') }, atr), pai);
      e.textContent = t;
      return e;
    }

    // Grade do eixo y em escala log, com rótulos em reais.
    var grade = no('g', {}, svg);
    for (var e = Math.floor(lmin); e <= Math.ceil(lmax); e++) {
      [1, 2, 5].forEach(function (m) {
        var v = m * Math.pow(10, e);
        if (Math.log10(v) < lmin || Math.log10(v) > lmax) return;
        no('line', { x1: M.esq, x2: W - M.dir, y1: y(v), y2: y(v), stroke: api.cor('--seg-borda'), 'stroke-width': 1 }, grade);
        texto('R$ ' + String(v).replace('.', ','), { x: M.esq - 10, y: y(v) + 5, 'text-anchor': 'end', 'font-weight': 300 }, grade);
      });
    }
    // Meses no eixo x.
    janela.forEach(function (d, i) {
      if (i === 0 || d.slice(5, 7) !== janela[i - 1].slice(5, 7)) {
        texto(d.slice(5, 7) + '/' + d.slice(2, 4), { x: x(i), y: H - 16, 'text-anchor': 'middle', 'font-weight': 300 }, grade);
      }
    });

    // Marcador do evento (aparece quando o tempo chega nele).
    var jEvento = iEvento - i0;
    var marcador = no('g', { opacity: 0 }, svg);
    no('line', { x1: x(jEvento), x2: x(jEvento), y1: M.topo, y2: H - M.base, stroke: api.cor('--seg-texto'),
      'stroke-width': 2, 'stroke-dasharray': '6 6' }, marcador);
    texto(dataBr(elemento.dataset.evento) + ': ' + (elemento.dataset.rotuloEvento || 'evento'),
      { x: x(jEvento) + 10, y: M.topo + 16, 'font-size': 16 }, marcador);

    var caminhos = SERIES.map(function (s) {
      return no('path', { fill: 'none', stroke: api.cor(s.cor), 'stroke-width': s.largura, 'stroke-linejoin': 'round' }, svg);
    });
    var rotulos = SERIES.map(function (s) { return texto(s.nome, { 'font-size': 16, fill: api.cor('--seg-texto') }, svg); });
    // Caixa da variação no dia do evento, no canto de baixo à direita, onde o
    // gráfico fica vazio depois do salto.
    var caixaVar = no('g', { opacity: 0 }, svg);
    no('rect', { x: x(jEvento) + 24, y: H - M.base - 112, width: 270, height: 100,
      fill: api.cor('--seg-base'), stroke: api.cor('--seg-borda'), 'stroke-width': 1 }, caixaVar);
    texto('Variação no dia ' + dataBr(elemento.dataset.evento), { x: x(jEvento) + 38, y: H - M.base - 88, 'font-size': 14 }, caixaVar);
    var variacoes = SERIES.map(function () { return texto('', { 'font-size': 16, 'font-weight': 700 }, caixaVar); });

    function desenhar(ate) {
      caminhos.forEach(function (c, k) {
        var d = '';
        for (var i = 0; i <= ate; i++) {
          var v = valores[k][i];
          if (!(v > 0)) continue;
          d += (d ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(v).toFixed(1);
        }
        c.setAttribute('d', d);
        var ult = valores[k][ate];
        rotulos[k].setAttribute('x', x(ate) + 10);
        // Rótulos empilhados na ordem da legenda, para não se sobreporem quando
        // as linhas se encontram (o negociado alcança o Close depois do evento).
        rotulos[k].setAttribute('y', y(ult) + 5 + (k - 1) * 18);
      });
      marcador.setAttribute('opacity', ate >= jEvento ? 1 : 0);
    }

    function mostrarVariacoes() {
      variacoes.forEach(function (t, k) {
        var antes = valores[k][jEvento - 1];
        var depois = valores[k][jEvento];
        t.textContent = SERIES[k].nome + ': ' + pct(depois / antes - 1);
        t.setAttribute('x', x(jEvento) + 38);
        t.setAttribute('y', H - M.base - 64 + k * 22);
        t.setAttribute('fill', api.cor(k === 0 ? '--seg-destaque' : '--seg-texto'));
      });
      caixaVar.setAttribute('opacity', 1);
    }

    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'visoes-evento-play';
    botao.textContent = 'Tocar';
    elemento.appendChild(botao);

    var quadro = null;
    function tocar() {
      if (quadro) cancelAnimationFrame(quadro);
      caixaVar.setAttribute('opacity', 0);
      var inicio = null;
      var pausa = 0;
      var DUR = 7000;
      var parado = false;
      botao.textContent = 'Repetir';
      function passo(agora) {
        if (inicio === null) inicio = agora;
        var t = Math.min(1, (agora - inicio - pausa) / DUR);
        var ate = Math.round(jEvento - 1 + t * (janela.length - jEvento));
        if (!parado && ate >= jEvento) {
          parado = true;
          desenhar(jEvento);
          mostrarVariacoes();
          var retoma = agora;
          quadro = requestAnimationFrame(function espera(a) {
            if (a - retoma < 1800) { quadro = requestAnimationFrame(espera); return; }
            pausa += a - retoma;
            quadro = requestAnimationFrame(passo);
          });
          return;
        }
        desenhar(Math.min(ate, janela.length - 1));
        if (t < 1) quadro = requestAnimationFrame(passo);
        else elemento.dataset.fase = 'final';
      }
      elemento.dataset.fase = 'tocando';
      quadro = requestAnimationFrame(passo);
    }
    botao.addEventListener('click', tocar);

    // Estado inicial: véspera do evento, para a previsão. Em ?print-pdf, o final.
    if (/print-pdf/.test(window.location.search)) {
      desenhar(janela.length - 1);
      mostrarVariacoes();
      elemento.dataset.fase = 'final';
    } else {
      desenhar(jEvento - 1);
      elemento.dataset.fase = 'previsao';
    }
    elemento.visoesEvento = { tocar: tocar, desenhar: desenhar };
  });
})();
