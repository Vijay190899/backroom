import type { EvidenceNumber } from "@/lib/contracts";

/** Half-up rounding, as the number guard does it (70.5 -> 71, not banker's 70). */
export function roundHalfUp(value: number, digits = 0): number {
  const factor = 10 ** digits;
  return Math.sign(value) * (Math.round(Math.abs(value) * factor + Number.EPSILON) / factor);
}

const eur = new Intl.NumberFormat("en-IE", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatEur(value: number): string {
  return eur.format(value);
}

function short(value: number): string {
  const rounded = roundHalfUp(value, 1);
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
}

const UNIT_SUFFIX: Record<string, string> = {
  days: " days",
  hours: " hours",
  mm: " mm",
  g: " g",
  ml: " ml",
};

/**
 * A computed number written the way the number guard accepts it
 * (mirrors `backroom_api.brief.guard.display`).
 */
export function displayNumber(n: EvidenceNumber): string {
  if (n.unit === "eur") return formatEur(Math.abs(n.value));
  if (n.unit === "eur_per_kg") return `${formatEur(Math.abs(n.value))}/kg`;
  if (n.unit === "eur_per_l") return `${formatEur(Math.abs(n.value))}/l`;
  if (n.unit === "pct") return `${short(Math.abs(n.value))}%`;
  return short(n.value) + (UNIT_SUFFIX[n.unit] ?? "");
}

const dayFormat = new Intl.DateTimeFormat("en-GB", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: "Europe/Berlin",
});

export function formatDay(iso: string): string {
  return dayFormat.format(new Date(iso));
}
