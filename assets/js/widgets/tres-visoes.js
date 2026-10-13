// Três visões de preço de um ativo: negociado na data, Close do Yahoo (ajustado
// por desdobramento) e Adj Close (ajustado também por proventos). Botões escolhem
// o ativo, ligam ou desligam cada visão e alternam a escala logarítmica. Eventos
// corporativos aparecem como linhas tracejadas. Dados: tools/dados_widgets_aula01.py.
(function () {
  'use strict';

  var VISOES = [
    { chave: 'negociado', rotulo: 'Negociado', token: '--seg-destaque' },
    { chave: 'fechamento', rotulo: 'Close', token: '--seg-primaria' },
    { chave: 'ajustado', rotulo: 'Adj Close', token: '--seg-secundaria' }
  ];

  IntelIWidgets.registrar('tres-visoes', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 330);
    var tickers = Object.keys(dados.tickers);
    var estado = {
      ticker: elemento.dataset.inicial || tickers[0],
      ligadas: { negociado: true, fechamento: true, ajustado: true },
      log: true
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
    var botoesVisao = VISOES.map(function (v) {
      return botao(v.rotulo, function () { estado.ligadas[v.chave] = !estado.ligadas[v.chave]; desenhar(); });
    });
    var botaoLog = botao('Escala log', function () { estado.log = !estado.log; desenhar(); });

    function desenhar() {
      botoesTicker.forEach(function (b, i) { b.classList.toggle('ativo', tickers[i] === estado.ticker); });
      botoesVisao.forEach(function (b, i) { b.classList.toggle('ativo', estado.ligadas[VISOES[i].chave]); });
      botaoLog.classList.toggle('ativo', estado.log);

      var serie = dados.tickers[estado.ticker];
      var ctx = canvas.getContext('2d');
      // Topo de 32 px: a faixa de cima guarda a legenda das linhas ligadas.
      var margem = { esquerda: 80, direita: 16, topo: 32, base: 34 };
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);

      var valores = [];
      VISOES.forEach(function (v) {
        if (!estado.ligadas[v.chave]) return;
        serie[v.chave].forEach(function (x) { if (x !== null) valores.push(x); });
      });
      if (!valores.length) {
        leitura.textContent = 'Ligue ao menos uma visão.';
        return;
      }
      var escala = estado.log ? Math.log : function (x) { return x; };
      var minimo = escala(Math.min.apply(null, valores));
      var maximo = escala(Math.max.apply(null, valores));
      var n = dados.datas.length;
      function px(i) { return margem.esquerda + (largura - margem.esquerda - margem.direita) * i / (n - 1); }
      function py(v) {
        return altura - margem.base - (altura - margem.topo - margem.base) * (escala(v) - minimo) / ((maximo - minimo) || 1);
      }

      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, margem.topo);
      ctx.lineTo(margem.esquerda, altura - margem.base);
      ctx.lineTo(largura - margem.direita, altura - margem.base);
      ctx.stroke();

      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(14, 300);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      var extremos = [Math.min.apply(null, valores), Math.max.apply(null, valores)];
      extremos.forEach(function (v) {
        ctx.fillText('R$ ' + v.toFixed(2).replace('.', ','), margem.esquerda - 8, py(v));
      });
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      var anoAnterior = '';
      dados.datas.forEach(function (d, i) {
        var ano = d.slice(0, 4);
        if (ano !== anoAnterior) {
          ctx.fillText(ano, px(i), altura - margem.base + 8);
          anoAnterior = ano;
        }
      });

      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = api.cor('--seg-borda');
      serie.eventos.forEach(function (evento) {
        var i = dados.datas.indexOf(evento.data);
        if (i < 0) return;
        ctx.beginPath();
        ctx.moveTo(px(i), margem.topo);
        ctx.lineTo(px(i), altura - margem.base);
        ctx.stroke();
      });
      ctx.setLineDash([]);

      VISOES.forEach(function (v) {
        if (!estado.ligadas[v.chave]) return;
        ctx.strokeStyle = api.cor(v.token);
        ctx.lineWidth = 2;
        ctx.beginPath();
        var aberto = false;
        serie[v.chave].forEach(function (x, i) {
          if (x === null) { aberto = false; return; }
          if (aberto) { ctx.lineTo(px(i), py(x)); } else { ctx.moveTo(px(i), py(x)); aberto = true; }
        });
        ctx.stroke();
      });

      // Legenda: um traço na cor de cada visão ligada, na ordem dos botões.
      ctx.font = api.fonte(14, 600);
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      var x = margem.esquerda;
      VISOES.forEach(function (v) {
        if (!estado.ligadas[v.chave]) return;
        ctx.strokeStyle = api.cor(v.token);
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(x, 12);
        ctx.lineTo(x + 22, 12);
        ctx.stroke();
        ctx.fillStyle = api.cor('--seg-texto');
        ctx.fillText(v.rotulo, x + 30, 12);
        x += 30 + ctx.measureText(v.rotulo).width + 28;
      });

      leitura.textContent = serie.leitura;
    }

    desenhar();
  });
})();
