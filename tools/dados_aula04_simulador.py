"""Cotações da Aula 04 em turnos: portal de simulação, kit e notebook.

Fica fora de dados/ de propósito: o snapshot do case termina em 31/08/2026 e
tem 15 ativos, e a aula parte da carteira que cada grupo montou na aula de
Negócios, com ativos escolhidos por eles e preço de referência de 13/11/2026
(ADR-018). Rodar de novo sobrescreve os três arquivos e precisa de rede.

Saídas:
  assets/data/aula04-cotacoes.json             portal
  exemplos/aula04-simulador/dados/precos.csv   kit e notebook
  exemplos/aula04-simulador/dados/rf.txt       taxa livre de risco anual

Regra de ausência, a mesma da ADR-009: lacuna isolada é preenchida com o último
preço e nada é preenchido antes da primeira cotação do ativo.
"""
import json
import os
import time
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INICIO = "2024-01-02"
CORTE = "2026-11-13"
MINIMO_COTACOES = 253
PREGOES_ANO = 252

IBRX = """ABEV3 ALOS3 ALPA4 ASAI3 AURE3 AZUL4 AZZA3 B3SA3 BBAS3 BBDC3 BBDC4 BBSE3 BEEF3 BPAC11
BRAP4 BRAV3 BRFS3 BRKM5 CAML3 CMIG4 CMIN3 COGN3 CPFE3 CPLE6 CSAN3 CSMG3 CSNA3 CURY3 CVCB3 CXSE3
CYRE3 DIRR3 DXCO3 ECOR3 EGIE3 ELET3 ELET6 EMBR3 ENEV3 ENGI11 EQTL3 EZTC3 FLRY3 GGBR4 GGPS3 GMAT3
GOAU4 HAPV3 HYPE3 IGTI11 INTB3 IRBR3 ISAE4 ITSA4 ITUB4 JBSS3 KLBN11 LREN3 LWSA3 MGLU3 MOVI3 MRFG3
MRVE3 MULT3 NATU3 NEOE3 ODPV3 PCAR3 PETR3 PETR4 PETZ3 POMO4 PRIO3 PSSA3 RADL3 RAIL3 RAIZ4 RAPT4
RDOR3 RECV3 RENT3 SANB11 SAPR11 SBSP3 SLCE3 SMFT3 SMTO3 SRNA3 STBP3 SUZB3 TAEE11 TIMS3 TOTS3
TTEN3 TUPY3 UGPA3 USIM5 VALE3 VAMO3 VBBR3 VIVA3 VIVT3 WEGE3 YDUQ3""".split()
ETFS = "BOVA11 IVVB11 GOLD11 SMAL11 DIVO11 HASH11 NASD11 XINA11 B5P211 IMAB11".split()
FIIS = "HGLG11 KNRI11 MXRF11 XPML11 VISC11 XPLG11 KNCR11 HGRU11 BTLG11 TRXF11".split()
NOVOS = "AXIA3 AXIA6 EMBJ3 JBSS32 CPLE3 MBRF3 SBFG3 CEAB3 POSI3 ITUB3 SANB3 BBDC4 KLBN4 UNIP6 FESA4 ALUP11 CPFE3 TRPL4 LEVE3 SIMH3 JHSF3 TEND3 PLPL3 ANIM3 ONCO3 BLAU3 MDIA3 ARML3 KEPL3 ROMI3 VULC3 GRND3 BMOB3 CASH3 LJQQ3 MLAS3 AMER3 HBSA3 PORT3 JSLG3 TGMA3 SEER3 BRSR6 ABCB4 BMGB4 BPAN4".split()
BDRS = "AAPL34 MSFT34 AMZO34 GOGL34 NVDC34 TSLA34 M1TA34 MELI34 BERK34 JPMC34 DISB34 NFLX34".split()
UNIVERSO = sorted(set(IBRX + NOVOS + ETFS + FIIS + BDRS))

URL_SGS = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
           "?formato=json&dataInicial={inicio}&dataFinal={fim}")


def _data_br(iso):
    ano, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{ano}"


def baixar_precos():
    import pandas as pd
    import yfinance as yf

    fim = (pd.Timestamp(CORTE) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    partes = []
    for i in range(0, len(UNIVERSO), 40):
        lote = [t + ".SA" for t in UNIVERSO[i:i + 40]]
        bruto = yf.download(lote, start=INICIO, end=fim, auto_adjust=True,
                            progress=False, threads=True)["Close"]
        partes.append(bruto)
    precos = pd.concat(partes, axis=1)
    precos.columns = [c.replace(".SA", "") for c in precos.columns]
    precos = precos.loc[INICIO:CORTE]
    # Pregão é a data em que a cesta de referência negociou.
    precos = precos[precos["PETR4"].notna()]
    precos = precos.ffill()  # nunca preenche antes da primeira cotação
    validos = [t for t in precos.columns
               if precos[t].notna().sum() >= MINIMO_COTACOES and (precos[t].dropna() > 0).all()]
    return precos[sorted(validos)].round(4)


def baixar_rf(datas):
    """CDI composto nos 252 pregões até o corte, em taxa anual."""
    inicio = datas[-(PREGOES_ANO + 1)]
    url = URL_SGS.format(inicio=_data_br(inicio), fim=_data_br(CORTE))
    ultimo_erro = None
    for _ in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as resposta:
                linhas = json.loads(resposta.read().decode("utf-8"))
            taxas = [float(l["valor"]) / 100 for l in linhas][-PREGOES_ANO:]
            fator = 1.0
            for taxa in taxas:
                fator *= 1 + taxa
            return fator ** (PREGOES_ANO / len(taxas)) - 1
        except Exception as erro:  # a API devolve HTML de vez em quando
            ultimo_erro = erro
            time.sleep(3)
    raise RuntimeError(f"série 12 do SGS indisponível: {ultimo_erro}")


def gravar(precos, rf):
    datas = [d.strftime("%Y-%m-%d") for d in precos.index]
    saida = {
        "corte": CORTE,
        "inicio": INICIO,
        "rf_anual": rf,
        "datas": datas,
        "precos": {t: [None if v != v else float(v) for v in precos[t].tolist()]
                   for t in precos.columns},
    }
    destino = os.path.join(RAIZ, "assets", "data", "aula04-cotacoes.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(saida, fh, separators=(",", ":"))
    pasta = os.path.join(RAIZ, "exemplos", "aula04-simulador", "dados")
    os.makedirs(pasta, exist_ok=True)
    tabela = precos.copy()
    tabela.index = datas
    tabela.index.name = "data"
    tabela.to_csv(os.path.join(pasta, "precos.csv"), float_format="%.4f")
    with open(os.path.join(pasta, "rf.txt"), "w", encoding="utf-8") as fh:
        fh.write(repr(rf) + "\n")


def main():
    precos = baixar_precos()
    datas = [d.strftime("%Y-%m-%d") for d in precos.index]
    rf = baixar_rf(datas)
    gravar(precos, rf)
    fora = sorted(set(UNIVERSO) - set(precos.columns))
    print(f"{len(precos.columns)} ativos, {len(precos)} pregões, "
          f"{datas[0]} a {datas[-1]}, rf {rf:.4%}")
    print("sem dado suficiente:", ", ".join(fora) or "nenhum")


if __name__ == "__main__":
    main()
