"""Adaptações da base do M03 para o repositório do M08."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_brand  # noqa: E402
import check_links  # noqa: E402


def test_link_do_notebook_aponta_para_o_repositorio_do_m08():
    assert check_links.REPO_BLOB == "https://github.com/josercf/2026-2B-M08/blob/main/"


def test_validadores_ignoram_ambiente_virtual_e_worktrees():
    for pasta in (".venv", ".claude"):
        assert pasta in check_brand.IGNORAR, pasta
        assert pasta in check_links.IGNORAR, pasta
