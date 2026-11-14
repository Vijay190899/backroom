# Graph Report - backroom laptop work  (2026-11-14)

## Corpus Check
- 29 files · ~78,026 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2265 nodes · 5619 edges · 102 communities (87 shown, 15 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 620 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- test_memory.py
- Invoice PDF rendering
- Brief pipeline tests
- Skills contract schema
- API settings and DB pool
- Web zod contracts
- Portal rendering helpers
- LLM planner agents
- Today action card UI
- Today page and brief
- LLM capability probe
- Detector context and proposals
- Number guard internals
- Memory SQL schema
- Portals admin API
- Sales data transform
- Model registry and providers
- generate
- Run event types
- client.py
- Cost meter and budget
- Portals contract models
- Service settings
- Web root layout and fonts
- Chaos variant catalog
- Formatting and ticking figures
- agents.py
- Skill schema fallbacks
- Spend ledger
- extract
- API response shapes
- Fixture clock
- Run events contract
- Data pipeline tests
- forced
- XLSX reader
- test_grainline.py
- External data sources
- TillDesk routes
- Owner preferences rules
- test_chaos_render.py
- TillDesk price editing
- Web agent rules
- Next config and routes
- CLI entry points
- Inventory world sim
- Web contracts check
- re
- Parquet writer
- Web lint and dependencies
- Sync logs and two-machine flow
- CI workflow
- Recipes data
- Serena project config
- Contracts overview
- Root package scripts
- shadcn components config
- TypeScript config
- Chaos variants and admin
- Staff rota data
- Handover setup
- MCP server config
- Preferences data
- Compose API service
- Compose portals service
- Compose build config
- Compose Postgres service
- Web package scripts
- Laptop sync log
- Compose root
- Product map
- Contract sections
- Compose dependencies
- Compose healthcheck
- API and bench packages
- Data and portals packages
- pnpm workspace
- Root package
- Stack, infra and CI
- Milestones and scope decisions
- PRD features and demo prices
- Data sources and memory packing
- Bench, golden runs and deploy
- Memory design and staleness
- Repo scripts and tooling
- Verification rules
- LLM non-negotiables and adapters
- Hosting and ADRs
- Demo Script - 5 minutes
- Frontend quality bar
- Pitch, audience and JD problems
- Demo beats and chaos story
- Demo story beats
- Brief pipeline contracts
- Run theater streaming
- Grainline portal templates

## God Nodes (most connected - your core abstractions)
1. `Laptop deviations (L-n log, append-only; PC renumbers on merge)` - 75 edges
2. `Candidate` - 59 edges
3. `Backroom Product Requirements Document` - 53 edges
4. `Contract` - 52 edges
5. `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)` - 31 edges
6. `LLM` - 30 edges
7. `build()` - 30 edges
8. `Settings` - 29 edges
9. `generate()` - 27 edges
10. `Handover` - 26 edges

## Surprising Connections (you probably didn't know these)
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `3. Chaos catalog` --references--> `Look`  [INFERRED]
  docs/CONTRACTS.md → services/portals/backroom_portals/rendering.py
- `Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)` --references--> `Look`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/rendering.py
- `Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)` --references--> `TillDeskState`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/contract.py

## Import Cycles
- 2-file cycle: `services/portals/backroom_portals/config.py -> services/portals/backroom_portals/totp.py -> services/portals/backroom_portals/config.py`

## Hyperedges (group relationships)
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — docs_prd_detectors, docs_prd_candidate, docs_prd_planner, docs_prd_verifier, docs_prd_number_guard, docs_architecture_route_brief_today [EXTRACTED 1.00]
- **Chaos-aware rendering primitives shared by all portals** — services_portals_backroom_portals_templates_macros_wrap, services_portals_backroom_portals_templates_macros_submit, services_portals_backroom_portals_templates_macros_field, services_portals_backroom_portals_templates_macros_nav, services_portals_backroom_portals_templates_macros_interstitial, services_portals_backroom_portals_templates_macros_chaos_js, services_portals_backroom_portals_templates_macros_look_chaos_object [EXTRACTED 1.00]
- **Single LLM call path: registry, client, cost meter, ledger, budget guard and capability flags** — docs_architecture_model_registry, docs_architecture_llm_client_call_path, docs_architecture_cost_meter, docs_architecture_llm_ledger, docs_architecture_budget_guard, docs_architecture_capability_flags [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — docs_prd_explore_mode, docs_prd_skill_compiler, docs_prd_replay_engine, docs_prd_heal_ladder, docs_prd_skill_versioning, docs_architecture_escalation_ladder [EXTRACTED 1.00]
- **Brief flow: detectors compute, planner writes, verifier checks, number guard verifies** — docs_contracts_detectors, docs_contracts_candidate, docs_contracts_brief_pipeline, docs_decisions_l_58_verifier_keep_or_veto, docs_contracts_number_guard_rules, docs_decisions_adr_5_agents_judgment_code_math [INFERRED 0.85]
- **Morning edition redesign and its font/performance follow-up** — docs_decisions_l_69_morning_edition, docs_decisions_l_70_newsreader_subset, docs_architecture_fonts, apps_web_src_fonts_ofl_newsreader_font, docs_sync_laptop_l8_part1_entry [INFERRED 0.85]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — docs_prd_franzbroetchen_story, docs_architecture_route_reject, docs_prd_episodes, docs_prd_extractor, docs_prd_preference_fact, docs_prd_verifier, demo_beat_learn_owner [INFERRED 0.85]
- **Reject-to-preference loop (F4): reject reason becomes a capped, re-proposed card with a new action id** — docs_architecture_route_reject, docs_decisions_l_64_preference_extractor_on_laptop, docs_decisions_l_54_token_estimate, docs_decisions_l_58_verifier_keep_or_veto, docs_decisions_l_44_pricing_rule, docs_decisions_l_63_action_id_hash [INFERRED 0.85]
- **Self-healing skill loop under chaos seed 7** — docs_prd_f3_skill_learning_healing, docs_architecture_escalation_ladder, docs_contracts_skill_versioning_heal, docs_contracts_skill_diff, docs_decisions_l_6_heal_semantics, docs_decisions_l_16_seed_7_pinned, docs_demo_script_break_it_seed_7_heal [INFERRED 0.85]
- **Two-machine contract-first coordination** — docs_decisions_adr_15_two_machine_workflow, docs_handover_work_split, docs_handover_ownership_table, docs_contracts_contract_change_process, docs_sync_laptop, docs_sync_pc [INFERRED 0.85]
- **Grainline ordering flow pages** — services_portals_backroom_portals_templates_grainline_catalog, services_portals_backroom_portals_templates_grainline_cart, services_portals_backroom_portals_templates_grainline_checkout, services_portals_backroom_portals_templates_grainline_order, services_portals_backroom_portals_templates_grainline_invoices [INFERRED 0.95]
- **TillDesk price change and publish flow** — services_portals_backroom_portals_templates_tilldesk_login, services_portals_backroom_portals_templates_tilldesk_menu, services_portals_backroom_portals_templates_tilldesk_edit, services_portals_backroom_portals_templates_tilldesk_menu_draft_publish_flow [INFERRED 0.95]

## Communities (102 total, 15 thin omitted)

### Community 0 - "test_memory.py"
Cohesion: 0.06
Nodes (47): ContextPack, conn(), world(), assert_fact(), pack(), fact_detail(), _graph_fact(), write_invoice() (+39 more)

### Community 1 - "Invoice PDF rendering"
Cohesion: 0.07
Nodes (42): Order, OrderLine, PriceEvent, Product, SeedLine, SeedOrder, GrainlineStore, Invoice (+34 more)

### Community 10 - "Brief pipeline tests"
Cohesion: 0.16
Nodes (28): FakePlanner, FakeVerifier, _Message, _Result, candidates(), conn(), data_dir(), brief() (+20 more)

### Community 11 - "Skills contract schema"
Cohesion: 0.08
Nodes (20): Skill, Step, StepChange, load(), make_skill(), to_sse(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form() (+12 more)

### Community 15 - "API settings and DB pool"
Cohesion: 0.10
Nodes (11): Settings, make_pool(), create_app(), get_settings(), ping(), lifespan(), health(), _portals_ok() (+3 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (63): Brief, BriefStreamEvent, ChaosState, FactDetail, GoldenFrame, GraphFact, GraphNode, MemoryGraph (+55 more)

### Community 23 - "Portal rendering helpers"
Cohesion: 0.09
Nodes (7): ChaosSeeds, Look, page(), fact(), testid(), label(), test_testids()

### Community 24 - "LLM planner agents"
Cohesion: 0.14
Nodes (18): BriefLLMError, CardCopy, LLMPlanner, Candidate, StubLLM, good_copy(), _timed(), _parse() (+10 more)

### Community 25 - "Today action card UI"
Cohesion: 0.12
Nodes (25): CardStatus, Variant, ActionCard, Evidence, Error(), ActionCard(), Actions(), impactNumber() (+17 more)

### Community 26 - "Today page and brief"
Cohesion: 0.16
Nodes (23): BriefSource, LoadedBrief, TodayPage(), PageHeader(), BriefSkeleton(), decisions(), TodayBrief(), approveAll() (+15 more)

### Community 28 - "LLM capability probe"
Cohesion: 0.18
Nodes (14): Check, LLM, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs() (+6 more)

### Community 3 - "Detector context and proposals"
Cohesion: 0.07
Nodes (31): Context, PriceProposal, Evidence, ProposedAction, candidates(), data_dir(), connect(), _n() (+23 more)

### Community 30 - "Number guard internals"
Cohesion: 0.12
Nodes (17): Found, EvidenceNumber, n(), display(), extract(), _matches(), _rounds_to(), _short() (+9 more)

### Community 32 - "Memory SQL schema"
Cohesion: 0.13
Nodes (20): OutOfOrderFactError, entity, episode, episode_kind_idx, fact, fact_episode_idx, fact_object_idx, fact_open_idx (+12 more)

### Community 34 - "Portals admin API"
Cohesion: 0.16
Nodes (12): ChaosRequest, ChaosState, GrainlineState, _Model, TillDeskState, chaos_set(), _chaos_state(), chaos_get() (+4 more)

### Community 36 - "Sales data transform"
Cohesion: 0.14
Nodes (12): Sale, apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), shift_days(), synthetic() (+4 more)

### Community 39 - "Model registry and providers"
Cohesion: 0.13
Nodes (16): LLMNotConfiguredError, build_async_client(), role_config(), make_settings(), is_configured(), wire_model_id(), test_anthropic_client_uses_default_base_url(), test_anthropic_uses_canonical_ids_and_rejects_slash_ids() (+8 more)

### Community 4 - "generate"
Cohesion: 0.09
Nodes (25): Planner, Verifier, BriefResult, Decision, _Drafted, Rules, Brief, BriefCardEvent (+17 more)

### Community 40 - "Run event types"
Cohesion: 0.15
Nodes (17): AskHuman, CostTick, _Event, GoldenFrame, HealAttempt, HealFailed, HealStarted, HealSucceeded (+9 more)

### Community 42 - "client.py"
Cohesion: 0.13
Nodes (12): LLMResult, CallRecord, Caps, Cost, Price, RoleConfig, caps_for(), cost_usd() (+4 more)

### Community 49 - "Cost meter and budget"
Cohesion: 0.18
Nodes (9): BudgetExceededError, FakeClient, FakeMessages, fake_message(), make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict(), test_create_sends_wire_model_and_effort_and_records_cost() (+1 more)

### Community 53 - "Portals contract models"
Cohesion: 0.12
Nodes (5): MenuItem, TillDeskStore, parse_price(), test_tilldesk_state_is_addressable_by_item_id(), test_suffix_euro_prices_parse()

### Community 57 - "Service settings"
Cohesion: 0.13
Nodes (5): Settings, client(), create_app(), get_settings(), default_secret()

### Community 6 - "Web root layout and fonts"
Cohesion: 0.07
Nodes (32): Status, Tone, NavItem, Health, RootLayout(), Providers(), ApiStatus(), AppShell() (+24 more)

### Community 60 - "Chaos variant catalog"
Cohesion: 0.17
Nodes (9): Label, pick_variants(), test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 61 - "Formatting and ticking figures"
Cohesion: 0.17
Nodes (14): EvidenceNumber, reducedMotion(), TickingEur(), displayNumber(), formatDateline(), formatEur(), formatTime(), roundHalfUp() (+6 more)

### Community 63 - "agents.py"
Cohesion: 0.23
Nodes (7): Draft, LLMVerifier, _Model, Plan, Verdict, Verdicts, Preference

### Community 73 - "Skill schema fallbacks"
Cohesion: 0.20
Nodes (7): CssFallback, Expect, LabelFallback, Postcondition, SkillStats, TextFallback, reorder_steps()

### Community 78 - "extract"
Cohesion: 0.24
Nodes (4): ExtractedRule, checked(), record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 8 - "API response shapes"
Cohesion: 0.09
Nodes (26): ActionCard, ApiError, ApproveResponse, ChaosRequest, ChaosState, EpisodeRef, ErrorResponse, FactDetail (+18 more)

### Community 43 - "Data pipeline tests"
Cohesion: 0.16
Nodes (14): built(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table(), test_cached_weather_and_nager_holidays_are_used(), test_corrupt_cached_download_falls_back_to_synthetic(), test_inventory_covers_only_the_order_window() (+6 more)

### Community 62 - "XLSX reader"
Cohesion: 0.15
Nodes (4): tiny_xlsx(), _column(), rows(), test_xlsx_reader_streams_rows_with_shared_strings()

### Community 21 - "test_grainline.py"
Cohesion: 0.21
Nodes (28): state(), has_testid(), login(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove(), test_catalog_paginates() (+20 more)

### Community 37 - "External data sources"
Cohesion: 0.14
Nodes (10): maven_zip(), cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), _parse_daily(), synthetic_weather() (+2 more)

### Community 50 - "TillDesk routes"
Cohesion: 0.30
Nodes (13): _redirect(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 67 - "Owner preferences rules"
Cohesion: 0.19
Nodes (4): rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 41 - "test_chaos_render.py"
Cohesion: 0.15
Nodes (17): make_settings(), fresh_client(), signed_in(), catalog_html(), dom_hash(), skill_path_pages(), test_admin_chaos_sets_reads_and_resets_seeds(), test_admin_chaos_validates_and_needs_the_token() (+9 more)

### Community 27 - "TillDesk price editing"
Cohesion: 0.19
Nodes (25): fresh(), state(), change_price(), dom_hash(), login(), pages(), test_a_fresh_login_drops_leftover_drafts(), test_bad_prices_show_an_error_and_change_nothing() (+17 more)

### Community 35 - "Web agent rules"
Cohesion: 0.14
Nodes (17): RejectDialog(), newsreaderDisplay, This is NOT the Next.js you know, Newsreader font (The Newsreader Project Authors, productiontype), SIL Open Font License 1.1, Charts (Recharts or visx; dataviz skill, palette validator), Fonts via next/font: Newsreader (display + text cut), Geist, Geist Mono, Frontend (apps/web) choices (+9 more)

### Community 47 - "Next config and routes"
Cohesion: 0.18
Nodes (14): AboutPage(), BenchPage(), MemoryPage(), SkillsPage(), EmptyState(), PlaceholderPage(), nextConfig, next@16.4.6 (+6 more)

### Community 48 - "CLI entry points"
Cohesion: 0.15
Nodes (6): main(), build(), main(), _maven_sales(), next_saturday(), _notes()

### Community 55 - "Inventory world sim"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 68 - "Web contracts check"
Cohesion: 0.15
Nodes (10): zod@^4.6.7, briefSchema, brief, fixtures, negatives, memoryGraphSchema, runEventSchema, skillSummarySchema (+2 more)

### Community 71 - "re"
Cohesion: 0.30
Nodes (5): code_at(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 12 - "Web lint and dependencies"
Cohesion: 0.08
Nodes (35): eslintConfig, dependencies, class-variance-authority@^0.7.1, lucide-react@^1.72.0, react@19.3.0, react-dom@19.3.0, shadcn@^4.23.0, @tanstack/react-query@^5.107.1 (+27 more)

### Community 13 - "Sync logs and two-machine flow"
Cohesion: 0.09
Nodes (24): Sync log: PC → laptop, Thu 12 Nov 2026 · two-machine mode starts, CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e), Fixtures and the drift check, Neon hosted Postgres (laptop database), Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite) (+16 more)

### Community 17 - "CI workflow"
Cohesion: 0.07
Nodes (33): concurrency, cancel-in-progress, group, name, runs-on, steps, jobs, docs (+25 more)

### Community 18 - "Recipes data"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 33 - "Serena project config"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 38 - "Contracts overview"
Cohesion: 0.12
Nodes (17): Playwright (Python) Chromium browser, Portals admin API (/_admin/chaos, state, reset), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Memory writers (assert_fact, write_world, write_invoice), pick_variants(portal, seed), Skill postconditions (url_matches, text_visible, portal_state) (+9 more)

### Community 44 - "Root package scripts"
Cohesion: 0.09
Nodes (22): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, scripts, bench (+14 more)

### Community 45 - "shadcn components config"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 51 - "TypeScript config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+11 more)

### Community 54 - "Chaos variants and admin"
Cohesion: 0.18
Nodes (6): POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Check: DOM-hash test per chaos seed, M1 gate (portals usable, DOM-hash determinism, seed loads), L2: chaos engine with 9 families (laptop/l2-chaos)

### Community 56 - "Staff rota data"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 59 - "Handover setup"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 66 - "MCP server config"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 69 - "Preferences data"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 75 - "Compose API service"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 76 - "Compose portals service"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 79 - "Compose build config"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 80 - "Compose Postgres service"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 81 - "Web package scripts"
Cohesion: 0.25
Nodes (8): scripts, build, contracts, dev, e2e, lint, start, typecheck

### Community 82 - "Laptop sync log"
Cohesion: 0.29
Nodes (7): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)

### Community 83 - "Compose root"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 84 - "Product map"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 86 - "Contract sections"
Cohesion: 0.33
Nodes (6): 1. Changing a contract, 3. Chaos catalog, 4. Skills, 8. Memory, 9. Fixtures and the drift check, Contracts (L0)

### Community 87 - "Compose dependencies"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 88 - "Compose healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 14 - "Stack, infra and CI"
Cohesion: 0.10
Nodes (31): Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), CDP Page.startScreencast live frames, Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), Deploy freeze: no deploys after Fri 11:30, infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test) (+23 more)

