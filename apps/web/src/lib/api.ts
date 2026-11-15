import type { Health } from "@/lib/schemas/health";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * The API answers 503 with the same body when a dependency is down. The schema (and
 * zod) load with the request rather than in the startup bundle.
 */
export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  const [res, { healthSchema }] = await Promise.all([
    fetch(`${API_URL}/health`, { signal, cache: "no-store" }),
    import("@/lib/schemas/health"),
  ]);
  return healthSchema.parse(await res.json());
}
