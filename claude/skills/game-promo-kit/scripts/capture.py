"""Record gameplay takes from a browser game: canvas video + game audio + juicy-event log.

  capture.py --project DIR [--url URL] [--no-build] [--take NAME] [--size 1920x1080] [--fps 60]
             [--seconds 30] (--scenario promo/scenario.py | --manual) [--ui] [--dpr 1]

Output: promo/raw/<take>.mp4 (CFR master, easy to cut) + promo/raw/<take>.events.json
        + promo/raw/<take>/shots/*.png (api.shot()).
Game side (optional, see templates/promo-hooks.ts): window.__promo.event(type, weight, label),
window.__promo.director = (on) => hide HUD/cursor, free camera, etc.
--manual: you play in the opened window; F9 (or `) marks a juicy moment.
--ui: record the whole page (DOM HUD included) via CDP screencast instead of the canvas only.
"""
import argparse, base64, importlib.util, json, os, shutil, signal, subprocess, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from common import die, load_config, need_ffmpeg, promo_dir, run, probe

INIT_JS = r"""
(() => {
  const P = window.__promo = window.__promo || {};
  P.events = []; P.t0 = null; P.marks = 0;
  P.now = () => P.t0 == null ? 0 : (performance.now() - P.t0) / 1000;
  P.event = (type, weight = 1, label = '', extra = {}) => { if (P.t0 != null) P.events.push({ t: P.now(), type, weight, label, ...extra }); };
  // tap every WebAudio context that reaches the speakers
  P.audio = [];
  const AC = window.AudioContext || window.webkitAudioContext;
  if (AC) {
    const dests = new WeakMap(); const orig = AudioNode.prototype.connect;
    AudioNode.prototype.connect = function (dst, ...rest) {
      const res = orig.call(this, dst, ...rest);
      try {
        if (dst instanceof AudioDestinationNode) {
          const ctx = dst.context; let d = dests.get(ctx);
          if (!d) { d = ctx.createMediaStreamDestination(); dests.set(ctx, d); P.audio.push(d); }
          orig.call(this, d);
        }
      } catch (e) {}
      return res;
    };
  }
  // HTMLMediaElement sounds (Howler html5 / <audio>)
  P.mediaTap = () => { for (const el of document.querySelectorAll('audio,video')) { try { if (!el.__promo && el.captureStream) { el.__promo = el.captureStream(); P.audio.push({ stream: el.__promo }); } } catch (e) {} } };
  addEventListener('keydown', (e) => { if (P.t0 != null && (e.code === 'F9' || e.code === 'Backquote')) { P.marks++; P.event('mark', 5, 'mark'); } }, true);
})();
"""

START_REC_JS = r"""
async ({ fps, ui, bitrate }) => {
  const P = window.__promo; P.mediaTap();
  const canvas = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0];
  // video and audio go to SEPARATE recorders: Chrome's combined h264+opus webm muxer stalls the video track at random.
  // webm streams a chunk every second (Chrome's mp4 muxer holds the whole file in renderer memory -> crash on long takes)
  P.bytes = 0; P.recs = []; P.parts = {};
  const make = (stream, kind, prefs, opts) => {
    const mime = prefs.find((m) => MediaRecorder.isTypeSupported(m)) || '';
    const rec = new MediaRecorder(stream, { mimeType: mime, ...opts });
    // Blobs stay in the page until stop (Chrome's blob store spills big ones to disk). Reading them while recording
    // (arrayBuffer / fetch upload / expose_function) stalls Chrome's hardware h264 encoder after a few seconds.
    const parts = P.parts[kind] = [];
    rec.ondataavailable = (e) => { if (e.data && e.data.size) { parts.push(e.data); if (kind === 'v') P.bytes += e.data.size; } };
    rec.onstart = () => { P['start_' + kind] = performance.now(); };
    P.recs.push(rec); return mime;
  };
  let vmime = null, amime = null, na = 0;
  if (!ui) {
    if (!canvas) throw new Error('no canvas on the page');
    vmime = make(new MediaStream(canvas.captureStream(fps).getVideoTracks()), 'v',
                 ['video/webm;codecs=h264', 'video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm'], { videoBitsPerSecond: bitrate });
  }
  const at = []; for (const d of P.audio) for (const t of d.stream.getAudioTracks()) at.push(t);
  if (at.length) {
    let astream = new MediaStream(at);
    if (at.length > 1) {  // several AudioContexts/media elements -> mix into one track
      const ac = new AudioContext(); const dst = ac.createMediaStreamDestination();
      for (const t of at) ac.createMediaStreamSource(new MediaStream([t])).connect(dst);
      astream = dst.stream;
    }
    na = at.length;
    amime = make(astream, 'a', ['audio/webm;codecs=opus', 'audio/webm'], { audioBitsPerSecond: 192000 });
  }
  for (const r of P.recs) r.start(1000);
  P.t0 = performance.now();
  return { mime: vmime, amime, audio: na, canvas: canvas ? [canvas.width, canvas.height] : null };
}
"""

