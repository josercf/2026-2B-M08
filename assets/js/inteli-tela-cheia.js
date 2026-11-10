// Botão de tela cheia dos decks. O Reveal já entra em tela cheia pela tecla F e o
// navegador sai pelo Esc; o botão deixa o recurso visível, no canto inferior esquerdo,
// e também sai da tela cheia. Sem suporte do navegador (iPhone, por exemplo) não aparece.
(function () {
  'use strict';

  if (!document.fullscreenEnabled) return;

  var SPRITE = '../assets/icons/icones.svg#';
  var botao = document.createElement('button');
  botao.type = 'button';
  botao.className = 'tela-cheia';

  function icone(nome) {
    return '<svg class="icone" aria-hidden="true"><use href="' + SPRITE + nome + '"></use></svg>';
  }

  function atualizar() {
    var cheia = Boolean(document.fullscreenElement);
    var rotulo = cheia ? 'Sair da tela cheia (Esc)' : 'Tela cheia (F)';
    botao.innerHTML = icone(cheia ? 'fullscreen_exit' : 'fullscreen');
    botao.setAttribute('aria-label', rotulo);
    botao.title = rotulo;
  }

  botao.addEventListener('click', function () {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen();
    // Sem foco no botão, Espaço e Enter continuam avançando os slides.
    botao.blur();
  });
  document.addEventListener('fullscreenchange', atualizar);

  atualizar();
  document.body.appendChild(botao);
})();
