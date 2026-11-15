# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 182 files · ~101,150 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 9, .lottie 5, .example 1)

## Summary
- 2539 nodes · 6441 edges · 108 communities (95 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 660 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d5bcd1d9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- grainline/routes.py
- test_memory.py
- Web zod contracts
- L5: temporal memory store, writers, context packer (laptop/l5-memory)
- gen_fixtures.py
- action-card.tsx
- Backroom Product Requirements Document
- registry.py
- Contract
- probe.py
- project.yml
- web/package.json
- PlaceholderPage
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
- api-status.tsx
- F2 Run theater (step timeline + live browser stream)
- app-shell.tsx
- grainline/store.py
- M4 Bench + Deploy (Thu 19:00-23:30)
- Demo Script - 5 minutes
- health.py
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
- Backend choices (services/api)
- Backroom Product Requirements Document
- laptop.md
- backroom-api
- pnpm-workspace.yaml
- Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)
- Handover
- CONTRACTS.md
- backroom-portals
- RuntimeError
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
- ADR-9 LLM provider = OpenRouter by default, Anthropic direct as a switch
- candidate.py
- .mcp.json
- agents.py
- Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)
- preferences
- health.py
- steps
- re
- jobs
- Demo Script - 5 minutes
- scripts
- backroom_bench/cli.py
- backroom_portals/main.py
- Build Plan (Wed 22:00 -> Fri 11:30 freeze)
- api
- caddy
- Security notes (talking points)
- duckdb
- L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)
- portals
- postgres
- package.json
- record_rejection
- Laptop deviations (L-n log, append-only; PC renumbers on merge)
- Contracts (L0)
- Verify every change
- services
- Rules
- rules
- depends_on
- healthcheck
- backroom-api
- backroom-data
- pnpm-workspace.yaml
- backroom
- Clock

