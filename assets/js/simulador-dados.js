// Camada de dados da sala do simulador da Aula 04 (ADR-018). O portal fala só
// com esta interface, e ela escolhe entre o Supabase (aula) e a memória (testes,
// ensaio sem rede e queda do banco em sala).
//
//   SimuladorDados.abrir(sessao) -> sala com:
//     tipo                      'supabase' ou 'memoria'
//     motivo                    por que está em memória ('' quando não está)
//     entrar(iniciais, grupo)   -> Promise<id do participante>
//     salvar(id, simulacao)     -> Promise  {ativos, pregoes, n, semente, pesos | null}
//     marcar(id, turno, feito)  -> Promise
//     sala()                    -> Promise<[{id, iniciais, grupo, carteira | null, turnos: [int]}]>
//     specLink(id, turno)       -> Promise<{grupo, sessao, turno, token, demo}>  (turnos 4 e 5)
//     assinar(aoMudar)          -> função que cancela
//
// Queda para memória: com ?demo=1, sem a biblioteca ou sem a configuração, a
// sala já nasce em memória. Em aula, se uma chamada ao banco falhar ou passar
// de 6 segundos, a sala troca para memória, avisa quem assinou e segue: o aluno
// continua simulando e só deixa de aparecer no painel dos outros.
//
// specLink é a exceção: um erro dela não derruba a sala. A função sim_spec_link
// pode ainda não existir no banco, e isso não é motivo para tirar o aluno do
// painel; o portal mostra a mensagem e a sala segue no Supabase. Em memória ela
// devolve o token fixo TOKEN_DEMO e demo: true, e o portal abre a tela de spec
// com ?quiz-demo=1, que aceita esse token.
//
// O banco usa as funções de exemplos/aula04-supabase/aula04.sql e não escreve
// em tabela nenhuma diretamente. Não guarda nome: só iniciais e grupo.
(function () {
  'use strict';

  var ESPERA = 6000;
  var INTERVALO = 3000;
  var TOKEN_DEMO = 'demo-aula04';

  function demo() {
    return /[?&]demo=1/.test(window.location.search);
  }

  function comPrazo(promessa) {
    return new Promise(function (resolver, rejeitar) {
      var relogio = setTimeout(function () { rejeitar(new Error('o banco não respondeu')); }, ESPERA);
      promessa.then(function (v) { clearTimeout(relogio); resolver(v); },
        function (e) { clearTimeout(relogio); rejeitar(e); });
    });
  }

  function montarSala(participantes, carteiras, turnos) {
    var porId = {};
    var lista = participantes.map(function (p) {
      var item = { id: p.id, iniciais: p.iniciais, grupo: p.grupo, carteira: null, turnos: [] };
      porId[p.id] = item;
      return item;
    });
    carteiras.forEach(function (c) {
      if (porId[c.participante]) {
        porId[c.participante].carteira = {
          ativos: c.ativos, pregoes: c.pregoes, n: c.n, semente: c.semente, pesos: c.pesos || null
        };
      }
    });
    turnos.forEach(function (t) {
      if (porId[t.participante]) porId[t.participante].turnos.push(t.turno);
    });
    lista.forEach(function (item) { item.turnos.sort(); });
    return lista;
  }

  // ----------------------------------------------------------- Supabase

  function supabase(sessao) {
    var cfg = window.IntelIQuizConfig || {};
    var cliente = window.supabase.createClient(cfg.url, cfg.chave, {
      auth: { persistSession: false, autoRefreshToken: false }
    });

    function rpc(nome, args) {
      return comPrazo(cliente.rpc(nome, args).then(function (r) {
        if (r.error) throw new Error(r.error.message);
        return r.data;
      }));
    }
    function tabela(nome, colunas) {
      return comPrazo(cliente.from(nome).select(colunas).eq('sessao', sessao).then(function (r) {
        if (r.error) throw new Error(r.error.message);
        return r.data || [];
      }));
    }

    return {
      tipo: 'supabase',
      entrar: function (iniciais, grupo) {
        return rpc('sim_entrar', { p_sessao: sessao, p_iniciais: iniciais, p_grupo: grupo });
      },
      salvar: function (id, s) {
        return rpc('sim_salvar', {
          p_participante: id, p_ativos: s.ativos, p_pregoes: s.pregoes, p_n: s.n,
          p_semente: s.semente, p_pesos: s.pesos || null
        });
      },
      marcar: function (id, turno, feito) {
        return rpc('sim_marcar', { p_participante: id, p_turno: turno, p_feito: feito });
      },
      specLink: function (id, turno) {
        return rpc('sim_spec_link', { p_participante: id, p_turno: turno }).then(function (r) {
          if (!r || !r.token) throw new Error('o banco não devolveu o token da spec');
          return { grupo: r.grupo, sessao: r.sessao, turno: r.turno, token: r.token, demo: false };
        });
      },
      sala: function () {
        return Promise.all([
          tabela('sim_participantes', 'id, iniciais, grupo, criado_em'),
          tabela('sim_carteiras', 'participante, ativos, pregoes, n, semente, pesos'),
          tabela('sim_turnos', 'participante, turno')
        ]).then(function (r) {
          r[0].sort(function (a, b) { return a.criado_em < b.criado_em ? -1 : 1; });
          return montarSala(r[0], r[1], r[2]);
        });
      }
    };
  }

  // ------------------------------------------------------------ memória

  // Estado em localStorage, avisado por BroadcastChannel: duas abas do mesmo
  // navegador se enxergam, como dois alunos no banco.
  function memoria(sessao) {
    var CHAVE = 'inteli-simulador-demo:' + sessao;
    var canal = window.BroadcastChannel ? new BroadcastChannel(CHAVE) : null;
    var ouvintes = [];

    function ler() {
      try { return JSON.parse(localStorage.getItem(CHAVE)) || { participantes: [], carteiras: [], turnos: [] }; }
      catch (e) { return { participantes: [], carteiras: [], turnos: [] }; }
    }
    function gravar(estado) {
      try { localStorage.setItem(CHAVE, JSON.stringify(estado)); } catch (e) { /* aba privada */ }
      if (canal) canal.postMessage('mudou');
      ouvintes.forEach(function (f) { setTimeout(f, 0); });
    }
    if (canal) canal.onmessage = function () { ouvintes.forEach(function (f) { f(); }); };

    return {
      tipo: 'memoria',
      entrar: function (iniciais, grupo) {
        var e = ler();
        var id = 'm' + Math.random().toString(36).slice(2, 10);
        e.participantes.push({ id: id, iniciais: iniciais, grupo: grupo });
        gravar(e);
        return Promise.resolve(id);
      },
      salvar: function (id, s) {
        var e = ler();
        e.carteiras = e.carteiras.filter(function (c) { return c.participante !== id; });
        e.carteiras.push({
          participante: id, ativos: s.ativos, pregoes: s.pregoes, n: s.n,
          semente: s.semente, pesos: s.pesos || null
        });
        gravar(e);
        return Promise.resolve();
      },
      marcar: function (id, turno, feito) {
        var e = ler();
        e.turnos = e.turnos.filter(function (t) { return !(t.participante === id && t.turno === turno); });
        if (feito) e.turnos.push({ participante: id, turno: turno });
        gravar(e);
        return Promise.resolve();
      },
      sala: function () {
        var e = ler();
        return Promise.resolve(montarSala(e.participantes, e.carteiras, e.turnos));
      },
      // Mesmas recusas de sim_spec_link, com o token fixo de demonstração.
      specLink: function (id, turno) {
        var pessoa = ler().participantes.filter(function (p) { return p.id === id; })[0];
        if (!pessoa) return Promise.reject(new Error('participante desconhecido'));
        if (pessoa.grupo === 'VIS') return Promise.reject(new Error('visitante não edita a spec do grupo'));
        if (turno !== 4 && turno !== 5) return Promise.reject(new Error('só os turnos 4 e 5 têm spec do grupo'));
        return Promise.resolve({ grupo: pessoa.grupo, sessao: sessao + '-t' + turno, turno: turno, token: TOKEN_DEMO, demo: true });
      },
      escutar: function (f) { ouvintes.push(f); }
    };
  }

  // ------------------------------------------------- sala com queda segura

  function abrir(sessao) {
    var semBanco = demo() ? 'modo de demonstração'
      : (!window.supabase || !window.IntelIQuizConfig) ? 'banco indisponível nesta página' : '';
    var atual = semBanco ? memoria(sessao) : supabase(sessao);
    var assinantes = [];
    var vigia = null;
    var sala = { tipo: atual.tipo, motivo: semBanco };

    function avisar() { assinantes.forEach(function (f) { f(); }); }
    function cair(erro) {
      if (sala.tipo === 'memoria') return;
      atual = memoria(sessao);
      atual.escutar(avisar);
      sala.tipo = 'memoria';
      sala.motivo = (erro && erro.message) || 'o banco não respondeu';
      if (vigia) { clearInterval(vigia); vigia = null; }
      avisar();
    }
    if (atual.escutar) atual.escutar(avisar);

    // Tenta no banco; se falhar, cai para memória e repete a mesma chamada lá.
    // `aoCair` devolve os argumentos para a repetição, porque um id criado no
    // banco não existe na memória.
    function ehDaMemoria(id) { return /^m[a-z0-9]{1,8}$/.test(String(id)); }

    function chamar(nome, args, aoCair) {
      // Em memória, a chamada que leva id passa por aoCair, que traduz o id.
      if (sala.tipo === 'memoria') return aoCair ? aoCair() : atual[nome].apply(atual, args);
      return atual[nome].apply(atual, args).catch(function (erro) {
        cair(erro);
        return aoCair ? aoCair() : atual[nome].apply(atual, args);
      });
    }

    var locais = {};  // id do banco -> {iniciais, grupo, id em memória}
    function idLocal(id) {
      var eu = locais[id];
      if (!eu) return Promise.resolve(id);
      if (eu.memoria) return Promise.resolve(eu.memoria);
      return atual.entrar(eu.iniciais, eu.grupo).then(function (novo) { eu.memoria = novo; return novo; });
    }

    sala.entrar = function (iniciais, grupo) {
      return chamar('entrar', [iniciais, grupo]).then(function (id) {
        locais[id] = { iniciais: iniciais, grupo: grupo, memoria: sala.tipo === 'memoria' ? id : null };
        return id;
      });
    };
    sala.conhecer = function (id, iniciais, grupo) {
      // Participante recuperado de uma visita anterior (id guardado no navegador).
      // O id só vale na memória se nasceu nela (ids de memória começam com "m" e
      // não são uuid). Um uuid do banco, numa sala que abriu em memória, ganha um
      // participante novo na primeira gravação, por idLocal.
      if (!locais[id]) locais[id] = { iniciais: iniciais, grupo: grupo, memoria: ehDaMemoria(id) ? id : null };
    };
    sala.salvar = function (id, simulacao) {
      return chamar('salvar', [id, simulacao], function () {
        return idLocal(id).then(function (local) { return atual.salvar(local, simulacao); });
      });
    };
    sala.marcar = function (id, turno, feito) {
      return chamar('marcar', [id, turno, feito], function () {
        return idLocal(id).then(function (local) { return atual.marcar(local, turno, feito); });
      });
    };
    sala.sala = function () { return chamar('sala', []); };
    // Sem `chamar`: o erro volta para o portal e a sala continua onde está.
    sala.specLink = function (id, turno) {
      if (sala.tipo === 'memoria') return idLocal(id).then(function (local) { return atual.specLink(local, turno); });
      return atual.specLink(id, turno);
    };
    sala.assinar = function (aoMudar) {
      assinantes.push(aoMudar);
      if (sala.tipo === 'supabase' && !vigia) vigia = setInterval(avisar, INTERVALO);
      return function () {
        assinantes = assinantes.filter(function (f) { return f !== aoMudar; });
        if (!assinantes.length && vigia) { clearInterval(vigia); vigia = null; }
      };
    };
    return sala;
  }

  window.SimuladorDados = { abrir: abrir, demo: demo, TOKEN_DEMO: TOKEN_DEMO };
})();
