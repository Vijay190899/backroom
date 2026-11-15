"use client";

import dynamic from "next/dynamic";

import { SceneDriver } from "@/components/fx/scene-driver";

// Everything here arrives after first paint: the intro player, the dock, the particle
// canvas and ⌘K. (The café scene lives in the hero band, `CafeHero`.)
const AgentDock = dynamic(() => import("./agent-dock").then((m) => m.AgentDock), { ssr: false });
const ParticleLayer = dynamic(() => import("@/components/fx/particle-layer").then((m) => m.ParticleLayer), {
  ssr: false,
});
const IntroPlayer = dynamic(() => import("@/components/intro/intro-player").then((m) => m.IntroPlayer), {
  ssr: false,
});
const CommandPalette = dynamic(() => import("./command-palette").then((m) => m.CommandPalette), { ssr: false });

export function ShellExtras() {
  return (
    <>
      <IntroPlayer />
      <SceneDriver />
      <AgentDock />
      <CommandPalette />
      <ParticleLayer />
    </>
  );
}
