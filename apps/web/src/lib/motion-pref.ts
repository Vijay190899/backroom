const QUERY = "(prefers-reduced-motion: reduce)";
const listeners = new Set<() => void>();

/**
 * "full" runs every effect (ambient scene, particles, physics); "calm" shows finished
 * states only. The app is always in motion unless the device asks for reduced motion
 * (an accessibility setting, CLAUDE.md quality bar). One source for every animation.
 */
export type MotionLevel = "full" | "calm";

export function motionLevel(): MotionLevel {
  if (typeof window === "undefined") return "full";
  return matchMedia(QUERY).matches ? "calm" : "full";
}

function notify() {
  document.documentElement.dataset.motion = motionLevel();
  listeners.forEach((l) => l());
}

export function subscribeMotion(listener: () => void): () => void {
  listeners.add(listener);
  const query = matchMedia(QUERY);
  query.addEventListener("change", notify);
  return () => {
    listeners.delete(listener);
    query.removeEventListener("change", notify);
  };
}

/** Runs before first paint (inline in <head>), so CSS can key off `html[data-motion]`. */
export const motionInitScript = `(function(){try{document.documentElement.dataset.motion=matchMedia("${QUERY}").matches?"calm":"full"}catch(e){}})()`;
