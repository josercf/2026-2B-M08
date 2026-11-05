// Camada de dados da Aula 02: jogo da moeda e ADR online dos grupos.
// O slide, o celular e o deck do grupo falam só com esta interface. Ela usa o
// Supabase do quiz (exemplos/aula02-supabase/aula02.sql) ou, com ?quiz-demo=1
// na URL, a memória do navegador (testes e ensaio sem rede).
//
//   IntelIAula02Dados.criar() -> backend com:
//     adrLinks(chave, sessao)                          -> Promise<[{grupo, token}]>
//     adrPrazo(chave, sessao, minutos)                 -> Promise<fim ISO>
//     adrAgora(sessao)                                 -> Promise<{agora, fim}>
//     adrTokenOk(sessao, grupo, token)                -> Promise<boolean>
//     adrSalvar(sessao, grupo, token, campo, texto, autor) -> Promise<ISO>
//     adrCampos(sessao, grupo?)                        -> Promise<[{grupo, campo, texto, autor, atualizado_em}]>
//     moedaLiberar(chave, sessao, rodada)              -> Promise<rodada>
//     moedaRodada(sessao)                              -> Promise<int>
//     moedaEntrar(sessao, apelido)                     -> Promise<id>
//     moedaCruzamento(sessao, pergunta)                -> Promise<[{opcao, abaixo, acima}]> (último voto x saldo final)
//     moedaSala(sessao)                                -> Promise<quantos entraram>
//     moedaJogar(sessao, jogador, rodada)              -> Promise<{cara, saldo}>
//     moedaJogadas(sessao, jogador?)                   -> Promise<[{jogador, rodada, cara, saldo}]>
//     moedaZerar(chave, sessao)                        -> Promise (apaga jogadas e jogadores da sessão)
//     ouvir(sessao, aoMudar, tabelas?)                 -> função que cancela; avisa no máximo a cada 300 ms
(function () {
  'use strict';

  var CAMPOS = ['titulo', 'contexto', 'criterios', 'opcoes', 'decisao', 'impacto', 'codigo'];
  var GRUPOS = ['G01', 'G02', 'G03', 'G04'];

  var TABELAS = ['adr_campos', 'adr_prazos', 'moeda_sessoes', 'moeda_jogadas'];

  // Muitos eventos em sequência (30 celulares jogando a mesma rodada) viram uma
  // única releitura a cada 300 ms.
  function juntar(f) {
    var marcado = null;
    return function () {
      if (marcado) return;
      marcado = setTimeout(function () { marcado = null; f(); }, 300);
    };
  }

  function demo() { return /[?&]quiz-demo=1/.test(window.location.search); }

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
    function primeira(l) { return Array.isArray(l) ? l[0] : l; }

    return {
      tipo: 'supabase',
      adrLinks: function (chave, sessao) { return rpc('adr_links', { p_chave: chave, p_sessao: sessao }); },
      adrPrazo: function (chave, sessao, minutos) {
        return rpc('adr_prazo', { p_chave: chave, p_sessao: sessao, p_minutos: minutos });
      },
      adrAgora: function (sessao) { return rpc('adr_agora', { p_sessao: sessao }).then(primeira); },
      adrEntrar: function (sessao, grupo, token, nome) {
        return rpc('adr_entrar', { p_sessao: sessao, p_grupo: grupo, p_token: token || '', p_nome: nome || '' });
      },
      adrParticipacao: function (chave, sessao) { return rpc('adr_participacao', { p_chave: chave, p_sessao: sessao }); },
      adrIntegrantes: function (sessao, grupo, token) {
        return rpc('adr_integrantes', { p_sessao: sessao, p_grupo: grupo, p_token: token || '' })
          .then(function (l) { return (l || []).map(function (x) { return x.nome; }); })
          .catch(function () { return []; });
      },
      adrTokenOk: function (sessao, grupo, token) {
        return rpc('adr_token_ok', { p_sessao: sessao, p_grupo: grupo, p_token: token || '' });
      },
      adrSalvar: function (sessao, grupo, token, campo, texto, autor) {
        return rpc('adr_salvar', {
          p_sessao: sessao, p_grupo: grupo, p_token: token || '', p_campo: campo, p_texto: texto, p_autor: autor || null
        });
      },
      adrCampos: function (sessao, grupo) {
        var q = cliente.from('adr_campos').select('grupo, campo, texto, autor, atualizado_em').eq('sessao', sessao);
        if (grupo) q = q.eq('grupo', grupo);
        return tabela(q);
      },
      moedaLiberar: function (chave, sessao, rodada) {
        return rpc('moeda_liberar', { p_chave: chave, p_sessao: sessao, p_rodada: rodada });
      },
      moedaRodada: function (sessao) {
        return tabela(cliente.from('moeda_sessoes').select('rodada').eq('sessao', sessao))
          .then(function (l) { return l.length ? l[0].rodada : 0; });
      },
      moedaSala: function (sessao) { return rpc('moeda_sala', { p_sessao: sessao }); },
      moedaEntrar: function (sessao, apelido, participante) {
        // Banco anterior à migração da participação: entra sem o vínculo com o quiz.
        return rpc('moeda_entrar', { p_sessao: sessao, p_apelido: apelido, p_participante: participante || null })
          .catch(function () { return rpc('moeda_entrar', { p_sessao: sessao, p_apelido: apelido }); });
      },
      moedaCruzamento: function (sessao, pergunta) {
        return rpc('moeda_cruzamento', { p_sessao: sessao, p_pergunta: pergunta });
      },
      moedaJogar: function (sessao, jogador, rodada) {
        return rpc('moeda_jogar', { p_sessao: sessao, p_jogador: jogador, p_rodada: rodada }).then(function (l) {
          var j = primeira(l);
          return { cara: j.cara, saldo: Number(j.saldo) };
        });
      },
      moedaJogadas: function (sessao, jogador) {
        var q = cliente.from('moeda_jogadas').select('jogador, rodada, cara, saldo').eq('sessao', sessao);
        if (jogador) q = q.eq('jogador', jogador);
        return tabela(q.order('rodada').limit(1000))
          .then(function (l) { return l.map(function (j) { j.saldo = Number(j.saldo); return j; }); });
      },
      moedaZerar: function (chave, sessao) { return rpc('moeda_zerar', { p_chave: chave, p_sessao: sessao }); },
      ouvir: function (sessao, aoMudarBruto, tabelas) {
        var aoMudar = juntar(aoMudarBruto);
        var filtro = 'sessao=eq.' + sessao;
        var canal = cliente.channel('aula02-' + sessao + '-' + Math.random().toString(36).slice(2));
        (tabelas || TABELAS).forEach(function (t) {
          canal = canal.on('postgres_changes', { event: '*', schema: 'public', table: t, filter: filtro }, aoMudar);
        });
        canal.subscribe();
        // Rede de segurança: se o Realtime cair, a tela se atualiza a cada 4 s.
        var vigia = setInterval(aoMudar, 4000);
        return function () { clearInterval(vigia); cliente.removeChannel(canal); };
      }
    };
  }

  // ------------------------------------------------------------ memória

  // Mesmas regras do SQL, em localStorage, com aviso por BroadcastChannel para
  // as outras abas do mesmo navegador.
  function memoria() {
    var CHAVE = 'inteli-aula02-demo';
    var canal = window.BroadcastChannel ? new BroadcastChannel(CHAVE) : null;
    var ouvintes = [];
    var vazio = function () { return { tokens: [], prazos: {}, campos: [], rodadas: {}, jogadores: [], jogadas: [] }; };

    function ler() {
      try { return JSON.parse(localStorage.getItem(CHAVE)) || vazio(); } catch (e) { return vazio(); }
    }
    function gravar(e) {
      localStorage.setItem(CHAVE, JSON.stringify(e));
      if (canal) canal.postMessage('mudou');
      ouvintes.forEach(function (f) { setTimeout(f, 0); });
    }
    function id() { return 'm' + Math.random().toString(36).slice(2, 12); }
    function professor(chave) { if (!chave) throw new Error('chave do professor inválida'); }
    function falha(msg) { return Promise.reject(new Error(msg)); }
    if (canal) canal.onmessage = function () { ouvintes.forEach(function (f) { f(); }); };

    return {
      tipo: 'memoria',
      adrLinks: function (chave, sessao) {
        try { professor(chave); } catch (err) { return Promise.reject(err); }
        var e = ler();
        GRUPOS.forEach(function (g) {
          var ja = e.tokens.some(function (t) { return t.sessao === sessao && t.grupo === g; });
          if (!ja) e.tokens.push({ sessao: sessao, grupo: g, token: id() });
        });
        gravar(e);
        return Promise.resolve(e.tokens.filter(function (t) { return t.sessao === sessao; })
          .map(function (t) { return { grupo: t.grupo, token: t.token }; }));
      },
      adrPrazo: function (chave, sessao, minutos) {
        try { professor(chave); } catch (err) { return Promise.reject(err); }
        var e = ler();
        e.prazos[sessao] = new Date(Date.now() + minutos * 60000).toISOString();
        gravar(e);
        return Promise.resolve(e.prazos[sessao]);
      },
      adrAgora: function (sessao) {
        return Promise.resolve({ agora: new Date().toISOString(), fim: ler().prazos[sessao] || null });
      },
      adrEntrar: function (sessao, grupo, token, nome) {
        var e = ler();
        var ok = e.tokens.some(function (t) { return t.sessao === sessao && t.grupo === grupo && t.token === token; });
        if (!ok || !nome) return Promise.resolve(false);
        e.presencas = e.presencas || [];
        if (!e.presencas.some(function (p) { return p.sessao === sessao && p.grupo === grupo && p.nome === nome; })) {
          e.presencas.push({ sessao: sessao, grupo: grupo, nome: nome, edicoes: 0 });
        }
        gravar(e);
        return Promise.resolve(true);
      },
      adrIntegrantes: function (sessao, grupo, token) {
        var e = ler();
        var ok = e.tokens.some(function (t) { return t.sessao === sessao && t.grupo === grupo && t.token === token; });
        return Promise.resolve(ok ? (e.presencas || []).filter(function (p) { return p.sessao === sessao && p.grupo === grupo; })
          .map(function (p) { return p.nome; }) : []);
      },
      adrParticipacao: function (chave, sessao) {
        try { professor(chave); } catch (err) { return Promise.reject(err); }
        return Promise.resolve((ler().presencas || []).filter(function (p) { return p.sessao === sessao; }));
      },
      adrTokenOk: function (sessao, grupo, token) {
        return Promise.resolve(ler().tokens.some(function (t) {
          return t.sessao === sessao && t.grupo === grupo && t.token === token;
        }));
      },
      adrSalvar: function (sessao, grupo, token, campo, texto, autor) {
        var e = ler();
        var ok = e.tokens.some(function (t) { return t.sessao === sessao && t.grupo === grupo && t.token === token; });
        if (!ok) return falha('link sem permissão de edição');
        if (CAMPOS.indexOf(campo) === -1) return falha('campo desconhecido');
        if ((texto || '').length > 4000) return falha('texto acima de 4000 caracteres');
        var fim = e.prazos[sessao];
        if (fim && Date.now() > Date.parse(fim)) return falha('prazo encerrado');
        var quando = new Date().toISOString();
        var c = e.campos.filter(function (x) { return x.sessao === sessao && x.grupo === grupo && x.campo === campo; })[0];
        if (!c) { c = { sessao: sessao, grupo: grupo, campo: campo }; e.campos.push(c); }
        c.texto = texto || '';
        c.autor = autor || null;
        String(autor || '').split(';').map(function (n) { return n.trim(); }).filter(Boolean).forEach(function (nome) {
          e.presencas = e.presencas || [];
          var pr = e.presencas.filter(function (p) { return p.sessao === sessao && p.grupo === grupo && p.nome === nome; })[0];
          if (!pr) { pr = { sessao: sessao, grupo: grupo, nome: nome, edicoes: 0 }; e.presencas.push(pr); }
          pr.edicoes += 1;
        });
        c.atualizado_em = quando;
        gravar(e);
        return Promise.resolve(quando);
      },
      adrCampos: function (sessao, grupo) {
        return Promise.resolve(ler().campos.filter(function (c) {
          return c.sessao === sessao && (!grupo || c.grupo === grupo);
        }));
      },
      moedaLiberar: function (chave, sessao, rodada) {
        try { professor(chave); } catch (err) { return Promise.reject(err); }
        if (rodada < 0 || rodada > 20) return falha('rodada fora de 0 a 20');
        var e = ler();
        e.rodadas[sessao] = rodada;
        gravar(e);
        return Promise.resolve(rodada);
      },
      moedaRodada: function (sessao) { return Promise.resolve(ler().rodadas[sessao] || 0); },
      moedaSala: function (sessao) {
        return Promise.resolve(ler().jogadores.filter(function (j) { return j.sessao === sessao; }).length);
      },
      moedaCruzamento: function (sessao, pergunta) {
        // Mesmo cruzamento do SQL, lendo o quiz em memória (inteli-quiz-dados.js).
        var quiz = {};
        try { quiz = JSON.parse(localStorage.getItem('inteli-quiz-demo')) || {}; } catch (err) { quiz = {}; }
        var rodadas = {};
        (quiz.rodadas || []).forEach(function (r) { if (r.sessao === sessao && r.pergunta === pergunta) rodadas[r.id] = r.rodada; });
        var voto = {};
        (quiz.votos || []).forEach(function (v) {
          if (!(v.rodada_id in rodadas)) return;
          var atual = voto[v.participante_id];
          if (!atual || rodadas[v.rodada_id] > atual.rodada) voto[v.participante_id] = { opcao: v.opcao, rodada: rodadas[v.rodada_id] };
        });
        var e = ler();
        var final = {};
        e.jogadores.forEach(function (j) {
          if (j.sessao !== sessao || !j.participante) return;
          var minhas = e.jogadas.filter(function (x) { return x.jogador === j.id; }).sort(function (a, b) { return b.rodada - a.rodada; });
          if (minhas.length) final[j.participante] = minhas[0].saldo;
        });
        var porOpcao = {};
        Object.keys(voto).forEach(function (p) {
          if (!(p in final)) return;
          var o = voto[p].opcao;
          porOpcao[o] = porOpcao[o] || { opcao: o, abaixo: 0, acima: 0 };
          if (final[p] < 100) porOpcao[o].abaixo += 1; else porOpcao[o].acima += 1;
        });
        return Promise.resolve(Object.keys(porOpcao).sort().map(function (k) { return porOpcao[k]; }));
      },
      moedaEntrar: function (sessao, apelido, participante) {
        var e = ler();
        var j = { id: id(), sessao: sessao, apelido: String(apelido).trim().slice(0, 30), participante: participante || null };
        e.jogadores.push(j);
        gravar(e);
        return Promise.resolve(j.id);
      },
      moedaJogar: function (sessao, jogador, rodada) {
        var e = ler();
        var feita = e.jogadas.filter(function (j) { return j.jogador === jogador && j.rodada === rodada; })[0];
        if (feita) return Promise.resolve({ cara: feita.cara, saldo: feita.saldo });
        if (!e.jogadores.some(function (j) { return j.id === jogador && j.sessao === sessao; })) return falha('jogador desconhecido');
        if (rodada < 1 || rodada > (e.rodadas[sessao] || 0)) return falha('rodada não liberada');
        var anterior = 100;
        if (rodada > 1) {
          var a = e.jogadas.filter(function (j) { return j.jogador === jogador && j.rodada === rodada - 1; })[0];
          if (!a) return falha('jogue a rodada anterior antes');
          anterior = a.saldo;
        }
        var cara = Math.random() < 0.5;
        var nova = { sessao: sessao, jogador: jogador, rodada: rodada, cara: cara,
          saldo: Math.round(anterior * (cara ? 1.5 : 0.6) * 100) / 100 };
        e.jogadas.push(nova);
        gravar(e);
        return Promise.resolve({ cara: nova.cara, saldo: nova.saldo });
      },
      moedaJogadas: function (sessao, jogador) {
        return Promise.resolve(ler().jogadas.filter(function (j) {
          return j.sessao === sessao && (!jogador || j.jogador === jogador);
        }));
      },
      moedaZerar: function (chave, sessao) {
        try { professor(chave); } catch (err) { return Promise.reject(err); }
        var e = ler();
        e.jogadas = e.jogadas.filter(function (j) { return j.sessao !== sessao; });
        e.jogadores = e.jogadores.filter(function (j) { return j.sessao !== sessao; });
        e.rodadas[sessao] = 0;
        gravar(e);
        return Promise.resolve();
      },
      ouvir: function (sessao, aoMudarBruto) {
        var aoMudar = juntar(aoMudarBruto);
        ouvintes.push(aoMudar);
        return function () { ouvintes = ouvintes.filter(function (f) { return f !== aoMudar; }); };
      }
    };
  }

  // Sessão da página: ?sessao= sobrescreve o data-sessao do markup (ensaio).
  function sessao(padrao) {
    var p = new URLSearchParams(window.location.search).get('sessao');
    return p || padrao;
  }

  window.IntelIAula02Dados = {
    criar: function () {
      if (demo() || !window.supabase || !window.IntelIQuizConfig) return memoria();
      return supabase();
    },
    demo: demo,
    sessao: sessao,
    CAMPOS: CAMPOS,
    GRUPOS: GRUPOS
  };
})();
