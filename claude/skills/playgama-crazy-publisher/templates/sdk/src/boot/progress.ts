/**
 * Loading screen bridge (index.html #boot, window.__boot). Shows real progress and hides only on bootDone(),
 * which main.ts calls after every model, texture and shader is ready and the first frame is drawn.
 * Engine hook: three.js -> import './threeHook' first in main.ts; other engines -> call track() on their loads.
 */
type BootUI = { set(p: number): void; lang(l: string): void; done(): void };
const ui = (): BootUI | undefined => (window as unknown as { __boot?: BootUI }).__boot;

export const bootProgress = (p: number) => ui()?.set(p);
export const bootLang = (l: string) => ui()?.lang(l);
export const bootDone = () => ui()?.done();

let pending = 0, settled = 0, engine = false;
const waiters: Array<() => void> = [];
const wake = () => { if (settled >= pending && !engine) waiters.splice(0).forEach((f) => f()); };
/** counts a load into the bar's asset share (10 % → 82 %) */
export function track<T>(p: Promise<T>): Promise<T> {
  pending++;
  const step = () => { settled++; bootProgress(0.1 + 0.72 * (settled / Math.max(1, pending))); wake(); };
  p.then(step, step);
  return p;
}
/** engine loaders report busy/idle (threeHook) */
export function engineBusy(b: boolean) { engine = b; wake(); }
/** resolves once nothing is loading (or after maxMs, so one stuck file never blocks the game) */
export function assetsIdle(maxMs = 30000): Promise<void> {
  if (settled >= pending && !engine) return Promise.resolve();
  return new Promise((res) => { waiters.push(res); setTimeout(res, maxMs); });
}
/** waits two animation frames: the first frame with everything in has really been drawn */
export const firstFrame = () => new Promise<void>((r) => requestAnimationFrame(() => requestAnimationFrame(() => r())));
