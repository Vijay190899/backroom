/**
 * Zod mirror of the Python contracts (L0, docs/CONTRACTS.md).
 *
 * Source of truth: services/api/backroom_api/contracts/*.py and skills/schema.py.
 * The server always sends complete objects (no exclude_none/defaults), so every key is
 * required here. Cross-field validators stay server-side (the server is authoritative).
 * Every object is strict, like the pydantic models (`extra="forbid"`), and the shared
 * fixtures in src/fixtures/ must parse on both sides (`pnpm check` runs both).
 * Uses relative imports only, so `node` can run contracts.check.ts directly.
 */
import { z } from "zod";

const datetime = z.iso.datetime({ offset: true });
const json = z.unknown();
const record = z.record(z.string(), json);

// --- common ---------------------------------------------------------------------------
export const portalSchema = z.enum(["grainline", "tilldesk", "localboard"]);
export const modeSchema = z.enum(["explore", "replay", "heal"]);
export const unitSchema = z.enum([
  "eur",
  "eur_per_kg",
  "eur_per_l",
  "pct",
  "count",
  "days",
  "hours",
  "mm",
  "g",
  "ml",
]);
export const candidateKindSchema = z.enum(["stockout", "margin_erosion", "weather_demand"]);
export const skillTaskSchema = z.enum([
  "grainline.reorder_item",
  "grainline.download_invoice",
  "tilldesk.change_price",
  "localboard.post_special",
]);
export type Portal = z.infer<typeof portalSchema>;
export type Mode = z.infer<typeof modeSchema>;

// --- evidence --------------------------------------------------------------------------
export const evidenceNumberSchema = z.strictObject({
  key: z.string(),
  value: z.number(),
  unit: unitSchema,
  label: z.string(),
});
export const evidenceSchema = z.strictObject({
  id: z.string(),
  kind: z.enum(["sql", "fact", "chart", "invoice"]),
  label: z.string(),
  sql: z.string().nullable().default(null),
  columns: z.array(z.string()).default([]),
  rows: z.array(z.array(json)).default([]),
  fact_ids: z.array(z.string()).default([]),
  synthetic: z.boolean().default(false),
});
export type EvidenceNumber = z.infer<typeof evidenceNumberSchema>;
export type Evidence = z.infer<typeof evidenceSchema>;

// --- skills ------------------------------------------------------------------------------
export const stepActionSchema = z.enum([
  "click",
  "fill",
  "fill_secret",
  "select",
  "press",
  "goto",
  "wait_for",
  "extract",
  "totp",
]);
export const locatorSchema = z.strictObject({ role: z.string(), name: z.string() });
export const fallbackSchema = z.union([
  z.strictObject({ label: z.string() }),
  z.strictObject({ text: z.string() }),
  z.strictObject({ css: z.string() }),
]);
export const expectSchema = z.strictObject({
  url_pattern: z.string().nullable().default(null),
  visible: locatorSchema.nullable().default(null),
  text: z.string().nullable().default(null),
});
export const stepSchema = z.strictObject({
  intent: z.string(),
  action: stepActionSchema,
  target: locatorSchema.nullable().default(null),
  fallbacks: z.array(fallbackSchema).default([]),
  value_template: z.string().nullable().default(null),
  expect: expectSchema.nullable().default(null),
  timeout_ms: z.number().int().positive().max(30_000).default(5_000),
});
export const postconditionSchema = z.strictObject({
  kind: z.enum(["url_matches", "text_visible", "portal_state"]),
  value: z.string(),
  equals: z.string().nullable().default(null),
});
export const skillStatsSchema = z.strictObject({
  runs: z.number().int(),
  successes: z.number().int(),
  mean_latency_ms: z.number().nullable(),
  mean_usd: z.number().nullable(),
  last_run_at: datetime.nullable(),
});
export const skillSchema = z.strictObject({
  id: z.string(),
  task: skillTaskSchema,
  portal: portalSchema,
  version: z.number().int().min(1),
  parent_version: z.number().int().nullable(),
  heal_note: z.string().nullable(),
  params_schema: record,
  steps: z.array(stepSchema).min(1),
  postconditions: z.array(postconditionSchema),
  stats: skillStatsSchema,
  created_at: datetime,
});
export const stepChangeSchema = z.strictObject({
  op: z.enum(["update", "insert", "delete"]),
  step_index: z.number().int(),
  field: z.string(),
  before: json,
  after: json,
});
export const skillDiffSchema = z.strictObject({
  skill_id: z.string(),
  from_version: z.number().int(),
  to_version: z.number().int(),
  changes: z.array(stepChangeSchema),
});
export type Step = z.infer<typeof stepSchema>;
export type Skill = z.infer<typeof skillSchema>;
export type StepChange = z.infer<typeof stepChangeSchema>;
export type SkillDiff = z.infer<typeof skillDiffSchema>;

