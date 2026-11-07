"""Evidence collectors for the moderator. Each probe returns a plain dict (cached by the runner)."""
import os, re, json, time, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.harness import ROOT, Session, dir_stats, sync_playwright

DIST = os.path.join(ROOT, 'dist')
OUT = os.path.join(ROOT, 'tools', 'out', 'moderator')
SRC = os.path.join(ROOT, 'src')

PATTERNS = {
    'escape': r"['\"]Escape['\"]|['\"]Esc['\"]|keyCode\s*===?\s*27",
    'storage': r"localStorage|sessionStorage|indexedDB|document\.cookie",
    'navlang': r"navigator\.(language|languages)|Intl\.DateTimeFormat",
    'synth': r"createOscillator|OscillatorNode",
    'payments': r"bridge\.payments|payments\.(purchase|getCatalog|consume)|\bpurchase\(|buyProduct|checkout",
    'auth': r"authorizePlayer|\.authorize\(|isAuthorizationSupported|signIn|\blogin\b",
    'links': r"\bwindow\.open\(|target=['\"]_blank|<a\s|location\.assign\(|location\.href\s*=",
    'urllock': r"location\.(host|hostname|origin)|document\.referrer",
    'analytics': r"gtag\(|google-analytics|googletagmanager|GoogleAnalytics|metrika|mixpanel\.|amplitude\.(init|track)",
    'fullscreen': r"requestFullscreen|webkitRequestFullscreen",
    'revive': r"reviveUsed",
    'audio_enabled': r"isAudioEnabled",
    'pause_event': r"PAUSE_STATE_CHANGED",
    'audio_event': r"AUDIO_STATE_CHANGED",
    'cg': r"CrazyGames",
    'gameplay_start': r"gameplayStart",
    'platform_language': r"platform\.language|bridge\.platform\.language",
    'userdata': r"getUserMedia|geolocation|mediaDevices|<input|FormData",
    'banner_bridge': r"advertisement\.showBanner",
    'roblox': r"roblox",
    'rewarded_supported': r"isRewardedSupported",
}


def _files(root, exts=('.ts', '.css', '.html')):
    for r, _, fs in os.walk(root):
        if os.sep + 'dev' in r.replace(root, ''): continue  # src/dev is dev-build only
        for f in fs:
            if f.endswith(exts): yield os.path.join(r, f)


def grep(pat, files=None):
    rx = re.compile(pat, re.I); hits = []
    for p in (files or list(_files(SRC))):
        try: lines = open(p, encoding='utf-8', errors='ignore').read().splitlines()
        except Exception: continue
        for i, l in enumerate(lines, 1):
            if rx.search(l) and not l.strip().startswith('//') and not l.strip().startswith('*'):
                hits.append(f"{os.path.relpath(p, ROOT)}:{i}: {l.strip()[:90]}")
    return hits


def static():
    d = {}
    d['total'], d['files'] = dir_stats(DIST)
    rels = []
    for r, _, fs in os.walk(DIST):
        for f in fs: rels.append(os.path.relpath(os.path.join(r, f), DIST))
    d['bad_names'] = [x for x in rels if not re.fullmatch(r'[A-Za-z0-9._\-/]+', x)]
    d['index'] = os.path.exists(os.path.join(DIST, 'index.html'))
    html = open(os.path.join(DIST, 'index.html'), encoding='utf-8').read() if d['index'] else ''
    head = html.split('</head>')[0]
    m = re.search(r'<script\b[^>]*>', head)
    d['first_script'] = m.group(0) if m else ''
    d['bridge_first'] = bool(m and 'playgama-bridge' in m.group(0) and ' async' not in m.group(0) and ' defer' not in m.group(0) and 'module' not in m.group(0))
    cfg = os.path.join(DIST, 'playgama-bridge-config.json')
    try: d['config_ok'] = isinstance(json.load(open(cfg)), dict)
    except Exception: d['config_ok'] = False
    css = ''.join(open(os.path.join(DIST, 'assets', f), encoding='utf-8', errors='ignore').read() for f in os.listdir(os.path.join(DIST, 'assets')) if f.endswith('.css')) if os.path.isdir(os.path.join(DIST, 'assets')) else ''
    d['ext_in_html'] = sorted(set(re.findall(r'(?:src|href)=["\'](https?://[^"\']+)', html)) | set(re.findall(r'url\(["\']?(https?://[^)"\']+)', css)))
    d['abs_paths'] = re.findall(r'(?:src|href)=["\'](/[^"\']*)', html) + re.findall(r'url\(["\']?(/[^)"\']*)', css)
    d['video_files'] = [x for x in rels if x.lower().endswith(('.mp4', '.webm', '.mov', '.ogv'))]
    d['audio_files'] = [x for x in rels if x.lower().endswith(('.mp3', '.ogg', '.wav', '.m4a'))]
    d['grep'] = {k: grep(v) for k, v in PATTERNS.items()}
    win = os.path.join(SRC, 'ui', 'windows')
    d['windows_no_close'] = [f for f in (os.listdir(win) if os.path.isdir(win) else []) if f.endswith('.ts') and f not in ('index.ts', 'UiWindow.ts', 'overlays.ts') and not re.search(r'close|extends UiWindow', open(os.path.join(win, f), encoding='utf-8').read(), re.I)]
    pj = json.load(open(os.path.join(ROOT, 'package.json')))
    d['bridge_range'] = pj['dependencies'].get('@playgama/bridge')
    try: d['bridge_installed'] = json.load(open(os.path.join(ROOT, 'node_modules/@playgama/bridge/package.json')))['version']
    except Exception: d['bridge_installed'] = None
    try:
        d['bridge_latest'] = subprocess.run(['npm', 'view', '@playgama/bridge', 'version'], capture_output=True, text=True, timeout=25, cwd=ROOT).stdout.strip() or None
    except Exception: d['bridge_latest'] = None
    return d


