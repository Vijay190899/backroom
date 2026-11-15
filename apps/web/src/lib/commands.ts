import { useEffect, useSyncExternalStore } from "react";

/** One action in the ⌘K palette. Pages register their own (approve a card, open evidence…). */
export type Command = {
  id: string;
  label: string;
  group: string;
  hint?: string;
  run: () => void;
};

const sources = new Map<string, Command[]>();
const listeners = new Set<() => void>();
let snapshot: Command[] = [];

function publish() {
  snapshot = [...sources.values()].flat();
  listeners.forEach((l) => l());
}

export function registerCommands(owner: string, commands: Command[]): () => void {
  sources.set(owner, commands);
  publish();
  return () => {
    sources.delete(owner);
    publish();
  };
}

export function useCommands(): Command[] {
  return useSyncExternalStore(
    (l) => {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    () => snapshot,
    () => snapshot,
  );
}

/** Register a page's commands while it is mounted. */
export function useRegisterCommands(owner: string, commands: Command[]): void {
  useEffect(() => registerCommands(owner, commands), [owner, commands]);
}

const openListeners = new Set<(open: boolean) => void>();
export function openPalette(): void {
  openListeners.forEach((l) => l(true));
}
export function onPaletteOpen(listener: (open: boolean) => void): () => void {
  openListeners.add(listener);
  return () => openListeners.delete(listener);
}
