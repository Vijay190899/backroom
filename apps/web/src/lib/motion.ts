import type { CSSProperties } from "react";

/** Delay for the one-off `.enter` / `.enter-rule` entrance, so a page staggers in. */
export function enterDelay(ms: number): CSSProperties {
  return { "--enter-delay": `${ms}ms` } as CSSProperties;
}

/** The reader asked for less motion: show finished states instead of animating to them. */
export function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;
}