def _external(reqs):
    return sorted({u for u in reqs if re.match(r'https?://', u) and not re.match(r'https?://(127\.0\.0\.1|localhost)[:/]', u)})


def boot(url):
    d = {}
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            t0 = time.time()
            s.pg.goto(url)
            s.pg.wait_for_function('window.__game && window.__game.player', timeout=90000)
            ready = None
            while time.time() - t0 < 60 and ready is None:
                if s.pg.evaluate("() => window.__spy.msgs.some(m => m[0] === 'game_ready')"): ready = time.time() - t0
                time.sleep(0.05)
            d['ready_s'] = ready
            time.sleep(1.0)
            d['ctx_before_gesture'] = s.pg.evaluate("() => window.__game.sfx.context()?.state ?? 'none'")
            a = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.2); b = s.st(); s.pg.keyboard.up('KeyW')   # no click yet: keys alone must work
            d['moved_without_click'] = ((b['x'] - a['x']) ** 2 + (b['z'] - a['z']) ** 2) ** 0.5
            s.pg.mouse.click(640, 360); time.sleep(1.5)
            d['ctx_after_gesture'] = s.pg.evaluate("() => window.__game.sfx.context()?.state ?? 'none'")
            n0 = s.pg.evaluate("() => window.__spy.ads.length")
            s.pg.keyboard.down('KeyW'); time.sleep(6); s.pg.keyboard.up('KeyW')
            d['ads_during_walk'] = s.pg.evaluate(f"() => window.__spy.ads.slice({n0}).map(a => a[0])")
            s.shot(os.path.join(OUT, 'boot.png'))
            d['info'] = s.pg.evaluate("""() => { const t = document.body.innerText || ''; const g = window.__game;
              return { title: document.title, lang: document.documentElement.lang, text: t.slice(0, 4000),
                links: [...document.querySelectorAll('a[href]')].map(a => a.href), cookie: document.cookie,
                userSelect: getComputedStyle(document.body).userSelect, mute: !!document.querySelector('.snd-mute'),
                muteText: document.querySelector('.snd-mute')?.textContent ?? '',
                rbxText: [...document.querySelectorAll('.rbx')].map(e => e.textContent).join(' ').slice(0, 6000),
                tutorial: g.econ.s.tutorial, heap: performance.memory ? performance.memory.usedJSHeapSize : null,
                bridgeLang: window.bridge.platform.language, bridgeAudio: window.bridge.platform.isAudioEnabled,
                platformId: window.bridge.platform.id, rewardedSupported: window.bridge.advertisement.isRewardedSupported,
                buttons: [...document.querySelectorAll('button')].map(b => b.textContent.trim()).filter(Boolean) }; }""")
            try: d['idb'] = s.pg.evaluate("async () => (indexedDB.databases ? (await indexedDB.databases()).map(x => x.name) : [])")
            except Exception: d['idb'] = []
            spy = s.pg.evaluate("() => ({ msgs: window.__spy.msgs, storage: window.__spy.storage, ls: window.__spy.ls })")
            d.update(spy)
            d['external'] = _external(s.requests)
            d['requests'] = len(s.requests)
            d['errors'] = list(s.errors)
        finally:
            s.close()
    return d


def _probe_js():
    return "window.__spy.probe = () => { const g = window.__game, c = g.sfx.context(); return { ctx: c ? c.state : 'none', x: g.player.pos.x, z: g.player.pos.z, lvl: g.econ.level }; };"


