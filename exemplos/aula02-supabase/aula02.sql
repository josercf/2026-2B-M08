-- Aula 02 (M08): jogo da moeda no celular e ADR online dos grupos.
-- Roda no mesmo projeto Supabase do quiz ao vivo (exemplos/quiz-supabase/quiz.sql),
-- que precisa existir antes: as ações de professor usam quiz_chave_ok.
-- É idempotente e só cria objetos com prefixo adr_ ou moeda_.
--
-- Modelo:
--   adr_tokens       um token por grupo e sessão; sem leitura pública
--   adr_prazos       fim do prazo da sessão; o celular lê para o cronômetro
--   adr_campos       um texto por campo da ADR de cada grupo
--   moeda_sessoes    rodada liberada pelo professor
--   moeda_jogadores  quem entrou no jogo; sem leitura pública
--   moeda_jogadas    resultado e saldo de cada jogador em cada rodada
--
-- Segurança: RLS em tudo, leitura pública só do que vai ao projetor, escrita só
-- pelas funções abaixo. Gerar links, iniciar prazo e liberar rodada exigem a
-- chave do professor. O sorteio da moeda acontece no servidor.

create extension if not exists pgcrypto;

create table if not exists adr_tokens (
  sessao text not null,
  grupo text not null,
  token text not null,
  primary key (sessao, grupo)
);

create table if not exists adr_prazos (
  sessao text primary key,
  fim timestamptz
);

create table if not exists adr_campos (
  sessao text not null,
  grupo text not null,
  campo text not null,
  texto text not null default '',
  autor text,
  atualizado_em timestamptz not null default now(),
  primary key (sessao, grupo, campo)
);

create table if not exists moeda_sessoes (
  sessao text primary key,
  rodada int not null default 0 check (rodada between 0 and 20)
);

create table if not exists moeda_jogadores (
  id uuid primary key default gen_random_uuid(),
  sessao text not null,
  apelido text not null check (char_length(apelido) between 1 and 30),
  criado_em timestamptz not null default now()
);

create table if not exists moeda_jogadas (
  sessao text not null,
  jogador uuid not null references moeda_jogadores (id) on delete cascade,
  rodada int not null check (rodada between 1 and 20),
  cara boolean not null,
  saldo numeric(14, 2) not null,
  jogado_em timestamptz not null default now(),
  primary key (jogador, rodada)
);

-- Quem escreveu na ADR de cada grupo, para o professor lançar a participação.
create table if not exists adr_presencas (
  sessao text not null,
  grupo text not null,
  nome text not null,
  edicoes int not null default 0,
  primeiro_em timestamptz not null default now(),
  ultimo_em timestamptz not null default now(),
  primary key (sessao, grupo, nome)
);

alter table adr_presencas enable row level security;
alter table adr_tokens enable row level security;
alter table adr_prazos enable row level security;
alter table adr_campos enable row level security;
alter table moeda_sessoes enable row level security;
alter table moeda_jogadores enable row level security;
alter table moeda_jogadas enable row level security;

drop policy if exists adr_prazos_ler on adr_prazos;
create policy adr_prazos_ler on adr_prazos for select using (true);
drop policy if exists adr_campos_ler on adr_campos;
create policy adr_campos_ler on adr_campos for select using (true);
drop policy if exists moeda_sessoes_ler on moeda_sessoes;
create policy moeda_sessoes_ler on moeda_sessoes for select using (true);
drop policy if exists moeda_jogadas_ler on moeda_jogadas;
create policy moeda_jogadas_ler on moeda_jogadas for select using (true);

-- Professor: links dos quatro grupos. Cria o token que faltar e devolve os
-- existentes, então chamar de novo não invalida link já enviado no Slack.
create or replace function adr_links(p_chave text, p_sessao text)
returns table (grupo text, token text)
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  insert into adr_tokens (sessao, grupo, token)
  select p_sessao, g, encode(gen_random_bytes(8), 'hex')
    from unnest(array['G01', 'G02', 'G03', 'G04']) as g
  on conflict on constraint adr_tokens_pkey do nothing;
  return query select t.grupo, t.token from adr_tokens t where t.sessao = p_sessao order by t.grupo;
end $$;

-- Professor: inicia ou estende o prazo da sessão (fim = agora + minutos).
create or replace function adr_prazo(p_chave text, p_sessao text, p_minutos int)
returns timestamptz
language plpgsql security definer set search_path = public, extensions as $$
declare v_fim timestamptz;
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  if p_minutos < 0 or p_minutos > 120 then raise exception 'prazo fora de 0 a 120 minutos'; end if;
  v_fim := now() + make_interval(mins => p_minutos);
  insert into adr_prazos (sessao, fim) values (p_sessao, v_fim)
  on conflict (sessao) do update set fim = excluded.fim;
  return v_fim;
end $$;

