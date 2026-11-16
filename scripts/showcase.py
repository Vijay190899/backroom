"""Record the README showcase from the live site.

    uv run --with pillow --with imageio-ffmpeg python scripts/showcase.py [--url URL]

Story: the morning brief -> tap Approve -> the agent's run (a warm replay, $0) -> "watch it
heal at seed 7" (the recorded run on a redesigned portal, real browser frames) -> the bench.
It drives the public site in replay mode: no access code, no model calls, nothing changes on
the server. A camera follows the action: it closes in on each button before the click and
on the part of the page where the result lands, then eases back out. Writes, at 60 fps,
docs/assets/showcase.avif (AV1: plays inline in the README) and var/showcase.mp4 (for
sharing), plus docs/assets/showcase.webp at 12 fps for browsers without animated AVIF.
`--reuse` encodes the last recording again (kept in var/) without recording.
"""

import argparse
import asyncio
import base64
import bisect
import functools
import io
import itertools
import math
import pickle
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from playwright.async_api import Locator, Page, async_playwright

ROOT = Path(__file__).resolve().parents[1]
W, H, DSF = 1280, 800, 2.0  # rendered at 2x, written at 1280x800: zooms up to 2x stay sharp
ZMAX = 1.8  # the closest the camera gets
EASE_S = 0.9  # a camera move
Box = tuple[float, float, float, float]  # x, y, width, height in viewport px
Window = tuple[float, float, float]  # x, y, width of what the camera shows (height follows)
Shot = tuple[int, Window]  # a source frame, seen through a camera window
WIDE: Window = (0.0, 0.0, float(W))

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
CARD = "xpath=ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' glass ')][1]"


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


def _ease(p: float) -> float:
    return 4 * p**3 if p < 0.5 else 1 - (2 - 2 * p) ** 3 / 2


class Camera:
    """What the video shows: timed shots (windows of the viewport), each eased in from
    wherever the camera was when it began. Times are wall-clock, like the frames'."""

    def __init__(self) -> None:
        self.shots: list[tuple[float, Window, float]] = []  # (start, window, ease seconds)

    def show(self, x: float, y: float, w: float, ease_s: float = EASE_S) -> None:
        """Move to this window (x, y, width), no closer than ZMAX and inside the viewport."""
        w = min(max(w, W / ZMAX), W)
        x, y = min(max(x, 0), W - w), min(max(y, 0), H - w * H / W)
        self.shots.append((time.time(), (x, y, w), ease_s))

    def wide(self, ease_s: float = EASE_S) -> None:
        self.show(0, 0, W, ease_s)

    def frame(
        self, box: Box, *, zoom: float | None = None, pad: float = 40, ease_s: float = EASE_S
    ) -> None:
        """Frame a box: fitted with some padding, or centred on it at a set zoom."""
        x0, y0 = max(box[0], 0), max(box[1], 0)
        x1, y1 = min(box[0] + box[2], W), min(box[1] + box[3], H)  # the visible part
        w = W / zoom if zoom else max(x1 - x0 + 2 * pad, (y1 - y0 + 2 * pad) * W / H)
        self.show((x0 + x1 - w) / 2, (y0 + y1 - w * H / W) / 2, w, ease_s)

    def at(self, t: float) -> Window:
        start, target, since, ease_s = WIDE, WIDE, -math.inf, 1.0
        for ts, window, e in self.shots:
            if ts > t:
                break
            start = self._mix(start, target, since, ease_s, ts)  # where this move begins
            target, since, ease_s = window, ts, e
        return self._mix(start, target, since, ease_s, t)

    @staticmethod
    def _mix(a: Window, b: Window, since: float, ease_s: float, t: float) -> Window:
        p = _ease(min(max((t - since) / ease_s, 0.0), 1.0))
        return (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p, a[2] + (b[2] - a[2]) * p)


async def box_of(*targets: Locator) -> Box:
    """The box around one or more elements, in viewport px."""
    rects = []
    for target in targets:
        r = await target.bounding_box()
        assert r, f"not visible: {target}"
        rects.append(r)
    x0, y0 = min(r["x"] for r in rects), min(r["y"] for r in rects)
    x1 = max(r["x"] + r["width"] for r in rects)
    y1 = max(r["y"] + r["height"] for r in rects)
    return x0, y0, x1 - x0, y1 - y0