### Community 16 - "Milestones and scope decisions"
Cohesion: 0.12
Nodes (10): data package backroom_data (script backroom-data; raw data not committed), Grainline (mock supplier portal), Localboard (mock portal, P1), Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), TillDesk (mock till / menu portal), Laptop deviations (L-n log, append-only; PC renumbers on merge), L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline), L3: TillDesk portal (laptop/l3-tilldesk) (+2 more)

### Community 19 - "PRD features and demo prices"
Cohesion: 0.11
Nodes (32): Langfuse Cloud Hobby traces (P1), Sentry free tier errors (P1), Demo-story prices (DEMO_PRICES_EUR), Five-minute demo beats (hook, evidence, act, break it, remember, learn, proof, close), F1 Morning brief, F5 Ask (P1), F8 Mobile owner view, Fix Franzbroetchen margin card (+24 more)

### Community 20 - "Data sources and memory packing"
Cohesion: 0.12
Nodes (29): Context packer (memory.packer.pack), Maven Coffee Shop Sales dataset, Nager.Date public holidays, Open-Meteo weather (Bonn), Seed pipeline (backroom-data, DATA_SEED=44), B3 Memory vs baseline, Open questions (Maven licence, graph library, Localboard), Data attribution (Open-Meteo CC BY 4.0, Nager.Date, Maven) (+21 more)

