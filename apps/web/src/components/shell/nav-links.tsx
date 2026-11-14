"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { isActive, NAV_ITEMS, navDirection } from "./nav-items";

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
              transitionTypes={active ? undefined : [navDirection(pathname, href)]}
              className={cn(
                "relative flex h-14 items-center text-sm transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground hover:text-ink",
              )}
            >
              {label}
              {/* One indicator, named for the view transition, so it glides to the new section. */}
              {active ? (
                <span
                  aria-hidden
                  style={{ viewTransitionName: "nav-indicator" }}
                  className="absolute inset-x-0 -bottom-px h-0.5 bg-press"
                />
              ) : null}
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
              transitionTypes={active ? undefined : [navDirection(pathname, href)]}
              className={cn(
                "relative flex min-h-16 flex-col items-center justify-center gap-1 text-[11px] transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground",
              )}
            >
              {active ? (
                <span
                  aria-hidden
                  style={{ viewTransitionName: "tab-indicator" }}
                  className="absolute top-0 h-0.5 w-8 bg-press"
                />
              ) : null}
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
