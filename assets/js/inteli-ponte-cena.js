// Cenas dos slides da ponte (Aula 02): o gráfico se monta junto com os passos do
// código linha a linha. O passo é a quantidade de .codigo-passo visíveis na
// section, como em inteli-sim-cena.js.
//
//   <div class="ponte-cena" data-ponte-cena data-modo="caminho" data-serie='{...}' data-rotulos='{...}'></div>
//
// modo "caminho": retornos anuais (passo 1), R$ 100 pela média aritmética
//   (passo 2), R$ 100 vividos por quem segurou (passo 3) e o imposto da
//   volatilidade (passo 4).
// modo "aportes": dinheiro aportado (passo 1), saldo de fim de ano (passo 2) e
//   a taxa interna de retorno (passo 3).
// Todos os números chegam prontos pelo markup, gerados de tools/medidas_aula02.py.
(function () {
  'use strict';

  var SVG = 'http://www.w3.org/2000/svg';
  function no(tag, attrs, pai, texto) {
    var e = document.createElementNS(SVG, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (texto !== undefined) e.textContent = texto;
    if (pai) pai.appendChild(e);
    return e;
  }
  function pct(v) { return (v > 0 ? '+' : '') + (v * 100).toFixed(1).replace('.', ',') + '%'; }

  function caminho(svg, d, rot, L, A) {
    var anos = d.anos, X0 = 60, X1 = L - 215, Y0 = A - 60, Y1 = 30, MIN = 45, MAX = 140;
    function x(i) { return X0 + i / (anos.length - 1) * (X1 - X0); }
    function y(v) { return Y0 - (v - MIN) / (MAX - MIN) * (Y0 - Y1); }
    var eixo = no('g', { class: 'pc-eixo' }, svg);
    no('line', { x1: X0, y1: y(100), x2: X1, y2: y(100), class: 'pc-cem' }, eixo);
    no('text', { x: X0 - 8, y: y(100) + 5, 'text-anchor': 'end', class: 'pc-rot' }, eixo, 'R$ 100');
    anos.forEach(function (ano, i) { no('text', { x: x(i), y: A - 34, 'text-anchor': 'middle', class: 'pc-rot' }, eixo, String(ano)); });

    var g1 = no('g', { class: 'pc-p1' }, svg);
    d.anuais.forEach(function (r, i) {
      no('text', { x: x(i + 1), y: A - 14, 'text-anchor': 'middle', class: 'pc-ano ' + (r >= 0 ? 'pc-pos' : 'pc-neg') }, g1, pct(r));
    });

    function linha(valores, classe, grupo) {
      var pts = valores.map(function (v, i) { return x(i) + ',' + y(v); }).join(' ');
      no('polyline', { points: pts, class: classe }, grupo);
    }
    var g2 = no('g', { class: 'pc-p2' }, svg);
    linha(d.promessa, 'pc-promessa', g2);
    no('text', { x: X1 + 12, y: y(d.promessa[d.promessa.length - 1]) + 6, class: 'pc-fim pc-verde' }, g2, rot.promessa);

    var g3 = no('g', { class: 'pc-p3' }, svg);
    linha(d.vivido, 'pc-vivido', g3);
    d.vivido.forEach(function (v, i) { no('circle', { cx: x(i), cy: y(v), r: 5, class: 'pc-ponto' }, g3); });
    no('text', { x: X1 + 12, y: y(d.vivido[d.vivido.length - 1]) + 6, class: 'pc-fim pc-coral' }, g3, rot.vivido);
    var u = d.vivido.length - 1;
    no('line', { x1: X1 + 4, y1: y(d.promessa[u]) + 4, x2: X1 + 4, y2: y(d.vivido[u]) - 4, class: 'pc-vao' }, g3);

    var g4 = no('g', { class: 'pc-p4' }, svg);
    no('rect', { x: X0 + 10, y: Y1 - 18, width: 520, height: 34, class: 'pc-caixa' }, g4);
    no('text', { x: X0 + 24, y: Y1 + 5, class: 'pc-imposto' }, g4, rot.imposto);
  }

  function aportes(svg, d, rot, L, A) {
    var n = d.aportado.length, X0 = 60, X1 = L - 40, Y0 = A - 40, Y1 = 40, MAX = 900;
    var passo = (X1 - X0) / n, larg = passo * 0.32;
    function y(v) { return Y0 - v / MAX * (Y0 - Y1); }
    var eixo = no('g', { class: 'pc-eixo' }, svg);
    no('line', { x1: X0, y1: Y0, x2: X1, y2: Y0, class: 'pc-base' }, eixo);
    d.anos.slice(1).forEach(function (ano, i) {
      no('text', { x: X0 + passo * (i + 0.5), y: A - 14, 'text-anchor': 'middle', class: 'pc-rot' }, eixo, String(ano));
    });
    var g1 = no('g', { class: 'pc-p1' }, svg);
    var g2 = no('g', { class: 'pc-p2' }, svg);
    d.aportado.forEach(function (v, i) {
      var cx = X0 + passo * (i + 0.5);
      no('rect', { x: cx - larg - 3, y: y(v), width: larg, height: Y0 - y(v), class: 'pc-aportado' }, g1);
      var s = d.saldo[i];
      no('rect', { x: cx + 3, y: y(s), width: larg, height: Y0 - y(s), class: 'pc-saldo ' + (s >= v ? 'pc-ganho' : 'pc-perda') }, g2);
    });
    no('text', { x: X0 + passo * (n - 0.5) + 3 + larg / 2, y: y(d.saldo[n - 1]) - 10, 'text-anchor': 'middle', class: 'pc-fim pc-verde' }, g2, rot.saldo);
    var g3 = no('g', { class: 'pc-p3' }, svg);
    no('rect', { x: X0 + 10, y: Y1 + 14, width: 560, height: 36, class: 'pc-caixa' }, g3);
    no('text', { x: X0 + 24, y: Y1 + 38, class: 'pc-imposto' }, g3, rot.tir);
    var leg = no('g', { class: 'pc-legenda' }, svg);
    no('rect', { x: X0 + 10, y: 4, width: 16, height: 16, class: 'pc-aportado' }, leg);
    no('text', { x: X0 + 32, y: 18, class: 'pc-rot' }, leg, 'aportado');
    no('rect', { x: X0 + 130, y: 4, width: 16, height: 16, class: 'pc-saldo pc-ganho' }, leg);
    no('text', { x: X0 + 152, y: 18, class: 'pc-rot' }, leg, 'saldo no fim do ano');
  }

  function montar(raiz) {
    var d = JSON.parse(raiz.dataset.serie);
    var rot = JSON.parse(raiz.dataset.rotulos || '{}');
    var L = Number(raiz.dataset.largura || 800), A = Number(raiz.dataset.altura || 260);
    var svg = no('svg', { viewBox: '0 0 ' + L + ' ' + A, class: 'pc-svg', 'aria-hidden': 'true' });
    raiz.appendChild(svg);
    (raiz.dataset.modo === 'aportes' ? aportes : caminho)(svg, d, rot, L, A);

    var secao = raiz.closest('section');
    function passo() {
      raiz.dataset.passo = String(secao ? secao.querySelectorAll('.codigo-passo.visible').length : 9);
    }
    if (window.Reveal && window.Reveal.on && secao) {
      ['fragmentshown', 'fragmenthidden', 'slidechanged', 'ready'].forEach(function (ev) { window.Reveal.on(ev, passo); });
    }
    passo();
    raiz.dataset.pronto = 'sim';
  }

  function iniciar() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-ponte-cena]'), montar);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
