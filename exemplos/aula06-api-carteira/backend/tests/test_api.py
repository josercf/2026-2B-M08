"""Testes da API de exemplo da Aula 06, com TestClient e sem subir servidor.

Rodar dentro de backend/:  python -m pytest tests -v
Os testes leem dados/ do acervo e nunca chamam o LLM: a chamada é trocada por
uma função falsa com monkeypatch, então nenhuma chave é necessária.
"""
import pytest
from fastapi.testclient import TestClient

import interpretacao
import main
from carteira import otimizador

PEDIDO = {"tickers": ["PETR4", "VALE3", "ITUB4", "WEGE3", "IVVB11"],
          "inicio": "2019-01-01", "fim": "2026-08-31"}


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    main._calcular.cache_clear()
    return TestClient(main.app)


def test_otimizar_devolve_200_com_as_duas_carteiras_e_a_fronteira(cliente):
    resposta = cliente.post("/carteiras/otimizar", json=PEDIDO)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["pregoes"] == 1906
    assert len(corpo["fronteira"]) == 50
    for carteira in ("variancia_minima", "maximo_sharpe"):
        assert abs(sum(corpo[carteira]["pesos"].values()) - 1) < 1e-9
        assert min(corpo[carteira]["pesos"].values()) >= 0


def test_ticker_em_minusculas_e_normalizado(cliente):
    pedido = dict(PEDIDO, tickers=["petr4", " vale3 "])
    assert cliente.post("/carteiras/otimizar", json=pedido).json()["tickers"] == ["PETR4", "VALE3"]


@pytest.mark.parametrize("mudanca,status", [
    ({"tickers": ["PETR4"]}, 422),                          # menos de dois ativos
    ({"tickers": ["PETR4", "petr4"]}, 422),                 # repetido depois de normalizar
    ({"inicio": "2026-08-31", "fim": "2019-01-01"}, 422),   # datas invertidas
    ({"taxa_livre_risco": 1.5}, 422),                       # taxa acima de 100% ao ano
    ({"tickers": ["PETR4", "XPTO3"]}, 404),                 # ticker fora da base
    ({"inicio": "2026-08-01"}, 422),                        # menos de 60 pregões
])
def test_entrada_invalida_devolve_o_status_do_contrato(cliente, mudanca, status):
    assert cliente.post("/carteiras/otimizar", json=dict(PEDIDO, **mudanca)).status_code == status


def test_ticker_inexistente_diz_qual_ticker(cliente):
    resposta = cliente.post("/carteiras/otimizar", json=dict(PEDIDO, tickers=["PETR4", "XPTO3"]))
    assert "XPTO3" in resposta.json()["detail"]


def test_cache_nao_resolve_de_novo_a_mesma_consulta(cliente):
    antes = otimizador.PROBLEMAS_RESOLVIDOS
    cliente.post("/carteiras/otimizar", json=PEDIDO)
    depois_do_primeiro = otimizador.PROBLEMAS_RESOLVIDOS
    cliente.post("/carteiras/otimizar", json=PEDIDO)
    assert depois_do_primeiro - antes == 52
    assert otimizador.PROBLEMAS_RESOLVIDOS == depois_do_primeiro


def test_interpretar_sem_chave_devolve_503(cliente):
    resposta = cliente.post("/carteiras/interpretar", json=PEDIDO)
    assert resposta.status_code == 503
    assert "chave" in resposta.json()["detail"]


def test_interpretar_confere_os_numeros_do_texto(cliente, monkeypatch):
    texto = "Sharpe de 0,91, volatilidade de 17,13% e CDI de 9,51%."
    monkeypatch.setattr(interpretacao, "chamar_llm", lambda prompt: (texto, "modelo-falso"))
    corpo = cliente.post("/carteiras/interpretar", json=PEDIDO).json()
    assert corpo["modelo"] == "modelo-falso"
    assert "9.51" in corpo["prompt"]  # o JSON do prompt leva os números reais
    assert [(v["trecho"], v["confere"]) for v in corpo["verificacao"]] == [
        ("0,91", True), ("17,13%", False), ("9,51%", True)]


def test_falha_do_provedor_vira_502(cliente, monkeypatch):
    def falhar(prompt):
        raise TimeoutError("sem resposta")

    monkeypatch.setattr(interpretacao, "chamar_llm", falhar)
    assert cliente.post("/carteiras/interpretar", json=PEDIDO).status_code == 502


def test_exportar_devolve_csv_com_os_pesos(cliente):
    resposta = cliente.post("/carteiras/exportar", json=PEDIDO)
    assert resposta.status_code == 200
    linhas = resposta.text.strip().splitlines()
    assert linhas[0] == "ticker,peso_variancia_minima,peso_maximo_sharpe"
    assert len(linhas) == 6


def test_cors_libera_o_frontend_do_vite(cliente):
    resposta = cliente.options("/carteiras/otimizar", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
    outra = cliente.options("/carteiras/otimizar", headers={
        "Origin": "http://exemplo.invalid", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in outra.headers


def test_chave_nunca_aparece_na_resposta(cliente, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-teste-nao-e-chave")
    monkeypatch.setattr(interpretacao, "chamar_llm", lambda prompt: ("ok", "modelo-falso"))
    resposta = cliente.post("/carteiras/interpretar", json=PEDIDO)
    assert "sk-or-teste" not in resposta.text
