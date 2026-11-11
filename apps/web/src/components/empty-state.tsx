import type { LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  body,
  milestone,
}: {
  icon: LucideIcon;
  title: string;
  body: string;
  milestone?: string;
}) {
  return (
    <section className="rounded-[var(--t-radius-card)] border border-line bg-surface px-6 py-12 text-center sm:py-16">
      <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-subtle text-caramel-ink">
        <Icon aria-hidden className="size-5" strokeWidth={1.75} />
      </span>
      <h2 className="mt-5 font-display text-2xl text-ink">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-muted-foreground">{body}</p>
      {milestone ? (
        <p className="mt-5 inline-flex items-center rounded-full border border-line px-2.5 py-1 font-mono text-xs text-muted-foreground">
          {milestone}
        </p>
      ) : null}
    </section>
  );
}
