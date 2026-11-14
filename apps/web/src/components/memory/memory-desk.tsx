"use client";

import NumberFlow from "@number-flow/react";
import { Pause, Play, Waypoints } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { BadgeSlot, SampleBadge } from "@/components/sample-badge";
import type { GraphFact, GraphNode, MemoryGraph } from "@/lib/contracts";
import { useLiveOrSample } from "@/lib/data";
import { formatDateline, formatEur } from "@/lib/format";
import { dayOf, endOfDay, layout, PREDICATE, record, timeline, validAt, type Slot } from "@/lib/memory";
import { prefersReducedMotion } from "@/lib/motion";
import { cn } from "@/lib/utils";

const PLAY_MS = 5200;
const shortDate = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "Europe/Berlin" });
const isoDay = (t: number) => new Date(t).toISOString().slice(0, 10);

type Point = { x: number; y: number };

/** A soft S-curve between two nodes, in pixels: horizontal bands on wide screens, vertical on phones. */
function edgePath(a: Point, b: Point, size: { w: number; h: number }, narrow: boolean): string {
  const [ax, ay, bx, by] = [(a.x * size.w) / 100, (a.y * size.h) / 100, (b.x * size.w) / 100, (b.y * size.h) / 100];
  // Two nodes in the same band: bow around the labels instead of running through them.
  if (narrow && Math.abs(ay - by) < 1) return `M ${ax} ${ay} C ${ax} ${ay + 70}, ${bx} ${by + 70}, ${bx} ${by}`;
  if (!narrow && Math.abs(ax - bx) < 1) return `M ${ax} ${ay} C ${ax - 70} ${ay}, ${bx - 70} ${by}, ${bx} ${by}`;
  if (narrow) {
    const my = (ay + by) / 2;
    return `M ${ax} ${ay} C ${ax} ${my}, ${bx} ${my}, ${bx} ${by}`;
  }
  const mx = (ax + bx) / 2;
  return `M ${ax} ${ay} C ${mx} ${ay}, ${mx} ${by}, ${bx} ${by}`;
}

function useGraph() {
  return useLiveOrSample<MemoryGraph>(
    "memory-graph",
    "/memory/graph",
    async () => (await import("@/lib/contracts")).memoryGraphSchema,
    () => import("@/fixtures/memory-graph.json"),
  );
}

/** A fact's value as words and rolling digits: "€8.24/kg", "77.5 g of Butter", "Grainline Wholesale". */
function FactValue({ fact, nodes }: { fact: GraphFact; nodes: Map<string, GraphNode> }) {
  const eur = { style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 2 } as const;
  if (typeof fact.value === "number" && fact.predicate.includes("eur")) {
    return (
      <NumberFlow
        value={fact.value}
        locales="en-IE"
        format={eur}
        suffix={fact.predicate.endsWith("per_kg") ? "/kg" : undefined}
      />
    );
  }
  const object = fact.object_id ? nodes.get(fact.object_id)?.name : null;
  const grams = fact.value && typeof fact.value === "object" && "grams" in fact.value ? fact.value.grams : null;
  if (typeof grams === "number" && object) return <span>{grams} g of {object}</span>;
  if (object) return <span>{object}</span>;
  return <span>{typeof fact.value === "object" ? JSON.stringify(fact.value) : String(fact.value)}</span>;
}

/** The previous value as plain text for the "was …" line, when it is a price. */
function plainValue(fact: GraphFact): string {
  if (typeof fact.value === "number" && fact.predicate.includes("eur")) {
    return formatEur(fact.value) + (fact.predicate.endsWith("per_kg") ? "/kg" : "");
  }
  return "";
}

