"use client";

import NumberFlow from "@number-flow/react";
import { Check, ShieldCheck } from "lucide-react";
import { startTransition, useEffect, useState, ViewTransition } from "react";

import { PageHeader } from "@/components/page-header";
import { BadgeSlot, SampleBadge } from "@/components/sample-badge";
import type { Skill, SkillSummary, SkillVersions } from "@/lib/contracts";
import { useLiveOrSample } from "@/lib/data";
import { skillsQuery, skillVersionsQuery } from "@/lib/queries";
import { PORTAL_LABEL, TASK_LABEL } from "@/lib/labels";
import { enterDelay } from "@/lib/motion";
import { annotate, stepLine } from "@/lib/skills";
import { cn } from "@/lib/utils";

function useRegistry() {
  return useLiveOrSample(skillsQuery());
}

function useVersions(skillId: string | null) {
  return useLiveOrSample(skillVersionsQuery(skillId));
}

/** The selected skill lives in the URL (`?skill=`), so a link opens the same view. */
function useSelected(fallback: string | undefined): [string | undefined, (id: string) => void] {
  const [picked, setPicked] = useState<string | null>(null);
  useEffect(() => {
    const fromUrl = new URLSearchParams(location.search).get("skill");
    if (fromUrl) startTransition(() => setPicked(fromUrl));
  }, []);
  const select = (id: string) => {
    const url = new URL(location.href);
    url.searchParams.set("skill", id);
    history.replaceState(null, "", url);
    startTransition(() => setPicked(id));
  };
  return [picked ?? fallback, select];
}

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="border-t border-ink pt-2">
      <dt className="kicker text-muted-foreground">{label}</dt>
      <dd className="mt-1 font-display text-3xl font-medium text-ink tabular">{children}</dd>
    </div>
  );
}

type Stats = { runs: number; rate: number | null; meanMs: number | null; meanUsd: number | null };

function versionStats(stats: Skill["stats"]): Stats {
  return {
    runs: stats.runs,
    rate: stats.runs ? stats.successes / stats.runs : null,
    meanMs: stats.mean_latency_ms,
    meanUsd: stats.mean_usd,
  };
}

/** A skill's figures; anything without data (no runs yet) reads "–", never a made-up 0. */
function VersionStats({ stats }: { stats: Stats }) {
  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-4">
      <Stat label="Runs">
        <NumberFlow value={stats.runs} />
      </Stat>
      <Stat label="Succeeded">
        {stats.rate === null ? (
          "–"
        ) : (
          <NumberFlow value={stats.rate} format={{ style: "percent", maximumFractionDigits: 0 }} />
        )}
      </Stat>
      <Stat label="Mean time">
        {stats.meanMs === null ? (
          "–"
        ) : (
          <NumberFlow
            value={stats.meanMs / 1000}
            format={{ maximumFractionDigits: 1, minimumFractionDigits: 1 }}
            suffix=" s"
          />
        )}
      </Stat>
      <Stat label="Mean cost">
        {stats.meanUsd === null ? (
          "–"
        ) : (
          <NumberFlow
            value={stats.meanUsd}
            locales="en-US"
            format={{ style: "currency", currency: "USD", minimumFractionDigits: 4, maximumFractionDigits: 4 }}
          />
        )}
      </Stat>
    </dl>
  );
}

