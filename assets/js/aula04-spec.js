// Tela de spec da Aula 04 (aulas/aula04-spec.html, ADR-018).
//
// Endereços:
//   ?g=G01&t=<token>&turno=4&a=JR   edição pelo grupo (turno 4 ou 5). Sai pronto
//                                   do botão "Abrir a spec do grupo" do portal.
//   ?g=G01&turno=4&ver=1            visão somente leitura, sem token e sem campo,
//                                   para o professor projetar.
//
// Na edição a página reaproveita o formulário da ADR online
// (assets/js/inteli-adr.js). Este script roda antes dele e:
//   1. lê grupo e turno da URL e grava data-grupo e data-sessao no formulário
//      (sessão m08-aula04-2026-11-18-t4 ou -t5);
//   2. define o autor pelas iniciais (a=), em data-autor. Sem a=, pede as
//      iniciais antes de liberar a edição. Nenhum nome de aluno vai ao banco: a
//      tabela de campos tem leitura pública, e por isso guarda iniciais e grupo;
//   3. mostra em cada campo o selo de quem editou por último e há quanto tempo,
//      e no cabeçalho quem está na spec do grupo agora;
//   4. liga o botão "Copiar como SPEC.md".
//
// Quem está na spec agora não passa pelo banco de dados: é a presença do canal
// Realtime do Supabase (iniciais e campo em foco), ou, em memória (?quiz-demo=1),
// uma chave do localStorage renovada a cada 2,5 s. Se o canal não conectar, o
// cabeçalho mostra quem gravou nos últimos 30 s e os selos seguem funcionando.
//
// O banco só aceita os campos da ADR. A spec usa cinco deles:
//   titulo -> Função, contexto -> Entrada, criterios -> Saída,
//   opcoes -> Casos de borda, decisao -> Critério de aceite.
(function () {
  'use strict';

  var SESSAO_BASE = 'm08-aula04-2026-11-18';
  var GRUPOS = ['G01', 'G02', 'G03', 'G04'];
  var TOKEN_DEMO = 'demo-aula04';   // o mesmo de assets/js/simulador-dados.js
  var RECENTE = 10000;              // edição com menos de 10 s ganha destaque
  var TURNOS = {
    '4': { funcao: '`simular(retornos, n, semente, rf)`', nome: 'simular' },
    '5': { funcao: '`simular(retornos, n, semente, rf)`, com requisito de tempo: 10.000 simulações em menos de 10 segundos, com 2 a 20 ativos; e `posicionar(pesos, retornos, rf)`', nome: 'simular e posicionar' }
  };
  var CAMPOS = [
    ['titulo', 'Função'],
    ['contexto', 'Entrada'],
    ['criterios', 'Saída'],
    ['opcoes', 'Casos de borda'],
    ['decisao', 'Critério de aceite']
  ];

  var params = new URLSearchParams(window.location.search);
  var grupo = (params.get('g') || '').toUpperCase();
  var turno = params.get('turno') || '4';
  var ver = params.get('ver') === '1';
  var form = document.querySelector('form[data-spec]');
  if (!form) return;

  function todos(seletor, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(seletor)); }
  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  // Mesma regra do portal: de 1 a 3 letras, em maiúsculas.
  function iniciaisLimpas(texto) {
    return String(texto || '').toLocaleUpperCase('pt-BR').replace(/[^A-ZÀ-Ý]/g, '').slice(0, 3);
  }

  var valido = GRUPOS.indexOf(grupo) !== -1 && Object.prototype.hasOwnProperty.call(TURNOS, turno);
  if (!valido) {
    // Sem grupo ou turno válidos o formulário não é montado: sai o atributo
    // que o inteli-adr.js procura e a página explica como abrir a spec.
    form.removeAttribute('data-adr');
    form.hidden = true;
    var aviso = document.querySelector('[data-spec-aviso]');
    if (aviso) aviso.hidden = false;
    document.documentElement.dataset.spec = 'sem-grupo';
    return;
  }

  var sessao = params.get('sessao') || (SESSAO_BASE + '-t' + turno);
  var Dados = window.IntelIAula02Dados;
  var memoria = !Dados || Dados.demo() || !window.supabase || !window.IntelIQuizConfig;
  var iniciais = ver ? '' : iniciaisLimpas(params.get('a'));

  form.dataset.grupo = grupo;
  form.dataset.sessao = SESSAO_BASE + '-t' + turno;
  document.documentElement.dataset.spec = ver ? 'leitura' : 'ok';

  todos('[data-spec-grupo]').forEach(function (e) { e.textContent = grupo; });
  todos('[data-spec-turno]').forEach(function (e) { e.textContent = turno; });
  todos('[data-spec-funcao]').forEach(function (e) { e.textContent = TURNOS[turno].nome; });
  document.title = 'Aula 04 - Spec do turno ' + turno + ' - Grupo ' + grupo + (ver ? ' - somente leitura' : '');

  var barra = document.querySelector('[data-spec-barra]');
  var fichas = document.querySelector('[data-spec-fichas]');
  var pedido = document.querySelector('[data-spec-iniciais]');
  var euEl = document.querySelector('[data-spec-eu]');
  if (barra) barra.hidden = false;

  // ------------------------------------------------- selos e presença

  var caixas = {};     // campo -> elemento que recebe o selo
  var linhas = {};     // campo -> {texto, autor, atualizado_em}
  var presentes = [];  // [{a, campo}]
  var canalVivo = false;  // a presença já respondeu ao menos uma vez
  var desvio = 0;      // relógio do servidor menos o relógio local, em ms

  function haQuanto(ms) {
    if (ms < RECENTE) return 'agora';
    if (ms < 60000) return 'há ' + Math.floor(ms / 1000) + ' s';
    if (ms < 3600000) return 'há ' + Math.floor(ms / 60000) + ' min';
    return 'há ' + Math.floor(ms / 3600000) + ' h';
  }

  function unicos(lista) {
    return lista.filter(function (v, i) { return v && lista.indexOf(v) === i; });
  }

  function pintarSelos() {
    var agora = Date.now() + desvio;
    CAMPOS.forEach(function (par) {
      var caixa = caixas[par[0]];
      if (!caixa) return;
      var selo = caixa.querySelector('.spec-selo');
      if (!selo) {
        selo = el('span', 'spec-selo');
        selo.appendChild(el('strong', 'spec-selo-quem'));
        selo.appendChild(el('span', 'spec-selo-quando'));
        caixa.appendChild(selo);
      }
      var editando = unicos(presentes.filter(function (p) { return p.campo === par[0]; }).map(function (p) { return p.a; }));
      var linha = linhas[par[0]];
      var quem = '', quando = '', vivo = false;
      if (editando.length) {
        quem = editando.join(' e ');
        quando = 'editando';
        vivo = true;
      } else if (linha && linha.autor) {
        var idade = Math.max(0, agora - Date.parse(linha.atualizado_em));
        quem = String(linha.autor).slice(0, 24);
        quando = haQuanto(idade);
        vivo = idade < RECENTE;
      }
      selo.hidden = !quem;
      selo.firstChild.textContent = quem;
      selo.lastChild.textContent = quem ? ', ' + quando : '';
      selo.dataset.vivo = vivo ? 'sim' : 'nao';
      caixa.dataset.vivo = vivo ? 'sim' : 'nao';
    });
    pintarPresentes(agora);
  }

  function pintarPresentes(agora) {
    if (!fichas) return;
    // Presença do canal. Enquanto o canal não responde, vale quem gravou nos últimos 30 s.
    var nomes = presentes.map(function (p) { return p.a; });
    if (!canalVivo) {
      Object.keys(linhas).forEach(function (campo) {
        var l = linhas[campo];
        if (l.autor && agora - Date.parse(l.atualizado_em) < 30000) nomes.push(iniciaisLimpas(l.autor) === l.autor ? l.autor : '');
      });
    }
    nomes = unicos(nomes).sort();
    var assinatura = nomes.join(',');
    if (fichas.dataset.quem === assinatura) return;
    fichas.dataset.quem = assinatura;
    fichas.textContent = '';
    if (!nomes.length) fichas.appendChild(el('span', 'spec-ninguem', 'ninguém do grupo'));
    nomes.forEach(function (a) {
      var ficha = el('span', 'spec-ficha' + (a === iniciais ? ' spec-ficha-eu' : ''), a);
      ficha.dataset.grupo = grupo;
      fichas.appendChild(ficha);
    });
  }

  function receber(lista, agora) {
    if (agora) desvio = agora - Date.now();
    (lista || []).forEach(function (l) {
      var atual = linhas[l.campo];
      // Uma leitura atrasada não desfaz o selo da gravação que esta aba acabou de fazer.
      if (atual && Date.parse(atual.atualizado_em) > Date.parse(l.atualizado_em)) return;
      linhas[l.campo] = { texto: l.texto, autor: l.autor, atualizado_em: l.atualizado_em };
    });
    pintarSelos();
  }

  // Presença: `definir({a, campo})` anuncia esta aba; `definir(null)` só observa.
  function criarPresenca(aoMudar) {
    var meu = null;
    var id = Math.random().toString(36).slice(2, 10);
    var nomesDeCampo = CAMPOS.map(function (par) { return par[0]; });
    function limpa(p) {
      return { a: iniciaisLimpas(p && p.a), campo: p && nomesDeCampo.indexOf(p.campo) !== -1 ? p.campo : null };
    }

    if (memoria) {
      var CHAVE = 'inteli-spec-presenca:' + sessao + ':' + grupo;
      var VALIDADE = 8000;
      var ler = function () {
        try { return JSON.parse(localStorage.getItem(CHAVE)) || {}; } catch (e) { return {}; }
      };
      var publicar = function (t) {
        var agora = Date.now();
        aoMudar(Object.keys(t).filter(function (k) { return agora - t[k].t <= VALIDADE; })
          .map(function (k) { return limpa(t[k]); }).filter(function (p) { return p.a; }));
      };
      var bater = function () {
        var t = ler();
        var agora = Date.now();
        Object.keys(t).forEach(function (k) { if (agora - t[k].t > VALIDADE) delete t[k]; });
        if (meu) t[id] = { a: meu.a, campo: meu.campo || null, t: agora }; else delete t[id];
        try { localStorage.setItem(CHAVE, JSON.stringify(t)); } catch (e) { /* aba privada */ }
        publicar(t);
      };
      setInterval(bater, 2500);
      setInterval(function () { publicar(ler()); }, 1000);
      window.addEventListener('storage', function (ev) { if (ev.key === CHAVE) publicar(ler()); });
      window.addEventListener('pagehide', function () { meu = null; bater(); });
      bater();
      return { definir: function (estado) { meu = estado; bater(); } };
    }

    try {
      var cfg = window.IntelIQuizConfig;
      var cliente = window.supabase.createClient(cfg.url, cfg.chave, {
        auth: { persistSession: false, autoRefreshToken: false }
      });
      var canal = cliente.channel('spec-presenca:' + sessao + ':' + grupo, { config: { presence: { key: id } } });
      var inscrito = false;
      // Quem só observa também entra no canal, com iniciais vazias (que a lista
      // descarta): o servidor do Realtime só manda a presença dos outros para a
      // conexão que anunciou a própria.
      var enviar = function () {
        if (!inscrito) return;
        canal.track(meu ? { a: meu.a, campo: meu.campo || null } : { a: '', campo: null });
      };
      canal.on('presence', { event: 'sync' }, function () {
        var estado = canal.presenceState();
        var lista = [];
        Object.keys(estado).forEach(function (k) {
          (estado[k] || []).forEach(function (p) { var q = limpa(p); if (q.a) lista.push(q); });
        });
        aoMudar(lista);
      }).subscribe(function (status) {
        if (status === 'SUBSCRIBED') { inscrito = true; enviar(); }
      });
      return { definir: function (estado) { meu = estado; enviar(); } };
    } catch (e) {
      console.warn('[spec] presença indisponível', e);
      return { definir: function () {} };
    }
  }

  var presenca = criarPresenca(function (lista) { canalVivo = true; presentes = lista; pintarSelos(); });
  setInterval(pintarSelos, 1000);

  // ------------------------------------------------------ somente leitura

  if (ver) {
    form.parentNode.removeChild(form);   // nenhum campo editável na página
    if (pedido) pedido.parentNode.removeChild(pedido);
    var cronometro = document.querySelector('[data-adr-cronometro]');
    if (cronometro) cronometro.textContent = 'Somente leitura';
    var depois = document.getElementById('depois');
    if (depois) {
      depois.parentNode.removeChild(depois);
      if (window.Reveal && window.Reveal.sync) window.Reveal.sync();
    }

    var leitura = document.querySelector('[data-spec-leitura]');
    var textos = {};
    CAMPOS.forEach(function (par) {
      var bloco = el('div', 'spec-leitura-campo');
      bloco.dataset.campo = par[0];
      bloco.appendChild(el('p', 'spec-leitura-rotulo', par[1]));
      textos[par[0]] = bloco.appendChild(el('p', 'spec-leitura-texto'));
      leitura.appendChild(bloco);
      caixas[par[0]] = bloco;
    });
    var estadoLeitura = leitura.appendChild(el('p', 'spec-leitura-estado', 'Conectando...'));
    leitura.hidden = false;

    // Atalhos para as outras specs, mantendo os parâmetros de ensaio.
    var outros = document.querySelector('[data-spec-outros]');
    var resto = ['quiz-demo', 'sessao'].filter(function (k) { return params.get(k); })
      .map(function (k) { return '&' + k + '=' + encodeURIComponent(params.get(k)); }).join('');
    var atalho = function (g, t, texto) {
      var a = el('a', '', texto);
      a.href = '?g=' + g + '&turno=' + t + '&ver=1' + resto;
      if (g === grupo && t === turno) a.setAttribute('aria-current', 'page');
      return a;
    };
    if (outros) {
      GRUPOS.forEach(function (g) { outros.appendChild(atalho(g, turno, g)); });
      outros.appendChild(el('span', 'spec-outros-separador'));
      Object.keys(TURNOS).forEach(function (t) { outros.appendChild(atalho(grupo, t, 'Turno ' + t)); });
      outros.hidden = false;
    }

    var dados = Dados.criar();
    var carregar = function () {
      return dados.adrCampos(sessao, grupo).then(function (lista) {
        var v = {};
        lista.forEach(function (l) { v[l.campo] = l.texto; });
        CAMPOS.forEach(function (par) {
          var texto = (v[par[0]] || '').trim();
          textos[par[0]].textContent = texto || 'Ainda em branco';
          textos[par[0]].dataset.vazio = texto ? 'nao' : 'sim';
        });
        estadoLeitura.textContent = 'Somente leitura. O texto atualiza sozinho enquanto o grupo escreve.';
        estadoLeitura.dataset.tipo = '';
        receber(lista);
      });
    };
    dados.adrAgora(sessao).then(function (r) { desvio = Date.parse(r.agora) - Date.now(); pintarSelos(); }, function () {});
    carregar().then(function () { leitura.dataset.pronto = 'sim'; }, function (err) {
      estadoLeitura.textContent = 'Sem conexão com o banco: ' + err.message;
      estadoLeitura.dataset.tipo = 'erro';
      leitura.dataset.pronto = 'erro';
      console.error('[spec]', err);
    });
    dados.ouvir(sessao, function () { carregar().catch(function () { /* a próxima leitura tenta de novo */ }); }, ['adr_campos']);
    window.IntelISpecAula04 = { sessao: sessao, grupo: grupo, turno: turno, leitura: true };
    return;
  }

  // --------------------------------------------------------------- edição

  // O autor é quem está neste computador, pelas iniciais. O formulário da ADR
  // fica só para leitura enquanto data-autor estiver vazio.
  form.setAttribute('data-autor', iniciais);
  form.dataset.semPermissao = 'Este endereço está sem permissão de edição. Abra a spec pelo botão "Abrir a spec do grupo", na tela Progresso do portal.';

  // Em memória, o token fixo que o portal entrega precisa existir na sala de
  // demonstração da ADR (inteli-aula02-dados.js guarda os tokens nesta chave).
  if (memoria && Dados && Dados.demo() && params.get('t') === TOKEN_DEMO) {
    try {
      var sala = JSON.parse(localStorage.getItem('inteli-aula02-demo')) ||
        { tokens: [], prazos: {}, campos: [], rodadas: {}, jogadores: [], jogadas: [] };
      var existe = sala.tokens.some(function (t) { return t.sessao === sessao && t.grupo === grupo && t.token === TOKEN_DEMO; });
      if (!existe) {
        sala.tokens.push({ sessao: sessao, grupo: grupo, token: TOKEN_DEMO });
        localStorage.setItem('inteli-aula02-demo', JSON.stringify(sala));
      }
    } catch (e) { /* aba privada: a spec abre só para leitura */ }
  }

  todos('[data-campo]', form).forEach(function (caixa) { caixas[caixa.getAttribute('data-campo')] = caixa; });
  var campoFuncao = form.querySelector('[name=titulo]');
  if (campoFuncao) campoFuncao.placeholder = TURNOS[turno].funcao.replace(/`/g, '');

  var podeEditar = false;
  var emFoco = null;

  function anunciar() {
    presenca.definir(podeEditar && iniciais ? { a: iniciais, campo: emFoco } : null);
  }

  function mostrarQuemSou() {
    if (pedido) pedido.hidden = !!iniciais || !podeEditar;
    if (euEl) {
      euEl.hidden = !iniciais || !podeEditar;
      euEl.textContent = iniciais ? 'Você edita como ' + iniciais : '';
    }
    form.dataset.iniciais = iniciais;
  }

  function definirIniciais(valor) {
    iniciais = iniciaisLimpas(valor);
    if (!iniciais) return false;
    form.setAttribute('data-autor', iniciais);
    form.dispatchEvent(new CustomEvent('adr-autor'));
    // A recarga da página mantém as iniciais.
    try {
      params.set('a', iniciais);
      window.history.replaceState(null, '', window.location.pathname + '?' + params.toString() + window.location.hash);
    } catch (e) { /* endereço fica como está */ }
    mostrarQuemSou();
    anunciar();
    if (fichas) fichas.dataset.quem = '';
    pintarSelos();
    return true;
  }

  if (pedido) {
    var campoIniciais = pedido.querySelector('input');
    var entrar = function () {
      if (definirIniciais(campoIniciais.value)) {
        var primeiro = form.querySelector('[name=titulo]');
        if (primeiro) primeiro.focus();
      } else {
        campoIniciais.focus();
      }
    };
    // Quem veio do portal neste navegador já tem iniciais: elas entram como sugestão.
    try {
      var portal = JSON.parse(localStorage.getItem('inteli-simulador-eu:' + SESSAO_BASE));
      if (portal && portal.grupo === grupo) campoIniciais.value = iniciaisLimpas(portal.iniciais);
    } catch (e) { /* sem sugestão */ }
    campoIniciais.addEventListener('input', function () { campoIniciais.value = iniciaisLimpas(campoIniciais.value); });
    campoIniciais.addEventListener('keydown', function (ev) {
      ev.stopPropagation();   // o deck não troca de slide enquanto a pessoa digita
      if (ev.key === 'Enter') { ev.preventDefault(); entrar(); }
    });
    pedido.querySelector('[data-spec-entrar]').addEventListener('click', entrar);
  }

  form.addEventListener('adr-pronto', function (ev) {
    podeEditar = !!(ev.detail && ev.detail.podeEditar);
    mostrarQuemSou();
    anunciar();
  });
  form.addEventListener('adr-campos', function (ev) { receber(ev.detail.linhas, ev.detail.agora); });
  form.addEventListener('adr-salvo', function (ev) {
    receber([{ campo: ev.detail.campo, texto: '', autor: ev.detail.autor, atualizado_em: ev.detail.atualizado_em }]);
  });
  form.addEventListener('focusin', function (ev) {
    var caixa = ev.target.closest && ev.target.closest('[data-campo]');
    emFoco = caixa && !ev.target.hasAttribute('readonly') ? caixa.getAttribute('data-campo') : null;
    anunciar();
  });
  form.addEventListener('focusout', function () { emFoco = null; anunciar(); });

  // Texto no formato do SPEC.md do kit (exemplos/aula04-simulador/SPEC.md):
  // título "## Turno N" e um parágrafo "**Campo:** texto" por campo.
  function specMarkdown() {
    var linhasMd = ['## Turno ' + turno, ''];
    CAMPOS.forEach(function (par) {
      var campo = form.querySelector('[name=' + par[0] + ']');
      var valor = campo ? campo.value.trim() : '';
      if (par[0] === 'titulo' && !valor) valor = TURNOS[turno].funcao;
      linhasMd.push('**' + par[1] + ':** ' + (valor || '(a preencher)'));
      linhasMd.push('');
    });
    return linhasMd.join('\n');
  }

  var botao = form.querySelector('.spec-copiar');
  var saida = form.querySelector('.spec-saida');
  var estado = form.querySelector('.spec-copiado');
  if (botao) {
    botao.addEventListener('click', function (ev) {
      ev.preventDefault();
      var texto = specMarkdown();
      if (saida) saida.value = texto;
      function ok() { if (estado) estado.textContent = 'Copiado. Cole no SPEC.md do kit, no lugar do bloco do turno ' + turno + '.'; }
      function manual() {
        // Sem permissão de área de transferência: seleciona o texto para Ctrl+C.
        if (saida) { saida.focus(); saida.select(); }
        var feito = false;
        try { feito = document.execCommand('copy'); } catch (e) { feito = false; }
        if (feito) ok();
        else if (estado) estado.textContent = 'A cópia automática falhou neste navegador. Avise o professor.';
      }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(ok, manual);
      else manual();
    });
  }

  window.IntelISpecAula04 = { markdown: specMarkdown, sessao: sessao, grupo: grupo, turno: turno };
})();
