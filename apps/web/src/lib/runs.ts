"use client";

import type { RunEvent } from "@/lib/contracts";

export { describeChange } from "@/lib/run-view";

/**
 * Golden runs (PRD F7): real runs recorded with `python -m backroom_api.replay.golden record`
 * and served as static files from /golden/<name>/, so they play with no API at all.
 */
export const GOLDEN_FOR_TASK: Partial<Record<string, string>> = {
  "grainline.reorder_item": "reorder",
  "grainline.cancel_order": "cancel",
  "tilldesk.change_price": "price",
};
/** The reorder healing itself after the seed-7 redesign (DEMO_SCRIPT 1:40). */
export const GOLDEN_HEAL = "reorder-heal";
export const GOLDEN_PREFIX = "golden-";
export const goldenRunId = (name: string) => `${GOLDEN_PREFIX}${name}`;

export async function loadGoldenRun(name: string, signal?: AbortSignal): Promise<RunEvent[] | null> {
  const [{ runEventSchema }, res] = await Promise.all([
    import("@/lib/contracts"),
    fetch(`/golden/${encodeURIComponent(name)}/events.json`, { signal }),
  ]);
  if (!res.ok) return null;
  return runEventSchema.array().parse(await res.json());
}

/** What plays when the API is unreachable and a card is approved: the recorded real run of
 *  that card's task, if there is one. */
export async function loadSampleRun(task: string | null): Promise<RunEvent[] | null> {
  const name = task ? GOLDEN_FOR_TASK[task] : undefined;
  return name ? loadGoldenRun(name) : null;
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
