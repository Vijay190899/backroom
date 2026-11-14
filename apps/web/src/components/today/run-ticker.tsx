"use client";

import NumberFlow from "@number-flow/react";
import { RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import type { RunEvent } from "@/lib/contracts";
import { enterDelay, prefersReducedMotion } from "@/lib/motion";
import { describeChange, playbackDelay } from "@/lib/runs";
import { cn } from "@/lib/utils";

type Mode = "explore" | "replay" | "heal";

const MODE_STYLE: Record<Mode, string> = {
  replay: "border-replay/50 text-replay",
  heal: "border-heal/50 text-heal",
  explore: "border-explore/50 text-explore",
};

/** Everything the strip shows, derived from the events played so far. */
function view(events: RunEvent[], upTo: number) {
  const played = events.slice(0, upTo);
  const totalSteps = events.filter((e) => e.type === "step.started").length;
  let mode: Mode = "replay";
  let step = 0;
  let intent = "";
  let heal: string | null = null;
  let heals = 0;
  let usd = 0;
  let finished: Extract<RunEvent, { type: "run.finished" }> | null = null;
  for (const e of played) {
    if (e.type === "run.started") mode = e.mode;
    if (e.type === "mode.changed") mode = e.to_mode;
    if (e.type === "step.started") {
      step += 1;
      intent = e.intent;
      heal = null;
    }
    if (e.type === "heal.started") heal = `Couldn’t find it: ${e.failure.replace("locator not found: ", "")}`;
    if (e.type === "heal.succeeded") {
      heals += 1;
      heal = `Healed to v${e.new_version}: ${e.changes.map(describeChange).join(", ")}`;
    }
    if (e.type === "cost.tick") usd = e.totals.usd;
    if (e.type === "run.finished") finished = e;
  }
  return { mode, step, totalSteps, intent, heal, heals, usd, finished };
}

/**
 * The approved card's run, played back from its recorded events: the step the agent is
 * on, REPLAY switching to HEAL when a button moved, the cost ticking, then the result.
 * Every word and number is an event field; nothing is generated here.
 */
export function RunTicker({ events, label }: { events: RunEvent[]; label: string }) {
  const [upTo, setUpTo] = useState(() => (prefersReducedMotion() ? events.length : 1));
  const [round, setRound] = useState(0);
  const strip = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (upTo >= events.length) return;
    const timer = setTimeout(() => setUpTo((n) => n + 1), playbackDelay(events[upTo - 1]));
    return () => clearTimeout(timer);
  }, [upTo, events, round]);

  const v = useMemo(() => view(events, upTo), [events, upTo]);
  const progress = v.finished ? 1 : v.totalSteps ? v.step / v.totalSteps : 0;
  // One live region that stays mounted, so screen readers hear each heal and the result
  // (not every step).
  const announce = v.finished ? v.finished.summary : v.heal?.startsWith("Healed") ? v.heal : "";

  return (
    <div ref={strip} tabIndex={-1} className="mt-5 border-t border-ink pt-3 outline-none">
      <p role="status" className="sr-only">
        {announce}
      </p>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        <span
          key={v.mode}
          className={cn(
            "stamp-in kicker inline-flex h-6 items-center border px-1.5 text-[0.625rem]",
            MODE_STYLE[v.mode],
          )}
        >
          {v.mode}
        </span>
        <span className="text-muted-foreground">
          {label} · step {v.step} of {v.totalSteps}
        </span>
        <span className="ml-auto font-mono text-xs text-muted-foreground tabular">
          <span className="sr-only">Model cost so far: </span>
          <NumberFlow
            value={v.usd}
            locales="en-US"
            format={{ style: "currency", currency: "USD", minimumFractionDigits: 4, maximumFractionDigits: 4 }}
          />
        </span>
      </div>

      <div aria-hidden className="mt-2 h-0.5 overflow-hidden bg-line">
        <div
          className={cn(
            "h-full origin-left transition-transform duration-300 ease-[var(--t-ease-out)]",
            v.mode === "heal" ? "bg-heal" : "bg-press",
          )}
          style={{ transform: `scaleX(${progress})` }}
        />
      </div>

      {v.finished ? (
        <div className="mt-3">
          <p className="enter font-serif text-[1.0625rem] leading-snug text-ink">{v.finished.summary}</p>
          <p className="enter mt-1 flex flex-wrap items-center gap-x-3 text-sm text-muted-foreground" style={enterDelay(80)}>
            <span>
              {v.finished.totals.steps} steps · {v.heals} {v.heals === 1 ? "heal" : "heals"} ·{" "}
              {v.finished.totals.llm_calls} model calls · skill now v{v.finished.skill_version}
            </span>
            {/* Replaying is motion; under reduced motion the result simply stays. */}
            <button
              type="button"
              onClick={() => {
                setUpTo(1);
                setRound((r) => r + 1);
                strip.current?.focus(); // the button unmounts while the run plays
              }}
              className="link-draw inline-flex min-h-11 cursor-pointer items-center gap-1 text-press-ink motion-reduce:hidden sm:min-h-0"
            >
              <RotateCcw aria-hidden className="size-3.5" />
              Watch again
            </button>
          </p>
        </div>
      ) : (
        <div className="mt-3 min-h-[3.25rem]" aria-hidden>
          <p key={`s${v.step}`} className="enter font-serif text-[1.0625rem] leading-snug text-ink">
            {v.intent}
          </p>
          {v.heal ? (
            <p key={v.heal} className="enter mt-1 font-mono text-xs text-heal">
              {v.heal}
            </p>
          ) : null}
        </div>
      )}
    </div>
  );
}
