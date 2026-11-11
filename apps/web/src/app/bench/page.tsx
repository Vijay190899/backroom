import type { Metadata } from "next";
import { Gauge } from "lucide-react";

import { PlaceholderPage } from "@/components/placeholder-page";

export const metadata: Metadata = { title: "Benchmarks" };

export default function BenchPage() {
  return (
    <PlaceholderPage
      title="Benchmarks"
      subtitle="Measured, reproducible numbers: success under change, speed, cost and memory accuracy."
      icon={Gauge}
      emptyTitle="No results yet"
      emptyBody="Results are committed with the provider, model IDs, seeds and git SHA they were measured on."
      milestone="Arrives in M4"
    />
  );
}
