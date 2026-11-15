"use client";

import { useEffect, useState } from "react";

import { API_URL } from "@/lib/api";
import type { RunEvent } from "@/lib/contracts";

/** The committed sample run's id (fixtures/run-events.json). */
export const SAMPLE_RUN_ID = "run_demo_seed7";

const EVENT_TYPES = [
  "run.started",
  "step.started",
  "step.finished",
  "mode.changed",
  "heal.started",
  "heal.attempt",
  "heal.succeeded",
  "heal.failed",
  "cost.tick",
  "ask_human",
  "run.finished",
] as const satisfies readonly RunEvent["type"][];

export type RunSource = {
  events: RunEvent[];
  source: "sample" | "live";
  status: "loading" | "streaming" | "done" | "error";
};

/**
 * A run's events: the committed sample for `SAMPLE_RUN_ID`, otherwise the API's SSE stream
 * (`GET /runs/{id}/events`, CONTRACTS §5). EventSource reconnects with Last-Event-ID on its
 * own, so a dropped connection resumes exactly; events are kept in `seq` order, once each.
 */
export function useRunEvents(id: string): RunSource {
  const sample = id === SAMPLE_RUN_ID;
  const [state, setState] = useState<RunSource>({ events: [], source: sample ? "sample" : "live", status: "loading" });

  useEffect(() => {
    let live = true;
    if (sample) {
      void Promise.all([import("@/lib/contracts"), import("@/fixtures/run-events.json")])
        .then(([{ runEventSchema }, fixture]) => {
          if (live) setState({ events: runEventSchema.array().parse(fixture.default), source: "sample", status: "done" });
        })
        .catch(() => live && setState((s) => ({ ...s, status: "error" })));
      return () => {
        live = false;
      };
    }

    const es = new EventSource(`${API_URL}/runs/${encodeURIComponent(id)}/events`);
    const seen = new Map<number, RunEvent>();
    const schema = import("@/lib/contracts").then((m) => m.runEventSchema);
    let failures = 0;
    const onEvent = (msg: MessageEvent<string>) => {
      failures = 0;
      void schema.then((runEventSchema) => {
        let data: unknown;
        try {
          data = JSON.parse(msg.data);
        } catch {
          return;
        }
        const parsed = runEventSchema.safeParse(data);
        if (!live || !parsed.success) return;
        seen.set(parsed.data.seq, parsed.data);
        const events = [...seen.values()].sort((a, b) => a.seq - b.seq);
        const done = parsed.data.type === "run.finished";
        if (done) es.close();
        setState({ events, source: "live", status: done ? "done" : "streaming" });
      });
    };
    for (const type of EVENT_TYPES) es.addEventListener(type, onEvent);
    es.onerror = () => {
      if (!live) return;
      failures += 1;
      // EventSource retries on its own (resuming from Last-Event-ID). Give up when the
      // browser has, or after three failed tries in a row; the events so far are kept.
      if (es.readyState === EventSource.CLOSED || failures >= 3) {
        es.close();
        setState((s) => (s.status === "done" ? s : { ...s, status: "error" }));
      }
    };
    return () => {
      live = false;
      es.close();
    };
  }, [id, sample]);

  return state;
}
