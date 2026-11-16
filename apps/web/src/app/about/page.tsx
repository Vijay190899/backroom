import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import { FlowDiagram } from "@/components/about/flow-diagram";
import { PageTransition } from "@/components/motion/page-transition";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "About" };

const MODELS = [
  { role: "Planner", job: "writes the brief's words from computed candidates", model: "Sonnet 5.5" },
  { role: "Escalation", job: "repairs a step the healer couldn't, with a screenshot", model: "Sonnet 5.5" },
  { role: "Verifier", job: "can only veto a card, citing a rule", model: "Haiku 5.5" },
  { role: "Healer", job: "finds the moved button when replay fails", model: "Haiku 5.5" },
  { role: "Worker", job: "explores a new task once, step by step", model: "Haiku 5.5" },
];

const LADDER = [
  "Deterministic fallbacks: the same label, the visible text, a stored selector",
  "The healer model reads the page and finds the moved control",
  "The escalation model, with a screenshot",
  "You: Backroom asks instead of guessing",
];

function Chapter({ n, title, children }: { n: string; title: string; children: ReactNode }) {
  return (
    <section className="glass panel mt-6 grid gap-x-10 gap-y-3 lg:grid-cols-12">
      <p aria-hidden className="font-display text-5xl leading-none text-press-ink lg:col-span-2">
        {n}
      </p>
      <div className="lg:col-span-10">
        <h2 className="font-display text-3xl font-medium tracking-tight text-ink sm:text-4xl">{title}</h2>
        <div className="mt-4 max-w-[44rem] space-y-4 font-serif text-[1.0625rem] leading-relaxed text-ink/85">
          {children}
        </div>
      </div>
    </section>
  );
}

export default function AboutPage() {
  return (
    <PageTransition>
      <PageHeader
        kicker="How it is built"
        title="About"
        subtitle="An agentic back office for one café: it reads the business, proposes a few decisions with the money behind them, and carries out the ones you approve in the café's own web tools."
      />

      <section aria-label="The loop" className="glass panel">
        <FlowDiagram />
      </section>

      <Chapter n="I" title="Agents for judgment, code for math">
        <p>
          Detectors compute every figure from the till, the invoices and the forecast. A model writes
          the words around them, and a deterministic number guard checks each number in that text
          against the evidence. If the words don&rsquo;t match, the model gets one rewrite; if they still
          don&rsquo;t, plain template text replaces them.
          A second model can only veto a card, and it must cite the rule it broke.
        </p>
      </Chapter>

      <Chapter n="II" title="Skills that repair themselves">
        <p>
          The first time Backroom does a task in a portal, it explores and records each step. Every
          run after that replays the recording with no model calls. When a page changes, it climbs a
          ladder, cheapest rung first, and saves the repair as a new version of the skill:
        </p>
        <ol className="space-y-2 border-l border-heal/50 pl-5 font-sans text-[0.9375rem]">
          {LADDER.map((rung, i) => (
            <li key={rung} className="flex gap-3">
              <span className="font-mono text-heal">{i + 1}</span>
              <span className="text-ink">{rung}</span>
            </li>
          ))}
        </ol>
      </Chapter>

      <Chapter n="III" title="Memory that knows when">
        <p>
          Facts are bitemporal: each one records when it became true and when Backroom learned it.
          A new butter invoice doesn&rsquo;t overwrite the old price; it closes that fact and opens a
          new one. Any past brief can be explained with what Backroom knew that day.
        </p>
      </Chapter>

      <Chapter n="IV" title="Every model call is metered">
        <p>
          There is one path to a model. It checks the day&rsquo;s budget first, then records each
          call&rsquo;s tokens, cache reads and cost in a ledger. Stable prompt prefixes are cached;
          long calls stream.
        </p>
        <table className="w-full font-sans text-[0.9375rem]">
          <caption className="sr-only">Model roles and their default models</caption>
          <thead>
            <tr className="border-b border-line text-left">
              <th scope="col" className="kicker py-2 pr-4 font-semibold text-ink">Role</th>
              <th scope="col" className="kicker py-2 pr-4 font-semibold text-ink">Job</th>
              <th scope="col" className="kicker py-2 font-semibold text-ink">Default</th>
            </tr>
          </thead>
          <tbody>
            {MODELS.map((m) => (
              <tr key={m.role} className="border-b border-line align-top">
                <th scope="row" className="py-2.5 pr-4 text-left font-medium text-ink">{m.role}</th>
                <td className="py-2.5 pr-4 text-muted-foreground">{m.job}</td>
                <td className="py-2.5 font-mono text-[0.8125rem] whitespace-nowrap text-ink">{m.model}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="font-sans text-sm text-muted-foreground">
          Every role&rsquo;s model is set by environment; the provider is OpenRouter by default, or
          Anthropic directly.
        </p>
      </Chapter>

      <Chapter n="V" title="Beyond one café">
        <p>
          Real merchant tools would use their APIs where they exist (tills, accounting) and browser
          skills for the long tail of portals without one; both look the same to the planner. Skills
          are shared per portal, so one merchant&rsquo;s repair fixes everyone&rsquo;s. Things only
          a person can do, like a code on the owner&rsquo;s phone, are a handoff, not a failure.
        </p>
      </Chapter>

      <p className="mt-6 border-t border-line pt-4 text-sm text-muted-foreground">
        Hafer &amp; Bohne, Grainline, TillDesk and Localboard are fictional. The portals are mock sites
        built for this demo, and Backroom never works around bot protection.
        <br />
        Café model (intro): &ldquo;Shop&rdquo; by Shaun Glowa, CC-BY 3.0, via{" "}
        <a href="https://poly.pizza" className="link-draw text-ink">
          Poly Pizza
        </a>
        ; modified (overlapping faces separated to stop flicker, and the door rigged to open).
        Background drawings from the{" "}
        <a href="https://lucide.dev" className="link-draw text-ink">
          Lucide
        </a>{" "}
        icon set (ISC).
        <br />
        Data: weather data by{" "}
        <a href="https://open-meteo.com/" className="link-draw text-ink">
          Open-Meteo.com
        </a>{" "}
        (
        <a href="https://creativecommons.org/licenses/by/4.0/" className="link-draw text-ink">
          CC BY 4.0
        </a>
        ; aggregated to daily values); public holidays from{" "}
        <a href="https://date.nager.at" className="link-draw text-ink">
          Nager.Date
        </a>
        ; sales patterns derived from Maven Analytics&rsquo; &ldquo;Coffee Shop Sales&rdquo; practice
        dataset (rescaled, re-dated and renamed; no raw rows are published).
        <br />
        The brief&rsquo;s wording comes from AI models; every number is computed by code.{" "}
        <Link href="/legal" className="link-draw text-ink">
          Privacy and legal notice
        </Link>
        .
      </p>
    </PageTransition>
  );
}
