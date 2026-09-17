"""Regressao da flakiness relatada no Task 6: uma conexao TCP aberta e muda
nao pode travar a proxima requisicao real do servidor de teste.

O Chromium abre conexoes especulativas de preconexao que as vezes nao chegam
a mandar nenhum byte. Um servidor de uma thread so (socketserver.TCPServer)
aceita essa conexao ociosa e fica preso dentro do readline() dela, porque nao
ha nada para ler; nenhuma outra requisicao e atendida ate ela fechar. Isso
apareceu no Chromium como net::ERR_CONNECTION_RESET ou
net::ERR_SOCKET_NOT_CONNECTED num recurso aleatorio da pagina, sem relacao
com o conteudo servido. Ver check_slides.servir().
"""
import os
import socket
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import check_slides  # noqa: E402


def test_conexao_ociosa_nao_trava_a_proxima_requisicao_real():
    porta = check_slides.porta_livre()
    httpd = check_slides.servir(porta)
    # Conexao TCP crua que completa o handshake e nao manda nenhum byte, como
    # a preconexao especulativa do Chromium. Um pequeno respiro depois de
    # abri-la da tempo do servidor aceitar essa conexao primeiro, para o
    # teste reproduzir o travamento de forma deterministica, e nao por sorte
    # de agendamento de thread.
    ociosa = socket.create_connection(("127.0.0.1", porta), timeout=3)
    try:
        time.sleep(0.2)
        url = "http://127.0.0.1:%d/aulas/_fixture-tema.html" % porta
        with urllib.request.urlopen(url, timeout=3) as resposta:
            assert resposta.status == 200
    finally:
        ociosa.close()
        httpd.shutdown()
