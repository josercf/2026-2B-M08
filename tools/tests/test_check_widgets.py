import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("playwright.sync_api")

import check_slides  # noqa: E402
import check_widgets  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def porta():
    numero = check_slides.porta_livre()
    httpd = check_slides.servir(numero)
    yield numero
    httpd.shutdown()


def _checar(porta, nome):
    [resultado] = check_widgets.checar([os.path.join(AQUI, nome)], porta)
    return resultado


def test_widget_que_monta_passa(porta):
    r = _checar(porta, "fixture_widget_ok.html")
    assert (r["declarados"], r["medidos"]) == (1, 1)
    assert r["problemas"] == []


def test_widget_que_lanca_erro_reprova(porta):
    problemas = " | ".join(_checar(porta, "fixture_widget_erro.html")["problemas"])
    assert "não montou" in problemas
    assert "falha proposital" in problemas


def test_widget_sem_registro_reprova(porta):
    assert any("não montou" in p for p in _checar(porta, "fixture_widget_sem_registro.html")["problemas"])


def test_fonte_de_dados_inexistente_reprova(porta):
    assert any("não montou" in p for p in _checar(porta, "fixture_widget_fonte_quebrada.html")["problemas"])


def test_widget_declarado_e_nao_medido_reprova(porta):
    r = _checar(porta, "fixture_widget_removido.html")
    assert (r["declarados"], r["medidos"]) == (1, 0)
    assert any("nenhum para medir" in p for p in r["problemas"])


def test_main_sem_deck_reprova(monkeypatch):
    monkeypatch.setattr(check_widgets, "_descobrir", lambda: [])
    assert check_widgets.main([]) == 1


def test_main_com_deck_inexistente_reprova():
    assert check_widgets.main(["aulas/nao-existe.html"]) == 1


def test_fixture_do_tema_monta_o_widget_de_demonstracao():
    assert check_widgets.main([os.path.join(check_widgets.RAIZ, "aulas", "_fixture-tema.html")]) == 0
