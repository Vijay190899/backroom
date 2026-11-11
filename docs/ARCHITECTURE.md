# Backroom — Technical Architecture

Stack follows Super44's: **Python + TypeScript + AWS**, with the frontend on Vercel (their marketing site is a Vercel-deployed Next.js app).

## 1. System overview

```mermaid
flowchart LR
  subgraph VC["Vercel"]
    WEB["Next.js web app<br/>Today · Run theater · Memory · Bench"]
  end
  subgraph LS["AWS Lightsail · docker compose"]
    CADDY["Caddy<br/>TLS + routing"]
    API["FastAPI api<br/>orchestrator · agents · memory · SSE/WS"]
    BR["Browser pool<br/>1 Chromium · 2 contexts"]
    PORT["FastAPI portals<br/>Grainline · TillDesk · Localboard<br/>+ chaos engine"]
    PG[("Postgres 16 + pgvector<br/>memory graph · runs · skills")]
    DUCK[("DuckDB / Parquet<br/>sales analytics")]
  end
  LLM[["OpenRouter (default) or Anthropic<br/>Claude Haiku 5.5 · Sonnet 5.5"]]
  WEB -->|"HTTPS · SSE · WS"| CADDY
  CADDY --> API
  API --> BR
  BR -->|"portals:8001"| PORT
  API --> PG
  API --> DUCK
  API --> LLM
  CADDY --> PORT
```

## 2. Repository layout

```
backroom/
├─ package.json              pnpm workspace root + task runner (pnpm check | seed | bench | dev | e2e | probe:llm)
├─ pnpm-workspace.yaml       packages: apps/web
├─ pyproject.toml            uv workspace root (members below) + dev deps: ruff, pyright, pytest
├─ .python-version           3.12
├─ apps/web/                 Next.js (App Router, TS, Tailwind v4, shadcn/ui, Motion)
│  └─ src/{app,components,lib,styles}
├─ services/api/             FastAPI — Python 3.12, uv
│  └─ backroom_api/
│     ├─ agents/             browser agent, planner, verifier, extractor
│     ├─ browser/            pool, observation (aria snapshot), executor, screencast
│     ├─ skills/             compiler, replay, healer, registry
│     ├─ memory/             schema, writers, supersession, context packer
│     ├─ analytics/          DuckDB queries, detectors (stockout, margin, weather)
│     ├─ llm/                model registry, client, cost meter, budget guard
│     ├─ routes/             brief, actions, runs (SSE/WS), memory, bench, health
│     └─ replay/             golden-run recorder & player
├─ services/portals/         FastAPI + Jinja2 mock merchant sites + chaos engine (package backroom_portals)
├─ data/                     package backroom_data, script `backroom-data` (raw data NOT committed)
├─ bench/                    package backroom_bench, script `backroom-bench`; results/*.json (committed)
├─ infra/                    docker-compose.yml, Caddyfile, deploy.sh, lightsail notes
└─ docs/                     PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS
```

### Task runner (one entry point, works on Windows and Linux)

| Command | Runs |
|---|---|
| `pnpm check` | `uv run ruff check . && uv run pyright && uv run pytest -q && pnpm -C apps/web lint && pnpm -C apps/web typecheck` |
| `pnpm seed` | `uv run backroom-data all` (download → transform → load Postgres + Parquet) |
| `pnpm bench` | `uv run backroom-bench all` (B1–B5 → `bench/results/*.json`) |
| `pnpm probe:llm` | `uv run backroom-bench probe` (provider capability probe → `bench/results/provider_probe.json`) |
| `pnpm dev` | `docker compose -f infra/docker-compose.yml up -d postgres` + api, portals (`uv run uvicorn --reload`) + `next dev`, in parallel |
| `pnpm e2e` | Playwright e2e of the demo path (390 px + 1440 px) |

## 3. Backend (services/api)

