"""Release archive for a platform: dist/ -> release/<name>-<platform>-<date>.zip (index.html at the root).
Usage: python3 tools/pack.py playgama|crazygames   (npm run pack:<platform> builds first). From playgama-crazy-publisher."""
import datetime, json, os, re, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIST = os.path.join(ROOT, 'dist')
plat = sys.argv[1] if len(sys.argv) > 1 else 'playgama'
name = json.load(open(os.path.join(ROOT, 'package.json'))).get('name', 'game')
if not os.path.exists(os.path.join(DIST, 'index.html')): sys.exit('dist/index.html missing: build first')
html = open(os.path.join(DIST, 'index.html'), encoding='utf-8').read()
if plat == 'playgama':
    first = re.search(r'<script\b[^>]*>', html.split('</head>')[0])
    if not (first and 'playgama-bridge.js' in first.group(0)): sys.exit('playgama build expected: playgama-bridge.js must be the first <script>')
    json.load(open(os.path.join(DIST, 'playgama-bridge-config.json')))
elif 'playgama-bridge' in html:
    sys.exit('crazygames build must not carry Playgama Bridge')
files, bad = [], []
for r, _, fs in os.walk(DIST):
    for f in fs:
        if f == '.DS_Store' or f.endswith('.map'): continue
        rel = os.path.relpath(os.path.join(r, f), DIST)
        if not re.fullmatch(r'[A-Za-z0-9._\-/]+', rel): bad.append(rel)
        files.append(rel)
if bad: sys.exit('non-latin file names: ' + ', '.join(bad[:5]))
os.makedirs(os.path.join(ROOT, 'release'), exist_ok=True)
out = os.path.join(ROOT, 'release', f'{name}-{plat}-{datetime.date.today():%Y%m%d}.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for rel in sorted(files): z.write(os.path.join(DIST, rel), rel)
raw = sum(os.path.getsize(os.path.join(DIST, f)) for f in files)
print(f'{out}\n{len(files)} files, {raw / 1e6:.1f} MB -> zip {os.path.getsize(out) / 1e6:.1f} MB')
