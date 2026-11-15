"use client";

import { motion } from "motion/react";

import type { ActionCard, EvidenceNumber } from "@/lib/contracts";
import { displayFigure } from "@/lib/format";
import { useMotionLevel } from "@/lib/use-motion-level";

const plain = new Intl.NumberFormat("en-IE", { maximumFractionDigits: 1 });

const SPRING = { type: "spring", stiffness: 90, damping: 14 } as const;

function num(card: ActionCard, key: string): EvidenceNumber | undefined {
  return card.numbers.find((n) => n.key === key);
}

/**
 * Margin on a scale: the dot falls from where the margin was to where it is now (below
 * the dashed target), then an ember dot springs up to where the proposed price puts it.
 */
function MarginScale({ card }: { card: ActionCard }) {
  const before = num(card, "margin_before_pct");
  const now = num(card, "margin_after_pct");
  const target = num(card, "margin_target_pct");
  const next = num(card, "margin_new_pct");
  if (!before || !now || !target) return null;
  const values = [before.value, now.value, target.value, ...(next ? [next.value] : [])];
  const lo = Math.min(...values) - 2;
  const hi = Math.max(...values) + 2;
  const x = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`;
  return (
    <div className="relative h-24">
      <div className="absolute inset-x-0 top-12 h-px bg-glass-line" />
      <div className="absolute top-3 bottom-6 w-px border-l border-dashed border-muted-foreground/60" style={{ left: x(target.value) }} />
      <span className="absolute top-0 -translate-x-1/2 text-[11px] whitespace-nowrap text-muted-foreground" style={{ left: x(target.value) }}>
        target {displayFigure(target)}
      </span>
      <motion.span
        aria-hidden
        className="absolute top-12 size-3 -translate-1/2 rounded-full bg-muted-foreground"
        initial={{ left: x(before.value) }}
        animate={{ left: x(now.value) }}
        transition={{ ...SPRING, delay: 0.5 }}
      />
      <span className="absolute top-[3.75rem] -translate-x-1/2 text-xs whitespace-nowrap text-ink tabular" style={{ left: x(now.value) }}>
        now {displayFigure(now)}
      </span>
      {next ? (
        <>
          <motion.span
            aria-hidden
            className="absolute top-12 size-3.5 -translate-1/2 rounded-full bg-press shadow-[0_0_18px_var(--t-glow)]"
            initial={{ left: x(now.value), scale: 0 }}
            animate={{ left: x(next.value), scale: 1 }}
            transition={{ ...SPRING, delay: 1.1 }}
          />
          <motion.span
            className="absolute top-[3.75rem] -translate-x-1/2 text-xs font-medium whitespace-nowrap text-press-ink tabular"
            style={{ left: x(next.value) }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
          >
            after {displayFigure(next)}
          </motion.span>
        </>
      ) : null}
    </div>
  );
}

/** Days of stock as cells: the ones left are lit and drain; the order refills the row. */
function StockCells({ card }: { card: ActionCard }) {
  const left = num(card, "days_left");
  const cover = num(card, "cover_days");
  const calm = useMotionLevel() === "calm";
  if (!left || !cover) return null;
  const cells = Math.max(1, Math.round(cover.value));
  const lit = Math.max(0, Math.min(cells, Math.round(left.value)));
  return (
    <div>
      <div className="flex gap-1.5" aria-hidden>
        {Array.from({ length: cells }, (_, i) => (
          <motion.span
            key={i}
            className="h-9 flex-1 rounded-md border border-glass-line"
            initial={{ backgroundColor: "var(--t-accent)", opacity: 1 }}
            animate={
              i < lit ? { opacity: calm ? 1 : [1, 0.55, 1] } : { backgroundColor: "rgba(0,0,0,0)", opacity: 1 }
            }
            transition={
              i < lit
                ? { duration: 1.6, repeat: 2, delay: 1.2 }
                : { duration: 0.35, delay: 0.4 + (cells - i) * 0.09 }
            }
          />
        ))}
      </div>
      <p className="mt-2 flex justify-between text-xs text-muted-foreground tabular">
        <span className="text-ink">{displayFigure(left)} left</span>
        <span>the order covers {displayFigure(cover)}</span>
      </p>
    </div>
  );
}

/** The card's chart evidence (e.g. footfall, dry vs rain) as two bars racing out. */
function EvidenceBars({ card }: { card: ActionCard }) {
  const chart = card.evidence.find((e) => e.kind === "chart" && e.rows.length > 0);
  const rows = (chart?.rows ?? []).filter((r): r is [string, number] => typeof r[0] === "string" && typeof r[1] === "number");
  if (!chart || rows.length === 0) return null;
  const max = Math.max(...rows.map((r) => r[1])) || 1;
  return (
    <div className="space-y-2">
      {rows.map(([label, value], i) => (
        <div key={label} className="grid grid-cols-[minmax(3rem,auto)_1fr_auto] items-center gap-3 text-xs">
          <span className="text-muted-foreground">{label}</span>
          <span className="h-3 overflow-hidden rounded-full bg-glass-strong">
            <motion.span
              aria-hidden
              className={`block h-full origin-left rounded-full ${i === rows.length - 1 ? "bg-chart-mark" : "bg-muted-foreground/60"}`}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: value / max }}
              transition={{ ...SPRING, delay: 0.5 + i * 0.15 }}
            />
          </span>
          <span className="min-w-8 text-right text-ink tabular">{plain.format(value)}</span>
        </div>
      ))}
      <p className="text-[11px] text-muted-foreground">{chart.label}</p>
    </div>
  );
}

/** The picture for a card, drawn only from its own numbers and evidence. */
export function CardVisual({ card }: { card: ActionCard }) {
  if (card.kind === "margin_erosion") return <MarginScale card={card} />;
  if (card.kind === "stockout") return <StockCells card={card} />;
  return <EvidenceBars card={card} />;
}
