"""Empacota o kit do simulador da Aula 04 em materiais/aula04-simulador.zip.

Uso:
    .venv/bin/python tools/empacotar_kit_aula04.py           grava o zip
    .venv/bin/python tools/empacotar_kit_aula04.py --check   confere se o zip está em dia

O pacote é determinístico: arquivos em ordem alfabética, data fixa, permissão
fixa, sem __pycache__ nem arquivo de sistema. Rodar duas vezes na mesma máquina
gera o mesmo arquivo.
"""
import os
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(RAIZ, "exemplos", "aula04-simulador")
ZIP = os.path.join(RAIZ, "materiais", "aula04-simulador.zip")
PREFIXO = "aula04-simulador"
DATA_FIXA = (2026, 11, 18, 0, 0, 0)
PASTAS_FORA = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".git", ".venv"}
ARQUIVOS_FORA = {".DS_Store", "Thumbs.db", "nuvem.png"}


def arquivos_do_kit(pasta=KIT):
    """Caminhos relativos dos arquivos que entram no pacote, com barra normal, em ordem."""
    achados = []
    for atual, pastas, arquivos in os.walk(pasta):
        pastas[:] = sorted(p for p in pastas if p not in PASTAS_FORA)
        for nome in arquivos:
            if nome in ARQUIVOS_FORA or nome.endswith(".pyc"):
                continue
            relativo = os.path.relpath(os.path.join(atual, nome), pasta)
            achados.append(relativo.replace(os.sep, "/"))
    return sorted(achados)


def conteudo_esperado(pasta=KIT):
    """Dicionário nome no zip -> bytes, a partir da pasta do kit."""
    esperado = {}
    for relativo in arquivos_do_kit(pasta):
        with open(os.path.join(pasta, *relativo.split("/")), "rb") as fh:
            esperado["%s/%s" % (PREFIXO, relativo)] = fh.read()
    return esperado


def conteudo_do_zip(caminho=ZIP):
    """Dicionário nome no zip -> bytes, lido do pacote gravado."""
    with zipfile.ZipFile(caminho) as pacote:
        return {nome: pacote.read(nome) for nome in pacote.namelist()}


def empacotar(pasta=KIT, destino=ZIP):
    """Grava o zip e devolve a lista de nomes, na ordem em que entraram."""
    esperado = conteudo_esperado(pasta)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as pacote:
        for nome in sorted(esperado):
            info = zipfile.ZipInfo(nome, date_time=DATA_FIXA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            pacote.writestr(info, esperado[nome], compresslevel=9)
    return sorted(esperado)


def em_dia(pasta=KIT, destino=ZIP):
    """Verdadeiro quando o zip existe e tem exatamente os arquivos e os bytes da pasta."""
    return os.path.exists(destino) and conteudo_do_zip(destino) == conteudo_esperado(pasta)


def main(argumentos):
    if argumentos == ["--check"]:
        if em_dia():
            print("materiais/aula04-simulador.zip está em dia")
            return 0
        print("materiais/aula04-simulador.zip está desatualizado: rode "
              "tools/empacotar_kit_aula04.py")
        return 1
    nomes = empacotar()
    print("materiais/aula04-simulador.zip gravado com %d arquivos" % len(nomes))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
