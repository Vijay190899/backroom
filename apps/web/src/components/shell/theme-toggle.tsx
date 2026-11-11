"use client";

import { Moon, Sun } from "lucide-react";
import { useSyncExternalStore } from "react";

import { isDark, setDark, subscribeTheme } from "@/lib/theme";
import { cn } from "@/lib/utils";

export function ThemeToggle({ className }: { className?: string }) {
  // The server cannot know the theme; the client snapshot takes over after hydration.
  const dark = useSyncExternalStore(subscribeTheme, isDark, () => false);
  const Icon = dark ? Sun : Moon;
  return (
    <button
      type="button"
      onClick={() => setDark(!dark)}
      aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      className={cn(
        "inline-flex size-11 cursor-pointer items-center justify-center rounded-lg text-muted-foreground transition-colors duration-150 hover:bg-subtle hover:text-ink",
        className,
      )}
    >
      <Icon aria-hidden className="size-[18px]" strokeWidth={1.75} />
    </button>
  );
}
