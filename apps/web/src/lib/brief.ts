"use client";

import { useQuery } from "@tanstack/react-query";

import { API_URL } from "@/lib/api";
import type { ActionCard, Brief } from "@/lib/contracts";
import type { Source } from "@/lib/data";

/**
 * Where a brief came from. "sample" is the committed fixture, shown with a visible
 * badge whenever the API has no brief to give (PRD §7: never present anything as live
 * when it isn't).
 */
export type LoadedBrief = { brief: Brief; source: Source };

// The schemas (and zod) load alongside the first request instead of in the startup
// bundle; every response and fixture is still parsed before use.
const contracts = () => import("@/lib/contracts");

async function fetchBrief(signal?: AbortSignal): Promise<LoadedBrief> {
  // The fixture downloads alongside the API call (not after it fails), so the sample
  // fallback costs no extra round trip before the first cards paint.
  const fixture = import("@/fixtures/brief.json");
  const schemas = contracts();
  try {
    const [res, { briefSchema }] = await Promise.all([
      fetch(`${API_URL}/brief/today`, { signal, cache: "no-store" }),
      schemas,
    ]);
    if (res.ok) return { brief: briefSchema.parse(await res.json()), source: "live" };
  } catch (error) {
    if (signal?.aborted) throw error;
  }
  const [{ briefSchema }, sample] = await Promise.all([schemas, fixture]);
  return { brief: briefSchema.parse(sample.default), source: "sample" };
}

export function useBrief() {
  return useQuery({ queryKey: ["brief"], queryFn: ({ signal }) => fetchBrief(signal) });
}

/** One key per proposal, so a double tap or a retry never orders twice. */
export function idempotencyKey(brief: Brief, card: ActionCard): string {
  return `${brief.id}:${card.id}`;
}

export async function approve(brief: Brief, card: ActionCard) {
  // Schema first: a failed chunk load must not report "couldn't start" after the POST.
  const { approveResponseSchema } = await contracts();
  const res = await fetch(`${API_URL}/actions/${encodeURIComponent(card.id)}/approve`, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey(brief, card) },
  });
  if (!res.ok) throw new Error(`approve failed: ${res.status}`);
  return approveResponseSchema.parse(await res.json());
}

export async function reject(card: ActionCard, reason: string) {
  const { rejectResponseSchema } = await contracts();
  const res = await fetch(`${API_URL}/actions/${encodeURIComponent(card.id)}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error(`reject failed: ${res.status}`);
  return rejectResponseSchema.parse(await res.json());
}

/**
 * Offline stand-in for the reject -> learn -> regenerate loop (PRD F4): rejecting the
 * margin card with a reason that names a cap swaps in the regenerated sample brief.
 * The real loop runs in the API (brief pipeline + preference extractor).
 */
export async function sampleAfterReject(card: ActionCard, reason: string): Promise<Brief | null> {
  const namesACap = /\d/.test(reason);
  if (card.kind !== "margin_erosion" || !namesACap) return null;
  const [{ briefSchema }, fixture] = await Promise.all([
    contracts(),
    import("@/fixtures/brief-after-reject.json"),
  ]);
  return briefSchema.parse(fixture.default);
}
