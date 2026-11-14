"use client";

import { Dialog } from "@base-ui/react/dialog";
import { BarChart3, Database, FileText, ReceiptText, ShieldCheck, X } from "lucide-react";

import type { ActionCard, Evidence } from "@/lib/contracts";
import { displayFigure } from "@/lib/format";
import { cn } from "@/lib/utils";

const KIND_ICON = { sql: Database, fact: FileText, chart: BarChart3, invoice: ReceiptText };
const KIND_LABEL = { sql: "Query", fact: "Memory fact", chart: "Chart data", invoice: "Invoice" };

function SyntheticChip() {
  return (
    <span className="kicker border border-dashed border-ink/30 px-1.5 py-0.5 text-[0.625rem] text-muted-foreground">
      Synthetic
    </span>
  );
}

function EvidenceItem({ item, index }: { item: Evidence; index: number }) {
  const Icon = KIND_ICON[item.kind];
  return (
    <section className="border-t border-line py-5 first:border-t-0 first:pt-0">
      <header className="flex flex-wrap items-center gap-2">
        <span className="font-display text-sm text-press-ink tabular">{index + 1}.</span>
        <Icon aria-hidden className="size-3.5 text-press-ink" strokeWidth={1.75} />
        <span className="kicker text-muted-foreground">{KIND_LABEL[item.kind]}</span>
        {item.synthetic ? <SyntheticChip /> : null}
      </header>
      <h4 className="mt-2 font-serif text-lg leading-snug text-ink">{item.label}</h4>
      {item.columns.length > 0 && item.rows.length > 0 ? (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full font-mono text-[0.8125rem] tabular">
            <thead>
              <tr className="border-b border-ink text-left text-muted-foreground">
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
          <summary className="link-draw inline-flex min-h-11 cursor-pointer items-center text-sm text-press-ink select-none sm:min-h-0">
            Show the query
          </summary>
          <pre className="mt-2 overflow-x-auto rounded-sm border-l-2 border-press bg-subtle p-3 font-mono text-xs leading-relaxed text-ink">
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
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/35 transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup
          className={cn(
            "fixed z-50 flex flex-col overflow-hidden overscroll-contain border-line bg-surface shadow-[0_0_0_1px_rgb(0_0_0/0.04),0_24px_48px_-12px_rgb(0_0_0/0.25)] outline-none",
            "inset-x-0 bottom-0 max-h-[88dvh] rounded-t-[var(--t-radius-card)] border-t pb-[env(safe-area-inset-bottom)]",
            "sm:inset-y-0 sm:right-0 sm:left-auto sm:max-h-none sm:w-[32rem] sm:rounded-none sm:border-t-0 sm:border-l",
            "transition-transform duration-[240ms] ease-[var(--t-ease-out)]",
            "data-[ending-style]:translate-y-full data-[starting-style]:translate-y-full",
            "sm:data-[ending-style]:translate-x-full sm:data-[ending-style]:translate-y-0",
            "sm:data-[starting-style]:translate-x-full sm:data-[starting-style]:translate-y-0",
          )}
        >
          <header className="flex items-start justify-between gap-4 px-6 pt-6">
            <div>
              <p className="kicker text-press-ink">Evidence</p>
              <Dialog.Title className="mt-2 font-display text-3xl leading-[1.08] font-medium tracking-tight text-ink">
                {card.title}
              </Dialog.Title>
            </div>
            <Dialog.Close
              aria-label="Close evidence"
              className="-mt-1 -mr-3 inline-flex size-11 cursor-pointer items-center justify-center rounded-md text-muted-foreground transition-colors duration-150 hover:bg-subtle hover:text-ink"
            >
              <X aria-hidden className="size-5" />
            </Dialog.Close>
          </header>

          <div aria-hidden className="rule-double mx-6 mt-4" />
          <div className="flex-1 space-y-8 overflow-y-auto overscroll-contain px-6 py-6">
            <Dialog.Description
              className={cn(
                "flex items-start gap-3 border px-4 py-3 text-sm leading-relaxed text-ink",
                guard.passed ? "border-pos/40 bg-pos/[0.06]" : "border-line bg-subtle",
              )}
            >
              <ShieldCheck
                aria-hidden
                className={cn("mt-0.5 size-4 shrink-0", guard.passed ? "text-pos" : "text-muted-foreground")}
              />
              {guard.passed ? (
                <span>
                  <strong className="font-semibold">Fact-checked.</strong> Every number on this
                  card was computed by code from the data below, and the AI-written text was
                  checked against them{guard.regenerations ? " after one rewrite" : ""}.
                </span>
              ) : (
                <span>
                  <strong className="font-semibold">Plain wording.</strong> Every number on this
                  card was computed by code from the data below. The AI-written text didn&rsquo;t
                  match them, so the card uses template text built from the same numbers.
                </span>
              )}
            </Dialog.Description>

            <section>
              <h3 className="kicker text-ink">The numbers</h3>
              <dl className="mt-3 border-t border-ink">
                {card.numbers.map((n) => (
                  <div key={n.key} className="flex items-baseline gap-2 border-b border-line py-2.5">
                    <dt className="flex min-w-0 flex-1 items-baseline gap-2 text-[0.9375rem] text-muted-foreground">
                      <span className="min-w-0">{n.label}</span>
                      <span aria-hidden className="mb-1 min-w-4 flex-1 border-b border-dotted border-line" />
                    </dt>
                    <dd className="shrink-0 font-medium text-ink tabular">{displayFigure(n)}</dd>
                  </div>
                ))}
              </dl>
            </section>

            <section>
              <h3 className="kicker text-ink">Where they come from</h3>
              <div className="mt-3 border-t border-ink pt-5">
                {card.evidence.map((item, i) => (
                  <EvidenceItem key={item.id} item={item} index={i} />
                ))}
              </div>
            </section>
          </div>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
