#!/usr/bin/env python3
"""Publisher helper for CrazyGames + Playgama. Run: publisher.py <command> --project DIR. See ../SKILL.md."""
import argparse, datetime, functools, hashlib, http.server, json, os, re, shutil, subprocess, sys, threading, zipfile

STAGES = ['audit', 'localization', 'promo', 'drafts', 'media_upload', 'alex_playtest', 'local_moderation', 'fixes', 'submit']
LANGS = ['en', 'ru', 'es', 'pt-BR', 'tr']
CHARS = {
    'en': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
    'ru': 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    'es': 'ÁÉÍÑÓÚÜáéíñóúü¿¡',
    'pt-BR': 'ÀÁÂÃÇÉÊÍÓÔÕÚàáâãçéêíóôõú',
    'tr': 'ÇĞİÖŞÜçğıöşü',
}
MEDIA = {
    'crazygames': {'cover_16x9': (1920, 1080), 'cover_2x3': (800, 1200), 'cover_1x1': (800, 800),
                   'video_16x9': (1920, 1080), 'video_2x3': (1080, 1620)},
    'playgama': {'cover_1x1': (800, 800), 'cover_9x16': (1080, 1920), 'cover_16x9': (1920, 1080)},
}
VIDEO_MAX_MB = {'crazygames': 50, 'playgama': 200}
CHUNK = 9 * 1024 * 1024
SKIP_DIRS = {'node_modules', 'dist', 'release', '.git', 'promo', 'tools', 'tests', 'docs', 'references', 'assets_src', 'art'}


def state_path(a): return os.path.join(a.state_dir or os.path.join(a.project, 'publish'), 'STATE.json')


def load(a):
    p = state_path(a)
    if not os.path.exists(p): sys.exit('нет STATE.json: сначала init')
    return json.load(open(p, encoding='utf-8'))


def save(a, s):
    p = state_path(a)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    s['updated'] = datetime.datetime.now().isoformat(timespec='seconds')
    tmp = p + '.tmp'
    json.dump(s, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    os.replace(tmp, p)


def cmd_init(a):
    if os.path.exists(state_path(a)) and not a.force:
        print('STATE.json уже есть, продолжаем с него'); return cmd_status(a)
    save(a, {'project': a.project, 'icon': a.icon, 'cover': a.cover, 'languages': LANGS,
             'stages': {k: {'status': 'todo', 'note': ''} for k in STAGES},
             'portals': {'crazygames': {}, 'playgama': {}}})
    print('создан', state_path(a))


def cmd_status(a):
    s = load(a)
    mark = {'todo': '·', 'active': '▶', 'done': '✓', 'blocked': '!'}
    for k in STAGES:
        v = s['stages'][k]; print(f"{mark.get(v['status'], '?')} {k}" + (f" — {v['note']}" if v['note'] else ''))


def cmd_stage(a):
    s = load(a)
    if a.id not in STAGES: sys.exit(f'этапы: {STAGES}')
    s['stages'][a.id] = {'status': a.value, 'note': a.note or s['stages'][a.id]['note']}
    save(a, s); cmd_status(a)


def source_files(root, exts=('.ts', '.tsx', '.js', '.jsx', '.html', '.vue')):
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in SKIP_DIRS and not d.startswith('.')]
        for f in fs:
            if f.endswith(exts) and not f.endswith('.d.ts') and '.test.' not in f: yield os.path.join(r, f)


def newest(root, subdirs):
    best = 0
    for d in subdirs:
        for r, _, fs in os.walk(os.path.join(root, d)):
            for f in fs:
                try: best = max(best, os.path.getmtime(os.path.join(r, f)))
                except OSError: pass
    return best


def latest_zip(root, plat):
    z = [os.path.join(root, 'release', f) for f in os.listdir(os.path.join(root, 'release'))
         if plat in f and f.endswith('.zip')] if os.path.isdir(os.path.join(root, 'release')) else []
    return max(z, key=os.path.getmtime) if z else None


