"use client";

import NumberFlow from "@number-flow/react";
import { Pause, Play, RotateCcw, Undo2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { RunScreen } from "@/components/runs/run-screen";
import { RunTimeline } from "@/components/runs/run-timeline";
import { SampleBadge } from "@/components/sample-badge";
import { Button } from "@/components/ui/button";
import { API_URL } from "@/lib/api";
import type { RunEvent } from "@/lib/contracts";
import { formatEur } from "@/lib/format";
import { PORTAL_LABEL, TASK_LABEL } from "@/lib/labels";
import { SAMPLE_RUN_ID, useRunEvents } from "@/lib/run-source";
import { foldRun, gapMs, type Mode, type RunView } from "@/lib/run-view";
import { cn } from "@/lib/utils";

const MODE_STYLE: Record<Mode, string> = {
  replay: "border-replay/60 text-replay",
  heal: "border-heal/60 text-heal shadow-[0_0_24px_-4px_var(--t-heal)]",
  explore: "border-explore/60 text-explore",
};
const SEEDS = [0, 7, 13, 42];

/** Recorded runs play back in (clipped) real time with play, pause and speed; live runs follow the stream. */
function usePlayhead(events: RunEvent[], live: boolean) {
  const [upTo, setUpTo] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1);
  useEffect(() => {
    if (live || !playing || upTo >= events.length) return;
    const timer = setTimeout(() => setUpTo((n) => n + 1), upTo === 0 ? 300 : gapMs(events, upTo, speed));
    return () => clearTimeout(timer);
  }, [live, playing, upTo, events, speed]);
  const shown = live ? events.length : upTo;
  return {
    shown,
    playing: playing && shown < events.length,
    speed,
    setSpeed,
    toggle: () => (shown >= events.length ? (setUpTo(0), setPlaying(true)) : setPlaying((p) => !p)),
    restart: () => {
      setUpTo(0);
      setPlaying(true);
    },
  };
}

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface px-4 py-3">
      <dt className="kicker text-[0.625rem] text-muted-foreground">{label}</dt>
      <dd className="mt-1 font-mono text-lg text-ink tabular">{children}</dd>
    </div>
  );
}

/** The ticker (F2): elapsed, model calls, tokens, cost, skill version. All from events. */
function Ticker({ view }: { view: RunView }) {
  const t = view.totals;
  return (
    <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-5">
      <Stat label="Elapsed">
        <NumberFlow value={view.elapsedMs / 1000} format={{ minimumFractionDigits: 1, maximumFractionDigits: 1 }} suffix=" s" />
      </Stat>
      <Stat label="Model calls">
        <NumberFlow value={t.llm_calls} />
      </Stat>
      <Stat label="Tokens in / out">
        <NumberFlow value={t.tokens_in} /> / <NumberFlow value={t.tokens_out} />
      </Stat>
      <Stat label="Cost">
        <NumberFlow
          value={t.usd}
          locales="en-US"
          format={{ style: "currency", currency: "USD", minimumFractionDigits: 4, maximumFractionDigits: 4 }}
        />
      </Stat>
      <Stat label="Skill">
        {view.skillVersion !== null ? (
          <span key={view.skillVersion} className="stamp-in inline-block">
            v{view.skillVersion}
          </span>
        ) : (
          "new"
        )}
      </Stat>
    </dl>
  );
}

/**
 * Chaos (F2): re-skin the portal before the next run, to show healing live. Needs the API;
 * a recorded run shows the seed it ran at.
 */
