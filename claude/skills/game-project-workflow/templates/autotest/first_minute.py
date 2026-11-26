"""First-minute check (GameFactory/DESIGN/FIRST_MINUTE.md): a fresh player's first 120 s as frames + funnel.
Usage (project): python3 tools/first_minute.py [--url URL] [--dev] [--no-build] [--secs 120]
Actions: tools/first_minute.actions.json = [{"t": 2, "do": "click", "x": 640, "y": 360},
  {"t": 4, "do": "hold", "key": "KeyW", "ms": 1500}, {"t": 8, "do": "key", "key": "KeyE"}] — like a newbie, no dev commands.
Output: tools/out/first_minute/{t###.png, sheet.jpg, report.json}. Then the lead runs the cold-read subagent on sheet.jpg."""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from harness import ROOT, Server, Session, build, sync_playwright

MARKS = [1, 3, 10, 20, 30, 45, 60, 90, 120]
ap = argparse.ArgumentParser()
ap.add_argument('--url'); ap.add_argument('--dev', action='store_true'); ap.add_argument('--no-build', action='store_true')
ap.add_argument('--secs', type=int, default=120)
a = ap.parse_args()
marks = [m for m in MARKS if m <= a.secs]
out = os.path.join(ROOT, 'tools', 'out', 'first_minute'); os.makedirs(out, exist_ok=True)
acts_p = os.path.join(ROOT, 'tools', 'first_minute.actions.json')
acts = sorted(json.load(open(acts_p)), key=lambda x: x['t']) if os.path.exists(acts_p) else []
if not acts: print('note: no tools/first_minute.actions.json — only a first click is made')
if not a.url and not a.dev and not a.no_build: build()


def do(pg, x):
    k = x['do']
    if k == 'click': pg.mouse.click(x.get('x', 640), x.get('y', 360))
    elif k in ('key', 'hold'):
        pg.keyboard.down(x['key']); time.sleep(x.get('ms', 120) / 1000); pg.keyboard.up(x['key'])
    elif k == 'move': pg.mouse.move(x['x'], x['y'])
    elif k == 'drag':
        pg.mouse.move(x['x'], x['y']); pg.mouse.down(); pg.mouse.move(x['x2'], x['y2'], steps=12); pg.mouse.up()


def go(url):
    rep = {'url': url, 'frames': [], 'funnel': None, 'errors': []}
    with sync_playwright() as pw:
        s = Session(pw, url)   # fresh context = no save, like a new player
        try:
            t0 = time.time(); s.pg.goto(url)
            try:
                s.pg.wait_for_function('window.__game && (window.__game.funnel ? window.__game.funnel.has("first_frame") : true)', timeout=60000)
            except Exception: pass
            rep['load_s'] = round(time.time() - t0, 1)
            t0 = time.time()
            if not acts or acts[0]['t'] > 1.5: s.pg.mouse.click(640, 360)
            todo, mi = list(acts), 0
            while mi < len(marks):
                now = time.time() - t0
                if todo and todo[0]['t'] <= now: do(s.pg, todo.pop(0)); continue
                if marks[mi] <= now:
                    p = os.path.join(out, f't{marks[mi]:03d}.png'); s.shot(p); rep['frames'].append([marks[mi], p]); mi += 1; continue
                time.sleep(0.05)
            rep['funnel'] = s.pg.evaluate('() => window.__game && window.__game.funnel ? window.__game.funnel.events : null')
            rep['errors'] = s.errors[:10]
        finally:
            s.close()
    return rep


if a.url: rep = go(a.url)
else:
    with Server(dev=a.dev) as srv: rep = go(srv.url)
try:
    from PIL import Image, ImageDraw
    th = [Image.open(p).convert('RGB').resize((640, 360)) for _, p in rep['frames']]
    cols = 3; rows = (len(th) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 640, rows * 380), (20, 20, 28)); d = ImageDraw.Draw(sheet)
    for i, (im, (t, _)) in enumerate(zip(th, rep['frames'])):
        x, y = (i % cols) * 640, (i // cols) * 380; sheet.paste(im, (x, y + 20)); d.text((x + 8, y + 4), f'{t} s', fill=(255, 220, 80))
    sheet.save(os.path.join(out, 'sheet.jpg'), quality=82); rep['sheet'] = os.path.join(out, 'sheet.jpg')
except ImportError:
    print('note: Pillow missing — no sheet.jpg')
json.dump(rep, open(os.path.join(out, 'report.json'), 'w'), indent=1, ensure_ascii=False)
ev = {e['name']: e['t'] for e in (rep['funnel'] or [])}
print(f"load {rep.get('load_s')} s · frames {len(rep['frames'])} · console errors {len(rep['errors'])}")
for k in ('first_frame', 'first_input', 'first_action', 'first_result', 'first_reward', 'next_goal_seen', 'loop_done'):
    print(f'  {k:15s} {ev.get(k, "—")}')
print('sheet:', rep.get('sheet', '—'))
