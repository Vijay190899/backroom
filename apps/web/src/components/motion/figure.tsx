"use client";

import NumberFlow, { type Format } from "@number-flow/react";
import { useEffect, useState } from "react";

import type { EvidenceNumber } from "@/lib/contracts";
import { UNIT_SUFFIX } from "@/lib/format";
import { prefersReducedMotion } from "@/lib/motion";

const EUR = {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
} as const;

/**
 * A euro figure that rolls its digits into place like an odometer: once when it first
 * shows, and again whenever the value changes (a rebuilt brief rolls €86.80 to €54.25).
 * NumberFlow keeps the final value in the accessible name; under reduced motion the
 * value is simply shown.
 */
export function Figure({ value, className }: { value: number; className?: string }) {
  // Cards only render in the browser (the brief loads client-side), so matchMedia is safe.
  const [shown, setShown] = useState(() => (prefersReducedMotion() ? value : 0));

  useEffect(() => {
    // The first frame paints the start state; the next one sets the target, so it rolls.
    const frame = requestAnimationFrame(() => setShown(value));
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return (
    <NumberFlow
      value={shown}
      locales="en-IE"
      format={EUR}
      className={className}
      willChange
      transformTiming={{ duration: 900, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }}
      spinTiming={{ duration: 900, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }}
      opacityTiming={{ duration: 350, easing: "ease-out" }}
    />
  );
}

const SUFFIX: Record<string, string> = { ...UNIT_SUFFIX, eur_per_kg: "/kg", eur_per_l: "/l", pct: "%" };

/**
 * A computed number in a figures table, written as `displayFigure` writes it (unit,
 * cents, a real minus sign), whose digits roll when the value changes: a rebuilt brief
 * turns "€3.60" into "€3.45" in place instead of swapping text.
 */
export function FigureValue({ n, className }: { n: EvidenceNumber; className?: string }) {
  const money = n.unit === "eur" || n.unit === "eur_per_kg" || n.unit === "eur_per_l";
  const signed = n.value < 0 && (money || n.unit === "pct");
  const format: Format = money
    ? EUR
    : { maximumFractionDigits: 1, roundingMode: "halfExpand", useGrouping: false };
  return (
    <NumberFlow
      value={signed ? Math.abs(n.value) : n.value}
      locales="en-IE"
      format={format}
      prefix={signed ? "−" : undefined}
      suffix={SUFFIX[n.unit]}
      className={className}
      transformTiming={{ duration: 700, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }}
      spinTiming={{ duration: 700, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }}
    />
  );
}
