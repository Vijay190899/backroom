"use client";

import { useQuery } from "@tanstack/react-query";

import { API_URL } from "@/lib/api";

const KEY = "backroom-code";

/**
 * The demo access code (PRD §8.6): opening the app once with `?code=…` keeps it in this
 * browser and removes it from the address bar. With it, the API runs live; without it,
 * visitors get recorded runs (replay mode).
 */
export function accessCode(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const url = new URL(window.location.href);
    const fromUrl = url.searchParams.get("code");
    if (fromUrl) {
      window.localStorage.setItem(KEY, fromUrl);
      url.searchParams.delete("code");
      window.history.replaceState(null, "", url);
    }
    return window.localStorage.getItem(KEY);
  } catch {
    return null; // storage blocked: replay mode, which is the safe default
  }
}

/** Sent with every call that acts or teaches (the API checks it per request). */
export function accessHeaders(): Record<string, string> {
  const code = accessCode();
  return code ? { "X-Demo-Code": code } : {};
}

async function fetchMode(signal?: AbortSignal) {
  const [{ modeInfoSchema }, res] = await Promise.all([
    import("@/lib/contracts"),
    fetch(`${API_URL}/mode`, { signal, cache: "no-store", headers: accessHeaders() }),
  ]);
  if (!res.ok) throw new Error(`mode: ${res.status}`);
  return modeInfoSchema.parse(await res.json());
}

/** This visitor's mode: live (real runs) or replay (recorded runs), and why. */
export function useMode() {
  return useQuery({ queryKey: ["mode"], queryFn: ({ signal }) => fetchMode(signal), refetchInterval: 30_000 });
}
