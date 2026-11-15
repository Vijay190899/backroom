"use client";

import { Check, LoaderCircle, Sparkles, X } from "lucide-react";
import { useEffect, useRef } from "react";

import { describeChange, type HealRung, type StepView } from "@/lib/run-view";
import { cn } from "@/lib/utils";

const RUNGS: HealRung["rung"][] = ["fallback", "healer", "escalation", "human"];
const RUNG_LABEL: Record<HealRung["rung"], string> = {
  fallback: "Fallback locators",
  healer: "Healer model",
  escalation: "Escalation model",
  human: "You",
};

const usd = (n: number) => `$${n.toFixed(4)}`;
const seconds = (ms: number) => `${(ms / 1000).toFixed(ms < 10_000 ? 2 : 1)} s`;

/** What the step did, in words: "click ‘Sign in’", "fill ‘Quantity’ with 28", "open /grainline/login". */
function actionLine(s: StepView): string {
  const name = s.heal?.target?.name ?? s.target?.name;
  if (s.action === "goto") return `open ${s.value ?? ""}`;
  if (s.action === "fill_secret") return `fill ‘${name}’ from the vault`;
  if (s.action === "totp") return `enter a fresh code in ‘${name}’`;
  if (s.action === "fill") return `fill ‘${name}’ with ${s.value ?? ""}`;
  return name ? `${s.action} ‘${name}’` : s.action;
}

function StateMark({ state }: { state: StepView["state"] }) {
  if (state === "running") return <LoaderCircle aria-label="Running" className="size-4 animate-spin text-press" />;
  if (state === "healing") return <Sparkles aria-label="Healing" className="size-4 animate-pulse text-heal" />;
  if (state === "healed") return <Sparkles aria-label="Healed" className="size-4 text-heal" />;
  if (state === "ok") return <Check aria-label="Done" className="size-4 text-replay" />;
  return <X aria-label="Failed" className="size-4 text-neg" />;
}

/** The heal ladder (F3): which rungs ran, which held, and what changed in the skill. */
function HealLadder({ heal }: { heal: NonNullable<StepView["heal"]> }) {
  return (
    <div className="mt-3 rounded-lg border border-heal/30 bg-heal/[0.06] p-3">
      <p className="text-xs text-muted-foreground">
        Couldn&rsquo;t find it: <span className="font-mono text-ink">{heal.failure.replace("locator not found: ", "")}</span>
      </p>
      <ol className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
        {RUNGS.map((rung, i) => {
          const tried = heal.rungs.find((r) => r.rung === rung);
          return (
            <li key={rung} className="flex items-center gap-1.5">
              {i > 0 ? <span aria-hidden className="text-muted-foreground/60">→</span> : null}
              <span
                className={cn(
                  "stamp-in inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5",
                  !tried && "border-line text-muted-foreground/60",
                  tried?.ok && "border-heal/60 text-heal",
                  tried && !tried.ok && "border-neg/40 text-neg line-through decoration-1",
                )}
              >
                {RUNG_LABEL[rung]}
                {tried?.model ? <span className="font-mono opacity-80">· {tried.model}</span> : null}
              </span>
            </li>
          );
        })}
      </ol>
      {heal.changes.length ? (
        <ul className="mt-2 space-y-0.5 font-mono text-xs text-ink">
          {heal.changes.map((c, i) => (
            <li key={i} className="enter">
              {describeChange(c)}
            </li>
          ))}
          {heal.newVersion !== null ? <li className="text-heal">skill saved as v{heal.newVersion}</li> : null}
        </ul>
      ) : null}
    </div>
  );
}

/**
 * The step timeline (F2, left): intent, what the agent did, its mode, how long it took,
 * and what it cost. The newest step stays in view inside the list (the page never jumps).
 */
export function RunTimeline({ steps, finished }: { steps: StepView[]; finished: boolean }) {
  const list = useRef<HTMLOListElement>(null);
  const lastState = steps.at(-1)?.state;
  useEffect(() => {
    const el = list.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [steps.length, lastState]);

  return (
    <ol ref={list} aria-label="Steps" className="max-h-[34rem] overflow-y-auto overscroll-contain pr-1 lg:max-h-[38rem]">
      {steps.map((s, pos) => (
        <li key={`${pos}-${s.index}`} className="enter grid grid-cols-[1.75rem_minmax(0,1fr)_auto] gap-x-3 border-b border-line py-3 last:border-0">
          <span className="pt-0.5 font-mono text-xs text-muted-foreground tabular">{String(s.index + 1).padStart(2, "0")}</span>
          <div className="min-w-0">
            <p className="text-sm leading-snug text-ink">{s.intent}</p>
            <p className="mt-0.5 truncate font-mono text-xs text-muted-foreground">{actionLine(s)}</p>
            {s.heal ? <HealLadder heal={s.heal} /> : null}
          </div>
          <div className="flex flex-col items-end gap-1 text-right font-mono text-xs text-muted-foreground tabular">
            <StateMark state={s.state} />
            {s.durationMs !== null ? <span>{seconds(s.durationMs)}</span> : null}
            {s.llmCalls > 0 ? (
              <span>
                {s.llmCalls} call · {usd(s.usd)}
              </span>
            ) : null}
          </div>
        </li>
      ))}
      {!finished && steps.length === 0 ? <li className="py-6 text-sm text-muted-foreground">Starting the browser…</li> : null}
    </ol>
  );
}
