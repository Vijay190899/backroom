"""Record the README showcase from the live site.

    uv run --with pillow --with imageio-ffmpeg python scripts/showcase.py [--url URL]

Story: the morning brief -> tap Approve -> the agent's run (a warm replay, $0) -> "watch it
heal at seed 7" (the recorded run on a redesigned portal, real browser frames) -> the bench.
It drives the public site in replay mode: no access code, no model calls, nothing changes on
the server. Writes docs/assets/showcase.webp (plays inline in the README) and
var/showcase.mp4 (for sharing).
"""

import argparse
import asyncio
import base64
import io
import time
from pathlib import Path
from typing import Any

from playwright.async_api import Locator, Page, async_playwright

ROOT = Path(__file__).resolve().parents[1]
W, H, DSF = 1280, 800, 1.5  # rendered at 1.5x, written at 1280x800: crisp text

CURSOR_JS = """
(() => {
  const install = () => {
    if (document.getElementById('__cursor')) return;
    const c = document.createElement('div');
    c.id = '__cursor';
    c.style.cssText = 'position:fixed;left:0;top:0;width:24px;height:24px;margin:-12px 0 0 -12px;'
      + 'border-radius:50%;background:rgba(200,116,43,.28);border:2px solid #c8742b;'
      + 'box-shadow:0 2px 10px rgba(0,0,0,.18);z-index:2147483647;pointer-events:none;'
      + 'transition:translate .75s cubic-bezier(.2,.7,.2,1);translate:' + (window.__cx || 900)
      + 'px ' + (window.__cy || 560) + 'px';
    document.documentElement.appendChild(c);
  };
  window.__cursorMove = (x, y) => { window.__cx = x; window.__cy = y; install();
    document.getElementById('__cursor').style.translate = x + 'px ' + y + 'px'; };
  window.__cursorPress = () => document.getElementById('__cursor')
    .animate([{ scale: 1 }, { scale: 0.65 }, { scale: 1 }], { duration: 320 });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();
"""

SETUP_JS = """
try {
  localStorage.setItem('backroom-theme', 'light');
  sessionStorage.setItem('backroom-intro', '1');
} catch (e) {}
"""

# A calmer frame for a compressed video: no particle bursts or delivery van, a still
# background. (The run screen's own canvas is untouched.)
CALM_CSS = """
canvas[style*="particles"], .cafe-truck { display: none !important; }
.cafe-pattern, .cafe-pattern * { animation-play-state: paused !important; }
"""
HIDE_DOCK_CSS = '[aria-label="Agent"] { display: none !important; }'


