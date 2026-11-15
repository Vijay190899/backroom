import type { Metadata } from "next";

import { MemoryDesk } from "@/components/memory/memory-desk";
import { PageTransition } from "@/components/motion/page-transition";

export const metadata: Metadata = { title: "Memory" };

export default function MemoryPage() {
  return (
    <PageTransition>
      <MemoryDesk />
    </PageTransition>
  );
}
