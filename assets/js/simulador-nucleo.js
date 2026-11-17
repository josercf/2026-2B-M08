// Conta do simulador de carteiras da Aula 04 em turnos (ADR-018), sem DOM.
// É a mesma de tools/simulador_referencia.py, e tools/tests/test_simulador_paridade.py
// compara as duas. Definições:
//   retorno diário simples do preço ajustado, na janela comum dos ativos;
//   retorno anual = média diária x 252; risco anual = desvio amostral x raiz de 252;
//   Sharpe = (retorno - rf) / risco; sorteio dos pesos uniforme normalizado.
(function () {
  'use strict';

  var PREGOES_ANO = 252;

  // Índice do primeiro pregão em que todos os ativos têm cotação, ou -1.
  function inicioComum(cotacoes, ativos) {
    var inicio = 0;
    for (var a = 0; a < ativos.length; a++) {
      var serie = cotacoes.precos[ativos[a]];
      if (!serie) return -1;
      var i = 0;
      while (i < serie.length && serie[i] === null) i++;
      if (i >= serie.length) return -1;
      if (i > inicio) inicio = i;
    }
    return inicio;
  }

  // Quantos retornos a janela comum dos ativos tem. Ativo desconhecido dá 0.
  function pregoesDisponiveis(cotacoes, ativos) {
    if (!ativos.length) return 0;
    var inicio = inicioComum(cotacoes, ativos);
    return inicio < 0 ? 0 : cotacoes.datas.length - 1 - inicio;
  }

  // Últimos `pregoes` retornos diários da janela comum: {datas, linhas}, uma
  // linha por pregão e uma coluna por ativo, na ordem de `ativos`.
  function retornos(cotacoes, ativos, pregoes) {
    var disponiveis = pregoesDisponiveis(cotacoes, ativos);
    if (pregoes < 2 || disponiveis < pregoes) {
      throw new Error('a janela comum tem ' + disponiveis + ' retornos e foram pedidos ' + pregoes);
    }
    var total = cotacoes.datas.length;
    var datas = [];
    var linhas = [];
    for (var t = total - pregoes; t < total; t++) {
      var linha = new Array(ativos.length);
      for (var a = 0; a < ativos.length; a++) {
        var serie = cotacoes.precos[ativos[a]];
        linha[a] = serie[t] / serie[t - 1] - 1;
      }
      datas.push(cotacoes.datas[t]);
      linhas.push(linha);
    }
    return { datas: datas, linhas: linhas };
  }

  function retornoDoDia(pesos, linha) {
    var soma = 0;
    for (var a = 0; a < pesos.length; a++) soma += pesos[a] * linha[a];
    return soma;
  }

  // Série diária da carteira, para a evolução do valor investido.
  function serieDaCarteira(pesos, linhas) {
    var serie = new Array(linhas.length);
    for (var t = 0; t < linhas.length; t++) serie[t] = retornoDoDia(pesos, linhas[t]);
    return serie;
  }

  function metricas(pesos, linhas) {
    var serie = serieDaCarteira(pesos, linhas);
    var n = serie.length;
    var media = 0;
    for (var i = 0; i < n; i++) media += serie[i];
    media /= n;
    var quadrados = 0;
    for (var j = 0; j < n; j++) quadrados += (serie[j] - media) * (serie[j] - media);
    return {
      retorno: media * PREGOES_ANO,
      risco: Math.sqrt(quadrados / (n - 1)) * Math.sqrt(PREGOES_ANO)
    };
  }

  // Gerador com semente (mulberry32): a mesma semente devolve a mesma sequência
  // em qualquer navegador, e por isso a nuvem de um aluno abre igual no projetor.
  function gerador(semente) {
    var estado = semente >>> 0;
    return function () {
      estado = (estado + 0x6D2B79F5) >>> 0;
      var t = estado;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sortearPesos(k, sorteio) {
    var pesos = new Array(k);
    var soma = 0;
    for (var a = 0; a < k; a++) {
      pesos[a] = sorteio();
      soma += pesos[a];
    }
    for (var b = 0; b < k; b++) pesos[b] /= soma;
    return pesos;
  }

  // Média e covariância anualizadas, para avaliar cada carteira sorteada sem
  // percorrer a série inteira de novo.
  function momentos(linhas) {
    var n = linhas.length;
    var k = linhas[0].length;
    var media = new Array(k).fill(0);
    for (var t = 0; t < n; t++) for (var a = 0; a < k; a++) media[a] += linhas[t][a];
    for (var m = 0; m < k; m++) media[m] /= n;
    var cov = [];
    for (var i = 0; i < k; i++) {
      cov.push(new Array(k).fill(0));
    }
    for (var u = 0; u < n; u++) {
      for (var p = 0; p < k; p++) {
        var dp = linhas[u][p] - media[p];
        for (var q = p; q < k; q++) cov[p][q] += dp * (linhas[u][q] - media[q]);
      }
    }
    for (var r = 0; r < k; r++) {
      for (var s = r; s < k; s++) {
        cov[r][s] = cov[r][s] / (n - 1) * PREGOES_ANO;
        cov[s][r] = cov[r][s];
      }
      media[r] *= PREGOES_ANO;
    }
    return { media: media, cov: cov };
  }

  function avaliar(pesos, mom, rf) {
    var k = pesos.length;
    var retorno = 0;
    var variancia = 0;
    for (var i = 0; i < k; i++) {
      retorno += pesos[i] * mom.media[i];
      for (var j = 0; j < k; j++) variancia += pesos[i] * mom.cov[i][j] * pesos[j];
    }
    var risco = Math.sqrt(variancia);
    return { retorno: retorno, risco: risco, sharpe: (retorno - rf) / risco };
  }

  // n carteiras sorteadas: vetores retorno, risco e sharpe, e os pesos de cada uma.
  function simular(linhas, n, semente, rf) {
    var sorteio = gerador(semente);
    var mom = momentos(linhas);
    var k = linhas[0].length;
    var saida = {
      retorno: new Float64Array(n), risco: new Float64Array(n),
      sharpe: new Float64Array(n), pesos: new Array(n)
    };
    for (var i = 0; i < n; i++) {
      var pesos = sortearPesos(k, sorteio);
      var ponto = avaliar(pesos, mom, rf);
      saida.retorno[i] = ponto.retorno;
      saida.risco[i] = ponto.risco;
      saida.sharpe[i] = ponto.sharpe;
      saida.pesos[i] = pesos;
    }
    return saida;
  }

  function posicionar(pesos, linhas, rf) {
    var soma = 0;
    for (var a = 0; a < pesos.length; a++) {
      if (pesos[a] < 0) throw new Error('os pesos precisam ser não negativos e somar 1');
      soma += pesos[a];
    }
    if (Math.abs(soma - 1) > 1e-6) throw new Error('os pesos precisam ser não negativos e somar 1');
    var m = metricas(pesos, linhas);
    return { retorno: m.retorno, risco: m.risco, sharpe: (m.retorno - rf) / m.risco };
  }

  window.SimuladorNucleo = {
    PREGOES_ANO: PREGOES_ANO,
    pregoesDisponiveis: pregoesDisponiveis,
    retornos: retornos,
    retornoDoDia: retornoDoDia,
    serieDaCarteira: serieDaCarteira,
    metricas: metricas,
    gerador: gerador,
    sortearPesos: sortearPesos,
    simular: simular,
    posicionar: posicionar
  };
})();
