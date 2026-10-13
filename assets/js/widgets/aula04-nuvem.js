// Sorteio progressivo de carteiras da Aula 04: as N primeiras das 10.000
// carteiras sorteadas no plano risco-retorno, a melhor sorteada até ali em
// destaque e a carteira de máximo Sharpe resolvida pelo SLSQP como referência.
// O botão "Ótimas e fronteira" acrescenta a carteira de variância mínima e a
// fronteira de 50 pontos. Dados: tools/dados_widgets_aula04.py, que lê
// tools/medidas_aula04.py.
(function () {
  'use strict';

  var EIXO_X = [0.08, 0.36];
  var EIXO_Y = [-0.02, 0.40];

  function pct(valor) {
    return (valor * 100).toFixed(0) + '%';
  }

  function milhar(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  IntelIWidgets.registrar('aula04-nuvem', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 360);
    var estado = {
      n: Number(elemento.dataset.inicial || dados.passos[0]),
      fronteira: elemento.dataset.fronteira === 'sim'
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

    var botoesN = dados.passos.map(function (n) {
      return botao(milhar(n) + ' sorteios', function () { estado.n = n; desenhar(); });
    });
    var botaoFronteira = botao('Ótimas e fronteira', function () {
      estado.fronteira = !estado.fronteira;
      desenhar();
    });

    var margem = { esquerda: 76, direita: 20, topo: 14, base: 50 };
    function px(vol) {
      return margem.esquerda + (largura - margem.esquerda - margem.direita) *
        (vol - EIXO_X[0]) / (EIXO_X[1] - EIXO_X[0]);
    }
    function py(ret) {
      return altura - margem.base - (altura - margem.topo - margem.base) *
        (ret - EIXO_Y[0]) / (EIXO_Y[1] - EIXO_Y[0]);
    }

    function eixos(ctx) {
      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, margem.topo);
      ctx.lineTo(margem.esquerda, altura - margem.base);
      ctx.lineTo(largura - margem.direita, altura - margem.base);
      ctx.stroke();
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.font = api.fonte(17, 400);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      for (var v = 0.10; v <= EIXO_X[1] + 1e-9; v += 0.05) {
        ctx.fillText(pct(v), px(v), altura - margem.base + 6);
      }
      ctx.fillText('volatilidade anual', (margem.esquerda + largura - margem.direita) / 2, altura - 22);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      for (var r = 0; r <= EIXO_Y[1] + 1e-9; r += 0.10) {
        ctx.fillText(pct(r), margem.esquerda - 8, py(r));
      }
      ctx.save();
      ctx.translate(16, (margem.topo + altura - margem.base) / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.textAlign = 'center';
      ctx.fillText('retorno anual', 0, 0);
      ctx.restore();

      // CDI como linha de referência: abaixo dela o Sharpe é negativo.
      ctx.setLineDash([5, 5]);
      ctx.strokeStyle = api.cor('--seg-primaria');
      ctx.beginPath();
      ctx.moveTo(margem.esquerda, py(dados.rf));
      ctx.lineTo(largura - margem.direita, py(dados.rf));
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = api.cor('--seg-primaria');
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      ctx.fillText('CDI ' + (dados.rf * 100).toFixed(2).replace('.', ',') + '%: verde acima, cinza abaixo',
        largura - margem.direita, py(dados.rf) - 4);
    }

    function marcador(ctx, x, y, raio, token, rotulo, alinhamento, dy) {
      ctx.fillStyle = api.cor(token);
      ctx.strokeStyle = api.cor('--seg-base');
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, raio, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
      ctx.font = api.fonte(17, 700);
      ctx.textAlign = alinhamento || 'left';
      ctx.textBaseline = 'middle';
      var tx = x + (alinhamento === 'right' ? -raio - 6 : raio + 6);
      var ty = y + (dy || 0);
      // Fundo da cor da base sob o rótulo, para a linha do CDI e os pontos
      // da nuvem não cruzarem o texto.
      var w = ctx.measureText(rotulo).width;
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(alinhamento === 'right' ? tx - w - 3 : tx - 3, ty - 12, w + 6, 24);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.fillText(rotulo, tx, ty);
    }

    function desenhar() {
      botoesN.forEach(function (b, i) { b.classList.toggle('ativo', dados.passos[i] === estado.n); });
      botaoFronteira.classList.toggle('ativo', estado.fronteira);

      var ctx = canvas.getContext('2d');
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
      eixos(ctx);

      var n = Math.min(estado.n, dados.sharpe.length);
      var raio = n <= 100 ? 4 : (n <= 1000 ? 2.5 : 1.6);
      var acima = api.cor('--seg-secundaria');
      var abaixo = api.cor('--seg-texto-suave');
      var melhor = 0;
      for (var i = 0; i < n; i++) {
        if (dados.sharpe[i] > dados.sharpe[melhor]) melhor = i;
        ctx.fillStyle = dados.sharpe[i] >= 0 ? acima : abaixo;
        ctx.beginPath();
        ctx.arc(px(dados.vol[i]), py(dados.ret[i]), raio, 0, 2 * Math.PI);
        ctx.fill();
      }

      if (estado.fronteira) {
        ctx.strokeStyle = api.cor('--seg-primaria');
        ctx.lineWidth = 3;
        ctx.beginPath();
        dados.fronteira.forEach(function (p, k) {
          if (k === 0) ctx.moveTo(px(p[0]), py(p[1])); else ctx.lineTo(px(p[0]), py(p[1]));
        });
        ctx.stroke();
        var mv = dados.variancia_minima;
        // Rótulo abaixo e à direita: à esquerda ele sai pela borda do canvas.
        marcador(ctx, px(mv.vol), py(mv.ret), 7, '--seg-primaria', 'Variância mínima', 'left', 18);
      }

      marcador(ctx, px(dados.vol[melhor]), py(dados.ret[melhor]), 7, '--seg-destaque',
        'Melhor sorteada', 'left');
      var ms = dados.maximo_sharpe;
      marcador(ctx, px(ms.vol), py(ms.ret), 8, '--seg-primaria', 'Máximo Sharpe (SLSQP)', 'left');

      leitura.textContent = dados.leituras[String(estado.n)] + (estado.fronteira ? ' ' + dados.leitura_otimas : '');
    }

    desenhar();
  });
})();
