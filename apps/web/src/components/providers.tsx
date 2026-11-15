"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import dynamic from "next/dynamic";
import { useState, type ReactNode } from "react";

import { useMotionLevel } from "@/lib/use-motion-level";

// The ambient light and the agent dock arrive after first paint; nothing waits on them.
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
  return (
    <QueryClientProvider client={queryClient}>
      {/* Calm (system setting or the header toggle) turns every Motion animation off. */}
      <MotionConfig reducedMotion={level === "calm" ? "always" : "never"}>
        <AmbientField />
        {children}
      </MotionConfig>
    </QueryClientProvider>
  );
}
