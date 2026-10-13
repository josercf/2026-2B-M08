"""Trava os achados da Aula 04, medidos em 13/10/2026 sobre dados/.

Amostra: Adj Close com as datas de ausência descartadas (1.423 pregões, 1.422
retornos de 14/12/2020 a 31/08/2026), anualização por 252, CDI como taxa livre
de risco, semente 42 no sorteio. Se um valor divergir depois de uma nova
coleta, o provedor mudou o histórico: investigar e registrar em dados/README.md
antes de atualizar o número aqui, no deck, no notebook, nos widgets e nas
animações.
"""
import json
import os
import re
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula04 as m  # noqa: E402

DECK = os.path.join(m.RAIZ, "aulas", "aula04.html")
DATA = os.path.join(m.RAIZ, "assets", "data")
NOTEBOOK = os.path.join(m.RAIZ, "notebooks", "aula04.ipynb")


def _r(valor, casas=4):
    return round(float(valor), casas)


# --- amostra e taxa livre de risco ------------------------------------------

def test_amostra_descarta_ausencias_e_comeca_com_o_gold11():
    precos = m.precos()
    retornos = m.retornos()
    assert len(precos) == 1423
    assert len(retornos) == 1422
    assert retornos.index[0].strftime("%Y-%m-%d") == "2020-12-14"
    assert retornos.index[-1].strftime("%Y-%m-%d") == "2026-08-31"
    assert retornos.shape[1] == 15
    assert not retornos.isna().any().any()


def test_cdi_anualizado_na_janela_dos_retornos():
    assert _r(m.taxa_livre_de_risco()) == 0.1130


def test_parametros_do_modelo_de_3_e_de_15_ativos():
    assert m.parametros_do_modelo(3) == 9
    assert m.parametros_do_modelo(15) == 135


@pytest.mark.parametrize("ticker,retorno,vol", [
    ("PETR4", 0.3756, 0.3341),
    ("GOLD11", 0.1747, 0.1980),
    ("IVVB11", 0.1585, 0.1767),
    ("ITUB4", 0.1565, 0.2553),
    ("BOVA11", 0.0979, 0.1851),
    ("MGLU3", -0.4284, 0.6775),
])
def test_retorno_e_volatilidade_anualizados(ticker, retorno, vol):
    assert _r(m.retorno_esperado()[ticker]) == retorno
    assert _r(m.volatilidade()[ticker]) == vol


def test_oito_dos_quinze_ativos_rendem_abaixo_do_cdi():
    abaixo = m.retorno_esperado() < m.taxa_livre_de_risco()
    assert int(abaixo.sum()) == 8
    assert sorted(abaixo[abaixo].index) == sorted(
        ["MGLU3", "RENT3", "SUZB3", "EGIE3", "ABEV3", "BBDC4", "B3SA3", "BOVA11"])


@pytest.mark.parametrize("ticker,sharpe", [
    ("PETR4", 0.7859), ("GOLD11", 0.3112), ("IVVB11", 0.2571), ("BOVA11", -0.0816),
])
def test_sharpe_por_ativo(ticker, sharpe):
    assert _r(m.sharpe_por_ativo()[ticker]) == sharpe


def test_metricas_da_carteira_igual_batem_com_a_forma_vetorial():
    w = np.full(15, 1 / 15)
    ret, vol, sharpe = m.metricas(w)
    r = m.retornos()
    carteira_diaria = r.values @ w
    assert ret == pytest.approx(carteira_diaria.mean() * 252)
    assert vol == pytest.approx(carteira_diaria.std(ddof=1) * np.sqrt(252))
    assert _r(ret) == 0.0834
    assert _r(vol) == 0.1632
    assert _r(sharpe) == -0.1814


# --- nuvem de Monte Carlo ----------------------------------------------------

def test_nuvem_de_10000_carteiras_com_pesos_validos():
    n = m.nuvem()
    assert n["pesos"].shape == (10_000, 15)
    assert np.allclose(n["pesos"].sum(axis=1), 1)
    assert (n["pesos"] >= 0).all()


