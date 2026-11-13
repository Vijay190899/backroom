# Graph Report - backroom laptop work  (2026-11-13)

## Corpus Check
- 158 files · ~74,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2172 nodes · 5271 edges · 94 communities (81 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 519 edges (avg confidence: 0.89)
- Token cost: 188,983 input · 0 output

## Community Hubs (Navigation)
- Temporal memory store
- Grainline TOTP and auth
- Web zod contracts
- LLM non-negotiables and adapters
- Web lint and dependencies
- Brief planner and candidates
- Memory design and staleness
- Stack, infra and CI
- Milestones and scope decisions
- Demo beats and chaos story
- Invoice PDF rendering
- Brief pipeline tests
- LLM planner agents
- Grainline portal templates
- Web root layout and fonts
- CI workflow
- Today action card UI
- Recipes data
- Demo evidence and memory beats
- TillDesk price editing
- Detectors
- Skills contract schema
- API response shapes
- Model registry and providers
- DuckDB analytics connect
- LLM client wrapper
- Today page and brief
- UI checks and chaos catalog
- Serena project config
- Verification rules
- Sales data transform
- External data sources
- Data pipeline tests
- Portals contract models
- Run theater and safety Q&A
- Ops guards and replay
- Number guard
- Portal rendering helpers
- Root package scripts
- Run event types
- Cost meter and budget
- shadcn components config
- CLI entry points
- Contract base models
- Grainline order store
- Next config and routes
- API settings and DB pool
- TillDesk routes
- TypeScript config
- Contracts and memory writers
- Service settings
- Chaos variant catalog
- Portals admin API
- Inventory world sim
- Staff rota data
- Frontend quality bar
- LLM capability probe
- Handover setup
- Hosting and ADRs
- Contract process and detectors
- Grainline catalog prices
- Agent rules and chaos deviations
- Two-machine workflow
- MCP server config
- XLSX reader
- Owner preferences rules
- Preferences data
- Preference extractor
- Health route
- Spend ledger
- Compose API service
- Compose portals service
- Parquet writer
- Compose build config
- Compose Postgres service
- Memory SQL schema
- Contract sections
- Compose root
- Product map
- Laptop sync log
- Context packer
- Compose dependencies
- Compose healthcheck
- Fixture clock
- Web agent rules
- SSE serialisation
- API and bench packages
- Data and portals packages
- pnpm workspace
- Root package

## God Nodes (most connected - your core abstractions)
1. `Candidate` - 58 edges
2. `Backroom Product Requirements Document` - 54 edges
3. `Decision Log (ADRs)` - 54 edges
4. `Contract` - 52 edges
5. `Backroom Technical Architecture` - 34 edges
6. `build()` - 30 edges
7. `LLM` - 30 edges
8. `Settings` - 29 edges
9. `generate()` - 26 edges
10. `FakePlanner` - 25 edges

## Surprising Connections (you probably didn't know these)
- `3. Chaos catalog` --references--> `Look`  [INFERRED]
  docs/CONTRACTS.md → services/portals/backroom_portals/rendering.py
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)` --references--> `Look`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/rendering.py
- `Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)` --references--> `TillDeskState`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/contract.py

## Import Cycles
- 2-file cycle: `services/portals/backroom_portals/config.py -> services/portals/backroom_portals/totp.py -> services/portals/backroom_portals/config.py`

## Hyperedges (group relationships)
- **Brief flow: detectors compute, planner writes, verifier checks, number guard verifies** — docs_contracts_detectors, docs_contracts_candidate, docs_contracts_brief_pipeline, docs_decisions_l_58_verifier_keep_or_veto, docs_contracts_number_guard_rules, docs_decisions_adr_5_agents_judgment_code_math [INFERRED 0.85]
- **Self-healing skill loop under chaos seed 7** — docs_prd_f3_skill_learning_healing, docs_architecture_escalation_ladder, docs_contracts_skill_versioning_heal, docs_contracts_skill_diff, docs_decisions_l_6_heal_semantics, docs_decisions_l_16_seed_7_pinned, docs_demo_script_break_it_seed_7_heal [INFERRED 0.85]
- **Two-machine contract-first coordination** — docs_decisions_adr_15_two_machine_workflow, docs_handover_work_split, docs_handover_ownership_table, docs_contracts_contract_change_process, docs_sync_laptop, docs_sync_pc [INFERRED 0.85]
- **Chaos-aware rendering primitives shared by all portals** — services_portals_backroom_portals_templates_macros_wrap, services_portals_backroom_portals_templates_macros_submit, services_portals_backroom_portals_templates_macros_field, services_portals_backroom_portals_templates_macros_nav, services_portals_backroom_portals_templates_macros_interstitial, services_portals_backroom_portals_templates_macros_chaos_js, services_portals_backroom_portals_templates_macros_look_chaos_object [EXTRACTED 1.00]
- **Grainline ordering flow pages** — services_portals_backroom_portals_templates_grainline_catalog, services_portals_backroom_portals_templates_grainline_cart, services_portals_backroom_portals_templates_grainline_checkout, services_portals_backroom_portals_templates_grainline_order, services_portals_backroom_portals_templates_grainline_invoices [INFERRED 0.95]
- **TillDesk price change and publish flow** — services_portals_backroom_portals_templates_tilldesk_login, services_portals_backroom_portals_templates_tilldesk_menu, services_portals_backroom_portals_templates_tilldesk_edit, services_portals_backroom_portals_templates_tilldesk_menu_draft_publish_flow [INFERRED 0.95]
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — docs_prd_detectors, docs_prd_candidate, docs_prd_planner, docs_prd_verifier, docs_prd_number_guard, docs_architecture_route_brief_today [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — docs_prd_explore_mode, docs_prd_skill_compiler, docs_prd_replay_engine, docs_prd_heal_ladder, docs_prd_skill_versioning, docs_architecture_escalation_ladder [EXTRACTED 1.00]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — docs_prd_franzbroetchen_story, docs_architecture_route_reject, docs_prd_episodes, docs_prd_extractor, docs_prd_preference_fact, docs_prd_verifier, demo_beat_learn_owner [INFERRED 0.85]

## Communities (94 total, 13 thin omitted)

### Community 0 - "Temporal memory store"
Cohesion: 0.05
Nodes (52): 8. Memory, Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, ContextPack, EpisodeRef, FactDetail, GraphNode, MemoryGraph (+44 more)

### Community 1 - "Grainline TOTP and auth"
Cohesion: 0.07
Nodes (52): code_at(), now_code(), verify(), catalog_html(), dom_hash(), forced(), fresh_client(), signed_in() (+44 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (68): actionCardSchema, briefSchema, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema, ChaosState, chaosStateSchema (+60 more)

### Community 3 - "LLM non-negotiables and adapters"
Cohesion: 0.08
Nodes (49): Check: one real LLM call (stop_reason, $, cache_read > 0), Rule: every LLM call through cost meter + budget guard, Rule: all LLM access through llm/registry.py, Beat 4:40 Close - /about, model table, adapters, Shared Action interface to the planner, Adapter strategy: API-first, browser skills for long tail, Backend stack (FastAPI, Postgres+pgvector, DuckDB, Playwright), Canonical model IDs mapped per provider (slash IDs pass through) (+41 more)

### Community 4 - "Web lint and dependencies"
Cohesion: 0.05
Nodes (49): eslintConfig, dependencies, @base-ui/react@^1.9.0, class-variance-authority@^0.7.1, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0, shadcn@^4.23.0 (+41 more)

### Community 5 - "Brief planner and candidates"
Cohesion: 0.09
Nodes (25): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), Planner, Verifier, action_id(), brief_for_today(), BriefResult, _copy_for() (+17 more)

### Community 6 - "Memory design and staleness"
Cohesion: 0.08
Nodes (50): Rule: LLMs never originate numbers, Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Q: How does memory avoid going stale, 'As of' query predicate, Key API routes, Memory schema sketch (entity, episode, fact), backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/memory (schema, writers, supersession, context packer) (+42 more)

### Community 7 - "Stack, infra and CI"
Cohesion: 0.08
Nodes (51): Stack and commands, Browser pool (1 Chromium, 2 contexts, queue), Caddy (TLS + routing, sslip.io auto-HTTPS), CI: GitHub Actions (lint, typecheck, unit, compose e2e), infra/deploy.sh (ssh, pull, compose up, health, smoke), infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), DuckDB / Parquet (sales analytics), FastAPI api service (orchestrator, agents, memory, SSE/WS) (+43 more)

### Community 8 - "Milestones and scope decisions"
Cohesion: 0.08
Nodes (43): Rule: fictional names only; no Super44 branding in UI, POST /ask (SSE, P1), Decision at 19:00: Localboard / Ask in or out, M1 Data + Portals (Wed 23:00-01:30), M1 Data + Portals, TillDesk may slip to Thu 08:00, B3 ground truth computed by SQL on same data, Data Sources & Honesty Notes (+35 more)

### Community 9 - "Demo beats and chaos story"
Cohesion: 0.07
Nodes (49): Rule: secrets never reach prompts or logs, Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Q: Cost at scale, Q: Why not browser-use / Stagehand, Backend choices table, Chaos variant families (labels EN/DE, DOM order, interstitials, delays, moved nav) (+41 more)

### Community 10 - "Invoice PDF rendering"
Cohesion: 0.17
Nodes (29): _document(), _eur(), invoice_pdf(), _text(), _authed(), cart(), cart_add(), cart_update() (+21 more)

### Community 11 - "Brief pipeline tests"
Cohesion: 0.14
Nodes (30): brief(), conn(), data_dir(), FakePlanner, FakeVerifier, _Message, _Result, rule() (+22 more)

### Community 12 - "LLM planner agents"
Cohesion: 0.09
Nodes (23): BriefLLMError, candidate_view(), CardCopy, Draft, LLMPlanner, LLMVerifier, _Model, _parse() (+15 more)

### Community 13 - "Grainline portal templates"
Cohesion: 0.13
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 14 - "Web root layout and fonts"
Cohesion: 0.10
Nodes (27): geistMono, geistSans, instrumentSerif, metadata, RootLayout(), viewport, Providers(), ApiStatus() (+19 more)

### Community 15 - "CI workflow"
Cohesion: 0.07
Nodes (33): concurrency, cancel-in-progress, group, name, runs-on, steps, jobs, docs (+25 more)

### Community 16 - "Today action card UI"
Cohesion: 0.11
Nodes (26): cn@^0.5.2, ActionCard(), CardStatus, KIND, PORTAL, EvidenceDrawer(), EvidenceItem(), KIND_ICON (+18 more)

### Community 17 - "Recipes data"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 18 - "Demo evidence and memory beats"
Cohesion: 0.09
Nodes (31): Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Beat 2:40 Remember - time slider, butter fact superseded, Portal patterns (login->TOTP->dashboard, cart, checkout, PDF invoices), GET /memory/facts/{id}, Rehearse demo script 3x on deployed URL, Demo-story prices (DEMO_PRICES_EUR), Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg) (+23 more)

### Community 19 - "TillDesk price editing"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 20 - "Detectors"
Cohesion: 0.12
Nodes (16): Context, _ingredient(), margin_erosion(), _n(), _shown(), stockout(), weather_demand(), margin_pct() (+8 more)

### Community 21 - "Skills contract schema"
Cohesion: 0.11
Nodes (17): Step, StepChange, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step(), test_margin_card_numbers_match_the_demo_story() (+9 more)

### Community 22 - "API response shapes"
Cohesion: 0.09
Nodes (15): 7. API shapes, ApiError, ApproveResponse, ChaosRequest, ChaosState, ErrorResponse, GraphFact, HumanReply (+7 more)

### Community 23 - "Model registry and providers"
Cohesion: 0.10
Nodes (21): build_async_client(), canonical_model_id(), cost_usd(), is_configured(), LLMNotConfiguredError, role_config(), wire_model_id(), make_settings() (+13 more)

### Community 24 - "DuckDB analytics connect"
Cohesion: 0.13
Nodes (17): connect(), run_all(), Candidate, candidates(), test_template_copy_passes_the_guard_for_every_candidate(), candidates(), data_dir(), numbers() (+9 more)

### Community 25 - "LLM client wrapper"
Cohesion: 0.14
Nodes (9): LLM, LLMResult, CallRecord, Caps, caps_for(), Cost, Price, RoleConfig (+1 more)

### Community 26 - "Today page and brief"
Cohesion: 0.13
Nodes (22): TodayPage(), PageHeader(), CardSkeleton(), TodayBrief(), approveAll(), approveOne(), rejectOne(), setOne() (+14 more)

### Community 27 - "UI checks and chaos catalog"
Cohesion: 0.12
Nodes (26): Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Beat 4:00 Proof - /bench, Mock portals and chaos engine, Langfuse Cloud Hobby traces (P1), pnpm e2e (Playwright e2e 390/1440 px), Sentry free tier (P1), Chaos catalog (nine variant families), Portal labels (en, en_alt, de) (+18 more)

### Community 28 - "Serena project config"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 29 - "Verification rules"
Cohesion: 0.11
Nodes (22): CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: DOM-hash test per chaos seed, Check: Lighthouse via web-perf skill, Check: pytest + ruff + pyright for Python logic, claude-api skill (load before Anthropic SDK code) (+14 more)

### Community 30 - "Sales data transform"
Cohesion: 0.14
Nodes (12): apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days(), synthetic() (+4 more)

### Community 31 - "External data sources"
Cohesion: 0.14
Nodes (10): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+2 more)

### Community 32 - "Data pipeline tests"
Cohesion: 0.14
Nodes (15): built(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table(), test_cached_weather_and_nager_holidays_are_used(), test_corrupt_cached_download_falls_back_to_synthetic(), test_inventory_covers_only_the_order_window() (+7 more)

### Community 33 - "Portals contract models"
Cohesion: 0.13
Nodes (8): 2. Portals, ChaosRequest, GrainlineState, MenuItem, _Model, TillDeskState, TillDeskStore, test_tilldesk_state_is_addressable_by_item_id()

### Community 34 - "Run theater and safety Q&A"
Cohesion: 0.11
Nodes (24): Rule: mock portals only; no bot-protection evasion, Q: Cloudflare / bot protection on real portals, Q: What breaks first in production, CDP Page.startScreencast live frames, POST /actions/{id}/approve (Idempotency-Key), POST /chaos {portal, seed}, WebSocket JPEG frames + cursor coords, ADR-1 Mock portals instead of real sites (+16 more)

### Community 35 - "Ops guards and replay"
Cohesion: 0.11
Nodes (22): backroom_api/llm (model registry, client, cost meter, budget guard), backroom_api/replay (golden-run recorder & player), Operational guards (budget cap, rate limit, DEMO_ACCESS_CODE, CORS), Ops guards (budget cap, rate limit, DEMO_ACCESS_CODE, CORS), Code freeze Fri 13 Nov 11:30, Build Plan (Wed 22:00 -> Fri 11:30 freeze), Record golden runs -> replay mode, M2 Browser agent (riskiest) (+14 more)

### Community 36 - "Number guard"
Cohesion: 0.15
Nodes (14): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), copy_for() (+6 more)

### Community 37 - "Portal rendering helpers"
Cohesion: 0.12
Nodes (6): fact(), testid(), label(), Look, page(), test_testids()

### Community 38 - "Root package scripts"
Cohesion: 0.09
Nodes (22): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, scripts, bench (+14 more)

### Community 39 - "Run event types"
Cohesion: 0.17
Nodes (16): AskHuman, CostTick, _Event, GoldenFrame, HealAttempt, HealFailed, HealStarted, HealSucceeded (+8 more)

### Community 40 - "Cost meter and budget"
Cohesion: 0.16
Nodes (9): BudgetExceededError, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict(), test_create_sends_wire_model_and_effort_and_records_cost() (+1 more)

### Community 41 - "shadcn components config"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 42 - "CLI entry points"
Cohesion: 0.14
Nodes (6): main(), build(), main(), _maven_sales(), next_saturday(), _notes()

### Community 43 - "Contract base models"
Cohesion: 0.15
Nodes (14): SkillVersions, Contract, Cursor, FrameMeta, CssFallback, Expect, LabelFallback, Locator (+6 more)

### Community 44 - "Grainline order store"
Cohesion: 0.19
Nodes (4): Order, OrderLine, GrainlineStore, Session

### Community 45 - "Next config and routes"
Cohesion: 0.18
Nodes (14): nextConfig, next@16.4.6, AboutPage(), metadata, BenchPage(), metadata, MemoryPage(), metadata (+6 more)

### Community 46 - "API settings and DB pool"
Cohesion: 0.15
Nodes (8): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 47 - "TillDesk routes"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 48 - "TypeScript config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+11 more)

### Community 49 - "Contracts and memory writers"
Cohesion: 0.14
Nodes (16): Security notes (vault, allowlist, idempotency), SSE run events + WebSocket JPEG frames, Portals admin API (/_admin/chaos, state, reset), Memory writers (assert_fact, write_world, write_invoice), pick_variants(portal, seed), Portals contract (one service, three path prefixes), Skill postconditions (url_matches, text_visible, portal_state), Predicate vocabulary (one-valued, many-valued) (+8 more)

### Community 50 - "Service settings"
Cohesion: 0.15
Nodes (4): get_settings(), Settings, create_app(), default_secret()

### Community 51 - "Chaos variant catalog"
Cohesion: 0.14
Nodes (9): pick_variants(), Label, test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 52 - "Portals admin API"
Cohesion: 0.19
Nodes (8): chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosState, ChaosSeeds

### Community 53 - "Inventory world sim"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 54 - "Staff rota data"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 55 - "Frontend quality bar"
Cohesion: 0.14
Nodes (17): dataviz skill (before any chart), Frontend quality bar (Lighthouse >= 90, reduced motion), apps/web/src/styles/tokens.css, ui-ux-pro-max skill, Charts (Recharts or visx, dataviz skill), Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query), Memory graph lib (@xyflow/react or force-graph), Route /memory (+9 more)

### Community 56 - "LLM capability probe"
Cohesion: 0.29
Nodes (12): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+4 more)

### Community 57 - "Handover setup"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 58 - "Hosting and ADRs"
Cohesion: 0.20
Nodes (5): Deploy flow (GHCR images, deploy.sh, snapshot), Hosting and operations (Vercel Hobby, Lightsail 2 GB, Caddy sslip.io), Decision Log (ADRs), Likely interview questions, Decisions already made (do not re-litigate)

### Community 59 - "Contract process and detectors"
Cohesion: 0.16
Nodes (12): Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Fixtures and the drift check, analytics.pricing.propose_price, Handover update protocol, Sync entry format (Done, Verify, Needs from PC, Notes), L0 contracts sync entry, L1 Grainline portal sync entry (+4 more)

### Community 60 - "Grainline catalog prices"
Cohesion: 0.22
Nodes (9): Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), next_weekday(), price_on(), PriceEvent, Product, seeded_orders(), SeedLine, SeedOrder (+1 more)

### Community 61 - "Agent rules and chaos deviations"
Cohesion: 0.21
Nodes (7): Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Brief pipeline (stream_today, BriefResult), Detector Candidate, Number guard rules 1-9, Laptop deviations (L-n log), L2 chaos engine sync entry, L7 brief pipeline sync entry

### Community 62 - "Two-machine workflow"
Cohesion: 0.22
Nodes (11): Handover, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13, Neon hosted Postgres for the laptop, PC tasks H1-H9, Suggested order and critical path (+3 more)

### Community 63 - "MCP server config"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 64 - "XLSX reader"
Cohesion: 0.18
Nodes (4): _column(), rows(), test_xlsx_reader_streams_rows_with_shared_strings(), tiny_xlsx()

### Community 65 - "Owner preferences rules"
Cohesion: 0.19
Nodes (4): rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 66 - "Preferences data"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 67 - "Preference extractor"
Cohesion: 0.23
Nodes (5): ActionCard, checked(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 68 - "Health route"
Cohesion: 0.25
Nodes (3): health(), _portals_ok(), _postgres_ok()

### Community 70 - "Compose API service"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 71 - "Compose portals service"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 73 - "Compose build config"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 74 - "Compose Postgres service"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 75 - "Memory SQL schema"
Cohesion: 0.42
Nodes (8): entity, episode, episode_kind_idx, fact, fact_episode_idx, fact_object_idx, fact_open_idx, fact_subject_predicate_idx

### Community 76 - "Contract sections"
Cohesion: 0.29
Nodes (7): RunEvent, 1. Changing a contract, 3. Chaos catalog, 4. Skills, 5. Run events, 9. Fixtures and the drift check, Contracts (L0)

### Community 77 - "Compose root"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 78 - "Product map"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 79 - "Laptop sync log"
Cohesion: 0.33
Nodes (6): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)

### Community 80 - "Context packer"
Cohesion: 0.40
Nodes (3): Context packer (memory.packer.pack), Memory contract (bitemporal facts, supersession), B3 Memory vs baseline

### Community 81 - "Compose dependencies"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 82 - "Compose healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

## Ambiguous Edges - Review These
- `F7 Offline replay` → `Replay engine (deterministic Playwright, expect checks, 0 LLM)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Scripted event: oat milk +9% day -3` → `Card: Reorder oat milk (stock-out, Grainline)`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `README badges (CI, license, stack)` → `Design tokens (crema/roasted caramel palette; tokens.css)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **37 isolated node(s):** `python`, `uvx`, `start-mcp-server`, `@upstash/context7-mcp`, `@playwright/mcp` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 616 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Contracts (L0)` connect `Contract sections` to `Temporal memory store`, `Portals contract models`, `Brief planner and candidates`, `Contracts and memory writers`, `Inventory world sim`, `API response shapes`, `DuckDB analytics connect`?**
  _High betweenness centrality (0.343) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `9.1 Laptop tasks (light)`) actually correct?**
  _`Candidate` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `python`, `uvx`, `start-mcp-server` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Temporal memory store` be split into smaller, more focused modules?**
  _Cohesion score 0.05036630036630037 - nodes in this community are weakly interconnected._
- **Why does `Candidate` connect `DuckDB analytics connect` to `Temporal memory store`, `Number guard`, `Brief planner and candidates`, `Contract base models`, `Contract sections`, `LLM planner agents`, `Brief pipeline tests`, `Laptop sync log`, `Detectors`, `API response shapes`, `Handover setup`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `F7 Offline replay` and `Replay engine (deterministic Playwright, expect checks, 0 LLM)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Scripted event: oat milk +9% day -3` and `Card: Reorder oat milk (stock-out, Grainline)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._