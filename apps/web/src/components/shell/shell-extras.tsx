"use client";

import dynamic from "next/dynamic";

// Everything here arrives after first paint: the dock, the particle canvas, ⌘K.
const AgentDock = dynamic(() => import("./agent-dock").then((m) => m.AgentDock), { ssr: false });
const ParticleLayer = dynamic(() => import("@/components/fx/particle-layer").then((m) => m.ParticleLayer), {
  ssr: false,
});
const CommandPalette = dynamic(() => import("./command-palette").then((m) => m.CommandPalette), { ssr: false });

export function ShellExtras() {
  return (
    <>
      <AgentDock />
      <CommandPalette />
      <ParticleLayer />
    </>
  );
}
