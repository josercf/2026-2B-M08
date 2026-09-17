"""JSON do widget de demonstração do fixture do tema: pregões com cotação por ativo.

Uso: .venv/bin/python tools/dados_widgets_fixture.py
"""
import json
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    fechamento = pd.read_csv(os.path.join(RAIZ, "dados", "precos_fechamento.csv"), index_col="data")
    contagem = fechamento.notna().sum()
    dados = {
        "titulo": "Pregões com cotação de 02/01/2019 a 31/08/2026",
        "unidade": "pregões",
        "itens": [{"rotulo": t, "valor": int(contagem[t])} for t in fechamento.columns],
    }
    destino = os.path.join(RAIZ, "assets", "data", "_fixture-pregoes.json")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("gravado:", os.path.relpath(destino, RAIZ))


if __name__ == "__main__":
    main()
