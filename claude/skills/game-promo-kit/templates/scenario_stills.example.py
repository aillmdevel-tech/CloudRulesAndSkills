"""EXAMPLE from Snack Toss Zoo (throw game): copy to promo/scenario_stills.py and rewrite the beats for the new game.
In new scenarios use api.shot_pair(name) instead of the local pair()/ui() helpers below.
promo/scenario_stills.py — stills for platform screenshots and covers (game-promo-kit shots).
Same honest flow as scenario_v3 (only the rolls are forced): aim meter, flight across biomes with LUCK xN,
letter reveal, rare card, Void Bar LEVEL UP, zoo plot with a late-game collection, Index / My Animals panels.
Each beat is shot twice: with the game HUD (screens) and without it (`_clean`, cover sources)."""
import math, os

MUT = {'none': 1, 'gold': 1.5, 'diamond': 3, 'ruby': 10, 'rainbow': 20}
BASE = {'bunny': 5, 'giraffe': 80, 'lion': 1000, 'frost-giant': 5_500 * 10**9,
        'snow-dragon': 3_800 * 10**9, 'trex': 150 * 10**12}
SPOT = (-66.0, -8.0)
ZOO = [('giraffe', 'gold'), ('lion', 'none'), ('rhino', 'diamond'), ('gorilla', 'none'), ('panda', 'gold'),
       ('crocodile', 'rainbow'), ('jaguar', 'none'), ('toucan', 'ruby'), ('bunny', 'none'), ('chicken', 'none')]


def ui(api, on):
    api.js("""(on) => { let s = document.getElementById('promo-noui'); if (!s) { s = document.createElement('style'); s.id = 'promo-noui'; document.head.append(s); } s.textContent = on ? '' : '#ui{visibility:hidden!important}';
      const g = __game; g.__hid = g.__hid || [];
      if (!on) g.scene.traverse((o) => { if (o.isSprite && o.visible) { o.visible = false; g.__hid.push(o); } });
      else { for (const o of g.__hid) o.visible = true; g.__hid = []; } }""", on)


def pair(api, name):
    api.shot(name)
    ui(api, False); api.wait(0.05); api.shot(name + '_clean'); ui(api, True)


def phase(api):
    return api.js('() => __game.flow.phase')


def prepare(api):
    api.js("""() => { const g = __game, st = g.session.state;
      st.level = 30; st.xp = 0; st.barIndex = 23; st.tutorial.step = 99; st.money = 25000n;
      st.animals = st.animals.slice(0, 3);
      delete st.discovered['frost-giant']; delete st.discovered['trex']; delete st.discovered['giraffe'];
      g.session.emit('level', 30); g.session.emit('change'); g.session.save();
      if (g.pen && g.pen.sync) g.pen.sync(st);
      if (g.R && g.R.setQuality) { g.R.auto = false; g.R.setQuality('high'); }
      const css = document.createElement('style'); css.textContent = '.tst-food,.tst-bar{display:none!important}';
      document.head.append(css); }""")
    api.wait(2.0)


