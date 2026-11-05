"""Gera os quatro decks de grupo da Aula 02 (aulas/aula02-g01.html a g04.html).

Cada grupo recebe a afirmação de um assessor, um ponto de partida no notebook,
a ADR online com o prazo do professor e o roteiro da defesa no comitê. Os
números das afirmações saem de medidas_aula02.afirmacoes_grupos(). O que
confirma ou desmonta cada afirmação não entra aqui: fica no gabarito, fora do
repositório.

    .venv/bin/python tools/gerar_decks_grupos_aula02.py
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import medidas_aula02 as m  # noqa: E402

SESSAO = "m08-aula02-2026-11-05"
NOTEBOOK = "https://github.com/josercf/2026-2B-M08/blob/main/notebooks/aula02.ipynb"


def conteudo():
    a = m.afirmacoes_grupos()
    return {
        "G01": {
            "ativo": "BBAS3",
            "afirmacao": "O BBAS3 deu prejuízo de %s entre 2019 e 2026." % a["bbas3_close"],
            "passos": [
                "Refaçam a conta do assessor: primeiro e último preço do BBAS3 na janela do snapshot.",
                "Repitam a conta com o outro arquivo de preço de <code>dados/</code> e comparem os dois resultados.",
                "Decidam qual dos números um cliente que comprou em 2019 e segurou até 2026 viveu de fato.",
            ],
        },
        "G02": {
            "ativo": "MGLU3",
            "afirmacao": "A MGLU3 caiu %s desde 2019. Uma alta de %s devolve o cliente ao zero a zero." % (
                a["mglu3_queda"], a["mglu3_queda"]),
            "passos": [
                "Comecem com R$ 100. Apliquem a queda de %s e, em seguida, a alta de %s. Onde o cliente termina?"
                % (a["mglu3_queda"], a["mglu3_queda"]),
                "Calculem a alta que a MGLU3 precisa, a partir do último preço, para voltar ao preço do "
                "primeiro pregão de 2019.",
                "Escrevam a regra em código: depois de uma queda de <code>x</code>, qual alta devolve o "
                "ponto de partida?",
            ],
        },
        "G03": {
            "ativo": "PETR4",
            "afirmacao": "A PETR4 tem volatilidade de %s ao ano, então o pior que acontece em um ano é perder %s."
                         % (a["petr4_vol"], a["petr4_vol"]),
            "passos": [
                "Confirmem a volatilidade anual da PETR4: desvio padrão dos retornos diários vezes a raiz de 252.",
                "Meçam a pior perda real em três escalas: o pior dia, a pior janela de 252 pregões e a queda "
                "do pico ao fundo.",
                "Comparem cada perda com os %s do assessor e escrevam o que o desvio padrão mede." % a["petr4_vol"],
            ],
        },
        "G04": {
            "ativo": "WEGE3",
            "afirmacao": "A WEGE3 ganhou da renda fixa no período.",
            "passos": [
                "Meçam o retorno total da WEGE3 na janela, com a visão de preço que o coletor da Aula 01 adotou.",
                "Calculem quanto R$ 100 viraram no CDI no mesmo período (<code>cdi_diario.csv</code>) e quanto "
                "a inflação levou (<code>ipca_mensal.csv</code>).",
                "Verifiquem se a conclusão muda quando a data de compra muda.",
            ],
        },
    }


CAMPOS = [
    ("titulo", "Título da decisão", "uma linha", "input"),
    ("contexto", "Contexto e problema", "a frase do assessor e o dado que vocês usaram", "textarea"),
    ("criterios", "Critérios de decisão", "o que pesa para o cliente", "textarea"),
    ("opcoes", "Opções consideradas", "o que o comitê pode fazer com a frase", "textarea"),
    ("decisao", "Decisão", "a afirmação é sustentada ou enganosa, e por quê", "textarea"),
    ("impacto", "Consequências", "o número que muda a decisão do cliente", "textarea"),
]


def _rodape(grupo, pagina):
    return """        <div class="slide-footer">
          <p class="footer-bar">Módulo 08 AdmTech &middot; Aula 02 &middot; Grupo %s</p>
          <p class="footer-page">%d</p>
        </div>""" % (grupo, pagina)


def _topo(titulo, extra=""):
    return """        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-positiva.svg" alt="Logo Inteli">
        <div class="slide-title-area%s">
          <div>
            <div class="accent-bar"></div>
            <h2>%s</h2>
          </div>%s
        </div>""" % (" slide-title-area-cronometro" if extra else "", titulo, extra)


def _formulario(grupo):
    blocos = []
    for nome, rotulo, dica, tipo in CAMPOS:
        if tipo == "input":
            controle = '<input id="adr-%s" name="%s" type="text" maxlength="200" autocomplete="off">' % (nome, nome)
        else:
            controle = '<textarea id="adr-%s" name="%s" maxlength="4000"></textarea>' % (nome, nome)
        blocos.append("""            <div data-campo="%s">
              <label for="adr-%s">%s <small>%s</small></label>
              %s
            </div>""" % (nome, nome, rotulo, dica, controle))
    return """        <div class="adr-area">
          <form class="adr-online" data-adr data-sessao="%s" data-grupo="%s">
