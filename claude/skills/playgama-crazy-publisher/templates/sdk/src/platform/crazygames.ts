import { FEATURES } from './config';
import { Listeners, NO_PURCHASES, type Platform, type PlatformStorage } from './types';

/**
 * CrazyGames HTML5 SDK v3, loaded from JS (index.html keeps relative paths only).
 * FEATURES.crazygames follows the launch status: Basic Launch = no ads, no IAP (SDK still gives loading/gameplay
 * events, Data module saves, mute). Full Launch = midgame/rewarded via SDK.ad. IAP on CrazyGames is invite-only
 * (Xsolla via getXsollaUserToken) and is not part of this template.
 * Rules: init awaited first; environment 'disabled' (foreign domain) -> every call throws, play offline;
 * mute and pause only on adStarted; reward only in adFinished; adError (unfilled, adblock, cooldown) -> just continue.
 */
const SDK_URL = 'https://sdk.crazygames.com/crazygames-sdk-v3.js';
type CGSDK = any;
const S = (): CGSDK | undefined => (window as any).CrazyGames?.SDK;
const F = FEATURES.crazygames;

function loadScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    const s = document.createElement('script');
    s.src = src;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error('CrazyGames SDK failed to load'));
    document.head.appendChild(s);
  });
}

class CGStore implements PlatformStorage {
  constructor(private ok: () => boolean) {}
  async get(key: string) {
    const s = S();
    if (!this.ok() || !s?.data) return null;
    try { return (s.data.getItem(key) as string | null) ?? null; } catch (e) { console.warn('[platform] data.getItem', e); return null; }
  }
  async set(key: string, value: string) {
    const s = S();
    if (!this.ok() || !s?.data) return;
    try { s.data.setItem(key, value); } catch (e) { console.warn('[platform] data.setItem', e); }
  }
}

export class CrazyGamesPlatform implements Platform {
  readonly id = 'crazygames' as const;
  private inited = false;
  readonly storage = new CGStore(() => this.inited);
  readonly purchases = NO_PURCHASES;
  private pause = new Listeners<boolean>();
  private audio = new Listeners<boolean>();
  private loading = false;
  private playing = false;
  private muted = false;

  get language() {
    const loc = this.inited ? (S()?.user?.systemInfo?.locale as string | undefined) : undefined;
    return (loc && loc.slice(0, 2).toLowerCase()) || 'en';
  }
  get audioEnabled() { return !this.muted; }

  readonly ads = {
    get rewardedAvailable() { return F.rewarded && !!S()?.ad; },
    banner: (_show: boolean) => { /* CG banners need an own container (requestResponsiveBanner); add only on Full Launch menus */ },
    interstitial: async (placement: string) => { if (F.interstitial) await this.requestAd('midgame', placement); },
    rewarded: async (placement: string) => (F.rewarded ? this.requestAd('rewarded', placement) : false),
  };

  async init() {
    if (!S()) await loadScript(SDK_URL);
    const s = S();
    if (!s) throw new Error('CrazyGames SDK missing');
    await s.init();
    if (s.environment === 'disabled') throw new Error('CrazyGames SDK disabled on this domain');
    this.inited = true;
    try {
      this.muted = !!s.game?.settings?.muteAudio;
      s.game?.addSettingsChangeListener?.((st: { muteAudio?: boolean }) => {
        const m = !!st?.muteAudio;
        if (m !== this.muted) { this.muted = m; this.audio.emit(!m); }
      });
    } catch (e) { console.warn('[platform] settings', e); }
  }

  private call(fn: string) { try { S()?.game?.[fn]?.(); } catch (e) { console.warn('[platform]', fn, e); } }
  loadingStart() { if (this.inited && !this.loading) { this.loading = true; this.call('loadingStart'); } }
  loadingStop() { if (this.inited && this.loading) { this.loading = false; this.call('loadingStop'); } }
  gameplayStart() { if (this.inited && !this.playing) { this.playing = true; this.call('gameplayStart'); } }
  gameplayStop() { if (this.inited && this.playing) { this.playing = false; this.call('gameplayStop'); } }
  happytime() { if (this.inited) this.call('happytime'); }
  onPause(cb: (p: boolean) => void) { this.pause.add(cb); }
  onAudio(cb: (e: boolean) => void) { this.audio.add(cb); }

  private requestAd(type: 'midgame' | 'rewarded', _placement: string): Promise<boolean> {
    const s = S();
    if (!this.inited || !s?.ad) return Promise.resolve(false);
    return new Promise<boolean>((resolve) => {
      let started = false, done = false;
      const end = (granted: boolean) => {
        if (done) return; done = true;
        if (started) this.pause.emit(false);
        resolve(granted);
      };
      try {
        s.ad.requestAd(type, {
          adStarted: () => { started = true; this.pause.emit(true); },
          adFinished: () => end(type === 'rewarded'),
          adError: () => end(false),
        });
      } catch (e) { console.warn('[platform] requestAd', e); end(false); }
      setTimeout(() => end(false), 90000);
    });
  }
}
