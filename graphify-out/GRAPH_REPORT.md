# Graph Report - backroom laptop work  (2026-11-15)

## Corpus Check
- 174 files · ~94,041 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 9, .lottie 5, .example 1)

## Summary
- 2470 nodes · 6261 edges · 111 communities (98 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 661 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `373a110c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- grainline/routes.py
- test_memory.py
- Web zod contracts
- writers.py
- memory/store.py
- action-card.tsx
- Data sources and memory packing
- guard.py
- Contract
- contract.py
- Grainline portal templates
- Brief pipeline tests
- react
- Skills contract schema
- Data pipeline tests
- Memory design and staleness
- skills-desk.tsx
- test_chaos_render.py
- Demo beats and chaos story
- Recipes data
- TillDesk price editing
- test_grainline.py
- Backend choices (services/api)
- Key API routes
- Web lint and dependencies
- Today page and brief
- L5: temporal memory store, writers, context packer (laptop/l5-memory)
- ci.yml
- Model roles table
- page
- memory-desk.tsx
- stream_today
- Run event types
- Sales data transform
- External data sources
- packer.py
- detectors.py
- L8 part 1: Today screen + Morning edition redesign (laptop/l8-today, Fri 13 Nov)
- Inventory world sim
- Model registry and providers
- Serena project config
- Stack, infra and CI
- Decision Log (ADRs + laptop deviations)
- Backroom Product Requirements Document
- API settings and DB pool
- shadcn components config
- Bench, golden runs and deploy
- Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)
- Sync logs and two-machine flow
- Contracts overview
- TillDesk routes
- Repository layout
- Memory SQL schema
- agent-dock.tsx
- Staff rota data
- client.py
- Candidate
- particles.ts
- memory-desk.tsx
- TypeScript config
- Laptop deviations (L-n log, append-only; PC renumbers on merge)
- pytest
- Handover setup
- re
- LLM capability probe checks
- Sync log: laptop → PC
- Number formatting
- Build Plan (Wed 22:00 -> Fri 11:30 freeze)
- Escalation ladder (deterministic fallbacks, healer, escalation + screenshot, ask_human)
- MCP server config
- agents.py
- LLM non-negotiables and adapters
- Preferences data
- health.py
- steps
- test_contract.py
- jobs
- Demo Script - 5 minutes
- Root package scripts
- build
- backroom_portals/main.py
- README - Backroom overview
- Compose API service
- Compose portals service
- backroom_bench/cli.py
- Parquet writer
- L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)
- Compose build config
- Compose Postgres service
- package.json
- api.py
- L4: data pipeline to Parquet (laptop/l4-data)
- typing
- Deploy flow (CI builds images, push to GHCR, deploy.sh pulls)
- L-54 (L5) Context packs estimate 3 chars/token; standing preferences and rules lead the pack
- Compose root
- L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)
- Product map
- Compose dependencies
- Compose healthcheck
- API and bench packages
- Data and portals packages
- pnpm workspace
- Root package
- schema.py
- Clock

## God Nodes (most connected - your core abstractions)
1. `Laptop deviations (L-n log, append-only; PC renumbers on merge)` - 77 edges
2. `Candidate` - 60 edges
3. `Backroom Product Requirements Document` - 53 edges
4. `Contract` - 52 edges
5. `LLM` - 30 edges
6. `build()` - 30 edges
7. `Settings` - 29 edges
8. `react` - 28 edges
9. `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)` - 28 edges
10. `TodayBrief()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `9.1 Laptop tasks (light)` --references--> `Candidate`  [INFERRED]
  docs/HANDOVER.md → services/api/backroom_api/contracts/candidate.py
- `Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)` --references--> `Candidate`  [INFERRED]
  docs/sync/laptop.md → services/api/backroom_api/contracts/candidate.py
- `Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)` --references--> `TillDeskState`  [INFERRED]
  docs/sync/laptop.md → services/portals/backroom_portals/contract.py
- `System overview (Vercel web, AWS Lightsail docker compose, LLM provider)` --semantically_similar_to--> `README architecture flowchart`  [INFERRED] [semantically similar]
  docs/ARCHITECTURE.md → README.md
- `L8 part 1: Today screen + Morning edition redesign (laptop/l8-today, Fri 13 Nov)` --references--> `TodayBrief()`  [INFERRED]
  docs/sync/laptop.md → apps/web/src/components/today/today-brief.tsx

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

## Communities (111 total, 13 thin omitted)

