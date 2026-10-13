"""JSON dos widgets da Aula 04, a partir de tools/medidas_aula04.py.

Uso: .venv/bin/python tools/dados_widgets_aula04.py
Saída: assets/data/aula04-nuvem.json e assets/data/aula04-triangulo.json

Os dois JSON declaram a janela da amostra, lida de tools/retornos.py: o
tratamento de ausência único do módulo (ADR-009), na janela comum dos 15 ativos.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula04 as m  # noqa: E402
import retornos  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
PASSOS_NUVEM = (10, 100, 1_000, 10_000)


def _num(valor, casas=2):
    return ("%.*f" % (casas, valor)).replace(".", ",")


def _pct(valor):
    return _num(valor * 100) + "%"


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _ponto(carteira):
    return {"vol": round(carteira["volatilidade"], 4), "ret": round(carteira["retorno"], 4),
            "sharpe": round(carteira["sharpe"], 4)}


def janela():
    """Início, fim e número de retornos da janela comum (ADR-009)."""
    comum = retornos.retornos_janela_comum()
    if not comum.equals(m.retornos()):
        raise RuntimeError("medidas_aula04 saiu da janela comum da ADR-009")
    return {"inicio": comum.index[0].strftime("%d/%m/%Y"),
            "fim": comum.index[-1].strftime("%d/%m/%Y"), "retornos": len(comum)}


def nuvem():
    n = m.nuvem()
    f = m.fronteira()
    mv = m.carteira(m.variancia_minima())
    ms = m.carteira(m.maximo_sharpe())
    progressivo = m.melhor_por_sorteios()
    leituras = {}
    for passo in PASSOS_NUVEM:
        leituras[str(passo)] = ("Melhor Sharpe entre %s sorteadas: %s. A carteira ótima chega a %s."
                                % (_milhar(passo), _num(progressivo[passo]), _num(ms["sharpe"])))
    return {
        "janela": janela(),
        "rf": round(m.taxa_livre_de_risco(), 4),
        "vol": [round(float(x), 4) for x in n["volatilidade"]],
        "ret": [round(float(x), 4) for x in n["retorno"]],
        "sharpe": [round(float(x), 4) for x in n["sharpe"]],
        "passos": list(PASSOS_NUVEM),
        "leituras": leituras,
        "fronteira": [[round(float(v), 4), round(float(r), 4)]
                      for v, r in zip(f["volatilidade"], f["retorno"])],
        "variancia_minima": _ponto(mv),
        "maximo_sharpe": _ponto(ms),
        "leitura_otimas": ("Variância mínima: volatilidade de %s. Máximo Sharpe: %s, retorno de %s, peso em só %s ativos."
                           % (_pct(mv["volatilidade"]), _num(ms["sharpe"]),
                              _pct(ms["retorno"]), ms["ativos"])),
    }


def triangulo():
    mu, cov = m.trio()
    _, final = m.caminho_slsqp_trio()
    ret, vol, sharpe = m.metricas(final, mu, cov)
    return {
        "janela": janela(),
        "tickers": list(m.TRIO),
        "mu": [round(float(x), 6) for x in mu],
        "cov": [[round(float(x), 6) for x in linha] for linha in cov],
        "rf": round(m.taxa_livre_de_risco(), 6),
        "otima": {"pesos": [round(float(w), 4) for w in final],
                  "ret": round(ret, 4), "vol": round(vol, 4), "sharpe": round(sharpe, 4)},
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula04-nuvem.json", nuvem()), ("aula04-triangulo.json", triangulo())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
