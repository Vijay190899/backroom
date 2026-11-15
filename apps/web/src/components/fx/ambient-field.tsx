"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";

import { useMotionLevel } from "@/lib/use-motion-level";
import { isDark, subscribeTheme } from "@/lib/theme";

const VERT = `#version 300 es
in vec2 a;
void main() { gl_Position = vec4(a, 0.0, 1.0); }`;

const NOISE = `
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  mat2 r = mat2(0.8, -0.6, 0.6, 0.8);
  for (int i = 0; i < 5; i++) { v += a * noise(p); p = r * p * 2.03; a *= 0.5; }
  return v;
}`;

/**
 * Which picture sits behind the app. "cafe" is the café scene (L-76, experimental);
 * "ember" is the earlier abstract field (L-75). Switch back here if the scene is reverted.
 */
const SCENE: "cafe" | "ember" = "cafe";

// The earlier abstract field: domain-warped fbm in ember and amber (Inigo Quilez's warping).
const EMBER = `#version 300 es
precision highp float;
uniform vec2 uRes;
uniform float uTime;
uniform float uDark;
uniform float uScroll;
out vec4 o;
${NOISE}
void main() {
  vec2 p = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;
  float t = uTime * 0.035;
  vec2 q = vec2(fbm(p * 1.3 + t), fbm(p * 1.3 + vec2(5.2, 1.3) - t));
  vec2 r = vec2(fbm(p * 1.7 + 3.2 * q + vec2(1.7, 9.2) + 0.7 * t), fbm(p * 1.7 + 3.2 * q + vec2(8.3, 2.8) - 0.6 * t));
  float f = fbm(p * 1.5 + 3.4 * r);
  vec3 ember = vec3(1.0, 0.48, 0.27);
  vec3 amber = vec3(1.0, 0.71, 0.28);
  vec3 wine = vec3(0.32, 0.07, 0.05);
  float glow = smoothstep(0.42, 1.05, f);
  vec3 dark = vec3(0.039, 0.035, 0.031) + wine * glow * 0.55 + mix(ember, amber, r.x) * (glow * glow) * 0.16;
  vec3 lite = vec3(0.957, 0.945, 0.925) - vec3(0.0, 0.05, 0.09) * glow * 0.55 + mix(ember, amber, r.y) * glow * 0.06;
  vec3 col = mix(lite, dark, uDark);
  col *= mix(1.0, smoothstep(1.25, 0.25, length(p)), 0.35 * uDark);
  col += (hash(gl_FragCoord.xy + uTime) - 0.5) / 255.0 * 2.0;
  o = vec4(col, 1.0);
}`;

