import { useSyncExternalStore } from "react";

import type { RunEvent } from "@/lib/contracts";

/** A run the agent dock shows: recorded events to play, or just a note (nothing to play). */
export type AgentRun = {
  id: string;
  title: string;
  portal: string | null;
  events: RunEvent[] | null;
  note: string;
  /** The run theater for this run, when there is one to watch. */
  href: string | null;
};

type State = { runs: AgentRun[]; pulse: number };
let state: State = { runs: [], pulse: 0 };
const listeners = new Set<() => void>();
let dock: HTMLElement | null = null;

function set(next: State) {
  state = next;
  listeners.forEach((l) => l());
}

export function startRun(run: AgentRun): void {
  set({ ...state, runs: [run, ...state.runs.filter((r) => r.id !== run.id)] });
}

/** Particles reached the dock: it pulses. */
export function absorb(): void {
  set({ ...state, pulse: state.pulse + 1 });
}

export function useAgent(): State {
  return useSyncExternalStore(
    (l) => {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    () => state,
    () => state,
  );
}

export function setDockAnchor(el: HTMLElement | null): void {
  dock = el;
}

/** Where particles fly to: the dock's ring, or the bottom-right corner if it isn't there. */
export function dockPoint(): { x: number; y: number } {
  const r = dock?.getBoundingClientRect();
  return r ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : { x: innerWidth - 60, y: innerHeight - 60 };
}
