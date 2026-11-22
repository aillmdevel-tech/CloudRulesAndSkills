"""Reference library for promo work: index what is in it now, pick the 3-5 best refs for this game, make timecoded sheets.

  refs.py --project DIR [--library PATH] [--platform crazygames|google_play|admob|ads_landscape|all] [--top 5]
          [--draft my_video.mp4] [--draft-notes notes.md] [--refresh]

Library (default ~/Downloads/WebAIGames/PromoLibrary, or $PROMO_LIBRARY, or "ref_library" in promo/config.json) is
re-scanned on every call, so new batches dropped into it are picked up. It understands:
  - videos (*.mp4/*.webm/*.mov): "Превью"/"preview" in the name or path -> hover preview, otherwise an ad
  - covers: images under a folder or name with "Обложк"/"cover"
  - breakdown frames: images under "Кадры"/"frames" named "NN — 07.45 — what happens.jpg" (time in seconds)
  - breakdown text: <video stem>.md / .txt next to the video, or "разбивк*"/"breakdown*" files in the game folder
  - catalogue notes: table rows of any *.md that mention the game folder name -> description of the game
Matching: game profile ("profile" in promo/config.json: mechanics, style, keywords; else docs/PROJECT_STATE.md,
docs/ART_SPEC.md, README.md) vs ref text (path + description + breakdown), plus platform and aspect fit.
Output: promo/refs/REFS.md (picked refs with files, lengths, cut timecodes, breakdown, sheet paths) + sheets:
  promo/refs/<kind>_<n>_<game>.jpg  (frame every second with timecode, CUT marks)
  promo/refs/covers_tile.jpg        (covers at real catalogue tile size next to full size: what reads first)
  promo/refs/draft.jpg              (the user's draft cut, if given)
Then write promo/BRIEF.md from templates/promo-brief.md, opening the sheets and the videos' frames yourself.
"""
import argparse, hashlib, json, math, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import need_ffmpeg, promo_dir

VID = ('.mp4', '.webm', '.mov', '.m4v')
IMG = ('.png', '.jpg', '.jpeg', '.webp')
AD_PLATFORMS = {'google_play', 'admob', 'ads_landscape', 'ads_vertical', 'ads_square', 'yandex_direct'}
PREVIEW_PLATFORMS = {'crazygames', 'poki', 'playgama', 'yandex'}
# synonym groups (ru/en): a group counts when the game profile and the ref both hit it
GROUPS = {
    'steal': ['steal', 'rob', 'heist', 'кра', 'укра', 'вор', 'грабе'],
    'escape': ['escape', 'run', 'chase', 'flee', 'побег', 'погон', 'убега', 'беж'],
    'egg': ['egg', 'яйц', 'яйц', 'инкубат', 'hatch'],
    'pet': ['animal', 'pet', 'dragon', 'monster', 'животн', 'питом', 'дракон', 'монстр', 'страж', 'guard'],
    'obby': ['obby', 'parkour', 'обби', 'паркур', 'платформ'],
    'climb': ['climb', 'tower', 'лаз', 'карабк', 'восхожд', 'башн', 'гора'],
    'grow': ['grow', 'evolution', 'evolve', 'upgrade', 'gym', 'train', 'прокач', 'эволю', 'рост', 'трениров', '+1', 'speed', 'скорост'],
    'merge': ['merge', 'слия', 'объедин'],
    'throw': ['throw', 'kick', 'launch', 'брос', 'кида', 'запуск'],
    'lucky': ['lucky', 'mystery', 'random', 'case', 'лаки', 'случайн', 'сундук'],
    'brainrot': ['brainrot', 'брейнрот'],
    'tsunami': ['tsunami', 'wave', 'flood', 'цунами', 'волн'],
    'physics': ['ragdoll', 'physics', 'rope', 'физик', 'рэгдолл', 'верёвк', 'щупал', 'tentacle', 'arm'],
    'race': ['kart', 'race', 'racing', 'гонк', 'карт'],
    'shooter': ['archer', 'arrow', 'shoot', 'лук', 'стрел'],
    'slice': ['slice', 'cut', 'knife', 'нож', 'реза'],
    'farm': ['farm', 'garden', 'ферм', 'сад', 'огород'],
    'arcade': ['wave', 'neon', 'dash', 'arcade', 'аркад', 'неон'],
    'underwater': ['underwater', 'ocean', 'sea', 'octopus', 'подвод', 'океан', 'море', 'осьмин'],
    'roblox': ['roblox', 'blocky', 'block', 'роблокс', 'блочн', 'кубич', 'voxel'],
    'toon': ['toon', 'cartoon', 'мульт', 'тун', 'стилиз'],
}
STYLE_GROUPS = {'roblox', 'toon', 'arcade', 'underwater'}