def test_melhor_carteira_sorteada():
    n = m.nuvem()
    assert n["melhor"] == 1927
    assert _r(n["melhor_sharpe"]) == 0.4077
    assert _r(n["melhor_retorno"]) == 0.1663
    assert _r(n["melhor_volatilidade"]) == 0.1306
    assert _r(n["melhor_maior_peso"]) == 0.1817


def test_nuvem_nao_alcanca_as_bordas_da_fronteira():
    n = m.nuvem()
    assert _r(n["maior_peso_da_nuvem"]) == 0.2461
    assert _r(n["menor_volatilidade"]) == 0.1188
    assert _r(n["maior_retorno"]) == 0.1663
    assert n["menor_volatilidade"] > m.carteira(m.variancia_minima())["volatilidade"]
    assert n["maior_retorno"] < m.retorno_esperado().max()


def test_motor_e_reprodutivel_com_a_semente():
    a = m.sortear(500)[3]
    b = m.sortear(500)[3]
    c = m.sortear(500, semente=7)[3]
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_melhor_sharpe_por_numero_de_sorteios():
    melhor = {n: _r(s) for n, s in m.melhor_por_sorteios().items()}
    assert melhor == {10: -0.0950, 100: 0.1475, 1_000: 0.2839, 10_000: 0.4077,
                      100_000: 0.4077, 1_000_000: 0.6013}


def test_dez_mil_sorteios_da_curva_coincidem_com_a_nuvem():
    assert m.melhor_por_sorteios((10_000,))[10_000] == pytest.approx(m.nuvem()["melhor_sharpe"])


# --- otimização ---------------------------------------------------------------

def test_carteira_de_variancia_minima():
    c = m.carteira(m.variancia_minima())
    assert _r(c["volatilidade"]) == 0.0967
    assert _r(c["retorno"]) == 0.1411
    assert _r(c["sharpe"]) == 0.2902
    assert c["ativos"] == 10
    assert c["maior_ativo"] == "IVVB11"
    assert _r(c["maior_peso"]) == 0.2679
    assert _r(c["pesos"]["GOLD11"]) == 0.2468
    assert _r(c["pesos"]["EGIE3"]) == 0.1720


def test_carteira_de_maximo_sharpe():
    c = m.carteira(m.maximo_sharpe())
    assert _r(c["sharpe"]) == 0.9219
    assert _r(c["retorno"]) == 0.2598
    assert _r(c["volatilidade"]) == 0.1591
    assert c["ativos"] == 3
    assert {t: _r(w) for t, w in c["pesos"].items()} == {
        "PETR4": 0.4429, "IVVB11": 0.2407, "GOLD11": 0.3164}


def test_maximo_sharpe_concentra_mais_que_a_variancia_minima():
    mv = m.carteira(m.variancia_minima())
    ms = m.carteira(m.maximo_sharpe())
    assert ms["maior_peso"] > mv["maior_peso"]
    assert ms["ativos"] < mv["ativos"]


def test_otimas_vencem_a_melhor_sorteada():
    n = m.nuvem()
    assert m.carteira(m.maximo_sharpe())["sharpe"] > n["melhor_sharpe"]
    assert m.carteira(m.variancia_minima())["volatilidade"] < n["menor_volatilidade"]
    assert (n["sharpe"] <= m.carteira(m.maximo_sharpe())["sharpe"]).all()


def test_fronteira_de_50_pontos():
    f = m.fronteira()
    assert len(f) == 50
    mv = m.carteira(m.variancia_minima())
    assert f["volatilidade"].iloc[0] == pytest.approx(mv["volatilidade"], abs=1e-5)
    assert _r(f["retorno"].iloc[-1]) == 0.3756
    assert _r(f["volatilidade"].iloc[-1]) == 0.3341
    assert (f["volatilidade"].diff().dropna() > 0).all()
    assert (f["retorno"].diff().dropna() > 0).all()


