# Sync log: laptop → PC

Only the **laptop** edits this file (the PC never does, so it cannot conflict). Newest entry first. One entry per finished task or branch.

Entry format:

```
## <date time> · L<id> · branch laptop/<id>-<slug>
Done: what works now.
Verify: the exact commands to check it (and what you should see).
Needs from PC: anything the PC must do to integrate (new dependency, migration, env var).
Notes: surprises, shortcuts, things left undone.
```

---

## Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)
Done:
- `backroom_api/analytics/detectors.py`: stock-out, margin erosion and weather demand as DuckDB SQL over the L4 Parquet files. Each emits contract `Candidate`s with every quotable number and inline SQL evidence. `run_all(max_price_increase_pct=…)` re-proposes within an owner's cap.
- `backroom_api/analytics/pricing.py`: deterministic prices, rounded half-up.
- On today's real data:
  - Franzbrötchen: butter +16.1%, €0.55 → €0.64; cost €0.93 → €1.02; margin 71% → 68% (target 70%); proposes €3.20 → €3.60 (+12.5%, margin 72%). With an 8% cap: €3.45, +7.8%, 70%.
  - Oat milk: 2.0 days left; 28 cartons, €44.52.
  - Rainy Saturday: 9 mm forecast, −14%, trim one of three 4-hour shifts, €58.
- Shared fixtures regenerated to match (driver_* keys, 28 cartons).
Verify:
- `uv run python -c "from backroom_api.analytics.detectors import run_all; [print(c.kind, c.impact_eur_weekly) for c in run_all()]"` (needs `uv run backroom-data all` first).
- `uv run pytest services/api/tests/test_detectors.py`: 14 tests. `pnpm check`: 232 pass.
Needs from PC:
- `uv sync --all-packages` (duckdb in backroom-api).
- The reorder is 28 cartons / €44.52 now (L-43); demo lines that say 24 / €38.16 need updating.
Notes:
- Deviations are logged as L-43…L-49.
- The audit found no blockers and 11 issues worth fixing; all are fixed. For L7: the number guard must check that units agree (CONTRACTS §6 rule 6).

## Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)
Done:
- `uv run backroom-data all` (`pnpm seed`'s data step) builds `data/out/`:
  - Parquet tables: sales, weather, holidays, menu, recipes, unit_costs, supplier_prices, grainline_orders, inventory, staff, rota;
  - `preferences.json` (Tue/Fri ordering and the 70% margin target; no price cap) and `manifest.json` (sources, row counts, honest notes).
- Sources: Maven Coffee Shop Sales (Hell's Kitchen store, mapped onto the TillDesk menu), Open-Meteo archive + forecast for Bonn, Nager.Date DE-NW. Downloads are cached in `data/raw/`; every one has a fallback (synthetic sales and weather, computed holidays).
- Story numbers come out of the data:
  - Franzbrötchen unit cost €0.93 → €1.02 (butter €0.55 at €7.10/kg);
  - oat milk exactly 2.0 days left;
  - rainy Saturdays −13.9% against nearby dry ones;
  - next Saturday 9 mm (`demo_override`);
  - three 14:00–18:00 shifts on Saturday.
Verify:
- `uv run backroom-data all` (≈4 s), then run it again: every file in `data/out/` is byte-identical.
- `uv run pytest data/tests`: 18 tests on tiny fixtures, offline.
- `pnpm check`: 218 pass.
Needs from PC:
- `uv sync --all-packages` (new deps: duckdb, pyyaml; data depends on portals).
- H1 loads the tables into Postgres (column types in `cli.SCHEMAS`; CONTRACTS §10).
- Rebuild the data on demo day, or pin `PORTALS_TODAY`, so data and portal agree.
Notes:
- Deviations are logged as L-32…L-42 in `docs/DECISIONS.md`. The Grainline usual oat order is now 10 cartons (L-37).
- The audit found 1 blocker (hard-coded "Maven/Open-Meteo" notes in fallback builds) and 8 issues worth fixing; all are fixed and tested.

## Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)
Done:
- The TillDesk portal at `/tilldesk`: login (username + password, no TOTP), menu list (8 items), edit price (a draft), and "Publish menu".
- Chaos applies through the shared macros, with cards on the menu list.
- Admin `GET /_admin/state/tilldesk` returns `TillDeskState`, with `items` keyed by id; `/_admin/reset` restores the menu.
- Undo is saving the old price and publishing again.
Verify:
- `uv run pytest services/portals/tests/test_tilldesk.py`. All of `pnpm check` passes: 200 tests.
- By hand: `pnpm dev:lite`, open http://localhost:8001/tilldesk/login, sign in as `$TILLDESK_USER` / `$TILLDESK_PASSWORD`.
Needs from PC:
- `tilldesk.change_price`: the postcondition is `items.<item_id>.published_price_eur`.
- Edit links are named "<Edit label> <item name>". Either target that, or `goto /tilldesk/menu/{{item_id}}/edit` (CONTRACTS §4).
- Use exact name matching in the runner (CONTRACTS §3 rule 5).
Notes:
- Deviations are logged as L-26…L-31 in `docs/DECISIONS.md`. Localboard (P1) is not built (L-26).
- The audit found 1 blocker (Publish was hidden when nothing had changed) and 4 issues worth fixing; all are fixed and tested.

## Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)
Done:
- The chaos engine, with 9 families (language, nav position, section order, wrapper depth, id/class salt, interstitials, delayed render, button↔link, table↔cards), rendered through `templates/macros.html` and the `Look` object in `rendering.py`.
- `GET /_admin/chaos` and `POST /_admin/chaos {portal, seed}` → `ChaosState`; `/_admin/reset` sets every seed back to 0.
- Seed 0 is canonical. Seed 7 gives German controls, top-bar nav and a cookie banner.
Verify:
- `uv run pytest services/portals` (146 in `pnpm check`):
  - same seed ⇒ same DOM hash across the whole reorder path;
  - seeds 0–19 ⇒ 20 distinct hashes;
  - every non-canonical variant has a DOM marker;
  - label/for/id soundness and the skill test ids hold at all 20 seeds;
  - the reorder flow works at seeds 3, 7 and 11.
- By hand: `curl -X POST localhost:8001/_admin/chaos -H "X-Admin-Token: $PORTALS_ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"portal":"grainline","seed":7}'`, then open http://localhost:8001/grainline/catalog.
Needs from PC (H2/H3), see `docs/CONTRACTS.md` §3 "Rules for the agent runner":
- a fresh browser context per run;
- wait for `[aria-busy]` to clear before each snapshot;
- open the hamburger `<details>` before clicking nav links;
- link-variant actions are role `link`.
Also: the api `POST /chaos` forwarding route is yours (L-23). Please time a real seed-7 heal early: it will touch at least 5 steps (L-24).
Notes:
- Deviations are logged as L-18…L-25 in `docs/DECISIONS.md`. L-1…L-17 (L0/L1/L10) were added on this branch too, at the user's request.
- The audit found no blockers and 8 issues worth fixing; all are fixed.

## Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts)
Done:
- The Grainline portal at `/grainline`: login + TOTP (RFC 6238, no new dependency), catalog search with pagination, cart (add, update, remove), checkout with a delivery-date choice, order page with cancel as the Undo, order history, invoices list, and invoice PDFs (hand-written, deterministic, € and umlauts via WinAnsi).
- Admin `GET /_admin/state/grainline` and `POST /_admin/reset` (`X-Admin-Token`).
- Seeded history: Tue/Fri orders over the last 28 days, `GW-10474`…`GW-10481`. Butter is €7.10 → €8.24 from day −9, oat milk €1.46 → €1.59 from day −3. The next order is `GW-10482` (24 × €1.59 = €38.16). It is pure functions in `grainline/catalog.py` (`seeded_orders`, `price_on`, `PRODUCTS` with pack sizes), so L4/L6 import the same numbers.
Verify:
- `uv run pytest services/portals` (52 pass) or `pnpm check`.
- By hand: `pnpm dev:lite`, open http://localhost:8001/grainline/login, sign in as `$GRAINLINE_USER` / `$GRAINLINE_PASSWORD`, and get the code from `uv run python -m backroom_portals.totp`.
Needs from PC:
- `pydantic-settings` added to `services/portals/pyproject.toml` (already in the lock via the api; `uv.lock` +2 lines). Re-lock on merge as usual.
- With `GRAINLINE_TOTP_SECRET` empty, the portal derives the secret from `DATA_SEED` (`backroom_portals.totp.default_secret`). The agent's vault must use the same rule, or `pnpm seed` writes a secret to `.env`.
- Contract change, proposed here (L0 not yet acknowledged): 4 Grainline labels added: `update_qty`, `remove`, `prev_page`, `next_page`.
Notes:
- A fresh login empties the cart, so a replay never inherits leftovers.
- Catalog and cart rows use `<th scope="row">` with the product name, so the agent can scope "Quantity" and "Add to cart" to a row when the page lists several products.
- The audit (2 blockers, 7 should-fix) is addressed. Left for L2: chaos rendering (nav position, wrappers, interstitials, button/link, table/cards). L2 will move the templates onto shared macros first.

## Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts
Done: contracts for every shared shape, in `docs/CONTRACTS.md` plus code. Portal routes, labels (EN / EN-alt / DE), test ids, admin API, SKUs and secret keys are in `backroom_portals/contract.py`. The chaos catalog (9 families; seed 0 canonical; seed 7 pinned to DE + top-bar nav + cookie banner) is `backroom_portals/chaos.py`. The skill schema is `backroom_api/skills/schema.py`. Run events (SSE), WS frames and golden-run frames are `backroom_api/contracts/events.py`; API bodies are `contracts/api.py`; the detector `Candidate` is `contracts/candidate.py`. The memory migration is `services/api/migrations/0001_memory.sql`, bitemporal with `invalidated_at`. The zod mirror is `apps/web/src/lib/contracts.ts`. Six shared fixtures in `apps/web/src/fixtures/` are generated from the pydantic models by `services/api/scripts/gen_fixtures.py`.
Verify: `pnpm check` (66 pytest pass, including fixtures parsed with pydantic; `pnpm -C apps/web contracts` parses the same fixtures with zod and checks rejections).
Needs from PC:
- Acknowledge L0 in `docs/sync/pc.md`.
- The migration runner (H1) should pick up `services/api/migrations/*.sql` in name order. The SQL is not yet run against a real Postgres, only reviewed; please apply it once on Docker Postgres in H1 and tell me if anything fails.
- Add `services/api/backroom_api/contracts/` and `services/api/migrations/` to the "shared, change only through L0" row of the HANDOVER ownership table.
- Decisions for the PC's side, which you may change via the contract process:
  - one new skill version per run, stored only on success;
  - `StepChange` insert and delete ops, for dismiss steps;
  - `POST /runs/{id}/undo` and `POST /runs/{id}/human`;
  - `ContextPack` on `RunSummary`.
Notes, files outside the laptop's ownership (all small, needed to wire the contract check):
- `.github/workflows/ci.yml`: one step after typecheck, `pnpm -C apps/web contracts` (the laptop's gh token now has the `workflow` scope);
- the root `package.json` `check:web` runs that step too;
- an `apps/web/package.json` `contracts` script;
- `apps/web/tsconfig.json` gains `allowImportingTsExtensions`, so node can run the check without a build step.
Notes, other:
- Fixtures are illustrative. On a real seed-7 run every German label heals, which is more steps than the fixture shows.
- An independent audit pass was run, and its findings are fixed.

## Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe
Done: `pnpm probe:llm` on OpenRouter (worker anthropic/claude-haiku-5.5, SDK 2.8.0): all 6 checks pass (basic, effort, strict_tools, structured_outputs, prompt_cache, streaming). Total $0.0020. `LLM_CAPS_OFF` stays empty; no DECISIONS entry needed. Closes the last M0 gate item.
Verify: `cat bench/results/provider_probe.json` (every check `"ok": true`), or rerun `pnpm probe:llm` with the key in `.env`.
Needs from PC: merge only; adds `bench/results/provider_probe.json` (PC-owned path, written as L10 specifies). Update HANDOVER §1 to mark the M0 gate closed.
Notes: laptop setup per §2b done; `pnpm check` green on macOS (20 passed).
