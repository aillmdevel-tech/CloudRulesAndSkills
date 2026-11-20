// Promo hooks: tiny, safe in prod. Without game-promo-kit `window.__promo` is undefined and nothing happens.
// 1) report juicy moments where they happen (weight 1..5):
//      promoEvent('combo', 3, 'x5');  promoEvent('levelup', 4);  promoEvent('boss_kill', 5);
// 2) director mode: hide HUD/cursor/dev UI, keep the game running (camera fly-through is optional).
type PromoApi = { event?: (type: string, weight?: number, label?: string) => void; director?: (on: boolean) => void };
const promo = (): PromoApi | undefined => (window as unknown as { __promo?: PromoApi }).__promo;

export function promoEvent(type: string, weight = 1, label = ''): void {
  promo()?.event?.(type, weight, label);
}

export function installPromoDirector(opts: { hud: () => HTMLElement[]; onToggle?: (on: boolean) => void }): void {
  const p = promo();
  if (!p) return;
  p.director = (on: boolean) => {
    for (const el of opts.hud()) el.style.visibility = on ? 'hidden' : '';
    document.body.style.cursor = on ? 'none' : '';
    opts.onToggle?.(on);
  };
}