def throw(api, side, sp, mut, n, tag):
    W, H = api.js('() => [innerWidth, innerHeight]')
    api.js("""([side, sp, mut, n, inc]) => { const g = __game, f = g.flow;
      f.forceMeter = 0.97; f.forceDistance = null; f.forceSide = side;
      f.forceResult = { speciesId: sp, mutation: mut, sizeSteps: 0, oneInN: n, income: BigInt(inc) };
      g.player.teleport(new g.THREE.Vector3(4, 3, -33), Math.PI); }""", [side, sp, mut, n, str(int(BASE[sp] * MUT[mut]))])
    api.wait(0.4)
    api.hold(['KeyW'], 1.5)
    api.wait(0.6)
    pair(api, f'{tag}_a_aim')
    api.click(W // 2, int(H * 0.55))
    seen, t_fl = set(), 0
    for _ in range(500):
        ph = phase(api)
        if ph == 'flight' and 'flight' not in seen:
            seen.add('flight'); api.wait(1.0); pair(api, f'{tag}_b_flight'); t_fl = 1
        elif ph == 'flight' and t_fl == 1:
            api.wait(1.6); pair(api, f'{tag}_c_flight'); t_fl = 2
        if ph == 'result' and 'result' not in seen:
            seen.add('result'); api.wait(0.35); pair(api, f'{tag}_d_reveal')
            api.wait(1.3); pair(api, f'{tag}_e_card'); api.wait(0.8); break
        api.wait(0.1)
    api.click(W // 2, int(H * 0.55))
    for _ in range(80):
        if phase(api) == 'idle': break
        api.wait(0.1)
    api.wait(0.9); pair(api, f'{tag}_f_showcase')


def train(api, target):
    api.js("([x, z]) => { const g = __game; g.player.teleport(new g.THREE.Vector3(x, 3, z + 7), Math.PI); }", list(SPOT))
    api.wait(0.6)
    lv0 = api.js('() => __game.session.state.level')
    api.hold(['KeyW'], 0.75)
    for _ in range(80):
        if api.js('() => __game.session.state.level') > lv0 + 50: break
        api.wait(0.05)
    api.wait(0.2); pair(api, 'train_levelup')      # first Void rep: LEVEL UP xN hundreds
    for _ in range(60):
        if api.js('() => __game.session.state.level') >= target: break
        api.wait(0.1)
    api.wait(1.2)
    api.press('Space')
    api.wait(0.8)


def zoo(api):
    api.js("""(zoo) => { const g = __game, st = g.session.state;
      st.animals = zoo.map(([sp, m], i) => ({ uid: 'promo_' + i, speciesId: sp, mutation: m, sizeSteps: 0, obtainedAt: Date.now(), placed: true }));
      for (const [sp, m] of zoo) { const d = st.discovered[sp] ?? (st.discovered[sp] = { mutations: [] }); if (!d.mutations.includes(m)) d.mutations.push(m); }
      g.session.emit('change'); g.pen.sync(st);
      g.player.teleport(new g.THREE.Vector3(-50, 3, 13), 0); }""", ZOO)
    api.wait(2.5)
    c = api.js("() => { const b = __game.pen.box; return [(b.min.x + b.max.x) / 2, (b.min.z + b.max.z) / 2, b.max.x - b.min.x, b.max.z - b.min.z]; }")
    print('pen box', c)
    R = max(c[2], c[3]) * 1.25
    for k, (a, h, pt) in enumerate(((0.0, 0.75, -0.55), (0.6, 0.7, -0.5), (-0.6, 0.7, -0.5), (2.6, 0.75, -0.55))):
        x, z = c[0] + math.sin(a) * R, c[1] + math.cos(a) * R
        api.js("(v) => __game.setCam(v[0], v[1], v[2], v[3], v[4])", [x, R * h, z, a, pt])
        api.wait(1.0); pair(api, f'zoo_{k}')
    api.js('() => __game.play()')
    api.js("() => { const g = __game; g.player.teleport(new g.THREE.Vector3(-50, 3, 13), 0); }"); api.wait(1.5)
    for pid in ('animals', 'index'):
        api.js("(id) => __game.ui.ctx.panels.open(id)", pid)
        api.wait(1.0)
        if pid == 'index':
            api.js("() => { const l = document.querySelector('.ix-list'); const rows = l && l.children; if (rows && rows[1]) l.scrollTop = rows[1].offsetTop - 8; }")
            api.wait(0.6)
        api.shot(f'panel_{pid}')
        api.js('() => __game.ui.ctx.panels.close()'); api.wait(0.7)
    api.js('() => __game.play()')


def run(api):
    api.wait(0.3)
    if os.environ.get('STILLS_PART') == 'fix':     # reshoot: first Void rep + zoo from above + panels
        train(api, 264); zoo(api); return
    throw(api, 0, 'giraffe', 'none', 3, 't1')
    train(api, 264)
    throw(api, 1, 'frost-giant', 'diamond', 3200, 't2')
    api.js("() => { const st = __game.session.state; st.level = 294; __game.session.emit('level', 294); __game.session.emit('change'); }")
    api.wait(0.5)
    throw(api, 0, 'trex', 'rainbow', 2_400_000, 't3')
    zoo(api)
