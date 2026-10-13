"""JSON dos widgets da Aula 06, a partir de tools/medidas_aula06.py.

Uso: .venv/bin/python tools/dados_widgets_aula06.py
Saída:
- assets/data/aula06-requisicoes.json: as nove combinações de rota e corpo do
  montador de requisição, com o status e a resposta gravados da API de exemplo;
- assets/data/aula06-verificador.json: o texto de interpretação com três erros
  plantados, declarado como exercício, e o que o verificador da API diz de cada
  número dele.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula06 as m  # noqa: E402

SAIDA = os.path.join(m.RAIZ, "assets", "data")
PONTOS_EXIBIDOS = 2


def _arredondar(valor):
    if isinstance(valor, float):
        return round(valor, 4)
    if isinstance(valor, list):
        return [_arredondar(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _arredondar(v) for k, v in valor.items()}
    return valor


def _texto_resposta(resposta):
    """JSON da resposta como o navegador mostraria, com a fronteira encurtada.

    A fronteira tem 50 pares; o slide mostra os dois primeiros e diz quantos
    ficaram de fora, para a resposta caber na caixa sem esconder o tamanho dela.
    """
    resposta = _arredondar(resposta)
    if isinstance(resposta, dict) and "fronteira" in resposta:
        total = len(resposta["fronteira"])
        resposta = dict(resposta, fronteira=resposta["fronteira"][:PONTOS_EXIBIDOS]
                        + ["... mais %d pares (volatilidade, retorno)" % (total - PONTOS_EXIBIDOS)])
    if isinstance(resposta, dict) and "ativos" in resposta:
        resposta = dict(resposta, ativos=resposta["ativos"][:1]
                        + ["... mais %d ativos" % (len(resposta["ativos"]) - 1)])
    return json.dumps(resposta, ensure_ascii=False, indent=2)


def requisicoes():
    casos = m.requisicoes()
    return {
        "rotas": ["%s %s" % rota for rota in m.ROTAS],
        "corpos": [{"nome": nome, "rotulo": rotulo} for nome, (rotulo, _) in m.CORPOS.items()],
        "casos": [{
            "chave": "%s %s|%s" % (c["metodo"], c["rota"], c["corpo_nome"] or "-"),
            "metodo": c["metodo"],
            "rota": c["rota"],
            "corpo": json.dumps(c["corpo"], ensure_ascii=False, indent=1) if c["corpo"] else "",
            "status": c["status"],
            "resposta": _texto_resposta(c["resposta"]),
        } for c in casos],
    }


def verificador():
    texto, erros = m.texto_com_erros()
    verificacao = m.verificacao_do_texto()
    conferem = sum(1 for v in verificacao if v["confere"])
    return {
        "aviso": "Texto escrito para o exercício com três erros plantados. Nenhum modelo o gerou.",
        "texto": texto,
        "numeros": verificacao,
        "erros": erros,
        "leitura": ("O verificador confere %d de %d números e acusa %d; dos %d que passam, %d estão "
                    "certos. O terceiro erro plantado passa: o número existe no JSON, mas pertence "
                    "a outro ativo." % (conferem, len(verificacao), len(verificacao) - conferem,
                                         conferem, conferem - (len(erros) - (len(verificacao) - conferem)))),
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, dados in (("aula06-requisicoes.json", requisicoes()),
                        ("aula06-verificador.json", verificador())):
        with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
        print("gravado:", nome, os.path.getsize(os.path.join(SAIDA, nome)), "bytes")


if __name__ == "__main__":
    main()