function ChaosPicker({ portal, seed, live }: { portal: string | null; seed: number | null; live: boolean }) {
  const [picked, setPicked] = useState(seed);
  const [note, setNote] = useState<string | null>(null);
  async function pick(next: number) {
    if (!portal) return;
    setPicked(next);
    try {
      const [res, { chaosStateSchema }] = await Promise.all([
        fetch(`${API_URL}/chaos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ portal, seed: next }),
        }),
        import("@/lib/contracts"),
      ]);
      if (!res.ok) throw new Error(String(res.status));
      const state = chaosStateSchema.parse(await res.json());
      const label = PORTAL_LABEL[state.portal] ?? state.portal;
      setNote(`${label} now renders seed ${state.seed} (${Object.keys(state.variants).length} variants). Approve again from Today to run on it.`);
    } catch {
      setPicked(seed);
      setNote("Couldn’t re-skin the portal. Is the API running?");
    }
  }
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
      <span className="kicker text-[0.625rem] text-muted-foreground">Chaos seed</span>
      <div role="radiogroup" aria-label="Chaos seed" className="flex gap-1">
        {SEEDS.map((s) => (
          <button
            key={s}
            type="button"
            role="radio"
            aria-checked={picked === s}
            disabled={!live}
            title={live ? `Re-skin the portal with seed ${s}` : `This recorded run used seed ${seed}. Re-skinning needs the live API.`}
            onClick={() => void pick(s)}
            className={cn(
              "h-9 min-w-10 rounded-md border px-2 font-mono text-sm tabular transition-colors",
              picked === s ? "border-press bg-press/15 text-ink" : "border-line text-muted-foreground",
              live ? "cursor-pointer hover:border-ink/40" : "cursor-not-allowed",
            )}
          >
            {s}
          </button>
        ))}
      </div>
      <p role="status" className="w-full text-xs text-muted-foreground sm:text-right">
        {note ?? (live ? null : `Recorded at seed ${seed}. Re-skinning a portal needs the live API.`)}
      </p>
    </div>
  );
}

function resultEntries(result: Record<string, unknown>): [string, string][] {
  return Object.entries(result).map(([k, v]) => [
    k.replace(/_eur$/, "").replace(/_/g, " "),
    k.endsWith("_eur") && typeof v === "number" ? formatEur(v) : String(v),
  ]);
}

/** On completion (F2): what happened, the totals, and Undo where the portal supports it. */
function Result({ view, live }: { view: RunView; live: boolean }) {
  const f = view.finished;
  const [undo, setUndo] = useState<{ state: "idle" | "busy" | "error" } | { state: "done"; runId: string }>({ state: "idle" });
  if (!f) return null;
  const heals = view.heals;
  async function doUndo() {
    if (!view.runId) return;
    setUndo({ state: "busy" });
    try {
      const [res, { undoResponseSchema }] = await Promise.all([
        fetch(`${API_URL}/runs/${encodeURIComponent(view.runId)}/undo`, { method: "POST" }),
        import("@/lib/contracts"),
      ]);
      if (!res.ok) throw new Error(String(res.status));
      setUndo({ state: "done", runId: undoResponseSchema.parse(await res.json()).run_id });
    } catch {
      setUndo({ state: "error" });
    }
  }
  return (
    <section aria-label="Result" className="enter rounded-xl border border-line bg-surface p-5">
      <p className={cn("kicker text-[0.625rem]", f.status === "succeeded" ? "text-replay" : "text-neg")}>
        {f.status.replace("_", " ")}
      </p>
      <p className="mt-2 text-xl leading-snug font-semibold tracking-[-0.02em] text-ink">{f.summary}</p>
      <dl className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm">
        {resultEntries(f.result).map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <dt className="text-muted-foreground">{k}</dt>
            <dd className="font-mono text-ink">{v}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-2 text-sm text-muted-foreground">
        {f.totals.steps} steps · {heals} {heals === 1 ? "heal" : "heals"} · {f.totals.llm_calls} model calls ·{" "}
        {(f.totals.elapsed_ms / 1000).toFixed(1)} s
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        {f.undo_available ? (
          <Button variant="outline" disabled={!live || undo.state === "busy" || undo.state === "done"} onClick={() => void doUndo()}>
            <Undo2 aria-hidden className="size-4" />
            Undo
          </Button>
        ) : null}
        <p role="status" className="text-sm text-muted-foreground">
          {!live && f.undo_available ? "Sample run: nothing to undo." : null}
          {undo.state === "done" ? (
            <>
              Undone.{" "}
              <Link href={`/runs/${undo.runId}`} className="link-draw text-ink">
                Watch the undo run
              </Link>
            </>
          ) : null}
          {undo.state === "error" ? "Couldn’t undo. Try again." : null}
        </p>
      </div>
    </section>
  );
}

/** The agent asked for a person (heal ladder's last rung): resume or cancel. */
function NeedsYou({ view, live }: { view: RunView; live: boolean }) {
  const [sent, setSent] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  if (!view.askHuman || view.finished) return null;
  async function reply(action: "resume" | "cancel") {
    if (!view.runId || busy) return;
    setBusy(true);
    const res = await fetch(`${API_URL}/runs/${encodeURIComponent(view.runId)}/human`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, note: null }),
    }).catch(() => null);
    setSent(res?.ok ? (action === "resume" ? "Resuming…" : "Cancelling…") : "Couldn’t send. Try again.");
    if (!res?.ok) setBusy(false);
  }
  return (
    <section aria-label="The agent needs you" className="enter rounded-xl border border-amber/50 bg-amber/10 p-5">
      <p className="kicker text-[0.625rem] text-amber">The agent needs you</p>
      <p className="mt-2 text-ink">{view.askHuman.reason}</p>
      <div className="mt-4 flex gap-3">
        <Button disabled={!live || busy} onClick={() => void reply("resume")}>
          I fixed it, resume
        </Button>
        <Button variant="outline" disabled={!live || busy} onClick={() => void reply("cancel")}>
          Cancel the run
        </Button>
      </div>
      {sent ? (
        <p role="status" className="mt-2 text-sm text-muted-foreground">
          {sent}
        </p>
      ) : null}
    </section>
  );
}

/**
 * The run theater (F2): the step timeline beside the browser, a ticker above, the result
 * below. Dark and focused whatever the app theme (PRD principle 3). A recorded run plays
 * back with controls; a live one follows its SSE stream.
 */
export function RunTheater({ id }: { id: string }) {
  const { events, source, status } = useRunEvents(id);
  const live = source === "live";
  const head = usePlayhead(events, live);
  const view = useMemo(() => foldRun(events.slice(0, head.shown)), [events, head.shown]);
  const started = events[0]?.type === "run.started" ? events[0] : null;
  const title = started ? (TASK_LABEL[started.task] ?? "Agent run") : "";
  const portal = started ? (PORTAL_LABEL[started.portal] ?? started.portal) : null;

  if (status === "error" && events.length === 0) {
    return (
      <>
        <PageHeader kicker="Run theater" title="Run not found" />
        <div role="alert" className="border-y border-line py-12 text-center">
          <p className="text-2xl text-ink">This run isn&rsquo;t available.</p>
          <p className="mt-2 text-muted-foreground">The API may be offline, or the run id is wrong.</p>
          <Link href={`/runs/${SAMPLE_RUN_ID}`} className="link-draw mt-6 inline-block text-press-ink">
            Watch the recorded sample run
          </Link>
        </div>
      </>
    );
  }

  // Until the run says what it is, hold the space: the header and stage then arrive
  // together instead of the stage being pushed down by a growing headline.
  if (!started) {
    return (
      <div data-theater aria-busy="true" className="min-h-[60vh]">
        <p className="kicker text-press-ink">Run theater</p>
        <p className="mt-4 text-muted-foreground">Connecting to the run…</p>
      </div>
    );
  }

  return (
    <>
      <PageHeader
        kicker={`Run theater${portal ? ` · ${portal}` : ""}`}
        title={title}
        subtitle={`${started.recorded ? "Recorded" : live ? "Live" : "Sample"} run at chaos seed ${started.chaos_seed}, starting on skill v${started.skill_version ?? "–"}.`}
        actions={live ? null : <SampleBadge label="Sample run" why="The committed recorded run, played back. No portal is touched." />}
      />

      <section data-theater aria-label="Run" className="dark space-y-4 rounded-[var(--t-radius-card)] border border-line bg-background p-3 text-ink sm:p-5">
        <div className="flex flex-wrap items-center gap-3">
          {/* A stable live region; only the badge inside it re-mounts to stamp in. */}
          <span aria-live="polite">
            <span
              key={view.mode}
              className={cn("stamp-in kicker inline-flex h-9 items-center rounded-md border px-3 text-xs", MODE_STYLE[view.mode])}
            >
              {view.mode}
            </span>
          </span>
          {!live ? (
            <div className="flex items-center gap-1">
              <Button size="icon" variant="ghost" aria-label={head.playing ? "Pause" : "Play"} onClick={head.toggle}>
                {head.playing ? <Pause className="size-4" /> : <Play className="size-4" />}
              </Button>
              <Button size="icon" variant="ghost" aria-label="Restart" onClick={head.restart}>
                <RotateCcw className="size-4" />
              </Button>
              <div role="radiogroup" aria-label="Speed" className="ml-1 flex rounded-md border border-line p-0.5">
                {[1, 2].map((s) => (
                  <button
                    key={s}
                    type="button"
                    role="radio"
                    aria-checked={head.speed === s}
                    onClick={() => head.setSpeed(s)}
                    className={cn(
                      "h-8 min-w-9 cursor-pointer rounded px-2 font-mono text-xs",
                      head.speed === s ? "bg-ink text-background" : "text-muted-foreground",
                    )}
                  >
                    {s}×
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <span className="kicker text-[0.625rem] text-replay">{status === "done" ? "finished" : "● live"}</span>
          )}
          <div className="ml-auto">
            <ChaosPicker key={view.chaosSeed ?? -1} portal={view.portal} seed={view.chaosSeed} live={live} />
          </div>
        </div>

        {status === "error" ? (
          <p role="alert" className="rounded-lg border border-neg/40 bg-neg/10 px-3 py-2 text-sm text-ink">
            Lost the connection to this run. The steps so far are below; reload to resume.
          </p>
        ) : null}

        <div aria-hidden className="h-0.5 overflow-hidden rounded-full bg-line">
          <div
            className={cn("h-full origin-left transition-transform duration-300", view.mode === "heal" ? "bg-heal" : "bg-press")}
            style={{ transform: `scaleX(${events.length ? head.shown / events.length : 0})` }}
          />
        </div>

        <Ticker view={view} />

        <div className="grid gap-4 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
          <div className="order-2 rounded-xl border border-line bg-surface/60 px-4 lg:order-1">
            <RunTimeline steps={view.steps} finished={!!view.finished} />
          </div>
          <div className="order-1 lg:order-2">
            <RunScreen view={view} live={live} />
          </div>
        </div>

        <NeedsYou view={view} live={live} />
        <Result view={view} live={live} />
      </section>
    </>
  );
}
