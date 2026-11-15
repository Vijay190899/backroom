# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 142 files · ~77,416 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 9, .example 1, .ico 1)

## Summary
- 2066 nodes · 4896 edges · 108 communities (90 shown, 18 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 383 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d0ee526a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- M3 Memory + Brief + UI (Thu 14:00-19:00)
- Hosting and operations
- M2 Browser agent (Thu 09:00-14:00, riskiest)
- gen_fixtures.py
- action-card.tsx
- Hosting and operations
- with
- Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)
- test_grainline.py
- steps
- project.yml
- web/package.json
- FastAPI api service (orchestrator, agents, memory, SSE/WS)
- PlaceholderPage
- scripts
- LLM
- dependencies
- test_memory.py
- registry.py
- compilerOptions
- test_llm_client.py
- Handover — read this first on a new machine or in a new session
- client.py
- Candidate
- api-status.tsx
- Number guard (every number in copy must match evidence)
- backroom_bench/cli.py
- app-shell.tsx
- Decision Log (ADRs)
- M0 Foundations (Wed 22:00-23:00)
- M4 Bench + Deploy (Thu 19:00-23:30)
- Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg)
- Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)
- Verify every change (cheapest sufficient check)
- api
- caddy
- backroom_bench/cli.py
- F1 Morning brief (Today, up to 3 action cards)
- portals
- postgres
- backroom_data/cli.py
- candidate.py
- scripts
- test_chaos_render.py
- M0 gate (pnpm check green, /health, probe:llm, shell at 390/1440)
- services
- depends_on
- writers.py
- Sync log: PC → laptop
- AGENTS.md
- laptop.md
- grainline/store.py
- pnpm-workspace.yaml
- memory/store.py
- backroom
- backroom-data
- backroom-portals
- RuntimeError
- backroom_portals/__init__.py
- extractor.py
- TillDeskStore
- api-status.tsx
- README - Backroom overview
- Settings
- layout.tsx
- sales.py
- client.py
- api
- caddy
- Demo Script - 5 minutes
- portals
- postgres
- fact
- scripts
- theme-toggle.tsx
- testid
- services
- rules
- depends_on
- healthcheck
- backroom_portals/main.py
- Clock
- Sync log: PC → laptop
- AGENTS.md
- backroom-api
- backroom-data
- pnpm-workspace.yaml
- test_llm_client.py
- backroom
- stream_today
- health.py
- totp.py
- write
- packer.py
- .create
- fakes.py
- LLMPlanner
- test_harness.py
- parquet.py
- _run
- forced

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
- `System overview (Vercel web + Lightsail compose)` --semantically_similar_to--> `README architecture flowchart`  [INFERRED] [semantically similar]
  docs/ARCHITECTURE.md → README.md
- `Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory)` --references--> `LLMPlanner`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/brief/agents.py

## Import Cycles
- 2-file cycle: `services/portals/backroom_portals/config.py -> services/portals/backroom_portals/totp.py -> services/portals/backroom_portals/config.py`

## Hyperedges (group relationships)
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — docs_prd_detectors, docs_prd_candidate, docs_prd_planner, docs_prd_verifier, docs_prd_number_guard, docs_architecture_route_brief_today [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — docs_prd_explore_mode, docs_prd_skill_compiler, docs_prd_replay_engine, docs_prd_heal_ladder, docs_prd_skill_versioning, docs_architecture_escalation_ladder [EXTRACTED 1.00]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — docs_prd_franzbroetchen_story, docs_architecture_route_reject, docs_prd_episodes, docs_prd_extractor, docs_prd_preference_fact, docs_prd_verifier, demo_beat_learn_owner [INFERRED 0.85]

## Communities (108 total, 18 thin omitted)

### Community 0 - "M3 Memory + Brief + UI (Thu 14:00-19:00)"
Cohesion: 0.10
Nodes (42): Rule: LLMs never originate numbers, Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, 'As of' query predicate, Memory SQL schema sketch, backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/analytics (DuckDB queries, detectors) (+34 more)

### Community 2 - "Hosting and operations"
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

### Community 6 - "Hosting and operations"
Cohesion: 0.11
Nodes (32): Rule: every LLM call through cost meter + budget guard, Beat 4:00 Proof - /bench, Cost meter (per-call provider/role/model/tokens/$), backroom_api/llm (model registry, client, cost meter, budget guard), backroom_api/replay (golden-run recorder & player), Ops guards (budget cap, rate limit, DEMO_ACCESS_CODE, CORS), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json) (+24 more)

### Community 7 - "with"
Cohesion: 0.10
Nodes (33): Order, OrderLine, _document(), _eur(), invoice_pdf(), _text(), _authed(), cart() (+25 more)

