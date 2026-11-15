import { useSyncExternalStore } from "react";

/**
 * What the café scene behind the app shows, driven by the app (L-78):
 * - `raining`: the brief on screen carries a rain forecast (weather card);
 * - `deliveries`: bumps when a supplier order is approved (a van pulls up);
 * - `busy`: the agent is running at least one task (the barista works faster);
 * - `serves`: bumps when a run finishes (a cup is served).
 */
type Scene = { raining: boolean; busy: boolean; deliveries: number; serves: number };

let scene: Scene = { raining: false, busy: false, deliveries: 0, serves: 0 };
let working = 0;
const listeners = new Set<() => void>();

function set(patch: Partial<Scene>) {
  scene = { ...scene, ...patch };
  listeners.forEach((l) => l());
}

export function setRaining(raining: boolean): void {
  if (scene.raining !== raining) set({ raining });
}
/** Marks one run as in progress; call the returned function when it stops. */
export function startWork(): () => void {
  working += 1;
  if (!scene.busy) set({ busy: true });
  let stopped = false;
  return () => {
    if (stopped) return;
    stopped = true;
    working -= 1;
    if (working === 0) set({ busy: false });
  };
}
export function deliver(): void {
  set({ deliveries: scene.deliveries + 1 });
}
export function serve(): void {
  set({ serves: scene.serves + 1 });
}

export function useScene(): Scene {
  return useSyncExternalStore(
    (l) => {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    () => scene,
    () => scene,
  );
}
