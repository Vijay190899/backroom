"use client";

import { Check, Loader2 } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { Figure, FigureValue } from "@/components/motion/figure";
import { RunTicker } from "@/components/today/run-ticker";
import { Button } from "@/components/ui/button";
import type { ActionCard as Card, EvidenceNumber, RunEvent } from "@/lib/contracts";
import { changedWords } from "@/lib/diff";
import { PORTAL_LABEL as PORTAL } from "@/lib/labels";
import { enterDelay } from "@/lib/motion";
import { loadSampleRun } from "@/lib/runs";
import { cn } from "@/lib/utils";

const KIND: Record<Card["kind"], string> = {
  stockout: "Stock",
  margin_erosion: "Margin",
  weather_demand: "Weather",
};
/** The figures worth printing beside the lead story, per kind, in reading order. */
const KEY_FIGURES: Record<Card["kind"], string[]> = {
  stockout: ["days_left", "qty", "order_total_eur"],
  margin_erosion: ["margin_after_pct", "margin_target_pct", "price_now_eur", "price_new_eur"],
  weather_demand: ["rain_mm", "footfall_change_pct", "shift_hours"],
};

// The drawer and the dialog (and Base UI's dialog code) load on first use, off the
// critical path of the first paint.
const EvidenceDrawer = dynamic(
  () => import("@/components/today/evidence-drawer").then((m) => m.EvidenceDrawer),
  { ssr: false },
);
const RejectDialog = dynamic(
  () => import("@/components/today/reject-dialog").then((m) => m.RejectDialog),
  { ssr: false },
);

export type CardStatus = "proposed" | "approving" | "approved" | "rejected";
type Variant = "lead" | "column";

function impactNumber(card: Card): EvidenceNumber | undefined {
  return card.numbers.find((n) => n.key === "impact_eur_weekly");
}

function keyFigures(card: Card): EvidenceNumber[] {
  const byKey = new Map(card.numbers.map((n) => [n.key, n]));
  const picked = KEY_FIGURES[card.kind].flatMap((k) => byKey.get(k) ?? []);
  const fallback = card.numbers.filter((n) => n.key !== "impact_eur_weekly").slice(0, 3);
  return picked.length ? picked : fallback;
}

function Kicker({ card }: { card: Card }) {
  return (
    <p className="kicker flex flex-wrap items-center gap-x-2 text-press-ink">
      <span>{KIND[card.kind]}</span>
      <span aria-hidden className="text-line">
        /
      </span>
      <span className="text-muted-foreground" translate="no">
        {card.portal ? (PORTAL[card.portal] ?? card.portal) : "Advice only"}
      </span>
    </p>
  );
}

/**
 * The deck, with the words Backroom just changed marked when a rebuilt brief swaps the
 * card's text (same story, new wording): the marker sweeps in once under the new words.
 */
function Deck({ text, className }: { text: string; className: string }) {
  const [seen, setSeen] = useState(text);
  const [before, setBefore] = useState<string | null>(null);
  if (seen !== text) {
    // Adjusting state on a prop change during render (React's sanctioned pattern).
    setBefore(seen);
    setSeen(text);
  }
  if (!before) return <p className={className}>{text}</p>;
  let marked = 0;
  return (
    <p className={className}>
      {changedWords(before, text).map((part, i) =>
        part.changed ? (
          <mark key={i} className="marker bg-transparent text-inherit" style={enterDelay(250 + marked++ * 140)}>
            {part.text}
          </mark>
        ) : (
          <span key={i}>{part.text}</span>
        ),
      )}
    </p>
  );
}

/** The recorded run for an approved sample card, when the fixture has one for it. */
function useSampleRun(card: Card, active: boolean): RunEvent[] | null {
  const [run, setRun] = useState<RunEvent[] | null>(null);
  useEffect(() => {
    if (!active) return;
    let live = true;
    void loadSampleRun(card.id).then((events) => {
      if (live) setRun(events);
    });
    return () => {
      live = false;
    };
  }, [active, card.id]);
  return active ? run : null;
}

function Actions({
  card,
  status,
  sample,
  hasRun,
  onApprove,
  onEvidence,
  onReject,
}: {
  card: Card;
  status: CardStatus;
  sample: boolean;
  hasRun: boolean;
  onApprove: () => void;
  onEvidence: () => void;
  onReject: () => void;
}) {
  if (status === "approved") {
    return (
      <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2">
        <p
          role="status"
          className="stamp-in kicker inline-flex h-11 items-center gap-2 border-2 border-pos px-3 text-pos sm:h-10"
        >
          <Check aria-hidden className="size-4" strokeWidth={2.5} />
          Approved
        </p>
        <p className="text-sm text-muted-foreground">
          {sample
            ? hasRun
              ? "Sample brief: replaying the recorded run, no portal touched."
              : "Sample brief: nothing was sent to a portal."
            : `The agent is on it in ${PORTAL[card.portal ?? ""] ?? "the portal"}.`}
        </p>
        <Button size="lg" variant="ghost" onClick={onEvidence}>
          See evidence
        </Button>
      </div>
    );
  }
  const busy = status === "approving";
  return (
    <div className="mt-6 flex flex-wrap items-center gap-2">
      {card.executable ? (
        <Button size="lg" onClick={onApprove} disabled={busy}>
          {busy ? <Loader2 aria-hidden className="animate-spin" /> : null}
          {busy ? "Starting…" : "Approve"}
        </Button>
      ) : null}
      <Button size="lg" variant="outline" onClick={onEvidence}>
        See evidence
      </Button>
      <Button size="lg" variant="ghost" onClick={onReject}>
        Not now
      </Button>
    </div>
  );
}