-- Relógio do servidor e fim do prazo, para os decks dos grupos sincronizarem.
create or replace function adr_agora(p_sessao text)
returns table (agora timestamptz, fim timestamptz)
language sql security definer set search_path = public, extensions as $$
  select now(), (select p.fim from adr_prazos p where p.sessao = p_sessao);
$$;

-- Grupo: confere o token do link antes de liberar a edição na tela.
create or replace function adr_token_ok(p_sessao text, p_grupo text, p_token text)
returns boolean
language sql security definer set search_path = public, extensions as $$
  select exists (select 1 from adr_tokens t where t.sessao = p_sessao and t.grupo = p_grupo and t.token = p_token);
$$;

-- Grupo: grava um campo. Recusa token errado, campo desconhecido, texto longo
-- e prazo encerrado. Sem prazo definido, aceita.
create or replace function adr_salvar(p_sessao text, p_grupo text, p_token text, p_campo text,
                                      p_texto text, p_autor text)
returns timestamptz
language plpgsql security definer set search_path = public, extensions as $$
declare v_fim timestamptz; v_quando timestamptz := now();
begin
  if not exists (select 1 from adr_tokens t where t.sessao = p_sessao and t.grupo = p_grupo and t.token = p_token) then
    raise exception 'link sem permissão de edição';
  end if;
  if p_campo not in ('titulo', 'contexto', 'criterios', 'opcoes', 'decisao', 'impacto') then
    raise exception 'campo desconhecido';
  end if;
  if char_length(coalesce(p_texto, '')) > 4000 then raise exception 'texto acima de 4000 caracteres'; end if;
  select p.fim into v_fim from adr_prazos p where p.sessao = p_sessao;
  if v_fim is not null and now() > v_fim then raise exception 'prazo encerrado'; end if;
  if coalesce(trim(p_autor), '') <> '' then
    insert into adr_presencas (sessao, grupo, nome, edicoes)
    values (p_sessao, p_grupo, left(trim(p_autor), 60), 1)
    on conflict on constraint adr_presencas_pkey
    do update set edicoes = adr_presencas.edicoes + 1, ultimo_em = now();
  end if;
  insert into adr_campos (sessao, grupo, campo, texto, autor, atualizado_em)
  values (p_sessao, p_grupo, p_campo, coalesce(p_texto, ''), left(p_autor, 40), v_quando)
  on conflict (sessao, grupo, campo)
  do update set texto = excluded.texto, autor = excluded.autor, atualizado_em = excluded.atualizado_em;
  return v_quando;
end $$;

-- Grupo: registra quem abriu o deck com o link do grupo, mesmo antes de escrever.
create or replace function adr_entrar(p_sessao text, p_grupo text, p_token text, p_nome text)
returns boolean
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from adr_tokens t where t.sessao = p_sessao and t.grupo = p_grupo and t.token = p_token) then
    return false;
  end if;
  if coalesce(trim(p_nome), '') = '' then return false; end if;
  insert into adr_presencas (sessao, grupo, nome) values (p_sessao, p_grupo, left(trim(p_nome), 60))
  on conflict on constraint adr_presencas_pkey do update set ultimo_em = now();
  return true;
end $$;

-- Professor: participação por grupo (nome e quantas gravações fez na ADR).
create or replace function adr_participacao(p_chave text, p_sessao text)
returns table (grupo text, nome text, edicoes int)
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  return query select p.grupo, p.nome, p.edicoes from adr_presencas p
   where p.sessao = p_sessao order by p.grupo, p.nome;
end $$;

-- Professor: libera até a rodada informada (0 volta ao começo sem apagar nada).
create or replace function moeda_liberar(p_chave text, p_sessao text, p_rodada int)
returns int
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  if p_rodada < 0 or p_rodada > 20 then raise exception 'rodada fora de 0 a 20'; end if;
  insert into moeda_sessoes (sessao, rodada) values (p_sessao, p_rodada)
  on conflict (sessao) do update set rodada = excluded.rodada;
  return p_rodada;
end $$;

-- Professor: apaga jogadas e jogadores da sessão e volta para a rodada 0.
create or replace function moeda_zerar(p_chave text, p_sessao text)
returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  delete from moeda_jogadores where sessao = p_sessao;
  insert into moeda_sessoes (sessao, rodada) values (p_sessao, 0)
  on conflict (sessao) do update set rodada = 0;
end $$;

-- Quem veio do quiz guarda o id de participante, para o slide cruzar voto e saldo.
alter table moeda_jogadores add column if not exists participante uuid;
drop function if exists moeda_entrar(text, text);

create or replace function moeda_entrar(p_sessao text, p_apelido text, p_participante uuid default null)
returns uuid
language plpgsql security definer set search_path = public, extensions as $$
declare v_id uuid;
begin
  insert into moeda_jogadores (sessao, apelido, participante)
  values (p_sessao, left(trim(p_apelido), 30), p_participante)
  returning id into v_id;
  return v_id;