### Community 22 - "Bench, golden runs and deploy"
Cohesion: 0.12
Nodes (31): Lightsail snapshot before final deploy (2-minute rollback), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), M4 Bench + Deploy, Golden runs (events.json, frames), B2 Learning curve, Benchmarks B1-B5 (+23 more)

### Community 29 - "Memory design and staleness"
Cohesion: 0.13
Nodes (29): Verifier role (LLM_VERIFIER_MODEL, Haiku 5.5, low): preference/rule checks, B5 Number guard benchmark, Brief pipeline: agents for judgment, code for math, F4 Memory (graph, time slider, fact inspector, context pack), Number guard, Temporal knowledge graph (bitemporal facts, supersession, episodes), Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Q: How does memory avoid going stale (+21 more)

### Community 31 - "Repo scripts and tooling"
Cohesion: 0.11
Nodes (25): docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), Lint/test: ruff, pyright (strict on core), pytest, pytest-asyncio, backroom_api/replay (golden-run recorder & player), Root package.json (pnpm workspace root + task runner), pnpm check (ruff, pyright, pytest, web lint, typecheck), pnpm dev (Postgres in Docker + api + portals + next dev in parallel), pnpm dev:lite (api, portals, web without Docker or a database; API reports degraded), pnpm e2e (Playwright e2e of the demo path at 390 px + 1440 px) (+17 more)

