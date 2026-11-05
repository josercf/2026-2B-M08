// Cena da simulação da moeda (Aula 02, slide da simulação): acompanha os passos
// do código linha a linha.
//
//   <div class="sim-cena" data-sim-cena data-caras="1101001110,0110100011,..."></div>
//
// Uma linha por jogador de exemplo, dez quadrados por rodada (verde é cara,
// coral é coroa). Passo 2: cada linha ganha a barra do saldo final, em escala
// log, com a linha dos R$ 100. Passo 3: as linhas se ordenam pelo saldo e
// aparecem a média e a mediana da amostra. O passo vem da quantidade de
// .codigo-passo visíveis na mesma section.
(function () {
  'use strict';

  var SVG = 'http://www.w3.org/2000/svg';
  function no(tag, attrs, pai) {
    var e = document.createElementNS(SVG, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (pai) pai.appendChild(e);
    return e;
  }
  function reais(v) {
    return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function montar(raiz) {
    var linhas = (raiz.dataset.caras || '').split(',').filter(Boolean).map(function (l) {
      return l.split('').map(function (c) { return c === '1'; });
    });
    var L = 800, ALTO = 15, GAP = 3, Q = 13;
    var A = linhas.length * (ALTO + GAP) + 24;
    var svg = no('svg', { viewBox: '0 0 ' + L + ' ' + A, class: 'sc-svg', 'aria-hidden': 'true' });
    raiz.appendChild(svg);

    var X0 = 210, X1 = 760;
    var MIN = Math.log10(0.5), MAX = Math.log10(6000);
    function x(v) { return X0 + (Math.log10(Math.max(v, 0.5)) - MIN) / (MAX - MIN) * (X1 - X0); }

    var saldos = linhas.map(function (l) {
      return l.reduce(function (s, c) { return s * (c ? 1.5 : 0.6); }, 100);
    });
    var ordem = saldos.map(function (_, i) { return i; }).sort(function (a, b) { return saldos[a] - saldos[b]; });
    var posicao = {};
    ordem.forEach(function (i, k) { posicao[i] = k; });

    var guia = no('g', { class: 'sc-guia' }, svg);
    no('line', { x1: x(100), y1: 0, x2: x(100), y2: A - 20, class: 'sc-cem' }, guia);
    no('text', { x: x(100), y: A - 4, 'text-anchor': 'middle', class: 'sc-rotulo' }, guia).textContent = 'R$ 100';

    var grupos = linhas.map(function (l, i) {
      var g = no('g', { class: 'sc-linha' }, svg);
      g.style.transform = 'translateY(' + (i * (ALTO + GAP)) + 'px)';
      l.forEach(function (cara, r) {
        var q = no('rect', { x: r * (Q + 3), y: 0, width: Q, height: ALTO, class: 'sc-q ' + (cara ? 'sc-cara' : 'sc-coroa') }, g);
        q.style.transitionDelay = (r * 40 + i * 15) + 'ms';
      });
      var barra = no('rect', { x: X0, y: 2, width: Math.max(2, x(saldos[i]) - X0), height: ALTO - 4,
        class: 'sc-barra ' + (saldos[i] >= 100 ? 'sc-ganha' : 'sc-perde') }, g);
      barra.style.transformOrigin = X0 + 'px 0';
      return g;
    });

    var media = saldos.reduce(function (a, b) { return a + b; }, 0) / saldos.length;
    var meio = ordem.length / 2;
    var mediana = ordem.length % 2 ? saldos[ordem[Math.floor(meio)]] : (saldos[ordem[meio - 1]] + saldos[ordem[meio]]) / 2;
    var marcas = no('g', { class: 'sc-marcas' }, svg);
    [[media, 'sc-media', 'Média ' + reais(media), -1], [mediana, 'sc-mediana', 'Mediana ' + reais(mediana), 1]]
      .forEach(function (m) {
        no('line', { x1: x(m[0]), y1: 0, x2: x(m[0]), y2: A - 20, class: m[1] }, marcas);
        no('text', { x: x(m[0]) + 6 * m[3], y: A - 4, 'text-anchor': m[3] < 0 ? 'end' : 'start', class: 'sc-rotulo ' + m[1] }, marcas)
          .textContent = m[2];
      });
    raiz.dataset.media = media.toFixed(2);
    raiz.dataset.mediana = mediana.toFixed(2);

    function passo(n) {
      raiz.dataset.passo = String(n);
      grupos.forEach(function (g, i) {
        var k = n >= 3 ? posicao[i] : i;
        g.style.transform = 'translateY(' + (k * (ALTO + GAP)) + 'px)';
      });
    }

    var secao = raiz.closest('section');
    function contar() {
      return secao ? secao.querySelectorAll('.codigo-passo.visible').length : 3;
    }
    if (window.Reveal && window.Reveal.on && secao) {
      ['fragmentshown', 'fragmenthidden', 'slidechanged', 'ready'].forEach(function (ev) {
        window.Reveal.on(ev, function () { passo(contar()); });
      });
    }
    passo(contar());
    raiz.dataset.pronto = 'sim';
  }

  function iniciar() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-sim-cena]'), montar);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
