"""Contrato das animações: arquivo, pôster, codec, tamanho, duração e uso.

Mede por ffprobe, sem tocar o vídeo: o Chromium do Playwright não tem H.264.
"""
import glob
import os
import re
import struct
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import midia  # noqa: E402

PAGINAS = sorted(glob.glob(os.path.join(midia.RAIZ, "aulas", "*.html"))
                 + glob.glob(os.path.join(midia.RAIZ, "materiais", "*.html")))
TAG_VIDEO = re.compile(r"<video\b.*?</video>", re.S)
SRC = re.compile(r'\bsrc\s*=\s*"([^"]+)"')
POSTER = re.compile(r'\bposter\s*=\s*"([^"]+)"')


def _tags():
    for pagina in PAGINAS:
        with open(pagina, encoding="utf-8") as fh:
            for tag in TAG_VIDEO.findall(fh.read()):
                yield pagina, tag


def _resolver(pagina, alvo):
    return os.path.normpath(os.path.join(os.path.dirname(pagina), alvo))


def _dimensoes_png(caminho):
    with open(caminho, "rb") as fh:
        cabecalho = fh.read(24)
    assert cabecalho[:8] == b"\x89PNG\r\n\x1a\n", "%s não é PNG" % caminho
    return struct.unpack(">II", cabecalho[16:24])


TAGS = list(_tags())
VIDEOS = sorted(glob.glob(os.path.join(midia.VIDEO, "*.mp4")))


@pytest.mark.parametrize("pagina,tag", TAGS,
                         ids=["%s-%d" % (os.path.basename(p), i) for i, (p, _) in enumerate(TAGS)])
def test_video_referenciado_existe_tem_poster_e_atributos(pagina, tag):
    fontes = SRC.findall(tag)
    assert fontes, "<video> sem <source src> em %s" % pagina
    for fonte in fontes:
        assert os.path.isfile(_resolver(pagina, fonte)), fonte
    posters = POSTER.findall(tag)
    assert posters, "<video> sem poster em %s" % pagina
    assert _dimensoes_png(_resolver(pagina, posters[0])) == (midia.LARGURA, midia.ALTURA)
    abertura = tag.split(">", 1)[0]
    for atributo in ("controls", "muted", "playsinline"):
        assert re.search(r"\b%s\b" % atributo, abertura), atributo


@pytest.mark.parametrize("video", VIDEOS, ids=os.path.basename)
def test_video_cumpre_o_contrato(video):
    assert midia.violacoes(midia.metadados(video)) == []


@pytest.mark.parametrize("video", VIDEOS, ids=os.path.basename)
def test_video_nao_esta_orfao(video):
    usados = {_resolver(p, s) for p, t in TAGS for s in SRC.findall(t)}
    assert os.path.normpath(video) in usados, "nenhuma página usa %s" % video


def test_gravar_produz_video_conforme(tmp_path, monkeypatch):
    monkeypatch.setattr(midia, "VIDEO", str(tmp_path))
    monkeypatch.setattr(midia, "IMG", str(tmp_path))
    fig = midia.figura()
    eixo = fig.add_subplot()
    eixo.set_xlim(0, 30)
    eixo.set_ylim(0, 30)
    ponto, = eixo.plot([0], [0], "o")

    def desenhar(i):
        ponto.set_data([i], [i])

    mp4, poster = midia.gravar(fig, desenhar, 30, "ensaio", 29)
    assert midia.violacoes(midia.metadados(mp4)) == []
    assert _dimensoes_png(poster) == (1280, 720)


def test_violacoes_acusa_video_fora_do_contrato(tmp_path):
    saida = str(tmp_path / "fora.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
                    "-f", "lavfi", "-i", "sine=frequency=440", "-t", "1",
                    "-c:v", "libx264", "-pix_fmt", "yuv444p", "-c:a", "aac", saida], check=True)
    erros = " | ".join(midia.violacoes(midia.metadados(saida)))
    for trecho in ("640x360", "yuv444p", "25/1", "áudio"):
        assert trecho in erros, trecho
