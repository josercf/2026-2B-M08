// Quiz ao vivo no slide: QR code, pergunta, contagem de votos e rodadas.
//
// Contrato de markup (ver o slide #preparo da Aula 01):
//   <div class="quiz-vivo" data-quiz-vivo data-sessao="m08-aula01-2026-10-20"
//        data-pergunta="preparo-end" data-correta="3" data-rodadas="2"
//        data-tempo="0" data-enunciado="texto que vai para o celular">
//     <p class="quiz-vivo-enunciado">...</p>
//     <ol class="quiz-vivo-opcoes"><li data-opcao="0">31</li> ...</ol>
//   </div>
// O restante (QR, placar, botões, barras) é montado aqui.
//
// Ciclo: o slide fica presente e a rodada 1 abre; os celulares mostram a
// pergunta. "Encerrar votação" fecha a rodada e mostra a distribuição; "Votar
// de novo" abre a rodada seguinte (Peer Instruction); "Revelar" marca a certa.
// Sair do slide fecha a rodada aberta. Com data-tempo > 0, a rodada fecha
// sozinha no fim do cronômetro.
//
// Abrir e fechar rodada exige a chave do professor, gravada uma vez neste
// navegador por ?quiz-chave=<chave> ou pelo campo que o widget mostra quando
// ela falta. Ela nunca entra no repositório.
(function () {
  'use strict';

  var LETRAS = ['A', 'B', 'C', 'D', 'E', 'F'];
  var CHAVE = 'inteli-quiz-chave';
  var SVG = 'http://www.w3.org/2000/svg';

  function ler() { try { return localStorage.getItem(CHAVE) || ''; } catch (e) { return ''; } }
  function gravar(v) { try { localStorage.setItem(CHAVE, v); } catch (e) { /* aba privada */ } }

  (function () {
    var p = new URLSearchParams(window.location.search).get('quiz-chave');
    if (p) gravar(p);
  })();

  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function linkAluno(sessao) {
    var url = new URL('../quiz/', window.location.href);
    url.searchParams.set('s', sessao);
    if (window.IntelIQuizDados.demo()) url.searchParams.set('quiz-demo', '1');
    return url.href;
  }

  // QR em SVG, um <rect> por módulo escuro, cor pelo tema (.quiz-vivo-qr rect).
  function desenharQr(alvo, texto) {
    alvo.innerHTML = '';
    if (!window.qrcode) { alvo.appendChild(el('p', 'quiz-vivo-sem-qr', texto)); return; }
    var qr = window.qrcode(0, 'M');
    qr.addData(texto);
    qr.make();
    var n = qr.getModuleCount();
    var borda = 2;
    var svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + (n + 2 * borda) + ' ' + (n + 2 * borda));
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'QR code para responder pelo celular');
    svg.setAttribute('shape-rendering', 'crispEdges');
    var fundo = document.createElementNS(SVG, 'rect');
    fundo.setAttribute('class', 'qr-fundo');
    fundo.setAttribute('width', n + 2 * borda);
    fundo.setAttribute('height', n + 2 * borda);
    svg.appendChild(fundo);
    var caminho = '';
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        if (qr.isDark(r, c)) caminho += 'M' + (c + borda) + ' ' + (r + borda) + 'h1v1h-1z';
      }
    }
    var p = document.createElementNS(SVG, 'path');
    p.setAttribute('class', 'qr-modulo');
    p.setAttribute('d', caminho);
    svg.appendChild(p);
    alvo.appendChild(svg);
  }

  function montar(raiz) {
    var dados = window.IntelIQuizDados.criar();
    var sessao = raiz.dataset.sessao;
    var pergunta = raiz.dataset.pergunta;
    var correta = raiz.dataset.correta === undefined ? null : Number(raiz.dataset.correta);
    var maxRodadas = Number(raiz.dataset.rodadas || 1);
    var tempo = Number(raiz.dataset.tempo || 0);
    var enunciado = raiz.dataset.enunciado || raiz.querySelector('.quiz-vivo-enunciado').textContent.trim();
    var itens = Array.prototype.slice.call(raiz.querySelectorAll('.quiz-vivo-opcoes li'));
    var opcoes = itens.map(function (li) { return li.textContent.trim(); });

    // Barras e letras em cada alternativa.
    itens.forEach(function (li, i) {
      var texto = li.textContent.trim();
      li.innerHTML = '';
      li.appendChild(el('span', 'qv-letra', LETRAS[i]));
      li.appendChild(el('span', 'qv-texto', texto));
      var barras = el('span', 'qv-barras');
      for (var k = 1; k <= maxRodadas; k++) {
        var b = el('span', 'qv-barra qv-barra-' + k);
        b.appendChild(el('span', 'qv-barra-cheia'));
        barras.appendChild(b);
      }
      li.appendChild(barras);
      li.appendChild(el('span', 'qv-pct', ''));
    });

    // Coluna do QR e dos controles.
    var lado = el('aside', 'quiz-vivo-lado');
    var qr = el('div', 'quiz-vivo-qr');
    var link = linkAluno(sessao);
    desenharQr(qr, link);
    var instrucao = el('p', 'quiz-vivo-instrucao', 'Aponte a câmera do celular');
    var placar = el('p', 'quiz-vivo-placar');
    var nVotos = el('strong', 'qv-n-votos', '0');
    var nSala = el('span', 'qv-n-sala', '0');
    placar.appendChild(nVotos);
    placar.appendChild(document.createTextNode(' votos de '));
    placar.appendChild(nSala);
    placar.appendChild(document.createTextNode(' na sala'));
    var cronometro = el('p', 'quiz-vivo-cronometro', '');
    var rotuloRodada = el('p', 'quiz-vivo-rodada', '');
    var acoes = el('div', 'quiz-vivo-acoes');
    function botao(acao, texto) {
      var b = el('button', 'quiz-vivo-botao', texto);
      b.type = 'button';
      b.dataset.acao = acao;
      acoes.appendChild(b);
      return b;
    }
    var bEncerrar = botao('encerrar', 'Encerrar votação');
    var bDeNovo = botao('rodada', 'Votar de novo');
    var bRevelar = botao('revelar', 'Revelar');
    var formChave = el('form', 'quiz-vivo-chave');
    var campo = el('input', '');
    campo.type = 'password';
    campo.placeholder = 'Chave do professor';
    campo.setAttribute('aria-label', 'Chave do professor');
    var bChave = el('button', 'quiz-vivo-botao', 'Abrir');
    bChave.type = 'submit';
    formChave.appendChild(campo);
    formChave.appendChild(bChave);
    var status = el('p', 'quiz-vivo-status', '');
    status.setAttribute('aria-live', 'polite');
    lado.appendChild(qr);
    lado.appendChild(instrucao);
    lado.appendChild(rotuloRodada);
    lado.appendChild(placar);
    lado.appendChild(cronometro);
    lado.appendChild(acoes);
    lado.appendChild(formChave);
    lado.appendChild(status);
    raiz.appendChild(lado);

    var estado = { rodada: 1, fase: 'parada', revelada: false, rodadaId: null };
    var cancelarOuvir = null;
    var relogio = null;
    var fimCronometro = 0;

    function avisar(texto) { status.textContent = texto || ''; }

    function pintar() {
      raiz.dataset.fase = estado.fase;
      raiz.classList.toggle('quiz-vivo-revelada', estado.revelada);
      var temChave = Boolean(ler());
      formChave.hidden = temChave;
      bEncerrar.hidden = !temChave || estado.fase !== 'aberta';
      bDeNovo.hidden = !temChave || estado.fase !== 'encerrada' || estado.rodada >= maxRodadas || estado.revelada;
      bRevelar.hidden = !temChave || estado.fase !== 'encerrada' || estado.revelada || correta === null;
      rotuloRodada.textContent = maxRodadas > 1 ? 'Rodada ' + estado.rodada + ' de ' + maxRodadas : '';
      itens.forEach(function (li, i) {
        li.classList.toggle('qv-certa', estado.revelada && i === correta);
      });
    }

    function atualizarContagem() {
      return Promise.all([dados.rodadas(sessao, pergunta), dados.sala(sessao)]).then(function (r) {
        var rodadas = r[0];
        nSala.textContent = String(r[1]);
        var ids = rodadas.map(function (x) { return x.id; });
        return dados.votos(ids).then(function (votos) {
          var porRodada = {};
          rodadas.forEach(function (x) { porRodada[x.id] = x.rodada; });
          var contas = {};
          var totais = {};
          votos.forEach(function (v) {
            var n = porRodada[v.rodada_id];
            contas[n] = contas[n] || opcoes.map(function () { return 0; });
            contas[n][v.opcao] += 1;
            totais[n] = (totais[n] || 0) + 1;
          });
          nVotos.textContent = String(totais[estado.rodada] || 0);
          itens.forEach(function (li, i) {
            for (var k = 1; k <= maxRodadas; k++) {
              var total = totais[k] || 0;
              var pct = total ? (contas[k][i] / total) * 100 : 0;
              li.querySelector('.qv-barra-' + k + ' .qv-barra-cheia').style.width = pct + '%';
            }
            var mostra = estado.fase === 'encerrada' || estado.revelada;
            var t = totais[estado.rodada] || 0;
            li.querySelector('.qv-pct').textContent = mostra && t ? Math.round((contas[estado.rodada][i] / t) * 100) + '%' : '';
          });
          raiz.classList.toggle('quiz-vivo-com-rodada-2', Boolean(totais[2]));
        });
      }).catch(function (e) { avisar('Sem conexão com o quiz (' + e.message + ').'); });
    }

    function pararCronometro() {
      if (relogio) clearInterval(relogio);
      relogio = null;
      cronometro.textContent = '';
    }

    function iniciarCronometro() {
      pararCronometro();
      if (!tempo) return;
      fimCronometro = Date.now() + tempo * 1000;
      var passo = function () {
        var resta = Math.max(0, Math.ceil((fimCronometro - Date.now()) / 1000));
        cronometro.textContent = resta + ' s';
        raiz.classList.toggle('quiz-vivo-acabando', resta <= 5);
        if (resta === 0) encerrar();
      };
      passo();
      relogio = setInterval(passo, 250);
    }

    function abrir() {
      var chave = ler();
      if (!chave) { avisar('Informe a chave do professor para abrir a votação.'); pintar(); return; }
      if (estado.fase === 'abrindo') return;
      estado.fase = 'abrindo';
      avisar('Abrindo a votação');
      dados.abrir(chave, sessao, pergunta, estado.rodada, enunciado, opcoes).then(function (id) {
        estado.rodadaId = id;
        estado.fase = 'aberta';
        avisar('');
        pintar();
        iniciarCronometro();
        return atualizarContagem();
      }).catch(function (e) {
        estado.fase = 'parada';
        avisar(/chave/.test(e.message) ? 'Chave do professor recusada.' : 'Não abriu (' + e.message + ').');
        if (/chave/.test(e.message)) { gravar(''); }
        pintar();
      });
    }

    function encerrar() {
      pararCronometro();
      if (estado.fase !== 'aberta') return Promise.resolve();
      estado.fase = 'encerrada';
      pintar();
      return dados.fechar(ler(), sessao).then(atualizarContagem).catch(function (e) { avisar('Não fechou (' + e.message + ').'); });
    }

    bEncerrar.addEventListener('click', encerrar);
    bDeNovo.addEventListener('click', function () {
      estado.rodada += 1;
      abrir();
    });
    bRevelar.addEventListener('click', function () {
      estado.revelada = true;
      pintar();
      dados.fechar(ler(), sessao, pergunta, correta).then(atualizarContagem);
    });
    formChave.addEventListener('submit', function (evento) {
      evento.preventDefault();
      if (!campo.value) return;
      gravar(campo.value);
      campo.value = '';
      pintar();
      abrir();
    });
    campo.addEventListener('keydown', function (e) { e.stopPropagation(); });

    function entrou() {
      if (!cancelarOuvir) cancelarOuvir = dados.ouvir(sessao, atualizarContagem);
      if (estado.fase === 'parada' && !estado.revelada) abrir();
      else atualizarContagem();
      pintar();
    }

    function saiu() {
      if (estado.fase === 'aberta') encerrar();
      pararCronometro();
      if (cancelarOuvir) { cancelarOuvir(); cancelarOuvir = null; }
    }

    var secao = raiz.closest('section');
    if (window.Reveal && window.Reveal.on && secao) {
      window.Reveal.on('slidechanged', function (e) {
        if (e.currentSlide === secao) entrou();
        else if (e.previousSlide === secao) saiu();
      });
      window.Reveal.on('ready', function (e) { if (e.currentSlide === secao) entrou(); });
      if (secao.classList.contains('present')) entrou();
    } else {
      entrou();
    }
    window.addEventListener('pagehide', saiu);

    pintar();
    raiz.dataset.pronto = 'sim';
    return { encerrar: encerrar, abrir: abrir, atualizar: atualizarContagem, estado: function () { return estado; } };
  }

  var instancias = [];
  function iniciar() {
    document.querySelectorAll('[data-quiz-vivo]').forEach(function (raiz) { instancias.push(montar(raiz)); });
  }
  window.IntelIQuizVivo = { instancias: instancias };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