function RecordRow({ slot, nodes, focus }: { slot: Slot; nodes: Map<string, GraphNode>; focus: string | null }) {
  const fact = slot.current ?? slot.previous;
  if (!fact || !slot.subject) return null;
  const dim = focus !== null && fact.subject_id !== focus && fact.object_id !== focus;
  const ended = !slot.current;
  return (
    // Dimmed rows step down to the muted ink (still 4.5:1), not to a faint opacity.
    <li className={cn("border-b border-line py-3", dim && "[&_*]:text-muted-foreground!")}>
      <p className="text-[0.9375rem] leading-snug">
        <span className="font-display text-lg text-ink">{slot.subject.name}</span>{" "}
        <span className="text-muted-foreground">{PREDICATE[slot.predicate] ?? slot.predicate.replaceAll("_", " ")}</span>{" "}
        <span
          key={slot.current?.id ?? "ended"}
          className={cn("font-medium text-ink tabular", ended ? "line-through decoration-neg" : slot.previous && "marker")}
        >
          <FactValue fact={fact} nodes={nodes} />
        </span>
      </p>
      <p className="mt-1 text-xs text-muted-foreground tabular">
        {ended
          ? `until ${shortDate.format(Date.parse(fact.valid_to ?? ""))}`
          : `since ${shortDate.format(Date.parse(fact.valid_from))}`}
        {slot.current && slot.previous && plainValue(slot.previous)
          ? ` · was ${plainValue(slot.previous)} until ${shortDate.format(Date.parse(slot.previous.valid_to ?? ""))}`
          : ""}
        {fact.confidence < 1 ? ` · ${Math.round(fact.confidence * 100)}% confidence` : ""}
      </p>
    </li>
  );
}

/**
 * The graph box's pixel size, so edges are drawn in real pixels (clean strokes). A
 * callback ref: the box only mounts once the graph has loaded.
 */
