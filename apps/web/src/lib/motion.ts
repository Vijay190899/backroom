import type { CSSProperties } from "react";

/** Delay for the one-off `.enter` / `.enter-rule` entrance, so a page staggers in. */
export function enterDelay(ms: number): CSSProperties {
  return { "--enter-delay": `${ms}ms` } as CSSProperties;
}
