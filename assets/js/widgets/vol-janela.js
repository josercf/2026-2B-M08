// Volatilidade anualizada em janela deslizante de 21, 63 e 252 pregões. Botões
// escolhem o ativo e ligam ou desligam cada janela; a linha tracejada é a
// volatilidade da janela inteira do snapshot. data-inicial-janelas="252" no
// markup define quais janelas abrem ligadas, para a turma prever antes de ligar
// as curtas. Dados: tools/dados_widgets_aula02.py.
(function () {
  'use strict';

  var TOKENS = { '21': '--seg-destaque', '63': '--seg-primaria', '252': '--seg-secundaria' };

  function porcentagem(valor, casas) {
    return (valor * 100).toFixed(casas).replace('.', ',') + '%';
  }

  IntelIWidgets.registrar('vol-janela', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 300);
    var tickers = Object.keys(dados.tickers);
    var janelas = dados.janelas.map(String);
    var iniciais = (elemento.dataset.inicialJanelas || janelas.join(',')).split(',');
    var estado = { ticker: elemento.dataset.inicial || tickers[0], ligadas: {} };
    janelas.forEach(function (j) { estado.ligadas[j] = iniciais.indexOf(j) >= 0; });

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
    var botoesJanela = janelas.map(function (j) {
      return botao(j + ' pregões', function () { estado.ligadas[j] = !estado.ligadas[j]; desenhar(); });
    });

    function desenhar() {
      botoesTicker.forEach(function (b, i) { b.classList.toggle('ativo', tickers[i] === estado.ticker); });
      botoesJanela.forEach(function (b, i) { b.classList.toggle('ativo', estado.ligadas[janelas[i]]); });

      var bloco = dados.tickers[estado.ticker];
      var ctx = canvas.getContext('2d');
      var margem = { esquerda: 64, direita: 16, topo: 12, base: 34 };
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);

      // Eixo vertical fixo pelo maior valor do ativo em todas as janelas, para
      // ligar uma janela não reescalar as outras.
      var maximo = bloco.vol_total;
      janelas.forEach(function (j) {
        bloco.series[j].forEach(function (x) { if (x !== null && x > maximo) maximo = x; });
      });
      maximo = Math.ceil(maximo * 4) / 4;
      var n = dados.datas.length;
      function px(i) { return margem.esquerda + (largura - margem.esquerda - margem.direita) * i / (n - 1); }
      function py(v) { return altura - margem.base - (altura - margem.topo - margem.base) * v / maximo; }

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
      for (var v = 0; v <= maximo + 1e-9; v += 0.5) {
        ctx.fillText(porcentagem(v, 0), margem.esquerda - 8, py(v));
      }
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

      ctx.setLineDash([6, 5]);
      ctx.strokeStyle = api.cor('--seg-texto');
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, py(bloco.vol_total));
      ctx.lineTo(largura - margem.direita, py(bloco.vol_total));
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      ctx.font = api.fonte(14, 600);
      ctx.fillText('Janela inteira: ' + porcentagem(bloco.vol_total, 2), largura - margem.direita, py(bloco.vol_total) - 4);

      var textos = [];
      janelas.forEach(function (j) {
        if (!estado.ligadas[j]) return;
        ctx.strokeStyle = api.cor(TOKENS[j]);
        ctx.lineWidth = 2;
        ctx.beginPath();
        var aberto = false;
        bloco.series[j].forEach(function (x, i) {
          if (x === null) { aberto = false; return; }
          if (aberto) { ctx.lineTo(px(i), py(x)); } else { ctx.moveTo(px(i), py(x)); aberto = true; }
        });
        ctx.stroke();
        textos.push(bloco.leituras[j]);
      });

      leitura.textContent = textos.length
        ? estado.ticker + ', em 2020. ' + textos.join('; ') + '.'
        : 'Ligue ao menos uma janela.';
    }

    desenhar();
  });
})();
