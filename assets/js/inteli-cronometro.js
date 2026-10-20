// Cronometro regressivo das atividades cronometradas do deck. O JS nao
// declara cor nem fonte: a aparencia vem de .cronometro em inteli-theme.css,
// e o estado de tempo esgotado e a classe .esgotado, nao um estilo inline,
// senao tools/check_brand.py acusa cor literal.
//
// Contrato de markup, no deck:
//   <div class="cronometro" data-minutos="4"></div>
// Com data-ampulheta, o primeiro play faz nascer do cronometro uma ampulheta
// que ocupa cerca de 1/6 da largura do slide, com a areia acompanhando o tempo
// restante; o slide ganha a classe .com-ampulheta para abrir espaco a ela.
// Com data-marcos="6" e data-marco-texto="Troquem de papel", quando o tempo
// decorrido chega a 6 minutos o cronometro toca tres bipes (Web Audio, sem
// arquivo), mostra uma faixa com o texto e destaca o item do slide marcado
// com data-marco="6". Varios marcos: data-marcos="4,8".
// O conteudo interno (botao e display) e construido aqui, para o slide nao
// carregar markup que so o JS entende.
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

  function trocarIcone(svg, nome) {
    svg.firstChild.setAttribute('href', SPRITE + '#' + nome);
  }

  function formatar(segundos) {
    var m = Math.floor(segundos / 60);
    var s = segundos % 60;
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  // Ampulheta em SVG: dois bulbos recortados por clipPath, a areia de cima
  // desce e a de baixo sobe conforme a fracao restante. Cor so por classe.
  var contadorAmpulheta = 0;
  function criarAmpulheta() {
    contadorAmpulheta += 1;
    var id = 'ampulheta-' + contadorAmpulheta;
    var caixa = document.createElement('div');
    caixa.className = 'ampulheta';
    caixa.setAttribute('aria-hidden', 'true');
    caixa.innerHTML =
      '<svg viewBox="0 0 120 190">' +
      '<defs>' +
      '<clipPath id="' + id + '-cima"><path d="M14 22 H106 Q106 60 64 92 H56 Q14 60 14 22 Z"/></clipPath>' +
      '<clipPath id="' + id + '-baixo"><path d="M56 98 H64 Q106 130 106 168 H14 Q14 130 56 98 Z"/></clipPath>' +
      '</defs>' +
      '<path class="ampulheta-vidro" d="M14 22 H106 Q106 60 64 95 Q106 130 106 168 H14 Q14 130 56 95 Q14 60 14 22 Z"/>' +
      '<rect class="ampulheta-areia ampulheta-areia-cima" clip-path="url(#' + id + '-cima)" x="10" y="22" width="100" height="70"/>' +
      '<rect class="ampulheta-areia ampulheta-areia-baixo" clip-path="url(#' + id + '-baixo)" x="10" y="168" width="100" height="0"/>' +
      '<line class="ampulheta-filete" x1="60" y1="92" x2="60" y2="168"/>' +
      '<rect class="ampulheta-moldura" x="4" y="8" width="112" height="14"/>' +
      '<rect class="ampulheta-moldura" x="4" y="168" width="112" height="14"/>' +
      '</svg>';
    return caixa;
  }

  function pintarAmpulheta(amp, fracao) {
    var cima = amp.querySelector('.ampulheta-areia-cima');
    var baixo = amp.querySelector('.ampulheta-areia-baixo');
    var filete = amp.querySelector('.ampulheta-filete');
    var hCima = 70 * fracao;
    var hBaixo = 70 * (1 - fracao);
    cima.setAttribute('y', String(92 - hCima));
    cima.setAttribute('height', String(hCima));
    baixo.setAttribute('y', String(168 - hBaixo));
    baixo.setAttribute('height', String(hBaixo));
    filete.setAttribute('y2', String(168 - hBaixo));
  }

  // Tres bipes curtos em 880 Hz. O AudioContext nasce no clique do play, que
  // e o gesto do usuario que o navegador exige para tocar som.
  var audio = null;
  function prepararAudio() {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!audio && Ctx) audio = new Ctx();
    if (audio && audio.state === 'suspended') audio.resume();
  }

  function tocarAlarme() {
    if (!audio) return;
    var agora = audio.currentTime;
    for (var i = 0; i < 3; i++) {
      var osc = audio.createOscillator();
      var ganho = audio.createGain();
      osc.type = 'square';
      osc.frequency.value = 880;
      var inicio = agora + i * 0.35;
      ganho.gain.setValueAtTime(0.0001, inicio);
      ganho.gain.exponentialRampToValueAtTime(0.25, inicio + 0.02);
      ganho.gain.exponentialRampToValueAtTime(0.0001, inicio + 0.25);
      osc.connect(ganho);
      ganho.connect(audio.destination);
      osc.start(inicio);
      osc.stop(inicio + 0.27);
    }
  }

  function montar(caixa) {
    var total = Math.round(parseFloat(caixa.dataset.minutos || '5') * 60);
    var restante = total;
    var timer = null;

    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'cronometro-play';
    var icone = criarIcone('play_arrow');
    botao.appendChild(icone);

    var display = document.createElement('p');
    display.className = 'cronometro-tempo';
    display.textContent = formatar(restante);

    // aria-live no display, e nao no container: o container so muda de classe,
    // e quem le em voz alta precisa do texto do tempo, nao do widget inteiro.
    display.setAttribute('aria-live', 'polite');

    caixa.appendChild(botao);
    caixa.appendChild(display);

    var marcos = String(caixa.dataset.marcos || '').split(',')
      .map(function (m) { return Math.round(parseFloat(m) * 60); })
      .filter(function (m) { return m > 0 && m < total; });
    var tocados = {};

    function dispararMarco(segundos) {
      tocarAlarme();
      var secaoMarco = caixa.closest('section');
      if (!secaoMarco) return;
      var faixa = secaoMarco.querySelector('.cronometro-marco');
      if (!faixa) {
        faixa = document.createElement('div');
        faixa.className = 'cronometro-marco';
        faixa.setAttribute('role', 'alert');
        secaoMarco.appendChild(faixa);
      }
      faixa.textContent = caixa.dataset.marcoTexto || 'Marco do cronometro';
      faixa.classList.remove('cronometro-marco-ativo');
      void faixa.offsetWidth;
      faixa.classList.add('cronometro-marco-ativo');
      var minutos = String(segundos / 60);
      secaoMarco.querySelectorAll('[data-marco="' + minutos + '"]').forEach(function (item) {
        item.classList.remove('marco-alcancado');
        void item.offsetWidth;
        item.classList.add('marco-alcancado');
      });
      caixa.dataset.ultimoMarco = minutos;
    }

    var ampulheta = null;
    var secao = caixa.closest('section');
    function mostrarAmpulheta() {
      if (!('ampulheta' in caixa.dataset) || !secao) return;
      if (!ampulheta) {
        ampulheta = criarAmpulheta();
        secao.appendChild(ampulheta);
        // Nasce no lugar do cronometro: a escala e o deslocamento iniciais
        // saem da posicao dele, e a transicao leva a ampulheta ao lugar final.
        var c = caixa.getBoundingClientRect();
        var s = secao.getBoundingClientRect();
        var escala = s.width / secao.offsetWidth || 1;
        var alvo = ampulheta.getBoundingClientRect();
        var dx = ((c.left + c.width / 2) - (alvo.left + alvo.width / 2)) / escala;
        var dy = ((c.top + c.height / 2) - (alvo.top + alvo.height / 2)) / escala;
        ampulheta.style.setProperty('--de-x', dx + 'px');
        ampulheta.style.setProperty('--de-y', dy + 'px');
      }
      pintarAmpulheta(ampulheta, restante / total);
      secao.classList.add('com-ampulheta');
      ampulheta.classList.remove('ampulheta-virada');
      void ampulheta.offsetWidth;
      ampulheta.classList.add('ampulheta-visivel');
    }

    function parar() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    function pintar() {
      display.textContent = formatar(restante);
      botao.setAttribute(
        'aria-label',
        timer ? 'Pausar o cronometro' : 'Iniciar o cronometro'
      );
    }

    function tique() {
      restante = restante - 1;
      var decorrido = total - restante;
      marcos.forEach(function (m) {
        if (decorrido >= m && !tocados[m]) { tocados[m] = true; dispararMarco(m); }
      });
      if (restante <= 0) {
        restante = 0;
        parar();
        caixa.classList.add('esgotado');
        trocarIcone(icone, 'replay');
        if (ampulheta) ampulheta.classList.add('ampulheta-virada');
      }
      if (ampulheta) {
        pintarAmpulheta(ampulheta, restante / total);
        ampulheta.classList.toggle('ampulheta-parada', !timer);
      }
      pintar();
    }

    function alternar() {
      // Tempo esgotado: o proximo clique reinicia. Sem isto, o cronometro so
      // volta ao inicio recarregando o deck, no meio da aula.
      if (restante === 0) {
        restante = total;
        caixa.classList.remove('esgotado');
        trocarIcone(icone, 'play_arrow');
        tocados = {};
        if (ampulheta) {
          ampulheta.classList.remove('ampulheta-virada');
          pintarAmpulheta(ampulheta, 1);
        }
        pintar();
        return;
      }
      if (timer) {
        parar();
        trocarIcone(icone, 'play_arrow');
      } else {
        if (marcos.length) prepararAudio();
        timer = setInterval(tique, 1000);
        trocarIcone(icone, 'pause');
        mostrarAmpulheta();
      }
      if (ampulheta) ampulheta.classList.toggle('ampulheta-parada', !timer);
      pintar();
    }

    botao.addEventListener('click', alternar);
    pintar();

    return { alternar: alternar, parar: parar, marco: dispararMarco };
  }

  function iniciar() {
    var caixas = document.querySelectorAll('.cronometro');
    for (var i = 0; i < caixas.length; i++) {
      montar(caixas[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
