// Verificador de números da Aula 06: o texto de interpretação com três erros
// plantados, declarado como exercício, com cada número clicável. A sala confere
// à mão primeiro; depois o botão roda a verificação de presença que a API faz
// (interpretacao.verificar_numeros) e o outro revela os três erros plantados,
// inclusive o que o código deixa passar. Dados: tools/dados_widgets_aula06.py.
(function () {
  'use strict';

  var TIPOS = {
    valor_alterado: 'valor alterado',
    promessa_inventada: 'promessa inventada',
    ativo_trocado: 'ativo trocado'
  };

  IntelIWidgets.registrar('verificador-numeros', function (elemento, dados) {
    var aviso = document.createElement('p');
    aviso.className = 'verificador-aviso';
    aviso.textContent = dados.aviso;
    var texto = document.createElement('p');
    texto.className = 'verificador-texto';
    var controles = document.createElement('div');
    controles.className = 'widget-controles verificador-controles';
    var leitura = document.createElement('p');
    leitura.className = 'widget-leitura verificador-leitura';
    elemento.appendChild(aviso);
    elemento.appendChild(texto);
    elemento.appendChild(controles);
    elemento.appendChild(leitura);

    // Cada número vira um span, na ordem em que o verificador o encontrou.
    var spans = [];
    var resto = dados.texto;
    dados.numeros.forEach(function (numero) {
      var i = resto.indexOf(numero.trecho);
      texto.appendChild(document.createTextNode(resto.slice(0, i)));
      var span = document.createElement('span');
      span.className = 'verificador-numero';
      span.textContent = numero.trecho;
      span.addEventListener('click', function () {
        leitura.textContent = numero.trecho + ': ' + (numero.confere
          ? 'aparece no JSON em ' + numero.origem + '.'
          : 'não aparece em nenhum campo do JSON.');
      });
      texto.appendChild(span);
      spans.push(span);
      resto = resto.slice(i + numero.trecho.length);
    });
    texto.appendChild(document.createTextNode(resto));

    function botao(rotulo, aoClicar) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = rotulo;
      b.addEventListener('click', function () {
        b.classList.add('ativo');
        aoClicar();
      });
      controles.appendChild(b);
    }

    botao('Conferir por código', function () {
      dados.numeros.forEach(function (numero, i) {
        spans[i].classList.add(numero.confere ? 'confere' : 'nao-confere');
      });
      leitura.textContent = dados.leitura;
    });

    botao('Revelar erros plantados', function () {
      var descricoes = dados.erros.map(function (erro) {
        dados.numeros.forEach(function (numero, i) {
          if (numero.trecho === erro.trecho) spans[i].classList.add('plantado');
        });
        return erro.trecho + ' (' + TIPOS[erro.tipo] + '; certo: ' + erro.certo + ')';
      });
      leitura.textContent = 'Erros plantados: ' + descricoes.join('; ') + '.';
    });

    leitura.textContent = 'Clique em um número para ver de onde ele vem.';
  });
})();
