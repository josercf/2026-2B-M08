// Nuvem de palavras ao vivo por voz (ADR-012).
//
// O professor clica no microfone, a turma responde em voz alta, o navegador
// grava trechos curtos e manda cada um a um webhook do n8n, que transcreve na
// ElevenLabs, extrai os termos e devolve JSON. Este script acumula as
// contagens e desenha a nuvem dentro do slide.
//
// O JS não declara cor nem família de fonte: a aparência vem de
// assets/css/inteli-nuvem.css por classe (.nuvem-t1, .nuvem-t2, .nuvem-t3,
// .nuvem-lider), senão tools/check_brand.py acusa cor literal. A família só é
// lida do token (--fonte-titulo, --fonte-texto) para medir o texto no canvas.
//
// Contrato de markup, no deck:
//   <div class="nuvem" id="nuvem-projeto" data-largura="880" data-altura="440"></div>
// O conteúdo interno é construído aqui. data-largura e data-altura fixam o
// palco, porque slide fora de cena mede zero (CLAUDE.md, seção 7).
//
// Configuração, em ordem de prioridade:
//   localStorage "inteli-nuvem-webhook" / "inteli-nuvem-token", gravados pelo
//   parâmetro ?nuvem=<url>&nuvem-token=<token> ou pelo botão Webhook;
//   data-webhook / data-token no markup, fixados no deck a pedido do professor
//   (20/10/2026). Sem nenhum dos dois, o primeiro clique no microfone abre o
//   campo de configuração no próprio slide.
//
// Modo limpo (data-modo="limpo"): a nuvem ocupa a largura toda, os controles
// ficam escondidos e um botão discreto no rodapé liga o microfone. No slide
// presente, a tecla M liga e desliga o microfone e a tecla C mostra ou esconde
// os controles (campo de texto, Limpar, Webhook).
//
// API para teste e para contingência em aula:
//   IntelINuvem.adicionar(['carteira', {texto: 'risco', peso: 2}])
//   IntelINuvem.limpar()
//   IntelINuvem.estado()   -> {termos: [...], gravando, enviados, falhas}
(function () {
  'use strict';

  var CHAVE_URL = 'inteli-nuvem-webhook';
  var CHAVE_TOKEN = 'inteli-nuvem-token';

  var MAX_VISIVEIS = 60;
  var FONTE_MIN = 22;
  var FONTE_MAX = 84;
  var FONTE_PISO = 15;          // piso depois da redução por falta de espaço
  var FAIXA_T1 = 0.8;           // posição relativa a partir da qual o termo usa a fonte de título
  var MAX_T1 = 3;               // no máximo três termos na fonte de título
  var FAIXA_T2 = 0.3;
  var ALTURA_RODAPE = 40;       // faixa da última frase, dentro do palco
  var FOLGA = 6;                // espaço mínimo entre dois termos, em px
  var MARGEM = 10;              // distância mínima da borda do palco

  // Corte dos trechos de áudio. Cada trecho é um arquivo completo (o recorder
  // para e recomeça), porque com timeslice só o primeiro pedaço WebM tem
  // cabeçalho e os seguintes não decodificam sozinhos. O corte espera uma
  // pausa da fala depois de TRECHO_MIN, para não partir uma palavra ao meio,
  // e força o corte em TRECHO_MAX.
  var TRECHO_MIN = 3500;
  var TRECHO_MAX = 8000;
  var PAUSA_CORTE = 300;
  var LIMIAR_SILENCIO = 0.012;  // RMS abaixo disto conta como pausa
  var LIMIAR_FALA = 0.02;       // trecho sem pico acima disto não é enviado
  var ENVIOS_PARALELOS = 2;
  var TEMPO_LIMITE_ENVIO = 30000;

  var SPRITE = ((document.currentScript && document.currentScript.src) || '')
    .replace(/js\/[^\/]*$/, 'icons/icones.svg');
  var SVG = 'http://www.w3.org/2000/svg';

  var instancias = [];

  // ---------------------------------------------------------------- utilidades

  function criarIcone(nome) {
    var svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('class', 'icone');
    svg.setAttribute('aria-hidden', 'true');
    var uso = document.createElementNS(SVG, 'use');
    uso.setAttribute('href', SPRITE + '#' + nome);
    svg.appendChild(uso);
    return svg;
  }

  function trocarIcone(icone, nome) {
    icone.firstChild.setAttribute('href', SPRITE + '#' + nome);
  }

  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function ler(chave) {
    try { return window.localStorage.getItem(chave) || ''; } catch (e) { return ''; }
  }

  function gravar(chave, valor) {
    try {
      if (valor) window.localStorage.setItem(chave, valor);
      else window.localStorage.removeItem(chave);
    } catch (e) { /* navegação privada: vale só nesta página */ }
  }

  function formatar(ms) {
    var s = Math.floor(ms / 1000);
    var m = Math.floor(s / 60);
    s = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  function chaveDe(texto) {
    return texto.normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function urlValida(texto) {
    try {
      var u = new URL(texto);
      if (u.protocol === 'https:') return true;
      return u.protocol === 'http:' && /^(localhost|127\.0\.0\.1)$/.test(u.hostname);
    } catch (e) {
      return false;
    }
  }

  // Hash estável para alternar a cor dentro da mesma faixa sem trocar de cor a
  // cada reorganização.
  function hash(texto) {
    var h = 0;
    for (var i = 0; i < texto.length; i++) h = (h * 31 + texto.charCodeAt(i)) | 0;
    return Math.abs(h);
  }

  function token(nome) {
    return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  }

  var canvasMedida = null;
  function larguraTexto(texto, tamanho, peso, familia) {
    if (!canvasMedida) canvasMedida = document.createElement('canvas').getContext('2d');
    canvasMedida.font = peso + ' ' + tamanho + 'px ' + familia;
    return canvasMedida.measureText(texto).width;
  }

  function tipoMime() {
    var opcoes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
    if (!window.MediaRecorder || !MediaRecorder.isTypeSupported) return '';
    for (var i = 0; i < opcoes.length; i++) {
      if (MediaRecorder.isTypeSupported(opcoes[i])) return opcoes[i];
    }
    return '';
  }

  function extensao(mime) {
    if (/mp4/.test(mime)) return '.m4a';
    if (/ogg/.test(mime)) return '.ogg';
    return '.webm';
  }

  // ------------------------------------------------------------------- layout

  // Espiral arquimediana achatada na proporção do palco, com teste de colisão
  // por retângulo. Cada termo tenta primeiro o centro que já ocupava: assim a
  // nuvem cresce sem que os termos antigos pulem de lugar. Devolve null se
  // algum termo não couber, e quem chama reduz a escala.
  function dispor(itens, W, H, usarAnterior) {
    var postos = [];
    var cx = W / 2;
    var cy = H / 2;
    var ax = Math.min(W / H, 1.9);
    // Raio que alcança os cantos do palco na espiral achatada.
    var rMax = Math.sqrt(Math.pow(W / (2 * ax), 2) + Math.pow(H / 2, 2)) + 20;

    function cabe(x, y, w, h) {
      var l = x - w / 2, t = y - h / 2;
      if (l < MARGEM || t < MARGEM || l + w > W - MARGEM || t + h > H - MARGEM) return false;
      for (var i = 0; i < postos.length; i++) {
        var p = postos[i];
        if (l < p.l + p.w && l + w > p.l && t < p.t + p.h && t + h > p.t) return false;
      }
      return true;
    }

    for (var i = 0; i < itens.length; i++) {
      var it = itens[i];
      var w = it.w + FOLGA;
      var h = it.h + FOLGA;
      var achou = null;
      if (usarAnterior && it.anterior && cabe(it.anterior.x, it.anterior.y, w, h)) {
        achou = it.anterior;
      } else {
        // Passo angular que mantém uns 8px de arco entre tentativas.
        var t = 0;
        var a = 2.4;
        while (true) {
          var r = a * t;
          if (r > rMax) break;
          var x = cx + r * Math.cos(t) * ax;
          var y = cy + r * Math.sin(t);
          if (cabe(x, y, w, h)) { achou = { x: x, y: y }; break; }
          t += Math.min(0.35, 8 / Math.max(r * ax, 1));
        }
      }
      if (!achou) {
        // A espiral deixa frestas nos cantos. Antes de desistir, varre o
        // palco em grade fina, de cima para baixo, procurando uma fresta.
        for (var gy = MARGEM + h / 2; gy <= H - MARGEM - h / 2 && !achou; gy += 4) {
          for (var gx = MARGEM + w / 2; gx <= W - MARGEM - w / 2; gx += 6) {
            if (cabe(gx, gy, w, h)) { achou = { x: gx, y: gy }; break; }
          }
        }
      }
      if (!achou) return null;
      postos.push({ l: achou.x - w / 2, t: achou.y - h / 2, w: w, h: h });
      it.x = achou.x;
      it.y = achou.y;
    }
    return itens;
  }

  // ---------------------------------------------------------------- instância

  function montar(raiz) {
    var W = parseInt(raiz.dataset.largura || '880', 10);
    var H = parseInt(raiz.dataset.altura || '440', 10);
    var HA = H - ALTURA_RODAPE;          // altura da área das palavras

    var termos = new Map();              // chave -> {texto, peso, ordem, x, y, el}
    var ordem = 0;
    var agendado = false;
    var escalaAtual = 1;

    // ----- DOM
    raiz.innerHTML = '';
    raiz.style.setProperty('--nuvem-largura', W + 'px');
    raiz.style.setProperty('--nuvem-altura', H + 'px');

    var controles = el('div', 'nuvem-controles');
    var botao = el('button', 'nuvem-mic');
    botao.type = 'button';
    botao.setAttribute('aria-pressed', 'false');
    var icone = criarIcone('mic');
    var rotulo = el('span', 'nuvem-mic-rotulo', 'Ouvir a turma');
    botao.appendChild(icone);
    botao.appendChild(rotulo);

    var medidor = el('div', 'nuvem-medidor');
    medidor.setAttribute('aria-hidden', 'true');
    var barras = [];
    for (var b = 0; b < 14; b++) {
      var barra = el('span', 'nuvem-barra');
      medidor.appendChild(barra);
      barras.push(barra);
    }

    var status = el('p', 'nuvem-status', 'Microfone desligado');
    status.setAttribute('aria-live', 'polite');

    var config = el('form', 'nuvem-config');
    config.setAttribute('novalidate', '');
    var rUrl = el('label', 'nuvem-rotulo', 'URL do webhook do n8n');
    var campoUrl = el('input', 'nuvem-campo');
    campoUrl.type = 'url';
    campoUrl.placeholder = 'https://.../webhook/...';
    campoUrl.setAttribute('autocomplete', 'off');
    rUrl.appendChild(campoUrl);
    var rToken = el('label', 'nuvem-rotulo', 'Token (opcional)');
    var campoToken = el('input', 'nuvem-campo');
    campoToken.type = 'password';
    campoToken.setAttribute('autocomplete', 'off');
    rToken.appendChild(campoToken);
    var salvar = el('button', 'nuvem-botao nuvem-salvar');
    salvar.type = 'submit';
    salvar.appendChild(criarIcone('check'));
    salvar.appendChild(el('span', '', 'Salvar e ouvir'));
    config.appendChild(rUrl);
    config.appendChild(rToken);
    config.appendChild(salvar);

    var entrada = el('input', 'nuvem-campo nuvem-entrada');
    entrada.type = 'text';
    entrada.placeholder = 'Digitar um termo e Enter';
    entrada.setAttribute('aria-label', 'Adicionar termo à nuvem');
    entrada.setAttribute('autocomplete', 'off');

    var acoes = el('div', 'nuvem-acoes');
    var limpar = el('button', 'nuvem-botao nuvem-limpar');
    limpar.type = 'button';
    limpar.appendChild(criarIcone('delete_sweep'));
    limpar.appendChild(el('span', '', 'Limpar'));
    var ajustes = el('button', 'nuvem-botao nuvem-ajustes');
    ajustes.type = 'button';
    ajustes.appendChild(criarIcone('settings'));
    ajustes.appendChild(el('span', '', 'Webhook'));
    acoes.appendChild(limpar);
    acoes.appendChild(ajustes);

    controles.appendChild(botao);
    controles.appendChild(status);
    controles.appendChild(medidor);
    controles.appendChild(config);
    controles.appendChild(entrada);
    controles.appendChild(acoes);

    var palco = el('div', 'nuvem-palco');
    var area = el('div', 'nuvem-area');
    var vazio = el('p', 'nuvem-vazio', 'As respostas da turma aparecem aqui');
    area.appendChild(vazio);
    var rodape = el('div', 'nuvem-rodape');
    var frase = el('p', 'nuvem-frase', '');
    var contagem = el('p', 'nuvem-contagem', '');
    rodape.appendChild(frase);
    rodape.appendChild(contagem);
    palco.appendChild(area);
    palco.appendChild(rodape);

    // Botão discreto do modo limpo: ícone e cronômetro no rodapé da nuvem.
    var chip = el('button', 'nuvem-chip');
    chip.type = 'button';
    chip.setAttribute('aria-label', 'Ouvir a turma (tecla M)');
    var chipIcone = criarIcone('mic');
    var chipTexto = el('span', 'nuvem-chip-texto', 'M');
    chip.appendChild(chipIcone);
    chip.appendChild(chipTexto);
    rodape.insertBefore(chip, frase);

    var limpo = raiz.dataset.modo === 'limpo';
    raiz.classList.toggle('nuvem-limpa', limpo);

    raiz.appendChild(controles);
    raiz.appendChild(palco);

    function urlAtual() { return ler(CHAVE_URL) || raiz.dataset.webhook || ''; }
    function tokenAtual() { return ler(CHAVE_TOKEN) || raiz.dataset.token || ''; }

    // ----- estado da nuvem

    function adicionar(lista) {
      if (!Array.isArray(lista)) lista = [lista];
      var mudou = false;
      for (var i = 0; i < lista.length; i++) {
        var item = lista[i];
        var texto = typeof item === 'string' ? item : (item && item.texto);
        var peso = typeof item === 'string' ? 1 : Number(item && item.peso) || 1;
        texto = String(texto || '').replace(/\s+/g, ' ').trim().slice(0, 40);
        if (!texto) continue;
        peso = Math.max(1, Math.min(20, Math.round(peso)));
        var chave = chaveDe(texto);
        var t = termos.get(chave);
        if (t) {
          t.peso += peso;
          t.cresceu = true;
        } else {
          termos.set(chave, { texto: texto, peso: peso, ordem: ordem++, novo: true });
        }
        mudou = true;
      }
      if (mudou) agendar();
    }

    function limparTudo() {
      termos.forEach(function (t) { if (t.el && t.el.parentNode) t.el.parentNode.removeChild(t.el); });
      termos.clear();
      escalaAtual = 1;
      frase.textContent = '';
      agendar();
    }

    function agendar() {
      if (agendado) return;
      agendado = true;
      var rodar = function () { agendado = false; desenhar(); };
      if (window.requestAnimationFrame && !document.hidden) window.requestAnimationFrame(rodar);
      else setTimeout(rodar, 0);
    }

    function medir(visiveis, pmin, pmax, escala, familiaTitulo, familiaTexto) {
      return visiveis.map(function (t, posicao) {
        // Posição relativa na escala de frequência (raiz), de 0 a 1. A faixa de
        // cor e de fonte sai dela, e não do tamanho em px, para o termo mais
        // citado continuar na fonte de título quando a nuvem encolhe.
        var rel = pmax === pmin
          ? (visiveis.length === 1 ? 1 : 0.4)
          : Math.sqrt((t.peso - pmin) / (pmax - pmin));
        var base = FONTE_MIN + (FONTE_MAX - FONTE_MIN) * rel;
        var tamanho = Math.max(FONTE_PISO, Math.round(base * escala));
        var faixa = rel >= FAIXA_T1 && posicao < MAX_T1 ? 1 : (rel >= FAIXA_T2 ? 2 : 3);
        var peso = faixa === 3 ? 600 : 700;
        var familia = faixa === 1 ? familiaTitulo : familiaTexto;
        return {
          termo: t,
          tamanho: tamanho,
          faixa: faixa,
          w: larguraTexto(t.texto, tamanho, peso, familia) + 0.3 * tamanho,
          h: 1.12 * tamanho,
          anterior: t.x !== undefined ? { x: t.x, y: t.y } : null
        };
      });
    }

    function desenhar() {
      var todos = [];
      termos.forEach(function (t) { todos.push(t); });
      todos.sort(function (a, b) { return b.peso - a.peso || a.ordem - b.ordem; });
      var visiveis = todos.slice(0, MAX_VISIVEIS);
      var ocultos = todos.slice(MAX_VISIVEIS);

      var total = 0;
      todos.forEach(function (t) { total += t.peso; });
      raiz.classList.toggle('nuvem-com-termos', todos.length > 0);
      contagem.textContent = todos.length
        ? todos.length + (todos.length === 1 ? ' termo, ' : ' termos, ') +
          total + (total === 1 ? ' menção' : ' menções')
        : '';

      var familiaTitulo = token('--fonte-titulo') || 'serif';
      var familiaTexto = token('--fonte-texto') || 'sans-serif';
      var pmax = visiveis.length ? visiveis[0].peso : 1;
      var pmin = visiveis.length ? visiveis[visiveis.length - 1].peso : 1;

      // A escala começa na última que coube e só diminui: voltar a crescer a
      // cada termo novo faria a nuvem inteira trocar de lugar. Em cada escala
      // tenta primeiro manter os centros anteriores e só depois refaz a
      // espiral do zero. Limpar devolve a escala a 1.
      var escala = escalaAtual;
      var resultado = null;
      var itens;
      for (var tentativa = 0; tentativa < 28 && !resultado; tentativa++) {
        var comAnterior = tentativa % 2 === 0;
        itens = medir(visiveis, pmin, pmax, escala, familiaTitulo, familiaTexto);
        resultado = dispor(itens, W, HA, comAnterior);
        if (!resultado && !comAnterior) escala *= 0.92;
      }
      if (!resultado) {
        // Último recurso: mostra os que couberam no piso, sem sobrepor.
        while (itens.length && !dispor(itens, W, HA, false)) itens.pop();
        resultado = itens;
      }
      escalaAtual = escala;

      var mostrados = new Set();
      resultado.forEach(function (it, i) {
        var t = it.termo;
        mostrados.add(t);
        var novo = !t.el;
        if (novo) {
          t.el = el('span', 'nuvem-termo');
          t.interno = el('span', 'nuvem-termo-texto', t.texto);
          t.el.appendChild(t.interno);
          area.appendChild(t.el);
        }
        t.x = it.x;
        t.y = it.y;
        var cor = hash(t.texto) % 2;
        t.el.className = 'nuvem-termo nuvem-t' + it.faixa + ' nuvem-cor' + cor +
          (i === 0 && pmax > 1 ? ' nuvem-lider' : '');
        t.el.dataset.peso = String(t.peso);
        t.el.style.fontSize = it.tamanho + 'px';
        t.el.style.transform = 'translate(' + it.x.toFixed(1) + 'px, ' + it.y.toFixed(1) +
          'px) translate(-50%, -50%)';
        if (novo || t.novo) {
          t.interno.classList.remove('nuvem-entra');
          void t.interno.offsetWidth;
          t.interno.classList.add('nuvem-entra');
        } else if (t.cresceu) {
          t.interno.classList.remove('nuvem-cresce');
          void t.interno.offsetWidth;
          t.interno.classList.add('nuvem-cresce');
        }
        t.novo = false;
        t.cresceu = false;
      });

      ocultos.concat(visiveis.filter(function (t) { return !mostrados.has(t); }))
        .forEach(function (t) {
          if (t.el && t.el.parentNode) t.el.parentNode.removeChild(t.el);
          t.el = null;
          t.x = undefined;
          t.novo = false;
          t.cresceu = false;
        });
    }

    // ----- configuração

    var lidoUrl = '';
    try {
      var params = new URLSearchParams(window.location.search);
      if (params.get('nuvem')) gravar(CHAVE_URL, params.get('nuvem'));
      if (params.get('nuvem-token')) gravar(CHAVE_TOKEN, params.get('nuvem-token'));
    } catch (e) { /* sem URLSearchParams: segue com o que estiver salvo */ }

    // URL e token também ficam no Supabase do quiz (quiz_segredos), lidos e
    // gravados com a chave do professor que o quiz já guarda neste navegador.
    // Assim um navegador novo se configura sozinho, e nada vai para o repositório.
    function clienteQuiz() {
      var cfg = window.IntelIQuizConfig;
      var chave = '';
      try { chave = localStorage.getItem('inteli-quiz-chave') || ''; } catch (e) { chave = ''; }
      if (!cfg || !window.supabase || !chave) return null;
      return { cliente: window.supabase.createClient(cfg.url, cfg.chave, { auth: { persistSession: false } }), chave: chave };
    }

    function guardarNaNuvem(url, tk) {
      var q = clienteQuiz();
      if (!q) return;
      q.cliente.rpc('quiz_guardar_segredo', { p_chave: q.chave, p_nome: 'nuvem-webhook', p_valor: url });
      if (tk) q.cliente.rpc('quiz_guardar_segredo', { p_chave: q.chave, p_nome: 'nuvem-token', p_valor: tk });
    }

    function buscarNaNuvem() {
      if (ler(CHAVE_URL) && ler(CHAVE_TOKEN)) return;
      var q = clienteQuiz();
      if (!q) return;
      ['nuvem-webhook', 'nuvem-token'].forEach(function (nome) {
        q.cliente.rpc('quiz_segredo', { p_chave: q.chave, p_nome: nome }).then(function (r) {
          if (r.error || !r.data) return;
          gravar(nome === 'nuvem-webhook' ? CHAVE_URL : CHAVE_TOKEN, r.data);
        });
      });
    }
    // Depois do load: o supabase-js e a configuração do quiz vêm depois deste script.
    if (document.readyState === 'complete') buscarNaNuvem();
    else window.addEventListener('load', buscarNaNuvem);

    function abrirConfig(mensagem) {
      raiz.classList.add('nuvem-configurando', 'nuvem-mostra-controles');
      campoUrl.value = urlAtual();
      campoToken.value = tokenAtual();
      avisar(mensagem || 'Informe a URL do webhook do n8n', false);
      setTimeout(function () { campoUrl.focus(); }, 0);
    }

    function fecharConfig() {
      raiz.classList.remove('nuvem-configurando');
    }

    config.addEventListener('submit', function (evento) {
      evento.preventDefault();
      var url = campoUrl.value.trim();
      if (!urlValida(url)) {
        avisar('URL inválida: use https:// (ou http://localhost)', true);
        campoUrl.focus();
        return;
      }
      gravar(CHAVE_URL, url);
      gravar(CHAVE_TOKEN, campoToken.value.trim());
      guardarNaNuvem(url, campoToken.value.trim());
      fecharConfig();
      raiz.classList.remove('nuvem-mostra-controles');
      iniciar();
    });

    // ----- gravação

    var gravando = false;
    var abrindo = false;          // pedido de microfone em andamento
    var stream = null;
    var contexto = null;
    var analisador = null;
    var amostras = null;
    var recorder = null;
    var mime = tipoMime();
    var inicio = 0;
    var inicioTrecho = 0;
    var silencioDesde = 0;
    var picoTrecho = 0;
    var relogio = null;
    var numeroTrecho = 0;
    var enviados = 0;
    var falhas = 0;
    var fila = [];
    var ativos = 0;

    function avisar(texto, erro) {
      status.textContent = texto;
      status.classList.toggle('nuvem-aviso', !!erro);
      chip.classList.toggle('nuvem-chip-aviso', !!erro);
      chip.title = texto;
    }

    function pintarBotao() {
      raiz.classList.toggle('nuvem-gravando', gravando);
      botao.setAttribute('aria-pressed', gravando ? 'true' : 'false');
      botao.setAttribute('aria-label', gravando ? 'Parar de ouvir' : 'Ouvir a turma');
      trocarIcone(icone, gravando ? 'stop' : 'mic');
      rotulo.textContent = gravando ? formatar(Date.now() - inicio) : 'Ouvir a turma';
      trocarIcone(chipIcone, gravando ? 'stop' : 'mic');
      chipTexto.textContent = gravando ? formatar(Date.now() - inicio) : 'M';
    }

    // O microfone só abre com o slide da nuvem na tela.
    function slideAtivo() {
      var secao = raiz.closest('section');
      return !secao || !window.Reveal || secao.classList.contains('present');
    }

    function iniciar() {
      // Clique e tecla M seguidos pediriam dois microfones, e só o último
      // seria fechado: um pedido por vez.
      if (gravando || abrindo) return;
      lidoUrl = urlAtual();
      if (!lidoUrl || !urlValida(lidoUrl)) {
        abrirConfig();
        return;
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
        avisar('Este navegador não grava áudio. Use o campo de texto.', true);
        return;
      }
      avisar('Pedindo acesso ao microfone', false);
      abrindo = true;
      navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      }).then(function (s) {
        abrindo = false;
        // A permissão pode chegar depois que o professor já trocou de slide.
        if (!slideAtivo()) {
          s.getTracks().forEach(function (trilha) { trilha.stop(); });
          avisar('Microfone fechado: o slide mudou antes da permissão', false);
          return;
        }
        stream = s;
        try {
          var Ctx = window.AudioContext || window.webkitAudioContext;
          contexto = new Ctx();
          analisador = contexto.createAnalyser();
          analisador.fftSize = 1024;
          contexto.createMediaStreamSource(stream).connect(analisador);
          amostras = new Uint8Array(analisador.fftSize);
        } catch (e) {
          analisador = null;   // sem medidor: corta só pelo tempo máximo
        }
        gravando = true;
        inicio = Date.now();
        enviados = 0;
        falhas = 0;
        avisar('Ouvindo', false);
        novoTrecho();
        relogio = setInterval(vigiar, 50);
        pintarBotao();
      }).catch(function (erro) {
        abrindo = false;
        avisar('Microfone indisponível (' + (erro && erro.name || 'erro') + '). Use o campo de texto.', true);
      });
    }

    function novoTrecho() {
      var partes = [];
      try {
        recorder = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      } catch (e) {
        avisar('Falha ao iniciar a gravação. Use o campo de texto.', true);
        parar();
        return;
      }
      var este = recorder;
      inicioTrecho = Date.now();
      silencioDesde = 0;
      picoTrecho = analisador ? 0 : 1;
      este.ondataavailable = function (e) { if (e.data && e.data.size) partes.push(e.data); };
      este.onstop = function () {
        var pico = este._pico;
        var blob = new Blob(partes, { type: este.mimeType || mime || 'audio/webm' });
        if (pico >= LIMIAR_FALA && blob.size > 800) enfileirar(blob);
        if (gravando) novoTrecho();
        else soltarMicrofone();
      };
      este.start();
    }

    function vigiar() {
      var agora = Date.now();
      rotulo.textContent = formatar(agora - inicio);
      var nivel = 0;
      if (analisador) {
        analisador.getByteTimeDomainData(amostras);
        var soma = 0;
        for (var i = 0; i < amostras.length; i++) {
          var v = (amostras[i] - 128) / 128;
          soma += v * v;
        }
        nivel = Math.sqrt(soma / amostras.length);
        if (nivel > picoTrecho) picoTrecho = nivel;
        if (nivel < LIMIAR_SILENCIO) { if (!silencioDesde) silencioDesde = agora; }
        else silencioDesde = 0;
      }
      // Medidor: 14 barras acendem da esquerda para a direita conforme o nível.
      var acesas = Math.min(barras.length, Math.round(Math.sqrt(nivel / 0.25) * barras.length));
      for (var k = 0; k < barras.length; k++) barras[k].classList.toggle('acesa', k < acesas);

      if (!recorder || recorder.state !== 'recording') return;
      var duracao = agora - inicioTrecho;
      var pausa = silencioDesde && agora - silencioDesde >= PAUSA_CORTE;
      if ((duracao >= TRECHO_MIN && pausa) || duracao >= TRECHO_MAX) {
        recorder._pico = picoTrecho;
        recorder.stop();
      }
    }

    function parar() {
      if (!gravando) return;
      gravando = false;
      clearInterval(relogio);
      relogio = null;
      for (var k = 0; k < barras.length; k++) barras[k].classList.remove('acesa');
      if (recorder && recorder.state === 'recording') {
        recorder._pico = picoTrecho;
        recorder.stop();             // o onstop envia o último trecho e solta o microfone
      } else {
        soltarMicrofone();
      }
      avisar(enviados + (enviados === 1 ? ' trecho enviado' : ' trechos enviados') +
        (falhas ? ', ' + falhas + ' com falha' : ''), falhas > 0);
      pintarBotao();
    }

    function soltarMicrofone() {
      if (stream) stream.getTracks().forEach(function (t) { t.stop(); });
      stream = null;
      if (contexto && contexto.close) contexto.close().catch(function () {});
      contexto = null;
      analisador = null;
    }

    // ----- envio

    function enfileirar(blob) {
      numeroTrecho++;
      fila.push({ blob: blob, numero: numeroTrecho });
      bombear();
    }

    function bombear() {
      while (ativos < ENVIOS_PARALELOS && fila.length) {
        enviar(fila.shift());
      }
    }

    function enviar(pedido) {
      ativos++;
      var url = urlAtual() || lidoUrl;
      var dados = new FormData();
      dados.append('audio', pedido.blob, 'trecho-' + pedido.numero + extensao(pedido.blob.type));
      var tk = tokenAtual();
      if (tk) dados.append('token', tk);
      var controle = window.AbortController ? new AbortController() : null;
      var limite = controle ? setTimeout(function () { controle.abort(); }, TEMPO_LIMITE_ENVIO) : null;
      // Sem cabeçalho próprio: multipart sem cabeçalho extra é requisição
      // simples de CORS e dispensa o preflight OPTIONS (ADR-012).
      fetch(url, { method: 'POST', body: dados, signal: controle ? controle.signal : undefined })
        .then(function (resposta) {
          if (!resposta.ok) throw new Error('HTTP ' + resposta.status);
          return resposta.json();
        })
        .then(function (corpo) {
          if (Array.isArray(corpo)) corpo = corpo[0] || {};
          corpo = corpo || {};
          enviados++;
          if (corpo.transcricao) frase.textContent = '“' + corpo.transcricao + '”';
          if (Array.isArray(corpo.termos)) adicionar(corpo.termos);
          if (gravando) avisar('Ouvindo. ' + enviados + (enviados === 1 ? ' trecho transcrito' : ' trechos transcritos'), false);
        })
        .catch(function (erro) {
          falhas++;
          var motivo = erro && erro.name === 'AbortError' ? 'tempo esgotado' : (erro && erro.message) || 'rede';
          // 403 é o ramo "Recusar" do workflow: token diferente do nó "Conferir
          // token". O aviso aponta o botão onde o token se corrige.
          var dica = motivo === 'HTTP 403'
            ? ' O n8n recusou o token: confira em Webhook.'
            : (gravando ? ' A gravação continua.' : '');
          avisar('Trecho ' + pedido.numero + ' sem resposta (' + motivo + ').' + dica, true);
          if (window.console) console.warn('[nuvem] envio falhou:', motivo);
        })
        .then(function () {
          if (limite) clearTimeout(limite);
          ativos--;
          bombear();
        });
    }

    // ----- eventos

    botao.addEventListener('click', function () {
      if (gravando) parar();
      else if (raiz.classList.contains('nuvem-configurando')) campoUrl.focus();
      else iniciar();
    });

    ajustes.addEventListener('click', function () {
      if (raiz.classList.contains('nuvem-configurando')) {
        fecharConfig();
        avisar(gravando ? 'Ouvindo' : 'Microfone desligado', false);
      } else {
        abrirConfig('URL e token ficam só neste navegador');
      }
    });

    limpar.addEventListener('click', limparTudo);

    chip.addEventListener('click', function () {
      if (gravando) parar();
      else iniciar();
    });

    // Atalhos do modo limpo, só com o slide da nuvem presente e fora dos
    // campos de texto. Captura antes do Reveal para M e C não virarem outra
    // ação do deck.
    document.addEventListener('keydown', function (evento) {
      var secao = raiz.closest('section');
      if (!secao || !secao.classList.contains('present')) return;
      var alvo = evento.target;
      if (alvo && (alvo.tagName === 'INPUT' || alvo.tagName === 'TEXTAREA')) return;
      if (evento.ctrlKey || evento.metaKey || evento.altKey) return;
      var tecla = (evento.key || '').toLowerCase();
      if (tecla === 'm') {
        evento.preventDefault();
        evento.stopPropagation();
        if (gravando) parar(); else iniciar();
      } else if (tecla === 'c') {
        evento.preventDefault();
        evento.stopPropagation();
        raiz.classList.toggle('nuvem-mostra-controles');
      }
    }, true);

    entrada.addEventListener('keydown', function (evento) {
      // As teclas do Reveal (setas, espaço, N, P) não podem andar o deck
      // enquanto o professor digita.
      evento.stopPropagation();
      if (evento.key === 'Enter') {
        evento.preventDefault();
        var partes = entrada.value.split(/[,;]/);
        adicionar(partes);
        entrada.value = '';
      } else if (evento.key === 'Escape') {
        entrada.blur();
      }
    });
    [campoUrl, campoToken].forEach(function (campo) {
      campo.addEventListener('keydown', function (evento) {
        evento.stopPropagation();
        if (evento.key === 'Escape') { fecharConfig(); campo.blur(); }
      });
    });

    // Sair do slide desliga o microfone: microfone aberto fora do slide grava
    // a aula inteira e gasta transcrição à toa.
    if (window.Reveal && typeof window.Reveal.on === 'function') {
      window.Reveal.on('slidechanged', function (e) {
        if (e.currentSlide && e.currentSlide.contains(raiz)) return;
        if (gravando) parar();
        else soltarMicrofone();
      });
    }

    // Fonte de título carregada depois da primeira medição: mede de novo.
    if (document.fonts && document.fonts.load) {
      var fam = token('--fonte-titulo');
      var famTexto = token('--fonte-texto');
      Promise.all([
        fam ? document.fonts.load('700 40px ' + fam) : null,
        famTexto ? document.fonts.load('700 30px ' + famTexto) : null,
        famTexto ? document.fonts.load('600 22px ' + famTexto) : null
      ]).then(agendar, function () {});
    }

    // Fechar ou esconder a aba também solta o microfone.
    window.addEventListener('pagehide', function () { if (gravando) parar(); else soltarMicrofone(); });
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden' && gravando) parar();
    });

    pintarBotao();
    raiz.dataset.pronto = 'sim';

    var api = {
      raiz: raiz,
      adicionar: adicionar,
      limpar: limparTudo,
      parar: parar,
      estado: function () {
        var lista = [];
        termos.forEach(function (t) { lista.push({ texto: t.texto, peso: t.peso, visivel: !!t.el }); });
        lista.sort(function (a, b) { return b.peso - a.peso; });
        return { termos: lista, escala: escalaAtual, gravando: gravando,
          microfone: !!(stream && stream.getTracks().some(function (trilha) { return trilha.readyState === 'live'; })), enviados: enviados, falhas: falhas, fila: fila.length + ativos };
      }
    };
    return api;
  }

  function primeira() {
    return instancias[0];
  }

  window.IntelINuvem = {
    instancias: instancias,
    adicionar: function (lista) { if (primeira()) primeira().adicionar(lista); },
    limpar: function () { if (primeira()) primeira().limpar(); },
    parar: function () { if (primeira()) primeira().parar(); },
    estado: function () { return primeira() ? primeira().estado() : null; },
    configurar: function (url, tk) {
      gravar(CHAVE_URL, url || '');
      gravar(CHAVE_TOKEN, tk || '');
    }
  };

  function iniciarTodas() {
    var raizes = document.querySelectorAll('.nuvem');
    for (var i = 0; i < raizes.length; i++) instancias.push(montar(raizes[i]));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciarTodas);
  } else {
    iniciarTodas();
  }
})();
