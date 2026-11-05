// Thin, interruptible layer over the Web Animations API + a rAF value animator for canvas/engine UI.
// Effects animate the individual CSS properties `scale`, `rotate`, `translate`, so they compose with
// a game's own `transform` instead of overwriting it.

import { bakeSpring, resolveSpring, type SpringOptions, type SpringName } from './spring';
import { dur } from './config';

/** CSS easing strings for WAAPI. */
export const EASE = {
  linear: 'linear',
  out: 'cubic-bezier(0.22, 1, 0.36, 1)',
  in: 'cubic-bezier(0.55, 0, 1, 0.45)',
  inOut: 'cubic-bezier(0.65, 0, 0.35, 1)',
  sine: 'cubic-bezier(0.37, 0, 0.63, 1)',
  backOut: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  backIn: 'cubic-bezier(0.36, 0, 0.66, -0.56)',
  anticipate: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
} as const;
export type EaseName = keyof typeof EASE;
export const easeCss = (e: EaseName | string): string => (e in EASE ? EASE[e as EaseName] : e);

/** JS easing functions (t: 0..1) for animateValue. */
export const EASE_FN: Record<string, (t: number) => number> = {
  linear: (t) => t,
  out: (t) => 1 - Math.pow(1 - t, 3),
  in: (t) => t * t * t,
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  sine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  backOut: (t) => 1 + 2.70158 * Math.pow(t - 1, 3) + 1.70158 * Math.pow(t - 1, 2),
  elasticOut: (t) => (t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1),
  bounceOut: (t) => {
    const n = 7.5625, d = 2.75;
    if (t < 1 / d) return n * t * t;
    if (t < 2 / d) return n * (t -= 1.5 / d) * t + 0.75;
    if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + 0.9375;
    return n * (t -= 2.625 / d) * t + 0.984375;
  },
};

export interface PlayOptions {
  duration: number;
  delay?: number;
  easing?: EaseName | string;
  /** Animations on the same element+channel interrupt each other. Default 'main'. */
  channel?: string;
  /** Keep the final state as inline style after finishing. Default true. */
  persist?: boolean;
  iterations?: number;
  direction?: PlaybackDirection;
  composite?: CompositeOperation;
}

const running = new WeakMap<Element, Map<string, Animation>>();

/** Stop whatever runs on this element+channel, freezing it at its current visual state. */
export function interrupt(el: Element, channel = 'main'): void {
  const prev = running.get(el)?.get(channel);
  if (!prev) return;
  try {
    prev.commitStyles();
  } catch {
    /* element not rendered */
  }
  prev.cancel();
  running.get(el)!.delete(channel);
}

export function play(el: HTMLElement, keyframes: Keyframe[] | PropertyIndexedKeyframes, o: PlayOptions): Animation {
  const channel = o.channel ?? 'main';
  interrupt(el, channel);
  const anim = el.animate(keyframes, {
    duration: dur(o.duration),
    delay: dur(o.delay ?? 0),
    easing: easeCss(o.easing ?? 'out'),
    iterations: o.iterations ?? 1,
    direction: o.direction,
    composite: o.composite,
    fill: 'both',
  });
  let map = running.get(el);
  if (!map) running.set(el, (map = new Map()));
  map.set(channel, anim);
  const persist = o.persist ?? true;
  anim.finished
    .then(() => {
      if (persist) {
        try {
          anim.commitStyles();
        } catch {
          /* not rendered */
        }
      }
      anim.cancel();
      if (map!.get(channel) === anim) map!.delete(channel);
    })
    .catch(() => {
      /* cancelled = interrupted, fine */
    });
  return anim;
}

/** Bake a spring into keyframes: `frame(p)` maps spring progress (may overshoot) to a keyframe. */
export function springFrames(
  spring: SpringOptions | SpringName | undefined,
  frame: (p: number) => Keyframe,
  fallback: SpringName = 'bouncy',
): { keyframes: Keyframe[]; duration: number } {
  const { samples, duration } = bakeSpring(resolveSpring(spring, fallback));
  return { keyframes: samples.map(frame), duration };
}

export function playSpring(
  el: HTMLElement,
  spring: SpringOptions | SpringName | undefined,
  frame: (p: number) => Keyframe,
  o: Omit<PlayOptions, 'duration' | 'easing'> = {},
): Animation {
  const { keyframes, duration } = springFrames(spring, frame);
  return play(el, keyframes, { ...o, duration, easing: 'linear' });
}

export interface ValueAnimation {
  stop(): void;
  finished: Promise<void>;
}

/** rAF tween of a number — for canvas/PlayCanvas/Three/Pixi UI where there is no DOM element. */
export function animateValue(o: {
  from: number;
  to: number;
  duration: number;
  delay?: number;
  ease?: keyof typeof EASE_FN | ((t: number) => number);
  onUpdate: (v: number) => void;
}): ValueAnimation {
  const ease = typeof o.ease === 'function' ? o.ease : EASE_FN[o.ease ?? 'out'];
  const total = dur(o.duration);
  const start = performance.now() + dur(o.delay ?? 0);
  let raf = 0;
  let resolve!: () => void;
  const finished = new Promise<void>((r) => (resolve = r));
  const tick = (now: number) => {
    const t = Math.max(0, Math.min(1, (now - start) / total));
    if (now >= start) o.onUpdate(o.from + (o.to - o.from) * ease(t));
    if (t < 1) raf = requestAnimationFrame(tick);
    else resolve();
  };
  raf = requestAnimationFrame(tick);
  return { stop: () => (cancelAnimationFrame(raf), resolve()), finished };
}

export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;
export const wait = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, dur(ms)));
