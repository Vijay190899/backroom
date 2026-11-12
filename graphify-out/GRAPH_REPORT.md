# Graph Report - .  (2026-11-11)

## Corpus Check
- Corpus is ~24,148 words - fits in a single context window. You may not need a graph.

## Summary
- 350 nodes · 902 edges · 9 communities detected
- Extraction: 83% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Browser Agent, Skills and Healing|Browser Agent, Skills and Healing]]
- [[_COMMUNITY_Frontend, API Routes and Memory Schema|Frontend, API Routes and Memory Schema]]
- [[_COMMUNITY_Data, Portals and Chaos Engine|Data, Portals and Chaos Engine]]
- [[_COMMUNITY_LLM Provider and Model Layer|LLM Provider and Model Layer]]
- [[_COMMUNITY_Brief Pipeline and Agents|Brief Pipeline and Agents]]
- [[_COMMUNITY_Hosting and Deploy|Hosting and Deploy]]
- [[_COMMUNITY_Task Runner, CI and Verification|Task Runner, CI and Verification]]
- [[_COMMUNITY_Runtime Services|Runtime Services]]
- [[_COMMUNITY_Goals and JD Mapping|Goals and JD Mapping]]

## God Nodes (most connected - your core abstractions)
1. `Backroom Product Requirements Document` - 27 edges
2. `M3 Memory + Brief + UI (Thu 14:00-19:00)` - 19 edges
3. `Demo Script - 5 minutes` - 18 edges
4. `M2 Browser agent (Thu 09:00-14:00, riskiest)` - 18 edges
5. `M4 Bench + Deploy (Thu 19:00-23:30)` - 18 edges
6. `Heal ladder (fallbacks -> healer -> escalation -> ask_human)` - 17 edges
7. `Temporal knowledge graph (memory)` - 17 edges
8. `FastAPI api service (orchestrator, agents, memory, SSE/WS)` - 17 edges
9. `README - Backroom overview` - 15 edges
10. `Browser agent` - 15 edges

## Surprising Connections (you probably didn't know these)
- `README architecture flowchart` --semantically_similar_to--> `System overview (Vercel web + Lightsail compose)`  [INFERRED] [semantically similar]
  README.md → docs/ARCHITECTURE.md
