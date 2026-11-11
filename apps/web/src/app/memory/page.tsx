import type { Metadata } from "next";
import { Waypoints } from "lucide-react";

import { PlaceholderPage } from "@/components/placeholder-page";

export const metadata: Metadata = { title: "Memory" };

export default function MemoryPage() {
  return (
    <PlaceholderPage
      title="Memory"
      subtitle="What Backroom knows about the business, and when each fact was true."
      icon={Waypoints}
      emptyTitle="Nothing remembered yet"
      emptyBody="Prices, preferences and patterns will appear here as a graph you can scrub through time."
      milestone="Arrives in M3"
    />
  );
}
