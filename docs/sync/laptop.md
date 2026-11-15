# Sync log: laptop → PC

Only the **laptop** edits this file (the PC never does, so it cannot conflict). Newest entry first. One entry per finished task or branch.

Entry format:

```
## Sun 15 Nov 2026 · L8 follow-up (glass panels on every page; drawings thicker again) · branch laptop/l9-run-theater
Done:
- Memory, Skills, Bench and About frame their sections in the same glass panels as Today's cards: a new `.panel` utility (card radius and padding) used as `glass panel`. The inner ink rules became hairlines.
- The background café drawings are 40% thicker again (1.75 → 2.45 px on screen).
Verify:
- Headless Chrome on each page: the panels compute a 20 px radius, 28 px padding and the shadow (Memory 3, Skills 2, Bench 2, About 6); no sideways scroll at 390 px; screenshots checked.
- `pnpm check` is green.

## Sun 15 Nov 2026 · L8 follow-up (thicker café drawings) · branch laptop/l9-run-theater
Done:
- The background café drawings' lines are 40% thicker (1.25 → 1.75 px on screen); the owner found them almost invisible. The intro stays on phones too (owner's call; `/` on phones stays about 71 on a first visit).
Verify:
- The rendered `stroke-width` is 1.4 at 30 px and 2.33 at 18 px (absolute 1.75 px); screenshot checked. `pnpm check` is green.

## Sun 15 Nov 2026 · L13 (part 1: bench page reads results; demo script) · branch laptop/l9-run-theater
Done:
- `/bench` reads `bench/results/b1,b2,b3,b5.json` at build time (`lib/bench-results.ts`) and shows each benchmark's measured headline with n, date and git SHA. A missing file, or one with `fake: true`, shows "Not run yet".
- `docs/DEMO_SCRIPT.md` follows the current UI: the intro, the dock → run theater, the chaos picker in the theater, the bench headlines.
Verify:
- With L11's fake results copied in as non-fake, `/bench` showed every headline. Without them, "Not run yet" stays.
- `pnpm check` is green.
Needs from PC:
- After H7 commits `bench/results/*.json`, a rebuild shows them; no code change needed.

## Sun 15 Nov 2026 · L11 · branch laptop/l11-bench (stacked on laptop/l7-brief)
Done:
- Bench harness (`bench/backroom_bench`), DECISIONS L-83:
  - B1: task × chaos seed × cold/warm, with success %, p50/p95, calls, tokens, $ and the target headline;
  - B2: 20-run learning curve with redesigns at runs 8 and 15;
  - B3: 30 questions with SQL ground truth on the seeded data, three arms, ±1% grading, an LLM answerer with a cached records prefix;
  - B5: guard verdicts plus independent re-verification of displayed numbers.
- Results JSON carries model ids per role, seeds, n, date, git SHA, a `fake` flag and the OpenRouter fee line.
- CLI: `backroom-bench all|b1|b2|b3|b5 [--fake] [--runner m:f] [--pack m:f] [--briefs DIR]`.
Verify:
- `uv run pytest -q bench/tests`: 6 passed (B1 grid, B2 spikes at 8 and 15, grading, B3 on the real ground truth, results header).
- `uv run backroom-bench all --fake --seeds 3` writes `var/bench-fake/b1,b2,b3,b5.json`.
- One real B3 call pair: both answers correct, `stop_reason` end_turn, the second call read 138,126 cached tokens, and both are in the ledger.
- ruff and pyright are clean.
- Audit (Sonnet): no blockers; 5 should-fix items and 3 nits, all fixed:
  - real runs never grade fixture briefs;
  - a skipped benchmark exits non-zero, and a real B3 needs `--pack`;
  - the B2 header carries its seeds, and its headline adds `warm_success`, `all_ok` and `redesigns_healed`;
  - the git SHA is marked `-dirty`;
  - answers get `max_tokens` 1024 and record `stop_reason`;
  - the budget guard stop writes a partial B3;
  - decimal commas and the Unicode minus are graded correctly.
Needs from PC (H7):
- A `TaskRunner` factory over the skill runner and portals; a `pack_for(question)` over the memory store.
- Run `pnpm bench`, then commit `bench/results/b1,b2,b3,b5.json`.
- Save the briefs generated during the bench to `var/bench/briefs/` (B5 reads them).
Notes:
- `bench/tests` was added to pytest testpaths.
- The L8 bench page reads these files once they exist; it is wired on the L9 line in L13, to avoid a conflict with this branch's M0 page.

## <date time> · L<id> · branch laptop/<id>-<slug>
Done: what works now.
Verify: the exact commands to check it (and what you should see).
Needs from PC: anything the PC must do to integrate (new dependency, migration, env var).
Notes: surprises, shortcuts, things left undone.
```

---

## Sun 15 Nov 2026 · L8 follow-up (door opens; café pattern background) · branch laptop/l9-run-theater
Done:
- Intro: the café door swings open onto a warm, lit doorway, and the camera steps through the glow into the app (DECISIONS L-82).
- The Lottie hero band is replaced by a subtle, drifting line-art café pattern behind every page, still driven by the data (rain, agent busy, delivery van, served cup).
- The Lottie files and dependency are removed.
Verify:
- Frame-by-frame intro capture: the door opens at about 2.7 s, the glow fills the screen by about 3.9 s, and no frame flickers.
- Headless Chrome checks:
  - the pattern renders on every page; its fills resolve;
  - rain is on, the approve sends the van and warms the field;
  - a cup rises after the run;
  - the phone has no sideways scroll; no console errors.
- `pnpm check`: green. Lighthouse on a production build: `/` desktop 94, phone 71 (the intro on a first visit), `/bench` phone 94, accessibility 100. Audit (Sonnet): 0 blockers and 0 should-fix items; one nit applied (`useId` pattern ids).
Needs from PC:
- `pnpm install` after merging (one dependency removed).
- The README on `main` still credits LottieFiles in "Asset attribution"; drop that line when this branch merges, or in L13.
Notes:
- `apps/web/public/intro/cafe-shop.glb` now carries the door rig and the `DoorOpen` animation.

## Sun 15 Nov 2026 · L8 follow-up (page transitions by name) + README banner · branch laptop/l9-run-theater
Done:
- Page changes fade through by view-transition name (`page`), so Safari gets the same no-overlap transition as Chrome (DECISIONS L-81).
- README banner merged into `main` (PR #10) at the owner's request.
Verify:
- Headless Chrome on a production build. Navigation runs exactly `old(page) page-out 120 ms` and `new(page) page-in 380 ms @140 ms`, and the frames never show both pages. Skills → Bench: the highlight's old copy is gone in 120 ms. `pnpm check` is green.
Needs from PC:
- Pull `main` (it now has the README banner) before merging the laptop branches.
Notes:
- Safari could not be automated from the laptop; the owner should confirm by eye.

## Sun 15 Nov 2026 · L9 · branch laptop/l9-run-theater (stacked on laptop/l8-today)
Done:
- Run theater at `/runs/[id]` (PRD F2, DECISIONS L-80):
  - a ticker with elapsed time, model calls, tokens, $ and skill version;
  - a step timeline with a mode, duration and cost for each step, and the heal ladder (fallback, healer model, escalation, you) with what changed;
  - the browser panel: schematic for the recorded sample, live JPEG frames and the cursor for real runs;
  - a chaos seed picker, the result with Undo, and an "agent needs you" panel.
- Plays `fixtures/run-events.json` end to end with pause, restart and 1×/2×. `/runs/run_demo_seed7` is the sample.
- The dock links to the theater (sample, or the `run_id` returned by approve). An unknown run shows a clear error state with a link to the sample.
Verify:
- `pnpm check`: green. `pnpm -C apps/web contracts` now also runs `run-view.check.mts`, which pins the fold on the fixture: 11 steps, 2 heals, 2 calls, $0.0031, 15.68 s, Sign in → Anmelden, the cookie banner inserted. It also covers failed runs, ask_human and secret masking.
- Headless Chrome on a production build:
  - mid-heal, the ladder shows fallback ✗ → healer (claude-haiku-5-5) ✓;
  - pause holds; the result reads "Order GW-10482 placed…";
  - the dock link opens the theater;
  - 390 px has no sideways scroll; the light and dark stages render correctly;
  - the cursor halo tracks the active element.
- Lighthouse `/runs/run_demo_seed7`: desktop 96, phone 84, accessibility 100, CLS 0.001.
- Independent audit (Sonnet): 0 blockers, 5 should-fix items, all fixed:
  - the WS frame/header race;
  - the halo offset;
  - failed runs left spinning;
  - "needs you" staying up after a resume;
  - one reconnect treated as fatal.
Needs from PC (H4):
- `GET /runs/{id}/events` as SSE, with `event: <type>`, `id: <seq>` and Last-Event-ID resume.
- `WS /runs/{id}/screen`: a frame header, then the JPEG; cursor messages.
- `POST /runs/{id}/undo`, `POST /runs/{id}/human`, `POST /chaos`.
- CORS for the web origin on all of these. `approve` must return `run_id`; the dock links to `/runs/{run_id}`.
Notes:
- The schematic is for runs without frames. Golden runs (F7: `frames.json` + `frames/*.jpg`) are not wired into the theater yet; that belongs with H4/H6.

## Sun 15 Nov 2026 · L8 (part 5: café hero band, fade-through pages, intro polish) · branch laptop/l8-today
Done:
- The animated café is now a small hero band at the top of every page, above the content, not behind it. Headings are smaller, so the data starts sooner (DECISIONS L-79).
- Page changes fade through (out in 120 ms, then in), so nothing from the old page lingers over the new one.
- The intro has no Skip button (click or Esc still ends it), walks to the door, and no longer flickers: the model's z-fighting faces were separated, and the render scale is fixed.
Verify:
- Headless-Chrome checks:
  - no part of the scene reaches the headline at 1440 or 390 px;
  - no Next issue badge and no hydration errors;
  - the intro plays, ends, and Esc ends it early;
  - frame-by-frame capture of the intro finds 0 flicker frames;
  - navigation frames show the old page gone before the new page rises.
- `pnpm check`: green (312 pytest, ruff, pyright, tsc, eslint, contracts).
- Lighthouse, production build:

  | Page | Performance | Notes |
  |---|---|---|
  | `/` desktop | 95 | |
  | `/bench` phone | 95 | |
  | `/` phone | 72 | the 3D intro on a session's first visit, unchanged from part 4 |

  Accessibility is 100 everywhere.
- Independent audit (Sonnet): 0 blockers and 0 should-fix items. Applied one nit: the Skills highlights now fade out with their page instead of vanishing.
Needs from PC:
- Nothing new.
Notes:
- `apps/web/public/intro/cafe-shop.glb` is the repaired model (credited as modified, per CC-BY).

## Sun 15 Nov 2026 · L8 (part 4: café intro + live café background) · branch laptop/l8-today
Done:
- A 3D intro: the app opens on a low-poly café, orbits it, walks through the door and fades into Today. It plays once per session, has a Skip button, and is skipped under reduced motion (DECISIONS L-78).
- An animated café diorama sits faded in the background of every page and follows the data: rain from the brief's forecast, a delivery van (now people-sized) when a supplier order is approved, a busier barista while the agent runs, a served cup when it finishes.
- The photo backdrop (L-77) and the GPU scene (`ambient-field.tsx`) are removed.
Verify:
- Headless-Chrome checks: the intro plays and ends about 4.4 s after the model loads, and a second load skips it. Rain shows on Today and on Skills (via the idle prefetch). The van arrives on the oat-milk approve. 390 px has no sideways scroll. No hydration errors.
- Skip is focused on arrival and ends the intro, and the old timers never fire again. Each delivery is a fresh van that unmounts after its trip, and one cup is served per finished run.
- `pnpm check`: green.
- Lighthouse, production build: desktop `/` 93; phone `/` 72 on a first visit (86 with the intro's assets blocked); phone `/bench` 94; accessibility 100.
Needs from PC:
- Nothing new. For live runs, `startRun` already drives the scene's busy state through the dock.
Notes:
- New dependencies: `@lottiefiles/dotlottie-react` 0.21.0 and `@google/model-viewer` 4.4.0. Assets are in `apps/web/public/scene/` and `apps/web/public/intro/`, credited on About.
- Development only: Lit and model-viewer print dev-mode warnings in the console.
- Independent audit (Sonnet): 0 blockers. All fixed:
  - the intro could stick if its script failed (now a 12 s safety timer);
  - Skip duplicated finish and the old timers fired again afterwards;
  - keyboard focus did not land on Skip;
  - a second delivery reversed the van;
  - the scene kept animating under reduced motion;
  - a cup was served on dock remount;
  - the van was sent before the approval succeeded.

## Sat 14 Nov 2026 · L8 (part 3: command-center redesign) · branch laptop/l8-today
Done:
- Second redesign at the owner's request (DECISIONS L-75): glass panels over a WebGL ember light field, Geist type, an ember accent.
- Today: cards spring in, light up and tilt under the cursor, and drag right to approve or left to skip. Each card has a graphic from its own numbers (margin scale, stock cells, rain-vs-dry bars).
- Approve explodes the card's text into particles that fly into a floating Agent dock; the dock plays the sample run (ring fills, turns violet while healing). A rebuilt card assembles from particles.
- ⌘K command palette (go to a page, approve a card, theme).
- Owner's follow-ups (L-76): always in motion (no toggle; the device's reduced-motion setting is still honoured), no cursor glow, a procedural café scene in the background (revert switch `SCENE`), light mode with matching depth, fluid page transitions with prefetched data.
Verify:
- `pnpm check`: green (312 pytest, eslint, tsc, contracts).
- Headless-Chrome checks at 390 and 1440 px, light and dark, cover every page and flow, including the explosion, the dock run, the particle rebuild and the palette.
- Lighthouse on a production build: `/` 87 on phones (the owner accepted phones in the 80s for the maximal option), `/bench` 96 on phones, desktop 99–100, accessibility 100. Page transitions hold 60 fps, and pages arrive filled at 0.13 s.
Needs from PC:
- Unchanged from part 2. For live approve, call `startRun` (`lib/agent-runs.ts`) with the run's events as they stream.
Notes:
- New dependency: `motion` 14.9.0. Removed: Newsreader and `src/fonts/`.
- Skills, Memory, Bench and About have the new theme and shell but their part-2 layouts.
- Independent audit: 0 blockers, 14 should-fix items. Fixed: the palette's see-through panel, calm mode still moving (drag, stock pulse, route slides, About pulse), the header toggle being ignored under the OS setting, a total that added unlike amounts (removed), the dock's missing "Sample run" label, 44 px targets, palette keyboard gaps, frame-rate-dependent particle physics, and a lost WebGL context.

## Sat 14 Nov 2026 · L8 (part 2: Skills, Memory, Bench, About + motion) · branch laptop/l8-today
Done:
- Motion layer (DECISIONS L-71), on View Transitions, CSS and NumberFlow:
  - route slides with an anchored header and a gliding nav indicator;
  - a masthead impression; € figures roll like an odometer;
  - reject → rebuilt brief: the figures roll and the changed words get a marker;
  - promoted stories morph into the lead slot;
  - the evidence drawer is a Base UI Drawer: a swipe-down sheet on phones, a swipe-right panel on desktop.
- Today: approving the oat card plays the sample run on the card (L-74).
- Skills: registry, version timeline (v1 ↔ v2), and steps shown like a code review, with healed lines wiping in and stats rolling; `?skill=` in the URL.
- Memory: an as-of slider with change ticks, replay, keyboard steps and `?as_of=` in the URL. The graph's edges draw in as facts become true; the record shows superseded values ("was €7.10/kg until 4 Nov") and each fact's confidence. The slider works in whole days, read as of the end of the day.
- Bench: the real provider probe (6/6, $0.002, latency bars with tooltips, raw table) and B1–B5 marked "Not run yet" (L-73).
- About: a numbered explainer with a pausable flow diagram whose pulse waits at "You approve".
Verify:
- `pnpm check`: green (312 pytest, eslint, tsc, contracts).
- Headless-Chrome checks (L-67) at 390 and 1440 px, light and dark, cover every page and interaction. Console errors are only 404s for unwired routes.
- Lighthouse on a production build (phones / desktop): `/` 95 / 100; `/skills` and `/memory` 95; `/bench` 91 / 100; `/about` 91. Accessibility 100, CLS ≤ 0.023.
Needs from PC:
- Wire `GET /skills`, `GET /skills/{id}/versions` and `GET /memory/graph` (shapes in `contracts.ts` / `contracts/api.py`), with CORS for the web origin.
- `/memory/graph` should include superseded facts (L-72).
- Live approve: when H4 lands, feed the run SSE into `RunTicker` (`components/today/run-ticker.tsx` takes `RunEvent[]`).
Notes:
- Independent audit: 1 blocker (the slider snapped to midnight UTC while facts change at 07:30, so 4 Nov showed the old price), 10 should-fix items and the nits, all fixed and re-checked in the browser.
- `/bench` imports `bench/results/provider_probe.json` from outside `apps/web`. The L12 deploy must build with files outside the app root available (Vercel's monorepo default).
- The long-running `next dev` (Turbopack) sometimes keeps serving an old `globals.css` after edits; restarting it fixes that. Production builds are unaffected.

## Fri 13 Nov 2026 · L8 (part 1: Today + redesign) · branch laptop/l8-today
Done:
- Today screen on the "Morning edition" design (DECISIONS L-69):
  - masthead and lead story with a figures column, "Also in this edition" columns;
  - evidence drawer laid out as a fact box;
  - reject dialog with ⌘/Ctrl+Enter;
  - Approve, Approve all, the sample-brief fallback (L-68) and the reject → rebuilt brief loop.
- Design system: `styles/tokens.css`, Newsreader display/text cuts, Geist, motion utilities (`.enter`, `.enter-rule`, `.stamp-in`, `.link-draw`), a newspaper top bar, and the section-front `PageHeader` on every route.
- Performance work (L-70): a self-hosted display-cut subset, a first-frame masthead, and lazy dialogs and schemas.
- graphify graph refreshed for L0–L8, code and docs (commit 96a9057).
Verify:
- `pnpm check`: green (312 pytest, eslint, tsc, contracts).
- UI: headless-Chrome tour (L-67) at 390×844 and 1440×900, light and dark. Every flow passes; the only console entries are the `/brief/today` 404s.
- Lighthouse 12.6.1 on `next build` + `next start`:
  - `/`: mobile 94–98, desktop 100;
  - `/bench`: mobile 99, desktop 100;
  - accessibility 100 everywhere; best practices 96 (404 only).
Needs from PC:
- Wire `GET /brief/today` (with CORS for the web origin) so the sample badge and the 404 disappear.
- The Playwright 390/1440 screenshots stay the formal record (H5).
Notes:
- Independent audit: 0 blockers, 8 should-fix items and the nits, all fixed:
  - error state with retry, plus `app/error.tsx` for a failed lazy chunk;
  - negative figures keep their sign ("−14%");
  - the decision count excludes approved cards;
  - no double reject via ⌘/Ctrl+Enter;
  - focus moves to `main` after a reject;
  - 44 px wordmark target; h3 for column stories;
  - "Plain wording" (not "Fact-checked") when the guard fell back to template text;
  - motion and shadow deviations added to L-69.
- `docs/ARCHITECTURE.md` font row updated to match (shared doc, one line).
- Skills, Memory, Bench and About are still placeholders on the new design (L8 part 2).
- A long-running `next dev` served stale CSS after the `@theme` font change; restarting it fixed that. Production builds were unaffected.

## Fri 13 Nov 2026 · L7 · branch laptop/l7-brief (stacked on laptop/l5-memory)
Done:
- `backroom_api/brief/`:
  - `guard.py`: deterministic number guard; units, cents, signs and number words are checked (CONTRACTS §6 rules 1–9).
  - `templates.py`: copy that passes the guard by construction.
  - `rules.py`: preferences and business rules from memory, plus the code-enforced checks.
  - `agents.py`: the Sonnet planner and Haiku verifier, through `llm/client.py`. Structured outputs, cached frozen prompts with worked examples, `stop_reason` checked, time limits.
  - `pipeline.py`: `generate` / `stream_today` / `brief_for_today`.
- `memory/extractor.py`: rejection reason → checked `Preference` (`extract` + `record_rejection`).
- Real runs on today's data (OpenRouter, about 2 cents per brief): all copy passed the guard first try. The full F4 loop worked: reject €3.60 with "too steep, max 8%" → extracted cap 8 → regenerated card €3.20 → €3.45, "Kept under your 8% cap", new action id.
Verify:
- `uv run pytest services/api/tests/test_brief.py`: 66 tests. The F4 loop runs on Neon when `DATABASE_URL` is set.
- `pnpm check`: 312 pass.
Needs from PC (H4/H5 wiring):
- `GET /brief/today[?regenerate=1]`: `rules_from_memory(conn, now)`, a context pack from `memory.packer`, then `pipeline.stream_today(...)` as SSE. Persist the final `BriefResult`: brief, decisions, vetoes. Serve it cached, with `cached: true`.
- `POST /actions/{id}/reject`: look the card up by action id, then `extractor.extract(llm, reason, card)` + `record_rejection(conn, ...)`, then commit.
- Pass `run_id` / brief id into `LLMPlanner` / `LLMVerifier` for the ledger.
- Consider pinning OpenRouter provider routing for reliable caching (L-66).
Notes:
- Deviations are logged as L-58…L-66.
- The audit found 2 blockers (non-LLM errors crashed the brief; stale action ids after a cap) and 9 issues worth fixing; all are fixed and tested.

## Fri 13 Nov 2026 · L5 · branch laptop/l5-memory (stacked on laptop/l6-detectors)
Done:
- `backroom_api/memory/`:
  - `store.py`: entities, episodes, bitemporal facts. Supersession runs under a per-key advisory lock, the "as we knew it at r" query is in place, `graph()` returns `MemoryGraph` and `fact_detail()` returns `FactDetail`.
  - `writers.py`: deterministic L4-world loader; `write_invoice` for one invoice; `record_preference` for learned rules.
  - `packer.py`: `ContextPack` under a 1,200-token budget; standing rules first; `seeds_for(task)`.
- `0001_memory.sql` ran for real on Neon (Postgres 18.6 + pgvector 0.8.6): all checks reject bad rows and the as-of queries give the right answers.
Verify:
- With a Neon `DATABASE_URL` in `.env`: `uv run pytest services/api/tests/test_memory.py`, 14 tests. They cover supersession, as-of, known_at, provenance, a two-connection race, the held-back invoice ingest and the 8% → 10% preference change. Each run uses its own schema and drops it.
- `pnpm check`: 246 pass. Without a database the memory tests skip.
Needs from PC:
- H1 runs `0001_memory.sql` through the runner, then `memory.writers.write_world(conn, Path("data/out"))` after `pnpm seed`'s Parquet step.
- For the F4 demo, hold back `invoices_from_price_change(out, "BUTTER-1KG")` and ingest the first via `POST /memory/ingest/invoice`.
- Time slider: call `store.graph(conn, as_of)` without `known_at`; seed facts are recorded "now".
Notes:
- Deviations are logged as L-50…L-57.
- The audit found 1 blocker (concurrent writers could leave two open facts) and 9 issues worth fixing; all are fixed and tested.

## Fri 13 Nov 2026 00:40 · L6 · branch laptop/l6-detectors (stacked on laptop/l4-data)
Done:
- `backroom_api/analytics/detectors.py`: stock-out, margin erosion and weather demand as DuckDB SQL over the L4 Parquet files. Each emits contract `Candidate`s with every quotable number and inline SQL evidence. `run_all(max_price_increase_pct=…)` re-proposes within an owner's cap.
- `backroom_api/analytics/pricing.py`: deterministic prices, rounded half-up.
- On today's real data:
  - Franzbrötchen: butter +16.1%, €0.55 → €0.64; cost €0.93 → €1.02; margin 71% → 68% (target 70%); proposes €3.20 → €3.60 (+12.5%, margin 72%). With an 8% cap: €3.45, +7.8%, 70%.
  - Oat milk: 2.0 days left; 28 cartons, €44.52.
  - Rainy Saturday: 9 mm forecast, −14%, trim one of three 4-hour shifts, €58.
- Shared fixtures regenerated to match (driver_* keys, 28 cartons).
Verify:
- `uv run python -c "from backroom_api.analytics.detectors import run_all; [print(c.kind, c.impact_eur_weekly) for c in run_all()]"` (needs `uv run backroom-data all` first).
- `uv run pytest services/api/tests/test_detectors.py`: 14 tests. `pnpm check`: 232 pass.
Needs from PC:
- `uv sync --all-packages` (duckdb in backroom-api).
- The reorder is 28 cartons / €44.52 now (L-43); demo lines that say 24 / €38.16 need updating.
Notes:
- Deviations are logged as L-43…L-49.
- The audit found no blockers and 11 issues worth fixing; all are fixed. For L7: the number guard must check that units agree (CONTRACTS §6 rule 6).

## Thu 12 Nov 2026 23:30 · L4 · branch laptop/l4-data (stacked on laptop/l3-tilldesk)
Done:
- `uv run backroom-data all` (`pnpm seed`'s data step) builds `data/out/`:
  - Parquet tables: sales, weather, holidays, menu, recipes, unit_costs, supplier_prices, grainline_orders, inventory, staff, rota;
  - `preferences.json` (Tue/Fri ordering and the 70% margin target; no price cap) and `manifest.json` (sources, row counts, honest notes).
- Sources: Maven Coffee Shop Sales (Hell's Kitchen store, mapped onto the TillDesk menu), Open-Meteo archive + forecast for Bonn, Nager.Date DE-NW. Downloads are cached in `data/raw/`; every one has a fallback (synthetic sales and weather, computed holidays).
- Story numbers come out of the data:
  - Franzbrötchen unit cost €0.93 → €1.02 (butter €0.55 at €7.10/kg);
  - oat milk exactly 2.0 days left;
  - rainy Saturdays −13.9% against nearby dry ones;
  - next Saturday 9 mm (`demo_override`);
  - three 14:00–18:00 shifts on Saturday.
Verify:
- `uv run backroom-data all` (≈4 s), then run it again: every file in `data/out/` is byte-identical.
- `uv run pytest data/tests`: 18 tests on tiny fixtures, offline.
- `pnpm check`: 218 pass.
Needs from PC:
- `uv sync --all-packages` (new deps: duckdb, pyyaml; data depends on portals).
- H1 loads the tables into Postgres (column types in `cli.SCHEMAS`; CONTRACTS §10).
- Rebuild the data on demo day, or pin `PORTALS_TODAY`, so data and portal agree.
Notes:
- Deviations are logged as L-32…L-42 in `docs/DECISIONS.md`. The Grainline usual oat order is now 10 cartons (L-37).
- The audit found 1 blocker (hard-coded "Maven/Open-Meteo" notes in fallback builds) and 8 issues worth fixing; all are fixed and tested.

## Thu 12 Nov 2026 21:40 · L3 · branch laptop/l3-tilldesk (stacked on laptop/l2-chaos)
Done:
- The TillDesk portal at `/tilldesk`: login (username + password, no TOTP), menu list (8 items), edit price (a draft), and "Publish menu".
- Chaos applies through the shared macros, with cards on the menu list.
- Admin `GET /_admin/state/tilldesk` returns `TillDeskState`, with `items` keyed by id; `/_admin/reset` restores the menu.
- Undo is saving the old price and publishing again.
Verify:
- `uv run pytest services/portals/tests/test_tilldesk.py`. All of `pnpm check` passes: 200 tests.
- By hand: `pnpm dev:lite`, open http://localhost:8001/tilldesk/login, sign in as `$TILLDESK_USER` / `$TILLDESK_PASSWORD`.
Needs from PC:
- `tilldesk.change_price`: the postcondition is `items.<item_id>.published_price_eur`.
- Edit links are named "<Edit label> <item name>". Either target that, or `goto /tilldesk/menu/{{item_id}}/edit` (CONTRACTS §4).
- Use exact name matching in the runner (CONTRACTS §3 rule 5).
Notes:
- Deviations are logged as L-26…L-31 in `docs/DECISIONS.md`. Localboard (P1) is not built (L-26).
- The audit found 1 blocker (Publish was hidden when nothing had changed) and 4 issues worth fixing; all are fixed and tested.

## Thu 12 Nov 2026 20:40 · L2 · branch laptop/l2-chaos (stacked on laptop/l1-grainline)
Done:
- The chaos engine, with 9 families (language, nav position, section order, wrapper depth, id/class salt, interstitials, delayed render, button↔link, table↔cards), rendered through `templates/macros.html` and the `Look` object in `rendering.py`.
- `GET /_admin/chaos` and `POST /_admin/chaos {portal, seed}` → `ChaosState`; `/_admin/reset` sets every seed back to 0.
- Seed 0 is canonical. Seed 7 gives German controls, top-bar nav and a cookie banner.
Verify:
- `uv run pytest services/portals` (146 in `pnpm check`):
  - same seed ⇒ same DOM hash across the whole reorder path;
  - seeds 0–19 ⇒ 20 distinct hashes;
  - every non-canonical variant has a DOM marker;
  - label/for/id soundness and the skill test ids hold at all 20 seeds;
  - the reorder flow works at seeds 3, 7 and 11.
- By hand: `curl -X POST localhost:8001/_admin/chaos -H "X-Admin-Token: $PORTALS_ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"portal":"grainline","seed":7}'`, then open http://localhost:8001/grainline/catalog.
Needs from PC (H2/H3), see `docs/CONTRACTS.md` §3 "Rules for the agent runner":
- a fresh browser context per run;
- wait for `[aria-busy]` to clear before each snapshot;
- open the hamburger `<details>` before clicking nav links;
- link-variant actions are role `link`.
Also: the api `POST /chaos` forwarding route is yours (L-23). Please time a real seed-7 heal early: it will touch at least 5 steps (L-24).
Notes:
- Deviations are logged as L-18…L-25 in `docs/DECISIONS.md`. L-1…L-17 (L0/L1/L10) were added on this branch too, at the user's request.
- The audit found no blockers and 8 issues worth fixing; all are fixed.

## Thu 12 Nov 2026 19:10 · L1 · branch laptop/l1-grainline (stacked on laptop/l0-contracts)
Done:
- The Grainline portal at `/grainline`: login + TOTP (RFC 6238, no new dependency), catalog search with pagination, cart (add, update, remove), checkout with a delivery-date choice, order page with cancel as the Undo, order history, invoices list, and invoice PDFs (hand-written, deterministic, € and umlauts via WinAnsi).
- Admin `GET /_admin/state/grainline` and `POST /_admin/reset` (`X-Admin-Token`).
- Seeded history: Tue/Fri orders over the last 28 days, `GW-10474`…`GW-10481`. Butter is €7.10 → €8.24 from day −9, oat milk €1.46 → €1.59 from day −3. The next order is `GW-10482` (24 × €1.59 = €38.16). It is pure functions in `grainline/catalog.py` (`seeded_orders`, `price_on`, `PRODUCTS` with pack sizes), so L4/L6 import the same numbers.
Verify:
- `uv run pytest services/portals` (52 pass) or `pnpm check`.
- By hand: `pnpm dev:lite`, open http://localhost:8001/grainline/login, sign in as `$GRAINLINE_USER` / `$GRAINLINE_PASSWORD`, and get the code from `uv run python -m backroom_portals.totp`.
Needs from PC:
- `pydantic-settings` added to `services/portals/pyproject.toml` (already in the lock via the api; `uv.lock` +2 lines). Re-lock on merge as usual.
- With `GRAINLINE_TOTP_SECRET` empty, the portal derives the secret from `DATA_SEED` (`backroom_portals.totp.default_secret`). The agent's vault must use the same rule, or `pnpm seed` writes a secret to `.env`.
- Contract change, proposed here (L0 not yet acknowledged): 4 Grainline labels added: `update_qty`, `remove`, `prev_page`, `next_page`.
Notes:
- A fresh login empties the cart, so a replay never inherits leftovers.
- Catalog and cart rows use `<th scope="row">` with the product name, so the agent can scope "Quantity" and "Add to cart" to a row when the page lists several products.
- The audit (2 blockers, 7 should-fix) is addressed. Left for L2: chaos rendering (nav position, wrappers, interstitials, button/link, table/cards). L2 will move the templates onto shared macros first.

## Thu 12 Nov 2026 17:30 · L0 · branch laptop/l0-contracts
Done: contracts for every shared shape, in `docs/CONTRACTS.md` plus code. Portal routes, labels (EN / EN-alt / DE), test ids, admin API, SKUs and secret keys are in `backroom_portals/contract.py`. The chaos catalog (9 families; seed 0 canonical; seed 7 pinned to DE + top-bar nav + cookie banner) is `backroom_portals/chaos.py`. The skill schema is `backroom_api/skills/schema.py`. Run events (SSE), WS frames and golden-run frames are `backroom_api/contracts/events.py`; API bodies are `contracts/api.py`; the detector `Candidate` is `contracts/candidate.py`. The memory migration is `services/api/migrations/0001_memory.sql`, bitemporal with `invalidated_at`. The zod mirror is `apps/web/src/lib/contracts.ts`. Six shared fixtures in `apps/web/src/fixtures/` are generated from the pydantic models by `services/api/scripts/gen_fixtures.py`.
Verify: `pnpm check` (66 pytest pass, including fixtures parsed with pydantic; `pnpm -C apps/web contracts` parses the same fixtures with zod and checks rejections).
Needs from PC:
- Acknowledge L0 in `docs/sync/pc.md`.
- The migration runner (H1) should pick up `services/api/migrations/*.sql` in name order. The SQL is not yet run against a real Postgres, only reviewed; please apply it once on Docker Postgres in H1 and tell me if anything fails.
- Add `services/api/backroom_api/contracts/` and `services/api/migrations/` to the "shared, change only through L0" row of the HANDOVER ownership table.
- Decisions for the PC's side, which you may change via the contract process:
  - one new skill version per run, stored only on success;
  - `StepChange` insert and delete ops, for dismiss steps;
  - `POST /runs/{id}/undo` and `POST /runs/{id}/human`;
  - `ContextPack` on `RunSummary`.
Notes, files outside the laptop's ownership (all small, needed to wire the contract check):
- `.github/workflows/ci.yml`: one step after typecheck, `pnpm -C apps/web contracts` (the laptop's gh token now has the `workflow` scope);
- the root `package.json` `check:web` runs that step too;
- an `apps/web/package.json` `contracts` script;
- `apps/web/tsconfig.json` gains `allowImportingTsExtensions`, so node can run the check without a build step.
Notes, other:
- Fixtures are illustrative. On a real seed-7 run every German label heals, which is more steps than the fixture shows.
- An independent audit pass was run, and its findings are fixed.

## Thu 12 Nov 2026 15:20 · L10 · branch laptop/l10-llm-probe
Done: `pnpm probe:llm` on OpenRouter (worker anthropic/claude-haiku-5.5, SDK 2.8.0): all 6 checks pass (basic, effort, strict_tools, structured_outputs, prompt_cache, streaming). Total $0.0020. `LLM_CAPS_OFF` stays empty; no DECISIONS entry needed. Closes the last M0 gate item.
Verify: `cat bench/results/provider_probe.json` (every check `"ok": true`), or rerun `pnpm probe:llm` with the key in `.env`.
Needs from PC: merge only; adds `bench/results/provider_probe.json` (PC-owned path, written as L10 specifies). Update HANDOVER §1 to mark the M0 gate closed.
Notes: laptop setup per §2b done; `pnpm check` green on macOS (20 passed).
