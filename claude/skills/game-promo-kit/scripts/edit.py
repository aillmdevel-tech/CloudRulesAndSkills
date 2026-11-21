"""Cut and edit promo videos from the picked moments, per platform preset, language and hook variant.

  edit.py --project DIR --platform ads_vertical [--video promo_vertical] [--lang en,ru]
          [--moments 3,1,5] [--style story|cartoon|clean] [--duration 15] [--music file.mp3] [--bpm 128]
          [--layout auto|cover|stack] [--variants 2] [--no-slowmo] [--no-sfx] [--no-beat] [--draft]

cartoon (ads): opener = strongest payoff within the first second, word-by-word hook, varied transitions
  (zoom, whip-slide, white flash) cut on the beat, speed-ramp -> 0.5x slow-mo (motion-interpolated when the
  game rendered < 50 fps) + push-in + shake + RGB split + boom at every payoff, pop-in captions, end card with
  blurred freeze-frame, rotating rays, logo/title and a pulsing CTA; whoosh/pop SFX; procedural beat bed when
  no music is given. Every payoff lands on a hit-stop (3 held frames exactly on the event: flash, RGB split, boom),
  the push-in jumps a notch on it and shake follows; the last payoff is the climax: music dips 0.35 s before it,
  then 3 anime impact frames (negative + speed lines). Captions and booms escalate clip by clip.
  Slow-mo segments are interpolated once into promo/cache/ in parallel and reused by every language and hook. Portrait output from a landscape take -> "stack": gameplay card on its blurred copy.
story (ads, default; from the H2T / CrazyGames reference base): 3-5 long gameplay shots of 2.4-4.5 s with hard cuts,
  payoff inside the first second, the game's own HUD left in, banner captions in the game's UI style ("RUN!"),
  a small persistent CTA pill, one hit-stop + impact frame only on the climax (the biggest reward last), end card.
clean (platform hover previews): 2-4 long shots of 3-6 s, hard cuts, no text/sound/speed tricks, action from frame 0,
  12-15 s; --cover-first puts the static cover first (CrazyGames recommends it, most top previews skip it).
texts.hook may hold a list per language -> one file per hook (A/B), each opening on a different moment.
Output: promo/out/<platform>/<lang|all>/<video>[_hN].mp4 + promo/review/<platform>_<video>_<lang>[_hN].jpg.
"""
import argparse, hashlib, json, math, os, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from common import (caption_for, die, font_file, hex_to_rgb, hooks_for, langs_arg, load_config,
                    load_moments, need_ffmpeg, platform, probe, promo_dir, run, sound, synth, text_for)

try:
    from PIL.Image import Resampling as _R
    BIC = _R.BICUBIC
except Exception:  # old Pillow
    from PIL.Image import BICUBIC as BIC

TRANSITIONS = ['zoomin', 'slideleft', 'fadewhite', 'slideup', 'smoothright', 'fadewhite']


def fit_text(text, font_path, size, max_w, max_lines=2):
    """Shrink + wrap so localized strings (long German, CJK) stay inside max_w."""
    from PIL import ImageFont
    words = text.split()
    while size > 12:
        f = ImageFont.truetype(font_path, int(size))
        wid = f.getlength
        if wid(text) <= max_w:
            return [text], int(size)
        if len(words) > 1 and max_lines >= 2:
            best = None
            for k in range(1, len(words)):
                a, b = ' '.join(words[:k]), ' '.join(words[k:])
                m = max(wid(a), wid(b))
                if best is None or m < best[0]: best = (m, [a, b])
            if best[0] <= max_w:
                return best[1], int(size)
        elif len(words) == 1 and len(text) > 4 and not text.isascii() and max_lines >= 2:
            half = len(text) // 2  # CJK: split by characters
            a, b = text[:half], text[half:]
            if max(wid(a), wid(b)) <= max_w: return [a, b], int(size)
        size *= 0.92
    return [text], 12


