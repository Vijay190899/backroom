# Build Plan — Wed 11 Nov 22:00 → Fri 13 Nov 11:30 (freeze)

Every milestone has a **gate**: don't start the next one until its acceptance checks pass, or until you consciously cut scope (log it in DECISIONS.md). Every step inside a milestone is verified before the next one starts (see "Verify every change" in CLAUDE.md). Times are targets. The cut list is in [PRD §6](PRD.md#6-prioritisation).

## M0 — Foundations · Wed 22:00–23:00
- Root task runner and workspaces ([ARCHITECTURE §2](ARCHITECTURE.md#2-repository-layout)):
  - `package.json` + `pnpm-workspace.yaml`
  - `pyproject.toml` (uv workspace) + `.python-version` (3.12)
  - members `services/api`, `services/portals`, `data`, `bench`, each with a package and its console scripts
- `apps/web` (Next.js); `infra/docker-compose.yml` (postgres, api, portals, caddy).
- `llm/registry.py` (provider + model mapping + capability flags + price table) and `pnpm probe:llm`.
- Design tokens file + fonts + app shell (sidebar/top bar, theme toggle).
- Extend the existing `.github/workflows/ci.yml`. The python/web jobs auto-activate once `pyproject.toml` / `apps/web/package.json` exist; make sure they pass.
- **Gate:**
  - `pnpm check` is green locally and in CI.
  - `/health` is green.
  - `pnpm probe:llm` passes on OpenRouter (or flags recorded in DECISIONS.md).
  - Web shell renders at 390 px and 1440 px (Playwright MCP screenshots).

## M1 — Data + Portals · Wed 23:00–01:30
- `pnpm seed` (`backroom-data all`):
  - Maven Coffee Shop Sales → one store, EUR, Bonn dates with weekday preserved → Parquet
  - Open-Meteo history + forecast for Bonn; Nager.Date holidays
  - `recipes.yaml`, staff, rota, seeded preference episodes (Tue/Fri ordering; **no price cap**)
  - Idempotent.
- Grainline: login + TOTP, catalog/search, cart, checkout, order history, invoice PDF.
- TillDesk: login, menu list, edit price, publish. **If behind, TillDesk slips to Thu 08:00.**
- Chaos engine with ≥ 8 variant families; seed 0 is canonical.
- **Gate:**
  - Both portals are usable by hand.
  - `pytest` proves same seed → same DOM hash and different seeds → different DOM.
  - Seed data loads into Postgres + DuckDB.

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
- Approve → run. Reject with reason → preference → regenerated brief respects it (Franzbrötchen +12.5% → reject "max 8%" → +7.8%).
- **Gate:** the full [DEMO_SCRIPT](DEMO_SCRIPT.md) works locally end-to-end.
- **Decision at 19:00:** Localboard / Ask (P1) in or out?

## M4 — Bench + Deploy · Thu 19:00–23:30
- `pnpm bench`: B1, B2, B3, B5 (B4 if time). JSON with provider, model IDs, seeds, n, SHA, date.
- `/bench` page rendered from the committed JSON (static; works without the API).
- Lightsail instance + 2 GB swap + static IP + Caddy (sslip.io) + compose; Vercel project; env vars; budget cap; access code; OpenRouter key credit limit.
- Record golden runs → replay mode.
- Add **Live demo** and **Benchmarks** badges to the README (URLs exist now).
- **Gate:**
  - The public URL works on your phone over 4G.
  - `/bench` shows real numbers.
  - Killing the API container makes the UI fall back to replay cleanly.

## M5 — Polish + Rehearse · Fri 08:00–11:30
- UI review pass (`ui-ux-pro-max` review + Playwright screenshots); Lighthouse ≥ 90 (`web-perf` skill + Chrome DevTools MCP).
- README: hero GIF, benchmark table with real numbers.
- Optional 2-minute screen recording as a backup.
- Rehearse the demo script 3× on the deployed URL.
- **11:30 FREEZE.** Take a Lightsail snapshot. No more deploys.

## Working agreements for Fable sessions
- Start each session: read `CLAUDE.md` → `graphify-out/GRAPH_REPORT.md` → the milestone section here.
- One milestone per session where possible. Commit at each gate (`feat(m2): heal ladder + skill diff`).
- After each gate: `/graphify . --update`, then update DECISIONS.md if you deviated.