class Recorder:
    """Chrome's screencast (CDP): JPEG frames with their timestamps."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.frames: list[tuple[float, bytes]] = []
        self._acks: set[asyncio.Future[Any]] = set()

    async def start(self) -> None:
        self.cdp = await self.page.context.new_cdp_session(self.page)

        def on_frame(params: dict[str, Any]) -> None:
            self.frames.append((params["metadata"]["timestamp"], base64.b64decode(params["data"])))
            ack = asyncio.ensure_future(
                self.cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
            )
            self._acks.add(ack)  # keep a reference until it's done
            ack.add_done_callback(self._acks.discard)

        self.cdp.on("Page.screencastFrame", on_frame)
        await self.cdp.send(
            "Page.startScreencast",
            {"format": "jpeg", "quality": 92, "maxWidth": int(W * DSF), "maxHeight": int(H * DSF)},
        )

    async def stop(self) -> None:
        await self.cdp.send("Page.stopScreencast")


async def point(page: Page, target: Locator, *, click: bool = True, settle_ms: int = 850) -> None:
    await target.scroll_into_view_if_needed()
    box = await target.bounding_box()
    assert box, f"not visible: {target}"
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    await page.evaluate("([x, y]) => window.__cursorMove(x, y)", [x, y])
    await page.wait_for_timeout(settle_ms)
    if click:
        await page.evaluate("() => window.__cursorPress()")
        await page.mouse.click(x, y)


async def scroll_to(page: Page, selector: str, offset: int = 96) -> None:
    await page.evaluate(
        """([sel, off]) => {
             const top = document.querySelector(sel).getBoundingClientRect().top + scrollY - off;
             window.scrollTo({ top, behavior: 'smooth' });
           }""",
        [selector, offset],
    )


async def scroll_to_locator(page: Page, target: Locator, offset: int) -> None:
    box = await target.bounding_box()
    assert box, f"not visible: {target}"
    await page.evaluate(
        "(top) => window.scrollTo({ top, behavior: 'smooth' })",
        box["y"] + await page.evaluate("() => scrollY") - offset,
    )


async def record(url: str) -> tuple[list[tuple[float, bytes]], dict[str, float]]:
    marks: dict[str, float] = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": W, "height": H},
            device_scale_factor=DSF,
            color_scheme="light",
        )
        await context.add_init_script(SETUP_JS)
        await context.add_init_script(CURSOR_JS)
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.add_style_tag(content=CALM_CSS)
        approve = page.get_by_role("button", name="Approve", exact=True).first
        await approve.wait_for()
        await page.wait_for_timeout(1200)  # fonts and the card entrance settle

        rec = Recorder(page)
        await rec.start()
        await page.wait_for_timeout(2200)  # the brief
        await point(page, approve)
        await page.wait_for_timeout(1500)  # "the agent has started"

        await point(page, page.get_by_text("Watch it in the run theater").first)
        await page.wait_for_url("**/runs/**")
        await page.add_style_tag(content=HIDE_DOCK_CSS)  # the theater shows the run now
        await page.get_by_text("Watch it heal at seed 7").first.wait_for()
        await page.wait_for_timeout(2200)  # the warm replay: 0 model calls, $0

        await point(page, page.get_by_text("Watch it heal at seed 7").first)
        await page.wait_for_url("**/runs/golden-reorder-heal")
        speed = page.get_by_role("radio", name="2×")  # noqa: RUF001 (the UI label)
        await speed.wait_for()
        await point(page, speed, settle_ms=600)
        await page.wait_for_timeout(300)
        await scroll_to_locator(page, page.get_by_text("Chaos seed").first, offset=40)
        marks["heal_start"] = time.time() + 1.0  # after the scroll settles
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            text = await page.evaluate("() => document.body.innerText")
            if "Order GW-" in text and "placed" in text:
                break
            await page.wait_for_timeout(250)
        marks["heal_end"] = time.time()
        await page.wait_for_timeout(2200)  # the order, placed after the heal

        await point(page, page.get_by_role("link", name="Bench", exact=True).first)
        await page.wait_for_url("**/bench")
        await page.locator("#bench-heading").wait_for()
        await page.wait_for_timeout(300)
        await scroll_to(page, "#bench-heading", offset=110)
        await page.wait_for_timeout(3800)  # the measured results
        await rec.stop()
        await browser.close()
        return rec.frames, marks


HEAL_SPEED = 1.5  # the heal plays at 2x in the theater; the video adds 1.5x on top
WEBP_SIZE, WEBP_FPS = (1200, 750), 12


def encode(
    frames: list[tuple[float, bytes]], marks: dict[str, float], webp: Path, mp4: Path
) -> None:
    from PIL import Image  # pyright: ignore[reportMissingImports]  (uv run --with pillow)

    t0, t1 = frames[0][0], frames[-1][0]
    stamps = [ts for ts, _ in frames]
    decoded: dict[int, Image.Image] = {}

    def frame_at(t: float) -> Image.Image:
        i = max(0, next((k for k, ts in enumerate(stamps) if ts > t), len(stamps)) - 1)
        if i not in decoded:
            img = Image.open(io.BytesIO(frames[i][1])).convert("RGB")
            decoded[i] = img.resize((W, H), Image.Resampling.LANCZOS)
        return decoded[i]

    def timeline(fps: int) -> list[Image.Image]:
        """Source time advances 1x, except HEAL_SPEED x through the long middle of the heal."""
        out, t = [], t0
        while t < t1:
            out.append(frame_at(t))
            fast = marks.get("heal_start", t1) <= t < marks.get("heal_end", t0)
            t += (HEAL_SPEED if fast else 1.0) / fps
        return out

    # Identical neighbours become one frame that is shown longer. (Left to the encoder, a
    # repeated frame is dropped without its time, so still moments play too fast.)
    step = 1000 / WEBP_FPS
    small: list[Image.Image] = []
    durations: list[float] = []
    for frame in timeline(WEBP_FPS):
        frame = frame.resize(WEBP_SIZE, Image.Resampling.LANCZOS)
        if small and frame.tobytes() == small[-1].tobytes():
            durations[-1] += step
        else:
            small.append(frame)
            durations.append(step)
    decoded.clear()
    webp.parent.mkdir(parents=True, exist_ok=True)
    small[0].save(
        webp, save_all=True, append_images=small[1:], duration=[round(d) for d in durations],
        loop=0, quality=70, method=6,
    )  # fmt: skip
    print(
        f"{webp.relative_to(ROOT)}: {len(small)} frames, {sum(durations) / 1000:.1f} s, "
        f"{webp.stat().st_size / 1e6:.1f} MB"
    )

    import imageio_ffmpeg  # pyright: ignore[reportMissingImports]  (a bundled ffmpeg)

    mp4.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio_ffmpeg.write_frames(
        str(mp4), (W, H), fps=30, codec="libx264",
        output_params=["-crf", "20", "-preset", "slow", "-movflags", "+faststart"],
    )  # fmt: skip
    writer.send(None)
    for img in timeline(30):
        writer.send(img.tobytes())
    writer.close()
    print(f"{mp4.relative_to(ROOT)}: {mp4.stat().st_size / 1e6:.1f} MB")


def main() -> None:
    ap = argparse.ArgumentParser(description="Record the README showcase from the live site.")
    ap.add_argument("--url", default="https://backroom-cafe.vercel.app/")
    args = ap.parse_args()
    frames, marks = asyncio.run(record(args.url))
    print(f"captured {len(frames)} screencast frames")
    encode(frames, marks, ROOT / "docs/assets/showcase.webp", ROOT / "var/showcase.mp4")


if __name__ == "__main__":
    main()