| Concern | Choice | Why |
|---|---|---|
| Runtime | Python 3.12, `uv`, FastAPI, Pydantic v2 | Their stack. Typed schemas shared with LLM structured outputs |
| DB | Postgres 16 + pgvector (`pgvector/pgvector:pg16`), `psycopg` 3, plain SQL migrations | One store for graph, runs and skills. Bitemporal queries are easy in SQL |
| Analytics | DuckDB over Parquet | Fast embedded OLAP. Detectors are pure SQL |
| Browser | Playwright (Python) Chromium; CDP `Page.startScreencast` for live frames | Own the loop. No vendor lock-in. Live view for free |
| Streaming | SSE for run events (resumable via `Last-Event-ID`); WebSocket for JPEG frames | SSE is simple and proxy-friendly; frames need binary |
| Lint/test | ruff, pyright (strict on core modules), pytest, pytest-asyncio | |
| Container | api image `FROM mcr.microsoft.com/playwright/python:<pinned>-noble` | Chromium + system deps preinstalled; no apt surprises on deploy night |
| Local dev | api and portals run natively (`uv run uvicorn --reload`); only Postgres runs in Docker | hot reload, Windows-friendly; compose is used for deploy parity |

### Key API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + dependency checks |
| GET | `/brief/today` | cached brief (`?regenerate=1` streams a new one) |
| POST | `/actions/{id}/approve` | header `Idempotency-Key` → `{run_id}` |
| POST | `/actions/{id}/reject` | `{reason}` → preference episode |
| GET | `/runs/{id}/events` | SSE: `step.started/finished`, `mode.changed`, `heal.*`, `cost.tick`, `run.finished` |
| WS | `/runs/{id}/screen` | JPEG frames + cursor coordinates |
| GET | `/skills`, `/skills/{id}/versions` | registry + diffs |
| GET | `/memory/graph?as_of=` | nodes/edges valid at time |
| GET | `/memory/facts/{id}` | fact + provenance |
| POST | `/memory/ingest/invoice` | PDF/image → extractor → facts |
| POST | `/chaos` | `{portal, seed}` (dev/demo only) |
| POST | `/ask` | SSE answer with tool calls + citations (P1) |

## 4. Mock portals and the chaos engine (services/portals)

- Server-rendered Jinja2 with tiny vanilla JS. Realistic patterns: login → TOTP (pyotp) → dashboard, cookie banner, catalog search + pagination, cart, checkout confirm, order history, generated PDF invoices (WeasyPrint or ReportLab).
- **Chaos engine:** each request reads a `chaos_seed` (session or `/chaos`). A seeded RNG picks variants from a catalog:
  - label synonyms and language (EN/DE: "Add to cart" ↔ "In den Warenkorb")
  - DOM order and layout permutations; wrapper-div depth; randomised ids/classes
  - interstitials (cookie banner, "what's new" modal, survey)
  - delayed rendering (skeleton → content after 300–1500 ms); button → link swaps
  - moved navigation (sidebar ↔ top bar ↔ hamburger)
- Seed 0 is the canonical design. Same seed ⇒ identical DOM (tested).
- Portals use their own visual identities, kept deliberately plain and "legacy SaaS". This contrast makes the Backroom UI pop.

## 5. Model layer

**Every provider and model choice is an environment variable. No model ID or SDK client is created outside `llm/registry.py`.** The defaults favour cost for the demo, and swapping is a one-line change.

### 5.1 Provider

One code path: the official `anthropic` Python SDK, pointed at the chosen provider. No OpenAI-compatible shim.

| `LLM_PROVIDER` | Client construction | Model ID mapping | Notes |
|---|---|---|---|
| `openrouter` (default) | `Anthropic(base_url="https://openrouter.ai/api", auth_token=OPENROUTER_API_KEY, default_headers={"X-Title": OPENROUTER_APP_NAME, "HTTP-Referer": OPENROUTER_SITE_URL})` | `claude-haiku-5-5` → `anthropic/claude-haiku-5.5`, `claude-sonnet-5-5` → `anthropic/claude-sonnet-5.5`, `claude-opus-5-5` → `anthropic/claude-opus-5.5` | OpenRouter's Anthropic-compatible Messages endpoint. Same per-token prices as direct (verified 11 Nov). ~5.5% fee on credit purchases. Anthropic **beta headers are off** |
| `anthropic` | `Anthropic(api_key=ANTHROPIC_API_KEY)` | canonical IDs as-is | Full feature set, including server-side refusal `fallbacks` on Sonnet 5.5 |

- `LLM_*_MODEL` env vars always hold **canonical IDs** (`claude-haiku-5-5`). The registry maps them per provider. An ID containing `/` (e.g. `google/gemini-…`) passes through untouched on OpenRouter, for B4 experiments.
- **Capability flags per provider** (`registry.CAPS[provider]`): `effort`, `strict_tools`, `structured_outputs`, `prompt_cache`, `streaming`, `server_fallbacks`, `betas`. Call sites check flags; they never branch on the provider name.
- **The capability probe** (`pnpm probe:llm`, M0 gate) makes one cheap Haiku call per feature: tool call with `strict`, structured output, cache hit on the repeat (`cache_read_input_tokens > 0`), streaming, `stop_reason`, and `output_config.effort` accepted. Results go to `bench/results/provider_probe.json`. Any failure flips that flag off for the provider and is logged in DECISIONS.md.

