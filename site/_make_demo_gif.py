"""Make examples/demo.gif, the README's tour of the three outputs.

Run from site/ after building the site:

    python _prepare.py && quarto render && python _make_demo_gif.py

It serves _site/ locally, drives headless Edge or Chrome through the
DevTools protocol (to click tabs and annotations, which plain --screenshot
can't), captures a few frames, adds a caption band to each, and writes an
animated GIF. Needs Pillow and websocket-client; the site build itself
doesn't.

Pass --browser PATH if Edge/Chrome isn't in a usual place.
"""

import argparse
import base64
import functools
import http.server
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import websocket  # websocket-client
from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parent
OUT = SITE.parent / "examples" / "demo.gif"
WIDTH, HEIGHT = 1100, 720
BAND = 52
FRAME_MS = 3200
PORT = 8791

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]

# JS helpers run in the page. scrollToEl puts an element `offset` px below the top.
HELPERS = """
window.k = {
  scrollToEl(el, offset) { window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - offset); },
  tab(scope, name) {
    const link = [...scope.querySelectorAll('.nav-link')].find(a => a.textContent.trim() === name);
    bootstrap.Tab.getOrCreateInstance(link).show();
  },
  markedTabset() {
    return [...document.querySelectorAll('.panel-tabset')]
      .find(t => t.querySelector('[data-changed], [data-added], [data-removed]'));
  },
};
"""

# (caption, page, JS to run after load)
FRAMES = [
    ("Explain: an answer in the chat, with every reason labelled by its evidence",
     "compare.html#explain",
     "k.scrollToEl(document.querySelector('.kompreni-compare'), 8)"),
    ("Walkthrough: a document to commit, for a reader who wasn't in the conversation",
     "examples/walkthrough.html",
     "window.scrollTo(0, 0)"),
    ("Walkthrough: Before/After tabs mark the lines the change touched (After)",
     "examples/walkthrough.html",
     "const t = k.markedTabset(); k.tab(t, 'After'); k.scrollToEl(t, 16)"),
    ("Walkthrough: ...and the same code before the change (Before)",
     "examples/walkthrough.html",
     "const t = k.markedTabset(); k.tab(t, 'Before'); k.scrollToEl(t, 16)"),
    ("Code tour: all the changed code, in the order it runs, annotated line by line",
     "examples/code-tour.html",
     "const t = k.markedTabset(); k.tab(t, 'After'); k.scrollToEl(t, 16)"),
]


def find_browser(given):
    for candidate in ([given] if given else BROWSERS):
        path = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if path:
            return path
    raise SystemExit("No Edge or Chrome found; pass --browser PATH")


class DevTools:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=30)
        self.next_id = 0

    def send(self, method, **params):
        self.next_id += 1
        self.ws.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def eval(self, js):
        result = self.send("Runtime.evaluate", expression=js, awaitPromise=True)
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    handler.log_message = lambda *a: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    server.handle_error = lambda *a: None  # the browser drops connections when it closes
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def caption_band(text, width):
    band = Image.new("RGB", (width, BAND), (55, 90, 127))  # darkly's navbar blue
    draw = ImageDraw.Draw(band)
    try:
        font = ImageFont.truetype("segoeui.ttf", 22)
    except OSError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except OSError:
            font = ImageFont.load_default()
    draw.text((20, BAND // 2), text, fill="white", font=font, anchor="lm")
    return band


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser")
    args = parser.parse_args()

    if not (SITE / "_site" / "compare.html").exists():
        raise SystemExit("Build the site first: python _prepare.py && quarto render")

    server = serve(SITE / "_site")
    profile = tempfile.mkdtemp()
    browser = subprocess.Popen(
        [find_browser(args.browser), "--headless=new", "--remote-debugging-port=9334",
         "--remote-allow-origins=*", "--hide-scrollbars", f"--user-data-dir={profile}",
         f"--window-size={WIDTH},{HEIGHT}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                targets = json.load(urllib.request.urlopen("http://127.0.0.1:9334/json"))
                page = next(t for t in targets if t["type"] == "page")
                break
            except (OSError, StopIteration):
                time.sleep(0.2)
        else:
            raise SystemExit("The browser's DevTools endpoint didn't start")

        dt = DevTools(page["webSocketDebuggerUrl"])
        dt.send("Emulation.setDeviceMetricsOverride", width=WIDTH, height=HEIGHT,
                deviceScaleFactor=1, mobile=False)
        dt.send("Emulation.setEmulatedMedia",
                features=[{"name": "prefers-color-scheme", "value": "dark"}])

        frames = []
        for caption, path, js in FRAMES:
            dt.send("Page.navigate", url=f"http://127.0.0.1:{PORT}/{path}")
            time.sleep(3)  # page scripts, fonts and mermaid
            dt.eval(HELPERS)
            dt.eval(f"(() => {{ {js} }})()")
            time.sleep(1)  # tab transition, highlight
            png = base64.b64decode(dt.send("Page.captureScreenshot", format="png")["data"])
            shot = Image.open(io.BytesIO(png)).convert("RGB")
            frame = Image.new("RGB", (WIDTH, HEIGHT + BAND))
            frame.paste(caption_band(caption, WIDTH), (0, 0))
            frame.paste(shot, (0, BAND))
            frames.append(frame)
            print(f"captured: {caption}")
    finally:
        browser.terminate()
        browser.wait(timeout=10)
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)

    paletted = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]
    paletted[0].save(OUT, save_all=True, append_images=paletted[1:], duration=FRAME_MS,
                     loop=0, optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
