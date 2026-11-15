/**
 * The intro's first frame, rendered on the server so the app never flashes before it:
 * a warm sky and the wordmark. It is opaque HTML to React (not hydrated), so
 * `IntroPlayer` can mount the 3D café into `#intro-stage` and fade it out freely.
 * Shown only while `html[data-intro="play"]` (set before paint, once per session).
 */
const MARKUP = `<div id="intro" class="intro" aria-hidden="true">
  <div id="intro-stage" class="absolute inset-0"></div>
  <p class="intro-title"><span class="intro-mark" aria-hidden="true"></span>backroom</p>
  <p class="intro-credit">Café model: Shaun Glowa, CC-BY 3.0, via poly.pizza</p>
</div>`;

export function IntroOverlay() {
  return <div dangerouslySetInnerHTML={{ __html: MARKUP }} />;
}

const KEY = "backroom-intro";
/** Runs before first paint: play the intro once per session, never under reduced motion. */
// The 12 s timer is a safety net: if the player never loads, the app still opens.
export const introInitScript = `(function(){var h=document.documentElement;try{var seen=sessionStorage.getItem("${KEY}")||matchMedia("(prefers-reduced-motion: reduce)").matches;h.dataset.intro=seen?"done":"play";if(!seen)setTimeout(function(){h.dataset.intro="done"},12000)}catch(e){h.dataset.intro="done"}})()`;
export const INTRO_KEY = KEY;