export function ActionCard({
  card,
  status,
  variant,
  index,
  sample,
  onApprove,
  onReject,
}: {
  card: Card;
  status: CardStatus;
  variant: Variant;
  index: number;
  sample: boolean;
  onApprove: () => void;
  onReject: (reason: string) => Promise<void>;
}) {
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  // Mounted from the first open on, so later closes still animate out.
  const [used, setUsed] = useState({ evidence: false, reject: false });
  const impact = impactNumber(card);
  const lead = variant === "lead";
  const titleId = `${card.id}-title`;
  // The lead is the page's first story (h2); columns sit under "Also in this edition".
  const Heading = lead ? "h2" : "h3";
  const run = useSampleRun(card, sample && status === "approved");

  const actions = (
    <Actions
      card={card}
      status={status}
      sample={sample}
      hasRun={run !== null}
      onApprove={onApprove}
      onEvidence={() => {
        setUsed((u) => ({ ...u, evidence: true }));
        setEvidenceOpen(true);
      }}
      onReject={() => {
        setUsed((u) => ({ ...u, reject: true }));
        setRejectOpen(true);
      }}
    />
  );
  const note = card.preference_note ? (
    <p className="mt-4 flex items-start gap-2 text-sm text-pos">
      <Check aria-hidden className="mt-0.5 size-4 shrink-0" strokeWidth={2.25} />
      {card.preference_note}
    </p>
  ) : null;

  return (
    <article
      aria-labelledby={titleId}
      data-status={status}
      style={enterDelay(index * 80)}
      className={cn("enter", lead && "grid gap-8 lg:grid-cols-12 lg:gap-10")}
    >
      <div className={cn(lead && "lg:col-span-8")}>
        <Kicker card={card} />
        <Heading
          id={titleId}
          className={cn(
            "mt-3 font-display font-medium tracking-[-0.015em] text-ink",
            lead
              ? "text-[2.375rem] leading-[1.02] sm:text-5xl lg:text-[3.5rem]"
              : "text-[1.875rem] leading-[1.08]",
          )}
        >
          {card.title}
        </Heading>
        {!lead ? (
          <p className="mt-3 flex flex-wrap items-baseline gap-x-2">
            <Figure
              value={card.impact_eur_weekly}
              className="font-display text-2xl font-medium text-ink"
            />
            <span className="text-sm text-muted-foreground">
              a week{impact ? ` · ${impact.label.toLowerCase()}` : ""}
            </span>
          </p>
        ) : null}
        <Deck
          text={card.why}
          className={cn(
            "mt-4 max-w-[40rem] font-serif text-ink/85",
            lead ? "text-xl leading-[1.5]" : "text-[1.0625rem] leading-[1.55]",
          )}
        />
        {note}
        {actions}
        {run ? <RunTicker events={run} label="Sample run" /> : null}
      </div>

      {lead ? (
        <aside
          aria-label="The figures"
          className="border-t border-line pt-6 lg:col-span-4 lg:border-t-0 lg:border-l lg:pt-1 lg:pl-10"
        >
          <p className="kicker text-muted-foreground">{impact?.label ?? "Weekly impact"}</p>
          <p className="mt-2 flex items-baseline gap-2">
            <Figure
              value={card.impact_eur_weekly}
              className="font-display text-6xl leading-none font-medium tracking-[-0.02em] text-ink"
            />
          </p>
          <p className="mt-1 text-sm text-muted-foreground">a week</p>
          <dl className="mt-6 border-t border-ink">
            {keyFigures(card).map((n) => (
              <div
                key={n.key}
                className="flex items-baseline gap-2 border-b border-line py-2.5 text-[0.9375rem]"
              >
                <dt className="flex min-w-0 flex-1 items-baseline gap-2 text-muted-foreground">
                  <span className="shrink-0">{n.label}</span>
                  <span aria-hidden className="mb-1 min-w-4 flex-1 border-b border-dotted border-line" />
                </dt>
                <dd className="font-medium text-ink tabular">
                  <FigureValue n={n} />
                </dd>
              </div>
            ))}
          </dl>
        </aside>
      ) : null}

      {used.evidence ? (
        <EvidenceDrawer card={card} open={evidenceOpen} onOpenChange={setEvidenceOpen} />
      ) : null}
      {used.reject ? (
        <RejectDialog
          card={card}
          open={rejectOpen}
          onOpenChange={setRejectOpen}
          onSubmit={onReject}
        />
      ) : null}
    </article>
  );
}
