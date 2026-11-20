"""promo/scenario.py — scripted take for capture.py. Keep it deterministic (fixed seed / save).
api: js(code[, arg]), wait(s), key_down/key_up/press/hold(keys, s), click(x, y), mouse_move, drag,
     event(type, weight, label)  -> juicy moment for moments.py (weight 1..5),
     director(on)                -> calls window.__promo.director if the game defines it,
     shot(name)                  -> crisp still for shots.py, t() -> seconds since recording start."""


def prepare(api):
    # before recording: load a good save, skip menus, set quality high
    api.js("() => { const g = window.__game; if (g?.renderer?.setQuality) g.renderer.setQuality('high'); }")


def run(api):
    api.wait(0.8)
    api.hold(['KeyW'], 1.5)
    api.hold(['KeyW', 'Space'], 2.0)
    api.event('big_jump', 4)          # the game can also call window.__promo.event itself
    api.shot('hero_jump')
    api.wait(1.0)
