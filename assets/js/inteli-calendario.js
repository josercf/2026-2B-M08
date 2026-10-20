// Calendário que conta: cada alternativa de uma pergunta de contagem de dias
// vira uma animação em que os quadrados do calendário acendem, voam para o
// trilho da alternativa e o contador sobe até o número dela.
//
// Contrato de markup (ver o slide #fim-exclusivo da Aula 01):
//   <div data-calendario>
//     <div class="calendario-grade">
//       <span class="cal-dia [cal-end]" data-dia="31" data-pregao="sim|nao">31</span> ...
//     </div>
//     <p class="calendario-explica"></p>
//     <button class="contagem [contagem-certa]" data-dias="todos|pregoes"
//             data-exclui-end="sim|nao" data-explica="...">
//       <span class="contagem-valor" data-final="20">20</span>
//       <span class="contagem-trilho"></span>
//     </button>
//   </div>
//
// Sem JavaScript, o slide mostra os quatro números (estado final). Com
// JavaScript, os valores começam em "?" e cada clique anima uma alternativa.
// Em ?print-pdf e com movimento reduzido, tudo aparece já contado, sem voo.
// O elemento recebe data-pronto="sim" ao montar.
(function () {
  'use strict';

  var PASSO_MS = 55;     // intervalo entre a saída de dois quadrados
  var VOO_MS = 650;      // duração do voo de um quadrado até o trilho

  function semMovimento() {
    return /print-pdf/.test(window.location.search) ||
      (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function diasContados(raiz, botao) {
    var soPregoes = botao.dataset.dias === 'pregoes';
    var excluiEnd = botao.dataset.excluiEnd === 'sim';
    return Array.prototype.filter.call(raiz.querySelectorAll('.cal-dia'), function (dia) {
      if (soPregoes && dia.dataset.pregao !== 'sim') return false;
      if (excluiEnd && dia.classList.contains('cal-end')) return false;
      return true;
    });
  }

  // Posição de um elemento em coordenadas do slide (1280x720), descontando a
  // escala que o Reveal aplica com transform.
  function posicao(elemento, palco) {
    var r = elemento.getBoundingClientRect();
    var p = palco.getBoundingClientRect();
    var escala = p.width / palco.offsetWidth || 1;
    return {
      x: (r.left - p.left) / escala,
      y: (r.top - p.top) / escala,
      w: r.width / escala,
      h: r.height / escala
    };
  }

  function marcarCalendario(raiz, botao) {
    var soPregoes = botao.dataset.dias === 'pregoes';
    var excluiEnd = botao.dataset.excluiEnd === 'sim';
    raiz.querySelectorAll('.cal-dia').forEach(function (dia) {
      dia.classList.remove('cal-contado', 'cal-fora', 'cal-excluido');
      if (soPregoes && dia.dataset.pregao !== 'sim') dia.classList.add('cal-fora');
      if (excluiEnd && dia.classList.contains('cal-end')) dia.classList.add('cal-excluido');
    });
  }

  function explicar(raiz, botao) {
    var alvo = raiz.querySelector('.calendario-explica');
    if (!alvo) return;
    alvo.classList.remove('explica-visivel');
    // Força o reinício da transição de entrada do texto.
    void alvo.offsetWidth;
    alvo.textContent = botao.dataset.explica || '';
    alvo.classList.toggle('explica-certa', botao.classList.contains('contagem-certa'));
    alvo.classList.add('explica-visivel');
  }

  function preencherTrilho(botao, quantidade) {
    var trilho = botao.querySelector('.contagem-trilho');
    trilho.innerHTML = '';
    for (var i = 0; i < quantidade; i++) {
      var marca = document.createElement('span');
      marca.className = 'trilho-marca';
      trilho.appendChild(marca);
    }
  }

  function revelar(botao) {
    var valor = botao.querySelector('.contagem-valor');
    valor.textContent = valor.dataset.final;
    botao.classList.add('contagem-revelada');
    botao.classList.remove('contagem-andando');
  }

  function contarSemVoo(raiz, botao) {
    var dias = diasContados(raiz, botao);
    preencherTrilho(botao, dias.length);
    revelar(botao);
  }

  function contar(raiz, botao) {
    if (raiz.dataset.ocupado === 'sim') return;
    var dias = diasContados(raiz, botao);
    var palco = raiz.closest('section') || raiz;
    var valor = botao.querySelector('.contagem-valor');
    var trilho = botao.querySelector('.contagem-trilho');

    raiz.querySelectorAll('.contagem').forEach(function (b) { b.classList.remove('contagem-ativa'); });
    botao.classList.add('contagem-ativa', 'contagem-andando');
    botao.classList.remove('contagem-revelada');
    marcarCalendario(raiz, botao);

    if (semMovimento()) {
      dias.forEach(function (dia) { dia.classList.add('cal-contado'); });
      contarSemVoo(raiz, botao);
      explicar(raiz, botao);
      return;
    }

    raiz.dataset.ocupado = 'sim';
    trilho.innerHTML = '';
    valor.textContent = '0';

    var camada = palco.querySelector('.calendario-voos');
    if (!camada) {
      camada = document.createElement('div');
      camada.className = 'calendario-voos';
      palco.appendChild(camada);
    }

    var pousados = 0;
    dias.forEach(function (dia, i) {
      window.setTimeout(function () {
        dia.classList.add('cal-contado');
        var marca = document.createElement('span');
        marca.className = 'trilho-marca trilho-marca-espera';
        trilho.appendChild(marca);

        var de = posicao(dia, palco);
        var para = posicao(marca, palco);
        var voo = document.createElement('span');
        voo.className = 'calendario-voo';
        voo.style.left = de.x + 'px';
        voo.style.top = de.y + 'px';
        voo.style.width = de.w + 'px';
        voo.style.height = de.h + 'px';
        camada.appendChild(voo);

        var dx = para.x - de.x;
        var dy = para.y - de.y;
        var sx = para.w / de.w;
        var sy = para.h / de.h;
        var animacao = voo.animate([
          { transform: 'translate(0, 0) scale(1)', opacity: 0.95 },
          { transform: 'translate(' + dx * 0.5 + 'px, ' + (dy * 0.5 - 60) + 'px) scale(0.6)', opacity: 1, offset: 0.5 },
          { transform: 'translate(' + dx + 'px, ' + dy + 'px) scale(' + sx + ', ' + sy + ')', opacity: 1 }
        ], { duration: VOO_MS, easing: 'cubic-bezier(0.4, 0, 0.2, 1)', fill: 'forwards' });

        animacao.onfinish = function () {
          voo.remove();
          marca.classList.remove('trilho-marca-espera');
          pousados += 1;
          valor.textContent = String(pousados);
          if (pousados === dias.length) {
            revelar(botao);
            explicar(raiz, botao);
            raiz.dataset.ocupado = 'nao';
          }
        };
      }, i * PASSO_MS);
    });
  }

  function reiniciar(raiz) {
    if (raiz.dataset.ocupado === 'sim') return;
    raiz.querySelectorAll('.contagem').forEach(function (botao) {
      botao.classList.remove('contagem-ativa', 'contagem-revelada', 'contagem-andando');
      botao.querySelector('.contagem-valor').textContent = '?';
      botao.querySelector('.contagem-trilho').innerHTML = '';
    });
    raiz.querySelectorAll('.cal-dia').forEach(function (dia) {
      dia.classList.remove('cal-contado', 'cal-fora', 'cal-excluido');
    });
    var alvo = raiz.querySelector('.calendario-explica');
    if (alvo) {
      alvo.classList.remove('explica-visivel', 'explica-certa');
      alvo.textContent = alvo.dataset.inicial || '';
    }
  }

  function montar(raiz) {
    var alvo = raiz.querySelector('.calendario-explica');
    if (alvo) alvo.dataset.inicial = alvo.textContent;
    var botoes = raiz.querySelectorAll('.contagem');

    if (/print-pdf/.test(window.location.search)) {
      // PDF: as quatro alternativas contadas, a certa por último no calendário.
      botoes.forEach(function (botao) { contarSemVoo(raiz, botao); });
      var certa = raiz.querySelector('.contagem-certa');
      if (certa) {
        marcarCalendario(raiz, certa);
        diasContados(raiz, certa).forEach(function (dia) { dia.classList.add('cal-contado'); });
        explicar(raiz, certa);
      }
    } else {
      reiniciar(raiz);
    }

    botoes.forEach(function (botao) {
      botao.addEventListener('click', function (evento) {
        evento.stopPropagation();
        contar(raiz, botao);
      });
    });
    raiz.dataset.pronto = 'sim';
  }

  function iniciar() {
    document.querySelectorAll('[data-calendario]').forEach(montar);
    // Voltar ao slide recomeça a pergunta do zero.
    if (window.Reveal && window.Reveal.on) {
      window.Reveal.on('slidechanged', function (evento) {
        if (/print-pdf/.test(window.location.search)) return;
        var anterior = evento.previousSlide;
        if (anterior) anterior.querySelectorAll('[data-calendario]').forEach(reiniciar);
      });
    }
  }

  window.IntelICalendario = { contar: contar, reiniciar: reiniciar };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
