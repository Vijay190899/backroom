"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { isActive, NAV_ITEMS } from "./nav-items";

/** Section links in the desktop top bar; the current one is underlined in press red. */
export function TopBarLinks() {
  const pathname = usePathname();
  return (
    <ul className="flex items-stretch gap-6">
      {NAV_ITEMS.map(({ href, label }) => {
        const active = isActive(pathname, href);
        return (
          <li key={href}>
            <Link
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "relative flex h-14 items-center text-sm transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground hover:text-ink",
              )}
            >
              {label}
              <span
                aria-hidden
                className={cn(
                  "absolute inset-x-0 -bottom-px h-0.5 origin-left bg-press transition-transform duration-200 ease-[var(--t-ease-out)]",
                  active ? "scale-x-100" : "scale-x-0",
                )}
              />
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

/** Bottom tab bar for phones: icon plus label, five destinations. */
export function TabBarLinks() {
  const pathname = usePathname();
  return (
    <ul className="mx-auto flex max-w-md items-stretch justify-between px-2">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
        return (
          <li key={href} className="flex-1">
            <Link
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "relative flex min-h-16 flex-col items-center justify-center gap-1 text-[11px] transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground",
              )}
            >
              <span
                aria-hidden
                className={cn(
                  "absolute top-0 h-0.5 w-8 origin-center bg-press transition-transform duration-200 ease-[var(--t-ease-out)]",
                  active ? "scale-x-100" : "scale-x-0",
                )}
              />
              <Icon
                aria-hidden
                className={cn("size-5", active && "text-press-ink")}
                strokeWidth={1.75}
              />
              {label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
