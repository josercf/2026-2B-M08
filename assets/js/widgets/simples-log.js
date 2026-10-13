// Retorno simples contra retorno logarítmico nos oito maiores movimentos diários
// de um ativo. Barras agrupadas por pregão: a barra do simples aparece de saída e
// a do log só depois do botão "Revelar log", para a turma registrar a previsão
// antes. data-log="sim" no markup abre com o log já revelado (material de apoio).
// Dados: tools/dados_widgets_aula02.py.
(function () {
  'use strict';

  function porcentagem(valor) {
    return (valor * 100).toFixed(2).replace('.', ',') + '%';
  }

  function dataCurta(texto) {
    var p = texto.split('-');
    return p[2] + '/' + p[1] + '/' + p[0].slice(2);
  }

  IntelIWidgets.registrar('simples-log', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 300);
    var tickers = Object.keys(dados.tickers);
    var estado = {
      ticker: elemento.dataset.inicial || tickers[0],
      log: elemento.dataset.log === 'sim'
    };

    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
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

    var botoesTicker = tickers.map(function (t) {
      return botao(t, function () { estado.ticker = t; desenhar(); });
    });
    var botaoLog = botao('Revelar log', function () { estado.log = !estado.log; desenhar(); });

    function desenhar() {
      botoesTicker.forEach(function (b, i) { b.classList.toggle('ativo', tickers[i] === estado.ticker); });
      botaoLog.classList.toggle('ativo', estado.log);
      botaoLog.textContent = estado.log ? 'Esconder log' : 'Revelar log';

      var movimentos = dados.tickers[estado.ticker].movimentos;
      var ctx = canvas.getContext('2d');
      var margem = { esquerda: 20, direita: 20, topo: 30, base: 30 };
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);

      // Escala simétrica em torno do zero, pelo maior valor absoluto do ativo
      // (com o log incluído mesmo escondido, para a escala não pular no clique).
      var limite = 0;
      movimentos.forEach(function (m) {
        limite = Math.max(limite, Math.abs(m.simples), Math.abs(m.log));
      });
      var util = altura - margem.topo - margem.base;
      var zero = margem.topo + util / 2;
      // Folga de 25% acima do maior valor, para o rótulo da barra mais longa
      // não encostar na legenda nem nas datas do eixo.
      function py(v) { return zero - (util / 2) * v / (limite * 1.25); }

      var grupo = (largura - margem.esquerda - margem.direita) / movimentos.length;
      var barra = grupo * 0.4;

      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, zero);
      ctx.lineTo(largura - margem.direita, zero);
      ctx.stroke();

      ctx.font = api.fonte(12, 600);
      ctx.textAlign = 'center';
      movimentos.forEach(function (m, i) {
        var centro = margem.esquerda + grupo * (i + 0.5);
        var series = [{ valor: m.simples, token: '--seg-primaria', x: centro - barra - 2 }];
        if (estado.log) series.push({ valor: m.log, token: '--seg-secundaria', x: centro + 2 });
        else series[0].x = centro - barra / 2;
        series.forEach(function (s) {
          ctx.fillStyle = api.cor(s.token);
          var y = py(s.valor);
          ctx.fillRect(s.x, Math.min(y, zero), barra, Math.abs(y - zero));
          ctx.fillStyle = api.cor('--seg-texto');
          ctx.textBaseline = s.valor < 0 ? 'top' : 'bottom';
          ctx.fillText(porcentagem(s.valor), s.x + barra / 2, s.valor < 0 ? y + 3 : y - 3);
        });
        ctx.font = api.fonte(14, 400);
        ctx.textBaseline = 'top';
        ctx.fillText(dataCurta(m.data), centro, altura - margem.base + 8);
        ctx.font = api.fonte(12, 600);
      });

      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.font = api.fonte(14, 600);
      ctx.fillStyle = api.cor('--seg-primaria');
      ctx.fillRect(margem.esquerda, 4, 14, 14);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.fillText('Simples', margem.esquerda + 20, 4);
      if (estado.log) {
        ctx.fillStyle = api.cor('--seg-secundaria');
        ctx.fillRect(margem.esquerda + 110, 4, 14, 14);
        ctx.fillStyle = api.cor('--seg-texto');
        ctx.fillText('Logarítmico', margem.esquerda + 130, 4);
      }

      leitura.textContent = estado.log
        ? dados.tickers[estado.ticker].leitura
        : 'O log de cada pregão fica acima ou abaixo da barra do simples? Revele depois de registrar a previsão.';
    }

    desenhar();
  });
})();
