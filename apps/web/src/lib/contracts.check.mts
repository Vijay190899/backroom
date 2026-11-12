/**
 * Contract check, web side: every shared fixture must parse with the zod mirror.
 * The Python side parses the same files (services/api/tests/test_contracts.py).
 * Run: `pnpm -C apps/web contracts` (part of `pnpm check`).
 */
import { readFileSync } from "node:fs";
import { z } from "zod";

import {
  briefSchema,
  memoryGraphSchema,
  runEventSchema,
  skillSummarySchema,
  skillVersionsSchema,
} from "./contracts.ts";

const fixtures: Record<string, z.ZodType> = {
  "brief.json": briefSchema,
  "brief-after-reject.json": briefSchema,
  "memory-graph.json": memoryGraphSchema,
  "run-events.json": z.array(runEventSchema),
  "skill-versions.json": skillVersionsSchema,
  "skills.json": z.array(skillSummarySchema),
};

function load(name: string): unknown {
  return JSON.parse(readFileSync(new URL(`../fixtures/${name}`, import.meta.url), "utf8"));
}

let failures = 0;
for (const [name, schema] of Object.entries(fixtures)) {
  const result = schema.safeParse(load(name));
  if (result.success) {
    console.log(`ok    ${name}`);
  } else {
    failures += 1;
    console.error(`FAIL  ${name}\n${z.prettifyError(result.error)}`);
  }
}

// The schemas must reject drift, not only accept the fixtures.
const brief = load("brief.json") as { cards: Record<string, unknown>[] };
const negatives: [string, z.ZodType, unknown][] = [
  ["unknown field", briefSchema, { ...brief, extra: 1 }],
  ["4 cards", briefSchema, { ...brief, cards: [...brief.cards, brief.cards[0]] }],
  ["unknown event type", runEventSchema, { seq: 1, run_id: "r", ts: "2026-11-13T07:30:00Z", type: "step.skipped" }],
];
for (const [label, schema, value] of negatives) {
  if (schema.safeParse(value).success) {
    failures += 1;
    console.error(`FAIL  accepted invalid input: ${label}`);
  } else {
    console.log(`ok    rejects ${label}`);
  }
}

if (failures > 0) process.exit(1);
