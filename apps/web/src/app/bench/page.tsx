import { Check, X } from "lucide-react";
import type { Metadata } from "next";

import probeJson from "../../../../../bench/results/provider_probe.json";

import { PageTransition } from "@/components/motion/page-transition";
import { PageHeader } from "@/components/page-header";
import { headline } from "@/lib/bench-results";
import { enterDelay } from "@/lib/motion";
import { probeSchema } from "@/lib/schemas/probe";
import { cn } from "@/lib/utils";

export const metadata: Metadata = { title: "Bench" };

// The committed result file, validated at build time. Nothing on this page is made up:
// what hasn't run yet says so.
const probe = probeSchema.parse(probeJson);

const CHECK_LABEL: Record<string, string> = {
  basic: "Basic call",
  effort: "Effort setting",
  strict_tools: "Strict tool use",
  structured_outputs: "Structured outputs",
  prompt_cache: "Prompt caching",
  streaming: "Streaming",
};

const BENCHMARKS = [
  {
    id: "B1",
    name: "Browser robustness",
    method: "3 tasks (reorder, change a price, download an invoice) across chaos seeds 0–19, cold and warm.",
    metrics: "Success rate, p50/p95 time, model calls, tokens, cost",
    target: "Cold ≥ 90% at seed 0; heal ≥ 85% across seeds",
  },
  {
    id: "B2",
    name: "Learning curve",
    method: "The same task 20 times in a row, with a portal redesign injected at runs 8 and 15.",
    metrics: "Time and cost per run",
    target: "Warm p50 under 5 s at $0",
  },
  {
    id: "B3",
    name: "Memory vs baseline",
    method: "30 questions with SQL ground truth: context pack, raw dump, and no memory.",
    metrics: "Accuracy, input tokens, cost, time",
    target: "≥ 90% accuracy at ≤ 20% of the raw dump's tokens",
  },
  {
    id: "B4",
    name: "Model swap (stretch goal)",
    method: "A cold B1 subset and B3 on Haiku 5.5, Sonnet 5.5 and Opus 5.5.",
    metrics: "The same, per model",
    target: "Informs the default model choice",
  },
  {
    id: "B5",
    name: "Number guard",
    method: "Every brief generated during the bench.",
    metrics: "Guard pass rate, rewrites",
    target: "100% of displayed numbers verified",
  },
];

/** A benchmark's measured headline, or an honest "not run yet" until its results exist. */
function BenchHeadline({ id }: { id: string }) {
  const h = headline(id);
  if (!h) {
    return (
      <p className="self-start sm:text-right">
        <span className="kicker inline-flex h-7 items-center border border-dashed border-ink/30 px-2 text-[0.625rem] text-muted-foreground">
          Not run yet
        </span>
      </p>
    );
  }
  return (
    <div className="self-start sm:text-right">
      <p className="font-display text-3xl text-ink tabular">{h.value}</p>
      <p className="mt-1 text-sm text-muted-foreground">{h.detail}</p>
      <p className="mt-1 font-mono text-[11px] text-muted-foreground">{h.meta}</p>
    </div>
  );
}

const ms = new Intl.NumberFormat("en-GB");
const usd = (v: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumSignificantDigits: 2 }).format(v);
const ranAt = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "Europe/Berlin",
}).format(new Date(probe.ran_at));

