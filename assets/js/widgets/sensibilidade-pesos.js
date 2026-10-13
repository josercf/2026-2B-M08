// Sensibilidade dos pesos ótimos na janela de treino principal: a mesma
// otimização com a estimativa original, com o retorno esperado perturbado e com a
// covariância de Ledoit-Wolf. A barra cheia é a versão escolhida e o contorno é
// a versão original; a leitura diz quanto da carteira trocou de ativo. Dados:
// tools/dados_widgets_aula05.py.
(function () {
  'use strict';

  function pct(valor, casas) {
    return (valor * 100).toFixed(casas === undefined ? 2 : casas).replace('.', ',') + '%';
  }

  IntelIWidgets.registrar('sensibilidade-pesos', function (elemento, dados, api) {
    var largura = Number(elemento.dataset.largura || 900);
    var altura = Number(elemento.dataset.altura || 300);
    var objetivos = Object.keys(dados.rotulos);
    var VERSOES = [
      { chave: 'base', rotulo: 'Estimativa original' },
      { chave: 'perturbado', rotulo: 'Retorno esperado ' + String.fromCharCode(177) + pct(dados.perturbacao, 0).replace('%', ' p.p.') },
      { chave: 'ledoit_wolf', rotulo: 'Covariância de Ledoit-Wolf' }
    ];
    var estado = {
      objetivo: elemento.dataset.objetivo || objetivos[0],
      versao: elemento.dataset.inicial || 'base'
    };

    var controlesObjetivo = document.createElement('div');
    controlesObjetivo.className = 'widget-controles';
    var controlesVersao = document.createElement('div');
    controlesVersao.className = 'widget-controles';
    var canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controlesObjetivo);
    elemento.appendChild(controlesVersao);
    elemento.appendChild(canvas);
    elemento.appendChild(leitura);

    function botao(pai, texto, aoClicar) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = texto;
      b.addEventListener('click', aoClicar);
      pai.appendChild(b);
      return b;
    }

    var botoesObjetivo = objetivos.map(function (o) {
      return botao(controlesObjetivo, dados.rotulos[o], function () { estado.objetivo = o; desenhar(); });
    });
    var botoesVersao = VERSOES.map(function (v) {
      return botao(controlesVersao, v.rotulo, function () { estado.versao = v.chave; desenhar(); });
    });

    function desenhar() {
      botoesObjetivo.forEach(function (b, i) { b.classList.toggle('ativo', objetivos[i] === estado.objetivo); });
      botoesVersao.forEach(function (b, i) { b.classList.toggle('ativo', VERSOES[i].chave === estado.versao); });
      var o = dados.objetivos[estado.objetivo];
      var escolhida = o[estado.versao];
      var maximo = 0;
      ['base', 'perturbado', 'ledoit_wolf'].forEach(function (v) {
        o[v].forEach(function (w) { if (w > maximo) maximo = w; });
      });

      var ctx = canvas.getContext('2d');
      ctx.fillStyle = api.cor('--seg-base');
      ctx.fillRect(0, 0, largura, altura);
      var esquerda = 90;
      var direita = largura - 90;
      var faixa = (altura - 8) / o.ativos.length;
      ctx.font = api.fonte(15, 300);
      o.ativos.forEach(function (ativo, i) {
        var y = 4 + i * faixa;
        var alto = Math.min(faixa - 6, 26);
        var meio = y + faixa / 2;
        var wEscolhida = escolhida[i];
        var wBase = o.base[i];
        ctx.fillStyle = api.cor('--seg-secundaria');
        ctx.fillRect(esquerda, meio - alto / 2, (direita - esquerda) * wEscolhida / maximo, alto);
        ctx.strokeStyle = api.cor('--seg-primaria');
        ctx.lineWidth = 2;
        ctx.strokeRect(esquerda, meio - alto / 2, (direita - esquerda) * wBase / maximo, alto);
        ctx.fillStyle = api.cor('--seg-texto');
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(ativo, esquerda - 10, meio);
        ctx.textAlign = 'left';
        var fim = (direita - esquerda) * Math.max(wEscolhida, wBase) / maximo;
        ctx.fillText(pct(wEscolhida, 1), esquerda + fim + 8, meio);
      });

      var rot = o.rotatividade[estado.versao];
      leitura.textContent = estado.versao === 'base'
        ? 'Treino ' + dados.treino[0] + ' e ' + dados.treino[1] + '. O contorno marca os pesos originais; escolha uma perturbação.'
        : 'Em relação à estimativa original, ' + pct(rot) + ' da carteira trocou de ativo.';
    }

    desenhar();
  });
})();
