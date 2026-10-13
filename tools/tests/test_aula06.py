"""Trava os achados da Aula 06, medidos em 13/10/2026 sobre dados/ pela API de exemplo.

Se um valor divergir depois de uma nova coleta, o provedor mudou o histórico:
investigar e registrar em dados/README.md antes de atualizar o número aqui, no
deck, no material, nas notas, no notebook, nos widgets e nas animações. Se
divergir sem coleta nova, alguém mudou a API de exemplo ou os módulos dela.
"""
import os
import sys

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("scipy")
pytest.importorskip("httpx")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula06 as m  # noqa: E402


@pytest.fixture(scope="module")
def resultado():
    return m.resultado()


@pytest.fixture(scope="module")
def contexto():
    return m.contexto()


def test_pedido_de_referencia_usa_1907_retornos_na_janela_comum(resultado):
    # ADR-009: a lacuna da IVVB11 em 24/10/2025 é preenchida com o último preço,
    # e sem a GOLD11 a janela comum é a série inteira: 1.908 pregões, menos o
    # primeiro, que não tem retorno. A API declara início e fim da janela.
    assert resultado["tickers"] == ["PETR4", "VALE3", "ITUB4", "WEGE3", "IVVB11"]
    assert resultado["pregoes"] == 1907
    assert resultado["inicio_janela"] == "2019-01-03"
    assert resultado["fim_janela"] == "2026-08-31"
    assert round(resultado["taxa_livre_risco"], 4) == 0.0951
    assert len(resultado["fronteira"]) == 50


def test_carteira_de_maximo_sharpe(contexto):
    sharpe = contexto["maximo_sharpe"]
    assert sharpe["pesos_pct"] == {"PETR4": 23.33, "WEGE3": 25.02, "IVVB11": 51.64}
    assert sharpe["retorno_anual_pct"] == 26.90
    assert sharpe["volatilidade_anual_pct"] == 19.13
    assert sharpe["sharpe"] == 0.91


def test_carteira_de_variancia_minima(contexto):
    minima = contexto["variancia_minima"]
    assert minima["pesos_pct"] == {"PETR4": 2.32, "VALE3": 2.54, "ITUB4": 22.55,
                                   "WEGE3": 10.94, "IVVB11": 61.65}
    assert minima["retorno_anual_pct"] == 21.04
    assert minima["volatilidade_anual_pct"] == 16.71
    assert minima["sharpe"] == 0.69


@pytest.mark.parametrize("ticker,retorno,volatilidade,correlacao", [
    ("PETR4", 33.94, 39.25, 0.32),
    ("VALE3", 20.39, 35.49, 0.32),
    ("ITUB4", 12.90, 29.36, 0.29),
    ("WEGE3", 30.83, 35.13, 0.24),
    ("IVVB11", 21.82, 20.15, 0.16),
])
def test_metricas_por_ativo(contexto, ticker, retorno, volatilidade, correlacao):
    ativo = {a["ticker"]: a for a in contexto["ativos"]}[ticker]
    assert ativo["retorno_anual_pct"] == retorno
    assert ativo["volatilidade_anual_pct"] == volatilidade
    assert ativo["correlacao_media"] == correlacao


def test_fronteira_vai_da_variancia_minima_ao_maior_retorno(resultado):
    vol_inicio, ret_inicio = resultado["fronteira"][0]
    vol_fim, ret_fim = resultado["fronteira"][-1]
    assert round(vol_inicio, 4) == round(resultado["variancia_minima"]["volatilidade"], 4)
    assert round(ret_inicio, 4) == round(resultado["variancia_minima"]["retorno"], 4)
    assert round(ret_fim, 4) == 0.3394  # retorno anual da PETR4, o maior da cesta
    assert round(vol_fim, 4) == 0.3925


def test_status_de_cada_requisicao_do_montador():
    assert m.status_por_caso() == {
        "GET /ativos -": 200,
        "POST /carteiras/otimizar valido": 200,
        "POST /carteiras/otimizar ticker-inexistente": 404,
        "POST /carteiras/otimizar um-ticker": 422,
        "POST /carteiras/otimizar datas-invertidas": 422,
        "POST /carteiras/interpretar valido": 503,
        "POST /carteiras/interpretar ticker-inexistente": 404,
        "POST /carteiras/interpretar um-ticker": 422,
        "POST /carteiras/interpretar datas-invertidas": 422,
    }


def test_get_ativos_lista_os_15_tickers_da_cesta():
    caso = [c for c in m.requisicoes() if c["metodo"] == "GET"][0]
    assert len(caso["resposta"]) == 15


