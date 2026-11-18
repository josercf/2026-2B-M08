"""Confere se o computador da dupla consegue rodar o kit.

Uso:  python checar_ambiente.py

Confere Python 3.10 ou mais novo, NumPy, pandas, matplotlib e pytest, e a
presença dos dados da aula. Imprime o que falta e o comando para instalar.

Confere também o SciPy, que só o turno 6 (depois do encontro) usa. Sem o
SciPy, os turnos 1 a 5 rodam: a resposta continua sendo AMBIENTE: OK, com o
aviso do que instalar antes do turno 6.
"""
import importlib
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
PACOTES = ["numpy", "pandas", "matplotlib", "pytest"]
PACOTES_TURNO6 = ["scipy"]
PYTHON_MINIMO = (3, 10)


def checar():
    """Devolve as linhas do relatório, o que falta e o que falta só para o turno 6."""
    linhas, faltas, faltas_turno6 = [], [], []
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
    executavel = os.path.basename(sys.executable) or "python"
    for pacote in PACOTES_TURNO6:
        try:
            modulo = importlib.import_module(pacote)
            linhas.append("OK     %s %s" % (pacote, getattr(modulo, "__version__", "")))
        except Exception:
            linhas.append("FALTA  %s (usado só no turno 6)" % pacote)
            faltas_turno6.append("Antes do turno 6, instale o pacote que falta com:  "
                                 "%s -m pip install %s" % (executavel, pacote))
    for nome in ("precos.csv", "rf.txt"):
        if os.path.exists(os.path.join(PASTA, "dados", nome)):
            linhas.append("OK     dados/%s" % nome)
        else:
            linhas.append("FALTA  dados/%s" % nome)
            faltas.append("Copie de novo a pasta dados/ do kit: o arquivo %s não está nela." % nome)
    return linhas, faltas, faltas_turno6


def main():
    linhas, faltas, faltas_turno6 = checar()
    for linha in linhas:
        print(linha)
    if faltas:
        print("AMBIENTE: AINDA NÃO")
        for falta in faltas + faltas_turno6:
            print("  - " + falta)
        return 1
    if faltas_turno6:
        print("AMBIENTE: OK para os turnos 1 a 5")
        for falta in faltas_turno6:
            print("  - " + falta)
        return 0
    print("AMBIENTE: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