def cmd_audit(a):
    root = a.project
    pkg = json.load(open(os.path.join(root, 'package.json'))) if os.path.exists(os.path.join(root, 'package.json')) else {}
    sc = pkg.get('scripts', {})
    print('сборки:', {k: k in sc for k in ('build:playgama', 'build:crazygames', 'pack:playgama', 'smoke', 'moderate')})
    print('модератор:', [f[:-5] for f in os.listdir(os.path.join(root, 'tools/moderator/rules'))] if os.path.isdir(os.path.join(root, 'tools/moderator/rules')) else 'НЕТ')
    src = ''.join(open(f, errors='replace').read() for f in source_files(os.path.join(root, 'src'))) if os.path.isdir(os.path.join(root, 'src')) else ''
    print('SDK:', {'playgama_bridge': 'bridge.platform' in src or 'playgama' in src.lower(), 'crazygames': 'CrazyGames' in src,
                   'lang_playgama': 'platform.language' in src, 'lang_crazygames': 'systemInfo' in src})
    code = newest(root, ['src', 'public'])
    for p in ('crazygames', 'playgama'):
        z = latest_zip(root, p)
        if not z: print(f'{p}: zip НЕТ'); continue
        print(f"{p}: {os.path.basename(z)} {os.path.getsize(z) / 1e6:.1f} МБ · " + ('код НОВЕЕ zip, нужна пересборка' if code > os.path.getmtime(z) else 'актуален по датам'))
    free = shutil.disk_usage(root).free / 1e9
    print(f'диск: {free:.1f} ГБ свободно' + (' · МАЛО для промо (нужно ≥ 8)' if free < 8 else ''))
    scan_summary(root)


STR_RE = re.compile(r"""(?:textContent|innerText|placeholder|title|ariaLabel)\s*=\s*(['"`])((?:(?!\1).)*[A-Za-z]{3,}(?:(?!\1).)*)\1|\b(?:label|text|title|desc|description|hint|name)\s*:\s*(['"`])((?:(?!\3).)*[A-Za-z]{2,}\s[A-Za-z](?:(?!\3).)*)\3|>\s*([A-Z][A-Za-z']+(?:\s+[A-Za-z'!?.,]+)*)\s*</""")


def scan(root):
    hits, keys = [], 0
    for f in source_files(os.path.join(root, 'src')):
        rel = os.path.relpath(f, root)
        if re.search(r'(^|/)(i18n|locales?)(/|$)', rel): continue
        for n, line in enumerate(open(f, errors='replace'), 1):
            keys += len(re.findall(r"\bt\(['\"`]", line))
            if line.lstrip().startswith(('//', '*', '/*', 'import ')): continue
            for m in STR_RE.finditer(line):
                txt = m.group(2) or m.group(4) or m.group(5) or ''
                if re.search(r'^[a-z0-9_.\-/]+$|https?:|\.(png|webp|glb|mp3|ogg|css)$|\$\{', txt): continue
                hits.append((rel, n, txt.strip()[:70]))
    return hits, keys


def locale_files(root):
    out = {}
    for f in source_files(os.path.join(root, 'src'), ('.ts', '.js', '.json')):
        m = re.search(r'(?:i18n|locales?)/(?:.*/)?(en|ru|es|pt-BR|pt|tr)\.(?:ts|js|json)$', f)
        if m: out['pt-BR' if m.group(1) == 'pt' else m.group(1)] = f
    return out


def scan_summary(root):
    hits, keys = scan(root); loc = locale_files(root)
    print(f"локализация: словари {sorted(loc) or 'нет'} · нет: {[l for l in LANGS if l not in loc]} · вызовов t(): {keys} · зашитых строк (эвристика): {len(hits)}")
    return hits, loc


