# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 182 files · ~102,730 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 9, .example 1, .glb 1)

## Summary
- 2541 nodes · 6433 edges · 119 communities (104 shown, 15 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 660 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `42e46f8c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- M3 Memory + Brief + UI (Thu 14:00-19:00)
- test_memory.py
- Hosting and operations
- M2 Browser agent (Thu 09:00-14:00, riskiest)
- gen_fixtures.py
- action-card.tsx
- Build Plan (Wed 22:00 -> Fri 11:30 freeze)
- registry.py
- steps
- probe.py
- project.yml
- web/package.json
- PlaceholderPage
- scripts
- components.json
- dependencies
- layout.tsx
- compilerOptions
- test_llm_client.py
- Handover — read this first on a new machine or in a new session
- client.py
- Browser agent
- .mcp.json
- Frontend (apps/web) choices
- F2 Run theater (step timeline + live browser stream)
- app-shell.tsx
- grainline/store.py
- M4 Bench + Deploy (Thu 19:00-23:30)
- Demo Script - 5 minutes
- health.py
- api
- caddy
- writers.py
- portals
- postgres
- SpendLedger
- scripts
- memory/store.py
- services
- Why this exists: Super44 JD hard problems
- depends_on
- healthcheck
- Backend choices (services/api)
- Backroom Product Requirements Document
- laptop.md
- backroom-api
- M4 Bench + Deploy (Thu 19:00-23:30)
- Verify every change
- L5: temporal memory store, writers, context packer (laptop/l5-memory)
- backroom-data
- backroom-portals
- RuntimeError
- backroom_portals/__init__.py
- agent-dock.tsx
- shifts
- format.ts
- Candidate
- particles.ts
- memory-desk.tsx
- compilerOptions
- L2: chaos engine with 9 families (laptop/l2-chaos)
- test_llm_client.py
- Handover — read this first on a new machine or in a new session
- totp.py
- LLM
- Decision Log (ADRs + laptop deviations)
- Repository layout
- page
- .mcp.json
- agents.py
- Security notes (talking points)
- preferences
- jobs
- steps
- test_contract.py
- Escalation ladder (deterministic fallbacks, healer, escalation + screenshot, ask_human)
- package.json
- Decision Log (ADRs + laptop deviations)
- backroom_bench/cli.py
- rendering.py
- package.json
- api
- caddy
- Handover
- typing
- layout.tsx
- portals
- postgres
- intro-player.tsx
- extractor.py
- L4: data pipeline to Parquet (laptop/l4-data)
- shell-extras.tsx
- Verify every change
- theme-toggle.tsx
- services
- rules.py
- rules
- depends_on
- healthcheck
- backroom-api
- backroom-data
- pnpm-workspace.yaml
- backroom
- app-shell.tsx
- run-screen.tsx
- command-palette.tsx
- cafe-pattern.tsx
- How this maps to the real Super44 problem
- Skill
- Clock
- L0: shared contracts (laptop/l0-contracts)
- L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)
- 9. Work split: laptop (light) vs this PC (heavy)
- GuardResult

## God Nodes (most connected - your core abstractions)
1. `Laptop deviations (L-n log, append-only; PC renumbers on merge)` - 77 edges
2. `Candidate` - 60 edges
3. `Backroom Product Requirements Document` - 53 edges
4. `Contract` - 52 edges
5. `react` - 32 edges
6. `LLM` - 30 edges
7. `build()` - 30 edges
8. `Settings` - 29 edges
9. `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)` - 28 edges
10. `generate()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `5. Run events` --references--> `RunEvent`  [INFERRED]
  docs/CONTRACTS.md → apps/web/src/lib/contracts.ts
- `Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)` --references--> `Look`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/rendering.py
- `Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)` --references--> `TillDeskState`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/contract.py
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py

## Import Cycles
- 2-file cycle: `services/portals/backroom_portals/config.py -> services/portals/backroom_portals/totp.py -> services/portals/backroom_portals/config.py`

