# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 142 files · ~77,075 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 9, .example 1, .ico 1)

## Summary
- 2061 nodes · 4892 edges · 90 communities (74 shown, 16 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 390 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0068547f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- grainline/routes.py
- M0 Foundations (Wed 22:00-23:00)
- M2 Browser agent (Thu 09:00-14:00, riskiest)
- gen_fixtures.py
- action-card.tsx
- Backroom Product Requirements Document
- grainline/routes.py
- Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)
- test_grainline.py
- contracts.ts
- detectors.py
- test_brief.py
- memory_bench.py
- Contract
- Candidate
- LLM
- steps
- test_memory.py
- Settings
- recipes.yaml
- Backroom Product Requirements Document
- test_tilldesk.py
- FastAPI api service (orchestrator, agents, memory, SSE/WS)
- pipeline.py
- guard.py
- page
- backroom_bench/cli.py
- test_contracts.py
- browser.py
- project.yml
- PlaceholderPage
- json
- contract.py
- web/package.json
- sources.py
- Rules
- Sync log: laptop → PC
- scripts
- gen_fixtures.py
- components.json
- backroom_data/cli.py
- tilldesk/routes.py
- to_sse
- dependencies
- compilerOptions
- Decision Log (ADRs)
- parse_maven
- world.py
- shifts
- test_contract.py
- typing
- Handover — read this first on a new machine or in a new session
- RunEvent
- .mcp.json
- schema.py
- contracts.check.mts
- app-shell.tsx
- preferences
- extractor.py
- TillDeskStore
- api-status.tsx
- README - Backroom overview
- layout.tsx
- sales.py
- Skill
- api
- caddy
- Demo Script - 5 minutes
- portals
- postgres
- fact
- scripts
- theme-toggle.tsx
- Contracts (L0)
- services
- rules
- depends_on
- healthcheck
- Clock
- Sync log: PC → laptop
- AGENTS.md
- backroom-api
- backroom-data
- pnpm-workspace.yaml
- backroom

## God Nodes (most connected - your core abstractions)
1. `Candidate` - 58 edges
2. `Contract` - 52 edges
3. `LLM` - 30 edges
4. `build()` - 30 edges
5. `Settings` - 28 edges
6. `Backroom Product Requirements Document` - 27 edges
7. `generate()` - 26 edges
8. `FakePlanner` - 25 edges
9. `FakeVerifier` - 25 edges
10. `login()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)` --references--> `Look`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/rendering.py
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `3. Chaos catalog` --references--> `Look`  [INFERRED]
  docs/CONTRACTS.md → services/portals/backroom_portals/rendering.py
- `System overview (Vercel web + Lightsail compose)` --semantically_similar_to--> `README architecture flowchart`  [INFERRED] [semantically similar]
  docs/ARCHITECTURE.md → README.md

## Import Cycles
- 2-file cycle: `services/portals/backroom_portals/config.py -> services/portals/backroom_portals/totp.py -> services/portals/backroom_portals/config.py`

