import { Suspense, type ReactNode } from "react";

import { ApiStatus } from "./api-status";
import { SidebarLinks, TabBarLinks } from "./nav-links";
import { ThemeToggle } from "./theme-toggle";
import { BusinessBadge, Wordmark } from "./wordmark";

/**
 * Sidebar on large screens; top bar plus bottom tab bar on phones.
 * The nav links read the pathname, so they sit inside Suspense (Cache Components).
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh">
      <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col border-r border-line px-4 py-6 lg:flex">
        <div className="px-2">
          <Wordmark />
        </div>
        <nav aria-label="Main" className="mt-8 flex-1">
          <Suspense fallback={<div className="h-56" />}>
            <SidebarLinks />
          </Suspense>
        </nav>
        <div className="space-y-4 border-t border-line px-2 pt-4">
          <BusinessBadge />
          <div className="flex items-center justify-between">
            <ApiStatus />
            <ThemeToggle className="-mr-2" />
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-line bg-background/90 px-4 backdrop-blur lg:hidden">
          <Wordmark />
          <div className="flex items-center gap-1">
            <ApiStatus />
            <ThemeToggle className="-mr-2" />
          </div>
        </header>

        <main
          id="main"
          tabIndex={-1}
          className="flex-1 px-4 pt-6 pb-28 outline-none sm:px-6 lg:px-10 lg:pt-10 lg:pb-12"
        >
          <div className="mx-auto w-full max-w-5xl">{children}</div>
        </main>
      </div>

      <nav
        aria-label="Main"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
      >
        <Suspense fallback={<div className="h-14" />}>
          <TabBarLinks />
        </Suspense>
      </nav>
    </div>
  );
}
