import Link from "next/link";

export function Wordmark() {
  return (
    <Link
      href="/"
      aria-label="Backroom home"
      translate="no"
      className="inline-flex min-h-11 items-center rounded-sm"
    >
      <span className="inline-flex items-baseline gap-1">
        <span className="font-display text-[22px] leading-none font-medium tracking-tight text-ink">
          Backroom
        </span>
        <span aria-hidden className="size-1.5 bg-press" />
      </span>
    </Link>
  );
}
