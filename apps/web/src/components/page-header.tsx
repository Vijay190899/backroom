import type { ReactNode } from "react";

import { enterDelay } from "@/lib/motion";

/**
 * A page's opening: a small label, then a large headline whose words drop into place
 * one by one on a spring (CSS only, so it starts with the first paint), then a line of
 * context with the page's actions beside it. That line is visible from the first frame:
 * it is the largest paint on phones.
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
  const words = title.split(" ");
  return (
    <header className="mb-8 lg:mb-10">
      {kicker || meta ? (
        <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
          {kicker ? <p className="kicker text-press-ink">{kicker}</p> : <span />}
          {meta ? <p className="text-sm text-muted-foreground tabular">{meta}</p> : null}
        </div>
      ) : null}
      <h1 className="mt-3 text-[2.5rem] leading-[0.98] font-semibold tracking-[-0.045em] text-ink sm:text-6xl lg:text-7xl">
        {words.map((word, i) => (
          <span key={i} className="inline-block overflow-hidden pb-[0.12em] align-bottom">
            <span
              style={enterDelay(i * 70)}
              className={`word-drop inline-block ${i === words.length - 1 ? "text-ember" : ""}`}
            >
              {word}
            </span>
            {i < words.length - 1 ? " " : ""}
          </span>
        ))}
      </h1>
      {subtitle || actions ? (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
          {subtitle ? <p className="max-w-prose text-lg leading-snug text-muted-foreground">{subtitle}</p> : <span />}
          {actions}
        </div>
      ) : null}
    </header>
  );
}