function useSize() {
  const [el, setEl] = useState<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  useEffect(() => {
    if (!el) return;
    const observer = new ResizeObserver(([entry]) =>
      setSize({ w: entry.contentRect.width, h: entry.contentRect.height }),
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [el]);
  return [setEl, size] as const;
}

export function MemoryDesk() {
  const query = useGraph();
  const graph = query.data?.data;
  const range = useMemo(() => (graph ? timeline(graph.facts, graph.as_of) : null), [graph]);
  // The day shown (midnight UTC); facts are read as of the end of that day.
  const [t, setT] = useState<number | null>(null);
  const [playing, setPlaying] = useState(false);
  const [focus, setFocus] = useState<string | null>(null);
  const frame = useRef(0);
  const [box, size] = useSize();
  const narrow = size.w > 0 && size.w < 560;

  // Start at the date in the URL (?as_of=2026-11-01) when there is one, else at the end.
  useEffect(() => {
    if (!range) return;
    const fromUrl = Date.parse(new URLSearchParams(location.search).get("as_of") ?? "");
    const id = requestAnimationFrame(() =>
      setT(Number.isNaN(fromUrl) ? range.end : Math.min(range.end, Math.max(range.start, dayOf(fromUrl)))),
    );
    return () => cancelAnimationFrame(id);
  }, [range]);

  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  const day = dayOf(t ?? range?.end ?? 0);
  const at = endOfDay(day);
  const nodes = useMemo(() => new Map((graph?.nodes ?? []).map((n) => [n.id, n])), [graph]);
  const pos = useMemo(() => layout(graph?.nodes ?? [], narrow), [graph, narrow]);
  const slots = useMemo(() => (graph ? record(graph.nodes, graph.facts, at) : []), [graph, at]);
  const edges = (graph?.facts ?? []).filter((f) => f.object_id && validAt(f, at));
  const known = new Set(
    (graph?.facts ?? []).filter((f) => Date.parse(f.valid_from) <= at).flatMap((f) => [f.subject_id, f.object_id ?? ""]),
  );

  function writeUrl(value: number) {
    const url = new URL(location.href);
    url.searchParams.set("as_of", isoDay(value));
    history.replaceState(null, "", url);
  }

  function play() {
    if (!range) return;
    if (prefersReducedMotion()) {
      setT(range.end);
      writeUrl(range.end);
      return;
    }
    setPlaying(true);
    const begin = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - begin) / PLAY_MS);
      setT(range.start + (range.end - range.start) * p);
      if (p < 1) frame.current = requestAnimationFrame(tick);
      else {
        setPlaying(false);
        writeUrl(range.end);
      }
    };
    frame.current = requestAnimationFrame(tick);
  }

  function stop() {
    cancelAnimationFrame(frame.current);
    setPlaying(false);
  }

  const pct = (v: number) => (range ? ((v - range.start) / (range.end - range.start)) * 100 : 0);

  return (
    <>
      <PageHeader
        kicker="What Backroom knows"
        title="Memory"
        subtitle="Every fact Backroom holds, when it became true, and what replaced it. Drag the date to see what was true then."
        actions={
          !query.data ? (
            <BadgeSlot />
          ) : query.data.source === "sample" ? (
            <SampleBadge why="The API has no memory route yet, so this is the committed sample." />
          ) : null
        }
      />

      {query.isError ? (
        <div role="alert" className="border-y border-line py-12 text-center">
          <p className="font-display text-2xl text-ink">Memory didn&rsquo;t load.</p>
          <button
            type="button"
            onClick={() => void query.refetch()}
            className="link-draw mt-3 inline-flex min-h-11 cursor-pointer items-center text-press-ink"
          >
            Try again
          </button>
        </div>
      ) : graph && !range ? (
        <EmptyState
          icon={Waypoints}
          title="Nothing remembered yet"
          body="Facts arrive with the first invoices, approvals and runs; each one keeps when it became true."
        />
      ) : graph && range ? (
        <>
          <section aria-label="Time" className="border-y border-ink py-5">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="kicker text-press-ink">As of</p>
                <p className="mt-1 font-display text-3xl text-ink tabular sm:text-4xl">
                  {formatDateline(new Date(day + 43_200_000).toISOString())}
                </p>
              </div>
              <button
                type="button"
                onClick={playing ? stop : play}
                className="inline-flex h-11 cursor-pointer items-center gap-2 border border-ink/25 px-4 text-sm font-medium text-ink transition-[border-color,background-color,transform] duration-150 hover:-translate-y-px hover:border-ink/60 active:scale-[0.98] sm:h-10"
              >
                {playing ? <Pause aria-hidden className="size-4" /> : <Play aria-hidden className="size-4" />}
                {playing ? "Pause" : "Replay the record"}
              </button>
            </div>

            <div className="relative mt-6 pb-6">
              <input
                type="range"
                aria-label="As-of date"
                aria-valuetext={formatDateline(new Date(day + 43_200_000).toISOString())}
                min={range.start}
                max={range.end}
                step={range.day}
                value={day}
                onChange={(e) => {
                  stop();
                  setT(Number(e.target.value));
                }}
                onPointerUp={(e) => writeUrl(Number(e.currentTarget.value))}
                onKeyUp={(e) => {
                  // Only keys that move the slider; tabbing onto it changes nothing.
                  if (/^(Arrow|Page|Home|End)/.test(e.key)) writeUrl(Number(e.currentTarget.value));
                }}
                className="timeline-range w-full"
              />
              {range.changes.map((c) => (
                <button
                  key={c}
                  type="button"
                  aria-label={`Jump to ${shortDate.format(c)}, when the record changed`}
                  onClick={() => {
                    stop();
                    setT(c);
                    writeUrl(c);
                  }}
                  style={{ left: `${pct(c)}%` }}
                  className="group absolute top-[calc(50%-0.75rem-0.5rem)] flex h-11 w-11 -translate-x-1/2 cursor-pointer flex-col items-center"
                >
                  <span aria-hidden className={cn("mt-4 h-3 w-px", c <= day ? "bg-press" : "bg-muted-foreground/50")} />
                  <span aria-hidden className="mt-1 text-[0.625rem] whitespace-nowrap text-muted-foreground tabular">
                    {shortDate.format(c)}
                  </span>
                </button>
              ))}
            </div>
          </section>

          <div className="mt-10 grid gap-12 lg:grid-cols-12 lg:gap-10">
            <section aria-label="Graph" className="lg:col-span-7">
              <h2 className="kicker text-ink">Who and what</h2>
              <div ref={box} className="relative mt-4 aspect-[4/5] w-full border-t border-ink sm:aspect-[16/11]">
                <svg
                  aria-hidden
                  className="absolute inset-0 size-full overflow-visible"
                  viewBox={`0 0 ${size.w || 100} ${size.h || 100}`}
                >
                  {(size.w ? edges : []).map((f) => {
                    const a = pos.get(f.subject_id);
                    const b = pos.get(f.object_id ?? "");
                    if (!a || !b) return null;
                    const dim = focus !== null && f.subject_id !== focus && f.object_id !== focus;
                    return (
                      <g key={f.id} className={cn("transition-opacity duration-200", dim && "opacity-20")}>
                        <path
                          d={edgePath(a, b, size, narrow)}
                          pathLength={1}
                          className="edge-draw fill-none stroke-ink/40"
                          strokeWidth={1.25}
                        />
                      </g>
                    );
                  })}
                </svg>
                {(narrow ? [] : edges).map((f) => {
                  const a = pos.get(f.subject_id);
                  const b = pos.get(f.object_id ?? "");
                  if (!a || !b) return null;
                  return (
                    <span
                      key={`label-${f.id}`}
                      aria-hidden
                      style={{
                        left: Math.abs(a.x - b.x) < 1 ? `calc(${a.x}% - 52px)` : `${(a.x + b.x) / 2}%`,
                        top: `${(a.y + b.y) / 2}%`,
                      }}
                      className="enter absolute -translate-1/2 bg-background px-1 font-mono text-[0.625rem] whitespace-nowrap text-muted-foreground"
                    >
                      {PREDICATE[f.predicate] ?? f.predicate}
                    </span>
                  );
                })}
                {(graph?.nodes ?? []).map((n) => {
                  const p = pos.get(n.id);
                  if (!p) return null;
                  const value = graph.facts.find(
                    (f) => f.subject_id === n.id && typeof f.value === "number" && validAt(f, at),
                  );
                  const isKnown = known.has(n.id);
                  return (
                    <button
                      key={n.id}
                      type="button"
                      onPointerEnter={() => setFocus(n.id)}
                      onPointerLeave={() => setFocus(null)}
                      onFocus={() => setFocus(n.id)}
                      onBlur={() => setFocus(null)}
                      style={{ left: `${p.x}%`, top: `${p.y}%` }}
                      className={cn(
                        // The dot sits exactly on the node's point, so edges meet dots, not labels:
                        // labels hang below it on wide screens and sit beside it on phones.
                        "absolute flex min-h-11 -translate-y-[0.3125rem] cursor-default",
                        narrow
                          ? "-translate-x-[0.3125rem] flex-row items-start gap-2 text-left"
                          : "-translate-x-1/2 flex-col items-center px-1 text-center",
                      )}
                    >
                      <span
                        aria-hidden
                        className={cn(
                          "size-2.5 shrink-0 border",
                          isKnown ? "border-ink" : "border-dashed border-muted-foreground",
                          focus === n.id ? "bg-press" : "bg-background",
                        )}
                      />
                      <span className={cn("flex flex-col", narrow ? "-mt-1 items-start" : "items-center")}>
                        <span className={cn("kicker text-[0.5625rem] text-muted-foreground", !narrow && "mt-1.5")}>{n.type}</span>
                        <span
                          className={cn(
                            "max-w-[34vw] font-display text-[0.875rem] leading-tight sm:max-w-[9rem] sm:text-base",
                            isKnown ? "text-ink" : "text-muted-foreground",
                          )}
                        >
                          {n.name}
                          {isKnown ? null : <span className="sr-only"> (not known yet)</span>}
                        </span>
                        {value ? (
                          <span className="mt-0.5 font-mono text-xs text-press-ink tabular">
                            <FactValue fact={value} nodes={nodes} />
                          </span>
                        ) : null}
                      </span>
                    </button>
                  );
                })}
              </div>
            </section>

            <section aria-labelledby="record-heading" className="lg:col-span-5">
              <h2 id="record-heading" className="kicker text-ink">
                The record
              </h2>
              <ul className="mt-4 border-t border-ink">
                {slots.map((s) => (
                  <RecordRow key={s.key} slot={s} nodes={nodes} focus={focus} />
                ))}
              </ul>
              <p className="mt-4 text-sm text-muted-foreground">
                Nothing is overwritten: a new invoice closes the old fact and opens a new one, so the
                record can be read as of any day.
              </p>
            </section>
          </div>
        </>
      ) : (
        <div role="status" aria-label="Loading memory" className="h-96 animate-pulse border-y border-line bg-subtle/50" />
      )}
    </>
  );
}
