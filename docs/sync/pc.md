# Sync log: PC → laptop

Only the **PC** edits this file. Newest entry first. Tell the laptop what changed under it: contracts, new env vars, merged branches, gate results.

Entry format:

```
## <date time> · H<id> / merge of laptop/<id>
Done: what works now.
Laptop must: pull, then run these commands (`uv sync --all-packages`, `pnpm install`, ...).
Contract changes: anything the laptop's code must adapt to.
```

## Mon 16 Nov 2026 · H7 real benchmarks, branch pc/h7-benchmarks
Done:
- **B1, first full run** (41323c9, n = 132): 67% cold at seed 0, 58% warm across 20 seeds; every `download_invoice` run failed. Kept in `bench/results/baseline/`. It exposed three product bugs, all fixed with tests (ADR-36):
  - the "Open menu" `<summary>` is role `generic`, so it is now learned by its text;
  - the invoices page is past the 12k snapshot cut, so explore has a new `find` tool;
  - after a heal, the 600 ms locate timeout also capped the click.
- **B1 after the fixes** (7ec59d4, same design): 0 failures. 100% cold at seed 0 (95% CI 80–100%), 100% warm across 20 seeds (94–100%), every redesigned seed healed, $0.31.
- **B2** (1605fc0): learns in 16 s for $0.003, then replays in 0.7 s at $0. The redesign at run 8 heals with the model (34 s, $0.004); the one at run 15 heals from remembered fallbacks at $0.
- **B3** (1605fc0): the context pack answers 80% of the 10 memory questions (40% in the first run) at 0.9% of the raw dump's tokens. The 20 analytics questions are for SQL (labels committed before any run, ADR-35). Packer changes: entity history, kinds a question names, and grouping under the entity's name (ADR-40).
- **B5** (3969c90): 178 of 178 displayed numbers verified over 10 generated briefs; the model's copy passed first time on 30 of 30 cards.
- **Bug found by running B1 and B3 at once:** two processes overwrote each other's LLM ledger records on Windows, and the torn line stopped every budget check. The ledger now takes a cross-process lock (ADR-11, amended). A four-process test reproduces the old crash and passes now.
- **Bug found while checking `/bench`:** `pnpm dev:api` and `infra/Dockerfile.api` start `backroom_api.main:app`, but H4 had dropped the module-level `app` (only `create_app()` was left), so neither could start the API. It is restored (cheap at import; the pool and browsers are built in `lifespan`). A new test resolves every `module:attr` in `package.json` and both Dockerfiles, and it fails without the fix. This would have broken H8.
- Also: secrets redacted as «hidden» (ADR-37), the `file_downloaded` postcondition and templated element names (ADR-38), result files carry the SHA from the start of the run (ADR-39). `/bench` shows each first full run beside the current one.
- `pnpm check`: 390 passed. `/bench` checked at 390 and 1440 px, light and dark: no horizontal scroll, 0 console errors with the API up.
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`.
Contract changes (CONTRACTS §4): `file_downloaded`; a step may have `target: null` with `fallbacks: [{text}]`; `{{param}}` inside a locator name. The context pack's text is now grouped by entity.
Known gap: an absent pop-up step costs 0.8 s per replay (HANDOVER §10.4).

## Mon 16 Nov 2026 · H6 golden runs and replay mode, branch pc/h6-golden-runs
Done:
- Recorder `python -m backroom_api.replay.golden record`: the demo's four runs recorded from the real stack (reorder 1.1 s, reorder-heal at seed 7 36.5 s / 14 calls / $0.0041, price, cancel), 1.9 MB in `apps/web/public/golden/`. Skills are snapshotted and restored, portals reset.
- Web: `/runs/golden-<name>` plays a recording with its frames and cursor, with no API at all (verified with the API stopped: Offline pill, Replay badge, "● recorded" frames). With no API, approving a card on Today plays its task's recording. `pnpm contracts` checks every golden run (schemas, recorded flag, seq, frames on disk).
- API replay mode (DECISIONS 31-33): `GET /mode`; live needs the access code (`X-Demo-Code`), budget left and `DEMO_MODE=live`. In replay, approve streams the golden run as a normal run (Replay badge, frames on the screen socket, card untouched); reject, regenerate, chaos, undo and human answers return 403 `live_mode_locked` with the reason, which the reject dialog now shows. Web: `?code=` is kept in the browser and sent on every acting call; the status pill shows this visitor's mode with the reason as its tooltip.
- Verified live with `DEMO_ACCESS_CODE=demo-test`: without the code the pill says Replay, approving the price card played the recording through the API, and reject showed "Live mode needs the demo access code"; with `?code=demo-test` the pill says Live and the code leaves the address bar.
- `pnpm check`: 379 passed; UI audit 0 findings on 24 views (with a golden run as the run page).
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`. Contract additions: `ModeInfo` / `GET /mode` (both sides).

