# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 181 files · ~101,850 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 9, .example 1, .glb 1)

## Summary
- 2538 nodes · 6429 edges · 115 communities (102 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 660 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `22f4f405`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- grainline/routes.py
- test_memory.py
- Web zod contracts
- GrainlineStore
- gen_fixtures.py
- action-card.tsx
- Backroom Product Requirements Document
- registry.py
- Contract
- admin.py
- project.yml
- web/package.json
- app-shell.tsx
- scripts
- components.json
- dependencies
- format.ts
- compilerOptions
- test_llm_client.py
- Handover — read this first on a new machine or in a new session
- client.py
- Browser agent
- run-theater.tsx
- Frontend (apps/web) choices
- F2 Run theater (step timeline + live browser stream)
- app-shell.tsx
- grainline/store.py
- M4 Bench + Deploy (Thu 19:00-23:30)
- Demo Script - 5 minutes
- Contracts (L0)
- api
- pipeline.py
- Build Plan (Wed 22:00 -> Fri 11:30 freeze)
- portals
- postgres
- TillDeskStore
- scripts
- Portals service (FastAPI + Jinja2, backroom_portals)
- services
- Why this exists: Super44 JD hard problems
- depends_on
- healthcheck
- Decision Log (ADRs + laptop deviations)
- Backroom Product Requirements Document
- laptop.md
- backroom-api
- pnpm-workspace.yaml
- Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)
- Handover
- CONTRACTS.md
- backroom-portals
- schema.py
- backroom_portals/__init__.py
- agent-dock.tsx
- shifts
- LLM
- Candidate
- particles.ts
- memory-desk.tsx
- compilerOptions
- L2: chaos engine with 9 families (laptop/l2-chaos)
- test_llm_client.py
- Handover — read this first on a new machine or in a new session
- totp.py
- probe.py
- Chaos engine (one chaos_seed per portal, seeded RNG variant catalog)
- xlsx.py
- rendering.py
- candidate.py
- .mcp.json
- agents.py
- Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)
- preferences
- health.py
- steps
- test_contract.py
- registry.py
- Demo Script - 5 minutes
- scripts
- backroom_data/cli.py
- backroom_portals/main.py
- README - Backroom overview
- api
- caddy
- laptop.md
- duckdb
- layout.tsx
- portals
- postgres
- contract.py
- record_rejection
- Laptop deviations (L-n log, append-only; PC renumbers on merge)
- shell-extras.tsx
- Verify every change
- command-palette.tsx
- services
- Rules
- rules
- depends_on
- healthcheck
- backroom-api
- backroom-data
- pnpm-workspace.yaml
- backroom
- json
- apps_web_src_lib_utils_cn
- commands.ts
- cafe-pattern.tsx
- How this maps to the real Super44 problem
- Skill
- Clock

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
- `Model price table (USD per 1M tokens; kept in llm/registry.py)` --references--> `Price`  [INFERRED]
  docs/ARCHITECTURE.md → services/api/backroom_api/llm/registry.py
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)` --references--> `TillDeskState`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/contract.py
- `5. Run events` --references--> `RunEvent`  [INFERRED]
  docs/CONTRACTS.md → apps/web/src/lib/contracts.ts

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

## Communities (115 total, 13 thin omitted)

### Community 0 - "grainline/routes.py"
Cohesion: 0.17
Nodes (29): _document(), _eur(), invoice_pdf(), _text(), _authed(), cart(), cart_add(), cart_update() (+21 more)

### Community 1 - "test_memory.py"
Cohesion: 0.05
Nodes (49): POST /memory/ingest/invoice (PDF/image to extractor to facts), Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), L5: temporal memory store, writers, context packer (laptop/l5-memory), EpisodeRef, FactDetail, estimate_tokens(), pack(), seeds_for() (+41 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (73): zod@^4.6.7, actionCardSchema, approveResponseSchema, briefSchema, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema (+65 more)

### Community 3 - "GrainlineStore"
Cohesion: 0.20
Nodes (4): Order, OrderLine, GrainlineStore, Session

### Community 4 - "gen_fixtures.py"
Cohesion: 0.16
Nodes (18): AskHuman, CostTick, Cursor, _Event, FrameMeta, HealAttempt, HealFailed, HealStarted (+10 more)

### Community 5 - "action-card.tsx"
Cohesion: 0.06
Nodes (56): @base-ui/react@^1.9.0, Error(), EUR, SUFFIX, ActionCard(), approve(), onDragEnd(), onPointerMove() (+48 more)

### Community 6 - "Backroom Product Requirements Document"
Cohesion: 0.17
Nodes (22): M1 Data + Portals (Wed 23:00-01:30), B3 ground truth computed by SQL on same data, Data Sources & Honesty Notes, Simulated inventory (opening + deliveries - sales x BOM), Maven Coffee Shop Sales dataset, Maven Analytics 'Coffee Shop Sales' (~149k rows, NYC), Maven source URL (S3 zip, verified 11 Nov), Nager.Date public holidays (+14 more)

### Community 7 - "registry.py"
Cohesion: 0.11
Nodes (15): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), copy_for() (+7 more)

### Community 8 - "Contract"
Cohesion: 0.10
Nodes (24): 7. API shapes, 8. Memory, ApiError, ApproveResponse, Brief, ChaosRequest, ChaosState, ContextPack (+16 more)

### Community 9 - "admin.py"
Cohesion: 0.23
Nodes (7): chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosState

### Community 10 - "project.yml"
Cohesion: 0.12
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 11 - "web/package.json"
Cohesion: 0.18
Nodes (26): brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier, rule(), test_a_reason_without_a_rule_records_only_the_episode() (+18 more)

### Community 12 - "app-shell.tsx"
Cohesion: 0.27
Nodes (12): ApiStatus(), AppShell(), CommandButton(), isActive(), NAV_ITEMS, navDirection(), NavItem, PILL (+4 more)

### Community 13 - "scripts"
Cohesion: 0.12
Nodes (18): to_sse(), Step, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step(), test_margin_card_numbers_match_the_demo_story() (+10 more)

### Community 14 - "components.json"
Cohesion: 0.13
Nodes (16): build(), next_saturday(), _notes(), built(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table() (+8 more)

### Community 15 - "dependencies"
Cohesion: 0.12
Nodes (34): Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, M3 Memory + Brief + UI (Thu 14:00-19:00), Context packer (memory.packer.pack), Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg), Scripted event: oat milk +9% day -3 (+26 more)

### Community 16 - "format.ts"
Cohesion: 0.11
Nodes (32): PageHeader(), Providers(), BadgeSlot(), SampleBadge(), SkillDetail(), SkillsDesk(), Stat(), Stats (+24 more)

### Community 17 - "compilerOptions"
Cohesion: 0.12
Nodes (17): catalog_html(), dom_hash(), forced(), fresh_client(), signed_in(), skill_path_pages(), test_admin_chaos_sets_reads_and_resets_seeds(), test_admin_chaos_validates_and_needs_the_token() (+9 more)

### Community 18 - "test_llm_client.py"
Cohesion: 0.09
Nodes (41): Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Q: What breaks first in production, CDP Page.startScreencast live frames, Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), backroom_api/browser (pool, ARIA snapshot observation, executor, screencast), M2 Browser agent (Thu 09:00-14:00, riskiest) (+33 more)

### Community 19 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 20 - "client.py"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 21 - "Browser agent"
Cohesion: 0.21
Nodes (28): has_testid(), login(), state(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove(), test_catalog_paginates() (+20 more)

### Community 22 - "run-theater.tsx"
Cohesion: 0.06
Nodes (56): metadata, RunPage(), Theater(), Element, ElementView(), FIELD_ROLES, fieldValue(), pageElements() (+48 more)

### Community 23 - "Frontend (apps/web) choices"
Cohesion: 0.09
Nodes (19): This is NOT the Next.js you know, Charts (Recharts or visx; dataviz skill, palette validator), Frontend (apps/web) choices, Memory graph lib (@xyflow/react or force-graph; benchmark at ~300 nodes), Key API routes, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), Navigation domain allowlist per run, Next.js (App Router, latest stable), TypeScript strict, pnpm (+11 more)

### Community 24 - "F2 Run theater (step timeline + live browser stream)"
Cohesion: 0.06
Nodes (45): eslintConfig, dependencies, class-variance-authority@^0.7.1, lucide-react@^1.72.0, motion@14.9.0, @number-flow/react@0.6.2, react@19.3.0, react-dom@19.3.0 (+37 more)

### Community 25 - "app-shell.tsx"
Cohesion: 0.09
Nodes (34): @google/model-viewer@4.4.0, @tanstack/react-query@^5.107.1, IntroPlayer(), ModelViewer, BriefCommands(), BriefSkeleton(), COUNT_WORDS, decisions() (+26 more)

### Community 26 - "grainline/store.py"
Cohesion: 0.13
Nodes (10): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), CallRecord, next_weekday(), price_on(), PriceEvent, Product, seeded_orders(), SeedLine (+2 more)

### Community 27 - "M4 Bench + Deploy (Thu 19:00-23:30)"
Cohesion: 0.12
Nodes (14): exclude, include, Fixtures and the drift check, concurrency, cancel-in-progress, group, name, on (+6 more)

### Community 28 - "Demo Script - 5 minutes"
Cohesion: 0.08
Nodes (33): Rule: all LLM access through llm/registry.py, Q: Cost at scale, Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), LLM_<ROLE>_EFFORT override, LLM_CAPS_OFF (switch capability flags off), LLM_PROVIDER env var (openrouter default | anthropic), backroom_api/agents (browser agent, planner, verifier, extractor), claude-haiku-5-5 ($0.10 / $0.50; long-prompt tier above 100K) (+25 more)

### Community 29 - "Contracts (L0)"
Cohesion: 0.14
Nodes (7): 1. Changing a contract, 3. Chaos catalog, 4. Skills, 9. Fixtures and the drift check, Contracts (L0), Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Look

### Community 30 - "api"
Cohesion: 0.09
Nodes (27): nextConfig, next@16.4.6, AboutPage(), Chapter(), LADDER, metadata, MODELS, BENCHMARKS (+19 more)

### Community 31 - "pipeline.py"
Cohesion: 0.11
Nodes (24): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), CardCopy, Planner, action_id(), brief_for_today(), BriefResult, _copy_for() (+16 more)

### Community 32 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.11
Nodes (22): Rule: every LLM call through cost meter + budget guard, Code freeze Fri 13 Nov 11:30, Build Plan (Wed 22:00 -> Fri 11:30 freeze), Record golden runs -> replay mode, M0 Foundations, M1 Data + Portals, M2 Browser agent (riskiest), M4 Bench + Deploy (+14 more)

### Community 33 - "portals"
Cohesion: 0.12
Nodes (13): _maven_sales(), apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days() (+5 more)

### Community 34 - "postgres"
Cohesion: 0.14
Nodes (11): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+3 more)

### Community 35 - "TillDeskStore"
Cohesion: 0.20
Nodes (4): MenuItem, TillDeskState, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 36 - "scripts"
Cohesion: 0.11
Nodes (17): connect(), Context, _ingredient(), margin_erosion(), _n(), _shown(), stockout(), weather_demand() (+9 more)

### Community 37 - "Portals service (FastAPI + Jinja2, backroom_portals)"
Cohesion: 0.20
Nodes (14): Frontend quality bar (Lighthouse >= 90, reduced motion), apps/web/src/styles/tokens.css, Fonts via next/font: Newsreader (display + text cut), Geist, Geist Mono, Route / Today, GET /brief/today (cached brief; ?regenerate=1 streams a new one), App shell (sidebar/top bar, theme toggle) + fonts, M5 Polish + Rehearse, Accessibility (WCAG AA, keyboard, ARIA live) (+6 more)

### Community 38 - "services"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 39 - "Why this exists: Super44 JD hard problems"
Cohesion: 0.13
Nodes (18): canonical_model_id(), cost_usd(), role_config(), wire_model_id(), make_settings(), test_anthropic_client_uses_default_base_url(), test_anthropic_uses_canonical_ids_and_rejects_slash_ids(), test_caps_defaults_and_overrides() (+10 more)

### Community 40 - "depends_on"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 41 - "healthcheck"
Cohesion: 0.10
Nodes (35): Stack and commands, Backroom Technical Architecture, Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), Deploy freeze: no deploys after Fri 11:30, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), FastAPI api service (orchestrator, agents, memory, SSE/WS) (+27 more)

### Community 42 - "Decision Log (ADRs + laptop deviations)"
Cohesion: 0.11
Nodes (19): Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test), GHCR container registry, infra/ (docker-compose.yml, Caddyfile, deploy.sh, Lightsail notes), Route /runs/[id] Run theater, api image FROM mcr.microsoft.com/playwright/python (noble) (+11 more)

### Community 43 - "Backroom Product Requirements Document"
Cohesion: 0.10
Nodes (29): Rule: fictional names only; no Super44 branding in UI, Sentry free tier errors (P1), Decision at 19:00: Localboard / Ask in or out, TillDesk may slip to Thu 08:00, Open or synthetic data only ('Synthetic' chip in UI), Action card (impact, why, evidence chips, Approve/Review/Not now), B2 Learning curve, Cut order if behind (+21 more)

### Community 44 - "laptop.md"
Cohesion: 0.15
Nodes (8): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 45 - "backroom-api"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 46 - "pnpm-workspace.yaml"
Cohesion: 0.17
Nodes (21): ui-ux-pro-max skill, Beat 4:00 Proof - /bench, Lightsail snapshot before final deploy (2-minute rollback), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), Code freeze Fri 13 Nov 11:30 (snapshot, no deploys), Milestone gate rule (don't start next until gate passes or scope cut logged) (+13 more)

### Community 47 - "Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)"
Cohesion: 0.16
Nodes (15): CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, claude-api skill (load before Anthropic SDK code), context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path), Session read order (HANDOVER, BUILD_PLAN, GRAPH_REPORT) (+7 more)

### Community 48 - "Handover"
Cohesion: 0.16
Nodes (12): pnpm dev:lite (api, portals, web without Docker or a database; API reports degraded), Neon hosted Postgres (laptop database), Handover, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13, Neon hosted Postgres for the laptop (+4 more)

### Community 49 - "CONTRACTS.md"
Cohesion: 0.13
Nodes (21): Portals admin API (/_admin/chaos, state, reset), Brief pipeline (stream_today, BriefResult), Detector Candidate, Chaos catalog (nine variant families), Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Portal labels (en, en_alt, de), Memory writers (assert_fact, write_world, write_invoice) (+13 more)

### Community 50 - "backroom-portals"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 51 - "schema.py"
Cohesion: 0.15
Nodes (9): L0: shared contracts (laptop/l0-contracts), GoldenFrame, CssFallback, Expect, LabelFallback, Postcondition, SkillStats, TextFallback (+1 more)

### Community 52 - "backroom_portals/__init__.py"
Cohesion: 0.18
Nodes (16): 'As of' query predicate (valid_from <= t and valid_to null or > t), Index fact (subject_id, predicate, valid_from desc), Memory schema sketch (entity, episode, fact), backroom_api/memory (schema, writers, supersession, context packer), Table entity (type, name, attrs, optional embedding vector(384), fastembed bge-small P1), Table episode (invoice | approval | rejection | chat | run | seed), Table fact (subject, predicate, object/value, valid_from/valid_to, recorded_at, source_episode, confidence), Memory contract (bitemporal facts, supersession) (+8 more)

### Community 53 - "agent-dock.tsx"
Cohesion: 0.08
Nodes (29): cn@^0.5.2, STEPS, AgentDock(), PlayableRun, PlayingRun(), Ring(), SPRING, TheaterLink() (+21 more)

### Community 54 - "shifts"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 55 - "LLM"
Cohesion: 0.18
Nodes (5): Brief AC: <1.5 s cached, <15 s cold, _timed(), LLMResult, Cost, RoleConfig

### Community 56 - "Candidate"
Cohesion: 0.14
Nodes (18): run_all(), Candidate, good_copy(), plan(), test_template_copy_passes_the_guard_for_every_candidate(), candidates(), data_dir(), numbers() (+10 more)

### Community 57 - "particles.ts"
Cohesion: 0.26
Nodes (12): attachParticleCanvas(), Effect, effects, ensureLoop(), explodeInto(), formFrom(), isDarkTheme(), Particle (+4 more)

### Community 58 - "memory-desk.tsx"
Cohesion: 0.14
Nodes (26): EmptyState(), edgePath(), FactValue(), isoDay(), MemoryDesk(), play(), writeUrl(), plainValue() (+18 more)

### Community 59 - "compilerOptions"
Cohesion: 0.12
Nodes (17): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+9 more)

### Community 60 - "L2: chaos engine with 9 families (laptop/l2-chaos)"
Cohesion: 0.15
Nodes (7): POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Independent audit pass per laptop task (blockers and should-fix items, all fixed), L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline), L2: chaos engine with 9 families (laptop/l2-chaos), L3: TillDesk portal (laptop/l3-tilldesk)

### Community 61 - "test_llm_client.py"
Cohesion: 0.13
Nodes (11): BudgetExceededError, SpendLedger, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict() (+3 more)

### Community 62 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 63 - "totp.py"
Cohesion: 0.23
Nodes (6): code_at(), default_secret(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 64 - "probe.py"
Cohesion: 0.26
Nodes (13): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+5 more)

### Community 65 - "Chaos engine (one chaos_seed per portal, seeded RNG variant catalog)"
Cohesion: 0.14
Nodes (10): Check: DOM-hash test per chaos seed, Q: Why not browser-use / Stagehand, Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), M1 gate (portals usable, DOM-hash determinism, seed loads), Alternative: browser-use / Stagehand, Alternative: Graphiti + FalkorDB / Neo4j, Likely interview questions, Decisions already made (do not re-litigate) (+2 more)

### Community 66 - "xlsx.py"
Cohesion: 0.18
Nodes (4): _column(), rows(), test_xlsx_reader_streams_rows_with_shared_strings(), tiny_xlsx()

### Community 67 - "rendering.py"
Cohesion: 0.17
Nodes (4): fact(), ChaosSeeds, label(), page()

### Community 69 - ".mcp.json"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 70 - "agents.py"
Cohesion: 0.12
Nodes (14): BriefLLMError, candidate_view(), Draft, LLMVerifier, _Model, _parse(), Plan, _system() (+6 more)

### Community 71 - "Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)"
Cohesion: 0.23
Nodes (9): Check: one real LLM call (stop_reason, $, cache_read > 0), Daily LLM budget guard (sums today's ledger rows before each call), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), backroom_api/llm (model registry, client, cost meter, budget guard), pnpm probe:llm (uv run backroom-bench probe), bench/results/provider_probe.json (+1 more)

### Community 72 - "preferences"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 73 - "health.py"
Cohesion: 0.21
Nodes (4): is_configured(), health(), _portals_ok(), _postgres_ok()

### Community 74 - "steps"
Cohesion: 0.12
Nodes (23): name, runs-on, steps, jobs, docs, python, web, name (+15 more)

### Community 75 - "test_contract.py"
Cohesion: 0.16
Nodes (8): pick_variants(), test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ(), test_seed_zero_is_canonical()

### Community 76 - "registry.py"
Cohesion: 0.17
Nodes (5): build_async_client(), Caps, caps_for(), LLMNotConfiguredError, Price

### Community 77 - "Demo Script - 5 minutes"
Cohesion: 0.18
Nodes (17): Beat 0:00 Hook - Today 3 cards, Q: Cloudflare / bot protection on real portals, M3 Memory + Brief + UI, Rehearse demo script 3x on deployed URL, Demo-story prices (DEMO_PRICES_EUR), Demo Script - 5 minutes, Five-minute demo beats (hook, evidence, act, break it, remember, learn, proof, close), Approve all button (+9 more)

### Community 78 - "scripts"
Cohesion: 0.10
Nodes (20): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, scripts, bench (+12 more)

### Community 80 - "backroom_portals/main.py"
Cohesion: 0.15
Nodes (5): get_settings(), Settings, create_app(), client(), make_settings()

### Community 81 - "README - Backroom overview"
Cohesion: 0.18
Nodes (11): Add Live demo + Benchmarks badges to README, Backroom: agentic back office for a cafe (engine under 'Approve all'), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration, JD problem 4: agentic self-improvement, Why this exists: Super44 JD hard problems (+3 more)

### Community 82 - "api"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 83 - "caddy"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 84 - "laptop.md"
Cohesion: 0.15
Nodes (10): Handover update protocol, Sync entry format (Done / Verify / Needs from PC / Notes), Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk) (+2 more)

### Community 86 - "layout.tsx"
Cohesion: 0.19
Nodes (10): geistMono, geistSans, metadata, RootLayout(), viewport, INTRO_KEY, introInitScript, IntroOverlay() (+2 more)

### Community 87 - "portals"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 88 - "postgres"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 89 - "contract.py"
Cohesion: 0.19
Nodes (7): 2. Portals, ChaosRequest, GrainlineState, Label, _Model, testid(), test_testids()

### Community 90 - "record_rejection"
Cohesion: 0.23
Nodes (5): ActionCard, checked(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 91 - "Laptop deviations (L-n log, append-only; PC renumbers on merge)"
Cohesion: 0.13
Nodes (8): DuckDB over Parquet (sales analytics), backroom_api/analytics (DuckDB queries, stockout/margin/weather detectors), data package backroom_data (script backroom-data; raw data not committed), pnpm seed (uv run backroom-data all: download, transform, load Postgres + Parquet), Laptop deviations (L-n log, append-only; PC renumbers on merge), Card: Rainy Saturday (trim shift / Localboard special), L4: data pipeline to Parquet (laptop/l4-data), L6: DuckDB detectors and deterministic pricing (laptop/l6-detectors)

### Community 92 - "shell-extras.tsx"
Cohesion: 0.30
Nodes (8): SceneDriver(), AgentDock, CommandPalette, IntroPlayer, ParticleLayer, ShellExtras(), useCachedBrief(), setRaining()

### Community 93 - "Verify every change"
Cohesion: 0.13
Nodes (15): Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: Lighthouse via web-perf skill, Check: pytest + ruff + pyright for Python logic, Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Verification rules (verify before next step, state evidence), web-perf skill (Lighthouse), CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e) (+7 more)

### Community 94 - "command-palette.tsx"
Cohesion: 0.30
Nodes (8): CommandPalette(), onPaletteOpen(), useCommands(), isDark(), listeners, setDark(), subscribeTheme(), THEME_STORAGE_KEY

### Community 95 - "services"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 96 - "Rules"
Cohesion: 0.11
Nodes (6): L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief), Rules, rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 97 - "rules"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 98 - "depends_on"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 99 - "healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 108 - "json"
Cohesion: 0.24
Nodes (8): LLMPlanner, extract(), _Message, _Result, StubLLM, test_llm_planner_raises_on_unusable_answers(), test_llm_planner_sends_a_cached_structured_request(), test_llm_rewrite_ends_on_a_user_turn()

### Community 109 - "apps_web_src_lib_utils_cn"
Cohesion: 0.27
Nodes (6): Status, Tone, TONE_DOT, fetchHealth(), Health, healthSchema

### Community 110 - "commands.ts"
Cohesion: 0.24
Nodes (8): Command, listeners, openListeners, openPalette(), publish(), registerCommands(), snapshot, sources

### Community 111 - "cafe-pattern.tsx"
Cohesion: 0.36
Nodes (7): CafePattern(), FAR, Glyph, Layer(), NEAR, Tile(), useScene()

### Community 112 - "How this maps to the real Super44 problem"
Cohesion: 0.32
Nodes (6): Beat 4:40 Close - /about, model table, adapters, Shared Action interface to the planner, Memory per merchant + cross-merchant best-practices layer, backroom_api/skills (compiler, replay, healer, registry), Route /about (architecture for the interview), How this maps to the real Super44 problem

## Ambiguous Edges - Review These
- `Card: Reorder oat milk (stock-out, Grainline)` → `Scripted event: oat milk +9% day -3`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **50 isolated node(s):** `backroom-api`, `backroom-bench`, `backroom-data`, `backroom-portals`, `backroom` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 694 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `schema.py` to `Web zod contracts`, `candidate.py`, `gen_fixtures.py`, `Contract`, `Laptop deviations (L-n log, append-only; PC renumbers on merge)`, `test_contract.py`, `CONTRACTS.md`, `laptop.md`, `backroom_portals/__init__.py`, `contract.py`, `M4 Bench + Deploy (Thu 19:00-23:30)`, `L2: chaos engine with 9 families (laptop/l2-chaos)`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `L-45 (L6) Weekly EUR impact defined per card kind; cards ranked by it`) actually correct?**
  _`Candidate` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backroom-api`, `backroom-bench`, `backroom-data` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_memory.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05311250713877784 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `Laptop deviations (L-n log, append-only; PC renumbers on merge)` to `test_memory.py`, `registry.py`, `project.yml`, `dependencies`, `format.ts`, `test_llm_client.py`, `app-shell.tsx`, `M4 Bench + Deploy (Thu 19:00-23:30)`, `api`, `pipeline.py`, `Build Plan (Wed 22:00 -> Fri 11:30 freeze)`, `Portals service (FastAPI + Jinja2, backroom_portals)`, `Decision Log (ADRs + laptop deviations)`, `pnpm-workspace.yaml`, `Handover`, `CONTRACTS.md`, `schema.py`, `backroom_portals/__init__.py`, `LLM`, `L2: chaos engine with 9 families (laptop/l2-chaos)`, `Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)`, `test_contract.py`, `laptop.md`, `Rules`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Card: Reorder oat milk (stock-out, Grainline)` and `Scripted event: oat milk +9% day -3`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._