def lib_root(project, arg):
    if arg: return os.path.abspath(os.path.expanduser(arg))
    if os.environ.get('PROMO_LIBRARY'): return os.path.expanduser(os.environ['PROMO_LIBRARY'])
    cfgp = os.path.join(promo_dir(project), 'config.json')
    if os.path.exists(cfgp):
        r = json.load(open(cfgp, encoding='utf-8')).get('ref_library')
        if r: return os.path.expanduser(r)
    return os.path.expanduser('~/Downloads/WebAIGames/PromoLibrary')


def strip_md(t):
    t = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', t)
    return re.sub(r'<br>|\*\*|`', ' ', t)


def game_dir(path, lib):
    d = os.path.dirname(path)
    while os.path.basename(d).lower() in ('видео', 'video', 'videos', 'скриншоты', 'screenshots', 'обложки crazygames',
                                          'кадры из превью', 'обложки', 'covers', 'frames', 'кадры') and d != lib:
        d = os.path.dirname(d)
    return d


def scan(lib):
    games, notes = {}, []
    for root, dirs, files in os.walk(lib):
        dirs[:] = [d for d in dirs if not d.startswith(('_', '.'))]
        for f in files:
            p = os.path.join(root, f); low = f.lower(); ext = os.path.splitext(low)[1]
            if ext == '.md':
                notes.append(p)
            if ext not in VID + IMG + ('.md', '.txt'): continue
            g = game_dir(p, lib); G = games.setdefault(g, dict(dir=g, name=os.path.basename(g), videos=[], covers=[],
                                                              frames=[], breakdown=[], desc=''))
            rel = os.path.relpath(p, lib).lower()
            if ext in VID:
                kind = 'preview' if re.search(r'превью|preview|hover', rel) else 'ad'
                G['videos'].append(dict(path=p, kind=kind))
            elif ext in IMG and re.search(r'обложк|cover|thumb|icon', rel):
                G['covers'].append(p)
            elif ext in IMG and re.search(r'кадр|frame', rel):
                m = re.match(r'\s*\d+\s*[—-]\s*([\d.,]+)\s*(?:с|s)?\s*(?:[—-]\s*(.*))?$', os.path.splitext(f)[0])
                if m:
                    t = float(m.group(1).replace(',', '.'))
                    G['frames'].append(dict(path=p, t=t, what=(m.group(2) or '').strip()))
            elif ext in ('.md', '.txt') and (re.search(r'разбивк|breakdown|раскадров', low) or
                                             any(os.path.splitext(v)[0] == os.path.splitext(p)[0] for v in
                                                 [os.path.join(root, x) for x in files if x.lower().endswith(VID)])):
                G['breakdown'].append(p)
    games = {k: v for k, v in games.items() if v['videos'] or v['covers']}
    # descriptions from catalogue tables: a row that links into the game folder or names it
    for n in notes:
        try: text = open(n, encoding='utf-8').read()
        except Exception: continue
        rows = [l for l in text.splitlines() if l.startswith('|') and '---' not in l]
        base = os.path.dirname(n)
        for G in games.values():
            keys = {G['name'].lower(), os.path.relpath(G['dir'], base).lower()}
            for r in rows:
                rl = r.lower(); rl_dec = urldecode(rl)
                if any(k and len(k) > 3 and (k in rl or k in rl_dec) for k in keys):
                    d = re.sub(r'\s+', ' ', strip_md(r).replace('|', ' · ')).strip(' ·')
                    if d not in G['desc']: G['desc'] = (G['desc'] + ' ' + d).strip()
    return games


