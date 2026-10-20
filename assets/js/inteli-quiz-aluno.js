// Tela do aluno do quiz ao vivo (quiz/index.html).
//
// Estados, em data-estado do <main>: entrar, esperar, votar, votou, sem-sessao.
// O aluno entra uma vez por sessão (nome e avatar ficam no localStorage do
// celular), e a tela segue a rodada aberta pelo slide: aparece quando o slide
// abre, some quando o slide fecha, e aceita um voto por rodada.
(function () {
  'use strict';

  var LETRAS = ['A', 'B', 'C', 'D', 'E', 'F'];
  var SPRITE = '../assets/icons/icones.svg#';
  var raiz = document.querySelector('.aluno');
  var params = new URLSearchParams(window.location.search);
  var sessao = params.get('s');
  var dados = window.IntelIQuizDados.criar();
  var chaveEu = 'inteli-quiz-eu-' + sessao;
  var eu = null;
  var rodadaAtual = null;
  var votando = false;

  function estado(nome) { raiz.dataset.estado = nome; }

  function lerEu() {
    try { return JSON.parse(localStorage.getItem(chaveEu)); } catch (e) { return null; }
  }

  function mostrarEu() {
    var quem = raiz.querySelector('.aluno-quem');
    quem.hidden = false;
    quem.querySelector('use').setAttribute('href', SPRITE + eu.avatar);
    quem.querySelector('.aluno-quem-nome').textContent = eu.nome;
  }

  // ----- entrar

  var form = raiz.querySelector('.entrar');
  var avatarEscolhido = '';
  raiz.querySelectorAll('.avatar').forEach(function (botao) {
    botao.setAttribute('role', 'radio');
    botao.setAttribute('aria-checked', 'false');
    botao.addEventListener('click', function () {
      raiz.querySelectorAll('.avatar').forEach(function (b) {
        b.classList.remove('escolhido');
        b.setAttribute('aria-checked', 'false');
      });
      botao.classList.add('escolhido');
      botao.setAttribute('aria-checked', 'true');
      avatarEscolhido = botao.dataset.avatar;
    });
  });

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();
    var nome = form.nome.value.trim();
    var erro = form.querySelector('.erro');
    if (nome.split(/\s+/).length < 2) { erro.textContent = 'Escreva o nome completo, com sobrenome.'; return; }
    if (!avatarEscolhido) { erro.textContent = 'Escolha um avatar.'; return; }
    erro.textContent = '';
    form.querySelector('.principal').disabled = true;
    dados.entrar(sessao, nome, avatarEscolhido).then(function (id) {
      eu = { id: id, nome: nome, avatar: avatarEscolhido };
      try {
        localStorage.setItem(chaveEu, JSON.stringify(eu));
        localStorage.setItem('inteli-quiz-perfil', JSON.stringify({ nome: nome, avatar: avatarEscolhido }));
      } catch (e) { /* aba privada */ }
      mostrarEu();
      atualizar();
    }).catch(function (e) {
      erro.textContent = 'Não deu para entrar (' + e.message + '). Tente de novo.';
      form.querySelector('.principal').disabled = false;
    });
  });

  // ----- seguir a rodada aberta

  function montarPergunta(rodada) {
    var tela = raiz.querySelector('.tela-votar');
    tela.querySelector('.rodada').textContent = rodada.rodada > 1 ? 'Rodada ' + rodada.rodada + ': vote de novo' : 'Pergunta';
    tela.querySelector('.enunciado').textContent = rodada.enunciado;
    tela.querySelector('.erro').textContent = '';
    var lista = tela.querySelector('.opcoes');
    lista.innerHTML = '';
    (rodada.opcoes || []).forEach(function (texto, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'opcao opcao-' + i;
      b.innerHTML = '<span class="opcao-letra"></span><span class="opcao-texto"></span>';
      b.querySelector('.opcao-letra').textContent = LETRAS[i];
      b.querySelector('.opcao-texto').textContent = texto;
      b.addEventListener('click', function () { votar(rodada, i); });
      lista.appendChild(b);
    });
  }

  function mostrarVotou(rodada, opcao) {
    var tela = raiz.querySelector('.tela-votou');
    tela.querySelector('.rodada').textContent = rodada.rodada > 1 ? 'Rodada ' + rodada.rodada : 'Pergunta';
    tela.querySelector('.votou-escolha').textContent = opcao === null
      ? 'Você já votou nesta rodada.'
      : 'Sua escolha: ' + LETRAS[opcao] + ', ' + rodada.opcoes[opcao];
    estado('votou');
  }

  function votar(rodada, opcao) {
    if (votando) return;
    votando = true;
    raiz.querySelectorAll('.opcao').forEach(function (b) { b.disabled = true; });
    dados.votar(rodada.id, eu.id, opcao).then(function (aceito) {
      mostrarVotou(rodada, aceito ? opcao : null);
    }).catch(function (e) {
      // O registro do aluno foi apagado no banco (sessão limpa depois de um
      // teste): entra de novo com o nome guardado e repete o voto.
      if (/participante/.test(e.message)) {
        return dados.entrar(sessao, eu.nome, eu.avatar).then(function (id) {
          eu.id = id;
          try { localStorage.setItem(chaveEu, JSON.stringify(eu)); } catch (x) { /* aba privada */ }
          return dados.votar(rodada.id, eu.id, opcao);
        }).then(function (aceito) { mostrarVotou(rodada, aceito ? opcao : null); });
      }
      throw e;
    }).catch(function (e) {
      raiz.querySelector('.tela-votar .erro').textContent = /fechada/.test(e.message)
        ? 'A votação já fechou.' : 'Não deu para votar (' + e.message + ').';
      raiz.querySelectorAll('.opcao').forEach(function (b) { b.disabled = false; });
    }).then(function () { votando = false; });
  }

  function atualizar() {
    if (!eu) return;
    dados.rodadaAberta(sessao).then(function (rodada) {
      if (!rodada) {
        rodadaAtual = null;
        estado('esperar');
        return;
      }
      return dados.votos([rodada.id]).then(function (votos) {
        var meu = votos.filter(function (v) { return v.participante_id === eu.id; })[0];
        if (meu) {
          rodadaAtual = rodada;
          mostrarVotou(rodada, meu.opcao);
        } else if (!rodadaAtual || rodadaAtual.id !== rodada.id || raiz.dataset.estado !== 'votar') {
          rodadaAtual = rodada;
          montarPergunta(rodada);
          estado('votar');
        }
      });
    }).catch(function () { /* sem rede: a próxima mudança ou o vigia tentam de novo */ });
  }

  // ----- início

  if (!sessao) {
    estado('sem-sessao');
    return;
  }
  eu = lerEu();
  if (eu && eu.id) {
    mostrarEu();
    atualizar();
  } else {
    eu = null;
    // Outra aula já guardou o nome e o avatar neste celular: entra sozinho.
    var perfil = null;
    try { perfil = JSON.parse(localStorage.getItem('inteli-quiz-perfil')); } catch (e) { perfil = null; }
    if (perfil && perfil.nome && perfil.avatar) {
      dados.entrar(sessao, perfil.nome, perfil.avatar).then(function (id) {
        eu = { id: id, nome: perfil.nome, avatar: perfil.avatar };
        try { localStorage.setItem(chaveEu, JSON.stringify(eu)); } catch (e) { /* aba privada */ }
        mostrarEu();
        atualizar();
      }).catch(function () { estado('entrar'); });
    } else {
      estado('entrar');
    }
  }
  dados.ouvir(sessao, function () { atualizar(); });
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') atualizar();
  });

  window.IntelIQuizAluno = { atualizar: atualizar };
})();
