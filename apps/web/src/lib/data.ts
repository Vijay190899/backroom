"use client";

import { useQuery } from "@tanstack/react-query";
import type { z } from "zod";

import { API_URL } from "@/lib/api";

/** Where a page's data came from: the API, or the committed sample (badged on screen). */
export type Source = "live" | "sample";
export type Loaded<T> = { data: T; source: Source };

/**
 * Fetch an API route and validate it; when the route isn't there yet (the PC wires
 * them in H4) fall back to the committed fixture, parsed by the same schema. PRD §7:
 * the screen says "Sample" whenever it isn't live. Returned as query options, so a page
 * can use it and the app can prefetch it (for page changes that arrive already filled).
 */
export function liveOrSample<T>(
  key: string,
  path: string,
  schema: () => Promise<z.ZodType<T>>,
  sample: () => Promise<{ default: unknown }>,
) {
  return {
    queryKey: [key],
    queryFn: async ({ signal }: { signal: AbortSignal }): Promise<Loaded<T>> => {
      const parser = await schema();
      let res: Response | null = null;
      try {
        res = await fetch(`${API_URL}${path}`, { signal, cache: "no-store" });
      } catch (error) {
        if (signal.aborted) throw error;
      }
      // A live answer that breaks the contract is an error to show, not a cue to swap in
      // the sample: only a missing route or an unreachable API falls back.
      if (res?.ok) return { data: parser.parse(await res.json()), source: "live" };
      return { data: parser.parse((await sample()).default), source: "sample" };
    },
  };
}

export function useLiveOrSample<T>(options: ReturnType<typeof liveOrSample<T>>) {
  return useQuery(options);
}
