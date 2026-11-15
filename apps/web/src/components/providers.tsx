"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";

import { briefQuery } from "@/lib/brief";
import { memoryQuery, skillsQuery, skillVersionsQuery } from "@/lib/queries";

import { useMotionLevel } from "@/lib/use-motion-level";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 10_000, retry: 1, refetchOnWindowFocus: false } },
      }),
  );
  const level = useMotionLevel();
  // Once the first page has settled, load every other page's data, so a page change lands on
  // a filled page instead of a skeleton that pops.
  useEffect(() => {
    const warm = async () => {
      const skills = await queryClient.fetchQuery(skillsQuery()).catch(() => null);
      await Promise.all([
        queryClient.prefetchQuery(briefQuery()),
        queryClient.prefetchQuery(memoryQuery()),
        ...(skills?.data ?? []).map((s) => queryClient.prefetchQuery(skillVersionsQuery(s.id))),
      ]);
    };
    // A few seconds after the first page has painted and settled, so this never competes
    // with it; then on an idle moment (Safari has no requestIdleCallback: run directly).
    let idle = 0;
    const timer = setTimeout(() => {
      if (typeof requestIdleCallback === "function") idle = requestIdleCallback(() => void warm(), { timeout: 2000 });
      else void warm();
    }, 3500);
    return () => {
      clearTimeout(timer);
      if (idle) cancelIdleCallback(idle);
    };
  }, [queryClient]);
  return (
    <QueryClientProvider client={queryClient}>
      {/* Calm (the device's reduced-motion setting) turns every Motion animation off. */}
      <MotionConfig reducedMotion={level === "calm" ? "always" : "never"}>
        {children}
      </MotionConfig>
    </QueryClientProvider>
  );
}