### Community 8 - "Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)"
Cohesion: 0.13
Nodes (21): Check: Lighthouse via web-perf skill, dataviz skill (before any chart), Frontend quality bar, apps/web/src/styles/tokens.css, ui-ux-pro-max skill, web-perf skill (Lighthouse), Charts (Recharts or visx, dataviz skill), Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query) (+13 more)

### Community 9 - "test_grainline.py"
Cohesion: 0.21
Nodes (28): has_testid(), login(), state(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove(), test_catalog_paginates() (+20 more)

### Community 10 - "steps"
Cohesion: 0.03
Nodes (66): ActionCard, actionCardSchema, approveResponseSchema, Brief, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema (+58 more)

### Community 11 - "project.yml"
Cohesion: 0.07
Nodes (30): connect(), Context, _ingredient(), margin_erosion(), _n(), run_all(), _shown(), stockout() (+22 more)

### Community 12 - "web/package.json"
Cohesion: 0.18
Nodes (26): brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier, rule(), test_a_reason_without_a_rule_records_only_the_episode() (+18 more)

### Community 13 - "FastAPI api service (orchestrator, agents, memory, SSE/WS)"
Cohesion: 0.11
Nodes (13): Answerer, b3(), connect(), ContextArm, correct(), ground_truth(), NoMemory, PackArm (+5 more)

### Community 14 - "PlaceholderPage"
Cohesion: 0.09
Nodes (19): 7. API shapes, 8. Memory, ApiError, ApproveResponse, Brief, ChaosRequest, ChaosState, ContextPack (+11 more)

### Community 15 - "scripts"
Cohesion: 0.11
Nodes (15): BriefLLMError, candidate_view(), Draft, LLMVerifier, _Model, _parse(), Plan, _system() (+7 more)

### Community 16 - "LLM"
Cohesion: 0.23
Nodes (12): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+4 more)

### Community 17 - "dependencies"
Cohesion: 0.07
Nodes (33): concurrency, cancel-in-progress, group, name, runs-on, steps, jobs, docs (+25 more)

### Community 18 - "test_memory.py"
Cohesion: 0.17
Nodes (21): at(), butter_prices(), conn(), test_back_dated_fact_is_refused(), test_concurrent_writers_leave_one_open_fact(), second(), test_context_pack_is_ranked_and_within_budget(), test_fact_detail_has_provenance_and_chain() (+13 more)

### Community 19 - "registry.py"
Cohesion: 0.10
Nodes (22): build_async_client(), canonical_model_id(), cost_usd(), LLMNotConfiguredError, Price, role_config(), RoleConfig, wire_model_id() (+14 more)

### Community 20 - "compilerOptions"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 21 - "test_llm_client.py"
Cohesion: 0.09
Nodes (33): Q: What breaks first in production, CDP Page.startScreencast live frames, Key API routes, Langfuse Cloud Hobby traces (P1), backroom_api/routes (brief, actions, runs, memory, bench, health), Route /runs/[id] Run theater, POST /actions/{id}/approve (Idempotency-Key), POST /ask (SSE, P1) (+25 more)

### Community 22 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 23 - "client.py"
Cohesion: 0.12
Nodes (32): Check: DOM-hash test per chaos seed, Backend choices table, Browser pool (1 Chromium, 2 contexts, queue), Caddy (TLS + routing, sslip.io auto-HTTPS), Chaos engine (seeded RNG variant catalog), Backroom Technical Architecture, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), DuckDB / Parquet (sales analytics) (+24 more)

### Community 24 - "Candidate"
Cohesion: 0.16
Nodes (16): CardCopy, Planner, action_id(), _copy_for(), Decision, _Drafted, _failure(), generate() (+8 more)

### Community 25 - "api-status.tsx"
Cohesion: 0.12
Nodes (15): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), protected_names() (+7 more)

### Community 26 - "Number guard (every number in copy must match evidence)"
Cohesion: 0.13
Nodes (6): 3. Chaos catalog, fact(), ChaosSeeds, label(), Look, page()

### Community 27 - "backroom_bench/cli.py"
Cohesion: 0.14
Nodes (6): _load(), main(), summarize(), verify(), main(), rate()

### Community 28 - "app-shell.tsx"
Cohesion: 0.11
Nodes (19): to_sse(), Step, StepChange, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step() (+11 more)

### Community 29 - "Decision Log (ADRs)"
Cohesion: 0.17
Nodes (7): b1(), b2(), RunOutcome, summarize(), TaskRunner, percentile(), test_percentile_and_rate()

### Community 30 - "M0 Foundations (Wed 22:00-23:00)"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 31 - "M4 Bench + Deploy (Thu 19:00-23:30)"
Cohesion: 0.16
Nodes (16): nextConfig, next@16.4.6, AboutPage(), metadata, BenchPage(), metadata, MemoryPage(), metadata (+8 more)

