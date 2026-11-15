import type { GraphFact, GraphNode } from "@/lib/contracts";

const DAY = 86_400_000;

/** True when the fact was valid at `t` (bitemporal: valid_from inclusive, valid_to exclusive). */
export function validAt(fact: GraphFact, t: number): boolean {
  const from = Date.parse(fact.valid_from);
  const to = fact.valid_to ? Date.parse(fact.valid_to) : Infinity;
  return from <= t && t < to;
}

// The café's days are Bonn days: a price that changes at midnight in Bonn (23:00 UTC in
// winter) belongs to the next day, not the one UTC still shows.
const BONN = new Intl.DateTimeFormat("en-US", {
  timeZone: "Europe/Berlin",
  hourCycle: "h23",
  year: "numeric",
  month: "numeric",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
});

/** How far Bonn's clock is ahead of UTC at `t` (1 h in winter, 2 h in summer). */
export function bonnOffset(t: number): number {
  const p = Object.fromEntries(BONN.formatToParts(t).map((x) => [x.type, x.value]));
  const local = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute);
  return local - Math.floor(t / 60_000) * 60_000;
}

/** The Bonn calendar day `t` falls on, as midnight UTC of that date: the slider's unit. */
export function dayOf(t: number): number {
  return Math.floor((t + bonnOffset(t)) / DAY) * DAY;
}

/** "As of a day" means as of the end of that day in Bonn: a fact from 07:30 counts, one
 *  from the next midnight does not. */
export function endOfDay(day: number): number {
  const next = dayOf(day) + DAY;
  return next - bonnOffset(next - bonnOffset(next)) - 1;
}

/**
 * The slider's range in whole days: a few days before the first fact, up to the
 * graph's as-of day, with a tick on each day the record changed. Null for an empty graph.
 */
export function timeline(facts: GraphFact[], asOf: string) {
  if (!facts.length) return null;
  const end = dayOf(Date.parse(asOf));
  const first = Math.min(...facts.map((f) => Date.parse(f.valid_from)));
  const start = dayOf(first) - 3 * DAY;
  const changes = [
    ...new Set(
      facts
        .flatMap((f) => [f.valid_from, ...(f.valid_to ? [f.valid_to] : [])])
        .map((d) => dayOf(Date.parse(d))),
    ),
  ]
    .filter((t) => t > start && t <= end)
    .sort((a, b) => a - b);
  return { start, end, changes, day: DAY };
}

/** One line of the record: a subject's predicate, now and (if replaced) before. */
export type Slot = {
  key: string;
  subject: GraphNode | undefined;
  predicate: string;
  current: GraphFact | null;
  previous: GraphFact | null;
};

/** Facts grouped by subject + predicate, as true at `t` (valid time). Facts not yet true are left out. */
export function record(nodes: GraphNode[], facts: GraphFact[], t: number): Slot[] {
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const slots = new Map<string, GraphFact[]>();
  for (const f of facts) {
    const key = `${f.subject_id}|${f.predicate}|${f.object_id ?? ""}`;
    const group = slots.get(key) ?? [];
    group.push(f);
    slots.set(key, group);
  }
  const out: Slot[] = [];
  for (const [key, group] of slots) {
    const known = group.filter((f) => Date.parse(f.valid_from) <= t);
    if (!known.length) continue;
    const current = known.find((f) => validAt(f, t)) ?? null;
    const ended = known
      .filter((f) => f.valid_to && Date.parse(f.valid_to) <= t)
      .sort((a, b) => Date.parse(b.valid_to ?? "") - Date.parse(a.valid_to ?? ""));
    out.push({
      key,
      subject: byId.get(group[0].subject_id),
      predicate: group[0].predicate,
      current,
      previous: ended[0] ?? null,
    });
  }
  return out;
}

export const PREDICATE: Record<string, string> = {
  unit_price_eur_per_kg: "costs",
  menu_price_eur: "sells at",
  supplied_by: "is supplied by",
  uses_ingredient: "uses",
  has_preference: "prefers",
};

const TYPE_COLUMN: Record<string, number> = {
  business: 0,
  preference: 0,
  product: 1,
  ingredient: 2,
  supplier: 3,
  portal: 3,
};

