"use client";

import { Sparkles, Wind } from "lucide-react";

import { setMotionLevel } from "@/lib/motion-pref";
import { useMotionLevel } from "@/lib/use-motion-level";
import { cn } from "@/lib/utils";

/** Turns the ambient light, particles and physics off (or back on) for this reader. */
export function MotionToggle({ className }: { className?: string }) {
  const level = useMotionLevel();
  const full = level === "full";
  return (
    <button
      type="button"
      aria-pressed={full}
      aria-label={full ? "Calm the motion" : "Turn the motion on"}
      title={full ? "Calm the motion" : "Turn the motion on"}
      onClick={() => setMotionLevel(full ? "calm" : "full")}
      className={cn(
        "inline-flex size-11 cursor-pointer items-center justify-center rounded-xl text-muted-foreground transition-colors duration-150 hover:bg-glass-strong hover:text-ink",
        className,
      )}
    >
      {full ? <Sparkles aria-hidden className="size-[18px]" strokeWidth={1.75} /> : <Wind aria-hidden className="size-[18px]" strokeWidth={1.75} />}
    </button>
  );
}