## Hyperedges (group relationships)
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — docs_prd_detectors, docs_prd_candidate, docs_prd_planner, docs_prd_verifier, docs_prd_number_guard, docs_architecture_route_brief_today [EXTRACTED 1.00]
- **Chaos-aware rendering primitives shared by all portals** — services_portals_backroom_portals_templates_macros_wrap, services_portals_backroom_portals_templates_macros_submit, services_portals_backroom_portals_templates_macros_field, services_portals_backroom_portals_templates_macros_nav, services_portals_backroom_portals_templates_macros_interstitial, services_portals_backroom_portals_templates_macros_chaos_js, services_portals_backroom_portals_templates_macros_look_chaos_object [EXTRACTED 1.00]
- **Single LLM call path: registry, client, cost meter, ledger, budget guard and capability flags** — docs_architecture_model_registry, docs_architecture_llm_client_call_path, docs_architecture_cost_meter, docs_architecture_llm_ledger, docs_architecture_budget_guard, docs_architecture_capability_flags [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — docs_prd_explore_mode, docs_prd_skill_compiler, docs_prd_replay_engine, docs_prd_heal_ladder, docs_prd_skill_versioning, docs_architecture_escalation_ladder [EXTRACTED 1.00]
- **Brief flow: detectors compute, planner writes, verifier checks, number guard verifies** — docs_contracts_detectors, docs_contracts_candidate, docs_contracts_brief_pipeline, docs_decisions_l_58_verifier_keep_or_veto, docs_contracts_number_guard_rules, docs_decisions_adr_5_agents_judgment_code_math [INFERRED 0.85]
- **F4 reject-to-preference loop (extract cap, re-price in code, fresh action id, rules lead the pack)** — docs_decisions_l_64_preference_extractor_on_laptop, docs_decisions_l_63_action_id_hash, docs_decisions_l_58_verifier_keep_or_veto, docs_decisions_l_54_token_estimate, docs_decisions_l_44_pricing_rule, services_api_backroom_api_memory_extractor_record_rejection [INFERRED 0.85]
- **Honest sample fallbacks in the web app until PC routes exist** — docs_decisions_l_68_sample_brief_badge, docs_decisions_l_72_skills_memory_sample_fallback, docs_decisions_l_73_bench_committed_results, docs_decisions_l_74_sample_run_ticker, apps_web_src_lib_data_useliveorsample, apps_web_src_components_sample_badge [INFERRED 0.85]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — docs_prd_franzbroetchen_story, docs_architecture_route_reject, docs_prd_episodes, docs_prd_extractor, docs_prd_preference_fact, docs_prd_verifier, demo_beat_learn_owner [INFERRED 0.85]
- **Chaos seed 7 demo heal (German labels, cookie banner, multi-step heal)** — docs_decisions_l_16_seed_7_pinned, docs_decisions_l_24_seed7_heal_risk, docs_decisions_l_6_heal_semantics, docs_decisions_l_21_interstitial_cookie, docs_decisions_l_15_chaos_labels_only [INFERRED 0.85]
- **Self-healing skill loop under chaos seed 7** — docs_prd_f3_skill_learning_healing, docs_architecture_escalation_ladder, docs_contracts_skill_versioning_heal, docs_contracts_skill_diff, docs_decisions_l_6_heal_semantics, docs_decisions_l_16_seed_7_pinned, docs_demo_script_break_it_seed_7_heal [INFERRED 0.85]
- **Two-machine contract-first coordination** — docs_decisions_adr_15_two_machine_workflow, docs_handover_work_split, docs_handover_ownership_table, docs_contracts_contract_change_process, docs_sync_laptop, docs_sync_pc [INFERRED 0.85]
- **Grainline ordering flow pages** — services_portals_backroom_portals_templates_grainline_catalog, services_portals_backroom_portals_templates_grainline_cart, services_portals_backroom_portals_templates_grainline_checkout, services_portals_backroom_portals_templates_grainline_order, services_portals_backroom_portals_templates_grainline_invoices [INFERRED 0.95]
- **TillDesk price change and publish flow** — services_portals_backroom_portals_templates_tilldesk_login, services_portals_backroom_portals_templates_tilldesk_menu, services_portals_backroom_portals_templates_tilldesk_edit, services_portals_backroom_portals_templates_tilldesk_menu_draft_publish_flow [INFERRED 0.95]

## Communities (119 total, 15 thin omitted)

### Community 0 - "M3 Memory + Brief + UI (Thu 14:00-19:00)"
Cohesion: 0.26
Nodes (24): _authed(), cart(), cart_add(), cart_update(), catalog(), checkout(), checkout_submit(), dashboard() (+16 more)

### Community 1 - "test_memory.py"
Cohesion: 0.05
Nodes (46): Invoice ingest AC (superseding price facts within 10 s), Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), GraphFact, estimate_tokens(), pack(), seeds_for(), _triple(), add_episode() (+38 more)

