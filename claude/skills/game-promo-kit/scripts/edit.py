"""Cut and edit promo videos from the picked moments, per platform preset and language.

  edit.py --project DIR --platform crazygames [--video preview_landscape] [--lang en,ru]
          [--moments 3,1,5] [--style cartoon|clean] [--duration 15] [--music file.mp3] [--bpm 128]
          [--no-slowmo] [--no-sfx]

cartoon: punch-zoom on every cut, white flash, speed-ramp + slow-mo at the payoff, impact shake,
         colour pop, pop-in localized texts (hook / captions / end card with title + CTA), whoosh/pop SFX.
clean:   hard cuts, no text, no speed tricks (platform hover/preview videos).
The preset (references/platforms.json) sets size, fps, duration, audio on/off, text policy, size cap.
Output: promo/out/<platform>/<lang|all>/<video>.mp4 + promo/review/<platform>_<video>_<lang>.jpg.
"""
import argparse, json, math, os, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from common import (caption_for, die, font_file, hex_to_rgb, langs_arg, load_config,
                    load_moments, need_ffmpeg, platform, probe, promo_dir, run, sound, text_for)


def fit_text(text, font_path, size, max_w, max_lines=2):
    """Shrink + wrap so localized strings (long German, CJK) stay inside max_w."""
    from PIL import ImageFont
    words = text.split()
    while size > 12:
        f = ImageFont.truetype(font_path, int(size))
        wid = lambda s: f.getlength(s)
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
        elif len(words) == 1 and len(text) > 8 and wid(text) > max_w and not text.isascii():
            half = len(text) // 2  # CJK: split by characters
            a, b = text[:half], text[half:]
            if max(wid(a), wid(b)) <= max_w: return [a, b], int(size)
        size *= 0.92
    return [text], 12


