"""TEMPLATE from Snack Toss Zoo: copy to <game>/tools/i18n_audit.py and rewrite play() and ALLOW for the new game
(the hook that records DOM + canvas text and the ru/tr/es/pt checks are generic).
Runtime localisation audit (2026-11-26): plays the same scenario in every language and records every string the game
shows — DOM text, placeholder/title/aria-label, and canvas fillText/strokeText (3D signs, labels) — then flags:
  ru / tr : any Latin word of 2+ letters (outside the allow-list)
  es / pt : strings identical to the English run that contain a real word (outside the allow-list)
Usage: resource-run /usr/local/bin/python3 tools/i18n_audit.py [--no-build] [--langs en,ru,es,pt,tr]
Report: tools/out/i18n_audit/REPORT.md (+ raw <lang>.json)."""
import argparse, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from lib.harness import ROOT, Server, Session, build, sync_playwright

ap = argparse.ArgumentParser(); ap.add_argument('--no-build', action='store_true'); ap.add_argument('--langs', default='en,ru,es,pt,tr')
a = ap.parse_args()
OUT = os.path.join(ROOT, 'tools', 'out', 'i18n_audit'); os.makedirs(OUT, exist_ok=True)

HOOK = r"""(() => {
  const S = window.__txt = new Map();
  const add = (s, src) => { if (s == null) return; s = String(s).replace(/\s+/g, ' ').trim(); if (!s || s.length > 300) return; if (!S.has(s)) S.set(s, src); };
  for (const fn of ['fillText', 'strokeText']) {
    const o = CanvasRenderingContext2D.prototype[fn];
    CanvasRenderingContext2D.prototype[fn] = function (t, ...r) { add(t, 'canvas'); return o.call(this, t, ...r); };
    if (window.OffscreenCanvasRenderingContext2D) { const p = OffscreenCanvasRenderingContext2D.prototype, q = p[fn]; p[fn] = function (t, ...r) { add(t, 'canvas'); return q.call(this, t, ...r); }; }
  }
  const scan = () => {
    if (!document.body) return;
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      const el = n.parentElement; if (!el || el.closest('script,style,.adm,[data-dev]')) continue;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      add(n.nodeValue, 'dom');
    }
    for (const el of document.querySelectorAll('[placeholder],[title],[aria-label]'))
      for (const k of ['placeholder', 'title', 'aria-label']) if (el.getAttribute(k)) add(el.getAttribute(k), 'attr');
  };
  setInterval(scan, 250);
  window.__txtDump = () => { scan(); return [...S.entries()]; };
})();"""


def wait(s, js, sec):
    t0 = time.time()
    while time.time() - t0 < sec:
        if s.pg.evaluate(js): return True
        time.sleep(0.1)
    return False


def throw(s, meter):
    s.pg.evaluate(f"() => {{ window.__game.flow.forceMeter = {meter}; }}")
    s.tp(4, -36)
    s.pg.keyboard.down('KeyW'); wait(s, "() => window.__game.flow.phase === 'aim'", 4); s.pg.keyboard.up('KeyW')
    time.sleep(0.9); s.pg.mouse.click(640, 400)
    wait(s, "() => window.__game.flow.phase === 'result'", 45)
    time.sleep(2.5); s.pg.mouse.click(640, 400)
    wait(s, "() => window.__game.flow.phase === 'idle' && window.__game.player.controllable", 8); time.sleep(1.5)


