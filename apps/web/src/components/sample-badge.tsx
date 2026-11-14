import { FlaskConical } from "lucide-react";

/** The visible "not live" marker every sample-backed screen carries (PRD §7, L-68). */
export function SampleBadge({ label = "Sample data", why }: { label?: string; why: string }) {
  return (
    <span
      title={why}
      className="kicker inline-flex h-11 items-center gap-1.5 border border-dashed border-ink/30 px-3 text-muted-foreground sm:h-10"
    >
      <FlaskConical aria-hidden className="size-3.5" />
      {label}
    </span>
  );
}

/** Holds the badge's space while data loads, so the header doesn't shift when it appears. */
export function BadgeSlot() {
  return (
    <span aria-hidden className="invisible">
      <SampleBadge why="" />
    </span>
  );
}
