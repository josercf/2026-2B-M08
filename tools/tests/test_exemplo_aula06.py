"""A API e a tela de exemplo da Aula 06 passam nos próprios testes, e nenhuma chave vaza.

Os testes do backend rodam em subprocesso, dentro de backend/, como o aluno
roda: assim o main.py, o carteira/ e o interpretacao.py do exemplo não se
misturam com os módulos de tools/ no mesmo processo. Os testes do frontend
usam node --test e ficam de fora quando o node não está instalado.
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEMPLO = os.path.join(RAIZ, "exemplos", "aula06-api-carteira")
BACKEND = os.path.join(EXEMPLO, "backend")
FRONTEND = os.path.join(EXEMPLO, "frontend")

# Formato das chaves da OpenRouter e da OpenAI. O valor falso dos testes
# ("sk-or-teste-nao-e-chave") é curto demais para casar.
CHAVE = re.compile(r"sk-(?:or-v1-)?[A-Za-z0-9]{32,}")


def test_backend_passa_nos_proprios_testes():
    pytest.importorskip("fastapi")
    pytest.importorskip("scipy")
    pytest.importorskip("httpx")
    ambiente = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    ambiente.pop("OPENROUTER_API_KEY", None)
    saida = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-W", "ignore"],
        cwd=BACKEND, env=ambiente, capture_output=True, text=True, timeout=300)
    assert saida.returncode == 0, saida.stdout[-3000:] + saida.stderr[-2000:]
    # Contagem exata de testes travava a suíte a cada teste novo do backend.
    assert " passed" in saida.stdout and "failed" not in saida.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="node não instalado")
def test_cliente_do_frontend_passa_nos_proprios_testes():
    # Os arquivos vão um a um: "node --test src/" só aceita diretório a partir do
    # Node 21 e falha no Node 18 e 20 com "Cannot find module".
    testes = sorted(os.path.join("src", n) for n in os.listdir(os.path.join(FRONTEND, "src"))
                    if n.endswith(".test.js"))
    assert testes, "nenhum src/*.test.js no frontend"
    saida = subprocess.run(["node", "--test", *testes], cwd=FRONTEND,
                           capture_output=True, text=True, timeout=120)
    assert saida.returncode == 0, saida.stdout[-3000:] + saida.stderr[-2000:]
    assert re.search(r"pass 8\b", saida.stdout)


def test_nenhuma_chave_no_exemplo_e_env_so_de_exemplo():
    for pasta, subs, nomes in os.walk(EXEMPLO):
        subs[:] = [s for s in subs if s not in {"node_modules", "__pycache__", ".venv", "dist"}]
        for nome in nomes:
            assert nome != ".env", "arquivo .env com segredo em %s" % pasta
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8", errors="ignore") as fh:
                assert not CHAVE.search(fh.read()), "chave de API em %s" % caminho


def test_env_example_deixa_a_chave_vazia():
    with open(os.path.join(BACKEND, ".env.example"), encoding="utf-8") as fh:
        linhas = dict(l.split("=", 1) for l in fh.read().splitlines() if "=" in l and not l.startswith("#"))
    assert linhas["OPENROUTER_API_KEY"] == ""


def test_frontend_nao_chama_o_provedor_do_llm():
    """A chamada ao LLM é do backend: nenhum arquivo do frontend fala com a OpenRouter."""
    for pasta, subs, nomes in os.walk(os.path.join(FRONTEND, "src")):
        for nome in nomes:
            with open(os.path.join(pasta, nome), encoding="utf-8") as fh:
                texto = fh.read()
            assert "openrouter" not in texto.lower(), nome
            assert "OPENROUTER_API_KEY" not in texto, nome
