"""Medições da Aula 06 sobre os CSVs de dados/, pela própria API de exemplo.

A Aula 06 ensina a API que importa os módulos das sprints anteriores sem copiar
código. Por isso as medições também não copiam: este script carrega a API de
exemplos/aula06-api-carteira/backend/ e mede o que ela devolve para o pedido de
referência da aula, o código de status de cada requisição do montador, quantos
problemas de otimização cada pedido resolve com e sem cache, e o que o
verificador de números acha no texto de interpretação com erros plantados.

Todo número que o deck, o material, as notas, os widgets e as animações da Aula
06 citam sai daqui e está travado em tools/tests/test_aula06.py.
"""
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(RAIZ, "exemplos", "aula06-api-carteira", "backend")

# Pedido de referência da aula: cinco ativos da cesta de dados/README.md, sem
# GOLD11 (que só estreia em 11/12/2020), na janela inteira do snapshot. Não é a
# carteira de nenhuma ponderada.
PEDIDO = {"tickers": ["PETR4", "VALE3", "ITUB4", "WEGE3", "IVVB11"],
          "inicio": "2019-01-01", "fim": "2026-08-31"}
# Segundo pedido da sequência do cache: mesmos ativos, janela a partir de 2021.
PEDIDO_2021 = dict(PEDIDO, inicio="2021-01-01")
# Ordem dos pedidos que cinco gestores fazem na animação do cache.
SEQUENCIA_CACHE = ["A", "A", "B", "A", "B"]

_API = None


def api():
    """O módulo main.py da API de exemplo, carregado com o backend no sys.path."""
    global _API
    if _API is None:
        if BACKEND not in sys.path:
            sys.path.insert(0, BACKEND)
        especificacao = importlib.util.spec_from_file_location(
            "aula06_api_main", os.path.join(BACKEND, "main.py"))
        _API = importlib.util.module_from_spec(especificacao)
        especificacao.loader.exec_module(_API)
    return _API


def cliente():
    from fastapi.testclient import TestClient

    return TestClient(api().app)


def _otimizador():
    return sys.modules["carteira.otimizador"]


def resultado():
    """O JSON que POST /carteiras/otimizar devolve para o pedido de referência."""
    resposta = cliente().post("/carteiras/otimizar", json=PEDIDO)
    resposta.raise_for_status()
    return resposta.json()


def contexto():
    """O recorte em porcentagem que a API manda ao LLM no prompt."""
    return api().interpretacao.contexto(resultado())


def problemas_por_pedido(com_cache):
    """Carteiras calculadas pelo otimizador (duas ótimas e 50 pontos da fronteira) por pedido da sequência.

    Sem cache, cada pedido refaz as duas carteiras ótimas e os 50 pontos da
    fronteira. Com cache, o pedido repetido devolve o resultado guardado.
    """
    modulo = api()
    otimizador = _otimizador()
    pedidos = {"A": PEDIDO, "B": PEDIDO_2021}
    contagem = []
    modulo._calcular.cache_clear()
    for chave in SEQUENCIA_CACHE:
        antes = otimizador.PROBLEMAS_RESOLVIDOS
        if com_cache:
            cliente().post("/carteiras/otimizar", json=pedidos[chave]).raise_for_status()
        else:
            modulo._calcular.__wrapped__(**_argumentos(pedidos[chave]))
        contagem.append(otimizador.PROBLEMAS_RESOLVIDOS - antes)
    modulo._calcular.cache_clear()
    return contagem


def _argumentos(pedido):
    return {"tickers": tuple(pedido["tickers"]), "inicio": pedido["inicio"],
            "fim": pedido["fim"], "rf": None}


# Requisições do widget montador: rota e corpo escolhidos pela turma, com a
# resposta gravada da API de exemplo. A interpretação é gravada sem chave no
# ambiente, e por isso o pedido válido nela devolve 503.
ROTAS = [("GET", "/ativos"), ("POST", "/carteiras/otimizar"), ("POST", "/carteiras/interpretar")]
CORPOS = {
    "valido": ("Pedido de referência", PEDIDO),
    "ticker-inexistente": ("Ticker que não existe", dict(PEDIDO, tickers=["PETR4", "XPTO3"])),
    "um-ticker": ("Um ticker só", dict(PEDIDO, tickers=["PETR4"])),
    "datas-invertidas": ("Início depois do fim", dict(PEDIDO, inicio="2026-08-31", fim="2019-01-01")),
}


def requisicoes():
    """Cada combinação de rota e corpo do montador, com status e resposta gravados."""
    chave_original = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        c = cliente()
        casos = []
        for metodo, rota in ROTAS:
            corpos = [(None, None, None)] if metodo == "GET" else [
                (nome, rotulo, corpo) for nome, (rotulo, corpo) in CORPOS.items()]
            for nome, rotulo, corpo in corpos:
                resposta = c.get(rota) if metodo == "GET" else c.post(rota, json=corpo)
                casos.append({"metodo": metodo, "rota": rota, "corpo_nome": nome,
                              "corpo_rotulo": rotulo, "corpo": corpo,
                              "status": resposta.status_code, "resposta": resposta.json()})
        return casos
    finally:
        if chave_original is not None:
            os.environ["OPENROUTER_API_KEY"] = chave_original