%s
            <div class="adr-rodape">
              <p class="adr-estado">Conectando...</p>
              <button type="button" class="adr-baixar">Baixar ADR em Markdown</button>
            </div>
          </form>
        </div>""" % (SESSAO, grupo, "\n".join(blocos))


def deck(grupo, dados):
    g = grupo.lower()
    passos = "\n".join("          <li>%s</li>" % p for p in dados["passos"])
    afirmacao = html.escape(dados["afirmacao"], quote=False)
    cronometro = '\n          <p class="adr-cronometro" data-adr-cronometro data-fase="espera">Prazo ainda não iniciado</p>'
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aula 02 - Grupo {grupo} - Comitê de investimentos</title>
  <!-- Gerado por tools/gerar_decks_grupos_aula02.py. Editar o gerador, não este arquivo. -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="../assets/css/inteli-brand.css">
  <link rel="stylesheet" href="../assets/css/inteli-theme.css">
  <link rel="stylesheet" href="../assets/css/inteli-adr.css">
  <link rel="stylesheet" href="../assets/css/inteli-print.css" media="print">
</head>
<body>
  <div class="reveal">
    <div class="slides">

      <section class="content-slide slide-grupo" id="afirmacao">
{topo1}
        <blockquote class="grupo-afirmacao">{afirmacao}</blockquote>
        <div class="grupo-papel">
          <p>Vocês são analistas do comitê de investimentos do BTG. O comitê quer saber se essa frase se sustenta nos dados de 2019 a 2026 antes de deixá-la chegar a outro cliente.</p>
          <p>Na reunião, o grupo tem 3 minutos para defender o veredito, com o número na tela.</p>
        </div>
{rodape1}
      </section>

      <section class="content-slide slide-grupo" id="partida">
{topo2}
        <ol class="grupo-passos">
{passos}
        </ol>
        <div class="faixa-nota">
          <svg class="icone" aria-hidden="true"><use href="../assets/icons/icones.svg#schedule"></use></svg>
          <p><strong>Aos 12 minutos</strong> o número que decide o veredito precisa estar calculado. O tempo que sobra vai para a ADR.</p>
        </div>
        <p class="grupo-notebook"><a href="{notebook}" target="_blank" rel="noopener">Abrir o notebook da Aula 02</a> e ir para a seção do grupo {grupo}, que já carrega os dados.</p>
{rodape2}
      </section>

      <section class="content-slide slide-grupo slide-adr" id="adr">
{topo3}
{formulario}
{rodape3}
      </section>

      <section class="content-slide slide-grupo" id="defesa">
{topo4}
        <ol class="grupo-passos">
          <li>Leiam a frase do assessor em voz alta.</li>
          <li>Mostrem o número que decide e a célula do notebook que chega nele.</li>
          <li>Digam o veredito e a frase que o cliente deveria ter ouvido no lugar.</li>
        </ol>
        <p class="grupo-depois">Depois da aula, a ADR baixada em Markdown entra no repositório do grupo como uma ADR do A2, com a autoria de quem fez o commit.</p>
{rodape4}
      </section>

    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script>
    Reveal.initialize({{
      width: 1280, height: 720, center: false, margin: 0,
      hash: true, slideNumber: false, pdfSeparateFragments: false, transition: 'fade'
    }});
  </script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>
  <script src="../assets/js/inteli-quiz-config.js"></script>
  <script src="../assets/js/inteli-aula02-dados.js"></script>
  <script src="../assets/js/inteli-adr.js"></script>
  <script src="../assets/js/inteli-zoom.js"></script>
  <script src="../assets/js/inteli-print.js"></script>
</body>
</html>
""".format(
        grupo=grupo,
        afirmacao=afirmacao,
        topo1=_topo("Grupo %s: a frase do assessor" % grupo),
        topo2=_topo("Por onde começar a checagem do %s" % dados["ativo"]),
        topo3=_topo("ADR do grupo %s" % grupo, cronometro),
        topo4=_topo("Defesa do veredito no comitê"),
        passos=passos,
        notebook=NOTEBOOK + "#" + g,
        formulario=_formulario(grupo),
        rodape1=_rodape(grupo, 1), rodape2=_rodape(grupo, 2), rodape3=_rodape(grupo, 3), rodape4=_rodape(grupo, 4),
    )


def gerar():
    return {"aulas/aula02-%s.html" % g.lower(): deck(g, d) for g, d in conteudo().items()}


def main():
    for caminho, texto in gerar().items():
        with open(os.path.join(m.RAIZ, caminho), "w", encoding="utf-8") as fh:
            fh.write(texto)
        print("gravado", caminho)


if __name__ == "__main__":
    main()