def urldecode(s):
    from urllib.parse import unquote
    return unquote(s)


def probe_video(p, cache):
    st = os.stat(p); key = hashlib.sha1(f'{p}|{st.st_size}|{st.st_mtime}'.encode()).hexdigest()[:16]
    if key in cache: return cache[key]
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', p],
                                  capture_output=True, text=True).stdout or '{}')
    v = next((s for s in j.get('streams', []) if s.get('codec_type') == 'video'), {})
    a = any(s.get('codec_type') == 'audio' for s in j.get('streams', []))
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-an', '-vf',
                        "scale=320:-2,select='gt(scene,0.32)',showinfo", '-f', 'null', '-'], capture_output=True, text=True)
    cuts = [round(float(x), 2) for x in re.findall(r'pts_time:([\d.]+)', r.stderr)]
    info = dict(dur=round(float(j.get('format', {}).get('duration', 0) or 0), 2), w=v.get('width', 0), h=v.get('height', 0),
                audio=a, cuts=cuts, key=key)
    cache[key] = info
    return info


def profile_text(project):
    cfgp = os.path.join(promo_dir(project), 'config.json'); parts = []
    if os.path.exists(cfgp):
        c = json.load(open(cfgp, encoding='utf-8')); pr = c.get('profile') or {}
        for k in ('mechanics', 'style', 'keywords'):
            v = pr.get(k); parts += (v if isinstance(v, list) else [v] if v else [])
        t = c.get('title'); parts += list(t.values()) if isinstance(t, dict) else [t or '']
    explicit = bool(parts)
    for f in ('docs/PROJECT_STATE.md', 'docs/ART_SPEC.md', 'README.md', 'docs/spec/README.md'):
        p = os.path.join(project, f)
        if os.path.exists(p): parts.append(open(p, encoding='utf-8', errors='ignore').read()[:6000])
    return ' '.join(str(x) for x in parts).lower(), explicit


def hits(text):
    return {g for g, words in GROUPS.items() if any(w in text for w in words)}


def score_game(G, prof, kind_want, aspect_want):
    text = (G['name'] + ' ' + G['desc'] + ' ' + ' '.join(open(b, encoding='utf-8', errors='ignore').read()[:3000]
                                                            for b in G['breakdown']) + ' ' +
            ' '.join(os.path.basename(f['path']) + ' ' + f['what'] for f in G['frames'])).lower()
    common = prof & hits(text)
    sc = sum(1.5 if g in STYLE_GROUPS else 3.0 for g in common)
    if G['breakdown'] or G['frames']: sc += 1.0  # timecoded breakdown available
    return sc, sorted(common)