### Community 2 - "Hosting and operations"
Cohesion: 0.03
Nodes (60): actionCardSchema, approveResponseSchema, briefSchema, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema, ChaosState (+52 more)

### Community 3 - "M2 Browser agent (Thu 09:00-14:00, riskiest)"
Cohesion: 0.15
Nodes (8): Order, OrderLine, _document(), _eur(), invoice_pdf(), _text(), GrainlineStore, Invoice

### Community 4 - "gen_fixtures.py"
Cohesion: 0.18
Nodes (16): AskHuman, CostTick, _Event, HealAttempt, HealFailed, HealStarted, HealSucceeded, ModeChanged (+8 more)

### Community 5 - "action-card.tsx"
Cohesion: 0.07
Nodes (41): @base-ui/react@^1.9.0, Error(), STEPS, ActionCard(), approve(), onDragEnd(), onPointerMove(), openReject() (+33 more)

### Community 6 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.12
Nodes (30): M1 Data + Portals (Wed 23:00-01:30), B3 ground truth computed by SQL on same data, Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg), Data Sources & Honesty Notes, Simulated inventory (opening + deliveries - sales x BOM), Maven Coffee Shop Sales dataset, Maven Analytics 'Coffee Shop Sales' (~149k rows, NYC), Maven source URL (S3 zip, verified 11 Nov) (+22 more)

### Community 7 - "registry.py"
Cohesion: 0.14
Nodes (15): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), copy_for() (+7 more)

### Community 8 - "steps"
Cohesion: 0.10
Nodes (25): 7. API shapes, 8. Memory, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, ActionCard, ApiError, ApproveResponse, Brief, ChaosRequest (+17 more)

### Community 9 - "probe.py"
Cohesion: 0.13
Nodes (15): 2. Portals, chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosRequest (+7 more)

### Community 10 - "project.yml"
Cohesion: 0.12
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 11 - "web/package.json"
Cohesion: 0.14
Nodes (30): brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier, _Message, _Result (+22 more)

### Community 12 - "PlaceholderPage"
Cohesion: 0.44
Nodes (7): isActive(), NAV_ITEMS, navDirection(), NavItem, PILL, TabBarLinks(), TopBarLinks()

### Community 13 - "scripts"
Cohesion: 0.11
Nodes (19): to_sse(), Step, StepChange, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step() (+11 more)

### Community 14 - "components.json"
Cohesion: 0.07
Nodes (24): build(), _maven_sales(), next_saturday(), _notes(), read(), load_map(), _column(), rows() (+16 more)

### Community 15 - "dependencies"
Cohesion: 0.12
Nodes (31): Rule: LLMs never originate numbers, Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, M3 Memory + Brief + UI (Thu 14:00-19:00), M3 Memory + Brief + UI, B5 Number guard benchmark, Bitemporal Fact model (valid time + record time) (+23 more)

### Community 16 - "layout.tsx"
Cohesion: 0.12
Nodes (27): Providers(), SkillDetail(), Stat(), Stats, Steps(), useRegistry(), useVersions(), versionStats() (+19 more)

### Community 17 - "compilerOptions"
Cohesion: 0.12
Nodes (18): catalog_html(), dom_hash(), forced(), fresh_client(), signed_in(), skill_path_pages(), test_admin_chaos_sets_reads_and_resets_seeds(), test_admin_chaos_validates_and_needs_the_token() (+10 more)