## Mon 16 Nov 2026 · Order undo with Grainline's cutoff, branch pc/order-undo
Done:
- New task `grainline.cancel_order {order_id}` (contract `SkillTask` on both sides; label "Cancel an order"); postconditions can select a record by id (`orders.{{order_id}}.status`).
- A reorder's result has `undo_until` (the day before delivery); its run records the undo (cancel that order) before `run.finished` is visible. `POST /runs/{id}/undo` checks Grainline's state first: 409 `too_late` after the cutoff, `already_cancelled` if so; nothing is attempted.
- Theater: "Undo (until Mon 16 Nov)"; the API's reason is shown when it refuses. `pnpm demo:reset` also learns the cancel task (reorder, then cancel that order).
- Live: first undo (cold explore) cancelled GW-10485 in 11.8 s, 8 calls, $0.0015; the second replayed in 0.5 s, 0 calls, $0 (GW-10486); through the theater, GW-10487 cancelled. Grainline's state shows `cancelled` each time.
- Tests: undo cancels exactly the placed order; refused after the cutoff and when already cancelled; select-by-id paths; the cancel path compiles to `/grainline/orders/{{order_id}}`. DECISIONS 30.
- Graph memory refreshed after the M3 gate (docs and code).
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`. New optional env var `PORTALS_TODAY` is now read by the API too (it already existed for the portals).

## Mon 16 Nov 2026 · H5 integration: the demo script end to end, branch pc/h5-integration
Every beat of `docs/DEMO_SCRIPT.md` was run in the browser on live data (real portals, Chromium, OpenRouter), starting from `pnpm demo:reset`:
- 0:00 Today: 3 live cards, Franzbrötchen at €3.60, no cap yet. 0:30 evidence: butter +16.1%, margin 71% → 68% (target 70%).
- 1:00 approve oat milk → replay 1.5 s, 0 calls, $0, GW-10482. 1:40 seed 7 + "Run again on seed 7" → heal 34 s, 13 calls, $0.0039 → v2 with diff on /skills.
- 2:40 Memory at 5 Nov: Butter €7.10/kg (today €8.24). 3:20 reject "too steep, max 8%" in the dialog → €3.20 → €3.45, "Kept under your 8% cap", preference fact in memory.
- Formal UI record: 6 pages x 390/1440 x light/dark, screenshots in `.playwright-mcp/h5/` (gitignored); an audit of console errors, horizontal overflow and covered buttons found 0 issues on all 48 views (healed run and fresh run).
Fixed (all found by running the script; most are seams between laptop UI built on fixtures and real data):
- Theater: no way to "approve again" after the first run (the card is done) → **Run again on seed N** button. Address bar now follows the real page (contract: `step.finished.url`). Duplicate React keys on healed runs; the phone layout overflowed; run results printed raw postconditions → order, total, delivery, "3 of 3 passed".
- Memory: the graph with real data (55 entities) was an unreadable pile → story nodes only, height grows with the busiest column, labels clamped; overlapping date-jump buttons; weather values printed as JSON; **UTC days showed the new butter price a day early** (Bonn days now, with a check).
- Today: an ordered card was offered again after a reload (local status ignored the server's); the idle agent dock covered the first card's buttons on phones.
- API: after midnight every brief request regenerated (cache keyed on the clock's day; now the data's day). Skills page: heal note cut mid-word (now a short summary); a new version showed the healing run's time and cost.
- Agent: the repeat guard reset on URL changes only, which made a cold TillDesk explore fail once; it now compares page content. Step descriptions keep parameter values templated.
- New `pnpm demo:reset` (DECISIONS 26). Contract change: `step.finished.url` (CONTRACTS §5).
`pnpm check`: 372 passed. Open: no fact inspector on Memory (the script's "provenance" is API-only), reorder undo (next branch), `/bench` waits for H7.
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`.