// --- run events (SSE) --------------------------------------------------------------------
export const runStatusSchema = z.enum([
  "queued",
  "running",
  "succeeded",
  "failed",
  "needs_human",
  "cancelled",
]);
export const runTotalsSchema = z.strictObject({
  elapsed_ms: z.number().int(),
  steps: z.number().int(),
  llm_calls: z.number().int(),
  tokens_in: z.number().int(),
  tokens_out: z.number().int(),
  cache_read_tokens: z.number().int(),
  usd: z.number(),
});
const eventBase = {
  seq: z.number().int().min(1),
  run_id: z.string(),
  ts: datetime,
};
export const runEventSchema = z.discriminatedUnion("type", [
  z.strictObject({
    ...eventBase,
    type: z.literal("run.started"),
    action_id: z.string(),
    task: skillTaskSchema,
    portal: portalSchema,
    mode: modeSchema,
    skill_version: z.number().int().nullable(),
    chaos_seed: z.number().int(),
    recorded: z.boolean(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("step.started"),
    index: z.number().int(),
    intent: z.string(),
    action: stepActionSchema,
    target: locatorSchema.nullable(),
    value: z.string().nullable(),
    mode: modeSchema,
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("step.finished"),
    index: z.number().int(),
    ok: z.boolean(),
    duration_ms: z.number().int(),
    llm_calls: z.number().int(),
    tokens_in: z.number().int(),
    tokens_out: z.number().int(),
    usd: z.number(),
    error: z.string().nullable(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("mode.changed"),
    from_mode: modeSchema,
    to_mode: modeSchema,
    reason: z.string(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("heal.started"),
    step_index: z.number().int(),
    failure: z.string(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("heal.attempt"),
    step_index: z.number().int(),
    rung: z.enum(["fallback", "healer", "escalation", "human"]),
    model: z.string().nullable(),
    ok: z.boolean(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("heal.succeeded"),
    step_index: z.number().int(),
    new_version: z.number().int(),
    changes: z.array(stepChangeSchema),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("heal.failed"),
    step_index: z.number().int(),
    reason: z.string(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("cost.tick"),
    totals: runTotalsSchema,
    skill_version: z.number().int().nullable(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("ask_human"),
    reason: z.string(),
    step_index: z.number().int().nullable(),
  }),
  z.strictObject({
    ...eventBase,
    type: z.literal("run.finished"),
    status: z.enum(["succeeded", "failed", "needs_human", "cancelled"]),
    summary: z.string(),
    result: record,
    undo_available: z.boolean(),
    skill_version: z.number().int().nullable(),
    totals: runTotalsSchema,
  }),
]);
export type RunEvent = z.infer<typeof runEventSchema>;
export type RunEventType = RunEvent["type"];
export type RunTotals = z.infer<typeof runTotalsSchema>;

// WS /runs/{id}/screen: a frame text message precedes each binary JPEG frame.
export const screenMessageSchema = z.discriminatedUnion("type", [
  z.strictObject({
    type: z.literal("frame"),
    seq: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    ts: datetime,
  }),
  z.strictObject({
    type: z.literal("cursor"),
    x: z.number(),
    y: z.number(),
    step_index: z.number().int().nullable(),
  }),
]);

// Golden runs (F7): events.json (RunEvent[]) + frames.json (GoldenFrame[]) + frames/<file>.
export const goldenFrameSchema = z.strictObject({
  file: z.string(),
  after_seq: z.number().int(),
  offset_ms: z.number().int(),
  width: z.number().int(),
  height: z.number().int(),
  cursor_x: z.number().nullable(),
  cursor_y: z.number().nullable(),
});
export type GoldenFrame = z.infer<typeof goldenFrameSchema>;

// --- API ------------------------------------------------------------------------------------
export const errorResponseSchema = z.strictObject({
  error: z.strictObject({ code: z.string(), message: z.string() }),
});

export const guardResultSchema = z.strictObject({
  passed: z.boolean(),
  regenerations: z.number().int(),
  unmatched: z.array(z.string()),
});
export const actionCardSchema = z.strictObject({
  id: z.string(),
  candidate_id: z.string(),
  kind: candidateKindSchema,
  rank: z.number().int(),
  title: z.string(),
  impact_eur_weekly: z.number(),
  why: z.string(),
  evidence: z.array(evidenceSchema),
  numbers: z.array(evidenceNumberSchema),
  task: skillTaskSchema.nullable(),
  portal: portalSchema.nullable(),
  params: record,
  executable: z.boolean(),
  status: z.enum(["proposed", "approved", "rejected", "running", "done", "failed"]),
  preference_note: z.string().nullable(),
  copy_source: z.enum(["llm", "template"]),
  guard: guardResultSchema,
});
export const briefSchema = z.strictObject({
  id: z.string(),
  generated_at: datetime,
  as_of: datetime,
  cards: z.array(actionCardSchema).max(3),
  cached: z.boolean(),
});
export type ActionCard = z.infer<typeof actionCardSchema>;
export type Brief = z.infer<typeof briefSchema>;

// GET /brief/today?regenerate=1 streams these over SSE (event name = type).
export const briefStreamEventSchema = z.discriminatedUnion("type", [
  z.strictObject({ type: z.literal("brief.skeleton"), cards: z.number().int().min(0).max(3) }),
  z.strictObject({ type: z.literal("brief.card"), card: actionCardSchema }),
  z.strictObject({ type: z.literal("brief.done"), brief: briefSchema }),
]);
export type BriefStreamEvent = z.infer<typeof briefStreamEventSchema>;

export const approveResponseSchema = z.strictObject({
  run_id: z.string(),
  action_id: z.string(),
  deduplicated: z.boolean(),
});
export const rejectRequestSchema = z.strictObject({ reason: z.string().min(1).max(500) });
export const rejectResponseSchema = z.strictObject({
  action_id: z.string(),
  episode_id: z.string(),
  preference_fact_ids: z.array(z.string()),
});

export const contextPackSchema = z.strictObject({
  as_of: datetime,
  fact_ids: z.array(z.string()),
  text: z.string(),
  tokens: z.number().int(),
  budget_tokens: z.number().int(),
});
export const runSummarySchema = z.strictObject({
  id: z.string(),
  action_id: z.string(),
  task: skillTaskSchema,
  portal: portalSchema,
  status: runStatusSchema,
  mode: modeSchema,
  skill_version: z.number().int().nullable(),
  chaos_seed: z.number().int(),
  started_at: datetime,
  finished_at: datetime.nullable(),
  totals: runTotalsSchema,
  summary: z.string().nullable(),
  context_pack: contextPackSchema.nullable(),
});
export const undoResponseSchema = z.strictObject({ run_id: z.string(), undo_of: z.string() });
export const humanReplySchema = z.strictObject({
  action: z.enum(["resume", "cancel"]),
  note: z.string().max(500).nullable(),
});
export type RunSummary = z.infer<typeof runSummarySchema>;

export const skillSummarySchema = z.strictObject({
  id: z.string(),
  task: skillTaskSchema,
  portal: portalSchema,
  latest_version: z.number().int(),
  runs: z.number().int(),
  success_rate: z.number().min(0).max(1).nullable(),
  mean_latency_ms: z.number().nullable(),
  mean_usd: z.number().nullable(),
  updated_at: datetime,
});
export const skillVersionsSchema = z.strictObject({
  skill_id: z.string(),
  versions: z.array(skillSchema),
  diffs: z.array(skillDiffSchema),
});
export type SkillSummary = z.infer<typeof skillSummarySchema>;
export type SkillVersions = z.infer<typeof skillVersionsSchema>;

export const entityTypeSchema = z.enum([
  "business",
  "product",
  "ingredient",
  "supplier",
  "staff",
  "shift",
  "portal",
  "skill",
  "preference",
  "weather_day",
  "holiday",
  "insight",
  "action",
]);
export const graphNodeSchema = z.strictObject({
  id: z.string(),
  type: entityTypeSchema,
  name: z.string(),
});
export const graphFactSchema = z.strictObject({
  id: z.string(),
  subject_id: z.string(),
  predicate: z.string(),
  object_id: z.string().nullable(),
  value: json,
  valid_from: datetime,
  valid_to: datetime.nullable(),
  confidence: z.number().min(0).max(1),
});
export const memoryGraphSchema = z.strictObject({
  as_of: datetime,
  nodes: z.array(graphNodeSchema),
  facts: z.array(graphFactSchema),
});
export const episodeRefSchema = z.strictObject({
  id: z.string(),
  kind: z.enum(["invoice", "approval", "rejection", "chat", "run", "seed"]),
  occurred_at: datetime,
  summary: z.string(),
});
export const factDetailSchema = z.strictObject({
  fact: graphFactSchema,
  recorded_at: datetime,
  source: episodeRefSchema.nullable(),
  supersedes: z.array(z.string()),
  superseded_by: z.string().nullable(),
  invalidated_at: datetime.nullable(),
});
export const invoiceIngestResponseSchema = z.strictObject({
  episode_id: z.string(),
  fact_ids: z.array(z.string()),
  superseded_fact_ids: z.array(z.string()),
});
export type GraphNode = z.infer<typeof graphNodeSchema>;
export type GraphFact = z.infer<typeof graphFactSchema>;
export type MemoryGraph = z.infer<typeof memoryGraphSchema>;
export type FactDetail = z.infer<typeof factDetailSchema>;

export const chaosRequestSchema = z.strictObject({
  portal: portalSchema,
  seed: z.number().int().min(0).max(999),
});
export const chaosStateSchema = z.strictObject({
  portal: portalSchema,
  seed: z.number().int(),
  variants: z.record(z.string(), z.string()),
});
export type ChaosState = z.infer<typeof chaosStateSchema>;
