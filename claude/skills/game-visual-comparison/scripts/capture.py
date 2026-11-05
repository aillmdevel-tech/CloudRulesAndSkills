#!/usr/bin/env python3
"""Screenshot a locally running web game with headless Chromium (Python Playwright).

usage: capture.py URL OUT.png [--size 1280x720] [--wait-ms 1500] [--eval JS] [--eval-after JS]
                  [--selector canvas] [--console console.log] [--dpr 1] [--headed]

--eval        JS run right after load (before waiting), e.g. "window.__game?.setCamera(...)"
--eval-after  JS run after waiting, right before the screenshot
--selector    screenshot only this element (default: full viewport)
Exit code 2 if the page threw uncaught errors (they are printed and saved to --console).
"""
import argparse
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("python playwright missing: python3 -m pip install --user playwright && python3 -m playwright install chromium")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--wait-ms", type=int, default=1500)
    ap.add_argument("--eval")
    ap.add_argument("--eval-after")
    ap.add_argument("--selector")
    ap.add_argument("--console")
    ap.add_argument("--dpr", type=float, default=1)
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    w, h = (int(x) for x in a.size.lower().split("x"))

    logs, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not a.headed,
                                    args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=a.dpr)
        page.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))
        page.goto(a.url, wait_until="load")
        if a.eval:
            print("eval ->", page.evaluate(a.eval))
        page.wait_for_timeout(a.wait_ms)
        if a.eval_after:
            print("eval-after ->", page.evaluate(a.eval_after))
        gl = page.evaluate("""() => { const c = document.querySelector('canvas');
            if (!c) return 'no canvas'; return `canvas ${c.width}x${c.height} css ${c.clientWidth}x${c.clientHeight}`; }""")
        if a.selector:
            page.locator(a.selector).first.screenshot(path=a.out)
        else:
            page.screenshot(path=a.out)
        browser.close()

    print(f"saved {a.out} ({gl})")
    all_logs = logs + errors
    errs = [l for l in all_logs if l.startswith("[error]") or l.startswith("[pageerror]")]
    print(f"console: {len(logs)} messages, {len(errs)} errors")
    for l in errs[:20]:
        print("  ", l)
    if a.console:
        with open(a.console, "w", encoding="utf-8") as f:
            f.write("\n".join(all_logs))
    sys.exit(2 if errors else 0)


if __name__ == "__main__":
    main()