### Community 46 - "Verification rules"
Cohesion: 0.13
Nodes (19): Session read order (HANDOVER, BUILD_PLAN, GRAPH_REPORT), Code freeze Fri 13 Nov 11:30, M0 Foundations, M1 Data + Portals, Chaos catalog (nine variant families), Portal labels (en, en_alt, de), Milestone state table, B1 Browser robustness under chaos seeds (+11 more)

### Community 5 - "LLM non-negotiables and adapters"
Cohesion: 0.07
Nodes (39): Daily LLM budget guard (sums today's ledger rows before each call), Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM_<ROLE>_EFFORT override, LLM_CAPS_OFF (switch capability flags off), LLM_PROVIDER env var (openrouter default | anthropic), backroom_api/agents (browser agent, planner, verifier, extractor) (+31 more)

### Community 52 - "Hosting and ADRs"
Cohesion: 0.14
Nodes (11): LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), psycopg 3 synchronous pool called from worker threads, Alternative: browser-use / Stagehand, Alternative: Graphiti + FalkorDB / Neo4j, Alternative: Makefile / just, Likely interview questions, Decisions already made (do not re-litigate), Rule: mock portals only; no bot-protection evasion (+3 more)

### Community 58 - "Demo Script - 5 minutes"
Cohesion: 0.13
Nodes (12): Shared Action interface to the planner, Key API routes, Memory per merchant + cross-merchant best-practices layer, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), backroom_api/skills (compiler, replay, healer, registry), Route /about (architecture for the interview), POST /actions/{id}/approve (Idempotency-Key header to run_id), How this maps to the real Super44 problem (+4 more)

