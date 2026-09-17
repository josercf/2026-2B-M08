"""Contrato e gravação das animações do acervo.

Toda animação é um MP4 H.264 em yuv420p, 1280x720, 30 quadros por segundo, sem
áudio, com até 60 segundos e 3 MB, acompanhado de um pôster PNG do mesmo
tamanho. O contrato mora aqui e é conferido por tools/tests/test_midia.py com
ffprobe, sem tocar o vídeo.
"""
import json
import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation, font_manager  # noqa: E402

from paleta import cor  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.path.join(RAIZ, "assets", "video")
IMG = os.path.join(RAIZ, "assets", "img")

LARGURA, ALTURA, DPI, FPS = 1280, 720, 100, 30
LIMITE_SEGUNDOS = 60
LIMITE_BYTES = 3 * 1024 * 1024


def _fonte_texto():
    """Manrope quando instalada; DejaVu Sans, que vem com o matplotlib, se não."""
    nomes = {fonte.name for fonte in font_manager.fontManager.ttflist}
    return "Manrope" if "Manrope" in nomes else "DejaVu Sans"


def figura():
    """Figura 1280x720 com fundo, tinta e fonte do tema."""
    plt.rcParams.update({
        "font.family": _fonte_texto(),
        "font.size": 18,
        "text.color": cor("--seg-texto"),
        "axes.labelcolor": cor("--seg-texto"),
        "axes.edgecolor": cor("--seg-borda"),
        "xtick.color": cor("--seg-texto"),
        "ytick.color": cor("--seg-texto"),
        "axes.facecolor": cor("--seg-base"),
        "figure.facecolor": cor("--seg-base"),
        "savefig.facecolor": cor("--seg-base"),
    })
    return plt.figure(figsize=(LARGURA / DPI, ALTURA / DPI), dpi=DPI)


def gravar(fig, desenhar, n_quadros, nome, quadro_poster):
    """Grava assets/video/<nome>.mp4 e assets/img/<nome>-poster.png.

    desenhar(i) atualiza a figura para o quadro i. O pôster é o quadro
    quadro_poster, escolhido para mostrar o conceito inteiro; use o último
    quadro quando a animação acumula elementos.
    """
    os.makedirs(VIDEO, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    mp4 = os.path.join(VIDEO, nome + ".mp4")
    poster = os.path.join(IMG, nome + "-poster.png")
    escritor = animation.FFMpegWriter(
        fps=FPS, codec="libx264",
        extra_args=["-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow",
                    "-movflags", "+faststart", "-an"],
    )
    animacao = animation.FuncAnimation(fig, desenhar, frames=n_quadros, blit=False)
    animacao.save(mp4, writer=escritor, dpi=DPI)
    desenhar(quadro_poster)
    fig.savefig(poster, dpi=DPI)
    plt.close(fig)
    return mp4, poster


def metadados(caminho):
    """Codec, tamanho, formato de pixel, taxa, duração, bytes e áudio, por ffprobe."""
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,pix_fmt,avg_frame_rate:format=duration,size",
         "-of", "json", caminho],
        capture_output=True, text=True, check=True,
    )
    dados = json.loads(saida.stdout)
    videos = [s for s in dados["streams"] if s["codec_type"] == "video"]
    if not videos:
        raise ValueError("%s não tem trilha de vídeo" % caminho)
    video = videos[0]
    return {
        "codec": video["codec_name"],
        "largura": video["width"],
        "altura": video["height"],
        "pix_fmt": video.get("pix_fmt"),
        "fps": video["avg_frame_rate"],
        "duracao": float(dados["format"]["duration"]),
        "bytes": int(dados["format"]["size"]),
        "tem_audio": any(s["codec_type"] == "audio" for s in dados["streams"]),
    }


def violacoes(meta):
    """Quebras do contrato. Lista vazia significa vídeo conforme."""
    erros = []
    if meta["codec"] != "h264":
        erros.append("codec %s, o contrato pede h264" % meta["codec"])
    if (meta["largura"], meta["altura"]) != (LARGURA, ALTURA):
        erros.append("%dx%d, o contrato pede %dx%d"
                     % (meta["largura"], meta["altura"], LARGURA, ALTURA))
    if meta["pix_fmt"] != "yuv420p":
        erros.append("pix_fmt %s, o contrato pede yuv420p" % meta["pix_fmt"])
    if meta["fps"] != "%d/1" % FPS:
        erros.append("taxa %s, o contrato pede %d/1" % (meta["fps"], FPS))
    if meta["duracao"] > LIMITE_SEGUNDOS + 0.5:
        erros.append("%.1f s, o limite é %d s" % (meta["duracao"], LIMITE_SEGUNDOS))
    if meta["bytes"] > LIMITE_BYTES:
        erros.append("%d bytes, o limite é %d" % (meta["bytes"], LIMITE_BYTES))
    if meta["tem_audio"]:
        erros.append("tem trilha de áudio, o contrato pede vídeo mudo")
    return erros
