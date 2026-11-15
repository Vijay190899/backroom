import type { Skill, SkillDiff, Step } from "@/lib/contracts";

export type Locator = { role: string; name: string };

function locator(target: Locator | null): string {
  return target ? `${target.role} ‘${target.name}’` : "";
}

/** One step as a code-review line: `click button ‘Anmelden’`, `goto /grainline/login`. */
export function stepLine(step: Pick<Step, "action" | "target" | "value_template">): string {
  const where = locator(step.target);
  if (step.action === "goto") return `goto ${step.value_template ?? ""}`.trim();
  if (step.action === "fill_secret") return `fill_secret ${where} ← ••••••`;
  if (step.value_template && step.action === "fill") return `fill ${where} ← ${step.value_template}`;
  return `${step.action} ${where}`.trim();
}

export type StepRow = {
  index: number;
  step: Step;
  kind: "same" | "added" | "changed";
  /** For a changed locator: the line as it was in the parent version. */
  before: string | null;
};

/**
 * A version's steps, marked with what its diff from the parent changed. Diff indices
 * are in the new version's numbering (an insert shifts the later steps).
 */
export function annotate(version: Skill, diff: SkillDiff | null): StepRow[] {
  return version.steps.map((step, index) => {
    const changes = diff?.changes.filter((c) => c.step_index === index) ?? [];
    if (changes.some((c) => c.op === "insert")) return { index, step, kind: "added", before: null };
    const update = changes.find((c) => c.op === "update" && c.field === "target");
    if (update) {
      const old = { ...step, target: update.before as Locator | null };
      return { index, step, kind: "changed", before: stepLine(old) };
    }
    return { index, step, kind: "same", before: null };
  });
}
