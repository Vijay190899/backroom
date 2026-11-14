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
    <section className="enter border-y border-line py-14 text-center sm:py-20">
      <Icon aria-hidden className="mx-auto size-6 text-press-ink" strokeWidth={1.5} />
      <h2 className="mt-5 font-display text-3xl font-medium tracking-tight text-ink">
        {title}
      </h2>
      <p className="mx-auto mt-3 max-w-md font-serif text-lg leading-relaxed text-muted-foreground">
        {body}
      </p>
      {milestone ? <p className="kicker mt-6 text-muted-foreground">{milestone}</p> : null}
    </section>
  );
}
