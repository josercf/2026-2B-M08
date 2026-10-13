"""API da ferramenta de simulação de carteira (exemplo da Aula 06).

Rotas organizadas por operação de negócio. Os cálculos vêm do pacote carteira,
que representa os artefatos A1, A2 e A4: a API importa esse código sem copiá-lo.

Rodar: fastapi dev main.py   (documentação automática em http://127.0.0.1:8000/docs)

CORS: o React do Vite roda em http://localhost:5173, outra origem; sem o
middleware abaixo, o navegador bloqueia a resposta mesmo com a API respondendo
200. A origem permitida vem de FRONTEND_ORIGEM quando definida.
"""
import os
import csv
import io
from datetime import date
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from carteira import dados, otimizador, pipeline
import interpretacao

app = FastAPI(title="Simulador de carteira eficiente", version="0.6.0")
app.add_middleware(CORSMiddleware,
                   allow_origins=[os.environ.get("FRONTEND_ORIGEM", "http://localhost:5173")],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class PedidoCarteira(BaseModel):
    tickers: list[str] = Field(min_length=2, max_length=15, examples=[["PETR4", "VALE3", "ITUB4"]])
    inicio: date = date(2019, 1, 1)
    fim: date = date(2026, 8, 31)
    taxa_livre_risco: float | None = Field(default=None, ge=0, le=1)

    @field_validator("tickers")
    @classmethod
    def normalizar(cls, tickers):
        return [t.strip().upper() for t in tickers]

    @model_validator(mode="after")
    def conferir(self):
        if self.inicio >= self.fim:
            raise ValueError("inicio precisa ser anterior a fim")
        if len(set(self.tickers)) != len(self.tickers):
            raise ValueError("ticker repetido na lista")
        return self


class Ativo(BaseModel):
    ticker: str
    retorno: float
    volatilidade: float
    correlacao_media: float


class Carteira(BaseModel):
    pesos: dict[str, float]
    retorno: float
    volatilidade: float
    sharpe: float


class Resultado(BaseModel):
    tickers: list[str]
    inicio_janela: str
    fim_janela: str
    pregoes: int
    taxa_livre_risco: float
    ativos: list[Ativo]
    variancia_minima: Carteira
    maximo_sharpe: Carteira
    fronteira: list[tuple[float, float]]


class NumeroConferido(BaseModel):
    trecho: str
    valor: float
    confere: bool
    origem: str | None


class Interpretacao(BaseModel):
    prompt: str
    texto: str
    modelo: str
    verificacao: list[NumeroConferido]


@lru_cache(maxsize=64)
def _calcular(tickers, inicio, fim, rf):
    """Mesma consulta (tickers, período e taxa) devolve o resultado guardado."""
    try:
        return Resultado(**pipeline.calcular(tickers, inicio, fim, rf))
    except dados.TickerDesconhecido as erro:
        raise HTTPException(404, "Ticker fora da base: " + ", ".join(erro.tickers))
    except dados.PeriodoSemDados as erro:
        raise HTTPException(422, "Período sem dados suficientes: " + str(erro))
    except otimizador.NaoConvergiu as erro:
        raise HTTPException(422, "Otimização sem solução para este pedido: " + str(erro))


def calcular(pedido: PedidoCarteira) -> Resultado:
    return _calcular(tuple(pedido.tickers), pedido.inicio.isoformat(),
                     pedido.fim.isoformat(), pedido.taxa_livre_risco)


@app.get("/ativos")
def listar_ativos() -> list[str]:
    """Tickers que a base do acervo cobre."""
    return dados.tickers_disponiveis()


@app.post("/carteiras/otimizar")
def otimizar(pedido: PedidoCarteira) -> Resultado:
    """Métricas por ativo, as duas carteiras ótimas e a fronteira de 50 pontos."""
    return calcular(pedido)


@app.post("/carteiras/interpretar")
def interpretar(pedido: PedidoCarteira) -> Interpretacao:
    """Texto em português do LLM, montado com os números de /carteiras/otimizar.

    Todo número do texto volta conferido contra o mesmo JSON que foi no prompt.
    """
    resultado = calcular(pedido).model_dump()
    prompt = interpretacao.montar_prompt(resultado)
    try:
        texto, modelo = interpretacao.chamar_llm(prompt)
    except interpretacao.ChaveAusente:
        raise HTTPException(503, "Interpretação indisponível: chave do LLM ausente no servidor")
    except Exception as erro:  # rede, cota ou modelo fora do ar no provedor
        raise HTTPException(502, "O provedor do LLM falhou: " + type(erro).__name__)
    return Interpretacao(prompt=prompt, texto=texto, modelo=modelo,
                         verificacao=interpretacao.verificar_numeros(texto, resultado))


@app.post("/carteiras/exportar", response_class=PlainTextResponse)
def exportar(pedido: PedidoCarteira) -> str:
    """Pesos das duas carteiras ótimas em CSV, para o gestor abrir na planilha."""
    resultado = calcular(pedido)
    saida = io.StringIO()
    escritor = csv.writer(saida)
    escritor.writerow(["ticker", "peso_variancia_minima", "peso_maximo_sharpe"])
    for t in resultado.tickers:
        escritor.writerow([t, round(resultado.variancia_minima.pesos[t], 6),
                           round(resultado.maximo_sharpe.pesos[t], 6)])
    return saida.getvalue()