def run(url, lang):
    with sync_playwright() as pw:
        s = Session(pw, url + f'?lang={lang}', init_script=HOOK)
        try:
            s.load(); time.sleep(2)              # fresh save: tutorial texts
            s.prep(); time.sleep(2)
            s.tp(-50, -6); s.pg.keyboard.down('KeyW'); time.sleep(1.5); s.pg.keyboard.up('KeyW'); time.sleep(1)
            # bar pad + training
            s.pg.evaluate("() => { const st = window.__game.session.state; st.money = 100n; }")
            pad = s.pg.evaluate("() => { const c = window.__game.zones.barUpgrade.getCenter(new window.__game.THREE.Vector3()); return [c.x, c.z]; }")
            s.tp(pad[0], pad[1]); time.sleep(1.2); s.pg.keyboard.press('KeyE'); time.sleep(1)
            s.tp(-66, -8, settle=0.3); wait(s, '() => window.__game.training.active', 3); time.sleep(4)
            try: s.pg.click('.trn-stop', timeout=2000)
            except Exception: pass
            time.sleep(1)
            # throws: short, mid, far (several biomes, near-miss lines, level up)
            for lvl, m in ((None, 0.5), (60, 0.95), (400, 0.99)):
                if lvl: s.pg.evaluate(f"() => {{ window.__game.session.state.level = {lvl}; window.__game.session.emit('change'); }}")
                throw(s, m)
            # every HUD panel and every tab/button inside it (no purchases: clicks only on tabs)
            s.pg.evaluate("() => { window.__game.session.state.money = 10n ** 15n; window.__game.session.emit('change'); }")
            huds = s.pg.evaluate("() => [...document.querySelectorAll('.hud-btn[data-hud]')].map(b => b.dataset.hud)")
            for h in huds:
                s.click_hud(h); time.sleep(1.2)
                tabs = s.pg.evaluate("() => [...document.querySelectorAll('.ui-panel [role=tab], .ui-panel .tab, .ui-panel [data-tab]')].length")
                for i in range(min(tabs, 12)):
                    s.pg.evaluate(f"() => [...document.querySelectorAll('.ui-panel [role=tab], .ui-panel .tab, .ui-panel [data-tab]')][{i}]?.click()"); time.sleep(0.6)
                s.pg.evaluate("() => window.__game.ui.ctx.panels.close()"); time.sleep(0.6)
            # walk the lobby/plot signs so their canvas labels are drawn
            for x, z in ((-50, -6), (-20, 10), (20, 10), (4, -30), (-80, -10)):
                s.tp(x, z, settle=1.0)
            return s.pg.evaluate('() => window.__txtDump()'), list(s.errors)
        finally:
            s.close()


ALLOW = {'qa', 'qi', 'sx', 'sp', 'oc', 'no', 'dc', 'ud', 'dd', 'td', 'x2', 'x3', 'ok', 'hp', 'xp', 'vs', 'id', 'fps', 'snack toss zoo', 'snack', 'toss', 'zoo', 'w', 'a', 's', 'd', 'e', 'esc',
         'lmb', 'rmb', 'm', 'k', 'b', 't', 'q', 'qa', 'sfx', 'ui', 'hud', 'cg', 'pc', 'ad'}
LAT = re.compile(r"[A-Za-z][A-Za-z'’]+")
NUMISH = re.compile(r"^[\d\s$€.,:%/x×+\-−()kmbtqKMBTQ!?]+$")


def words(sv): return [w for w in LAT.findall(sv) if w.lower() not in ALLOW]


if not a.no_build: build()
langs = a.langs.split(',')
data = {}
with Server() as srv:
    for L in langs:
        t0 = time.time(); txt, errs = run(srv.url, L); data[L] = dict(txt)
        json.dump({'texts': txt, 'errors': errs}, open(os.path.join(OUT, f'{L}.json'), 'w'), ensure_ascii=False, indent=1)
        print(f'{L}: {len(txt)} strings, errors={len(errs)} [{time.time() - t0:.0f} s]', flush=True)

en = set(data.get('en', {}))
rep = ['# i18n runtime audit', '', f'langs: {langs}', '']
total = 0
for L in langs:
    if L == 'en': continue
    bad = []
    for sv, src in data[L].items():
        if NUMISH.match(sv): continue
        w = words(sv)
        if not w: continue
        if L == 'ru': bad.append((src, sv))
        elif sv in en and re.search(r'[A-Za-z]{3,}', sv): bad.append((src, sv))
    rep += [f'## {L}: {len(bad)}', ''] + [f'- [{src}] {sv}' for src, sv in sorted(bad, key=lambda x: x[1])] + ['']
    total += len(bad)
open(os.path.join(OUT, 'REPORT.md'), 'w').write('\n'.join(rep))
print(f'flagged: {total} → tools/out/i18n_audit/REPORT.md')