export default function BenchPage() {
  const checks = Object.entries(probe.checks);
  const passed = checks.filter(([, c]) => c.ok).length;
  const slowest = Math.max(...checks.map(([, c]) => c.ms));
  const totalMs = checks.reduce((sum, [, c]) => sum + c.ms, 0);

  return (
    <PageTransition>
      <PageHeader
        kicker="How well it works"
        title="Bench"
        subtitle="Backroom measures itself. The provider probe below is a real run; the benchmarks run on the main machine once the whole stack is together, and stay empty until then."
      />

      <section aria-labelledby="probe-heading">
        <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
          <h2 id="probe-heading" className="kicker text-ink">
            The provider probe
          </h2>
          <p className="text-sm text-muted-foreground tabular">
            {ranAt} · {probe.model} via {probe.provider} · SDK {probe.sdk_version} · commit{" "}
            <span className="font-mono">{probe.git_sha}</span>
          </p>
        </div>

        <dl className="mt-4 grid gap-x-10 gap-y-6 border-t border-ink pt-5 sm:grid-cols-3">
          <div>
            <dt className="kicker text-muted-foreground">Checks passed</dt>
            <dd className="mt-1 font-display text-6xl leading-none font-medium tracking-tight text-ink tabular">
              {passed}
              <span className="text-muted-foreground"> / {checks.length}</span>
            </dd>
          </div>
          <div>
            <dt className="kicker text-muted-foreground">Cost of the whole probe</dt>
            <dd className="mt-1 font-display text-6xl leading-none font-medium tracking-tight text-ink tabular">
              {usd(probe.total_usd)}
            </dd>
          </div>
          <div>
            <dt className="kicker text-muted-foreground">Time, all checks</dt>
            <dd className="mt-1 font-display text-6xl leading-none font-medium tracking-tight text-ink tabular">
              {(totalMs / 1000).toFixed(1)}
              <span className="text-muted-foreground"> s</span>
            </dd>
          </div>
        </dl>

        <figure className="mt-12">
          <figcaption className="kicker text-ink">How long each check took</figcaption>
          <ul className="mt-3 border-t border-ink">
            {checks.map(([id, c], i) => (
              <li
                key={id}
                className="group grid grid-cols-[minmax(7rem,10rem)_1fr_auto] items-center gap-x-4 border-b border-line py-3 sm:grid-cols-[12rem_1fr_auto]"
              >
                <span className="text-[0.9375rem] text-ink">{CHECK_LABEL[id] ?? id}</span>
                <span className="relative h-3.5">
                  <span
                    aria-hidden
                    style={{ width: `${(c.ms / slowest) * 100}%`, ...enterDelay(120 + i * 70) }}
                    className="bar-grow absolute inset-y-0 left-0 rounded-r-[4px] bg-chart-mark transition-opacity duration-150 group-hover:opacity-80"
                  />
                </span>
                <span className="flex items-center gap-3 text-sm tabular">
                  <span className="w-16 text-right text-ink">{ms.format(c.ms)} ms</span>
                  <span className="hidden w-16 text-right text-muted-foreground sm:inline">{usd(c.usd)}</span>
                  <span className={cn("inline-flex items-center gap-1", c.ok ? "text-pos" : "text-neg")}>
                    {c.ok ? <Check aria-hidden className="size-3.5" /> : <X aria-hidden className="size-3.5" />}
                    {c.ok ? "passed" : "failed"}
                  </span>
                </span>
              </li>
            ))}
          </ul>
          <details className="mt-4 text-sm">
            <summary className="link-draw inline-flex min-h-11 cursor-pointer items-center text-press-ink sm:min-h-0">
              Show the raw results
            </summary>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full font-mono text-[0.8125rem] tabular">
                <thead>
                  <tr className="border-b border-ink text-left text-muted-foreground">
                    <th scope="col" className="py-1.5 pr-4 font-normal">check</th>
                    <th scope="col" className="py-1.5 pr-4 font-normal">ok</th>
                    <th scope="col" className="py-1.5 pr-4 font-normal">ms</th>
                    <th scope="col" className="py-1.5 pr-4 font-normal">usd</th>
                    <th scope="col" className="py-1.5 font-normal">detail</th>
                  </tr>
                </thead>
                <tbody>
                  {checks.map(([id, c]) => (
                    <tr key={id} className="border-b border-line/60 align-top">
                      <td className="py-1.5 pr-4 text-ink">{id}</td>
                      <td className="py-1.5 pr-4 text-ink">{String(c.ok)}</td>
                      <td className="py-1.5 pr-4 text-ink">{c.ms}</td>
                      <td className="py-1.5 pr-4 text-ink">{c.usd.toFixed(6)}</td>
                      <td className="py-1.5 break-all text-muted-foreground">{c.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </figure>
      </section>

      <section aria-labelledby="bench-heading" className="mt-16">
        <h2 id="bench-heading" className="kicker text-ink">
          The benchmarks
        </h2>
        <ol className="mt-3 border-t border-ink">
          {BENCHMARKS.map((b) => (
            <li
              key={b.id}
              className="grid gap-x-8 gap-y-2 border-b border-line py-5 sm:grid-cols-[4rem_1fr_14rem]"
            >
              <span className="font-display text-3xl text-press-ink">{b.id}</span>
              <div>
                <h3 className="font-display text-2xl text-ink">{b.name}</h3>
                <p className="mt-1 font-serif text-[1.0625rem] leading-relaxed text-ink/85">{b.method}</p>
                <p className="mt-2 text-sm text-muted-foreground">
                  <span className="kicker mr-2 text-[0.625rem]">Measures</span>
                  {b.metrics}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  <span className="kicker mr-2 text-[0.625rem]">Target</span>
                  {b.target}
                </p>
              </div>
              <BenchHeadline id={b.id} />
            </li>
          ))}
        </ol>
      </section>
    </PageTransition>
  );
}
