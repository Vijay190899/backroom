"use client";

import { Dialog } from "@base-ui/react/dialog";
import { CornerDownLeft, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { onPaletteOpen, useCommands, type Command } from "@/lib/commands";
import { isDark, setDark } from "@/lib/theme";
import { cn } from "@/lib/utils";

import { NAV_ITEMS } from "./nav-items";

/** ⌘K: jump anywhere or act on what's on screen (pages register their own commands). */
export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const pageCommands = useCommands();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() !== "k" || !(e.metaKey || e.ctrlKey)) return;
      // Not over another open dialog (evidence, reject): that dialog keeps the keyboard.
      const other = document.querySelector("[role=dialog]:not([data-palette])");
      if (other) return;
      e.preventDefault();
      setOpen((o) => !o);
    };
    addEventListener("keydown", onKey);
    const off = onPaletteOpen(setOpen);
    return () => {
      removeEventListener("keydown", onKey);
      off();
    };
  }, []);

  const commands = useMemo<Command[]>(
    () => [
      ...pageCommands,
      ...NAV_ITEMS.map((n) => ({ id: `go:${n.href}`, group: "Go to", label: n.label, run: () => router.push(n.href) })),
      { id: "theme", group: "Settings", label: "Switch light / dark theme", run: () => setDark(!isDark()) },
    ],
    [pageCommands, router],
  );
  const q = query.trim().toLowerCase();
  const shown = q ? commands.filter((c) => `${c.group} ${c.label}`.toLowerCase().includes(q)) : commands;
  const active = Math.min(index, Math.max(0, shown.length - 1));

  function run(command: Command | undefined) {
    if (!command) return;
    setOpen(false);
    setQuery("");
    setIndex(0);
    command.run();
  }

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          setQuery("");
          setIndex(0);
        }
      }}
    >
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup data-palette className="glass glass-solid fixed top-[14vh] left-1/2 z-[61] w-[min(36rem,calc(100vw-1.5rem))] -translate-x-1/2 overflow-hidden rounded-2xl outline-none transition-[opacity,scale,translate] duration-200 ease-[var(--t-ease-out)] data-[ending-style]:scale-[0.97] data-[ending-style]:opacity-0 data-[starting-style]:-translate-y-2 data-[starting-style]:scale-[0.97] data-[starting-style]:opacity-0">
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <div className="flex items-center gap-3 border-b border-glass-line px-4">
            <Search aria-hidden className="size-4 shrink-0 text-muted-foreground" />
            <input
              autoFocus
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIndex(0);
              }}
              onKeyDown={(e) => {
                if (e.key === "ArrowDown") {
                  e.preventDefault();
                  setIndex(Math.min(active + 1, shown.length - 1));
                } else if (e.key === "ArrowUp") {
                  e.preventDefault();
                  setIndex(Math.max(active - 1, 0));
                } else if (e.key === "Enter") {
                  e.preventDefault();
                  run(shown[active]);
                }
              }}
              role="combobox"
              aria-expanded
              aria-controls="palette-list"
              aria-activedescendant={shown[active] ? `cmd-${shown[active].id}` : undefined}
              aria-label="Search commands"
              placeholder="Approve a card, go to a page…"
              className="h-14 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-muted-foreground"
            />
          </div>
          <ul id="palette-list" role="listbox" aria-label="Commands" className="max-h-[50vh] overflow-y-auto overscroll-contain p-2">
            {shown.length === 0 ? (
              <li role="option" aria-selected={false} aria-disabled className="px-3 py-6 text-center text-sm text-muted-foreground">Nothing matches “{query}”.</li>
            ) : null}
            {shown.map((c, i) => (
              <li
                key={c.id}
                id={`cmd-${c.id}`}
                ref={i === active ? (el) => el?.scrollIntoView({ block: "nearest" }) : undefined}
                role="option"
                aria-selected={i === active}
                onPointerMove={() => setIndex(i)}
                onClick={() => run(c)}
                className={cn(
                  "flex min-h-11 cursor-pointer items-center justify-between gap-3 rounded-xl px-3 text-sm",
                  i === active ? "bg-glass-strong text-ink" : "text-muted-foreground",
                )}
              >
                <span>
                  <span className="mr-2 text-xs text-muted-foreground">{c.group}</span>
                  <span className="text-ink">{c.label}</span>
                </span>
                {i === active ? <CornerDownLeft aria-hidden className="size-3.5" /> : null}
              </li>
            ))}
          </ul>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