### 5.2 Roles

| Role | Env var | Default | Effort | Used for |
|---|---|---|---|---|
| Planner | `LLM_PLANNER_MODEL` | `claude-sonnet-5-5` | `medium` | brief ranking/copy, skill binding |
| Worker | `LLM_WORKER_MODEL` | `claude-haiku-5-5` | `low` | browser explore steps, extraction, routing |
| Verifier | `LLM_VERIFIER_MODEL` | `claude-haiku-5-5` | `low` | preference/rule checks |
| Healer | `LLM_HEAL_MODEL` | `claude-haiku-5-5` | `low` | first heal attempt |
| Heal escalation | `LLM_ESCALATION_MODEL` | `claude-sonnet-5-5` | `medium` | second attempt (with screenshot) |
| Ask (P1) | `LLM_ASK_MODEL` | `claude-sonnet-5-5` | `low` | chat with tools |

Also: `LLM_<ROLE>_EFFORT` overrides effort for that role.

**Price table** (USD per 1M tokens. Anthropic first-party rates cached 2026-11-03; OpenRouter lists the same rates under `anthropic/…` IDs, checked 2026-11-11. Keep it in `llm/registry.py` for the cost meter.)

| Model | Input | Output | Notes |
|---|---|---|---|
| `claude-haiku-5-5` | 0.10 | 0.50 | ≤100K-token prompts ($0.50/$2.50 above). No server-side refusal fallback |
| `claude-sonnet-5-5` | 2.00 | 10.00 | cache reads 0.10 |
| `claude-opus-5-5` | 4.00 | 20.00 | effort default is `medium`; set explicitly |
| `claude-fable-5-2` | 8.00 | 40.00 | most capable; thinking always on |

**Swap examples**
```bash
# Go direct to Anthropic instead of OpenRouter (same model IDs)
LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=sk-ant-...
# Higher quality planning for a live demo
LLM_PLANNER_MODEL=claude-opus-5-5
# Everything on the cheapest tier (bench B4 comparison)
LLM_PLANNER_MODEL=claude-haiku-5-5 LLM_ESCALATION_MODEL=claude-haiku-5-5
```

**API rules for the current models** (verify against the `claude-api` skill before writing SDK code):
- Official `anthropic` Python SDK only. Stream long calls (`.stream()` + `.get_final_message()`).
- Thinking: adaptive (omit `thinking` or `{type:"adaptive"}`). Do **not** send `budget_tokens`, `temperature`, `top_p` or `top_k` (400 errors). Control depth with `output_config.effort`.
- **Forced `tool_choice` (`any`/`tool`) returns 400 on Sonnet 5.5.** Use `auto` + `strict: true` tools + prompt steering, or structured outputs (`output_config.format`) for pure JSON.
- Always check `stop_reason` (`refusal`, `max_tokens`) before using content. When `server_fallbacks` is on (provider `anthropic`), Sonnet 5.5 calls send beta `server-side-fallback-2026-07-01` with `fallbacks: "default"`. Otherwise (OpenRouter, or any Haiku call), the client escalates to the next model in the ladder.
- **Prompt caching:** frozen system prompt + deterministic tool list first; volatile content (time, page snapshot) after the last breakpoint. Track `cache_read_input_tokens` and show the cache-hit % on the bench page.
- Parse tool inputs with `json.loads` / Pydantic. Never string-match.

**Escalation ladder** (shared by heal and refusal handling): deterministic fallbacks → worker model → escalation model (+ screenshot) → `ask_human`.

**Cost meter:** every call records `{provider, role, model, input, output, cache_read, $}` to the run. On OpenRouter, the bench JSON adds the ~5.5% credit fee as a separate line (`OPENROUTER_FEE_PCT=5.5`). That feeds the UI ticker, the budget guard and the bench JSON.

**Rough budget:** explore run ≈ 15 steps × 4K in / 200 out on Haiku ≈ **$0.008**. Planner brief ≈ 30K in / 4K out on Sonnet ≈ **$0.10**. Full bench B1–B3 ≈ **< $5**. Total build + bench ≈ **$15–30**.