### Community 32 - "Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg)"
Cohesion: 0.10
Nodes (16): _column(), rows(), built(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table(), test_cached_weather_and_nager_holidays_are_used() (+8 more)

### Community 33 - "Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query)"
Cohesion: 0.18
Nodes (10): chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosRequest, ChaosState (+2 more)

### Community 34 - "Verify every change (cheapest sufficient check)"
Cohesion: 0.12
Nodes (22): eslintConfig, devDependencies, eslint@^9, eslint-config-next@16.4.6, tailwindcss@4.3.3, @tailwindcss/turbopack@4.3.3, @types/node@^20, @types/react@^19 (+14 more)

### Community 35 - "api"
Cohesion: 0.15
Nodes (10): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+2 more)

### Community 36 - "caddy"
Cohesion: 0.13
Nodes (5): Rules, rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 37 - "backroom_bench/cli.py"
Cohesion: 0.29
Nodes (6): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)

### Community 38 - "F1 Morning brief (Today, up to 3 action cards)"
Cohesion: 0.09
Nodes (22): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, scripts, bench (+14 more)

### Community 39 - "portals"
Cohesion: 0.17
Nodes (16): AskHuman, CostTick, _Event, GoldenFrame, HealAttempt, HealFailed, HealStarted, HealSucceeded (+8 more)

### Community 40 - "postgres"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 41 - "backroom_data/cli.py"
Cohesion: 0.20
Nodes (4): main(), next_saturday(), _notes(), test_story_numbers_come_out_of_the_built_data()

### Community 42 - "candidate.py"
Cohesion: 0.20
Nodes (4): ActionCard, Evidence, EvidenceNumber, n()

### Community 43 - "scripts"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 44 - "test_chaos_render.py"
Cohesion: 0.12
Nodes (17): catalog_html(), dom_hash(), fresh_client(), signed_in(), skill_path_pages(), test_admin_chaos_validates_and_needs_the_token(), test_demo_seed_7_page(), test_different_seeds_give_different_doms() (+9 more)

### Community 45 - "M0 gate (pnpm check green, /health, probe:llm, shell at 390/1440)"
Cohesion: 0.12
Nodes (18): dependencies, @base-ui/react@^1.9.0, class-variance-authority@^0.7.1, cn@^0.5.2, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0, shadcn@^4.23.0 (+10 more)

### Community 46 - "services"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+11 more)

### Community 47 - "depends_on"
Cohesion: 0.16
Nodes (20): CLAUDE.md - Backroom agent guide, context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path), Read order (BUILD_PLAN -> GRAPH_REPORT -> PRD/ARCH sections), Rule: mock portals only; no bot-protection evasion, serena MCP (symbol navigation and edits) (+12 more)

### Community 48 - "writers.py"
Cohesion: 0.15
Nodes (10): Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), _at(), ingredient_id(), invoices_from_price_change(), pack_sizes(), record_preference(), _rows(), write_invoice() (+2 more)

### Community 49 - "Sync log: PC → laptop"
Cohesion: 0.17
Nodes (10): build(), daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost() (+2 more)

### Community 50 - "AGENTS.md"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 51 - "laptop.md"
Cohesion: 0.14
Nodes (10): pick_variants(), Label, test_admin_chaos_sets_reads_and_resets_seeds(), test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix() (+2 more)

### Community 52 - "grainline/store.py"
Cohesion: 0.10
Nodes (9): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), next_weekday(), price_on(), PriceEvent, Product, seeded_orders(), SeedLine, SeedOrder (+1 more)

### Community 53 - "pnpm-workspace.yaml"
Cohesion: 0.08
Nodes (23): RunEvent, 1. Changing a contract, 4. Skills, 5. Run events, 9. Fixtures and the drift check, Contracts (L0), 1. Where we are, 2. Setup (+15 more)

### Community 54 - "memory/store.py"
Cohesion: 0.14
Nodes (12): EpisodeRef, FactDetail, add_episode(), assert_fact(), Assertion, fact_detail(), facts_as_of(), graph() (+4 more)

### Community 55 - "backroom"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 56 - "backroom-data"
Cohesion: 0.15
Nodes (14): SkillVersions, Contract, Cursor, FrameMeta, CssFallback, Expect, LabelFallback, Locator (+6 more)

### Community 57 - "backroom-portals"
Cohesion: 0.15
Nodes (10): zod@^4.6.7, briefSchema, brief, fixtures, negatives, memoryGraphSchema, runEventSchema, skillSummarySchema (+2 more)

