"use client";

import type { RunEvent, StepChange } from "@/lib/contracts";
import type { Locator } from "@/lib/skills";

/**
 * The committed sample run (fixtures/run-events.json), parsed like any API payload.
 * It belongs to one action; any other card has no recorded run to show.
 */
export async function loadSampleRun(actionId: string): Promise<RunEvent[] | null> {
  const [{ runEventSchema }, fixture] = await Promise.all([
    import("@/lib/contracts"),
    import("@/fixtures/run-events.json"),
  ]);
  const events = runEventSchema.array().parse(fixture.default);
  const start = events[0];
  return start?.type === "run.started" && start.action_id === actionId ? events : null;
}

function locatorName(value: unknown): string | null {
  const loc = value as Partial<Locator> | null;
  return loc && typeof loc.name === "string" ? loc.name : null;
}

/** "‘Sign in’ → ‘Anmelden’" or "+ Accept the cookie banner": what a heal changed. */
export function describeChange(change: StepChange): string {
  if (change.op === "insert") {
    const after = change.after as { intent?: string } | null;
    return `+ ${after?.intent ?? "new step"}`;
  }
  if (change.op === "delete") return `− step ${change.step_index + 1}`;
  const before = locatorName(change.before);
  const after = locatorName(change.after);
  return before && after ? `‘${before}’ → ‘${after}’` : `${change.field} updated`;
}

/** Playback pacing: about 2× real time, with failed waits (5 s timeouts) clipped. */
export function playbackDelay(event: RunEvent): number {
  switch (event.type) {
    case "step.finished":
      return Math.min(event.duration_ms, 600) / 3 + 80;
    case "heal.attempt":
      return 380;
    case "heal.succeeded":
    case "mode.changed":
      return 400;
    default:
      return 90;
  }
}
