-- Quiz ao vivo das aulas (M08): rodadas abertas pelo slide, votos pelo celular.
-- Colar inteiro no SQL Editor do Supabase e rodar uma vez. É idempotente: rodar
-- de novo não apaga votos.
--
-- Modelo:
--   quiz_rodadas       uma pergunta aberta numa sessão (aula), rodada 1 ou 2
--   quiz_participantes quem entrou pelo QR code, com nome e avatar
--   quiz_votos         um voto por participante por rodada (chave primária)
--
-- Segurança: RLS ligado em tudo. O celular e o slide usam a chave anon, que é
-- pública por desenho. Ninguém escreve direto nas tabelas: entrar e votar passam
-- por funções que conferem a rodada aberta; abrir e fechar rodada exigem a chave
-- do professor, guardada em quiz_config e nunca no repositório.

create extension if not exists pgcrypto;

create table if not exists quiz_config (
  id boolean primary key default true check (id),
  chave_professor_hash text not null
);

create table if not exists quiz_rodadas (
  id uuid primary key default gen_random_uuid(),
  sessao text not null,
  pergunta text not null,
  rodada int not null default 1 check (rodada between 1 and 9),
  enunciado text not null,
  opcoes jsonb not null,
  correta int,
  aberta boolean not null default false,
  aberta_em timestamptz,
  fechada_em timestamptz,
  unique (sessao, pergunta, rodada)
);

create table if not exists quiz_participantes (
  id uuid primary key default gen_random_uuid(),
  sessao text not null,
  nome text not null check (char_length(nome) between 1 and 40),
  avatar text not null check (char_length(avatar) between 1 and 40),
  criado_em timestamptz not null default now()
);

create table if not exists quiz_votos (
  rodada_id uuid not null references quiz_rodadas (id) on delete cascade,
  participante_id uuid not null references quiz_participantes (id) on delete cascade,
  opcao int not null,
  votado_em timestamptz not null default now(),
  primary key (rodada_id, participante_id)
);

alter table quiz_config enable row level security;
alter table quiz_rodadas enable row level security;
alter table quiz_participantes enable row level security;
alter table quiz_votos enable row level security;

-- Leitura pública das três tabelas da aula (o Realtime precisa dela). Nenhuma
-- política de escrita: escrever só pelas funções abaixo. quiz_config não tem
-- política nenhuma, então fica invisível para a chave anon.
drop policy if exists quiz_rodadas_ler on quiz_rodadas;
create policy quiz_rodadas_ler on quiz_rodadas for select using (true);
-- O nome completo do aluno serve só ao lançamento da participação: nenhuma
-- política de leitura em quiz_participantes, e o slide recebe só a contagem
-- de quem está na sala, por quiz_sala.
drop policy if exists quiz_participantes_ler on quiz_participantes;
drop policy if exists quiz_votos_ler on quiz_votos;
create policy quiz_votos_ler on quiz_votos for select using (true);

-- Celular: entrar na sessão com nome e avatar. Devolve o id do participante.
create or replace function quiz_entrar(p_sessao text, p_nome text, p_avatar text)
returns uuid language plpgsql security definer set search_path = public, extensions as $$
declare novo uuid;
begin
  insert into quiz_participantes (sessao, nome, avatar)
  values (p_sessao, left(trim(p_nome), 40), left(p_avatar, 40))
  returning id into novo;
  return novo;
end $$;

-- Celular: votar. Só na rodada aberta, uma vez: o segundo voto é recusado
-- pela chave primária e a função devolve false.
create or replace function quiz_votar(p_rodada uuid, p_participante uuid, p_opcao int)
returns boolean language plpgsql security definer set search_path = public, extensions as $$
declare r quiz_rodadas;
begin
  select * into r from quiz_rodadas where id = p_rodada;
  if r.id is null or not r.aberta then
    raise exception 'rodada fechada';
  end if;
  if p_opcao < 0 or p_opcao >= jsonb_array_length(r.opcoes) then
    raise exception 'opção inválida';
  end if;
  if not exists (select 1 from quiz_participantes p where p.id = p_participante and p.sessao = r.sessao) then
    raise exception 'participante fora da sessão';
  end if;
  insert into quiz_votos (rodada_id, participante_id, opcao)
  values (p_rodada, p_participante, p_opcao)
  on conflict do nothing;
  return found;
end $$;

-- Slide: quantas pessoas entraram na sessão, sem expor nomes.
create or replace function quiz_sala(p_sessao text)
returns int language sql security definer set search_path = public, extensions as $$
  select count(*)::int from quiz_participantes where sessao = p_sessao;
