import type { ReactNode } from "react";

import { enterDelay } from "@/lib/motion";

/**
 * A section front: kicker line, a large serif title, the thick-and-thin rule, then a
 * standfirst with the page's actions beside it. The text is visible from the first
 * frame (it is the page's first paint); only the rule draws in.
 */
export function PageHeader({
  title,
  kicker,
  meta,
  subtitle,
  actions,
}: {
  title: string;
  kicker?: ReactNode;
  meta?: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-10 lg:mb-12">
      {kicker || meta ? (
        <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
          {kicker ? <p className="kicker text-press-ink">{kicker}</p> : <span />}
          {meta ? <p className="text-sm text-muted-foreground tabular">{meta}</p> : null}
        </div>
      ) : null}
      <h1 className="mt-3 font-display text-[2.75rem] leading-[0.95] font-medium tracking-[-0.02em] text-ink sm:text-6xl lg:text-7xl">
        {title}
      </h1>
      <div aria-hidden className="enter-rule rule-double mt-5" style={enterDelay(60)} />
      {subtitle || actions ? (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
          {subtitle ? (
            <p className="max-w-prose font-serif text-lg leading-snug text-muted-foreground">
              {subtitle}
            </p>
          ) : (
            <span />
          )}
          {actions}
        </div>
      ) : null}
    </header>
  );
}
