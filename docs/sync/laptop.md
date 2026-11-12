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
