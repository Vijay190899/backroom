import type { GraphFact, GraphNode } from "@/lib/contracts";

const DAY = 86_400_000;

/** True when the fact was valid at `t` (bitemporal: valid_from inclusive, valid_to exclusive). */
export function validAt(fact: GraphFact, t: number): boolean {
  const from = Date.parse(fact.valid_from);
  const to = fact.valid_to ? Date.parse(fact.valid_to) : Infinity;
  return from <= t && t < to;
}

/** Midnight UTC of the day `t` falls on: the slider moves in whole days. */
export function dayOf(t: number): number {
  return Math.floor(t / DAY) * DAY;
}

/** "As of a day" means as of the end of that day: a fact that starts at 07:30 counts. */
export function endOfDay(day: number): number {
  return dayOf(day) + DAY - 1;
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
  staff: 0,
  product: 1,
  ingredient: 2,
  supplier: 3,
  portal: 3,
};

/**
 * Deterministic layout for a small graph: one band per role (the café, what it sells,
 * what that is made of, who supplies it). Wide containers lay the bands out as columns,
 * narrow ones (phones) as rows. Percent coordinates.
 */
export function layout(nodes: GraphNode[], narrow = false): Map<string, { x: number; y: number }> {
  const bands = new Map<number, GraphNode[]>();
  for (const n of nodes) {
    const c = TYPE_COLUMN[n.type] ?? 1;
    bands.set(c, [...(bands.get(c) ?? []), n]);
  }
  const used = [...bands.keys()].sort((a, b) => a - b);
  const pos = new Map<string, { x: number; y: number }>();
  used.forEach((c, bi) => {
    const band = bands.get(c) ?? [];
    const along = used.length === 1 ? 50 : 12 + (bi * 76) / (used.length - 1);
    band.forEach((n, i) => {
      if (narrow) {
        // Labels sit right of their dot here, so dots keep to the left of each half.
        const x = band.length === 1 ? 30 : 6 + (i * 48) / (band.length - 1);
        pos.set(n.id, { x, y: 6 + (bi * 74) / Math.max(1, used.length - 1) });
      } else {
        const y = band.length === 1 ? 46 : 22 + (i * 52) / (band.length - 1);
        pos.set(n.id, { x: along, y });
      }
    });
  });
  return pos;
}
