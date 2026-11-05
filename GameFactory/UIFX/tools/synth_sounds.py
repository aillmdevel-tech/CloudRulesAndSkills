#!/usr/bin/env python3
"""Procedural UI sounds for GameFactory UIFX (stdlib only). Output: 44.1 kHz mono 16-bit WAV.

usage: synth_sounds.py OUTDIR [--seed 7]
Every sound is a small function — tweak pitch/duration here and re-run tools/build_sounds.py.
These sounds are original works made for GameFactory and are released as CC0.
"""
import math
import os
import random
import struct
import sys
import wave

SR = 44100


def env_adsr(t, a, d, s, r, dur):
    if t < a:
        return t / a
    if t < a + d:
        return 1 - (1 - s) * (t - a) / d
    if t < dur - r:
        return s
    return max(0.0, s * (dur - t) / r)


def env_exp(t, k):
    return math.exp(-k * t)


def sine(ph):
    return math.sin(2 * math.pi * ph)


def tri(ph):
    return 4 * abs((ph % 1) - 0.5) - 1


def square(ph, duty=0.5):
    return 1.0 if (ph % 1) < duty else -1.0


def render(fn, dur):
    n = int(SR * dur)
    return [fn(i / SR, i) for i in range(n)]


def lowpass(sig, cutoff_fn):
    out, y = [], 0.0
    for i, x in enumerate(sig):
        c = cutoff_fn(i / SR)
        a = 1 - math.exp(-2 * math.pi * c / SR)
        y += a * (x - y)
        out.append(y)
    return out


def mix(*tracks):
    n = max(int(off * SR) + len(t) for t, off in tracks)
    out = [0.0] * n
    for t, off in tracks:
        o = int(off * SR)
        for i, v in enumerate(t):
            out[o + i] += v
    return out


def norm(sig, peak=0.89):
    m = max(abs(x) for x in sig) or 1
    fade = int(0.004 * SR)
    sig = [x * peak / m for x in sig]
    for i in range(min(fade, len(sig))):
        sig[-1 - i] *= i / fade
    return sig


def write(path, sig):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 32767)) for x in sig))


class Osc:
    def __init__(self):
        self.ph = 0.0

    def step(self, f):
        self.ph += f / SR
        return self.ph


# ---------------------------------------------------------------- sounds
def jelly_click():
    """Wobbly cartoon 'boing' press: pitch drop with vibrato that settles."""
    o = Osc(); dur = 0.22
    def f(t, i):
        freq = 520 * (1 + 0.9 * math.exp(-t * 28)) * (1 + 0.06 * math.sin(2 * math.pi * 32 * t) * math.exp(-t * 14))
        return sine(o.step(freq)) * env_exp(t, 16) * min(1, t / 0.002)
    return norm(render(f, dur))


def jelly_release():
    o = Osc(); dur = 0.16
    def f(t, i):
        freq = 640 * (1 + 0.5 * (1 - math.exp(-t * 30)))
        return sine(o.step(freq)) * env_exp(t, 22) * min(1, t / 0.002)
    return norm(render(f, dur), 0.7)


def pop():
    """Bubble pop for Pop In: fast upward chirp."""
    o = Osc(); dur = 0.09
    def f(t, i):
        freq = 300 + 1700 * (t / dur) ** 0.6
        return sine(o.step(freq)) * env_exp(t, 40) * min(1, t / 0.001)
    return norm(render(f, dur))


def bubble_hover():
    """Very soft, short hover blip."""
    o = Osc(); dur = 0.06
    def f(t, i):
        return sine(o.step(880 + 600 * t / dur)) * math.sin(math.pi * t / dur) ** 2
    return norm(render(f, dur), 0.5)


def whoosh(rising=True, dur=0.35):
    rnd = random.Random(11 if rising else 12)
    noise = [rnd.uniform(-1, 1) for _ in range(int(SR * dur))]
    def cut(t):
        x = t / dur
        return 300 + 4200 * (x if rising else 1 - x) ** 1.5
    sig = lowpass(lowpass(noise, cut), cut)
    sig = [v * math.sin(math.pi * min(1, (i / SR) / dur)) ** 1.6 for i, v in enumerate(sig)]
    return norm(sig, 0.75)


