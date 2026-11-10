// Cenas animadas por fragmentos (Aula 03): a planilha do slide #planilha e o ciclo do TDD.
// O número de fragmentos visíveis da seção vira o atributo data-passo da cena, e o CSS
// decide o que aparece e o que anima.
(function () {
  'use strict';

  var CENAS = '.planilha-cena, .passos-cena';

  function atualizar(secao) {
    var passo = String(secao.querySelectorAll('.fragment.visible').length);
    secao.querySelectorAll(CENAS).forEach(function (cena) { cena.setAttribute('data-passo', passo); });
  }

  function ligar() {
    var secoes = Array.prototype.filter.call(document.querySelectorAll('.reveal .slides section'),
      function (secao) { return secao.querySelector(CENAS); });
    if (!secoes.length) return;
    function todas() { secoes.forEach(atualizar); }
    todas();
    ['fragmentshown', 'fragmenthidden', 'slidechanged'].forEach(function (evento) { Reveal.on(evento, todas); });
  }

  if (window.Reveal && typeof Reveal.isReady === 'function' && Reveal.isReady()) ligar();
  else if (window.Reveal) Reveal.on('ready', ligar);
})();