def sheet(video, info, out, step=1.0, label=''):
    """Frame every `step` s with its timecode; red CUT mark when a cut fell since the previous tile."""
    from PIL import Image, ImageDraw, ImageFont
    tmp = out + '.d'; os.makedirs(tmp, exist_ok=True)
    n = max(1, min(30, int(info['dur'] / step) + 1)); tw = 320 if info['w'] >= info['h'] else 180
    ts = [round(min(info['dur'] - 0.05, 0.1 if i == 0 else i * step), 2) for i in range(n)]
    tiles = []
    for i, t in enumerate(ts):
        fp = os.path.join(tmp, f'{i:03d}.jpg')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t}', '-i', video, '-frames:v', '1', '-vf', f'scale={tw}:-2', fp])
        if os.path.exists(fp): tiles.append((t, Image.open(fp).convert('RGB')))
    if not tiles: return None
    th = tiles[0][1].height; cols = 6 if tw == 320 else 8; rows = math.ceil(len(tiles) / cols)
    try: font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
    except Exception: font = ImageFont.load_default()
    head = 30 if label else 0
    im = Image.new('RGB', (cols * tw, rows * th + head), (18, 18, 24)); d = ImageDraw.Draw(im)
    if label: d.text((8, 5), label[:150], fill=(255, 255, 255), font=font)
    prev = -1.0
    for k, (t, fr) in enumerate(tiles):
        x, y = (k % cols) * tw, (k // cols) * th + head; im.paste(fr, (x, y))
        cut = any(prev < c <= t for c in info['cuts'])
        d.rectangle((x, y, x + 74, y + 24), fill=(0, 0, 0)); d.text((x + 5, y + 3), f'{t:05.2f}s', fill=(255, 230, 90), font=font)
        if cut:
            d.rectangle((x + tw - 52, y, x + tw, y + 24), fill=(220, 30, 40)); d.text((x + tw - 47, y + 3), 'CUT', fill=(255, 255, 255), font=font)
        prev = t
    im.save(out, quality=86)
    for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return out


def covers_tile(picks, out):
    """Each cover at catalogue-tile size (what a player sees in the grid) next to a larger copy."""
    from PIL import Image, ImageDraw, ImageFont
    try: font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 16)
    except Exception: font = ImageFont.load_default()
    rows = []
    for G in picks:
        cs = sorted(G['covers'])[:3]
        if not cs: continue
        row = Image.new('RGB', (1500, 300), (18, 18, 24)); d = ImageDraw.Draw(row); x = 10
        d.text((10, 6), G['name'][:60], fill=(255, 255, 255), font=font)
        for c in cs:
            im = Image.open(c).convert('RGB'); ar = im.width / im.height
            small = im.resize((int(150 * ar) if ar < 1.2 else 200, 150 if ar < 1.2 else int(200 / ar)))  # grid tile
            big = im.resize((int(250 * ar), 250)) if ar < 1.2 else im.resize((400, int(400 / ar)))
            row.paste(small, (x, 30)); row.paste(big, (x + small.width + 8, 30)); x += small.width + big.width + 28
            if x > 1400: break
        rows.append(row)
    if not rows: return None
    im = Image.new('RGB', (1500, 300 * len(rows)), (18, 18, 24))
    for i, r in enumerate(rows): im.paste(r, (0, i * 300))
    im.save(out, quality=88); return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--library')
    ap.add_argument('--platform', default='all', help='crazygames | google_play | admob | ads_landscape | all')
    ap.add_argument('--top', type=int, default=5)
    ap.add_argument('--draft', help="the user's own draft video: probed and sheeted like a ref")
    ap.add_argument('--draft-notes', help="the user's own rough breakdown of the draft")
    ap.add_argument('--refresh', action='store_true', help='re-probe every video (ignore the index cache)')
    a = ap.parse_args(); need_ffmpeg()
    project = os.path.abspath(a.project); lib = lib_root(project, a.library)
    if not os.path.isdir(lib): sys.exit(f'library not found: {lib} (pass --library or set ref_library in promo/config.json)')
    idx_dir = os.path.join(lib, '_index'); os.makedirs(idx_dir, exist_ok=True)
    cache_p = os.path.join(idx_dir, 'probe_cache.json')
    cache = {} if a.refresh or not os.path.exists(cache_p) else json.load(open(cache_p, encoding='utf-8'))
    games = scan(lib)
    for G in games.values():
        for v in G['videos']: v.update(probe_video(v['path'], cache))
    json.dump(cache, open(cache_p, 'w', encoding='utf-8'))
    json.dump({k: v for k, v in games.items()}, open(os.path.join(idx_dir, 'index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=str)
    ptxt, explicit = profile_text(project); prof = hits(ptxt)
    out = os.path.join(promo_dir(project), 'refs'); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.jpg'): os.remove(os.path.join(out, f))
    pl = a.platform
    sections = []
    if pl in ('all',) or pl in PREVIEW_PLATFORMS: sections.append(('preview', 'Hover-превью в каталоге (CrazyGames и др.)'))
    if pl in ('all',) or pl in AD_PLATFORMS: sections.append(('ad', 'Реклама установки (Google Play / AdMob / сети)'))
    md = [f'# Референсы для {os.path.basename(project)}', '',
          f'Библиотека: `{lib}` · игр/папок: {len(games)} · видео: {sum(len(g["videos"]) for g in games.values())} · '
          f'обложек: {sum(len(g["covers"]) for g in games.values())} · кадров-разбивок: {sum(len(g["frames"]) for g in games.values())}',
          f'Профиль игры ({"promo/config.json profile" if explicit else "из docs/README, задай profile в config для точности"}): '
          f'{", ".join(sorted(prof)) or "не найден"}', '']
    picked_games = []
    for kind, title in sections:
        cands = []
        for G in games.values():
            vs = [v for v in G['videos'] if v['kind'] == kind]
            if not vs: continue
            sc, why = score_game(G, prof, kind, None)
            v = max(vs, key=lambda v: (v['w'] >= v['h'], v['dur'] > 0))  # landscape first, it is Alex's main format
            cands.append((sc, why, G, v))
        cands.sort(key=lambda x: -x[0])
        md += [f'## {title}', '']
        for n, (sc, why, G, v) in enumerate(cands[:a.top], 1):
            sp = sheet(v['path'], v, os.path.join(out, f'{kind}_{n}_{re.sub(r"[^A-Za-z0-9]+", "-", G["name"])[:30]}.jpg'),
                       1.0 if v['dur'] <= 30 else 2.0, f'{G["name"]} · {os.path.basename(v["path"])} · {v["dur"]}s')
            picked_games.append(G)
            md += [f'### {n}. {G["name"]} — совпадения: {", ".join(why) or "нет (взято по площадке)"} (score {sc:.1f})',
                   f'- Файл: `{v["path"]}`',
                   f'- {v["w"]}×{v["h"]}, {v["dur"]} с, звук: {"да" if v["audio"] else "нет"}, склейки ({len(v["cuts"])}): '
                   f'{", ".join(f"{c:.1f}" for c in v["cuts"][:20]) or "один план"}',
                   f'- Лист кадров (каждую {1 if v["dur"] <= 30 else 2} с, CUT = склейка): `{sp}`']
            if G['desc']: md.append(f'- Из каталога: {G["desc"][:500]}')
            fr = sorted(G['frames'], key=lambda f: f['t'])
            if fr: md.append('- Разбивка кадрами: ' + '; '.join(f'{f["t"]:.2f} с — {f["what"] or os.path.basename(f["path"])}' for f in fr[:12]))
            for b in G['breakdown']: md.append(f'- Разбивка текстом: `{b}`')
            md.append('')
    cov_games = []
    seen = set()
    for G in picked_games:
        if id(G) not in seen and G['covers']: seen.add(id(G)); cov_games.append(G)
    if len(cov_games) < 3:
        for G in sorted(games.values(), key=lambda g: -score_game(g, prof, None, None)[0]):
            if id(G) not in seen and G['covers']: seen.add(id(G)); cov_games.append(G)
            if len(cov_games) >= 5: break
    ct = covers_tile(cov_games[:5], os.path.join(out, 'covers_tile.jpg'))
    md += ['## Обложки', f'- Лист «плитка каталога + крупно»: `{ct}`'] + [f'- {G["name"]}: ' + ', '.join(f'`{c}`' for c in sorted(G['covers'])) for G in cov_games[:5]] + ['']
    if a.draft:
        dp = os.path.abspath(a.draft); di = probe_video(dp, {})
        ds = sheet(dp, di, os.path.join(out, 'draft.jpg'), 1.0 if di['dur'] <= 30 else 2.0, f'DRAFT · {os.path.basename(dp)} · {di["dur"]}s')
        md += ['## Черновик Alex', f'- Файл: `{dp}` · {di["w"]}×{di["h"]}, {di["dur"]} с, склейки: '
               f'{", ".join(f"{c:.1f}" for c in di["cuts"]) or "один план"}', f'- Лист: `{ds}`']
        if a.draft_notes: md.append(f'- Разбивка Alex: `{os.path.abspath(a.draft_notes)}`')
        md.append('')
    md += ['Дальше: открой листы и сами видео в нужных таймкодах, сверь с разбивкой и заполни promo/BRIEF.md '
           'по templates/promo-brief.md.']
    open(os.path.join(out, 'REFS.md'), 'w', encoding='utf-8').write('\n'.join(md))
    print(f'library {lib}: {len(games)} folders; profile: {", ".join(sorted(prof)) or "-"}')
    print(f'-> {os.path.relpath(os.path.join(out, "REFS.md"), project)} + {len([f for f in os.listdir(out) if f.endswith(".jpg")])} sheets')


if __name__ == '__main__':
    main()
