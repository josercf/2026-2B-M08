"""Confere se o computador da dupla consegue rodar o kit.

Uso:  python checar_ambiente.py

Confere Python 3.10 ou mais novo, NumPy, pandas, matplotlib e pytest, e a
presença dos dados da aula. Imprime o que falta e o comando para instalar.
"""
import importlib
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
PACOTES = ["numpy", "pandas", "matplotlib", "pytest"]
PYTHON_MINIMO = (3, 10)


def checar():
    """Devolve a lista de linhas do relatório e a lista do que falta."""
    linhas, faltas = [], []
    versao = "%d.%d.%d" % tuple(sys.version_info[:3])
    if tuple(sys.version_info[:2]) >= PYTHON_MINIMO:
        linhas.append("OK     Python %s" % versao)
    else:
        linhas.append("FALTA  Python %s: o kit pede Python 3.10 ou mais novo" % versao)
        faltas.append("Instale o Python 3.10 ou mais novo (https://www.python.org/downloads/) "
                      "e rode este arquivo com ele.")
    ausentes = []
    for pacote in PACOTES:
        try:
            modulo = importlib.import_module(pacote)
            linhas.append("OK     %s %s" % (pacote, getattr(modulo, "__version__", "")))
        except Exception:
            linhas.append("FALTA  %s" % pacote)
            ausentes.append(pacote)
    if ausentes:
        faltas.append("Instale os pacotes que faltam com:  %s -m pip install %s"
                      % (os.path.basename(sys.executable) or "python", " ".join(ausentes)))
    for nome in ("precos.csv", "rf.txt"):
        if os.path.exists(os.path.join(PASTA, "dados", nome)):
            linhas.append("OK     dados/%s" % nome)
        else:
            linhas.append("FALTA  dados/%s" % nome)
            faltas.append("Copie de novo a pasta dados/ do kit: o arquivo %s não está nela." % nome)
    return linhas, faltas


def main():
    linhas, faltas = checar()
    for linha in linhas:
        print(linha)
    if faltas:
        print("AMBIENTE: AINDA NÃO")
        for falta in faltas:
            print("  - " + falta)
        return 1
    print("AMBIENTE: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