### Community 0 - "grainline/routes.py"
Cohesion: 0.07
Nodes (43): L1: Grainline portal with TOTP, cart, checkout, invoices (laptop/l1-grainline), Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts), Order, OrderLine, next_weekday(), price_on(), PriceEvent, Product (+35 more)

### Community 1 - "test_memory.py"
Cohesion: 0.17
Nodes (21): at(), butter_prices(), conn(), test_back_dated_fact_is_refused(), test_concurrent_writers_leave_one_open_fact(), second(), test_context_pack_is_ranked_and_within_budget(), test_fact_detail_has_provenance_and_chain() (+13 more)

### Community 2 - "Web zod contracts"
Cohesion: 0.03
Nodes (63): zod@^4.6.7, actionCardSchema, approveResponseSchema, briefSchema, BriefStreamEvent, briefStreamEventSchema, candidateKindSchema, chaosRequestSchema (+55 more)

### Community 3 - "writers.py"
Cohesion: 0.16
Nodes (9): _at(), ingredient_id(), invoices_from_price_change(), pack_sizes(), record_preference(), _rows(), write_invoice(), write_world() (+1 more)

### Community 4 - "memory/store.py"
Cohesion: 0.15
Nodes (13): Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors), EpisodeRef, FactDetail, add_episode(), assert_fact(), Assertion, fact_detail(), facts_as_of() (+5 more)

### Community 5 - "action-card.tsx"
Cohesion: 0.08
Nodes (41): cn@^0.5.2, Error(), Anim(), CafeScene(), ActionCard(), approve(), onDragEnd(), onPointerMove() (+33 more)

### Community 6 - "Data sources and memory packing"
Cohesion: 0.09
Nodes (38): Rule: fictional names only; no Super44 branding in UI, Decision at 19:00: Localboard / Ask in or out, M1 Data + Portals (Wed 23:00-01:30), TillDesk may slip to Thu 08:00, B3 ground truth computed by SQL on same data, Data Sources & Honesty Notes, Simulated inventory (opening + deliveries - sales x BOM), Maven Coffee Shop Sales dataset (+30 more)

### Community 7 - "guard.py"
Cohesion: 0.14
Nodes (15): display(), extract(), Found, _matches(), _rounds_to(), _short(), unmatched(), copy_for() (+7 more)

### Community 8 - "Contract"
Cohesion: 0.09
Nodes (26): 7. API shapes, 8. Memory, ApiError, ApproveResponse, Brief, ChaosRequest, ChaosState, ContextPack (+18 more)

### Community 9 - "contract.py"
Cohesion: 0.07
Nodes (15): chaos_get(), chaos_set(), _chaos_state(), require_admin(), reset(), state(), ChaosRequest, ChaosState (+7 more)

### Community 10 - "Grainline portal templates"
Cohesion: 0.13
Nodes (41): Grainline app shell template, Grainline base layout template, Grainline cart page, cart s_checkout section, cart s_lines section, Grainline catalog page, catalog add_form macro, Grainline checkout page (+33 more)

### Community 11 - "Brief pipeline tests"
Cohesion: 0.11
Nodes (40): CardCopy, LLMPlanner, brief(), candidates(), conn(), data_dir(), FakePlanner, FakeVerifier (+32 more)

### Community 12 - "react"
Cohesion: 0.06
Nodes (42): nextConfig, next@16.4.6, geistMono, geistSans, metadata, RootLayout(), viewport, INTRO_KEY (+34 more)

### Community 13 - "Skills contract schema"
Cohesion: 0.10
Nodes (19): to_sse(), Step, StepChange, load(), make_skill(), test_brief_has_at_most_three_cards(), test_goto_needs_a_path_and_secrets_need_the_exact_form(), test_heal_diff_can_insert_a_step() (+11 more)

### Community 14 - "Data pipeline tests"
Cohesion: 0.10
Nodes (17): _column(), rows(), built(), cached_weather(), maven_zip(), test_build_is_idempotent(), test_build_is_idempotent_for_every_table(), test_cached_weather_and_nager_holidays_are_used() (+9 more)

### Community 15 - "Memory design and staleness"
Cohesion: 0.13
Nodes (27): Beat 3:20 Learn the owner - reject 'max 8%' -> EUR3.45, Beat 2:40 Remember - time slider, butter fact superseded, Q: How does memory avoid going stale, Route / Today, GET /brief/today (cached brief; ?regenerate=1 streams a new one), M3 Memory + Brief + UI (Thu 14:00-19:00), Bitemporal Fact model (valid time + record time), Candidate{kind, evidence[], impact_eur, proposed_action} (+19 more)

