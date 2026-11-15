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
  animationName: string;
  play: (options?: { repetitions?: number }) => void;
};

/**
 * Walks you into the café: a 3D shop (CC-BY 3.0, Shaun Glowa) seen from a three-quarter
 * view, orbiting round to its front, walking up to the door, which swings open on a warm,
 * lit doorway (the model's `DoorOpen` animation, DECISIONS L-82), then stepping through
 * the glow into the app. About five seconds; a click or Esc ends it at once.
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
    timers.push(setTimeout(finish, 9000));

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
        // The walk ends inside the doorway: lift model-viewer's default close-up limits
        // (minimum radius and a 25° field of view), which would stop the camera short.
        mv.setAttribute("min-camera-orbit", "auto auto 0.02m");
        mv.setAttribute("min-field-of-view", "10deg");
        mv.cameraOrbit = "105deg 68deg 115%";
        mv.fieldOfView = "30deg";
        mv.interpolationDecay = 260;
        mv.className = "intro-model";
        mv.addEventListener("load", () => {
          if (done) return;
          stage.classList.add("is-ready");
          // Orbit round to the shop front…
          timers.push(setTimeout(() => (mv.cameraOrbit = "180deg 80deg 95%"), 150));
          // …walk up to the door (left of the lamp post, so the walk is clear)…
          timers.push(
            setTimeout(() => {
              mv.interpolationDecay = 170;
              // The doorway centre, measured with positionAndNormalFromPoint on the model.
              mv.cameraTarget = "0.374m -0.04m 0.083m";
              mv.cameraOrbit = "180deg 85deg 0.95m";
              mv.fieldOfView = "24deg";
            }, 1500),
          );
          // …the door swings open (it holds open: one repetition)…
          timers.push(
            setTimeout(() => {
              mv.animationName = "DoorOpen";
              mv.play({ repetitions: 1 });
            }, 2500),
          );
          // …step through into the warm light…
          timers.push(
            setTimeout(() => {
              mv.interpolationDecay = 150;
              mv.cameraTarget = "0.374m -0.06m 0.083m";
              mv.cameraOrbit = "180deg 88deg 0.12m";
              mv.fieldOfView = "18deg";
            }, 3500),
          );
          // …and the café becomes the app.
          timers.push(setTimeout(finish, 4800));
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
