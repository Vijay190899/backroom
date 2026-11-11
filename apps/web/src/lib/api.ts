import { z } from "zod";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const healthSchema = z.object({
  status: z.enum(["ok", "degraded"]),
  checks: z.object({
    postgres: z.enum(["ok", "down"]),
    portals: z.enum(["ok", "down"]),
    llm: z.object({ provider: z.string(), configured: z.boolean() }),
  }),
  demo_mode: z.enum(["live", "replay"]),
});
export type Health = z.infer<typeof healthSchema>;

/** The API answers 503 with the same body when a dependency is down. */
export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  const res = await fetch(`${API_URL}/health`, { signal, cache: "no-store" });
  return healthSchema.parse(await res.json());
}
