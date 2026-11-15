import type { Metadata } from "next";

import { PageTransition } from "@/components/motion/page-transition";
import { SkillsDesk } from "@/components/skills/skills-desk";

export const metadata: Metadata = { title: "Skills" };

export default function SkillsPage() {
  return (
    <PageTransition>
      <SkillsDesk />
    </PageTransition>
  );
}
