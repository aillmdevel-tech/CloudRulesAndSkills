// Global UIFX settings: reduced motion, global intensity/speed multipliers.

export type ReducedMotionMode = 'auto' | 'reduce' | 'full';

export interface UIFXConfig {
  /** 'auto' follows the OS prefers-reduced-motion setting. */
  reducedMotion: ReducedMotionMode;
  /** Multiplies motion amplitude (scale deltas, angles, distances). 0..2 */
  intensity: number;
  /** Multiplies speed (durations are divided by it). 0.25..3 */
  speed: number;
}

export const config: UIFXConfig = { reducedMotion: 'auto', intensity: 1, speed: 1 };

const mq = typeof matchMedia === 'function' ? matchMedia('(prefers-reduced-motion: reduce)') : null;

export function prefersReducedMotion(): boolean {
  if (config.reducedMotion === 'reduce') return true;
  if (config.reducedMotion === 'full') return false;
  return !!mq?.matches;
}

export function configure(patch: Partial<UIFXConfig>): void {
  Object.assign(config, patch);
  document.documentElement.toggleAttribute('data-uifx-reduced', prefersReducedMotion());
}

mq?.addEventListener?.('change', () => configure({}));

/** Scale a duration (ms) by the global speed. */
export const dur = (ms: number): number => ms / Math.max(0.05, config.speed);
/** Scale an amplitude by the global intensity. */
export const amp = (v: number): number => v * config.intensity;
