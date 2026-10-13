// ATENCAO, heranca da FIAP: o PDF gerado por este script (botao "Exportar
// PDF", URL com ?print-pdf) revela o gabarito de todos os quizzes do deck E de
// todas as escolhas de destino (.escolha). Esse PDF traz a resposta certa
// marcada e NAO deve ser distribuido para a turma antes da aula.
//
// Injeta um botao flutuante que reabre a URL atual com ?print-pdf, o
// parametro que o proprio Reveal.js usa para empilhar os slides em modo de
// impressao. Quando esse parametro esta presente, revela a resposta certa
// de cada quiz usando window.IntelIQuiz (exposto por inteli-quiz.js) em vez
// de reimplementar a logica de resposta. O JS nao declara cor nem fonte
// nenhuma aqui: a aparencia do botao vem de .print-button em
// inteli-theme.css.
(function () {
  'use strict';

  // Icone Sharp do sprite do brand kit (ICO-01), no mesmo endereco deste
  // script trocando js/ por icons/. currentScript so existe durante a carga.
  var SPRITE = ((document.currentScript && document.currentScript.src) || '')
    .replace(/js\/[^\/]*$/, 'icons/icones.svg');
  var SVG = 'http://www.w3.org/2000/svg';

  function criarIcone(nome) {
    var svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('class', 'icone');
    svg.setAttribute('aria-hidden', 'true');
    var uso = document.createElementNS(SVG, 'use');
    uso.setAttribute('href', SPRITE + '#' + nome);
    svg.appendChild(uso);
    return svg;
  }

  function urlDeImpressao() {
    var semQuery = window.location.href.split('?')[0].split('#')[0];
    return semQuery + '?print-pdf' + (window.location.hash || '');
  }

  function criarBotao() {
    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'print-button';
    botao.title = 'Exportar PDF';
    botao.setAttribute('aria-label', 'Exportar PDF');
    botao.appendChild(criarIcone('picture_as_pdf'));
    botao.addEventListener('click', function () {
      window.open(urlDeImpressao(), '_blank');
    });
    document.body.appendChild(botao);
  }

  function revelarGabarito() {
    if (!window.IntelIQuiz) return;
    var quizzes = document.querySelectorAll('.quiz-container');
    for (var i = 0; i < quizzes.length; i++) {
      var quiz = quizzes[i];
      // querySelectorAll, nao querySelector: um quiz pode ter mais de uma
      // opcao correta, e o gabarito do PDF precisa marcar todas, senao o
      // professor confere a aula com um gabarito incompleto. So a primeira
      // chamada passa por window.IntelIQuiz.responder (que grava
      // dataset.respondido e escreve o paragrafo de feedback); as demais
      // opcoes corretas so precisam da classe visual, adicionada direto.
      var corretas = quiz.querySelectorAll('[data-correct="true"]');
      for (var j = 0; j < corretas.length; j++) {
        if (j === 0) {
          window.IntelIQuiz.responder(quiz, corretas[j]);
        } else {
          corretas[j].classList.add('certa');
        }
      }
    }
  }

  function revelarEscolhas() {
    if (!window.IntelIEscolha) return;
    var blocos = document.querySelectorAll('.escolha');
    for (var i = 0; i < blocos.length; i++) {
      // Mesmo raciocinio do gabarito dos quizzes: marcar TODOS os destinos
      // aceitaveis, senao o professor confere a aula achando que a foto do
      // time tem uma resposta unica.
      var corretas = blocos[i].querySelectorAll('[data-correct="true"]');
      for (var j = 0; j < corretas.length; j++) {
        if (j === 0) {
          window.IntelIEscolha.responder(blocos[i], corretas[j]);
        } else {
          corretas[j].classList.add('certa');
        }
      }
    }
  }

  // No PDF o <video> sai como player vazio ou com a barra de controles por
  // cima do quadro. Troca cada video pelo poster dele, com a mesma classe e o
  // mesmo style, para o slide impresso mostrar o quadro que o professor
  // escolheu como capa da animacao.
  function trocarVideosPorPoster() {
    var videos = document.querySelectorAll('video');
    for (var i = 0; i < videos.length; i++) {
      var video = videos[i];
      var img = document.createElement('img');
      img.className = (video.className ? video.className + ' ' : '') + 'video-poster';
      var estilo = video.getAttribute('style');
      if (estilo) img.setAttribute('style', estilo);
      img.setAttribute('src', video.getAttribute('poster') || '');
      img.setAttribute('alt', video.getAttribute('aria-label') || 'Quadro inicial da animação');
      video.parentNode.replaceChild(img, video);
    }
  }

  function estaEmModoImpressao() {
    return window.location.search.indexOf('print-pdf') !== -1;
  }

  function iniciar() {
    criarBotao();
    if (estaEmModoImpressao()) {
      revelarGabarito();
      revelarEscolhas();
      trocarVideosPorPoster();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
