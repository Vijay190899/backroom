"use client";

import { motion } from "motion/react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { isActive, NAV_ITEMS, navDirection } from "./nav-items";

const PILL = { type: "spring", stiffness: 420, damping: 34, mass: 0.8 } as const;

/** Section links in the floating header; a lit pill springs to the current one. */
export function TopBarLinks() {
  const pathname = usePathname();
  return (
    <ul className="flex items-center gap-1">
      {NAV_ITEMS.map(({ href, label }) => {
        const active = isActive(pathname, href);
        return (
          <li key={href} className="relative">
            {active ? (
              <motion.span
                layoutId="nav-pill"
                transition={PILL}
                aria-hidden
                className="absolute inset-0 rounded-xl border border-glass-line bg-glass-strong shadow-[0_0_24px_-6px_var(--t-glow)]"
              />
            ) : null}
            <Link
              href={href}
              aria-current={active ? "page" : undefined}
              transitionTypes={active ? undefined : [navDirection(pathname, href)]}
              className={cn(
                "relative flex h-10 items-center rounded-xl px-3.5 text-sm transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground hover:text-ink",
              )}
            >
              {label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

/** Floating tab bar for phones: icon plus label, a lit pill springs between them. */
export function TabBarLinks() {
  const pathname = usePathname();
  return (
    <ul className="flex items-stretch justify-between px-1">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
        return (
          <li key={href} className="relative flex-1">
            {active ? (
              <motion.span
                layoutId="tab-pill"
                transition={PILL}
                aria-hidden
                className="absolute inset-1 rounded-xl bg-glass-strong shadow-[0_0_24px_-8px_var(--t-glow)]"
              />
            ) : null}
            <Link
              href={href}
              aria-current={active ? "page" : undefined}
              transitionTypes={active ? undefined : [navDirection(pathname, href)]}
              className={cn(
                "relative flex min-h-15 flex-col items-center justify-center gap-0.5 text-[11px] transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground",
              )}
            >
              <Icon aria-hidden className={cn("size-5", active && "text-press-ink")} strokeWidth={1.75} />
              {label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
