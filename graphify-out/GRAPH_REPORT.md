# Graph Report - backroom laptop work  (2026-11-14)

## Corpus Check
- 33 files · ~86,762 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2360 nodes · 5951 edges · 108 communities (95 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 660 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Invoice PDF rendering
- test_memory.py
- Brief pipeline tests
- Web root layout and fonts
- Skills contract schema
- skills-desk.tsx
- Web zod contracts
- Cost meter and budget
- Today page and brief
- api-status.tsx
- rendering.py
- generate
- memory-desk.tsx
- Candidate
- Run event types
- Sales data transform
- margin_erosion
- LLM planner agents
- API settings and DB pool
- action-card.tsx
- LLM capability probe
- writers.py
- Chaos catalog tests
- LLM capability probe checks
- registry.py
- Number formatting
- Number guard internals
- packer.py
- memory/store.py
- Contract
- backroom_portals/main.py
- Portals admin API
- api.py
- Contract types and extractor
- L0 contracts and early deviations
- Data pipeline tests
- test_chaos_render.py
- re
- backroom_bench/cli.py
- Model registry and providers
- test_grainline.py
- External data sources
- TillDesk routes
- TillDesk price editing
- bench/page.tsx
- Web agent rules
- Inventory world sim
- Chaos variants and admin
- health.py
- Data build pipeline
- Parquet writer
- Owner preferences rules
- API and bench packages
- Data and portals packages
- pnpm workspace
- Root package
- Recipes data
- Key API routes
- Web lint and dependencies
- Serena project config
- Hosting and ADRs
- shadcn components config
- Sync logs and two-machine flow
- Contracts overview
- Memory SQL schema
- Staff rota data
- CI workflow
- TypeScript config
- Contracts (L0)
- Handover setup
- MCP server config
- Preferences data
- CI workflow steps
- Root package scripts
- CI jobs
- Compose API service
- Compose portals service
- Look
- Compose build config
- Compose Postgres service
- Root package manifest
- Web package scripts (2)
- Compose root
- Product map
- Compose dependencies
- Compose healthcheck
- Grainline portal templates
- Memory design and staleness
- Demo beats and chaos story
- Model roles table
- Milestones and scope decisions
- Stack, infra and CI
- PRD features and demo prices
- Bench, golden runs and deploy
- Repo scripts and tooling
- Repository layout and packages
- Data sources and memory packing
- CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e)
- Build Plan (Wed 22:00 -> Fri 11:30 freeze)
- Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)
- Frontend quality bar (Lighthouse >= 90, reduced motion)
- LLM non-negotiables and adapters
- Demo story beats
- Prioritisation P0/P1/P2

