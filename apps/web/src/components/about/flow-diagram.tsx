"use client";

import { Pause, Play } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/utils";

const STEPS = [
  { name: "Your data", who: "till, invoices, forecast" },
  { name: "Detectors", who: "code computes every figure" },
  { name: "Planner", who: "a model writes the words" },
  { name: "Number guard", who: "code checks each number" },
  { name: "You approve", who: "nothing acts before this" },
  { name: "Browser agent", who: "replays a learned skill" },
];

/**
 * The loop, drawn as a press line with one pulse travelling it. The pulse waits at
 * "You approve" (the loop never acts on its own), then carries on to the portal. It loops,
 * so it has a pause button; under reduced motion it rests on the approval step instead.
 */
export function FlowDiagram() {
  const [paused, setPaused] = useState(false);
  return (
    <figure data-paused={paused || undefined} className="flow relative">
      <div className="flow-track relative">
        <span aria-hidden className="flow-line absolute bg-ink" />
        <span aria-hidden className="flow-pulse absolute size-3 bg-press" />
        <ol className="grid h-full sm:grid-cols-6 sm:gap-x-2">
        {STEPS.map((s, i) => (
          <li key={s.name} className="relative flex h-18 items-start gap-4 sm:h-auto sm:flex-col sm:items-center sm:gap-0 sm:text-center">
            <span
              aria-hidden
              className={cn(
                "relative z-10 mt-1 size-3 shrink-0 border border-ink sm:mt-0",
                i === 4 ? "bg-press" : "bg-background",
              )}
            />
            <span className="sm:mt-4">
              <span className="block font-display text-lg leading-tight text-ink">{s.name}</span>
              <span className="mt-0.5 block text-sm text-muted-foreground">{s.who}</span>
            </span>
          </li>
        ))}
        </ol>
      </div>
      <button
        type="button"
        onClick={() => setPaused((p) => !p)}
        aria-label={paused ? "Play the flow" : "Pause the flow"}
        className="absolute -top-12 right-0 inline-flex size-11 cursor-pointer calm-hidden items-center justify-center rounded-full border border-ink/25 text-ink transition-colors duration-150 hover:border-ink/60"
      >
        {paused ? <Play aria-hidden className="size-4" /> : <Pause aria-hidden className="size-4" />}
      </button>
    </figure>
  );
}