class TextLayer:
    """Pop-in texts rendered by Pillow as RGBA frame sequences, overlaid by ffmpeg (no libass needed)."""
    def __init__(self, W, H, font_path, cfg):
        c = cfg['colors']; self.W, self.H, self.fp, self.items = W, H, font_path, []
        self.text, self.acc, self.out = hex_to_rgb(c['text']), hex_to_rgb(c['accent']), hex_to_rgb(c['outline'])

    def pop(self, t0, t1, lines, size, x, y, colour=None, rot=-3, pulse=False):
        if t1 - t0 > 0.15:
            self.items.append(dict(t0=t0, t1=t1, lines=lines, size=int(size), x=x, y=y, col=colour or self.text, rot=rot, pulse=pulse))

    def _sprite(self, it):
        from PIL import Image, ImageDraw, ImageFont
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
            ph = ((ms - 700) % 500) / 500; s *= 1 + 0.10 * math.sin(ph * math.pi)
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
                im = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC).rotate(r, Image.BICUBIC, expand=True)
                if al < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * al)))
                fr = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
                fr.alpha_composite(im, (max(0, (bw - im.width) // 2), max(0, (bh - im.height) // 2)))
                fr.save(os.path.join(d, f'{i:04d}.png'), compress_level=1)
            res.append((d, it['t0'], int(it['x'] - bw / 2), int(it['y'] - bh / 2)))
        return res


def order_moments(ms, explicit):
    if explicit:
        return ms
    if len(ms) < 3:
        return ms
    best, second, rest = ms[0], ms[1], ms[2:]
    return [best] + rest + [second]


def plan_clips(ms, vp, style, total, fps_src, a):
    """Return list of clips, each a list of segments (start, end, speed, fx) on the source take."""
    beat = 60.0 / a.bpm if a.bpm else 0
    scenes = vp.get('scenes')
    slowmo = style == 'cartoon' and not a.no_slowmo and fps_src >= 45
    pre_speed = min(1.25, vp.get('speed_max', 1.0)) if style == 'cartoon' else 1.0
    clips, acc = [], 0.0
    if scenes:  # short loop (Poki): k scenes of equal length
        k = max(scenes[0], min(scenes[-1], len(ms)))
        per = total / k
        for m in ms[:k]:
            s = max(0.0, m['peak'] - 0.6 * per); clips.append([(s, s + per, 1.0, {'first': True, 'ev': m, 'peak': m['peak']})])
        return clips
    for m in ms:
        left = total - acc
        if left < 0.6: break
        s, e, p = m['start'], m['end'], m['peak']
        segs = []
        if slowmo and p - s > 0.4 and e - p > 0.45:
            a1, b1 = s, p - 0.12; a2, b2 = p - 0.12, p + 0.33; a3, b3 = b2, e
            segs = [(a1, b1, pre_speed, {}), (a2, b2, 0.5, {'impact': True}), (a3, b3, 1.0, {})]
        else:
            segs = [(s, e, 1.0, {'impact': style == 'cartoon'})]
        segs[0][3]['first'] = True
        out = sum((b - a_) / sp for a_, b, sp, _ in segs)
        want = out
        if beat:
            want = max(2 * beat, round(out / beat) * beat)
        want = min(want, left)
        # trim/extend the last segment to hit `want`
        a_, b, sp, fx = segs[-1]
        b = max(a_ + 0.2, b + (want - out) * sp)
        segs[-1] = (a_, b, sp, fx)
        clips.append([(x[0], x[1], x[2], dict(x[3], peak=p, ev=m)) for x in segs])
        acc += sum((b_ - a__) / sp_ for a__, b_, sp_, _ in segs)
    return clips


def atempo_chain(sp):
    parts = []
    while sp < 0.5: parts.append('atempo=0.5'); sp /= 0.5
    while sp > 2.0: parts.append('atempo=2.0'); sp /= 2.0
    parts.append(f'atempo={sp:.4f}')
    return ','.join(parts)


def build(project, cfg, pname, plat, vp, lang, moments, a, workroot):
    W, H, F = vp['w'], vp['h'], vp.get('fps', 30)
    style = a.style or ('clean' if vp.get('text') == 'none' else 'cartoon')
    with_text = vp.get('text') != 'none' and style == 'cartoon'
    with_audio = vp.get('audio', True)
    total = a.duration or (vp['max_s'] if style == 'clean' else min(vp['max_s'], max(vp.get('min_s', 9), 15)))
    total = max(vp.get('min_s', 1), min(vp['max_s'], total))
    endcard = 1.8 if with_text and text_for(cfg, 'cta', lang) else 0.0
    cover = None
    if plat.get('first_frame_cover'):
        cdir = os.path.join(promo_dir(project), 'out', pname, 'covers')
        ar = W / H
        cands = [os.path.join(cdir, f) for f in os.listdir(cdir)] if os.path.isdir(cdir) else []
        cands = [c for c in cands if c.endswith('.png')]
        if cands:
            from PIL import Image
            cover = min(cands, key=lambda c: abs(Image.open(c).size[0] / Image.open(c).size[1] - ar))
        else:
            print(f'  warn: {pname} wants the cover as first frame; run shots.py --covers first')
    intro = 0.5 if cover else 0.0
    body = total - endcard - intro
    if not moments: die('no moments selected')
    src = {m['take']: probe(os.path.join(promo_dir(project), 'raw', f'{m["take"]}.mp4')) for m in moments}
    clips = plan_clips(moments, vp, style, body, min(p['fps'] for p in src.values()), a)
    if not clips: die('not enough material for this duration')

    fam_path = font_file(cfg)
    work = tempfile.mkdtemp(prefix=f'{pname}_{vp["name"]}_{lang}_', dir=workroot)
    inputs, fc, vlab, alab = [], [], [], []
    fx_amt = style == 'cartoon'
    over = 1.06 if fx_amt else 1.0
    fxp = cfg.get('focus_x', 0.5); fyp = cfg.get('focus_y', 0.5)
    sw, sh = int(math.ceil(W * over / 2) * 2), int(math.ceil(H * over / 2) * 2)
    timeline = 0.0; cut_times, captions = [], []
    idx = 0
    if cover:
        inputs += ['-loop', '1', '-framerate', str(F), '-t', f'{intro:.3f}', '-i', cover]
        fc.append(f'[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={F},setsar=1,format=yuv420p[v{idx}]')
        fc.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{intro:.3f}[a{idx}]')
        vlab.append(f'[v{idx}]'); alab.append(f'[a{idx}]'); idx += 1; timeline += intro
    for ci, clip in enumerate(clips):
        if ci > 0 or cover: cut_times.append(timeline)
        for (s, e, sp, fx) in clip:
            take = fx.get('ev', moments[0])['take'] if fx.get('ev') else moments[0]['take']
            pr = src[take]
            inputs += ['-ss', f'{s:.3f}', '-t', f'{e - s:.3f}', '-i', os.path.join(promo_dir(project), 'raw', f'{take}.mp4')]
            d_out = (e - s) / sp
            ch = [f'[{idx}:v]setpts=(PTS-STARTPTS)/{sp:.4f}', f'fps={F}',
                  f'scale={sw}:{sh}:force_original_aspect_ratio=increase:flags=lanczos']
            if fx.get('impact') and fx_amt:
                amp = int(min(W, H) * 0.012)
                ch.append(f"crop={W}:{H}:x='(iw-ow)*{fxp}+{amp}*sin(t*57)*exp(-t*6)':y='(ih-oh)*{fyp}+{amp}*cos(t*43)*exp(-t*6)'")
            else:
                ch.append(f"crop={W}:{H}:x='(iw-ow)*{fxp}':y='(ih-oh)*{fyp}'")
            if fx.get('first') and fx_amt:
                ch.append(f"zoompan=z='max(1,1.16-0.64*it)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={F}")
                if ci > 0 or cover:
                    ch.append('fade=t=in:st=0:d=0.10:color=white')
            if fx_amt:
                ch.append('eq=saturation=1.16:contrast=1.05')
            ch += ['setsar=1', 'format=yuv420p']
            fc.append(','.join(ch) + f'[v{idx}]')
            if pr['audio']:
                fc.append(f'[{idx}:a]asetpts=PTS-STARTPTS,{atempo_chain(sp)},aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d_out:.3f}[a{idx}]')
            else:
                fc.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{d_out:.3f}[a{idx}]')
            vlab.append(f'[v{idx}]'); alab.append(f'[a{idx}]')
            if fx.get('impact') and with_text and fx.get('ev'):
                txt = caption_for(cfg, fx['ev'], lang)
                if txt: captions.append((timeline + 0.05, txt))
            idx += 1; timeline += d_out
    n = len(vlab)
    fc.append(''.join(v + a_ for v, a_ in zip(vlab, alab)) + f'concat=n={n}:v=1:a=1[cv][ca]')
    body_end = timeline; total_out = body_end + endcard
    vtail = '[cv]'
    if endcard:
        fc.append(f"[cv]tpad=stop_mode=clone:stop_duration={endcard:.2f},gblur=sigma=16:enable='gte(t,{body_end:.2f})',"
                  f"eq=brightness=-0.10:enable='gte(t,{body_end:.2f})'[ce]")
        vtail = '[ce]'
    if with_text:
        safe = vp.get('safe', {'top': 0.06, 'bottom': 0.08, 'side': 0.05})
        maxw = W * (1 - 2 * safe.get('side', 0.05)) * 0.92
        ass = TextLayer(W, H, fam_path, cfg); base = min(W, H)
        hook = text_for(cfg, 'hook', lang)
        if hook:
            lines, size = fit_text(hook, fam_path, base * 0.105, maxw)
            y = int(H * safe['top'] + H * (0.16 if H > W else 0.17))
            ass.pop(0.12 + intro, min(2.2 + intro, body_end), lines, size, W // 2, y, colour=ass.acc)
        for t0, txt in captions:
            if t0 < 2.0 + intro: continue
            lines, size = fit_text(txt, fam_path, base * 0.085, maxw)
            ass.pop(t0, min(t0 + 1.0, body_end), lines, size, W // 2, int(H * (1 - safe['bottom']) - size * 1.4), rot=3)
        if endcard:
            title = text_for(cfg, 'title', lang); cta = text_for(cfg, 'cta', lang)
            lines, size = fit_text(title, fam_path, base * 0.13, maxw)
            ass.pop(body_end + 0.02, total_out, lines, size, W // 2, int(H * 0.42), rot=-2)
            lines, size = fit_text(cta, fam_path, base * 0.075, maxw, max_lines=1)
            ass.pop(body_end + 0.35, total_out, lines, size, W // 2, int(H * 0.60), colour=ass.acc, rot=2, pulse=True)
        cur = vtail
        for k, (d, t0, x, y) in enumerate(ass.render(work, F)):
            inputs += ['-framerate', str(F), '-i', os.path.join(d, '%04d.png')]
            fc.append(f'[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{t0:.3f}/TB[tx{k}]')
            fc.append(f'{cur}[tx{k}]overlay=x={x}:y={y}:eof_action=pass:format=auto[ov{k}]')
            cur = f'[ov{k}]'; idx += 1
        fc.append(f'{cur}format=yuv420p[vout]')
    else:
        fc.append(f'{vtail}null[vout]')
    maps = ['-map', '[vout]']
    if with_audio:
        mix = [f'[ca]apad,atrim=0:{total_out:.3f},volume={cfg.get("game_volume", 0.7)}[g]']; mixl = ['[g]']
        music = a.music or cfg.get('music')
        if music:
            music = music if os.path.isabs(music) else os.path.join(project, music)
            if os.path.exists(music):
                inputs += ['-stream_loop', '-1', '-i', music]
                mix.append(f'[{idx}:a]atrim=0:{total_out:.3f},afade=t=in:d=0.2,afade=t=out:st={max(0, total_out - 1.0):.2f}:d=1.0,'
                           f'volume={cfg.get("music_volume", 0.8)},aresample=48000,aformat=channel_layouts=stereo[m]')
                mixl.append('[m]'); idx += 1
            else:
                print(f'  warn: music {music} not found')
        if style == 'cartoon' and not a.no_sfx:
            sfx = []
            wh = sound('whoosh_in.mp3'); pp = sound('pop.mp3'); win = sound('success_big.mp3') or sound('reward.mp3')
            sfx += [(wh, max(0, t - 0.12), 0.55) for t in cut_times] if wh else []
            sfx += [(pp, t, 0.6) for t, _ in captions] if pp else []
            if win and endcard: sfx.append((win, body_end + 0.05, 0.7))
            for k, (f, t, vol) in enumerate(sfx):
                inputs += ['-i', f]
                mix.append(f'[{idx}:a]adelay={int(t * 1000)}:all=1,volume={vol},aresample=48000,aformat=channel_layouts=stereo[s{k}]')
                mixl.append(f'[s{k}]'); idx += 1
        mix.append(''.join(mixl) + f'amix=inputs={len(mixl)}:normalize=0:duration=first,alimiter=limit=0.95[aout]')
        fc += mix; maps += ['-map', '[aout]']
    else:
        fc.append('[ca]anullsink')
    graph = os.path.join(work, 'graph.txt'); open(graph, 'w').write(';\n'.join(fc))
    odir = os.path.join(promo_dir(project), 'out', pname, lang if with_text else 'all'); os.makedirs(odir, exist_ok=True)
    out = os.path.join(odir, f'{vp["name"]}.mp4')
    enc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(F), '-movflags', '+faststart']
    enc += (['-c:a', 'aac', '-b:a', '192k'] if with_audio else ['-an'])
    cmd = ['ffmpeg', '-y', '-v', 'error'] + inputs + ['-filter_complex_script', 'graph.txt'] + maps + enc + ['-t', f'{total_out:.3f}', out]
    cwd = os.getcwd(); os.chdir(work)
    try:
        run(cmd)
        pr = probe(out)
        if pr['size_mb'] > vp.get('max_mb', 1e9):
            br = int(vp['max_mb'] * 8e6 * 0.93 / max(pr['dur'], 1) - (192000 if with_audio else 0))
            enc2 = [x for x in enc]; i = enc2.index('-crf'); enc2[i:i + 2] = ['-b:v', str(br), '-maxrate', str(br), '-bufsize', str(br * 2)]
            run(['ffmpeg', '-y', '-v', 'error'] + inputs + ['-filter_complex_script', 'graph.txt'] + maps + enc2 + ['-t', f'{total_out:.3f}', out])
            pr = probe(out)
    finally:
        os.chdir(cwd)
    rev = os.path.join(promo_dir(project), 'review'); os.makedirs(rev, exist_ok=True)
    sheet = os.path.join(rev, f'{pname}_{vp["name"]}_{lang if with_text else "all"}.jpg')
    cols = 4 if W >= H else 6
    run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-vf', f'fps={8 / max(pr["dur"], 1):.4f},scale={480 if W >= H else 240}:-2,tile={cols}x{math.ceil(8 / cols)}',
         '-frames:v', '1', sheet])
    problems = []
    if pr['w'] != W or pr['h'] != H: problems.append(f'size {pr["w"]}x{pr["h"]}')
    if pr['dur'] < vp.get('min_s', 0) - 0.2: problems.append(f'too short {pr["dur"]:.1f}s < {vp["min_s"]}s (need more moments)')
    if pr['dur'] > vp['max_s'] + 0.2: problems.append(f'too long {pr["dur"]:.1f}s')
    if pr['size_mb'] > vp.get('max_mb', 1e9): problems.append(f'{pr["size_mb"]:.1f} MB > {vp["max_mb"]} MB')
    if not with_audio and pr['audio']: problems.append('has audio but preset is muted')
    shutil.rmtree(work, ignore_errors=True)
    return out, pr, sheet, problems, len(clips), style


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--platform', required=True)
    ap.add_argument('--video', help='preset name inside the platform (default: all videos of the platform)')
    ap.add_argument('--lang')
    ap.add_argument('--moments', help='ids from moments.json in the wanted order')
    ap.add_argument('--style', choices=['cartoon', 'clean'])
    ap.add_argument('--duration', type=float)
    ap.add_argument('--music')
    ap.add_argument('--bpm', type=float, default=0)
    ap.add_argument('--no-slowmo', action='store_true')
    ap.add_argument('--no-sfx', action='store_true')
    a = ap.parse_args()
    need_ffmpeg()
    project = os.path.abspath(a.project); cfg = load_config(project)
    if not a.bpm: a.bpm = cfg.get('bpm', 0)
    plat = platform(a.platform)
    vids = [v for v in plat.get('videos', []) if not a.video or v['name'] == a.video]
    if not vids: die(f'no video preset {a.video} in {a.platform}')
    ms = load_moments(project)
    if a.moments:
        by = {m['id']: m for m in ms}; ms = [by[int(i)] for i in a.moments.split(',') if int(i) in by]
    ms = order_moments(ms, bool(a.moments))
    workroot = os.path.join(promo_dir(project), '.work'); os.makedirs(workroot, exist_ok=True)
    for vp in vids:
        needs_text = vp.get('text') != 'none' and (a.style or 'cartoon') == 'cartoon'
        for lang in (langs_arg(cfg, a.lang) if needs_text else ['all']):
            out, pr, sheet, probs, nclips, style = build(project, cfg, a.platform, plat, vp, lang, ms, a, workroot)
            flag = 'OK ' if not probs else 'FIX'
            print(f'{flag} {os.path.relpath(out, project)}: {pr["w"]}x{pr["h"]} {pr["dur"]:.1f}s {pr["size_mb"]:.1f}MB '
                  f'audio={pr["audio"]} clips={nclips} style={style} | sheet {os.path.relpath(sheet, project)}'
                  + (' | ' + '; '.join(probs) if probs else ''))
    shutil.rmtree(workroot, ignore_errors=True)


if __name__ == '__main__':
    main()
