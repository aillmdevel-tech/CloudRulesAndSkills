/**
 * Platform layer (playgama-crazy-publisher, stage «SDK»): one adapter per build (VITE_PLATFORM = web | playgama | crazygames).
 * The game talks only to this interface. Nothing outside src/platform and src/dev touches an SDK or browser storage.
 */
export type PlatformId = 'web' | 'playgama' | 'crazygames';

export interface PlatformStorage {
  /** raw string, or null when nothing is saved / storage is unavailable */
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
}

/** Ads. Which kinds are on comes from FEATURES (src/platform/config.ts, generated from the game's launch status). */
export interface PlatformAds {
  /** show a WATCH AD button only while this is true */
  readonly rewardedAvailable: boolean;
  /** sticky banner on menu screens; no-op where off or unsupported */
  banner(show: boolean): void;
  /** logical pause only (level end, death screen closed). Resolves when the game may continue, ad or no ad. */
  interstitial(placement: string): Promise<void>;
  /** resolves true only when the reward must be granted (ad watched to the end) */
  rewarded(placement: string): Promise<boolean>;
}

export interface Product { id: string; price: string }

/** In-app purchases (FEATURES.iap). Grant only on purchase() === true; consume consumables right after granting. */
export interface PlatformPurchases {
  /** shop buttons are shown only while this is true */
  readonly supported: boolean;
  catalog(): Promise<Product[]>;
  /** call only from a direct player tap; true = paid, grant the item now */
  purchase(id: string): Promise<boolean>;
  /** consumables (coins, boosts) right after granting; never for permanent items (no ads, skins) */
  consume(id: string): Promise<void>;
  /** ids bought earlier and not consumed: check once at boot, grant unprocessed consumables and restore permanent items */
  owned(): Promise<string[]>;
}

export interface Platform {
  readonly id: PlatformId;
  /** platform language code; 'en' fallback */
  readonly language: string;
  /** platform audio switch (Playgama isAudioEnabled / CrazyGames muteAudio) */
  readonly audioEnabled: boolean;
  init(): Promise<void>;
  loadingStart(): void;
  /** first call = loaded and playable (Playgama game_ready / CrazyGames loadingStop) */
  loadingStop(): void;
  /** playing: loaded, not paused, no menu open, no ad */
  gameplayStart(): void;
  gameplayStop(): void;
  /** rare celebration moment (CrazyGames happytime) */
  happytime(): void;
  readonly storage: PlatformStorage;
  readonly ads: PlatformAds;
  readonly purchases: PlatformPurchases;
  /** platform pause and fullscreen ads: freeze the loop and silence audio while true */
  onPause(cb: (paused: boolean) => void): void;
  /** platform audio switch changed */
  onAudio(cb: (enabled: boolean) => void): void;
}

export class Listeners<T> {
  private fns: ((v: T) => void)[] = [];
  add(fn: (v: T) => void) { this.fns.push(fn); }
  emit(v: T) { for (const f of this.fns) { try { f(v); } catch (e) { console.warn('[platform] listener', e); } } }
}

/** shared: no purchases on this build */
export const NO_PURCHASES: PlatformPurchases = {
  supported: false,
  catalog: async () => [],
  purchase: async () => false,
  consume: async () => {},
  owned: async () => [],
};
