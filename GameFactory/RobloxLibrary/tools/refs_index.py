"""Build refs/_palettes.json and the frame list for REFS.md.
usage: python3 refs_index.py <RobloxLibrary> [FRAMES_DIR]
FRAMES_DIR = dir with <videoId>/palette.json from the YouTube grab (optional: palettes are kept from the last run)."""
import sys, os, glob, json
lib = sys.argv[1]; fr = sys.argv[2] if len(sys.argv) > 2 else None
out = os.path.join(lib, 'refs', '_palettes.json')
pal = json.load(open(out)) if os.path.exists(out) else {}
for d in sorted(glob.glob(os.path.join(lib, 'refs', '*/'))):
    slug = os.path.basename(d[:-1]); files = sorted(os.path.basename(f) for f in glob.glob(d + '*.jpg'))
    ids = sorted({f.rsplit('_', 2)[0] for f in files if not f.startswith('alex_')})
    if fr:
        ps = [json.load(open(p)) for i in ids for p in [os.path.join(fr, i, 'palette.json')] if os.path.exists(p)]
        if ps:
            cols = {}
            for p in ps:
                for c, w in p['colors']: cols[c] = cols.get(c, 0) + w / len(ps)
            pal[slug] = {'videos': ids, 'brightness': round(sum(p['brightness'] for p in ps) / len(ps)),
                         'saturation': round(sum(p['saturation'] for p in ps) / len(ps)),
                         'colors': [c for c, _ in sorted(cols.items(), key=lambda x: -x[1])[:6]]}
    p = pal.get(slug, {})
    print(f"| `{slug}` | {len(files)} | {p.get('brightness', '—')} / {p.get('saturation', '—')}% | {' '.join(p.get('colors', [])[:5])} | {', '.join(f for f in files if 'ui' in f or 'hud' in f)[:120]} |")
json.dump(pal, open(out, 'w'), indent=1)
