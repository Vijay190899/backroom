"use client";

import {
  Bean,
  CakeSlice,
  Coffee,
  Cookie,
  Croissant,
  CupSoda,
  Leaf,
  Milk,
  Truck,
  Wheat,
  type LucideIcon,
} from "lucide-react";
import { useId, useState } from "react";

import { useScene } from "@/lib/scene";
import { cn } from "@/lib/utils";

type Glyph = { Icon: LucideIcon; x: number; y: number; r: number };

// Two tiles of line-drawn café things. Glyphs sit inside the tile with a margin, so the
// pattern repeats without clipped edges; rotations are fixed, so the field never jitters.
const NEAR: { size: number; icon: number; glyphs: Glyph[] } = {
  size: 380,
  icon: 30,
  glyphs: [
    { Icon: Coffee, x: 28, y: 34, r: -8 },
    { Icon: Croissant, x: 214, y: 22, r: 14 },
    { Icon: Bean, x: 128, y: 118, r: 32 },
    { Icon: Milk, x: 300, y: 128, r: -6 },
    { Icon: CakeSlice, x: 40, y: 214, r: 10 },
    { Icon: Wheat, x: 196, y: 236, r: -18 },
    { Icon: Bean, x: 312, y: 300, r: -40 },
    { Icon: CupSoda, x: 112, y: 318, r: 6 },
  ],
};
const FAR: { size: number; icon: number; glyphs: Glyph[] } = {
  size: 270,
  icon: 18,
  glyphs: [
    { Icon: Bean, x: 70, y: 30, r: 20 },
    { Icon: Leaf, x: 200, y: 64, r: -30 },
    { Icon: Cookie, x: 24, y: 150, r: 0 },
    { Icon: Bean, x: 150, y: 168, r: -52 },
    { Icon: Coffee, x: 226, y: 226, r: 12 },
    { Icon: Bean, x: 96, y: 236, r: 64 },
  ],
};

function Tile({ id, tile }: { id: string; tile: typeof NEAR }) {
  return (
    <pattern id={id} width={tile.size} height={tile.size} patternUnits="userSpaceOnUse">
      {tile.glyphs.map(({ Icon, x, y, r }, i) => (
        <g key={i} transform={`rotate(${r} ${x + tile.icon / 2} ${y + tile.icon / 2})`}>
          <Icon x={x} y={y} width={tile.icon} height={tile.icon} strokeWidth={2.45} absoluteStrokeWidth />
        </g>
      ))}
    </pattern>
  );
}

/** One drifting layer: an oversized pattern moved by exactly one tile, so the loop is seamless. */
function Layer({ id, tile, className }: { id: string; tile: typeof NEAR; className: string }) {
  return (
    <svg
      className={cn("cafe-layer", className)}
      style={{ "--tile": `${tile.size}px` } as React.CSSProperties}
      width="100%"
      height="100%"
    >
      <defs>
        <Tile id={id} tile={tile} />
      </defs>
      <rect width="100%" height="100%" fill={`url(#${id})`} />
    </svg>
  );
}

/**
 * The café behind every page (L-82): line-drawn coffee, beans, croissants and milk at a
 * whisper of contrast, drifting slowly in two depths and fading out behind the content
 * column, so it never competes with the data. It still follows the business: fine rain
 * when the brief forecasts rain, the field warms while the agent works, a delivery van
 * crosses the bottom on a supplier order, a cup rises when a run finishes. Static under
 * reduced motion.
 */
export function CafePattern() {
  const { raining, busy, deliveries, serves } = useScene();
  // A finished trip unmounts the van; trips from before this mount never replay.
  const [lastTrip, setLastTrip] = useState(deliveries);
  const [lastServe] = useState(serves);
  const id = useId();

  return (
    <div
      aria-hidden
      style={{ viewTransitionName: "ambient" }}
      className={cn("cafe-pattern pointer-events-none fixed inset-0 -z-10 overflow-hidden", busy && "is-busy")}
    >
      <div className="cafe-field absolute inset-0">
        <Layer id={`${id}far`} tile={FAR} className="cafe-layer-far" />
        <Layer id={`${id}near`} tile={NEAR} className="cafe-layer-near" />
      </div>
      <div className={cn("cafe-rainfall absolute inset-0", raining && "is-on")} />
      {deliveries !== lastTrip ? (
        <span
          key={deliveries}
          className="cafe-truck"
          onAnimationEnd={(e) => e.animationName === "cafe-truck" && setLastTrip(deliveries)}
        >
          <Truck strokeWidth={2.45} absoluteStrokeWidth className="size-full" />
        </span>
      ) : null}
      {serves !== lastServe ? (
        <span key={serves} className="cafe-serve">
          <Coffee strokeWidth={2.45} absoluteStrokeWidth className="size-full" />
        </span>
      ) : null}
    </div>
  );
}
