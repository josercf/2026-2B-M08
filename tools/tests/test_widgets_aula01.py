"""Os JSON dos widgets da Aula 01 repetem as medições travadas, sem número à mão."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import medidas_aula01 as m  # noqa: E402

DATA = os.path.join(m.RAIZ, "assets", "data")


def _json(nome):
    with open(os.path.join(DATA, nome), encoding="utf-8") as fh:
        return json.load(fh)


def test_tres_visoes_tem_os_cinco_ativos_alinhados_as_datas():
    dados = _json("aula01-tres-visoes.json")
    assert len(dados["datas"]) == 1908
    assert sorted(dados["tickers"]) == ["B3SA3", "BBAS3", "MGLU3", "PETR4", "WEGE3"]
    for ticker, serie in dados["tickers"].items():
        for chave in ("negociado", "fechamento", "ajustado"):
            assert len(serie[chave]) == 1908, (ticker, chave)
        assert serie["leitura"]


def test_tres_visoes_repete_o_salto_medido_de_b3sa3():
    dados = _json("aula01-tres-visoes.json")
    i = dados["datas"].index("2021-05-17")
    b3 = dados["tickers"]["B3SA3"]
    assert (b3["negociado"][i - 1], b3["negociado"][i]) == (53.55, 17.58)
    assert "-67,17%" in b3["leitura"]
    assert "-1,51%" in b3["leitura"]


def test_leitura_da_petr4_cita_os_retornos_medidos():
    leitura = _json("aula01-tres-visoes.json")["tickers"]["PETR4"]["leitura"]
    assert "87,12%" in leitura
    assert "616,00%" in leitura


def test_ausencias_repete_os_tratamentos_medidos():
    dados = _json("aula01-ausencias.json")
    c = m.comparar_tratamentos()
    assert dados["pregoes_total"] == 1908
    assert dados["ausentes"] == {"BOVA11": 1, "IVVB11": 1, "GOLD11": 485}
    assert dados["descartar"]["pregoes"] == 1423
    assert dados["preencher"]["pregoes"] == 1908
    for ativo in dados["ativos"]:
        assert dados["descartar"]["vol"][ativo] == round(float(c["vol_descartar"][ativo]), 4)
        assert dados["preencher"]["vol"][ativo] == round(float(c["vol_preencher"][ativo]), 4)
    assert "1.423" in dados["descartar"]["leitura"]


def test_leitura_do_preencher_cita_a_data_medida_e_os_tres_etfs():
    leitura = _json("aula01-ausencias.json")["preencher"]["leitura"]
    assert m.data_ausencia_compartilhada().strftime("%d/%m/%Y") in leitura
    for ticker in ("BOVA11", "IVVB11", "GOLD11"):
        assert ticker in leitura


def test_tres_visoes_desenha_legenda_das_linhas_ligadas():
    """Revisão de 13/10/2026: o canvas mostrava três linhas sem dizer qual era qual."""
    with open(os.path.join(m.RAIZ, "assets", "js", "widgets", "tres-visoes.js"), encoding="utf-8") as fh:
        js = fh.read()
    legenda = js.split("// Legenda:", 1)[1].split("leitura.textContent", 1)[0]
    assert "estado.ligadas[v.chave]" in legenda
    assert "ctx.fillText(v.rotulo" in legenda
    assert "api.cor(v.token)" in legenda