end $$;

-- Slide: o último voto de cada aluno numa pergunta do quiz contra o saldo final
-- dele na moeda. Devolve só contagens por alternativa, sem nomes.
create or replace function moeda_cruzamento(p_sessao text, p_pergunta text)
returns table (opcao int, abaixo int, acima int)
language sql security definer set search_path = public, extensions as $$
  with votos as (
    select distinct on (v.participante_id) v.participante_id, v.opcao
      from quiz_votos v join quiz_rodadas r on r.id = v.rodada_id
     where r.sessao = p_sessao and r.pergunta = p_pergunta
     order by v.participante_id, r.rodada desc
  ), finais as (
    select distinct on (mj.participante) mj.participante, j.saldo
      from moeda_jogadas j join moeda_jogadores mj on mj.id = j.jogador
     where mj.sessao = p_sessao and mj.participante is not null
     order by mj.participante, j.rodada desc, mj.criado_em desc
  )
  select v.opcao, (count(*) filter (where f.saldo < 100))::int, (count(*) filter (where f.saldo >= 100))::int
    from votos v join finais f on f.participante = v.participante_id
   group by v.opcao order by v.opcao;
$$;

-- Slide: quantas pessoas entraram no jogo, sem expor apelidos.
create or replace function moeda_sala(p_sessao text)
returns int
language sql security definer set search_path = public, extensions as $$
  select count(*)::int from moeda_jogadores where sessao = p_sessao;
$$;

-- Jogador: joga uma rodada liberada. O sorteio é do servidor; repetir a mesma
-- rodada devolve a jogada gravada, então recarregar o celular não muda o saldo.
create or replace function moeda_jogar(p_sessao text, p_jogador uuid, p_rodada int)
returns table (cara boolean, saldo numeric)
language plpgsql security definer set search_path = public, extensions as $$
declare v_liberada int; v_anterior numeric; v_cara boolean;
begin
  return query select j.cara, j.saldo from moeda_jogadas j where j.jogador = p_jogador and j.rodada = p_rodada;
  if found then return; end if;
  if not exists (select 1 from moeda_jogadores x where x.id = p_jogador and x.sessao = p_sessao) then
    raise exception 'jogador desconhecido';
  end if;
  select s.rodada into v_liberada from moeda_sessoes s where s.sessao = p_sessao;
  if v_liberada is null or p_rodada > v_liberada or p_rodada < 1 then raise exception 'rodada não liberada'; end if;
  if p_rodada = 1 then
    v_anterior := 100;
  else
    select j.saldo into v_anterior from moeda_jogadas j where j.jogador = p_jogador and j.rodada = p_rodada - 1;
    if v_anterior is null then raise exception 'jogue a rodada anterior antes'; end if;
  end if;
  v_cara := random() < 0.5;
  insert into moeda_jogadas (sessao, jogador, rodada, cara, saldo)
  values (p_sessao, p_jogador, p_rodada, v_cara,
          round(v_anterior * case when v_cara then 1.5 else 0.6 end, 2))
  -- Dois toques simultâneos na mesma rodada: o segundo devolve a jogada do primeiro.
  on conflict on constraint moeda_jogadas_pkey do nothing;
  return query select j.cara, j.saldo from moeda_jogadas j where j.jogador = p_jogador and j.rodada = p_rodada;
end $$;

grant execute on function adr_links(text, text) to anon, authenticated;
grant execute on function adr_prazo(text, text, int) to anon, authenticated;
grant execute on function adr_agora(text) to anon, authenticated;
grant execute on function adr_token_ok(text, text, text) to anon, authenticated;
grant execute on function adr_entrar(text, text, text, text) to anon, authenticated;
grant execute on function adr_participacao(text, text) to anon, authenticated;
grant execute on function adr_salvar(text, text, text, text, text, text) to anon, authenticated;
grant execute on function moeda_liberar(text, text, int) to anon, authenticated;
grant execute on function moeda_zerar(text, text) to anon, authenticated;
grant execute on function moeda_entrar(text, text, uuid) to anon, authenticated;
grant execute on function moeda_cruzamento(text, text) to anon, authenticated;
grant execute on function moeda_sala(text) to anon, authenticated;
grant execute on function moeda_jogar(text, uuid, int) to anon, authenticated;

-- Atualização ao vivo para o projetor e para os decks dos grupos.
do $$
begin
  begin alter publication supabase_realtime add table adr_campos; exception when duplicate_object then null; end;
  begin alter publication supabase_realtime add table adr_prazos; exception when duplicate_object then null; end;
  begin alter publication supabase_realtime add table moeda_sessoes; exception when duplicate_object then null; end;
  begin alter publication supabase_realtime add table moeda_jogadas; exception when duplicate_object then null; end;

end $$;
