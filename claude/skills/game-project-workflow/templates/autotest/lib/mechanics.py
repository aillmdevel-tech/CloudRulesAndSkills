"""Mechanic tests: setup -> act like a player -> wait until the game state proves the result.
Usage (project): python3 tools/mechanics.py [--only name,name] [--url URL] [--dev] [--no-build]
Define MECHANICS in tools/mechanics.py (copy of examples/mechanics.example.py) and call run(MECHANICS).
Each test: dict(name, setup=js, act=[steps], expect=js predicate, timeout=s, shot=True)
  steps: ('key', 'KeyE', ms) press/hold a key ms · ('hold', 'Space', ms) · ('click', x, y) · ('js', code) · ('wait', s)
Waits on state, never on fixed sleeps (LESSONS/testing.md). Exit 1 on any FAIL."""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from harness import ROOT, Server, Session, build, sync_playwright


def _act(pg, step):
    kind = step[0]
    if kind in ('key', 'hold'):
        pg.keyboard.down(step[1]); time.sleep((step[2] if len(step) > 2 else 120) / 1000); pg.keyboard.up(step[1])
    elif kind == 'click': pg.mouse.click(step[1], step[2])
    elif kind == 'js': pg.evaluate(f'() => {{ {step[1]} }}')
    elif kind == 'wait': time.sleep(step[1])
    else: raise ValueError(f'unknown step {step}')


def run(tests):
    ap = argparse.ArgumentParser()
    ap.add_argument('--only'); ap.add_argument('--url'); ap.add_argument('--dev', action='store_true')
    ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    only = set(a.only.split(',')) if a.only else None
    tests = [t for t in tests if not only or t['name'] in only]
    out = os.path.join(ROOT, 'tools', 'out', 'mechanics'); os.makedirs(out, exist_ok=True)
    if not a.url and not a.dev and not a.no_build: build()
    results = []

    def go(url):
        with sync_playwright() as pw:
            s = Session(pw, url)
            try:
                s.load()
                s.pg.mouse.click(640, 360)  # first user gesture
                for t in tests:
                    t0 = time.time(); ok, err = False, ''
                    try:
                        if t.get('setup'): s.pg.evaluate(f"() => {{ {t['setup']} }}")
                        for step in t.get('act', []): _act(s.pg, step)
                        s.pg.wait_for_function(f"() => !!({t['expect']})", timeout=int(t.get('timeout', 5) * 1000))
                        ok = True
                    except Exception as e:
                        err = str(e).splitlines()[0][:160]
                    if t.get('shot', True) or not ok: s.shot(os.path.join(out, f"{t['name']}.png"))
                    results.append((t['name'], ok, round(time.time() - t0, 1), err))
                    print(('PASS' if ok else 'FAIL'), t['name'], f'{results[-1][2]}s', err)
                if s.errors: print('console errors:', *s.errors[:5], sep='\n  ')
            finally:
                s.close()

    if a.url: go(a.url)
    else:
        with Server(dev=a.dev) as srv: go(srv.url)
    fails = [r for r in results if not r[1]]
    print(f'mechanics: {len(results) - len(fails)}/{len(results)} PASS · shots tools/out/mechanics/')
    raise SystemExit(1 if fails else 0)
