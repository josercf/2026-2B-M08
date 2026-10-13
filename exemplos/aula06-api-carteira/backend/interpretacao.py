"""Camada de interpretação: prompt montado com os números reais, chamada ao LLM e
verificação de todo número que o texto devolvido cita.

A chamada acontece no servidor. A chave fica na variável de ambiente
OPENROUTER_API_KEY e nunca chega ao navegador; sem ela, chamar_llm levanta
ChaveAusente e a API devolve 503.
"""
import json
import os
import re

URL = "https://openrouter.ai/api/v1/chat/completions"
MODELO_PADRAO = "openai/gpt-4o-mini"

INSTRUCOES = (
    "Você é analista de carteiras e escreve para um gestor financeiro que não programa. "
    "Use apenas os números do JSON abaixo, em porcentagem com duas casas. "
    "Explique por que a carteira de máximo Sharpe tem esses pesos, o que a fronteira diz "
    "sobre o risco e quais ativos mais diversificam (menor correlação média). "
    "Termine com as limitações: os números vêm de uma janela passada e os pesos mudam com ela. "
    "Não recomende compra nem prometa retorno futuro."
)

# Número escrito em português: 1.906, 26,92%, 0,91. O separador de milhar é o
# ponto e o decimal é a vírgula, como o prompt pede ao modelo. Pedaço de data
# (02/01/2019) e de ticker (PETR4) fica de fora da contagem.
NUMERO = re.compile(r"(?<![\w,./])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w/])(\s?%)?")


class ChaveAusente(RuntimeError):
    """OPENROUTER_API_KEY não está definida no ambiente do servidor."""


def _pct(x):
    return round(100 * x, 2)


def contexto(resultado):
    """O recorte do JSON da API que vai para o prompt, em porcentagem."""
    def carteira(c):
        return {"pesos_pct": {t: _pct(p) for t, p in c["pesos"].items() if p >= 0.0005},
                "retorno_anual_pct": _pct(c["retorno"]),
                "volatilidade_anual_pct": _pct(c["volatilidade"]),
                "sharpe": round(c["sharpe"], 2)}
    return {
        "pregoes": resultado["pregoes"],
        "taxa_livre_risco_pct": _pct(resultado["taxa_livre_risco"]),
        "ativos": [{"ticker": a["ticker"], "retorno_anual_pct": _pct(a["retorno"]),
                    "volatilidade_anual_pct": _pct(a["volatilidade"]),
                    "correlacao_media": round(a["correlacao_media"], 2)} for a in resultado["ativos"]],
        "variancia_minima": carteira(resultado["variancia_minima"]),
        "maximo_sharpe": carteira(resultado["maximo_sharpe"]),
    }


def montar_prompt(resultado):
    return INSTRUCOES + "\n\nResultado da otimização:\n" + json.dumps(
        contexto(resultado), ensure_ascii=False, indent=1)


def _folhas(valor, caminho=""):
    """Todos os números do contexto, com o caminho de onde cada um veio."""
    if isinstance(valor, dict):
        for chave, filho in valor.items():
            yield from _folhas(filho, caminho + "." + chave if caminho else chave)
    elif isinstance(valor, list):
        for item in valor:
            rotulo = item.get("ticker", "") if isinstance(item, dict) else ""
            yield from _folhas(item, "%s[%s]" % (caminho, rotulo))
    elif isinstance(valor, (int, float)) and not isinstance(valor, bool):
        yield caminho, valor


def numeros_citados(texto):
    """Cada número do texto, na ordem: (trecho como escrito, valor, é porcentagem)."""
    achados = []
    for casamento in NUMERO.finditer(texto):
        inteiro, decimal, pct = casamento.groups()
        valor = float(inteiro.replace(".", "") + ("." + decimal if decimal else ""))
        achados.append((casamento.group(0).strip(), valor, bool(pct)))
    return achados


def verificar_numeros(texto, resultado):
    """Confere cada número do texto contra o contexto que foi para o prompt.

    Um número confere quando aparece em algum lugar do contexto com o mesmo
    valor (porcentagem com o campo em porcentagem, número puro com número puro).
    É uma verificação de presença: ela pega número inventado e número com
    arredondamento errado, mas não pega número certo atribuído ao ativo
    errado, que continua exigindo leitura humana ou uma regra mais estrita.
    """
    folhas = list(_folhas(contexto(resultado)))
    saida = []
    for trecho, valor, eh_pct in numeros_citados(texto):
        candidatos = [caminho for caminho, v in folhas
                      if ("pct" in caminho) == eh_pct and abs(float(v) - valor) < 0.005]
        saida.append({"trecho": trecho, "valor": valor, "confere": bool(candidatos),
                      "origem": candidatos[0] if candidatos else None})
    return saida


def chamar_llm(prompt, timeout=60):
    """Texto do modelo e nome do modelo. Só roda no servidor, com a chave no ambiente."""
    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        raise ChaveAusente()
    import httpx  # só no servidor que chama o LLM

    modelo = os.environ.get("LLM_MODELO", MODELO_PADRAO)
    resposta = httpx.post(URL, timeout=timeout, headers={"Authorization": "Bearer " + chave},
                          json={"model": modelo, "temperature": 0.2,
                                "messages": [{"role": "user", "content": prompt}]})
    resposta.raise_for_status()
    return resposta.json()["choices"][0]["message"]["content"], modelo
