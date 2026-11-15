import type { MemoryGraph, SkillSummary, SkillVersions } from "@/lib/contracts";
import { liveOrSample } from "@/lib/data";

const contracts = () => import("@/lib/contracts");

/** The skills registry (live route, else the committed sample). */
export const skillsQuery = () =>
  liveOrSample<SkillSummary[]>(
    "skills",
    "/skills",
    async () => (await contracts()).skillSummarySchema.array(),
    () => import("@/fixtures/skills.json"),
  );

/** One skill's versions and diffs. The sample has one skill's history; others have none. */
export const skillVersionsQuery = (skillId: string | null) =>
  liveOrSample<SkillVersions | null>(
    `skill-versions:${skillId}`,
    `/skills/${encodeURIComponent(skillId ?? "")}/versions`,
    async () => (await contracts()).skillVersionsSchema.nullable(),
    async () => {
      const fixture = await import("@/fixtures/skill-versions.json");
      return { default: fixture.default.skill_id === skillId ? fixture.default : null };
    },
  );

/** The memory graph with its full history (the time slider filters it in the browser). */
export const memoryQuery = () =>
  liveOrSample<MemoryGraph>(
    "memory-graph",
    "/memory/graph",
    async () => (await contracts()).memoryGraphSchema,
    () => import("@/fixtures/memory-graph.json"),
  );