### Community 64 - "Frontend quality bar"
Cohesion: 0.15
Nodes (14): Frontend quality bar (Lighthouse >= 90, reduced motion), M5 Polish + Rehearse, Goals G1-G7, Visual language tokens (crema, roasted caramel), dataviz skill (before any chart), apps/web/src/styles/tokens.css, Accessibility (WCAG AA, keyboard, ARIA live), Design tokens (crema/roasted caramel palette; tokens.css) (+6 more)

### Community 65 - "Pitch, audience and JD problems"
Cohesion: 0.13
Nodes (15): Approve all button, Audience: Super44 founders (Founding Engineer interview), Backroom: agentic back office for a cafe (engine under 'Approve all'), Interviewer (demo user), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration (+7 more)

### Community 7 - "Demo beats and chaos story"
Cohesion: 0.09
Nodes (43): Healer role (LLM_HEAL_MODEL, Haiku 5.5, low): first heal attempt, M2 Browser agent (riskiest), Break it: chaos seed 7 heal beat, F2 Run theater, F3 Skill learning and healing (EXPLORE / REPLAY / HEAL), Interview pitch: what happens after Approve all, What Backroom demonstrates (five hard problems), Check: run task at seed 0 and one chaos seed + metrics (+35 more)

### Community 70 - "Demo story beats"
Cohesion: 0.22
Nodes (13): M3 Memory + Brief + UI, Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Beat 2:40 Remember - time slider, butter fact superseded, Rehearse demo script 3x on deployed URL, Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg), Scripted event: oat milk +9% day -3, Supplier prices & invoices (generated by Grainline) (+5 more)

