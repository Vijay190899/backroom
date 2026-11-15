const KEY = "backroom-motion";
const QUERY = "(prefers-reduced-motion: reduce)";
const listeners = new Set<() => void>();

/**
 * "full" runs every effect (ambient light, particles, physics); "calm" shows finished
 * states only. The reader's choice in the header wins; without one, the system's
 * reduced-motion setting decides. One source for every animation in the app.
 */
export type MotionLevel = "full" | "calm";

export function motionLevel(): MotionLevel {
  if (typeof window === "undefined") return "full";
  // An explicit choice in the header wins; otherwise the system setting decides.
  let stored: string | null = null;
  try {
    stored = localStorage.getItem(KEY);
  } catch {
    // Private mode: fall through to the system setting.
  }
  if (stored === "calm" || stored === "full") return stored;
  return matchMedia(QUERY).matches ? "calm" : "full";
}

function notify() {
  document.documentElement.dataset.motion = motionLevel();
  listeners.forEach((l) => l());
}

export function setMotionLevel(level: MotionLevel): void {
  try {
    localStorage.setItem(KEY, level);
  } catch {
    // Private mode: the choice lasts for this page view.
  }
  notify();
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
export const motionInitScript = `(function(){try{var s=localStorage.getItem("${KEY}");var c=s?s==="calm":matchMedia("${QUERY}").matches;document.documentElement.dataset.motion=c?"calm":"full"}catch(e){}})()`;
