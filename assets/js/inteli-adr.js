// ADR online da Aula 02: o grupo preenche junto, dentro do próprio deck, com
// prazo comum dado pelo professor. Três componentes, todos sobre
// IntelIAula02Dados (assets/js/inteli-aula02-dados.js):
//
//   <form class="adr-online" data-adr data-sessao="..." data-grupo="G02">
//     textarea/input com name = titulo, contexto, criterios, opcoes, decisao, impacto,
//     cada um dentro de um elemento com data-campo="<name>".
//   </form>
//     Lê o token de ?t=, salva cada campo 800 ms depois da última tecla, recebe
//     o que os colegas escrevem, não sobrescreve o campo em que a pessoa está
//     digitando (mostra um aviso) e trava tudo quando o prazo do servidor acaba.
//
//   <div data-adr-links data-sessao="..." data-base="">   (slide do professor)
//     Gera os quatro links com token e inicia ou estende o prazo. Exige a chave
//     do professor, a mesma do quiz ao vivo.
//
//   <div data-adr-comite data-sessao="..." data-grupo="G01">   (projetor)
//     Mostra a ADR do grupo ao vivo, com a decisão em destaque.
(function () {
  'use strict';

  var CHAVE_PROFESSOR = 'inteli-quiz-chave';
  var ESPERA = 800;

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

  function relogio(ms) {
    var s = Math.max(0, Math.ceil(ms / 1000));
    var m = Math.floor(s / 60);
    s = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  // Relógio do servidor: guarda a diferença para o relógio local e o fim do prazo.
  function prazo(dados, sessao) {
    var estado = { desvio: 0, fim: null };
    function atualizar() {
      var antes = Date.now();
      return dados.adrAgora(sessao).then(function (r) {
        var agora = Date.parse(r.agora);
        estado.desvio = agora - (antes + Date.now()) / 2;
        estado.fim = r.fim ? Date.parse(r.fim) : null;
        return estado;
      });
    }
    estado.atualizar = atualizar;
    estado.restante = function () { return estado.fim === null ? null : estado.fim - (Date.now() + estado.desvio); };
    return estado;
  }

  // ----------------------------------------------------------------- grupo

  var MODELO = [
    ['contexto', 'Contexto e problema'],
    ['criterios', 'Critérios de decisão'],
    ['opcoes', 'Opções consideradas'],
    ['decisao', 'Decisão'],
    ['impacto', 'Consequências']
  ];

  function markdown(valores, grupo) {
    var linhas = [
      '# ADR NNNN: ' + (valores.titulo || 'título curto da decisão'),
      '',
      '- Status: proposto',
      '- Data: ' + new Date().toISOString().slice(0, 10),
      '- Decisores: grupo ' + grupo,
      '- Consultados: comitê de investimentos (Aula 02)',
      ''
    ];
    MODELO.forEach(function (par) {
      linhas.push('## ' + par[1]);
      linhas.push(valores[par[0]] || '(a preencher)');
      linhas.push('');
    });
    return linhas.join('\n');
  }

  function montarFormulario(form) {
    var dados = IntelIAula02Dados.criar();
    var sessao = IntelIAula02Dados.sessao(form.dataset.sessao);
    var grupo = form.dataset.grupo;
    var token = new URLSearchParams(window.location.search).get('t') || '';
    var campos = {};
    var enviado = {};     // último texto que esta aba gravou, por campo
    var timers = {};
    var podeEditar = false;
    var travado = false;
    var relogioServidor = prazo(dados, sessao);

    var estadoEl = form.querySelector('.adr-estado') || form.insertBefore(el('p', 'adr-estado'), form.firstChild);
    var cronometroEl = document.querySelector('[data-adr-cronometro]');

    IntelIAula02Dados.CAMPOS.forEach(function (nome) {
      var c = form.querySelector('[name=' + nome + ']');
      if (!c) return;
      campos[nome] = c;
      var caixa = c.closest('[data-campo]') || c.parentNode;
      var aviso = caixa.querySelector('.adr-aviso');
      if (!aviso) {
        aviso = el('span', 'adr-aviso', 'Outra pessoa do grupo editou este campo. Saia dele para ver o texto atual.');
        aviso.hidden = true;
        caixa.appendChild(aviso);
      }
      c.addEventListener('input', function () {
        if (!podeEditar || travado) return;
        clearTimeout(timers[nome]);
        timers[nome] = setTimeout(function () { salvar(nome); }, ESPERA);
      });
      c.addEventListener('blur', function () {
        aviso.hidden = true;
        // Primeiro grava, depois relê: ler antes de gravar traria de volta o texto antigo.
        if (timers[nome]) { clearTimeout(timers[nome]); salvar(nome).then(carregar); }
        else carregar();
      });
    });

    function mensagem(texto, tipo) {
      estadoEl.textContent = texto;
      estadoEl.dataset.tipo = tipo || '';
    }

    function somenteLeitura(sim) {
      Object.keys(campos).forEach(function (n) {
        if (sim) campos[n].setAttribute('readonly', ''); else campos[n].removeAttribute('readonly');
      });
    }

    var emVoo = {};       // gravações em curso, por campo

    function salvar(nome) {
      timers[nome] = null;
      var texto = campos[nome].value;
      enviado[nome] = texto;
      emVoo[nome] = (emVoo[nome] || 0) + 1;
      var fim = function () { emVoo[nome] -= 1; };
      return dados.adrSalvar(sessao, grupo, token, nome, texto, null).then(function () {
        fim();
        mensagem('Salvo às ' + new Date().toLocaleTimeString('pt-BR'), 'ok');
      }, function (err) {
        fim();
        mensagem(err.message === 'prazo encerrado' ? 'Prazo encerrado: o texto não foi salvo.' : 'Não salvou: ' + err.message, 'erro');
        if (err.message === 'prazo encerrado') travar();
      });
    }

    function carregar() {
      return dados.adrCampos(sessao, grupo).then(function (linhas) {
        linhas.forEach(function (l) {
          var c = campos[l.campo];
          if (!c || c.value === l.texto || emVoo[l.campo] || timers[l.campo]) return;
          var aviso = (c.closest('[data-campo]') || c.parentNode).querySelector('.adr-aviso');
          if (document.activeElement === c && !travado) {
            if (l.texto !== enviado[l.campo]) aviso.hidden = false;
            return;
          }
          c.value = l.texto;
        });
      });
    }

    function travar() {
      if (travado) return;
      travado = true;
      Object.keys(timers).forEach(function (n) { clearTimeout(timers[n]); });
      somenteLeitura(true);
      form.classList.add('adr-travado');
      mensagem('Prazo encerrado. A ADR ficou só para leitura.', 'fim');
    }

    function tique() {
      var r = relogioServidor.restante();
      if (cronometroEl) {
        cronometroEl.textContent = r === null ? 'Prazo ainda não iniciado' : (r > 0 ? relogio(r) : 'Prazo encerrado');
        cronometroEl.dataset.fase = r === null ? 'espera' : (r > 0 ? (r < 120000 ? 'final' : 'correndo') : 'fim');
      }
      if (r !== null && r <= 0) travar();
      else if (r !== null && r > 0 && travado && podeEditar) {
        // O professor estendeu o prazo.
        travado = false;
        somenteLeitura(false);
        form.classList.remove('adr-travado');
        mensagem('Prazo estendido. Podem continuar.', 'ok');
      }
    }

    form.querySelector('.adr-baixar') && form.querySelector('.adr-baixar').addEventListener('click', function (ev) {
      ev.preventDefault();
      var valores = {};
      Object.keys(campos).forEach(function (n) { valores[n] = campos[n].value.trim(); });
      var blob = new Blob([markdown(valores, grupo)], { type: 'text/markdown;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'adr-aula02-' + grupo.toLowerCase() + '.md';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    });
    form.addEventListener('submit', function (ev) { ev.preventDefault(); });

    somenteLeitura(true);
    Promise.all([dados.adrTokenOk(sessao, grupo, token), relogioServidor.atualizar(), carregar()]).then(function (r) {
      podeEditar = r[0];
      if (podeEditar) {
        somenteLeitura(false);
        mensagem('Editando como grupo ' + grupo + '. Cada campo salva sozinho.', 'ok');
      } else {
        form.classList.add('adr-leitura');
        mensagem('Este link está sem permissão de edição. Peça ao professor o link do grupo no Slack.', 'erro');
      }
      tique();
      setInterval(tique, 1000);
      dados.ouvir(sessao, function () { carregar(); relogioServidor.atualizar().then(tique); }, ['adr_campos', 'adr_prazos']);
      form.dataset.pronto = 'sim';
    }).catch(function (err) {
      mensagem('Sem conexão com o banco: ' + err.message, 'erro');
      form.dataset.pronto = 'erro';
      console.error('[adr]', err);
    });
  }

  // ------------------------------------------------------------- professor

  function montarLinks(raiz) {
    var dados = IntelIAula02Dados.criar();
    var sessao = IntelIAula02Dados.sessao(raiz.dataset.sessao);
    var base = raiz.dataset.base || '';
    var relogioServidor = prazo(dados, sessao);

    var lista = el('ol', 'adr-links-lista');
    var gerar = el('button', 'adr-gerar', 'Gerar os links dos grupos');
    gerar.type = 'button';
    var copiar = el('button', 'adr-copiar-todos', 'Copiar os quatro para o Slack');
    copiar.type = 'button';
    copiar.hidden = true;
    var minutos = el('input', 'adr-minutos');
    minutos.type = 'number';
    minutos.min = '0';
    minutos.max = '120';
    minutos.value = raiz.dataset.minutos || '25';
    var iniciar = el('button', 'adr-iniciar', 'Iniciar prazo');
    iniciar.type = 'button';
    var restante = el('span', 'adr-restante', 'Prazo ainda não iniciado');
    var aviso = el('p', 'adr-aviso-professor');

    var barra = el('div', 'adr-links-controles');
    barra.appendChild(gerar);
    barra.appendChild(copiar);
    var barraPrazo = el('div', 'adr-links-prazo');
    var rotulo = el('label', '', 'Minutos');
    rotulo.appendChild(minutos);
    barraPrazo.appendChild(rotulo);
    barraPrazo.appendChild(iniciar);
    barraPrazo.appendChild(restante);
    raiz.appendChild(barra);
    raiz.appendChild(lista);
    raiz.appendChild(barraPrazo);
    raiz.appendChild(aviso);

    var extras = [];
    if (IntelIAula02Dados.demo()) extras.push('quiz-demo=1');
    var override = new URLSearchParams(window.location.search).get('sessao');
    if (override) extras.push('sessao=' + encodeURIComponent(override));

    function url(grupo, token) {
      var u = new URL(base + 'aula02-' + grupo.toLowerCase() + '.html', window.location.href);
      return u.href.split('?')[0] + '?t=' + token + (extras.length ? '&' + extras.join('&') : '');
    }

    var textos = [];
    gerar.addEventListener('click', function () {
      if (!chave()) { aviso.textContent = 'Falta a chave do professor neste navegador (?quiz-chave=).'; return; }
      dados.adrLinks(chave(), sessao).then(function (links) {
        lista.textContent = '';
        textos = [];
        links.forEach(function (l) {
          var li = el('li');
          li.dataset.grupo = l.grupo;
          li.appendChild(el('strong', 'adr-link-grupo', l.grupo));
          var u = url(l.grupo, l.token);
          li.appendChild(el('code', 'adr-link-url', u));
          lista.appendChild(li);
          textos.push(l.grupo + ': ' + u);
        });
        copiar.hidden = false;
        aviso.textContent = '';
      }, function (err) { aviso.textContent = err.message; });
    });
    copiar.addEventListener('click', function () {
      var t = textos.join('\n');
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject())
        .then(function () { aviso.textContent = 'Copiado.'; }, function () { aviso.textContent = t; });
    });
    iniciar.addEventListener('click', function () {
      dados.adrPrazo(chave(), sessao, Number(minutos.value)).then(function () {
        return relogioServidor.atualizar();
      }).then(tique, function (err) { aviso.textContent = err.message; });
    });

    function tique() {
      var r = relogioServidor.restante();
      restante.textContent = r === null ? 'Prazo ainda não iniciado' : (r > 0 ? 'Faltam ' + relogio(r) : 'Prazo encerrado');
    }
    relogioServidor.atualizar().then(tique);
    setInterval(tique, 1000);
    dados.ouvir(sessao, function () { relogioServidor.atualizar().then(tique); }, ['adr_prazos']);
    raiz.dataset.pronto = 'sim';
  }

  // ---------------------------------------------------------------- comitê

  function montarComite(raiz) {
    var dados = IntelIAula02Dados.criar();
    var sessao = IntelIAula02Dados.sessao(raiz.dataset.sessao);
    var grupo = raiz.dataset.grupo;
    var titulo = el('p', 'adr-comite-titulo', 'Aguardando a ADR do grupo ' + grupo);
    var decisao = el('p', 'adr-comite-decisao');
    var detalhes = el('dl', 'adr-comite-detalhes');
    raiz.appendChild(titulo);
    raiz.appendChild(decisao);
    raiz.appendChild(detalhes);
    var NOMES = { contexto: 'Contexto', criterios: 'Critérios', opcoes: 'Opções', impacto: 'Consequências' };

    function carregar() {
      return dados.adrCampos(sessao, grupo).then(function (linhas) {
        var v = {};
        linhas.forEach(function (l) { v[l.campo] = l.texto; });
        titulo.textContent = v.titulo || ('ADR do grupo ' + grupo);
        decisao.textContent = v.decisao || 'Decisão ainda em branco';
        detalhes.textContent = '';
        ['contexto', 'criterios', 'opcoes', 'impacto'].forEach(function (n) {
          if (!v[n]) return;
          detalhes.appendChild(el('dt', '', NOMES[n]));
          detalhes.appendChild(el('dd', '', v[n]));
        });
      });
    }
    carregar().then(function () { raiz.dataset.pronto = 'sim'; }, function (err) {
      raiz.dataset.pronto = 'erro';
      console.error('[adr-comite]', err);
    });
    dados.ouvir(sessao, carregar, ['adr_campos']);
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
    [['form[data-adr]', montarFormulario], ['[data-adr-links]', montarLinks], ['[data-adr-comite]', montarComite]]
      .forEach(function (par) {
        Array.prototype.forEach.call(document.querySelectorAll(par[0]), function (r) { quandoPresente(r, par[1]); });
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