### Community 72 - "Brief pipeline contracts"
Cohesion: 0.27
Nodes (5): POST /actions/{id}/reject ({reason} to preference episode), Brief pipeline (stream_today, BriefResult), Detector Candidate, Number guard rules 1-9, L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)

### Community 85 - "Run theater streaming"
Cohesion: 0.40
Nodes (6): Route /runs/[id] Run theater, GET /runs/{id}/events (SSE run events), WS /runs/{id}/screen (JPEG frames + cursor), SSE run events (step.started/finished, mode.changed, heal.*, cost.tick, run.finished; Last-Event-ID resumable), Web data layer: TanStack Query, EventSource SSE, WS frames, zod-validated API types, WebSocket JPEG frames + cursor coordinates

### Community 9 - "Grainline portal templates"
Cohesion: 0.13
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

## Ambiguous Edges - Review These
- `F7 Offline replay` → `Replay engine (deterministic Playwright, expect checks, 0 LLM)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references
- `Scripted event: oat milk +9% day -3` → `Card: Reorder oat milk (stock-out, Grainline)`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to

## Knowledge Gaps
- **54 isolated node(s):** `python`, `uvx`, `@playwright/mcp`, `start-mcp-server`, `@upstash/context7-mcp` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 635 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `Sync logs and two-machine flow` to `Memory SQL schema`, `Web zod contracts`, `Portals admin API`, `Contracts overview`, `API response shapes`, `Skill schema fallbacks`, `Run event types`, `Milestones and scope decisions`, `Chaos variants and admin`, `Candidate contract`, `Demo Script - 5 minutes`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Laptop deviations (L-n log, append-only; PC renumbers on merge)` (e.g. with `ADR-15 Two-machine workflow: light tasks on the laptop, heavy tasks on the PC` and `Integration rules (branches, merge --no-ff)`) actually correct?**
  _`Laptop deviations (L-n log, append-only; PC renumbers on merge)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `python`, `uvx`, `@playwright/mcp` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_memory.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05554386703134862 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `Milestones and scope decisions` to `Memory SQL schema`, `test_memory.py`, `Portals admin API`, `Web agent rules`, `generate`, `LLM non-negotiables and adapters`, `Contracts overview`, `Brief pipeline contracts`, `Skill schema fallbacks`, `Sync logs and two-machine flow`, `Stack, infra and CI`, `Hosting and ADRs`, `Chaos variants and admin`, `Service settings`, `Demo Script - 5 minutes`, `XLSX reader`, `Repo scripts and tooling`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `F7 Offline replay` and `Replay engine (deterministic Playwright, expect checks, 0 LLM)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Design tokens (crema/roasted caramel palette; tokens.css)` and `README badges (CI, license, stack)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._