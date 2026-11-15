import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

import { z } from "zod";

/**
 * The committed benchmark results (bench/results/<id>.json, written by `pnpm bench`),
 * read at build time. A missing file, or one from a `--fake` run, reads as "not run yet":
 * the page never shows a number that wasn't measured.
 */
const header = z.object({ ran_at: z.string(), git_sha: z.string(), n: z.number(), fake: z.boolean() });
const rate = z.number().nullable();

const schemas = {
  B1: header.extend({
    headline: z.object({ cold_success_at_seed0: rate, warm_success_across_seeds: rate }),
  }),
  B2: header.extend({
    headline: z.object({ warm_p50_ms: z.number().nullable(), warm_usd: z.number(), warm_success: rate.optional() }),
  }),
  B3: header.extend({
    arms: z.record(z.string(), z.object({ accuracy: rate })),
    headline: z.object({ pack_tokens_vs_dump: z.number().nullable() }),
  }),
  B5: header.extend({
    verification: z.object({ verified: rate, numbers_checked: z.number() }),
  }),
};
export type BenchId = keyof typeof schemas;

const DIR = path.join(process.cwd(), "..", "..", "bench", "results");

export function benchResult<K extends BenchId>(id: K): z.infer<(typeof schemas)[K]> | null {
  const file = path.join(DIR, `${id.toLowerCase()}.json`);
  if (!existsSync(file)) return null;
  const parsed = schemas[id].safeParse(JSON.parse(readFileSync(file, "utf8")));
  if (!parsed.success || parsed.data.fake) return null;
  return parsed.data as z.infer<(typeof schemas)[K]>;
}

const pct = (v: number | null | undefined) =>
  v === null || v === undefined ? "–" : v < 0.1 && v > 0 ? `${(v * 100).toFixed(1)}%` : `${Math.round(v * 100)}%`;

/** The headline a benchmark row shows, in words built only from the result file. */
export function headline(id: string): { value: string; detail: string; meta: string } | null {
  const meta = (r: z.infer<typeof header>) =>
    `n = ${r.n} · ${new Date(r.ran_at).toLocaleDateString("en-GB", { day: "numeric", month: "short" })} · ${r.git_sha}`;
  if (id === "B1") {
    const r = benchResult("B1");
    return r && { value: pct(r.headline.cold_success_at_seed0), detail: `cold at seed 0 · ${pct(r.headline.warm_success_across_seeds)} warm across seeds`, meta: meta(r) };
  }
  if (id === "B2") {
    const r = benchResult("B2");
    const p50 = r?.headline.warm_p50_ms;
    return r && { value: p50 === null || p50 === undefined ? "–" : `${(p50 / 1000).toFixed(1)} s`, detail: `warm p50 · $${r.headline.warm_usd.toFixed(4)} warm · ${pct(r.headline.warm_success)} succeeded`, meta: meta(r) };
  }
  if (id === "B3") {
    const r = benchResult("B3");
    const ratio = r?.headline.pack_tokens_vs_dump;
    return r && { value: pct(r.arms.context_pack?.accuracy), detail: `with the context pack · ${ratio === null || ratio === undefined ? "–" : pct(ratio)} of the raw dump's tokens · ${pct(r.arms.raw_dump?.accuracy)} with the dump`, meta: meta(r) };
  }
  if (id === "B5") {
    const r = benchResult("B5");
    return r && { value: pct(r.verification.verified), detail: `of ${r.verification.numbers_checked} displayed numbers verified`, meta: meta(r) };
  }
  return null;
}
