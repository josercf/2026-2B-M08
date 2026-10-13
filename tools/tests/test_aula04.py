"""Trava os achados da Aula 04, medidos em 13/10/2026 sobre dados/.

Amostra: o tratamento de ausência único do módulo (ADR-009, tools/retornos.py),
com a lacuna de 24/10/2025 preenchida e a cesta na janela comum dos 15 ativos
(1.423 retornos de 14/12/2020 a 31/08/2026), anualização por 252, CDI como taxa
livre de risco, semente 42 no sorteio. Se um valor divergir depois de uma nova
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

def test_amostra_e_a_janela_comum_da_adr_009():
    retornos = m.retornos()
    assert len(retornos) == 1423
    assert retornos.index[0].strftime("%Y-%m-%d") == "2020-12-14"
    assert retornos.index[-1].strftime("%Y-%m-%d") == "2026-08-31"
    assert retornos.shape[1] == 15
    assert not retornos.isna().any().any()
    assert retornos.equals(m.tratamento.retornos_janela_comum())


def test_pregao_de_24_10_2025_volta_com_retorno_zero_nos_tres_etfs():
    dia = m.retornos().loc["2025-10-24"]
    assert [float(dia[t]) for t in ("BOVA11", "IVVB11", "GOLD11")] == [0.0, 0.0, 0.0]
    assert float(dia["PETR4"]) != 0.0


def test_custo_da_janela_comum_perde_marco_de_2020_e_baixa_a_volatilidade_da_petr4():
    assert m.retornos().loc["2020-03-01":"2020-03-31"].empty
    custo = m.custo_da_janela("PETR4")
    assert _r(custo["serie_inteira"]) == 0.3925
    assert _r(custo["janela_comum"]) == 0.3340
    assert custo["retornos_serie_inteira"] == 1907
    assert custo["retornos_janela_comum"] == 1423
    assert custo["janela_comum"] == pytest.approx(m.volatilidade()["PETR4"])


def test_cdi_anualizado_na_janela_dos_retornos():
    assert _r(m.taxa_livre_de_risco()) == 0.1130


def test_parametros_do_modelo_de_3_e_de_15_ativos():
    assert m.parametros_do_modelo(3) == 9
    assert m.parametros_do_modelo(15) == 135


@pytest.mark.parametrize("ticker,retorno,vol", [
    ("PETR4", 0.3753, 0.3340),
    ("GOLD11", 0.1746, 0.1980),
    ("IVVB11", 0.1584, 0.1766),
    ("ITUB4", 0.1564, 0.2552),
    ("BOVA11", 0.0979, 0.1850),
    ("MGLU3", -0.4283, 0.6768),
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
    ("PETR4", 0.7853), ("GOLD11", 0.3107), ("IVVB11", 0.2566), ("BOVA11", -0.0820),
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
    assert _r(vol) == 0.1631
    assert _r(sharpe) == -0.1820


# --- nuvem de Monte Carlo ----------------------------------------------------

def test_nuvem_de_10000_carteiras_com_pesos_validos():
    n = m.nuvem()
    assert n["pesos"].shape == (10_000, 15)
    assert np.allclose(n["pesos"].sum(axis=1), 1)
    assert (n["pesos"] >= 0).all()


def test_melhor_carteira_sorteada():
    n = m.nuvem()
    assert n["melhor"] == 1927
    assert _r(n["melhor_sharpe"]) == 0.4069
    assert _r(n["melhor_retorno"]) == 0.1662
    assert _r(n["melhor_volatilidade"]) == 0.1305
    assert _r(n["melhor_maior_peso"]) == 0.1817


def test_nuvem_nao_alcanca_as_bordas_da_fronteira():
    n = m.nuvem()
    assert _r(n["maior_peso_da_nuvem"]) == 0.2461
    assert _r(n["menor_volatilidade"]) == 0.1187
    assert _r(n["maior_retorno"]) == 0.1662
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
    assert melhor == {10: -0.0955, 100: 0.1469, 1_000: 0.2832, 10_000: 0.4069,
                      100_000: 0.4069, 1_000_000: 0.6004}


def test_dez_mil_sorteios_da_curva_coincidem_com_a_nuvem():
    assert m.melhor_por_sorteios((10_000,))[10_000] == pytest.approx(m.nuvem()["melhor_sharpe"])


# --- otimização ---------------------------------------------------------------

def test_carteira_de_variancia_minima():
    c = m.carteira(m.variancia_minima())
    assert _r(c["volatilidade"]) == 0.0967
    assert _r(c["retorno"]) == 0.1410
    assert _r(c["sharpe"]) == 0.2893
    assert c["ativos"] == 10
    assert c["maior_ativo"] == "IVVB11"
    assert _r(c["maior_peso"]) == 0.2678
    assert _r(c["pesos"]["GOLD11"]) == 0.2471
    assert _r(c["pesos"]["EGIE3"]) == 0.1720


def test_carteira_de_maximo_sharpe():
    c = m.carteira(m.maximo_sharpe())
    assert _r(c["sharpe"]) == 0.9212
    assert _r(c["retorno"]) == 0.2596
    assert _r(c["volatilidade"]) == 0.1591
    assert c["ativos"] == 3
    assert {t: _r(w) for t, w in c["pesos"].items()} == {
        "PETR4": 0.4431, "IVVB11": 0.2397, "GOLD11": 0.3172}


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
    assert _r(f["retorno"].iloc[-1]) == 0.3753
    assert _r(f["volatilidade"].iloc[-1]) == 0.3340
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
    assert _r(sharpe) == 0.9212
    assert [_r(w) for w in final] == [0.4431, 0.2397, 0.3172]


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
    assert n["abaixo_do_cdi"] == 8851
    assert int((n["retorno"] < m.taxa_livre_de_risco()).sum()) == 8851
    assert _r(n["maior_volatilidade"]) == 0.2434


def test_correlacao_e_volatilidade_do_trio():
    c = m.correlacao_trio()
    assert _r(c.loc["PETR4", "IVVB11"]) == -0.0933
    assert _r(c.loc["PETR4", "GOLD11"]) == -0.1336
    assert _r(c.loc["IVVB11", "GOLD11"]) == 0.2516
    assert [_r(m.volatilidade()[t]) for t in m.TRIO] == [0.3340, 0.1766, 0.1980]


def test_cinco_maiores_pesos_da_variancia_minima():
    pesos = m.carteira(m.variancia_minima())["pesos"]
    maiores = sorted(pesos.items(), key=lambda par: -par[1])[:5]
    assert [(t, _r(w)) for t, w in maiores] == [
        ("IVVB11", 0.2678), ("GOLD11", 0.2471), ("EGIE3", 0.1720),
        ("ABEV3", 0.0757), ("BOVA11", 0.0673)]
    assert "MGLU3" not in pesos


def test_caminho_do_slsqp_parte_de_sharpe_046():
    passos, _ = m.caminho_slsqp_trio()
    mu, cov = m.trio()
    assert _r(m.metricas(passos[0], mu, cov)[2]) == 0.4646
    assert _r(m.metricas(passos[1], mu, cov)[2]) == 0.7853


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


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def test_json_da_nuvem_repete_a_nuvem_medida():
    dados = _json("aula04-nuvem.json")
    n = m.nuvem()
    assert len(dados["sharpe"]) == len(dados["vol"]) == len(dados["ret"]) == 10_000
    assert dados["sharpe"][n["melhor"]] == _r(n["melhor_sharpe"])
    assert len(dados["fronteira"]) == 50
    assert dados["maximo_sharpe"]["sharpe"] == 0.9212
    assert dados["variancia_minima"]["vol"] == 0.0967


def test_json_dos_widgets_declara_a_janela_comum():
    comum = m.tratamento.retornos_janela_comum()
    esperado = {"inicio": comum.index[0].strftime("%d/%m/%Y"),
                "fim": comum.index[-1].strftime("%d/%m/%Y"), "retornos": len(comum)}
    assert esperado == {"inicio": "14/12/2020", "fim": "31/08/2026", "retornos": 1423}
    for nome in ("aula04-nuvem.json", "aula04-triangulo.json"):
        assert _json(nome)["janela"] == esperado, nome


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
    assert dados["otima"]["sharpe"] == 0.9212


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
        _pct(m.retorno_esperado()["MGLU3"]), "8.851", _pct(mv["retorno"]), _pct(mv["volatilidade"]),
        _num(mv["sharpe"]), _pct(mv["maior_peso"]), _pct(pesos_mv["GOLD11"]), _pct(pesos_mv["EGIE3"]),
        _pct(pesos_mv["PETR4"]), _pct(outros), _pct(ms["pesos"]["IVVB11"]), _pct(ms["pesos"]["GOLD11"]),
        _pct(n["menor_volatilidade"]), _pct(m.fronteira()["retorno"].iloc[-1]),
        "1.423", "14/12/2020", "135", "10 iterações",
    ] + [_num(v) for v in progressivo.values()]
    esperados += [_pct(m.volatilidade()[t]) for t in m.TRIO]
    c = m.correlacao_trio()
    esperados += [_num(c.loc["PETR4", "IVVB11"]), _num(c.loc["PETR4", "GOLD11"])]
    for valor in esperados:
        assert valor in deck, valor
    assert len(m.caminho_slsqp_trio()[0]) - 1 == 10
    assert 15 - ms["ativos"] == 12 and "zera 12" in deck
    assert "Oito dos 15 ativos" in deck


def test_slide_3_traz_a_volatilidade_do_trio_nas_duas_janelas():
    slide = _secoes()[2]
    assert [_r(m.custo_da_janela(t)["serie_inteira"]) for t in m.TRIO] == [0.3925, 0.2015, 0.1980]
    for t in m.TRIO:
        custo = m.custo_da_janela(t)
        assert _pct(custo["serie_inteira"]) in slide and _pct(custo["janela_comum"]) in slide


def test_slide_3_declara_a_regra_da_adr_009_e_o_custo_da_janela():
    slide = _secoes()[2]
    custo = m.custo_da_janela("PETR4")
    assert custo["serie_inteira"] > custo["janela_comum"]
    for valor in ("ADR-009", "1.423", "14/12/2020", "março de 2020", "Aula 01", "Aula 03",
                  _pct(custo["serie_inteira"]), _pct(custo["janela_comum"])):
        assert valor in slide, valor


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
    for valor in ("8.851", "1.423", "135", _pct(tres), _pct(n["menor_volatilidade"]),
                  _pct(n["maior_peso_da_nuvem"]), _num(m.metricas(passos[1], *m.trio())[2]),
                  _pct(m.taxa_livre_de_risco()), _pct(mv["volatilidade"]), _pct(ms["retorno"]),
                  _num(m.correlacao_trio().loc["PETR4", "GOLD11"]), "20/11/2026, às 23h59"):
        assert valor in material, valor
    assert 'id="preparacao"' in material
    amostra = material.split('id="amostra"')[1].split('<section')[0]
    custo = m.custo_da_janela("PETR4")
    inteira = m.tratamento.retornos_por_ativo()["PETR4"].dropna()
    for valor in ("ADR-009", "24/10/2025", "março de 2020", "Aula 01", "Aula 03", "14/12/2020",
                  "1.423", _pct(custo["serie_inteira"]), _pct(custo["janela_comum"]),
                  _milhar(custo["retornos_serie_inteira"]), inteira.index[0].strftime("%d/%m/%Y")):
        assert valor in amostra, valor
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


# --- notebook: a mesma regra da ADR-009 sem importar tools/ ------------------------

def _notebook():
    with open(NOTEBOOK, encoding="utf-8") as fh:
        return json.load(fh)


def test_notebook_aplica_a_regra_da_adr_009_e_chega_a_mesma_janela():
    celulas = _notebook()["cells"]
    codigo = "".join(celulas[2]["source"])
    assert "import retornos" not in codigo and "tools" not in codigo
    assert ".ffill()" in codigo and "pct_change(fill_method=None)" in codigo
    # Reproduz as três linhas do notebook sobre o mesmo CSV e compara com tools/retornos.py.
    import pandas as pd
    precos = pd.read_csv(os.path.join(m.RAIZ, "dados", "precos_ajustados.csv"),
                         index_col="data", parse_dates=["data"]).ffill()
    retornos = precos.pct_change(fill_method=None).iloc[1:].dropna()
    assert retornos.equals(m.retornos())


def test_notebook_declara_a_janela_e_o_custo():
    texto = "".join(_notebook()["cells"][1]["source"])
    custo = m.custo_da_janela("PETR4")
    for valor in ("ADR-009", "24/10/2025", "Aula 01", "Aula 03", "março de 2020", "1.423",
                  "14/12/2020", _pct(custo["serie_inteira"]), _pct(custo["janela_comum"])):
        assert valor in texto, valor


# --- distribuição dos pesos (C-09): mesma semente, mesmo orçamento ------------------

def _esquemas():
    return m.comparar_esquemas()


def test_uniforme_normalizado_da_comparacao_e_o_motor_da_aula():
    e = _esquemas()["uniforme_normalizado"]
    n = m.nuvem()
    assert e["melhor_sharpe"] == pytest.approx(n["melhor_sharpe"])
    assert e["maior_peso"] == pytest.approx(n["maior_peso_da_nuvem"])
    assert e["abaixo_do_cdi"] == n["abaixo_do_cdi"] == 8851


def test_tres_distribuicoes_com_10000_sorteios_e_semente_42():
    e = _esquemas()
    resumo = {nome: (_r(v["melhor_sharpe"]), _r(v["melhor_maior_peso"]), _r(v["maior_peso"]),
                     _r(v["ativos_efetivos_mediana"]), _r(v["ativos_efetivos_melhor"]),
                     _r(v["fracao_concentrada"]))
              for nome, v in e.items()}
    assert resumo == {
        "uniforme_normalizado": (0.4069, 0.1817, 0.2461, 11.4126, 8.2326, 0.0),
        "dirichlet_1": (0.6399, 0.5526, 0.5974, 8.3663, 3.0466, 0.2621),
        "dirichlet_02": (0.8495, 0.6835, 0.9713, 3.6952, 1.8960, 0.9491),
    }


def test_distribuicao_rende_mais_que_multiplicar_sorteios_e_nenhuma_alcanca_a_otima():
    e = _esquemas()
    otima = m.carteira(m.maximo_sharpe())["sharpe"]
    milhao = m.melhor_por_sorteios((1_000_000,))[1_000_000]
    assert e["dirichlet_1"]["melhor_sharpe"] > milhao
    sharpes = [e[nome]["melhor_sharpe"] for nome, _ in m.ESQUEMAS]
    assert sharpes == sorted(sharpes)
    assert max(sharpes) < otima
    medianas = [e[nome]["ativos_efetivos_mediana"] for nome, _ in m.ESQUEMAS]
    assert medianas == sorted(medianas, reverse=True)


def test_ativos_efetivos_da_otima_e_dos_casos_extremos():
    assert m.ativos_efetivos(np.full(15, 1 / 15))[0] == pytest.approx(15)
    assert m.ativos_efetivos(np.eye(15)[0])[0] == pytest.approx(1)
    assert _r(m.ativos_efetivos(m.maximo_sharpe())[0]) == 2.8216
    # A melhor da Dirichlet(0,2) concentra mais que a ótima.
    assert _esquemas()["dirichlet_02"]["ativos_efetivos_melhor"] < m.ativos_efetivos(m.maximo_sharpe())[0]


def test_no_trio_as_tres_distribuicoes_chegam_a_otima():
    mu, cov = m.trio()
    e = m.comparar_esquemas(mu=mu, cov=cov)
    otima_trio = m.metricas(m.caminho_slsqp_trio()[1], mu, cov)[2]
    for nome, v in e.items():
        assert _r(v["melhor_sharpe"], 2) == 0.92, nome
        assert v["melhor_sharpe"] <= otima_trio + 1e-9


def _numeros_da_comparacao():
    e = _esquemas()
    numeros = []
    for nome, _ in m.ESQUEMAS:
        v = e[nome]
        numeros += [_num(v["melhor_sharpe"]), _pct(v["melhor_maior_peso"]),
                    _num(v["ativos_efetivos_mediana"]), _pct(v["fracao_concentrada"])]
    ms = m.carteira(m.maximo_sharpe())
    numeros += [_num(ms["sharpe"]), _pct(ms["maior_peso"]),
                _num(m.ativos_efetivos(m.maximo_sharpe())[0]),
                _num(m.melhor_por_sorteios((1_000_000,))[1_000_000])]
    return numeros


def _secao(id_):
    for s in _secoes():
        if 'id="%s"' % id_ in s:
            return s
    raise AssertionError(id_)


def test_slide_da_distribuicao_cita_a_comparacao_medida():
    slide = _secao("distribuicao")
    for valor in _numeros_da_comparacao() + ["Uniform(0,1)", "Dirichlet(1)", "Dirichlet(0,2)",
                                              "10.000", "semente 42", "PETR4, IVVB11 e GOLD11"]:
        assert valor in slide, valor
    assert _num(_esquemas()["dirichlet_02"]["melhor_sharpe"]) in re.search(r"<h2>(.*?)</h2>", slide).group(1)
    assert "[9]" in slide
    assert 'id="ref-9"' in _deck() and "DEVROYE" in _deck()


def test_slides_da_nuvem_nomeiam_a_distribuicao_dos_pesos():
    for id_ in ("sorteada-contra-otima", "milhao"):
        assert "Uniform(0,1)" in _secao(id_), id_
    assert "1/15" in _secao("motor")
    assert "uniformes normalizados" not in _deck()
    assert "Pesos sorteados quase nunca concentram" not in _deck()


def test_quiz_final_inclui_a_distribuicao_dos_pesos():
    quiz = _secao("quiz-final")
    certa = re.search(r'data-correct="true"\s+data-correct-msg="([^"]*)"\s+data-incorrect-msg="[^"]*">([^<]*)</li>',
                      quiz)
    assert "distribuição dos pesos" in certa.group(2)
    e = _esquemas()
    for valor in (_pct(m.nuvem()["maior_peso_da_nuvem"]), _num(e["dirichlet_02"]["melhor_sharpe"]),
                  _num(m.carteira(m.maximo_sharpe())["sharpe"])):
        assert valor in certa.group(1), valor


def test_material_cita_a_comparacao_de_distribuicoes():
    with open(os.path.join(m.RAIZ, "materiais", "aula04.html"), encoding="utf-8") as fh:
        material = fh.read()
    for valor in _numeros_da_comparacao() + [_num(_esquemas()["dirichlet_02"]["ativos_efetivos_melhor"]),
                                             "Dirichlet(1)", "Dirichlet(0,2)", "Devroye"]:
        assert valor in material, valor
    assert "uniforme quase nunca" not in material


def test_referencias_trazem_a_amostragem_no_simplex():
    with open(os.path.join(m.RAIZ, "referencias", "aula04.html"), encoding="utf-8") as fh:
        pagina = fh.read()
    complementar = pagina.split('id="complementar"')[1]
    itens = re.findall(r"<li>", complementar.split("</ol>")[0])
    assert len(itens) == 9
    assert "DEVROYE" in complementar and "Dirichlet" in complementar


def test_notas_do_professor_citam_a_comparacao():
    with open(os.path.join(m.RAIZ, "docs", "notas-do-professor", "aula04.md"), encoding="utf-8") as fh:
        notas = fh.read()
    e = _esquemas()
    for valor in (_num(e["dirichlet_1"]["melhor_sharpe"]), _num(e["dirichlet_02"]["melhor_sharpe"]),
                  _num(e["dirichlet_02"]["ativos_efetivos_melhor"]),
                  _num(m.ativos_efetivos(m.maximo_sharpe())[0]), "Slide 14",
                  "A distribuição dos pesos quase nunca concentra"):
        assert valor in notas, valor


def test_notebook_compara_as_tres_distribuicoes():
    celulas = {c.get("id"): c for c in _notebook()["cells"]}
    codigo = "".join(celulas["aula04-09b"]["source"])
    assert "dirichlet" in codigo and "semente=42" in codigo and "10_000" in codigo
    assert "import" not in codigo and "tools" not in codigo
    resposta = "".join(celulas["aula04-09c"]["source"])
    e = _esquemas()
    for valor in (_num(e["dirichlet_1"]["melhor_sharpe"]), _num(e["dirichlet_02"]["melhor_sharpe"]),
                  _num(m.melhor_por_sorteios((1_000_000,))[1_000_000]), "0,92"):
        assert valor in resposta, valor
    texto = json.dumps(_notebook(), ensure_ascii=False)
    assert "quase nunca concentram" not in texto