def cmd_i18n_scan(a):
    hits, loc = scan_summary(a.project)
    key_re = re.compile(r"""^\s*['"]?([\w.\-]+)['"]?\s*:""", re.M)
    sets = {l: set(key_re.findall(open(f, errors='replace').read())) for l, f in loc.items()}
    if 'en' in sets:
        for l, ks in sets.items():
            if l != 'en' and sets['en'] - ks: print(f'{l}: нет {len(sets["en"] - ks)} ключей, напр. {sorted(sets["en"] - ks)[:5]}')
    out = os.path.join(a.state_dir or os.path.join(a.project, 'publish'), 'i18n_scan.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write('# Зашитые строки (эвристика, просмотри)\n\n' + '\n'.join(f'- `{p}:{n}` {t}' for p, n, t in hits))
    print('список:', out)


FONT_JS = r"""async ([b64, chars]) => {
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const face = new FontFace('PubCheck', bytes.buffer);
  await face.load(); document.fonts.add(face);
  const ctx = document.createElement('canvas').getContext('2d');
  const w = (c, f) => { ctx.font = `64px ${f}`; return ctx.measureText(c).width; };
  // a glyph the font lacks falls through to the fallback, so its width follows the fallback
  const has = c => w(c, 'PubCheck, monospace') === w(c, 'PubCheck, serif');
  const out = [...chars].filter(has).join('');
  document.fonts.delete(face);
  return out;
}"""


def cmd_i18n_fonts(a):
    import base64
    from playwright.sync_api import sync_playwright
    roots = [os.path.join(a.project, d) for d in ('public', 'src')]
    fonts = [os.path.join(r, f) for base in roots for r, _, fs in os.walk(base) for f in fs if f.lower().endswith(('.woff2', '.woff', '.ttf', '.otf'))]
    if not fonts: print('шрифтов в проекте нет (системные)'); return
    total = {l: set() for l in LANGS}; failed = 0; partial = []; every = ''.join(CHARS.values())
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto('about:blank')
        for path in sorted(fonts):
            try: have_all = set(pg.evaluate(FONT_JS, [base64.b64encode(open(path, 'rb').read()).decode(), every]))
            except Exception as e:
                failed += 1; print(f'{os.path.relpath(path, a.project)}: не прочитан ({type(e).__name__})'); continue
            row = []
            for l in LANGS:
                have = {c for c in CHARS[l] if c in have_all}; total[l] |= have
                row.append(f"{l} {len(have) * 100 // len(CHARS[l])}%")
                if len(have) < len(CHARS[l]): partial.append(f"{os.path.basename(path)} · {l}: нет {''.join(c for c in CHARS[l] if c not in have)}")
            print(os.path.relpath(path, a.project), '·', ' '.join(row))
        b.close()
    if partial: print('НЕПОЛНЫЕ ШРИФТЫ (если шрифт стоит в UI, буквы уйдут в чужой fallback):'); print('\n'.join('  ' + x for x in partial))
    print('покрытие всеми шрифтами вместе:')
    miss_any = bool(partial)
    for l in LANGS:
        miss = ''.join(c for c in CHARS[l] if c not in total[l]); miss_any |= bool(miss); print(f"  {l}: {'OK' if not miss else 'нет ' + miss}")
    if failed: print(f'не прочитано шрифтов: {failed}, итог неполный')
    sys.exit(1 if miss_any or failed else 0)


OVERFLOW_JS = r"""() => {
  const W = innerWidth, H = innerHeight, bad = [];
  for (const el of document.querySelectorAll('body *')) {
    const direct = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!direct) continue;
    const st = getComputedStyle(el), r = el.getBoundingClientRect();
    if (st.display === 'none' || st.visibility === 'hidden' || +st.opacity === 0 || !r.width || !r.height) continue;
    const off = r.left < -1 || r.top < -1 || r.right > W + 1 || r.bottom > H + 1;
    const clip = el.scrollWidth > el.clientWidth + 1 && st.overflowX !== 'visible' && st.display !== 'inline';
    if (off || clip) bad.push({text: el.textContent.trim().slice(0, 40), why: off ? 'за экраном' : 'обрезан', cls: String(el.className).slice(0, 40)});
  }
  return {bad: bad.slice(0, 25), html: document.documentElement.lang};
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass


def cmd_i18n_fit(a):
    from playwright.sync_api import sync_playwright
    out = a.out or os.path.join(a.state_dir or os.path.join(a.project, 'publish'), 'i18n_fit')
    os.makedirs(out, exist_ok=True)
    srv = None; url = a.url
    if not url:
        dist = os.path.join(a.project, 'dist')
        if not os.path.exists(os.path.join(dist, 'index.html')): sys.exit('нет dist/index.html: сначала сборка')
        srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=dist))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{srv.server_address[1]}/'
    sizes = {'desktop': (1280, 720), 'iframe': (907, 510), 'mobile_land': (800, 450), 'portrait': (390, 844)}
    total = 0; wrong_lang = []; shots_failed = 0
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--mute-audio', '--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for lang in (a.langs.split(',') if a.langs else LANGS):
            for name, (w, h) in sizes.items():
                pg = b.new_page(viewport={'width': w, 'height': h})
                pg.goto(url + ('&' if '?' in url else '?') + 'lang=' + lang, wait_until='domcontentloaded', timeout=60000)
                pg.wait_for_timeout(a.wait)
                r = pg.evaluate(OVERFLOW_JS)
                if r['html'].lower() != lang.lower() and lang not in wrong_lang: wrong_lang.append(lang)
                try: pg.screenshot(path=os.path.join(out, f'{lang}_{name}.jpg'), type='jpeg', quality=70, timeout=60000)
                except Exception as e: shots_failed += 1; print(f'{lang} {name}: кадр не снят ({type(e).__name__})')
                total += len(r['bad'])
                print(f"{lang} {name}: {len(r['bad'])} проблем" + ''.join(f"\n  {x['why']}: {x['text']!r} .{x['cls']}" for x in r['bad'][:6]))
                pg.close()
        b.close()
    if srv: srv.shutdown()
    if wrong_lang: print('ЯЗЫК НЕ ПЕРЕКЛЮЧИЛСЯ (html lang):', wrong_lang)
    if shots_failed: print('кадров не снято:', shots_failed)
    print(f'итого проблем: {total} · кадры: {out} · проверен только открытый экран')
    sys.exit(1 if total or wrong_lang or shots_failed else 0)


def probe(path):
    if path.lower().endswith(('.mp4', '.webm', '.mov')):
        j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))
        v = next(s for s in j['streams'] if s['codec_type'] == 'video')
        return {'w': v['width'], 'h': v['height'], 'dur': float(j['format']['duration']), 'audio': any(s['codec_type'] == 'audio' for s in j['streams']), 'video': True}
    from PIL import Image
    with Image.open(path) as im: return {'w': im.width, 'h': im.height, 'video': False}


def cmd_media_check(a):
    bad = 0
    for path in a.files:
        i = probe(path); mb = os.path.getsize(path) / 1e6; fits = []; near = []
        for plat, specs in MEDIA.items():
            for key, (w, h) in specs.items():
                if key.startswith('video') != i['video']: continue
                if (i['w'], i['h']) == (w, h): fits.append(f'{plat}:{key}')
                elif abs(i['w'] / i['h'] - w / h) < .01 and i['w'] > w: near.append(f'{plat}:{key} (уменьшить)')
                elif abs(i['w'] / i['h'] - w / h) < .01: near.append(f'{plat}:{key} (МАЛО, нужно {w}×{h})')
        extra = f" · {i['dur']:.1f} с · звук {'да' if i['audio'] else 'нет'}" if i['video'] else ''
        if i['video'] and mb > VIDEO_MAX_MB['crazygames'] and any(x.startswith('crazygames') for x in fits): fits = [x for x in fits if not x.startswith('crazygames')]; extra += ' · >50 МБ для CG'
        ok = bool(fits or any('уменьшить' in x for x in near)); bad += not ok
        print(f"{'OK' if ok else '✗ '} {os.path.basename(path)} {i['w']}×{i['h']} {mb:.1f} МБ{extra} → {', '.join(fits + near) or 'нет подходящего поля'}")
    sys.exit(1 if bad else 0)


def cmd_prep_upload(a):
    z = a.zip or latest_zip(a.project, a.platform)
    if not z: sys.exit('нет zip: сначала сборка')
    out = a.out or os.path.join(a.state_dir or os.path.join(a.project, 'publish'), 'upload', a.platform)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out)
    man = {'source': os.path.basename(z), 'sha256': hashlib.sha256(open(z, 'rb').read()).hexdigest(), 'size': os.path.getsize(z)}
    if a.platform == 'playgama':
        parts = []
        with open(z, 'rb') as f:
            for n, chunk in enumerate(iter(lambda: f.read(CHUNK), b'')):
                name = f'part{n:03d}.bin'; open(os.path.join(out, name), 'wb').write(chunk); parts.append(name)
        man['parts'] = parts
    else:
        files = []; batch = 0; used = 0
        with zipfile.ZipFile(z) as zf:
            for inf in zf.infolist():
                if inf.is_dir(): continue
                if inf.file_size > CHUNK: sys.exit(f'файл больше 9 МБ, нужен другой способ: {inf.filename}')
                if used + inf.file_size > CHUNK: batch += 1; used = 0
                used += inf.file_size
                flat = inf.filename.replace('/', '~~'); d = os.path.join(out, f'batch{batch:03d}'); os.makedirs(d, exist_ok=True)
                open(os.path.join(d, flat), 'wb').write(zf.read(inf))
                files.append({'path': inf.filename, 'flat': flat, 'batch': batch, 'size': inf.file_size})
        man['files'] = files; man['batches'] = batch + 1
    json.dump(man, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
    print(f"{a.platform}: {os.path.basename(z)} · " + (f"{len(man['parts'])} частей" if a.platform == 'playgama' else f"{len(man['files'])} файлов, {man['batches']} пачек") + f' · {out}')


def summarize(text, full=''):
    title = text.split('\n', 1)[0].strip()
    line = next((l for l in (full or text).splitlines() if l.startswith('- **' + title + ':')), '')
    v = re.search(r'нельзя отправлять|можно отправлять[^\n|*]*', line)
    c = re.search(r'✓\s*(\d+)\s*·\s*✗\s*(\d+)\s*·\s*👀\s*(\d+)', text)
    fails = [l for l in text.splitlines() if l.startswith('|') and '| ✗' in l]
    return (v.group(0).strip() if v else 'нет вердикта'), c.groups() if c else ('?', '?', '?'), fails


def report_section(text, plat):
    title = {'crazygames': 'crazy', 'playgama': 'playgama'}[plat]
    parts = re.split(r'(?m)^## ', text)
    for p in parts[1:]:
        if title in p.split('\n', 1)[0].lower(): return p
    return None


def cmd_moderate(a):
    root = a.project; dest = os.path.join(a.state_dir or os.path.join(root, 'publish'), 'moderation'); os.makedirs(dest, exist_ok=True)
    plats = ['crazygames', 'playgama'] if a.platform == 'all' else [a.platform]; code = 0
    report = os.path.join(root, 'docs', 'moderation', 'REPORT.md')
    for pl in plats:
        if not a.parse_only:
            cmd = [sys.executable, os.path.join(root, 'tools/moderator/run.py'), '--platform', pl] + (['--no-build'] if a.no_build else [])
            log = os.path.join(dest, pl + '.log')
            with open(log, 'w') as f: rc = subprocess.run(cmd, cwd=root, stdout=f, stderr=subprocess.STDOUT).returncode
            if rc not in (0, 1): print(f'{pl}: модератор упал, лог {log}'); code = 2; continue
        if not os.path.exists(report): print(f'{pl}: нет REPORT.md'); code = 2; continue
        full = open(report, encoding='utf-8').read()
        text = report_section(full, pl)
        if text is None: print(f'{pl} build: в REPORT.md нет этой площадки, вердикта нет'); code = 2; continue
        open(os.path.join(dest, pl + '.md'), 'w', encoding='utf-8').write('## ' + text)
        v, (ok, fail, man), fails = summarize(text, full)
        print(f'{pl} build: {v} · ✓{ok} ✗{fail} 👀{man}')
        for l in fails[:12]: print('- ✗', ' '.join(c.strip() for c in l.strip('|').split('|')[1:])[:220])
        if v == 'нет вердикта': code = 2
        elif fail != '0' or 'нельзя' in v: code = max(code, 1)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    def add(name, fn):
        p = sub.add_parser(name); p.add_argument('--project', default=os.getcwd()); p.add_argument('--state-dir'); p.set_defaults(fn=fn); return p
    p = add('init', cmd_init); p.add_argument('--icon'); p.add_argument('--cover'); p.add_argument('--force', action='store_true')
    add('status', cmd_status)
    p = add('stage', cmd_stage); p.add_argument('id'); p.add_argument('value', choices=['todo', 'active', 'done', 'blocked']); p.add_argument('--note')
    add('audit', cmd_audit); add('i18n-scan', cmd_i18n_scan); add('i18n-fonts', cmd_i18n_fonts)
    p = add('i18n-fit', cmd_i18n_fit); p.add_argument('--url'); p.add_argument('--out'); p.add_argument('--langs'); p.add_argument('--wait', type=int, default=6000)
    p = add('media-check', cmd_media_check); p.add_argument('files', nargs='+')
    p = add('prep-upload', cmd_prep_upload); p.add_argument('--platform', required=True, choices=['crazygames', 'playgama']); p.add_argument('--zip'); p.add_argument('--out')
    p = add('moderate', cmd_moderate); p.add_argument('--platform', default='all', choices=['all', 'crazygames', 'playgama']); p.add_argument('--no-build', action='store_true'); p.add_argument('--parse-only', action='store_true')
    a = ap.parse_args(); a.project = os.path.abspath(a.project); a.fn(a)


if __name__ == '__main__':
    main()
