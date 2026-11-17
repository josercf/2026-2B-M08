// Aula 04 em turnos (ADR-018). Dois componentes pequenos do deck do professor:
//
//   <div class="qr-fixo" data-qr="https://..."></div>
//     QR code de um endereço fixo, em SVG, com a cor do tema (aula04-turnos.css).
//     Sem a biblioteca qrcode-generator, mostra o endereço em texto.
//
//   <div class="spec-abas" data-spec-abas> botões com data-turno e data-grupo </div>
//   <div class="spec-projetor"> vários [data-adr-comite] com data-turno e data-grupo </div>
//     Mostra uma spec por vez no projetor. Os painéis são os de inteli-adr.js;
//     este script só troca qual deles está visível.
(function () {
  'use strict';

  var SVG = 'http://www.w3.org/2000/svg';

  function desenharQr(alvo) {
    var texto = alvo.dataset.qr;
    alvo.textContent = '';
    if (!window.qrcode) {
      var p = document.createElement('p');
      p.textContent = texto;
      alvo.appendChild(p);
      alvo.dataset.pronto = 'texto';
      return;
    }
    var qr = window.qrcode(0, 'M');
    qr.addData(texto);
    qr.make();
    var n = qr.getModuleCount();
    var borda = 2;
    var svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + (n + 2 * borda) + ' ' + (n + 2 * borda));
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'QR code de ' + texto);
    svg.setAttribute('shape-rendering', 'crispEdges');
    var fundo = document.createElementNS(SVG, 'rect');
    fundo.setAttribute('class', 'qr-fundo');
    fundo.setAttribute('width', n + 2 * borda);
    fundo.setAttribute('height', n + 2 * borda);
    svg.appendChild(fundo);
    var caminho = '';
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        if (qr.isDark(r, c)) caminho += 'M' + (c + borda) + ' ' + (r + borda) + 'h1v1h-1z';
      }
    }
    var modulo = document.createElementNS(SVG, 'path');
    modulo.setAttribute('class', 'qr-modulo');
    modulo.setAttribute('d', caminho);
    svg.appendChild(modulo);
    alvo.appendChild(svg);
    alvo.dataset.pronto = 'sim';
  }

  function montarAbas(abas) {
    var secao = abas.closest('section') || document;
    var paineis = secao.querySelectorAll('.spec-projetor [data-adr-comite]');
    var estado = { turno: abas.dataset.turno || '4', grupo: abas.dataset.grupo || 'G01' };

    function pintar() {
      Array.prototype.forEach.call(abas.querySelectorAll('button'), function (b) {
        var ativo = b.dataset.turno ? b.dataset.turno === estado.turno : b.dataset.grupo === estado.grupo;
        b.setAttribute('aria-pressed', ativo ? 'true' : 'false');
      });
      Array.prototype.forEach.call(paineis, function (p) {
        p.hidden = !(p.dataset.turno === estado.turno && p.dataset.grupo === estado.grupo);
      });
    }

    abas.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      if (b.dataset.turno) estado.turno = b.dataset.turno;
      if (b.dataset.grupo) estado.grupo = b.dataset.grupo;
      pintar();
    });
    pintar();
  }

  function iniciar() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-qr]'), desenharQr);
    Array.prototype.forEach.call(document.querySelectorAll('[data-spec-abas]'), montarAbas);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
