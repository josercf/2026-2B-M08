// Cliente da API do simulador. Tudo que fala HTTP mora aqui, fora dos
// componentes: o componente pede "otimizar" e recebe dados ou um erro já
// traduzido para o gestor, sem saber de status, JSON ou URL.
//
// Nenhuma chave aqui. A chave do LLM vive no backend, em variável de ambiente;
// qualquer coisa que o navegador recebe, o usuário consegue ler.

const ENV = (typeof import.meta !== 'undefined' && import.meta.env) || {};
export const API_URL = ENV.VITE_API_URL || 'http://127.0.0.1:8000';

// Mensagem para quem decide, por código de status do contrato da API.
const MENSAGENS = {
  404: 'Algum ativo pedido não está na base de dados. Confira o código do ticker.',
  422: 'O pedido não passou na validação. Escolha ao menos dois ativos distintos e um período com início antes do fim.',
  502: 'O serviço de interpretação não respondeu. Os números da carteira continuam válidos.',
  503: 'A interpretação está indisponível neste servidor. Os números da carteira continuam válidos.',
};

export function traduzirErro(status, detalhe) {
  const base = MENSAGENS[status] || 'O servidor não conseguiu calcular agora. Tente de novo em instantes.';
  // O detalhe do 404 diz qual ticker faltou: vale mostrar ao gestor.
  if (status === 404 && typeof detalhe === 'string' && detalhe.includes(':')) {
    return base + ' (' + detalhe.split(':').pop().trim() + ')';
  }
  return base;
}

// Taxa livre de risco em % ao ano, como o gestor digita ("10,5"). Vazia, o
// backend usa o CDI acumulado do período.
export function montarPedido(textoTickers, inicio, fim, textoTaxa = '') {
  const tickers = textoTickers
    .split(/[\s,;]+/)
    .map((t) => t.trim().toUpperCase())
    .filter(Boolean);
  const pedido = { tickers, inicio, fim };
  const taxa = parseFloat(String(textoTaxa).replace(',', '.'));
  if (!Number.isNaN(taxa)) pedido.taxa_livre_risco = taxa / 100;
  return pedido;
}

async function postar(rota, pedido, comoTexto = false, buscar = fetch) {
  let resposta;
  try {
    resposta = await buscar(API_URL + rota, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pedido),
    });
  } catch (erro) {
    // fetch só rejeita sem resposta: servidor desligado ou CORS bloqueado.
    throw new Error('Não foi possível falar com o servidor em ' + API_URL + '. Ele está rodando?');
  }
  if (!resposta.ok) {
    let detalhe = null;
    try {
      detalhe = (await resposta.json()).detail;
    } catch (_) {
      // corpo sem JSON: fica a mensagem genérica do status
    }
    const erro = new Error(traduzirErro(resposta.status, detalhe));
    erro.status = resposta.status;
    throw erro;
  }
  return comoTexto ? resposta.text() : resposta.json();
}

export const otimizar = (pedido, buscar) => postar('/carteiras/otimizar', pedido, false, buscar);
export const interpretar = (pedido, buscar) => postar('/carteiras/interpretar', pedido, false, buscar);
export const exportarCsv = (pedido, buscar) => postar('/carteiras/exportar', pedido, true, buscar);