def test_nenhuma_carteira_sorteada_passa_da_fronteira():
    f = m.fronteira()
    n = m.nuvem()
    limite = np.interp(n["retorno"], f["retorno"], f["volatilidade"])
    dentro = n["retorno"] >= f["retorno"].iloc[0]
    assert (n["volatilidade"][dentro] >= limite[dentro] - 1e-6).all()


def test_trio_reproduz_o_maximo_sharpe_da_cesta():
    passos, final = m.caminho_slsqp_trio()
    ret, vol, sharpe = m.metricas(final, *m.trio())
    assert _r(sharpe) == 0.9219
    assert [_r(w) for w in final] == [0.4429, 0.2407, 0.3164]


def test_caminho_do_slsqp_no_triangulo():
    passos, final = m.caminho_slsqp_trio()
    assert len(passos) == 11
    assert [_r(w, 2) for w in passos[0]] == [0.1, 0.8, 0.1]
    assert [_r(w, 2) for w in passos[1]] == [1.0, 0.0, 0.0]
    assert np.allclose(passos.sum(axis=1), 1)
    assert np.allclose(passos[-1], final, atol=1e-6)


# --- acréscimos da retomada: nuvem abaixo do CDI, trio e desempenho ---------

def test_a_maioria_da_nuvem_rende_abaixo_do_cdi():
    n = m.nuvem()
    assert n["abaixo_do_cdi"] == 8843
    assert int((n["retorno"] < m.taxa_livre_de_risco()).sum()) == 8843
    assert _r(n["maior_volatilidade"]) == 0.2435


def test_correlacao_e_volatilidade_do_trio():
    c = m.correlacao_trio()
    assert _r(c.loc["PETR4", "IVVB11"]) == -0.0939
    assert _r(c.loc["PETR4", "GOLD11"]) == -0.1326
    assert _r(c.loc["IVVB11", "GOLD11"]) == 0.2516
    assert [_r(m.volatilidade()[t]) for t in m.TRIO] == [0.3341, 0.1767, 0.1980]


def test_cinco_maiores_pesos_da_variancia_minima():
    pesos = m.carteira(m.variancia_minima())["pesos"]
    maiores = sorted(pesos.items(), key=lambda par: -par[1])[:5]
    assert [(t, _r(w)) for t, w in maiores] == [
        ("IVVB11", 0.2679), ("GOLD11", 0.2468), ("EGIE3", 0.1720),
        ("ABEV3", 0.0756), ("BOVA11", 0.0672)]
    assert "MGLU3" not in pesos


def test_caminho_do_slsqp_parte_de_sharpe_047():
    passos, _ = m.caminho_slsqp_trio()
    mu, cov = m.trio()
    assert _r(m.metricas(passos[0], mu, cov)[2]) == 0.4654
    assert _r(m.metricas(passos[1], mu, cov)[2]) == 0.7859


def test_motor_roda_10000_carteiras_em_menos_de_1_segundo():
    """Requisito do A3: menos de 10 s. O motor vetorizado fica abaixo de 1 s."""
    import time
    mu, cov, rf = m.retorno_esperado().values, m.covariancia().values, m.taxa_livre_de_risco()
    inicio = time.perf_counter()
    m.sortear(10_000, mu=mu, cov=cov, rf=rf)
    assert time.perf_counter() - inicio < 1.0


def test_otimizador_converge_em_menos_de_5_segundos():
    """Requisito do A4: as duas ótimas em menos de 5 s para até 15 ativos."""
    import time
    mu, cov, rf = m.retorno_esperado().values, m.covariancia().values, m.taxa_livre_de_risco()
    inicio = time.perf_counter()
    m.variancia_minima()
    m.maximo_sharpe(mu, cov, rf)
    assert time.perf_counter() - inicio < 5.0


# --- JSON dos widgets: repetem as medições, sem número à mão ------------------

def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def _num(valor, casas=2):
    return ("%.*f" % (casas, valor)).replace(".", ",")


