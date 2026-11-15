"use client";

import type { RunEvent } from "@/lib/contracts";

export { describeChange } from "@/lib/run-view";

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
