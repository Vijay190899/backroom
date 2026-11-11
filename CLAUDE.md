# Backroom — agent guide

Agentic back office for a café: brief → approve → a browser agent acts in mock merchant portals, with self-healing skills, temporal memory and benchmarks. Interview demo; **code freeze Fri 13 Nov 11:30**.

## Read order (stop when you have enough)
1. `docs/BUILD_PLAN.md`: find the current milestone and its gate.
2. `graphify-out/GRAPH_REPORT.md`: map of docs and code (if present).
3. Only the PRD/ARCHITECTURE sections the task touches. Don't read whole docs by default.

## Token discipline (graph memory)
- **Navigate before reading.** Use the `graphify` MCP (`query_graph`, `get_neighbors`, `shortest_path`) to find concepts, and the `serena` MCP (`find_symbol`, `find_referencing_symbols`, `get_symbols_overview`) to find code. Read whole files only when editing them.
- Prefer Serena's symbol-level edits for surgical changes in large files.
- After each milestone gate, refresh the graph: `/graphify . --update` (the code-only post-commit hook does AST updates automatically).
- Use `context7` for library docs instead of guessing APIs. **Before writing any Anthropic SDK code, load the `claude-api` skill.**

## Stack and commands
- Python 3.12 + uv (`services/api`, `services/portals`, `data`, `bench`); FastAPI, Pydantic v2, psycopg 3, DuckDB, Playwright.
- Next.js + TS strict + pnpm (`apps/web`); Tailwind v4, shadcn/ui, Motion, TanStack Query.
- Infra: `infra/docker-compose.yml` (postgres+pgvector, api, portals, caddy).
- Checks before every commit: `uv run ruff check . && uv run pyright && uv run pytest -q` and `pnpm -C apps/web lint && pnpm -C apps/web typecheck`.

## Non-negotiables
- **Models only via `services/api/backroom_api/llm/registry.py`**, configured by env (`LLM_*_MODEL`, `LLM_*_EFFORT`). Defaults: worker/verifier/healer `claude-haiku-5-5`, planner/escalation `claude-sonnet-5-5`. No hard-coded model IDs elsewhere. Docs: `docs/ARCHITECTURE.md` §5.
- Current API rules: adaptive thinking (no `budget_tokens`); no `temperature`/`top_p`/`top_k`; no forced `tool_choice` (use `auto` + `strict: true`); always check `stop_reason`; stream long calls; cache stable prefixes.
- **LLMs never originate numbers.** Detectors compute; the number guard verifies copy.
- Secrets never reach prompts or logs (`fill_secret` / `{{secret:key}}`).
- Every LLM call goes through the cost meter + daily budget guard.
- Mock portals only; no bot-protection evasion.
- Fictional names only (Hafer & Bohne, Grainline, TillDesk, Localboard). Never use Super44 branding in the product UI.

## Frontend quality bar
- Load the `ui-ux-pro-max` skill for UI work and `dataviz` before any chart. Tokens live in `apps/web/src/styles/tokens.css` (starting palette: PRD §7).
- Verify visually with the Playwright MCP at 390 px and 1440 px, light and dark, before calling UI done. Check console errors with the Chrome DevTools MCP.
- Lighthouse ≥ 90 (perf/a11y/best-practices) on `/` and `/bench`; honour `prefers-reduced-motion`.

## Git
- Small commits at each gate: `feat(m2): heal ladder + skill diff`.
- **Do not add `Co-Authored-By` trailers or any AI attribution to commits or PRs.**
- Log deviations from the PRD in `docs/DECISIONS.md` (one numbered line plus why).