async def point(
    page: Page,
    target: Locator,
    cam: Camera,
    *,
    frame: Box | None = None,
    zoom: float | None = None,
    settle_ms: int = 1000,
    leaves: bool = False,
) -> None:
    """Close in on the target's surroundings, move the cursor to it and click. A click that
    opens another page eases the camera back out."""
    await target.scroll_into_view_if_needed()
    b = await box_of(target)
    if frame is not None or zoom is not None:
        cam.frame(frame or b, zoom=zoom)
    x, y = b[0] + b[2] / 2, b[1] + b[3] / 2
    await page.evaluate("([x, y]) => window.__cursorMove(x, y)", [x, y])
    await page.wait_for_timeout(settle_ms)
    await page.evaluate("() => window.__cursorPress()")
    await page.mouse.click(x, y)
    if leaves:
        cam.wide(ease_s=0.4)  # out by the time the next page has faded in


async def scroll_to(target: Locator, offset: int) -> None:
    """Smooth-scroll the page until the target sits `offset` px below the top."""
    await target.evaluate(
        "(el, off) => window.scrollTo({ top: el.getBoundingClientRect().top + scrollY - off,"
        " behavior: 'smooth' })",
        offset,
    )


async def record(url: str) -> tuple[list[tuple[float, bytes]], dict[str, float], Camera]:
    marks: dict[str, float] = {}
    cam = Camera()
    async with async_playwright() as p:
        # Without the scale flag the screencast sends 1x frames, whatever the context's
        # scale; without the GPU, headless Chrome renders 2x at about 10 fps (55 with it).
        browser = await p.chromium.launch(
            args=[f"--force-device-scale-factor={DSF}", "--enable-gpu"]
        )
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
        # Today: the brief, then closer on the first card and its Approve button.
        await page.wait_for_timeout(1800)
        card_text = approve.locator(CARD).locator(":scope > div").first
        await point(page, approve, cam, frame=await box_of(card_text, approve))
        await page.wait_for_timeout(150)
        # Follow the card to the agent dock: "the agent has started", and a link to watch.
        cam.frame(await box_of(page.locator('[aria-label="Agent"]')), zoom=1.6)
        await page.wait_for_timeout(1800)
        await point(page, page.get_by_text("Watch it in the run theater").first, cam, leaves=True)

        # The run theater: a warm replay, 1.1 s, no model calls, $0.
        await page.wait_for_url("**/runs/**")
        await page.add_style_tag(content=HIDE_DOCK_CSS)  # the theater shows the run now
        heal_link = page.get_by_text("Watch it heal at seed 7").first
        await heal_link.wait_for()
        # Next keeps a page you left in the DOM, hidden: look only in the one on screen.
        theater = page.locator("[data-theater]").filter(visible=True)
        await scroll_to(theater, offset=88)
        await page.wait_for_timeout(900)
        stats = theater.locator("dl > div")
        done = theater.get_by_text("Order GW-").first
        cam.frame(await box_of(stats.nth(0), stats.nth(3), done))
        await page.wait_for_timeout(2300)
        seeds = theater.locator('[role="radiogroup"][aria-label="Chaos seed"]')
        await point(page, heal_link, cam, frame=await box_of(seeds, heal_link), leaves=True)

        # The heal: the same order on a redesigned, German-language portal. It plays at 1x
        # here and HEAL_SPEED x in the video (camera moves slowed to match).
        await page.wait_for_url("**/runs/golden-reorder-heal")
        speed = theater.get_by_role("radio", name="2×")  # noqa: RUF001 (the UI label)
        await speed.wait_for()  # the recorded run has loaded
        await scroll_to(theater, offset=88)
        await page.wait_for_timeout(700)
        # The right pane starts at the "Tokens" cell, past the step list's text, so no line
        # is cut in half; it shows the portal, and later the cost over the placed order.
        gap = (await box_of(stats.nth(2)))[0]
        pane = W - gap
        _, sy, _, sh = await box_of(theater.locator(":scope > div.grid > div:nth-child(2) > div"))
        marks["heal_start"] = time.time()
        slow = EASE_S * HEAL_SPEED
        cam.show(gap, sy + sh / 2 - pane * H / W / 2, pane, slow)  # the redesigned portal
        await page.wait_for_timeout(7000)
        steps = await box_of(theater.locator('ol[aria-label="Steps"]'))
        bottom = min(steps[1] + steps[3], H)  # where each new step and its heal appear
        cam.frame((steps[0], bottom - 340, steps[2], 340), zoom=1.6, ease_s=slow)
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            text = await page.evaluate("() => document.body.innerText")
            if "Order GW-" in text and "placed" in text:
                break
            await page.wait_for_timeout(250)
        marks["heal_end"] = time.time()
        ticker_y = (await box_of(stats.nth(0)))[1]
        cam.show(gap, ticker_y - 12, pane)  # what it cost, over the order it placed
        await page.wait_for_timeout(2800)

        # The bench: the measured results.
        bench = page.get_by_role("link", name="Bench", exact=True).first
        await point(page, bench, cam, zoom=ZMAX, leaves=True)
        await page.wait_for_url("**/bench")
        heading = page.locator("#bench-heading")
        await heading.wait_for()
        await page.wait_for_timeout(300)
        await scroll_to(heading, offset=110)
        await page.wait_for_timeout(900)
        rows = page.locator('section[aria-labelledby="bench-heading"] ol > li')
        cam.frame(await box_of(rows.nth(0), rows.nth(1)), pad=24)  # full-width rows: a nudge
        await page.wait_for_timeout(3400)
        marks["end"] = time.time()  # a still page sends no frames: hold the last one to here
        await rec.stop()
        await browser.close()
        return rec.frames, marks, cam


