import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-4xl leading-none tracking-tight text-ink sm:text-5xl">
          {title}
        </h1>
        {subtitle ? <p className="mt-3 max-w-prose text-muted-foreground">{subtitle}</p> : null}
      </div>
      {actions}
    </header>
  );
}