### Community 58 - "RuntimeError"
Cohesion: 0.32
Nodes (9): ApiStatus(), AppShell(), isActive(), NAV_ITEMS, NavItem, SidebarLinks(), TabBarLinks(), BusinessBadge() (+1 more)

### Community 59 - "backroom_portals/__init__.py"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 60 - "extractor.py"
Cohesion: 0.19
Nodes (5): checked(), extract(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 61 - "TillDeskStore"
Cohesion: 0.17
Nodes (6): 2. Portals, Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), MenuItem, TillDeskState, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 62 - "api-status.tsx"
Cohesion: 0.18
Nodes (9): @tanstack/react-query@^5.107.1, Status, Tone, TONE_DOT, API_URL, fetchHealth(), Health, healthSchema (+1 more)

### Community 63 - "README - Backroom overview"
Cohesion: 0.17
Nodes (12): Add Live demo + Benchmarks badges to README, Backroom: agentic back office for a cafe (engine under 'Approve all'), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration, JD problem 4: agentic self-improvement, Why this exists: Super44 JD hard problems (+4 more)

### Community 64 - "Settings"
Cohesion: 0.17
Nodes (8): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 65 - "layout.tsx"
Cohesion: 0.22
Nodes (8): geistMono, geistSans, instrumentSerif, metadata, RootLayout(), viewport, Providers(), themeInitScript

### Community 66 - "sales.py"
Cohesion: 0.13
Nodes (13): _maven_sales(), apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days() (+5 more)

### Community 68 - "client.py"
Cohesion: 0.15
Nodes (5): CallRecord, SpendLedger, Caps, caps_for(), test_ledger_only_counts_today()

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

### Community 82 - "backroom_portals/main.py"
Cohesion: 0.16
Nodes (4): get_settings(), Settings, create_app(), default_secret()

### Community 89 - "test_llm_client.py"
Cohesion: 0.20
Nodes (9): BudgetExceededError, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict(), test_create_sends_wire_model_and_effort_and_records_cost() (+1 more)

### Community 94 - "stream_today"
Cohesion: 0.24
Nodes (11): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), brief_for_today(), BriefResult, stream(), stream_today(), BriefCardEvent, BriefDone (+3 more)

### Community 95 - "health.py"
Cohesion: 0.19
Nodes (4): is_configured(), health(), _portals_ok(), _postgres_ok()

### Community 96 - "totp.py"
Cohesion: 0.30
Nodes (5): code_at(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 97 - "write"
Cohesion: 0.18
Nodes (5): git_sha(), models(), with_fee(), write(), test_fee_line_only_on_openrouter()

### Community 98 - "packer.py"
Cohesion: 0.27
Nodes (4): estimate_tokens(), pack(), seeds_for(), _triple()

### Community 101 - "LLMPlanner"
Cohesion: 0.22
Nodes (9): LLMPlanner, _Message, _Result, StubLLM, test_guard_accepts_numbers_from_the_evidence(), test_guard_rejects_unbacked_numbers(), test_llm_planner_raises_on_unusable_answers(), test_llm_planner_sends_a_cached_structured_request() (+1 more)

### Community 102 - "test_harness.py"
Cohesion: 0.22
Nodes (3): FakeRunner, test_b1_grid_and_headline(), test_b2_spikes_at_redesigns_then_recovers()

### Community 103 - "parquet.py"
Cohesion: 0.29
Nodes (3): read(), write(), test_inventory_covers_only_the_order_window()

### Community 104 - "_run"
Cohesion: 0.22
Nodes (3): _briefs(), _run(), LlmAnswerer

## Ambiguous Edges - Review These
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay (golden runs, DEMO_MODE=replay)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Scripted event: oat milk +9% day -3` → `Card: Reorder oat milk (stock-out, Grainline)`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `README badges (CI, license, stack)` → `Design tokens (crema/roasted caramel palette; tokens.css)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **26 isolated node(s):** `python`, `uvx`, `@playwright/mcp`, `start-mcp-server`, `@upstash/context7-mcp` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 643 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Contracts (L0)` connect `pnpm-workspace.yaml` to `PlaceholderPage`, `Sync log: PC → laptop`, `Candidate`, `Number guard (every number in copy must match evidence)`, `TillDeskStore`, `stream_today`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `9.1 Laptop tasks (light)`) actually correct?**
  _`Candidate` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `python`, `uvx`, `@playwright/mcp` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `M3 Memory + Brief + UI (Thu 14:00-19:00)` be split into smaller, more focused modules?**
  _Cohesion score 0.09872241579558652 - nodes in this community are weakly interconnected._
- **Why does `RunEvent` connect `pnpm-workspace.yaml` to `steps`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay (golden runs, DEMO_MODE=replay)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Scripted event: oat milk +9% day -3` and `Card: Reorder oat milk (stock-out, Grainline)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._