"use client";

import { ListChecks, Loader2, Sunrise } from "lucide-react";
import { startTransition, useEffect, useMemo, useRef, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { BadgeSlot, SampleBadge } from "@/components/sample-badge";
import { ActionCard, type CardStatus } from "@/components/today/action-card";
import { Button } from "@/components/ui/button";
import { approve, reject, sampleAfterReject, useBrief, type LoadedBrief } from "@/lib/brief";
import type { ActionCard as Card } from "@/lib/contracts";
import { formatDateline, formatTime } from "@/lib/format";
import { PORTAL_LABEL } from "@/lib/labels";
import { loadSampleRun } from "@/lib/runs";
import { startRun } from "@/lib/agent-runs";
import { deliver } from "@/lib/scene";
import { useRegisterCommands, type Command } from "@/lib/commands";

const PLACE = "Hafer & Bohne · Bonn-Südstadt";
const COUNT_WORDS = ["No", "One", "Two", "Three", "Four", "Five", "Six"];

function decisions(n: number): string {
  const word = COUNT_WORDS[n] ?? String(n);
  return `${word} ${n === 1 ? "decision needs" : "decisions need"} you this morning.`;
}

/** Mirrors the loaded page (lead + two columns) so nothing shifts when the brief arrives. */
function BriefSkeleton() {
  const bar = "animate-pulse bg-subtle";
  return (
    <div role="status" aria-label="Loading the brief">
      <div className="grid gap-8 lg:grid-cols-12 lg:gap-10">
        <div className="space-y-4 lg:col-span-8">
          <div className={`${bar} h-3 w-32`} />
          <div className={`${bar} h-12 w-4/5`} />
          <div className={`${bar} h-5 w-full`} />
          <div className={`${bar} h-5 w-3/4`} />
        </div>
        <div className="space-y-3 border-t border-line pt-6 lg:col-span-4 lg:border-t-0 lg:border-l lg:pt-1 lg:pl-10">
          <div className={`${bar} h-3 w-24`} />
          <div className={`${bar} h-14 w-40`} />
        </div>
      </div>
      <div className="mt-12 grid gap-10 border-t border-line pt-8 sm:grid-cols-2">
        {[0, 1].map((i) => (
          <div key={i} className="space-y-3">
            <div className={`${bar} h-3 w-24`} />
            <div className={`${bar} h-8 w-3/4`} />
            <div className={`${bar} h-4 w-full`} />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Puts "Approve …" for each pending card into the ⌘K palette while the brief is shown. */
function BriefCommands({ pending, onApprove }: { pending: Card[]; onApprove: (card: Card) => void }) {
  const latest = useRef(onApprove);
  useEffect(() => {
    latest.current = onApprove;
  });
  const commands = useMemo<Command[]>(
    () =>
      pending.map((card) => ({
        id: `approve:${card.id}`,
        group: "Approve",
        label: card.title,
        run: () => latest.current(card),
      })),
    [pending],
  );
  useRegisterCommands("brief", commands);
  return null;
}

export function TodayBrief() {
  const query = useBrief();
  // A sample brief rebuilt locally after a rejection replaces what the query loaded.
  const [regenerated, setRegenerated] = useState<LoadedBrief | null>(null);
  const [status, setStatus] = useState<Record<string, CardStatus>>({});
  const [message, setMessage] = useState("");
  const [approvingAll, setApprovingAll] = useState(false);
  const loaded = regenerated ?? query.data ?? null;

  if (!loaded && query.isError) {
    // Only a failed code-chunk load gets here: an API error already falls back to the sample.
    return (
      <>
        <PageHeader kicker={PLACE} title="The Morning Brief" />
        <div role="alert" className="border-y border-line py-12 text-center">
          <p className="font-display text-2xl text-ink">The brief didn&rsquo;t load.</p>
          <p className="mt-2 text-muted-foreground">Check the connection, then try again.</p>
          <Button size="lg" className="mt-6" onClick={() => void query.refetch()}>
            Try again
          </Button>
        </div>
      </>
    );
  }

  if (!loaded) {
    return (
      <>
        <PageHeader
          kicker={PLACE}
          title="The Morning Brief"
          subtitle="Reading the till, the invoices and the forecast…"
          actions={<BadgeSlot />}
        />
        <BriefSkeleton />
      </>
    );
  }

  const { brief, source } = loaded;
  const sample = source === "sample";
  const visible = brief.cards
    .filter((c) => status[c.id] !== "rejected")
    .sort((a, b) => a.rank - b.rank);
  const pending = visible.filter((c) => c.executable && (status[c.id] ?? "proposed") === "proposed");
  const [lead, ...rest] = visible;
  const open = visible.filter((c) => (status[c.id] ?? "proposed") !== "approved");

  function setOne(id: string, value: CardStatus) {
    setStatus((s) => ({ ...s, [id]: value }));
  }

  async function approveOne(card: Card) {
    setOne(card.id, "approving");
    const portal = card.portal ? (PORTAL_LABEL[card.portal] ?? card.portal) : null;
    // An approved supplier order sends a delivery van to the café scene.
    const delivery = () => card.portal === "grainline" && deliver();
    if (sample) {
      setOne(card.id, "approved");
      delivery();
      setMessage(`${card.title}: approved (sample brief, no portal was touched).`);
      // The dock plays the recorded sample run when the fixture has one for this card.
      const events = await loadSampleRun(card.id).catch(() => null);
      startRun({
        id: card.id,
        title: card.title,
        portal,
        events,
        note: `${card.title}: approved · no recorded run in the sample`,
        href: events?.[0] ? `/runs/${events[0].run_id}` : null,
      });
      return;
    }
    try {
      const { run_id } = await approve(brief, card);
      delivery();
      startRun({
        id: card.id,
        title: card.title,
        portal,
        events: null,
        note: `${card.title}: the agent has started`,
        href: `/runs/${encodeURIComponent(run_id)}`,
      });
      setOne(card.id, "approved");
      setMessage(`${card.title}: approved, the agent is on it.`);
    } catch {
      setOne(card.id, "proposed");
      setMessage(`${card.title}: couldn't start. Try again.`);
    }
  }

  async function approveAll() {
    setApprovingAll(true);
    try {
      for (const card of pending) {
        await approveOne(card);
      }
    } finally {
      setApprovingAll(false);
    }
  }

  // The rejected card (and its open dialog) unmounts; give focus a place to land.
  function refocus() {
    requestAnimationFrame(() => document.getElementById("main")?.focus());
  }

  async function rejectOne(card: Card, reason: string) {
    if (sample) {
      const rebuilt = await sampleAfterReject(card, reason);
      // Transitions, so the stories animate: a rebuilt card stays the same story (its
      // figures roll, its new words are marked); a skipped one leaves and the rest close up.
      startTransition(() => {
        if (rebuilt) {
          setRegenerated({ brief: rebuilt, source: "sample" });
          // Cards that survive the rebuild keep their state (an approved card's run keeps playing).
          const kept = new Set(rebuilt.cards.map((c) => c.id));
          setStatus((st) => Object.fromEntries(Object.entries(st).filter(([id]) => kept.has(id))));
          setMessage("Noted. The brief was rebuilt with your rule.");
        } else {
          setOne(card.id, "rejected");
          setMessage(`${card.title}: skipped. Backroom will remember why.`);
        }
      });
      refocus();
      return;
    }
    await reject(card, reason);
    startTransition(() => {
      setOne(card.id, "rejected");
      setMessage("Noted. Backroom will remember why.");
    });
    refocus();
    void query.refetch();
  }

  // Identity is the candidate (stock-out of oat milk, margin of Franzbrötchen…), not the
  // card id, which changes when a rebuilt brief re-prices the same story.
  const story = (card: Card, variant: "lead" | "column", index: number) => (
    <ActionCard
      key={card.candidate_id}
      card={card}
      variant={variant}
      index={index}
      sample={sample}
      status={status[card.id] ?? "proposed"}
      onApprove={() => void approveOne(card)}
      onReject={(reason) => rejectOne(card, reason)}
    />
  );
  return (
    <>
      <PageHeader
        kicker={PLACE}
        meta={formatDateline(brief.as_of)}
        title="The Morning Brief"
        subtitle={decisions(open.length)}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {sample ? (
              <SampleBadge
                label="Sample brief"
                why="The API has no brief yet, so this is the committed sample. Nothing here touches a portal."
              />
            ) : null}
            {pending.length > 1 ? (
              <Button size="lg" onClick={approveAll} disabled={approvingAll}>
                {approvingAll ? <Loader2 aria-hidden className="animate-spin" /> : <ListChecks aria-hidden />}
                Approve all {pending.length}
              </Button>
            ) : null}
          </div>
        }
      />

      <p role="status" aria-live="polite" className="sr-only">
        {message}
      </p>
      <BriefCommands pending={pending} onApprove={(card) => void approveOne(card)} />

      {!lead ? (
        <EmptyState
          icon={Sunrise}
          title="Nothing needs you today"
          body="Backroom checked stock, margins and the forecast. When something is worth your time, it shows up here with the money behind it."
        />
      ) : (
        <>
          {story(lead, "lead", 0)}
          {rest.length > 0 ? (
            <section aria-labelledby="also-heading" className="mt-10">
              <h2 id="also-heading" className="kicker text-muted-foreground">
                Also today
              </h2>
              <div className="mt-4 grid items-start gap-5 md:grid-cols-2">
                {rest.map((card, i) => story(card, "column", i + 1))}
              </div>
            </section>
          ) : null}
        </>
      )}

      {message ? (
        <p aria-hidden className="mt-10 text-sm text-muted-foreground">
          {message}
        </p>
      ) : null}

      <footer className="mt-16 border-t border-line pt-4 text-sm leading-relaxed text-muted-foreground">
        <p className="max-w-3xl">
          Prepared at {formatTime(brief.generated_at)} from the till, the invoices and the
          forecast. Every figure here was computed by code, and the words around them were
          checked against those figures before you saw them; where they didn&rsquo;t match,
          plain template text stands in.
        </p>
      </footer>
    </>
  );
}
