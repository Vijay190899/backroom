# Sync log: PC → laptop

Only the **PC** edits this file. Newest entry first. Tell the laptop what changed under it: contracts, new env vars, merged branches, gate results.

Entry format:

```
## <date time> · H<id> / merge of laptop/<id>
Done: what works now.
Laptop must: pull, then run these commands (`uv sync --all-packages`, `pnpm install`, ...).
Contract changes: anything the laptop's code must adapt to.
```

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
