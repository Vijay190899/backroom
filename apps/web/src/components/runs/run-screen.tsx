"use client";

import { CircleCheck, Lock, MousePointer2 } from "lucide-react";
import { animate } from "motion/react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";

import { API_URL } from "@/lib/api";
import { PORTAL_LABEL } from "@/lib/labels";
import type { Locator, RunView, StepView } from "@/lib/run-view";
import { cn } from "@/lib/utils";

const FIELD_ROLES = new Set(["textbox", "searchbox", "spinbutton", "combobox"]);

/** "/grainline/catalog?q=OAT-1L" → "Catalog". */
function pageTitle(path: string | null): string {
  const seg = path?.split("?")[0].split("/").filter(Boolean).at(-1);
  return seg ? seg[0].toUpperCase() + seg.slice(1).replace(/-/g, " ") : "";
}

/** What a filled field shows: secrets and codes are never displayed. */
function fieldValue(s: StepView): string {
  if (s.state === "running") return "";
  if (s.action === "fill_secret") return "••••••••";
  if (s.action === "totp") return "••• •••";
  return s.value ?? "";
}

type Element = { key: string; step: StepView; target: Locator; banner?: boolean };

/** The elements on the page the agent is on: everything it touched since the last page load. */
function pageElements(steps: StepView[]): Element[] {
  const from = steps.findLastIndex((s) => s.action === "goto");
  const out: Element[] = [];
  for (const s of steps.slice(from + 1)) {
    for (const [i, ins] of (s.heal?.inserted ?? []).entries()) {
      if (ins.target) out.push({ key: `${s.index}-ins-${i}`, step: { ...s, state: "ok" }, target: ins.target, banner: true });
    }
    if (s.target) out.push({ key: String(s.index), step: s, target: s.target });
  }
  return out;
}

function ElementView({ el, healedTo }: { el: Element; healedTo: Locator | null }) {
  const { step, target } = el;
  const failed = step.state === "failed" || step.state === "healing" || step.state === "heal_failed";
  if (el.banner) {
    return (
      <div className="enter flex items-center justify-between gap-3 rounded-lg bg-ink/[0.06] px-3 py-2 text-xs text-muted-foreground">
        Cookie banner
        <span className="rounded-md bg-ink px-2.5 py-1 font-medium text-background">{target.name}</span>
      </div>
    );
  }
  if (FIELD_ROLES.has(target.role)) {
    return (
      <label className="enter block text-xs text-muted-foreground">
        {target.name}
        <span
          className={cn(
            "mt-1 flex h-9 items-center rounded-md border bg-background/60 px-3 font-mono text-sm text-ink",
            step.state === "running" ? "border-press" : "border-line",
          )}
        >
          {fieldValue(step)}
          {step.state === "running" ? <span aria-hidden className="ml-px h-4 w-px animate-pulse bg-press" /> : null}
        </span>
      </label>
    );
  }
  return (
    <div className="enter flex flex-wrap items-center gap-2">
      <span
        className={cn(
          "inline-flex h-9 items-center rounded-md px-4 text-sm font-medium",
          failed ? "border border-dashed border-neg/70 text-neg" : "bg-press text-white",
        )}
      >
        {healedTo && !failed ? healedTo.name : target.name}
      </span>
      {failed ? <span className="text-xs text-neg">not found on the page</span> : null}
      {healedTo && !failed ? (
        <span className="text-xs text-muted-foreground">
          was <s>{target.name}</s>
        </span>
      ) : null}
    </div>
  );
}

/** Live frames from `WS /runs/{id}/screen`: a JSON header, then the JPEG; cursor moves the halo. */
function useScreenFrames(runId: string | null, enabled: boolean) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [frame, setFrame] = useState<{ width: number; height: number } | null>(null);
  const [cursor, setCursor] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    if (!enabled || !runId) return;
    let live = true;
    let ws: WebSocket | null = null;
    let drawn = 0;
    // The schema first, so no message (and no first frame) waits on an import.
    void import("@/lib/contracts").then(({ screenMessageSchema }) => {
      if (!live) return;
      ws = new WebSocket(`${API_URL.replace(/^http/, "ws")}/runs/${encodeURIComponent(runId)}/screen`);
      ws.binaryType = "blob";
      let expecting = false;
      ws.onmessage = (m: MessageEvent<string | Blob>) => {
        if (typeof m.data === "string") {
          let data: unknown;
          try {
            data = JSON.parse(m.data);
          } catch {
            return;
          }
          const msg = screenMessageSchema.safeParse(data);
          if (!msg.success) return;
          if (msg.data.type === "frame") expecting = true;
          else setCursor({ x: msg.data.x, y: msg.data.y });
          return;
        }
        if (!expecting) return;
        expecting = false;
        const order = ++drawn;
        void createImageBitmap(m.data).then((bmp) => {
          const c = canvas.current;
          // Draw only the newest frame, at its own size; always free the bitmap.
          if (live && c && order === drawn) {
            c.width = bmp.width;
            c.height = bmp.height;
            c.getContext("2d")?.drawImage(bmp, 0, 0);
            setFrame({ width: bmp.width, height: bmp.height });
          }
          bmp.close();
        });
      };
    });
    return () => {
      live = false;
      ws?.close();
    };
  }, [runId, enabled]);

  return { canvas, frame, cursor };
}