def _pct(valor):
    return _num(valor * 100) + "%"


def test_json_da_nuvem_repete_a_nuvem_medida():
    dados = _json("aula04-nuvem.json")
    n = m.nuvem()
    assert len(dados["sharpe"]) == len(dados["vol"]) == len(dados["ret"]) == 10_000
    assert dados["sharpe"][n["melhor"]] == _r(n["melhor_sharpe"])
    assert len(dados["fronteira"]) == 50
    assert dados["maximo_sharpe"]["sharpe"] == 0.9219
    assert dados["variancia_minima"]["vol"] == 0.0967


def test_json_da_nuvem_tem_a_leitura_de_cada_patamar():
    dados = _json("aula04-nuvem.json")
    progressivo = m.melhor_por_sorteios()
    for passo in dados["passos"]:
        # O widget recalcula a melhor entre as N primeiras; a leitura precisa bater.
        assert max(dados["sharpe"][:passo]) == pytest.approx(progressivo[passo], abs=1e-4)
        assert _num(progressivo[passo]) in dados["leituras"][str(passo)]


def test_json_do_triangulo_reproduz_o_otimo():
    dados = _json("aula04-triangulo.json")
    assert dados["tickers"] == list(m.TRIO)
    w = np.array(dados["otima"]["pesos"])
    ret, vol, sharpe = m.metricas(w, np.array(dados["mu"]), np.array(dados["cov"]), dados["rf"])
    assert _r(sharpe, 2) == 0.92
    assert dados["otima"]["sharpe"] == 0.9219


# --- deck ------------------------------------------------------------------------

def _deck():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _secoes():
    return re.findall(r"<section\b(.*?)</section>", _deck(), flags=re.S)


def test_rodapes_do_deck_numerados_em_sequencia():
    numeros = [int(n) for n in re.findall(r'<p class="footer-page">(\d+)</p>', _deck())]
    esperados = [i + 1 for i, s in enumerate(_secoes()) if "footer-page" in s]
    assert numeros == esperados


def test_deck_abre_pelo_resgate_e_pelo_peer_instruction():
    secoes = _secoes()
    assert 'class="cover-slide"' in secoes[0]
    assert 'id="agenda"' in secoes[1]
    assert 'id="resgate"' in secoes[2] and "Aula 03" in secoes[2]
    assert 'class="quiz-slide" id="preparo"' in secoes[3]


def test_deck_cita_os_numeros_medidos():
    deck = _deck()
    n = m.nuvem()
    mv = m.carteira(m.variancia_minima())
    ms = m.carteira(m.maximo_sharpe())
    progressivo = m.melhor_por_sorteios()
    w = np.full(15, 1 / 15)
    ret_igual, vol_igual, sharpe_igual = m.metricas(w)
    pesos_mv = mv["pesos"]
    outros = sum(v for k, v in pesos_mv.items() if k not in ("PETR4", "IVVB11", "GOLD11", "EGIE3"))
    esperados = [
        _num(n["melhor_sharpe"]), _num(ms["sharpe"]), _pct(n["melhor_retorno"]),
        _pct(n["melhor_volatilidade"]), _pct(n["melhor_maior_peso"]), _pct(ms["retorno"]),
        _pct(ms["volatilidade"]), _pct(ms["maior_peso"]), _pct(n["maior_peso_da_nuvem"]),
        _pct(m.taxa_livre_de_risco()), _pct(ret_igual), _pct(vol_igual), _num(sharpe_igual),
        _pct(m.retorno_esperado()["MGLU3"]), "8.843", _pct(mv["retorno"]), _pct(mv["volatilidade"]),
        _num(mv["sharpe"]), _pct(mv["maior_peso"]), _pct(pesos_mv["GOLD11"]), _pct(pesos_mv["EGIE3"]),
        _pct(pesos_mv["PETR4"]), _pct(outros), _pct(ms["pesos"]["IVVB11"]), _pct(ms["pesos"]["GOLD11"]),
        _pct(n["menor_volatilidade"]), _pct(m.fronteira()["retorno"].iloc[-1]),
        "1.422", "14/12/2020", "135", "10 iterações",
    ] + [_num(v) for v in progressivo.values()]
    esperados += [_pct(m.volatilidade()[t]) for t in m.TRIO]
    c = m.correlacao_trio()
    esperados += [_num(c.loc["PETR4", "IVVB11"]), _num(c.loc["PETR4", "GOLD11"])]
    for valor in esperados:
        assert valor in deck, valor
    assert len(m.caminho_slsqp_trio()[0]) - 1 == 10
    assert 15 - ms["ativos"] == 12 and "zera 12" in deck
    assert "Oito dos 15 ativos" in deck


