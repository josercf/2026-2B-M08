"""SQL da sala da Aula 04: só acrescenta objetos sim_ e não guarda nome de aluno."""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL = os.path.join(RAIZ, "exemplos", "aula04-supabase", "aula04.sql")


def _sql():
    with open(SQL, encoding="utf-8") as fh:
        texto = fh.read()
    return re.sub(r"--[^\n]*", "", texto).lower()


def test_so_cria_objetos_com_prefixo_sim():
    sql = _sql()
    for nome in re.findall(r"create table if not exists (\w+)", sql):
        assert nome.startswith("sim_"), nome
    for nome in re.findall(r"create or replace function (\w+)", sql):
        assert nome.startswith("sim_"), nome
    for nome in re.findall(r"create policy (\w+)", sql):
        assert nome.startswith("sim_"), nome
    assert len(re.findall(r"create table if not exists", sql)) == 3
    assert len(re.findall(r"create or replace function", sql)) == 4


def test_nao_altera_nem_remove_o_que_existe():
    sql = _sql()
    assert "drop table" not in sql and "truncate" not in sql and "drop function" not in sql
    for alvo in re.findall(r"alter table (\w+)", sql):
        assert alvo.startswith("sim_"), alvo
    assert set(re.findall(r"alter table \w+ (\w+ \w+ \w+ \w+)", sql)) == {"enable row level security"}
    for alvo in re.findall(r"drop policy if exists \w+ on (\w+)", sql):
        assert alvo.startswith("sim_"), alvo
    # A única remoção de linha é a do turno do próprio participante.
    assert re.findall(r"delete from (\w+)", sql) == ["sim_turnos"]
    for prefixo in ("quiz_", "moeda_"):
        assert prefixo not in sql, prefixo
    # Única exceção: o token de spec do grupo, linha nova em adr_tokens (sim_spec_link).
    assert set(re.findall(r"adr_\w+", sql)) == {"adr_tokens", "adr_tokens_pkey"}
    assert re.findall(r"insert into (\w+)", sql).count("adr_tokens") == 1
    assert "update adr_" not in sql and "delete from adr_" not in sql


def test_toda_tabela_tem_rls_e_nenhuma_guarda_nome():
    sql = _sql()
    tabelas = re.findall(r"create table if not exists (\w+)", sql)
    for tabela in tabelas:
        assert "alter table %s enable row level security" % tabela in sql
    for corpo in re.findall(r"create table if not exists \w+ \((.*?)\n\);", sql, flags=re.S):
        colunas = [l.strip().split()[0] for l in corpo.splitlines() if l.strip()]
        assert "nome" not in colunas and "email" not in colunas and "ra" not in colunas


def test_escrita_so_por_funcao():
    sql = _sql()
    assert "for insert" not in sql and "for update" not in sql and "for delete" not in sql
    assert "for all" not in sql
    assert sql.count("security definer") == 4
