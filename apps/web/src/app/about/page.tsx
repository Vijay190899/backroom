import type { Metadata } from "next";
import { Info } from "lucide-react";

import { PlaceholderPage } from "@/components/placeholder-page";

export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  return (
    <PlaceholderPage
      title="About"
      subtitle="How Backroom works, and what it would take to run on real merchant tools."
      icon={Info}
      emptyTitle="Architecture overview"
      emptyBody="A walkthrough of the browser agent, the skill lifecycle, the memory graph and the model layer."
      milestone="Arrives in M5"
    />
  );
}
