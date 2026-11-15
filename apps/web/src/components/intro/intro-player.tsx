"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { afterFirstData } from "@/lib/brief";

import { INTRO_KEY } from "./intro-overlay";

type ModelViewer = HTMLElement & {
  cameraOrbit: string;
  fieldOfView: string;
  interpolationDecay: number;
};

/**
 * Walks you into the café: a 3D shop (CC-BY 3.0, Shaun Glowa) seen from a three-quarter
 * view, orbiting round to its front, then the camera pushes in toward the door and the
 * scene dissolves into the app. About four seconds; Skip ends it at once.
 */
export function IntroPlayer() {
  const [active] = useState(() => document.documentElement.dataset.intro === "play");
  const [leaving, setLeaving] = useState(false);
  const finishRef = useRef<() => void>(() => {});
  const skipRef = useRef<HTMLButtonElement>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!active) return;
    const root = document.getElementById("intro");
    const stage = document.getElementById("intro-stage");
    if (!root || !stage) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    let done = false;
    // The only control on screen while it plays, so keyboard users can leave at once.
    skipRef.current?.focus({ preventScroll: true });

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
      setLeaving(true);
      // Not tracked: once leaving starts, the app must open even if this unmounts.
      setTimeout(() => (document.documentElement.dataset.intro = "done"), 750);
    };
    finishRef.current = finish;

    // Never hold the app hostage: if the model is slow, go straight in.
    timers.push(setTimeout(finish, 7000));

    // The page's own data goes first (it is what paints under the intro).
    afterFirstData(queryClient, 1500)
      .then(() => import("@google/model-viewer"))
      .then(() => {
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
          // …then walk up to the door…
          timers.push(
            setTimeout(() => {
              mv.interpolationDecay = 180;
              mv.cameraOrbit = "180deg 87deg 28%";
              mv.fieldOfView = "16deg";
            }, 2300),
          );
          // …and step inside.
          timers.push(setTimeout(finish, 3500));
        });
        stage.appendChild(mv);
      })
      .catch(finish);

    return () => {
      done = true;
      timers.forEach(clearTimeout);
    };
  }, [active, queryClient]);

  if (!active || leaving) return null;
  return (
    <button ref={skipRef} type="button" onClick={() => finishRef.current()} className="intro-skip">
      Skip intro
    </button>
  );
}