def ads(url):
    d = {'interstitial': [], 'interstitial_fail': [], 'rewarded_ok': {}, 'rewarded_skip': {}, 'rewarded_fail': {}}
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            s.load(); s.prep(level=6)
            s.pg.evaluate(_probe_js() + "window.__spy.emulate = true;")
            time.sleep(1.5)
            d['rbxText'] = s.pg.evaluate("() => [...document.querySelectorAll('.rbx')].map(e => e.textContent).join(' ')")
            lobby = s.st()
            log = lambda: s.pg.evaluate("() => window.__spy.adLog.splice(0)")
            waitlog = lambda kind, state, sec: _wait(s, kind, state, sec)
            # interstitial after a fall (natural pause)
            s.tp(0, 10, -200, settle=1.5)   # a stage, so the kill zone counts (the lobby has none)
            d['fall_ok'] = s.fall()
            time.sleep(1.3); s.pg.keyboard.down('KeyW')   # respawned in the lobby: keep walking, a paused game must not move
            d['interstitial_called'] = _wait_ad_call(s, 'interstitial', 10)
            waitlog('interstitial', 'after', 8); d['interstitial'] = log(); s.pg.keyboard.up('KeyW')
            # interstitial that fails: game must go on
            s.pg.evaluate("window.__spy.interstitialMode = 'fail'")
            time.sleep(1); s.tp(lobby['x'], lobby['y'], lobby['z'], settle=0.5)
            s.tp(0, 10, -200, settle=1.5); s.fall(); time.sleep(4.5)
            a = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.2); b = s.st(); s.pg.keyboard.up('KeyW')
            d['interstitial_fail'] = log()
            d['after_fail_moved'] = ((b['x'] - a['x']) ** 2 + (b['z'] - a['z']) ** 2) ** 0.5
            d['after_fail_ctx'] = s.pg.evaluate("() => window.__game.sfx.context()?.state")
            s.pg.evaluate("window.__spy.interstitialMode = 'ok'")
            # rewarded: ok / skip / fail
            for mode, key in (('ok', 'rewarded_ok'), ('skip', 'rewarded_skip'), ('fail', 'rewarded_fail')):
                time.sleep(2); s.tp(lobby['x'], lobby['y'], lobby['z'], settle=0.8); s.pg.mouse.click(640, 360)
                s.pg.evaluate(f"window.__spy.rewardedMode = '{mode}'; window.__spy.adLog.length = 0; window.__spy.ads.length = 0")
                l0 = s.pg.evaluate("() => window.__game.econ.level")
                clicked = s.click_hud('Bottom.Packs.Pack1.Button')
                s.pg.keyboard.down('KeyW')
                if mode == 'fail': time.sleep(3)
                else: waitlog('rewarded', 'after', 9)
                time.sleep(0.5); s.pg.keyboard.up('KeyW')
                l1 = s.pg.evaluate("() => window.__game.econ.level")
                moved = s.st()
                d[key] = {'clicked': clicked, 'l0': l0, 'l1': l1, 'log': log(), 'calls': s.pg.evaluate("() => window.__spy.ads")}
            d['errors'] = list(s.errors)
        finally:
            s.close()
    return d


def _wait(s, kind, state, sec):
    t0 = time.time()
    while time.time() - t0 < sec:
        if s.pg.evaluate(f"() => window.__spy.adLog.some(e => e.kind === '{kind}' && e.state === '{state}')"): return True
        time.sleep(0.1)
    return False


def _wait_ad_call(s, kind, sec):
    t0 = time.time()
    while time.time() - t0 < sec:
        if s.pg.evaluate(f"() => window.__spy.ads.some(a => a[0] === '{kind}')"): return True
        time.sleep(0.1)
    return False


