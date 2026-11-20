"""Find the juiciest moments in recorded takes and make a review sheet.

  moments.py --project DIR [--take T1,T2] [--top 12] [--len 2.2] [--skip-start 1.0]

Score per 0.1 s bin = motion (scene change) + loudness + game events (window.__promo.event)
+ manual marks (F9). Dark/frozen bins are penalised. Picks non-overlapping windows with
the peak at ~65% of the clip (action builds up, cut right after the payoff).
Output: promo/moments.json, promo/review/moments.jpg (contact sheet), promo/review/MOMENTS.md.
"""
import argparse, glob, json, math, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import die, font_file, load_config, need_ffmpeg, probe, promo_dir, run

BIN = 0.1


def motion_series(path):
    """Per-frame scene score + luma via one ffmpeg pass on a small proxy."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-an', '-vf',
                        "scale=320:-2,signalstats,select='gte(scene,0)',metadata=print:file=-", '-f', 'null', '-'],
                       capture_output=True, text=True)
    out, t, cur = [], None, {}
    for line in r.stdout.splitlines():
        m = re.search(r'pts_time:([\d.]+)', line)
        if m:
            if t is not None: out.append((t, cur.get('scene', 0.0), cur.get('y', 128.0)))
            t, cur = float(m.group(1)), {}
            continue
        m = re.search(r'lavfi\.scene_score=([\d.]+)', line)
        if m: cur['scene'] = float(m.group(1))
        m = re.search(r'lavfi\.signalstats\.YAVG=([\d.]+)', line)
        if m: cur['y'] = float(m.group(1))
    if t is not None: out.append((t, cur.get('scene', 0.0), cur.get('y', 128.0)))
    return out


def loudness_series(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-af',
                        'ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-', '-f', 'null', '-'],
                       capture_output=True, text=True)
    out, t = [], None
    for line in r.stdout.splitlines():
        m = re.search(r'pts_time:([\d.]+)', line)
        if m: t = float(m.group(1)); continue
        m = re.search(r'lavfi\.r128\.M=(-?[\d.inf]+)', line)
        if m and t is not None:
            try: v = float(m.group(1))
            except ValueError: v = -70.0
            out.append((t, max(v, -70.0)))
    return out


def norm(xs):
    if not xs: return xs
    s = sorted(xs); lo = s[int(len(s) * 0.1)]; hi = s[int(len(s) * 0.98)]
    if hi - lo < 1e-9: return [0.0 for _ in xs]
    return [min(1.0, max(0.0, (x - lo) / (hi - lo))) for x in xs]


def analyse(project, take, args):
    raw = os.path.join(promo_dir(project), 'raw')
    vid = os.path.join(raw, f'{take}.mp4')
    meta = json.load(open(os.path.join(raw, f'{take}.events.json'), encoding='utf-8'))
    pr = probe(vid); dur = pr['dur']; n = int(dur / BIN) + 1
    mot = [0.0] * n; luma = [128.0] * n; cnt = [0] * n
    for t, s, y in motion_series(vid):
        i = min(n - 1, int(t / BIN)); mot[i] += s; luma[i] += y; cnt[i] += 1
    for i in range(n):
        if cnt[i]: mot[i] /= cnt[i]; luma[i] = (luma[i] - 128.0) / cnt[i]
    # smooth motion a bit (0.3 s) so one-frame flicker does not win
    mot = [sum(mot[max(0, i - 1):i + 2]) / len(mot[max(0, i - 1):i + 2]) for i in range(n)]
    loud = [-70.0] * n
    if pr['audio']:
        for t, v in loudness_series(vid):
            i = min(n - 1, int(t / BIN)); loud[i] = max(loud[i], v)
    evb = [0.0] * n; labels = {}
    for e in meta.get('events', []):
        if e.get('type') == 'shot': continue
        w = float(e.get('weight', 1)); c = e['t']
        for i in range(max(0, int((c - 1.2) / BIN)), min(n, int((c + 0.6) / BIN) + 1)):
            d = i * BIN - c
            evb[i] += w * math.exp(-(d * d) / (2 * (0.35 if d < 0 else 0.25) ** 2))
        labels.setdefault(int(c / BIN), []).append(e)
    mn, ln = norm(mot), norm(loud) if pr['audio'] else [0.0] * n
    emax = max(evb) or 1.0
    score = []
    for i in range(n):
        s = 0.5 * mn[i] + 0.25 * ln[i] + 1.0 * (evb[i] / emax if any(evb) else 0)
        if luma[i] < 18: s -= 0.8      # black / loading
        if mot[i] < 0.002: s -= 0.3    # frozen frame
        t = i * BIN
        if t < args.skip_start or t > dur - 0.4: s -= 2
        score.append(s)
    return {'take': take, 'dur': dur, 'score': score, 'labels': labels, 'meta': meta, 'video': vid}


def pick(an, top, length):
    used = []; res = []
    order = sorted(range(len(an['score'])), key=lambda i: -an['score'][i])
    for i in order:
        if len(res) >= top: break
        peak = i * BIN
        if an['score'][i] < 0.15: break
        start = max(0.0, peak - 0.65 * length); end = min(an['dur'] - 0.05, start + length)
        start = max(0.0, end - length)
        if any(not (end <= a or start >= b) for a, b in used): continue
        used.append((start - 0.2, end + 0.2))
        evs = [e for k in range(int(start / BIN), int(end / BIN) + 1) for e in an['labels'].get(k, [])]
        best_ev = max(evs, key=lambda e: e.get('weight', 1)) if evs else None
        res.append({'take': an['take'], 'start': round(start, 2), 'end': round(end, 2), 'peak': round(peak, 2),
                    'score': round(an['score'][i], 3), 'type': best_ev['type'] if best_ev else 'motion',
                    'label': best_ev.get('label', '') if best_ev else '', 'events': len(evs)})
    return res


def contact_sheet(project, moments, cfg):
    from PIL import Image, ImageDraw, ImageFont
    rev = os.path.join(promo_dir(project), 'review'); os.makedirs(rev, exist_ok=True)
    tiles = []
    for m in moments:
        vid = os.path.join(promo_dir(project), 'raw', f'{m["take"]}.mp4')
        row = []
        for t in (m['start'] + 0.15, m['peak'], min(m['end'] - 0.1, m['peak'] + 0.5)):
            p = os.path.join(rev, '.f.jpg')
            run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.2f}', '-i', vid, '-frames:v', '1', '-vf', 'scale=360:-2', p])
            row.append(Image.open(p).convert('RGB'))
        tiles.append((m, row))
    if not tiles: return None
    tw, th = tiles[0][1][0].size
    sheet = Image.new('RGB', (tw * 3 + 20, (th + 34) * len(tiles)), (20, 20, 28))
    d = ImageDraw.Draw(sheet)
    try: f = ImageFont.truetype(font_file(cfg), 20)
    except Exception: f = ImageFont.load_default()
    for r, (m, row) in enumerate(tiles):
        y = r * (th + 34)
        d.text((8, y + 6), f'#{m["id"]}  {m["take"]} {m["start"]:.1f}-{m["end"]:.1f}s  peak {m["peak"]:.1f}  '
                            f'{m["type"]} {m["label"]}  score {m["score"]}', fill=(255, 220, 90), font=f)
        for c, im in enumerate(row): sheet.paste(im, (c * (tw + 10), y + 32))
    out = os.path.join(rev, 'moments.jpg'); sheet.save(out, quality=88)
    try: os.remove(os.path.join(rev, '.f.jpg'))
    except OSError: pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--take', help='comma list; default: all takes in promo/raw')
    ap.add_argument('--top', type=int, default=12)
    ap.add_argument('--len', type=float, default=2.2, help='clip length, s')
    ap.add_argument('--skip-start', type=float, default=1.0)
    ap.add_argument('--no-sheet', action='store_true')
    a = ap.parse_args()
    need_ffmpeg()
    project = os.path.abspath(a.project); cfg = load_config(project)
    raw = os.path.join(promo_dir(project), 'raw')
    takes = a.take.split(',') if a.take else sorted(os.path.basename(p)[:-12] for p in glob.glob(os.path.join(raw, '*.events.json')))
    if not takes: die('no takes in promo/raw: run capture.py first')
    allm = []
    for t in takes:
        an = analyse(project, t, a)
        allm += pick(an, a.top, a.len)
    allm.sort(key=lambda m: -m['score'])
    allm = allm[:a.top]
    for i, m in enumerate(allm, 1): m['id'] = i
    json.dump(allm, open(os.path.join(promo_dir(project), 'moments.json'), 'w'), ensure_ascii=False, indent=1)
    sheet = None if a.no_sheet else contact_sheet(project, allm, cfg)
    md = ['# Моменты для промо', '', 'Убери лишние: `edit.py --moments 1,3,5` или удали строки в moments.json.', '',
          '| # | дубль | отрезок, с | пик | тип | метка | счёт |', '|---|---|---|---|---|---|---|']
    md += [f'| {m["id"]} | {m["take"]} | {m["start"]}–{m["end"]} | {m["peak"]} | {m["type"]} | {m["label"]} | {m["score"]} |' for m in allm]
    rev = os.path.join(promo_dir(project), 'review'); os.makedirs(rev, exist_ok=True)
    open(os.path.join(rev, 'MOMENTS.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(f'OK {len(allm)} moments from {len(takes)} take(s) -> promo/moments.json' + (f', sheet {os.path.relpath(sheet, project)}' if sheet else ''))
    for m in allm[:8]:
        print(f'  #{m["id"]} {m["take"]} {m["start"]}-{m["end"]}s {m["type"]} {m["label"]} score={m["score"]}')


if __name__ == '__main__':
    main()
