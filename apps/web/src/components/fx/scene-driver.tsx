"use client";

import { useEffect } from "react";

import { useCachedBrief } from "@/lib/brief";
import { setRaining } from "@/lib/scene";

/**
 * Weather in the café scene follows the business data on every page: it rains when the
 * brief carries a rain forecast (the weather card's `rain_mm`). It only reads the shared
 * cache (filled by the Today page or the idle prefetch), so it never fetches on its own.
 */
export function SceneDriver() {
  const { data } = useCachedBrief();
  const rain = data?.brief.cards.some((c) =>
    c.numbers.some((n) => n.key === "rain_mm" && n.value > 0),
  );
  useEffect(() => {
    setRaining(Boolean(rain));
  }, [rain]);
  return null;
}
