// Montador de requisição da Aula 06: a turma escolhe a rota e o corpo, registra
// a previsão do código de status e só então envia. A resposta mostrada é a
// gravada da API de exemplo (exemplos/aula06-api-carteira) pelo TestClient, sem
// servidor no ar: o slide funciona sem rede. Dados: tools/dados_widgets_aula06.py.
(function () {
  'use strict';

  var CLASSE_STATUS = { 2: 'status-ok', 4: 'status-cliente', 5: 'status-servidor' };

  IntelIWidgets.registrar('montador-requisicao', function (elemento, dados) {
    var casos = {};
    dados.casos.forEach(function (c) { casos[c.chave] = c; });
    var estado = { rota: dados.rotas[1], corpo: dados.corpos[0].nome };

    function grupo(rotulo) {
      var linha = document.createElement('div');
      linha.className = 'widget-controles montador-linha';
      var nome = document.createElement('span');
      nome.className = 'montador-rotulo';
      nome.textContent = rotulo;
      linha.appendChild(nome);
      elemento.appendChild(linha);
      return linha;
    }

    function botao(linha, texto, aoClicar) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = texto;
      b.addEventListener('click', aoClicar);
      linha.appendChild(b);
      return b;
    }

    var linhaRota = grupo('Rota');
    var botoesRota = dados.rotas.map(function (rota) {
      return botao(linhaRota, rota, function () { estado.rota = rota; atualizar(); });
    });
    var linhaCorpo = grupo('Corpo');
    var botoesCorpo = dados.corpos.map(function (corpo) {
      return botao(linhaCorpo, corpo.rotulo, function () { estado.corpo = corpo.nome; atualizar(); });
    });
    var enviar = botao(linhaCorpo, 'Enviar', mostrarResposta);
    enviar.classList.add('montador-enviar');

    var painel = document.createElement('div');
    painel.className = 'montador-painel';
    var requisicao = document.createElement('pre');
    requisicao.className = 'montador-caixa';
    var resposta = document.createElement('pre');
    resposta.className = 'montador-caixa';
    painel.appendChild(requisicao);
    painel.appendChild(resposta);
    elemento.appendChild(painel);

    function casoAtual() {
      var get = estado.rota.indexOf('GET') === 0;
      return casos[estado.rota + '|' + (get ? '-' : estado.corpo)];
    }

    function atualizar() {
      var get = estado.rota.indexOf('GET') === 0;
      botoesRota.forEach(function (b, i) { b.classList.toggle('ativo', dados.rotas[i] === estado.rota); });
      botoesCorpo.forEach(function (b, i) {
        b.classList.toggle('ativo', !get && dados.corpos[i].nome === estado.corpo);
        b.disabled = get;
      });
      var caso = casoAtual();
      requisicao.textContent = caso.metodo + ' ' + caso.rota + ' HTTP/1.1\n'
        + (caso.corpo ? 'Content-Type: application/json\n\n' + caso.corpo : '\n(sem corpo)');
      resposta.className = 'montador-caixa';
      resposta.textContent = 'Status: ?\n\nRegistre a previsão do código de status antes de enviar.';
    }

    function mostrarResposta() {
      var caso = casoAtual();
      resposta.className = 'montador-caixa ' + (CLASSE_STATUS[Math.floor(caso.status / 100)] || '');
      resposta.textContent = 'Status: ' + caso.status + '\n\n' + caso.resposta;
      resposta.scrollTop = 0;
    }

    atualizar();
  });
})();
