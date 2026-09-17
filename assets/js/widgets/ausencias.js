// Descartar datas com ausência ou preencher para a frente: para cada tratamento,
// quantos pregões sobram e a volatilidade anual de cada ativo afetado. Dados:
// tools/dados_widgets_aula01.py.
(function () {
  'use strict';

  var OPCOES = [
    { chave: 'descartar', rotulo: 'Descartar datas (dropna)' },
    { chave: 'preencher', rotulo: 'Preencher para a frente (ffill)' }
  ];

  function porcentagem(valor) {
    return (valor * 100).toFixed(2).replace('.', ',') + '%';
  }

  IntelIWidgets.registrar('ausencias', function (elemento, dados) {
    var controles = document.createElement('div');
    controles.className = 'widget-controles';
    var tabela = document.createElement('table');
    tabela.className = 'widget-tabela';
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura';
    elemento.appendChild(controles);
    elemento.appendChild(tabela);
    elemento.appendChild(leitura);

    var botoes = OPCOES.map(function (opcao) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = opcao.rotulo;
      b.addEventListener('click', function () { mostrar(opcao.chave); });
      controles.appendChild(b);
      return b;
    });

    function mostrar(chave) {
      botoes.forEach(function (b, i) { b.classList.toggle('ativo', OPCOES[i].chave === chave); });
      var tratamento = dados[chave];
      tabela.textContent = '';
      var cabecalho = tabela.insertRow();
      ['Ativo', 'Volatilidade anual'].forEach(function (texto) {
        var th = document.createElement('th');
        th.textContent = texto;
        cabecalho.appendChild(th);
      });
      dados.ativos.forEach(function (ativo) {
        var linha = tabela.insertRow();
        linha.insertCell().textContent = ativo;
        linha.insertCell().textContent = porcentagem(tratamento.vol[ativo]);
      });
      leitura.textContent = tratamento.leitura;
    }

    mostrar(elemento.dataset.inicial || 'descartar');
  });
})();
