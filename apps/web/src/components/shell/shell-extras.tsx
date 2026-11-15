"use client";

import { useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { SceneDriver } from "@/components/fx/scene-driver";
import { afterFirstData } from "@/lib/brief";

// Everything here arrives after first paint: the intro player, the café scene, the dock,
// the particle canvas and ⌘K.
const AgentDock = dynamic(() => import("./agent-dock").then((m) => m.AgentDock), { ssr: false });
const ParticleLayer = dynamic(() => import("@/components/fx/particle-layer").then((m) => m.ParticleLayer), {
  ssr: false,
});
const CafeScene = dynamic(() => import("@/components/fx/cafe-scene").then((m) => m.CafeScene), { ssr: false });
const IntroPlayer = dynamic(() => import("@/components/intro/intro-player").then((m) => m.IntroPlayer), {
  ssr: false,
});
const CommandPalette = dynamic(() => import("./command-palette").then((m) => m.CommandPalette), { ssr: false });

export function ShellExtras() {
  // The café scene (half a megabyte of animation runtime) fades in once the page's
  // first data has painted and the cards have settled.
  const queryClient = useQueryClient();
  const [scene, setScene] = useState(false);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let live = true;
    void afterFirstData(queryClient, 1500).then(() => {
      if (live) timer = setTimeout(() => setScene(true), 1200);
    });
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [queryClient]);
  return (
    <>
      <IntroPlayer />
      {scene ? <CafeScene /> : null}
      <SceneDriver />
      <AgentDock />
      <CommandPalette />
      <ParticleLayer />
    </>
  );
}