/** The graph draws the story (who the café is, what it sells, what that is made of, who
 *  supplies it). Context rows (staff, shifts, weather days, holidays...) stay in the record:
 *  drawn, 30-odd of them would bury the story. */
export function isDrawn(node: GraphNode): boolean {
  return node.type in TYPE_COLUMN;
}

export type Layout = { pos: Map<string, { x: number; y: number }>; minHeight: number };

const ROW_PX = 80; // a dot, its type, a two-line name and a value, with air
const PHONE_ROW_PX = 58;

/**
 * Deterministic layout: one band per role. Wide containers lay the bands out as columns,
 * narrow ones (phones) as rows of two. Percent coordinates, plus the height the busiest
 * band needs, so a real café's memory never stacks labels on top of each other.
 */
export function layout(nodes: GraphNode[], narrow = false): Layout {
  const bands = new Map<number, GraphNode[]>();
  for (const n of nodes.filter(isDrawn)) {
    const c = TYPE_COLUMN[n.type];
    bands.set(c, [...(bands.get(c) ?? []), n]);
  }
  const used = [...bands.keys()].sort((a, b) => a - b);
  const pos = new Map<string, { x: number; y: number }>();
  if (narrow) {
    const rows = used.reduce((sum, c) => sum + Math.ceil((bands.get(c) ?? []).length / 2), 0);
    let row = 0;
    for (const c of used) {
      const band = bands.get(c) ?? [];
      band.forEach((n, i) => {
        // Labels sit right of their dot here, so two per row: left half and right half.
        pos.set(n.id, { x: i % 2 === 0 ? 4 : 52, y: ((row + Math.floor(i / 2) + 0.35) / rows) * 100 });
      });
      row += Math.ceil(band.length / 2);
    }
    return { pos, minHeight: rows * PHONE_ROW_PX };
  }
  const tallest = Math.max(1, ...used.map((c) => (bands.get(c) ?? []).length));
  used.forEach((c, bi) => {
    const band = bands.get(c) ?? [];
    const along = used.length === 1 ? 50 : 12 + (bi * 76) / (used.length - 1);
    band.forEach((n, i) => {
      // Rows share one pitch across columns, centred in the box.
      const y = 50 + ((i - (band.length - 1) / 2) * 100) / (tallest + 1);
      pos.set(n.id, { x: along, y });
    });
  });
  return { pos, minHeight: (tallest + 1) * ROW_PX };
}

/** Which timeline ticks get a date label: never two closer than `minGapPct`. */
export function labelledTicks(ticks: number[], pct: (v: number) => number, minGapPct = 7): Set<number> {
  const out = new Set<number>();
  let last = -Infinity;
  for (const t of [...ticks].sort((a, b) => a - b)) {
    if (pct(t) - last >= minGapPct) {
      out.add(t);
      last = pct(t);
    }
  }
  return out;
}

const UNIT: Record<string, (v: unknown) => string> = {
  tmax_c: (v) => `${v} °C`,
  precip_mm: (v) => `${v} mm rain`,
  grams: (v) => `${v} g`,
  ml: (v) => `${v} ml`,
  pcs: (v) => `${v} pcs`,
  margin_target_pct: (v) => `a ${v}% margin`,
  max_price_increase_pct: (v) => `rises of at most ${v}%`,
  weekdays: (v) => (Array.isArray(v) ? v.map((d) => String(d).slice(0, 1).toUpperCase() + String(d).slice(1)).join(" and ") : String(v)),
};

/** A structured fact value in words ("11.1 °C, 0.3 mm rain (archive)"), never raw JSON:
 *  real memory holds weather, amounts, roles and rules the sample never had. */
export function describeValue(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value !== "object" || Array.isArray(value)) return String(value);
  const entries = Object.entries(value as Record<string, unknown>);
  const source = entries.find(([k]) => k === "source")?.[1];
  const parts = entries
    .filter(([k]) => k !== "source")
    .map(([k, v]) => (UNIT[k] ? UNIT[k](v) : `${k.replace(/_/g, " ")} ${String(v)}`));
  return parts.join(", ") + (source ? ` (${String(source)})` : "");
}
