// Código linha a linha: cada fragment do Reveal destaca um trecho, a janela de
// código desliza até ele e o painel ao lado explica o que aquelas linhas fazem.
//
// Contrato de markup (ver o slide #coletar-codigo da Aula 01):
//   <div class="codigo-passos" data-codigo-passos
//        data-intro-titulo="..." data-intro="...">
//     <div class="codigo-janela">
//       <pre class="codigo-linhas"><code>
//         <span class="cl" data-n="1"><span class="cl-n">1</span>def f():</span> ...
//       </code></pre>
//     </div>
//     <aside class="codigo-explica">
//       <p class="codigo-contador"></p><p class="codigo-titulo"></p><p class="codigo-texto"></p>
//     </aside>
//     <span class="fragment codigo-passo" data-linhas="12-21"
//           data-titulo="..." data-texto="..."></span>
//   </div>
//
// Sem fragment visível, o painel mostra a introdução e nenhuma linha fica em
// destaque. Em ?print-pdf o slide fica nesse estado inicial. O elemento recebe
// data-pronto="sim" ao montar.
(function () {
  'use strict';

  function intervalo(texto) {
    var linhas = [];
    String(texto || '').split(',').forEach(function (parte) {
      var limites = parte.trim().split('-').map(Number);
      var de = limites[0];
      var ate = limites.length > 1 ? limites[1] : de;
      for (var n = de; n <= ate; n++) linhas.push(n);
    });
    return linhas;
  }

  function escrever(raiz, contador, titulo, texto) {
    var painel = raiz.querySelector('.codigo-explica');
    painel.querySelector('.codigo-contador').textContent = contador;
    painel.querySelector('.codigo-titulo').textContent = titulo;
    painel.querySelector('.codigo-texto').textContent = texto;
    painel.classList.remove('codigo-explica-troca');
    // Força o reinício da transição de entrada do painel.
    void painel.offsetWidth;
    painel.classList.add('codigo-explica-troca');
  }

  // Desliza o código para que o trecho em destaque fique no meio da janela,
  // sem passar do começo nem do fim. Usa offsetTop e clientHeight, que não
  // sofrem a escala que o Reveal aplica com transform.
  function enquadrar(raiz, linhas) {
    var janela = raiz.querySelector('.codigo-janela');
    var bloco = raiz.querySelector('.codigo-linhas');
    var deslocamento = 0;
    if (linhas.length) {
      var primeira = raiz.querySelector('.cl[data-n="' + linhas[0] + '"]');
      var ultima = raiz.querySelector('.cl[data-n="' + linhas[linhas.length - 1] + '"]');
      if (primeira && ultima) {
        var meio = (primeira.offsetTop + ultima.offsetTop + ultima.offsetHeight) / 2;
        var maximo = Math.max(0, bloco.scrollHeight - janela.clientHeight);
        deslocamento = Math.min(maximo, Math.max(0, meio - janela.clientHeight / 2));
      }
    }
    bloco.style.transform = 'translateY(' + (-deslocamento) + 'px)';
  }

  function atualizar(raiz) {
    var passos = Array.prototype.slice.call(raiz.querySelectorAll('.codigo-passo'));
    var visiveis = passos.filter(function (p) { return p.classList.contains('visible'); });
    var atual = visiveis[visiveis.length - 1];
    var linhas = atual ? intervalo(atual.dataset.linhas) : [];

    raiz.classList.toggle('codigo-em-passo', Boolean(atual));
    // Modo foco: o resto do slide esmaece enquanto um trecho está em destaque.
    var secao = raiz.closest('section');
    if (secao) secao.classList.toggle('codigo-foco', Boolean(atual));
    var progresso = raiz.querySelector('.codigo-progresso');
    if (!progresso) {
      progresso = document.createElement('div');
      progresso.className = 'codigo-progresso';
      passos.forEach(function () { progresso.appendChild(document.createElement('span')); });
      raiz.querySelector('.codigo-explica').appendChild(progresso);
    }
    Array.prototype.forEach.call(progresso.children, function (marca, i) {
      marca.classList.toggle('feito', i <= passos.indexOf(atual));
    });
    var referencia = raiz.querySelector('.codigo-referencia');
    if (!referencia) {
      referencia = document.createElement('p');
      referencia.className = 'codigo-referencia';
      var painel = raiz.querySelector('.codigo-explica');
      painel.insertBefore(referencia, painel.querySelector('.codigo-titulo'));
    }
    referencia.textContent = atual
      ? (linhas.length > 1 ? 'linhas ' + linhas[0] + ' a ' + linhas[linhas.length - 1] : 'linha ' + linhas[0])
      : '';
    raiz.querySelectorAll('.cl').forEach(function (linha) {
      linha.classList.toggle('cl-destaque', linhas.indexOf(Number(linha.dataset.n)) !== -1);
    });
    enquadrar(raiz, linhas);

    if (atual) {
      escrever(raiz, (passos.indexOf(atual) + 1) + ' de ' + passos.length,
        atual.dataset.titulo, atual.dataset.texto);
    } else {
      escrever(raiz, passos.length + ' passos', raiz.dataset.introTitulo, raiz.dataset.intro);
    }
  }

  function atualizarSecao(secao) {
    if (!secao) return;
    secao.querySelectorAll('[data-codigo-passos]').forEach(atualizar);
  }

  function iniciar() {
    document.querySelectorAll('[data-codigo-passos]').forEach(function (raiz) {
      atualizar(raiz);
      raiz.dataset.pronto = 'sim';
    });
    if (window.Reveal && window.Reveal.on) {
      ['fragmentshown', 'fragmenthidden'].forEach(function (nome) {
        window.Reveal.on(nome, function (evento) {
          atualizarSecao(evento.fragment && evento.fragment.closest('section'));
        });
      });
      window.Reveal.on('slidechanged', function (evento) { atualizarSecao(evento.currentSlide); });
      window.Reveal.on('ready', function (evento) { atualizarSecao(evento.currentSlide); });
    }
  }

  window.IntelICodigo = { atualizar: atualizar };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
