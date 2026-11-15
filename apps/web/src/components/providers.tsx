"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import dynamic from "next/dynamic";
import { useEffect, useState, type ReactNode } from "react";

import { memoryQuery, skillsQuery, skillVersionsQuery } from "@/lib/queries";

import { useMotionLevel } from "@/lib/use-motion-level";

// The ambient scene arrives after first paint; nothing waits on it.
const AmbientField = dynamic(() => import("@/components/fx/ambient-field").then((m) => m.AmbientField), {
  ssr: false,
});

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 10_000, retry: 1, refetchOnWindowFocus: false } },
      }),
  );
  const level = useMotionLevel();
  // The scene starts once the page has loaded and gone idle: its GPU frames never
  // compete with the first paint (it fades in, so nothing visibly pops).
  const [scene, setScene] = useState(false);
  useEffect(() => {
    const start = () => {
      if (typeof requestIdleCallback === "function") requestIdleCallback(() => setScene(true), { timeout: 1500 });
      else setTimeout(() => setScene(true), 300);
    };
    if (document.readyState === "complete") start();
    else addEventListener("load", start, { once: true });
    return () => removeEventListener("load", start);
  }, []);

  // Once the first page has settled, load every other page's data, so a page change lands on
  // a filled page instead of a skeleton that pops.
  useEffect(() => {
    const warm = async () => {
      const skills = await queryClient.fetchQuery(skillsQuery()).catch(() => null);
      await Promise.all([
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
        {scene ? <AmbientField /> : null}
        {children}
      </MotionConfig>
    </QueryClientProvider>
  );
}