## Hyperedges (group relationships)
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — docs_prd_detectors, docs_prd_candidate, docs_prd_planner, docs_prd_verifier, docs_prd_number_guard, docs_architecture_route_brief_today [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — docs_prd_explore_mode, docs_prd_skill_compiler, docs_prd_replay_engine, docs_prd_heal_ladder, docs_prd_skill_versioning, docs_architecture_escalation_ladder [EXTRACTED 1.00]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — docs_prd_franzbroetchen_story, docs_architecture_route_reject, docs_prd_episodes, docs_prd_extractor, docs_prd_preference_fact, docs_prd_verifier, demo_beat_learn_owner [INFERRED 0.85]

## Communities (90 total, 16 thin omitted)

### Community 0 - "grainline/routes.py"
Cohesion: 0.10
Nodes (42): Rule: LLMs never originate numbers, Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, 'As of' query predicate, Memory SQL schema sketch, backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/analytics (DuckDB queries, detectors) (+34 more)

### Community 2 - "M0 Foundations (Wed 22:00-23:00)"
Cohesion: 0.10
Nodes (34): Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: one real LLM call (stop_reason, $, cache_read > 0), Check: pytest + ruff + pyright for Python logic, Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Stack and commands, Verification rules (verify before next step, state evidence), Verify every change (cheapest sufficient check) (+26 more)

### Community 3 - "M2 Browser agent (Thu 09:00-14:00, riskiest)"
Cohesion: 0.11
Nodes (37): Rule: secrets never reach prompts or logs, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Q: Cost at scale, Q: Why not browser-use / Stagehand, Chaos variant families (labels EN/DE, DOM order, interstitials, delays, moved nav), backroom_api/skills (compiler, replay, healer, registry), Route /skills (+29 more)

### Community 4 - "gen_fixtures.py"
Cohesion: 0.09
Nodes (43): Rule: fictional names only; no Super44 branding in UI, Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Portal patterns (login->TOTP->dashboard, cart, checkout, PDF invoices), GET /brief/today, M1 Data + Portals (Wed 23:00-01:30), TillDesk may slip to Thu 08:00 (+35 more)

### Community 5 - "action-card.tsx"
Cohesion: 0.12
Nodes (35): claude-api skill (load before Anthropic SDK code), Non-negotiables, Rule: all LLM access through llm/registry.py, Beat 4:40 Close - /about, model table, adapters, API rules for current models (adaptive thinking, no sampling params, no forced tool_choice, check stop_reason, stream), Canonical model IDs mapped per provider (slash IDs pass through), Capability flags registry.CAPS[provider] (effort, strict_tools, prompt_cache, ...), Capability probe (one cheap Haiku call per feature -> provider_probe.json) (+27 more)

### Community 6 - "Backroom Product Requirements Document"
Cohesion: 0.11
Nodes (32): Rule: every LLM call through cost meter + budget guard, Beat 4:00 Proof - /bench, Cost meter (per-call provider/role/model/tokens/$), backroom_api/llm (model registry, client, cost meter, budget guard), backroom_api/replay (golden-run recorder & player), Ops guards (budget cap, rate limit, DEMO_ACCESS_CODE, CORS), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json) (+24 more)

### Community 7 - "grainline/routes.py"
Cohesion: 0.08
Nodes (36): get_settings(), Settings, Order, OrderLine, _document(), _eur(), invoice_pdf(), _text() (+28 more)

### Community 8 - "Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)"
Cohesion: 0.13
Nodes (21): Check: Lighthouse via web-perf skill, dataviz skill (before any chart), Frontend quality bar, apps/web/src/styles/tokens.css, ui-ux-pro-max skill, web-perf skill (Lighthouse), Charts (Recharts or visx, dataviz skill), Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query) (+13 more)

### Community 9 - "test_grainline.py"
Cohesion: 0.06
Nodes (54): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), code_at(), default_secret(), now_code(), verify(), catalog_html(), dom_hash(), forced() (+46 more)

### Community 10 - "contracts.ts"
Cohesion: 0.03
Nodes (66): ActionCard, actionCardSchema, approveResponseSchema, Brief, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema (+58 more)

### Community 11 - "detectors.py"
Cohesion: 0.07
Nodes (31): connect(), Context, _ingredient(), margin_erosion(), _n(), run_all(), _shown(), stockout() (+23 more)

### Community 12 - "test_brief.py"
Cohesion: 0.16
Nodes (28): brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier, _Message, _Result (+20 more)

### Community 13 - "memory_bench.py"
Cohesion: 0.08
Nodes (15): FakeAnswerer, Answer, Answerer, b3(), connect(), ContextArm, correct(), ground_truth() (+7 more)

### Community 14 - "Contract"
Cohesion: 0.12
Nodes (21): 7. API shapes, 8. Memory, ApiError, ApproveResponse, ChaosRequest, ChaosState, ContextPack, ErrorResponse (+13 more)

### Community 15 - "Candidate"
Cohesion: 0.11
Nodes (23): BriefLLMError, candidate_view(), CardCopy, Draft, LLMPlanner, LLMVerifier, _Model, _parse() (+15 more)

### Community 16 - "LLM"
Cohesion: 0.06
Nodes (30): main(), Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs() (+22 more)

### Community 17 - "steps"
Cohesion: 0.07
Nodes (33): concurrency, cancel-in-progress, group, name, runs-on, steps, jobs, docs (+25 more)

### Community 18 - "test_memory.py"
Cohesion: 0.05
Nodes (49): Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), EpisodeRef, FactDetail, GraphFact, estimate_tokens(), pack(), seeds_for(), _triple() (+41 more)

### Community 19 - "Settings"
Cohesion: 0.05
Nodes (32): get_settings(), Settings, make_pool(), ping(), build_async_client(), canonical_model_id(), cost_usd(), is_configured() (+24 more)

