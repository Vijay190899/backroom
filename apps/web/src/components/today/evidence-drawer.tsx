"use client";

import { Dialog } from "@base-ui/react/dialog";
import { BarChart3, Database, FileText, ReceiptText, ShieldCheck, X } from "lucide-react";

import type { ActionCard, Evidence } from "@/lib/contracts";
import { displayNumber } from "@/lib/format";
import { cn } from "@/lib/utils";

const KIND_ICON = { sql: Database, fact: FileText, chart: BarChart3, invoice: ReceiptText };
const KIND_LABEL = { sql: "Query", fact: "Memory fact", chart: "Chart data", invoice: "Invoice" };

function SyntheticChip() {
  return (
    <span className="rounded-full border border-line px-2 py-0.5 font-mono text-[0.7rem] text-muted-foreground">
      Synthetic
    </span>
  );
}

function EvidenceItem({ item }: { item: Evidence }) {
  const Icon = KIND_ICON[item.kind];
  return (
    <section className="rounded-xl border border-line bg-background/60 p-4">
      <header className="flex flex-wrap items-center gap-2">
        <Icon aria-hidden className="size-4 text-caramel-ink" strokeWidth={1.75} />
        <span className="text-xs uppercase tracking-wide text-muted-foreground">
          {KIND_LABEL[item.kind]}
        </span>
        {item.synthetic ? <SyntheticChip /> : null}
      </header>
      <h4 className="mt-2 font-medium text-ink">{item.label}</h4>
      {item.columns.length > 0 && item.rows.length > 0 ? (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-sm tabular">
            <thead>
              <tr className="border-b border-line text-left text-muted-foreground">
                {item.columns.map((c) => (
                  <th key={c} scope="col" className="py-1.5 pr-4 font-normal">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {item.rows.map((row, i) => (
                <tr key={i} className="border-b border-line/60 last:border-0">
                  {row.map((cell, j) => (
                    <td key={j} className="py-1.5 pr-4 text-ink">
                      {String(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      {item.sql ? (
        <details className="mt-3 group">
          <summary className="cursor-pointer text-sm text-caramel-ink select-none">
            Show the query
          </summary>
          <pre className="mt-2 overflow-x-auto rounded-lg bg-subtle p-3 font-mono text-xs leading-relaxed text-ink">
            {item.sql}
          </pre>
        </details>
      ) : null}
    </section>
  );
}

export function EvidenceDrawer({
  card,
  open,
  onOpenChange,
}: {
  card: ActionCard;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const guard = card.guard;
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/30 transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup
          className={cn(
            "fixed z-50 flex flex-col overflow-hidden border-line bg-surface shadow-xl outline-none",
            "inset-x-0 bottom-0 max-h-[88dvh] rounded-t-[var(--t-radius-card)] border-t",
            "sm:inset-y-0 sm:right-0 sm:left-auto sm:max-h-none sm:w-[30rem] sm:rounded-none sm:border-t-0 sm:border-l",
            "transition-transform duration-[240ms] ease-[var(--t-ease-out)]",
            "data-[ending-style]:translate-y-full data-[starting-style]:translate-y-full",
            "sm:data-[ending-style]:translate-x-full sm:data-[ending-style]:translate-y-0",
            "sm:data-[starting-style]:translate-x-full sm:data-[starting-style]:translate-y-0",
          )}
        >
          <header className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Evidence</p>
              <Dialog.Title className="mt-1 font-display text-2xl leading-tight text-ink">
                {card.title}
              </Dialog.Title>
            </div>
            <Dialog.Close
              aria-label="Close evidence"
              className="-mr-2 rounded-lg p-2 text-muted-foreground hover:bg-subtle hover:text-ink"
            >
              <X aria-hidden className="size-5" />
            </Dialog.Close>
          </header>

          <div className="flex-1 space-y-5 overflow-y-auto px-5 py-5">
            <Dialog.Description className="flex items-start gap-2 rounded-xl bg-subtle px-3 py-2.5 text-sm text-ink">
              <ShieldCheck aria-hidden className="mt-0.5 size-4 shrink-0 text-pos" />
              <span>
                Every number on this card was computed by code from the data below
                {guard.passed
                  ? guard.regenerations
                    ? ", and the AI-written text was checked against them after one rewrite."
                    : ", and the AI-written text was checked against them."
                  : "; the AI-written text didn't match, so the card shows template text instead."}
              </span>
            </Dialog.Description>

            <section>
              <h3 className="text-sm font-medium text-ink">The numbers</h3>
              <dl className="mt-2 divide-y divide-line rounded-xl border border-line">
                {card.numbers.map((n) => (
                  <div key={n.key} className="flex items-baseline justify-between gap-4 px-3 py-2">
                    <dt className="text-sm text-muted-foreground">{n.label}</dt>
                    <dd className="font-medium text-ink tabular">{displayNumber(n)}</dd>
                  </div>
                ))}
              </dl>
            </section>

            <section className="space-y-3">
              <h3 className="text-sm font-medium text-ink">Where they come from</h3>
              {card.evidence.map((item) => (
                <EvidenceItem key={item.id} item={item} />
              ))}
            </section>
          </div>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
