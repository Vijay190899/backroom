import type { Metadata } from "next";
import { Workflow } from "lucide-react";

import { PlaceholderPage } from "@/components/placeholder-page";

export const metadata: Metadata = { title: "Skills" };

export default function SkillsPage() {
  return (
    <PlaceholderPage
      title="Skills"
      subtitle="Tasks the agent has learned to do in your web tools, and every repair it has made."
      icon={Workflow}
      emptyTitle="No skills learned yet"
      emptyBody="Each successful run is saved as a replayable skill, with a version history of its fixes."
      milestone="Arrives in M2"
    />
  );
}