## 6. Frontend (apps/web)

| Concern | Choice |
|---|---|
| Framework | Next.js (latest stable, App Router), TypeScript strict, pnpm |
| UI | Tailwind v4 + shadcn/ui (via shadcn MCP), Motion, lucide icons, cmdk (⌘K) |
| Data | TanStack Query; native `EventSource` for SSE; WS for frames; zod-validated API types |
| Graph | `@xyflow/react` (React Flow) or a force-graph lib. Benchmark at ~300 nodes |
| Charts | Recharts or visx. Follow the `dataviz` skill (palette validator, light/dark) |
| Fonts | `next/font` (Instrument Serif, Inter/Geist, JetBrains Mono) |
| Quality | ESLint, `tsc --noEmit`, Playwright e2e (390 px + 1440 px), Lighthouse ≥ 90 |

Routes: `/` Today · `/runs/[id]` Run theater · `/memory` · `/skills` · `/bench` · `/about` (architecture for the interview).

## 7. Memory schema (sketch)

```sql
create table entity (
  id text primary key, type text not null, name text not null,
  attrs jsonb not null default '{}', embedding vector(384)          -- embedding optional (P1, fastembed bge-small)
);
create table episode (
  id text primary key, kind text not null,                          -- invoice|approval|rejection|chat|run|seed
  payload jsonb not null, occurred_at timestamptz not null, recorded_at timestamptz default now()
);
create table fact (
  id text primary key, subject_id text references entity(id), predicate text not null,
  object_id text references entity(id), value jsonb,
  valid_from timestamptz not null, valid_to timestamptz,            -- valid time
  recorded_at timestamptz not null default now(),                   -- transaction time
  source_episode text references episode(id), confidence real not null default 1.0
);
create index on fact (subject_id, predicate, valid_from desc);
-- "as of" query:  valid_from <= :t and (valid_to is null or valid_to > :t)
```

## 8. Hosting and operations (cheap, reliable)

| Piece | Where | Cost |
|---|---|---|
| Web | Vercel Hobby | $0 |
| API + portals + Postgres + Chromium | AWS Lightsail, Ubuntu 24.04, **2 GB / 2 vCPU** instance plus a **2 GB swap file**, static IP, docker compose, `restart: unless-stopped`, one Chromium with 2 contexts | ~$12/mo (check the current free-trial offer); 4 GB ($24/mo) is the safe upgrade if memory is tight; delete after the interview |
| LLM | OpenRouter credits (or Anthropic direct) | pay-as-you-go; set a credit limit on the key |
| TLS / DNS | Caddy auto-HTTPS on `api.<ip>.sslip.io` and `portals.<ip>.sslip.io` (no domain purchase needed) | $0 |
| Errors (P1) | Sentry free tier | $0 |
| Traces (P1) | Langfuse Cloud Hobby | $0 |
| CI | GitHub Actions: lint, typecheck, unit tests, compose-based e2e | $0 |

- **Deploy:** `infra/deploy.sh`: ssh → `git pull` → `docker compose up -d --build` → wait for health → smoke test. Take a Lightsail snapshot before the final deploy (rollback in 2 minutes).
- **Guards:** daily LLM budget cap, per-IP rate limit on mutation endpoints, live mode behind `DEMO_ACCESS_CODE`, CORS restricted to the Vercel domain.
- **Fallback:** no AWS account or quota issue → the same compose file runs on Hetzner CX22 (~€4/mo) or Fly.io. Keep compose portable.
- **Freeze:** no deploys after Fri 11:30.

## 9. Security notes (talking points)
- Secrets live in a server-side vault (env or file); the model only sees `secret_key` names; events are redacted.
- Navigation domain allowlist per run; page content is treated as untrusted (prompt-injection P1 demo).
- Idempotency keys; dry-run previews; undo where the portal supports it.
- No PII; synthetic or open data only, clearly labelled.

## 10. How this maps to the real Super44 problem
- **Adapter strategy:** API-first integrations where they exist (POS, accounting). Browser skills cover the long tail of portals without APIs. Both expose the same `Action` interface to the planner.
- **Skills per portal** are shared across merchants on the same portal. One merchant's heal fixes everyone. Compounding at the network level.
- **Memory per merchant** plus a cross-merchant "best practices" layer (their "unique dataset of industry knowledge").
- **Human handoff** (CAPTCHA, 2FA on the owner's phone, ambiguous choices) as first-class UX, not a failure.