def coin():
    """Two-step bright coin (B5 -> E6) with square-ish timbre."""
    o = Osc(); dur = 0.42
    def f(t, i):
        freq = 988 if t < 0.07 else 1319
        v = 0.6 * square(o.step(freq), 0.5) + 0.4 * sine(o.ph * 2)
        return v * (env_exp(t, 9) if t >= 0.07 else 0.9) * 0.6
    return norm(lowpass(render(f, dur), lambda t: 6000))


def chime(freqs, step=0.08, tail=0.6, shimmer=True):
    tracks = []
    for k, fr in enumerate(freqs):
        o = Osc(); o2 = Osc()
        def f(t, i, fr=fr, o=o, o2=o2):
            v = sine(o.step(fr)) + 0.35 * sine(o2.step(fr * 2.01)) + (0.15 * sine(o.ph * 3) if shimmer else 0)
            return v * env_exp(t, 5.5) * min(1, t / 0.003)
        tracks.append((render(f, tail), k * step))
    return norm(mix(*tracks))


def reward():
    # C6 E6 G6 C7 sparkle
    return chime([1047, 1319, 1568, 2093], step=0.06, tail=0.7)


def level_up():
    # rising major arpeggio + final chord
    notes = [523, 659, 784, 1047, 1319, 1568]
    base = chime(notes, step=0.075, tail=0.5)
    final = chime([1047, 1319, 1568], step=0.0, tail=1.0)
    return norm(mix((base, 0), ([x * 0.8 for x in final], 0.45)))


def success():
    return chime([784, 1175], step=0.09, tail=0.55)


def notify():
    return chime([1319, 988], step=0.12, tail=0.6, shimmer=False)


def error_soft():
    """Cartoon 'nope': two low descending triangle blips."""
    tracks = []
    for k, fr in enumerate((330, 247)):
        o = Osc()
        def f(t, i, fr=fr, o=o):
            return tri(o.step(fr * (1 - 0.08 * t))) * env_adsr(t, 0.004, 0.05, 0.6, 0.05, 0.13)
        tracks.append((render(f, 0.13), k * 0.11))
    return norm(lowpass(mix(*tracks), lambda t: 2500), 0.8)


def tick():
    o = Osc(); dur = 0.03
    return norm(render(lambda t, i: sine(o.step(2400)) * env_exp(t, 160), dur), 0.6)


def counter_tick():
    o = Osc(); dur = 0.045
    return norm(render(lambda t, i: (0.7 * square(o.step(1600), 0.3)) * env_exp(t, 90), dur), 0.45)


def sparkle():
    rnd = random.Random(5)
    tracks = []
    for k in range(7):
        fr = rnd.choice([2093, 2349, 2637, 3136, 3520])
        o = Osc()
        def f(t, i, fr=fr, o=o):
            return sine(o.step(fr)) * env_exp(t, 18)
        tracks.append((render(f, 0.25), k * 0.045 + rnd.uniform(0, 0.02)))
    return norm(mix(*tracks), 0.6)


def confetti():
    """Party-popper: noise burst + sparkle."""
    rnd = random.Random(9)
    burst = [rnd.uniform(-1, 1) * env_exp(i / SR, 35) for i in range(int(SR * 0.18))]
    burst = lowpass(burst, lambda t: 3500)
    return norm(mix((burst, 0), ([x * 0.7 for x in sparkle()], 0.05)), 0.8)


def squish():
    """Squash: low rubbery 'blop'."""
    o = Osc(); dur = 0.18
    def f(t, i):
        freq = 180 + 140 * math.exp(-t * 25) + 25 * math.sin(2 * math.pi * 18 * t)
        return (sine(o.step(freq)) + 0.3 * tri(o.ph * 2)) * env_exp(t, 14) * min(1, t / 0.003)
    return norm(render(f, dur), 0.85)


SOUNDS = {
    "jelly_click": jelly_click, "jelly_release": jelly_release, "pop": pop, "bubble_hover": bubble_hover,
    "whoosh_in": lambda: whoosh(True), "whoosh_out": lambda: whoosh(False, 0.28),
    "coin": coin, "reward": reward, "level_up": level_up, "success_chime": success,
    "notify_chime": notify, "error_soft": error_soft, "tick_soft": tick, "counter_tick": counter_tick,
    "sparkle": sparkle, "confetti": confetti, "squish": squish,
}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in SOUNDS.items():
        write(os.path.join(out, name + ".wav"), fn())
        print("synth", name)


if __name__ == "__main__":
    main()