### Community 18 - "test_llm_client.py"
Cohesion: 0.08
Nodes (48): Rule: secrets never reach prompts or logs, Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Q: What breaks first in production, Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), Healer role (LLM_HEAL_MODEL, Haiku 5.5, low): first heal attempt, M2 Browser agent (Thu 09:00-14:00, riskiest) (+40 more)

### Community 19 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 20 - "client.py"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 21 - "Browser agent"
Cohesion: 0.21
Nodes (28): has_testid(), login(), state(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove(), test_catalog_paginates() (+20 more)

### Community 22 - ".mcp.json"
Cohesion: 0.05
Nodes (64): motion@14.9.0, metadata, RunPage(), Theater(), Element, ElementView(), FIELD_ROLES, fieldValue() (+56 more)

### Community 23 - "Frontend (apps/web) choices"
Cohesion: 0.09
Nodes (25): This is NOT the Next.js you know, Charts (Recharts or visx; dataviz skill, palette validator), Frontend (apps/web) choices, Memory graph lib (@xyflow/react or force-graph; benchmark at ~300 nodes), Key API routes, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), Next.js (App Router, latest stable), TypeScript strict, pnpm, Route /memory (+17 more)

### Community 24 - "F2 Run theater (step timeline + live browser stream)"
Cohesion: 0.06
Nodes (42): eslintConfig, dependencies, class-variance-authority@^0.7.1, cn@^0.5.2, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0, shadcn@^4.23.0 (+34 more)

### Community 25 - "app-shell.tsx"
Cohesion: 0.12
Nodes (31): TodayPage(), EmptyState(), BadgeSlot(), SampleBadge(), BriefCommands(), BriefSkeleton(), COUNT_WORDS, decisions() (+23 more)

### Community 26 - "grainline/store.py"
Cohesion: 0.13
Nodes (9): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), next_weekday(), price_on(), seeded_orders(), SeedLine, SeedOrder, Session, default_secret() (+1 more)

### Community 27 - "M4 Bench + Deploy (Thu 19:00-23:30)"
Cohesion: 0.17
Nodes (10): concurrency, cancel-in-progress, group, name, on, pull_request, push, permissions (+2 more)

### Community 28 - "Demo Script - 5 minutes"
Cohesion: 0.15
Nodes (24): Rule: all LLM access through llm/registry.py, Q: Cost at scale, Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), LLM_<ROLE>_EFFORT override, LLM_PROVIDER env var (openrouter default | anthropic), backroom_api/agents (browser agent, planner, verifier, extractor), claude-haiku-5-5 ($0.10 / $0.50; long-prompt tier above 100K), Model layer (every provider and model choice is an env var) (+16 more)

### Community 29 - "health.py"
Cohesion: 0.18
Nodes (7): 1. Changing a contract, 3. Chaos catalog, 4. Skills, 5. Run events, 9. Fixtures and the drift check, Contracts (L0), Look

### Community 30 - "api"
Cohesion: 0.08
Nodes (32): nextConfig, next@16.4.6, AboutPage(), Chapter(), LADDER, metadata, MODELS, BenchHeadline() (+24 more)

### Community 31 - "caddy"
Cohesion: 0.08
Nodes (28): Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), CardCopy, Planner, Verifier, action_id(), brief_for_today(), BriefResult, _copy_for() (+20 more)

### Community 32 - "writers.py"
Cohesion: 0.11
Nodes (20): Rule: every LLM call through cost meter + budget guard, Code freeze Fri 13 Nov 11:30, Build Plan (Wed 22:00 -> Fri 11:30 freeze), Record golden runs -> replay mode, M0 Foundations, M1 Data + Portals, M2 Browser agent (riskiest), M4 Bench + Deploy (+12 more)

### Community 33 - "portals"
Cohesion: 0.14
Nodes (10): apply_rainy_saturdays(), map_item(), parse_maven(), rebase(), Sale, shift_days(), synthetic(), test_rain_effect_follows_the_local_trend() (+2 more)