### Community 16 - "skills-desk.tsx"
Cohesion: 0.10
Nodes (31): metadata, SkillsPage(), Providers(), SkillDetail(), SkillsDesk(), Stat(), Stats, Steps() (+23 more)

### Community 17 - "test_chaos_render.py"
Cohesion: 0.12
Nodes (18): catalog_html(), dom_hash(), forced(), fresh_client(), signed_in(), skill_path_pages(), test_admin_chaos_sets_reads_and_resets_seeds(), test_admin_chaos_validates_and_needs_the_token() (+10 more)

### Community 18 - "Demo beats and chaos story"
Cohesion: 0.10
Nodes (36): Beat 1:00 Act - approve oat milk, REPLAY $0.000, Beat 1:40 Break it - chaos seed 7 -> HEAL -> skill v2 diff, Chaos seed 7 (German labels, moved nav, cookie modal), Q: What breaks first in production, Chaos variant families (EN/DE label synonyms, DOM order, wrapper depth, random ids, interstitials, delayed render, button/link swap, moved nav), Portal patterns (login, TOTP via pyotp, dashboard, cookie banner, catalog, cart, checkout, order history, PDF invoices), Healer role (LLM_HEAL_MODEL, Haiku 5.5, low): first heal attempt, M2 Browser agent (Thu 09:00-14:00, riskiest) (+28 more)

### Community 19 - "Recipes data"
Cohesion: 0.09
Nodes (32): banana-bread, other_eur, uses, cappuccino, other_eur, uses, croissant, other_eur (+24 more)

### Community 20 - "TillDesk price editing"
Cohesion: 0.16
Nodes (27): parse_price(), change_price(), dom_hash(), fresh(), login(), pages(), state(), test_a_fresh_login_drops_leftover_drafts() (+19 more)

### Community 21 - "test_grainline.py"
Cohesion: 0.19
Nodes (29): client(), has_testid(), login(), state(), test_admin_needs_the_token(), test_bad_cart_input_shows_an_error_not_a_raw_4xx(), test_cancel_is_the_undo_and_only_works_once(), test_cart_update_and_remove() (+21 more)

### Community 22 - "Backend choices (services/api)"
Cohesion: 0.18
Nodes (13): Backend choices (services/api), Runtime: Python 3.12, uv, FastAPI, Pydantic v2, CDP Page.startScreencast live frames, backroom_api/browser (pool, ARIA snapshot observation, executor, screencast), Native local dev (uv run uvicorn --reload; only Postgres in Docker), Route /runs/[id] Run theater, GET /runs/{id}/events (SSE run events), WS /runs/{id}/screen (JPEG frames + cursor) (+5 more)

### Community 23 - "Key API routes"
Cohesion: 0.08
Nodes (22): This is NOT the Next.js you know, Backroom Technical Architecture, Charts (Recharts or visx; dataviz skill, palette validator), Frontend (apps/web) choices, Memory graph lib (@xyflow/react or force-graph; benchmark at ~300 nodes), Key API routes, backroom_api/routes (brief, actions, runs SSE/WS, memory, bench, health), Navigation domain allowlist per run (+14 more)

### Community 24 - "Web lint and dependencies"
Cohesion: 0.05
Nodes (50): eslintConfig, dependencies, @base-ui/react@^1.9.0, class-variance-authority@^0.7.1, @google/model-viewer@4.4.0, @lottiefiles/dotlottie-react@0.21.0, lucide-react@^1.72.0, motion@14.9.0 (+42 more)

### Community 25 - "Today page and brief"
Cohesion: 0.09
Nodes (36): Status, Tone, TONE_DOT, CardStatus, BriefCommands(), BriefSkeleton(), COUNT_WORDS, decisions() (+28 more)

### Community 26 - "L5: temporal memory store, writers, context packer (laptop/l5-memory)"
Cohesion: 0.20
Nodes (4): POST /memory/ingest/invoice (PDF/image to extractor to facts), Neon hosted Postgres (laptop database), L5: temporal memory store, writers, context packer (laptop/l5-memory), OutOfOrderFactError

### Community 27 - "ci.yml"
Cohesion: 0.17
Nodes (10): concurrency, cancel-in-progress, group, name, on, pull_request, push, permissions (+2 more)

