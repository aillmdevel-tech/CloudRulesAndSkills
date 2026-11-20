"""Screenshots of the juiciest moments and platform covers, in exact sizes.

  shots.py --project DIR --platform crazygames [--lang en,ru] [--count 6] [--covers] [--screens]
           [--sizes 1920x1080,1080x1920] [--source path.png] [--captions]

Screens: for each top moment the sharpest frame around the peak (or api.shot() stills from the take),
cover-cropped to every size, light colour pop. No text unless --captions (localized banner).
Covers: per platform preset sizes; source = --source / config.cover_source (e.g. Blender key art)
or the best moment frame; vignette + grade; title text by the preset rule
(none / title_only / title_localized). Output: promo/out/<platform>/screens|covers/.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import (die, font_file, hex_to_rgb, langs_arg, load_config, load_moments, need_ffmpeg, platform,
                    promo_dir, run, text_for)


def frame_at(video, t, path):
    run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{max(0, t):.3f}', '-i', video, '-frames:v', '1', path])
    return path


def sharpness(img):
    from PIL import ImageFilter, ImageStat
    g = img.convert('L').resize((480, int(480 * img.height / img.width)))
    return ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).var[0]


def best_frame(project, m, tmp):
    vid = os.path.join(promo_dir(project), 'raw', f'{m["take"]}.mp4')
    from PIL import Image
    best = None
    for k, dt in enumerate((-0.25, -0.12, 0.0, 0.1, 0.22)):
        p = frame_at(vid, m['peak'] + dt, os.path.join(tmp, f'c{k}.png'))
        im = Image.open(p).convert('RGB'); s = sharpness(im)
        if best is None or s > best[0]: best = (s, im)
    return best[1]


def cover_crop(im, w, h, fx=0.5, fy=0.5):
    from PIL import Image
    sc = max(w / im.width, h / im.height)
    r = im.resize((max(w, round(im.width * sc)), max(h, round(im.height * sc))), Image.LANCZOS)
    x = int((r.width - w) * fx); y = int((r.height - h) * fy)
    return r.crop((x, y, x + w, y + h))


def grade(im, strength=1.0):
    from PIL import ImageEnhance
    im = ImageEnhance.Color(im).enhance(1 + 0.18 * strength)
    im = ImageEnhance.Contrast(im).enhance(1 + 0.06 * strength)
    return ImageEnhance.Sharpness(im).enhance(1 + 0.3 * strength)


def vignette(im, amount=0.35):
    from PIL import Image, ImageDraw, ImageFilter
    w, h = im.size
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.ellipse((-w * 0.15, -h * 0.2, w * 1.15, h * 1.2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12))
    dark = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(im, Image.blend(im, dark, amount), m)


def draw_title(im, text, cfg, ypos=0.8, rel=0.15, colour=None):
    from PIL import ImageDraw, ImageFont
    w, h = im.size; fp = font_file(cfg)
    size = int(min(w, h) * rel) if w < h * 1.4 else int(h * rel)
    words = text.split(); lines = [text]
    while size > 10:
        f = ImageFont.truetype(fp, size)
        if f.getlength(text) <= w * 0.86: lines = [text]; break
        if len(words) > 1:
            cands = [(' '.join(words[:k]), ' '.join(words[k:])) for k in range(1, len(words))]
            a, b = min(cands, key=lambda c: max(f.getlength(c[0]), f.getlength(c[1])))
            if max(f.getlength(a), f.getlength(b)) <= w * 0.86: lines = [a, b]; break
        size = int(size * 0.92)
    f = ImageFont.truetype(fp, size)
    d = ImageDraw.Draw(im)
    col = hex_to_rgb(colour or cfg['colors']['text']); out = hex_to_rgb(cfg['colors']['outline'])
    lh = int(size * 1.08); y0 = int(h * ypos - lh * len(lines) / 2)
    for i, ln in enumerate(lines):
        tw = f.getlength(ln); x = int((w - tw) / 2); y = y0 + i * lh
        sw = max(2, int(size * 0.09))
        d.text((x + int(size * 0.05), y + int(size * 0.07)), ln, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
        d.text((x, y), ln, font=f, fill=col, stroke_width=sw, stroke_fill=out)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--platform', required=True)
    ap.add_argument('--lang')
    ap.add_argument('--count', type=int, default=6)
    ap.add_argument('--covers', action='store_true')
    ap.add_argument('--screens', action='store_true')
    ap.add_argument('--sizes', help='screen sizes, e.g. 1920x1080,1080x1920 (default: preset screens or 1920x1080)')
    ap.add_argument('--source', help='image for covers (Blender key art); default config.cover_source or best moment')
    ap.add_argument('--captions', action='store_true', help='localized caption banner on screens (store screenshots)')
    ap.add_argument('--moments', help='ids to use, in order')
    a = ap.parse_args()
    if not a.covers and not a.screens: a.covers = a.screens = True
    need_ffmpeg()
    from PIL import Image
    project = os.path.abspath(a.project); cfg = load_config(project); plat = platform(a.platform)
    ms = load_moments(project)
    if a.moments:
        by = {m['id']: m for m in ms}; ms = [by[int(i)] for i in a.moments.split(',') if int(i) in by]
    base = os.path.join(promo_dir(project), 'out', a.platform)
    tmp = os.path.join(promo_dir(project), '.work_shots'); os.makedirs(tmp, exist_ok=True)
    fx, fy = cfg.get('focus_x', 0.5), cfg.get('focus_y', 0.5)
    report = []
    # stills from scenario api.shot() rank first: they are crisp and composed
    stills = []
    for p in sorted(os.listdir(os.path.join(promo_dir(project), 'raw'))) if os.path.isdir(os.path.join(promo_dir(project), 'raw')) else []:
        if p.endswith('.events.json'):
            j = json.load(open(os.path.join(promo_dir(project), 'raw', p), encoding='utf-8'))
            for s in j.get('shots', []):
                fp = os.path.join(promo_dir(project), s['file']) if not os.path.isabs(s['file']) else s['file']
                if os.path.exists(fp): stills.append((s['name'], Image.open(fp).convert('RGB')))
    frames = [(f'm{m["id"]:02d}', best_frame(project, m, tmp), m) for m in ms[:a.count]]
    if a.screens:
        sizes = ([tuple(int(x) for x in s.split('x')) for s in a.sizes.split(',')] if a.sizes else
                 [(s['w'], s['h']) for s in plat.get('screens', [])] or [(1920, 1080)])
        langs = langs_arg(cfg, a.lang) if a.captions else ['all']
        pool = [(n, im, None) for n, im in stills] + frames
        for lang in langs:
            od = os.path.join(base, 'screens', lang); os.makedirs(od, exist_ok=True)
            for n, im, m in pool[:max(a.count, len(stills))]:
                for (w, h) in sizes:
                    out = grade(cover_crop(im, w, h, fx, fy), 0.6)
                    if a.captions and m:
                        from common import caption_for
                        cap = caption_for(cfg, m, lang) or text_for(cfg, 'hook', lang)
                        if cap: out = draw_title(out, cap, cfg, ypos=0.12, rel=0.09, colour=cfg['colors']['accent'])
                    p = os.path.join(od, f'{n}_{w}x{h}.png'); out.save(p, optimize=True)
                    if min(im.width / w, im.height / h) < 0.75: report.append(f'upscaled {n} to {w}x{h}: capture bigger (--size/--dpr)')
            report.append(f'screens: {len(pool[:max(a.count, len(stills))])} x {len(sizes)} sizes -> {os.path.relpath(od, project)}')
    if a.covers:
        src = a.source or cfg.get('cover_source')
        if src:
            src = src if os.path.isabs(src) else os.path.join(project, src)
            if not os.path.exists(src): die(f'cover source {src} not found')
            key = Image.open(src).convert('RGB')
        elif stills:
            key = stills[0][1]
        elif frames:
            key = frames[0][1]
        else:
            die('no source for covers')
        rule = plat.get('cover_text', 'title_only')
        langs = langs_arg(cfg, a.lang) if rule == 'title_localized' else [langs_arg(cfg, a.lang)[0]]
        od = os.path.join(base, 'covers'); os.makedirs(od, exist_ok=True)
        for lang in langs:
            for c in plat.get('covers', []):
                w, h = c['w'], c['h']
                im = vignette(grade(cover_crop(key, w, h, fx, fy)), 0.3)
                if rule != 'none' and not (c['name'] == 'icon' and w <= 512):
                    im = draw_title(im, text_for(cfg, 'title', lang), cfg, ypos=0.80 if h >= w else 0.78, rel=0.16)
                suffix = f'_{lang}' if rule == 'title_localized' else ''
                p = os.path.join(od, f'{c["name"]}{suffix}.png'); im.save(p, optimize=True)
                if key.width < w * 0.75 or key.height < h * 0.75:
                    report.append(f'cover {c["name"]} upscaled from {key.width}x{key.height}: use a bigger source')
        report.append(f'covers ({rule}): {len(plat.get("covers", []))} sizes x {len(langs)} lang -> {os.path.relpath(od, project)}')
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    print('OK ' + '\n   '.join(report))


if __name__ == '__main__':
    main()
