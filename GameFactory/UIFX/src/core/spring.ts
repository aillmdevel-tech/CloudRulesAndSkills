// Damped spring physics (renderer-agnostic). Used to bake WAAPI keyframes and to drive live values.

export interface SpringOptions {
  /** Higher = snappier. Typical 150..900 */
  stiffness: number;
  /** Higher = less bounce. Typical 8..40 */
  damping: number;
  /** Typical 0.5..2 */
  mass: number;
  /** Initial velocity in progress-units per second. */
  velocity?: number;
  restDelta?: number;
  restSpeed?: number;
}

export const SPRINGS = {
  /** Wobbly jelly — lots of overshoot. */
  jelly: { stiffness: 420, damping: 9, mass: 1 },
  /** Bouncy but settles fast — buttons, pop-ins. */
  bouncy: { stiffness: 500, damping: 16, mass: 1 },
  /** Snappy with tiny overshoot — modern UI. */
  snappy: { stiffness: 700, damping: 32, mass: 1 },
  /** Soft and slow — casual panels. */
  soft: { stiffness: 180, damping: 20, mass: 1 },
  /** No overshoot. */
  stiff: { stiffness: 900, damping: 60, mass: 1 },
} satisfies Record<string, SpringOptions>;

export type SpringName = keyof typeof SPRINGS;

export function resolveSpring(s: SpringOptions | SpringName | undefined, fallback: SpringName = 'bouncy'): SpringOptions {
  if (!s) return SPRINGS[fallback];
  return typeof s === 'string' ? SPRINGS[s] : s;
}

/**
 * Simulate a spring from 0 to 1. Returns samples at `fps` and the settle duration in ms.
 * Progress can overshoot above 1 / below 0 — that is the bounce.
 */
export function bakeSpring(opts: SpringOptions, fps = 60, maxMs = 3000): { samples: number[]; duration: number } {
  const { stiffness: k, damping: c, mass: m } = opts;
  const restDelta = opts.restDelta ?? 0.001;
  const restSpeed = opts.restSpeed ?? 0.01;
  let x = 0;
  let v = opts.velocity ?? 0;
  const sub = 8;
  const dt = 1 / fps / sub;
  const samples = [0];
  let t = 0;
  while (t * 1000 < maxMs) {
    for (let i = 0; i < sub; i++) {
      const a = (-k * (x - 1) - c * v) / m;
      v += a * dt;
      x += v * dt;
    }
    t += 1 / fps;
    samples.push(x);
    if (Math.abs(1 - x) < restDelta && Math.abs(v) < restSpeed) break;
  }
  samples[samples.length - 1] = 1;
  return { samples, duration: Math.round(t * 1000) };
}

/** Live spring for continuously retargeted values (hover follow, camera zoom). Interruptible by design. */
export class SpringValue {
  value: number;
  target: number;
  velocity = 0;
  private raf = 0;
  private last = 0;

  constructor(
    initial: number,
    public opts: SpringOptions,
    private onUpdate: (v: number) => void,
  ) {
    this.value = initial;
    this.target = initial;
  }

  set(target: number, velocity?: number): void {
    this.target = target;
    if (velocity !== undefined) this.velocity = velocity;
    if (!this.raf) {
      this.last = performance.now();
      this.raf = requestAnimationFrame(this.tick);
    }
  }

  jump(v: number): void {
    this.stop();
    this.value = this.target = v;
    this.velocity = 0;
    this.onUpdate(v);
  }

  stop(): void {
    cancelAnimationFrame(this.raf);
    this.raf = 0;
  }

  private tick = (now: number): void => {
    const { stiffness: k, damping: c, mass: m } = this.opts;
    let elapsed = Math.min(0.064, (now - this.last) / 1000);
    this.last = now;
    const step = 1 / 240;
    while (elapsed > 0) {
      const dt = Math.min(step, elapsed);
      const a = (-k * (this.value - this.target) - c * this.velocity) / m;
      this.velocity += a * dt;
      this.value += this.velocity * dt;
      elapsed -= dt;
    }
    const done = Math.abs(this.value - this.target) < 0.0005 && Math.abs(this.velocity) < 0.005;
    if (done) {
      this.value = this.target;
      this.velocity = 0;
    }
    this.onUpdate(this.value);
    this.raf = done ? 0 : requestAnimationFrame(this.tick);
  };
}