FPS = 60  # the README animation and the MP4
HEAL_SPEED = 3.0  # the heal plays at 1x in the theater, 3x in the video: every third frame
WEBP_SIZE, WEBP_FPS = (1200, 750), 12  # the fallback for browsers without animated AVIF
CAPTURE = ROOT / "var/showcase-capture.pkl"  # the last recording, for --reuse
# Colour as browsers expect it: BT.709 primaries and matrix; sRGB transfer for the image.
YUV = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"]
TAGS = ["-color_primaries", "bt709", "-colorspace", "bt709", "-color_range", "tv"]


def ffmpeg() -> str:
    import imageio_ffmpeg  # pyright: ignore[reportMissingImports]  (a bundled ffmpeg)

    return imageio_ffmpeg.get_ffmpeg_exe()


def h264(ff: str) -> list[str]:
    """The GPU's H.264 encoder (NVENC) when there is one, else libx264."""
    probe = [ff, "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.1"]
    nvenc = subprocess.run([*probe, "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
    if nvenc.returncode:
        return ["-c:v", "libx264", "-preset", "slow", "-crf", "21"]
    return ["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "23",
            "-b:v", "0"]  # fmt: skip


def encode(
    frames: list[tuple[float, bytes]], marks: dict[str, float], cam: Camera, outs: dict[str, Path]
) -> None:
    from PIL import Image  # pyright: ignore[reportMissingImports]  (uv run --with pillow)

    t0, t1 = frames[0][0], max(frames[-1][0], marks.get("end", 0.0))
    stamps = [ts for ts, _ in frames]

    @functools.lru_cache(maxsize=16)
    def source(i: int) -> Image.Image:
        return Image.open(io.BytesIO(frames[i][1])).convert("RGB")

    def timeline(fps: int) -> list[Shot]:
        """Source time advances 1x, except HEAL_SPEED x through the long middle of the heal.
        Each step takes the newest frame by a few ms past it, so jitter in the frame times
        doesn't show one frame twice and skip the next."""
        out, t = [], t0
        while t < t1:
            i = max(0, bisect.bisect_right(stamps, t + 0.008) - 1)
            x, y, w = cam.at(t)
            out.append((i, (round(x, 2), round(y, 2), round(w, 2))))
            fast = marks.get("heal_start", t1) <= t < marks.get("heal_end", t0)
            t += (HEAL_SPEED if fast else 1.0) / fps
        return out

    def render(shot: Shot, size: tuple[int, int]) -> Image.Image:
        i, (x, y, w) = shot
        img = source(i)
        sx, sy = img.width / W, img.height / H  # frame px per viewport px
        h = w * H / W
        crop = (x * sx, y * sy, min((x + w) * sx, img.width), min((y + h) * sy, img.height))
        return img.resize(size, Image.Resampling.LANCZOS, box=crop)

    def runs(shots: list[Shot]) -> list[tuple[Shot, int]]:
        """Identical neighbours as (shot, how many)."""
        out: list[tuple[Shot, int]] = []
        for s in shots:
            if out and out[-1][0] == s:
                out[-1] = (s, out[-1][1] + 1)
            else:
                out.append((s, 1))
        return out

    ff = ffmpeg()
    for path in outs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    # One pass at 60 fps into one ffmpeg: AV1 as an animated AVIF for the README (AV1 has
    # no encoder on this GPU, so libaom), H.264 as an MP4 for sharing (NVENC if present).
    cmd = [
        ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        *YUV, *TAGS, "-color_trc", "iec61966-2-1", "-c:v", "libaom-av1", "-crf", "30",
        "-b:v", "0", "-cpu-used", "6", "-row-mt", "1", "-tiles", "2x2", "-g", "300",
        "-aom-params", "tune-content=screen", "-f", "avif", str(outs["avif"]),
        *YUV, *TAGS, "-color_trc", "bt709", *h264(ff), "-g", "120",
        "-movflags", "+faststart", str(outs["mp4"]),
    ]  # fmt: skip
    began = time.monotonic()
    video = runs(timeline(FPS))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin
    with ThreadPoolExecutor() as pool:  # Pillow lets go of the GIL to decode and resize
        for batch in itertools.batched(video, 48):
            images = pool.map(lambda s: render(s, (W, H)).tobytes(), [s for s, _ in batch])
            for (_, n), data in zip(batch, images, strict=True):
                for _ in range(n):
                    proc.stdin.write(data)
        proc.stdin.close()
        assert proc.wait() == 0, "ffmpeg failed"
        frames_out = sum(n for _, n in video)
        print(f"{frames_out} frames at {FPS} fps ({frames_out / FPS:.1f} s) in "
              f"{time.monotonic() - began:.0f} s")  # fmt: skip
        for key in ("avif", "mp4"):
            print(f"  {outs[key].relative_to(ROOT)}: {outs[key].stat().st_size / 1e6:.1f} MB")

        # The fallback: an animated WebP. A run of identical frames becomes one frame shown
        # longer (left to the encoder, a repeated frame is dropped without its time).
        step = 1000 / WEBP_FPS
        still = runs(timeline(WEBP_FPS))
        small = list(pool.map(lambda s: render(s, WEBP_SIZE), [s for s, _ in still]))
    durations = [round(n * step) for _, n in still]
    small[0].save(
        outs["webp"], save_all=True, append_images=small[1:], duration=durations, loop=0,
        quality=70, method=4,
    )  # fmt: skip
    print(f"  {outs['webp'].relative_to(ROOT)}: {len(small)} frames at {WEBP_FPS} fps, "
          f"{outs['webp'].stat().st_size / 1e6:.1f} MB")  # fmt: skip


def main() -> None:
    ap = argparse.ArgumentParser(description="Record the README showcase from the live site.")
    ap.add_argument("--url", default="https://backroom-cafe.vercel.app/")
    ap.add_argument("--reuse", action="store_true", help="encode the last recording again")
    args = ap.parse_args()
    if args.reuse:
        with CAPTURE.open("rb") as f:
            frames, marks, cam = pickle.load(f)  # our own file, written below
    else:
        frames, marks, cam = asyncio.run(record(args.url))
        CAPTURE.parent.mkdir(parents=True, exist_ok=True)
        with CAPTURE.open("wb") as f:
            pickle.dump((frames, marks, cam), f, protocol=pickle.HIGHEST_PROTOCOL)
    gaps = [b - a for (a, _), (b, _) in itertools.pairwise(frames)]
    heal = [g for (ts, _), g in zip(frames, gaps, strict=False)
            if marks["heal_start"] <= ts < marks["heal_end"]]  # fmt: skip
    print(f"captured {len(frames)} frames ({len(heal) / sum(heal):.0f} fps through the heal), "
          f"{len(cam.shots)} camera shots")  # fmt: skip
    encode(frames, marks, cam, {
        "avif": ROOT / "docs/assets/showcase.avif",
        "webp": ROOT / "docs/assets/showcase.webp",
        "mp4": ROOT / "var/showcase.mp4",
    })  # fmt: skip


if __name__ == "__main__":
    main()