### Community 20 - "recipes.yaml"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 21 - "Backroom Product Requirements Document"
Cohesion: 0.09
Nodes (33): Q: What breaks first in production, CDP Page.startScreencast live frames, Key API routes, Langfuse Cloud Hobby traces (P1), backroom_api/routes (brief, actions, runs, memory, bench, health), Route /runs/[id] Run theater, POST /actions/{id}/approve (Idempotency-Key), POST /ask (SSE, P1) (+25 more)

### Community 22 - "test_tilldesk.py"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 23 - "FastAPI api service (orchestrator, agents, memory, SSE/WS)"
Cohesion: 0.12
Nodes (32): Check: DOM-hash test per chaos seed, Backend choices table, Browser pool (1 Chromium, 2 contexts, queue), Caddy (TLS + routing, sslip.io auto-HTTPS), Chaos engine (seeded RNG variant catalog), Backroom Technical Architecture, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), DuckDB / Parquet (sales analytics) (+24 more)

### Community 24 - "pipeline.py"
Cohesion: 0.09
Nodes (26): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), Planner, Verifier, action_id(), brief_for_today(), BriefResult, Decision (+18 more)

### Community 25 - "guard.py"
Cohesion: 0.12
Nodes (17): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), copy_for() (+9 more)

### Community 26 - "page"
Cohesion: 0.15
Nodes (4): ChaosSeeds, label(), Look, page()

### Community 27 - "backroom_bench/cli.py"
Cohesion: 0.09
Nodes (10): _briefs(), _load(), _run(), summarize(), verify(), git_sha(), models(), with_fee() (+2 more)

### Community 28 - "test_contracts.py"
Cohesion: 0.14
Nodes (16): Step, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step(), test_margin_card_numbers_match_the_demo_story(), test_naive_datetimes_are_rejected() (+8 more)

### Community 29 - "browser.py"
Cohesion: 0.12
Nodes (11): b1(), b2(), RunOutcome, summarize(), TaskRunner, FakeRunner, percentile(), rate() (+3 more)

### Community 30 - "project.yml"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 31 - "PlaceholderPage"
Cohesion: 0.16
Nodes (16): nextConfig, next@16.4.6, AboutPage(), metadata, BenchPage(), metadata, MemoryPage(), metadata (+8 more)

### Community 32 - "json"
Cohesion: 0.10
Nodes (19): build(), next_saturday(), _notes(), read(), write(), built(), cached_weather(), maven_zip() (+11 more)

### Community 33 - "contract.py"
Cohesion: 0.18
Nodes (10): chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosRequest, ChaosState (+2 more)

### Community 34 - "web/package.json"
Cohesion: 0.12
Nodes (22): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3, @types/node@^20, @types/react@^19 (+14 more)

### Community 35 - "sources.py"
Cohesion: 0.14
Nodes (10): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+2 more)

### Community 36 - "Rules"
Cohesion: 0.21
Nodes (4): rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 37 - "Sync log: laptop → PC"
Cohesion: 0.29
Nodes (6): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)

### Community 38 - "scripts"
Cohesion: 0.09
Nodes (22): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, scripts, bench (+14 more)

### Community 39 - "gen_fixtures.py"
Cohesion: 0.14
Nodes (18): AskHuman, CostTick, Cursor, _Event, FrameMeta, GoldenFrame, HealAttempt, HealFailed (+10 more)

### Community 40 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 43 - "tilldesk/routes.py"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 45 - "dependencies"
Cohesion: 0.12
Nodes (18): dependencies, @base-ui/react@^1.9.0, class-variance-authority@^0.7.1, cn@^0.5.2, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0, shadcn@^4.23.0 (+10 more)

### Community 46 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+11 more)

### Community 47 - "Decision Log (ADRs)"
Cohesion: 0.16
Nodes (20): CLAUDE.md - Backroom agent guide, context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path), Read order (BUILD_PLAN -> GRAPH_REPORT -> PRD/ARCH sections), Rule: mock portals only; no bot-protection evasion, serena MCP (symbol navigation and edits) (+12 more)

### Community 48 - "parse_maven"
Cohesion: 0.19
Nodes (4): _column(), rows(), test_xlsx_reader_streams_rows_with_shared_strings(), tiny_xlsx()

### Community 49 - "world.py"
Cohesion: 0.18
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 50 - "shifts"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 51 - "test_contract.py"
Cohesion: 0.16
Nodes (9): pick_variants(), Label, test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 52 - "typing"
Cohesion: 0.08
Nodes (11): Caps, caps_for(), Price, next_weekday(), price_on(), PriceEvent, Product, seeded_orders() (+3 more)