$$;

create or replace function quiz_chave_ok(p_chave text)
returns boolean language sql security definer set search_path = public, extensions as $$
  select exists (select 1 from quiz_config where chave_professor_hash = crypt(p_chave, chave_professor_hash));
$$;

-- Slide: abrir uma rodada. Fecha qualquer outra aberta na mesma sessão, para o
-- celular nunca ver duas perguntas. Reabrir a mesma rodada mantém os votos.
create or replace function quiz_abrir(p_chave text, p_sessao text, p_pergunta text, p_rodada int,
                                      p_enunciado text, p_opcoes jsonb)
returns uuid language plpgsql security definer set search_path = public, extensions as $$
declare rid uuid;
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  update quiz_rodadas set aberta = false, fechada_em = now()
   where sessao = p_sessao and aberta and not (pergunta = p_pergunta and rodada = p_rodada);
  insert into quiz_rodadas (sessao, pergunta, rodada, enunciado, opcoes, aberta, aberta_em)
  values (p_sessao, p_pergunta, p_rodada, p_enunciado, p_opcoes, true, now())
  on conflict (sessao, pergunta, rodada)
  do update set aberta = true, aberta_em = coalesce(quiz_rodadas.aberta_em, now()),
                fechada_em = null, enunciado = excluded.enunciado, opcoes = excluded.opcoes
  returning id into rid;
  return rid;
end $$;

-- Slide: fechar as rodadas abertas da sessão (ao sair do slide) e, se
-- informada, gravar a alternativa certa para o relatório de participação.
create or replace function quiz_fechar(p_chave text, p_sessao text, p_pergunta text default null,
                                       p_correta int default null)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  update quiz_rodadas set aberta = false, fechada_em = coalesce(fechada_em, now())
   where sessao = p_sessao and aberta;
  if p_pergunta is not null and p_correta is not null then
    update quiz_rodadas set correta = p_correta where sessao = p_sessao and pergunta = p_pergunta;
  end if;
end $$;

grant execute on function quiz_entrar(text, text, text) to anon, authenticated;
grant execute on function quiz_votar(uuid, uuid, int) to anon, authenticated;
grant execute on function quiz_sala(text) to anon, authenticated;
grant execute on function quiz_abrir(text, text, text, int, text, jsonb) to anon, authenticated;
grant execute on function quiz_fechar(text, text, text, int) to anon, authenticated;
revoke execute on function quiz_chave_ok(text) from anon, authenticated, public;

-- Participação por aula: uma linha por aluno, com votos e acertos.
create or replace view quiz_participacao as
select p.sessao, p.nome, p.avatar,
       count(v.*) as votos,
       count(v.*) filter (where r.correta is not null and v.opcao = r.correta) as acertos,
       min(p.criado_em) as entrou_em
  from quiz_participantes p
  left join quiz_votos v on v.participante_id = p.id
  left join quiz_rodadas r on r.id = v.rodada_id
 group by p.sessao, p.id, p.nome, p.avatar;

revoke all on quiz_participacao from anon, authenticated;

-- Atualização ao vivo para o slide e para o celular.
do $$
begin
  begin alter publication supabase_realtime add table quiz_rodadas; exception when duplicate_object then null; end;
  begin alter publication supabase_realtime add table quiz_votos; exception when duplicate_object then null; end;
end $$;

-- Chave do professor: troque o texto abaixo por uma frase sua antes de rodar.
-- Ela fica só como hash no banco e é digitada uma vez no navegador da sala.
insert into quiz_config (id, chave_professor_hash)
values (true, crypt('TROQUE-PELA-SUA-CHAVE', gen_salt('bf')))
on conflict (id) do nothing;

-- Configuração das ferramentas da aula (URL e token do webhook da nuvem de
-- palavras), guardada fora do repositório público. Sem política de leitura:
-- só as duas funções abaixo, com a chave do professor, leem ou gravam.
create table if not exists quiz_segredos (
  nome text primary key,
  valor text not null
);
alter table quiz_segredos enable row level security;

create or replace function quiz_segredo(p_chave text, p_nome text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  return (select valor from quiz_segredos where nome = p_nome);
end $$;

create or replace function quiz_guardar_segredo(p_chave text, p_nome text, p_valor text)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  insert into quiz_segredos (nome, valor) values (p_nome, p_valor)
  on conflict (nome) do update set valor = excluded.valor;
end $$;

grant execute on function quiz_segredo(text, text) to anon, authenticated;
grant execute on function quiz_guardar_segredo(text, text, text) to anon, authenticated;
