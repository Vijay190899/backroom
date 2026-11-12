# Handover — read this first on a new machine or in a new session

Last updated: Thu 12 Nov 2026 (after M0). **Interview: Fri 13 Nov afternoon. Code freeze: Fri 11:30.**

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

## 2. Setup on a new machine (about 10 minutes)

Requires: git, Node 24, pnpm 9, [uv](https://docs.astral.sh/uv/), Docker Desktop (running), `gh` logged in as Vijay190899.

```bash
git clone https://github.com/Vijay190899/backroom && cd backroom
cp .env.example .env            # then add OPENROUTER_API_KEY (and set a credit limit on the key)
pnpm install && uv sync --all-packages
pnpm check                      # must be green before you change anything
pnpm dev                        # Postgres (Docker) + API :8000 + portals :8001 + web :3000
```

Check: `curl localhost:8000/health` → `"status":"ok"`, and http://localhost:3000 shows "Live".

**Not in git, so recreate or copy by hand:**
- `.env`: secrets. Copy the file securely, or re-enter the keys. Never commit it.
- Claude Code memory (`~/.claude/projects/<project>/memory/`): its useful content is summarised in §5 and §6 below, so a fresh session loses nothing.
- Chat history: not needed; this file, `CLAUDE.md` and the docs are the context.

MCP servers (`.mcp.json`) install themselves on first use. Approve them when Claude Code asks, or run `/mcp`. Figma and Vercel need an OAuth sign-in and are optional. Serena needs `uvx` on the PATH. graphify needs `pip install "mcp<2"` into the Python that runs `python -m graphify.serve`.

## 3. Starting a Claude Code session on the new machine

Paste this as the first message:

> Read CLAUDE.md and docs/HANDOVER.md. Then continue with the next milestone in docs/BUILD_PLAN.md. Stop at each gate and show me the evidence.

The graph memory (`graphify-out/graph.json`, `GRAPH_REPORT.md`) is committed, so the `graphify` MCP works immediately without a re-extraction. Refresh it at each gate: `/graphify . --update`.

## 4. Decisions already made (do not re-litigate)

The full list is `docs/DECISIONS.md` (ADR-1 to ADR-13). The ones a new session is most likely to question:
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
- To stop dev servers, use PowerShell (`Get-CimInstance Win32_Process` filtered on `backroom_api.main|backroom_portals.main` or `Super44 Demo` + `next|concurrently`, then `Stop-Process`). Bash `netstat` does not find them, and a leftover server causes `WinError 10013` on the next `pnpm dev`.
- Run graphify Python snippets with `PYTHONUTF8=1 python -X utf8`.
- Write files with the editor tools rather than shell heredocs containing apostrophes.

## 7. Open items and next steps

1. **User action:** add OpenRouter credits and `OPENROUTER_API_KEY` to `.env`, set a credit limit on the key, then run `pnpm probe:llm`. If any capability fails, set `LLM_CAPS_OFF=<names>` in `.env`, record the result in `docs/DECISIONS.md`, and commit `bench/results/provider_probe.json`.
2. **M1** (no model calls needed, so it is not blocked by the key): `backroom-data` pipeline (Maven sales → one store, EUR, Bonn dates; Open-Meteo; Nager.Date; recipes, staff, rota, seeded preferences), Grainline portal, TillDesk portal, chaos engine with ≥ 8 variant families and `POST /_admin/chaos`. Gate in `docs/BUILD_PLAN.md`. The Maven download URL and fallback are in `docs/DATA.md`.
3. **Deploy prerequisites** (needed before M4): an AWS account for Lightsail, a Vercel account. The API image is 4.3 GB, so the first deploy takes a few minutes.
4. `pnpm e2e` is a placeholder that exits non-zero ("lands in M3").
5. Serena MCP: connects only when VS Code's PATH contains `uvx` (a full restart of VS Code fixes it).

## 8. Update protocol (keep this file true)

At every milestone gate, before committing:
1. Update §1 (state table, what exists), §7 (open items) and the "Last updated" line.
2. Add any new decision to `docs/DECISIONS.md` and, if a new session might question it, to §4.
3. Run `/graphify . --update` and commit `graphify-out/graph.json` and `GRAPH_REPORT.md`.
4. Commit and push, so the other machine can `git pull` and continue.