- `Check: pytest + ruff + pyright for Python logic` --semantically_similar_to--> `pnpm check (ruff, pyright, pytest, web lint, typecheck)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/ARCHITECTURE.md
- `README badges (CI, license, stack)` --references--> `Design tokens (crema/roasted caramel palette; tokens.css)`  [AMBIGUOUS]
  README.md → docs/PRD.md
- `Check: Playwright MCP screenshots 390/1440 light+dark, no console errors` --semantically_similar_to--> `pnpm e2e (Playwright e2e 390/1440 px)`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/ARCHITECTURE.md
- `Models (swappable) table` --semantically_similar_to--> `Model roles table`  [INFERRED] [semantically similar]
  README.md → docs/ARCHITECTURE.md

## Hyperedges (group relationships)
- **Brief pipeline: detectors -> planner -> verifier -> number guard** — prd_detectors, prd_candidate, prd_planner, prd_verifier, prd_number_guard, architecture_route_brief_today [EXTRACTED 1.00]
- **Skill lifecycle: explore -> compile -> replay -> heal -> new version** — prd_explore_mode, prd_skill_compiler, prd_replay_engine, prd_heal_ladder, prd_skill_versioning, architecture_escalation_ladder [EXTRACTED 1.00]
- **Preference learning: reject with reason -> episode -> extractor -> Preference fact -> verifier -> regenerated card** — prd_franzbroetchen_story, architecture_route_reject, prd_episodes, prd_extractor, prd_preference_fact, prd_verifier, demo_beat_learn_owner [INFERRED 0.85]

## Communities

### Community 0 - "Browser Agent, Skills and Healing"
Cohesion: 0.07
Nodes (58): CDP Page.startScreencast live frames, Chaos variant families (labels EN/DE, DOM order, interstitials, delays, moved nav), backroom_api/skills (compiler, replay, healer, registry), Healer role (LLM_HEAL_MODEL, Haiku 5.5, low), Rough budget (explore ~$0.008, brief ~$0.10, build+bench $15-30), Security notes (vault, allowlist, idempotency, no PII), Skills shared per portal across merchants (network compounding), SSE run events (step.*, mode.changed, heal.*, cost.tick) (+50 more)

### Community 1 - "Frontend, API Routes and Memory Schema"
Cohesion: 0.07
Nodes (49): 'As of' query predicate, Charts (Recharts or visx, dataviz skill), Frontend stack (Next.js, Tailwind v4, shadcn/ui, Motion, TanStack Query), Memory graph lib (@xyflow/react or force-graph), Key API routes, Memory SQL schema sketch, backroom_api/memory (schema, writers, supersession, context packer), backroom_api/routes (brief, actions, runs, memory, bench, health) (+41 more)

### Community 2 - "Data, Portals and Chaos Engine"
Cohesion: 0.08
Nodes (47): Chaos engine (seeded RNG variant catalog), data package backroom_data (script backroom-data), pnpm seed (uv run backroom-data all), Portals service (FastAPI + Jinja2, backroom_portals), POST /chaos {portal, seed}, Why portals are plain 'legacy SaaS' (contrast makes Backroom UI pop), Decision at 19:00: Localboard / Ask in or out, M1 Data + Portals (Wed 23:00-01:30) (+39 more)

### Community 3 - "LLM Provider and Model Layer"
Cohesion: 0.09
Nodes (44): API rules for current models (adaptive thinking, no sampling params, no forced tool_choice, check stop_reason, stream), Canonical model IDs mapped per provider (slash IDs pass through), Capability flags registry.CAPS[provider] (effort, strict_tools, prompt_cache, ...), Capability probe (one cheap Haiku call per feature -> provider_probe.json), Cost meter (per-call provider/role/model/tokens/$), LLM_<ROLE>_EFFORT override, Escalation ladder (deterministic -> worker -> escalation -> ask_human), LLM_PROVIDER env var (+36 more)

### Community 4 - "Brief Pipeline and Agents"
Cohesion: 0.08
Nodes (42): Shared Action interface to the planner, Adapter strategy: API-first, browser skills for long tail, backroom_api/agents (browser agent, planner, verifier, extractor), backroom_api/analytics (DuckDB queries, detectors), Route /about (architecture for interview), Portal patterns (login->TOTP->dashboard, cart, checkout, PDF invoices), GET /brief/today, M3 gate (full DEMO_SCRIPT works locally end-to-end) (+34 more)

### Community 5 - "Hosting and Deploy"
Cohesion: 0.09
Nodes (40): Caddy (TLS + routing, sslip.io auto-HTTPS), infra/deploy.sh (ssh, pull, compose up, health, smoke), infra/docker-compose.yml (postgres+pgvector, api, portals, caddy), Hosting and operations, Hosting fallback (Hetzner CX22 / Fly.io), infra/ (docker-compose.yml, Caddyfile, deploy.sh), Langfuse Cloud Hobby traces (P1), AWS Lightsail 2 GB/2 vCPU + 2 GB swap, docker compose (+32 more)

### Community 6 - "Task Runner, CI and Verification"
Cohesion: 0.08
Nodes (40): CI: GitHub Actions (lint, typecheck, unit, compose e2e), claude-fable-5-2 ($8/$40), pnpm check (ruff, pyright, pytest, web lint, typecheck), pnpm dev (postgres docker + api + portals + next dev), pnpm e2e (Playwright e2e 390/1440 px), pnpm workspace (apps/web), Repository layout, Task runner: root package.json pnpm scripts (+32 more)

### Community 7 - "Runtime Services"
Cohesion: 0.16
Nodes (19): Backend choices table, Browser pool (1 Chromium, 2 contexts, queue), Backroom Technical Architecture, DuckDB / Parquet (sales analytics), FastAPI api service (orchestrator, agents, memory, SSE/WS), Memory per merchant + cross-merchant best-practices layer, backroom_api/browser (pool, aria observation, executor, screencast), Postgres 16 + pgvector (memory graph, runs, skills) (+11 more)

### Community 8 - "Goals and JD Mapping"
Cohesion: 0.18
Nodes (11): Add Live demo + Benchmarks badges to README, Backroom: agentic back office for a cafe (engine under 'Approve all'), JD problem 5: UX for agentic systems, JD problem 1: browser automation that actually works, JD problem 3: memory and context that compound, JD problem 2: multi-agent orchestration, Why this exists: Super44 JD hard problems, README architecture flowchart (+3 more)

## Ambiguous Edges - Review These
- `Card: Reorder oat milk (stock-out, Grainline)` → `Scripted event: oat milk +9% day -3`  [AMBIGUOUS]
  docs/DATA.md · relation: conceptually_related_to
- `Replay engine (deterministic Playwright, expect checks, 0 LLM)` → `F7 Offline replay (golden runs, DEMO_MODE=replay)`  [AMBIGUOUS]
  docs/PRD.md · relation: semantically_similar_to
- `Design tokens (crema/roasted caramel palette; tokens.css)` → `README badges (CI, license, stack)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **16 isolated node(s):** `Brief AC: <1.5 s cached, <15 s cold`, `Accessibility (WCAG AA, keyboard, ARIA live)`, `Skill diff rendered like a code review`, `Template copy fallback`, `Why portals are plain 'legacy SaaS' (contrast makes Backroom UI pop)` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Card: Reorder oat milk (stock-out, Grainline)` and `Scripted event: oat milk +9% day -3`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Replay engine (deterministic Playwright, expect checks, 0 LLM)` and `F7 Offline replay (golden runs, DEMO_MODE=replay)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Design tokens (crema/roasted caramel palette; tokens.css)` and `README badges (CI, license, stack)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Backroom Product Requirements Document` connect `Browser Agent, Skills and Healing` to `Frontend, API Routes and Memory Schema`, `Data, Portals and Chaos Engine`, `LLM Provider and Model Layer`, `Brief Pipeline and Agents`, `Hosting and Deploy`, `Task Runner, CI and Verification`, `Goals and JD Mapping`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `Backroom Technical Architecture` connect `Runtime Services` to `Browser Agent, Skills and Healing`, `Frontend, API Routes and Memory Schema`, `Data, Portals and Chaos Engine`, `LLM Provider and Model Layer`, `Hosting and Deploy`, `Task Runner, CI and Verification`, `Goals and JD Mapping`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `README - Backroom overview` connect `Goals and JD Mapping` to `Browser Agent, Skills and Healing`, `Frontend, API Routes and Memory Schema`, `Data, Portals and Chaos Engine`, `LLM Provider and Model Layer`, `Brief Pipeline and Agents`, `Hosting and Deploy`, `Task Runner, CI and Verification`, `Runtime Services`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Demo Script - 5 minutes` (e.g. with `Success criteria for the interview` and `Interviewer (demo user)`) actually correct?**
  _`Demo Script - 5 minutes` has 2 INFERRED edges - model-reasoned connections that need verification._