### Community 28 - "Model roles table"
Cohesion: 0.11
Nodes (28): Rule: all LLM access through llm/registry.py, Q: Cost at scale, Canonical model IDs mapped per provider (slash IDs pass through on OpenRouter), LLM_<ROLE>_EFFORT override, LLM_PROVIDER env var (openrouter default | anthropic), backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/skills (compiler, replay, healer, registry), claude-fable-5-2 ($8 / $40; thinking always on) (+20 more)

### Community 29 - "page"
Cohesion: 0.10
Nodes (12): 1. Changing a contract, 2. Portals, 3. Chaos catalog, 4. Skills, 9. Fixtures and the drift check, Contracts (L0), Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline), testid() (+4 more)

### Community 30 - "memory-desk.tsx"
Cohesion: 0.11
Nodes (24): AboutPage(), Chapter(), LADDER, metadata, MODELS, BENCHMARKS, BenchPage(), CHECK_LABEL (+16 more)

### Community 31 - "stream_today"
Cohesion: 0.09
Nodes (25): 6. Candidates and the number guard, Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory), Planner, Verifier, action_id(), brief_for_today(), BriefResult, _copy_for() (+17 more)

### Community 32 - "Run event types"
Cohesion: 0.19
Nodes (16): AskHuman, CostTick, _Event, HealAttempt, HealFailed, HealStarted, HealSucceeded, ModeChanged (+8 more)

### Community 33 - "Sales data transform"
Cohesion: 0.10
Nodes (13): _maven_sales(), apply_rainy_saturdays(), load_map(), map_item(), parse_maven(), rebase(), Sale, shift_days() (+5 more)

### Community 34 - "External data sources"
Cohesion: 0.15
Nodes (10): cached(), computed_nrw_holidays(), easter(), _fetch(), holidays(), maven_zip(), _parse_daily(), synthetic_weather() (+2 more)

### Community 35 - "packer.py"
Cohesion: 0.31
Nodes (4): estimate_tokens(), pack(), seeds_for(), _triple()

### Community 36 - "detectors.py"
Cohesion: 0.10
Nodes (19): connect(), Context, _ingredient(), margin_erosion(), _n(), run_all(), _shown(), stockout() (+11 more)

### Community 37 - "L8 part 1: Today screen + Morning edition redesign (laptop/l8-today, Fri 13 Nov)"
Cohesion: 0.17
Nodes (14): EUR, Figure(), SUFFIX, prefersReducedMotion(), Frontend quality bar (Lighthouse >= 90, reduced motion), apps/web/src/styles/tokens.css, Fonts via next/font: Newsreader (display + text cut), Geist, Geist Mono, Accessibility (WCAG AA, keyboard, ARIA live) (+6 more)

### Community 38 - "Inventory world sim"
Cohesion: 0.19
Nodes (9): daily_usage(), inventory(), load_recipes(), recipe_rows(), rota(), supplier_prices(), unit_cost(), test_franzbroetchen_unit_cost_tells_the_story() (+1 more)

### Community 39 - "Model registry and providers"
Cohesion: 0.09
Nodes (24): build_async_client(), canonical_model_id(), Caps, caps_for(), cost_usd(), is_configured(), LLMNotConfiguredError, role_config() (+16 more)

### Community 40 - "Serena project config"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 41 - "Stack, infra and CI"
Cohesion: 0.19
Nodes (19): Browser pool (1 Chromium, 2 contexts), Caddy (TLS + routing, auto-HTTPS), Deploy freeze: no deploys after Fri 11:30, infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), FastAPI api service (orchestrator, agents, memory, SSE/WS), Hosting fallback (Hetzner CX22 / Fly.io with the same compose file), Hosting and operations (cheap, reliable), AWS Lightsail 2 GB / 2 vCPU + 2 GB swap, docker compose (+11 more)

### Community 42 - "Decision Log (ADRs + laptop deviations)"
Cohesion: 0.13
Nodes (14): Q: Why not browser-use / Stagehand, LLM_CAPS_OFF (switch capability flags off), OpenRouter ~5.5% credit fee (OPENROUTER_FEE_PCT), Provider openrouter (default; base_url openrouter.ai/api, auth_token, X-Title/HTTP-Referer headers), Decision Log (ADRs + laptop deviations), Alternative: browser-use / Stagehand, Alternative: Graphiti + FalkorDB / Neo4j, Alternative: Makefile / just (+6 more)