### Community 34 - "postgres"
Cohesion: 0.14
Nodes (11): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+3 more)

### Community 35 - "SpendLedger"
Cohesion: 0.19
Nodes (3): MenuItem, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 36 - "scripts"
Cohesion: 0.09
Nodes (20): 6. Candidates and the number guard, connect(), Context, _ingredient(), margin_erosion(), _n(), run_all(), _shown() (+12 more)

### Community 37 - "memory/store.py"
Cohesion: 0.17
Nodes (17): Frontend quality bar (Lighthouse >= 90, reduced motion), apps/web/src/styles/tokens.css, ui-ux-pro-max skill, Fonts via next/font: Newsreader (display + text cut), Geist, Geist Mono, Lightsail snapshot before final deploy (2-minute rollback), Route / Today, GET /brief/today (cached brief; ?regenerate=1 streams a new one), Code freeze Fri 13 Nov 11:30 (snapshot, no deploys) (+9 more)

### Community 38 - "services"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 39 - "Why this exists: Super44 JD hard problems"
Cohesion: 0.08
Nodes (24): build_async_client(), canonical_model_id(), Caps, caps_for(), Cost, cost_usd(), is_configured(), LLMNotConfiguredError (+16 more)

### Community 40 - "depends_on"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 41 - "healthcheck"
Cohesion: 0.12
Nodes (23): Backroom Technical Architecture, Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), Deploy freeze: no deploys after Fri 11:30, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), FastAPI api service (orchestrator, agents, memory, SSE/WS), Hosting fallback (Hetzner CX22 / Fly.io with the same compose file), Hosting and operations (cheap, reliable) (+15 more)

### Community 42 - "Backend choices (services/api)"
Cohesion: 0.17
Nodes (11): Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, CDP Page.startScreencast live frames, Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test), GHCR container registry, infra/ (docker-compose.yml, Caddyfile, deploy.sh, Lightsail notes), backroom_api/browser (pool, ARIA snapshot observation, executor, screencast) (+3 more)

### Community 43 - "Backroom Product Requirements Document"
Cohesion: 0.09
Nodes (32): Rule: fictional names only; no Super44 branding in UI, Langfuse Cloud Hobby traces (P1), Sentry free tier errors (P1), Decision at 19:00: Localboard / Ask in or out, TillDesk may slip to Thu 08:00, Open or synthetic data only ('Synthetic' chip in UI), Action card (impact, why, evidence chips, Approve/Review/Not now), B2 Learning curve (+24 more)

### Community 44 - "laptop.md"
Cohesion: 0.10
Nodes (11): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), health(), _portals_ok() (+3 more)

### Community 45 - "backroom-api"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 46 - "M4 Bench + Deploy (Thu 19:00-23:30)"
Cohesion: 0.12
Nodes (26): Check: DOM-hash test per chaos seed, Beat 4:00 Proof - /bench, CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), GET /health (liveness + dependency checks) (+18 more)

### Community 47 - "Verify every change"
Cohesion: 0.19
Nodes (13): CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, claude-api skill (load before Anthropic SDK code), context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path), Session read order (HANDOVER, BUILD_PLAN, GRAPH_REPORT) (+5 more)

### Community 48 - "L5: temporal memory store, writers, context packer (laptop/l5-memory)"
Cohesion: 0.19
Nodes (7): Context packer (memory.packer.pack), Memory writers (assert_fact, write_world, write_invoice), Predicate vocabulary (one-valued, many-valued), Neon hosted Postgres (laptop database), Neon hosted Postgres for the laptop, B3 Memory vs baseline, L5: temporal memory store, writers, context packer (laptop/l5-memory)

### Community 49 - "backroom-data"
Cohesion: 0.17
Nodes (16): Portals admin API (/_admin/chaos, state, reset), Brief pipeline (stream_today, BriefResult), Detector Candidate, Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Number guard rules 1-9, pick_variants(portal, seed), Skill postconditions (url_matches, text_visible, portal_state) (+8 more)

