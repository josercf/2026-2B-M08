-- Aula 04 (M08): portal de simulação de carteiras, painel da sala e placar dos turnos.
-- Roda no mesmo projeto Supabase do quiz ao vivo (exemplos/quiz-supabase/quiz.sql).
-- É idempotente e só cria objetos com prefixo sim_. Nada do que já existe é alterado;
-- a única escrita fora do prefixo é o token de spec do grupo, em adr_tokens.
--
-- Modelo:
--   sim_participantes  quem entrou no portal: iniciais e grupo, sem o nome
--   sim_carteiras      os parâmetros da simulação de cada participante
--   sim_turnos         turnos que a dupla do participante declarou concluídos
--
-- Segurança: RLS em tudo, leitura pública (o painel vai ao projetor e a chave
-- anon é pública por desenho) e escrita só pelas funções abaixo. Por isso a
-- tabela guarda iniciais, e não o nome: qualquer pessoa que conheça a sessão lê.
-- A nuvem de pontos não é gravada; cada navegador recalcula a partir de ativos,
-- período, quantidade e semente.

create table if not exists sim_participantes (
  id uuid primary key default gen_random_uuid(),
  sessao text not null,
  iniciais text not null check (iniciais ~ '^[A-ZÀ-Ý]{1,3}$'),
  grupo text not null check (grupo in ('G01', 'G02', 'G03', 'G04', 'VIS')),
  criado_em timestamptz not null default now()
);
create index if not exists sim_participantes_sessao on sim_participantes (sessao);

create table if not exists sim_carteiras (
  participante uuid primary key references sim_participantes (id) on delete cascade,
  sessao text not null,
  ativos text[] not null check (cardinality(ativos) between 2 and 5),
  pregoes int not null check (pregoes in (9, 21, 63, 126, 252)),
  n int not null check (n in (0, 10, 100, 1000, 10000)),
  semente int not null,
  pesos jsonb,
  atualizado_em timestamptz not null default now()
);
create index if not exists sim_carteiras_sessao on sim_carteiras (sessao);

create table if not exists sim_turnos (
  participante uuid not null references sim_participantes (id) on delete cascade,
  sessao text not null,
  turno int not null check (turno between 1 and 5),
  feito_em timestamptz not null default now(),
  primary key (participante, turno)
);
create index if not exists sim_turnos_sessao on sim_turnos (sessao);

alter table sim_participantes enable row level security;
alter table sim_carteiras enable row level security;
alter table sim_turnos enable row level security;

drop policy if exists sim_participantes_ler on sim_participantes;
create policy sim_participantes_ler on sim_participantes for select using (true);
drop policy if exists sim_carteiras_ler on sim_carteiras;
create policy sim_carteiras_ler on sim_carteiras for select using (true);
drop policy if exists sim_turnos_ler on sim_turnos;
create policy sim_turnos_ler on sim_turnos for select using (true);

-- Portal: entrar na sessão com iniciais e grupo. Devolve o id do participante.
create or replace function sim_entrar(p_sessao text, p_iniciais text, p_grupo text)
returns uuid language plpgsql security definer set search_path = public, extensions as $$
declare novo uuid;
begin
  if char_length(coalesce(p_sessao, '')) not between 1 and 60 then
    raise exception 'sessão inválida';
  end if;
  insert into sim_participantes (sessao, iniciais, grupo)
  values (p_sessao, upper(trim(p_iniciais)), p_grupo)
  returning id into novo;
  return novo;
end $$;

-- Portal: grava ou atualiza a simulação do participante. Os ativos são tickers
-- em maiúsculas; os pesos próprios, quando informados, são um vetor do mesmo
-- tamanho, não negativo, que soma 1.
create or replace function sim_salvar(p_participante uuid, p_ativos text[], p_pregoes int,
                                      p_n int, p_semente int, p_pesos jsonb)
