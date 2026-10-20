// Extração e agrupamento dos termos da nuvem de palavras por voz (ADR-012),
// feitos no navegador a partir da transcrição que o n8n devolve. Pedido de
// 20/10/2026, depois da primeira aula: a nuvem mostrava muletas e verbos da
// fala ("olha", "legal", "colocou", "assistindo") e partia nomes próprios
// ("gisele" e "bündchen" separados).
//
//   IntelINuvemTermos.extrair(transcricao) -> [{texto, peso}]
//     1. nomes próprios: duas ou mais palavras seguidas com inicial maiúscula
//        (com "de", "da", "do" no meio) viram um termo só;
//     2. termos compostos do vocabulário do módulo ("fronteira eficiente");
//     3. palavras soltas, sem palavras vazias, sem muletas da fala e sem verbos
//        conjugados (passado, gerúndio, infinitivo), salvo as do vocabulário.
//   IntelINuvemTermos.chave(texto)      -> chave que junta plural, acento e caixa
//   IntelINuvemTermos.parecidos(a, b)   -> true quando são o mesmo termo com
//        pequena variação de transcrição (distância de edição curta)
//
// Funções puras: rodam no navegador e no node (tools/tests/test_nuvem_termos.py).
(function (raiz) {
  'use strict';

  var VAZIAS = (
    'a à às ao aos as o os um uma uns umas de da das do dos dum duma em na nas no nos num numa ' +
    'por pela pelas pelo pelos para pra pro pras pros com sem sob sobre entre até após ante desde ' +
    'contra perante e é ou mas nem que se porque pois porém como quando onde quanto enquanto ' +
    'embora caso então logo assim também já ainda só sim não muito muita muitos muitas pouco ' +
    'mais menos bem mal tão tanto tanta tantos tantas todo toda todos todas tudo nada algo ' +
    'alguém ninguém cada outro outra outros outras mesmo mesma mesmos mesmas próprio própria ' +
    'algum alguma alguns algumas qualquer quaisquer certo certa vários várias ' +
    'eu tu ele ela nós vós eles elas você vocês me te lhe nos vos lhes mim ti si comigo conosco ' +
    'meu minha meus minhas teu tua seu sua seus suas nosso nossa nossos nossas dele dela deles ' +
    'delas este esta estes estas esse essa esses essas aquele aquela aqueles aquelas isto isso ' +
    'aquilo aqui ali lá cá aí qual quais quem cujo cuja ' +
    'ser sou és é somos são era eram foi foram fosse sido sendo seja sejam será serão seria ' +
    'estar estou está estamos estão estava estavam esteve estive estiver estando ' +
    'ter tenho tem temos têm tinha tinham teve tive tido tendo haver há havia houve ' +
    'fazer faz fazem fez feito fazendo vai vão vou ir indo iam vem vêm veio vamos ' +
    'pode podem poder posso podemos deve devem dá dar dou deu ' +
    'acho acha achei achou sei sabe saber gente coisa coisas forma jeito vez vezes ' +
    'projeto módulo deste desta neste nesta nisso disso nesse nessa desse dessa ' +
    'zero um dois duas três quatro cinco seis sete oito nove dez cem mil ' +
    'hoje ontem amanhã agora depois antes sempre nunca daqui lado parte ponto'
  ).split(/\s+/);

  // Muletas e comentários da fala que não dizem nada do projeto.
  var MULETAS = (
    'tipo né aí daí então ok okay hum hã ah eh tá pronto bom boa certo exatamente basicamente ' +
    'olha olhe veja cara mano gente legal bacana top show massa bastante super hein cadê ' +
    'nossa caramba poxa beleza tranquilo verdade realmente literalmente meio ' +
    'sensacional incrível ótimo ótima demais parabéns obrigado obrigada valeu ' +
    'menino menina pessoal galera professor professora nome exemplo'
  ).split(/\s+/);

  // Vocabulário do módulo: nunca sai pelo filtro de verbo.
  var VOCABULARIO = (
    'mercado carteira carteiras risco retorno retornos fronteira eficiente markowitz caixa ' +
    'excedente parceiro investimento investimentos ação ações ativo ativos simulador simulação ' +
    'otimizador otimização alocação dados coletor volatilidade correlação covariância sharpe ' +
    'cdi selic ipca liquidez dividendos proventos rentabilidade valor lucro capital tesouro ' +
    'renda bolsa fundo fundos etf preço preços yfinance python notebook api react fastapi llm ' +
    'gestor gestores decisão diversificação benchmark modelo previsão cenário cenários'
  ).split(/\s+/);

  var COMPOSTOS = [
    'fronteira eficiente', 'carteira eficiente', 'carteira de investimentos',
    'excedente de caixa', 'fluxo de caixa', 'taxa livre de risco', 'renda fixa',
    'renda variável', 'mercado financeiro', 'dados de mercado', 'análise de risco',
    'gestão de risco', 'retorno esperado', 'retorno real', 'tolerância a risco',
    'perfil de risco', 'índice de sharpe', 'modelo de markowitz', 'teoria de markowitz',
    'série histórica', 'preço ajustado', 'tesouro direto', 'banco central',
    'bolsa de valores', 'inteligência artificial', 'machine learning', 'aprendizado de máquina',
    'simulação de carteira', 'otimização de carteira', 'alocação de ativos',
    'tomada de decisão', 'diversificação de risco', 'mínima variância', 'máximo sharpe'
  ];

  var SIGLAS = ['b3', 'ia', 'api', 'cdi', 'ipca', 'etf', 'cdb', 'lci', 'lca', 'bcb', 'xp', 'btg', 'llm'];

  function semAcento(texto) {
    return texto.normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function conjunto(lista) {
    var s = {};
    lista.forEach(function (p) { s[semAcento(p.toLowerCase())] = true; });
    return s;
  }

  var S_VAZIAS = conjunto(VAZIAS);
  var S_MULETAS = conjunto(MULETAS);
  var S_VOCAB = conjunto(VOCABULARIO);
  var S_SIGLAS = conjunto(SIGLAS);

  // Verbo conjugado pela terminação: passado (-ou, -ei, -amos), gerúndio
  // (-ando, -endo, -indo), infinitivo (-ar, -er, -ir) e algumas formas do
  // imperfeito e do futuro, já sem acento. Falso positivo raro em substantivo ("lugar") é o
  // custo de tirar da nuvem a maior parte da fala que não é conteúdo.
  // Fora de propósito: "-ia" (latência, estratégia) e "-esse" (interesse), que
  // pegariam substantivos do assunto.
  var VERBO = /(ou|ei|amos|emos|imos|aram|eram|iram|ando|endo|indo|ar|er|ir|ava|avam|arei|erei|irei|ara|era|ira)$/;

  function palavraBoa(palavra) {
    var k = semAcento(palavra);
    if (S_SIGLAS[k]) return true;
    if (k.length < 3) return false;
    if (/^\d+$/.test(k)) return false;
    if (S_VAZIAS[k] || S_MULETAS[k]) return false;
    if (S_VOCAB[k]) return true;
    if (k.length >= 4 && VERBO.test(k)) return false;
    return true;
  }

  // Singular sem acento e em caixa baixa: "Ações" e "ação" têm a mesma chave.
  function chave(texto) {
    return String(texto).normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim()
      .split(' ').map(function (p) {
        var k = semAcento(p);
        if (k.length > 4) {
          if (/oes$|aes$/.test(k)) return k.slice(0, -3) + 'ao';
          if (/ais$/.test(k)) return k.slice(0, -2) + 'l';
          if (/eis$/.test(k)) return k.slice(0, -3) + 'el';
          if (/ns$/.test(k)) return k.slice(0, -2) + 'm';
          if (/[rsz]es$/.test(k)) return k.slice(0, -2);
          if (/[aeiou]s$/.test(k)) return k.slice(0, -1);
        }
        return k;
      }).join(' ');
  }

  function distancia(a, b) {
    var anterior = [];
    for (var j = 0; j <= b.length; j++) anterior.push(j);
    for (var i = 1; i <= a.length; i++) {
      var atual = [i];
      for (j = 1; j <= b.length; j++) {
        atual.push(Math.min(anterior[j] + 1, atual[j - 1] + 1,
          anterior[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)));
      }
      anterior = atual;
    }
    return anterior[b.length];
  }

  // Mesmo termo com variação de transcrição: "bundchen" e "bunchen".
  function parecidos(a, b) {
    var ka = chave(a);
    var kb = chave(b);
    if (ka === kb) return true;
    // Dígito diferente é outro termo ("B3" e "B4", "termo1" e "termo2").
    if (/\d/.test(ka + kb)) return false;
    var menor = Math.min(ka.length, kb.length);
    if (menor < 6) return false;
    var limite = menor >= 10 ? 2 : 1;
    return Math.abs(ka.length - kb.length) <= limite && distancia(ka, kb) <= limite;
  }

  function extrair(transcricao) {
    var texto = String(transcricao || '').normalize('NFC')
      .replace(/\[[^\]]*\]|\([^)]*\)/g, ' ');
    var achados = [];
    var usados = [];

    // 1. Nomes próprios no texto original (antes de baixar a caixa).
    var NOME = /\b(\p{Lu}[\p{L}'-]+(?:\s+(?:de|da|do|dos|das)?\s*\p{Lu}[\p{L}'-]+)+)/gu;
    texto = texto.replace(NOME, function (m) {
      var limpo = m.replace(/\s+/g, ' ').trim();
      // Início de frase seguido de outra maiúscula também casa ("Vou Ver"):
      // só vale como nome se nenhuma palavra for vazia ou muleta.
      var partes = limpo.split(' ').filter(function (p) { return !/^(de|da|do|dos|das)$/.test(p); });
      var ok = partes.every(function (p) {
        var k = semAcento(p.toLowerCase());
        return !S_VAZIAS[k] && !S_MULETAS[k];
      });
      if (!ok) return m;
      achados.push(limpo);
      return ' ';
    });

    var palavras = semAcento(texto.toLowerCase()).replace(/[^\p{L}\p{N}\s-]/gu, ' ')
      .replace(/(^|\s)-+|-+(?=\s|$)/g, ' ').split(/\s+/).filter(Boolean);
    var originais = texto.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, ' ')
      .replace(/(^|\s)-+|-+(?=\s|$)/g, ' ').split(/\s+/).filter(Boolean);
    for (var u = 0; u < palavras.length; u++) usados.push(false);

    // 2. Compostos do vocabulário.
    COMPOSTOS.forEach(function (composto) {
      var alvo = semAcento(composto).split(' ');
      for (var i = 0; i + alvo.length <= palavras.length; i++) {
        var casa = true;
        for (var j = 0; j < alvo.length; j++) {
          if (usados[i + j] || palavras[i + j] !== alvo[j]) { casa = false; break; }
        }
        if (casa) {
          achados.push(composto);
          for (j = 0; j < alvo.length; j++) usados[i + j] = true;
        }
      }
    });

    // 3. Palavras soltas.
    for (var i = 0; i < palavras.length; i++) {
      if (usados[i] || !palavraBoa(palavras[i])) continue;
      var p = originais[i] || palavras[i];
      achados.push(S_SIGLAS[palavras[i]] ? palavras[i].toUpperCase() : p);
    }

    // Soma por chave, mantendo a primeira grafia.
    var porChave = {};
    var ordem = [];
    achados.forEach(function (t) {
      var k = chave(t);
      if (!porChave[k]) { porChave[k] = { texto: t, peso: 0 }; ordem.push(k); }
      porChave[k].peso += 1;
    });
    return ordem.map(function (k) { return porChave[k]; });
  }

  // Nome próprio: duas ou mais palavras, todas com inicial maiúscula fora
  // dos conectivos ("Gisele Bündchen", "Banco do Brasil").
  function ehNome(texto) {
    var partes = String(texto).trim().split(/\s+/).filter(function (p) { return !/^(de|da|do|dos|das)$/.test(p); });
    return partes.length > 1 && partes.every(function (p) { return /^\p{Lu}/u.test(p); });
  }

  var api = { extrair: extrair, ehNome: ehNome, chave: chave, parecidos: parecidos, palavraBoa: palavraBoa };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.IntelINuvemTermos = api;
})(typeof window !== 'undefined' ? window : this);
