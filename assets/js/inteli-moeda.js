// Jogo da moeda da Aula 02. Cada celular joga a própria moeda: cara rende +50%,
// coroa rende -40%, todos começam com R$ 100. O professor libera as rodadas
// pelo slide; o slide mostra o histograma dos saldos com a média e a mediana.
//
// Slide:   <div class="moeda-sala" data-moeda data-sessao="..." data-rodadas="10"
//               data-largura="760" data-altura="380"></div>
// Celular: o mesmo quiz/index.html do quiz ao vivo. Quando o slide da moeda
//          aparece, ele abre no quiz uma rodada com pergunta "moeda", e o
//          celular que entrou pelo QR de qualquer slide anterior troca de tela
//          sozinho, com o nome do quiz. quiz/moeda.html segue como entrada avulsa.
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
    // Duas vistas do mesmo jogo: a distribuição dos saldos agora e a trajetória
    // de cada aluno rodada a rodada, com a média e a mediana da turma.
    var abas = el('div', 'moeda-abas');
    var vista = 'distribuicao';
    [['distribuicao', 'Distribuição'], ['trajetorias', 'Trajetórias']].forEach(function (par) {
      var b = el('button', 'moeda-aba', par[1]);
      b.type = 'button';
      b.dataset.vista = par[0];
      b.setAttribute('aria-pressed', par[0] === vista ? 'true' : 'false');
      b.addEventListener('click', function () {
        vista = par[0];
        raiz.dataset.vista = vista;
        Array.prototype.forEach.call(abas.children, function (x) {
          x.setAttribute('aria-pressed', x.dataset.vista === vista ? 'true' : 'false');
        });
        redesenhar();
      });
      abas.appendChild(b);
    });
    raiz.dataset.vista = vista;
    grafico.appendChild(abas);
    var canvas = el('canvas', 'moeda-canvas');
    var escala = window.devicePixelRatio || 1;
    canvas.width = largura * escala;
    canvas.height = altura * escala;
    canvas.style.width = largura + 'px';
    canvas.style.height = altura + 'px';
    grafico.appendChild(canvas);

    var lado = el('div', 'moeda-lado');
    var aviso = el('p', 'moeda-aviso', 'Os celulares que entraram no quiz já estão no jogo.');
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
    [aviso, jogadores, rodada, media, med, botoes].forEach(function (e) { lado.appendChild(e); });
    raiz.appendChild(grafico);
    raiz.appendChild(lado);

    // Sinal para os celulares do quiz: rodada "moeda" aberta enquanto o slide
    // está na tela, fechada quando o professor sai dele.
    var quiz = window.IntelIQuizDados ? window.IntelIQuizDados.criar() : null;
    function abrirSinal() {
      if (!quiz || !chave()) return;
      quiz.abrir(chave(), sessao, 'moeda', 1, 'Jogo da moeda', []).catch(function (err) { console.error('[moeda]', err); });
    }
    function fecharSinal() {
      if (!quiz || !chave()) return;
      quiz.fechar(chave(), sessao).catch(function (err) { console.error('[moeda]', err); });
    }
    var secao = raiz.closest('section');
    if (window.Reveal && window.Reveal.on && secao) {
      window.Reveal.on('slidechanged', function (e) {
        if (e.currentSlide === secao) abrirSinal();
        else if (e.previousSlide === secao) fecharSinal();
      });
    }
    abrirSinal();

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

    // Uma linha por aluno (saldo depois de cada rodada, escala log), mais a
    // média e a mediana da turma em cada rodada e a linha dos R$ 100.
    function desenharTrajetorias(jogadas) {
      var ctx = canvas.getContext('2d');
      ctx.setTransform(escala, 0, 0, escala, 0, 0);
      ctx.clearRect(0, 0, largura, altura);
      var esq = 70, dir = largura - 90, base = altura - 40, topo = 16;
      var MIN = Math.log10(0.5), MAX = Math.log10(6000);
      function x(r) { return esq + r / total * (dir - esq); }
      function y(v) { return base - (Math.log10(Math.max(v, 0.5)) - MIN) / (MAX - MIN) * (base - topo); }

      ctx.font = '600 14px ' + cor('--fonte-texto');
      ctx.fillStyle = cor('--seg-texto-suave');
      ctx.strokeStyle = cor('--seg-borda');
      ctx.lineWidth = 1;
      ctx.textAlign = 'right';
      [1, 10, 100, 1000].forEach(function (v) {
        ctx.fillText(reais(v).replace(',00', ''), esq - 10, y(v) + 5);
      });
      ctx.textAlign = 'center';
      for (var r = 0; r <= total; r++) ctx.fillText(String(r), x(r), base + 22);
      ctx.beginPath(); ctx.moveTo(esq, base); ctx.lineTo(dir, base); ctx.stroke();

      ctx.setLineDash([6, 6]);
      ctx.strokeStyle = cor('--seg-texto-suave');
      ctx.beginPath(); ctx.moveTo(esq, y(100)); ctx.lineTo(dir, y(100)); ctx.stroke();
      ctx.setLineDash([]);

      var porJogador = {};
      jogadas.forEach(function (j) {
        if (j.rodada > liberada) return;
        (porJogador[j.jogador] = porJogador[j.jogador] || {})[j.rodada] = j.saldo;
      });
      var ids = Object.keys(porJogador);
      ctx.strokeStyle = cor('--seg-primaria');
      ctx.globalAlpha = ids.length > 15 ? 0.25 : 0.4;
      ctx.lineWidth = 2;
      ids.forEach(function (id) {
        ctx.beginPath();
        ctx.moveTo(x(0), y(100));
        for (var r = 1; r <= total && porJogador[id][r] !== undefined; r++) ctx.lineTo(x(r), y(porJogador[id][r]));
        ctx.stroke();
      });
      ctx.globalAlpha = 1;

      var medias = [100], medianas = [100];
      for (var r2 = 1; r2 <= liberada; r2++) {
        var v = ids.map(function (id) { return porJogador[id][r2]; }).filter(function (s) { return s !== undefined; });
        if (!v.length) break;
        medias.push(v.reduce(function (a, b) { return a + b; }, 0) / v.length);
        medianas.push(mediana(v));
      }
      function serie(valores, nome, rotulo, dy) {
        ctx.strokeStyle = cor(nome);
        ctx.fillStyle = cor(nome);
        ctx.lineWidth = 5;
        ctx.beginPath();
        valores.forEach(function (v, i) { if (i === 0) ctx.moveTo(x(i), y(v)); else ctx.lineTo(x(i), y(v)); });
        ctx.stroke();
        var u = valores.length - 1;
        ctx.font = '700 16px ' + cor('--fonte-texto');
        ctx.textAlign = 'left';
        ctx.fillText(rotulo, x(u) + 10, y(valores[u]) + 5 + (dy || 0));
      }
      if (medias.length > 1) {
        // Rótulos afastados quando as duas linhas terminam perto uma da outra.
        var u2 = medias.length - 1;
        var perto = Math.abs(y(medias[u2]) - y(medianas[u2])) < 20;
        var mediaAcima = y(medias[u2]) <= y(medianas[u2]);
        serie(medianas, '--inteli-coral', 'Mediana', perto ? (mediaAcima ? 11 : -11) : 0);
        serie(medias, '--inteli-verde', 'Média', perto ? (mediaAcima ? -11 : 11) : 0);
      }
      canvas.dataset.linhas = String(ids.length);
    }

    var ultimas = [];
    var ultimosSaldos = [];
    var ultimaMedia = null;
    var ultimaMediana = null;
    function redesenhar() {
      if (vista === 'trajetorias') desenharTrajetorias(ultimas);
      else desenhar(ultimosSaldos, ultimaMedia, ultimaMediana);
    }

    function atualizar() {
      return Promise.all([dados.moedaRodada(sessao), dados.moedaJogadas(sessao), dados.moedaSala(sessao)]).then(function (r) {
        liberada = r[0];
        var jogadas = r[1];
        ultimas = jogadas;
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
        ultimosSaldos = saldos;
        ultimaMedia = vMedia;
        ultimaMediana = vMediana;
        redesenhar();
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

  // opcoes.apelido: entra no jogo sozinho com esse nome (celular vindo do quiz).
  function montarAluno(raiz, opcoes) {
    opcoes = opcoes || {};
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
    var giro = raiz.querySelector('.moeda-giro');
    var trilha = raiz.querySelector('.moeda-trilha');
    var GIRO_MS = 1300;
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
      if (trilha) {
        // Um marcador por rodada: as jogadas com o lado e o saldo, as liberadas
        // e ainda não jogadas em destaque, e as que faltam até a rodada 10 vazias.
        trilha.textContent = '';
        var ate = Math.max(10, liberada, feitas.length);
        for (var r = 1; r <= ate; r++) {
          var j = feitas[r - 1];
          var m = el('li', 'mt ' + (j ? (j.cara ? 'mt-cara' : 'mt-coroa') : (r <= liberada ? 'mt-liberada' : 'mt-vazia')));
          m.appendChild(el('span', 'mt-n', String(r)));
          if (j) m.title = 'Rodada ' + r + ': ' + (j.cara ? 'cara' : 'coroa') + ', ' + reais(j.saldo);
          trilha.appendChild(m);
        }
      }
      if (giro && !ocupado && feitas.length) giro.dataset.lado = feitas[feitas.length - 1].cara ? 'cara' : 'coroa';
      var proxima = feitas.length + 1;
      var pode = proxima <= liberada && !ocupado;
      jogar.disabled = !pode;
      jogar.textContent = proxima > 10 ? 'Fim do jogo' :
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
      if (opcoes.apelido) entrar(opcoes.apelido); else tela('entrar');
    }

    function entrar(apelido) {
      return dados.moedaEntrar(sessao, apelido, opcoes.participante).then(function (id) {
        eu = { id: id, apelido: apelido };
        try { sessionStorage.setItem(CHAVE, JSON.stringify(eu)); } catch (e) { /* aba privada */ }
        comecar();
      });
    }

    var ouvindo = false;
    function comecar() {
      if (quem) quem.textContent = eu.apelido;
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
      resultado.textContent = 'A moeda está no ar...';
      var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var inicio = Date.now();
      if (giro && !reduzir) {
        giro.classList.remove('girando');
        void giro.offsetWidth;  // reinicia a animação
        giro.classList.add('girando');
      }
      dados.moedaJogar(sessao, eu.id, rodada).then(function (j) {
        var falta = reduzir ? 0 : Math.max(0, GIRO_MS - (Date.now() - inicio));
        setTimeout(function () {
          if (giro) { giro.classList.remove('girando'); giro.dataset.lado = j.cara ? 'cara' : 'coroa'; }
          resultado.dataset.fase = j.cara ? 'cara' : 'coroa';
          resultado.textContent = j.cara ? 'Cara: +50%' : 'Coroa: -40%';
          guardar(feitas.concat([{ rodada: rodada, cara: j.cara, saldo: j.saldo }]));
          ocupado = false;
          render();
        }, falta);
      }, function (err) {
        ocupado = false;
        if (giro) giro.classList.remove('girando');
        if (err.message.indexOf('jogador desconhecido') !== -1) { sair(); return; }
        resultado.dataset.fase = 'erro';
        resultado.textContent = err.message;
        carregar();
      });
    });

    if (form) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var apelido = form.querySelector('#apelido').value.trim();
        if (!apelido) return;
        entrar(apelido).catch(function (err) { form.querySelector('.erro').textContent = err.message; });
      });
    }

    if (eu && eu.id) comecar();
    else if (opcoes.apelido) entrar(opcoes.apelido).catch(function (err) { console.error('[moeda]', err); });
    else tela('entrar');
  }

  window.IntelIMoeda = { montarAluno: montarAluno };

  // ------------------------------------------------- voto contra resultado

  // <div data-moeda-cruzamento data-sessao="..." data-pergunta="vale-jogar"
  //      data-opcoes='["Jogo...", "Não jogo...", "Tanto faz..."]'
  //      data-acerto='["acima", "abaixo", null]'></div>
  // Cada aluno é contado uma vez: o último voto dele na pergunta e o saldo final
  // na moeda. Acerta quem previu o lado de R$ 100 em que terminou.
  function montarCruzamento(raiz) {
    var dados = IntelIAula02Dados.criar();
    var sessao = IntelIAula02Dados.sessao(raiz.dataset.sessao);
    var opcoes = JSON.parse(raiz.dataset.opcoes || '[]');
    var acerto = JSON.parse(raiz.dataset.acerto || '[]');

    var placar = el('p', 'mc-placar');
    var lista = el('ol', 'mc-linhas');
    var legenda = el('p', 'mc-legenda');
    legenda.appendChild(el('span', 'mc-l-abaixo', 'terminou abaixo de R$ 100'));
    legenda.appendChild(el('span', 'mc-l-acima', 'terminou com R$ 100 ou mais'));
    raiz.appendChild(placar);
    raiz.appendChild(lista);
    raiz.appendChild(legenda);

    function atualizar() {
      return dados.moedaCruzamento(sessao, raiz.dataset.pergunta).then(function (linhas) {
        var por = {};
        linhas.forEach(function (l) { por[l.opcao] = l; });
        var total = 0, certos = 0, maior = 1;
        opcoes.forEach(function (_, i) {
          var l = por[i] || { abaixo: 0, acima: 0 };
          total += l.abaixo + l.acima;
          if (acerto[i] === 'abaixo') certos += l.abaixo;
          if (acerto[i] === 'acima') certos += l.acima;
          maior = Math.max(maior, l.abaixo + l.acima);
        });
        placar.textContent = '';
        placar.appendChild(el('strong', '', certos + ' de ' + total));
        placar.appendChild(el('span', '', ' acertaram o lado de R$ 100 em que terminaram'));
        raiz.dataset.acertos = String(certos);
        raiz.dataset.total = String(total);
        lista.textContent = '';
        opcoes.forEach(function (texto, i) {
          var l = por[i] || { abaixo: 0, acima: 0 };
          var li = el('li', 'mc-linha');
          li.dataset.opcao = String(i);
          li.appendChild(el('span', 'mc-texto', texto));
          var barra = el('span', 'mc-barra');
          var a = el('span', 'mc-abaixo', l.abaixo ? String(l.abaixo) : '');
          a.style.width = (l.abaixo / maior * 100) + '%';
          var b = el('span', 'mc-acima', l.acima ? String(l.acima) : '');
          b.style.width = (l.acima / maior * 100) + '%';
          barra.appendChild(a);
          barra.appendChild(b);
          li.appendChild(barra);
          lista.appendChild(li);
        });
      });
    }
    atualizar().then(function () { raiz.dataset.pronto = 'sim'; }, function (err) {
      raiz.dataset.pronto = 'erro';
      console.error('[moeda-cruzamento]', err);
    });
    dados.ouvir(sessao, atualizar, ['moeda_jogadas']);
    var secao = raiz.closest('section');
    if (window.Reveal && window.Reveal.on && secao) {
      window.Reveal.on('slidechanged', function (e) { if (e.currentSlide === secao) atualizar(); });
    }
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
    Array.prototype.forEach.call(document.querySelectorAll('[data-moeda-cruzamento]'), function (r) { quandoPresente(r, montarCruzamento); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-moeda-aluno]:not([data-moeda-auto="nao"])'),
      function (r) { montarAluno(r); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