FPS_JS = r"""(ms) => new Promise((r) => { let n = 0; const t0 = performance.now();
  const f = () => { n++; if (performance.now() - t0 < ms) requestAnimationFrame(f); else r(n); }; requestAnimationFrame(f); })"""

STOP_REC_JS = r"""
async ({ sink }) => { const P = window.__promo; if (!P.recs || !P.recs.length) return {};
  await Promise.all(P.recs.map((rec) => new Promise((r) => { rec.onstop = r; rec.stop(); })));
  for (const [kind, parts] of Object.entries(P.parts)) {  // binary upload to the local sink, in order
    for (let i = 0; i < parts.length; i++)
      await fetch(`${sink}/${kind}/${i}`, { method: 'POST', body: parts[i], headers: { 'Content-Type': 'text/plain' } });
    P.parts[kind] = [];
  }
  return { v: P.start_v != null ? (P.start_v - P.t0) / 1000 : null, a: P.start_a != null ? (P.start_a - P.t0) / 1000 : null }; }
"""


class Sink:
    """Local HTTP receiver for recorder chunks: POST /<kind>/<seq>, written in order to files[kind]."""
    def __init__(self, files):
        import http.server, threading
        self.files = {k: open(p, 'wb') for k, p in files.items()}; self.next = {k: 0 for k in files}; self.buf = {k: {} for k in files}
        self.lock = threading.Lock(); sink = self
        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *x): pass
            def _ok(self):
                self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true'); self.send_header('Content-Length', '0'); self.end_headers()
            def do_OPTIONS(self):
                self.send_response(204); self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST'); self.send_header('Access-Control-Allow-Headers', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true'); self.end_headers()
            def do_POST(self):
                _, kind, seq = self.path.split('/')[:3]
                data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
                sink.put(kind, int(seq), data); self._ok()
        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.url = f'http://127.0.0.1:{self.httpd.server_address[1]}'
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def put(self, kind, seq, data):
        with self.lock:
            b = self.buf[kind]; b[seq] = data
            while self.next[kind] in b:
                self.files[kind].write(b.pop(self.next[kind])); self.next[kind] += 1

    def close(self):
        self.httpd.shutdown()
        with self.lock:
            for k, f in self.files.items():
                for seq in sorted(self.buf[k]): f.write(self.buf[k][seq])  # gaps: keep what arrived
                f.close()


class Api:
    """Handed to scenario.run(api). Keep scenarios short and deterministic."""
    def __init__(self, page, shots_dir, t0):
        self.page, self.shots_dir, self._t0 = page, shots_dir, t0
        self.shots = []

    def js(self, code, arg=None):
        return self.page.evaluate(code, arg) if arg is not None else self.page.evaluate(code)

    def wait(self, s): self.page.wait_for_timeout(int(s * 1000))
    def key_down(self, k): self.page.keyboard.down(k)
    def key_up(self, k): self.page.keyboard.up(k)
    def press(self, k, hold=0.08): self.page.keyboard.down(k); self.wait(hold); self.page.keyboard.up(k)
    def hold(self, keys, s):
        keys = [keys] if isinstance(keys, str) else keys
        for k in keys: self.page.keyboard.down(k)
        self.wait(s)
        for k in reversed(keys): self.page.keyboard.up(k)
    def click(self, x, y): self.page.mouse.click(x, y)
    def mouse_move(self, x, y, steps=10): self.page.mouse.move(x, y, steps=steps)
    def drag(self, x0, y0, x1, y1, steps=20):
        m = self.page.mouse; m.move(x0, y0); m.down(); m.move(x1, y1, steps=steps); m.up()

    def event(self, type_, weight=1, label=''):
        self.page.evaluate('([a, b, c]) => window.__promo.event(a, b, c)', [type_, weight, label])

    def director(self, on=True):
        return self.page.evaluate('(on) => { const d = window.__promo && window.__promo.director; if (d) { d(on); return true; } return false; }', on)

    def t(self):
        return self.page.evaluate('() => window.__promo.now()')

    def shot(self, name, full_ui=True):
        """High-quality still at the current moment (page screenshot, DPR applies)."""
        os.makedirs(self.shots_dir, exist_ok=True)
        p = os.path.join(self.shots_dir, f'{name}.png')
        t = self.t()
        self.page.screenshot(path=p)
        self.shots.append({'name': name, 't': t, 'file': os.path.relpath(p, os.path.dirname(os.path.dirname(self.shots_dir)))})
        self.event('shot', 0, name)
        return p


