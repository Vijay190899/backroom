import { Suspense, type ReactNode } from "react";

import { ApiStatus } from "./api-status";
import { TabBarLinks, TopBarLinks } from "./nav-links";
import { ThemeToggle } from "./theme-toggle";
import { Wordmark } from "./wordmark";

/**
 * A newspaper's top bar: wordmark, section links, status. Phones swap the section links
 * for a bottom tab bar. The nav links read the pathname, so they sit inside Suspense
 * (Cache Components).
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col">
      <header
        style={{ viewTransitionName: "site-header" }}
        className="sticky top-0 z-20 border-b border-line bg-background/92 px-4 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center gap-8">
          <Wordmark />
          <nav aria-label="Main" className="hidden flex-1 lg:block">
            <Suspense fallback={<div className="h-14" />}>
              <TopBarLinks />
            </Suspense>
          </nav>
          <div className="ml-auto flex items-center gap-1">
            <ApiStatus />
            <ThemeToggle className="-mr-2" />
          </div>
        </div>
      </header>

      <main
        id="main"
        tabIndex={-1}
        className="flex-1 px-4 pt-6 pb-28 outline-none sm:px-6 lg:px-10 lg:pt-10 lg:pb-16"
      >
        <div className="mx-auto w-full max-w-6xl">{children}</div>
      </main>

      <nav
        aria-label="Main"
        style={{ viewTransitionName: "tab-bar" }}
        className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-sm lg:hidden"
      >
        <Suspense fallback={<div className="h-16" />}>
          <TabBarLinks />
        </Suspense>
      </nav>
    </div>
  );
}
