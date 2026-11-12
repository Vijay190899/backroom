# Contracts (L0)

The shapes the PC and the laptop build against in parallel ([HANDOVER §9](HANDOVER.md#9-work-split-laptop-light-vs-this-pc-heavy)). The code is the source of truth; this page says where it lives and the rules the code cannot express.

| Contract | Code | Section |
|---|---|---|
| Portal routes, labels, test ids, admin API | `services/portals/backroom_portals/contract.py` | [§2](#2-portals) |
| Chaos variant catalog | `services/portals/backroom_portals/chaos.py` | [§3](#3-chaos-catalog) |
| Skill format | `services/api/backroom_api/skills/schema.py` | [§4](#4-skills) |
| Run events (SSE) and screen frames (WS) | `services/api/backroom_api/contracts/events.py` | [§5](#5-run-events) |
| Detector `Candidate` and the number guard | `services/api/backroom_api/contracts/candidate.py` | [§6](#6-candidates-and-the-number-guard) |
| API request and response bodies | `services/api/backroom_api/contracts/api.py` | [§7](#7-api-shapes) |
| Memory schema | `services/api/migrations/0001_memory.sql` | [§8](#8-memory) |
| Web mirror (zod) | `apps/web/src/lib/contracts.ts` | [§9](#9-fixtures-and-the-drift-check) |
| Shared fixtures | `apps/web/src/fixtures/*.json` | [§9](#9-fixtures-and-the-drift-check) |

## 1. Changing a contract

- Contract files are shared: neither machine edits them alone. The laptop proposes a change in `docs/sync/laptop.md`; the PC applies it (or acknowledges the laptop's branch) and announces it in `docs/sync/pc.md`.
- Every contract model is strict (`extra="forbid"` in pydantic, `z.strictObject` in zod): an unknown field is an error, not a silent drop.
- The server always serialises complete objects (never `exclude_none`, `exclude_defaults` or `exclude_unset`), so zod treats every key as present. Cross-field validators (skill templates, executable actions) live only in Python; the server is authoritative.
- Datetimes are always timezone-aware ISO 8601 (`AwareDatetime`); naive values are rejected.
- A change touches three places at once: the pydantic model, the zod mirror and the fixtures. `pnpm check` fails until all three agree.
- Migrations are append-only: never edit an applied `NNNN_*.sql`; add the next number.

## 2. Portals

- **One service, three prefixes.** `services/portals` serves Grainline under `/grainline`, TillDesk under `/tilldesk` and Localboard (P1) under `/localboard`, all on one origin (`:8001` locally, `portals.<ip>.sslip.io` deployed). A run's navigation allowlist is therefore **origin + path prefix**, not origin alone.
- **Routes** are the `*_ROUTES` tables. Forms post and redirect with 303, like a classic SaaS app. Undo is `order_cancel` on Grainline and saving the old price again on TillDesk.
- **Labels** (`*_LABELS`) are what the agent sees and what skills match. Each has three forms: `en` (canonical, seed 0), `en_alt` (synonym) and `de`; chaos picks one.
- **Test ids** (`data-testid`, built by `testid()`): `gl-` / `td-` / `lb-` + label key with `-`, plus a row key for list rows (`gl-add-to-cart-OAT-1L`, `td-edit-franzbroetchen`). They **never change under chaos** and are for our tests and fixtures only. The agent never sees them (they are not in the ARIA snapshot), and a skill must never use them as a locator.
- **Non-label test ids** (structure, not controls): Grainline uses `gl-nav`, `gl-row-<SKU>`, `gl-cart`, `gl-cart-line-<SKU>`, `gl-cart-qty-<SKU>`, `gl-cart-total`, `gl-checkout-total`, `gl-order-<id>`, `gl-order-status`, `gl-order-total`, `gl-invoice-<id>`, `gl-download-invoice-<invoice id>`, and one per message (`gl-login-error`, `gl-totp-error`, `gl-cart-error`, `gl-checkout-error`, `gl-cancel-error`, `gl-added-notice`, `gl-order-placed`, `gl-order-cancelled`).
- **Visible copy:** only control labels (the `*_LABELS` tables) vary with chaos. Headings and messages stay English at every seed.
- **Signing in by hand:** `uv run python -m backroom_portals.totp` prints the TOTP secret and the current code.
- **Ids and demo prices:** order ids `GW-\d{5}`, invoice ids `INV-\d{6}`; SKUs in `GRAINLINE_SKUS`, TillDesk item ids in `TILLDESK_ITEM_IDS`. The demo-story prices (`DEMO_PRICES_EUR`: oat milk €1.59, butter €7.10 → €8.24/kg, Franzbrötchen €3.20) are fixed here so the portal (L1), the data pipeline (L4) and the detectors (L6) agree.
- **Admin API** (header `X-Admin-Token: $PORTALS_ADMIN_TOKEN`; only the api and the bench call it):

| Method | Path | Body → response |
|---|---|---|
| GET | `/_admin/chaos` | → `ChaosState[]` (every portal) |
| POST | `/_admin/chaos` | `ChaosRequest {portal, seed}` → `ChaosState {portal, seed, variants}` |
| GET | `/_admin/state/{portal}` | → `GrainlineState` (`orders` newest last) or `TillDeskState` (`items` keyed by item id); used by `portal_state` postconditions and bench checks. Localboard state comes with Localboard (P1) |
| POST | `/_admin/reset` | wipe carts, orders and edits; every seed back to 0 |

- **Secrets:** a skill references vault keys as `{{secret:<key>}}`; `SECRET_KEYS` maps each key to its `.env` variable (`grainline_user`, `grainline_password`, `grainline_totp`, `tilldesk_user`, `tilldesk_password`).

The api's `POST /chaos` takes the same `ChaosRequest` and returns the same `ChaosState` (a test keeps the two models identical).

## 3. Chaos catalog

Nine families, the first variant of each canonical: `language` (en, en_alt, de), `nav_position` (sidebar, topbar, hamburger), `section_order`, `wrapper_depth`, `id_class_salt`, `interstitial` (none, cookie_banner, whats_new_modal, survey), `delayed_render` (0–1500 ms), `control_kind` (button or link), `list_layout` (table or cards).

- `pick_variants(portal, seed)` is the only way a seed becomes variants: seed **0 is canonical**; seed **7 (the demo seed) is pinned** to German labels + top-bar nav + cookie banner and nothing else; every other seed draws from `random.Random(f"{portal}:{seed}")` and always changes at least one family.
- L2 implements the rendering. Its DOM-hash tests prove same seed ⇒ same DOM, different seeds ⇒ different DOM.

## 4. Skills

`Skill {id, task, portal, version, parent_version, heal_note, params_schema, steps[], postconditions[], stats, created_at}`, `Step {intent, action, target, fallbacks, value_template, expect, timeout_ms}` (PRD §8.2).

- `id` equals the task: `grainline.reorder_item`, `grainline.download_invoice`, `tilldesk.change_price`, `localboard.post_special` (P1). One skill per task; versions count up from 1.
- Locator order: `target` (ARIA role + name), then `fallbacks` in order (`{label}`, `{text}`, `{css}`).
- `value_template`: `{{param}}` must be declared in `params_schema.properties`; `{{secret:key}}` is resolved by the vault and is allowed only in `fill_secret` and `totp` steps (the schema enforces both).
- `goto` and `press` need a `value_template` (the path or the key).
- Postconditions: `url_matches`, `text_visible`, or `portal_state` with a dotted path into the admin state (`orders.last.status` equals `placed`; `items.franzbroetchen.published_price_eur` equals `{{price_eur}}`). `equals` is rendered, then parsed as JSON when it parses, so `"3.6"` equals `3.60`. A run without passing postconditions never reports success.
- A heal produces a **new version** (`parent_version` = the old one). A run that heals several steps produces **one** new version. It is **stored only if the run finishes `succeeded` with every postcondition passing**; until then `heal.succeeded.new_version` is provisional.
- `SkillDiff.changes` are `StepChange`s with `op`: `update` (one field of a step), `insert` (a new step, e.g. dismissing a cookie banner) or `delete` (`field` is `"step"` for both). `step_index` is in the newer version for update and insert, in the older one for delete.

## 5. Run events

`GET /runs/{id}/events` streams `RunEvent`s over SSE: `id: <seq>`, `event: <type>`, `data: <JSON>`. `seq` starts at 1 and goes up by 1, so `Last-Event-ID` resumes exactly. Types: `run.started`, `step.started`, `step.finished`, `mode.changed`, `heal.started`, `heal.attempt` (rung `fallback` → `healer` → `escalation` → `human`), `heal.succeeded`, `heal.failed`, `cost.tick`, `ask_human`, `run.finished`.

- Secrets never appear: `step.started.value` is `null` for `fill_secret` and `totp`.
- `cost.tick.totals` and `run.finished.totals` are running totals for the ticker (elapsed, steps, LLM calls, tokens, cache reads, $).
- Golden runs (F7) are a directory: `events.json` (the same events, with `run.started.recorded = true`, which shows the Replay badge), `frames.json` (`GoldenFrame {file, after_seq, offset_ms, width, height, cursor_x, cursor_y}`) and `frames/*.jpg`.
- `ask_human` pauses the run until `POST /runs/{id}/human {action: "resume" | "cancel", note}`.
- `WS /runs/{id}/screen`: a `{"type":"frame", seq, width, height, ts}` text message, then the binary JPEG; `{"type":"cursor", x, y, step_index}` moves the halo.

## 6. Candidates and the number guard

A detector emits `Candidate {id, kind, subject_id, title_hint, impact_eur_weekly, numbers[], evidence[], proposed_action, as_of, computed_at}`. `numbers` holds **every** figure the copy may quote (`EvidenceNumber {key, value, unit, label}`; percentages are in percent: `71.0`, not `0.71`). `id` is deterministic: `<kind>:<subject_id>:<as_of date>`.

Number guard rules (L7 implements them; deterministic, no LLM):
1. Extract every number from the card's `title`, `why` and `preference_note` (`12.5`, `3.20`, `−14`). Copy is English: `.` is the decimal mark and `,` only separates thousands (`1,200`).
2. A number written with *d* decimals matches an evidence value *v* when it equals `round(|v|, d)`. Signs are ignored ("14% fewer" matches `-14`).
3. Digits inside ids and names do not count: SKUs, order and invoice ids, entity names.
4. Any unmatched number fails the card: one regeneration, then template copy from `title_hint` and `numbers`. `GuardResult` records the outcome.
5. Copy avoids clock times and dates written as numbers ("Friday", not "13.11.").

## 7. API shapes

The models in `contracts/api.py` are the bodies of the ARCHITECTURE §3 routes: `Brief` and `ActionCard` (`/brief/today`), `ApproveResponse` (`Idempotency-Key` header; a repeat returns the same `run_id` with `deduplicated: true`), `RejectRequest` and `RejectResponse`, `RunSummary` (with the run's `ContextPack`; `null` for a replay), `UndoResponse` (`POST /runs/{id}/undo`, 409 when `undo_available` is false), `HumanReply` (`POST /runs/{id}/human`), `SkillSummary` and `SkillVersions` (`diffs[i]` goes from `versions[i]` to `versions[i+1]`), `MemoryGraph`, `FactDetail`, `InvoiceIngestResponse`, `ContextPack`, `ChaosRequest` and `ChaosState`. `GET /brief/today?regenerate=1` streams SSE events `brief.skeleton {cards}`, then one `brief.card {card}` per card as it passes the guard, then `brief.done {brief}`. Errors (all but `/health`) are `{"error": {"code", "message"}}`. `/health` stays as defined in `routes/health.py`.

## 8. Memory

`0001_memory.sql` creates `entity`, `episode` and `fact` (ARCHITECTURE §7) plus checks and indexes; it needs the `vector` extension (Neon and `pgvector/pgvector:pg16` both have it).

- Entity ids are `<type>:<slug>` (lowercase kebab slug: `ingredient:oat-milk`, `product:franzbroetchen`); the table checks the prefix.
- Facts are bitemporal: valid time (`valid_from`, `valid_to`) and transaction time (`recorded_at`, `invalidated_at`). The "as we knew it at :r" query is in the migration header.
- Facts are only ever inserted. Supersession sets the old row's `valid_to`, `invalidated_at` and `superseded_by` in the same transaction as the insert. The writer locks the open rows first (`select … for update`), so two writers can't leave two open facts on a one-valued predicate. One-valued predicates supersede on `(subject, predicate)`, many-valued ones on `(subject, predicate, object)`.
- Starting predicate vocabulary (snake_case; extend as needed and note it in the sync log): one-valued `unit_price_eur_per_kg`, `unit_price_eur_per_l`, `menu_price_eur`, `stock_on_hand`, `supplied_by`; many-valued `uses_ingredient` (value `{grams}` or `{ml}`), `has_preference` (value holds the rule, e.g. `{"max_price_increase_pct": 8}`).
- Runs and skills tables belong to the PC (H4) and come in later migrations.

## 9. Fixtures and the drift check

`apps/web/src/fixtures/` holds a brief (the three demo cards with the story numbers), the brief after the rejection (€3.20 → €3.45, +7.8%, "Kept under your 8% cap"), the skill list, `grainline.reorder_item` v1 → v2 with its diff, a warm replay at seed 7 that inserts a cookie-banner step and heals two labels, and a memory graph with the butter price supersession. L8 and L9 build their screens on them.

- Regenerate them from the models with `uv run python services/api/scripts/gen_fixtures.py`; don't edit them by hand.
- `pnpm check` validates every fixture on both sides: pytest with pydantic (`services/api/tests/test_contracts.py`) and node with zod (`pnpm -C apps/web contracts`). Both also check that invalid input is rejected.
- The fixtures are illustrative. Real runs on chaos seed 7 will heal more steps (every label is German); the shapes are what matter.
