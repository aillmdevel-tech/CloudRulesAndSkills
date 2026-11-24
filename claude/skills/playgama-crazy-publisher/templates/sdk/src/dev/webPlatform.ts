import { FEATURES } from '../platform/config';
import { Listeners, type Platform, type PlatformPurchases, type PlatformStorage, type Product } from '../platform/types';

/**
 * Local / dev build (npm run dev, npm run build): browser localStorage, no SDK.
 * Lives in src/dev because platform moderators grep src/ for localStorage (src/dev is excluded).
 * QA flags: ?fakeads=1 scripted ads with an overlay, ?fakeiap=1 scripted shop, ?adfail=1 every ad fails,
 * ?iapfail=1 every purchase is cancelled. window.__platform.log records every call for pub sdk-run and smoke.
 */
const Q = new URLSearchParams(location.search);
const F = FEATURES.web;

class LocalStore implements PlatformStorage {
  async get(key: string) { try { return localStorage.getItem(key); } catch { return null; } }
  async set(key: string, value: string) { try { localStorage.setItem(key, value); } catch { /* blocked or full */ } }
}

export class WebPlatform implements Platform {
  readonly id = 'web' as const;
  readonly language = (Q.get('lang') || navigator.language || 'en').slice(0, 2).toLowerCase();
  readonly audioEnabled = !Q.has('muted');
  readonly storage = new LocalStore();
  readonly log: string[] = [];
  private fakeAds = Q.has('fakeads');
  private adFail = Q.has('adfail');
  private bannerOn = false;
  private lastInter = -1e9;
  private pause = new Listeners<boolean>();
  private audio = new Listeners<boolean>();

  readonly ads = {
    rewardedAvailable: this.fakeAds && F.rewarded,
    banner: (show: boolean) => {
      if (!F.banner || show === this.bannerOn) return;
      this.bannerOn = show; this.log.push('banner:' + show);
      if (this.fakeAds) this.fakeBanner(show);
    },
    interstitial: async (placement: string) => {
      if (!F.interstitial) return;
      this.log.push('interstitial:' + placement);
      if (!this.fakeAds || performance.now() - this.lastInter < 60000) return; // Bridge spaces interstitials ≥ 60 s
      this.lastInter = performance.now();
      await this.fakeAd('AD · ' + placement);
    },
    rewarded: async (placement: string) => {
      if (!F.rewarded) return false;
      this.log.push('rewarded:' + placement);
      return this.fakeAds ? this.fakeAd('REWARDED AD · ' + placement) : false;
    },
  };

  readonly purchases: PlatformPurchases = (() => {
    const on = F.iap && Q.has('fakeiap'), fail = Q.has('iapfail'), KEY = '__fake_iap';
    const read = (): string[] => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } };
    const write = (v: string[]) => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch { /* */ } };
    return {
      supported: on,
      catalog: async (): Promise<Product[]> => (on ? FAKE_CATALOG : []),
      purchase: async (id: string) => {
        this.log.push('purchase:' + id);
        if (!on || fail) return false;
        write([...read(), id]); return true;
      },
      consume: async (id: string) => {
        this.log.push('consume:' + id);
        const v = read(); const i = v.indexOf(id); if (i >= 0) { v.splice(i, 1); write(v); }
      },
      owned: async () => { this.log.push('owned'); return on ? read() : []; },
    };
  })();

  async init() { this.log.push('init'); }
  loadingStart() { this.log.push('loadingStart'); }
  loadingStop() { this.log.push('loadingStop'); }
  gameplayStart() { this.log.push('gameplayStart'); }
  gameplayStop() { this.log.push('gameplayStop'); }
  happytime() { this.log.push('happytime'); }
  onPause(cb: (p: boolean) => void) { this.pause.add(cb); }
  onAudio(cb: (e: boolean) => void) { this.audio.add(cb); }
  /** QA hooks: emulate platform events */
  emitPause(p: boolean) { this.log.push('pause:' + p); this.pause.emit(p); }
  emitAudio(e: boolean) { this.log.push('audio:' + e); this.audio.emit(e); }

  private fakeAd(text: string): Promise<boolean> {
    const el = document.createElement('div');
    el.id = 'fake-ad'; el.textContent = this.adFail ? text + ' · FAILED' : text;
    el.style.cssText = 'position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;background:rgba(20,20,24,.92);color:#fff;font:700 32px sans-serif';
    document.body.append(el);
    if (this.adFail) return new Promise((r) => setTimeout(() => { el.remove(); this.log.push('ad:failed'); r(false); }, 400));
    this.pause.emit(true);
    return new Promise((r) => setTimeout(() => { el.remove(); this.pause.emit(false); this.log.push('ad:done'); r(true); }, 1500));
  }
  private fakeBanner(show: boolean) {
    let el = document.getElementById('fake-banner');
    if (!show) { el?.remove(); return; }
    if (el) return;
    el = document.createElement('div');
    el.id = 'fake-banner'; el.textContent = 'BANNER 728×90';
    el.style.cssText = 'position:fixed;left:50%;bottom:0;translate:-50% 0;width:min(728px,100vw);height:90px;z-index:9998;display:flex;align-items:center;justify-content:center;background:#c9ccd3;color:#333;font:700 18px sans-serif;pointer-events:none';
    document.body.append(el);
  }
}

/** fill from publish/STATE.json sdk.products (pub sdk-config writes the same ids into playgama-bridge-config.json) */
const FAKE_CATALOG: Product[] = /*PRODUCTS*/[]/*END*/;
