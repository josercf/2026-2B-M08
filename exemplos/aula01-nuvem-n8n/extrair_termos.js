// Extração de termos da transcrição para a nuvem de palavras da Aula 01.
//
// Este arquivo é, caractere por caractere, o código do nó Code "Extrair termos"
// do workflow.json ao lado. tools/tests/test_nuvem_workflow.py confere a
// igualdade e roda as funções abaixo com node. Ao alterar um, alterar o outro
// (o teste reprova a divergência).
//
// Entrada no n8n: a resposta da ElevenLabs Speech-to-Text, com a transcrição
// em "text". Saída: { transcricao, termos: [{ texto, peso }] }.

// Palavras sem conteúdo em pt-BR: artigos, preposições, pronomes, verbos de
// ligação, muletas da fala ("tipo", "né", "aí") e números por extenso.
const STOPWORDS = new Set((
  'a à às ao aos as o os um uma uns umas de da das do dos dum duma em na nas no nos num numa ' +
  'por pela pelas pelo pelos para pra pro pras pros com sem sob sobre entre até após ante desde ' +
  'contra perante e é ou mas nem que se porque pois porém como quando onde quanto enquanto ' +
  'embora caso então logo assim também já ainda só sim não muito muita muitos muitas pouco ' +
  'mais menos bem mal tão tanto tanta tantos tantas todo toda todos todas tudo nada algo ' +
  'alguém ninguém cada outro outra outros outras mesmo mesma mesmos mesmas próprio própria ' +
  'eu tu ele ela nós vós eles elas você vocês me te lhe nos vos lhes mim ti si comigo conosco ' +
  'meu minha meus minhas teu tua seu sua seus suas nosso nossa nossos nossas dele dela deles ' +
  'delas este esta estes estas esse essa esses essas aquele aquela aqueles aquelas isto isso ' +
  'aquilo aqui ali lá cá aí qual quais quem cujo cuja ser sou és somos são era eram foi foram ' +
  'fosse sido sendo seja sejam será serão seria estar estou está estamos estão estava estavam ' +
  'esteve estive estiver estando ter tenho tem temos têm tinha tinham teve tive tido tendo ' +
  'haver há havia houve fazer faz fazem fez feito fazendo vai vão vou ir indo iam pode podem ' +
  'poder posso podemos deve devem usar usa usam usando serve servir ajuda ajudar acho acha achamos sei sabe saber gente coisa coisas forma ' +
  'jeito tipo né aí daí então ok okay hum hã ah eh tá pronto bom boa certo exatamente basicamente ' +
  'projeto módulo deste desta neste nesta nisso disso nesse nessa desse dessa ' +
  'zero um dois duas três quatro cinco seis sete oito nove dez cem mil vez vezes'
).split(/\s+/));

// Termos compostos do vocabulário do módulo. Casam antes das palavras soltas e
// saem como um termo só, para "fronteira eficiente" não virar duas palavras.
// A comparação é feita sem acento, então "analise de risco" também casa.
const COMPOSTOS = [
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

// Siglas curtas que a regra de tamanho mínimo descartaria.
const SIGLAS = new Set(['b3', 'ia', 'api', 'cdi', 'ipca', 'etf', 'cdb', 'lci', 'lca', 'bcb', 'xp', 'btg']);

function semAcento(texto) {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '');
}

// Caixa baixa, NFC, só letras, dígitos e espaço. Hífen interno é mantido
// ("pré-processamento"); o resto da pontuação vira espaço.
function normalizar(texto) {
  return String(texto || '')
    .normalize('NFC')
    .toLowerCase()
    .replace(/\[[^\]]*\]|\([^)]*\)/g, ' ')        // eventos de áudio: [risos], (música)
    .replace(/[^\p{L}\p{N}\s-]/gu, ' ')
    .replace(/(^|\s)-+|-+(?=\s|$)/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function palavraValida(palavra) {
  if (STOPWORDS.has(palavra)) return false;
  if (/^\d+$/.test(palavra)) return false;
  if (palavra.length < 3) return SIGLAS.has(palavra);
  return true;
}

// Conta os termos de uma transcrição. Compostos primeiro, depois palavras
// soltas. Um par de palavras de conteúdo vizinhas que aparece duas vezes ou
// mais no mesmo trecho também vira composto ("simulador financeiro" dito duas
// vezes), e as palavras dele deixam de contar sozinhas.
function extrairTermos(textoBruto) {
  const texto = normalizar(textoBruto);
  if (!texto) return [];
  const contagem = new Map();
  const somar = (termo, n) => contagem.set(termo, (contagem.get(termo) || 0) + n);

  const palavras = texto.split(' ');
  const chaves = palavras.map(semAcento);
  const usada = new Array(palavras.length).fill(false);

  for (const composto of COMPOSTOS) {
    const alvo = semAcento(composto).split(' ');
    for (let i = 0; i + alvo.length <= chaves.length; i++) {
      let casa = true;
      for (let j = 0; j < alvo.length; j++) {
        if (usada[i + j] || chaves[i + j] !== alvo[j]) { casa = false; break; }
      }
      if (casa) {
        somar(composto, 1);
        for (let j = 0; j < alvo.length; j++) usada[i + j] = true;
      }
    }
  }

  const pares = new Map();
  for (let i = 0; i + 1 < palavras.length; i++) {
    if (usada[i] || usada[i + 1]) continue;
    if (!palavraValida(palavras[i]) || !palavraValida(palavras[i + 1])) continue;
    if (chaves[i] === chaves[i + 1]) continue;   // "carteira carteira" é repetição
    const par = palavras[i] + ' ' + palavras[i + 1];
    pares.set(par, (pares.get(par) || []).concat(i));
  }
  for (const [par, posicoes] of pares) {
    if (posicoes.length < 2) continue;
    // Só ocorrências que não se sobrepõem, e só marca as palavras como usadas
    // se o par de fato se repetir.
    const livres = [];
    for (const i of posicoes) {
      const ultima = livres[livres.length - 1];
      if (usada[i] || usada[i + 1] || (ultima !== undefined && i <= ultima + 1)) continue;
      livres.push(i);
    }
    if (livres.length < 2) continue;
    for (const i of livres) usada[i] = usada[i + 1] = true;
    somar(par, livres.length);
  }

  for (let i = 0; i < palavras.length; i++) {
    if (!usada[i] && palavraValida(palavras[i])) somar(palavras[i], 1);
  }

  return [...contagem.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'pt-BR'))
    .map(([termo, peso]) => ({ texto: SIGLAS.has(termo) ? termo.toUpperCase() : termo, peso: peso }));
}

// Fora do n8n (node, testes) o arquivo é um módulo CommonJS.
if (typeof module !== 'undefined' && module.exports && typeof $input === 'undefined') {
  module.exports = { extrairTermos, normalizar, STOPWORDS, COMPOSTOS };
}

// Dentro do nó Code do n8n ("Run Once for All Items"): um item por trecho de
// áudio, com a transcrição da ElevenLabs em "text".
if (typeof $input !== 'undefined') {
  return $input.all().map((item) => {
    const transcricao = String((item.json && item.json.text) || '').trim();
    return { json: { transcricao: transcricao, termos: extrairTermos(transcricao) } };
  });
}