// The café: an espresso-and-crema (dark) or latte-foam (light) field, out-of-focus café
// lights drifting at the edges (kept off the reading column), steam rising from cups
// below the fold, and a sparse scatter of coffee beans that drifts with the scroll.
const CAFE = `#version 300 es
precision highp float;
uniform vec2 uRes;
uniform float uTime;
uniform float uDark;
uniform float uScroll;
out vec4 o;
${NOISE}

vec3 bokeh(vec2 p, float t, vec3 a, vec3 b, float aspect) {
  vec3 acc = vec3(0.0);
  for (int i = 0; i < 18; i++) {
    float fi = float(i);
    vec2 h = vec2(hash(vec2(fi, 1.3)), hash(vec2(fi, 7.1)));
    // Spread across the width, but pushed toward the sides.
    float side = h.x < 0.5 ? -1.0 : 1.0;
    float x = side * mix(0.32, 0.98, fract(h.x * 2.0)) * aspect * 0.5 * 1.05;
    vec2 c = vec2(x, (h.y - 0.5) * 1.25);
    c += 0.05 * vec2(sin(t * 0.21 + fi), cos(t * 0.17 + fi * 1.7));
    c.y = mod(c.y + uScroll * (0.15 + 0.35 * h.y) + 0.8, 1.6) - 0.8;
    float r = mix(0.035, 0.13, hash(vec2(fi, 3.7)));
    float d = length(p - c);
    float disc = smoothstep(r, r * 0.86, d);
    float rim = smoothstep(r * 0.62, r * 0.97, d) * disc;
    float tw = 0.65 + 0.35 * sin(t * 0.6 + fi * 2.3);
    vec3 col = mix(a, b, hash(vec2(fi, 9.9)));
    acc += col * (disc * 0.3 + rim * 0.16) * tw;
  }
  return acc;
}

float steam(vec2 p, float t) {
  float s = 0.0;
  for (int i = 0; i < 3; i++) {
    float fi = float(i);
    float x0 = (fi - 1.0) * 0.82 + 0.08 * sin(fi * 4.0);
    float y = p.y + 0.62;
    float sway = 0.14 * sin(y * 2.4 - t * 0.8 + fi * 2.0) * y;
    float dx = p.x - x0 - sway;
    float width = 0.04 + 0.2 * clamp(y, 0.0, 1.5);
    float column = exp(-dx * dx / (width * width));
    float n = fbm(vec2(dx * 4.5 + fi * 10.0, y * 2.3 - t * 0.5));
    float fade = smoothstep(-0.05, 0.3, y) * smoothstep(1.7, 0.5, y);
    s += column * smoothstep(0.42, 0.85, n) * fade;
  }
  return s;
}

float beans(vec2 p, float t) {
  p.y -= uScroll * 0.35 - t * 0.008;
  vec2 g = p * 3.4;
  vec2 id = floor(g);
  vec2 f = fract(g) - 0.5;
  float keep = step(0.74, hash(id));
  float a = hash(id + 3.1) * 6.283 + t * 0.02 * (hash(id + 8.0) - 0.5);
  mat2 R = mat2(cos(a), -sin(a), sin(a), cos(a));
  vec2 q = R * (f - (vec2(hash(id + 1.7), hash(id + 5.3)) - 0.5) * 0.4);
  q *= vec2(1.0, 1.42);
  float d = length(q) - 0.14;
  float body = smoothstep(0.012, -0.012, d);
  float crease = smoothstep(0.02, 0.0, abs(q.x + 0.035 * sin(q.y * 22.0))) * step(abs(q.y), 0.12);
  return keep * body * (1.0 - 0.85 * crease);
}

void main() {
  vec2 p = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;
  float aspect = uRes.x / uRes.y;
  float t = uTime;
  float w = t * 0.03;
  vec2 q = vec2(fbm(p * 1.2 + w), fbm(p * 1.2 + vec2(5.2, 1.3) - w));
  vec2 r = vec2(fbm(p * 1.6 + 3.0 * q + vec2(1.7, 9.2) + 0.5 * w), fbm(p * 1.6 + 3.0 * q + vec2(8.3, 2.8) - 0.4 * w));
  float f = fbm(p * 1.4 + 3.2 * r);
  float st = steam(p, t);
  float bn = beans(p, t);

  // Espresso and crema
  vec3 dark = vec3(0.036, 0.028, 0.022) + vec3(0.30, 0.15, 0.07) * smoothstep(0.45, 1.0, f) * 0.45;
  dark = mix(dark, vec3(0.13, 0.075, 0.045), bn * 0.55);
  dark += bokeh(p, t, vec3(1.0, 0.48, 0.27), vec3(1.0, 0.74, 0.42), aspect) * 0.16;
  dark += vec3(0.95, 0.86, 0.76) * st * 0.055;

  // Latte foam, caramel veins, morning light
  vec3 milk = vec3(0.968, 0.948, 0.918);
  vec3 latte = vec3(0.905, 0.815, 0.69);
  float swirl = smoothstep(0.35, 0.95, f);
  vec3 lite = mix(milk, latte, swirl * 0.55);
  float vein = smoothstep(0.6, 0.66, f) - smoothstep(0.66, 0.76, f);
  lite = mix(lite, vec3(0.78, 0.55, 0.33), vein * 0.18);
  lite = mix(lite, vec3(0.6, 0.4, 0.25), bn * 0.09);
  lite += bokeh(p, t, vec3(1.0, 0.86, 0.62), vec3(1.0, 0.97, 0.9), aspect) * 0.09;
  lite = mix(lite, vec3(1.0), clamp(st * 0.32, 0.0, 0.5));

  vec3 col = mix(lite, dark, uDark);
  col *= mix(1.0, smoothstep(1.3, 0.25, length(p)), 0.3 * uDark);
  col += (hash(gl_FragCoord.xy + uTime) - 0.5) / 255.0 * 2.0;
  o = vec4(col, 1.0);
}`;

