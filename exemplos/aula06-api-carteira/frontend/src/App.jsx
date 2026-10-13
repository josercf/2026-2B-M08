// Tela do gestor: formulário de tickers e período, as duas carteiras ótimas, a
// fronteira e a interpretação conferida número a número. Todo cálculo acontece
// no servidor; este componente só guarda estado, chama a API e desenha.
import { useState } from 'react';

import { exportarCsv, interpretar, montarPedido, otimizar } from './api.js';
import Fronteira from './Fronteira.jsx';

const pct = (x) => (100 * x).toFixed(2).replace('.', ',') + '%';

function TabelaCarteiras({ resultado }) {
  return (
    <table className="tabela">
      <thead>
        <tr><th>Ativo</th><th>Variância mínima</th><th>Máximo Sharpe</th></tr>
      </thead>
      <tbody>
        {resultado.tickers.map((t) => (
          <tr key={t}>
            <td>{t}</td>
            <td>{pct(resultado.variancia_minima.pesos[t])}</td>
            <td>{pct(resultado.maximo_sharpe.pesos[t])}</td>
          </tr>
        ))}
        <tr className="destaque">
          <td>Retorno anual</td>
          <td>{pct(resultado.variancia_minima.retorno)}</td>
          <td>{pct(resultado.maximo_sharpe.retorno)}</td>
        </tr>
        <tr className="destaque">
          <td>Volatilidade anual</td>
          <td>{pct(resultado.variancia_minima.volatilidade)}</td>
          <td>{pct(resultado.maximo_sharpe.volatilidade)}</td>
        </tr>
      </tbody>
    </table>
  );
}

function Interpretacao({ dados }) {
  const naoConferem = dados.verificacao.filter((v) => !v.confere);
  return (
    <section className="cartao">
      <h2>Interpretação</h2>
      <p className="nota">Modelo: {dados.modelo}. Texto gerado por LLM, conferido contra os números da API.</p>
      <p>{dados.texto}</p>
      <p className={naoConferem.length ? 'alerta' : 'nota'}>
        {dados.verificacao.length - naoConferem.length} de {dados.verificacao.length} números conferem.
        {naoConferem.length > 0 && ' Não aparecem no resultado: ' + naoConferem.map((v) => v.trecho).join(', ') + '.'}
      </p>
    </section>
  );
}

export default function App() {
  const [tickers, setTickers] = useState('PETR4, VALE3, ITUB4, WEGE3, IVVB11');
  const [inicio, setInicio] = useState('2019-01-01');
  const [fim, setFim] = useState('2026-08-31');
  const [taxa, setTaxa] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [textoIA, setTextoIA] = useState(null);

  const pedido = () => montarPedido(tickers, inicio, fim, taxa);

  async function aoOtimizar(evento) {
    evento.preventDefault();
    setCarregando(true);
    setErro(null);
    setTextoIA(null);
    try {
      setResultado(await otimizar(pedido()));
    } catch (e) {
      setResultado(null);
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }

  async function aoInterpretar() {
    setCarregando(true);
    setErro(null);
    try {
      setTextoIA(await interpretar(pedido()));
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }

  async function aoExportar() {
    try {
      const csv = await exportarCsv(pedido());
      const link = document.createElement('a');
      link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
      link.download = 'carteiras.csv';
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (e) {
      setErro(e.message);
    }
  }

  return (
    <main className="pagina">
      <header>
        <h1>Simulador de carteira eficiente</h1>
        <p className="nota">Fronteira de Markowitz sobre o snapshot de dados/, calculada pela API.</p>
      </header>

      <form className="cartao formulario" onSubmit={aoOtimizar}>
        <label>
          Tickers
          <input value={tickers} onChange={(e) => setTickers(e.target.value)} />
        </label>
        <label>
          Início
          <input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} />
        </label>
        <label>
          Fim
          <input type="date" value={fim} onChange={(e) => setFim(e.target.value)} />
        </label>
        <label>
          Taxa livre de risco (% a.a.)
          <input value={taxa} placeholder="CDI do período" onChange={(e) => setTaxa(e.target.value)} />
        </label>
        <button type="submit" disabled={carregando}>{carregando ? 'Calculando...' : 'Otimizar'}</button>
      </form>

      {erro && <p className="cartao alerta" role="alert">{erro}</p>}

      {resultado && (
        <>
          <section className="cartao">
            <h2>Fronteira eficiente</h2>
            <Fronteira resultado={resultado} />
            <p className="nota">
              {resultado.pregoes} retornos diários; CDI de {pct(resultado.taxa_livre_risco)} ao ano como taxa livre de risco.
            </p>
          </section>
          <section className="cartao">
            <h2>Carteiras ótimas</h2>
            <TabelaCarteiras resultado={resultado} />
            <div className="acoes">
              <button type="button" onClick={aoInterpretar} disabled={carregando}>Interpretar com LLM</button>
              <button type="button" onClick={aoExportar}>Exportar CSV</button>
            </div>
          </section>
        </>
      )}

      {textoIA && <Interpretacao dados={textoIA} />}
    </main>
  );
}
