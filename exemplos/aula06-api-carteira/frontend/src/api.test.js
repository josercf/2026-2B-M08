// Testes do cliente da API, sem navegador e sem dependência: node --test src/
// O fetch é trocado por uma função falsa, então nenhum servidor precisa subir.
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { montarPedido, otimizar, traduzirErro } from './api.js';

function respostaFalsa(status, corpo) {
  return async () => ({
    ok: status >= 200 && status < 300,
    status,
    json: async () => corpo,
    text: async () => JSON.stringify(corpo),
  });
}

test('montarPedido normaliza tickers digitados pelo gestor', () => {
  assert.deepEqual(montarPedido(' petr4, vale3;itub4 ', '2019-01-01', '2026-08-31'), {
    tickers: ['PETR4', 'VALE3', 'ITUB4'],
    inicio: '2019-01-01',
    fim: '2026-08-31',
  });
});

test('taxa digitada em porcentagem vai para a API como fração', () => {
  assert.equal(montarPedido('PETR4 VALE3', '2019-01-01', '2026-08-31', '10,5').taxa_livre_risco, 0.105);
  assert.equal('taxa_livre_risco' in montarPedido('PETR4 VALE3', '2019-01-01', '2026-08-31', ''), false);
});

test('404 vira mensagem com o ticker que faltou', () => {
  const texto = traduzirErro(404, 'Ticker fora da base: XPTO3');
  assert.match(texto, /não está na base/);
  assert.match(texto, /XPTO3/);
});

test('422 vira instrução para corrigir o pedido, sem jargão de HTTP', () => {
  const texto = traduzirErro(422, [{ loc: ['body', 'tickers'] }]);
  assert.match(texto, /ao menos dois ativos/);
  assert.doesNotMatch(texto, /422|HTTP|JSON/);
});

test('status desconhecido cai na mensagem genérica', () => {
  assert.match(traduzirErro(500, null), /Tente de novo/);
});

test('otimizar devolve o JSON quando a API responde 200', async () => {
  const dados = await otimizar({ tickers: ['PETR4', 'VALE3'] }, respostaFalsa(200, { pregoes: 1906 }));
  assert.equal(dados.pregoes, 1906);
});

test('otimizar lança erro traduzido e guarda o status quando a API responde 404', async () => {
  await assert.rejects(
    otimizar({ tickers: ['PETR4', 'XPTO3'] }, respostaFalsa(404, { detail: 'Ticker fora da base: XPTO3' })),
    (erro) => erro.status === 404 && /XPTO3/.test(erro.message),
  );
});

test('servidor desligado vira mensagem com o endereço da API', async () => {
  const semServidor = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(otimizar({ tickers: [] }, semServidor), /Ele está rodando/);
});
