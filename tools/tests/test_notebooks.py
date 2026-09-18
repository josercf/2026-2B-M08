"""Estrutura comum dos notebooks: badge do Colab, carga com queda para a URL bruta e nenhuma saída gravada."""
import glob
import json
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTEBOOKS = sorted(glob.glob(os.path.join(RAIZ, "notebooks", "aula*.ipynb")))
COLAB = "https://colab.research.google.com/github/josercf/2026-2B-M08/blob/main/notebooks/%s"
BRUTA = "https://raw.githubusercontent.com/josercf/2026-2B-M08/main/dados/"


def test_existe_ao_menos_um_notebook():
    assert NOTEBOOKS, "nenhum notebook em notebooks/"


@pytest.mark.parametrize("caminho", NOTEBOOKS, ids=os.path.basename)
def test_notebook_segue_o_contrato(caminho):
    with open(caminho, encoding="utf-8") as fh:
        nb = json.load(fh)
    primeira = "".join(nb["cells"][0]["source"])
    assert nb["cells"][0]["cell_type"] == "markdown"
    assert COLAB % os.path.basename(caminho) in primeira
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    assert BRUTA in codigo
    assert "M08_OFFLINE" in codigo
    for celula in nb["cells"]:
        if celula["cell_type"] == "code":
            assert celula.get("outputs") == [], "saída gravada em %s" % os.path.basename(caminho)
            assert celula.get("execution_count") is None
    texto = json.dumps(nb, ensure_ascii=False)
    assert chr(0x2014) not in texto
