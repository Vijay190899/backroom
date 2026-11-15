import type { CSSProperties } from "react";

import { motionLevel } from "@/lib/motion-pref";

/** Delay for the one-off `.enter` / `.enter-rule` entrance, so a page staggers in. */
export function enterDelay(ms: number): CSSProperties {
  return { "--enter-delay": `${ms}ms` } as CSSProperties;
}

/**
 * The reader asked for less motion (system setting or the header toggle): show finished
 * states instead of animating to them.
 */
export function prefersReducedMotion(): boolean {
  return motionLevel() === "calm";
}
