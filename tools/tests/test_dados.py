"""Trava o contrato e os fatos medidos dos dados do case em dados/."""
import csv
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "dados")
TICKERS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "EGIE3",
           "SUZB3", "RENT3", "B3SA3", "MGLU3", "BOVA11", "IVVB11", "GOLD11"]
PRECOS = ["precos_ajustados.csv", "precos_fechamento.csv"]
# arquivo: (linhas, primeira data, primeiro valor, última data, último valor)
SERIES_BCB = {
    "cdi_diario.csv": (1926, "2019-01-02", 0.02462, "2026-08-31", 0.05166),
    "selic_meta.csv": (2800, "2019-01-01", 6.5, "2026-08-31", 14.0),
    "ipca_mensal.csv": (92, "2019-01-01", 0.32, "2026-08-01", -0.32),
    "ptax_venda.csv": (1926, "2019-01-02", 3.8595, "2026-08-31", 5.1816),
}


def _ler(nome):
    with open(os.path.join(DADOS, nome), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("arquivo", PRECOS)
def test_precos_seguem_o_contrato_e_a_janela(arquivo):
    linhas = _ler(arquivo)
    assert list(linhas[0].keys()) == ["data"] + TICKERS
    datas = [linha["data"] for linha in linhas]
    assert len(datas) == 1908
    assert (datas[0], datas[-1]) == ("2019-01-02", "2026-08-31")
    assert datas == sorted(set(datas))


def test_as_duas_tabelas_de_preco_tem_as_mesmas_datas():
    assert [l["data"] for l in _ler(PRECOS[0])] == [l["data"] for l in _ler(PRECOS[1])]


@pytest.mark.parametrize("arquivo", PRECOS)
def test_todo_preco_presente_e_positivo(arquivo):
    for linha in _ler(arquivo):
        for ticker in TICKERS:
            if linha[ticker] != "":
                assert float(linha[ticker]) > 0, (arquivo, linha["data"], ticker)


def test_ausencias_reais_do_provedor():
    linhas = _ler("precos_fechamento.csv")
    vazios = {t: [l["data"] for l in linhas if l[t] == ""] for t in TICKERS}
    assert {t: len(v) for t, v in vazios.items() if v} == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}
    assert vazios["BOVA11"] == ["2025-10-24"]
    assert vazios["IVVB11"] == ["2025-10-24"]
    assert vazios["GOLD11"][-1] == "2025-10-24"
    assert vazios["GOLD11"][-2] < "2020-12-11"
    assert next(l["data"] for l in linhas if l["GOLD11"] != "") == "2020-12-11"


def test_ausencia_e_igual_nas_duas_tabelas():
    ajustado, fechamento = _ler(PRECOS[0]), _ler(PRECOS[1])
    for ticker in TICKERS:
        assert ([l["data"] for l in ajustado if l[ticker] == ""]
                == [l["data"] for l in fechamento if l[ticker] == ""]), ticker


def test_adj_close_da_petr4_desconta_proventos():
    ajustado, fechamento = _ler(PRECOS[0])[0], _ler(PRECOS[1])[0]
    assert round(float(ajustado["PETR4"]) / float(fechamento["PETR4"]), 4) == 0.2613
    for etf in ("BOVA11", "IVVB11"):
        assert float(ajustado[etf]) == pytest.approx(float(fechamento[etf]), rel=1e-9)


def test_eventos_de_desdobramento_do_periodo():
    linhas = _ler("eventos_desdobramento.csv")
    assert list(linhas[0].keys()) == ["ticker", "data", "fator"]
    eventos = {(l["ticker"], l["data"]): float(l["fator"]) for l in linhas}
    assert len(eventos) == 15
    assert eventos[("B3SA3", "2021-05-17")] == 3.0
    assert eventos[("WEGE3", "2021-04-28")] == 2.0
    assert eventos[("BBAS3", "2024-04-16")] == 2.0
    assert eventos[("MGLU3", "2024-05-27")] == pytest.approx(0.1)


def test_classificacao_de_eventos_por_fator_bate_com_o_readme():
    """Classifica cada evento de eventos_desdobramento.csv pela mesma regra de
    fator usada em dados/README.md (seção 6: fator menor que 1 é grupamento,
    fator inteiro maior que 1 é desdobramento, fator fracionário maior que 1 é
    bonificação em ações) e trava a contagem por classificação e o exemplo de
    bonificação citado no README.
    """
    linhas = _ler("eventos_desdobramento.csv")
    contagem = {"grupamento": 0, "desdobramento": 0, "bonificação": 0}
    for linha in linhas:
        fator = float(linha["fator"])
        if fator < 1:
            contagem["grupamento"] += 1
        elif fator.is_integer():
            contagem["desdobramento"] += 1
        else:
            contagem["bonificação"] += 1
    assert contagem == {"grupamento": 1, "desdobramento": 5, "bonificação": 9}
    exemplo = next(l for l in linhas if (l["ticker"], l["data"]) == ("BBDC4", "2019-04-01"))
    assert float(exemplo["fator"]) == pytest.approx(1.2)


def test_proventos_tem_contrato_e_volume_medido():
    linhas = _ler("eventos_proventos.csv")
    assert list(linhas[0].keys()) == ["ticker", "data", "valor"]
    assert len(linhas) == 499
    assert all(l["ticker"] in TICKERS and float(l["valor"]) > 0 for l in linhas)


@pytest.mark.parametrize("arquivo", sorted(SERIES_BCB))
def test_series_do_banco_central(arquivo):
    n, d0, v0, d1, v1 = SERIES_BCB[arquivo]
    linhas = _ler(arquivo)
    assert list(linhas[0].keys()) == ["data", "valor"]
    datas = [linha["data"] for linha in linhas]
    assert datas == sorted(set(datas))
    assert len(linhas) == n
    assert (datas[0], datas[-1]) == (d0, d1)
    assert float(linhas[0]["valor"]) == pytest.approx(v0)
    assert float(linhas[-1]["valor"]) == pytest.approx(v1)


def test_readme_documenta_cada_arquivo():
    with open(os.path.join(DADOS, "README.md"), encoding="utf-8") as fh:
        texto = fh.read()
    for nome in sorted(os.listdir(DADOS)):
        if nome.endswith(".csv"):
            assert nome in texto, nome
