"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { isActive, NAV_ITEMS } from "./nav-items";

/** Vertical navigation for the desktop sidebar. */
export function SidebarLinks() {
  const pathname = usePathname();
  return (
    <ul className="flex flex-col gap-1">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
        return (
          <li key={href}>
            <Link
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "relative flex h-10 items-center gap-3 rounded-lg px-3 text-sm transition-colors duration-150",
                active
                  ? "bg-subtle font-medium text-ink"
                  : "text-muted-foreground hover:bg-subtle/60 hover:text-ink",
              )}
            >
              <span
                aria-hidden
                className={cn(
                  "absolute top-2 bottom-2 left-0 w-0.5 rounded-full bg-caramel transition-opacity duration-150",
                  active ? "opacity-100" : "opacity-0",
                )}
              />
              <Icon aria-hidden className="size-[18px] shrink-0" strokeWidth={1.75} />
              {label}
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
                "flex min-h-14 flex-col items-center justify-center gap-1 rounded-lg text-[11px] transition-colors duration-150",
                active ? "font-medium text-ink" : "text-muted-foreground",
              )}
            >
              <span
                className={cn(
                  "flex h-7 w-12 items-center justify-center rounded-full transition-colors duration-150",
                  active && "bg-subtle text-caramel-ink",
                )}
              >
                <Icon aria-hidden className="size-5" strokeWidth={1.75} />
              </span>
              {label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
