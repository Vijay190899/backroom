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
const ci = z.tuple([z.number(), z.number()]).nullable().optional();

const schemas = {
  B1: header.extend({
    headline: z.object({
      cold_success_at_seed0: rate,
      cold_success_at_seed0_ci95: ci,
      warm_success_across_seeds: rate,
      warm_success_across_seeds_ci95: ci,
      warm_success_on_redesigned_seeds: rate.optional(),
    }),
  }),
  B2: header.extend({
    headline: z.object({ warm_p50_ms: z.number().nullable(), warm_usd: z.number(), warm_success: rate.optional() }),
  }),
  B3: header.extend({
    arms: z.record(
      z.string(),
      z.object({ accuracy: rate, accuracy_by_scope: z.record(z.string(), rate).optional() }),
    ),
    headline: z.object({
      pack_tokens_vs_dump: z.number().nullable(),
      pack_accuracy_memory_scope: rate.optional(),
      scopes: z.object({ memory: z.number(), analytics: z.number() }).optional(),
    }),
  }),
  B5: header.extend({
    verification: z.object({ verified: rate, numbers_checked: z.number() }),
    guard: z
      .object({ cards: z.number(), model_copy_passed_first_try: rate, template_fallbacks: z.number() })
      .optional(),
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

/** "95% CI 64–96%", or nothing when the file has no interval. */
const interval = (c: [number, number] | null | undefined) =>
  c ? ` (95% CI ${Math.round(c[0] * 100)}–${Math.round(c[1] * 100)}%)` : "";

const pct = (v: number | null | undefined) =>
  v === null || v === undefined ? "–" : v < 0.1 && v > 0 ? `${(v * 100).toFixed(1)}%` : `${Math.round(v * 100)}%`;

/** The headline a benchmark row shows, in words built only from the result file. */
export function headline(id: string): { value: string; detail: string; meta: string } | null {
  const meta = (r: z.infer<typeof header>) =>
    `n = ${r.n} · ${new Date(r.ran_at).toLocaleDateString("en-GB", { day: "numeric", month: "short" })} · ${r.git_sha}`;
  if (id === "B1") {
    const r = benchResult("B1");
    if (!r) return null;
    const h = r.headline;
    const healed = h.warm_success_on_redesigned_seeds;
    return {
      value: pct(h.cold_success_at_seed0),
      detail:
        `cold at seed 0${interval(h.cold_success_at_seed0_ci95)} · ${pct(h.warm_success_across_seeds)} warm across seeds${interval(h.warm_success_across_seeds_ci95)}` +
        (healed === undefined ? "" : ` · ${pct(healed)} on redesigned seeds (healed)`),
      meta: meta(r),
    };
  }
  if (id === "B2") {
    const r = benchResult("B2");
    const p50 = r?.headline.warm_p50_ms;
    return r && { value: p50 === null || p50 === undefined ? "–" : `${(p50 / 1000).toFixed(1)} s`, detail: `warm p50 · $${r.headline.warm_usd.toFixed(4)} warm · ${pct(r.headline.warm_success)} succeeded`, meta: meta(r) };
  }
  if (id === "B3") {
    const r = benchResult("B3");
    if (!r) return null;
    const ratio = r.headline.pack_tokens_vs_dump;
    const scopes = r.headline.scopes;
    const inScope = r.headline.pack_accuracy_memory_scope;
    return {
      value: pct(r.arms.context_pack?.accuracy),
      detail:
        `with the context pack, at ${ratio === null ? "–" : pct(ratio)} of the raw dump's tokens · ${pct(r.arms.raw_dump?.accuracy)} with the dump` +
        (scopes && inScope !== undefined
          ? ` · ${pct(inScope)} on the ${scopes.memory} questions memory is built for (the other ${scopes.analytics} are sales analytics, which the agents answer with SQL)`
          : ""),
      meta: meta(r),
    };
  }
  if (id === "B5") {
    const r = benchResult("B5");
    if (!r) return null;
    const g = r.guard;
    const firstTry = g && g.model_copy_passed_first_try !== null ? Math.round(g.model_copy_passed_first_try * g.cards) : null;
    return {
      value: pct(r.verification.verified),
      detail:
        `of ${r.verification.numbers_checked} displayed numbers verified` +
        (g && firstTry !== null
          ? ` · the model's copy passed the guard first time on ${firstTry} of ${g.cards} cards, ${g.template_fallbacks} fell back to template copy`
          : ""),
      meta: meta(r),
    };
  }
  return null;
}
