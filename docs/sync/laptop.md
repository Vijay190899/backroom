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
- **PC: please add one CI step** after typecheck in `.github/workflows/ci.yml`: `run: pnpm -C apps/web contracts`. I couldn't push it: the laptop's GitHub token has no `workflow` scope;
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