def status_por_caso():
    return {"%s %s %s" % (c["metodo"], c["rota"], c["corpo_nome"] or "-"): c["status"]
            for c in requisicoes()}


def _br(valor, casas=2):
    return ("%.*f" % (casas, valor)).replace(".", ",")


def _milhar(numero):
    return "{:,}".format(numero).replace(",", ".")


def texto_com_erros():
    """Texto de interpretação no estilo de um LLM, com três erros plantados.

    O texto é escrito por este script a partir dos números reais da API e
    declarado como exercício em todo lugar em que aparece: nenhum modelo o
    gerou. Cada erro plantado é de um tipo:

    - valor_alterado: a volatilidade da carteira de máximo Sharpe com dois
      pontos a menos, um número que não existe no JSON;
    - promessa_inventada: um retorno para o próximo ano, número que o JSON não
      tem e frase que o prompt proíbe;
    - ativo_trocado: a correlação média do IVVB11 atribuída à VALE3, número que
      existe no JSON, mas no ativo errado.

    Devolve (texto, erros), com o trecho como aparece no texto e o valor certo.
    """
    c = contexto()
    sharpe = c["maximo_sharpe"]
    minima = c["variancia_minima"]
    ativos = {a["ticker"]: a for a in c["ativos"]}
    pesos = sorted(sharpe["pesos_pct"].items(), key=lambda par: -par[1])
    menor_corr = min(c["ativos"], key=lambda a: a["correlacao_media"])
    vol_errada = round(sharpe["volatilidade_anual_pct"] - 2, 2)
    promessa = 30.0
    maior_minima = max(minima["pesos_pct"].items(), key=lambda par: par[1])

    erros = [
        {"tipo": "valor_alterado", "trecho": _br(vol_errada) + "%",
         "certo": _br(sharpe["volatilidade_anual_pct"]) + "%"},
        {"tipo": "promessa_inventada", "trecho": _br(promessa) + "%",
         "certo": "nenhum: o JSON não tem retorno futuro"},
        {"tipo": "ativo_trocado", "trecho": _br(menor_corr["correlacao_media"]),
         "certo": "o %s é o que mais diversifica, com %s; a VALE3 tem %s" % (
             menor_corr["ticker"], _br(menor_corr["correlacao_media"]),
             _br(ativos["VALE3"]["correlacao_media"]))},
    ]
    texto = (
        "Com %s retornos diários e o CDI de %s%% ao ano como taxa livre de risco, a carteira "
        "de máximo Sharpe concentra %s. Ela tem retorno anual de %s%% com volatilidade de %s%%, "
        "e Sharpe de %s. A carteira de variância mínima reduz a volatilidade para %s%%, com %s%% "
        "em %s. A VALE3 é o ativo que mais diversifica, com correlação média de %s. Se o cenário "
        "se repetir, a carteira de máximo Sharpe deve render %s%% no próximo ano. Esses números "
        "vêm de uma janela passada, e os pesos mudam quando a janela muda."
        % (_milhar(c["pregoes"]), _br(c["taxa_livre_risco_pct"]),
           ", ".join("%s%% em %s" % (_br(p), t) for t, p in pesos[:-1]) + " e %s%% em %s" % (
               _br(pesos[-1][1]), pesos[-1][0]),
           _br(sharpe["retorno_anual_pct"]), _br(vol_errada), _br(sharpe["sharpe"]),
           _br(minima["volatilidade_anual_pct"]), _br(maior_minima[1]), maior_minima[0],
           _br(menor_corr["correlacao_media"]), _br(promessa)))
    return texto, erros


def verificacao_do_texto():
    """O que o verificador da API diz de cada número do texto com erros plantados."""
    texto, _ = texto_com_erros()
    return api().interpretacao.verificar_numeros(texto, resultado())


def resumo():
    """Os números da aula num dicionário só, para o notebook, as notas e a conferência."""
    r = resultado()
    verificacao = verificacao_do_texto()
    return {
        "pregoes": r["pregoes"],
        "taxa_livre_risco": r["taxa_livre_risco"],
        "maximo_sharpe": r["maximo_sharpe"],
        "variancia_minima": r["variancia_minima"],
        "pontos_fronteira": len(r["fronteira"]),
        "status": status_por_caso(),
        "problemas_sem_cache": problemas_por_pedido(False),
        "problemas_com_cache": problemas_por_pedido(True),
        "numeros_no_texto": len(verificacao),
        "numeros_que_nao_conferem": [v["trecho"] for v in verificacao if not v["confere"]],
    }


if __name__ == "__main__":
    print(json.dumps(resumo(), ensure_ascii=False, indent=1))
