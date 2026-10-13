"""JSON dos widgets da Aula 03, a partir de tools/medidas_aula03.py.

Uso: .venv/bin/python tools/dados_widgets_aula03.py
Saída: assets/data/aula03-heatmap.json e assets/data/aula03-correlacao-peso.json

Nenhum número é digitado aqui: a matriz, as volatilidades, os retornos, as
correlações e os pesos de menor risco vêm das funções de medidas_aula03, e as
frases de leitura são montadas a partir desses mesmos valores.

Tratamento de ausência da ADR-009, via tools/retornos.py: o heatmap mostra a
matriz da cesta na janela comum dos 15 ativos (1.423 retornos desde
14/12/2020), e cada par do widget de peso é medido na janela comum dos dois
ativos, com início e número de retornos escritos na leitura.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula03 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def _data_br(iso):
    return "/".join(reversed(iso.split("-")))


def heatmap():
    """Matriz de correlação da cesta na janela comum, com os pregões de cada par."""
    rets = m.retornos_cesta()
    corr = m.matriz_correlacao()
    presentes = rets.notna().astype(int)
    comuns = presentes.T @ presentes
    tickers = list(corr.columns)
    return {
        "tickers": tickers,
        "correlacao": [[round(float(corr.loc[a, b]), 4) for b in tickers] for a in tickers],
        "pregoes": [[int(comuns.loc[a, b]) for b in tickers] for a in tickers],
        # Só a instrução: o par mais correlacionado é a resposta da pergunta
        # disparada do Bloco 2 e aparece no slide seguinte.
        "leitura": "Passe o cursor sobre uma célula.",
    }


def correlacao_peso():
    """Volatilidade, retorno e correlação medidos de cada par do widget."""
    pares = []
    for a, b in m.PARES_WIDGET:
        par = m.estatisticas_par(a, b)
        pares.append({
            "a": a, "b": b,
            "vol_a": round(par["vol_a"], 4), "vol_b": round(par["vol_b"], 4),
            "ret_a": round(par["ret_a"], 4), "ret_b": round(par["ret_b"], 4),
            "rho": round(par["rho"], 4),
            "pregoes": par["pregoes"],
            "inicio": par["inicio"],
            "peso_minimo": round(par["peso_minimo"], 4),
            "risco_minimo": round(par["risco_minimo"], 4),
            "medido": ("Medido em %s pregões desde %s: correlação %s; o menor risco, %s, sai com %s em %s."
                       % (_milhar(par["pregoes"]), _data_br(par["inicio"]), m.dec(par["rho"]),
                          m.pct(par["risco_minimo"]), m.pct(par["peso_minimo"]), a)),
        })
    return {"pares": pares}


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula03-heatmap.json", heatmap()),
                        ("aula03-correlacao-peso.json", correlacao_peso())):
        caminho = os.path.join(SAIDA, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(caminho), "bytes")


if __name__ == "__main__":
    main()
