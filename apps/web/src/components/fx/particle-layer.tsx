"use client";

import { attachParticleCanvas } from "@/lib/particles";

/** The one canvas every particle effect draws on: above everything, never in the way. */
export function ParticleLayer() {
  return (
    <canvas
      aria-hidden
      ref={attachParticleCanvas}
      style={{ viewTransitionName: "particles" }}
      className="pointer-events-none fixed inset-0 z-[70] size-full"
    />
  );
}
