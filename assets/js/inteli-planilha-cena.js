// Cenas animadas da planilha do slide #planilha (Aula 03). Cada pergunta e cada
// resposta são fragmentos do Reveal; o número de fragmentos visíveis vira o
// atributo data-passo da cena, e o CSS decide qual planilha aparece e o que anima.
(function () {
  'use strict';

  function atualizar(secao) {
    var cena = secao.querySelector('.planilha-cena');
    if (!cena) return;
    cena.setAttribute('data-passo', String(secao.querySelectorAll('.fragment.visible').length));
  }

  function ligar() {
    var secao = document.getElementById('planilha');
    if (!secao) return;
    atualizar(secao);
    ['fragmentshown', 'fragmenthidden', 'slidechanged'].forEach(function (evento) {
      Reveal.on(evento, function () { atualizar(secao); });
    });
  }

  if (window.Reveal && typeof Reveal.isReady === 'function' && Reveal.isReady()) ligar();
  else if (window.Reveal) Reveal.on('ready', ligar);
})();
