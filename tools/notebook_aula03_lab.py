"""Gera notebooks/aula03.ipynb, os microexercícios da Aula 03 redesenhada (ADR-017).

O aluno escreve as funções; conferir() compara com o valor medido em tools/medidas_aula03_lab.py
e imprime OK ou AINDA NÃO, sem levantar erro, para o notebook rodar inteiro no CI.
Uso: .venv/bin/python tools/notebook_aula03_lab.py
"""
import os

import nbformat as nbf

import medidas_aula03_lab as m

DESTINO = os.path.join(m.RAIZ, "notebooks", "aula03.ipynb")

lac = m.lacuna_bova11()
base, sem = m.retiradas_demo()
bug = m.caca_ao_bug()


def md(t):
    return nbf.v4.new_markdown_cell(t.strip())


def code(t):
    return nbf.v4.new_code_cell(t.strip())


def construir():
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
    c = nb.cells
    c.append(md("""
# Aula 03: do Excel ao Python, com funções, gráficos e testes

Módulo 08 AdmTech, Computação · Semana 5 · Sprint 3 · Prof. José Romualdo

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/aula03.ipynb)

Cinco microexercícios, de 5 a 6 minutos cada, sobre o snapshot do case. Em cada um você escreve o código e roda `conferir(...)`, que responde **OK** ou **AINDA NÃO** com o valor esperado. As operações são as mesmas da Atividade Ponderada 1.
"""))
    c.append(code('''
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DADOS_LOCAL = os.path.join("..", "dados")
DADOS_BRUTOS = "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/"


def ler_csv(nome, **kwargs):
    """Lê um CSV de dados/: do disco quando o repositório está clonado, da URL bruta no Colab."""
    local = os.path.join(DADOS_LOCAL, nome)
    if os.path.exists(local):
        return pd.read_csv(local, **kwargs)
    if os.environ.get("M08_OFFLINE") == "1":
        raise FileNotFoundError("M08_OFFLINE=1 e %s não existe localmente" % local)
    return pd.read_csv(DADOS_BRUTOS + nome, **kwargs)


precos_ajustados = ler_csv("precos_ajustados.csv", index_col="data", parse_dates=["data"])
precos_fechamento = ler_csv("precos_fechamento.csv", index_col="data", parse_dates=["data"])
dolar = ler_csv("ptax_venda.csv", index_col="data", parse_dates=["data"])["valor"].rename("DOLAR")


def conferir(nome, valor, esperado, tolerancia=1e-4):
    """Compara o seu resultado com o esperado e diz OK ou AINDA NÃO, sem parar o notebook."""
    try:
        ok = abs(float(valor) - esperado) <= tolerancia
    except (TypeError, ValueError):
        ok = False
    print("%-28s %s  (seu: %s | esperado: %.4f)" % (nome, "OK" if ok else "AINDA NÃO", valor, esperado))
'''))
    c.append(md("""
## M1. A célula vazia do BOVA11 (5 min)

O BOVA11 ficou sem cotação em 24/10/2025, um pregão normal da B3.

1. Abra `dados/precos_ajustados.csv` no Google Sheets, calcule o retorno do BOVA11 com `=B3/B2-1` arrastado e olhe as linhas de 24/10 e 27/10/2025.
2. Abaixo, refaça a conta do jeito da planilha (célula vazia vira zero) e do jeito da ADR-009 (`ffill` antes do `pct_change`). Compare a volatilidade anual das duas.
"""))
    c.append(code('''
bova = precos_ajustados["BOVA11"]
print(bova.loc["2025-10-21":"2025-10-28"])

# Jeito da planilha: vazio vira zero; a divisão por zero vira erro e sai da conta.
como_planilha = bova.fillna(0)
r_planilha = (como_planilha / como_planilha.shift(1) - 1).replace([np.inf, -np.inf], np.nan)

# Jeito da ADR-009: complete a linha abaixo.
r_certo = None  # bova.ffill().pct_change(fill_method=None)

vol_planilha = r_planilha.dropna().std() * np.sqrt(252)   # com o -100%%, sem o #DIV/0!
vol_certa = None  # r_certo.std() * np.sqrt(252)
conferir("retorno de 24/10 na planilha", r_planilha.loc["2025-10-24"], %.4f)
conferir("volatilidade da planilha", vol_planilha, %.4f)
conferir("volatilidade, jeito ADR-009", vol_certa, %.4f)
''' % (lac["ret_planilha_2410"], lac["vol_planilha"], lac["vol_certa"])))
    c.append(md("""
### Os três testes de unidade do slide

A regra da ADR-009 vira a função `retornos`, e cada teste afirma o resultado de uma série pequena. Rode a célula, depois troque `ffill()` por `fillna(0)` na função e rode de novo: dois testes reprovam.
"""))
    c.append(code('''
def retornos(precos):
    return precos.ffill().pct_change(fill_method=None)


def test_retorno_de_um_pregao_normal():
    r = retornos(pd.Series([100.0, 110.0]))
    assert round(r.iloc[1], 4) == 0.10


def test_lacuna_vale_zero_e_o_dia_seguinte_acumula():
    r = retornos(pd.Series([100.0, None, 110.0]))
    assert r.iloc[1] == 0 and round(r.iloc[2], 4) == 0.10


def test_antes_da_primeira_cotacao_nao_inventa_preco():
    r = retornos(pd.Series([None, 100.0, 110.0]))
    assert pd.isna(r.iloc[1])


for teste in (test_retorno_de_um_pregao_normal, test_lacuna_vale_zero_e_o_dia_seguinte_acumula,
              test_antes_da_primeira_cotacao_nao_inventa_preco):
    try:
        teste()
        print("passou   ", teste.__name__)
    except AssertionError:
        print("REPROVOU ", teste.__name__)
'''))
    c.append(md("""
## M2. A primeira função (5 min)

No Excel, a fórmula de risco de dois ativos seria copiada célula a célula. Em Python ela vira uma função: tem nome, recebe entradas e devolve um resultado.

Escreva `risco_dois_ativos(peso, vol_a, vol_b, rho)`, que devolve a volatilidade da carteira com `peso` no ativo A e `1 - peso` no B:

`sqrt(w² σa² + (1 − w)² σb² + 2 w (1 − w) ρ σa σb)`
"""))
    c.append(code('''
def risco_dois_ativos(peso, vol_a, vol_b, rho):
    """Volatilidade anual de uma carteira de dois ativos."""
    return None  # escreva a conta aqui


conferir("30%, 30%, rho 0,5, 50/50", risco_dois_ativos(0.5, 0.30, 0.30, 0.5), 0.2598)
conferir("rho 1 devolve a média", risco_dois_ativos(0.5, 0.30, 0.20, 1.0), 0.25)
conferir("rho -1 com pesos que zeram", risco_dois_ativos(0.4, 0.30, 0.20, -1.0), 0.0)
'''))
    c.append(md("""
## M3. Uma função chamada cinco vezes (6 min)

Escreva `vol_carteira(retornos, pesos)`, que devolve `sqrt(w' Σ w)` com Σ anualizada. Depois, num laço `for`, tire um ativo de cada vez da carteira abaixo, redistribua o peso dele entre os outros na proporção dos pesos atuais e meça a volatilidade. O laço mede as cinco retiradas em seis linhas de código.

Antes do laço, repare no `std()` do pandas: ele usa `ddof=1`, o desvio padrão amostral, que divide a soma dos quadrados por n - 1. O `ddof=0` divide por n. A célula abaixo mostra a diferença para a BBAS3.

Carteira de demonstração: BBAS3 35%, BBDC4 25%, VALE3 15%, WEGE3 15%, IVVB11 10%, de 01/01/2022 a 31/12/2023.
"""))
    c.append(code('''
carteira = {"BBAS3": 0.35, "BBDC4": 0.25, "VALE3": 0.15, "WEGE3": 0.15, "IVVB11": 0.10}
retornos = precos_ajustados.ffill().pct_change(fill_method=None).loc["2022-01-01":"2023-12-31"]


def vol_carteira(retornos, pesos):
    """Volatilidade anual da carteira: sqrt(w' Σ w), com Σ anualizada."""
    r = retornos[list(pesos)].dropna()
    return None  # monte w, a covariância anualizada e devolva a raiz


print("std() com ddof=1 (padrão):", retornos["BBAS3"].std())
print("std(ddof=0):", retornos["BBAS3"].std(ddof=0))

conferir("carteira inteira", vol_carteira(retornos, carteira), %.4f)

for ativo in carteira:
    resto = {}  # o dicionário sem o ativo, com os pesos redistribuídos
    print(ativo, "->", resto)
''' % base))
    c.append(md("""
## M4. Heatmap e correlação móvel (5 min)

1. Faça o heatmap da matriz de correlação dos retornos dos 15 ativos, com o valor escrito em cada célula, como no vídeo do autoestudo.
2. Junte o Close do BOVA11 e o dólar como o vídeo faz (`pd.concat`, `dropna`) e trace a correlação móvel de 252 pregões **sobre os preços** e **sobre os retornos**. Calcule também o BOVA11 dolarizado, `tabela["BOVA11"] / tabela["DOLAR"]`, e marque um período em que as duas linhas da móvel discordam de sinal.
3. Descubra em que mês a móvel sobre os retornos atinge o menor valor: `movel_retornos.idxmin()` devolve o rótulo do índice, a data, em que está o menor valor.
4. Separe `tabela.pct_change()` em duas metades pela data, `índice < data_meio` e `índice >= data_meio`, e compare a correlação do BOVA11 com o dólar em cada uma.
"""))
    c.append(code('''
matriz = precos_ajustados.ffill().pct_change(fill_method=None).dropna().corr()

fig, eixo = plt.subplots(figsize=(9, 8))
eixo.imshow(matriz, cmap="PRGn_r", vmin=-1, vmax=1)
eixo.set_xticks(range(len(matriz)), matriz.columns, rotation=90)
eixo.set_yticks(range(len(matriz)), matriz.columns)
# escreva os valores nas células com eixo.text(coluna, linha, texto)
plt.show()
'''))
    c.append(code('''
tabela = pd.concat([precos_fechamento["BOVA11"], dolar], axis=1, sort=True).dropna()
movel_precos = tabela["BOVA11"].rolling(252).corr(tabela["DOLAR"])
# movel_retornos = ...
# dolarizado = ...
# mes_minimo = movel_retornos.idxmin()
# data_meio = tabela.index[len(tabela) // 2]
# primeira = tabela.pct_change().loc[tabela.index < data_meio]
# segunda = tabela.pct_change().loc[tabela.index >= data_meio]

fig, eixo = plt.subplots(figsize=(11, 4))
eixo.plot(movel_precos, label="preços")
eixo.axhline(0, linewidth=1)
eixo.legend()
plt.show()
'''))
    c.append(md("""
## M5. Caça ao bug com testes (5 min)

As três funções abaixo dizem calcular a volatilidade anual. Duas têm defeito. Escreva um `assert` para cada propriedade que uma volatilidade anual precisa cumprir e veja quais funções reprovam:

1. a anual dividida pela diária é `sqrt(252)`;
2. a volatilidade anual da PETR4 na série inteira fica entre 10% e 100%.

Na planilha, o mesmo erro passaria como mais um número numa célula.
"""))
    c.append(code('''
def vol_a(r):
    return r.std() * np.sqrt(252)


def vol_b(r):
    return r.std() * np.sqrt(365)


def vol_c(r):
    return r.std() * 252


petr4 = precos_ajustados["PETR4"].ffill().pct_change(fill_method=None).dropna()

for funcao in (vol_a, vol_b, vol_c):
    v = funcao(petr4)
    try:
        # escreva aqui os dois asserts, por exemplo: assert abs(v / petr4.std() - np.sqrt(252)) < 1e-9
        print(funcao.__name__, "%.4f" % v, "passou")
    except AssertionError:
        print(funcao.__name__, "%.4f" % v, "REPROVADA")
'''))
    c.append(md("""
## Para a Atividade Ponderada 1

As operações de M1 a M5 são as da prova: retornos com `ffill` e `pct_change`, `vol_carteira` com pesos, o laço de retiradas, a tabela do vídeo e a correlação móvel. Antes da prova, refaça o notebook de treino da ponderada, que traz o gabarito numérico de cada exercício.
"""))
    return nb


if __name__ == "__main__":
    nbf.write(construir(), DESTINO)
    print("ok:", DESTINO)
