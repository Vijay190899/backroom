"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "@/lib/api";
import { cn } from "@/lib/utils";

type Tone = "pos" | "warn" | "neg" | "idle";
type Status = { label: string; tone: Tone };

const TONE_DOT: Record<Tone, string> = {
  pos: "bg-pos",
  warn: "bg-explore",
  neg: "bg-neg",
  idle: "bg-muted-foreground/50",
};

export function ApiStatus({ className }: { className?: string }) {
  const { data, isPending, isError } = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchInterval: 15_000,
  });

  let status: Status;
  if (isPending) status = { label: "Connecting", tone: "idle" };
  else if (isError || !data) status = { label: "Offline", tone: "neg" };
  else if (data.status !== "ok") status = { label: "Degraded", tone: "warn" };
  else if (data.demo_mode === "replay") status = { label: "Replay", tone: "warn" };
  else status = { label: "Live", tone: "pos" };

  return (
    <span
      role="status"
      aria-label={`Backroom API: ${status.label}`}
      className={cn(
        "inline-flex h-7 items-center gap-2 rounded-full border border-line bg-surface px-2.5 text-xs text-muted-foreground",
        className,
      )}
    >
      <span aria-hidden className={cn("size-1.5 rounded-full", TONE_DOT[status.tone])} />
      {status.label}
    </span>
  );
}
