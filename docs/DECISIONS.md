# Decision Log

Short ADRs. Newest at the bottom. Format: **Decision**, then *why*, then *alternatives*.

1. **Mock portals instead of real sites.** *Why:* reproducible benchmarks, no credentials, legal, can't break during the interview, and the chaos engine is only possible on sites we control. *Alt:* real sandbox sites (flaky, ToS issues).
2. **No bot-protection evasion.** *Why:* ToS and ethics; not a durable strategy. Human handoff is better UX. *Alt:* stealth browsers (rejected).
3. **Own browser-agent loop on Playwright + ARIA snapshots.** *Why:* skill compilation and healing are the differentiator and need full control and metrics. *Alt:* browser-use, Stagehand.
4. **Temporal graph in Postgres (custom) instead of Graphiti/Neo4j.** *Why:* one datastore, bitemporal SQL is simple, deterministic writers for structured data (no per-row LLM extraction cost), fewer moving parts to break. *Alt:* Graphiti + FalkorDB (richer, but LLM-heavy ingest and another service).
5. **"Agents for judgment, code for math."** *Why:* trust. LLMs never originate numbers, and the number guard enforces it. *Alt:* LLM-computed insights (hallucination risk).
6. **Cheap-by-default model ladder (Haiku 5.5 worker, Sonnet 5.5 planner), env-swappable.** *Why:* demo cost and latency; also a cost-aware multi-model talking point. *Alt:* Opus 5.5 everywhere (≈2× Sonnet; benchmark it in B4).
7. **Vercel (web) + AWS Lightsail (backend, docker compose) + Caddy/sslip.io.** *Why:* their stack (Vercel + AWS), ~$12/mo, one box, two-minute rollback via snapshot. *Alt:* App Runner/ECS (more setup), Fly/Hetzner (not their stack).