function Steps({ version, history }: { version: Skill; history: SkillVersions }) {
  const diff =
    history.diffs.find((d) => d.to_version === version.version && d.from_version === version.parent_version) ??
    null;
  const rows = annotate(version, diff);
  let changed = 0;
  return (
    <ol className="border-t border-ink font-mono text-[0.8125rem]">
      {rows.map(({ index, step, kind, before }) => {
        const delay = kind === "same" ? 0 : 200 + changed++ * 260;
        return (
          <li
            key={index}
            className={cn(
              "grid grid-cols-[2.25rem_1.25rem_1fr] gap-x-2 border-b border-line py-2.5",
              kind !== "same" && "bg-heal/[0.06]",
            )}
          >
            <span className="text-right text-muted-foreground tabular">{String(index + 1).padStart(2, "0")}</span>
            <span aria-hidden className={cn("text-center", kind === "same" ? "text-line" : "text-heal")}>
              {kind === "added" ? "+" : kind === "changed" ? "~" : "·"}
            </span>
            <div className="min-w-0">
              <p className="font-serif text-[0.9375rem] text-ink">{step.intent}</p>
              {before ? (
                <p className="mt-1 break-words text-neg line-through decoration-neg/60">
                  <span className="sr-only">Was: </span>
                  {before}
                </p>
              ) : null}
              <p
                style={kind === "same" ? undefined : enterDelay(delay)}
                className={cn(
                  "mt-1 break-words",
                  kind === "same" ? "text-muted-foreground" : "wipe font-medium text-pos",
                )}
              >
                {kind !== "same" ? <span className="sr-only">{kind === "added" ? "Added: " : "Now: "}</span> : null}
                {stepLine(step)}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function SkillDetail({ summary, registryLive }: { summary: SkillSummary; registryLive: boolean }) {
  const { data } = useVersions(summary.id);
  const history = data?.data ?? null;
  const latest = history?.versions.at(-1) ?? null;
  const [picked, setPicked] = useState<number | null>(null);
  const version = history?.versions.find((v) => v.version === picked) ?? latest;

  return (
    <div>
      <p className="kicker text-press-ink" translate="no">
        {PORTAL_LABEL[summary.portal] ?? summary.portal}
      </p>
      <h2 className="mt-2 font-display text-4xl font-medium tracking-tight text-ink">{TASK_LABEL[summary.task]}</h2>
      {registryLive && data?.source === "sample" ? (
        <div className="mt-3">
          <SampleBadge
            label="Sample history"
            why="The API has no versions route yet, so these steps and versions are the committed sample."
          />
        </div>
      ) : null}

      {history && version ? (
        <>
          <div role="group" aria-label="Version" className="mt-6 flex flex-wrap items-center gap-x-1 gap-y-3">
            {history.versions.map((v, i) => (
              <span key={v.version} className="flex items-center">
                {i > 0 ? <span aria-hidden className="mx-2 h-px w-10 bg-ink/40" /> : null}
                <button
                  type="button"
                  aria-pressed={v.version === version.version}
                  onClick={() => startTransition(() => setPicked(v.version))}
                  className={cn(
                    "relative inline-flex h-11 min-w-14 cursor-pointer items-center justify-center px-3 font-mono text-sm transition-colors duration-150 sm:h-10",
                    v.version === version.version ? "text-background" : "text-ink hover:bg-subtle",
                  )}
                >
                  {v.version === version.version ? (
                    <span aria-hidden style={{ viewTransitionName: "version-pick" }} className="absolute inset-0 bg-ink" />
                  ) : null}
                  <span className="relative">v{v.version}</span>
                </button>
              </span>
            ))}
          </div>

          <ViewTransition key={version.version} enter="swap-in" exit="swap-out" default="none">
            <div className="mt-6">
              {version.heal_note ? (
                <p className="flex items-start gap-3 border border-heal/40 bg-heal/[0.06] px-4 py-3 text-sm text-ink">
                  <span className="kicker mt-0.5 shrink-0 border border-heal/50 px-1.5 py-0.5 text-[0.625rem] text-heal">
                    Heal
                  </span>
                  <span>
                    <strong className="font-semibold">Healed from v{version.parent_version}.</strong>{" "}
                    {version.heal_note}
                  </span>
                </p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Learned by exploring once; every run since replays it with no model calls.
                </p>
              )}

              <div className="mt-6">
                <VersionStats stats={versionStats(version.stats)} />
              </div>

              <h3 className="kicker mt-10 text-ink">Steps</h3>
              <div className="mt-3">
                <Steps version={version} history={history} />
              </div>

              <h3 className="kicker mt-10 text-ink">Checked after every run</h3>
              <ul className="mt-3 border-t border-ink">
                {version.postconditions.map((c) => (
                  <li key={`${c.kind}:${c.value}`} className="flex items-start gap-3 border-b border-line py-2.5 text-sm">
                    <ShieldCheck aria-hidden className="mt-0.5 size-4 shrink-0 text-pos" />
                    <span className="font-mono text-[0.8125rem] text-ink">
                      {c.value}
                      {c.equals !== null ? <span className="text-muted-foreground"> = {c.equals}</span> : null}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </ViewTransition>
        </>
      ) : (
        <div className="mt-6">
          <VersionStats
            stats={{
              runs: summary.runs,
              rate: summary.success_rate,
              meanMs: summary.mean_latency_ms,
              meanUsd: summary.mean_usd,
            }}
          />
          <p className="mt-8 border-y border-line py-8 text-center font-serif text-lg text-muted-foreground">
            {data ? "This skill’s steps and versions aren’t in the sample data." : "Loading the steps…"}
          </p>
        </div>
      )}
    </div>
  );
}

export function SkillsDesk() {
  const registry = useRegistry();
  const skills = registry.data?.data ?? [];
  const [selected, select] = useSelected(skills[0]?.id);
  const current = skills.find((s) => s.id === selected) ?? skills[0];

  return (
    <>
      <PageHeader
        kicker="What Backroom can do"
        title="Skills"
        subtitle="Tasks the agent learned by doing them once. It replays them for free, and when a page changes it repairs the step and saves a new version."
        actions={
          !registry.data ? (
            <BadgeSlot />
          ) : registry.data.source === "sample" ? (
            <SampleBadge why="The API has no skills route yet, so this is the committed sample." />
          ) : null
        }
      />

      {registry.isError ? (
        <div role="alert" className="mb-10 border-y border-line py-12 text-center">
          <p className="font-display text-2xl text-ink">The skills didn&rsquo;t load.</p>
          <button
            type="button"
            onClick={() => void registry.refetch()}
            className="link-draw mt-3 inline-flex min-h-11 cursor-pointer items-center text-press-ink"
          >
            Try again
          </button>
        </div>
      ) : null}

      <div className="grid gap-12 lg:grid-cols-12 lg:gap-10">
        <section aria-labelledby="registry-heading" className="lg:col-span-4">
          <h2 id="registry-heading" className="kicker text-ink">
            The registry
          </h2>
          <ul className="mt-3 border-t border-ink">
            {registry.isPending
              ? [0, 1].map((i) => <li key={i} aria-hidden className="h-24 animate-pulse border-b border-line bg-subtle/60" />)
              : skills.map((s, i) => {
                  const active = s.id === current?.id;
                  return (
                    <li key={s.id} className="enter border-b border-line" style={enterDelay(i * 70)}>
                      <button
                        type="button"
                        aria-pressed={active}
                        onClick={() => select(s.id)}
                        className="group relative block w-full cursor-pointer py-4 pr-2 pl-4 text-left transition-colors duration-150 hover:bg-subtle/60"
                      >
                        {active ? (
                          <span
                            aria-hidden
                            style={{ viewTransitionName: "skill-pick" }}
                            className="absolute inset-y-3 left-0 w-0.5 bg-press"
                          />
                        ) : null}
                        <span className="kicker text-muted-foreground" translate="no">
                          {PORTAL_LABEL[s.portal] ?? s.portal}
                        </span>
                        <span className="mt-1 block font-display text-xl text-ink">{TASK_LABEL[s.task]}</span>
                        <span className="mt-1 flex flex-wrap gap-x-3 text-sm text-muted-foreground tabular">
                          <span className="font-mono text-ink">v{s.latest_version}</span>
                          <span>
                            {s.runs} {s.runs === 1 ? "run" : "runs"}
                          </span>
                          {s.success_rate !== null ? <span>{Math.round(s.success_rate * 100)}% ok</span> : null}
                          {s.mean_latency_ms !== null ? <span>{(s.mean_latency_ms / 1000).toFixed(1)} s</span> : null}
                        </span>
                      </button>
                    </li>
                  );
                })}
          </ul>
          <p className="mt-4 flex items-start gap-2 text-sm text-muted-foreground">
            <Check aria-hidden className="mt-0.5 size-4 shrink-0 text-pos" />
            Replays cost nothing: a model is only called to explore a new task or repair a step.
          </p>
        </section>

        <section aria-label="Skill detail" className="lg:col-span-8 lg:border-l lg:border-line lg:pl-10">
          {current ? (
            <ViewTransition key={current.id} enter="swap-in" exit="swap-out" default="none">
              <div>
                <SkillDetail summary={current} registryLive={registry.data?.source === "live"} />
              </div>
            </ViewTransition>
          ) : null}
        </section>
      </div>
    </>
  );
}
