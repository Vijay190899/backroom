"use client";

import { useQuery } from "@tanstack/react-query";

import { API_URL } from "@/lib/api";
import {
  approveResponseSchema,
  briefSchema,
  rejectResponseSchema,
  type ActionCard,
  type Brief,
} from "@/lib/contracts";
import afterRejectFixture from "@/fixtures/brief-after-reject.json";
import briefFixture from "@/fixtures/brief.json";

/**
 * Where a brief came from. "sample" is the committed fixture, shown with a visible
 * badge whenever the API has no brief to give (PRD §7: never present anything as live
 * when it isn't).
 */
export type BriefSource = "live" | "sample";
export type LoadedBrief = { brief: Brief; source: BriefSource };

export const SAMPLE_BRIEF: Brief = briefSchema.parse(briefFixture);
export const SAMPLE_BRIEF_AFTER_REJECT: Brief = briefSchema.parse(afterRejectFixture);

async function fetchBrief(signal?: AbortSignal): Promise<LoadedBrief> {
  try {
    const res = await fetch(`${API_URL}/brief/today`, { signal, cache: "no-store" });
    if (res.ok) return { brief: briefSchema.parse(await res.json()), source: "live" };
  } catch (error) {
    if (signal?.aborted) throw error;
  }
  return { brief: SAMPLE_BRIEF, source: "sample" };
}

export function useBrief() {
  return useQuery({ queryKey: ["brief"], queryFn: ({ signal }) => fetchBrief(signal) });
}

/** One key per proposal, so a double tap or a retry never orders twice. */
export function idempotencyKey(brief: Brief, card: ActionCard): string {
  return `${brief.id}:${card.id}`;
}

export async function approve(brief: Brief, card: ActionCard) {
  const res = await fetch(`${API_URL}/actions/${encodeURIComponent(card.id)}/approve`, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey(brief, card) },
  });
  if (!res.ok) throw new Error(`approve failed: ${res.status}`);
  return approveResponseSchema.parse(await res.json());
}

export async function reject(card: ActionCard, reason: string) {
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
export function sampleAfterReject(card: ActionCard, reason: string): Brief | null {
  const namesACap = /\d/.test(reason);
  return card.kind === "margin_erosion" && namesACap ? SAMPLE_BRIEF_AFTER_REJECT : null;
}
