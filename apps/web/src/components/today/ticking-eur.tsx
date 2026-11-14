"use client";

import { useEffect, useState } from "react";

import { formatEur } from "@/lib/format";

const DURATION_MS = 700;

function reducedMotion(): boolean {
  return typeof window !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * A euro figure that counts up to its value once, on first show (PRD §7: numbers that
 * tick to value). Screen readers get the final value; reduced motion skips the count.
 */
export function TickingEur({ value, className }: { value: number; className?: string }) {
  // Cards only render in the browser (the brief loads client-side), so matchMedia is safe.
  const [shown, setShown] = useState(() => (reducedMotion() ? value : 0));

  useEffect(() => {
    if (reducedMotion()) return;
    let frame = 0;
    const start = performance.now();
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / DURATION_MS);
      setShown(value * (1 - (1 - t) ** 3));
      if (t < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    // A throttled or hidden tab can drop the last frame; the figure must still land exact.
    const land = setTimeout(() => {
      cancelAnimationFrame(frame);
      setShown(value);
    }, DURATION_MS + 50);
    return () => {
      cancelAnimationFrame(frame);
      clearTimeout(land);
    };
  }, [value]);

  return (
    <span className={className}>
      <span className="sr-only">{formatEur(value)}</span>
      <span aria-hidden className="tabular">
        {formatEur(reducedMotion() ? value : shown)}
      </span>
    </span>
  );
}
