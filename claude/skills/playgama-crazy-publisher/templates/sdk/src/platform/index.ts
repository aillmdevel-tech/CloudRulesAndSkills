import type { Platform, PlatformId } from './types';

export type { Platform, PlatformId, Product } from './types';
export { FEATURES } from './config';

export const PLATFORM_ID: PlatformId = (import.meta.env.VITE_PLATFORM as PlatformId | undefined) ?? 'web';

function timeout<T>(p: Promise<T>, ms: number): Promise<T | undefined> {
  return Promise.race([p, new Promise<undefined>((r) => setTimeout(r, ms))]);
}

/** VITE_PLATFORM is a build-time constant: each build carries one adapter. Init failure never blocks the game. */
export async function createPlatform(): Promise<Platform> {
  let p: Platform;
  if (PLATFORM_ID === 'playgama') p = new (await import('./playgama')).PlaygamaPlatform();
  else if (PLATFORM_ID === 'crazygames') p = new (await import('./crazygames')).CrazyGamesPlatform();
  else p = new (await import('../dev/webPlatform')).WebPlatform();
  try { await timeout(p.init(), 10000); } catch (e) { console.warn('[platform] init failed, playing offline', e); }
  (window as unknown as { __platform?: Platform }).__platform = p; // QA hook (pub sdk-run, smoke)
  return p;
}
