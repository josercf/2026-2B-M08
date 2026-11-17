// Tela de spec da Aula 04 (aulas/aula04-spec.html, ADR-018).
//
// A página abre com ?g=G01&t=<token>&turno=4 (ou 5) e reaproveita o formulário
// da ADR online (assets/js/inteli-adr.js). Este script roda antes dele e:
//   1. lê grupo e turno da URL e grava data-grupo e data-sessao no formulário
//      (sessão m08-aula04-2026-11-18-t4 ou -t5);
//   2. registra o código do grupo como autor, para nenhum nome de aluno ir ao
//      banco (a tabela de campos tem leitura pública);
//   3. liga o botão "Copiar como SPEC.md".
//
// O banco só aceita os campos da ADR. A spec usa cinco deles:
//   titulo -> Função, contexto -> Entrada, criterios -> Saída,
//   opcoes -> Casos de borda, decisao -> Critério de aceite.
(function () {
  'use strict';

  var SESSAO_BASE = 'm08-aula04-2026-11-18';
  var GRUPOS = ['G01', 'G02', 'G03', 'G04'];
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
  var form = document.querySelector('form[data-spec]');
  if (!form) return;

  var valido = GRUPOS.indexOf(grupo) !== -1 && Object.prototype.hasOwnProperty.call(TURNOS, turno);
  if (!valido) {
    // Sem grupo ou turno válidos o formulário não é montado: sai o atributo
    // que o inteli-adr.js procura e a página explica como abrir o link.
    form.removeAttribute('data-adr');
    form.hidden = true;
    var aviso = document.querySelector('[data-spec-aviso]');
    if (aviso) aviso.hidden = false;
    document.documentElement.dataset.spec = 'sem-grupo';
    return;
  }

  var sessao = params.get('sessao') || (SESSAO_BASE + '-t' + turno);
  form.dataset.grupo = grupo;
  form.dataset.sessao = SESSAO_BASE + '-t' + turno;
  document.documentElement.dataset.spec = 'ok';

  // O formulário da ADR pede o nome de quem digita. Aqui o autor é o grupo.
  try {
    localStorage.setItem('inteli-adr-nomes-' + sessao + '-' + grupo, JSON.stringify(['Grupo ' + grupo]));
  } catch (e) { /* aba privada: o formulário pede um nome e segue funcionando */ }

  Array.prototype.forEach.call(document.querySelectorAll('[data-spec-grupo]'), function (e) { e.textContent = grupo; });
  Array.prototype.forEach.call(document.querySelectorAll('[data-spec-turno]'), function (e) { e.textContent = turno; });
  Array.prototype.forEach.call(document.querySelectorAll('[data-spec-funcao]'), function (e) { e.textContent = TURNOS[turno].nome; });
  var campoFuncao = form.querySelector('[name=titulo]');
  if (campoFuncao) campoFuncao.placeholder = TURNOS[turno].funcao.replace(/`/g, '');
  document.title = 'Aula 04 - Spec do turno ' + turno + ' - Grupo ' + grupo;

  // Texto no formato do SPEC.md do kit (exemplos/aula04-simulador/SPEC.md):
  // título "## Turno N" e um parágrafo "**Campo:** texto" por campo.
  function specMarkdown() {
    var linhas = ['## Turno ' + turno, ''];
    CAMPOS.forEach(function (par) {
      var campo = form.querySelector('[name=' + par[0] + ']');
      var valor = campo ? campo.value.trim() : '';
      if (par[0] === 'titulo' && !valor) valor = TURNOS[turno].funcao;
      linhas.push('**' + par[1] + ':** ' + (valor || '(a preencher)'));
      linhas.push('');
    });
    return linhas.join('\n');
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