## God Nodes (most connected - your core abstractions)
1. `Laptop deviations (L-n log, append-only; PC renumbers on merge)` - 77 edges
2. `Candidate` - 60 edges
3. `Backroom Product Requirements Document` - 53 edges
4. `Contract` - 52 edges
5. `react` - 33 edges
6. `LLM` - 30 edges
7. `build()` - 30 edges
8. `Settings` - 29 edges
9. `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)` - 28 edges
10. `generate()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `3. Chaos catalog` --references--> `Look`  [INFERRED]
  docs/CONTRACTS.md → services/portals/backroom_portals/rendering.py
- `Model price table (USD per 1M tokens; kept in llm/registry.py)` --references--> `Price`  [INFERRED]
  docs/ARCHITECTURE.md → services/api/backroom_api/llm/registry.py
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `L-71 (L8) Motion built on the platform (React ViewTransition, CSS/WAAPI keyframes, @number-flow/react) instead of the Motion library` --rationale_for--> `PageTransition()`  [INFERRED]
  docs/DECISIONS.md → apps/web/src/components/motion/page-transition.tsx

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

## Communities (108 total, 13 thin omitted)

### Community 0 - "grainline/routes.py"
Cohesion: 0.10
Nodes (33): Order, OrderLine, _document(), _eur(), invoice_pdf(), _text(), _authed(), cart() (+25 more)

### Community 1 - "test_memory.py"
Cohesion: 0.05
Nodes (46): Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), EpisodeRef, FactDetail, estimate_tokens(), pack(), seeds_for(), _triple(), add_episode() (+38 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (74): zod@^4.6.7, actionCardSchema, approveResponseSchema, briefSchema, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema (+66 more)

### Community 3 - "L5: temporal memory store, writers, context packer (laptop/l5-memory)"
Cohesion: 0.19
Nodes (6): POST /memory/ingest/invoice (PDF/image to extractor to facts), Context packer (memory.packer.pack), Memory writers (assert_fact, write_world, write_invoice), Predicate vocabulary (one-valued, many-valued), Neon hosted Postgres (laptop database), L5: temporal memory store, writers, context packer (laptop/l5-memory)

### Community 4 - "gen_fixtures.py"
Cohesion: 0.12
Nodes (24): L0: shared contracts (laptop/l0-contracts), AskHuman, CostTick, _Event, HealAttempt, HealFailed, HealStarted, HealSucceeded (+16 more)

### Community 5 - "action-card.tsx"
Cohesion: 0.07
Nodes (50): @base-ui/react@^1.9.0, motion@14.9.0, Error(), ActionCard(), approve(), onDragEnd(), onPointerMove(), openReject() (+42 more)

### Community 6 - "Backroom Product Requirements Document"
Cohesion: 0.12
Nodes (29): Decision at 19:00: Localboard / Ask in or out, M1 Data + Portals (Wed 23:00-01:30), B3 ground truth computed by SQL on same data, Data Sources & Honesty Notes, Simulated inventory (opening + deliveries - sales x BOM), Maven Coffee Shop Sales dataset, Maven Analytics 'Coffee Shop Sales' (~149k rows, NYC), Maven source URL (S3 zip, verified 11 Nov) (+21 more)

### Community 7 - "registry.py"
Cohesion: 0.09
Nodes (21): margin_pct(), PriceProposal, propose_price(), round_half_up(), display(), extract(), Found, _matches() (+13 more)

### Community 8 - "Contract"
Cohesion: 0.08
Nodes (26): 7. API shapes, 8. Memory, ActionCard, ApiError, ApproveResponse, Brief, ChaosRequest, ChaosState (+18 more)

### Community 9 - "probe.py"
Cohesion: 0.10
Nodes (16): Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), fact(), chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state() (+8 more)

### Community 10 - "project.yml"
Cohesion: 0.12
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 11 - "web/package.json"
Cohesion: 0.14
Nodes (30): brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier, _Message, _Result (+22 more)

### Community 12 - "PlaceholderPage"
Cohesion: 0.05
Nodes (50): @google/model-viewer@4.4.0, geistMono, geistSans, metadata, RootLayout(), viewport, STEPS, CafeHero() (+42 more)

### Community 13 - "scripts"
Cohesion: 0.08
Nodes (21): SkillVersions, to_sse(), Skill, Step, StepChange, load(), make_skill(), test_brief_has_at_most_three_cards() (+13 more)

### Community 14 - "components.json"
Cohesion: 0.10
Nodes (19): build(), _maven_sales(), next_saturday(), _notes(), built(), cached_weather(), maven_zip(), test_build_is_idempotent() (+11 more)

### Community 15 - "dependencies"
Cohesion: 0.10
Nodes (33): Rule: LLMs never originate numbers, Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, backroom_api/agents (browser agent, planner, verifier, extractor), Worker role (LLM_WORKER_MODEL, Haiku 5.5, low): explore steps, extraction, routing, M3 Memory + Brief + UI (Thu 14:00-19:00), Alternative: Graphiti + FalkorDB / Neo4j (+25 more)

### Community 16 - "format.ts"
Cohesion: 0.11
Nodes (31): useGraph(), Providers(), BadgeSlot(), SampleBadge(), SkillDetail(), SkillsDesk(), Stat(), Stats (+23 more)

### Community 17 - "compilerOptions"
Cohesion: 0.12
Nodes (18): catalog_html(), dom_hash(), forced(), fresh_client(), signed_in(), skill_path_pages(), test_admin_chaos_sets_reads_and_resets_seeds(), test_admin_chaos_validates_and_needs_the_token() (+10 more)

### Community 18 - "test_llm_client.py"
Cohesion: 0.13
Nodes (28): Rule: secrets never reach prompts or logs, Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), M2 Browser agent (Thu 09:00-14:00, riskiest), M2 gate (cold explore seed 0, warm replay <5 s 0 LLM, chaos seed 7 heal -> v2 diff), Why M2 first and fresh: riskiest milestone (+20 more)

### Community 19 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 20 - "client.py"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 21 - "Browser agent"
Cohesion: 0.20
Nodes (29): GrainlineState, has_testid(), login(), state(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove() (+21 more)

### Community 22 - "run-theater.tsx"
Cohesion: 0.06
Nodes (56): metadata, RunPage(), Theater(), Element, ElementView(), FIELD_ROLES, fieldValue(), pageElements() (+48 more)

### Community 23 - "api-status.tsx"
Cohesion: 0.13
Nodes (16): This is NOT the Next.js you know, Charts (Recharts or visx; dataviz skill, palette validator), Frontend (apps/web) choices, Memory graph lib (@xyflow/react or force-graph; benchmark at ~300 nodes), Next.js (App Router, latest stable), TypeScript strict, pnpm, Route /memory, Route /runs/[id] Run theater, Route /skills (+8 more)

### Community 24 - "F2 Run theater (step timeline + live browser stream)"
Cohesion: 0.05
Nodes (46): eslintConfig, dependencies, class-variance-authority@^0.7.1, cn@^0.5.2, @lottiefiles/dotlottie-react@0.21.0, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0 (+38 more)

### Community 25 - "app-shell.tsx"
Cohesion: 0.11
Nodes (32): CardStatus, BriefCommands(), BriefSkeleton(), COUNT_WORDS, decisions(), TodayBrief(), approveAll(), approveOne() (+24 more)

### Community 26 - "grainline/store.py"
Cohesion: 0.16
Nodes (9): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), next_weekday(), price_on(), PriceEvent, Product, seeded_orders(), SeedLine, SeedOrder (+1 more)

### Community 27 - "M4 Bench + Deploy (Thu 19:00-23:30)"
Cohesion: 0.18
Nodes (10): concurrency, cancel-in-progress, group, name, on, pull_request, push, permissions (+2 more)

### Community 28 - "Demo Script - 5 minutes"
Cohesion: 0.11
Nodes (29): Rule: all LLM access through llm/registry.py, Beat 4:40 Close - /about, model table, adapters, Q: Cost at scale, Shared Action interface to the planner, Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), LLM_<ROLE>_EFFORT override, LLM_PROVIDER env var (openrouter default | anthropic), Memory per merchant + cross-merchant best-practices layer (+21 more)

### Community 29 - "health.py"
Cohesion: 0.12
Nodes (6): Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Label, label(), Look, page(), test_every_label_has_three_forms_and_a_german_one()

### Community 30 - "api"
Cohesion: 0.10
Nodes (26): nextConfig, next@16.4.6, AboutPage(), Chapter(), LADDER, metadata, MODELS, BENCHMARKS (+18 more)

### Community 31 - "pipeline.py"
Cohesion: 0.10
Nodes (25): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), CardCopy, Planner, action_id(), brief_for_today(), BriefResult, _copy_for() (+17 more)

### Community 32 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.15
Nodes (17): Langfuse Cloud Hobby traces (P1), Sentry free tier errors (P1), Code freeze Fri 13 Nov 11:30, Build Plan (Wed 22:00 -> Fri 11:30 freeze), M0 Foundations, M1 Data + Portals, M2 Browser agent (riskiest), Break it: chaos seed 7 heal beat (+9 more)

### Community 33 - "portals"
Cohesion: 0.14
Nodes (12): apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days(), synthetic() (+4 more)

### Community 34 - "postgres"
Cohesion: 0.14
Nodes (11): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+3 more)

### Community 35 - "TillDeskStore"
Cohesion: 0.19
Nodes (3): MenuItem, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 36 - "scripts"
Cohesion: 0.16
Nodes (10): connect(), Context, _ingredient(), margin_erosion(), _n(), _shown(), stockout(), weather_demand() (+2 more)

### Community 37 - "Portals service (FastAPI + Jinja2, backroom_portals)"
Cohesion: 0.17
Nodes (16): dataviz skill (before any chart), Frontend quality bar (Lighthouse >= 90, reduced motion), apps/web/src/styles/tokens.css, ui-ux-pro-max skill, Lightsail snapshot before final deploy (2-minute rollback), Route / Today, UI kit: Tailwind v4, shadcn/ui, Motion, lucide icons, cmdk, Code freeze Fri 13 Nov 11:30 (snapshot, no deploys) (+8 more)

### Community 38 - "services"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 39 - "Why this exists: Super44 JD hard problems"
Cohesion: 0.09
Nodes (24): build_async_client(), canonical_model_id(), Caps, caps_for(), cost_usd(), is_configured(), LLMNotConfiguredError, Price (+16 more)

### Community 40 - "depends_on"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 41 - "healthcheck"
Cohesion: 0.20
Nodes (19): Backroom Technical Architecture, Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), Deploy freeze: no deploys after Fri 11:30, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), FastAPI api service (orchestrator, agents, memory, SSE/WS), Hosting fallback (Hetzner CX22 / Fly.io with the same compose file), Hosting and operations (cheap, reliable) (+11 more)

### Community 42 - "Backend choices (services/api)"
Cohesion: 0.10
Nodes (17): Q: Why not browser-use / Stagehand, Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, CDP Page.startScreencast live frames, Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test), GHCR container registry, infra/ (docker-compose.yml, Caddyfile, deploy.sh, Lightsail notes) (+9 more)

### Community 43 - "Backroom Product Requirements Document"
Cohesion: 0.10
Nodes (25): Add Live demo + Benchmarks badges to README, Open or synthetic data only ('Synthetic' chip in UI), Action card (impact, why, evidence chips, Approve/Review/Not now), B2 Learning curve, B4 Model swap (P1), Backroom: agentic back office for a cafe (engine under 'Approve all'), Brief AC: <1.5 s cached, <15 s cold, Backroom Product Requirements Document (+17 more)

### Community 44 - "laptop.md"
Cohesion: 0.17
Nodes (8): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 45 - "backroom-api"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 46 - "pnpm-workspace.yaml"
Cohesion: 0.13
Nodes (27): Rule: every LLM call through cost meter + budget guard, Beat 4:00 Proof - /bench, Route /bench, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), Milestone gate rule (don't start next until gate passes or scope cut logged), Record golden runs -> replay mode, M3 gate (full DEMO_SCRIPT works locally end-to-end) (+19 more)

### Community 47 - "Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)"
Cohesion: 0.19
Nodes (13): CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, claude-api skill (load before Anthropic SDK code), context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path), Session read order (HANDOVER, BUILD_PLAN, GRAPH_REPORT) (+5 more)

### Community 48 - "Handover"
Cohesion: 0.11
Nodes (19): Decision Log (ADRs + laptop deviations), Handover, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13, Neon hosted Postgres for the laptop, PC tasks H1-H9 (+11 more)

### Community 49 - "CONTRACTS.md"
Cohesion: 0.10
Nodes (27): Key API routes, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), POST /ask (SSE answer with tool calls + citations, P1), GET /memory/facts/{id} (fact + provenance), POST /actions/{id}/reject ({reason} to preference episode), Portals admin API (/_admin/chaos, state, reset), API shapes (contracts/api.py), Brief pipeline (stream_today, BriefResult) (+19 more)

### Community 50 - "backroom-portals"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 51 - "RuntimeError"
Cohesion: 0.16
Nodes (18): Stack and commands, docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), backroom_api/memory (schema, writers, supersession, context packer), backroom_api/replay (golden-run recorder & player), Root package.json (pnpm workspace root + task runner), data package backroom_data (script backroom-data; raw data not committed), pnpm dev (Postgres in Docker + api + portals + next dev in parallel), pnpm dev:lite (api, portals, web without Docker or a database; API reports degraded) (+10 more)

### Community 52 - "backroom_portals/__init__.py"
Cohesion: 0.20
Nodes (15): 'As of' query predicate (valid_from <= t and valid_to null or > t), Index fact (subject_id, predicate, valid_from desc), Memory schema sketch (entity, episode, fact), Table entity (type, name, attrs, optional embedding vector(384), fastembed bge-small P1), Table episode (invoice | approval | rejection | chat | run | seed), Table fact (subject, predicate, object/value, valid_from/valid_to, recorded_at, source_episode, confidence), Memory contract (bitemporal facts, supersession), entity (+7 more)

### Community 53 - "agent-dock.tsx"
Cohesion: 0.08
Nodes (32): SceneDriver(), AgentDock(), PlayableRun, PlayingRun(), Ring(), SPRING, TheaterLink(), AgentDock (+24 more)

### Community 54 - "shifts"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 55 - "LLM"
Cohesion: 0.24
Nodes (4): LLM, LLMResult, Cost, RoleConfig

### Community 56 - "Candidate"
Cohesion: 0.17
Nodes (15): run_all(), Candidate, test_template_copy_passes_the_guard_for_every_candidate(), candidates(), data_dir(), numbers(), test_a_date_the_data_was_not_built_for_is_refused(), test_all_three_detectors_fire() (+7 more)

### Community 57 - "particles.ts"
Cohesion: 0.26
Nodes (12): attachParticleCanvas(), Effect, effects, ensureLoop(), explodeInto(), formFrom(), isDarkTheme(), Particle (+4 more)

### Community 58 - "memory-desk.tsx"
Cohesion: 0.08
Nodes (42): @number-flow/react@0.6.2, EmptyState(), edgePath(), FactValue(), isoDay(), MemoryDesk(), play(), writeUrl() (+34 more)

### Community 59 - "compilerOptions"
Cohesion: 0.12
Nodes (17): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+9 more)

### Community 60 - "L2: chaos engine with 9 families (laptop/l2-chaos)"
Cohesion: 0.14
Nodes (8): POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Sync entry format (Done / Verify / Needs from PC / Notes), Independent audit pass per laptop task (blockers and should-fix items, all fixed), L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline), L2: chaos engine with 9 families (laptop/l2-chaos), L3: TillDesk portal (laptop/l3-tilldesk)

### Community 61 - "test_llm_client.py"
Cohesion: 0.11
Nodes (12): BudgetExceededError, CallRecord, SpendLedger, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling() (+4 more)

### Community 62 - "Handover — read this first on a new machine or in a new session"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 63 - "totp.py"
Cohesion: 0.23
Nodes (6): code_at(), default_secret(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 64 - "probe.py"
Cohesion: 0.32
Nodes (12): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+4 more)

### Community 65 - "Chaos engine (one chaos_seed per portal, seeded RNG variant catalog)"
Cohesion: 0.24
Nodes (6): Check: DOM-hash test per chaos seed, DuckDB over Parquet (sales analytics), backroom_api/analytics (DuckDB queries, stockout/margin/weather detectors), Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), M1 gate (portals usable, DOM-hash determinism, seed loads), Chaos toggle (seed picker)

### Community 67 - "ADR-9 LLM provider = OpenRouter by default, Anthropic direct as a switch"
Cohesion: 0.31
Nodes (6): LLM_CAPS_OFF (switch capability flags off), OpenRouter ~5.5% credit fee (OPENROUTER_FEE_PCT), Provider openrouter (default; base_url openrouter.ai/api, auth_token, X-Title/HTTP-Referer headers), Alternative: OpenAI-compatible OpenRouter API (second code path), L10: LLM capability probe on OpenRouter (laptop/l10-llm-probe), probe:llm

### Community 69 - ".mcp.json"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 70 - "agents.py"
Cohesion: 0.10
Nodes (18): L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief), BriefLLMError, candidate_view(), LLMPlanner, LLMVerifier, _Model, _parse(), Plan (+10 more)

### Community 71 - "Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)"
Cohesion: 0.14
Nodes (10): Check: one real LLM call (stop_reason, $, cache_read > 0), Daily LLM budget guard (sums today's ledger rows before each call), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), backroom_api/llm (model registry, client, cost meter, budget guard), Operational guards (daily LLM budget cap, per-IP rate limit, DEMO_ACCESS_CODE, CORS to Vercel domain), pnpm probe:llm (uv run backroom-bench probe) (+2 more)

### Community 72 - "preferences"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 73 - "health.py"
Cohesion: 0.21
Nodes (3): health(), _portals_ok(), _postgres_ok()

### Community 74 - "steps"
Cohesion: 0.24
Nodes (13): steps, steps, id, if, name, run, uses, with (+5 more)

### Community 75 - "re"
Cohesion: 0.19
Nodes (7): 2. Portals, testid(), test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_routes_are_unique_and_under_one_prefix(), test_seed_zero_is_canonical(), test_testids()

### Community 76 - "jobs"
Cohesion: 0.20
Nodes (10): name, runs-on, jobs, docs, python, web, name, runs-on (+2 more)

### Community 77 - "Demo Script - 5 minutes"
Cohesion: 0.11
Nodes (28): Rule: fictional names only; no Super44 branding in UI, Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, M3 Memory + Brief + UI, Rehearse demo script 3x on deployed URL, TillDesk may slip to Thu 08:00, Demo-story prices (DEMO_PRICES_EUR), Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg) (+20 more)

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (12): scripts, bench, check, check:py, dev, dev:api, dev:db, dev:lite (+4 more)

### Community 80 - "backroom_portals/main.py"
Cohesion: 0.11
Nodes (5): main(), get_settings(), Settings, create_app(), client()

### Community 81 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.16
Nodes (14): Q: Cloudflare / bot protection on real portals, Q: What breaks first in production, Agent-cursor overlay / halo, F2 Run theater, Human handoff (ask_human: CAPTCHA, 2FA, ambiguity), Idempotency key on approve (no double orders), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works (+6 more)

### Community 82 - "api"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 83 - "caddy"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 84 - "Security notes (talking points)"
Cohesion: 0.29
Nodes (3): Navigation domain allowlist per run, POST /actions/{id}/approve (Idempotency-Key header to run_id), Security notes (talking points)

### Community 86 - "L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)"
Cohesion: 0.40
Nodes (3): exclude, include, check:web

### Community 87 - "portals"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 88 - "postgres"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 89 - "package.json"
Cohesion: 0.25
Nodes (8): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, version, concurrently

### Community 90 - "record_rejection"
Cohesion: 0.24
Nodes (4): checked(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 91 - "Laptop deviations (L-n log, append-only; PC renumbers on merge)"
Cohesion: 0.16
Nodes (3): Laptop deviations (L-n log, append-only; PC renumbers on merge), L4: data pipeline to Parquet (laptop/l4-data), L6: DuckDB detectors and deterministic pricing (laptop/l6-detectors)

### Community 92 - "Contracts (L0)"
Cohesion: 0.40
Nodes (5): 1. Changing a contract, 3. Chaos catalog, 4. Skills, 9. Fixtures and the drift check, Contracts (L0)

### Community 93 - "Verify every change"
Cohesion: 0.12
Nodes (15): Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: Lighthouse via web-perf skill, Check: pytest + ruff + pyright for Python logic, Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Verification rules (verify before next step, state evidence), web-perf skill (Lighthouse), CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e) (+7 more)

### Community 95 - "services"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 96 - "Rules"
Cohesion: 0.09
Nodes (11): Draft, Verdict, Verifier, _rules_note(), _verify(), Preference, Rules, rules_from_memory() (+3 more)

### Community 97 - "rules"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 98 - "depends_on"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 99 - "healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

## Ambiguous Edges - Review These
- `Card: Reorder oat milk (stock-out, Grainline)` → `Scripted event: oat milk +9% day -3`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **50 isolated node(s):** `backroom-api`, `backroom-bench`, `backroom-data`, `backroom-portals`, `backroom` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 691 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `gen_fixtures.py` to `Web zod contracts`, `L5: temporal memory store, writers, context packer (laptop/l5-memory)`, `candidate.py`, `Contract`, `M4 Bench + Deploy (Thu 19:00-23:30)`, `probe.py`, `CONTRACTS.md`, `backroom_portals/__init__.py`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `Laptop deviations (L-n log, append-only; PC renumbers on merge)`, `L2: chaos engine with 9 families (laptop/l2-chaos)`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `L-45 (L6) Weekly EUR impact defined per card kind; cards ranked by it`) actually correct?**
  _`Candidate` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backroom-api`, `backroom-bench`, `backroom-data` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `grainline/routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09814563545906829 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `Laptop deviations (L-n log, append-only; PC renumbers on merge)` to `L5: temporal memory store, writers, context packer (laptop/l5-memory)`, `gen_fixtures.py`, `action-card.tsx`, `Backroom Product Requirements Document`, `Contract`, `project.yml`, `dependencies`, `format.ts`, `test_llm_client.py`, `api`, `pipeline.py`, `Portals service (FastAPI + Jinja2, backroom_portals)`, `pnpm-workspace.yaml`, `Handover`, `CONTRACTS.md`, `backroom_portals/__init__.py`, `memory-desk.tsx`, `L2: chaos engine with 9 families (laptop/l2-chaos)`, `Chaos engine (one chaos_seed per portal, seeded RNG variant catalog)`, `ADR-9 LLM provider = OpenRouter by default, Anthropic direct as a switch`, `agents.py`, `Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id)`, `Build Plan (Wed 22:00 -> Fri 11:30 freeze)`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `Verify every change`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Card: Reorder oat milk (stock-out, Grainline)` and `Scripted event: oat milk +9% day -3`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._