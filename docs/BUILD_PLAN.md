# Build Plan — Wed 11 Nov 20:00 → Fri 13 Nov 11:30 (freeze)

Every milestone has a **gate**: don't start the next one until its acceptance checks pass, or until you consciously cut scope (log it in DECISIONS.md). Times are targets. The cut list is in [PRD §6](PRD.md#6-prioritisation).

## M0 — Foundations · Wed 20:00–21:00
- Monorepo: `apps/web` (Next.js, pnpm), `services/api` + `services/portals` (uv, Python 3.12), `infra/docker-compose.yml` (postgres, api, portals).
- Design tokens file + fonts + app shell (sidebar/top bar, theme toggle).
- CI workflow: ruff, pyright, pytest, eslint, tsc.
- **Gate:** `docker compose up` → `/health` green; web shell renders at 390 px and 1440 px (check with Playwright MCP screenshots).

## M1 — Data + Portals · Wed 21:00–01:00
- `data/`: download Maven Coffee Shop Sales → transform (one store, EUR, Bonn dates with weekday preserved) → Parquet. Open-Meteo history + forecast for Bonn. Nager.Date holidays. `recipes.yaml`, staff, rota, seeded preference episodes. One `make seed` / `uv run seed` command.
- Grainline: login + TOTP, catalog/search, cart, checkout, order history, invoice PDF.
- TillDesk: login, menu list, edit price, publish.
- Chaos engine with ≥ 8 variant families; seed 0 is canonical.
- **Gate:** both portals usable by hand; `pytest` proves same seed → same DOM hash and different seeds → different DOM; seed data loads into Postgres + DuckDB.

## M2 — Browser agent · Thu 09:00–14:00 (riskiest; do it first, fresh)
- Browser pool, ARIA-snapshot observation, action tools, secret vault, allowlist.
- Explore loop on the worker model with step/$ budgets.
- Skill compiler → JSON skill; replay engine with `expect` checks; heal ladder; skill versioning + diff.
- CDP screencast → WS; run events → SSE; runs persisted.
- **Gate:**
  - "Reorder oat milk ×24": cold explore succeeds at seed 0.
  - Warm replay < 5 s, 0 LLM calls.
  - Seed 3 → heal succeeds and creates v2 with a visible diff.

## M3 — Memory + Brief + UI · Thu 14:00–19:00
- Memory schema, deterministic writers, supersession, context packer.
- Invoice extractor (worker model, structured output, PDF/image).
- Detectors (stockout, margin, weather) → planner → verifier → number guard → `/brief/today`.
- UI: Today cards (evidence drawer), Run theater (timeline + live stream + ticker + chaos toggle), Memory graph with time slider + fact inspector, Skills page.
- Approve → run; reject with reason → preference → regenerated brief respects it.
- **Gate:** the full [DEMO_SCRIPT](DEMO_SCRIPT.md) works locally end-to-end.
- **Decision at 19:00:** Localboard / Ask (P1) in or out?

## M4 — Bench + Deploy · Thu 19:00–23:30
- `bench/`: B1, B2, B3, B5 (B4 if time). JSON with model IDs, seeds, n, SHA, date.
- `/bench` page rendered from the committed JSON (static; works without the API).
- Lightsail instance + static IP + Caddy (sslip.io) + compose; Vercel project; env vars; budget cap; access code.
- Record golden runs → replay mode.
- **Gate:** public URL works on your phone over 4G; `/bench` shows real numbers; killing the API container makes the UI fall back to replay cleanly.

## M5 — Polish + Rehearse · Fri 08:00–11:30
- UI review pass (`ui-ux-pro-max` review + Playwright screenshots); Lighthouse ≥ 90 (`web-perf` skill + Chrome DevTools MCP).
- README: hero GIF, architecture diagram, benchmark table with real numbers, model-swap section.
- Optional 2-minute screen recording as a backup.
- Rehearse the demo script 3× on the deployed URL. Write 5 likely interview questions + answers in DEMO_SCRIPT.md.
- **11:30 FREEZE.** Take a Lightsail snapshot. No more deploys.

## Working agreements for Fable sessions
- Start each session: read `CLAUDE.md` → `graphify-out/GRAPH_REPORT.md` → the milestone section here.
- One milestone per session where possible. Commit at each gate (`feat(m2): heal ladder + skill diff`).
- After each gate: `graphify . --update`, then update DECISIONS.md if you deviated.
