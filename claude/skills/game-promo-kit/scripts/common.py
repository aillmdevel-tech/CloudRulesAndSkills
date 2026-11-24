"""Shared helpers for game-promo-kit: paths, config, platform presets, ffmpeg, fonts."""
import json, os, re, shutil, subprocess, sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORMS_FILE = os.path.join(KIT, 'references', 'platforms.json')
def _gf_from_claude_md():
    """GameFactory folder from ~/.claude/CLAUDE.md («GameFactory: `…`»), so a new device needs no edits."""
    try:
        m = re.search(r'GameFactory: `([^`]+)`', open(os.path.expanduser('~/.claude/CLAUDE.md'), encoding='utf-8').read())
        return os.path.join(os.path.expanduser(m.group(1)), 'UIFX', 'sounds') if m else ''
    except OSError:
        return ''


UIFX_SOUNDS = [
    os.environ.get('UIFX_SOUNDS', ''),
    _gf_from_claude_md(),
    os.path.expanduser('~/Downloads/WebAIGames/Rules/GameFactory/UIFX/sounds'),
]

DEFAULT_CONFIG = {
    'title': {'en': 'My Game'},
    'languages': ['en'],
    'texts': {'hook': {'en': 'CAN YOU BEAT IT?'}, 'cta': {'en': 'PLAY NOW'}},
    'captions': {},
    'font': 'Arial Black',
    'font_file': '',
    'colors': {'text': '#FFFFFF', 'accent': '#FFD23F', 'outline': '#16162A'},
    'music': '',
    'music_volume': 0.8,
    'game_volume': 0.7,
    'bpm': 0,
    'capture': {'size': '1920x1080', 'fps': 60},
    'focus_x': 0.5,
    'focus_y': 0.5,
    'cover_source': '',
    'logo': '',
}


def die(msg):
    print('ERROR:', msg, file=sys.stderr)
    raise SystemExit(1)


def promo_dir(project):
    d = os.path.join(os.path.abspath(project), 'promo')
    os.makedirs(d, exist_ok=True)
    return d


def load_config(project):
    p = os.path.join(promo_dir(project), 'config.json')
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(p):
        user = json.load(open(p, encoding='utf-8'))
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict) and k not in ('texts', 'captions', 'title'):
                cfg[k].update(v)
            else:
                cfg[k] = v
    else:
        print(f'note: {p} not found, using defaults (copy templates/config.example.json)')
    return cfg


def platforms():
    data = json.load(open(PLATFORMS_FILE, encoding='utf-8'))
    return {k: v for k, v in data.items() if not k.startswith('_')}


def platform(name):
    all_ = platforms()
    if name not in all_:
        die(f'unknown platform {name}; known: {", ".join(all_)}')
    return all_[name]


def text_for(cfg, key, lang):
    """Localized string: texts[key][lang] -> texts[key]['en'] -> ''."""
    block = cfg.get('texts', {}).get(key) if key != 'title' else cfg.get('title')
    if isinstance(block, str):
        return block
    if not block:
        return ''
    return block.get(lang) or block.get('en') or next(iter(block.values()), '')


def hooks_for(cfg, lang):
    """texts.hook may be a string, {lang: str}, or {lang: [variant1, variant2, ...]} for A/B ads."""
    block = cfg.get('texts', {}).get('hook')
    if not block: return []
    if isinstance(block, (str, list)): v = block
    else: v = block.get(lang) or block.get('en') or next(iter(block.values()), '')
    return [x for x in ([v] if isinstance(v, str) else v) if x]


