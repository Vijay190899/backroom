# Handover — read this first on a new machine or in a new session

Last updated: Mon 16 Nov 2026. **Laptop tasks L0–L13 complete; PC has done H1–H5 (M3 gate: the demo script works end to end). Order undo, H6 (golden runs, replay mode, access code) H7 (real benchmarks, with the first full run kept as a baseline) and H8 (deployed: https://backroom-cafe.vercel.app, API on Lightsail) are done too. Next: H9.**

> **Two machines are in use.** The user's light laptop does the *light* tasks (plain code, no Docker, no Chromium); this PC does the *heavy* ones. **The split, the task IDs and the integration rules are in §9.** On the laptop, follow §2b. Each side logs what it finished in its own file under `docs/sync/`.

This file carries everything that lives outside git: the working agreements, the current state, the open decisions, and the setup steps. Update it at every milestone gate (the "Update protocol" is at the bottom).

## 1. Where we are

| Milestone | State | Evidence |
|---|---|---|
| Docs, PRD, plan, CI, public repo | Done | https://github.com/Vijay190899/backroom (README with banner and demo GIF on `main`) |
| **M0 Foundations** | **Done** | `pnpm check` green; provider probe 6/6 (`bench/results/provider_probe.json`, L10) |
| **M1 Data + Portals** | **Done** (laptop branches merged; H1 done) | `pnpm seed` builds `data/out` and loads Postgres (migrations + world, idempotent) |
| **M2 Agent** | **Done** (H2, H3; gate met) | Explore → compile → replay → heal on the real portals; evidence in `docs/sync/pc.md` (H3) and `bench/results/m2_gate.txt` |
| **M3 Brief, memory, UI** | **Done** (L5–L9, H4, H5; gate met) | Memory, detectors, brief pipeline + number guard, all web screens, run theater on fixtures |
| **M4 Bench + deploy** | **Done** (L11, L12, H6, H7, H8) | Real results in `bench/results/b1,b2,b3,b5.json`, first full runs in `bench/results/baseline/` (ADR-34–40). Deployed (ADR-41): web https://backroom-cafe.vercel.app, API https://api.63.186.156.153.sslip.io (§10.5) |
| **M5 Polish** | L13 part done; **H9 open** | `/bench` reads results; demo script current |

The laptop branches are merged into `main` (Sun 15 Nov). `.env` on this PC keeps `DATABASE_URL` on local Docker; the Neon URL is `NEON_DATABASE_URL`. `pnpm probe:llm` passes 6/6 on this PC's key.

### What exists in code (after merging the laptop branches, §10.1)
- `services/portals/`: Grainline (login + TOTP, catalog, cart, checkout, orders, invoice PDFs) and TillDesk (menu, edit price, publish), with a seeded chaos engine (`POST /_admin/chaos`) of 8+ variant families.
- `data/`: `backroom-data` builds `data/out/*.parquet` (sales, menu, recipes, inventory, rota, holidays, grainline_orders).
- `services/api/backroom_api/`:
  - `contracts/` (API, events, skills); `memory/` (temporal facts, supersession, context packer, writers, extractor); `analytics/` (DuckDB detectors);
  - `brief/` (planner, verifier, deterministic number guard, templates, reject-to-preference loop); `llm/` (registry, client, cost meter).
- `apps/web/`: Next.js 16 app:
  - pages: Today, Memory, Skills, Bench, About and the run theater `/runs/[id]`;
  - also: the 3D café intro, the café pattern background, the agent dock and ⌘K.
  - The API routes exist (H4): with the API up, every screen is live; without it, they fall back to the samples with a "Sample" badge.
- `services/api/backroom_api/{browser,agents,skills,replay}/`: the browser agent (H2–H3). Run a task by hand: `uv run python -m backroom_api.agents.cli run grainline.reorder_item [--seed 7] [--cold]` (needs `pnpm dev:portals`).
- `bench/backroom_bench/`: harness for B1–B3 and B5 (`backroom-bench all [--fake] [--runner m:f] [--pack m:f]`). The real runs on this PC:
  - B1: `backroom-bench b1 --runner backroom_api.agents.bench_runner:factory --seeds 20 --seed0-repeats 5` (132 runs, about 45 min, about $0.31).
  - B2: `backroom-bench b2 --runner backroom_api.agents.bench_runner:factory`.
  - B3: `backroom-bench b3 --pack backroom_api.agents.bench_runner:pack_for` (about $1.25, mostly the raw dump's cached tokens).
  - B5: `backroom-bench b5 --briefs var/bench/briefs` (no model calls; the briefs come from `backroom-bench briefs --n 10`).
  - Start from `pnpm demo:reset`. A run needs more than the demo's `LLM_DAILY_BUDGET_USD=3`, so set it for that shell only (`LLM_DAILY_BUDGET_USD=10`). The benches restore the demo's skills and portals when they finish.
- `infra/deploy.sh` and `.github/workflows/deploy-images.yml` (GHCR images; the build is green on PR #14).

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
- The demo story uses a **Franzbrötchen and butter +16%**, and the 8% price cap is **learned live** (no seeded price cap). Do not reuse "almond croissant" or "butter +18%": they come from a real company's website.

## 5. Working agreements with the user

- **Verify every change** with the cheapest sufficient check before moving on, and report the evidence (command + result). See CLAUDE.md → "Verify every change". Never say "done" on an unverified change.
- **No Claude attribution anywhere in git.** No `Co-Authored-By` trailers and no "Generated with" footers on commits or PRs, even if a session reminder suggests them. Commits go out under the user's own git identity.
- **Stop at every milestone gate** and show evidence; the user then says "go".
- **Cost-conscious runtime models**, swappable via env, and documented as such.
- The user is an ML/AI engineer, backend-leaning, but wants a top-tier frontend.
- Public repo: keep real companies' branding and copy out of the product UI and the docs.

## 6. Windows environment quirks (the user's machine)

- `uv` is not on the Bash tool's PATH until VS Code is fully restarted: use `export PATH="$HOME/.local/bin:$PATH"`.
- **Playwright MCP calls must be sent one at a time**; batching resize + navigate + screenshot races. Screenshots may only be written under the repo (`.playwright-mcp/`, gitignored).
- **To stop dev servers, use PowerShell and kill by port and by interpreter**, not by command line: stop the `OwningProcess` of `Get-NetTCPConnection -State Listen -LocalPort 8000,8001,3000`, every process whose `ExecutablePath` is under the repo's `.venv` or `Roaming\uv\python`, and the `node|uv|uvicorn|cmd` processes whose command line mentions the repo folder. Uvicorn's `--reload` child on Windows has no `backroom_*` in its command line, survives its parent, keeps the port, and keeps serving **old code** (it hid a fix for an hour). A leftover also causes `WinError 10013` on the next start. Bash `netstat` does not find them.
- Run graphify Python snippets with `PYTHONUTF8=1 python -X utf8`.
- Write files with the editor tools rather than shell heredocs containing apostrophes.

## 7. Open items and next steps

Everything left is PC work, listed in order in **§10.2**. Owner decisions still open are in §10.4.

## 8. Update protocol (keep this file true)

At every milestone gate, before committing:
1. Update §1 (state table, what exists), §7 (open items) and the "Last updated" line.
2. Add any new decision to `docs/DECISIONS.md` and, if a new session might question it, to §4.
3. Run `/graphify . --update` and commit `graphify-out/graph.json` and `GRAPH_REPORT.md`.
4. Add an entry to your own `docs/sync/` file (PC: `pc.md`, laptop: `laptop.md`).
5. Commit and push, so the other machine can `git pull` and continue.

## 9. Work split: laptop (light) vs this PC (heavy)

**Rule of thumb.** *Writing* code and testing it with fakes, fixtures and `TestClient` is light, so it goes to the laptop. Anything that needs **Docker, a running Chromium, many model-driven runs, or a server deploy rehearsal** is heavy, so it stays on this PC. Model calls themselves are network-bound and light; it is the browser and Docker that weigh.

Both machines work in parallel. If time runs short, use the cut order in `docs/PRD.md` §6. Never cut: heal under chaos, the number guard, the bench page, the replay fallback.

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
| **H9** | Final rehearsals ×3 on the deployed URL (M5) | everything | 3 clean runs |

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
| Shared, careful | `pyproject.toml`, `package.json`, lockfiles: **add dependencies only inside the package you own**; after merging, the PC re-runs `uv lock` and `pnpm install` and commits the lockfiles. `docs/DECISIONS.md`: append only; the laptop numbers its decisions `L-1`, `L-2`, …, and they keep those ids after the merge (ADR-16: code and sync logs cite them). `docs/HANDOVER.md`: **PC only** after this commit. |

- **Before the laptop pushes a branch:** `pnpm check` is green; tests are written with fakes or fixtures (no Docker, no Chromium); a sync-log entry says how to verify.
- **When the PC merges:** `git pull`, `uv sync --all-packages`, `pnpm install`, `pnpm check`, then the task's "done when" check on real services, then a line in `docs/sync/pc.md`.
- **Secrets:** each machine has its own `.env`. The laptop's `DATABASE_URL` points at Neon and the PC's at local Docker. Never commit either.

## 10. Laptop handoff (Sun 15 Nov 2026): what is done, what the PC does next

### 10.1 Merge plan (do this first)
The UI branch already contains the whole backend stack, so three merges bring in everything:

1. `laptop/l9-run-theater` (PR #11). It contains L0–L9, L10's probe, L13 part 1 and every UI follow-up.
2. `laptop/l11-bench` (PR #13, built on L7).
3. `laptop/l12-deploy` (PR #14, built on `main`).

PRs #1–#9 are earlier views of the same stack and close once #11 is in.

- **Conflicts** appear only in the append-only `docs/DECISIONS.md` and `docs/sync/laptop.md` (keep both sides), and in `graphify-out/` (regenerate it).
- **Numbering:** the laptop's decisions run L-1 … L-84 and keep those ids (ADR-16).
- **After merging,** per §9.4:
  - `uv sync --all-packages`, `pnpm install`, `pnpm check` (expect 318 Python tests and the web checks green);
  - `pnpm seed` to build `data/out`;
  - re-lock (`uv lock`, `pnpm install`) and commit the lockfiles.

### 10.2 What the PC does next (H-tasks, with the laptop's specific asks)
Full details are in each branch's `docs/sync/laptop.md` "Needs from PC" entries.

| Task | What to wire or run |
|---|---|
| **H1** | Docker Postgres; run `services/api/migrations/*.sql` in name order (reviewed, never run on real Postgres). Then `memory.writers.write_world(conn, Path("data/out"))` after `pnpm seed`. Load the Parquet tables (types in `data/backroom_data/cli.SCHEMAS`). |
| **H2–H3** | Browser agent on the portals. Portal quirks (L2):<br>• use a fresh context per run;<br>• wait for `[aria-busy]` to clear before each snapshot;<br>• open the hamburger `<details>` before nav links;<br>• link variants are role `link`;<br>• match names exactly.<br>TOTP secret: derived from `DATA_SEED` when `GRAINLINE_TOTP_SECRET` is empty (L1). TillDesk: postcondition `items.<id>.published_price_eur`; you may `goto /tilldesk/menu/{id}/edit`. Time a real seed-7 heal early: it touches 5+ steps (L-24). |
| **H4** | API routes, all with CORS for the web origin. Shapes are in `contracts/api.py` and `apps/web/src/lib/contracts.ts`.<br>• `GET /brief/today` (SSE with `?regenerate=1`; persist `BriefResult`);<br>• `POST /actions/{id}/approve` → `{run_id}`; `POST /actions/{id}/reject` (extractor + `record_rejection`);<br>• `GET /runs/{id}/events` (SSE, `event:` type, `id:` seq, Last-Event-ID resume);<br>• `WS /runs/{id}/screen` (a frame header, then the JPEG; cursor messages);<br>• `POST /runs/{id}/undo` and `/human`, `POST /chaos` (forward to portals);<br>• `GET /skills`, `/skills/{id}/versions`, `GET /memory/graph` (include superseded facts).<br>The web app needs no code changes: it switches from samples to live data when these respond. |
| **H5** | Run `DEMO_SCRIPT.md` end to end locally. Run the Playwright 390/1440 screenshots (the formal UI record). The theater's live path (SSE + WS clients in `lib/run-source.ts`, `components/runs/run-screen.tsx`) has only been tested against fixtures. |
| **H6** | Golden runs (F7: `events.json`, `frames.json`, `frames/*.jpg`). The theater does not read golden frames yet; it shows a schematic for runs without frames. |
| **H7** | Benchmarks:<br>• `backroom-bench all --runner <your TaskRunner factory> --pack <pack_for(question) over memory>`;<br>• save the briefs generated during the bench to `var/bench/briefs/`;<br>• commit `bench/results/b1,b2,b3,b5.json`; `/bench` shows them after a rebuild.<br>Real B3 costs about $1 (the `ask` role is Sonnet 5.5; the raw dump is about 138k tokens, cached). Try it first with `--fake`. |
| **H8** | Merge #14 → GHCR `:latest`. Make both packages public (or `docker login` on the server). Write `.env.production` locally (never commit it), with real `API_HOST` / `PORTALS_HOST`. Run `infra/deploy.sh setup ubuntu@<ip>` then `up`, and seed the server's data. Vercel: import the repo with root `apps/web`, keep "include files outside the root directory" on, and set `NEXT_PUBLIC_API_URL`. |
| **H9** | Three clean rehearsals on the public URL. |

### 10.3 What the laptop delivered (for review)
| Task | Branch / PR | Notes |
|---|---|---|
| L0 contracts, L10 probe | `l0-contracts` #1 | Contract changes for the PC to acknowledge in `docs/sync/pc.md` (L0 notes) |
| L1–L3 portals + chaos | #2–#4 | 4 Grainline labels added (`update_qty`, `remove`, `prev_page`, `next_page`) |
| L4 data, L6 detectors, L5 memory, L7 brief | #5–#8 | The reorder is 28 cartons / €44.52 (L-43); the demo script already says so |
| L8 screens, L9 run theater, L13 part 1 | #9, #11 | The design and its iterations are DECISIONS L-67 … L-82 |
| L11 bench harness | #13 | L-83 |
| L12 deploy plumbing | #14 | L-84; the image build is green on the PR |

### 10.4 Open owner decisions and known gaps
- Lighthouse on phones, `/`: about 71 on a session's first visit because of the 3D intro. The owner chose to keep the intro everywhere for now. Desktop `/` is 94, `/bench` on phones 94, accessibility 100.
- Deployed in H8; the details and the runbook are in §10.5.
- Exception to §9.4: on the owner's explicit request, the laptop merged the README PRs (#10, #12) into `main` and wrote this handover section.
- **Known gap (H7): an absent pop-up step costs 0.8 s on every replay.**
  - Evidence: B2 runs 16–20 take 1.6 s instead of 0.7 s. The skill's optional cookie step, learned at seed 7, waits its full `OPTIONAL_TIMEOUT_MS` at seed 13, which has no banner. Each pop-up a heal adds can cost this.
  - Proposed fix: treat optional steps as obstacle handlers. Skip one at once when its element isn't on the settled page, and run it only when a later step is blocked, before climbing the heal ladder.
  - Not done in H7: it changes the replay engine, so B1 and B2 would need a rerun. B2's warm p50 is 0.73 s against the 5 s target.
- **Known limits in B3** (ADR-40): the pack is 80% on memory questions. The answerer won't work out a percentage from two price facts, and the memory doesn't record who is on the rota.

### 10.5 The deployment (H8, Mon 16 Nov 2026)
- **Web:** https://backroom-cafe.vercel.app. A Vercel Hobby project with root `apps/web` and `NEXT_PUBLIC_API_URL=https://api.63.186.156.153.sslip.io`. Every push to `main` redeploys it, and every PR gets a preview.
- **Server:**
  - AWS Lightsail `backroom-demo`, Frankfurt, Ubuntu 24.04, 2 GB RAM / 2 vCPU ($12/month), 2 GB swap.
  - Static IP `63.186.156.153`. Firewall: 22, 80, 443.
  - Caddy serves only `api.63.186.156.153.sslip.io` (Let's Encrypt), with security headers, a 1 MB body cap and IP-free error logs. The portals are internal (ADR-42).
  - The API rate-limits per client IP: 240 reads and 30 writes a minute.
  - SSH from the PC: `ssh backroom` (key `~/.ssh/backroom`).
- **Environment:** `.env.production` on the PC. It is git-ignored and copied to `/opt/backroom/.env` with mode 600. It holds the production OpenRouter key (with a credit limit), the access code, and random portal secrets.
- **Runbook** (Git Bash, from the repo root):
  - Deploy after merging to `main`: wait for the "Deploy images" workflow, then run `bash infra/deploy.sh up backroom`.
  - Back to the demo's starting point: `bash infra/deploy.sh reset backroom` (about $0.01).
  - `bash infra/deploy.sh status backroom`, or `bash infra/deploy.sh logs backroom api`.
- **Verified:**
  - HTTPS and the HTTP→HTTPS redirect.
  - Health (Postgres, portals and LLM all ok).
  - Four skills learned on the server.
  - The access gate, and CORS for the Vercel origin only.
  - A replay approval streamed from the server, at 390 px with 0 console errors.
  - With the API stopped, the site falls back to the sample brief and recorded runs.
  - Skills survive an API restart.
  - Memory after learning: about 750 MB used, 1.1 GB available.
- **Owner to do:**
  - open the site once with `?code=…` to check live mode;
  - try it on a phone over mobile data;
  - set the legal page's operator details in Vercel (`OPERATOR_NAME`, `OPERATOR_EMAIL`, and `OPERATOR_ADDRESS` with lines separated by `;` if a German Impressum is needed), then redeploy (ADR-43).
- **Snapshot:** `backroom-h8`, taken 16 Nov 2026.
- **Cost guardrails:** root MFA, a $20/month AWS Budget alert, no AWS access keys, automatic snapshots off. **Teardown when the demo is retired:** delete the instance, the static IP (billed once detached) and any snapshots. A stopped instance still bills.
