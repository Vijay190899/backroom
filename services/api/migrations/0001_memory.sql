-- 0001_memory: bitemporal knowledge graph (PRD §8.3, ARCHITECTURE §7).
-- Shared contract (L0). Applied in file-name order by the PC's migration runner (H1);
-- each file runs once, in one transaction. Never edit an applied file: add 0002_*.
--
-- Valid time:       valid_from <= :t and (valid_to is null or valid_to > :t)
-- Transaction time: recorded_at is when we learned the row; invalidated_at is when a
--                   later fact superseded it (and valid_to was set). "Valid at :t, as
--                   we knew it at :r":
--                     recorded_at <= :r and valid_from <= :t
--                     and (valid_to is null or valid_to > :t
--                          or (invalidated_at is not null and invalidated_at > :r))
-- Supersession:     a new fact on the same (subject_id, predicate) — or on the same
--                   (subject_id, predicate, object_id) for many-valued predicates —
--                   with a later valid_from sets the old row's valid_to, invalidated_at
--                   and superseded_by, in the same transaction as the insert. Nothing
--                   else ever updates a fact, and nothing deletes one.

create extension if not exists vector;

create table entity (
  id         text primary key,                  -- "<type>:<slug>", e.g. "ingredient:butter"
  type       text not null check (type in (
               'business', 'product', 'ingredient', 'supplier', 'staff', 'shift', 'portal',
               'skill', 'preference', 'weather_day', 'holiday', 'insight', 'action')),
  name       text not null,
  attrs      jsonb not null default '{}',
  embedding  vector(384),                       -- optional (P1, fastembed bge-small)
  created_at timestamptz not null default now(),
  check (id like type || ':%')
);

create table episode (
  id          text primary key,
  kind        text not null check (kind in ('invoice', 'approval', 'rejection', 'chat', 'run', 'seed')),
  payload     jsonb not null,
  occurred_at timestamptz not null,
  recorded_at timestamptz not null default now()
);

create table fact (
  id             text primary key,
  subject_id     text not null references entity(id),
  predicate      text not null check (predicate ~ '^[a-z][a-z0-9_]*$'),
  object_id      text references entity(id),
  value          jsonb,
  valid_from     timestamptz not null,
  valid_to       timestamptz,
  recorded_at    timestamptz not null default now(),
  source_episode text references episode(id),
  confidence     real not null default 1.0 check (confidence between 0 and 1),
  superseded_by  text references fact(id),
  invalidated_at timestamptz,                    -- end of transaction time
  check (object_id is not null or value is not null),
  check (valid_to is null or valid_to > valid_from),
  check ((superseded_by is null) = (invalidated_at is null))
);

create index fact_subject_predicate_idx on fact (subject_id, predicate, valid_from desc);
create index fact_object_idx on fact (object_id) where object_id is not null;
create index fact_open_idx on fact (subject_id, predicate) where valid_to is null;
create index fact_episode_idx on fact (source_episode);
create index episode_kind_idx on episode (kind, occurred_at desc);
