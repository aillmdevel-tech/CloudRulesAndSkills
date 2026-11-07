// Injected before the game (add_init_script). Wraps window.bridge in a Proxy: records Bridge calls and
// localStorage use; with __spy.emulate the ad calls are answered by a scripted ad (opened → rewarded → closed).
(() => {
  const S = window.__spy = { msgs: [], ads: [], storage: [], ls: [], adLog: [], emulate: false, adMs: 1500, rewardedMode: 'ok', interstitialMode: 'ok', probe: null, t0: performance.now() };
  const t = () => Math.round(performance.now() - S.t0);
  for (const n of ['setItem', 'getItem', 'removeItem']) {
    const o = Storage.prototype[n];
    Storage.prototype[n] = function (...a) { S.ls.push([n, String(a[0]), this === window.localStorage ? 'local' : 'session']); return o.apply(this, a); };
  }
  let real, wrapped;
  const emulateAd = (kind, states, placement) => {
    const ad = real.advertisement._platformBridge; const set = kind === 'interstitial' ? '_setInterstitialState' : '_setRewardedState';
    const rec = (s) => S.adLog.push({ kind, state: s, t: t(), ...(S.probe ? S.probe() : {}) });
    rec('requested'); // before the ad opens: game must still run and be audible (CrazyGames: mute only when the ad really plays)
    setTimeout(() => { ad[set](states[0]); rec(states[0]); }, 150);
    setTimeout(() => rec('mid'), 150 + S.adMs * 0.6);
    let d = 150 + S.adMs;
    states.slice(1).forEach((s) => { setTimeout(() => { ad[set](s); rec(s); }, d); d += 100; });
    setTimeout(() => rec('after'), d + 900);
  };
  const hook = (mod, fn, a) => {
    if (mod === 'platform' && fn === 'sendMessage') S.msgs.push([a[0], t(), real.isInitialized === true]);
    else if (mod === 'storage' && (fn === 'get' || fn === 'set')) S.storage.push([fn, a[0], t()]);
    else if (mod === 'advertisement') {
      if (fn === 'showBanner' || fn === 'hideBanner') S.ads.push([fn, a[0], t()]);
      else if (fn === 'showInterstitial' || fn === 'showRewarded') {
        const kind = fn === 'showInterstitial' ? 'interstitial' : 'rewarded';
        S.ads.push([kind, a[0], t()]);
        if (S.emulate) {
          if (kind === 'interstitial') emulateAd(kind, S.interstitialMode === 'fail' ? ['failed'] : ['opened', 'closed'], a[0]);
          else emulateAd(kind, S.rewardedMode === 'fail' ? ['failed'] : S.rewardedMode === 'skip' ? ['opened', 'closed'] : ['opened', 'rewarded', 'closed'], a[0]);
          return 'skip';
        }
      }
    }
  };
  const sub = (name, mod) => new Proxy(mod, { get(tg, k) {
    if (name === 'advertisement' && S.emulate && (k === 'isRewardedSupported' || k === 'isInterstitialSupported' || k === 'isBannerSupported')) return true;
    const v = Reflect.get(tg, k);
    if (typeof v !== 'function') return v;
    return (...a) => (hook(name, k, a) === 'skip' ? undefined : v.apply(tg, a));
  } });
  Object.defineProperty(window, 'bridge', {
    configurable: true,
    get() {
      if (!real) return undefined;
      return wrapped || (wrapped = new Proxy(real, { get(tg, k) {
        const v = Reflect.get(tg, k);
        if (k === 'platform' || k === 'advertisement' || k === 'storage') return sub(k, v);
        return typeof v === 'function' ? v.bind(tg) : v;
      } }));
    },
    set(v) { real = v; wrapped = null; },
  });
})();
