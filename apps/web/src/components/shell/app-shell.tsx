import { Suspense, type ReactNode } from "react";

import { CafePattern } from "@/components/fx/cafe-pattern";

import { ApiStatus } from "./api-status";
import { CommandButton } from "./command-button";
import { TabBarLinks, TopBarLinks } from "./nav-links";
import { ShellExtras } from "./shell-extras";
import { ThemeToggle } from "./theme-toggle";
import { Wordmark } from "./wordmark";

/**
 * A floating glass header over the café pattern; phones get a floating tab bar. The
 * agent dock, particle canvas and ⌘K palette load after first paint (ShellExtras). The
 * nav links read the pathname, so they sit inside Suspense (Cache Components).
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col">
      <header style={{ viewTransitionName: "site-header" }} className="sticky top-0 z-30 px-3 pt-3 sm:px-6">
        <div className="glass mx-auto flex h-14 w-full max-w-6xl items-center gap-4 rounded-2xl glass-solid px-3">
          <Wordmark />
          <nav aria-label="Main" className="hidden flex-1 lg:block">
            <Suspense fallback={<div className="h-10" />}>
              <TopBarLinks />
            </Suspense>
          </nav>
          <div className="ml-auto flex items-center gap-1">
            <ApiStatus />
            <CommandButton />
            <ThemeToggle />
          </div>
        </div>
      </header>
      <CafePattern />

      <main id="main" tabIndex={-1} className="flex-1 px-4 pt-8 pb-44 outline-none sm:px-6 lg:px-10 lg:pt-12 lg:pb-28">
        <div className="mx-auto w-full max-w-6xl">{children}</div>
      </main>

      <nav
        aria-label="Main"
        style={{ viewTransitionName: "tab-bar" }}
        className="glass fixed inset-x-3 bottom-3 z-30 rounded-2xl glass-solid pb-[env(safe-area-inset-bottom)] lg:hidden"
      >
        <Suspense fallback={<div className="h-15" />}>
          <TabBarLinks />
        </Suspense>
      </nav>
      <ShellExtras />
    </div>
  );
}