class TextLayer:
    """Pop-in texts/images rendered by Pillow as RGBA frame sequences, overlaid by ffmpeg (no libass needed)."""
    def __init__(self, W, H, font_path, cfg):
        c = cfg['colors']; self.W, self.H, self.fp, self.items = W, H, font_path, []
        self.text, self.acc, self.out = hex_to_rgb(c['text']), hex_to_rgb(c['accent']), hex_to_rgb(c['outline'])
        self.ban = hex_to_rgb(c.get('banner', '#E0262B'))

    def pop(self, t0, t1, lines, size, x, y, colour=None, rot=-3, pulse=False, image=None, button=False, banner=False):
        if t1 - t0 > 0.15:
            self.items.append(dict(t0=t0, t1=t1, lines=lines, size=int(size), x=x, y=y, col=colour or self.text,
                                   rot=rot, pulse=pulse, image=image, button=button, banner=banner))

    def pop_words(self, t0, t1, lines, size, cx, cy, colour=None, stagger=0.09):
        """Kinetic hook: every word pops on its own with alternating tilt; the phrase layout is kept."""
        from PIL import ImageFont
        f = ImageFont.truetype(self.fp, int(size)); sp = f.getlength(' '); lh = size * 1.12
        k = 0
        for li, line in enumerate(lines):
            words = line.split()
            if len(words) == 1 and not line.isascii() and len(line) > 3:  # CJK line: pop it whole
                words = [line]
            ws = [f.getlength(w) for w in words]; tot = sum(ws) + sp * (len(words) - 1)
            x = cx - tot / 2; y = cy + (li - (len(lines) - 1) / 2) * lh
            for w, wl in zip(words, ws):
                self.pop(t0 + k * stagger, t1, [w], size, x + wl / 2, y, colour, rot=(-5 if k % 2 == 0 else 4))
                x += wl + sp; k += 1

    def _sprite(self, it):
        from PIL import Image, ImageDraw, ImageFont
        if it['image']:
            im = Image.open(it['image']).convert('RGBA')
            sc = it['size'] / max(im.width, im.height)
            return im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
        if it.get('banner'):  # game-UI banner ("RUN!"): white caps on a red rounded plate with a dark lip, no tilt
            f = ImageFont.truetype(self.fp, it['size']); sw = max(2, int(it['size'] * 0.06)); lh = int(it['size'] * 1.1)
            ws = [f.getlength(l) for l in it['lines']]; px, py = it['size'] * 0.55, it['size'] * 0.22
            bw_, bh_ = int(max(ws) + 2 * px), int(lh * len(it['lines']) + 2 * py); lip = max(3, int(bh_ * 0.08))
            im = Image.new('RGBA', (bw_ + 6, bh_ + lip + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            r_ = int(bh_ * 0.28)
            d.rounded_rectangle((3, 3 + lip, 3 + bw_, 3 + bh_ + lip), r_, fill=tuple(int(c * 0.55) for c in self.ban) + (255,))
            d.rounded_rectangle((3, 3, 3 + bw_, 3 + bh_), r_, fill=self.ban + (255,), outline=(255, 255, 255, 230), width=max(2, sw))
            for i, l in enumerate(it['lines']):
                d.text((3 + bw_ / 2, 3 + py + i * lh + lh / 2), l, font=f, fill=(255, 255, 255, 255), anchor='mm',
                       stroke_width=sw, stroke_fill=self.out + (255,))
            return im
        if it.get('button'):  # CTA as a fat cartoon button: white rim, accent face over a darker lip, gloss, dark label
            f = ImageFont.truetype(self.fp, it['size']); l, t, rr, b = f.getbbox(it['lines'][0])
            tw, th = rr - l, b - t; px, py, rim = it['size'] * 0.8, it['size'] * 0.45, max(4, int(it['size'] * 0.09))
            bw_, bh_ = int(tw + 2 * px), int(th + 2 * py); lip = int(bh_ * 0.12); sh = int(it['size'] * 0.14)
            W_, H_ = bw_ + 2 * rim, bh_ + lip + 2 * rim
            im = Image.new('RGBA', (W_ + sh, H_ + sh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((sh, sh, sh + W_, sh + H_), H_ // 2, fill=(0, 0, 0, 110))
            d.rounded_rectangle((0, 0, W_, H_), H_ // 2, fill=(255, 255, 255, 255))
            dark = tuple(int(c * 0.70) for c in it['col'])
            d.rounded_rectangle((rim, rim, rim + bw_, rim + bh_ + lip), (bh_ + lip) // 2, fill=dark + (255,))
            d.rounded_rectangle((rim, rim, rim + bw_, rim + bh_), bh_ // 2, fill=it['col'] + (255,))
            gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
            ImageDraw.Draw(gl).rounded_rectangle((rim + bh_ * 0.35, rim + bh_ * 0.10, rim + bw_ - bh_ * 0.35, rim + bh_ * 0.32),
                                                 int(bh_ * 0.11), fill=(255, 255, 255, 80))
            im.alpha_composite(gl); d = ImageDraw.Draw(im)
            d.text((rim + bw_ / 2, rim + bh_ / 2), it['lines'][0], font=f, fill=self.out + (255,), anchor='mm')
            return im
        f = ImageFont.truetype(self.fp, it['size']); sw = max(3, int(it['size'] * 0.11)); sh = max(2, int(it['size'] * 0.07))
        lh = int(it['size'] * 1.1); ws = [f.getlength(l) for l in it['lines']]
        w = int(max(ws) + 2 * sw + sh + 8); h = int(lh * len(it['lines']) + 2 * sw + sh + it['size'] * 0.3)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for i, (l, lw) in enumerate(zip(it['lines'], ws)):
            x = (w - sh - lw) / 2; y = sw + i * lh
            d.text((x + sh, y + sh), l, font=f, fill=(0, 0, 0, 170), stroke_width=sw, stroke_fill=(0, 0, 0, 170))
            d.text((x, y), l, font=f, fill=it['col'] + (255,), stroke_width=sw, stroke_fill=self.out + (255,))
        return im

    @staticmethod
    def _curve(ms, dur_ms, rot, pulse):
        def lerp(a, b, k): return a + (b - a) * max(0.0, min(1.0, k))
        if ms < 130: s = lerp(0.08, 1.24, ms / 130)
        elif ms < 250: s = lerp(1.24, 0.96, (ms - 130) / 120)
        elif ms < 330: s = lerp(0.96, 1.0, (ms - 250) / 80)
        else: s = 1.0
        if pulse and ms > 700:
            ph = ((ms - 700) % 520) / 520; s *= 1 + 0.10 * math.sin(ph * math.pi)
        r = rot if ms < 330 else lerp(rot, -rot * 0.6, (ms - 330) / 370)
        al = 1.0 if ms < dur_ms - 140 else max(0.0, (dur_ms - ms) / 140)
        return s, r, al

    def render(self, work, F):
        """-> list of (dir, t0, left, top) for ffmpeg inputs."""
        from PIL import Image
        res = []
        for k, it in enumerate(self.items):
            spr = self._sprite(it); bw = int(spr.width * 1.45) // 2 * 2; bh = int(spr.height * 1.6) // 2 * 2
            d = os.path.join(work, f'txt{k}'); os.makedirs(d, exist_ok=True)
            n = max(1, int(round((it['t1'] - it['t0']) * F))); dur = (it['t1'] - it['t0']) * 1000
            for i in range(n):
                s, r, al = self._curve(i * 1000 / F, dur, it['rot'], it['pulse'])
                im = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), BIC).rotate(r, BIC, expand=True)
                if al < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * al)))
                fr = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
                fr.alpha_composite(im, (max(0, (bw - im.width) // 2), max(0, (bh - im.height) // 2)))
                fr.save(os.path.join(d, f'{i:04d}.png'), compress_level=1)
            res.append((d, it['t0'], int(it['x'] - bw / 2), int(it['y'] - bh / 2)))
        return res


def sunburst(path, W, H, rgb, rays=14):
    """Cartoon rays for the end card (rotated by ffmpeg)."""
    from PIL import Image, ImageDraw, ImageFilter
    D = int(math.hypot(W, H)) + 4; c = D / 2
    im = Image.new('RGBA', (D, D), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(rays):
        a0 = 2 * math.pi * i / rays; a1 = a0 + math.pi / rays
        d.polygon([(c, c), (c + D * math.cos(a0), c + D * math.sin(a0)), (c + D * math.cos(a1), c + D * math.sin(a1))], fill=rgb + (90,))
    m = Image.new('L', (D, D), 0); ImageDraw.Draw(m).ellipse((c - D * 0.40, c - D * 0.40, c + D * 0.40, c + D * 0.40), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(D * 0.12))
    im.putalpha(Image.composite(im.getchannel('A'), Image.new('L', (D, D), 0), m))
    im.save(path)


def take_meta(project, take):
    p = os.path.join(promo_dir(project), 'raw', f'{take}.events.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def order_moments(ms, explicit, variant=0):
    if not explicit and len(ms) >= 3:
        ms = [ms[0]] + ms[2:] + [ms[1]]  # best first, second-best right before the end card
    if variant and len(ms) > 1:
        v = variant % len(ms); ms = [ms[v]] + ms[:v] + ms[v + 1:]
    return ms


def seg_len(x):
    return x[3]['hold'] if x[3].get('hold') else (x[1] - x[0]) / x[2]


def payoff_segs(s, e, p, slow, pre_speed, cartoon, F, hold_f):
    """Segments of one clip around its payoff p. Cartoon: speed-ramp -> 0.5x slow-mo into the hit, a hit-stop
    (held frame) exactly on p with flash + RGB split + boom, then shake + push-in out of it."""
    if not cartoon:
        return [(s, e, 1.0, {})]
    hold = hold_f / F if hold_f else 0.0
    if slow and p - s > 0.35 and e - p > 0.45:
        pre = [(s, p - 0.12, pre_speed, {}), (p - 0.12, p, 0.5, {'zoom': (1.0, 1.04)})]
        post = [(p, p + 0.33, 0.5, {'zoom': (1.06, 1.10), 'shake': True}), (p + 0.33, e, 1.0, {})]
    elif p - s > 1.5 / F and e - p > 0.3:
        pre = [(s, p, 1.0, {})]
        post = [(p, e, 1.0, {'zoom': (1.06, 1.0), 'shake': True})]
    else:  # payoff at the very edge of the clip: old-style hit on the cut
        return [(s, e, 1.0, {'impact': True, 'shake': True, 'zoom': (1.0, 1.10)})]
    if hold:
        hit = [(p, p + 1.0 / F, 1.0, {'impact': True, 'hold': hold, 'zoom': (1.06, 1.06)})]
    else:
        hit = []; post[0][3]['impact'] = True
    return pre + hit + post


def plan_long(ms, total, take_dur, story, a, F, hold_f):
    """Few long shots, as in the reference base: top CrazyGames previews cut 0-7 times in 6-19 s, H2T-style ads hold
    2.5-6 s shots of the game with its HUD. Story ads: payoff inside the first second, hit-stop only on the climax."""
    lo, hi = (2.4, 4.5) if story else (3.0, 6.0)
    n = max(1, min(len(ms), math.ceil(total / hi)))
    while n > 1 and total / n < lo: n -= 1
    per = total / n; clips = []
    for i, m in enumerate(ms[:n]):
        p = m['peak']; dur = take_dur.get(m['take'], p + per)
        lead = 0.6 if (story and i == 0) else (0.3 if i == 0 else 0.4) * per
        s0 = max(0.0, p - lead); e0 = min(dur, s0 + per); s0 = max(0.0, e0 - per)
        segs = [(s0, e0, 1.0, {})]
        if story and i == n - 1 and hold_f:  # the climax: biggest reward last, the only hit-stop of the video
            segs = payoff_segs(s0, e0, p, not a.no_slowmo, 1.0, True, F, hold_f)
            over_ = sum(seg_len(x) for x in segs) - (e0 - s0)
            a_, b, sp, fx = segs[-1]
            if b - over_ * sp - a_ >= 0.25: segs[-1] = (a_, b - over_ * sp, sp, fx)
            else: segs = [(s0, e0, 1.0, {})]
        segs[0][3]['first'] = True
        clips.append([(x[0], x[1], x[2], dict(x[3], peak=p, ev=m)) for x in segs])
    return clips


def plan_clips(ms, vp, style, total, a, xd, F=30, take_dur=None):
    """-> list of clips, each a list of segments (start, end, speed, fx) on the source take."""
    beat = 60.0 / a.bpm if a.bpm else 0
    scenes = vp.get('scenes')
    if style in ('story', 'clean') and not scenes:
        clips = plan_long(ms, total, take_dur or {}, style == 'story', a, F, 0 if a.no_hitstop else 3)
        if style == 'story' and not a.no_impact_frame:
            for x in clips[-1]:
                if x[3].get('hold'):
                    x[3]['hold'] += 2.0 / F; x[3]['climax'] = True
                    a_, b, sp, fx = clips[-1][-1]
                    if (b - a_) / sp > 2.0 / F + 0.25: clips[-1][-1] = (a_, b - 2.0 / F * sp, sp, fx)
        return clips
    cartoon = style == 'cartoon'
    slowmo = cartoon and not a.no_slowmo
    hold_f = 3 if cartoon and not a.no_hitstop else 0
    pre_speed = min(1.25, vp.get('speed_max', 1.0)) if cartoon else 1.0
    clips, acc = [], 0.0
    if scenes:  # short loop (Poki): k scenes of equal length
        k = max(scenes[0], min(scenes[-1], len(ms)))
        per = total / k
        for m in ms[:k]:
            s = max(0.0, m['peak'] - 0.6 * per); clips.append([(s, s + per, 1.0, {'first': True, 'ev': m, 'peak': m['peak']})])
        return clips
    for ci, m in enumerate(ms):
        ov = xd if ci else 0.0  # the transition overlap eats the head of every clip after the first
        left = total - acc
        if left < 0.8: break
        s, e, p = m['start'], m['end'], m['peak']
        if ci == 0 and cartoon:
            s = max(s, p - 0.85)  # the opener pays off inside the first second
        segs = payoff_segs(s, e, p, slowmo, pre_speed, cartoon, F, hold_f)
        fixed = sum(seg_len(x) for x in segs[:-1]) + 0.2
        if len(segs) > 1 and fixed > left + ov:  # no room for the slow-mo build-up: plain cut around the peak
            room = left + ov; s2 = max(m['start'], p - 0.4 * room)
            segs = payoff_segs(s2, s2 + room, p, False, 1.0, cartoon, F, hold_f)
        segs[0][3]['first'] = True
        out = sum(seg_len(x) for x in segs)
        want = out
        if beat:
            want = max(2 * beat, round((out - ov) / beat) * beat) + ov
        want = min(want, left + ov)
        a_, b, sp, fx = segs[-1]
        segs[-1] = (a_, max(a_ + 0.2, b + (want - out) * sp), sp, fx)
        clips.append([(x[0], x[1], x[2], dict(x[3], peak=p, ev=m)) for x in segs])
        acc += sum(seg_len(x) for x in segs) - ov
    # the last payoff before the end card is the climax: 2 more held frames that carry the anime impact frame
    if hold_f and not a.no_impact_frame:
        for clip in reversed(clips):
            hi = next((i for i, x in enumerate(clip) if x[3].get('hold')), None)
            if hi is None: continue
            extra = 2.0 / F; a_, b, sp, fx = clip[-1]
            if (b - a_) / sp < extra + 0.25: continue
            clip[-1] = (a_, b - extra * sp, sp, fx)
            clip[hi][3]['hold'] += extra; clip[hi][3]['climax'] = True
            break
    return clips


def interp_cache(project, jobs, FW, FH, sw, sh, fxp, fyp, F, has_audio):
    """Motion-interpolate slow-mo segments once (in parallel) into promo/cache/: {(take, s, e, sp): file}."""
    from concurrent.futures import ThreadPoolExecutor
    cdir = os.path.join(promo_dir(project), 'cache'); os.makedirs(cdir, exist_ok=True)
    todo, out = [], {}
    for (take, s, e, sp) in jobs:
        raw = os.path.join(promo_dir(project), 'raw', f'{take}.mp4')
        key = hashlib.sha1(repr((raw, os.path.getmtime(raw), round(s, 4), round(e, 4), round(sp, 4),
                                 FW, FH, sw, sh, fxp, fyp, F)).encode()).hexdigest()[:16]
        path = os.path.join(cdir, f'interp_{key}.mkv'); out[(take, s, e, sp)] = path
        if not os.path.exists(path) and path not in [t[4] for t in todo]:
            todo.append((raw, s, e, sp, path, has_audio[take]))

    def one(j):
        raw, s, e, sp, path, aud = j
        vf = ','.join(['mpdecimate', f"crop='min(iw,ih*{FW}/{FH})':'min(ih,iw*{FH}/{FW})':'(iw-ow)*{fxp}':'(ih-oh)*{fyp}'",
                       f'scale={sw}:{sh}:flags=lanczos', f'minterpolate=fps={int(round(F / sp))}:mi_mode=mci:mc_mode=obmc:me_mode=bidir',
                       f'setpts=(PTS-STARTPTS)/{sp:.4f}', f'fps={F}'])
        cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{max(0, s):.3f}', '-t', f'{e - s:.3f}', '-i', raw, '-vf', vf]
        cmd += (['-af', f'asetpts=PTS-STARTPTS,{atempo_chain(sp)}', '-c:a', 'pcm_s16le'] if aud else ['-an'])
        cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12', '-pix_fmt', 'yuv420p', path + '.part.mkv']
        run(cmd); os.replace(path + '.part.mkv', path)
    if todo:
        with ThreadPoolExecutor(max(1, min(4, (os.cpu_count() or 2) // 2))) as ex:
            list(ex.map(one, todo))
    return out


def impact_lines(path, W, H, seed):
    """Speed lines for the anime impact frame: black wedges converging on the centre, centre left clear."""
    import random
    from PIL import Image, ImageChops, ImageDraw
    rnd = random.Random(seed)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx, cy = W / 2, H / 2; R = math.hypot(W, H) / 2 + 10; base = min(W, H)
    for i in range(56):
        ang = rnd.random() * 2 * math.pi; thick = i < 34
        hw = rnd.uniform(0.010, 0.026) if thick else rnd.uniform(0.002, 0.006)
        r_in = base * rnd.uniform(0.30, 0.50)
        d.polygon([(cx + R * math.cos(ang - hw), cy + R * math.sin(ang - hw)), (cx + R * math.cos(ang + hw), cy + R * math.sin(ang + hw)),
                   (cx + r_in * math.cos(ang), cy + r_in * math.sin(ang))], fill=(0, 0, 0, 255 if thick else 210))
    mask = Image.radial_gradient('L').resize((W, H)).point(lambda v: min(255, int(max(0, v - 70) * 2.2)))
    img.putalpha(ImageChops.multiply(img.split()[3], mask)); img.save(path)
    return path


def atempo_chain(sp):
    parts = []
    while sp < 0.5: parts.append('atempo=0.5'); sp /= 0.5
    while sp > 2.0: parts.append('atempo=2.0'); sp /= 2.0
    parts.append(f'atempo={sp:.4f}')
    return ','.join(parts)


def build(project, cfg, pname, plat, vp, lang, moments, a, workroot, hook='', variant=0):
    W, H, F = vp['w'], vp['h'], vp.get('fps', 30)
    style = a.style or ('clean' if vp.get('text') == 'none' else 'story')
    cartoon = style == 'cartoon'; story = style == 'story'; juicy = cartoon or story
    with_text = vp.get('text') != 'none' and juicy
    with_audio = vp.get('audio', True)
    total = a.duration or vp.get('target_s') or (vp['max_s'] if not juicy else min(vp['max_s'], max(vp.get('min_s', 9), 15)))
    total = max(vp.get('min_s', 1), min(vp['max_s'], total))
    title = text_for(cfg, 'title', lang); cta = text_for(cfg, 'cta', lang)
    endcard = (1.5 if story else 1.8) if with_text and (cta or title) else 0.0
    cover = None
    if a.cover_first or plat.get('first_frame_cover') is True:
        cdir = os.path.join(promo_dir(project), 'out', pname, 'covers')
        cands = [os.path.join(cdir, f) for f in os.listdir(cdir) if f.endswith('.png')] if os.path.isdir(cdir) else []
        if cands:
            from PIL import Image
            def ar(c): w_, h_ = Image.open(c).size; return w_ / h_
            cover = min(cands, key=lambda c: abs(math.log(ar(c) / (W / H))))
        else:
            print(f'  warn: {pname} wants the cover as first frame; run shots.py --covers first')
    intro = 0.5 if cover else 0.0
    xd = 0.14 if cartoon else 0.0
    if not moments: die('no moments selected')
    src = {m['take']: probe(os.path.join(promo_dir(project), 'raw', f'{m["take"]}.mp4')) for m in moments}
    real_fps = {t: take_meta(project, t).get('real_fps', src[t]['fps']) for t in src}
    clips = plan_clips(moments, vp, style, total - endcard - intro, a, xd, F, {t: src[t]['dur'] for t in src})
    if not clips: die('not enough material for this duration')

    # layout: portrait ad from a landscape take -> gameplay card on its own blurred copy
    sp0 = next(iter(src.values())); src_ar = sp0['w'] / max(1, sp0['h']); dst_ar = W / H
    layout = a.layout if a.layout != 'auto' else ('stack' if juicy and src_ar / dst_ar > 1.5 and H > W else 'cover')
    fam_path = font_file(cfg)
    safe = vp.get('safe', {'top': 0.06, 'bottom': 0.08, 'side': 0.05})
    top_y = H * safe['top']; bot_y = H * (1 - safe['bottom'])
    maxw = W * (1 - 2 * safe.get('side', 0.05)) * 0.92; base = min(W, H)
    hook_lines, hook_size = fit_text(hook, fam_path, base * 0.105, maxw) if (with_text and hook) else ([], 0)
    hook_h = hook_size * 1.12 * len(hook_lines)
    if layout == 'stack':  # card under the hook band, its bottom may run into the lower safe zone a little
        FW = (W - 2 * int(W * 0.035)) // 2 * 2
        card_top = int(top_y + hook_h + H * 0.03) if hook_h else int(top_y)
        FH = int(min(FW * 1.25, bot_y + H * 0.04 - card_top)) // 2 * 2
        if not hook_h: card_top = (H - FH) // 2
    else:
        FW, FH, card_top = W, H, 0
    work = tempfile.mkdtemp(prefix=f'{pname}_{vp["name"]}_{lang}_', dir=workroot)
    inputs, fc, idx = [], [], 0
    over = 1.06 if juicy else 1.0
    fxp = cfg.get('focus_x', 0.5); fyp = cfg.get('focus_y', 0.5)
    sw, sh = int(math.ceil(FW * over / 2) * 2), int(math.ceil(FH * over / 2) * 2)
    clip_v, clip_a, clip_len, clip_caps, clip_imp = [], [], [], [], []
    if cover:
        inputs += ['-loop', '1', '-framerate', str(F), '-t', f'{intro:.3f}', '-i', cover]
        fc.append(f'[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p,settb=AVTB,fps={F}[cvI]')
        fc.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{intro:.3f}[caI]')
        clip_v.append('[cvI]'); clip_a.append('[caI]'); clip_len.append(intro); clip_caps.append([]); clip_imp.append([])
        idx += 1
    interp_used = False
    cache = {}
    if not a.draft:  # slow-mo of a low-fps take: in-between frames synthesized once, in parallel, reused next time
        jobs = [(fx['ev']['take'] if fx.get('ev') else moments[0]['take'], s_, e_, sp_) for clip in clips for (s_, e_, sp_, fx) in clip]
        jobs = [j for j in jobs if j[3] < 0.99 and real_fps[j[0]] * j[3] < 40]
        cache = interp_cache(project, jobs, FW, FH, sw, sh, fxp, fyp, F, {t: src[t]['audio'] for t in src}) if jobs else {}
    for ci, clip in enumerate(clips):
        segv, sega, local, caps, imps = [], [], 0.0, [], []
        for (s, e, sp, fx) in clip:
            take = fx['ev']['take'] if fx.get('ev') else moments[0]['take']
            pr = src[take]
            hold = fx.get('hold', 0.0)
            d_out = hold or (e - s) / sp
            L = f's{idx}'
            cached = None if hold else cache.get((take, s, e, sp))
            if cached:  # already cropped, scaled, interpolated and retimed
                inputs += ['-i', cached]; fg = []; bg_time = ''
                interp_used = True
            else:
                inputs += ['-ss', f'{max(0, s):.3f}', '-t', f'{(max(e - s, 0.2) if hold else e - s):.3f}', '-i', os.path.join(promo_dir(project), 'raw', f'{take}.mp4')]
                fg = [f"crop='min(iw,ih*{FW}/{FH})':'min(ih,iw*{FH}/{FW})':'(iw-ow)*{fxp}':'(ih-oh)*{fyp}'",
                      f'scale={sw}:{sh}:flags=lanczos']
                if hold:  # hit-stop: the event frame held still
                    n_ = max(1, int(round(hold * F)))
                    tm = ['trim=end_frame=1', f'loop=loop={n_ - 1}:size=1:start=0', f'setpts=N/{F}/TB']
                else:
                    tm = [f'setpts=(PTS-STARTPTS)/{sp:.4f}', f'fps={F}']
                fg += tm; bg_time = ','.join(tm) + ','
            if layout == 'stack':
                fc.append(f'[{idx}:v]split[{L}bg0][{L}fg0]')
                fc.append(f'[{L}bg0]{bg_time}scale={W // 4}:{H // 4}:force_original_aspect_ratio=increase,'
                          f'crop={W // 4}:{H // 4},gblur=sigma=10,scale={W}:{H},eq=brightness=-0.14:saturation=1.25[{L}bg]')
                ch = [f'[{L}fg0]'] + fg
            else:
                ch = [f'[{idx}:v]'] + fg
            if fx.get('shake') and juicy:
                amp = int(min(FW, FH) * 0.014)
                ch.append(f"crop={FW}:{FH}:x='(iw-ow)*{fxp}+{amp}*sin(t*57)*exp(-t*9)':y='(ih-oh)*{fyp}+{amp}*cos(t*43)*exp(-t*9)'")
            else:
                ch.append(f"crop={FW}:{FH}:x='(iw-ow)*{fxp}':y='(ih-oh)*{fyp}'")
            if cartoon and fx.get('first'):
                ch.append(f"zoompan=z='max(1,1.16-0.64*it)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={FW}x{FH}:fps={F}")
            elif juicy and fx.get('zoom'):  # push-in into the hit, a notch up on it, on out of it
                z0, z1 = fx['zoom']
                z = f'{z0}' if z0 == z1 else f'{z0}+{z1 - z0:.4f}*min(1,it/{max(d_out, 0.1):.3f})'
                ch.append(f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={FW}x{FH}:fps={F}")
            if juicy and fx.get('impact'):
                k = max(4, int(FW * 0.006))
                ch.append(f"rgbashift=rh=-{k}:bh={k}:enable='lt(t,0.16)'")
                ch.append(f"eq=brightness=0.12:enable='lt(t,{1.5 / F:.4f})'")
            if juicy:
                ch.append('eq=saturation=1.16:contrast=1.05' if cartoon else 'eq=saturation=1.08:contrast=1.03')
            ch += ['setsar=1', 'format=yuv420p']
            if layout == 'stack':
                bw_ = max(4, int(W * 0.006))
                ch.append(f'pad=iw+{2 * bw_}:ih+{2 * bw_}:{bw_}:{bw_}:color=white')
                fc.append(ch[0] + ','.join(ch[1:]) + f'[{L}fg]')
                fc.append(f'[{L}bg][{L}fg]overlay=(W-w)/2:{card_top - max(4, int(W * 0.006))},setsar=1,format=yuv420p[v{idx}]')
            else:
                fc.append(ch[0] + ','.join(ch[1:]) + f'[v{idx}]')
            if pr['audio'] and not hold:
                tempo = '' if cached else f'{atempo_chain(sp)},'
                fc.append(f'[{idx}:a]asetpts=PTS-STARTPTS,{tempo}aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d_out:.3f}[a{idx}]')
            else:  # the hit-stop is silent: the boom carries it
                fc.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{d_out:.3f}[a{idx}]')
            segv.append(f'[v{idx}]'); sega.append(f'[a{idx}]')
            if fx.get('impact') and juicy:
                imps.append((local, bool(fx.get('climax'))))
                if with_text and fx.get('ev'):
                    txt = caption_for(cfg, fx['ev'], lang)
                    if txt: caps.append((local + 0.05, txt))
            elif story and with_text and fx.get('ev') and not caps and s <= fx['peak'] < e:  # banner on every shot's event
                txt = caption_for(cfg, fx['ev'], lang)
                if txt: caps.append((local + (fx['peak'] - s) / sp, txt))
            idx += 1; local += d_out
        fc.append(''.join(v + a_ for v, a_ in zip(segv, sega)) + f'concat=n={len(segv)}:v=1:a=1[cv{ci}r][ca{ci}]')
        fc.append(f'[cv{ci}r]settb=AVTB,fps={F}[cv{ci}]')
        clip_v.append(f'[cv{ci}]'); clip_a.append(f'[ca{ci}]'); clip_len.append(local); clip_caps.append(caps); clip_imp.append(imps)
    # join clips: xfade/acrossfade in cartoon, hard concat otherwise
    starts, t = [], 0.0
    if xd and len(clip_v) > 1:
        vcur, acur = clip_v[0], clip_a[0]; t = clip_len[0]; starts.append(0.0)
        for k in range(1, len(clip_v)):
            off = t - xd; starts.append(off)
            tr = 'fadewhite' if (cover and k == 1) else TRANSITIONS[(k - 1 + variant) % len(TRANSITIONS)]
            fc.append(f'{vcur}{clip_v[k]}xfade=transition={tr}:duration={xd}:offset={off:.4f}[xv{k}]')
            fc.append(f'{acur}{clip_a[k]}acrossfade=d={xd}:c1=tri:c2=tri[xa{k}]')
            vcur, acur = f'[xv{k}]', f'[xa{k}]'; t = off + clip_len[k]
    else:
        for L_ in clip_len: starts.append(t); t += L_
        fc.append(''.join(v + a_ for v, a_ in zip(clip_v, clip_a)) + f'concat=n={len(clip_v)}:v=1:a=1[xv][xa]')
        vcur, acur = '[xv]', '[xa]'
    body_end = t; total_out = body_end + endcard
    cut_times = starts[1:]
    captions = [(starts[k] + lt, txt) for k, cs in enumerate(clip_caps) for lt, txt in cs]
    impacts = [(starts[k] + lt, cl) for k, im in enumerate(clip_imp) for lt, cl in im]
    climax = next((round(t_ * F) / F for t_, cl in impacts if cl), None)
    if climax is not None:  # anime impact frame: 3 frames of negative + speed lines on the climax hit-stop
        def fwin(k0, k1): return f'between(t,{climax + (k0 - 0.5) / F:.4f},{climax + (k1 - 0.5) / F:.4f})'
        en = fwin(0, 3)
        lines = [impact_lines(os.path.join(work, f'lines{j}.png'), W, H, 11 + j) for j in (0, 1)]
        for j, lp in enumerate(lines):
            inputs += ['-loop', '1', '-framerate', str(F), '-t', f'{total_out:.3f}', '-i', lp]
            fc.append(f'[{idx}:v]format=rgba[ln{j}]'); idx += 1
        fc.append(f"{vcur}hue=s=0:enable='{en}',negate=enable='{en}',eq=contrast=1.45:enable='{en}'[cx0]")
        fc.append(f"[cx0][ln0]overlay=0:0:enable='{fwin(0, 1)}+{fwin(2, 3)}':format=auto[cx1]")
        fc.append(f"[cx1][ln1]overlay=0:0:enable='{fwin(1, 2)}':format=auto[cx2]")
        vcur = '[cx2]'
    vtail = vcur
    if endcard:
        fc.append(f"{vcur}tpad=stop_mode=clone:stop_duration={endcard:.2f},gblur=sigma=18:enable='gte(t,{body_end:.2f})',"
                  f"eq=brightness=-0.12:saturation=1.2:enable='gte(t,{body_end:.2f})'[ce]")
        bpath = os.path.join(work, 'burst.png'); sunburst(bpath, W, H, hex_to_rgb(cfg['colors']['accent']))
        inputs += ['-loop', '1', '-framerate', str(F), '-t', f'{endcard:.3f}', '-i', bpath]
        fc.append(f"[{idx}:v]format=rgba,rotate=a='t*0.45':c=none:ow={W}:oh={H},fade=t=in:st=0:d=0.25:alpha=1,"
                  f"setpts=PTS-STARTPTS+{body_end:.3f}/TB[burst]")
        fc.append('[ce][burst]overlay=0:0:eof_action=pass:format=auto[ceb]')
        vtail = '[ceb]'; idx += 1
    hook_end = 0.0
    if with_text:
        tl = TextLayer(W, H, fam_path, cfg)
        ban_size = int(base * 0.075)
        ban_y = int(H * cfg['banner_y']) if cfg.get('banner_y') else int(top_y + ban_size * 0.9)  # lower it under the game's own top UI
        if hook and story and layout != 'stack':  # the hook as the game's own banner ("RUN!") over the opener
            b_lines, b_size = fit_text(hook, fam_path, ban_size * 1.15, maxw * 0.8)
            hook_end = min(2.4 + intro, body_end)
            tl.pop(0.10 + intro, hook_end, b_lines, b_size, W // 2, ban_y, rot=0, banner=True)
        elif hook:
            if layout == 'stack':  # headline stays over the card for the whole body
                tl.pop_words(0.10 + intro, body_end, hook_lines, hook_size, W // 2, int(top_y + hook_h / 2), colour=tl.acc)
            else:
                y = int(top_y + hook_h / 2 + H * (0.10 if H > W else 0.06))
                tl.pop_words(0.10 + intro, min(2.3 + intro, body_end), hook_lines, hook_size, W // 2, y, colour=tl.acc)
        shown = 0
        for t0, txt in captions:  # each caption a notch bigger and more tilted than the last
            if story:  # banner captions: same size, no tilt, top centre, never over the hook banner
                if t0 < hook_end or t0 > body_end - 0.4: continue
                lines, size = fit_text(txt, fam_path, ban_size, maxw * 0.8)
                y = ban_y if layout != 'stack' else int(min(bot_y, card_top + FH) - size * 1.2)
                tl.pop(t0, min(t0 + 1.2, body_end), lines, size, W // 2, y, rot=0, banner=True)
                shown += 1; continue
            if (layout != 'stack' and t0 < 2.2 + intro) or t0 > body_end - 0.4: continue
            lines, size = fit_text(txt, fam_path, base * 0.082 * min(1.3, 1 + 0.1 * shown), maxw)
            y = int(min(bot_y, card_top + FH) - size * 0.75 * len(lines) - size * 0.5)
            tl.pop(t0, min(t0 + 1.0, body_end), lines, size, W // 2, y, rot=(1 if shown % 2 else -1) * min(6, 3 + shown))
            shown += 1
        logo = cfg.get('logo')
        logo = (logo if os.path.isabs(logo) else os.path.join(project, logo)) if logo else ''
        if story and cta and not a.no_cta_bar and body_end > 3.4:  # small persistent "Play free" pill under the action
            p_lines, p_size = fit_text(cta, fam_path, base * 0.042, maxw * 0.4, max_lines=1)
            tl.pop(2.4 + intro, body_end, p_lines, p_size, W // 2, int(bot_y - p_size * 1.3), colour=tl.acc, rot=0,
                   pulse=True, button=True)
        if story and cfg.get('corner_logo') and logo and os.path.exists(logo):  # game logo held in the top-left corner
            lsz = int(base * 0.17)
            tl.pop(0.0, body_end, [], lsz, int(W * safe.get('side', 0.05) + lsz * 0.55), int(top_y + lsz * 0.4), rot=0, image=logo)
        if endcard:
            c_lines, c_size = fit_text(cta, fam_path, base * 0.075, maxw * 0.72, max_lines=1) if cta else ([], 0)
            btn_h = c_size * 2.2 if cta else 0; gap = base * 0.05
            if logo and os.path.exists(logo):
                from PIL import Image
                lw, lh_ = Image.open(logo).size; t_size = int(base * 0.62); t_h = t_size * min(1.0, lh_ / max(lw, lh_))
                t_lines = []
            elif title:
                t_lines, t_size = fit_text(title, fam_path, base * 0.16, maxw); t_h = t_size * 1.12 * len(t_lines)
            else:
                t_lines, t_size, t_h = [], 0, 0
            block = t_h + (gap + btn_h if cta else 0)  # title + button stacked, centred a bit above the middle
            y0 = max(top_y, min(H * 0.46 - block / 2, bot_y - block))
            if logo and os.path.exists(logo):
                tl.pop(body_end + 0.02, total_out, [], t_size, W // 2, int(y0 + t_h / 2), rot=-2, image=logo)
            elif t_lines:
                tl.pop(body_end + 0.02, total_out, t_lines, t_size, W // 2, int(y0 + t_h / 2), rot=-2)
            if cta:
                tl.pop(body_end + 0.35, total_out, c_lines, c_size, W // 2, int(y0 + t_h + gap + btn_h / 2), colour=tl.acc,
                       rot=0, pulse=True, button=True)
        cur = vtail
        for k, (d, t0, x, y) in enumerate(tl.render(work, F)):
            inputs += ['-framerate', str(F), '-i', os.path.join(d, '%04d.png')]
            fc.append(f'[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{t0:.3f}/TB[tx{k}]')
            fc.append(f'{cur}[tx{k}]overlay=x={x}:y={y}:eof_action=pass:format=auto[ov{k}]')
            cur = f'[ov{k}]'; idx += 1
        fc.append(f'{cur}format=yuv420p[vout]')
    else:
        fc.append(f'{vtail}null[vout]')
    maps = ['-map', '[vout]']
    beat_note = ''
    if with_audio:
        dip = f"volume='if(between(t,{climax - 0.35:.3f},{climax:.3f}),0.2,1)':eval=frame," if climax is not None else ''
        mix = [f'{acur}apad,atrim=0:{total_out:.3f},{dip}volume={cfg.get("game_volume", 0.7)}[g]']; mixl = ['[g]']
        music = a.music or cfg.get('music')
        if music:
            music = music if os.path.isabs(music) else os.path.join(project, music)
            if not os.path.exists(music):
                print(f'  warn: music {music} not found'); music = ''
        if not music and juicy and not a.no_beat:
            music = synth(os.path.join(work, 'beat.wav'), 'beat', a.bpm or 120, total_out + 1)
            beat_note = f' beat={int(a.bpm or 120)}bpm(generated)'
        if music:
            inputs += ['-stream_loop', '-1', '-i', music]
            mv = cfg.get('music_volume', 0.8) * (0.7 if beat_note else 1.0) * (0.75 if story else 1.0)  # story: the game leads
            mix.append(f'[{idx}:a]atrim=0:{total_out:.3f},afade=t=in:d=0.05,afade=t=out:st={max(0, total_out - 1.0):.2f}:d=1.0,'
                       f'{dip}volume={mv},aresample=48000,aformat=channel_layouts=stereo[m]')
            mixl.append('[m]'); idx += 1
        if juicy and not a.no_sfx:
            wh = sound('whoosh_in.mp3'); pp = sound('pop.mp3'); win = sound('success_big.mp3') or sound('reward.mp3')
            boom = synth(os.path.join(work, 'boom.wav'), 'boom', dur=1.0)
            # sample peaks (measured): whoosh_in 0.19 s, success_big 0.16 s, boom/pop at 0 -> peak on the frame
            sfx = [(wh, max(0, t_ + xd / 2 - 0.19), 0.5) for t_ in cut_times] if (wh and cartoon) else []
            sfx += [(boom, t_, 1.0 if cl else min(0.85, 0.6 + 0.08 * i)) for i, (t_, cl) in enumerate(impacts)]
            sfx += [(pp, t_, 0.55) for t_, _ in captions if (layout == 'stack' or t_ >= (hook_end if story else 2.2 + intro))
                    and t_ <= body_end - 0.4] if pp else []
            if pp and hook: sfx.append((pp, 0.10 + intro, 0.5))
            if win and endcard: sfx.append((win, max(0, body_end + 0.02 - 0.16), 0.7))
            for k, (f, t_, vol) in enumerate(sfx):
                inputs += ['-i', f]
                mix.append(f'[{idx}:a]adelay={int(t_ * 1000)}:all=1,volume={vol},aresample=48000,aformat=channel_layouts=stereo[s{k}]')
                mixl.append(f'[s{k}]'); idx += 1
        mix.append(''.join(mixl) + f'amix=inputs={len(mixl)}:normalize=0:duration=first,'
                   f'loudnorm=I={vp.get("lufs", -14)}:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.89[aout]')
        fc += mix; maps += ['-map', '[aout]']
    else:
        fc.append(f'{acur}anullsink')
    open(os.path.join(work, 'graph.txt'), 'w').write(';\n'.join(fc))
    odir = os.path.join(promo_dir(project), 'out', pname, lang if with_text else 'all'); os.makedirs(odir, exist_ok=True)
    suffix = f'_h{variant + 1}' if variant else ''
    out = os.path.join(odir, f'{vp["name"]}{suffix}.mp4')
    enc = ['-c:v', 'libx264', '-preset', 'veryfast' if a.draft else 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(F), '-movflags', '+faststart']
    enc += (['-c:a', 'aac', '-b:a', '192k'] if with_audio else ['-an'])
    cmd = ['ffmpeg', '-y', '-v', 'error'] + inputs + ['-/filter_complex', 'graph.txt'] + maps + enc + ['-t', f'{total_out:.3f}', out]
    cwd = os.getcwd(); os.chdir(work)
    try:
        run(cmd)
        pr = probe(out)
        if pr['size_mb'] > vp.get('max_mb', 1e9):
            br = int(vp['max_mb'] * 8e6 * 0.93 / max(pr['dur'], 1) - (192000 if with_audio else 0))
            enc2 = list(enc); i = enc2.index('-crf'); enc2[i:i + 2] = ['-b:v', str(br), '-maxrate', str(br), '-bufsize', str(br * 2)]
            run(['ffmpeg', '-y', '-v', 'error'] + inputs + ['-/filter_complex', 'graph.txt'] + maps + enc2 + ['-t', f'{total_out:.3f}', out])
            pr = probe(out)
    finally:
        os.chdir(cwd)
        if a.keep_work: print('  work dir:', work)
    rev = os.path.join(promo_dir(project), 'review'); os.makedirs(rev, exist_ok=True)
    sheet = os.path.join(rev, f'{pname}_{vp["name"]}_{lang if with_text else "all"}{suffix}.jpg')
    cols = 4 if W >= H else 6; nfr = 12 if W < H else 8
    run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-vf', f'fps={nfr / max(pr["dur"], 1):.4f},scale={480 if W >= H else 240}:-2,tile={cols}x{math.ceil(nfr / cols)}',
         '-frames:v', '1', sheet])
    problems = []
    if pr['w'] != W or pr['h'] != H: problems.append(f'size {pr["w"]}x{pr["h"]}')
    if pr['dur'] < vp.get('min_s', 0) - 0.2: problems.append(f'too short {pr["dur"]:.1f}s < {vp["min_s"]}s (need more moments)')
    if pr['dur'] > vp['max_s'] + 0.2: problems.append(f'too long {pr["dur"]:.1f}s')
    if pr['size_mb'] > vp.get('max_mb', 1e9): problems.append(f'{pr["size_mb"]:.1f} MB > {vp["max_mb"]} MB')
    if not with_audio and pr['audio']: problems.append('has audio but preset is muted')
    if not a.keep_work: shutil.rmtree(work, ignore_errors=True)
    info = (f'clips={len(clips)} style={style} layout={layout}{beat_note}' + (' slowmo=interpolated' if interp_used else '')
            + (f' hook="{hook}"' if hook else ''))
    return out, pr, sheet, problems, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--platform', default='ads_landscape', help='default: ads_landscape (Alex\'s main ad format, 16:9)')
    ap.add_argument('--video', help='preset name inside the platform (default: all videos of the platform)')
    ap.add_argument('--lang')
    ap.add_argument('--moments', help='ids from moments.json in the wanted order')
    ap.add_argument('--style', choices=['story', 'cartoon', 'clean'], help='ads: story (default) or cartoon; previews: clean')
    ap.add_argument('--cover-first', action='store_true', help='static cover as the first 0.5 s (CrazyGames recommends it)')
    ap.add_argument('--no-cta-bar', action='store_true', help='story: no persistent CTA pill')
    ap.add_argument('--duration', type=float)
    ap.add_argument('--music')
    ap.add_argument('--bpm', type=float, default=0)
    ap.add_argument('--layout', choices=['auto', 'cover', 'stack'], default='auto')
    ap.add_argument('--variants', type=int, default=0, help='hook variants per language (default: every hook in config)')
    ap.add_argument('--no-slowmo', action='store_true')
    ap.add_argument('--no-sfx', action='store_true')
    ap.add_argument('--no-hitstop', action='store_true', help='no held frames on the payoffs')
    ap.add_argument('--no-impact-frame', action='store_true', help='no negative + speed-lines frame on the climax')
    ap.add_argument('--no-beat', action='store_true', help='no generated beat bed when there is no music')
    ap.add_argument('--draft', action='store_true', help='fast preview: no motion interpolation, fast encoder')
    ap.add_argument('--keep-work', action='store_true', help='keep the filter graph and text frames (debug)')
    a = ap.parse_args()
    need_ffmpeg()
    project = os.path.abspath(a.project); cfg = load_config(project)
    if not a.bpm: a.bpm = cfg.get('bpm', 0)
    if not a.bpm and not (a.music or cfg.get('music')) and not a.no_beat: a.bpm = 120
    plat = platform(a.platform)
    vids = [v for v in plat.get('videos', []) if not a.video or v['name'] == a.video]
    if not vids: die(f'no video preset {a.video} in {a.platform}')
    ms = load_moments(project)
    if a.moments:
        by = {m['id']: m for m in ms}; ms = [by[int(i)] for i in a.moments.split(',') if int(i) in by]
    workroot = os.path.join(promo_dir(project), '.work'); os.makedirs(workroot, exist_ok=True)
    for vp in vids:
        needs_text = vp.get('text') != 'none' and (a.style or 'story') in ('story', 'cartoon')
        for lang in (langs_arg(cfg, a.lang) if needs_text else ['all']):
            hooks = hooks_for(cfg, lang) if needs_text else []
            hooks = (hooks[:a.variants] if a.variants else hooks) or ['']
            for v, hook in enumerate(hooks):
                order = order_moments(ms, bool(a.moments), v)
                a_ = argparse.Namespace(**{**vars(a), 'bpm': a.bpm if needs_text else 0})
                out, pr, sheet, probs, info = build(project, cfg, a.platform, plat, vp, lang, order, a_, workroot, hook, v)
                flag = 'OK ' if not probs else 'FIX'
                print(f'{flag} {os.path.relpath(out, project)}: {pr["w"]}x{pr["h"]} {pr["dur"]:.1f}s {pr["size_mb"]:.1f}MB '
                      f'audio={pr["audio"]} {info} | sheet {os.path.relpath(sheet, project)}'
                      + (' | ' + '; '.join(probs) if probs else ''), flush=True)
    if not a.keep_work: shutil.rmtree(workroot, ignore_errors=True)


if __name__ == '__main__':
    main()