def pause(url):
    d = {}
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            s.load(); s.prep(level=None); time.sleep(1.5)
            ctx = lambda: s.pg.evaluate("() => window.__game.sfx.context()?.state ?? 'none'")
            d['ctx0'] = ctx()
            d['has_audio_api'] = s.pg.evaluate("() => typeof window.bridge.platform._platformBridge._setAudioState === 'function'")
            if d['has_audio_api']:
                s.pg.evaluate("window.bridge.platform._platformBridge._setAudioState(false)"); time.sleep(0.9); d['ctx_audio_off'] = ctx()
                s.pg.evaluate("window.bridge.platform._platformBridge._setAudioState(true)"); time.sleep(0.9); d['ctx_audio_on'] = ctx()
                s.pg.evaluate("window.bridge.platform._platformBridge._setPauseState(true)"); time.sleep(0.5)
                a = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.0); b = s.st(); s.pg.keyboard.up('KeyW')
                d['pause_moved'] = ((b['x'] - a['x']) ** 2 + (b['z'] - a['z']) ** 2) ** 0.5; d['ctx_paused'] = ctx()
                s.pg.evaluate("window.bridge.platform._platformBridge._setPauseState(false)"); time.sleep(0.9)
                a = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.0); b = s.st(); s.pg.keyboard.up('KeyW')
                d['resume_moved'] = ((b['x'] - a['x']) ** 2 + (b['z'] - a['z']) ** 2) ** 0.5; d['ctx_resumed'] = ctx()
            # hidden tab: bring another tab to the front
            other = s.ctx.new_page(); other.goto('about:blank'); other.bring_to_front(); time.sleep(1.5)
            d['hidden'] = s.pg.evaluate("() => document.hidden"); d['ctx_hidden'] = ctx()
            other.close(); s.pg.bring_to_front(); time.sleep(1.5)
            if not d['hidden']:   # headed Chromium keeps both tabs visible: emulate visibilitychange
                s.pg.evaluate("() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' }); document.dispatchEvent(new Event('visibilitychange')); }")
                time.sleep(1.2); d['ctx_hidden'] = ctx(); d['hidden'] = True; d['hidden_emulated'] = True
                s.pg.evaluate("() => { delete document.hidden; delete document.visibilityState; document.dispatchEvent(new Event('visibilitychange')); }"); time.sleep(1.2)
            d['ctx_back'] = ctx(); a = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.0); b = s.st(); s.pg.keyboard.up('KeyW')
            d['back_moved'] = ((b['x'] - a['x']) ** 2 + (b['z'] - a['z']) ** 2) ** 0.5
            d['errors'] = list(s.errors)
        finally:
            s.close()
    return d


SIZES = [(1920, 1080), (1366, 768), (1280, 720), (1024, 768), (800, 600), (1000, 1000), (600, 900), (390, 844),
         (907, 510), (1216, 684), (800, 450), (1080, 607)]
SIZE_JS = """() => { const de = document.documentElement, cv = document.querySelector('canvas'), r = cv ? cv.getBoundingClientRect() : null, over = [];
  for (const el of document.querySelectorAll('body *')) { if (el === cv || el.tagName === 'CANVAS') continue; const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue; const b = el.getBoundingClientRect(); if (b.width < 4 || b.height < 4) continue;
    if (b.right > innerWidth + 2 || b.bottom > innerHeight + 2 || b.left < -2 || b.top < -2) over.push(String(el.className || el.tagName).slice(0, 40) + ' [' + [b.left, b.top, b.right, b.bottom].map(Math.round) + ']'); }
  return { iw: innerWidth, ih: innerHeight, sw: de.scrollWidth, sh: de.scrollHeight, cw: de.clientWidth, ch: de.clientHeight,
    canvas: r ? [r.left, r.top, r.width, r.height].map(Math.round) : null, buf: cv ? [cv.width, cv.height] : null, nover: over.length, over: over.slice(0, 5) }; }"""


def sizes(url):
    d = {'rows': []}
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            s.load(); s.prep(level=None)
            for w, h in SIZES:
                s.pg.set_viewport_size({'width': w, 'height': h}); time.sleep(0.9)
                m = s.pg.evaluate(SIZE_JS); m['size'] = [w, h]; d['rows'].append(m)
                s.shot(os.path.join(OUT, 'sizes', f'{w}x{h}.png'))
            d['errors'] = list(s.errors)
        finally:
            s.close()
    return d


def persist(url):
    d = {}
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            s.load(); s.pg.mouse.click(640, 360)
            l0 = s.pg.evaluate("() => window.__game.econ.level")
            s.pg.evaluate("window.__game.econ.addLevels(3)"); time.sleep(0.5)
            l1 = s.pg.evaluate("() => window.__game.econ.level")
            n0 = s.pg.evaluate("() => window.__spy.storage.filter(x => x[0] === 'set').length")
            s.pg.keyboard.down('KeyW'); time.sleep(8); s.pg.keyboard.up('KeyW')
            d['sets_idle_walk'] = s.pg.evaluate("() => window.__spy.storage.filter(x => x[0] === 'set').length") - n0
            d['sets_total'] = s.pg.evaluate("() => window.__spy.storage.filter(x => x[0] === 'set').length")
            time.sleep(1.0)
            s.pg.reload(); s.pg.wait_for_function('window.__game && window.__game.player', timeout=90000); time.sleep(3)
            l2 = s.pg.evaluate("() => window.__game.econ.level")
            d.update({'l0': l0, 'l1': l1, 'l2': l2})
            # restore the mock save so later runs start fresh
            s.pg.evaluate("() => window.bridge.storage.set(['spiderarm.save.v1'], [null])"); time.sleep(0.3)
            d['errors'] = list(s.errors)
        finally:
            s.close()
    return d
