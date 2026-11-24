import { FEATURES } from './config';
import { Listeners, NO_PURCHASES, type Platform, type PlatformPurchases, type PlatformStorage, type Product } from './types';

/**
 * Playgama Bridge 2.x. playgama-bridge.js is the first <script> in <head> of the playgama build
 * (vite.config.ts: @playgama/bridge/vite in 'local' mode), so window.bridge exists before the game module runs.
 * Config: public/playgama-bridge-config.json (placements, payments, minimumDelayBetweenInterstitial).
 * Rules: initialize first; game_ready only when the player can interact; language from platform.language;
 * saves only via bridge.storage; isAudioEnabled + AUDIO_STATE_CHANGED / PAUSE_STATE_CHANGED; ads and payments only via Bridge.
 */
type Bridge = any;
const B = (): Bridge | undefined => (window as any).bridge;
const F = FEATURES.playgama;

class BridgeStore implements PlatformStorage {
  async get(key: string) {
    const b = B();
    if (!b?.storage) return null;
    try {
      const v = await b.storage.get(key);
      if (v == null || v === '') return null;
      return typeof v === 'string' ? v : JSON.stringify(v);
    } catch (e) { console.warn('[platform] storage.get', e); return null; }
  }
  async set(key: string, value: string) {
    const b = B();
    if (!b?.storage) return;
    try { await b.storage.set(key, value); } catch (e) { console.warn('[platform] storage.set', e); }
  }
}

class BridgePurchases implements PlatformPurchases {
  get supported() { return F.iap && !!B()?.payments?.isSupported; }
  async catalog(): Promise<Product[]> {
    if (!this.supported) return [];
    try { return ((await B().payments.getCatalog()) || []).map((p: any) => ({ id: p.id, price: p.price ?? '' })); }
    catch (e) { console.warn('[platform] getCatalog', e); return []; }
  }
  async purchase(id: string) {
    if (!this.supported) return false;
    try { const r = await B().payments.purchase(id); return !!r; }
    catch (e) { console.warn('[platform] purchase', id, e); return false; }
  }
  async consume(id: string) {
    if (!this.supported) return;
    try { await B().payments.consumePurchase(id); } catch (e) { console.warn('[platform] consumePurchase', id, e); }
  }
  async owned() {
    if (!this.supported) return [];
    try { return ((await B().payments.getPurchases()) || []).map((p: any) => String(p.id)); }
    catch (e) { console.warn('[platform] getPurchases', e); return []; }
  }
}

export class PlaygamaPlatform implements Platform {
  readonly id = 'playgama' as const;
  readonly storage = new BridgeStore();
  readonly purchases: PlatformPurchases = F.iap ? new BridgePurchases() : NO_PURCHASES;
  private pause = new Listeners<boolean>();
  private audio = new Listeners<boolean>();
  private ready = false;
  private playing = false;
  private adOpen = false;
  private adBusy = false;
  private bannerOn = false;

  get language() { const b = B(); return (b ? (b.platform.language as string | undefined) : undefined) || 'en'; }
  get audioEnabled() { const b = B(); return b ? b.platform.isAudioEnabled !== false : true; }

  readonly ads = {
    get rewardedAvailable() { return F.rewarded && !!B()?.advertisement?.isRewardedSupported; },
    banner: (show: boolean) => {
      const a = B()?.advertisement;
      if (!F.banner || !a?.isBannerSupported || show === this.bannerOn) return;
      this.bannerOn = show;
      try { if (show) a.showBanner('bottom', 'menu'); else a.hideBanner(); } catch (e) { console.warn('[platform] banner', e); }
    },
    interstitial: async (placement: string) => {
      const b = B();
      if (!F.interstitial || this.adBusy || !b?.advertisement?.isInterstitialSupported) return;
      await this.runAd('interstitial', () => b.advertisement.showInterstitial(placement));
    },
    rewarded: async (placement: string) => {
      const b = B();
      if (!F.rewarded || this.adBusy || !b?.advertisement?.isRewardedSupported) return false;
      return this.runAd('rewarded', () => b.advertisement.showRewarded(placement));
    },
  };

  async init() {
    const b = B();
    if (!b) throw new Error('window.bridge missing (playgama-bridge.js not loaded)');
    await b.initialize();
    const E = b.EVENT_NAME;
    b.platform.on(E.PAUSE_STATE_CHANGED, (paused: boolean) => this.pause.emit(!!paused));
    b.platform.on(E.AUDIO_STATE_CHANGED, (on: boolean) => this.audio.emit(!!on));
  }

  private send(msg: string) {
    try { void B()?.platform?.sendMessage(msg)?.catch?.(() => {}); } catch { /* platform without messages */ }
  }

  loadingStart() { if (this.ready) this.send('in_game_loading_started'); }
  loadingStop() {
    if (!this.ready) { this.ready = true; this.send('game_ready'); }
    else this.send('in_game_loading_stopped');
  }
  gameplayStart() { if (!this.playing) { this.playing = true; this.send('gameplay_started'); } }
  gameplayStop() { if (this.playing) { this.playing = false; this.send('gameplay_stopped'); } }
  happytime() { /* Bridge has no happytime */ }
  onPause(cb: (p: boolean) => void) { this.pause.add(cb); }
  onAudio(cb: (e: boolean) => void) { this.audio.add(cb); }

  /** pauses the game while the ad is open; true when a rewarded ad reached 'rewarded'. Never leaves the game paused. */
  private runAd(kind: 'interstitial' | 'rewarded', show: () => void): Promise<boolean> {
    const b = B(); const E = b.EVENT_NAME;
    const ev = kind === 'interstitial' ? E.INTERSTITIAL_STATE_CHANGED : E.REWARDED_STATE_CHANGED;
    this.adBusy = true;
    return new Promise<boolean>((resolve) => {
      let rewarded = false, done = false;
      const finish = () => {
        if (done) return; done = true;
        b.advertisement.off?.(ev, onState);
        this.adBusy = false;
        if (this.adOpen) { this.adOpen = false; this.pause.emit(false); }
        resolve(rewarded);
      };
      const onState = (s: string) => {
        if (s === 'opened') { this.adOpen = true; this.pause.emit(true); }
        else if (s === 'rewarded') rewarded = true;
        else if (s === 'closed' || s === 'failed') finish();
      };
      b.advertisement.on(ev, onState);
      try { show(); } catch (e) { console.warn('[platform] ad', e); finish(); }
      setTimeout(finish, 90000);
    });
  }
}
