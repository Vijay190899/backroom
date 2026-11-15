"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";

import { useMotionLevel } from "@/lib/use-motion-level";
import { isDark, subscribeTheme } from "@/lib/theme";

const VERT = `#version 300 es
in vec2 a;
void main() { gl_Position = vec4(a, 0.0, 1.0); }`;

// Domain-warped fbm (Inigo Quilez's warping) in ember and amber, very low in the dark so
// text on glass keeps its contrast; a soft light follows the pointer; grain kills banding.
const FRAG = `#version 300 es
precision highp float;
uniform vec2 uRes;
uniform float uTime;
uniform vec2 uMouse;
uniform float uDark;
out vec4 o;

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
}

void main() {
  vec2 p = (gl_FragCoord.xy - 0.5 * uRes) / uRes.y;
  float t = uTime * 0.035;
  vec2 q = vec2(fbm(p * 1.3 + t), fbm(p * 1.3 + vec2(5.2, 1.3) - t));
  vec2 r = vec2(fbm(p * 1.7 + 3.2 * q + vec2(1.7, 9.2) + 0.7 * t), fbm(p * 1.7 + 3.2 * q + vec2(8.3, 2.8) - 0.6 * t));
  float f = fbm(p * 1.5 + 3.4 * r);

  vec3 ember = vec3(1.0, 0.48, 0.27);
  vec3 amber = vec3(1.0, 0.71, 0.28);
  vec3 wine = vec3(0.32, 0.07, 0.05);

  vec3 bgD = vec3(0.039, 0.035, 0.031);
  vec3 bgL = vec3(0.957, 0.945, 0.925);
  float glow = smoothstep(0.42, 1.05, f);
  float vein = smoothstep(0.55, 0.62, f) - smoothstep(0.62, 0.72, f);

  vec2 m = (uMouse - 0.5 * uRes) / uRes.y;
  float light = exp(-3.2 * length(p - m));

  vec3 dark = bgD + wine * glow * 0.55 + mix(ember, amber, r.x) * (glow * glow) * 0.16 + ember * vein * 0.05 + ember * light * 0.07;
  vec3 lite = bgL - vec3(0.0, 0.05, 0.09) * glow * 0.55 + mix(ember, amber, r.y) * glow * 0.06 + ember * light * 0.04;
  vec3 col = mix(lite, dark, uDark);

  float vig = smoothstep(1.25, 0.25, length(p));
  col *= mix(1.0, vig, 0.35 * uDark);
  col += (hash(gl_FragCoord.xy + uTime) - 0.5) / 255.0 * 2.0;
  o = vec4(col, 1.0);
}`;

function compile(gl: WebGL2RenderingContext, type: number, src: string): WebGLShader | null {
  const sh = gl.createShader(type);
  if (!sh) return null;
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  return gl.getShaderParameter(sh, gl.COMPILE_STATUS) ? sh : null;
}

/**
 * The light behind everything: a slow ember field at half resolution, 30 fps, paused in
 * hidden tabs, one still frame in calm mode. Purely decorative (aria-hidden); without
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
    const uMouse = gl.getUniformLocation(prog, "uMouse");
    const uDark = gl.getUniformLocation(prog, "uDark");

    const scale = 0.5;
    const target = { x: innerWidth * 0.7, y: innerHeight * 0.3 };
    const mouse = { ...target };
    const start = performance.now();
    let frame = 0;
    let last = 0;

    const draw = (now: number) => {
      mouse.x += (target.x - mouse.x) * 0.06;
      mouse.y += (target.y - mouse.y) * 0.06;
      gl.uniform2f(uRes, el.width, el.height);
      gl.uniform1f(uTime, (now - start) / 1000);
      gl.uniform2f(uMouse, mouse.x * scale, (innerHeight - mouse.y) * scale);
      gl.uniform1f(uDark, live.current.dark ? 1 : 0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    };
    const loop = (now: number) => {
      if (live.current.level !== "full") {
        frame = 0;
        draw(start + 40_000); // calm: one still frame
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
    const onMove = (e: PointerEvent) => {
      target.x = e.clientX;
      target.y = e.clientY;
    };
    resize();
    addEventListener("resize", resize);
    addEventListener("pointermove", onMove, { passive: true });
    el.dataset.ready = "1";
    // A lost context would leave an opaque black canvas: fade it out instead.
    const onLost = () => delete el.dataset.ready;
    el.addEventListener("webglcontextlost", onLost);

    return () => {
      cancelAnimationFrame(frame);
      state.wake = () => {};
      removeEventListener("resize", resize);
      removeEventListener("pointermove", onMove);
      el.removeEventListener("webglcontextlost", onLost);
    };
  }, []);

  return (
    <canvas
      ref={canvas}
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 size-full opacity-0 transition-opacity duration-[1200ms] data-[ready]:opacity-100"
    />
  );
}