## Sun 15 Nov 2026 · H4 runs, briefs and the API routes, branch pc/h4-runs-api
Done:
- Migration `0002_runs.sql` (brief, action, run, run_event); applied by `pnpm seed` and at API start-up.
- `backroom_api/live/` (repo, RunManager, BriefService) and the routes in `routes/{brief,runs,catalog,errors}.py`: `GET /brief/today` (cached; `?regenerate=1` streams), `POST /actions/{id}/approve` (Idempotency-Key) and `/reject`, `GET /runs/{id}`, `GET /runs/{id}/events` (SSE, Last-Event-ID), `WS /runs/{id}/screen`, `POST /runs/{id}/human` and `/undo`, `GET /skills`, `/skills/{id}/versions`, `GET /memory/graph` (all facts, superseded included), `/memory/facts/{id}`, `GET`/`POST /chaos`. Errors use `{"error": {code, message}}`.
- Live evidence (real portals, Chromium, OpenRouter): brief generated in 7.3 s, cached 0.26 s; approve → order GW-10482, 28 x OAT-1L, €44.52, events streamed and resumed from Last-Event-ID 60 (61-66); a repeated approve is deduplicated; reject "too steep, max 8%" → preference fact → regenerated card €3.45 (+7.8%, "Kept under your 8% cap"); the price run sent 11 JPEG frames and 6 cursor moves to the screen socket; undo restored €3.20. Through the web app: Approve on Today started a real run (GW-10483) and the run theater played it live.
- Tests: `test_api_live.py` (10, own Postgres schema, scripted runner). CI now has a Postgres service. `pnpm check`: 370 passed.
Fixed on the laptop's side, found while testing in the browser:
- **Today cards: the hidden swipe hints covered the Approve and Not now buttons**, so a mouse click on them did nothing (the browser's own hit test landed on the hint). The hints are now click-through and the card paints above them (`components/today/action-card.tsx`).
- Step descriptions kept the explore run's values ("Set quantity to 24" on a 28-carton run). They are now templated like values and rendered per run (skills compiled from now on; the dev skills in `var/` predate it).
Open for H5: the run theater's address bar shows the first step's path, not the current page; reorder has no undo (no cancel-order task).
Laptop must: `git pull`, `uv sync --all-packages`.

## Sun 15 Nov 2026 · review of the PC session (merges, H1-H3), branch pc/h3-review
Fixed:
- **Secret leak to the model:** the ARIA snapshot shows typed field values, so the vault-held username reached explore/heal prompts. Every prompt now goes through `vault.redact`; a test proves the value never appears.
- A model error (API, timeout, daily budget) ended a run without `run.finished`. It now ends that attempt cleanly; model calls in the loop time out after 30 s; any crash in a run still emits `run.finished` (status failed).
- New `RUN_MAX_USD` (0.25): a healing run stops and asks a human beyond it. Runs of the same task are serialised, so two runs cannot store the same version.
- CI now installs Chromium, so the 31 browser and agent tests run there instead of skipping.
Checked and fine: H1 loader (idempotent), H2 executor/vault/allowlist, the H3 compiler, store and postconditions.
`pnpm check`: 359 passed. Live: cold $0.0028, seed-7 heal $0.0039, warm 1.5 s / 0 calls.
Laptop must: `git pull`. New optional env var `RUN_MAX_USD`.

## Sun 15 Nov 2026 · H3 explore, compile, replay, heal (M2 gate)
Done:
- `agents/` (explore loop, runner, task specs, postconditions, recorder, portal admin client, CLI, bench adapter), `skills/` (compiler, diff, file store), `replay/engine.py` (heal ladder: fallback → healer (Haiku) → escalation (Sonnet) → ask_human).
- **Contract change (PC-owned, both sides updated):** `Step.optional: bool = false` in `skills/schema.py` and `apps/web/src/lib/contracts.ts`; fixtures regenerated (the seed-7 cookie step is optional). CONTRACTS §4 documents it. Existing skills and fixtures stay valid (the field has a default).
- Gate evidence (`bench/results/m2_gate.txt`, real Chromium + portals + OpenRouter): cold explore at seed 0 ok (13 calls, $0.0029, 19 s); warm replay 1.3 s, 0 calls; seed 7 heal → v2 with diff ($0.0037, 36 s); warm at seed 7 1.4 s, 0 calls; seed 13 → v3 (rung 1, $0); switching back to 7, 0, 13: 0 calls each. Every success is proved from `/_admin/state`, with a baseline so an old order cannot count.
- TillDesk `change_price`: cold 8 steps $0.0025; the skill goes to `/tilldesk/menu/{{item_id}}/edit`, so it works for any item (cappuccino €3.80 replayed in 1.0 s, 0 calls); healed at seed 7.
- Bench: `--runner backroom_api.agents.bench_runner:factory` is the real B1/B2 runner.
- `pnpm check` green: 355 passed. DECISIONS 17–21.
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`. The web `Step` type has `optional` now (a Skills-page badge for optional steps would be nice; not required).
Not done: `grainline.download_invoice` has no task spec yet (its success needs a download check, which the postcondition kinds don't cover).

## Sun 15 Nov 2026 · H2 browser agent core
Done (`services/api/backroom_api/browser/`):
- `BrowserPool`: one Chromium, a fresh isolated context per run, `max_contexts` semaphore (2), allowlist enforced on every request.
- `Allowlist` (origin + path prefix), `SecretVault` (`{{secret:key}}`, TOTP, `redact`), `observe()` (AI-mode ARIA snapshot with refs; waits for `[aria-busy]` to clear), `Executor` (all nine step actions, locator order target → fallbacks, `expect` checks, typed `error_kind`s for the heal ladder, `resolved_via` for rung 1), `Screencast` (CDP JPEG frames).
- Tests: 19 (`test_browser_unit.py`, `test_browser.py`; the latter run real Chromium and skip when it is not installed). `pnpm check` green: 337 passed.
- Real-portal smoke: Grainline login with password + TOTP through the vault works. It found one bug the fixture could not: refs after a navigation are `f1e4`, not `e4` (fixed, regression test added).
Laptop must: `git pull`, `uv sync --all-packages`. The API `Settings` gained the portal credentials and `DATA_SEED` (same `.env` variables the portals read). No contract changes.
Notes for H3: a bare `paragraph` has no accessible name, so the explore loop can only target named elements; a blocked navigation shows up as `error_kind="blocked"`.

## Sun 15 Nov 2026 · merge of laptop/l9-run-theater, l11-bench, l12-deploy + H1
Done:
- Merged the three branches (PRs #11, #13, #14 content) into `main`; conflicts only in DECISIONS, laptop.md (kept both) and graphify-out (kept ours; regenerate after the next big task).
- `pnpm check` green: 301 passed, 17 skipped. One Windows-only fix: the TOTP CLI test now passes `SYSTEMROOT`.
- H1: `pnpm seed` now builds `data/out` and runs `backroom_api.seed_db` (migrations once each via `schema_migrations`, then `write_world`). Verified on Docker Postgres: 55 entities, 86 facts, 9 episodes; a second run creates 0 facts; `/health` is ok.
- Parquet tables are read by DuckDB straight from `data/out` (detectors); they are not copied into Postgres.
Laptop must: `git pull`, `uv sync --all-packages`, `pnpm install`.
Contract changes: none. DECISIONS keep the `L-n` ids (ADR-16).

---

## Thu 12 Nov 2026 · two-machine mode starts
Done: M0 finished and pushed. `pnpm dev:lite` added (api + portals + web, no Docker, no database). `/health` now answers in about 1.3 s even when Postgres is down.
Laptop must: follow HANDOVER §2b, then start with task L0 (contracts) from §9.
