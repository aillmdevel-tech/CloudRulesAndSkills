export type NumParam = { label: string; min: number; max: number; step: number };
export type OptParam = { label: string; options: readonly string[] };
export type ParamSpec = NumParam | OptParam;
export type Params = Record<string, number | string>;

/** Something running that can be stopped (loops, attached listeners). */
export interface Handle {
  stop(): void;
}

export type RunResult = Animation | Promise<unknown> | Handle | void;

export interface EffectDef<P extends Params = Params> {
  id: string;
  name: string;
  category: 'press' | 'hover' | 'window' | 'sequence' | 'attention' | 'reward' | 'feedback' | 'text';
  description: string;
  defaults: P;
  params: { [K in keyof P]?: ParamSpec };
  /** One-shot run (also used by the demo "play" button). */
  run(el: HTMLElement, p: P, ev?: { clientX: number; clientY: number }): RunResult;
  /** Interactive effects attach listeners and return a detach handle. */
  attach?(el: HTMLElement, p: () => P): Handle;
  /** true = runs forever until stopped (shine, breathe...). */
  loop?: boolean;
}

export const defineEffect = <P extends Params>(d: EffectDef<P>): EffectDef<P> => d;

/** Spring params shared by many effects. */
export const springParams = {
  stiffness: { label: 'spring stiffness', min: 50, max: 1500, step: 10 },
  damping: { label: 'spring damping', min: 2, max: 80, step: 1 },
  mass: { label: 'mass', min: 0.2, max: 4, step: 0.1 },
} as const;

export const easeParam = {
  label: 'easing',
  options: ['out', 'inOut', 'in', 'sine', 'backOut', 'backIn', 'anticipate', 'linear'],
} as const;