def test_cada_pedido_sem_cache_resolve_52_problemas_de_otimizacao():
    # 1 de variância mínima, 1 de máximo Sharpe e 50 pontos da fronteira.
    assert m.problemas_por_pedido(com_cache=False) == [52, 52, 52, 52, 52]


def test_cache_resolve_so_o_primeiro_pedido_de_cada_consulta():
    contagem = m.problemas_por_pedido(com_cache=True)
    assert m.SEQUENCIA_CACHE == ["A", "A", "B", "A", "B"]
    assert contagem == [52, 0, 52, 0, 0]
    assert sum(contagem) == 104


def test_texto_com_erros_planta_tres_erros_de_tipos_diferentes():
    texto, erros = m.texto_com_erros()
    assert [e["tipo"] for e in erros] == ["valor_alterado", "promessa_inventada", "ativo_trocado"]
    assert [e["trecho"] for e in erros] == ["17,13%", "30,00%", "0,16"]
    for erro in erros:
        assert erro["trecho"] in texto
    assert chr(0x2014) not in texto


def test_verificador_confere_12_numeros_e_acusa_dois_dos_tres_erros():
    verificacao = m.verificacao_do_texto()
    assert len(verificacao) == 12
    assert [v["trecho"] for v in verificacao if not v["confere"]] == ["17,13%", "30,00%"]


def test_verificador_aprova_o_ativo_trocado_e_a_origem_entrega_o_erro():
    trocado = [v for v in m.verificacao_do_texto() if v["trecho"] == "0,16"][0]
    assert trocado["confere"] is True
    assert trocado["origem"] == "ativos[IVVB11].correlacao_media"


def test_verificador_reprova_numero_inventado_e_aceita_numero_do_json():
    """Visto falhando: com o filtro de porcentagem invertido, 0,91 deixava de conferir."""
    verificar = m.api().interpretacao.verificar_numeros
    r = m.resultado()
    assert [v["confere"] for v in verificar("Sharpe de 0,91 e 9,51% de CDI.", r)] == [True, True]
    assert [v["confere"] for v in verificar("Sharpe de 9,51 e 0,91% de CDI.", r)] == [False, False]
    assert verificar("Em 02/01/2019 a PETR4 abriu.", r) == []


# ADR-009: o backend do exemplo implementa a regra sozinho, porque é o código que
# o aluno copia, e por isso não importa tools/retornos.py. Estes testes conferem
# que as duas implementações devolvem os mesmos retornos, pedido a pedido.
PEDIDOS_JANELA = [
    (["PETR4", "VALE3", "ITUB4", "WEGE3", "IVVB11"], "2019-01-01", "2026-08-31"),  # com ETF
    (["PETR4", "VALE3", "ITUB4", "WEGE3"], "2019-01-01", "2026-08-31"),            # sem ETF
    (["PETR4", "BOVA11", "GOLD11"], "2019-01-01", "2026-08-31"),                   # ETF e GOLD11
    (["VALE3", "GOLD11"], "2021-01-01", "2025-12-31"),                             # GOLD11 recortada
    (["PETR4", "VALE3", "ITUB4", "WEGE3", "IVVB11"], "2021-01-01", "2026-08-31"),  # pedido B do cache
]


@pytest.mark.parametrize("tickers,inicio,fim", PEDIDOS_JANELA)
def test_retornos_do_backend_sao_os_da_janela_comum_do_modulo(tickers, inicio, fim):
    import pandas as pd

    import retornos as modulo

    m.api()
    carteira = sys.modules["carteira"]
    backend = carteira.metricas.retornos(carteira.dados.precos(tickers), inicio, fim)
    pd.testing.assert_frame_equal(backend, modulo.retornos_janela_comum(tickers, inicio, fim),
                                  check_freq=False)


@pytest.mark.parametrize("tickers,inicio,fim", PEDIDOS_JANELA)
def test_api_declara_a_janela_comum_que_usou(tickers, inicio, fim):
    import retornos as modulo

    esperado = modulo.retornos_janela_comum(tickers, inicio, fim)
    resposta = m.cliente().post("/carteiras/otimizar",
                                json={"tickers": tickers, "inicio": inicio, "fim": fim})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["pregoes"] == len(esperado)
    assert corpo["inicio_janela"] == esperado.index[0].strftime("%Y-%m-%d")
    assert corpo["fim_janela"] == esperado.index[-1].strftime("%Y-%m-%d")


def test_com_a_gold11_a_janela_comeca_em_14_12_2020_e_perde_marco_de_2020():
    corpo = m.cliente().post("/carteiras/otimizar", json={
        "tickers": ["PETR4", "BOVA11", "GOLD11"], "inicio": "2019-01-01", "fim": "2026-08-31"}).json()
    assert corpo["inicio_janela"] == "2020-12-14"
    assert corpo["pregoes"] == 1423
