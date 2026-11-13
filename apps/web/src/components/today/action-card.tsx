"use client";

import {
  CheckCircle2,
  CloudRain,
  Loader2,
  PackageOpen,
  Percent,
  ShieldCheck,
  Store,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";

import { EvidenceDrawer } from "@/components/today/evidence-drawer";
import { RejectDialog } from "@/components/today/reject-dialog";
import { Button } from "@/components/ui/button";
import type { ActionCard as Card } from "@/lib/contracts";
import { formatEur } from "@/lib/format";
import { cn } from "@/lib/utils";

const KIND: Record<Card["kind"], { icon: LucideIcon; label: string }> = {
  stockout: { icon: PackageOpen, label: "Stock" },
  margin_erosion: { icon: Percent, label: "Margin" },
  weather_demand: { icon: CloudRain, label: "Weather" },
};
const PORTAL: Record<string, string> = {
  grainline: "Grainline",
  tilldesk: "TillDesk",
  localboard: "Localboard",
};

export type CardStatus = "proposed" | "approving" | "approved" | "rejected";

export function ActionCard({
  card,
  status,
  index,
  onApprove,
  onReject,
}: {
  card: Card;
  status: CardStatus;
  index: number;
  onApprove: () => void;
  onReject: (reason: string) => Promise<void>;
}) {
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const kind = KIND[card.kind];
  const Icon = kind.icon;
  const done = status === "approved";

  return (
    <article
      aria-labelledby={`${card.id}-title`}
      style={{ animationDelay: `${index * 70}ms` }}
      className={cn(
        "animate-in fade-in-0 slide-in-from-bottom-2 fill-mode-both duration-300",
        "rounded-[var(--t-radius-card)] border border-line bg-surface p-5 sm:p-6",
        done && "border-pos/40",
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-subtle px-2.5 py-1 text-ink">
            <Icon aria-hidden className="size-3.5 text-caramel-ink" strokeWidth={2} />
            {kind.label}
          </span>
          {card.portal ? (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-line px-2.5 py-1">
              <Store aria-hidden className="size-3.5" strokeWidth={1.75} />
              {PORTAL[card.portal] ?? card.portal}
            </span>
          ) : (
            <span className="rounded-full border border-dashed border-line px-2.5 py-1">
              Recommendation
            </span>
          )}
        </div>
        <p className="shrink-0 text-right">
          <span className="block font-display text-3xl leading-none text-ink tabular sm:text-4xl">
            {formatEur(card.impact_eur_weekly)}
          </span>
          <span className="mt-1 block text-xs text-muted-foreground">a week</span>
        </p>
      </div>

      <h2 id={`${card.id}-title`} className="mt-4 font-display text-2xl leading-tight text-ink">
        {card.title}
      </h2>
      <p className="mt-2 max-w-prose text-[0.95rem] leading-relaxed text-muted-foreground">
        {card.why}
      </p>

      {card.preference_note ? (
        <p className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-pos/10 px-2.5 py-1 text-sm text-pos">
          <CheckCircle2 aria-hidden className="size-4" />
          {card.preference_note}
        </p>
      ) : null}

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {done ? (
          <span role="status" className="inline-flex h-9 items-center gap-2 text-sm text-pos">
            <CheckCircle2 aria-hidden className="size-4" />
            Approved
          </span>
        ) : card.executable ? (
          <Button size="lg" className="px-4" onClick={onApprove} disabled={status === "approving"}>
            {status === "approving" ? (
              <Loader2 aria-hidden className="animate-spin" />
            ) : null}
            {status === "approving" ? "Starting…" : "Approve"}
          </Button>
        ) : null}
        <Button size="lg" variant="outline" className="px-4" onClick={() => setEvidenceOpen(true)}>
          <ShieldCheck aria-hidden />
          Review
        </Button>
        {!done ? (
          <Button size="lg" variant="ghost" className="px-4" onClick={() => setRejectOpen(true)}>
            Not now
          </Button>
        ) : null}
      </div>

      <EvidenceDrawer card={card} open={evidenceOpen} onOpenChange={setEvidenceOpen} />
      <RejectDialog
        card={card}
        open={rejectOpen}
        onOpenChange={setRejectOpen}
        onSubmit={onReject}
      />
    </article>
  );
}
