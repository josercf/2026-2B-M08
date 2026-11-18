// Aula 04 em turnos (ADR-018). Componentes pequenos do deck do professor:
//
//   <div class="qr-fixo" data-qr="https://..."></div>
//     QR code de um endereço fixo, em SVG, com a cor do tema (aula04-turnos.css).
//     Sem a biblioteca qrcode-generator, mostra o endereço em texto.
//
//   <div class="spec-abas" data-spec-abas> botões com data-turno e data-grupo </div>
//   <div class="spec-projetor"> vários [data-adr-comite] com data-turno e data-grupo </div>
//     Mostra uma spec por vez no projetor. Os painéis são os de inteli-adr.js;
//     este script só troca qual deles está visível.
//
//   <div data-ampulheta-espera></div>   (dentro de section[data-atividade])
//     Ampulheta cheia e parada no lugar em que a do cronômetro aparece.
//
//   <button type="button" class="copiar" data-copiar="python conferir.py 1">...</button>
//     Copia o texto para a área de transferência.
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
      // Visão somente leitura da spec em projeção (aulas/aula04-spec.html?ver=1),
      // sem token: o endereço não dá permissão de edição.
      var ver = abas.querySelector('[data-spec-ver]');
      if (ver) {
        var demo = /[?&]quiz-demo=1/.test(window.location.search) ? '&quiz-demo=1' : '';
        ver.href = 'aula04-spec.html?g=' + estado.grupo + '&turno=' + estado.turno + '&ver=1' + demo;
      }
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

  // Ampulheta em espera: o mesmo desenho da ampulheta do cronômetro
  // (inteli-cronometro.js), cheia e parada, no lugar em que a de verdade
  // aparece quando o professor inicia o tempo. Assim o slide de atividade não
  // muda de layout no primeiro play.
  function desenharEspera(alvo) {
    alvo.setAttribute('aria-hidden', 'true');
    alvo.innerHTML =
      '<svg viewBox="0 0 120 190">' +
      '<path class="ampulheta-vidro" d="M14 22 H106 Q106 60 64 95 Q106 130 106 168 H14 Q14 130 56 95 Q14 60 14 22 Z"/>' +
      '<path class="ampulheta-areia" d="M14 22 H106 Q106 60 64 92 H56 Q14 60 14 22 Z"/>' +
      '<rect class="ampulheta-moldura" x="4" y="8" width="112" height="14"/>' +
      '<rect class="ampulheta-moldura" x="4" y="168" width="112" height="14"/>' +
      '</svg>';
  }

  // Antes de o cronômetro criar a ampulheta, grava no slide a posição da
  // ampulheta em espera. offsetTop e offsetLeft não sofrem a escala do Reveal.
  function posicionarAmpulheta(ev) {
    var botao = ev.target.closest ? ev.target.closest('.cronometro-play') : null;
    var secao = botao && botao.closest('section[data-atividade]');
    var espera = secao && secao.querySelector('[data-ampulheta-espera]');
    if (!espera) return;
    var topo = 0;
    var esquerda = 0;
    for (var no = espera; no && no !== secao; no = no.offsetParent) {
      topo += no.offsetTop;
      esquerda += no.offsetLeft;
    }
    secao.style.setProperty('--ampulheta-topo', topo + 'px');
    secao.style.setProperty('--ampulheta-esquerda', esquerda + 'px');
    secao.style.setProperty('--ampulheta-largura', espera.offsetWidth + 'px');
  }

  // Bloco copiável: <button class="copiar" data-copiar="texto">. O rótulo de
  // confirmação fica em data-copiado por 1,5 s (aula04-turnos.css).
  function copiar(ev) {
    var botao = ev.target.closest ? ev.target.closest('button[data-copiar]') : null;
    if (!botao) return;
    var texto = botao.dataset.copiar;
    var feito = function () {
      botao.dataset.copiado = 'sim';
      setTimeout(function () { delete botao.dataset.copiado; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(feito, function () { botao.dataset.copiado = 'falhou'; });
    } else {
      botao.dataset.copiado = 'falhou';
    }
  }

  function iniciar() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-qr]'), desenharQr);
    Array.prototype.forEach.call(document.querySelectorAll('[data-spec-abas]'), montarAbas);
    Array.prototype.forEach.call(document.querySelectorAll('[data-ampulheta-espera]'), desenharEspera);
    document.addEventListener('click', posicionarAmpulheta, true);
    document.addEventListener('click', copiar);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
