"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { afterFirstData } from "@/lib/brief";

import { INTRO_KEY } from "./intro-overlay";

type ModelViewer = HTMLElement & {
  cameraOrbit: string;
  cameraTarget: string;
  fieldOfView: string;
  interpolationDecay: number;
};

/**
 * Walks you into the café: a 3D shop (CC-BY 3.0, Shaun Glowa) seen from a three-quarter
 * view, orbiting round to its front, then the camera pushes in toward the door and the
 * scene dissolves into the app. About four seconds; a click or Esc ends it at once.
 */
export function IntroPlayer() {
  const [active] = useState(() => document.documentElement.dataset.intro === "play");
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!active) return;
    const root = document.getElementById("intro");
    const stage = document.getElementById("intro-stage");
    if (!root || !stage) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    let done = false;

    const finish = () => {
      if (done) return;
      done = true;
      timers.forEach(clearTimeout);
      try {
        sessionStorage.setItem(INTRO_KEY, "1");
      } catch {
        // Private mode: it may play again next visit.
      }
      root.classList.add("is-leaving");
      removeEventListener("keydown", onKey);
      removeEventListener("pointerdown", finish);
      // Not tracked: once leaving starts, the app must open even if this unmounts.
      setTimeout(() => (document.documentElement.dataset.intro = "done"), 750);
    };
    // No button on screen: a click or Esc walks straight in.
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && finish();
    addEventListener("keydown", onKey);
    addEventListener("pointerdown", finish);

    // Never hold the app hostage: if the model is slow, go straight in.
    timers.push(setTimeout(finish, 7000));

    // The page's own data goes first (it is what paints under the intro).
    afterFirstData(queryClient, 1500)
      .then(() => import("@google/model-viewer"))
      .then(({ ModelViewerElement }) => {
        // Hold full resolution: the automatic drop under load reads as flicker.
        ModelViewerElement.minimumRenderScale = 1;
        if (done) return;
        const mv = document.createElement("model-viewer") as ModelViewer;
        mv.setAttribute("src", "/intro/cafe-shop.glb");
        mv.setAttribute("alt", "");
        mv.setAttribute("shadow-intensity", "1");
        mv.setAttribute("environment-image", "neutral");
        mv.setAttribute("interaction-prompt", "none");
        mv.setAttribute("disable-zoom", "");
        mv.cameraOrbit = "105deg 68deg 115%";
        mv.fieldOfView = "30deg";
        mv.interpolationDecay = 260;
        mv.className = "intro-model";
        mv.addEventListener("load", () => {
          if (done) return;
          stage.classList.add("is-ready");
          // Orbit round to the shop front…
          timers.push(setTimeout(() => (mv.cameraOrbit = "180deg 80deg 95%"), 150));
          // …then walk up to the door (left of the lamp post, so the walk is clear)…
          timers.push(
            setTimeout(() => {
              mv.interpolationDecay = 170;
              mv.cameraTarget = "0.27m -0.04m 0.07m";
              mv.cameraOrbit = "180deg 86deg 0.45m";
              mv.fieldOfView = "24deg";
            }, 1600),
          );
          // …and step inside.
          timers.push(setTimeout(finish, 3700));
        });
        stage.appendChild(mv);
      })
      .catch(finish);

    return () => {
      done = true;
      timers.forEach(clearTimeout);
      removeEventListener("keydown", onKey);
      removeEventListener("pointerdown", finish);
    };
  }, [active, queryClient]);

  return null;
}
