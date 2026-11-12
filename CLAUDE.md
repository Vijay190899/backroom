# Backroom — agent guide

Agentic back office for a café: brief → approve → a browser agent acts in mock merchant portals, with self-healing skills, temporal memory and benchmarks. Interview demo; **code freeze Fri 13 Nov 11:30**.

## Verify every change
**Find the most optimal way to verify your own work after doing it and make sure you verify every update before going further to next task or in the same task.**

Use the cheapest check that actually proves the change works:

| Change | Sufficient check |
|---|---|
| Python logic | targeted `uv run pytest -q path::test` + `uv run ruff check <files>` + `uv run pyright <files>` |
| API route | start the service, `curl` the route, assert status + response shape |
| Portal / chaos engine | DOM-hash test for the seed(s) touched |
| Browser agent / skills | run the task at seed 0 **and** one chaos seed; check postconditions + run metrics (steps, LLM calls, $) |
| LLM code | one real call: check `stop_reason`, tokens/$ in the cost meter, `cache_read_input_tokens > 0` on the repeat call |
| UI | Playwright MCP screenshot at 390 px and 1440 px, light + dark; zero console errors (Chrome DevTools MCP) |
| Performance | Lighthouse via the `web-perf` skill |
| Docs / config | links resolve, JSON/YAML parses |

Rules:
- Verify each step before starting the next, including steps inside one task.
- A failed check is fixed before anything else.
- When reporting done, state the evidence (command + result).
- Never call something done on an unverified change.
- Run `pnpm check` before every commit and at each milestone gate.

## Read order (stop when you have enough)
1. `docs/HANDOVER.md`: current state, setup, working agreements, open items. **Update it at every milestone gate.**
2. `docs/BUILD_PLAN.md`: find the current milestone and its gate.
3. `graphify-out/GRAPH_REPORT.md`: map of docs and code (committed).
4. Only the PRD/ARCHITECTURE sections the task touches. Don't read whole docs by default.

## Token discipline (graph memory)
- **Navigate before reading.** Use the `graphify` MCP (`query_graph`, `get_neighbors`, `shortest_path`) to find concepts, and the `serena` MCP (`find_symbol`, `find_referencing_symbols`, `get_symbols_overview`) to find code. Read whole files only when editing them.
- Prefer Serena's symbol-level edits for surgical changes in large files.
- After each milestone gate, refresh the graph: `/graphify . --update`.
- Use `context7` for library docs instead of guessing APIs. **Before writing any Anthropic SDK code, load the `claude-api` skill.**

## Stack and commands
- Python 3.12 uv workspace (root `pyproject.toml`; members `services/api`, `services/portals`, `data`, `bench`): FastAPI, Pydantic v2, psycopg 3, DuckDB, Playwright.
- Next.js + TS strict + pnpm (`apps/web`): Tailwind v4, shadcn/ui, Motion, TanStack Query.
- Root scripts (the only entry points): `pnpm check` · `pnpm seed` · `pnpm bench` · `pnpm probe:llm` · `pnpm dev` · `pnpm dev:lite` · `pnpm e2e`. See ARCHITECTURE §2.
- **Two machines:** a light laptop (no Docker, no Chromium) and the main PC. Which tasks belong to which, the ownership table and the merge rules are in `docs/HANDOVER.md` §9. On the laptop, run `pnpm dev:lite`, never `pnpm dev`, and never start a browser agent.
- Infra: `infra/docker-compose.yml` (postgres+pgvector, api, portals, caddy). Locally only Postgres runs in Docker.

## Non-negotiables
- **All LLM access goes through `services/api/backroom_api/llm/registry.py`.** It builds the `anthropic` SDK client for `LLM_PROVIDER` (`openrouter` default: `base_url=https://openrouter.ai/api` + `auth_token`; or `anthropic`), maps canonical model IDs per provider, and exposes capability flags. Never construct clients or write model IDs anywhere else. Docs: ARCHITECTURE §5.
- Model roles come from env (`LLM_*_MODEL`, `LLM_*_EFFORT`). Defaults: worker/verifier/healer `claude-haiku-5-5`, planner/escalation `claude-sonnet-5-5`.
- Current API rules: adaptive thinking (no `budget_tokens`); no `temperature`/`top_p`/`top_k`; no forced `tool_choice` (use `auto` + `strict: true`); always check `stop_reason`; stream long calls; cache stable prefixes; gate beta features on capability flags.
- **LLMs never originate numbers.** Detectors compute; the number guard verifies copy.
- Secrets never reach prompts or logs (`fill_secret` / `{{secret:key}}`).
- Every LLM call goes through the cost meter + daily budget guard.
- Mock portals only; no bot-protection evasion.
- Fictional names only (Hafer & Bohne, Grainline, TillDesk, Localboard). Never use Super44 branding or copy in the product UI.

## Frontend quality bar
- Load the `ui-ux-pro-max` skill for UI work and `dataviz` before any chart. Tokens live in `apps/web/src/styles/tokens.css` (starting palette: PRD §7).
- Lighthouse ≥ 90 (perf/a11y/best-practices) on `/` and `/bench`; honour `prefers-reduced-motion`.

## Git
- Small commits at each gate: `feat(m2): heal ladder + skill diff`.
- **Do not add `Co-Authored-By` trailers or any AI attribution to commits or PRs.**
- Log deviations from the PRD in `docs/DECISIONS.md` (one numbered line plus why).
