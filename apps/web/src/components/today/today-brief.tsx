"use client";

import { FlaskConical, ListChecks, Sunrise } from "lucide-react";
import { useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { ActionCard, type CardStatus } from "@/components/today/action-card";
import { Button } from "@/components/ui/button";
import { approve, reject, sampleAfterReject, useBrief, type LoadedBrief } from "@/lib/brief";
import type { ActionCard as Card } from "@/lib/contracts";
import { formatDay } from "@/lib/format";

function CardSkeleton({ index }: { index: number }) {
  return (
    <div
      aria-hidden
      style={{ animationDelay: `${index * 70}ms` }}
      className="h-56 animate-pulse rounded-[var(--t-radius-card)] border border-line bg-surface"
    />
  );
}

export function TodayBrief() {
  const query = useBrief();
  // A sample brief rebuilt locally after a rejection replaces what the query loaded.
  const [regenerated, setRegenerated] = useState<LoadedBrief | null>(null);
  const [status, setStatus] = useState<Record<string, CardStatus>>({});
  const [message, setMessage] = useState("");
  const loaded = regenerated ?? query.data ?? null;

  if (!loaded) {
    return (
      <>
        <PageHeader title="Today" subtitle="Reading the till, the invoices and the weather…" />
        <div className="grid gap-4" role="status" aria-label="Loading the brief">
          {[0, 1, 2].map((i) => (
            <CardSkeleton key={i} index={i} />
          ))}
        </div>
      </>
    );
  }

  const { brief, source } = loaded;
  const sample = source === "sample";
  const visible = brief.cards.filter((c) => status[c.id] !== "rejected");
  const pending = visible.filter((c) => c.executable && (status[c.id] ?? "proposed") === "proposed");

  function setOne(id: string, value: CardStatus) {
    setStatus((s) => ({ ...s, [id]: value }));
  }

  async function approveOne(card: Card) {
    setOne(card.id, "approving");
    if (sample) {
      setOne(card.id, "approved");
      setMessage(`${card.title}: approved (sample brief, no portal was touched).`);
      return;
    }
    try {
      await approve(brief, card);
      setOne(card.id, "approved");
      setMessage(`${card.title}: approved, the agent is on it.`);
    } catch {
      setOne(card.id, "proposed");
      setMessage(`${card.title}: couldn't start. Try again.`);
    }
  }

  async function approveAll() {
    for (const card of pending) {
      await approveOne(card);
    }
  }

  async function rejectOne(card: Card, reason: string) {
    if (sample) {
      const rebuilt = sampleAfterReject(card, reason);
      if (rebuilt) {
        setRegenerated({ brief: rebuilt, source: "sample" });
        setStatus({});
        setMessage("Noted. The brief was rebuilt with your rule.");
      } else {
        setOne(card.id, "rejected");
        setMessage(`${card.title}: skipped. Backroom will remember why.`);
      }
      return;
    }
    await reject(card, reason);
    setOne(card.id, "rejected");
    setMessage("Noted. Backroom will remember why.");
    void query.refetch();
  }

  return (
    <>
      <PageHeader
        title="Today"
        subtitle={`${formatDay(brief.as_of)} · what matters for Hafer & Bohne, with the money behind each one.`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {sample ? (
              <span
                className="inline-flex h-9 items-center gap-1.5 rounded-full border border-line px-3 text-sm text-muted-foreground"
                title="The API has no brief yet, so this is the committed sample. Nothing here touches a portal."
              >
                <FlaskConical aria-hidden className="size-4" />
                Sample brief
              </span>
            ) : null}
            {pending.length > 1 ? (
              <Button size="lg" className="px-4" onClick={approveAll}>
                <ListChecks aria-hidden />
                Approve all
              </Button>
            ) : null}
          </div>
        }
      />

      <p role="status" aria-live="polite" className="sr-only">
        {message}
      </p>

      {visible.length === 0 ? (
        <EmptyState
          icon={Sunrise}
          title="Nothing needs you today"
          body="Backroom checked stock, margins and the forecast. When something is worth your time, it shows up here with the money behind it."
        />
      ) : (
        <div className="grid gap-4">
          {visible.map((card, i) => (
            <ActionCard
              key={card.id}
              card={card}
              index={i}
              status={status[card.id] ?? "proposed"}
              onApprove={() => void approveOne(card)}
              onReject={(reason) => rejectOne(card, reason)}
            />
          ))}
        </div>
      )}
      {message ? (
        <p aria-hidden className="mt-4 text-sm text-muted-foreground">
          {message}
        </p>
      ) : null}
    </>
  );
}
