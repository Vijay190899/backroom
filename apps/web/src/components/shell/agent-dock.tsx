"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { Bot, ChevronDown } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { RunTicker, useRunPlayback } from "@/components/today/run-ticker";
import { setDockAnchor, useAgent, type AgentRun } from "@/lib/agent-runs";
import { serve, startWork } from "@/lib/scene";
import { cn } from "@/lib/utils";

const SPRING = { type: "spring", stiffness: 380, damping: 32 } as const;

function Ring({ progress, mode, idle }: { progress: number; mode: string; idle: boolean }) {
  const c = 2 * Math.PI * 13;
  return (
    <svg aria-hidden viewBox="0 0 32 32" className="size-8 -rotate-90">
      <circle cx="16" cy="16" r="13" className="fill-none stroke-glass-line" strokeWidth="3" />
      <motion.circle
        cx="16"
        cy="16"
        r="13"
        className={cn("fill-none", mode === "heal" ? "stroke-heal" : "stroke-press")}
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray={c}
        animate={{ strokeDashoffset: c * (1 - (idle ? 0 : Math.max(0.04, progress))) }}
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
      />
    </svg>
  );
}

type PlayableRun = AgentRun & { events: NonNullable<AgentRun["events"]> };

/** One playback drives both the collapsed line (ring, current step) and the open panel. */
function PlayingRun({ run, open, onToggle }: { run: PlayableRun; open: boolean; onToggle: () => void }) {
  const playback = useRunPlayback(run.events);
  const { v, progress } = playback;
  // The café scene works while the agent works, and serves a cup when the run finishes.
  const finished = Boolean(v.finished);
  const wasFinished = useRef(finished);
  useEffect(() => (finished ? undefined : startWork()), [finished]);
  useEffect(() => {
    if (finished && !wasFinished.current) serve();
    wasFinished.current = finished;
  }, [finished]);
  return (
    <>
      <button
        type="button"
        ref={setDockAnchor}
        aria-expanded={open}
        onClick={onToggle}
        className="flex min-h-11 w-full cursor-pointer items-center justify-between gap-3"
      >
        <span className="flex min-w-0 items-center gap-3">
          <Ring progress={progress} mode={v.mode} idle={false} />
          <span className="min-w-0 text-left">
            <span className="block text-xs text-muted-foreground">
              Sample run · {v.finished ? "done" : v.mode} · {run.title}
            </span>
            <span className="block truncate text-sm font-medium text-ink">
              {v.finished ? v.finished.summary : v.intent || "Starting…"}
            </span>
          </span>
        </span>
        <ChevronDown aria-hidden className={cn("size-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>
      <p role="status" className="sr-only">
        {v.finished ? `Sample run finished: ${v.finished.summary}` : ""}
      </p>
      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            key="panel"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={SPRING}
            className="overflow-hidden"
          >
            <div className="mt-3 border-t border-glass-line pt-3">
              <RunTicker playback={playback} label={run.portal ? `Sample run on ${run.portal}` : "Sample run"} />
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}

/**
 * Floating "Agent" dock: where approved cards go. Idle until a run starts; a ring fills
 * as the run plays, turning violet while it heals; pulses when particles land in it.
 */
export function AgentDock() {
  const { runs, pulse } = useAgent();
  const [open, setOpen] = useState(false);
  const controls = useAnimationControls();
  const latest = runs[0];
  const pathname = usePathname();

  useEffect(() => {
    if (pulse) void controls.start({ scale: [1, 1.08, 1], transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] } });
  }, [pulse, controls]);

  // Idle, it only shows on Today (where cards are sent from); with a run it follows you.
  if (!latest && pathname !== "/") return null;

  return (
    <motion.section
      aria-label="Agent"
      layout
      transition={SPRING}
      animate={controls}
      className={cn(
        "glass fixed right-3 bottom-[5.75rem] left-3 z-40 rounded-2xl glass-solid px-3 py-2.5 sm:left-auto lg:right-6 lg:bottom-6",
        open ? "sm:w-[26rem]" : "sm:w-[22rem]",
      )}
    >
      {latest?.events ? (
        <PlayingRun key={latest.id} run={{ ...latest, events: latest.events }} open={open} onToggle={() => setOpen((o) => !o)} />
      ) : (
        <div ref={setDockAnchor} className="flex min-w-0 items-center gap-3">
          <span className="grid size-8 place-items-center rounded-full border border-glass-line">
            <Bot aria-hidden className="size-4 text-muted-foreground" />
          </span>
          <span className="min-w-0 text-left">
            <span className="block text-xs text-muted-foreground">Agent</span>
            <span role="status" className="block truncate text-sm font-medium text-ink">
              {latest ? latest.note : "Idle · approve a card to send it here"}
            </span>
          </span>
        </div>
      )}
    </motion.section>
  );
}
