"use client";

import { Search } from "lucide-react";

import { openPalette } from "@/lib/commands";

export function CommandButton() {
  return (
    <button
      type="button"
      onClick={openPalette}
      aria-label="Open the command palette"
      className="group inline-flex h-11 cursor-pointer items-center gap-2 rounded-xl border border-glass-line bg-glass px-3 text-sm text-muted-foreground transition-colors duration-150 hover:text-ink"
    >
      <Search aria-hidden className="size-4" strokeWidth={1.75} />
      <span className="hidden md:inline">Search or act</span>
      <kbd className="hidden rounded-md border border-glass-line px-1.5 font-mono text-[11px] md:inline">⌘K</kbd>
    </button>
  );
}