### Community 53 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.11
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 55 - ".mcp.json"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 56 - "schema.py"
Cohesion: 0.21
Nodes (8): CssFallback, Expect, LabelFallback, Locator, Postcondition, SkillStats, TextFallback, reorder_steps()

### Community 57 - "contracts.check.mts"
Cohesion: 0.15
Nodes (10): zod@^4.6.7, briefSchema, brief, fixtures, negatives, memoryGraphSchema, runEventSchema, skillSummarySchema (+2 more)

### Community 58 - "app-shell.tsx"
Cohesion: 0.32
Nodes (9): ApiStatus(), AppShell(), isActive(), NAV_ITEMS, NavItem, SidebarLinks(), TabBarLinks(), BusinessBadge() (+1 more)

### Community 59 - "preferences"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 60 - "extractor.py"
Cohesion: 0.21
Nodes (6): ActionCard, checked(), extract(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 61 - "TillDeskStore"
Cohesion: 0.18
Nodes (5): Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), MenuItem, TillDeskState, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 62 - "api-status.tsx"
Cohesion: 0.18
Nodes (9): @tanstack/react-query@^5.107.1, Status, Tone, TONE_DOT, API_URL, fetchHealth(), Health, healthSchema (+1 more)

### Community 63 - "README - Backroom overview"
Cohesion: 0.17
Nodes (12): Add Live demo + Benchmarks badges to README, Backroom: agentic back office for a cafe (engine under 'Approve all'), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration, JD problem 4: agentic self-improvement, Why this exists: Super44 JD hard problems (+4 more)

### Community 65 - "layout.tsx"
Cohesion: 0.22
Nodes (8): geistMono, geistSans, instrumentSerif, metadata, RootLayout(), viewport, Providers(), themeInitScript

### Community 66 - "sales.py"
Cohesion: 0.13
Nodes (13): _maven_sales(), apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days() (+5 more)

### Community 69 - "api"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 70 - "caddy"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 71 - "Demo Script - 5 minutes"
Cohesion: 0.25
Nodes (9): Shared Action interface to the planner, Adapter strategy: API-first, browser skills for long tail, M3 gate (full DEMO_SCRIPT works locally end-to-end), Rehearse demo script 3x on deployed URL, Demo Script - 5 minutes, Audience: Super44 founders (Founding Engineer interview), Interviewer (demo user), Success criteria for the interview (+1 more)

### Community 72 - "portals"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 73 - "postgres"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 74 - "fact"
Cohesion: 0.42
Nodes (8): entity, episode, episode_kind_idx, fact, fact_episode_idx, fact_object_idx, fact_open_idx, fact_subject_predicate_idx

### Community 75 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, contracts, dev, e2e, lint, start, typecheck

### Community 76 - "theme-toggle.tsx"
Cohesion: 0.46
Nodes (6): ThemeToggle(), isDark(), listeners, setDark(), subscribeTheme(), THEME_STORAGE_KEY

### Community 77 - "Contracts (L0)"
Cohesion: 0.22
Nodes (8): 1. Changing a contract, 2. Portals, 3. Chaos catalog, 4. Skills, 9. Fixtures and the drift check, Contracts (L0), testid(), test_testids()

### Community 78 - "services"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 79 - "rules"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 80 - "depends_on"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 81 - "healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

## Ambiguous Edges - Review These
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay (golden runs, DEMO_MODE=replay)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Scripted event: oat milk +9% day -3` → `Card: Reorder oat milk (stock-out, Grainline)`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `README badges (CI, license, stack)` → `Design tokens (crema/roasted caramel palette; tokens.css)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **26 isolated node(s):** `backroom`, `python`, `uvx`, `@playwright/mcp`, `start-mcp-server` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 639 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Contracts (L0)` connect `Contracts (L0)` to `Contract`, `Candidate`, `world.py`, `Handover — read this first on a new machine or in a new session`, `RunEvent`, `pipeline.py`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `9.1 Laptop tasks (light)`) actually correct?**
  _`Candidate` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backroom`, `python`, `uvx` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `grainline/routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09872241579558652 - nodes in this community are weakly interconnected._
- **Why does `5. Run events` connect `RunEvent` to `Contracts (L0)`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay (golden runs, DEMO_MODE=replay)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Scripted event: oat milk +9% day -3` and `Card: Reorder oat milk (stock-out, Grainline)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._