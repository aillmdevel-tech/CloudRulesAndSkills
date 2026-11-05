#!/usr/bin/env python3
"""Frame extraction and contact sheets for gameplay reference videos.

Commands:
  info   VIDEO
  sample VIDEO OUTDIR --every SEC [--start S] [--end S] [--width W]
  scenes VIDEO OUTDIR [--threshold 0.3] [--width W]
  burst  VIDEO OUTDIR --start S --end S [--fps 15] [--width W]
  sheet  FRAMEDIR OUT.jpg [--cols 4] [--thumb 480]

Frame files are named t_<seconds>.jpg (e.g. t_0012.500.jpg) so the timecode travels with the frame.
Requires ffmpeg/ffprobe on PATH. Pillow is optional (used for labelled sheets).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"{tool} not found on PATH")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def fmt_tc(sec):
    m, s = divmod(float(sec), 60)
    h, m = divmod(int(m), 60)
    return f"{h:02d}:{m:02d}:{s:06.3f}" if h else f"{m:02d}:{s:06.3f}"


def frame_name(sec):
    return f"t_{float(sec):08.3f}.jpg"


def probe(video):
    need("ffprobe")
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", video])
    if r.returncode:
        sys.exit(r.stderr.strip() or "ffprobe failed")
    return json.loads(r.stdout)


def cmd_info(a):
    d = probe(a.video)
    fmt = d.get("format", {})
    print(f"file:     {a.video}")
    print(f"duration: {fmt_tc(float(fmt.get('duration', 0)))} ({float(fmt.get('duration', 0)):.2f}s)")
    print(f"size:     {int(fmt.get('size', 0)) / 1e6:.1f} MB")
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            num, den = (s.get("avg_frame_rate", "0/1").split("/") + ["1"])[:2]
            fps = float(num) / float(den) if float(den) else 0
            print(f"video:    {s.get('width')}x{s.get('height')} {s.get('codec_name')} {fps:.2f} fps, frames~{s.get('nb_frames', '?')}")
        elif s.get("codec_type") == "audio":
            print(f"audio:    {s.get('codec_name')} {s.get('sample_rate')} Hz {s.get('channels')} ch")


def duration(video):
    return float(probe(video).get("format", {}).get("duration", 0))


def grab(video, sec, out, width):
    vf = f"scale={width}:-2" if width else "null"
    r = run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sec:.3f}", "-i", video, "-frames:v", "1",
             "-vf", vf, "-q:v", "3", out])
    return r.returncode == 0 and os.path.exists(out)


def cmd_sample(a):
    need("ffmpeg")
    os.makedirs(a.outdir, exist_ok=True)
    end = a.end if a.end is not None else duration(a.video)
    t, n = a.start, 0
    while t < end:
        if grab(a.video, t, os.path.join(a.outdir, frame_name(t)), a.width):
            n += 1
        t += a.every
    print(f"{n} frames -> {a.outdir}")


def cmd_burst(a):
    a.every = 1.0 / a.fps
    cmd_sample(a)


def cmd_scenes(a):
    need("ffmpeg")
    os.makedirs(a.outdir, exist_ok=True)
    r = run(["ffmpeg", "-v", "info", "-i", a.video, "-vf",
             f"select='gt(scene,{a.threshold})',showinfo", "-an", "-f", "null", "-"])
    times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
    times = [0.0] + times
    n = 0
    for t in times:
        if grab(a.video, t, os.path.join(a.outdir, frame_name(t)), a.width):
            n += 1
    print(f"{n} scene frames (threshold {a.threshold}) -> {a.outdir}")
    for t in times:
        print(f"  {fmt_tc(t)}  {frame_name(t)}")


def cmd_sheet(a):
    files = sorted(f for f in os.listdir(a.framedir) if f.lower().endswith((".jpg", ".png")))
    if not files:
        sys.exit("no frames in " + a.framedir)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        need("ffmpeg")
        rows = (len(files) + a.cols - 1) // a.cols
        r = run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i",
                 os.path.join(a.framedir, "*.jpg"), "-vf",
                 f"scale={a.thumb}:-2,tile={a.cols}x{rows}", "-frames:v", "1", a.out])
        print(("sheet (no labels, Pillow missing) -> " + a.out) if not r.returncode else r.stderr)
        return
    thumbs = []
    for f in files:
        im = Image.open(os.path.join(a.framedir, f)).convert("RGB")
        im.thumbnail((a.thumb, a.thumb * 4))
        m = re.match(r"t_([0-9.]+)\.", f)
        label = fmt_tc(float(m.group(1))) if m else f
        thumbs.append((im, label))
    w = max(t[0].width for t in thumbs)
    h = max(t[0].height for t in thumbs)
    pad, lab = 6, 22
    rows = (len(thumbs) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (a.cols * (w + pad) + pad, rows * (h + lab + pad) + pad), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = None
    for p in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "C:/Windows/Fonts/consola.ttf"):
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 16)
                break
            except OSError:
                pass
    font = font or ImageFont.load_default()
    for i, (im, label) in enumerate(thumbs):
        x = pad + (i % a.cols) * (w + pad)
        y = pad + (i // a.cols) * (h + lab + pad)
        draw.text((x + 2, y + 2), label, fill=(255, 220, 80), font=font)
        sheet.paste(im, (x, y + lab))
    sheet.save(a.out, quality=88)
    print(f"sheet {len(thumbs)} frames {a.cols} cols -> {a.out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("info"); s.add_argument("video"); s.set_defaults(fn=cmd_info)
    for name, fn in (("sample", cmd_sample), ("burst", cmd_burst), ("scenes", cmd_scenes)):
        s = sp.add_parser(name); s.add_argument("video"); s.add_argument("outdir")
        s.add_argument("--width", type=int, default=960)
        if name == "sample":
            s.add_argument("--every", type=float, required=True)
            s.add_argument("--start", type=float, default=0.0)
            s.add_argument("--end", type=float)
        if name == "burst":
            s.add_argument("--start", type=float, required=True)
            s.add_argument("--end", type=float, required=True)
            s.add_argument("--fps", type=float, default=15)
        if name == "scenes":
            s.add_argument("--threshold", type=float, default=0.3)
        s.set_defaults(fn=fn)
    s = sp.add_parser("sheet"); s.add_argument("framedir"); s.add_argument("out")
    s.add_argument("--cols", type=int, default=4); s.add_argument("--thumb", type=int, default=480)
    s.set_defaults(fn=cmd_sheet)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
