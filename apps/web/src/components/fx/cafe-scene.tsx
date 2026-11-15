"use client";

import { DotLottieWorkerReact, setWasmUrl, type DotLottieWorkerReactProps } from "@lottiefiles/dotlottie-react";
import { useState } from "react";

import { useScene } from "@/lib/scene";
import { useMotionLevel } from "@/lib/use-motion-level";
import { cn } from "@/lib/utils";

// The player's WebAssembly is served from this app, not a CDN.
setWasmUrl("/scene/dotlottie-player.wasm");

/**
 * Every animation renders in one shared worker (off the main thread, so the page stays
 * responsive) at 1x pixel density: the scene is faded and blurred, extra pixels buy nothing.
 */
function Anim(props: Omit<DotLottieWorkerReactProps, "workerId" | "renderConfig">) {
  return <DotLottieWorkerReact workerId="cafe-scene" renderConfig={{ devicePixelRatio: 1 }} {...props} />;
}

/**
 * The café behind the app (L-78): an illustrated scene, softened into the background,
 * always moving, and driven by what the app is doing: rain when the brief carries a
 * rain forecast, a delivery van (people-sized) when a supplier order is approved, the
 * barista working faster while the agent runs, a cup served when a run finishes.
 * Under reduced motion it holds still on each animation's first frame.
 * Animations: LottieFiles (Lottie Simple License).
 */
export function CafeScene() {
  const { raining, busy, deliveries, serves } = useScene();
  const play = useMotionLevel() !== "calm";
  // Each delivery is its own van (keyed): it drives in, waits and drives off (CSS), so a
  // second order mid-trip starts a fresh van from the left instead of reversing this one.
  // A finished trip unmounts the van; trips from before this mount never replay.
  const [lastTrip, setLastTrip] = useState(deliveries);

  return (
    <div
      aria-hidden
      style={{ viewTransitionName: "ambient" }}
      className={cn("cafe-scene pointer-events-none fixed inset-0 -z-10 overflow-hidden", raining && "is-raining")}
    >
      <div className="cafe-sky absolute inset-0" />
      <Anim src="/scene/clouds.lottie" autoplay={play} loop speed={raining ? 1.6 : 0.6} className="cafe-cloud cafe-cloud-a" />
      <Anim src="/scene/clouds.lottie" autoplay={play} loop speed={raining ? 1.6 : 0.6} className="cafe-cloud cafe-cloud-b" />

      <div className="cafe-stage">
        <div className="cafe-ground" />
        <Anim src="/scene/cafe.lottie" autoplay={play} loop speed={busy ? 1.7 : 1} className="cafe-shop" />
        <Anim src="/scene/steam-cup.lottie" autoplay={play} loop className="cafe-steam" />
        {serves ? (
          <Anim key={serves} src="/scene/served-cup.lottie" autoplay={play} loop className="cafe-served" />
        ) : null}
        {deliveries !== lastTrip ? (
          <div
            key={deliveries}
            className="cafe-van is-trip"
            onAnimationEnd={(e) => e.animationName === "van-out" && setLastTrip(deliveries)}
          >
            <Anim src="/scene/van.lottie" autoplay={play} loop className="size-full" />
          </div>
        ) : null}
      </div>

      <div className="cafe-rain absolute inset-0" />
      <div className="cafe-veil absolute inset-0" />
    </div>
  );
}
