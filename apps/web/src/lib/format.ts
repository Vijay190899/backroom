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

export const UNIT_SUFFIX: Record<string, string> = {
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

const UNSIGNED_UNITS = new Set(["eur", "eur_per_kg", "eur_per_l", "pct"]);

/**
 * A computed number for a figures table, where no sentence carries the direction:
 * like `displayNumber`, but a negative euro or percent keeps its minus sign ("−14%").
 */
export function displayFigure(n: EvidenceNumber): string {
  const signed = n.value < 0 && UNSIGNED_UNITS.has(n.unit);
  return (signed ? "\u2212" : "") + displayNumber(n);
}

const datelineFormat = new Intl.DateTimeFormat("en-GB", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "Europe/Berlin",
});

/** "Friday 13 November 2026", the masthead's dateline (café time). */
export function formatDateline(iso: string): string {
  return datelineFormat.format(new Date(iso));
}

const timeFormat = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "Europe/Berlin",
});

/** "08:30" in café time. */
export function formatTime(iso: string): string {
  return timeFormat.format(new Date(iso));
}