/**
 * The browser (F2, right). A live run streams the real page (CDP screencast frames) with
 * the agent's cursor. The recorded sample has no frames, so it draws a schematic of the page
 * from the recorded steps (the elements the agent touched, with their real labels) and
 * says so.
 */
export function RunScreen({ view, live }: { view: RunView; live: boolean }) {
  const { canvas, frame, cursor } = useScreenFrames(view.runId, live);
  const body = useRef<HTMLDivElement>(null);
  const halo = useRef<HTMLDivElement>(null);
  const elements = pageElements(view.steps);
  const last = view.steps.at(-1);
  const active = last && last.state !== "ok" && last.state !== "healed" && last.target ? String(last.index) : null;
  const done = view.finished?.status === "succeeded";

  // The cursor glides to the element being acted on (imperative: it is measurement, not state).
  useLayoutEffect(() => {
    const target = active ? body.current?.querySelector<HTMLElement>(`[data-el="${active}"]`) : null;
    if (!target || !halo.current || !body.current) return;
    const b = body.current.getBoundingClientRect();
    const r = target.getBoundingClientRect();
    void animate(
      halo.current,
      { x: r.left - b.left + Math.min(r.width - 12, 64), y: r.top - b.top + r.height / 2, opacity: 1 },
      { type: "spring", stiffness: 260, damping: 26 },
    );
  }, [active, elements.length]);

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-surface shadow-[0_30px_60px_-30px_rgb(0_0_0/0.6)]">
      <div className="flex items-center gap-3 border-b border-line px-3 py-2">
        <span aria-hidden className="flex gap-1.5">
          <span className="size-2.5 rounded-full bg-ink/15" />
          <span className="size-2.5 rounded-full bg-ink/15" />
          <span className="size-2.5 rounded-full bg-ink/15" />
        </span>
        <span className="flex min-w-0 flex-1 items-center gap-1.5 rounded-md bg-background/70 px-2.5 py-1 font-mono text-xs text-muted-foreground">
          <Lock aria-hidden className="size-3 shrink-0" />
          <span className="truncate">{view.path ?? "about:blank"}</span>
        </span>
        <span className={cn("kicker text-[0.625rem]", frame ? "text-replay" : "text-muted-foreground")}>
          {frame ? "● live" : live ? "connecting" : "schematic"}
        </span>
      </div>

      <div ref={body} className="relative h-[24rem] overflow-hidden p-5 sm:p-6">
        {/* One canvas for the whole run, so drawn frames survive re-renders; the halo is
            placed in the canvas's own box. */}
        {live ? (
          <div className={frame ? "relative" : "hidden"}>
            <canvas ref={canvas} aria-label="The agent's browser" className="block h-auto w-full" />
            {frame && cursor ? (
              <div
                aria-hidden
                className="pointer-events-none absolute size-8 -translate-1/2 rounded-full border-2 border-press bg-press/20 transition-[left,top] duration-200"
                style={{ left: `${(cursor.x / frame.width) * 100}%`, top: `${(cursor.y / frame.height) * 100}%` }}
              />
            ) : null}
          </div>
        ) : null}
        {frame ? null : (
          <>
            <p className="kicker text-[0.625rem] text-muted-foreground">
              {view.portal ? (PORTAL_LABEL[view.portal] ?? view.portal) : "Portal"}
            </p>
            <p className="mt-1 text-xl font-semibold tracking-[-0.02em] text-ink">{pageTitle(view.path)}</p>
            <div className="mt-5 max-w-sm space-y-3">
              {elements.map((el) => (
                <div key={el.key} data-el={el.key}>
                  <ElementView el={el} healedTo={el.banner ? null : (el.step.heal?.target ?? null)} />
                </div>
              ))}
            </div>
            {done ? (
              <div className="enter absolute inset-0 grid place-items-center bg-surface/85 p-6 text-center backdrop-blur-[2px]">
                <div>
                  <CircleCheck aria-hidden className="mx-auto size-10 text-replay" />
                  <p className="mt-3 text-lg font-semibold text-ink">{view.finished?.summary}</p>
                </div>
              </div>
            ) : null}
            <div
              ref={halo}
              aria-hidden
              className={cn(
                "pointer-events-none absolute top-0 left-0 opacity-0",
                (!active || done) && "invisible",
              )}
            >
              <span className="absolute -top-4 -left-4 size-8 rounded-full bg-press/25 motion-safe:animate-ping" />
              <MousePointer2 className="relative size-5 fill-press text-white drop-shadow" />
            </div>
          </>
        )}
      </div>
      {!frame ? (
        <p className="border-t border-line px-3 py-2 text-[11px] text-muted-foreground">
          {live
            ? "Waiting for the browser stream; the page is drawn from the steps until it arrives."
            : "Schematic: drawn from the recorded steps and their real labels. A live run streams the actual page."}
        </p>
      ) : null}
    </div>
  );
}
