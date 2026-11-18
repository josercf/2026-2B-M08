// Documentos do kit dentro do deck da Aula 04 (ADR-018): o SPEC.md, o AGENTS.md
// e as duas ADRs de exemplo aparecem no slide com aparência de arquivo, lidos
// de exemplos/aula04-simulador/ em tempo de execução. Sem biblioteca externa.
//
//   <button type="button" class="doc-abrir"
//           data-documento="../exemplos/aula04-simulador/SPEC.md"
//           data-nome="SPEC.md" data-secao="Turno 3">SPEC.md</button>
//     Abre o arquivo numa sobreposição com rolagem interna. Fecha por Esc, por
//     clique fora e pelo botão, e devolve o foco ao botão que abriu. Enquanto
//     está aberta, nenhuma tecla chega ao Reveal. data-secao rola até o
//     primeiro título que começa com o texto dado.
//
//   <div class="doc-fixo" data-documento-abas>
//     <div class="doc-fixo-barra">
//       <button type="button" data-documento="..." data-nome="SPEC.md">SPEC.md</button>
//       <button type="button" data-documento="..." data-nome="AGENTS.md">AGENTS.md</button>
//     </div>
//     <div class="doc-fixo-corpo"></div>
//   </div>
//     Painel fixo no slide, com uma aba por arquivo e rolagem interna. Recebe
//     data-pronto="sim" quando o primeiro arquivo é desenhado.
//
// Se o fetch falhar, o corpo mostra uma mensagem e o link do arquivo.
// window.Aula04Documento expõe markdown(texto) para os testes.
(function () {
  'use strict';

  function escapar(texto) {
    return texto.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Marcação dentro da linha: código, negrito e link. O código sai primeiro,
  // para que asterisco dentro de crase não vire negrito.
  function emLinha(texto) {
    var trechos = [];
    var saida = escapar(texto).replace(/`([^`]+)`/g, function (_, codigo) {
      trechos.push('<code>' + codigo + '</code>');
      return '\u0000' + (trechos.length - 1) + '\u0000';
    });
    saida = saida.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    saida = saida.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    return saida.replace(/\u0000(\d+)\u0000/g, function (_, i) { return trechos[Number(i)]; });
  }

  function celulas(linha) {
    return linha.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (c) { return c.trim(); });
  }

  // Conversor mínimo de Markdown: títulos, parágrafos, listas com linha de
  // continuação, citação, negrito, código em linha e em bloco, tabela simples.
  function markdown(fonte) {
    var linhas = String(fonte).replace(/\r\n?/g, '\n').split('\n');
    var html = [];
    var i = 0;

    function lista(ordenada) {
      var marca = ordenada ? /^\s*\d+[.)]\s+(.*)$/ : /^\s*[-*]\s+(.*)$/;
      var itens = [];
      while (i < linhas.length) {
        var m = marca.exec(linhas[i]);
        if (m) { itens.push(m[1]); i += 1; continue; }
        // Linha recuada continua o item anterior.
        if (itens.length && /^\s+\S/.test(linhas[i])) { itens[itens.length - 1] += ' ' + linhas[i].trim(); i += 1; continue; }
        break;
      }
      var tag = ordenada ? 'ol' : 'ul';
      html.push('<' + tag + '>' + itens.map(function (t) { return '<li>' + emLinha(t) + '</li>'; }).join('') + '</' + tag + '>');
    }

    while (i < linhas.length) {
      var linha = linhas[i];
      if (!linha.trim()) { i += 1; continue; }

      var cerca = /^```/.exec(linha);
      if (cerca) {
        var codigo = [];
        i += 1;
        while (i < linhas.length && !/^```/.test(linhas[i])) { codigo.push(linhas[i]); i += 1; }
        i += 1;
        html.push('<pre><code>' + escapar(codigo.join('\n')) + '</code></pre>');
        continue;
      }

      var titulo = /^(#{1,4})\s+(.*)$/.exec(linha);
      if (titulo) {
        var nivel = titulo[1].length;
        html.push('<h' + nivel + '>' + emLinha(titulo[2]) + '</h' + nivel + '>');
        i += 1;
        continue;
      }

      if (/^\s*\|/.test(linha) && i + 1 < linhas.length && /^\s*\|[\s:|-]+\|\s*$/.test(linhas[i + 1])) {
        var cabecalho = celulas(linha);
        var corpo = [];
        i += 2;
        while (i < linhas.length && /^\s*\|/.test(linhas[i])) { corpo.push(celulas(linhas[i])); i += 1; }
        html.push('<table><thead><tr>' + cabecalho.map(function (c) { return '<th>' + emLinha(c) + '</th>'; }).join('') +
          '</tr></thead><tbody>' + corpo.map(function (l) {
            return '<tr>' + l.map(function (c) { return '<td>' + emLinha(c) + '</td>'; }).join('') + '</tr>';
          }).join('') + '</tbody></table>');
        continue;
      }

      if (/^>\s?/.test(linha)) {
        var citacao = [];
        while (i < linhas.length && /^>\s?/.test(linhas[i])) { citacao.push(linhas[i].replace(/^>\s?/, '')); i += 1; }
        html.push('<blockquote><p>' + emLinha(citacao.join(' ')) + '</p></blockquote>');
        continue;
      }

      if (/^\s*[-*]\s+/.test(linha)) { lista(false); continue; }
      if (/^\s*\d+[.)]\s+/.test(linha)) { lista(true); continue; }

      var paragrafo = [];
      while (i < linhas.length && linhas[i].trim() && !/^(#{1,4}\s|```|>\s?|\s*[-*]\s+|\s*\d+[.)]\s+|\s*\|)/.test(linhas[i])) {
        paragrafo.push(linhas[i].trim());
        i += 1;
      }
      // Linha que começa por um marcador não reconhecido acima: vira parágrafo sozinha.
      if (!paragrafo.length) { paragrafo.push(linha.trim()); i += 1; }
      html.push('<p>' + emLinha(paragrafo.join(' ')) + '</p>');
    }
    return html.join('\n');
  }

  // Cada arquivo é pedido uma vez; a promessa fica guardada.
  var cache = {};
  function carregar(url) {
    if (!cache[url]) {
      cache[url] = fetch(url).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.text();
      });
      cache[url].catch(function () { delete cache[url]; });
    }
    return cache[url];
  }

  function desenhar(corpo, url, nome, secao) {
    corpo.dataset.estado = 'carregando';
    corpo.dataset.documento = nome;
    corpo.textContent = 'Carregando ' + nome + '...';
    return carregar(url).then(function (texto) {
      corpo.innerHTML = markdown(texto);
      corpo.dataset.estado = 'pronto';
      corpo.scrollTop = 0;
      if (secao) {
        var alvo = Array.prototype.filter.call(corpo.querySelectorAll('h1, h2, h3, h4'), function (h) {
          return h.textContent.trim().indexOf(secao) === 0;
        })[0];
        if (alvo) corpo.scrollTop += alvo.getBoundingClientRect().top - corpo.getBoundingClientRect().top - 18;
      }
    }, function () {
      corpo.textContent = '';
      var aviso = document.createElement('p');
      aviso.className = 'doc-erro';
      aviso.textContent = 'O arquivo ' + nome + ' não carregou neste navegador. ';
      var link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = 'Abrir ' + nome + ' em outra aba';
      aviso.appendChild(link);
      corpo.appendChild(aviso);
      corpo.dataset.estado = 'erro';
    });
  }

  // ------------------------------------------------------------- sobreposição
  var popup = null;
  var origem = null;

  function montarPopup() {
    var fundo = document.createElement('div');
    fundo.className = 'doc-popup';
    fundo.hidden = true;
    var janela = document.createElement('div');
    janela.className = 'doc-popup-janela';
    janela.setAttribute('role', 'dialog');
    janela.setAttribute('aria-modal', 'true');
    janela.setAttribute('aria-labelledby', 'doc-popup-nome');
    var barra = document.createElement('div');
    barra.className = 'doc-popup-barra';
    var nome = document.createElement('p');
    nome.className = 'doc-popup-nome';
    nome.id = 'doc-popup-nome';
    // O nome do arquivo vai em <code>, que é onde o tema aplica a fonte mono.
    var nomeCodigo = document.createElement('code');
    nome.appendChild(nomeCodigo);
    var link = document.createElement('a');
    link.className = 'doc-popup-link';
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = 'Abrir em outra aba';
    var fechar = document.createElement('button');
    fechar.type = 'button';
    fechar.className = 'doc-popup-fechar';
    fechar.textContent = 'Fechar (Esc)';
    barra.appendChild(nome);
    barra.appendChild(link);
    barra.appendChild(fechar);
    var corpo = document.createElement('div');
    corpo.className = 'doc-popup-corpo doc-texto';
    corpo.tabIndex = 0;
    janela.appendChild(barra);
    janela.appendChild(corpo);
    fundo.appendChild(janela);
    document.body.appendChild(fundo);

    fechar.addEventListener('click', fecharPopup);
    // Clique fora da janela fecha; clique dentro dela, não.
    fundo.addEventListener('mousedown', function (ev) {
      if (ev.target !== fundo) return;
      // Sem o preventDefault, o próprio clique tiraria o foco do botão de origem.
      ev.preventDefault();
      fecharPopup();
    });
    return { fundo: fundo, nome: nomeCodigo, link: link, corpo: corpo, fechar: fechar };
  }

  function abrirPopup(botao) {
    if (!popup) popup = montarPopup();
    origem = botao;
    var url = botao.dataset.documento;
    var nome = botao.dataset.nome || url.split('/').pop();
    popup.nome.textContent = nome;
    popup.link.href = url;
    popup.fundo.hidden = false;
    document.documentElement.classList.add('doc-popup-aberto');
    desenhar(popup.corpo, url, nome, botao.dataset.secao || '');
    // O foco vai para o corpo do documento, e não para o botão Fechar: com o
    // foco no botão, a barra de espaço do passador de slides fecharia a janela.
    popup.corpo.focus();
  }

  function fecharPopup() {
    if (!popup || popup.fundo.hidden) return;
    popup.fundo.hidden = true;
    document.documentElement.classList.remove('doc-popup-aberto');
    if (origem && document.contains(origem)) origem.focus();
    origem = null;
  }

  function aberto() { return !!popup && !popup.fundo.hidden; }

  // Na fase de captura da janela, antes do Reveal: com o documento aberto,
  // nenhuma tecla navega o deck. Esc fecha, Tab circula dentro da janela e as
  // teclas de rolagem seguem para o corpo do documento.
  window.addEventListener('keydown', function (ev) {
    if (!aberto()) return;
    ev.stopPropagation();
    if (ev.key === 'Escape') { ev.preventDefault(); fecharPopup(); return; }
    if (ev.key === 'Tab') {
      var foco = [popup.link, popup.fechar, popup.corpo];
      var atual = foco.indexOf(document.activeElement);
      var proximo = (atual + (ev.shiftKey ? -1 : 1) + foco.length) % foco.length;
      ev.preventDefault();
      foco[atual === -1 ? 0 : proximo].focus();
      return;
    }
    var rolagem = { ArrowDown: 60, ArrowUp: -60, PageDown: 400, PageUp: -400, ' ': 400 };
    var noBotao = document.activeElement === popup.fechar || document.activeElement === popup.link;
    if (Object.prototype.hasOwnProperty.call(rolagem, ev.key) && !(noBotao && ev.key === ' ')) {
      ev.preventDefault();
      popup.corpo.scrollTop += rolagem[ev.key];
    }
  }, true);
  ['keyup', 'keypress'].forEach(function (tipo) {
    window.addEventListener(tipo, function (ev) { if (aberto()) ev.stopPropagation(); }, true);
  });

  // --------------------------------------------------------------- painel fixo
  function montarAbas(raiz) {
    var botoes = raiz.querySelectorAll('.doc-fixo-barra button[data-documento]');
    var corpo = raiz.querySelector('.doc-fixo-corpo');
    var ampliar = raiz.querySelector('.doc-fixo-ampliar');
    if (!botoes.length || !corpo) return;
    corpo.classList.add('doc-texto');

    function escolher(botao) {
      Array.prototype.forEach.call(botoes, function (b) { b.setAttribute('aria-pressed', b === botao ? 'true' : 'false'); });
      if (ampliar) {
        ampliar.dataset.documento = botao.dataset.documento;
        ampliar.dataset.nome = botao.dataset.nome || '';
      }
      return desenhar(corpo, botao.dataset.documento, botao.dataset.nome || botao.textContent.trim(), '');
    }

    Array.prototype.forEach.call(botoes, function (b) {
      b.addEventListener('click', function () { escolher(b); });
    });
    escolher(botoes[0]).then(function () { raiz.dataset.pronto = 'sim'; });
  }

  function iniciar() {
    document.addEventListener('click', function (ev) {
      var botao = ev.target.closest ? ev.target.closest('.doc-abrir[data-documento]') : null;
      if (!botao) return;
      ev.preventDefault();
      abrirPopup(botao);
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-documento-abas]'), montarAbas);
    // Os arquivos do slide em cena ficam em memória antes do clique: a
    // sobreposição abre sem esperar a rede no meio do turno. Só o slide em
    // cena, para um arquivo ausente não gerar erro na carga do deck.
    function adiantar(ev) {
      var secao = ev && ev.currentSlide;
      if (!secao) return;
      Array.prototype.forEach.call(secao.querySelectorAll('.doc-abrir[data-documento]'), function (b) {
        carregar(b.dataset.documento).catch(function () { /* a mensagem aparece ao abrir */ });
      });
    }
    if (window.Reveal && window.Reveal.on) {
      window.Reveal.on('ready', adiantar);
      window.Reveal.on('slidechanged', adiantar);
    }
  }

  window.Aula04Documento = { markdown: markdown, abrir: abrirPopup, fechar: fecharPopup, aberto: aberto };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