## God Nodes (most connected - your core abstractions)
1. `Laptop deviations (L-n log, append-only; PC renumbers on merge)` - 77 edges
2. `Candidate` - 60 edges
3. `Backroom Product Requirements Document` - 53 edges
4. `Contract` - 52 edges
5. `LLM` - 30 edges
6. `build()` - 30 edges
7. `Settings` - 29 edges
8. `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)` - 28 edges
9. `generate()` - 26 edges
10. `FakePlanner` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)` --references--> `Look`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/rendering.py
- `5. Run events` --references--> `RunEvent`  [INFERRED]
  docs/CONTRACTS.md → apps/web/src/lib/contracts.ts
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `Model price table (USD per 1M tokens; kept in llm/registry.py)` --references--> `Price`  [INFERRED]
  docs/ARCHITECTURE.md → services/api/backroom_api/llm/registry.py

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

### Community 0 - "Invoice PDF rendering"
Cohesion: 0.07
Nodes (43): GrainlineState, Order, OrderLine, PriceEvent, Product, SeedLine, SeedOrder, GrainlineStore (+35 more)

### Community 1 - "test_memory.py"
Cohesion: 0.07
Nodes (38): Assertion, conn(), world(), assert_fact(), write_invoice(), graph(), pack_sizes(), add_episode() (+30 more)

### Community 11 - "Brief pipeline tests"
Cohesion: 0.16
Nodes (28): FakePlanner, FakeVerifier, _Message, _Result, candidates(), conn(), data_dir(), brief() (+20 more)

### Community 12 - "Web root layout and fonts"
Cohesion: 0.09
Nodes (26): NavItem, RootLayout(), Providers(), AppShell(), isActive(), navDirection(), TabBarLinks(), TopBarLinks() (+18 more)

### Community 13 - "Skills contract schema"
Cohesion: 0.08
Nodes (18): Step, StepChange, load(), make_skill(), to_sse(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step() (+10 more)

### Community 16 - "skills-desk.tsx"
Cohesion: 0.11
Nodes (26): Stats, Skill, SkillDiff, SkillSummary, SkillVersions, Step, Locator, StepRow (+18 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (62): BriefStreamEvent, ChaosState, Evidence, FactDetail, GoldenFrame, Mode, Portal, RunEventType (+54 more)

### Community 22 - "Cost meter and budget"
Cohesion: 0.12
Nodes (11): BudgetExceededError, SpendLedger, FakeClient, FakeMessages, fake_message(), make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict() (+3 more)

### Community 25 - "Today page and brief"
Cohesion: 0.15
Nodes (24): CardStatus, LoadedBrief, Brief, EmptyState(), BadgeSlot(), SampleBadge(), BriefSkeleton(), decisions() (+16 more)

### Community 26 - "api-status.tsx"
Cohesion: 0.09
Nodes (24): Status, Tone, Loaded, Source, Health, ApiStatus(), fetchHealth(), dependencies (+16 more)

### Community 29 - "rendering.py"
Cohesion: 0.09
Nodes (8): ChaosSeeds, Look, page(), fact(), testid(), label(), test_testids(), 3. Chaos catalog

### Community 3 - "generate"
Cohesion: 0.08
Nodes (26): CardCopy, Planner, Verifier, BriefResult, Decision, _Drafted, Rules, BriefCardEvent (+18 more)

### Community 30 - "memory-desk.tsx"
Cohesion: 0.15
Nodes (25): Point, GraphFact, GraphNode, MemoryGraph, Slot, edgePath(), FactValue(), isoDay() (+17 more)

### Community 31 - "Candidate"
Cohesion: 0.14
Nodes (17): Candidate, candidates(), data_dir(), good_copy(), run_all(), plan(), numbers(), test_a_date_the_data_was_not_built_for_is_refused() (+9 more)

### Community 32 - "Run event types"
Cohesion: 0.13
Nodes (17): AskHuman, CostTick, _Event, HealAttempt, HealFailed, HealStarted, HealSucceeded, ModeChanged (+9 more)

### Community 33 - "Sales data transform"
Cohesion: 0.12
Nodes (12): Sale, apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), shift_days(), synthetic() (+4 more)

### Community 36 - "margin_erosion"
Cohesion: 0.15
Nodes (10): Context, Evidence, ProposedAction, connect(), _n(), _ingredient(), margin_erosion(), _shown() (+2 more)

### Community 4 - "LLM planner agents"
Cohesion: 0.08
Nodes (22): BriefLLMError, Draft, LLMPlanner, LLMVerifier, _Model, Plan, Verdict, Verdicts (+14 more)

### Community 44 - "API settings and DB pool"
Cohesion: 0.15
Nodes (8): Settings, make_pool(), create_app(), get_settings(), ping(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 5 - "action-card.tsx"
Cohesion: 0.09
Nodes (38): Variant, Mode, ActionCard, RunEvent, StepChange, Error(), FigureValue(), ActionCard() (+30 more)

### Community 55 - "LLM capability probe"
Cohesion: 0.22
Nodes (5): LLM, LLMResult, CallRecord, Cost, RoleConfig

### Community 56 - "writers.py"
Cohesion: 0.14
Nodes (7): OutOfOrderFactError, POST /memory/ingest/invoice (PDF/image to extractor to facts), Context packer (memory.packer.pack), Memory writers (assert_fact, write_world, write_invoice), Predicate vocabulary (one-valued, many-valued), Neon hosted Postgres (laptop database), L5: temporal memory store, writers, context packer (laptop/l5-memory)

### Community 57 - "Chaos catalog tests"
Cohesion: 0.16
Nodes (9): Label, pick_variants(), test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 64 - "LLM capability probe checks"
Cohesion: 0.32
Nodes (12): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _run() (+4 more)

### Community 65 - "registry.py"
Cohesion: 0.17
Nodes (5): Caps, LLMNotConfiguredError, Price, build_async_client(), caps_for()

### Community 66 - "Number formatting"
Cohesion: 0.18
Nodes (13): EvidenceNumber, displayFigure(), displayNumber(), formatTime(), roundHalfUp(), short(), EUR, SUFFIX (+5 more)

### Community 7 - "Number guard internals"
Cohesion: 0.08
Nodes (25): PriceProposal, Found, EvidenceNumber, n(), propose_price(), margin_pct(), round_half_up(), display() (+17 more)

### Community 75 - "packer.py"
Cohesion: 0.26
Nodes (5): ContextPack, pack(), estimate_tokens(), seeds_for(), _triple()

### Community 76 - "memory/store.py"
Cohesion: 0.21
Nodes (7): EpisodeRef, FactDetail, GraphFact, GraphNode, MemoryGraph, fact_detail(), _graph_fact()

### Community 8 - "Contract"
Cohesion: 0.09
Nodes (29): ApiError, ApproveResponse, Brief, ChaosRequest, ChaosState, ErrorResponse, HumanReply, InvoiceIngestResponse (+21 more)

### Community 9 - "Portals admin API"
Cohesion: 0.08
Nodes (14): ChaosRequest, ChaosState, MenuItem, _Model, TillDeskState, TillDeskStore, chaos_set(), _chaos_state() (+6 more)

### Community 90 - "api.py"
Cohesion: 0.28
Nodes (4): ExtractedRule, checked(), record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 14 - "Data pipeline tests"
Cohesion: 0.10
Nodes (17): built(), tiny_xlsx(), _column(), rows(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table() (+9 more)

### Community 17 - "test_chaos_render.py"
Cohesion: 0.10
Nodes (20): forced(), client(), create_app(), make_settings(), fresh_client(), signed_in(), catalog_html(), dom_hash() (+12 more)

### Community 63 - "re"
Cohesion: 0.21
Nodes (7): code_at(), default_secret(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector(), Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts)

### Community 39 - "Model registry and providers"
Cohesion: 0.14
Nodes (19): cost_usd(), role_config(), make_settings(), canonical_model_id(), wire_model_id(), test_naive_datetimes_are_rejected(), test_anthropic_client_uses_default_base_url(), test_anthropic_uses_canonical_ids_and_rejects_slash_ids() (+11 more)

### Community 21 - "test_grainline.py"
Cohesion: 0.21
Nodes (28): state(), has_testid(), login(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove(), test_catalog_paginates() (+20 more)

### Community 34 - "External data sources"
Cohesion: 0.13
Nodes (11): maven_zip(), cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), _parse_daily(), synthetic_weather() (+3 more)

### Community 50 - "TillDesk routes"
Cohesion: 0.30
Nodes (13): _redirect(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 20 - "TillDesk price editing"
Cohesion: 0.16
Nodes (27): fresh(), state(), parse_price(), change_price(), dom_hash(), login(), pages(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 27 - "bench/page.tsx"
Cohesion: 0.11
Nodes (21): AboutPage(), Chapter(), BenchPage(), usd(), MemoryPage(), TodayPage(), FlowDiagram(), PageTransition() (+13 more)

### Community 37 - "Web agent rules"
Cohesion: 0.14
Nodes (20): Figure(), prefersReducedMotion(), newsreaderDisplay, Newsreader font (The Newsreader Project Authors, productiontype), SIL Open Font License 1.1, Frontend quality bar (Lighthouse >= 90, reduced motion), Fonts via next/font: Newsreader (display + text cut), Geist, Geist Mono, GET /brief/today (cached brief; ?regenerate=1 streams a new one) (+12 more)

### Community 38 - "Inventory world sim"
Cohesion: 0.14
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 53 - "Chaos variants and admin"
Cohesion: 0.13
Nodes (15): loadSampleRun(), Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), F2 Run theater, Non-goals (no real integrations, no evasion), Q: What breaks first in production, Open or synthetic data only ('Synthetic' chip in UI), Action card (impact, why, evidence chips, Approve/Review/Not now), Agent-cursor overlay / halo (+7 more)

### Community 73 - "health.py"
Cohesion: 0.21
Nodes (4): is_configured(), health(), _portals_ok(), _postgres_ok()

### Community 79 - "Data build pipeline"
Cohesion: 0.29
Nodes (4): build(), _maven_sales(), next_saturday(), _notes()

### Community 96 - "Owner preferences rules"
Cohesion: 0.33
Nodes (3): weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 19 - "Recipes data"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 23 - "Key API routes"
Cohesion: 0.08
Nodes (23): This is NOT the Next.js you know, Charts (Recharts or visx; dataviz skill, palette validator), Frontend (apps/web) choices, Memory graph lib (@xyflow/react or force-graph; benchmark at ~300 nodes), Key API routes, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), Navigation domain allowlist per run, Next.js (App Router, latest stable), TypeScript strict, pnpm (+15 more)

### Community 24 - "Web lint and dependencies"
Cohesion: 0.09
Nodes (28): eslintConfig, react-dom@19.3.0, shadcn@^4.23.0, tw-animate-css@^1.4.0, devDependencies, eslint@^9, eslint-config-next@16.4.6, tailwindcss@4.3.3 (+20 more)

### Community 40 - "Serena project config"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 42 - "Hosting and ADRs"
Cohesion: 0.12
Nodes (13): probe:llm, LLM_CAPS_OFF (switch capability flags off), OpenRouter ~5.5% credit fee (OPENROUTER_FEE_PCT), Provider openrouter (default; base_url openrouter.ai/api, auth_token, X-Title/HTTP-Referer headers), psycopg 3 synchronous pool called from worker threads, Alternative: browser-use / Stagehand, Alternative: Graphiti + FalkorDB / Neo4j, Alternative: OpenAI-compatible OpenRouter API (second code path) (+5 more)

### Community 45 - "shadcn components config"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 48 - "Sync logs and two-machine flow"
Cohesion: 0.15
Nodes (16): Sync log: PC → laptop, Thu 12 Nov 2026 · two-machine mode starts, M0 Foundations, Fixtures and the drift check, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13 (+8 more)

### Community 49 - "Contracts overview"
Cohesion: 0.16
Nodes (18): Portals admin API (/_admin/chaos, state, reset), Brief pipeline (stream_today, BriefResult), Detector Candidate, Chaos catalog (nine variant families), Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Portal labels (en, en_alt, de), Number guard rules 1-9 (+10 more)

### Community 52 - "Memory SQL schema"
Cohesion: 0.18
Nodes (16): entity, episode, episode_kind_idx, fact, fact_episode_idx, fact_object_idx, fact_open_idx, fact_subject_predicate_idx (+8 more)

### Community 54 - "Staff rota data"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 58 - "CI workflow"
Cohesion: 0.12
Nodes (13): exclude, include, concurrency, cancel-in-progress, group, name, on, pull_request (+5 more)

### Community 59 - "TypeScript config"
Cohesion: 0.12
Nodes (17): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+9 more)

### Community 60 - "Contracts (L0)"
Cohesion: 0.18
Nodes (10): 1. Changing a contract, 4. Skills, 5. Run events, 9. Fixtures and the drift check, Contracts (L0), POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names) (+2 more)

### Community 62 - "Handover setup"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 69 - "MCP server config"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 72 - "Preferences data"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 74 - "CI workflow steps"
Cohesion: 0.24
Nodes (13): steps, steps, id, if, name, run, uses, with (+5 more)

### Community 78 - "Root package scripts"
Cohesion: 0.17
Nodes (12): scripts, bench, check, check:py, dev, dev:api, dev:db, dev:lite (+4 more)

### Community 81 - "CI jobs"
Cohesion: 0.20
Nodes (10): name, runs-on, jobs, docs, python, web, name, runs-on (+2 more)

### Community 82 - "Compose API service"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 83 - "Compose portals service"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 86 - "Look"
Cohesion: 0.22
Nodes (7): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk), Sync entry format (Done / Verify / Needs from PC / Notes)

### Community 87 - "Compose build config"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 88 - "Compose Postgres service"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 89 - "Root package manifest"
Cohesion: 0.25
Nodes (8): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, version, concurrently

### Community 91 - "Web package scripts (2)"
Cohesion: 0.25
Nodes (8): scripts, build, contracts, dev, e2e, lint, start, typecheck

### Community 95 - "Compose root"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 97 - "Product map"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 98 - "Compose dependencies"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 99 - "Compose healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 10 - "Grainline portal templates"
Cohesion: 0.13
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 15 - "Memory design and staleness"
Cohesion: 0.11
Nodes (35): Brief pipeline: agents for judgment, code for math, F4 Memory (graph, time slider, fact inspector, context pack), Goals G1-G7, Interview pitch: what happens after Approve all, Number guard, Temporal knowledge graph (bitemporal facts, supersession, episodes), What Backroom demonstrates (five hard problems), Rule: LLMs never originate numbers (+27 more)

### Community 18 - "Demo beats and chaos story"
Cohesion: 0.11
Nodes (32): Rule: secrets never reach prompts or logs, Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), M2 Browser agent (Thu 09:00-14:00, riskiest), M2 gate (cold explore seed 0, warm replay <5 s 0 LLM, chaos seed 7 heal -> v2 diff), Why M2 first and fresh: riskiest milestone, Demo setup (pre-warmed skills, chaos seed 7 verified, access code, local compose backup) (+24 more)

### Community 28 - "Model roles table"
Cohesion: 0.12
Nodes (27): Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), LLM_<ROLE>_EFFORT override, LLM_PROVIDER env var (openrouter default | anthropic), backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/skills (compiler, replay, healer, registry), claude-fable-5-2 ($8 / $40; thinking always on), claude-haiku-5-5 ($0.10 / $0.50; long-prompt tier above 100K), Model layer (every provider and model choice is an env var) (+19 more)

### Community 35 - "Milestones and scope decisions"
Cohesion: 0.13
Nodes (8): Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), pnpm seed (uv run backroom-data all: download, transform, load Postgres + Parquet), TillDesk (mock till / menu portal), Laptop deviations (L-n log, append-only; PC renumbers on merge), Independent audit pass per laptop task (blockers and should-fix items, all fixed), L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline), L4: data pipeline to Parquet (laptop/l4-data), L6: DuckDB detectors and deterministic pricing (laptop/l6-detectors)

### Community 41 - "Stack, infra and CI"
Cohesion: 0.15
Nodes (23): Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e), Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), Deploy freeze: no deploys after Fri 11:30, infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test), infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), FastAPI api service (orchestrator, agents, memory, SSE/WS) (+15 more)

### Community 43 - "PRD features and demo prices"
Cohesion: 0.14
Nodes (24): M2 Browser agent (riskiest), M3 Memory + Brief + UI, Demo-story prices (DEMO_PRICES_EUR), Break it: chaos seed 7 heal beat, Five-minute demo beats (hook, evidence, act, break it, remember, learn, proof, close), B2 Learning curve, B4 Model swap (P1), B5 Number guard benchmark (+16 more)

### Community 46 - "Bench, golden runs and deploy"
Cohesion: 0.17
Nodes (22): Lightsail snapshot before final deploy (2-minute rollback), Route /bench, Route / Today, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), Benchmarks B1-B5, F6 Benchmarks page, README benchmarks table (B1, B2, B3, B5) (+14 more)

### Community 47 - "Repo scripts and tooling"
Cohesion: 0.12
Nodes (15): pnpm check (ruff, pyright, pytest, web lint, typecheck), pnpm e2e (Playwright e2e of the demo path at 390 px + 1440 px), Web quality: ESLint, tsc --noEmit, Playwright e2e (390/1440 px), Lighthouse >= 90, Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: DOM-hash test per chaos seed, Check: Lighthouse via web-perf skill, Check: pytest + ruff + pyright for Python logic (+7 more)

### Community 51 - "Repository layout and packages"
Cohesion: 0.15
Nodes (17): docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), DuckDB over Parquet (sales analytics), backroom_api/analytics (DuckDB queries, stockout/margin/weather detectors), backroom_api/replay (golden-run recorder & player), Root package.json (pnpm workspace root + task runner), data package backroom_data (script backroom-data; raw data not committed), pnpm dev (Postgres in Docker + api + portals + next dev in parallel), pnpm dev:lite (api, portals, web without Docker or a database; API reports degraded) (+9 more)

### Community 6 - "Data sources and memory packing"
Cohesion: 0.09
Nodes (41): Code freeze Fri 13 Nov 11:30, M1 Data + Portals, Maven Coffee Shop Sales dataset, Nager.Date public holidays, Open-Meteo weather (Bonn), Seed pipeline (backroom-data, DATA_SEED=44), B3 Memory vs baseline, F5 Ask (P1) (+33 more)

### Community 61 - "CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e)"
Cohesion: 0.13
Nodes (16): Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, CDP Page.startScreencast live frames, GHCR container registry, Lint/test: ruff, pyright (strict on core), pytest, pytest-asyncio, backroom_api/browser (pool, ARIA snapshot observation, executor, screencast), Native local dev (uv run uvicorn --reload; only Postgres in Docker), Route /runs/[id] Run theater (+8 more)

### Community 67 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.16
Nodes (14): M4 Bench + Deploy, Golden runs (events.json, frames), F7 Offline replay, Reliability and safety (idempotency, daily spend cap, replay for public), Rule: every LLM call through cost meter + budget guard, Record golden runs -> replay mode, Observation: ARIA snapshot + numbered interactive elements, Daily budget guard (LLM_DAILY_BUDGET_USD, default $3/day) (+6 more)

### Community 68 - "Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)"
Cohesion: 0.16
Nodes (7): Shared Action interface to the planner, Memory per merchant + cross-merchant best-practices layer, Route /about (architecture for the interview), Provider anthropic (direct; full features incl. server-side refusal fallbacks), Server-side refusal fallbacks (beta server-side-fallback-2026-07-01, anthropic provider only), How this maps to the real Super44 problem, Beat 4:40 Close - /about, model table, adapters

### Community 70 - "Frontend quality bar (Lighthouse >= 90, reduced motion)"
Cohesion: 0.23
Nodes (11): Session read order (HANDOVER, BUILD_PLAN, GRAPH_REPORT), CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, claude-api skill (load before Anthropic SDK code), context7 for library docs, Git rules (small commits per gate, no AI attribution, log deviations), graphify-out/GRAPH_REPORT.md, graphify MCP (query_graph, get_neighbors, shortest_path) (+3 more)

### Community 71 - "LLM non-negotiables and adapters"
Cohesion: 0.23
Nodes (9): Daily LLM budget guard (sums today's ledger rows before each call), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), backroom_api/llm (model registry, client, cost meter, budget guard), pnpm probe:llm (uv run backroom-bench probe), bench/results/provider_probe.json, Open items and next steps (+1 more)

### Community 77 - "Demo story beats"
Cohesion: 0.21
Nodes (12): Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg), Scripted event: oat milk +9% day -3, Supplier prices & invoices (generated by Grainline), Approve all button, Audience: Super44 founders (Founding Engineer interview), Card: Fix Franzbroetchen margin (butter +16%, EUR3.20->3.60, TillDesk) (+4 more)

### Community 93 - "Prioritisation P0/P1/P2"
Cohesion: 0.29
Nodes (7): Langfuse Cloud Hobby traces (P1), Sentry free tier errors (P1), F8 Mobile owner view (390 px; WhatsApp-style P2), Never cut: heal under chaos, number guard, bench page, replay fallback, P2 stretch items (WhatsApp thread, voice, multi-shop, OSM map), Prioritisation P0/P1/P2, Prompt-injection demo (P1)

## Ambiguous Edges - Review These
- `Card: Reorder oat milk (stock-out, Grainline)` → `Scripted event: oat milk +9% day -3`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `F7 Offline replay` → `Replay engine (deterministic Playwright, expect checks, 0 LLM)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `README badges (CI, license, stack)` → `Design tokens (crema/roasted caramel palette; tokens.css)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **50 isolated node(s):** `python`, `uvx`, `@playwright/mcp`, `start-mcp-server`, `@upstash/context7-mcp` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 639 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `L0 contracts and early deviations` to `Run event types`, `Web zod contracts`, `Milestones and scope decisions`, `margin_erosion`, `Contract`, `Portals admin API`, `Sync logs and two-machine flow`, `Contracts overview`, `Memory SQL schema`, `Look`, `writers.py`, `CI workflow`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `L-45 (L6) Weekly EUR impact defined per card kind; cards ranked by it`) actually correct?**
  _`Candidate` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `python`, `uvx`, `@playwright/mcp` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Invoice PDF rendering` be split into smaller, more focused modules?**
  _Cohesion score 0.07487091222030981 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `Milestones and scope decisions` to `generate`, `LLM planner agents`, `Data sources and memory packing`, `Number guard internals`, `skills-desk.tsx`, `Demo beats and chaos story`, `Key API routes`, `rendering.py`, `Sales data transform`, `External data sources`, `Web agent rules`, `Hosting and ADRs`, `Repo scripts and tooling`, `Sync logs and two-machine flow`, `Contracts overview`, `Repository layout and packages`, `Memory SQL schema`, `Chaos variants and admin`, `writers.py`, `CI workflow`, `Contracts (L0)`, `Build Plan (Wed 22:00 -> Fri 11:30 freeze)`, `LLM non-negotiables and adapters`, `Look`, `L0 contracts and early deviations`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Card: Reorder oat milk (stock-out, Grainline)` and `Scripted event: oat milk +9% day -3`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `F7 Offline replay` and `Replay engine (deterministic Playwright, expect checks, 0 LLM)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._