// Portal de simulação da Aula 04 em turnos (ADR-018): telas de simulador/index.html.
//
// A conta vem de SimuladorNucleo e a sala de SimuladorDados; este arquivo só
// cuida de tela, navegação por hash e desenho em canvas. Nenhuma cor é escrita
// aqui: todas saem dos tokens de assets/css/inteli-brand.css.
//
// Identidade do participante (id, iniciais, grupo, simulação e turnos) fica no
// localStorage, para a pessoa voltar sem entrar de novo. Com ?demo=1 ela fica no
// sessionStorage: cada aba é um participante, e duas abas do mesmo navegador
// servem de ensaio da sala.
//
// Modo telão (?painel=1&telao=1): só o painel e a simulação aberta por um
// avatar, sem barra de topo, rodapé nem entrada. É o que o deck embute no slide
// e o que o professor abre em tela cheia. O tamanho de tudo sai de unidades de
// viewport em assets/css/simulador.css (bloco "telão").
//
// Spec do grupo: a tela Progresso monta o endereço de aulas/aula04-spec.html
// com grupo, token, turno e iniciais (sala.specLink), e o painel leva à visão
// somente leitura da spec de cada grupo (?ver=1).
(function () {
  'use strict';

  var SESSAO = 'm08-aula04-2026-11-18';
  var COTACOES = '../assets/data/aula04-cotacoes.json';
  var BIBLIOTECA = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js';
  var ESPERA_BIBLIOTECA = 4000;
  var PERIODOS = [9, 21, 63, 126, 252];
  var QUANTIDADES = [10, 100, 1000, 10000];
  var MINIMO = 2;
  var MAXIMO = 5;
  var CAPITAL = 100000;
  var GRUPOS = [
    { id: 'G01', nome: 'Grupo 01' }, { id: 'G02', nome: 'Grupo 02' },
    { id: 'G03', nome: 'Grupo 03' }, { id: 'G04', nome: 'Grupo 04' },
    { id: 'VIS', nome: 'Visitantes' }
  ];
  var TELAS = ['entrar', 'montar', 'simular', 'progresso', 'painel'];

  var N = window.SimuladorNucleo;
  var DEMO = window.SimuladorDados.demo();
  var PAINEL_DIRETO = /[?&]painel=1/.test(window.location.search);
  var TELAO = PAINEL_DIRETO && /[?&]telao=1/.test(window.location.search);
  var SPEC = '../aulas/aula04-spec.html';
  var TURNOS_COM_SPEC = [4, 5];
  var CHEIO = 10;              // avatares de um grupo que cabem em uma linha do telão
  var CHAVE_EU = 'inteli-simulador-eu:' + SESSAO;

  var cotacoes = null;
  var tickers = [];
  var sala = null;
  var eu = null;               // {id, iniciais, grupo}
  var sim = simulacaoNova();   // {ativos, pregoes, n, semente, pesos}
  var turnos = [];             // turnos marcados por este participante
  var telaAtual = 'carregando';
  var conhecidos = {};         // ids já desenhados no painel
  var salvamentos = 0;
  var relogioSalvar = null;
  var pedidoPainel = 0;
  var atalhos = {};            // atalhos da spec já resolvidos: chave -> {url} ou {erro}

  if (TELAO) document.body.classList.add('sim-telao');

  // ------------------------------------------------------------ utilidades

  function $(seletor, raiz) { return (raiz || document).querySelector(seletor); }
  function $$(seletor, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(seletor)); }

  function criar(tag, atributos, filhos) {
    var no = document.createElement(tag);
    Object.keys(atributos || {}).forEach(function (nome) {
      if (nome === 'texto') no.textContent = atributos[nome];
      else if (nome === 'classe') no.className = atributos[nome];
      else no.setAttribute(nome, atributos[nome]);
    });
    (filhos || []).forEach(function (filho) {
      no.appendChild(typeof filho === 'string' ? document.createTextNode(filho) : filho);
    });
    return no;
  }

  function limpar(no) { while (no.firstChild) no.removeChild(no.firstChild); }

  function numero(valor, casas) {
    return valor.toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }
  function porcento(valor, casas) { return numero(valor * 100, casas === undefined ? 2 : casas) + '%'; }
  function reais(valor) { return 'R$ ' + numero(valor, 2); }
  function inteiro(valor) { return numero(valor, 0); }
  function decimal(valor) { return valor.toFixed(6); }
  function data(iso) { return iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4); }

  function semente() { return Math.floor(Math.random() * 2147483647) + 1; }
  function simulacaoNova() { return { ativos: [], pregoes: 252, n: 1000, semente: semente(), pesos: null }; }
  function pesosIguais(k) { var p = []; for (var i = 0; i < k; i++) p.push(1 / k); return p; }
  function nomeDoGrupo(id) {
    for (var i = 0; i < GRUPOS.length; i++) if (GRUPOS[i].id === id) return GRUPOS[i].nome;
    return id;
  }

  // ------------------------------------------------------------- cor e tipo

  var estilo = null;
  function token(nome) {
    if (!estilo) estilo = getComputedStyle(document.documentElement);
    return estilo.getPropertyValue(nome).trim();
  }
  function rgb(nome) {
    var hexa = token(nome).replace('#', '');
    return [parseInt(hexa.slice(0, 2), 16), parseInt(hexa.slice(2, 4), 16), parseInt(hexa.slice(4, 6), 16)];
  }
  function misturar(a, b, t) {
    return [Math.round(a[0] + (b[0] - a[0]) * t), Math.round(a[1] + (b[1] - a[1]) * t), Math.round(a[2] + (b[2] - a[2]) * t)];
  }
  function tinta(cor, alfa) {
    return 'rgba(' + cor[0] + ',' + cor[1] + ',' + cor[2] + ',' + (alfa === undefined ? 1 : alfa) + ')';
  }
  function fonte(tamanho, peso) {
    return peso + ' ' + tamanho + 'px ' + getComputedStyle(document.body).fontFamily;
  }

  // ----------------------------------------------------------- armazenamento

  function gaveta() { return DEMO ? window.sessionStorage : window.localStorage; }
  function lerEu() {
    try { return JSON.parse(gaveta().getItem(CHAVE_EU)); } catch (e) { return null; }
  }
  function gravarEu() {
    try {
      if (!eu) gaveta().removeItem(CHAVE_EU);
      else gaveta().setItem(CHAVE_EU, JSON.stringify({ id: eu.id, iniciais: eu.iniciais, grupo: eu.grupo, sim: sim, turnos: turnos }));
    } catch (e) { /* navegação privada: a sessão vale só enquanto a aba estiver aberta */ }
  }

  // ------------------------------------------------------------------- sala

  function carregarBiblioteca() {
    if (DEMO || window.supabase) return Promise.resolve();
    return new Promise(function (resolver) {
      var script = document.createElement('script');
      var relogio = setTimeout(resolver, ESPERA_BIBLIOTECA);
      script.src = BIBLIOTECA;
      script.onload = script.onerror = function () { clearTimeout(relogio); resolver(); };
      document.head.appendChild(script);
    });
  }

  function carregarCotacoes() {
    return fetch(COTACOES).then(function (resposta) {
      if (!resposta.ok) throw new Error('o servidor respondeu ' + resposta.status);
      return resposta.json();
    }).then(function (dados) {
      cotacoes = dados;
      tickers = Object.keys(dados.precos).sort();
    });
  }

  function atualizarAviso() {
    var aviso = $('#aviso');
    var semBanco = sala && sala.tipo === 'memoria' && !DEMO;
    aviso.hidden = !semBanco;
    if (semBanco) {
      $('#aviso-texto').textContent = 'Sala sem conexão com o banco (' + sala.motivo +
        '). Montar e simular funcionam normalmente; o painel mostra só quem entrou por este navegador.';
    }
    $('#rodape-modo').textContent = DEMO ? 'Modo de demonstração: a sala fica só neste navegador.' : '';
  }

  // Refaz no destino atual o que este navegador já tinha registrado.
  function ressincronizar() {
    var pendentes = [];
    if (carteiraValida()) pendentes.push(sala.salvar(eu.id, registro()));
    turnos.forEach(function (turno) { pendentes.push(sala.marcar(eu.id, turno, true)); });
    return Promise.all(pendentes);
  }

  function reentrar() {
    return sala.entrar(eu.iniciais, eu.grupo).then(function (id) {
      eu.id = id;
      gravarEu();
      return ressincronizar();
    });
  }

  // Participante guardado de uma visita anterior. O id só vale no lugar em que
  // foi criado: um id de memória não existe no banco, e um id do banco não
  // existe na memória de uma sala que já abriu sem conexão.
  function recuperar() {
    var guardado = lerEu();
    if (!guardado || !guardado.id) return Promise.resolve();
    eu = { id: guardado.id, iniciais: guardado.iniciais, grupo: guardado.grupo };
    turnos = (guardado.turnos || []).filter(function (t) { return t >= 1 && t <= 5; });
    if (guardado.sim && Array.isArray(guardado.sim.ativos)) {
      sim = guardado.sim;
      sim.ativos = sim.ativos.filter(function (t) { return cotacoes.precos[t]; }).slice(0, MAXIMO);
      if (PERIODOS.indexOf(sim.pregoes) < 0) sim.pregoes = 252;
      if (QUANTIDADES.indexOf(sim.n) < 0) sim.n = 1000;
      if (!sim.semente) sim.semente = semente();
      if (sim.pesos && sim.pesos.length !== sim.ativos.length) sim.pesos = null;
    }
    if (sala.tipo === 'memoria') {
      return sala.sala().then(function (lista) {
        var existe = lista.some(function (p) { return p.id === eu.id; });
        if (existe) { sala.conhecer(eu.id, eu.iniciais, eu.grupo); return null; }
        return reentrar();
      });
    }
    if (/^m[a-z0-9]+$/.test(eu.id)) return reentrar();
    sala.conhecer(eu.id, eu.iniciais, eu.grupo);
    return Promise.resolve();
  }

  function carteiraValida() {
    return eu && sim.ativos.length >= MINIMO && sim.ativos.length <= MAXIMO &&
      N.pregoesDisponiveis(cotacoes, sim.ativos) >= sim.pregoes;
  }
  function registro() {
    return { ativos: sim.ativos.slice(), pregoes: sim.pregoes, n: sim.n, semente: sim.semente, pesos: sim.pesos };
  }

  function guardar() {
    gravarEu();
    clearTimeout(relogioSalvar);
    if (!carteiraValida()) return;
    relogioSalvar = setTimeout(function () {
      sala.salvar(eu.id, registro()).catch(function () { /* a sala já caiu para memória */ }).then(function () {
        salvamentos += 1;
        document.body.setAttribute('data-salvo', String(salvamentos));
        atualizarAviso();
      });
    }, 300);
  }

  // ------------------------------------------------------------- navegação

  function mostrar(tela) {
    telaAtual = tela;
    document.body.setAttribute('data-tela', tela);
    $$('.tela').forEach(function (secao) { secao.hidden = secao.getAttribute('data-tela') !== tela; });
    $$('.sim-nav a').forEach(function (link) {
      if (link.getAttribute('data-nav') === tela) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    var quem = $('.sim-eu');
    quem.hidden = !eu;
    if (eu) pintarAvatar($('#eu-avatar'), eu);
    window.scrollTo(0, 0);
  }

  function rota() {
    if (!cotacoes || !sala) return;
    var destino = window.location.hash.replace(/^#/, '');
    if (!destino) destino = PAINEL_DIRETO ? 'painel' : (eu ? 'montar' : 'entrar');
    if (destino.indexOf('ver=') === 0) { mostrar('ver'); abrirSimulacaoDe(destino.slice(4)); return; }
    // O telão só tem painel e simulação: qualquer outro destino volta ao painel.
    if (TELAO && destino !== 'painel') { window.location.replace('#painel'); return; }
    if (TELAS.indexOf(destino) < 0) destino = eu ? 'montar' : 'entrar';
    if (!eu && destino !== 'entrar' && destino !== 'painel') { window.location.replace('#entrar'); return; }
    if (eu && destino === 'entrar') { window.location.replace('#montar'); return; }
    mostrar(destino);
    if (destino === 'entrar') desenharVitrine();
    if (destino === 'montar') atualizarMontagem();
    if (destino === 'simular') atualizarSimulacao();
    if (destino === 'progresso') atualizarProgresso();
    if (destino === 'painel') carregarPainel();
  }

  // ---------------------------------------------------------------- avatar

  function pintarAvatar(no, pessoa) {
    no.textContent = pessoa.iniciais;
    no.setAttribute('data-grupo', pessoa.grupo || '');
  }

  // ---------------------------------------------------------------- entrar

  function iniciaisLimpas(texto) {
    return texto.toLocaleUpperCase('pt-BR').replace(/[^A-ZÀ-Ý]/g, '').slice(0, 3);
  }

  function prepararEntrada() {
    var campo = $('#iniciais');
    var previa = $('#previa');
    function atualizar() {
      var grupo = $('input[name="grupo"]:checked');
      previa.textContent = campo.value || '?';
      previa.setAttribute('data-grupo', grupo ? grupo.value : '');
    }
    campo.addEventListener('input', function () {
      campo.value = iniciaisLimpas(campo.value);
      $('#entrar-erro').textContent = '';
      atualizar();
    });
    $$('input[name="grupo"]').forEach(function (radio) {
      radio.addEventListener('change', function () { $('#entrar-erro').textContent = ''; atualizar(); });
    });
    atualizar();

    $('#form-entrar').addEventListener('submit', function (evento) {
      evento.preventDefault();
      var iniciais = iniciaisLimpas(campo.value);
      var grupo = $('input[name="grupo"]:checked');
      var erro = $('#entrar-erro');
      if (!iniciais) { erro.textContent = 'Informe de 1 a 3 letras.'; campo.focus(); return; }
      if (!grupo) { erro.textContent = 'Escolha o grupo.'; return; }
      var botao = $('#entrar-botao');
      botao.disabled = true;
      botao.textContent = 'Entrando na sala';
      sala.entrar(iniciais, grupo.value).then(function (id) {
        eu = { id: id, iniciais: iniciais, grupo: grupo.value };
        turnos = [];
        sim = simulacaoNova();
        gravarEu();
        atualizarAviso();
        window.location.hash = '#montar';
      }).catch(function (falha) {
        erro.textContent = 'A entrada falhou: ' + ((falha && falha.message) || 'erro desconhecido') + '. Tente de novo.';
      }).then(function () {
        botao.disabled = false;
        botao.textContent = 'Entrar na sala';
      });
    });

    $('#sair').addEventListener('click', function () {
      if (!window.confirm('Sair da sala neste navegador? A carteira montada aqui é descartada.')) return;
      eu = null;
      turnos = [];
      sim = simulacaoNova();
      gravarEu();
      campo.value = '';
      $$('input[name="grupo"]').forEach(function (radio) { radio.checked = false; });
      atualizar();
      window.location.hash = '#entrar';
    });
  }

  // Nuvem de abertura: uma carteira de exemplo com dados reais do arquivo.
  function desenharVitrine() {
    var exemplo = ['PETR4', 'VALE3', 'ITUB4'].filter(function (t) { return cotacoes.precos[t]; });
    var tela = $('#vitrine');
    if (exemplo.length < 2 || N.pregoesDisponiveis(cotacoes, exemplo) < 252) { tela.parentNode.hidden = true; return; }
    var linhas = N.retornos(cotacoes, exemplo, 252).linhas;
    var resultado = N.simular(linhas, 2000, 18, cotacoes.rf_anual);
    desenharNuvem(tela, { resultado: resultado, n: 2000, rf: cotacoes.rf_anual, marcas: [], enxuta: true });
    $('#vitrine-legenda').textContent = '2.000 carteiras sorteadas com ' + exemplo.join(', ').replace(/, ([^,]*)$/, ' e $1') +
      ' em 252 pregões. Cada ponto é uma combinação de pesos: risco anual na horizontal, retorno anual na vertical.';
  }

  // ---------------------------------------------------------------- montar

  function avisarBusca(texto) { $('#busca-erro').textContent = texto; }

  function sugerir(consulta) {
    if (!consulta) return [];
    var comeca = tickers.filter(function (t) { return t.indexOf(consulta) === 0; });
    var contem = tickers.filter(function (t) { return t.indexOf(consulta) > 0; });
    return comeca.concat(contem).filter(function (t) { return sim.ativos.indexOf(t) < 0; }).slice(0, 8);
  }

  function adicionar(bruto) {
    var ticker = bruto.trim().toUpperCase().replace(/\.SA$/, '');
    if (!ticker) { avisarBusca('Digite o código do ativo.'); return false; }
    if (!cotacoes.precos[ticker]) {
      avisarBusca(ticker + ': ativo não encontrado no arquivo da aula. Troque por outro do mesmo setor.');
      return false;
    }
    if (sim.ativos.indexOf(ticker) >= 0) { avisarBusca(ticker + ' já está na carteira.'); return false; }
    if (sim.ativos.length >= MAXIMO) { avisarBusca('A carteira aceita até ' + MAXIMO + ' ativos. Remova um para trocar.'); return false; }
    sim.ativos.push(ticker);
    sim.pesos = null;
    avisarBusca('');
    ajustarPeriodo();
    guardar();
    atualizarMontagem();
    return true;
  }

  function remover(ticker) {
    sim.ativos = sim.ativos.filter(function (t) { return t !== ticker; });
    sim.pesos = null;
    avisarBusca('');
    ajustarPeriodo();
    guardar();
    atualizarMontagem();
  }

  // O período escolhido não pode passar da janela comum dos ativos.
  function ajustarPeriodo() {
    if (!sim.ativos.length) return;
    var disponiveis = N.pregoesDisponiveis(cotacoes, sim.ativos);
    if (sim.pregoes <= disponiveis) return;
    var cabem = PERIODOS.filter(function (p) { return p <= disponiveis; });
    if (cabem.length) sim.pregoes = cabem[cabem.length - 1];
  }

  function prepararBusca() {
    var campo = $('#busca');
    var lista = $('#sugestoes');
    var marcada = -1;

    function fechar() { lista.hidden = true; campo.setAttribute('aria-expanded', 'false'); marcada = -1; }
    function abrir() {
      var opcoes = sugerir(campo.value);
      limpar(lista);
      marcada = -1;
      if (!opcoes.length) { fechar(); return; }
      opcoes.forEach(function (ticker, i) {
        var item = criar('li', { role: 'option', id: 'sugestao-' + i, 'data-ticker': ticker, texto: ticker });
        item.addEventListener('mousedown', function (evento) {
          evento.preventDefault();
          if (adicionar(ticker)) campo.value = '';
          fechar();
        });
        lista.appendChild(item);
      });
      lista.hidden = false;
      campo.setAttribute('aria-expanded', 'true');
    }
    function marcar(indice) {
      var itens = $$('li', lista);
      if (!itens.length) return;
      marcada = (indice + itens.length) % itens.length;
      itens.forEach(function (item, i) { item.setAttribute('aria-selected', i === marcada ? 'true' : 'false'); });
      campo.setAttribute('aria-activedescendant', itens[marcada].id);
    }

    campo.addEventListener('input', function () {
      campo.value = campo.value.toUpperCase().replace(/[^A-Z0-9.]/g, '');
      avisarBusca('');
      abrir();
    });
    campo.addEventListener('keydown', function (evento) {
      if (evento.key === 'ArrowDown') { evento.preventDefault(); if (lista.hidden) abrir(); marcar(marcada + 1); }
      else if (evento.key === 'ArrowUp') { evento.preventDefault(); marcar(marcada - 1); }
      else if (evento.key === 'Escape') fechar();
    });
    campo.addEventListener('blur', fechar);
    $('#form-busca').addEventListener('submit', function (evento) {
      evento.preventDefault();
      var itens = $$('li', lista);
      var escolhido = marcada >= 0 && itens[marcada] ? itens[marcada].getAttribute('data-ticker') : campo.value;
      if (adicionar(escolhido)) campo.value = '';
      fechar();
      campo.focus();
    });
  }

  function desenharAtivos() {
    var lista = $('#ativos');
    limpar(lista);
    var total = cotacoes.datas.length;
    sim.ativos.forEach(function (ticker) {
      var serie = cotacoes.precos[ticker];
      var primeiro = 0;
      while (serie[primeiro] === null) primeiro++;
      var detalhe = primeiro > 0 ? 'cotação desde ' + data(cotacoes.datas[primeiro]) : reais(serie[total - 1]) + ' em ' + data(cotacoes.corte);
      var botao = criar('button', { type: 'button', classe: 'ativo-remover', 'aria-label': 'Remover ' + ticker, texto: 'Remover' });
      botao.addEventListener('click', function () { remover(ticker); });
      lista.appendChild(criar('li', { classe: 'ativo' + (primeiro > 0 ? ' ativo-tardio' : ''), 'data-ticker': ticker }, [
        criar('strong', { texto: ticker }), criar('span', { texto: detalhe }), botao
      ]));
    });
    var faltam = MINIMO - sim.ativos.length;
    $('#ativos-ajuda').textContent = !sim.ativos.length ? 'Nenhum ativo na carteira. O arquivo da aula tem ' + tickers.length + ' ativos.'
      : faltam > 0 ? 'Falta 1 ativo para calcular.'
      : sim.ativos.length + ' de ' + MAXIMO + ' ativos.';
  }

  function desenharSegmentos() {
    var disponiveis = sim.ativos.length ? N.pregoesDisponiveis(cotacoes, sim.ativos) : cotacoes.datas.length - 1;
    $$('.periodos').forEach(function (grupo) {
      limpar(grupo);
      PERIODOS.forEach(function (pregoes) {
        var botao = criar('button', {
          type: 'button', 'data-pregoes': pregoes, texto: String(pregoes),
          'aria-pressed': pregoes === sim.pregoes ? 'true' : 'false'
        });
        if (pregoes > disponiveis) {
          botao.disabled = true;
          botao.title = 'A janela comum tem ' + inteiro(disponiveis) + ' pregões';
        }
        botao.addEventListener('click', function () {
          sim.pregoes = pregoes;
          guardar();
          if (telaAtual === 'simular') atualizarSimulacao(); else atualizarMontagem();
        });
        grupo.appendChild(botao);
      });
    });
    $$('.quantidades').forEach(function (grupo) {
      limpar(grupo);
      QUANTIDADES.forEach(function (n) {
        var botao = criar('button', {
          type: 'button', 'data-n': n, texto: inteiro(n), 'aria-pressed': n === sim.n ? 'true' : 'false'
        });
        botao.addEventListener('click', function () { sim.n = n; guardar(); atualizarSimulacao(); });
        grupo.appendChild(botao);
      });
    });
    var janela = $('#m-janela');
    janela.setAttribute('data-disponiveis', String(disponiveis));
    if (!sim.ativos.length) janela.textContent = 'O arquivo tem ' + inteiro(disponiveis) + ' pregões, de ' + data(cotacoes.inicio) + ' a ' + data(cotacoes.corte) + '.';
    else {
      var fora = PERIODOS.filter(function (p) { return p > disponiveis; });
      janela.textContent = 'A janela comum ' + (sim.ativos.length > 1 ? 'destes ativos' : 'deste ativo') + ' tem ' + inteiro(disponiveis) + ' pregões' +
        (fora.length ? ', então ' + fora.join(' e ') + (fora.length > 1 ? ' ficam indisponíveis.' : ' fica indisponível.') : '.');
    }
    $('#nota-periodo').classList.toggle('nota-forte', sim.pregoes === 9);
  }

  function atualizarMontagem() {
    desenharAtivos();
    desenharSegmentos();
    var pronto = sim.ativos.length >= MINIMO && N.pregoesDisponiveis(cotacoes, sim.ativos) >= sim.pregoes;
    $('#montar-vazio').hidden = pronto;
    $('#montar-resultado').hidden = !pronto;
    if (!pronto) return;

    var k = sim.ativos.length;
    var pesos = pesosIguais(k);
    var janela = N.retornos(cotacoes, sim.ativos, sim.pregoes);
    var medidas = N.metricas(pesos, janela.linhas);
    var serie = N.serieDaCarteira(pesos, janela.linhas);

    var retorno = $('#m-retorno');
    var risco = $('#m-risco');
    retorno.setAttribute('data-valor', String(medidas.retorno));
    risco.setAttribute('data-valor', String(medidas.risco));
    retorno.textContent = porcento(medidas.retorno);
    risco.textContent = porcento(medidas.risco);
    $('#m-retorno-dec').textContent = decimal(medidas.retorno);
    $('#m-risco-dec').textContent = decimal(medidas.risco);
    $('#m-pesos').textContent = 'Pesos iguais: ' + porcento(1 / k) + ' em cada um dos ' + k + ' ativos, de ' +
      data(janela.datas[0]) + ' a ' + data(janela.datas[janela.datas.length - 1]) + '.';

    var total = cotacoes.datas.length;
    var valores = [CAPITAL];
    var datas = [cotacoes.datas[total - sim.pregoes - 1]];
    for (var t = 0; t < serie.length; t++) {
      valores.push(valores[t] * (1 + serie[t]));
      datas.push(janela.datas[t]);
    }
    var final = valores[valores.length - 1];
    $('#m-evolucao-titulo').textContent = reais(CAPITAL) + ' aplicados na carteira ' + (final >= CAPITAL ? 'sobem' : 'caem') +
      ' para ' + reais(final) + ' em ' + sim.pregoes + ' pregões';
    var nota = $('#m-final');
    nota.setAttribute('data-valor', String(final));
    nota.textContent = 'Variação no período: ' + porcento(final / CAPITAL - 1) + '. Aplicação em ' + data(datas[0]) +
      ', valor em ' + data(datas[datas.length - 1]) + '.';
    evolucao = { valores: valores, datas: datas };
    desenharEvolucao();

    var diaria = $('#bloco-diaria');
    diaria.hidden = sim.pregoes !== 9;
    if (sim.pregoes === 9) desenharTabelaDiaria(janela, serie);
    aplicarDecimal();
  }

  function desenharTabelaDiaria(janela, serie) {
    var tabela = $('#tabela-diaria');
    limpar(tabela);
    var cabeca = criar('tr', {}, [criar('th', { scope: 'col', texto: 'Pregão' })]);
    sim.ativos.forEach(function (ticker) { cabeca.appendChild(criar('th', { scope: 'col', classe: 'num', texto: ticker })); });
    cabeca.appendChild(criar('th', { scope: 'col', classe: 'num destaque', texto: 'Carteira' }));
    tabela.appendChild(criar('thead', {}, [cabeca]));
    var corpo = criar('tbody');
    janela.linhas.forEach(function (linha, t) {
      var tr = criar('tr', { 'data-data': janela.datas[t] }, [criar('th', { scope: 'row', texto: data(janela.datas[t]) })]);
      linha.forEach(function (valor, a) { tr.appendChild(celula(valor, { 'data-ativo': sim.ativos[a] })); });
      tr.appendChild(celula(serie[t], { 'data-ativo': 'carteira', classe: 'num destaque' }));
      corpo.appendChild(tr);
    });
    tabela.appendChild(corpo);
  }

  // Célula numérica com as duas leituras: porcentagem e decimal com 6 casas.
  function celula(valor, atributos) {
    var td = criar('td', { classe: 'num', 'data-valor': String(valor) });
    Object.keys(atributos).forEach(function (nome) {
      if (nome === 'classe') td.className = atributos[nome]; else td.setAttribute(nome, atributos[nome]);
    });
    td.appendChild(criar('span', { classe: 'em-porcento', texto: porcento(valor) }));
    td.appendChild(criar('code', { classe: 'em-decimal', texto: decimal(valor) }));
    return td;
  }

  function aplicarDecimal() {
    document.body.classList.toggle('mostra-decimal', $('#decimal').checked);
  }

  // Evolução do valor aplicado: gráfico de linha em canvas.
  var evolucao = null;
  var geometriaEvolucao = null;

  function prepararTela(tela, altura) {
    var largura = tela.parentNode.clientWidth;
    if (!largura) return null;
    var razao = window.devicePixelRatio || 1;
    tela.style.height = altura + 'px';
    tela.width = Math.round(largura * razao);
    tela.height = Math.round(altura * razao);
    var ctx = tela.getContext('2d');
    ctx.setTransform(razao, 0, 0, razao, 0, 0);
    ctx.clearRect(0, 0, largura, altura);
    return { ctx: ctx, largura: largura, altura: altura };
  }

  function marcasDoEixo(minimo, maximo, alvo) {
    var faixa = (maximo - minimo) || 1;
    var bruto = faixa / alvo;
    var passo = Math.pow(10, Math.floor(Math.log(bruto) / Math.LN10));
    var resto = bruto / passo;
    passo *= resto >= 5 ? 10 : resto >= 2 ? 5 : resto >= 1 ? 2 : 1;
    var marcas = [];
    for (var v = Math.ceil(minimo / passo) * passo; v <= maximo + passo * 1e-9; v += passo) marcas.push(Math.abs(v) < passo * 1e-9 ? 0 : v);
    return { marcas: marcas, passo: passo };
  }

  function desenharEvolucao() {
    if (!evolucao) return;
    var tela = $('#evolucao');
    var estreito = tela.parentNode.clientWidth < 520;
    var area = prepararTela(tela, estreito ? 220 : 280);
    if (!area) return;
    var ctx = area.ctx;
    var roxo = rgb('--inteli-roxo');
    var verde = rgb('--inteli-verde');
    var cinza = rgb('--inteli-cinza-escuro');
    var claro = rgb('--inteli-cinza-claro');
    var valores = evolucao.valores;
    var minimo = Math.min.apply(null, valores);
    var maximo = Math.max.apply(null, valores);
    var folga = (maximo - minimo) * 0.12 || CAPITAL * 0.01;
    minimo -= folga; maximo += folga;
    var m = { esq: estreito ? 62 : 78, dir: 18, topo: 14, base: 30 };
    var w = area.largura - m.esq - m.dir;
    var h = area.altura - m.topo - m.base;
    function x(i) { return m.esq + w * i / (valores.length - 1); }
    function y(v) { return m.topo + h * (1 - (v - minimo) / (maximo - minimo)); }

    var eixo = marcasDoEixo(minimo, maximo, 4);
    ctx.font = fonte(12, 300);
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'right';
    eixo.marcas.forEach(function (v) {
      ctx.strokeStyle = tinta(claro);
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(m.esq, Math.round(y(v)) + 0.5); ctx.lineTo(m.esq + w, Math.round(y(v)) + 0.5); ctx.stroke();
      ctx.fillStyle = tinta(roxo);
      ctx.fillText(estreito ? numero(v / 1000, eixo.passo < 1000 ? 1 : 0) + ' mil' : inteiro(v), m.esq - 10, y(v));
    });

    // Valor aplicado, como referência
    ctx.setLineDash([5, 4]);
    ctx.strokeStyle = tinta(cinza);
    ctx.beginPath(); ctx.moveTo(m.esq, y(CAPITAL)); ctx.lineTo(m.esq + w, y(CAPITAL)); ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.moveTo(x(0), y(valores[0]));
    for (var i = 1; i < valores.length; i++) ctx.lineTo(x(i), y(valores[i]));
    ctx.lineTo(x(valores.length - 1), m.topo + h);
    ctx.lineTo(x(0), m.topo + h);
    ctx.closePath();
    ctx.fillStyle = tinta(verde, 0.28);
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(x(0), y(valores[0]));
    for (var j = 1; j < valores.length; j++) ctx.lineTo(x(j), y(valores[j]));
    ctx.strokeStyle = tinta(roxo);
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.stroke();

    var ultimo = valores.length - 1;
    ctx.fillStyle = tinta(roxo);
    ctx.beginPath(); ctx.arc(x(ultimo), y(valores[ultimo]), 4.5, 0, Math.PI * 2); ctx.fill();

    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = tinta(roxo);
    ctx.textAlign = 'left';
    ctx.fillText(data(evolucao.datas[0]), m.esq, area.altura - 8);
    ctx.textAlign = 'right';
    ctx.fillText(data(evolucao.datas[ultimo]), m.esq + w, area.altura - 8);

    geometriaEvolucao = { x: x, y: y, m: m, w: w, h: h };
  }

  function prepararEvolucao() {
    var palco = $('#evolucao-palco');
    var fio = $('#evolucao-fio');
    var dica = $('#evolucao-dica');
    function sumir() { fio.hidden = true; dica.hidden = true; }
    palco.addEventListener('pointermove', function (evento) {
      if (!evolucao || !geometriaEvolucao) return;
      var g = geometriaEvolucao;
      var caixa = palco.getBoundingClientRect();
      var px = evento.clientX - caixa.left;
      var i = Math.round((px - g.m.esq) / g.w * (evolucao.valores.length - 1));
      if (i < 0 || i >= evolucao.valores.length) { sumir(); return; }
      fio.hidden = false;
      fio.style.left = g.x(i) + 'px';
      fio.style.top = g.m.topo + 'px';
      fio.style.height = g.h + 'px';
      dica.hidden = false;
      limpar(dica);
      dica.appendChild(criar('strong', { texto: reais(evolucao.valores[i]) }));
      dica.appendChild(criar('span', { texto: data(evolucao.datas[i]) }));
      posicionarDica(dica, palco, g.x(i), g.y(evolucao.valores[i]));
    });
    palco.addEventListener('pointerleave', sumir);
  }

  function posicionarDica(dica, palco, px, py) {
    var largura = dica.offsetWidth;
    var esquerda = px + 14;
    if (esquerda + largura > palco.clientWidth - 4) esquerda = px - largura - 14;
    dica.style.left = Math.max(4, esquerda) + 'px';
    dica.style.top = Math.max(4, py - dica.offsetHeight - 10) + 'px';
  }

  // --------------------------------------------------------------- simular

  // Calcula a simulação e as carteiras em destaque. `parametros` segue o
  // registro da sala: {ativos, pregoes, n, semente, pesos}.
  function calcular(parametros) {
    var linhas = N.retornos(cotacoes, parametros.ativos, parametros.pregoes).linhas;
    var rf = cotacoes.rf_anual;
    var inicio = performance.now();
    var resultado = N.simular(linhas, parametros.n, parametros.semente, rf);
    var melhor = 0;
    for (var i = 1; i < parametros.n; i++) if (resultado.sharpe[i] > resultado.sharpe[melhor]) melhor = i;
    var k = parametros.ativos.length;
    var iguais = pesosIguais(k);
    var destaques = [];
    if (parametros.n > 0) {
      destaques.push({
        id: 'melhor', nome: 'Melhor Sharpe sorteado', pesos: resultado.pesos[melhor],
        retorno: resultado.retorno[melhor], risco: resultado.risco[melhor], sharpe: resultado.sharpe[melhor]
      });
    }
    var pontoIguais = N.posicionar(iguais, linhas, rf);
    destaques.push({ id: 'iguais', nome: 'Pesos iguais', pesos: iguais, retorno: pontoIguais.retorno, risco: pontoIguais.risco, sharpe: pontoIguais.sharpe });
    if (parametros.pesos && parametros.pesos.length === k) {
      var proprio = N.posicionar(parametros.pesos, linhas, rf);
      destaques.push({ id: 'proprios', nome: 'Seus pesos', pesos: parametros.pesos, retorno: proprio.retorno, risco: proprio.risco, sharpe: proprio.sharpe });
    }
    return { resultado: resultado, n: parametros.n, rf: rf, marcas: destaques, ativos: parametros.ativos, ms: performance.now() - inicio };
  }

  function pesosEmTexto(ativos, pesos) {
    return ativos.map(function (ticker, a) { return ticker + ' ' + porcento(pesos[a], 1); }).join(', ');
  }

  // Monta o bloco da nuvem (canvas, legenda, leitura e tabela) dentro de `raiz`.
  function mostrarSimulacao(raiz, parametros, dono) {
    if (!raiz.firstChild) raiz.appendChild($('#molde-nuvem').content.cloneNode(true));
    var tela = $('.nuvem-tela', raiz);
    tela.setAttribute('data-pronto', 'nao');
    var calculo = calcular(parametros);
    raiz.calculo = calculo;
    ajustarAoTelao(raiz, calculo);
    desenharNuvem(tela, calculo);

    var sharpe = calculo.resultado.sharpe;
    var menor = Infinity, maior = -Infinity;
    for (var i = 0; i < calculo.n; i++) { if (sharpe[i] < menor) menor = sharpe[i]; if (sharpe[i] > maior) maior = sharpe[i]; }
    $('.escala-min', raiz).textContent = numero(menor, 2);
    $('.escala-max', raiz).textContent = numero(maior, 2);
    var temProprios = calculo.marcas.some(function (m) { return m.id === 'proprios'; });
    $('.legenda-proprios', raiz).hidden = !temProprios;
    if (dono) $('.legenda-proprios', raiz).lastChild.textContent = 'Pesos de ' + dono;

    var corpo = $('.destaques tbody', raiz);
    limpar(corpo);
    calculo.marcas.forEach(function (marca) {
      var nome = marca.id === 'proprios' && dono ? 'Pesos de ' + dono : marca.nome;
      var tr = criar('tr', {
        'data-carteira': marca.id, 'data-retorno': String(marca.retorno),
        'data-risco': String(marca.risco), 'data-sharpe': String(marca.sharpe)
      }, [
        criar('th', { scope: 'row', texto: nome }),
        criar('td', { texto: pesosEmTexto(calculo.ativos, marca.pesos) }),
        celula(marca.retorno, {}), celula(marca.risco, {}),
        criar('td', { classe: 'num', texto: numero(marca.sharpe, 2) })
      ]);
      corpo.appendChild(tr);
    });

    var melhor = calculo.marcas[0];
    var iguais = calculo.marcas.filter(function (m) { return m.id === 'iguais'; })[0];
    var texto = 'Entre ' + (calculo.n === 1 ? 'a carteira sorteada' : 'as ' + inteiro(calculo.n) + ' carteiras sorteadas') +
      ', o maior Sharpe foi ' + numero(melhor.sharpe, 2) + ', com retorno de ' + porcento(melhor.retorno) +
      ' ao ano e risco de ' + porcento(melhor.risco) + ' (' + pesosEmTexto(calculo.ativos, melhor.pesos) + '). ' +
      'A carteira de pesos iguais tem Sharpe ' + numero(iguais.sharpe, 2) + '. A taxa livre de risco do período é ' +
      porcento(calculo.rf) + ' ao ano.';
    $('.leitura', raiz).textContent = texto;

    tela.setAttribute('data-n', String(calculo.n));
    tela.setAttribute('data-semente', String(parametros.semente));
    tela.setAttribute('data-ms', String(Math.round(calculo.ms)));
    tela.setAttribute('data-pronto', 'sim');
    ligarDica(raiz);
  }

  // No telão o canvas é absoluto dentro do palco, e o palco tem a altura que a
  // grade da tela lhe dá. A nuvem é desenhada nessa altura.
  function ajustarAoTelao(raiz, calculo) {
    if (!TELAO) return;
    calculo.altura = Math.max(200, $('.nuvem-palco', raiz).clientHeight);
    calculo.escala = Math.max(1.15, Math.min(2.2, window.innerHeight / 470));
  }

  // Nuvem em canvas: risco no eixo x, retorno no eixo y, cor pelo Sharpe.
  function desenharNuvem(tela, calculo) {
    var largura = tela.parentNode.clientWidth;
    if (!largura) return;
    var estreito = largura < 520;
    // No telão a altura vem do palco, que ocupa o que sobra da tela, e `e`
    // aumenta letra, margem e ponto para a leitura do fundo da sala.
    var e = calculo.escala || 1;
    var altura = calculo.altura ? calculo.altura
      : calculo.enxuta ? Math.max(240, Math.min(460, Math.round(largura * 0.8)))
      : Math.max(280, Math.min(480, Math.round(largura * (estreito ? 0.82 : 0.56))));
    var area = prepararTela(tela, altura);
    var ctx = area.ctx;
    var r = calculo.resultado;
    var n = calculo.n;
    var branco = rgb('--inteli-branco');
    var verde = rgb('--inteli-verde');
    var coral = rgb('--inteli-coral');
    var roxo = rgb('--inteli-roxo');
    var fundo = misturar(roxo, rgb('--inteli-cinza-escuro'), 0.6);

    var xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity, sMin = Infinity, sMax = -Infinity;
    function incluir(risco, retorno) {
      if (risco < xMin) xMin = risco; if (risco > xMax) xMax = risco;
      if (retorno < yMin) yMin = retorno; if (retorno > yMax) yMax = retorno;
    }
    for (var i = 0; i < n; i++) {
      incluir(r.risco[i], r.retorno[i]);
      if (r.sharpe[i] < sMin) sMin = r.sharpe[i]; if (r.sharpe[i] > sMax) sMax = r.sharpe[i];
    }
    calculo.marcas.forEach(function (marca) { incluir(marca.risco, marca.retorno); });
    if (!calculo.enxuta) { if (calculo.rf < yMin) yMin = calculo.rf; if (calculo.rf > yMax) yMax = calculo.rf; }
    var fx = (xMax - xMin) * 0.08 || 0.01;
    var fy = (yMax - yMin) * 0.1 || 0.01;
    xMin -= fx; xMax += fx; yMin -= fy; yMax += fy;

    var m = calculo.enxuta ? { esq: 18, dir: 18, topo: 18, base: 18 }
      : { esq: (estreito ? 50 : 64) * e, dir: 20 * e, topo: 22 * e, base: (estreito ? 44 : 50) * e };
    var w = area.largura - m.esq - m.dir;
    var h = area.altura - m.topo - m.base;
    function x(risco) { return m.esq + w * (risco - xMin) / (xMax - xMin); }
    function y(retorno) { return m.topo + h * (1 - (retorno - yMin) / (yMax - yMin)); }

    if (!calculo.enxuta) {
      var ex = marcasDoEixo(xMin, xMax, estreito ? 4 : 6);
      var ey = marcasDoEixo(yMin, yMax, 5);
      var casasX = ex.passo >= 0.01 ? 0 : ex.passo >= 0.001 ? 1 : 2;
      var casasY = ey.passo >= 0.01 ? 0 : ey.passo >= 0.001 ? 1 : 2;
      ctx.lineWidth = 1;
      ctx.font = fonte(Math.round(12 * e), 300);
      ctx.fillStyle = tinta(branco, 0.82);
      ctx.strokeStyle = tinta(branco, 0.1);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ey.marcas.forEach(function (v) {
        ctx.beginPath(); ctx.moveTo(m.esq, Math.round(y(v)) + 0.5); ctx.lineTo(m.esq + w, Math.round(y(v)) + 0.5); ctx.stroke();
        ctx.fillText(porcento(v, casasY), m.esq - 8, y(v));
      });
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ex.marcas.forEach(function (v) {
        ctx.beginPath(); ctx.moveTo(Math.round(x(v)) + 0.5, m.topo); ctx.lineTo(Math.round(x(v)) + 0.5, m.topo + h); ctx.stroke();
        ctx.fillText(porcento(v, casasX), x(v), m.topo + h + 8);
      });
      ctx.font = fonte(Math.round(12 * e), 600);
      ctx.fillStyle = tinta(branco);
      ctx.fillText('Risco anual', m.esq + w / 2, area.altura - 18 * e);
      ctx.save();
      ctx.translate(14 * e, m.topo + h / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.textBaseline = 'middle';
      ctx.fillText('Retorno anual', 0, 0);
      ctx.restore();

      // Taxa livre de risco
      ctx.setLineDash([6, 5]);
      ctx.strokeStyle = tinta(branco, 0.9);
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(m.esq, y(calculo.rf)); ctx.lineTo(m.esq + w, y(calculo.rf)); ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = fonte(Math.round(12 * e), 600);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      ctx.fillStyle = tinta(branco);
      ctx.fillText('Taxa livre de risco ' + porcento(calculo.rf), m.esq + w - 4, y(calculo.rf) - 4);
    }

    // Pontos em faixas de Sharpe, da menor para a maior: os melhores ficam por cima.
    var FAIXAS = 20;
    var raio = (n <= 10 ? 6 : n <= 100 ? 4.5 : n <= 1000 ? 2.6 : 1.7) * (1 + (e - 1) * 0.6);
    var alfa = n <= 100 ? 0.95 : n <= 1000 ? 0.8 : 0.62;
    var faixas = [];
    for (var f = 0; f < FAIXAS; f++) faixas.push([]);
    var px = new Float32Array(n);
    var py = new Float32Array(n);
    var amplitude = (sMax - sMin) || 1;
    for (var p = 0; p < n; p++) {
      px[p] = x(r.risco[p]);
      py[p] = y(r.retorno[p]);
      faixas[Math.min(FAIXAS - 1, Math.floor((r.sharpe[p] - sMin) / amplitude * FAIXAS))].push(p);
    }
    faixas.forEach(function (indices, faixa) {
      if (!indices.length) return;
      ctx.fillStyle = tinta(misturar(fundo, verde, faixa / (FAIXAS - 1)), alfa);
      ctx.beginPath();
      indices.forEach(function (q) { ctx.moveTo(px[q] + raio, py[q]); ctx.arc(px[q], py[q], raio, 0, Math.PI * 2); });
      ctx.fill();
    });

    calculo.marcas.forEach(function (marca) {
      var cx = x(marca.risco), cy = y(marca.retorno);
      var d = 10 * e;
      ctx.lineWidth = 2.5 * e;
      if (marca.id === 'melhor') {
        ctx.beginPath(); ctx.arc(cx, cy, 8 * e, 0, Math.PI * 2);
        ctx.fillStyle = tinta(verde); ctx.fill();
        ctx.strokeStyle = tinta(branco); ctx.stroke();
      } else if (marca.id === 'iguais') {
        ctx.beginPath(); ctx.arc(cx, cy, 7 * e, 0, Math.PI * 2);
        ctx.fillStyle = tinta(roxo); ctx.fill();
        ctx.strokeStyle = tinta(branco); ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.moveTo(cx, cy - d); ctx.lineTo(cx + d, cy); ctx.lineTo(cx, cy + d); ctx.lineTo(cx - d, cy);
        ctx.closePath();
        ctx.fillStyle = tinta(coral); ctx.fill();
        ctx.strokeStyle = tinta(branco); ctx.stroke();
      }
    });

    calculo.pontos = { x: px, y: py };
  }

  // Dica ao passar o ponteiro: a carteira sorteada mais próxima.
  function ligarDica(raiz) {
    if (raiz.dicaLigada) return;
    raiz.dicaLigada = true;
    var palco = $('.nuvem-palco', raiz);
    var mira = $('.nuvem-mira', raiz);
    var dica = $('.nuvem-dica', raiz);
    function sumir() { mira.hidden = true; dica.hidden = true; }
    palco.addEventListener('pointermove', function (evento) {
      var calculo = raiz.calculo;
      if (!calculo || !calculo.pontos) return;
      var caixa = palco.getBoundingClientRect();
      var mx = evento.clientX - caixa.left, my = evento.clientY - caixa.top;
      var perto = -1, distancia = 18 * 18;
      for (var i = 0; i < calculo.n; i++) {
        var dx = calculo.pontos.x[i] - mx, dy = calculo.pontos.y[i] - my;
        var d = dx * dx + dy * dy;
        if (d < distancia) { distancia = d; perto = i; }
      }
      if (perto < 0) { sumir(); return; }
      var r = calculo.resultado;
      mira.hidden = false;
      mira.style.left = calculo.pontos.x[perto] + 'px';
      mira.style.top = calculo.pontos.y[perto] + 'px';
      limpar(dica);
      dica.appendChild(criar('strong', { texto: 'Sharpe ' + numero(r.sharpe[perto], 2) }));
      dica.appendChild(criar('span', { texto: 'Retorno ' + porcento(r.retorno[perto]) + ', risco ' + porcento(r.risco[perto]) }));
      dica.appendChild(criar('span', { texto: pesosEmTexto(calculo.ativos, r.pesos[perto]) }));
      dica.hidden = false;
      posicionarDica(dica, palco, calculo.pontos.x[perto], calculo.pontos.y[perto]);
    });
    palco.addEventListener('pointerleave', sumir);
  }

  function desenharPesos() {
    var caixa = $('#pesos');
    var atuais = $$('input', caixa).map(function (campo) { return campo.getAttribute('data-peso'); }).join();
    if (atuais !== sim.ativos.join()) {
      limpar(caixa);
      sim.ativos.forEach(function (ticker, a) {
        var campo = criar('input', {
          type: 'text', inputmode: 'decimal', 'data-peso': ticker, id: 'peso-' + ticker,
          placeholder: numero(100 / sim.ativos.length, 2), autocomplete: 'off'
        });
        if (sim.pesos) campo.value = numero(sim.pesos[a] * 100, 2);
        campo.addEventListener('input', function () { $('#pesos-erro').textContent = ''; somarPesos(); });
        caixa.appendChild(criar('label', { classe: 'peso', 'for': 'peso-' + ticker }, [
          criar('span', { texto: ticker }), campo, criar('span', { classe: 'peso-unidade', texto: '%', 'aria-hidden': 'true' })
        ]));
      });
    }
    $('#pesos-limpar').hidden = !sim.pesos;
    somarPesos();
  }

  function lerPesos() {
    return $$('#pesos input').map(function (campo) {
      // "12,5", "12.5" e "12,5%" valem o mesmo; com vírgula, o ponto é separador de milhar.
      var texto = campo.value.trim().replace('%', '').trim();
      if (texto.indexOf(',') >= 0) texto = texto.replace(/\./g, '').replace(',', '.');
      return texto === '' ? NaN : Number(texto);
    });
  }

  function somarPesos() {
    var valores = lerPesos();
    var preenchidos = valores.filter(function (v) { return !isNaN(v); });
    var soma = preenchidos.reduce(function (a, b) { return a + b; }, 0);
    var saida = $('#pesos-soma');
    saida.setAttribute('data-soma', String(soma));
    saida.textContent = preenchidos.length ? 'Soma: ' + numero(soma, 2) + '%' : 'Soma: 0,00%';
    saida.classList.toggle('pesos-soma-certa', preenchidos.length === valores.length && Math.abs(soma - 100) <= 0.005);
    return { valores: valores, soma: soma };
  }

  function prepararSimulacao() {
    $('#novo-sorteio').addEventListener('click', function () {
      sim.semente = semente();
      guardar();
      atualizarSimulacao();
    });
    $('#form-pesos').addEventListener('submit', function (evento) {
      evento.preventDefault();
      var lido = somarPesos();
      var erro = $('#pesos-erro');
      if (lido.valores.some(function (v) { return isNaN(v); })) {
        erro.textContent = 'Preencha o peso de cada ativo com um número. Use 0 para deixar um ativo de fora.';
        return;
      }
      if (lido.valores.some(function (v) { return v < 0; })) {
        erro.textContent = 'Os pesos não podem ser negativos.';
        return;
      }
      if (Math.abs(lido.soma - 100) > 0.005) {
        erro.textContent = 'Os pesos somam ' + numero(lido.soma, 2) + '%. Ajuste para somar 100%.';
        return;
      }
      erro.textContent = '';
      sim.pesos = lido.valores.map(function (v) { return v / lido.soma; });
      guardar();
      atualizarSimulacao();
    });
    $('#pesos-limpar').addEventListener('click', function () {
      sim.pesos = null;
      $$('#pesos input').forEach(function (campo) { campo.value = ''; });
      $('#pesos-erro').textContent = '';
      guardar();
      atualizarSimulacao();
    });
  }

  function atualizarSimulacao() {
    ajustarPeriodo();
    desenharSegmentos();
    var pronto = sim.ativos.length >= MINIMO && N.pregoesDisponiveis(cotacoes, sim.ativos) >= sim.pregoes;
    $('#simular-vazio').hidden = pronto;
    $('#simular-corpo').hidden = !pronto;
    $('#simular-resumo').textContent = pronto
      ? 'Carteira com ' + sim.ativos.join(', ').replace(/, ([^,]*)$/, ' e $1') + '. Cada ponto da nuvem é uma combinação de pesos sorteada.'
      : '';
    if (!pronto) return;
    $('#semente').textContent = String(sim.semente);
    desenharPesos();
    mostrarSimulacao($('#simular-nuvem'), sim, null);
    aplicarDecimal();
  }

  // -------------------------------------------------------------- progresso

  function atualizarProgresso() {
    $$('#turnos input').forEach(function (caixa) {
      var turno = Number(caixa.getAttribute('data-turno'));
      caixa.checked = turnos.indexOf(turno) >= 0;
      caixa.parentNode.parentNode.classList.toggle('turno-feito', caixa.checked);
    });
    $('#progresso-nota').textContent = eu && eu.grupo === 'VIS'
      ? 'Visitantes ficam fora do placar da sala.'
      : turnos.length + ' de 5 turnos marcados. Nos turnos 1 e 2, o valor esperado do teste é o número que a tela Montar mostra em 9 pregões.';
    atualizarAtalhos(false);
  }

  // Atalho da spec do grupo, nos turnos 4 e 5. O endereço é resolvido quando a
  // tela abre e vira um link comum com target="_blank": o clique é do próprio
  // navegador, e nenhum bloqueador de pop-up entra no caminho.
  function specDeEdicao(r) {
    return SPEC + '?g=' + r.grupo + '&t=' + encodeURIComponent(r.token) + '&turno=' + r.turno +
      '&a=' + encodeURIComponent(eu.iniciais) + (r.demo ? '&quiz-demo=1' : '');
  }
  function specDeLeitura(grupo, turno) {
    return SPEC + '?g=' + grupo + '&turno=' + turno + '&ver=1' + (sala.tipo === 'memoria' ? '&quiz-demo=1' : '');
  }

  function mensagemDaSpec(falha) {
    var detalhe = (falha && falha.message) || 'erro desconhecido';
    if (/sim_spec_link|function|schema cache/i.test(detalhe)) {
      return 'O atalho da spec ainda não está ativo no banco da aula. Chame o professor e, depois do aviso dele, clique de novo neste botão.';
    }
    return 'A spec do grupo não abriu (' + detalhe + '). Chame o professor ou clique de novo para tentar outra vez.';
  }

  function pintarAtalho(turno, estado, texto, url) {
    var botao = $('#spec-t' + turno);
    botao.setAttribute('data-estado', estado);
    botao.removeAttribute('href');
    botao.removeAttribute('role');
    botao.removeAttribute('tabindex');
    botao.removeAttribute('aria-disabled');
    if (url) botao.setAttribute('href', url);
    else if (estado === 'erro') { botao.setAttribute('role', 'button'); botao.setAttribute('tabindex', '0'); }
    else botao.setAttribute('aria-disabled', 'true');
    $('#spec-t' + turno + '-nota').textContent = texto;
  }

  function chaveDoAtalho(turno) { return eu.id + ':' + turno + ':' + sala.tipo; }

  function aplicarAtalho(turno, atalho) {
    if (atalho.pedindo) pintarAtalho(turno, 'preparando', 'Preparando o atalho da spec.');
    else if (atalho.erro) pintarAtalho(turno, 'erro', atalho.erro);
    else {
      pintarAtalho(turno, 'pronto', 'Abre em nova aba, com o grupo ' + eu.grupo + ' e as iniciais ' + eu.iniciais + '.' +
        (atalho.demo ? ' Sala sem banco: esta spec fica só neste navegador.' : ''), atalho.url);
    }
  }

  // `repetir` refaz o pedido que terminou em erro (clique no botão). A troca
  // da sala para memória muda a chave, e o pedido é refeito sozinho.
  function atualizarAtalhos(repetir) {
    if (!eu) return;
    TURNOS_COM_SPEC.forEach(function (turno) {
      if (eu.grupo === 'VIS') {
        pintarAtalho(turno, 'visitante', 'Visitante não edita a spec do grupo. Para editar, saia e entre de novo com o seu grupo.');
        return;
      }
      var chave = chaveDoAtalho(turno);
      var atalho = atalhos[chave];
      if (atalho && !(repetir && atalho.erro)) { aplicarAtalho(turno, atalho); return; }
      atalhos[chave] = { pedindo: true };
      aplicarAtalho(turno, atalhos[chave]);
      sala.specLink(eu.id, turno).then(function (r) {
        atalhos[chave] = { url: specDeEdicao(r), demo: r.demo };
      }, function (falha) {
        atalhos[chave] = { erro: mensagemDaSpec(falha) };
      }).then(function () {
        if (!eu || telaAtual !== 'progresso') return;
        if (chave === chaveDoAtalho(turno)) aplicarAtalho(turno, atalhos[chave]);
        else atualizarAtalhos(false);
        document.body.setAttribute('data-spec', TURNOS_COM_SPEC.map(function (t) { return $('#spec-t' + t).getAttribute('data-estado'); }).join(','));
      });
    });
  }

  function prepararProgresso() {
    TURNOS_COM_SPEC.forEach(function (turno) {
      var botao = $('#spec-t' + turno);
      function semEndereco(evento) {
        if (botao.hasAttribute('href')) return;
        evento.preventDefault();
        if (botao.getAttribute('data-estado') === 'erro') atualizarAtalhos(true);
      }
      botao.addEventListener('click', semEndereco);
      botao.addEventListener('keydown', function (evento) {
        if (evento.key === 'Enter' || evento.key === ' ') semEndereco(evento);
      });
    });
    $$('#turnos input').forEach(function (caixa) {
      caixa.addEventListener('change', function () {
        var turno = Number(caixa.getAttribute('data-turno'));
        turnos = turnos.filter(function (t) { return t !== turno; });
        if (caixa.checked) turnos.push(turno);
        turnos.sort();
        gravarEu();
        atualizarProgresso();
        sala.marcar(eu.id, turno, caixa.checked).catch(function () { /* a sala já caiu para memória */ }).then(function () {
          document.body.setAttribute('data-marcado', turnos.join(','));
          atualizarAviso();
        });
      });
    });
  }

  // ----------------------------------------------------------------- painel

  function carregarPainel() {
    var pedido = ++pedidoPainel;
    return sala.sala().then(function (lista) {
      atualizarAviso();
      if (pedido !== pedidoPainel || telaAtual !== 'painel') return;
      desenharPainel(lista);
    });
  }

  function desenharPainel(lista) {
    var grade = $('#painel-grade');
    var primeiraVez = !Object.keys(conhecidos).length;
    limpar(grade);
    // O telão mostra os cinco blocos mesmo com a sala vazia: o slide não muda de forma.
    $('#painel-vazio').hidden = TELAO || lista.length > 0;
    grade.hidden = !TELAO && !lista.length;
    $('.painel-turnos').hidden = !lista.length;
    var comCarteira = lista.filter(function (p) { return p.carteira; }).length;
    var concluidos = lista.reduce(function (soma, p) { return soma + (p.grupo === 'VIS' ? 0 : p.turnos.length); }, 0);
    $('#telao-pessoas').textContent = inteiro(lista.length);
    $('#telao-pessoas-rotulo').textContent = lista.length === 1 ? 'pessoa na sala' : 'pessoas na sala';
    $('#telao-carteiras').textContent = inteiro(comCarteira);
    $('#telao-turnos').textContent = inteiro(concluidos);
    $('#telao-turnos-rotulo').textContent = concluidos === 1 ? 'turno concluído' : 'turnos concluídos';
    var semBanco = sala.tipo === 'memoria' && !DEMO;
    $('#telao-vivo').classList.toggle('telao-vivo-alerta', semBanco);
    $('#telao-hora').textContent = semBanco ? 'Sem conexão com o banco'
      : 'Atualizado às ' + new Date().toLocaleTimeString('pt-BR');
    document.body.setAttribute('data-painel', String(lista.length));
    $('#painel-resumo').textContent = !lista.length ? 'Sala ' + SESSAO + '.'
      : inteiro(lista.length) + (lista.length === 1 ? ' pessoa na sala, ' : ' pessoas na sala, ') +
        inteiro(comCarteira) + ' com carteira montada.';

    GRUPOS.forEach(function (grupo) {
      var membros = lista.filter(function (p) { return p.grupo === grupo.id; });
      if (grupo.id === 'VIS' && !membros.length && !TELAO) return;
      var linha = criar('section', {
        classe: 'painel-linha', 'data-grupo': grupo.id, 'aria-label': grupo.nome,
        'data-densidade': membros.length <= CHEIO ? '1' : membros.length <= CHEIO * 2 + 2 ? '2' : '3'
      });
      var cabeca = criar('div', { classe: 'painel-grupo' }, [
        criar('span', { classe: 'painel-cor', 'data-grupo': grupo.id, 'aria-hidden': 'true' }),
        criar('h2', { texto: grupo.nome }),
        criar('p', { classe: 'painel-quantos', texto: membros.length === 1 ? '1 pessoa' : membros.length + ' pessoas' })
      ]);
      if (grupo.id !== 'VIS') {
        // Visão somente leitura da spec do grupo, para projetar sem link.
        cabeca.appendChild(criar('p', { classe: 'painel-specs' }, TURNOS_COM_SPEC.map(function (turno) {
          return criar('a', {
            href: specDeLeitura(grupo.id, turno), target: '_blank', rel: 'noopener', 'data-turno': turno,
            'aria-label': 'Abrir a spec do turno ' + turno + ' do ' + grupo.nome + ' em nova aba, somente leitura',
            texto: 'Spec T' + turno
          });
        })));
      }
      linha.appendChild(cabeca);

      var avatares = criar('div', { classe: 'painel-avatares' });
      // No telão, acima de CHEIO os avatares encolhem e se dividem em 2 ou 3 linhas iguais.
      var fileiras = Number(linha.getAttribute('data-densidade'));
      avatares.style.setProperty('--por-linha', String(Math.ceil(membros.length / fileiras) || 1));
      if (!membros.length) avatares.appendChild(criar('p', { classe: 'painel-sem', texto: grupo.id === 'VIS' ? 'Nenhum visitante.' : 'Ninguém do grupo entrou.' }));
      membros.forEach(function (pessoa) {
        var rotulo = pessoa.iniciais + ', ' + grupo.nome + (pessoa.carteira ? ': abrir a simulação' : ': ainda sem carteira');
        var link = criar('a', {
          classe: 'avatar painel-avatar' + (pessoa.carteira ? '' : ' avatar-sem-carteira') +
            (!primeiraVez && !conhecidos[pessoa.id] ? ' avatar-chegou' : '') + (eu && eu.id === pessoa.id ? ' avatar-eu' : ''),
          href: '#ver=' + pessoa.id, 'data-id': pessoa.id, 'data-grupo': pessoa.grupo,
          'data-carteira': pessoa.carteira ? 'sim' : 'nao', 'aria-label': rotulo, title: rotulo, texto: pessoa.iniciais
        });
        conhecidos[pessoa.id] = true;
        avatares.appendChild(link);
      });
      linha.appendChild(avatares);

      if (grupo.id === 'VIS') {
        linha.appendChild(criar('p', { classe: 'placar placar-fora', texto: 'Fora do placar' }));
      } else {
        var placar = criar('ol', { classe: 'placar', 'aria-label': 'Duplas que concluíram cada turno, ' + grupo.nome });
        for (var turno = 1; turno <= 5; turno++) {
          var contagem = membros.filter(function (p) { return p.turnos.indexOf(turno) >= 0; }).length;
          placar.appendChild(criar('li', {
            classe: 'placar-celula' + (contagem ? ' placar-celula-cheia' : ''), 'data-grupo': grupo.id,
            'data-turno': turno, 'data-contagem': contagem,
            'aria-label': 'Turno ' + turno + ': ' + contagem + (contagem === 1 ? ' dupla concluiu' : ' duplas concluíram')
          }, [criar('span', { texto: 'T' + turno }), criar('strong', { classe: 'numero-destaque-valor', texto: String(contagem) })]));
        }
        linha.appendChild(placar);
      }
      grade.appendChild(linha);
    });
  }

  // ------------------------------------------ simulação de outro participante

  function abrirSimulacaoDe(id) {
    var vazio = $('#ver-vazio');
    var corpo = $('#ver-corpo');
    vazio.hidden = true;
    corpo.hidden = true;
    function semSimulacao(titulo, texto) {
      $('#ver-vazio-titulo').textContent = titulo;
      $('#ver-vazio-texto').textContent = texto;
      vazio.hidden = false;
    }
    sala.sala().then(function (lista) {
      atualizarAviso();
      if (telaAtual !== 'ver') return;
      var pessoa = lista.filter(function (p) { return p.id === id; })[0];
      if (!pessoa) {
        semSimulacao('Participante não encontrado nesta sala', 'O endereço aponta para alguém que não está na sala ' + SESSAO + '.');
        return;
      }
      var c = pessoa.carteira;
      if (!c) {
        semSimulacao(pessoa.iniciais + ' ainda não montou uma carteira', 'A simulação aparece aqui quando a pessoa escolher pelo menos 2 ativos.');
        return;
      }
      var faltando = c.ativos.filter(function (t) { return !cotacoes.precos[t]; });
      if (faltando.length || N.pregoesDisponiveis(cotacoes, c.ativos) < c.pregoes) {
        semSimulacao('A carteira de ' + pessoa.iniciais + ' não abre com o arquivo da aula',
          faltando.length ? 'Ativo fora do arquivo: ' + faltando.join(', ') + '.' : 'A janela comum dos ativos é menor que o período gravado.');
        return;
      }
      pintarAvatar($('#ver-avatar'), pessoa);
      $('#ver-titulo').textContent = 'Simulação de ' + pessoa.iniciais + ', ' + nomeDoGrupo(pessoa.grupo);
      $('#ver-parametros').textContent = c.ativos.join(', ') + '. ' + c.pregoes + ' pregões, ' + inteiro(c.n) +
        (c.n === 1 ? ' carteira sorteada' : ' carteiras sorteadas') + ', semente ' + c.semente + '.';
      corpo.hidden = false;
      var raiz = $('#ver-nuvem');
      mostrarSimulacao(raiz, c, eu && eu.id === pessoa.id ? null : pessoa.iniciais);
      // Os três números do melhor Sharpe, em destaque no telão.
      var melhor = raiz.calculo.marcas[0];
      var numeros = $('#ver-numeros');
      limpar(numeros);
      [['Maior Sharpe', numero(melhor.sharpe, 2)], ['Retorno anual', porcento(melhor.retorno, 1)], ['Risco anual', porcento(melhor.risco, 1)]]
        .forEach(function (par) {
          numeros.appendChild(criar('div', {}, [criar('dt', { texto: par[0] }), criar('dd', { classe: 'numero-destaque-valor', texto: par[1] })]));
        });
      aplicarDecimal();
    });
  }

  // ---------------------------------------------------------------- partida

  function redesenhar() {
    if (telaAtual === 'montar') desenharEvolucao();
    if (telaAtual === 'simular' && $('#simular-nuvem').calculo) desenharNuvem($('#simular-nuvem .nuvem-tela'), $('#simular-nuvem').calculo);
    if (telaAtual === 'ver' && $('#ver-nuvem').calculo) {
      ajustarAoTelao($('#ver-nuvem'), $('#ver-nuvem').calculo);
      desenharNuvem($('#ver-nuvem .nuvem-tela'), $('#ver-nuvem').calculo);
    }
    if (telaAtual === 'entrar') desenharVitrine();
  }

  function falhar(erro) {
    $('#erro-detalhe').textContent = 'Verifique a conexão e tente de novo. Detalhe: ' + ((erro && erro.message) || 'erro desconhecido') + '.';
    mostrar('erro');
  }

  function partir() {
    mostrar('carregando');
    Promise.all([carregarCotacoes(), carregarBiblioteca()]).then(function () {
      sala = window.SimuladorDados.abrir(SESSAO);
      return recuperar();
    }).then(function () {
      sala.assinar(function () {
        atualizarAviso();
        if (telaAtual === 'painel') carregarPainel();
        if (telaAtual === 'progresso') atualizarAtalhos(false);
      });
      atualizarAviso();
      document.body.setAttribute('data-sala', sala.tipo);
      rota();
    }).catch(falhar);
  }

  prepararEntrada();
  prepararBusca();
  prepararEvolucao();
  prepararSimulacao();
  prepararProgresso();
  $('#decimal').addEventListener('change', aplicarDecimal);
  $('#tentar').addEventListener('click', partir);
  window.addEventListener('hashchange', rota);
  var larguraAnterior = window.innerWidth;
  var alturaAnterior = window.innerHeight;
  window.addEventListener('resize', function () {
    // Fora do telão a altura não muda o desenho (e muda a toda hora no celular).
    if (window.innerWidth === larguraAnterior && (!TELAO || window.innerHeight === alturaAnterior)) return;
    larguraAnterior = window.innerWidth;
    alturaAnterior = window.innerHeight;
    redesenhar();
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(redesenhar);
  partir();
})();
