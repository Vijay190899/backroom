import type { Metadata } from "next";
import { Suspense } from "react";

import { PageTransition } from "@/components/motion/page-transition";
import { RunTheater } from "@/components/runs/run-theater";

export const metadata: Metadata = { title: "Run" };

async function Theater({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <RunTheater key={id} id={id} />;
}

export default function RunPage({ params }: PageProps<"/runs/[id]">) {
  return (
    <PageTransition>
      {/* Marked as the theater from the first byte, so the café hero never shows then collapses. */}
      <Suspense fallback={<div data-theater className="min-h-[60vh]" />}>
        <Theater params={params} />
      </Suspense>
    </PageTransition>
  );
}
