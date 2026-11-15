"use client";

import { useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { afterFirstData } from "@/lib/brief";

const CafeScene = dynamic(() => import("./cafe-scene").then((m) => m.CafeScene), { ssr: false });

/**
 * The hero band at the top of every page (L-79): a small window onto the café, above the
 * page's content and never behind it. It runs from under the floating header to just
 * above the headline and stays put across page changes (the layout owns it). The sky is
 * server-rendered so nothing shifts; the animated scene (half a megabyte of runtime)
 * fades in once the page's first data has painted.
 */
export function CafeHero() {
  const queryClient = useQueryClient();
  const [scene, setScene] = useState(false);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let live = true;
    void afterFirstData(queryClient, 1500).then(() => {
      if (live) timer = setTimeout(() => setScene(true), 600);
    });
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [queryClient]);
  return (
    <div aria-hidden style={{ viewTransitionName: "ambient" }} className="cafe-hero">
      <div className="cafe-sky absolute inset-0" />
      {scene ? <CafeScene /> : null}
    </div>
  );
}