def start_server(project, no_build, port):
    pkg = os.path.join(project, 'package.json')
    if not os.path.exists(pkg):
        die('no package.json: pass --url of a running game')
    if not no_build:
        r = subprocess.run(['npm', 'run', 'build'], cwd=project, capture_output=True, text=True)
        if r.returncode != 0:
            die('npm run build failed:\n' + (r.stdout + r.stderr)[-1500:])
    p = subprocess.Popen(['npx', 'vite', 'preview', '--host', '127.0.0.1', '--port', str(port), '--strictPort'],
                         cwd=project, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    url = f'http://127.0.0.1:{port}/'
    for _ in range(120):
        try:
            urllib.request.urlopen(url, timeout=1); return p, url
        except Exception:
            time.sleep(0.5)
    os.killpg(p.pid, signal.SIGTERM); die('vite preview did not start')


def load_scenario(path):
    spec = importlib.util.spec_from_file_location('promo_scenario', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if not hasattr(mod, 'run'):
        die(f'{path} must define run(api)')
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--url')
    ap.add_argument('--serve', help='serve this built folder (e.g. dist) in-process instead of vite preview')
    ap.add_argument('--no-build', action='store_true')
    ap.add_argument('--port', type=int, default=4191)
    ap.add_argument('--take', default=time.strftime('take_%m%d_%H%M%S'))
    ap.add_argument('--size')
    ap.add_argument('--fps', type=int)
    ap.add_argument('--dpr', type=float, default=1.0)
    ap.add_argument('--seconds', type=float, default=30)
    ap.add_argument('--scenario')
    ap.add_argument('--manual', action='store_true')
    ap.add_argument('--ui', action='store_true', help='record whole page incl. DOM HUD (CDP screencast)')
    ap.add_argument('--ready', default='() => document.querySelector("canvas") !== null',
                    help='JS predicate: game is ready to record')
    ap.add_argument('--warmup', type=float, default=2.0)
    ap.add_argument('--no-director', action='store_true')
    ap.add_argument('--bitrate', type=int, default=24_000_000)
    ap.add_argument('--chrome-arg', action='append', default=[], help='extra Chromium flag (repeatable)')
    ap.add_argument('--keep-rec', action='store_true', help='keep the raw recorder file (debug)')
    ap.add_argument('--min-fps', type=float, default=0, help='re-record the take until the game rendered >= this fps')
    ap.add_argument('--retries', type=int, default=3, help='tries for --min-fps')
    ap.add_argument('--init-js', action='append', default=[], help='extra init script, e.g. tools/lib/spy.js (SDK emulation)')
    a = ap.parse_args()
    if a.min_fps and not os.environ.get('PROMO_CAPTURE_TRY'):  # retry loop: each try is a fresh child capture
        meta_p = os.path.join(promo_dir(os.path.abspath(a.project)), 'raw', f'{a.take}.events.json')
        best = 0.0
        for k in range(1, max(1, a.retries) + 1):
            rc = subprocess.run([sys.executable] + sys.argv, env=dict(os.environ, PROMO_CAPTURE_TRY=str(k))).returncode
            got = json.load(open(meta_p)).get('real_fps', 0) if rc == 0 and os.path.exists(meta_p) else 0
            print(f'try {k}: real_fps={got}', flush=True); best = max(best, got)
            if rc and rc != 0 and not got: sys.exit(rc)
            if got >= a.min_fps: return
        print(f'WARN real_fps {got} < {a.min_fps} after {a.retries} tries: the machine is busy (close heavy apps, '
              'run no ffmpeg/analysis during capture) — the last take is kept')
        return

    from playwright.sync_api import sync_playwright
    need_ffmpeg()
    project = os.path.abspath(a.project)
    cfg = load_config(project)
    size = a.size or cfg['capture'].get('size', '1920x1080')
    W, H = (int(x) for x in size.lower().split('x'))
    fps = a.fps or int(cfg['capture'].get('fps', 60))
    raw = os.path.join(promo_dir(project), 'raw'); os.makedirs(raw, exist_ok=True)
    free = shutil.disk_usage(raw).free / 1e9
    need = (0.03 if a.ui else 0.01) * (a.seconds if a.manual or not a.scenario else 60) + 1.5   # --ui frames ~25 MB/s
    if free < need:
        die(f'only {free:.1f} GB free on disk, a take needs ~{need:.1f} GB (--ui JPEG frames ~25 MB/s): '
            'free space or record one short take per loop')
    tmp = os.path.join(raw, f'.{a.take}.v.webm'); tmpa = os.path.join(raw, f'.{a.take}.a.webm'); shots_dir = os.path.join(raw, a.take, 'shots')
    scenario = None
    if not a.manual:
        sp = a.scenario or os.path.join(promo_dir(project), 'scenario.py')
        if not os.path.exists(sp):
            die(f'no scenario ({sp}); pass --scenario or --manual')
        scenario = load_scenario(sp)

    server = None
    url = a.url
    if not url and a.serve:
        import functools, http.server, threading
        root = a.serve if os.path.isabs(a.serve) else os.path.join(project, a.serve)
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *x): pass
        h = functools.partial(Quiet, directory=root)
        httpd = http.server.ThreadingHTTPServer(('127.0.0.1', a.port), h)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{a.port}/'
    elif not url:
        server, url = start_server(project, a.no_build, a.port)
    sink = Sink({'v': tmp, 'a': tmpa}); sink_url = sink.url
    frames = []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=False, args=['--use-angle=metal', f'--window-size={min(W, 1600)},{min(H, 1000)}',
                                                         '--autoplay-policy=no-user-gesture-required', '--hide-scrollbars',
                                                         '--disable-renderer-backgrounding', '--disable-background-timer-throttling',
                                                         '--disable-backgrounding-occluded-windows', '--disable-features=CalculateNativeWinOcclusion'] + a.chrome_arg)
            ctx = br.new_context(viewport={'width': W, 'height': H}, device_scale_factor=a.dpr, locale='en-US')
            for f in a.init_js:
                ctx.add_init_script(path=os.path.join(project, f) if not os.path.isabs(f) else f)
            ctx.add_init_script(INIT_JS)
            pg = ctx.new_page()
            errors = []
            pg.on('pageerror', lambda e: errors.append(str(e)))
            pg.goto(url)
            pg.wait_for_function(a.ready, timeout=120000)
            pg.wait_for_timeout(int(a.warmup * 1000))
            if hasattr(scenario, 'prepare'):
                scenario.prepare(Api(pg, shots_dir, 0))
            pg.mouse.click(W // 2, H // 2)  # user gesture: unlocks audio
            pg.wait_for_timeout(300)
            directed = False if a.no_director else pg.evaluate('() => { const d = window.__promo && window.__promo.director; if (d) { d(true); return true; } return false; }')
            cdp = None
            if a.ui:
                cdp = ctx.new_cdp_session(pg)
                fdir = os.path.join(raw, f'.{a.take}.frames'); os.makedirs(fdir, exist_ok=True)
                def on_frame(p):
                    n = len(frames); fp = os.path.join(fdir, f'{n:06d}.jpg')
                    open(fp, 'wb').write(base64.b64decode(p['data']))
                    frames.append((p['metadata']['timestamp'], fp))
                    try: cdp.send('Page.screencastFrameAck', {'sessionId': p['sessionId']})
                    except Exception: pass
                cdp.on('Page.screencastFrame', on_frame)
                cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': W, 'maxHeight': H, 'everyNthFrame': 1})
            pre_fps = pg.evaluate(FPS_JS, 1000)
            info = pg.evaluate(START_REC_JS, {'fps': fps, 'ui': a.ui, 'bitrate': a.bitrate})
            print(f'recording {a.take}: {W}x{H}@{fps} video={info.get("mime")} audio={info.get("amime")} audio_sources={info.get("audio")} director={directed}', flush=True)
            api = Api(pg, shots_dir, 0)
            settle = 0.0
            if info.get('mime') and not a.ui:  # encoder start-up stalls the page for a while: wait it out, trim it later
                t_s = time.time(); fps_ok = max(20, int(pre_fps * 0.7))
                while time.time() - t_s < 90:
                    got = pg.evaluate('() => window.__promo.bytes || 0')
                    f_now = pg.evaluate(FPS_JS, 500) * 2
                    if got > 20000 and f_now >= fps_ok: break
                else:
                    print(f'WARN recorder still stalling after 90s (bytes={got}, fps={f_now})')
                settle = pg.evaluate('() => window.__promo.now()') + 0.2
                pg.evaluate('() => { window.__promo.events = []; }')
                print(f'settled after {settle:.1f}s (fps {f_now}, page fps before {pre_fps})')
            if a.manual:
                print(f'MANUAL: play in the window for {a.seconds:.0f}s; F9 or ` marks a juicy moment')
                pg.wait_for_timeout(int(a.seconds * 1000))
            else:
                try:
                    scenario.run(api)
                except Exception as e:  # keep what was recorded
                    print('scenario error:', e)
            events = pg.evaluate('() => window.__promo.events')
            dur = pg.evaluate('() => window.__promo.now()')
            starts = pg.evaluate(STOP_REC_JS, {'sink': sink_url}) or {}
            if cdp:
                try: cdp.send('Page.stopScreencast')
                except Exception: pass
            if directed:
                pg.evaluate('() => window.__promo.director(false)')
            br.close()
    finally:
        sink.close()
        if server:
            try: os.killpg(server.pid, signal.SIGTERM)
            except Exception: pass

    master = os.path.join(raw, f'{a.take}.mp4')
    enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-g', str(fps // 2), '-pix_fmt', 'yuv420p']
    have_v = os.path.getsize(tmp) > 0; have_a = os.path.getsize(tmpa) > 0
    a_in = []
    if have_a:  # align the audio recorder to the video timeline (both relative to P.t0)
        off = (starts.get('a') or 0) - (0 if a.ui else (starts.get('v') or 0))
        a_in = ['-itsoffset', f'{off:.3f}', '-i', tmpa]
    if a.ui:
        if not frames: die('no screencast frames captured')
        lst = os.path.join(raw, f'.{a.take}.frames.txt')
        with open(lst, 'w') as f:
            for i, (ts, fp) in enumerate(frames):
                d = (frames[i + 1][0] - ts) if i + 1 < len(frames) else 1 / fps
                f.write(f"file '{fp}'\nduration {max(d, 0.001):.4f}\n")
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst] + a_in + ['-map', '0:v']
        if have_a: cmd += ['-map', '1:a', '-c:a', 'aac', '-b:a', '192k']
        cmd += ['-vf', f'fps={fps},scale={W}:{H}:flags=lanczos'] + enc + ['-shortest', master]
        run(cmd)
    else:
        if not have_v: die('recorder produced no data (canvas tainted or MediaRecorder unsupported): try --ui')
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', tmp] + a_in + ['-map', '0:v'] + (['-map', '1:a', '-c:a', 'aac', '-b:a', '192k'] if have_a else [])
        run(cmd + ['-ss', f'{settle:.3f}', '-vf', f'fps={fps}'] + enc + [master])
    real_fps = float(fps)
    if have_v and not a.ui:  # frames the page really rendered (the master is CFR with duplicates)
        pts = [float(x) for x in run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time',
                                      '-of', 'csv=p=0', tmp]).stdout.split() if x.strip()]
        pts = [x for x in pts if x >= settle]
        if len(pts) > 10: real_fps = round((len(pts) - 1) / max(0.1, pts[-1] - pts[0]), 1)
    elif a.ui and len(frames) > 10:
        real_fps = round((len(frames) - 1) / max(0.1, frames[-1][0] - frames[0][0]), 1)
    if settle:
        for e in events: e['t'] = round(e['t'] - settle, 3)
        for s_ in api.shots: s_['t'] = round(s_['t'] - settle, 3)
        events = [e for e in events if e['t'] >= 0]; dur -= settle
    for p in (() if a.keep_rec else (tmp, tmpa)):
        try: os.remove(p)
        except OSError: pass
    if a.ui:
        shutil.rmtree(os.path.join(raw, f'.{a.take}.frames'), ignore_errors=True)
        try: os.remove(os.path.join(raw, f'.{a.take}.frames.txt'))
        except OSError: pass
    pr = probe(master)
    vdur = float(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=duration', '-of', 'csv=p=0', master]).stdout.strip() or 0)
    if vdur < dur * 0.9:
        print(f'WARN video track {vdur:.1f}s < take {dur:.1f}s: the page rendered too few frames (window hidden/minimised or GPU busy)')
    if real_fps < fps * 0.75:
        print(f'note: the game rendered {real_fps} fps (< {fps}): close heavy apps for smoother takes; slow-mo will be interpolated')
    meta = {'take': a.take, 'w': pr['w'], 'h': pr['h'], 'fps': fps, 'real_fps': real_fps, 'dur': pr['dur'], 'audio': pr['audio'],
            'mode': 'ui' if a.ui else 'canvas', 'manual': a.manual, 'director': bool(directed),
            'events': events, 'shots': api.shots, 'page_errors': errors[:10]}
    json.dump(meta, open(os.path.join(raw, f'{a.take}.events.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'OK {os.path.relpath(master, project)}: {pr["w"]}x{pr["h"]} {pr["dur"]:.1f}s audio={pr["audio"]} '
          f'events={len(events)} shots={len(api.shots)} errors={len(errors)}')


if __name__ == '__main__':
    main()