returns timestamptz language plpgsql security definer set search_path = public, extensions as $$
declare v_sessao text; v_quando timestamptz := now(); v_soma numeric;
begin
  select sessao into v_sessao from sim_participantes where id = p_participante;
  if v_sessao is null then raise exception 'participante desconhecido'; end if;
  if exists (select 1 from unnest(p_ativos) a where a !~ '^[A-Z0-9]{4,7}$') then
    raise exception 'ticker inválido';
  end if;
  if p_pesos is not null then
    if jsonb_typeof(p_pesos) <> 'array' or jsonb_array_length(p_pesos) <> cardinality(p_ativos) then
      raise exception 'pesos fora do tamanho da carteira';
    end if;
    select sum(v::numeric) into v_soma from jsonb_array_elements_text(p_pesos) v;
    if abs(v_soma - 1) > 0.000001
       or exists (select 1 from jsonb_array_elements_text(p_pesos) v where v::numeric < 0) then
      raise exception 'os pesos precisam ser não negativos e somar 1';
    end if;
  end if;
  insert into sim_carteiras (participante, sessao, ativos, pregoes, n, semente, pesos, atualizado_em)
  values (p_participante, v_sessao, p_ativos, p_pregoes, p_n, p_semente, p_pesos, v_quando)
  on conflict (participante) do update
    set ativos = excluded.ativos, pregoes = excluded.pregoes, n = excluded.n,
        semente = excluded.semente, pesos = excluded.pesos, atualizado_em = excluded.atualizado_em;
  return v_quando;
end $$;

-- Portal: a dupla declara um turno concluído, ou desfaz a marcação.
create or replace function sim_marcar(p_participante uuid, p_turno int, p_feito boolean)
returns boolean language plpgsql security definer set search_path = public, extensions as $$
declare v_sessao text;
begin
  select sessao into v_sessao from sim_participantes where id = p_participante;
  if v_sessao is null then raise exception 'participante desconhecido'; end if;
  if p_feito then
    insert into sim_turnos (participante, sessao, turno) values (p_participante, v_sessao, p_turno)
    on conflict do nothing;
  else
    -- Só a linha do próprio participante, que é quem conhece o id.
    delete from sim_turnos where participante = p_participante and turno = p_turno;
  end if;
  return p_feito;
end $$;

-- Portal: link da tela de spec do grupo do participante, para o turno 4 ou 5, sem
-- o professor distribuir endereço. Devolve grupo, sessão da spec e o token que a
-- ADR online (exemplos/aula02-supabase/aula02.sql) exige para gravar; cria o
-- token se ainda não existir. É a única referência a um objeto fora do prefixo
-- sim_: uma linha nova em adr_tokens, que adr_links criaria do mesmo jeito.
-- Visitante não edita spec.
create or replace function sim_spec_link(p_participante uuid, p_turno int)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare v_sessao text; v_grupo text; v_spec text; v_token text;
begin
  select sessao, grupo into v_sessao, v_grupo from sim_participantes where id = p_participante;
  if v_sessao is null then raise exception 'participante desconhecido'; end if;
  if v_grupo = 'VIS' then raise exception 'visitante não edita a spec do grupo'; end if;
  if p_turno not in (4, 5) then raise exception 'só os turnos 4 e 5 têm spec do grupo'; end if;
  v_spec := v_sessao || '-t' || p_turno;
  insert into adr_tokens (sessao, grupo, token)
  values (v_spec, v_grupo, encode(gen_random_bytes(8), 'hex'))
  on conflict on constraint adr_tokens_pkey do nothing;
  select t.token into v_token from adr_tokens t where t.sessao = v_spec and t.grupo = v_grupo;
  return jsonb_build_object('grupo', v_grupo, 'sessao', v_spec, 'turno', p_turno, 'token', v_token);
end $$;

grant execute on function sim_entrar(text, text, text) to anon, authenticated;
grant execute on function sim_spec_link(uuid, int) to anon, authenticated;
grant execute on function sim_salvar(uuid, text[], int, int, int, jsonb) to anon, authenticated;
grant execute on function sim_marcar(uuid, int, boolean) to anon, authenticated;
