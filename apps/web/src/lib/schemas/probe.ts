import { z } from "zod";

/** `bench/results/provider_probe.json`, written by `pnpm probe:llm` (bench package). */
export const probeSchema = z.object({
  provider: z.string(),
  model: z.string(),
  wire_model: z.string(),
  sdk_version: z.string(),
  ran_at: z.string(),
  git_sha: z.string(),
  total_usd: z.number(),
  checks: z.record(
    z.string(),
    z.object({ ok: z.boolean(), detail: z.string(), ms: z.number(), usd: z.number() }),
  ),
});
