"""Shared harness for tools/smoke.py and tools/moderator: build, static server, browser, game helpers.
Game control goes through window.__game (always present, also in prod) — see src/main.ts."""
import os, re, subprocess, sys, time, signal, urllib.request, json
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SPY_JS = open(os.path.join(os.path.dirname(__file__), 'spy.js')).read()
ARGS = ['--use-angle=metal', '--window-size=1300,800', '--autoplay-policy=document-user-activation-required']


def build():
    r = subprocess.run(['npm', 'run', 'build'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit('npm run build failed')
    return r.stdout


class Server:
    """vite preview (prod, default) or vite dev on a private port; killed on exit."""
    def __init__(self, dev=False, port=None):
        self.dev = dev; self.port = port or (5189 if dev else 4189); self.p = None
        self.url = f'http://127.0.0.1:{self.port}/'

    def __enter__(self):
        cmd = ['npx', 'vite'] + ([] if self.dev else ['preview']) + ['--host', '127.0.0.1', '--port', str(self.port), '--strictPort']
        self.p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(120):
            try:
                urllib.request.urlopen(self.url, timeout=1); return self
            except Exception:
                time.sleep(0.5)
        self.__exit__(); raise SystemExit('server did not start')

    def __exit__(self, *a):
        if self.p:
            try: os.killpg(self.p.pid, signal.SIGTERM)
            except Exception: pass


class Session:
    """One browser page with console/network capture."""
    def __init__(self, pw, url, width=1280, height=720, init_script=SPY_JS):
        self.url = url
        self.browser = pw.chromium.launch(headless=False, args=ARGS)
        self.ctx = self.browser.new_context(viewport={'width': width, 'height': height}, locale='en-US')
        if init_script: self.ctx.add_init_script(init_script)
        self.pg = self.ctx.new_page()
        self.errors, self.warnings, self.requests, self.responses = [], [], [], []
        self.pg.on('console', self._console)
        self.pg.on('pageerror', lambda e: self.errors.append('pageerror: ' + str(e)))
        self.pg.on('request', lambda r: self.requests.append(r.url))
        self.pg.on('response', lambda r: self.responses.append((r.url, r.status)))

    def _console(self, m):
        if m.type == 'error': self.errors.append(m.text)
        elif m.type == 'warning': self.warnings.append(m.text)

    def load(self, timeout=90000):
        self.pg.goto(self.url)
        self.pg.wait_for_function('window.__game && window.__game.player', timeout=timeout)
        time.sleep(3)

    def prep(self, level=6):
        """Level up (level=None: keep the save) + hide dev UI + fixed quality; click the canvas = first user gesture."""
        lv = f"g.gameplay.dev.level = {level}; g.applyProgression();" if level else ''
        self.pg.evaluate(f"""() => {{ const g = window.__game; {lv}
          for (const el of document.querySelectorAll('.devpanel, .devpanel-toggle')) el.style.display = 'none';
          g.renderer.auto = false; g.renderer.setQuality('high'); g.fly.enabled = false; }}""")
        self.pg.mouse.click(640, 360)

    STATE = """() => { const g = window.__game, p = g.player; return { x: p.pos.x, y: p.pos.y, z: p.pos.z, s: p.state,
        grip: p.grip, gripMax: p.gripMax, vy: p.vel.y, h: p.height, docked: p.docked, xp: g.econ.xp, lvl: g.econ.level }; }"""

    def st(self): return self.pg.evaluate(self.STATE)

    def tp(self, x, y, z, yaw=3.1416, pitch=-14, dist=22, settle=1.2):
        self.pg.evaluate(f"""() => {{ const g = window.__game; const V = g.player.pos.constructor;
            g.player.teleport(new V({x}, {y}, {z}), new V(Math.sin({yaw}), 0, Math.cos({yaw})).normalize());
            g.camCtl.yaw = {yaw}; g.camCtl.pitch = {pitch} * Math.PI / 180; g.camCtl.zoom = {dist}; g.camCtl.snap(g.player.pos); }}""")
        time.sleep(settle)

    def callouts(self):
        return self.pg.evaluate("() => [...document.querySelectorAll('.callout')].map(e => e.textContent).join('|')")

    def fall(self):
        """Put the player inside a kill zone (→ 'YOU FELL!' → lobby; a free fall can catch on stage geometry). False if no zone exists."""
        kz = self.pg.evaluate("() => { const b = window.__game.triggers.killZones[0]; if (!b) return null; const c = b.getCenter(new b.min.constructor()); return { x: c.x, y: c.y, z: c.z }; }")
        if not kz: return False
        self.tp(kz['x'], kz['y'], kz['z'], settle=0.1); return True

    def click_hud(self, path):
        """Click the HUD button with the game's own path (e.g. Bottom.Packs.Pack1.Button). False if absent."""
        return self.pg.evaluate("""(want) => { for (const btn of document.querySelectorAll('.rbx-button')) { const n = [];
          for (let el = btn; el && !el.classList.contains('rbx-gui'); el = el.parentElement) if (el.classList.contains('rbx') && el.dataset.name) n.unshift(el.dataset.name);
          if (n.join('.') === want) { btn.click(); return true; } } return false; }""", path)

    def shot(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True); self.pg.screenshot(path=path)

    def close(self):
        try: self.browser.close()
        except Exception: pass


def dir_stats(path):
    total, n = 0, 0
    for r, _, fs in os.walk(path):
        for f in fs: total += os.path.getsize(os.path.join(r, f)); n += 1
    return total, n
