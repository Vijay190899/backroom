/**
 * The particle engine behind the "explode into the dock" and "materialise" moments. One
 * full-screen 2D canvas (mounted by <ParticleLayer>), up to a few thousand particles,
 * additive glow in the dark theme. Elements are sampled from what they really show: the
 * text of every `[data-particle-text]` node, drawn with its own font and colour, plus a
 * sparse dust of the panel itself. Nothing here invents content; it re-draws the element.
 */

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  tx: number; // target (attract phase / materialise)
  ty: number;
  size: number;
  color: string;
  life: number; // 0..1 remaining for fades
  delay: number; // ms before it starts moving
};

type Effect = {
  kind: "explode" | "form";
  particles: Particle[];
  start: number;
  done: boolean;
  arrived: number;
  onArrive?: () => void;
  onDone?: () => void;
  fired: boolean;
};

let canvas: HTMLCanvasElement | null = null;
let ctx: CanvasRenderingContext2D | null = null;
let effects: Effect[] = [];
let frame = 0;
let lastTick = 0;
let dpr = 1;
const BURST_MS = 620;

export function attachParticleCanvas(el: HTMLCanvasElement | null): void {
  canvas = el;
  ctx = el?.getContext("2d") ?? null;
  resize();
}

function resize() {
  if (!canvas) return;
  dpr = Math.min(2, devicePixelRatio || 1);
  canvas.width = Math.floor(innerWidth * dpr);
  canvas.height = Math.floor(innerHeight * dpr);
}
if (typeof window !== "undefined") addEventListener("resize", resize);

function isDarkTheme(): boolean {
  return document.documentElement.classList.contains("dark");
}

/**
 * Pixels of an element as it looks: its panel (rounded rect in the glass tint), then the
 * text of each `[data-particle-text]` child in its computed font and colour, wrapped to
 * the child's width. Returns screen-space points with colours.
 */
function sample(el: HTMLElement, step: number): { x: number; y: number; color: string }[] {
  const rect = el.getBoundingClientRect();
  const w = Math.max(1, Math.ceil(rect.width));
  const h = Math.max(1, Math.ceil(rect.height));
  const off = document.createElement("canvas");
  off.width = w;
  off.height = h;
  const c = off.getContext("2d", { willReadFrequently: true });
  if (!c) return [];

  // Panel dust: an outline and a faint fill, so the card's shape is part of the burst.
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--t-accent").trim() || "#ff7a45";
  c.strokeStyle = accent;
  c.lineWidth = 2;
  c.beginPath();
  if (c.roundRect) c.roundRect(1, 1, w - 2, h - 2, 20);
  else c.rect(1, 1, w - 2, h - 2);
  c.stroke();

  for (const node of el.querySelectorAll<HTMLElement>("[data-particle-text]")) {
    const r = node.getBoundingClientRect();
    const cs = getComputedStyle(node);
    c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    c.fillStyle = cs.color;
    c.textBaseline = "top";
    const lineHeight = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
    const words = (node.textContent ?? "").replace(/\s+/g, " ").trim().split(" ");
    let line = "";
    let y = r.top - rect.top;
    const x = r.left - rect.left;
    for (const word of words) {
      const next = line ? `${line} ${word}` : word;
      if (c.measureText(next).width > r.width && line) {
        c.fillText(line, x, y);
        line = word;
        y += lineHeight;
      } else line = next;
    }
    if (line) c.fillText(line, x, y);
  }

  const data = c.getImageData(0, 0, w, h).data;
  const points: { x: number; y: number; color: string }[] = [];
  for (let y = 0; y < h; y += step) {
    for (let x = 0; x < w; x += step) {
      const i = (y * w + x) * 4;
      if (data[i + 3] > 90) {
        points.push({ x: rect.left + x, y: rect.top + y, color: `rgb(${data[i]},${data[i + 1]},${data[i + 2]})` });
      }
    }
  }
  return points;
}

function ensureLoop() {
  if (!frame) frame = requestAnimationFrame(tick);
}

