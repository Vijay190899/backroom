"use client";

import { Check, Loader2, MoveLeft, MoveRight } from "lucide-react";
import { motion, useMotionValue, useSpring, useTransform, type PanInfo } from "motion/react";
import dynamic from "next/dynamic";
import { useEffect, useRef, useState, type PointerEvent } from "react";

import { Figure } from "@/components/motion/figure";
import { CardVisual } from "@/components/today/card-visual";
import { Button } from "@/components/ui/button";
import { absorb, dockPoint } from "@/lib/agent-runs";
import type { ActionCard as Card, EvidenceNumber } from "@/lib/contracts";
import { changedWords } from "@/lib/diff";
import { PORTAL_LABEL as PORTAL } from "@/lib/labels";
import { enterDelay } from "@/lib/motion";
import { motionLevel } from "@/lib/motion-pref";
import { useMotionLevel } from "@/lib/use-motion-level";
import { explodeInto, formFrom } from "@/lib/particles";
import { cn } from "@/lib/utils";

const KIND: Record<Card["kind"], string> = {
  stockout: "Stock",
  margin_erosion: "Margin",
  weather_demand: "Weather",
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

const SWIPE = 120; // px a card must be dragged to count as a decision
const FALL = { type: "spring", stiffness: 170, damping: 17, mass: 0.9 } as const;

function impactNumber(card: Card): EvidenceNumber | undefined {
  return card.numbers.find((n) => n.key === "impact_eur_weekly");
}

/**
 * The card's sentence, with the words Backroom just changed marked when a rebuilt brief
 * swaps the text (same story, new wording): the marker sweeps in once under the new words.
 */
function Deck({ text, className }: { text: string; className: string }) {
  const [seen, setSeen] = useState(text);
  const [before, setBefore] = useState<string | null>(null);
  if (seen !== text) {
    // Adjusting state on a prop change during render (React's sanctioned pattern).
    setBefore(seen);
    setSeen(text);
  }
  if (!before) {
    return (
      <p data-particle-text className={className}>
        {text}
      </p>
    );
  }
  let marked = 0;
  return (
    <p data-particle-text className={className}>
      {changedWords(before, text).map((part, i) =>
        part.changed ? (
          <mark key={i} className="marker bg-transparent text-inherit" style={enterDelay(900 + marked++ * 140)}>
            {part.text}
          </mark>
        ) : (
          <span key={i}>{part.text}</span>
        ),
      )}
    </p>
  );
}

/**
 * One decision as a glass card. It falls into place on a spring, lights up under the
 * cursor and tilts toward it; drag it right to approve or left to skip (the buttons do
 * the same, and calm mode turns dragging off). Approving breaks it into particles that fly into the agent dock; a rebuilt
 * card assembles itself out of particles.
 */
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
  const ref = useRef<HTMLElement>(null);
  const impact = impactNumber(card);
  const lead = variant === "lead";
  const titleId = `${card.candidate_id}-title`;
  // The lead is the page's first card (h2); the others sit under "Also today".
  const Heading = lead ? "h2" : "h3";
  const proposed = status === "proposed";
  const level = useMotionLevel();

  // A rebuilt card (same story, new id) assembles out of particles.
  const [seenId, setSeenId] = useState(card.id);
  const [forming, setForming] = useState(false);
  if (seenId !== card.id) {
    setSeenId(card.id);
    setForming(motionLevel() === "full");
  }
  useEffect(() => {
    if (!forming || !ref.current) return;
    const done = () => setForming(false);
    const started = formFrom(ref.current, { x: innerWidth / 2, y: innerHeight / 2 }, done);
    const fallback = setTimeout(done, started ? 1600 : 0);
    return () => clearTimeout(fallback);
  }, [forming]);

  // Pointer light and tilt.
  const tiltX = useSpring(useMotionValue(0), { stiffness: 180, damping: 18 });
  const tiltY = useSpring(useMotionValue(0), { stiffness: 180, damping: 18 });
  function onPointerMove(e: PointerEvent<HTMLElement>) {
    const el = e.currentTarget;
    // Events from the portalled drawer and dialog bubble here through React; ignore them.
    if (!el.contains(e.target as Node)) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", `${e.clientX - r.left}px`);
    el.style.setProperty("--my", `${e.clientY - r.top}px`);
    el.style.setProperty("--spot", "1");
    if (e.pointerType === "mouse" && motionLevel() === "full") {
      tiltY.set(((e.clientX - r.left) / r.width - 0.5) * 5);
      tiltX.set(-((e.clientY - r.top) / r.height - 0.5) * 5);
    }
  }
  function onPointerLeave(e: PointerEvent<HTMLElement>) {
    e.currentTarget.style.setProperty("--spot", "0");
    tiltX.set(0);
    tiltY.set(0);
  }

  // Drag to decide.
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-240, 240], [-7, 7]);
  const approveHint = useTransform(x, [30, SWIPE], [0, 1]);
  const skipHint = useTransform(x, [-SWIPE, -30], [1, 0]);

  function approve() {
    try {
      if (ref.current && motionLevel() === "full") explodeInto(ref.current, dockPoint(), absorb);
    } catch {
      // The effect is decoration: approving must never depend on it.
    }
    onApprove();
  }
  function openReject() {
    setUsed((u) => ({ ...u, reject: true }));
    setRejectOpen(true);
  }
  function onDragEnd(_: unknown, info: PanInfo) {
    if (info.offset.x > SWIPE && card.executable) approve();
    else if (info.offset.x < -SWIPE) openReject();
  }

  const dialogs = (
    <>
      {used.evidence ? <EvidenceDrawer card={card} open={evidenceOpen} onOpenChange={setEvidenceOpen} /> : null}
      {used.reject ? (
        <RejectDialog card={card} open={rejectOpen} onOpenChange={setRejectOpen} onSubmit={onReject} />
      ) : null}
    </>
  );
  const openEvidence = () => {
    setUsed((u) => ({ ...u, evidence: true }));
    setEvidenceOpen(true);
  };

  if (status === "approved") {
    return (
      <motion.article
        layout
        aria-labelledby={titleId}
        data-status={status}
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ ...FALL, delay: motionLevel() === "full" ? 0.35 : 0 }}
        className="glass flex flex-wrap items-center gap-x-4 gap-y-2 rounded-2xl px-5 py-4"
      >
        <span className="grid size-8 shrink-0 place-items-center rounded-full bg-pos/15 text-pos">
          <Check aria-hidden className="size-4" strokeWidth={2.5} />
        </span>
        <div className="min-w-0 flex-1">
          <Heading id={titleId} className="truncate font-medium text-ink">
            {card.title}
          </Heading>
          <p role="status" className="text-sm text-muted-foreground">
            Approved ·{" "}
            {sample
              ? "sample brief, no portal touched"
              : `the agent is on it in ${PORTAL[card.portal ?? ""] ?? "the portal"}`}
          </p>
        </div>
        <Button size="lg" variant="ghost" onClick={openEvidence}>
          See evidence
        </Button>
        {dialogs}
      </motion.article>
    );
  }

  return (
    <div className="relative [perspective:1200px]">
      {/* What a drag will do, revealed behind the card as it moves. */}
      {card.executable ? (
        <motion.p
          aria-hidden
          style={{ opacity: approveHint }}
          className="absolute inset-y-0 left-6 flex items-center gap-2 text-sm font-medium text-pos"
        >
          Approve <MoveRight className="size-4" />
        </motion.p>
      ) : null}
      <motion.p
        aria-hidden
        style={{ opacity: skipHint }}
        className="absolute inset-y-0 right-6 flex items-center gap-2 text-sm font-medium text-muted-foreground"
      >
        <MoveLeft className="size-4" /> Not now
      </motion.p>

      <motion.article
        ref={ref}
        layout="position"
        aria-labelledby={titleId}
        data-status={status}
        initial={{ opacity: 0, y: -60, scale: 0.94 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ ...FALL, delay: 0.15 + index * 0.12 }}
        style={{ x, rotate, rotateX: tiltX, rotateY: tiltY }}
        drag={proposed && level === "full" ? "x" : false}
        dragDirectionLock
        dragSnapToOrigin
        dragElastic={1}
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={onDragEnd}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
        whileDrag={{ scale: 1.02, cursor: "grabbing" }}
        className={cn(
          "glass spotlight touch-pan-y rounded-[var(--t-radius-card)] p-6 sm:p-8",
          lead && "grid gap-8 lg:grid-cols-12 lg:gap-10",
        )}
      >
        <div
          className={cn("transition-opacity duration-300", forming && "opacity-0", lead && "lg:col-span-7")}
        >
          <p className="flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full bg-press/15 px-2.5 py-1 font-medium text-press-ink">{KIND[card.kind]}</span>
            <span className="rounded-full border border-glass-line px-2.5 py-1 text-muted-foreground" translate="no">
              {card.portal ? (PORTAL[card.portal] ?? card.portal) : "Advice only"}
            </span>
          </p>
          <Heading
            id={titleId}
            data-particle-text
            className={cn(
              "mt-4 font-semibold tracking-[-0.035em] text-ink",
              lead ? "text-4xl leading-[1.02] sm:text-5xl" : "text-[1.75rem] leading-[1.08]",
            )}
          >
            {card.title}
          </Heading>
          {!lead ? (
            <p className="mt-3 flex flex-wrap items-baseline gap-x-2">
              <Figure value={card.impact_eur_weekly} className="text-2xl font-semibold tracking-tight text-ink" />
              <span className="text-sm text-muted-foreground">
                a week{impact ? ` · ${impact.label.toLowerCase()}` : ""}
              </span>
            </p>
          ) : null}
          <Deck
            text={card.why}
            className={cn("mt-4 max-w-[40rem] text-muted-foreground", lead ? "text-lg leading-relaxed" : "leading-relaxed")}
          />
          {card.preference_note ? (
            <p className="mt-4 flex items-start gap-2 text-sm text-pos">
              <Check aria-hidden className="mt-0.5 size-4 shrink-0" strokeWidth={2.25} />
              {card.preference_note}
            </p>
          ) : null}
          {!lead ? (
            <div className="mt-6">
              <CardVisual card={card} />
            </div>
          ) : null}

          <div className="mt-6 flex flex-wrap items-center gap-2">
            {card.executable ? (
              <Button size="lg" onClick={approve} disabled={status === "approving"}>
                {status === "approving" ? <Loader2 aria-hidden className="animate-spin" /> : null}
                {status === "approving" ? "Starting…" : "Approve"}
              </Button>
            ) : null}
            <Button size="lg" variant="outline" onClick={openEvidence}>
              See evidence
            </Button>
            <Button size="lg" variant="ghost" onClick={openReject}>
              Not now
            </Button>
          </div>
        </div>

        {lead ? (
          <aside
            aria-label="The figures"
            className={cn("transition-opacity duration-300 lg:col-span-5", forming && "opacity-0")}
          >
            <p className="text-sm text-muted-foreground">{impact?.label ?? "Weekly impact"}</p>
            <p className="mt-1 flex items-baseline gap-2">
              <Figure
                value={card.impact_eur_weekly}
                className="text-6xl leading-none text-press-ink font-semibold tracking-[-0.04em] sm:text-7xl"
              />
              <span className="text-sm text-muted-foreground">a week</span>
            </p>
            <div className="mt-8">
              <CardVisual card={card} />
            </div>
          </aside>
        ) : null}
        {dialogs}
      </motion.article>
    </div>
  );
}
