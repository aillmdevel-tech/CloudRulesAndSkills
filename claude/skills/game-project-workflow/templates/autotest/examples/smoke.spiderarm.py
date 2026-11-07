"""Smoke test: does the game work (not how it looks). Usage: npm run smoke [-- --dev] [--no-build]
Builds the game, serves it (vite preview; --dev = vite dev), plays a ~1 min scenario, one line per step,
exit code 0 = PASS / 1 = FAIL. Screenshots: tools/out/smoke/."""
import os, sys, time, argparse
sys.path.insert(0, os.path.dirname(__file__))
from lib.harness import ROOT, build, Server, Session, sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--dev', action='store_true'); ap.add_argument('--no-build', action='store_true'); ap.add_argument('--url')
a = ap.parse_args()
OUT = os.path.join(ROOT, 'tools', 'out', 'smoke')
results = []


def step(name, ok, why=''):
    results.append((name, bool(ok)))
    print(f"{'✓' if ok else '✗'} {name}: {why}", flush=True)


def callout_text(s):
    return s.pg.evaluate("() => [...document.querySelectorAll('.callout')].map(e => e.textContent).join('|')")


def run(url):
    with sync_playwright() as pw:
        s = Session(pw, url)
        try:
            # 1. load
            s.load()
            sp = s.pg.evaluate('() => ({ init: !!window.bridge?.isInitialized, msgs: window.__spy.msgs.map(m => m[0]), ms: window.__spy.msgs.map(m => m[2]) })')
            step('load', sp['init'] and 'game_ready' in sp['msgs'] and not s.errors,
                 f"bridge init={sp['init']}, game_ready={'game_ready' in sp['msgs']}, console errors={len(s.errors)}")
            s.prep(level=6)
            spawn = s.st()
            # 2. lobby
            a = s.st(); time.sleep(1.0); b = s.st()
            s.tp(spawn['x'], spawn['y'], spawn['z'], settle=1.0)
            p0 = s.st(); s.pg.keyboard.down('KeyW'); time.sleep(1.2); p1 = s.st(); s.pg.keyboard.up('KeyW')
            moved = ((p1['x'] - p0['x']) ** 2 + (p1['z'] - p0['z']) ** 2) ** 0.5
            step('lobby', b['s'] == 'grounded' and abs(b['y'] - a['y']) < 0.5 and moved > 3 and p1['y'] > p0['y'] - 3,
                 f"state={b['s']}, dy_idle={b['y'] - a['y']:.2f}, W moved {moved:.1f} studs")
            s.shot(os.path.join(OUT, '1_lobby.png'))
            # 3. trainer
            st = s.pg.evaluate("() => { const t = window.__game.trainers.stations.filter(x => x.rebirths === 0).sort((p, q) => p.mult - q.mult)[0]; if (!t) return null;"
                               " const c = t.zone.getCenter(new t.zone.min.constructor()); return { x: c.x, y: t.zone.min.y + 2, z: c.z, mult: t.mult }; }")
            if not st: step('trainer', False, 'no free trainer station found')
            else:
                s.tp(st['x'], st['y'], st['z'], settle=0.5)
                t0 = time.time(); docked = False
                while time.time() - t0 < 4 and not docked: docked = s.st()['docked']; time.sleep(0.1)
                x0 = s.st()['xp']; time.sleep(4); x1 = s.st()
                step('trainer', docked and x1['xp'] > x0, f"docked={docked}, XP {x0} → {x1['xp']} in 4 s (x{st['mult']})")
                s.shot(os.path.join(OUT, '2_trainer.png'))
            # 4. stage 1
            s.tp(0, 10, -200, settle=1.0)
            g0 = s.st()
            s.pg.keyboard.down('KeyW'); s.pg.keyboard.down('Space')
            t0 = time.time(); climbing = False; top = g0
            while time.time() - t0 < 3.5:
                top = s.st(); climbing = climbing or top['s'] == 'climbing'
                if top['y'] > 35: break
                time.sleep(0.05)
            s.pg.keyboard.up('Space'); s.pg.keyboard.up('KeyW')
            s.shot(os.path.join(OUT, '3_stage1.png'))
            time.sleep(1.2); hang = s.st()
            step('stage1_grab', climbing and top['y'] > g0['y'] + 20, f"climbing={climbing}, height {g0['y']:.0f} → {top['y']:.0f}")
            step('stage1_grip', hang['grip'] < hang['gripMax'] - 0.5 or top['grip'] < top['gripMax'] - 0.5,
                 f"grip {top['gripMax']:.0f} → {min(top['grip'], hang['grip']):.1f}")
            # 5. fall → YOU FELL → lobby
            kz = s.fall()
            if not kz: step('fall', False, 'no kill zone available'); step('return_lobby', False, 'skipped')
            else:
                t0 = time.time(); txt = ''
                while time.time() - t0 < 5 and 'FELL' not in txt: txt = callout_text(s); time.sleep(0.1)
                step('fall', 'FELL' in txt, f"callout='{txt[:40]}' after {time.time() - t0:.1f} s")
                s.shot(os.path.join(OUT, '4_fell.png'))
                time.sleep(2.5); e = s.st()
                d = ((e['x'] - spawn['x']) ** 2 + (e['z'] - spawn['z']) ** 2) ** 0.5
                step('return_lobby', d < 80 and e['s'] in ('grounded', 'airborne'), f"{d:.0f} studs from spawn, state={e['s']}")
            # 6. sound
            snd = s.pg.evaluate("() => ({ ctx: window.__game.sfx.context()?.state })")
            urls = [u for u, c in s.responses if c == 200]
            music = any('sherwood' in u for u in urls); steps = sum('step_' in u for u in urls)
            step('sound', snd['ctx'] == 'running' and music and steps > 0, f"AudioContext={snd['ctx']}, music loaded={music}, step sounds={steps}")
            # 7. console
            time.sleep(0.5)
            step('console', not s.errors, f"{len(s.errors)} errors" + (': ' + s.errors[0][:120] if s.errors else ''))
        finally:
            s.close()
    return len(s.errors)


if not a.url and not a.no_build and not a.dev: build()
t0 = time.time()
if a.url: nerr = run(a.url)
else:
    with Server(dev=a.dev) as srv: nerr = run(srv.url)
ok = sum(1 for _, r in results if r)
print(f"console errors: {nerr}")
print(('PASS' if ok == len(results) else f'FAIL ({ok}/{len(results)})') + f'  [{time.time() - t0:.0f} s]')
sys.exit(0 if ok == len(results) else 1)