def test_deck_cita_os_pesos_e_prazos_da_fonte():
    deck = _deck()
    assert "A3 vale 3 pontos" in deck
    assert "O A4 (3 pontos)" in deck
    assert "19/11/2026" in deck and "20/11/2026, 23h59" in deck


def test_deck_declara_os_dois_widgets_e_as_tres_animacoes():
    deck = _deck()
    assert 'data-widget="aula04-triangulo"' in deck
    assert 'data-widget="aula04-nuvem"' in deck
    for nome in ("nuvem-monte-carlo", "fronteira", "slsqp-triangulo"):
        assert "../assets/video/aula04-%s.mp4" % nome in deck


def test_sem_travessao_nos_artefatos_da_aula():
    for caminho in (DECK, NOTEBOOK,
                    os.path.join(m.RAIZ, "materiais", "aula04.html"),
                    os.path.join(m.RAIZ, "referencias", "aula04.html"),
                    os.path.join(m.RAIZ, "docs", "notas-do-professor", "aula04.md")):
        with open(caminho, encoding="utf-8") as fh:
            assert chr(0x2014) not in fh.read(), caminho


def test_material_cita_os_numeros_medidos():
    with open(os.path.join(m.RAIZ, "materiais", "aula04.html"), encoding="utf-8") as fh:
        material = fh.read()
    n = m.nuvem()
    mv = m.carteira(m.variancia_minima())
    ms = m.carteira(m.maximo_sharpe())
    passos, _ = m.caminho_slsqp_trio()
    tres = mv["pesos"]["IVVB11"] + mv["pesos"]["GOLD11"] + mv["pesos"]["EGIE3"]
    for valor in ("8.843", "1.422", "135", _pct(tres), _pct(n["menor_volatilidade"]),
                  _pct(n["maior_peso_da_nuvem"]), _num(m.metricas(passos[1], *m.trio())[2]),
                  _pct(m.taxa_livre_de_risco()), _pct(mv["volatilidade"]), _pct(ms["retorno"]),
                  _num(m.correlacao_trio().loc["PETR4", "GOLD11"]), "20/11/2026, às 23h59"):
        assert valor in material, valor
    assert 'id="preparacao"' in material
    assert material.index('id="preparacao"') < material.index('id="amostra"')
    assert material.count("<details>") == 5
    for titulo in ("Carteiras e simulação de Monte Carlo com Python",
                   "Da nuvem à fronteira eficiente de Markowitz"):
        assert titulo in material


def test_referencias_copiam_os_autoestudos_da_semana_6():
    with open(os.path.join(m.RAIZ, "referencias", "aula04.html"), encoding="utf-8") as fh:
        pagina = fh.read()
    with open(os.path.join(m.RAIZ, "docs", "autoestudos-por-semana.md"), encoding="utf-8") as fh:
        fonte = fh.read()
    semana = fonte.split("## Semana 06")[1].split("## Semana")[0]
    titulos = re.findall(r"^- (.+)$", semana, flags=re.M)
    assert len(titulos) == 2
    for titulo in titulos:
        assert titulo in pagina
    assert "65 min" in pagina and "70 min" in pagina
    assert 'id="autoestudos"' in pagina and 'id="complementar"' in pagina
