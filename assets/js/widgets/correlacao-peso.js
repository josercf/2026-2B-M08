// Risco de uma carteira de dois ativos reais em função do peso e da correlação.
// As volatilidades vêm medidas da cesta; dois controles deslizantes mudam o peso
// no primeiro ativo e a correlação. A curva cheia é a da correlação escolhida, a
// tracejada é a da correlação medida, e o ponto marca o peso escolhido.
// Dados: tools/dados_widgets_aula03.py.
(function () {
  'use strict';

  function risco(w, a, b, rho) {
    var v = w * w * a * a + (1 - w) * (1 - w) * b * b + 2 * w * (1 - w) * rho * a * b;
    return Math.sqrt(Math.max(v, 0));
  }

  function pct(valor) {
    return (valor * 100).toFixed(2).replace('.', ',').replace('-', '\u2212') + '%';
  }

  function decimal(valor) {
    return valor.toFixed(2).replace('.', ',').replace('-', '\u2212');
  }

  IntelIWidgets.registrar('correlacao-peso', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 900);
    var altura = Number(elemento.dataset.altura || 300);
    var pares = dados.pares;
    var inicial = elemento.dataset.inicial || '';
    var indice = Math.max(0, pares.findIndex(function (p) { return p.a + '-' + p.b === inicial; }));
    var estado = { par: pares[indice], peso: 0.5, rho: pares[indice].rho, revelar: false };

    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var deslizantes = document.createElement('div');
    deslizantes.className = 'widget-controles';
    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controles);
    elemento.appendChild(deslizantes);
    elemento.appendChild(canvas);
    elemento.appendChild(leitura);

    var botoes = pares.map(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = p.a + ' e ' + p.b;
      b.addEventListener('click', function () {
        estado.par = p;
        estado.rho = p.rho;
        estado.peso = 0.5;
        estado.revelar = false;
        sincronizar();
      });
      controles.appendChild(b);
      return b;
    });

    function deslizante(rotulo, min, max, passo, aoMudar) {
      var caixa = document.createElement('label');
      var texto = document.createElement('span');
      var entrada = document.createElement('input');
      entrada.type = 'range';
      entrada.min = min;
      entrada.max = max;
      entrada.step = passo;
      entrada.style.accentColor = api.cor('--seg-primaria');
      entrada.addEventListener('input', function () { aoMudar(Number(entrada.value)); desenhar(); });
      caixa.appendChild(texto);
      caixa.appendChild(entrada);
      deslizantes.appendChild(caixa);
      return { entrada: entrada, texto: texto, rotulo: rotulo };
    }

    var controlePeso = deslizante('Peso', 0, 1, 0.01, function (v) { estado.peso = v; });
    var controleRho = deslizante('Correlação', -1, 1, 0.01, function (v) { estado.rho = v; });
    var medida = document.createElement('button');
    medida.type = 'button';
    medida.textContent = 'Correlação medida';
    medida.addEventListener('click', function () { estado.rho = estado.par.rho; sincronizar(); });
    deslizantes.appendChild(medida);
    // O peso de menor risco medido só aparece depois da previsão da turma.
    var revelar = document.createElement('button');
    revelar.type = 'button';
    revelar.textContent = 'Revelar o menor risco';
    revelar.addEventListener('click', function () { estado.revelar = !estado.revelar; desenhar(); });
    deslizantes.appendChild(revelar);

    function sincronizar() {
      controlePeso.entrada.value = estado.peso;
      controleRho.entrada.value = estado.rho;
      desenhar();
    }

    function desenhar() {
      var p = estado.par;
      botoes.forEach(function (b, i) { b.classList.toggle('ativo', pares[i] === p); });
      revelar.classList.toggle('ativo', estado.revelar);
      controlePeso.texto.textContent = 'Peso em ' + p.a + ': ' + Math.round(estado.peso * 100) + '% ';
      controleRho.texto.textContent = 'Correlação: ' + decimal(estado.rho) + ' ';

      var ctx = canvas.getContext('2d');
      var margem = { esquerda: 60, direita: 20, topo: 14, base: 48 };
      var topo = Math.max(p.vol_a, p.vol_b) * 1.1;
      function px(w) { return margem.esquerda + (largura - margem.esquerda - margem.direita) * w; }
      function py(v) { return altura - margem.base - (altura - margem.topo - margem.base) * v / topo; }

      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
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
      ctx.fillText('risco', margem.esquerda - 8, margem.topo);
      for (var marca = 0; marca <= topo; marca += 0.1) {
        ctx.fillText(Math.round(marca * 100) + '%', margem.esquerda - 8, py(marca));
      }
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      [0, 0.25, 0.5, 0.75, 1].forEach(function (w) {
        ctx.textAlign = w === 0 ? 'left' : (w === 1 ? 'right' : 'center');
        ctx.fillText(Math.round(w * 100) + '%', px(w), altura - margem.base + 8);
      });
      ctx.textAlign = 'center';
      ctx.fillText('peso em ' + p.a, px(0.5), altura - margem.base + 24);

      function curva(rho, tracejada, token) {
        ctx.setLineDash(tracejada ? [6, 6] : []);
        ctx.strokeStyle = api.cor(token);
        ctx.lineWidth = tracejada ? 2 : 3;
        ctx.beginPath();
        for (var k = 0; k <= 100; k++) {
          var w = k / 100;
          if (k === 0) ctx.moveTo(px(w), py(risco(w, p.vol_a, p.vol_b, rho)));
          else ctx.lineTo(px(w), py(risco(w, p.vol_a, p.vol_b, rho)));
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }

      curva(p.rho, true, '--seg-borda');
      curva(estado.rho, false, '--seg-primaria');

      if (estado.revelar) {
        ctx.strokeStyle = api.cor('--seg-secundaria');
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(px(p.peso_minimo), margem.topo);
        ctx.lineTo(px(p.peso_minimo), altura - margem.base);
        ctx.stroke();
      }

      var atual = risco(estado.peso, p.vol_a, p.vol_b, estado.rho);
      ctx.fillStyle = api.cor('--seg-destaque');
      ctx.beginPath();
      ctx.arc(px(estado.peso), py(atual), 8, 0, 2 * Math.PI);
      ctx.fill();

      leitura.textContent = 'Risco da carteira: ' + pct(atual) + ' (' + p.a + ' ' + pct(p.vol_a) +
        ', ' + p.b + ' ' + pct(p.vol_b) + ').' + (estado.revelar ? ' ' + p.medido : '');
    }

    sincronizar();
  });
})();
