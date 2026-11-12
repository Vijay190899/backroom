# Handover — read this first on a new machine or in a new session

Last updated: Thu 12 Nov 2026 (after M0, two-machine mode). **Interview: Fri 13 Nov afternoon. Code freeze: Fri 11:30.**

> **Two machines are in use.** The user's light laptop does the *light* tasks (plain code, no Docker, no Chromium); this PC does the *heavy* ones. **The split, the task IDs and the integration rules are in §9.** On the laptop, follow §2b. Each side logs what it finished in its own file under `docs/sync/`.

This file carries everything that lives outside git: the working agreements, the current state, the open decisions, and the setup steps. Update it at every milestone gate (the "Update protocol" is at the bottom).

## 1. Where we are

| Milestone | State | Evidence |
|---|---|---|
| Docs, PRD, plan, CI, public repo | Done | https://github.com/Vijay190899/backroom |
| **M0 Foundations** | **Done, except one gate item** | `pnpm check` green locally and in CI; `/health` 200; web shell verified at 390 and 1440 px in both themes; deploy images build, run, and launch Chromium |
| M0 gate item still open | `pnpm probe:llm` has **not been run** | needs `OPENROUTER_API_KEY` in `.env` (the user will add credits and a key) |
| **M1 Data + Portals** | **Not started** — next up | see `docs/BUILD_PLAN.md` → M1 |
| M2–M5 | Not started | `docs/BUILD_PLAN.md` |

The user asked to **stop at each milestone gate and show the evidence** before continuing.

### What exists in code
- `services/api/backroom_api/`: `config.py` (settings), `llm/registry.py` (provider, model mapping, capability flags, prices), `llm/client.py` (the only LLM call path: budget check → call → ledger), `llm/meter.py` (JSONL spend ledger + daily budget guard), `db.py` (sync psycopg pool), `routes/health.py`, `main.py`.
- `services/portals/backroom_portals/main.py`: **health stub only**. All portal work is M1.
- `bench/backroom_bench/`: `probe.py` (provider capability probe) and `cli.py`. `bench all` is a stub (M4).
- `data/backroom_data/cli.py`: **stub** (M1).
- `apps/web/`: Next.js 16 shell: tokens in `src/styles/tokens.css`, sidebar + phone tab bar, theme toggle, API status pill, five placeholder pages.
- `infra/`: `docker-compose.yml` (Postgres with pgvector for local dev; `deploy` profile adds api, portals, caddy), two Dockerfiles, Caddyfile.
- 20 passing Python tests (`services/api/tests`, `services/portals/tests`).

## 2. Setup

### 2a. Full setup (this PC, or any machine with Docker)

