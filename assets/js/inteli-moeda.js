// Jogo da moeda da Aula 02. Cada celular joga a própria moeda: cara rende +50%,
// coroa rende -40%, todos começam com R$ 100. O professor libera as rodadas
// pelo slide; o slide mostra o histograma dos saldos com a média e a mediana.
//
// Slide:   <div class="moeda-sala" data-moeda data-sessao="..." data-rodadas="10"
//               data-aluno="../quiz/moeda.html" data-largura="760" data-altura="380"></div>
// Celular: quiz/moeda.html?s=<sessão>, com <main data-moeda-aluno>.
//
// Dados por IntelIAula02Dados (assets/js/inteli-aula02-dados.js). O sorteio é
// feito no servidor (moeda_jogar).
(function () {
  'use strict';

  var CHAVE_PROFESSOR = 'inteli-quiz-chave';

  function chave() { try { return localStorage.getItem(CHAVE_PROFESSOR) || ''; } catch (e) { return ''; } }
  (function () {
    var p = new URLSearchParams(window.location.search).get('quiz-chave');
    if (p) { try { localStorage.setItem(CHAVE_PROFESSOR, p); } catch (e) { /* aba privada */ } }
  })();

  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function reais(v) {
    return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function cor(nome) { return getComputedStyle(document.documentElement).getPropertyValue(nome).trim() || '#000'; }

  // Último saldo de cada jogador, até a rodada liberada.
  function saldosAtuais(jogadas, liberada) {
    var ultimo = {};
    jogadas.forEach(function (j) {
      if (j.rodada > liberada) return;
      if (!ultimo[j.jogador] || ultimo[j.jogador].rodada < j.rodada) ultimo[j.jogador] = j;
    });
    return Object.keys(ultimo).map(function (k) { return ultimo[k].saldo; });
  }

  function mediana(v) {
    if (!v.length) return null;
    var s = v.slice().sort(function (a, b) { return a - b; });
    var m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  // ----------------------------------------------------------------- slide

  function montarSlide(raiz) {
    var dados = IntelIAula02Dados.criar();
    var sessao = IntelIAula02Dados.sessao(raiz.dataset.sessao);
    var total = Number(raiz.dataset.rodadas || 10);
    var largura = Number(raiz.dataset.largura || 760);
    var altura = Number(raiz.dataset.altura || 380);

    var grafico = el('div', 'moeda-grafico');
    var canvas = el('canvas', 'moeda-canvas');
    var escala = window.devicePixelRatio || 1;
    canvas.width = largura * escala;
    canvas.height = altura * escala;
    canvas.style.width = largura + 'px';
    canvas.style.height = altura + 'px';
    grafico.appendChild(canvas);

    var lado = el('div', 'moeda-lado');
    var qr = el('div', 'moeda-qr');
    var link = el('p', 'moeda-link');
    var jogadores = el('p', 'moeda-jogadores', '0 jogadores');
    jogadores.dataset.n = '0';
    var rodada = el('p', 'moeda-rodada', 'Rodada 0 de ' + total);
    rodada.dataset.rodada = '0';
    var media = el('p', 'moeda-media');
    var med = el('p', 'moeda-mediana');
    var liberar = el('button', 'moeda-liberar', 'Liberar rodada 1');
    liberar.type = 'button';
    liberar.hidden = !chave();
    var zerar = el('button', 'moeda-zerar', 'Zerar');
    zerar.type = 'button';
    zerar.hidden = !chave();
    var botoes = el('div', 'moeda-botoes');
    botoes.appendChild(liberar);
    botoes.appendChild(zerar);
    [qr, link, jogadores, rodada, media, med, botoes].forEach(function (e) { lado.appendChild(e); });
    raiz.appendChild(grafico);
    raiz.appendChild(lado);

    var alvo = new URL(raiz.dataset.aluno || '../quiz/moeda.html', window.location.href);
    alvo.search = '?s=' + encodeURIComponent(sessao) + (IntelIAula02Dados.demo() ? '&quiz-demo=1' : '');
    link.textContent = alvo.href.replace(/^https?:\/\//, '');
    if (window.qrcode) {
      var q = window.qrcode(0, 'M');
      q.addData(alvo.href);
      q.make();
      qr.innerHTML = q.createSvgTag({ cellSize: 4, margin: 0, scalable: true });
    }

    var liberada = 0;

    function desenhar(saldos, valorMedia, valorMediana) {
      var ctx = canvas.getContext('2d');
      ctx.setTransform(escala, 0, 0, escala, 0, 0);
      ctx.clearRect(0, 0, largura, altura);
      var esq = 20, dir = largura - 20, base = altura - 44, topo = 30;
      var MIN = Math.log10(0.5), MAX = Math.log10(6000), FAIXAS = 20;
      function x(v) { return esq + (Math.log10(Math.max(v, 0.5)) - MIN) / (MAX - MIN) * (dir - esq); }
      var contagem = new Array(FAIXAS).fill(0);
      saldos.forEach(function (v) {
        var i = Math.floor((Math.log10(Math.max(v, 0.5)) - MIN) / (MAX - MIN) * FAIXAS);
        contagem[Math.min(FAIXAS - 1, Math.max(0, i))] += 1;
      });
      var maior = Math.max.apply(null, contagem.concat([1]));
      var passo = (dir - esq) / FAIXAS;
      ctx.fillStyle = cor('--seg-primaria');
      contagem.forEach(function (c, i) {
        if (!c) return;
        var h = (base - topo) * c / maior;
        ctx.fillRect(esq + i * passo + 2, base - h, passo - 4, h);
      });
      ctx.strokeStyle = cor('--seg-borda');
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(esq, base); ctx.lineTo(dir, base); ctx.stroke();
      ctx.fillStyle = cor('--seg-texto-suave');
      ctx.font = '600 15px ' + cor('--fonte-texto');
      ctx.textAlign = 'center';
      [1, 10, 100, 1000].forEach(function (v) {
        ctx.fillText(reais(v).replace(',00', ''), x(v), base + 24);
      });
      function linha(v, nome, rotulo, y) {
        if (v === null) return;
        ctx.strokeStyle = cor(nome);
        ctx.fillStyle = cor(nome);
        ctx.lineWidth = 3;
        ctx.setLineDash(nome === '--seg-texto-suave' ? [6, 6] : []);
        ctx.beginPath(); ctx.moveTo(x(v), topo - 6); ctx.lineTo(x(v), base); ctx.stroke();
        ctx.setLineDash([]);
        ctx.font = '700 15px ' + cor('--fonte-texto');
        ctx.fillText(rotulo, x(v), y);
      }
      linha(100, '--seg-texto-suave', 'Início', topo - 12);
      linha(valorMediana, '--inteli-coral', 'Mediana', topo + 8);
      linha(valorMedia, '--inteli-verde', 'Média', topo + 26);
    }

    function atualizar() {
      return Promise.all([dados.moedaRodada(sessao), dados.moedaJogadas(sessao), dados.moedaSala(sessao)]).then(function (r) {
        liberada = r[0];
        var jogadas = r[1];
        var saldos = saldosAtuais(jogadas, liberada);
        var n = r[2];
        jogadores.textContent = n + (n === 1 ? ' jogador' : ' jogadores');
        jogadores.dataset.n = String(n);
        rodada.textContent = 'Rodada ' + liberada + ' de ' + total;
        rodada.dataset.rodada = String(liberada);
        liberar.textContent = liberada >= total ? 'Fim do jogo' : 'Liberar rodada ' + (liberada + 1);
        liberar.disabled = liberada >= total;
        var vMedia = saldos.length ? saldos.reduce(function (a, b) { return a + b; }, 0) / saldos.length : null;
        var vMediana = mediana(saldos);
        media.dataset.valor = vMedia === null ? '' : vMedia.toFixed(2);
        med.dataset.valor = vMediana === null ? '' : vMediana.toFixed(2);
        media.innerHTML = '';
        media.appendChild(el('span', 'moeda-rotulo', 'Média'));
        media.appendChild(el('strong', '', vMedia === null ? '-' : reais(vMedia)));
        med.innerHTML = '';
        med.appendChild(el('span', 'moeda-rotulo', 'Mediana'));
        med.appendChild(el('strong', '', vMediana === null ? '-' : reais(vMediana)));
        desenhar(saldos, vMedia, vMediana);
      });
    }

    // O contador conta quem entrou; média e mediana usam quem já jogou ao menos uma rodada.
    liberar.addEventListener('click', function () {
      dados.moedaLiberar(chave(), sessao, liberada + 1).then(atualizar, function (err) { console.error('[moeda]', err); });
    });
    // Zerar apaga o jogo inteiro: pede um segundo clique em até 4 s.
    var confirmando = null;
    zerar.addEventListener('click', function () {
      if (!confirmando) {
        zerar.textContent = 'Clique de novo para apagar';
        confirmando = setTimeout(function () { confirmando = null; zerar.textContent = 'Zerar'; }, 4000);
        return;
      }
      clearTimeout(confirmando);
      confirmando = null;
      zerar.textContent = 'Zerar';
      dados.moedaZerar(chave(), sessao).then(atualizar, function (err) { console.error('[moeda]', err); });
    });

    atualizar().then(function () { raiz.dataset.pronto = 'sim'; }, function (err) {
      raiz.dataset.pronto = 'erro';
      console.error('[moeda]', err);
    });
    dados.ouvir(sessao, atualizar, ['moeda_sessoes', 'moeda_jogadas']);
  }

  // --------------------------------------------------------------- celular

  function montarAluno(raiz) {
    var dados = IntelIAula02Dados.criar();
    var params = new URLSearchParams(window.location.search);
    var sessao = params.get('s') || IntelIAula02Dados.sessao(raiz.dataset.sessao);
    var CHAVE = 'inteli-moeda-' + sessao;
    var eu = null;
    try { eu = JSON.parse(sessionStorage.getItem(CHAVE)); } catch (e) { eu = null; }

    var form = raiz.querySelector('.tela-entrar form');
    var saldoEl = raiz.querySelector('.moeda-saldo-valor');
    var jogar = raiz.querySelector('.jogar');
    var resultado = raiz.querySelector('.moeda-resultado');
    var historico = raiz.querySelector('.historico');
    var quem = raiz.querySelector('.moeda-quem');
    var liberada = 0;
    var feitas = [];      // jogadas deste jogador, em ordem de rodada
    var ocupado = false;
    var leitura = 0;      // descarta respostas de leituras antigas

    function tela(nome) { raiz.dataset.estado = nome; }

    function render() {
      var saldo = feitas.length ? feitas[feitas.length - 1].saldo : 100;
      saldoEl.textContent = reais(saldo);
      saldoEl.dataset.valor = saldo.toFixed(2);
      historico.textContent = '';
      feitas.forEach(function (j) {
        var li = el('li', j.cara ? 'cara' : 'coroa');
        li.dataset.saldo = j.saldo.toFixed(2);
        li.appendChild(el('span', 'h-rodada', 'Rodada ' + j.rodada));
        li.appendChild(el('span', 'h-lado', j.cara ? 'Cara +50%' : 'Coroa -40%'));
        li.appendChild(el('strong', 'h-saldo', reais(j.saldo)));
        historico.insertBefore(li, null);
      });
      var proxima = feitas.length + 1;
      var pode = proxima <= liberada && !ocupado;
      jogar.disabled = !pode;
      jogar.textContent = proxima > 20 ? 'Fim do jogo' :
        (proxima <= liberada ? 'Jogar rodada ' + proxima : 'Aguarde o professor liberar a rodada ' + proxima);
    }

    function guardar(lista) {
      var porRodada = {};
      lista.forEach(function (j) { porRodada[j.rodada] = j; });
      feitas = Object.keys(porRodada).map(function (k) { return porRodada[k]; })
        .sort(function (a, b) { return a.rodada - b.rodada; });
    }

    function carregar() {
      var minha = ++leitura;
      return Promise.all([dados.moedaRodada(sessao), dados.moedaJogadas(sessao, eu.id)]).then(function (r) {
        if (minha !== leitura || ocupado) return;
        liberada = r[0];
        // O professor zerou o jogo: este jogador não existe mais.
        if (liberada === 0 && feitas.length && !r[1].length) { sair(); return; }
        guardar(r[1]);
        render();
      });
    }

    function sair() {
      try { sessionStorage.removeItem(CHAVE); } catch (e) { /* aba privada */ }
      eu = null;
      feitas = [];
      tela('entrar');
    }

    var ouvindo = false;
    function comecar() {
      quem.textContent = eu.apelido;
      tela('jogar');
      carregar();
      if (ouvindo) return;
      ouvindo = true;
      dados.ouvir(sessao, function () { if (eu && !ocupado) carregar(); }, ['moeda_sessoes']);
    }

    jogar.addEventListener('click', function () {
      var rodada = feitas.length + 1;
      ocupado = true;
      leitura++;
      jogar.disabled = true;
      resultado.dataset.fase = 'girando';
      resultado.textContent = 'Jogando...';
      dados.moedaJogar(sessao, eu.id, rodada).then(function (j) {
        var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        setTimeout(function () {
          resultado.dataset.fase = j.cara ? 'cara' : 'coroa';
          resultado.textContent = j.cara ? 'Cara: +50%' : 'Coroa: -40%';
          guardar(feitas.concat([{ rodada: rodada, cara: j.cara, saldo: j.saldo }]));
          ocupado = false;
          render();
        }, reduzir ? 0 : 700);
      }, function (err) {
        ocupado = false;
        if (err.message.indexOf('jogador desconhecido') !== -1) { sair(); return; }
        resultado.dataset.fase = 'erro';
        resultado.textContent = err.message;
        carregar();
      });
    });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var apelido = form.querySelector('#apelido').value.trim();
      if (!apelido) return;
      dados.moedaEntrar(sessao, apelido).then(function (id) {
        eu = { id: id, apelido: apelido };
        try { sessionStorage.setItem(CHAVE, JSON.stringify(eu)); } catch (e) { /* aba privada */ }
        comecar();
      }, function (err) { form.querySelector('.erro').textContent = err.message; });
    });

    if (eu && eu.id) comecar(); else tela('entrar');
  }


  // Dentro de um deck Reveal, o componente só conecta ao banco quando o slide
  // dele aparece pela primeira vez (como o quiz ao vivo). Fora do deck, na hora.
  function quandoPresente(raiz, montar) {
    var secao = raiz.closest('section');
    var feito = false;
    function vai() { if (!feito) { feito = true; montar(raiz); } }
    if (!(window.Reveal && window.Reveal.on && secao)) { vai(); return; }
    window.Reveal.on('slidechanged', function (e) { if (e.currentSlide === secao) vai(); });
    window.Reveal.on('ready', function (e) { if (e.currentSlide === secao) vai(); });
    if (secao.classList.contains('present')) vai();
  }

  function iniciar() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-moeda]'), function (r) { quandoPresente(r, montarSlide); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-moeda-aluno]'), montarAluno);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
