// Gráfico da fronteira em SVG puro: volatilidade no eixo x, retorno no eixo y,
// os ativos isolados e as duas carteiras ótimas marcadas. Sem biblioteca de
// gráfico, para o grupo ver que um gráfico é só a conversão de número em pixel.
const L = 640;
const A = 360;
const M = { esq: 60, dir: 20, topo: 16, base: 44 };

const pct = (x) => (100 * x).toFixed(0) + '%';

export default function Fronteira({ resultado }) {
  const pontos = [
    ...resultado.fronteira.map(([v, r]) => ({ v, r })),
    ...resultado.ativos.map((a) => ({ v: a.volatilidade, r: a.retorno })),
  ];
  const vMax = Math.max(...pontos.map((p) => p.v)) * 1.08;
  const rMin = Math.min(0, ...pontos.map((p) => p.r));
  const rMax = Math.max(...pontos.map((p) => p.r)) * 1.08;
  const x = (v) => M.esq + (v / vMax) * (L - M.esq - M.dir);
  const y = (r) => A - M.base - ((r - rMin) / (rMax - rMin)) * (A - M.topo - M.base);
  const curva = resultado.fronteira.map(([v, r]) => x(v) + ',' + y(r)).join(' ');
  const marcas = [0.1, 0.2, 0.3, 0.4].filter((t) => t < vMax);

  return (
    <svg className="fronteira" viewBox={`0 0 ${L} ${A}`} role="img"
         aria-label="Fronteira eficiente com os ativos e as duas carteiras ótimas">
      <line className="eixo" x1={M.esq} y1={A - M.base} x2={L - M.dir} y2={A - M.base} />
      <line className="eixo" x1={M.esq} y1={M.topo} x2={M.esq} y2={A - M.base} />
      {marcas.map((t) => (
        <text key={t} className="rotulo" x={x(t)} y={A - M.base + 20} textAnchor="middle">{pct(t)}</text>
      ))}
      <text className="rotulo" x={(L + M.esq) / 2} y={A - 6} textAnchor="middle">volatilidade anual</text>
      <text className="rotulo" x={M.esq + 8} y={M.topo + 10}>retorno anual</text>
      <polyline className="curva" points={curva} />
      {resultado.ativos.map((a) => (
        <g key={a.ticker}>
          <circle className="ativo" cx={x(a.volatilidade)} cy={y(a.retorno)} r={5} />
          <text className="rotulo" x={x(a.volatilidade) + 8} y={y(a.retorno) + 4}>{a.ticker}</text>
        </g>
      ))}
      {/* Variância mínima rotulada abaixo e Máximo Sharpe acima, os dois à esquerda
          do ponto, onde a curva da fronteira não passa. */}
      {[['variancia_minima', 'Variância mínima', -12, 26, 'end'],
        ['maximo_sharpe', 'Máximo Sharpe', -12, -16, 'end']].map(([chave, nome, dx, dy, ancora]) => (
        <g key={chave}>
          <circle className="otima" cx={x(resultado[chave].volatilidade)} cy={y(resultado[chave].retorno)} r={8} />
          <text className="rotulo forte" x={x(resultado[chave].volatilidade) + dx}
                y={y(resultado[chave].retorno) + dy} textAnchor={ancora}>{nome}</text>
        </g>
      ))}
    </svg>
  );
}