### Community 50 - "backroom-portals"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 51 - "RuntimeError"
Cohesion: 0.20
Nodes (8): CssFallback, Expect, LabelFallback, Postcondition, SkillDiff, SkillStats, TextFallback, reorder_steps()

### Community 52 - "backroom_portals/__init__.py"
Cohesion: 0.20
Nodes (15): 'As of' query predicate (valid_from <= t and valid_to null or > t), Index fact (subject_id, predicate, valid_from desc), Memory schema sketch (entity, episode, fact), Table entity (type, name, attrs, optional embedding vector(384), fastembed bge-small P1), Table episode (invoice | approval | rejection | chat | run | seed), Table fact (subject, predicate, object/value, valid_from/valid_to, recorded_at, source_episode, confidence), Memory contract (bitemporal facts, supersession), entity (+7 more)

### Community 53 - "agent-dock.tsx"
Cohesion: 0.11
Nodes (24): AgentDock(), PlayableRun, PlayingRun(), Ring(), SPRING, TheaterLink(), Mode, MODE_STYLE (+16 more)

### Community 54 - "shifts"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 55 - "format.ts"
Cohesion: 0.12
Nodes (22): @number-flow/react@0.6.2, EUR, SUFFIX, CardVisual(), EvidenceBars(), MarginScale(), num(), plain (+14 more)

### Community 56 - "Candidate"
Cohesion: 0.21
Nodes (13): Candidate, candidates(), data_dir(), numbers(), test_a_date_the_data_was_not_built_for_is_refused(), test_all_three_detectors_fire(), test_every_card_lists_its_impact_and_ids_are_deterministic(), test_franzbroetchen_margin_story_comes_out_of_the_data() (+5 more)

### Community 57 - "particles.ts"
Cohesion: 0.26
Nodes (12): attachParticleCanvas(), Effect, effects, ensureLoop(), explodeInto(), formFrom(), isDarkTheme(), Particle (+4 more)

### Community 58 - "memory-desk.tsx"
Cohesion: 0.16
Nodes (23): edgePath(), FactValue(), isoDay(), MemoryDesk(), play(), writeUrl(), plainValue(), Point (+15 more)

### Community 59 - "compilerOptions"
Cohesion: 0.12
Nodes (17): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+9 more)

### Community 60 - "L2: chaos engine with 9 families (laptop/l2-chaos)"
Cohesion: 0.14
Nodes (10): POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), TillDesk (mock till / menu portal), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Laptop deviations (L-n log, append-only; PC renumbers on merge), Brief AC: <1.5 s cached, <15 s cold, Independent audit pass per laptop task (blockers and should-fix items, all fixed), L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline) (+2 more)

### Community 61 - "test_llm_client.py"
Cohesion: 0.11
Nodes (12): BudgetExceededError, CallRecord, SpendLedger, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling() (+4 more)

### Community 62 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.17
Nodes (12): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+4 more)

### Community 63 - "totp.py"
Cohesion: 0.30
Nodes (5): code_at(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 64 - "LLM"
Cohesion: 0.13
Nodes (17): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+9 more)

### Community 65 - "Decision Log (ADRs + laptop deviations)"
Cohesion: 0.13
Nodes (14): Q: Why not browser-use / Stagehand, LLM_CAPS_OFF (switch capability flags off), OpenRouter ~5.5% credit fee (OPENROUTER_FEE_PCT), Provider openrouter (default; base_url openrouter.ai/api, auth_token, X-Title/HTTP-Referer headers), psycopg 3 synchronous pool called from worker threads, Decision Log (ADRs + laptop deviations), Alternative: browser-use / Stagehand, Alternative: Graphiti + FalkorDB / Neo4j (+6 more)

### Community 66 - "Repository layout"
Cohesion: 0.17
Nodes (16): Stack and commands, docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), backroom_api/memory (schema, writers, supersession, context packer), backroom_api/replay (golden-run recorder & player), Native local dev (uv run uvicorn --reload; only Postgres in Docker), Root package.json (pnpm workspace root + task runner), pnpm dev (Postgres in Docker + api + portals + next dev in parallel), pnpm-workspace.yaml (packages: apps/web) (+8 more)

