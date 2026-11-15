import type { RunEvent, RunTotals, StepChange } from "./contracts";

/**
 * A run as the theater shows it, folded from its events (CONTRACTS §5). Pure, so the
 * same fold serves a recorded run, a live SSE stream and the node check
 * (run-view.check.mts). Every number here is an event field or a sum of them.
 */
export type Mode = "explore" | "replay" | "heal";
export type Locator = { role: string; name: string };
export type StepState = "running" | "ok" | "failed" | "healing" | "healed" | "heal_failed";
export type HealRung = { rung: "fallback" | "healer" | "escalation" | "human"; model: string | null; ok: boolean };

export type StepView = {
  index: number;
  intent: string;
  action: string;
  target: Locator | null;
  value: string | null;
  mode: Mode;
  state: StepState;
  startedAt: string;
  durationMs: number | null;
  llmCalls: number;
  tokensIn: number;
  tokensOut: number;
  usd: number;
  error: string | null;
  heal: {
    failure: string;
    rungs: HealRung[];
    changes: StepChange[];
    newVersion: number | null;
    /** The locator the healed skill uses for this step, when the heal re-targeted it. */
    target: Locator | null;
    /** Steps the heal inserted before this one (e.g. accept a cookie banner). */
    inserted: { intent: string; target: Locator | null }[];
  } | null;
};

type Finished = Extract<RunEvent, { type: "run.finished" }>;

export type RunView = {
  runId: string | null;
  actionId: string | null;
  task: string | null;
  portal: string | null;
  chaosSeed: number | null;
  recorded: boolean;
  mode: Mode;
  skillVersion: number | null;
  steps: StepView[];
  totals: RunTotals;
  elapsedMs: number;
  /** The path of the last page the agent opened. */
  path: string | null;
  askHuman: { reason: string; stepIndex: number | null } | null;
  /** Heals that succeeded (heal.succeeded events). */
  heals: number;
  finished: Finished | null;
};

const ZERO: RunTotals = { elapsed_ms: 0, steps: 0, llm_calls: 0, tokens_in: 0, tokens_out: 0, cache_read_tokens: 0, usd: 0 };

function locator(value: unknown): Locator | null {
  const v = value as Partial<Locator> | null;
  return v && typeof v.role === "string" && typeof v.name === "string" ? { role: v.role, name: v.name } : null;
}

const same = (a: Locator | null, b: Locator | null) => !!a && !!b && a.role === b.role && a.name === b.name;

/** "‘Sign in’ → ‘Anmelden’" or "+ Accept the cookie banner": what a heal changed. */
export function describeChange(change: StepChange): string {
  if (change.op === "insert") {
    const after = change.after as { intent?: string } | null;
    return `+ ${after?.intent ?? "new step"}`;
  }
  if (change.op === "delete") return `− step ${change.step_index + 1}`;
  const before = locator(change.before);
  const after = locator(change.after);
  return before && after ? `‘${before.name}’ → ‘${after.name}’` : `${change.field} updated`;
}