def synth(path, kind, bpm=120, dur=20.0, sr=44100):
    """Royalty-free procedural audio (written as WAV): 'beat' bed (kick/clap/hat/offbeat bass) or 'boom' impact."""
    import array, math, random, wave
    rnd = random.Random(7)
    n = int(dur * sr); buf = array.array('f', bytes(4 * n))
    def shot(length, fn): return [fn(i / sr) for i in range(int(length * sr))]
    def add(t0, s, g=1.0):
        i0 = int(t0 * sr)
        for i, v in enumerate(s[:max(0, n - i0)]): buf[i0 + i] += v * g
    kick = shot(0.38, lambda t: math.sin(2 * math.pi * (45 * t + 95 * (1 - math.exp(-t * 28)) / 28)) * math.exp(-t * 9))
    if kind == 'boom':
        noise = shot(0.08, lambda t: (rnd.random() * 2 - 1) * math.exp(-t * 60))
        boom = shot(0.9, lambda t: math.sin(2 * math.pi * (32 * t + 140 * (1 - math.exp(-t * 14)) / 14)) * math.exp(-t * 4.5))
        add(0, boom, 0.95); add(0, noise, 0.5)
    else:
        beat = 60.0 / bpm; prev = [0.0]
        def hp(t):  # crude high-passed noise
            x = rnd.random() * 2 - 1; y = x - prev[0]; prev[0] = x; return y
        clap = shot(0.22, lambda t: hp(t) * (math.exp(-t * 22) + 0.6 * math.exp(-((t - 0.012) ** 2) * 4e5)))
        hat = shot(0.05, lambda t: hp(t) * math.exp(-t * 90))
        crash = shot(1.4, lambda t: hp(t) * math.exp(-t * 3.2))
        notes = [55.0, 43.65, 65.41, 49.0]
        k = 0
        while k * beat < dur:
            t = k * beat; bar = (k // 4) % 4
            add(t, kick, 0.9)
            if k % 4 in (1, 3): add(t, clap, 0.35)
            add(t + beat / 2, hat, 0.22); add(t + beat / 4 * 3, hat, 0.1)
            f = notes[bar]
            bass = shot(beat / 2, lambda x, f=f: (math.sin(2 * math.pi * f * x) + 0.35 * math.sin(4 * math.pi * f * x))
                        * (1 - math.exp(-x * 60)) * math.exp(-x * 5))
            add(t + beat / 2, bass, 0.32)
            k += 1
        add(0, crash, 0.25)
    peak = max(1e-6, max(abs(v) for v in buf))
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(array.array('h', (int(max(-1, min(1, v / peak * 0.9)) * 32767) for v in buf)).tobytes()); w.close()
    return path


def caption_for(cfg, ev, lang):
    caps = cfg.get('captions', {})
    for k in (ev.get('label'), ev.get('type')):
        if k and k in caps:
            c = caps[k]
            return c.get(lang) or c.get('en') or ''
    return ''


def run(cmd, quiet=True, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        tail = (r.stderr or r.stdout)[-1500:]
        die(f'command failed: {" ".join(cmd[:6])} ...\n{tail}')
    return r


def need_ffmpeg():
    for b in ('ffmpeg', 'ffprobe'):
        if not shutil.which(b):
            die(f'{b} not found (brew install ffmpeg)')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True)
    if r.returncode != 0:
        die('ffmpeg does not start: ' + (r.stderr[-400:] or '') + '\nfix: brew upgrade ffmpeg')
    return r.stdout


def has_filter(name):
    out = need_ffmpeg()
    return re.search(rf'\s{re.escape(name)}\s', out) is not None


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path])
    j = json.loads(r.stdout)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    fps = 30.0
    if v and v.get('avg_frame_rate', '0/0') != '0/0':
        n, d = v['avg_frame_rate'].split('/')
        fps = float(n) / float(d or 1)
    return {
        'w': int(v['width']) if v else 0, 'h': int(v['height']) if v else 0, 'fps': fps,
        'dur': float(j['format'].get('duration', 0) or 0), 'audio': a is not None,
        'size_mb': int(j['format'].get('size', 0)) / 1e6,
    }


def font_file(cfg):
    """Path to a TTF/OTF for Pillow and libass. font_file wins, else fc-match on the family."""
    ff = cfg.get('font_file')
    if ff:
        ff = os.path.expanduser(ff)
        if os.path.exists(ff):
            return ff
        print(f'warn: font_file {ff} not found, falling back to {cfg.get("font")}')
    if shutil.which('fc-match'):
        r = subprocess.run(['fc-match', '-f', '%{file}', cfg.get('font', 'Arial Black')], capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(r.stdout.strip()):
            return r.stdout.strip()
    for c in ('/System/Library/Fonts/Supplemental/Arial Black.ttf', '/Library/Fonts/Arial Black.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(c):
            return c
    die('no font found: set font_file in promo/config.json')


def font_family(path):
    if shutil.which('fc-scan'):
        r = subprocess.run(['fc-scan', '-f', '%{family[0]}', path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return os.path.splitext(os.path.basename(path))[0]


def sound(name):
    for d in UIFX_SOUNDS:
        if d:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None


def hex_to_ass(h, alpha=0):
    h = h.lstrip('#')
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f'&H{alpha:02X}{b}{g}{r}'.upper()


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_moments(project):
    p = os.path.join(promo_dir(project), 'moments.json')
    if not os.path.exists(p):
        die('promo/moments.json missing: run moments.py first')
    return json.load(open(p, encoding='utf-8'))


def take_paths(project, take):
    raw = os.path.join(promo_dir(project), 'raw')
    return os.path.join(raw, f'{take}.mp4'), os.path.join(raw, f'{take}.events.json')


def langs_arg(cfg, arg):
    if arg:
        return [x.strip() for x in arg.split(',') if x.strip()]
    return cfg.get('languages') or ['en']