const FRAG = SCENE === "cafe" ? CAFE : EMBER;

function compile(gl: WebGL2RenderingContext, type: number, src: string): WebGLShader | null {
  const sh = gl.createShader(type);
  if (!sh) return null;
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  return gl.getShaderParameter(sh, gl.COMPILE_STATUS) ? sh : null;
}

/**
 * The picture behind everything (see SCENE): half resolution, 30 fps, paused in hidden
 * tabs, one still frame under reduced motion. Purely decorative (aria-hidden); without
 * WebGL2 the plain background shows.
 */
export function AmbientField() {
  const canvas = useRef<HTMLCanvasElement>(null);
  const level = useMotionLevel();
  const dark = useSyncExternalStore(subscribeTheme, isDark, () => true);
  // Read live by the render loop, so a theme or motion change never rebuilds the context.
  const live = useRef({ level, dark, wake: () => {} });

  useEffect(() => {
    live.current.level = level;
    live.current.dark = dark;
    live.current.wake();
  }, [level, dark]);

  useEffect(() => {
    const el = canvas.current;
    const gl = el?.getContext("webgl2", { antialias: false, alpha: false, powerPreference: "low-power" });
    if (!el || !gl) return;
    const vs = compile(gl, gl.VERTEX_SHADER, VERT);
    const fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    const prog = gl.createProgram();
    if (!vs || !fs || !prog) return;
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "a");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    const uRes = gl.getUniformLocation(prog, "uRes");
    const uTime = gl.getUniformLocation(prog, "uTime");
    const uScroll = gl.getUniformLocation(prog, "uScroll");
    const uDark = gl.getUniformLocation(prog, "uDark");

    const scale = 0.5;
    const start = performance.now();
    let frame = 0;
    let last = 0;

    const draw = (now: number) => {
      gl.uniform2f(uRes, el.width, el.height);
      gl.uniform1f(uTime, (now - start) / 1000);
      gl.uniform1f(uScroll, scrollY / Math.max(1, innerHeight));
      gl.uniform1f(uDark, live.current.dark ? 1 : 0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    };
    const loop = (now: number) => {
      if (live.current.level !== "full") {
        frame = 0;
        draw(start + 40_000); // reduced motion: one still frame, 40 s in (a settled look)
        return;
      }
      frame = requestAnimationFrame(loop);
      if (document.hidden || now - last < 33) return;
      last = now;
      draw(now);
    };
    const wake = () => {
      if (!frame) frame = requestAnimationFrame(loop);
    };
    const state = live.current;
    state.wake = wake;

    const resize = () => {
      el.width = Math.max(1, Math.floor(innerWidth * scale));
      el.height = Math.max(1, Math.floor(innerHeight * scale));
      gl.viewport(0, 0, el.width, el.height);
      wake();
    };
    resize();
    addEventListener("resize", resize);
    el.dataset.ready = "1";
    // A lost context would leave an opaque black canvas: fade it out instead.
    const onLost = () => delete el.dataset.ready;
    el.addEventListener("webglcontextlost", onLost);

    return () => {
      cancelAnimationFrame(frame);
      state.wake = () => {};
      removeEventListener("resize", resize);
      el.removeEventListener("webglcontextlost", onLost);
    };
  }, []);

  return (
    <canvas
      ref={canvas}
      aria-hidden
      style={{ viewTransitionName: "ambient" }}
      className="pointer-events-none fixed inset-0 -z-10 size-full opacity-0 transition-opacity duration-[1200ms] data-[ready]:opacity-100"
    />
  );
}
