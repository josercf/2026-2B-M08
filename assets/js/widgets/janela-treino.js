// Janela de treino deslizante: para cada uma das janelas de 24 meses, os pesos
// ótimos pré-calculados da carteira escolhida (máximo Sharpe ou variância
// mínima), com a marca do peso da janela anterior, e a curva de drawdown dos 12
// meses de teste seguintes. O controle deslizante troca a janela; a leitura diz
// o Sharpe prometido no treino, o entregue no teste, o drawdown máximo e quanto
// da carteira mudou em relação à janela anterior. Dados:
// tools/dados_widgets_aula05.py.
(function () {
  'use strict';

  function pct(valor, casas) {
    return (valor * 100).toFixed(casas === undefined ? 2 : casas).replace('.', ',') + '%';
  }

  function num(valor) {
    return valor.toFixed(2).replace('.', ',');
  }

  IntelIWidgets.registrar('janela-treino', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 1000);
    var altura = Number(elemento.dataset.altura || 320);
    var objetivos = Object.keys(dados.rotulos);
    var inicial = elemento.dataset.inicial === 'principal' ? dados.principal : Number(elemento.dataset.inicial || 0);
    var estado = { objetivo: elemento.dataset.objetivo || objetivos[0], janela: inicial };

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

    var botoes = objetivos.map(function (objetivo) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = dados.rotulos[objetivo];
      b.addEventListener('click', function () { estado.objetivo = objetivo; desenhar(); });
      controles.appendChild(b);
      return b;
    });

    var deslizante = document.createElement('input');
    deslizante.type = 'range';
    deslizante.min = 0;
    deslizante.max = dados.janelas.length - 1;
    deslizante.step = 1;
    deslizante.value = estado.janela;
    deslizante.className = 'widget-deslizante';
    deslizante.setAttribute('aria-label', 'Janela de treino');
    deslizante.addEventListener('input', function () { estado.janela = Number(deslizante.value); desenhar(); });
    var rotuloJanela = document.createElement('span');
    rotuloJanela.className = 'widget-rotulo';
    controles.appendChild(deslizante);
    controles.appendChild(rotuloJanela);

    function desenharPesos(ctx, atual, anterior) {
      var esquerda = 74;
      var direita = 470;
      var topo = 26;
      var faixa = (altura - topo - 8) / dados.ativos.length;
      var maior = 1;
      ctx.font = api.fonte(15, 600);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';
      ctx.fillText('Pesos ótimos na janela de treino', esquerda, 16);
      ctx.font = api.fonte(13, 400);
      dados.ativos.forEach(function (ativo, i) {
        var y = topo + i * faixa;
        var w = atual.pesos[i];
        ctx.fillStyle = api.cor('--seg-superficie');
        ctx.fillRect(esquerda, y + 2, direita - esquerda, faixa - 4);
        ctx.fillStyle = api.cor('--seg-primaria');
        ctx.fillRect(esquerda, y + 2, (direita - esquerda) * w / maior, faixa - 4);
        // Sem marca quando o ativo está fora das duas janelas: a marca no zero
        // viraria uma coluna coral sem informação.
        if (anterior && (anterior.pesos[i] >= 0.0005 || w >= 0.0005)) {
          var xa = esquerda + (direita - esquerda) * anterior.pesos[i] / maior;
          ctx.fillStyle = api.cor('--seg-destaque');
          ctx.fillRect(xa - 1.5, y, 3, faixa);
        }
        ctx.fillStyle = api.cor('--seg-texto');
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(ativo, esquerda - 8, y + faixa / 2);
        if (w >= 0.005) {
          ctx.textAlign = 'left';
          ctx.fillText(pct(w, 1), esquerda + (direita - esquerda) * w / maior + 6, y + faixa / 2);
        }
      });
    }

    function desenharDrawdown(ctx, atual, janela) {
      var esquerda = 590;
      var direita = largura - 14;
      var topo = 26;
      var base = altura - 30;
      var serie = atual.drawdown;
      var piso = -0.25;
      serie.forEach(function (x) { if (x < piso) piso = x * 1.1; });
      function px(i) { return esquerda + (direita - esquerda) * i / (serie.length - 1); }
      function py(v) { return topo + (base - topo) * v / piso; }

      ctx.font = api.fonte(15, 600);
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';
      ctx.fillText('Drawdown no teste, ' + janela.teste[0] + ' a ' + janela.teste[1], esquerda, 16);

      ctx.strokeStyle = api.cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.font = api.fonte(13, 400);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      [0, -0.1, -0.2].forEach(function (v) {
        if (v < piso) return;
        ctx.beginPath();
        ctx.moveTo(esquerda, py(v));
        ctx.lineTo(direita, py(v));
        ctx.stroke();
        ctx.fillStyle = api.cor('--seg-texto');
        ctx.fillText(pct(v, 0), esquerda - 6, py(v));
      });

      ctx.fillStyle = api.cor('--seg-secundaria');
      ctx.beginPath();
      ctx.moveTo(px(0), py(0));
      serie.forEach(function (x, i) { ctx.lineTo(px(i), py(x)); });
      ctx.lineTo(px(serie.length - 1), py(0));
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = api.cor('--seg-primaria');
      ctx.lineWidth = 2;
      ctx.beginPath();
      serie.forEach(function (x, i) { if (i) { ctx.lineTo(px(i), py(x)); } else { ctx.moveTo(px(i), py(x)); } });
      ctx.stroke();

      var fundo = serie.indexOf(Math.min.apply(null, serie));
      ctx.fillStyle = api.cor('--seg-destaque');
      ctx.beginPath();
      ctx.arc(px(fundo), py(serie[fundo]), 5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = api.cor('--seg-texto');
      ctx.textAlign = px(fundo) > (esquerda + direita) / 2 ? 'right' : 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(pct(atual.drawdown_max) + ' em ' + atual.data_fundo,
                   px(fundo) + (ctx.textAlign === 'left' ? 8 : -8), py(serie[fundo]) + 6);
    }

    function desenhar() {
      botoes.forEach(function (b, i) { b.classList.toggle('ativo', objetivos[i] === estado.objetivo); });
      var janela = dados.janelas[estado.janela];
      var atual = janela.objetivos[estado.objetivo];
      var anterior = estado.janela > 0 ? dados.janelas[estado.janela - 1].objetivos[estado.objetivo] : null;
      rotuloJanela.textContent = 'treino ' + janela.treino[0] + ' a ' + janela.treino[1] +
        (estado.janela === dados.principal ? ' (divisão principal)' : '');

      var ctx = canvas.getContext('2d');
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
      desenharPesos(ctx, atual, anterior);
      desenharDrawdown(ctx, atual, janela);

      var texto = 'Sharpe prometido no treino ' + num(atual.prometido) + ', entregue no teste ' +
        num(atual.entregue) + '. ';
      texto += atual.rotatividade === null
        ? 'Primeira janela, sem anterior para comparar.'
        : 'Em relação à janela anterior, ' + pct(atual.rotatividade) + ' da carteira trocou de ativo.';
      leitura.textContent = texto;
    }

    desenhar();
  });
})();
