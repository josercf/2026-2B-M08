"""Trava o arquivo de cotações da Aula 04 em turnos (portal, kit e notebook)."""
import csv
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON = os.path.join(RAIZ, "assets", "data", "aula04-cotacoes.json")
CSV = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados", "precos.csv")
RF = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados", "rf.txt")
OBRIGATORIOS = ["PETR4", "VALE3", "ITUB4", "BOVA11", "IVVB11", "GOLD11"]


def _json():
    with open(JSON, encoding="utf-8") as fh:
        return json.load(fh)


def _csv():
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_janela_termina_no_corte_da_atividade_de_negocios():
    dados = _json()
    assert dados["corte"] == "2026-11-13"
    assert dados["datas"][-1] == "2026-11-13"
    assert dados["datas"][0] >= "2024-01-02"
    assert dados["datas"] == sorted(set(dados["datas"]))


def test_universo_cobre_a_cesta_do_acervo_e_passa_de_cem_ativos():
    precos = _json()["precos"]
    for ticker in OBRIGATORIOS:
        assert ticker in precos
    assert len(precos) >= 100


def test_nenhuma_lacuna_depois_da_primeira_cotacao():
    dados = _json()
    for ticker, serie in dados["precos"].items():
        assert len(serie) == len(dados["datas"]), ticker
        primeiro = next(i for i, v in enumerate(serie) if v is not None)
        assert all(v is not None and v > 0 for v in serie[primeiro:]), ticker


def test_todo_ativo_tem_pelo_menos_253_cotacoes():
    for ticker, serie in _json()["precos"].items():
        assert sum(v is not None for v in serie) >= 253, ticker


def test_json_e_csv_tem_as_mesmas_datas_e_os_mesmos_ativos():
    dados, linhas = _json(), _csv()
    assert [l["data"] for l in linhas] == dados["datas"]
    assert list(linhas[0].keys()) == ["data"] + list(dados["precos"].keys())
    ultima = linhas[-1]
    for ticker in OBRIGATORIOS:
        assert abs(float(ultima[ticker]) - dados["precos"][ticker][-1]) < 1e-9


def test_taxa_livre_de_risco_e_plausivel_e_igual_nos_dois_arquivos():
    rf = _json()["rf_anual"]
    assert 0.05 < rf < 0.25
    with open(RF, encoding="utf-8") as fh:
        assert abs(float(fh.read().strip()) - rf) < 1e-12


def test_json_cabe_em_tres_megabytes():
    assert os.path.getsize(JSON) < 3 * 1024 * 1024
