// Heatmap da matriz de correlação da cesta. Cada célula é pintada pela
// correlação do par: verde para correlação negativa, base perto de zero e roxo
// para correlação positiva. Passar o cursor (ou tocar) numa célula escreve a
// leitura do par e os pregões em comum. Dados: tools/dados_widgets_aula03.py.
(function () {
  'use strict';

  // Converte a cor do token (hex de 6 dígitos ou rgb()) em [r, g, b].
  function rgb(valor) {
    var v = valor.trim();
    if (v.charAt(0) === '#') {
      return [1, 3, 5].map(function (i) { return parseInt(v.substr(i, 2), 16); });
    }
    return (v.match(/\d+/g) || [0, 0, 0]).slice(0, 3).map(Number);
  }

  function misturar(a, b, t) {
    return 'rgb(' + a.map(function (x, i) { return Math.round(x + (b[i] - x) * t); }).join(',') + ')';
  }

  function decimal(valor) {
    return valor.toFixed(2).replace('.', ',').replace('-', '\u2212');
  }

  function milhar(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  IntelIWidgets.registrar('heatmap-correlacao', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 640);
    var altura = Number(elemento.dataset.altura || 440);
    var tickers = dados.tickers;
    var n = tickers.length;
    var margem = { esquerda: 92, topo: 80 };
    var lado = Math.min((largura - margem.esquerda - 8) / n, (altura - margem.topo - 8) / n);

    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(canvas);
    elemento.appendChild(leitura);

    var base = rgb(api.cor('--seg-base'));
    var positiva = rgb(api.cor('--seg-primaria'));
    var negativa = rgb(api.cor('--seg-secundaria'));
    var selecionada = null;

    function corDaCelula(valor) {
      return valor >= 0 ? misturar(base, positiva, valor) : misturar(base, negativa, Math.min(1, -valor * 2));
    }

    function desenhar() {
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
      ctx.font = api.fonte(16, 600);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.textBaseline = 'middle';
      tickers.forEach(function (t, i) {
        ctx.textAlign = 'right';
        ctx.fillText(t, margem.esquerda - 6, margem.topo + lado * (i + 0.5));
        ctx.save();
        ctx.translate(margem.esquerda + lado * (i + 0.5), margem.topo - 6);
        ctx.rotate(-Math.PI / 3);
        ctx.textAlign = 'left';
        ctx.fillText(t, 0, 0);
        ctx.restore();
      });
      for (var i = 0; i < n; i++) {
        for (var j = 0; j < n; j++) {
          ctx.fillStyle = corDaCelula(dados.correlacao[i][j]);
          ctx.fillRect(margem.esquerda + lado * j, margem.topo + lado * i, lado - 1, lado - 1);
        }
      }
      // Escala de cor à direita da matriz, de -1 a 1.
      var barraX = margem.esquerda + lado * n + 24;
      var barraTopo = margem.topo;
      var barraAltura = lado * n;
      for (var k = 0; k < barraAltura; k++) {
        ctx.fillStyle = corDaCelula(1 - 2 * k / barraAltura);
        ctx.fillRect(barraX, barraTopo + k, 18, 1);
      }
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(16, 300);
      ctx.textAlign = 'left';
      [[1, '1'], [0, '0'], [-1, '\u22121']].forEach(function (marca) {
        ctx.fillText(marca[1], barraX + 24, barraTopo + barraAltura * (1 - marca[0]) / 2);
      });
      if (selecionada) {
        ctx.strokeStyle = api.cor('--seg-destaque');
        ctx.lineWidth = 3;
        ctx.strokeRect(margem.esquerda + lado * selecionada[1], margem.topo + lado * selecionada[0], lado - 1, lado - 1);
      }
    }

    function escolher(evento) {
      var p = api.ponto(evento, canvas);
      var j = Math.floor((p.x - margem.esquerda) / lado);
      var i = Math.floor((p.y - margem.topo) / lado);
      if (i < 0 || j < 0 || i >= n || j >= n) return;
      selecionada = [i, j];
      if (i === j) {
        leitura.textContent = tickers[i] + ' com ele mesmo: correlação 1, a diagonal da matriz.';
      } else {
        leitura.textContent = tickers[i] + ' com ' + tickers[j] + ': correlação ' +
          decimal(dados.correlacao[i][j]) + ' em ' + milhar(dados.pregoes[i][j]) + ' pregões em comum.';
      }
      desenhar();
    }

    canvas.addEventListener('mousemove', escolher);
    canvas.addEventListener('click', escolher);
    leitura.textContent = dados.leitura;
    desenhar();
  });
})();
