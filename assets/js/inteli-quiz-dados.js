// Camada de dados do quiz ao vivo: o slide e a página do aluno falam só com
// esta interface, e ela escolhe entre o Supabase (aula) e a memória (testes e
// ensaio sem rede, com ?quiz-demo=1 na URL).
//
//   IntelIQuizDados.criar() -> backend com:
//     entrar(sessao, nome, avatar)              -> Promise<id do participante>
//     votar(rodadaId, participanteId, opcao)    -> Promise<true | false (já votou)>
//     abrir(chave, sessao, pergunta, rodada, enunciado, opcoes) -> Promise<rodadaId>
//     fechar(chave, sessao, pergunta, correta)  -> Promise
//     rodadaAberta(sessao)                      -> Promise<rodada | null>
//     rodadas(sessao, pergunta)                 -> Promise<[rodada]>
//     votos(rodadaIds)                          -> Promise<[{rodada_id, participante_id, opcao}]>
//     sala(sessao)                              -> Promise<quantos entraram> (sem nomes)
//     ouvir(sessao, aoMudar)                    -> função que cancela
//
// A versão Supabase usa as funções de exemplos/quiz-supabase/quiz.sql; ela não
// escreve em tabela nenhuma diretamente.
(function () {
  'use strict';

  function demo() {
    return /[?&]quiz-demo=1/.test(window.location.search);
  }

  // ----------------------------------------------------------- Supabase

  function supabase() {
    var cfg = window.IntelIQuizConfig || {};
    var cliente = window.supabase.createClient(cfg.url, cfg.chave, {
      auth: { persistSession: false, autoRefreshToken: false }
    });

    function rpc(nome, args) {
      return cliente.rpc(nome, args).then(function (r) {
        if (r.error) throw new Error(r.error.message);
        return r.data;
      });
    }

    function tabela(consulta) {
      return consulta.then(function (r) {
        if (r.error) throw new Error(r.error.message);
        return r.data || [];
      });
    }

    return {
      tipo: 'supabase',
      entrar: function (sessao, nome, avatar) {
        return rpc('quiz_entrar', { p_sessao: sessao, p_nome: nome, p_avatar: avatar });
      },
      votar: function (rodadaId, participanteId, opcao) {
        return rpc('quiz_votar', { p_rodada: rodadaId, p_participante: participanteId, p_opcao: opcao });
      },
      abrir: function (chave, sessao, pergunta, rodada, enunciado, opcoes) {
        return rpc('quiz_abrir', {
          p_chave: chave, p_sessao: sessao, p_pergunta: pergunta, p_rodada: rodada,
          p_enunciado: enunciado, p_opcoes: opcoes
        });
      },
      fechar: function (chave, sessao, pergunta, correta) {
        return rpc('quiz_fechar', {
          p_chave: chave, p_sessao: sessao,
          p_pergunta: pergunta === undefined ? null : pergunta,
          p_correta: correta === undefined ? null : correta
        });
      },
      rodadaAberta: function (sessao) {
        return tabela(cliente.from('quiz_rodadas').select('*').eq('sessao', sessao).eq('aberta', true)
          .order('aberta_em', { ascending: false }).limit(1)).then(function (l) { return l[0] || null; });
      },
      rodadas: function (sessao, pergunta) {
        return tabela(cliente.from('quiz_rodadas').select('*').eq('sessao', sessao).eq('pergunta', pergunta)
          .order('rodada'));
      },
      votos: function (rodadaIds) {
        if (!rodadaIds.length) return Promise.resolve([]);
        return tabela(cliente.from('quiz_votos').select('rodada_id, participante_id, opcao').in('rodada_id', rodadaIds));
      },
      sala: function (sessao) {
        return rpc('quiz_sala', { p_sessao: sessao });
      },
      ouvir: function (sessao, aoMudar) {
        var canal = cliente.channel('quiz-' + sessao + '-' + Math.random().toString(36).slice(2))
          .on('postgres_changes', { event: '*', schema: 'public', table: 'quiz_rodadas', filter: 'sessao=eq.' + sessao }, aoMudar)
          .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'quiz_votos' }, aoMudar)
          .subscribe();
        // Rede de segurança: se o Realtime cair, a tela se atualiza a cada 4 s.
        var vigia = setInterval(aoMudar, 4000);
        return function () { clearInterval(vigia); cliente.removeChannel(canal); };
      }
    };
  }

  // ------------------------------------------------------------ memória

  // Estado guardado em localStorage e avisado por BroadcastChannel: o slide e a
  // página do aluno, abertos no mesmo navegador, conversam como no Supabase.
  function memoria() {
    var CHAVE = 'inteli-quiz-demo';
    var canal = window.BroadcastChannel ? new BroadcastChannel(CHAVE) : null;
    var ouvintes = [];

    function ler() {
      try { return JSON.parse(localStorage.getItem(CHAVE)) || { rodadas: [], participantes: [], votos: [] }; }
      catch (e) { return { rodadas: [], participantes: [], votos: [] }; }
    }
    function gravar(estado) {
      localStorage.setItem(CHAVE, JSON.stringify(estado));
      if (canal) canal.postMessage('mudou');
      ouvintes.forEach(function (f) { setTimeout(f, 0); });
    }
    function id() { return 'm' + Math.random().toString(36).slice(2, 10); }
    if (canal) canal.onmessage = function () { ouvintes.forEach(function (f) { f(); }); };

    return {
      tipo: 'memoria',
      entrar: function (sessao, nome, avatar) {
        var e = ler();
        var p = { id: id(), sessao: sessao, nome: nome.slice(0, 40), avatar: avatar };
        e.participantes.push(p);
        gravar(e);
        return Promise.resolve(p.id);
      },
      votar: function (rodadaId, participanteId, opcao) {
        var e = ler();
        var r = e.rodadas.filter(function (x) { return x.id === rodadaId; })[0];
        if (!r || !r.aberta) return Promise.reject(new Error('rodada fechada'));
        var ja = e.votos.some(function (v) { return v.rodada_id === rodadaId && v.participante_id === participanteId; });
        if (ja) return Promise.resolve(false);
        e.votos.push({ rodada_id: rodadaId, participante_id: participanteId, opcao: opcao });
        gravar(e);
        return Promise.resolve(true);
      },
      abrir: function (chave, sessao, pergunta, rodada, enunciado, opcoes) {
        var e = ler();
        e.rodadas.forEach(function (x) {
          if (x.sessao === sessao && !(x.pergunta === pergunta && x.rodada === rodada)) x.aberta = false;
        });
        var r = e.rodadas.filter(function (x) { return x.sessao === sessao && x.pergunta === pergunta && x.rodada === rodada; })[0];
        if (!r) {
          r = { id: id(), sessao: sessao, pergunta: pergunta, rodada: rodada, correta: null };
          e.rodadas.push(r);
        }
        r.enunciado = enunciado;
        r.opcoes = opcoes;
        r.aberta = true;
        r.aberta_em = r.aberta_em || new Date().toISOString();
        gravar(e);
        return Promise.resolve(r.id);
      },
      fechar: function (chave, sessao, pergunta, correta) {
        var e = ler();
        e.rodadas.forEach(function (x) {
          if (x.sessao === sessao) {
            x.aberta = false;
            if (pergunta !== undefined && correta !== undefined && x.pergunta === pergunta) x.correta = correta;
          }
        });
        gravar(e);
        return Promise.resolve();
      },
      rodadaAberta: function (sessao) {
        return Promise.resolve(ler().rodadas.filter(function (x) { return x.sessao === sessao && x.aberta; })[0] || null);
      },
      rodadas: function (sessao, pergunta) {
        return Promise.resolve(ler().rodadas.filter(function (x) { return x.sessao === sessao && x.pergunta === pergunta; })
          .sort(function (a, b) { return a.rodada - b.rodada; }));
      },
      votos: function (rodadaIds) {
        return Promise.resolve(ler().votos.filter(function (v) { return rodadaIds.indexOf(v.rodada_id) !== -1; }));
      },
      sala: function (sessao) {
        return Promise.resolve(ler().participantes.filter(function (p) { return p.sessao === sessao; }).length);
      },
      ouvir: function (sessao, aoMudar) {
        ouvintes.push(aoMudar);
        return function () { ouvintes = ouvintes.filter(function (f) { return f !== aoMudar; }); };
      }
    };
  }

  window.IntelIQuizDados = {
    criar: function () {
      if (demo() || !window.supabase || !window.IntelIQuizConfig) return memoria();
      return supabase();
    },
    demo: demo
  };
})();
