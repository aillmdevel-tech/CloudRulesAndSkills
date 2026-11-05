#!/usr/bin/env python3
"""Compare a reference image with a game capture. Pillow only.

usage: compare_images.py REF SHOT OUTDIR [--crop x,y,w,h] [--crop-shot x,y,w,h] [--amp 4]

Writes OUTDIR/side_by_side.png, diff.png (amplified abs difference), blend.png (50/50 overlay)
and prints colour/brightness/contrast/saturation stats, per-quadrant brightness and dominant colours.
SHOT is resized to REF's size; aspect-ratio mismatch is reported (fix the camera/viewport first).
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except ImportError:
    sys.exit("Pillow missing: python3 -m pip install --user Pillow")


def crop(im, spec):
    if not spec:
        return im
    x, y, w, h = (int(v) for v in spec.split(","))
    return im.crop((x, y, x + w, y + h))


def stats(im):
    st = ImageStat.Stat(im)
    gray = ImageStat.Stat(im.convert("L"))
    sat = ImageStat.Stat(im.convert("HSV").split()[1])
    return {"mean_rgb": tuple(round(v) for v in st.mean), "brightness": round(gray.mean[0], 1),
            "contrast": round(gray.stddev[0], 1), "saturation": round(sat.mean[0], 1)}


def quadrants(im):
    g = im.convert("L")
    w, h = g.size
    out = []
    for j in range(3):
        row = []
        for i in range(3):
            box = (i * w // 3, j * h // 3, (i + 1) * w // 3, (j + 1) * h // 3)
            row.append(round(ImageStat.Stat(g.crop(box)).mean[0]))
        out.append(row)
    return out


def dominant(im, n=6):
    q = im.resize((160, int(160 * im.height / im.width) or 1)).quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    return [("#%02x%02x%02x" % tuple(pal[i * 3:i * 3 + 3]), round(100 * c / total)) for c, i in counts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("shot")
    ap.add_argument("outdir")
    ap.add_argument("--crop")
    ap.add_argument("--crop-shot")
    ap.add_argument("--amp", type=float, default=4)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    ref = crop(Image.open(a.ref).convert("RGB"), a.crop)
    shot = crop(Image.open(a.shot).convert("RGB"), a.crop_shot or a.crop)
    ar_r, ar_s = ref.width / ref.height, shot.width / shot.height
    if abs(ar_r - ar_s) > 0.02:
        print(f"WARNING aspect mismatch: ref {ref.width}x{ref.height} ({ar_r:.3f}) vs shot "
              f"{shot.width}x{shot.height} ({ar_s:.3f}) — match the viewport before judging composition")
    shot_r = shot.resize(ref.size, getattr(Image, "Resampling", Image).LANCZOS)

    lab = 28
    sbs = Image.new("RGB", (ref.width * 2 + 10, ref.height + lab), (20, 20, 20))
    sbs.paste(ref, (0, lab))
    sbs.paste(shot_r, (ref.width + 10, lab))
    d = ImageDraw.Draw(sbs)
    d.text((8, 6), "REFERENCE", fill=(255, 220, 80))
    d.text((ref.width + 18, 6), "GAME", fill=(120, 220, 255))
    sbs.save(os.path.join(a.outdir, "side_by_side.png"))

    diff = ImageChops.difference(ref, shot_r)
    diff.point(lambda v: min(255, int(v * a.amp))).save(os.path.join(a.outdir, "diff.png"))
    Image.blend(ref, shot_r, 0.5).save(os.path.join(a.outdir, "blend.png"))
    mean_diff = sum(ImageStat.Stat(diff).mean) / 3

    sr, ss = stats(ref), stats(shot_r)
    print(f"{'':12}{'REFERENCE':>22}{'GAME':>22}")
    for k in sr:
        print(f"{k:12}{str(sr[k]):>22}{str(ss[k]):>22}")
    print(f"mean abs diff (0-255): {mean_diff:.1f}")
    print("brightness 3x3 (ref | game):")
    for rr, gg in zip(quadrants(ref), quadrants(shot_r)):
        print(f"   {rr}  |  {gg}")
    print("dominant colours ref :", dominant(ref))
    print("dominant colours game:", dominant(shot_r))
    print("written:", ", ".join(os.path.join(a.outdir, f) for f in ("side_by_side.png", "diff.png", "blend.png")))


if __name__ == "__main__":
    main()
