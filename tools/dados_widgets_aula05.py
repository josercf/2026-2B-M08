"""JSON dos widgets da Aula 05, a partir de tools/medidas_aula05.py.

Uso: .venv/bin/python tools/dados_widgets_aula05.py
Saída: assets/data/aula05-janela-treino.json e assets/data/aula05-sensibilidade.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula05 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")


def _r(valor, casas=4):
    return round(float(valor), casas)


def janela_treino(resultados=None):
    """Pesos, prometido, entregue e drawdown de cada janela deslizante, nas duas carteiras."""
    resultados = resultados if resultados is not None else m.resultados_deslizantes()
    resumo = m.resumo_deslizante(resultados)
    janelas = []
    anteriores = {}
    for r in resultados:
        objetivos = {}
        for objetivo in m.OBJETIVOS:
            o = r[objetivo]
            pesos = o["pesos"]
            objetivos[objetivo] = {
                "pesos": [_r(w) for w in pesos],
                "prometido": _r(o["esperado"]["sharpe"]),
                "entregue": _r(o["realizado"]["sharpe"]),
                "drawdown_max": _r(o["realizado"]["drawdown_max"]),
                "data_fundo": o["realizado"]["data_fundo"].strftime("%d/%m/%Y"),
                "rotatividade": (None if objetivo not in anteriores
                                 else _r(m.rotatividade(anteriores[objetivo], pesos))),
                "drawdown": [_r(x) for x in o["realizado"]["drawdown"]],
            }
            anteriores[objetivo] = pesos
        janelas.append({
            "treino": [r["treino"][0].strftime("%m/%Y"), r["treino"][1].strftime("%m/%Y")],
            "teste": [r["teste"][0].strftime("%m/%Y"), r["teste"][1].strftime("%m/%Y")],
            "objetivos": objetivos,
        })
    return {
        "ativos": resultados[0]["ativos"],
        "principal": m.janela_da_divisao_principal(resultados),
        "rotulos": {"max_sharpe": "Máximo Sharpe", "var_min": "Variância mínima"},
        "resumo": {objetivo: {"abaixo_do_prometido": resumo[objetivo]["abaixo_do_prometido"],
                              "rotatividade_mensal_mediana": _r(resumo[objetivo]["rotatividade_mensal_mediana"])}
                   for objetivo in m.OBJETIVOS},
        "janelas": janelas,
    }


def sensibilidade():
    """Pesos da janela de treino principal com a estimativa original, perturbada e encolhida."""
    s = m.sensibilidade()
    ativos = s["ativos"]
    objetivos = {}
    for objetivo in m.OBJETIVOS:
        o = s[objetivo]
        variantes = ("base", "perturbado", "ledoit_wolf")
        # Só os ativos que passam de 0,5% em alguma das três versões: o resto é
        # zero nas três e só ocuparia linha no gráfico.
        mostrados = [t for t in ativos if max(o[v][t] for v in variantes) > 0.005]
        objetivos[objetivo] = {
            "ativos": mostrados,
            "base": [_r(o["base"][t]) for t in mostrados],
            "perturbado": [_r(o["perturbado"][t]) for t in mostrados],
            "ledoit_wolf": [_r(o["ledoit_wolf"][t]) for t in mostrados],
            "rotatividade": {"base": 0.0,
                             "perturbado": _r(o["rotatividade_perturbado"]),
                             "ledoit_wolf": _r(o["rotatividade_ledoit_wolf"])},
        }
    return {
        "treino": [m.TREINO[0][:4], m.TREINO[1][:4]],
        "perturbacao": m.PERTURBACAO,
        "encolhimento": _r(s["encolhimento"]),
        "erro_padrao_mediano": _r(s["erro_padrao_mediano"]),
        "rotulos": {"max_sharpe": "Máximo Sharpe", "var_min": "Variância mínima"},
        "objetivos": objetivos,
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula05-janela-treino.json", janela_treino()),
                        ("aula05-sensibilidade.json", sensibilidade())):
        caminho = os.path.join(SAIDA, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(caminho), "bytes")


if __name__ == "__main__":
    main()
