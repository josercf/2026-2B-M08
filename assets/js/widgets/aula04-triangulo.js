// Triângulo de pesos de três ativos da Aula 04. À esquerda, o triângulo em que
// cada ponto é uma carteira (os três pesos somam 1 e nenhum é negativo); à
// direita, o plano risco-retorno com todas as carteiras do trio em cinza e a
// carteira escolhida em destaque. Arrastar dentro do triângulo move o ponto, e
// retorno, volatilidade e Sharpe são recalculados em forma vetorial a partir
// das médias, da covariância e do CDI do JSON. O ótimo só aparece no botão,
// para a turma registrar a previsão antes. Dados: tools/dados_widgets_aula04.py.
(function () {
  'use strict';

  function pct(valor, casas) {
    return (valor * 100).toFixed(casas === undefined ? 2 : casas).replace('.', ',') + '%';
  }

  function num(valor) {
    return valor.toFixed(2).replace('.', ',');
  }

  function metricas(w, dados) {
    var ret = 0;
    var variancia = 0;
    for (var i = 0; i < 3; i++) {
      ret += w[i] * dados.mu[i];
      for (var j = 0; j < 3; j++) variancia += w[i] * w[j] * dados.cov[i][j];
    }
    var vol = Math.sqrt(variancia);
    return { ret: ret, vol: vol, sharpe: (ret - dados.rf) / vol };
  }

  IntelIWidgets.registrar('aula04-triangulo', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 360);
    var estado = { w: [1 / 3, 1 / 3, 1 / 3], otimo: false, arrastando: false };

    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    canvas.style.touchAction = 'none';
    canvas.style.cursor = 'crosshair';
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controles);
    elemento.appendChild(canvas);
    elemento.appendChild(leitura);

    function botao(texto, aoClicar) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = texto;
      b.addEventListener('click', aoClicar);
      controles.appendChild(b);
      return b;
    }

    botao('Pesos iguais', function () { estado.w = [1 / 3, 1 / 3, 1 / 3]; desenhar(); });
    dados.tickers.forEach(function (t, k) {
      botao('Só ' + t, function () {
        estado.w = [0, 0, 0];
        estado.w[k] = 1;
        desenhar();
      });
    });
    var botaoOtimo = botao('Mostrar ótimo', function () { estado.otimo = !estado.otimo; desenhar(); });

    // Triângulo: vértice de cima é o primeiro ticker, os de baixo, os outros dois.
    var lado = Math.min(360, (altura - 70) * 2 / Math.sqrt(3));
    var alturaTri = lado * Math.sqrt(3) / 2;
    var cx = 40 + lado / 2;
    var topo = 34;
    var V = [
      { x: cx, y: topo },
      { x: cx - lado / 2, y: topo + alturaTri },
      { x: cx + lado / 2, y: topo + alturaTri }
    ];

    function paraTela(w) {
      return {
        x: w[0] * V[0].x + w[1] * V[1].x + w[2] * V[2].x,
        y: w[0] * V[0].y + w[1] * V[1].y + w[2] * V[2].y
      };
    }

    function paraPesos(p) {
      var det = (V[1].y - V[2].y) * (V[0].x - V[2].x) + (V[2].x - V[1].x) * (V[0].y - V[2].y);
      var a = ((V[1].y - V[2].y) * (p.x - V[2].x) + (V[2].x - V[1].x) * (p.y - V[2].y)) / det;
      var b = ((V[2].y - V[0].y) * (p.x - V[2].x) + (V[0].x - V[2].x) * (p.y - V[2].y)) / det;
      var w = [a, b, 1 - a - b].map(function (x) { return Math.max(0, x); });
      var soma = w[0] + w[1] + w[2];
      return w.map(function (x) { return x / soma; });
    }

    // Plano risco-retorno à direita, com eixos fixos que cabem o trio inteiro.
    var nuvem = [];
    var passo = 0.025;
    for (var a = 0; a <= 1 + 1e-9; a += passo) {
      for (var b = 0; a + b <= 1 + 1e-9; b += passo) {
        nuvem.push(metricas([a, b, Math.max(0, 1 - a - b)], dados));
      }
    }
    var vols = nuvem.map(function (p) { return p.vol; });
    var rets = nuvem.map(function (p) { return p.ret; });
    var eixoX = [Math.floor(Math.min.apply(null, vols) * 20) / 20, Math.ceil(Math.max.apply(null, vols) * 20) / 20];
    var eixoY = [Math.floor(Math.min.apply(null, rets) * 20) / 20, Math.ceil(Math.max.apply(null, rets) * 20) / 20];
    var plano = { esquerda: 40 + lado + 120, direita: largura - 20, topo: 14, base: altura - 50 };

    function px(vol) {
      return plano.esquerda + (plano.direita - plano.esquerda) * (vol - eixoX[0]) / (eixoX[1] - eixoX[0]);
    }
    function py(ret) {
      return plano.base - (plano.base - plano.topo) * (ret - eixoY[0]) / (eixoY[1] - eixoY[0]);
    }

    function desenharTriangulo(ctx) {
      ctx.fillStyle = api.cor('--seg-superficie');
      ctx.strokeStyle = api.cor('--seg-primaria');
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(V[0].x, V[0].y);
      ctx.lineTo(V[1].x, V[1].y);
      ctx.lineTo(V[2].x, V[2].y);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(18, 700);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(dados.tickers[0], V[0].x, V[0].y - 6);
      ctx.textBaseline = 'top';
      ctx.fillText(dados.tickers[1], V[1].x, V[1].y + 8);
      ctx.fillText(dados.tickers[2], V[2].x, V[2].y + 8);
    }

    function desenharPlano(ctx) {
      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(plano.esquerda, plano.topo);
      ctx.lineTo(plano.esquerda, plano.base);
      ctx.lineTo(plano.direita, plano.base);
      ctx.stroke();
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(17, 300);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      for (var v = eixoX[0]; v <= eixoX[1] + 1e-9; v += 0.05) {
        ctx.fillText(pct(v, 0), px(v), plano.base + 6);
      }
      ctx.fillText('volatilidade anual', (plano.esquerda + plano.direita) / 2, altura - 22);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      for (var r = eixoY[0]; r <= eixoY[1] + 1e-9; r += 0.05) {
        ctx.fillText(pct(r, 0), plano.esquerda - 8, py(r));
      }
      ctx.fillStyle = api.cor('--seg-borda');
      nuvem.forEach(function (p) {
        ctx.beginPath();
        ctx.arc(px(p.vol), py(p.ret), 2.5, 0, 2 * Math.PI);
        ctx.fill();
      });
    }

    function ponto(ctx, x, y, raio, token) {
      ctx.fillStyle = api.cor(token);
      ctx.strokeStyle = api.cor('--seg-base');
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, raio, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }

    function desenhar() {
      botaoOtimo.classList.toggle('ativo', estado.otimo);
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
      desenharTriangulo(ctx);
      desenharPlano(ctx);

      var m = metricas(estado.w, dados);
      if (estado.otimo) {
        var o = dados.otima;
        var t = paraTela(o.pesos);
        ponto(ctx, t.x, t.y, 8, '--seg-primaria');
        ponto(ctx, px(o.vol), py(o.ret), 8, '--seg-primaria');
      }
      var p = paraTela(estado.w);
      ponto(ctx, p.x, p.y, 9, '--seg-destaque');
      ponto(ctx, px(m.vol), py(m.ret), 9, '--seg-destaque');

      var texto = dados.tickers.map(function (tk, k) { return tk + ' ' + pct(estado.w[k], 0); }).join(', ') +
        '. Retorno ' + pct(m.ret) + ', volatilidade ' + pct(m.vol) + ', Sharpe ' + num(m.sharpe) + '.';
      if (estado.otimo) {
        texto += ' Ótimo do SLSQP: Sharpe ' + num(dados.otima.sharpe) + '.';
      }
      leitura.textContent = texto;
    }

    function dentroDoTriangulo(q) {
      return q.x >= V[1].x - 20 && q.x <= V[2].x + 20 && q.y >= V[0].y - 20 && q.y <= V[1].y + 20;
    }

    canvas.addEventListener('pointerdown', function (evento) {
      var q = api.ponto(evento, canvas);
      if (!dentroDoTriangulo(q)) return;
      estado.arrastando = true;
      if (canvas.setPointerCapture) canvas.setPointerCapture(evento.pointerId);
      estado.w = paraPesos(q);
      desenhar();
    });
    canvas.addEventListener('pointermove', function (evento) {
      if (!estado.arrastando) return;
      estado.w = paraPesos(api.ponto(evento, canvas));
      desenhar();
    });
    ['pointerup', 'pointercancel'].forEach(function (tipo) {
      canvas.addEventListener(tipo, function () { estado.arrastando = false; });
    });

    desenhar();
  });
})();