function tick(now: number) {
  frame = 0;
  if (!ctx || !canvas) return;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, innerWidth, innerHeight);
  ctx.globalCompositeOperation = isDarkTheme() ? "lighter" : "source-over";

  // Physics in 60 fps steps, so the effect lasts the same time on any display.
  const f = lastTick ? Math.min(3, (now - lastTick) / 16.67) : 1;
  lastTick = now;
  for (const fx of effects) {
    const t = now - fx.start;
    let alive = 0;
    for (const p of fx.particles) {
      if (p.life <= 0) continue;
      alive++;
      if (t < p.delay) {
        ctx.globalAlpha = 1;
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
        continue;
      }
      if (fx.kind === "explode") {
        const k = t - p.delay;
        if (k < BURST_MS) {
          // Burst: fly apart, with a little drag.
          p.vx *= 0.955 ** f;
          p.vy = p.vy * 0.955 ** f + 0.04 * f;
        } else {
          // Stream: curl toward the dock, accelerating.
          const dx = p.tx - p.x;
          const dy = p.ty - p.y;
          const d = Math.hypot(dx, dy) || 1;
          const pull = Math.min(2.2, 0.2 + (k - BURST_MS) / 420);
          p.vx = p.vx * 0.86 ** f + ((dx / d) * pull * 2.2 + (-dy / d) * 0.9) * f;
          p.vy = p.vy * 0.86 ** f + ((dy / d) * pull * 2.2 + (dx / d) * 0.9) * f;
          if (d < 14 + Math.hypot(p.vx, p.vy) * f) {
            p.life = 0;
            fx.arrived++;
            continue;
          }
        }
      } else {
        // Form: spring onto the target pixel, then fade as the real element appears.
        const k = t - p.delay;
        p.vx = (p.vx + (p.tx - p.x) * 0.08 * f) * 0.78 ** f;
        p.vy = (p.vy + (p.ty - p.y) * 0.08 * f) * 0.78 ** f;
        if (k > 900) p.life -= 0.06 * f;
      }
      p.x += p.vx * f;
      p.y += p.vy * f;
      ctx.globalAlpha = Math.max(0, Math.min(1, p.life));
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x, p.y, p.size, p.size);
    }
    ctx.globalAlpha = 1;
    const total = fx.particles.length || 1;
    if (!fx.fired && (fx.arrived / total > 0.55 || (fx.kind === "form" && t > 750))) {
      fx.fired = true;
      fx.onArrive?.();
    }
    if (!alive || t > 4000) {
      fx.done = true;
      fx.onDone?.();
    }
  }
  effects = effects.filter((fx) => !fx.done);
  if (effects.length) ensureLoop();
  else {
    lastTick = 0;
    ctx.clearRect(0, 0, innerWidth, innerHeight);
  }
}

const MAX_PARTICLES = 7000;

/** Sample every other pixel, then thin at random to the budget (text is sparse). */
function points(el: HTMLElement) {
  const all = sample(el, 2);
  if (all.length <= MAX_PARTICLES) return all;
  const keep = MAX_PARTICLES / all.length;
  return all.filter(() => Math.random() < keep);
}

/**
 * Break `el` into particles that burst, then stream into `target` (screen point).
 * `onArrive` fires when most have landed (the dock reacts); returns false if there is no
 * particle canvas (the caller just skips the effect).
 */
export function explodeInto(
  el: HTMLElement,
  target: { x: number; y: number },
  onArrive?: () => void,
): boolean {
  if (!ctx) return false;
  const pts = points(el);
  const r = el.getBoundingClientRect();
  const cx = r.left + r.width / 2;
  const cy = r.top + r.height / 2;
  const particles = pts.map((pt) => {
    const a = Math.atan2(pt.y - cy, pt.x - cx) + (Math.random() - 0.5) * 0.8;
    const speed = 1.5 + Math.random() * 9;
    return {
      x: pt.x,
      y: pt.y,
      vx: Math.cos(a) * speed,
      vy: Math.sin(a) * speed - 1.5,
      tx: target.x + (Math.random() - 0.5) * 10,
      ty: target.y + (Math.random() - 0.5) * 10,
      size: Math.random() < 0.12 ? 3 : 1.8,
      color: pt.color,
      life: 1,
      delay: Math.random() * 160,
    };
  });
  effects.push({ kind: "explode", particles, start: performance.now(), done: false, arrived: 0, onArrive, fired: false });
  ensureLoop();
  return true;
}

/**
 * Assemble `el` out of particles flying in from `from` (screen point): the inverse of an
 * explosion, for a card that has just been rebuilt. `onArrive` fires when the shape has
 * formed, so the caller can show the real element underneath.
 */
export function formFrom(el: HTMLElement, from: { x: number; y: number }, onArrive?: () => void): boolean {
  if (!ctx) return false;
  const particles = points(el).map((pt) => ({
    x: from.x + (Math.random() - 0.5) * 160,
    y: from.y + (Math.random() - 0.5) * 160,
    vx: (Math.random() - 0.5) * 18,
    vy: (Math.random() - 0.5) * 18,
    tx: pt.x,
    ty: pt.y,
    size: 1.8,
    color: pt.color,
    life: 1.4,
    delay: Math.random() * 220,
  }));
  effects.push({ kind: "form", particles, start: performance.now(), done: false, arrived: 0, onArrive, fired: false });
  ensureLoop();
  return true;
}
