import Link from "next/link";

export function Wordmark() {
  return (
    <Link
      href="/"
      aria-label="Backroom home"
      className="inline-flex items-baseline gap-1.5 rounded-md"
    >
      <span className="font-display text-[26px] leading-none tracking-tight text-ink">
        Backroom
      </span>
      <span aria-hidden className="size-1.5 rounded-full bg-caramel" />
    </Link>
  );
}

export function BusinessBadge() {
  return (
    <div className="flex items-center gap-3">
      <span
        aria-hidden
        className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-ink font-display text-sm text-background"
      >
        H&amp;B
      </span>
      <div className="min-w-0 leading-tight">
        <p className="truncate text-sm font-medium text-ink">Hafer &amp; Bohne</p>
        <p className="truncate text-xs text-muted-foreground">Bonn-Südstadt</p>
      </div>
    </div>
  );
}