export function foldRun(events: readonly RunEvent[]): RunView {
  const view: RunView = {
    runId: null,
    actionId: null,
    task: null,
    portal: null,
    chaosSeed: null,
    recorded: false,
    mode: "replay",
    skillVersion: null,
    steps: [],
    totals: ZERO,
    elapsedMs: 0,
    path: null,
    askHuman: null,
    heals: 0,
    finished: null,
  };
  // Cost arrives in cost.tick snapshots; steps that finish after the last tick add theirs.
  let tick: RunTotals = ZERO;
  let since = { llm_calls: 0, tokens_in: 0, tokens_out: 0, usd: 0 };
  let startTs: number | null = null;
  let lastTs: number | null = null;
  const byIndex = (i: number) => view.steps.findLast((s) => s.index === i);

  for (const e of events) {
    const t = Date.parse(e.ts);
    startTs ??= t;
    lastTs = t;
    view.runId ??= e.run_id;
    // The agent moved on after asking for a person: the request is answered.
    if (view.askHuman && e.type !== "ask_human" && e.type !== "cost.tick") view.askHuman = null;
    switch (e.type) {
      case "run.started":
        Object.assign(view, {
          actionId: e.action_id,
          task: e.task,
          portal: e.portal,
          chaosSeed: e.chaos_seed,
          recorded: e.recorded,
          mode: e.mode,
          skillVersion: e.skill_version,
        });
        break;
      case "step.started":
        view.steps.push({
          index: e.index,
          intent: e.intent,
          action: e.action,
          target: e.target,
          // Secrets and one-time codes are never kept, even if a stream carried them.
          value: e.action === "fill_secret" || e.action === "totp" ? null : e.value,
          mode: e.mode,
          state: "running",
          startedAt: e.ts,
          durationMs: null,
          llmCalls: 0,
          tokensIn: 0,
          tokensOut: 0,
          usd: 0,
          error: null,
          heal: null,
        });
        if (e.action === "goto" && e.value) view.path = e.value;
        break;
      case "step.finished": {
        const s = byIndex(e.index);
        // A healed step keeps its verdict; a late finish for it only adds its numbers.
        if (s && (s.state === "healed" || s.state === "heal_failed")) {
          Object.assign(s, { durationMs: e.duration_ms, llmCalls: e.llm_calls, tokensIn: e.tokens_in, tokensOut: e.tokens_out, usd: e.usd });
        } else if (s) {
          Object.assign(s, {
            state: e.ok ? "ok" : "failed",
            durationMs: e.duration_ms,
            llmCalls: e.llm_calls,
            tokensIn: e.tokens_in,
            tokensOut: e.tokens_out,
            usd: e.usd,
            error: e.error,
          });
        }
        since = {
          llm_calls: since.llm_calls + e.llm_calls,
          tokens_in: since.tokens_in + e.tokens_in,
          tokens_out: since.tokens_out + e.tokens_out,
          usd: since.usd + e.usd,
        };
        break;
      }
      case "mode.changed":
        view.mode = e.to_mode;
        break;
      case "heal.started": {
        const s = byIndex(e.step_index);
        if (s) {
          s.state = "healing";
          s.heal = { failure: e.failure, rungs: [], changes: [], newVersion: null, target: null, inserted: [] };
        }
        break;
      }
      case "heal.attempt":
        byIndex(e.step_index)?.heal?.rungs.push({ rung: e.rung, model: e.model, ok: e.ok });
        break;
      case "heal.succeeded": {
        const s = byIndex(e.step_index);
        if (s?.heal) {
          s.state = "healed";
          s.heal.changes = e.changes;
          s.heal.newVersion = e.new_version;
          for (const c of e.changes) {
            if (c.op === "insert") {
              const after = c.after as { intent?: string; target?: unknown } | null;
              s.heal.inserted.push({ intent: after?.intent ?? "New step", target: locator(after?.target) });
            }
            if (c.op === "update" && c.field === "target" && same(locator(c.before), s.target)) {
              s.heal.target = locator(c.after);
            }
          }
        }
        view.skillVersion = e.new_version;
        view.heals += 1;
        break;
      }
      case "heal.failed": {
        const s = byIndex(e.step_index);
        if (s) s.state = "heal_failed";
        break;
      }
      case "cost.tick":
        tick = e.totals;
        since = { llm_calls: 0, tokens_in: 0, tokens_out: 0, usd: 0 };
        if (e.skill_version !== null) view.skillVersion = e.skill_version;
        break;
      case "ask_human":
        view.askHuman = { reason: e.reason, stepIndex: e.step_index };
        break;
      case "run.finished":
        view.finished = e;
        // Nothing is still running once the run is over (a failed or cancelled run).
        for (const s of view.steps) {
          if (s.state === "running") s.state = "failed";
          if (s.state === "healing") s.state = "heal_failed";
        }
        tick = e.totals;
        since = { llm_calls: 0, tokens_in: 0, tokens_out: 0, usd: 0 };
        if (e.skill_version !== null) view.skillVersion = e.skill_version;
        view.askHuman = null;
        break;
    }
  }

  view.elapsedMs = view.finished ? view.finished.totals.elapsed_ms : startTs !== null && lastTs !== null ? lastTs - startTs : 0;
  view.totals = {
    ...tick,
    steps: view.steps.length,
    llm_calls: tick.llm_calls + since.llm_calls,
    tokens_in: tick.tokens_in + since.tokens_in,
    tokens_out: tick.tokens_out + since.tokens_out,
    usd: tick.usd + since.usd,
    elapsed_ms: view.elapsedMs,
  };
  return view;
}

/** How long to wait before showing the next recorded event: real time, waits clipped. */
export function gapMs(events: readonly RunEvent[], i: number, speed: number): number {
  const a = events[i - 1];
  const b = events[i];
  if (!a || !b) return 0;
  const real = Date.parse(b.ts) - Date.parse(a.ts);
  // A failed 5 s locator wait reads as a stall on screen; show it as a short pause.
  return Math.max(40, Math.min(real, 900) / speed);
}