Requires: git, Node 24, pnpm 9, [uv](https://docs.astral.sh/uv/), Docker Desktop (running), `gh` logged in as Vijay190899.

```bash
git clone https://github.com/Vijay190899/backroom && cd backroom
cp .env.example .env            # then add OPENROUTER_API_KEY (and set a credit limit on the key)
pnpm install && uv sync --all-packages
pnpm check                      # must be green before you change anything
pnpm dev                        # Postgres (Docker) + API :8000 + portals :8001 + web :3000
```

Check: `curl localhost:8000/health` → `"status":"ok"`, and http://localhost:3000 shows "Live".

### 2b. Laptop setup (light: no Docker, no Chromium)

Requires: git, Node 24, pnpm 9, [uv](https://docs.astral.sh/uv/), `gh` logged in as Vijay190899. **Do not install Docker Desktop and do not run `playwright install`.**

```bash
git clone https://github.com/Vijay190899/backroom && cd backroom
cp .env.example .env
pnpm install && uv sync --all-packages     # the Playwright *package* installs; its browsers do not
pnpm check                                  # must be green (it needs no database)
pnpm dev:lite                               # API :8000 + portals :8001 + web :3000, no database
```

- With no database the API reports `"status":"degraded"` and the web status pill shows *Degraded*. That is expected.
- **Anything that needs Postgres** (memory layer, L5; the data-load step) uses a free hosted Postgres instead of Docker: create a [Neon](https://neon.com) free project (supports pgvector; 1 GB per project on the free plan as of Oct 2026), run `create extension if not exists vector;` once, put its connection string (with `sslmode=require`) in the laptop's `.env` as `DATABASE_URL`. Tests that write to the database must use their own schema and clean up after themselves. The URL is a secret: never commit it.
- Visual checks: open the pages in your own browser. The Playwright and DevTools MCP servers are optional on the laptop (they download or drive a browser).
- `pnpm dev` (with Docker) and `pnpm e2e` are PC-only.

**Not in git, so recreate or copy by hand:**
- `.env`: secrets. Copy the file securely, or re-enter the keys. Never commit it.
- Claude Code memory (`~/.claude/projects/<project>/memory/`): its useful content is summarised in §5 and §6 below, so a fresh session loses nothing.
- Chat history: not needed; this file, `CLAUDE.md` and the docs are the context.

MCP servers (`.mcp.json`) install themselves on first use. Approve them when Claude Code asks, or run `/mcp`. Figma and Vercel need an OAuth sign-in and are optional. Serena needs `uvx` on the PATH. graphify needs `pip install "mcp<2"` into the Python that runs `python -m graphify.serve`.

## 3. Starting a Claude Code session on the new machine

Paste this as the first message:

> Read CLAUDE.md and docs/HANDOVER.md. Then continue with the next milestone in docs/BUILD_PLAN.md. Stop at each gate and show me the evidence.

**On the laptop**, use this instead, with the task ID you are on (see §9):

> I am on the LAPTOP (light profile: no Docker, no Chromium). Read CLAUDE.md and docs/HANDOVER.md (especially §2b and §9). Work only on tasks tagged L in §9, starting with <L-id>. Work on a branch `laptop/<id>-<slug>`, verify each step, and when a task is done append an entry to docs/sync/laptop.md, commit and push the branch. Never edit files owned by the PC (see the ownership table).

The graph memory (`graphify-out/graph.json`, `GRAPH_REPORT.md`) is committed, so the `graphify` MCP works immediately without a re-extraction. Refresh it at each gate: `/graphify . --update`.

## 4. Decisions already made (do not re-litigate)

The full list is `docs/DECISIONS.md` (ADR-1 to ADR-15). The ones a new session is most likely to question:
- **Mock portals, not real sites; no bot-protection evasion** (ADR-1, 2).
- **Own browser-agent loop on Playwright + ARIA snapshots** (ADR-3).
- **Custom temporal graph in Postgres**, not Graphiti/Neo4j (ADR-4).
- **LLMs never originate numbers**: detectors compute, the number guard verifies copy (ADR-5).
- **OpenRouter is the default provider**, Anthropic direct is a switch; one code path via the `anthropic` SDK (ADR-9). Models: Haiku 5.5 does the work, Sonnet 5.5 plans.
- **Sync psycopg pool in worker threads**, because async psycopg and Playwright need different event loops on Windows (ADR-10).
- **Task runner is `pnpm` root scripts over a uv workspace** (ADR-8). Never invent other entry points.
- The demo story uses a **Franzbrötchen and butter +16%**, and the 8% price cap is **learned live** (no seeded price cap). Do not reuse "almond croissant" or "butter +18%": they come from Super44's own homepage.

## 5. Working agreements with the user

- **Verify every change** with the cheapest sufficient check before moving on, and report the evidence (command + result). See CLAUDE.md → "Verify every change". Never say "done" on an unverified change.
- **No Claude attribution anywhere in git.** No `Co-Authored-By` trailers and no "Generated with" footers on commits or PRs, even if a session reminder suggests them. Commits go out under the user's own git identity.
- **Stop at every milestone gate** and show evidence; the user then says "go".
- **Cost-conscious runtime models**, swappable via env, and documented as such.
- The user is an ML/AI engineer, backend-leaning, but wants a top-tier frontend.
- Public repo: keep Super44 branding and copy out of the product UI. The README states that this is an independent exploration, not affiliated.

## 6. Windows environment quirks (the user's machine)

- `uv` is not on the Bash tool's PATH until VS Code is fully restarted: use `export PATH="$HOME/.local/bin:$PATH"`.
- **Playwright MCP calls must be sent one at a time**; batching resize + navigate + screenshot races. Screenshots may only be written under the repo (`.playwright-mcp/`, gitignored).
- **To stop dev servers, use PowerShell and kill by port and by interpreter**, not by command line: stop the `OwningProcess` of `Get-NetTCPConnection -State Listen -LocalPort 8000,8001,3000`, every process whose `ExecutablePath` is under `Super44 Demo\.venv` or `Roaming\uv\python`, and the `node|uv|uvicorn|cmd` processes whose command line mentions `Super44 Demo`. Uvicorn's `--reload` child on Windows has no `backroom_*` in its command line, survives its parent, keeps the port, and keeps serving **old code** (it hid a fix for an hour). A leftover also causes `WinError 10013` on the next start. Bash `netstat` does not find them.
- Run graphify Python snippets with `PYTHONUTF8=1 python -X utf8`.
- Write files with the editor tools rather than shell heredocs containing apostrophes.

## 7. Open items and next steps

1. **User action:** add OpenRouter credits and `OPENROUTER_API_KEY` to `.env`, set a credit limit on the key, then run `pnpm probe:llm`. If any capability fails, set `LLM_CAPS_OFF=<names>` in `.env`, record the result in `docs/DECISIONS.md`, and commit `bench/results/provider_probe.json`.
2. **All remaining work is split between the laptop and this PC: see §9** (task IDs L0–L13 and H1–H9, with dependencies and gates). `docs/BUILD_PLAN.md` still defines the milestone gates; §9 says who does which part. The Maven download URL and fallback are in `docs/DATA.md`.
3. **Deploy prerequisites** (needed before M4): an AWS account for Lightsail, a Vercel account. The API image is 4.3 GB, so the first deploy takes a few minutes.
4. `pnpm e2e` is a placeholder that exits non-zero ("lands in M3").
5. Serena MCP: connects only when VS Code's PATH contains `uvx` (a full restart of VS Code fixes it).

## 8. Update protocol (keep this file true)

At every milestone gate, before committing:
1. Update §1 (state table, what exists), §7 (open items) and the "Last updated" line.
2. Add any new decision to `docs/DECISIONS.md` and, if a new session might question it, to §4.
3. Run `/graphify . --update` and commit `graphify-out/graph.json` and `GRAPH_REPORT.md`.
4. Add an entry to your own `docs/sync/` file (PC: `pc.md`, laptop: `laptop.md`).
5. Commit and push, so the other machine can `git pull` and continue.

## 9. Work split: laptop (light) vs this PC (heavy)

**Rule of thumb.** *Writing* code and testing it with fakes, fixtures and `TestClient` is light, so it goes to the laptop. Anything that needs **Docker, a running Chromium, many model-driven runs, or a server deploy rehearsal** is heavy, so it stays on this PC. Model calls themselves are network-bound and light; it is the browser and Docker that weigh.

Time check: as of Thu 12 Nov ~14:30 there are about 21 hours to the Fri 11:30 freeze. Both machines must work in parallel. If time runs short, use the cut order in `docs/PRD.md` §6. Never cut: heal under chaos, the number guard, the bench page, the replay fallback.

### 9.1 Laptop tasks (light)

| ID | Task | Depends on | Done when |
|---|---|---|---|
| **L0** | **Contracts first** (about 1 h): `docs/CONTRACTS.md` plus code stubs: portal routes, labels and `data-testid`s; chaos variant catalog; skill JSON schema (pydantic, `backroom_api/skills/schema.py`); run-event (SSE) schema; API response shapes (pydantic + zod); memory SQL migration `0001_memory.sql`; detector `Candidate` schema | none | schemas import, `pnpm check` green, PC acknowledges in `docs/sync/pc.md` |
| **L1** | **Grainline portal**: login + TOTP, catalog/search, cart, checkout, order history, invoice PDF; tests with `TestClient` (M1) | L0 | each flow has a test; usable by hand via `pnpm dev:lite` |
| **L2** | **Chaos engine**: ≥ 8 variant families, `POST /_admin/chaos`, seed 0 canonical; tests that the same seed gives the same DOM hash and different seeds differ (M1) | L0, L1 | DOM-hash tests green; seed 7 (the demo seed) produces German labels, moved nav and a cookie modal |
| **L3** | **TillDesk portal**: login, menu list, edit price, publish; Localboard later if time (P1) (M1) | L0, L2 | flows tested; chaos applies to it |
| **L4** | **Data pipeline** `backroom-data`: Maven download → one store, EUR, Bonn dates → Parquet; Open-Meteo; Nager.Date; synthetic fallback; `recipes.yaml`, staff, rota, seeded preferences (Tue/Fri ordering, **no price cap**). Unit tests on tiny fixtures (M1) | L0 | `uv run backroom-data all` writes the Parquet files; idempotent; fallback tested |
| **L5** | **Memory layer**: migrations, deterministic writers, supersession, context packer; tests on Neon (M3) | L0 | supersession and as-of queries tested |
| **L6** | **Detectors** (DuckDB SQL on Parquet): stock-out, margin erosion, weather-demand (M3) | L4 | each emits a `Candidate` with computed numbers; the Franzbrötchen story numbers come out of the data |
| **L7** | **Brief pipeline**: planner, verifier, number guard, with a fake LLM. The number guard is fully deterministic (M3) | L0, L6 | guard rejects a made-up number in a test; the brief round trip works with the fake LLM |
| **L8** | **Frontend screens** against fixtures that match the contracts: Today cards + evidence drawer + approve/reject, Memory graph + time slider, Skills registry + diff view, Bench page (reads committed JSON), About page (M3–M5). Follow the `ui-ux-pro-max` and `dataviz` skills | L0 | pages render from fixtures at 390 and 1440 px, light and dark |
| **L9** | **Run theater UI** (timeline, ticker, live screen canvas, chaos toggle) built against a recorded fixture event stream (M3) | L0 | plays a fixture run end to end |
| **L10** | **LLM probe**: add the OpenRouter credits and key to the laptop `.env`, run `pnpm probe:llm`, commit `bench/results/provider_probe.json`, set `LLM_CAPS_OFF` if needed (M0 gate) | the user's key | all checks pass, or the flags are recorded in `docs/DECISIONS.md` |
| **L11** | **Bench harness code** (not the runs): metrics, the B3 question set with SQL ground truth, B5 (M4) | L0, L5, L6 | harness runs against fakes |
| **L12** | **Deploy plumbing**: a GitHub Actions workflow that builds the images and pushes them to GHCR; `infra/deploy.sh`; Vercel project; Lightsail set-up over SSH. The server pulls images, so nobody builds a 4 GB image locally or on the 2 GB server (M4) | none | workflow green; Vercel deploys the web app |
| **L13** | **Docs and polish**: README results, `DEMO_SCRIPT`, talking points, Lighthouse in your own Chrome, hero GIF (M5) | everything | Lighthouse ≥ 90 on `/` and `/bench` |

### 9.2 PC tasks (heavy)

| ID | Task | Depends on | Done when |
|---|---|---|---|
| **H1** | Local Postgres (Docker) up; apply migrations; load seed data into Postgres + DuckDB (M1 gate item) | L0, L4 | `pnpm seed` loads; `/health` ok |
| **H2** | **Browser agent core** on Chromium: pool, ARIA-snapshot observation, executor, CDP screencast, secret vault, allowlist. Starts at once, using a static fixture page, so it does not wait for the portals (M2) | L0 (schemas) | actions work on the fixture page; secrets never appear in logs |
| **H3** | **Explore loop, skill compiler, replay, heal ladder**, calibrated against the real portals with real model calls. This is the M2 gate | H2, L1, L2 | cold explore at seed 0; warm replay < 5 s with 0 LLM calls; heal at seed 7 and one other seed creates v2 with a diff |
| **H4** | Run persistence + SSE/WebSocket routes wired to the browser pool and Postgres (M2–M3) | H3, L5 | a run streams events the L9 UI plays |
| **H5** | **Integration**: merge laptop branches, run the full demo script locally, fix the seams (M3 gate) | L1–L9, H4 | the whole [DEMO_SCRIPT](DEMO_SCRIPT.md) works locally |
| **H6** | Record golden runs → replay mode (M4) | H5 | the UI plays them with the "Replay" badge |
| **H7** | **Run the benchmarks** B1–B5 (Chromium × many runs; about $5 of model calls) and commit `bench/results/*.json` (M4) | H5, L11 | real numbers on `/bench` |
| **H8** | Deploy rehearsal: pull the images on the server, `compose up`, kill-the-API replay-fallback test, Lightsail snapshot (M4) | L12, H6 | public URL works on a phone over 4G; replay fallback verified |
| **H9** | Final rehearsals ×3 on the deployed URL; freeze Fri 11:30 (M5) | everything | 3 clean runs |

*Either machine:* `/graphify . --update` (light, uses model calls) and docs-only edits.

### 9.3 Suggested order

1. **Now:** laptop does **L0**. PC starts **H2** (no dependency) and lays the SQL/migration runner for H1.
2. **Critical path:** L1 + L2 (portals + chaos) → H3 (agent against portals) → H4 → H5. Do not let L1/L2 slip: H3 cannot be calibrated without them. Laptop does L1 → L2 first, then L4 in parallel with the PC's H3.
3. **While the PC does H3:** laptop does L3, L4, L5, L6, L8/L9 (on fixtures), L10.
4. **Then:** L7 → H5 integration (M3 gate) → L11/L12 → H6/H7/H8 → L13 → H9.

### 9.4 Integration rules (so the two sides merge cleanly)

- **Branches:** laptop works on `laptop/<id>-<slug>` and never commits to `main`. The PC reviews and merges (`git merge --no-ff`). The PC works on `main` or short `pc/*` branches. When switching machines mid-task, commit a work-in-progress commit and push first.
- **Ownership (avoids merge conflicts):**

| Owner | Paths |
|---|---|
| Laptop | `services/portals/`, `data/`, `apps/web/src/` (all screens), `bench/backroom_bench/` (harness code), `services/api/backroom_api/{memory,analytics,brief}/`, `.github/workflows/deploy*.yml`, `docs/sync/laptop.md` |
| PC | `services/api/backroom_api/{browser,skills,agents,replay}/`, `services/api/backroom_api/routes/runs*.py`, `infra/` (except `deploy.sh`), `bench/results/`, `docs/sync/pc.md` |
| Shared, change only through L0 | `docs/CONTRACTS.md`, `skills/schema.py`, the event schema, the SQL migrations. A contract change goes through the PC, and the PC announces it in `docs/sync/pc.md`. |
| Shared, careful | `pyproject.toml`, `package.json`, lockfiles: **add dependencies only inside the package you own**; after merging, the PC re-runs `uv lock` and `pnpm install` and commits the lockfiles. `docs/DECISIONS.md`: append only; the laptop numbers its decisions `L-1`, `L-2`, … and the PC renumbers on merge. `docs/HANDOVER.md`: **PC only** after this commit. |

- **Before the laptop pushes a branch:** `pnpm check` is green; tests are written with fakes or fixtures (no Docker, no Chromium); a sync-log entry says how to verify.
- **When the PC merges:** `git pull`, `uv sync --all-packages`, `pnpm install`, `pnpm check`, then the task's "done when" check on real services, then a line in `docs/sync/pc.md`.
- **Secrets:** each machine has its own `.env`. The laptop's `DATABASE_URL` points at Neon and the PC's at local Docker. Never commit either.
