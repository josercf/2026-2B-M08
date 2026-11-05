"""Trava as regras de segurança do SQL da moeda e da ADR online da Aula 02.

O SQL roda no mesmo projeto Supabase do quiz ao vivo. O banco real é conferido
no ensaio; aqui o teste lê o texto e garante que cada objeto novo segue o padrão
de exemplos/quiz-supabase/quiz.sql.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL = os.path.join(RAIZ, "exemplos", "aula02-supabase", "aula02.sql")


def _sql():
    with open(SQL, encoding="utf-8") as fh:
        return fh.read()


def _funcoes():
    """Nome da função -> corpo, do create até o fechamento do bloco $$."""
    corpo = {}
    for m in re.finditer(r"create or replace function (\w+)\((.*?)\$\$(.*?)\$\$", _sql(), re.S | re.I):
        corpo[m.group(1)] = m.group(2) + m.group(3)
    return corpo


def test_funcoes_de_escrita_sao_security_definer_e_tabelas_tem_rls():
    sql = _sql()
    tabelas = re.findall(r"create table if not exists (\w+)", sql, re.I)
    assert len(tabelas) == 7, tabelas
    for t in tabelas:
        assert re.search(r"alter table %s enable row level security" % t, sql, re.I), t
    funcoes = _funcoes()
    assert funcoes, "nenhuma função encontrada"
    for nome, corpo in funcoes.items():
        assert "security definer set search_path" in corpo, nome


def test_funcoes_de_professor_checam_a_chave():
    funcoes = _funcoes()
    for nome in ("adr_links", "adr_prazo", "moeda_liberar", "moeda_zerar", "adr_participacao"):
        assert "quiz_chave_ok(p_chave)" in funcoes[nome], nome
    for nome in ("adr_salvar", "moeda_jogar", "moeda_entrar", "adr_agora"):
        assert "quiz_chave_ok" not in funcoes[nome], nome


def test_adr_salvar_recusa_prazo_token_e_campo():
    corpo = _funcoes()["adr_salvar"]
    assert "now() >" in corpo
    assert "adr_tokens" in corpo
    for campo in ("titulo", "contexto", "criterios", "opcoes", "decisao", "impacto"):
        assert "'%s'" % campo in corpo, campo
    assert "4000" in corpo


def test_moeda_sorteia_no_servidor():
    corpo = _funcoes()["moeda_jogar"]
    assert "random()" in corpo
    assert "1.5" in corpo and "0.6" in corpo
    assert "100" in corpo
    assert "on conflict on constraint moeda_jogadas_pkey do nothing" in corpo


def test_sql_nao_cria_nada_fora_dos_prefixos():
    sql = _sql()
    criados = re.findall(r"create (?:table if not exists|or replace function|policy) (\w+)", sql, re.I)
    assert criados
    for nome in criados:
        assert nome.startswith(("adr_", "moeda_")), nome
    assert not re.search(r"\b(drop|alter|delete from|update|insert into)\s+(table\s+)?quiz_", sql, re.I)


def test_sql_sem_travessao():
    assert chr(0x2014) not in _sql()
