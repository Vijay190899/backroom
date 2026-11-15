"use client";

import { useSyncExternalStore } from "react";

import { motionLevel, subscribeMotion, type MotionLevel } from "@/lib/motion-pref";

export function useMotionLevel(): MotionLevel {
  return useSyncExternalStore(subscribeMotion, motionLevel, () => "full");
}
