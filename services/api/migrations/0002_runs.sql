-- 0002_runs: briefs, the actions on their cards, runs and their event streams (H4).
-- Applied once, in one transaction, by backroom_api.seed_db (or the API at start-up).
--
-- Events are stored as they are emitted, so `GET /runs/{id}/events` can replay a run
-- from any `Last-Event-ID`, and golden runs (H6) can be exported from here.

create table brief (
  id           text primary key,
  day          date not null,
  generated_at timestamptz not null,
  body         jsonb not null,                 -- the Brief as served (cards with status)
  stale        boolean not null default false  -- a rejection taught something: regenerate
);
create index brief_day on brief (day, generated_at desc);

-- One row per proposed action. The id hashes the candidate and its params, so the same
-- proposal in a regenerated brief is the same action (and keeps its status).
create table action (
  id         text primary key,
  brief_id   text not null references brief(id),
  card       jsonb not null,
  status     text not null default 'proposed' check (status in (
               'proposed', 'approved', 'rejected', 'running', 'done', 'failed')),
  updated_at timestamptz not null default now()
);

create table run (
  id              text primary key,
  action_id       text not null,
  task            text not null,
  portal          text not null,
  params          jsonb not null,
  idempotency_key text unique,                 -- a repeated approve returns the same run
  status          text not null check (status in (
                    'queued', 'running', 'succeeded', 'failed', 'needs_human', 'cancelled')),
  mode            text not null default 'replay' check (mode in ('explore', 'replay', 'heal')),
  skill_version   integer,
  chaos_seed      integer not null default 0,
  started_at      timestamptz not null default now(),
  finished_at     timestamptz,
  totals          jsonb not null,
  summary         text,
  undo_of         text references run(id),
  undo_params     jsonb,                       -- the inverse action's params, if any
  undo_available  boolean not null default false
);
create index run_action on run (action_id, started_at desc);

create table run_event (
  run_id text not null references run(id) on delete cascade,
  seq    integer not null check (seq >= 1),
  type   text not null,
  body   jsonb not null,                       -- the RunEvent as streamed
  primary key (run_id, seq)
);
