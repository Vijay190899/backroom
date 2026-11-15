import Link from "next/link";

export function Wordmark() {
  return (
    <Link href="/" aria-label="Backroom home" translate="no" className="group inline-flex min-h-11 items-center gap-2 rounded-lg px-1">
      <span aria-hidden className="relative grid size-6 place-items-center">
        <span className="absolute inset-0 rounded-md bg-press/25 blur-md transition-opacity duration-300 group-hover:opacity-100" />
        <span className="relative size-3 rounded-[3px] bg-gradient-to-br from-press to-amber shadow-[0_0_14px_var(--t-glow)]" />
      </span>
      <span className="text-[17px] font-semibold tracking-[-0.03em] text-ink">backroom</span>
    </Link>
  );
}