### Community 43 - "Backroom Product Requirements Document"
Cohesion: 0.10
Nodes (31): Langfuse Cloud Hobby traces (P1), Sentry free tier errors (P1), M3 Memory + Brief + UI, Demo-story prices (DEMO_PRICES_EUR), Open or synthetic data only ('Synthetic' chip in UI), Five-minute demo beats (hook, evidence, act, break it, remember, learn, proof, close), Action card (impact, why, evidence chips, Approve/Review/Not now), B2 Learning curve (+23 more)

### Community 44 - "API settings and DB pool"
Cohesion: 0.16
Nodes (8): get_settings(), Settings, make_pool(), ping(), create_app(), lifespan(), test_health_reports_degraded_when_dependencies_are_down(), connect()

### Community 45 - "shadcn components config"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 46 - "Bench, golden runs and deploy"
Cohesion: 0.12
Nodes (30): ui-ux-pro-max skill, Beat 4:00 Proof - /bench, Lightsail snapshot before final deploy (2-minute rollback), Route /bench, bench package backroom_bench (script backroom-bench; results/*.json committed), pnpm bench (uv run backroom-bench all: B1-B5 to bench/results/*.json), Code freeze Fri 13 Nov 11:30 (snapshot, no deploys), Record golden runs -> replay mode (+22 more)

### Community 47 - "Non-negotiables (LLM via registry, no LLM numbers, secrets, budget)"
Cohesion: 0.10
Nodes (22): CLAUDE.md agent guide, CLAUDE.md - Backroom agent guide, Check: start service + curl route, Check: run task at seed 0 and one chaos seed + metrics, Check: DOM-hash test per chaos seed, Check: Lighthouse via web-perf skill, claude-api skill (load before Anthropic SDK code), context7 for library docs (+14 more)

### Community 48 - "Sync logs and two-machine flow"
Cohesion: 0.18
Nodes (13): Handover, Full setup (Docker, pnpm dev), Integration rules (branches, merge --no-ff), Laptop setup (no Docker, no Chromium, pnpm dev:lite), Laptop tasks L0-L13, Neon hosted Postgres for the laptop, PC tasks H1-H9, Suggested order and critical path (+5 more)

### Community 49 - "Contracts overview"
Cohesion: 0.13
Nodes (19): Portals admin API (/_admin/chaos, state, reset), Brief pipeline (stream_today, BriefResult), Detector Candidate, Data tables (Parquet, cli.SCHEMAS), Detectors (stock-out, margin, weather) and weekly impact, Fixtures and the drift check, Memory writers (assert_fact, write_world, write_invoice), Number guard rules 1-9 (+11 more)

### Community 50 - "TillDesk routes"
Cohesion: 0.30
Nodes (13): _authed(), home(), item_edit(), item_save(), login(), login_submit(), logout(), menu() (+5 more)

### Community 51 - "Repository layout"
Cohesion: 0.11
Nodes (26): Check: pytest + ruff + pyright for Python logic, Check: Playwright MCP screenshots 390/1440 light+dark, no console errors, Stack and commands, Verification rules (verify before next step, state evidence), CI: GitHub Actions (lint, typecheck, unit tests, compose-based e2e), docs/ (PRD, ARCHITECTURE, BUILD_PLAN, DATA, DEMO_SCRIPT, DECISIONS), Lint/test: ruff, pyright (strict on core), pytest, pytest-asyncio, backroom_api/memory (schema, writers, supersession, context packer) (+18 more)

### Community 52 - "Memory SQL schema"
Cohesion: 0.19
Nodes (15): 'As of' query predicate (valid_from <= t and valid_to null or > t), Index fact (subject_id, predicate, valid_from desc), Memory schema sketch (entity, episode, fact), Table entity (type, name, attrs, optional embedding vector(384), fastembed bge-small P1), Table episode (invoice | approval | rejection | chat | run | seed), Table fact (subject, predicate, object/value, valid_from/valid_to, recorded_at, source_episode, confidence), Memory contract (bitemporal facts, supersession), entity (+7 more)

### Community 53 - "agent-dock.tsx"
Cohesion: 0.09
Nodes (30): AgentDock(), PlayableRun, PlayingRun(), Ring(), SPRING, Mode, MODE_STYLE, Playback (+22 more)

### Community 54 - "Staff rota data"
Cohesion: 0.11
Nodes (18): hourly_wage_eur, end, staff, start, shifts, saturday, sunday, weekday (+10 more)

### Community 55 - "client.py"
Cohesion: 0.21
Nodes (3): LLMResult, CallRecord, Cost

### Community 56 - "Candidate"
Cohesion: 0.19
Nodes (13): Candidate, candidates(), data_dir(), numbers(), test_a_date_the_data_was_not_built_for_is_refused(), test_all_three_detectors_fire(), test_every_card_lists_its_impact_and_ids_are_deterministic(), test_franzbroetchen_margin_story_comes_out_of_the_data() (+5 more)

### Community 57 - "particles.ts"
Cohesion: 0.11
Nodes (23): SceneDriver(), IntroPlayer(), ModelViewer, AgentDock, CafeScene, CommandPalette, IntroPlayer, ParticleLayer (+15 more)

### Community 58 - "memory-desk.tsx"
Cohesion: 0.13
Nodes (28): EmptyState(), edgePath(), FactValue(), isoDay(), MemoryDesk(), play(), writeUrl(), plainValue() (+20 more)

### Community 59 - "TypeScript config"
Cohesion: 0.12
Nodes (17): compilerOptions, allowImportingTsExtensions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib (+9 more)

### Community 60 - "Laptop deviations (L-n log, append-only; PC renumbers on merge)"
Cohesion: 0.14
Nodes (8): POST /_admin/chaos {portal, seed} (PORTALS_ADMIN_TOKEN header), TillDesk (mock till / menu portal), POST /chaos {portal, seed} (dev/demo; forwards to portals /_admin/chaos), Rules for the agent runner (fresh context, aria-busy, hamburger, links, exact names), Laptop deviations (L-n log, append-only; PC renumbers on merge), Brief AC: <1.5 s cached, <15 s cold, L2: chaos engine with 9 families (laptop/l2-chaos), L3: TillDesk portal (laptop/l3-tilldesk)

### Community 61 - "pytest"
Cohesion: 0.20
Nodes (9): BudgetExceededError, fake_message(), FakeClient, FakeMessages, make_llm(), test_budget_guard_blocks_before_calling(), test_caps_off_strips_effort_and_strict(), test_create_sends_wire_model_and_effort_and_records_cost() (+1 more)

### Community 62 - "Handover setup"
Cohesion: 0.12
Nodes (17): 1. Where we are, 2. Setup, 2a. Full setup (this PC, or any machine with Docker), 2b. Laptop setup (light: no Docker, no Chromium), 3. Starting a Claude Code session on the new machine, 4. Decisions already made (do not re-litigate), 5. Working agreements with the user, 6. Windows environment quirks (the user's machine) (+9 more)

### Community 63 - "re"
Cohesion: 0.23
Nodes (6): code_at(), default_secret(), now_code(), verify(), test_totp_cli_prints_a_valid_code(), test_totp_matches_the_rfc_6238_vector()

### Community 64 - "LLM capability probe checks"
Cohesion: 0.17
Nodes (14): Check, check_basic(), check_effort(), check_prompt_cache(), check_streaming(), check_strict_tools(), check_structured_outputs(), _git_sha() (+6 more)

### Community 65 - "Sync log: laptop → PC"
Cohesion: 0.29
Nodes (6): Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data), Sync log: laptop → PC, Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe, Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts, Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos), Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)

### Community 66 - "Number formatting"
Cohesion: 0.18
Nodes (17): CardVisual(), EvidenceBars(), MarginScale(), num(), plain, SPRING, StockCells(), EvidenceNumber (+9 more)

### Community 67 - "Build Plan (Wed 22:00 -> Fri 11:30 freeze)"
Cohesion: 0.18
Nodes (12): Code freeze Fri 13 Nov 11:30, Build Plan (Wed 22:00 -> Fri 11:30 freeze), M0 Foundations, M1 Data + Portals, M2 Browser agent (riskiest), M5 Polish + Rehearse, Chaos catalog (nine variant families), Portal labels (en, en_alt, de) (+4 more)

### Community 68 - "Escalation ladder (deterministic fallbacks, healer, escalation + screenshot, ask_human)"
Cohesion: 0.16
Nodes (7): Beat 4:40 Close - /about, model table, adapters, Shared Action interface to the planner, Memory per merchant + cross-merchant best-practices layer, Route /about (architecture for the interview), Provider anthropic (direct; full features incl. server-side refusal fallbacks), Server-side refusal fallbacks (beta server-side-fallback-2026-07-01, anthropic provider only), How this maps to the real Super44 problem

### Community 69 - "MCP server config"
Cohesion: 0.16
Nodes (14): cmd, python, uvx, chrome-devtools, context7, figma, graphify, playwright (+6 more)

### Community 70 - "agents.py"
Cohesion: 0.13
Nodes (11): BriefLLMError, candidate_view(), Draft, _Model, _parse(), Plan, _system(), Verdict (+3 more)

### Community 71 - "LLM non-negotiables and adapters"
Cohesion: 0.15
Nodes (11): Check: one real LLM call (stop_reason, $, cache_read > 0), Daily LLM budget guard (sums today's ledger rows before each call), Capability probe (one cheap Haiku call per feature; M0 gate), Cost meter (per-call ledger row: provider, role, model, tokens, cache, $, stop_reason, run_id), LLM spend ledger var/llm_ledger.jsonl (LLM_LEDGER_PATH), backroom_api/llm (model registry, client, cost meter, budget guard), pnpm probe:llm (uv run backroom-bench probe), bench/results/provider_probe.json (+3 more)

### Community 72 - "Preferences data"
Cohesion: 0.15
Nodes (12): business_rules, id, rule, text, preferences, id, rule, since_days_ago (+4 more)

### Community 73 - "health.py"
Cohesion: 0.23
Nodes (3): health(), _portals_ok(), _postgres_ok()

### Community 74 - "steps"
Cohesion: 0.24
Nodes (13): steps, steps, id, if, name, run, uses, with (+5 more)

### Community 75 - "test_contract.py"
Cohesion: 0.17
Nodes (9): pick_variants(), Label, test_demo_seed_is_german_with_moved_nav_and_cookie_banner(), test_demo_story_ids_and_prices(), test_every_label_has_three_forms_and_a_german_one(), test_negative_seed_is_rejected(), test_routes_are_unique_and_under_one_prefix(), test_same_seed_same_variants_and_seeds_differ() (+1 more)

### Community 76 - "jobs"
Cohesion: 0.20
Nodes (10): name, runs-on, jobs, docs, python, web, name, runs-on (+2 more)

### Community 77 - "Demo Script - 5 minutes"
Cohesion: 0.17
Nodes (16): Beat 0:30 Evidence drawer (Franzbroetchen margin 71% -> 68%), Beat 0:00 Hook - Today 3 cards, Q: Cloudflare / bot protection on real portals, Rehearse demo script 3x on deployed URL, Scripted event: butter +16% day -9 (EUR7.10 -> 8.24/kg), Scripted event: oat milk +9% day -3, Supplier prices & invoices (generated by Grainline), Demo Script - 5 minutes (+8 more)

### Community 78 - "Root package scripts"
Cohesion: 0.17
Nodes (12): scripts, bench, check, check:py, dev, dev:api, dev:db, dev:lite (+4 more)

### Community 79 - "build"
Cohesion: 0.32
Nodes (4): build(), next_saturday(), _notes(), test_story_numbers_come_out_of_the_built_data()

### Community 80 - "backroom_portals/main.py"
Cohesion: 0.15
Nodes (3): get_settings(), Settings, create_app()

### Community 81 - "README - Backroom overview"
Cohesion: 0.17
Nodes (12): Add Live demo + Benchmarks badges to README, Backroom: agentic back office for a cafe (engine under 'Approve all'), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration, JD problem 4: agentic self-improvement, Why this exists: Super44 JD hard problems (+4 more)

### Community 82 - "Compose API service"
Cohesion: 0.20
Nodes (10): env_file, environment, expose, profiles, restart, volumes, DATABASE_URL, LLM_LEDGER_PATH (+2 more)

### Community 83 - "Compose portals service"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, profiles, restart, volumes, API_HOST (+2 more)

### Community 85 - "Parquet writer"
Cohesion: 0.29
Nodes (3): read(), write(), test_inventory_covers_only_the_order_window()

### Community 86 - "L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)"
Cohesion: 0.40
Nodes (3): exclude, include, check:web

### Community 87 - "Compose build config"
Cohesion: 0.25
Nodes (9): build, context, dockerfile, build, env_file, expose, profiles, restart (+1 more)

### Community 88 - "Compose Postgres service"
Cohesion: 0.22
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, ports, restart, volumes (+1 more)

### Community 89 - "package.json"
Cohesion: 0.25
Nodes (8): description, devDependencies, concurrently@^9.1.0, name, packageManager, private, version, concurrently

### Community 90 - "api.py"
Cohesion: 0.20
Nodes (5): checked(), extract(), ExtractedRule, record_rejection(), test_extracted_rules_need_the_owners_words()

### Community 91 - "L4: data pipeline to Parquet (laptop/l4-data)"
Cohesion: 0.21
Nodes (8): DuckDB over Parquet (sales analytics), backroom_api/analytics (DuckDB queries, stockout/margin/weather detectors), data package backroom_data (script backroom-data; raw data not committed), pnpm seed (uv run backroom-data all: download, transform, load Postgres + Parquet), Sync entry format (Done / Verify / Needs from PC / Notes), Independent audit pass per laptop task (blockers and should-fix items, all fixed), L4: data pipeline to Parquet (laptop/l4-data), L6: DuckDB detectors and deterministic pricing (laptop/l6-detectors)

### Community 93 - "Deploy flow (CI builds images, push to GHCR, deploy.sh pulls)"
Cohesion: 0.33
Nodes (5): Deploy flow (CI builds images, push to GHCR, deploy.sh pulls), infra/deploy.sh (ssh, compose pull, compose up, wait for health, smoke test), GHCR container registry, infra/ (docker-compose.yml, Caddyfile, deploy.sh, Lightsail notes), api image FROM mcr.microsoft.com/playwright/python (noble)

### Community 95 - "Compose root"
Cohesion: 0.29
Nodes (6): name, services, volumes, apidata, caddydata, pgdata

### Community 96 - "L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)"
Cohesion: 0.16
Nodes (6): L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief), LLMVerifier, rules_from_memory(), weekday_index(), _weekdays(), test_weekday_names_are_normalised()

### Community 97 - "Product map"
Cohesion: 0.33
Nodes (5): rules, detail, item, type, store

### Community 98 - "Compose dependencies"
Cohesion: 0.40
Nodes (5): depends_on, portals, postgres, condition, condition

### Community 99 - "Compose healthcheck"
Cohesion: 0.40
Nodes (5): interval, retries, test, timeout, healthcheck

### Community 109 - "schema.py"
Cohesion: 0.19
Nodes (8): L0: shared contracts (laptop/l0-contracts), CssFallback, Expect, LabelFallback, Postcondition, SkillStats, TextFallback, reorder_steps()

## Ambiguous Edges - Review These
- `Card: Reorder oat milk (stock-out, Grainline)` → `Scripted event: oat milk +9% day -3`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **50 isolated node(s):** `backroom-api`, `backroom-bench`, `backroom-data`, `backroom-portals`, `backroom` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 667 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `L0: shared contracts (laptop/l0-contracts)` connect `schema.py` to `Run event types`, `grainline/routes.py`, `Web zod contracts`, `Contract`, `ci.yml`, `contract.py`, `typing`, `Sync logs and two-machine flow`, `Contracts overview`, `Memory SQL schema`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `L4: data pipeline to Parquet (laptop/l4-data)`, `Laptop deviations (L-n log, append-only; PC renumbers on merge)`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Candidate` (e.g. with `Contracts (L0)` and `L-45 (L6) Weekly EUR impact defined per card kind; cards ranked by it`) actually correct?**
  _`Candidate` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backroom-api`, `backroom-bench`, `backroom-data` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `grainline/routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06948798328108673 - nodes in this community are weakly interconnected._
- **Why does `Laptop deviations (L-n log, append-only; PC renumbers on merge)` connect `Laptop deviations (L-n log, append-only; PC renumbers on merge)` to `grainline/routes.py`, `Data sources and memory packing`, `Contract`, `Memory design and staleness`, `skills-desk.tsx`, `Demo beats and chaos story`, `Key API routes`, `L5: temporal memory store, writers, context packer (laptop/l5-memory)`, `ci.yml`, `memory-desk.tsx`, `stream_today`, `Sales data transform`, `L8 part 1: Today screen + Morning edition redesign (laptop/l8-today, Fri 13 Nov)`, `Decision Log (ADRs + laptop deviations)`, `Backroom Product Requirements Document`, `Bench, golden runs and deploy`, `Sync logs and two-machine flow`, `Contracts overview`, `Repository layout`, `Memory SQL schema`, `agent-dock.tsx`, `Candidate`, `Sync log: laptop → PC`, `LLM non-negotiables and adapters`, `L-3 (L0) Contract-check wiring outside laptop ownership (check:web, contracts script, allowImportingTsExtensions, CI step)`, `L4: data pipeline to Parquet (laptop/l4-data)`, `L-54 (L5) Context packs estimate 3 chars/token; standing preferences and rules lead the pack`, `L7: brief pipeline with planner, verifier, number guard, reject-to-preference (laptop/l7-brief)`, `schema.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Card: Reorder oat milk (stock-out, Grainline)` and `Scripted event: oat milk +9% day -3`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._