### Community 67 - "page"
Cohesion: 0.21
Nodes (3): fact(), label(), page()

### Community 69 - ".mcp.json"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 70 - "agents.py"
Cohesion: 0.10
Nodes (19): L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief), BriefLLMError, candidate_view(), Draft, LLMPlanner, LLMVerifier, _Model, _parse() (+11 more)

### Community 71 - "Security notes (talking points)"
Cohesion: 0.23
Nodes (9): Check: one real LLM call (stop_reason, $, cache_read > 0), Daily LLM budget guard (sums today's ledger rows before each call), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), backroom_api/llm (model registry, client, cost meter, budget guard), pnpm probe:llm (uv run backroom-bench probe), bench/results/provider_probe.json (+1 more)

### Community 72 - "preferences"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 73 - "jobs"
Cohesion: 0.20
Nodes (10): name, runs-on, jobs, docs, python, web, name, runs-on (+2 more)

### Community 74 - "steps"
Cohesion: 0.24
Nodes (13): steps, steps, id, if, name, run, uses, with (+5 more)

### Community 75 - "test_contract.py"
Cohesion: 0.16
Nodes (9): pick_variants(), Label, test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 77 - "package.json"
Cohesion: 0.18
Nodes (17): Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Q: Cloudflare / bot protection on real portals, Rehearse demo script 3x on deployed URL, Demo-story prices (DEMO_PRICES_EUR), Demo Script - 5 minutes, Five-minute demo beats (hook, evidence, act, break it, remember, learn, proof, close), Approve all button (+9 more)

### Community 78 - "Decision Log (ADRs + laptop deviations)"
Cohesion: 0.17
Nodes (12): scripts, bench, check, check:py, dev, dev:api, dev:db, dev:lite (+4 more)

### Community 80 - "rendering.py"
Cohesion: 0.13
Nodes (5): main(), get_settings(), Settings, create_app(), client()

### Community 81 - "package.json"
Cohesion: 0.25
Nodes (8): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, version, concurrently

### Community 82 - "api"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 83 - "caddy"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 84 - "Handover"
Cohesion: 0.10
Nodes (21): pnpm dev:lite (api, portals, web without Docker or a database; API reports degraded), Fixtures and the drift check, Handover, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13, PC tasks H1-H9 (+13 more)

### Community 85 - "typing"
Cohesion: 0.09
Nodes (3): write(), PriceEvent, Product

### Community 86 - "layout.tsx"
Cohesion: 0.21
Nodes (9): geistMono, geistSans, metadata, RootLayout(), viewport, INTRO_KEY, introInitScript, IntroOverlay() (+1 more)

### Community 87 - "portals"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 88 - "postgres"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 89 - "intro-player.tsx"
Cohesion: 0.29
Nodes (5): @google/model-viewer@4.4.0, IntroPlayer(), ModelViewer, afterFirstData(), @google/model-viewer

### Community 90 - "extractor.py"
Cohesion: 0.24
Nodes (4): checked(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 91 - "L4: data pipeline to Parquet (laptop/l4-data)"
Cohesion: 0.18
Nodes (6): DuckDB over Parquet (sales analytics), backroom_api/analytics (DuckDB queries, stockout/margin/weather detectors), data package backroom_data (script backroom-data; raw data not committed), pnpm seed (uv run backroom-data all: download, transform, load Postgres + Parquet), L4: data pipeline to Parquet (laptop/l4-data), L6: DuckDB detectors and deterministic pricing (laptop/l6-detectors)

### Community 92 - "shell-extras.tsx"
Cohesion: 0.30
Nodes (8): SceneDriver(), AgentDock, CommandPalette, IntroPlayer, ParticleLayer, ShellExtras(), useCachedBrief(), setRaining()

### Community 93 - "Verify every change"
Cohesion: 0.14
Nodes (11): Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: Lighthouse via web-perf skill, Check: pytest + ruff + pyright for Python logic, Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Verification rules (verify before next step, state evidence), web-perf skill (Lighthouse), Lint/test: ruff, pyright (strict on core), pytest, pytest-asyncio (+3 more)

### Community 94 - "theme-toggle.tsx"
Cohesion: 0.22
Nodes (10): CommandPalette(), Command, onPaletteOpen(), useCommands(), isDark(), listeners, setDark(), subscribeTheme() (+2 more)

### Community 95 - "services"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 96 - "rules.py"
Cohesion: 0.21
Nodes (4): rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 97 - "rules"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 98 - "depends_on"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 99 - "healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 108 - "app-shell.tsx"
Cohesion: 0.52
Nodes (5): ApiStatus(), AppShell(), CommandButton(), ThemeToggle(), Wordmark()

### Community 109 - "run-screen.tsx"
Cohesion: 0.16
Nodes (13): @tanstack/react-query@^5.107.1, zod@^4.6.7, Status, Tone, TONE_DOT, API_URL, fetchHealth(), Loaded (+5 more)

### Community 110 - "command-palette.tsx"
Cohesion: 0.28
Nodes (7): listeners, openListeners, openPalette(), publish(), registerCommands(), snapshot, sources

### Community 111 - "cafe-pattern.tsx"
Cohesion: 0.36
Nodes (7): CafePattern(), FAR, Glyph, Layer(), NEAR, Tile(), useScene()

### Community 112 - "How this maps to the real Super44 problem"
Cohesion: 0.32
Nodes (6): Beat 4:40 Close - /about, model table, adapters, Shared Action interface to the planner, Memory per merchant + cross-merchant best-practices layer, backroom_api/skills (compiler, replay, healer, registry), Route /about (architecture for the interview), How this maps to the real Super44 problem

### Community 116 - "L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)"
Cohesion: 0.40
Nodes (3): exclude, include, check:web

### Community 117 - "9. Work split: laptop (light) vs this PC (heavy)"
Cohesion: 0.40
Nodes (5): 9.1 Laptop tasks (light), 9.2 PC tasks (heavy), 9.3 Suggested order, 9.4 Integration rules (so the two sides merge cleanly), 9. Work split: laptop (light) vs this PC (heavy)

## Ambiguous Edges - Review These
- `Scripted event: oat milk +9% day -3` → `Card: Reorder oat milk (stock-out, Grainline)`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **50 isolated node(s):** `backroom-api`, `backroom-bench`, `backroom-data`, `backroom-portals`, `backroom` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 696 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `L0: shared contracts (laptop/l0-contracts)` to `Hosting and operations`, `candidate.py`, `gen_fixtures.py`, `steps`, `probe.py`, `L5: temporal memory store, writers, context packer (laptop/l5-memory)`, `backroom-data`, `RuntimeError`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `Handover`, `backroom_portals/__init__.py`, `typing`, `M4 Bench + Deploy (Thu 19:00-23:30)`, `L2: chaos engine with 9 families (laptop/l2-chaos)`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `L-45 (L6) Weekly EUR impact defined per card kind; cards ranked by it`) actually correct?**
  _`Candidate` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backroom-api`, `backroom-bench`, `backroom-data` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_memory.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0516404581634634 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `L2: chaos engine with 9 families (laptop/l2-chaos)` to `test_memory.py`, `Build Plan (Wed 22:00 -> Fri 11:30 freeze)`, `project.yml`, `dependencies`, `layout.tsx`, `test_llm_client.py`, `M4 Bench + Deploy (Thu 19:00-23:30)`, `health.py`, `api`, `caddy`, `writers.py`, `portals`, `scripts`, `memory/store.py`, `healthcheck`, `Backroom Product Requirements Document`, `L5: temporal memory store, writers, context packer (laptop/l5-memory)`, `backroom-data`, `backroom_portals/__init__.py`, `Decision Log (ADRs + laptop deviations)`, `agents.py`, `Security notes (talking points)`, `Handover`, `L4: data pipeline to Parquet (laptop/l4-data)`, `Verify every change`, `L0: shared contracts (laptop/l0-contracts)`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `GuardResult`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Scripted event: oat milk +9% day -3` and `Card: Reorder oat milk (stock-out, Grainline)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._