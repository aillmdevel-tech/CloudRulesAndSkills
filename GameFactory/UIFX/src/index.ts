// GameFactory UIFX — game UI motion + sound. Zero dependencies. Import './uifx.css' once.
//
//   const fx = await createUIFX({ style: 'roblox-cartoon', soundsUrl: '/assets/audio/ui/' });
//   fx.button(playBtn);                 // hover + press + sounds from the style
//   await fx.open(shopWindow, { backdrop: overlay, camera: sceneEl });
//   fx.reward.coins(chestEl, coinCounterEl, 120);
//   fx.override('button.press', { sound: 'click_soft' });   // per-game tweak from references
//
// Declarative: <button data-uifx="button">, <button data-uifx="button cta">, <div data-uifx="list">

import { configure, config, prefersReducedMotion, type UIFXConfig } from './core/config';
import { EFFECTS, countUp, flyTo, type Handle, type Params } from './effects';
import { SoundManager } from './sound';
import { STYLES, type FxSlot, type UIEvent, type StylePreset } from './styles';
import { interrupt } from './core/animate';

export * from './core/config';
export * from './core/spring';
export * from './core/animate';
export * from './effects';
export * from './sound';
export * from './styles';

export interface CreateOptions {
  style?: string | StylePreset;
  /** Folder with sounds.json + <id>.ogg/.mp3. Omit for silent mode. */
  soundsUrl?: string;
  config?: Partial<UIFXConfig>;
  /** Per-event overrides applied on top of the style. */
  overrides?: Partial<Record<UIEvent, Partial<FxSlot>>>;
}

type RunAny = Animation | Promise<unknown> | Handle | void;

const settle = async (r: RunAny): Promise<void> => {
  if (!r) return;
  if (r instanceof Promise) await r.catch(() => {});
  else if ('finished' in r) await r.finished.catch(() => {});
};

export class UIFX {
  slots!: Record<UIEvent, FxSlot>;
  style!: StylePreset;
  private attached = new WeakMap<HTMLElement, Handle[]>();

  constructor(
    public sound: SoundManager | null,
    style: string | StylePreset = 'roblox-cartoon',
    private baseOverrides: CreateOptions['overrides'] = {},
  ) {
    this.setStyle(style);
  }

  setStyle(style: string | StylePreset): void {
    this.style = typeof style === 'string' ? STYLES[style] ?? STYLES['roblox-cartoon'] : style;
    this.slots = structuredClone(this.style.slots);
    configure({ intensity: 1, speed: 1, ...this.style.config });
    for (const [k, v] of Object.entries(this.baseOverrides ?? {})) this.override(k as UIEvent, v!);
  }

  /** Change one event's effect / params / sound. Params merge with the current ones. */
  override(event: UIEvent, patch: Partial<FxSlot>): void {
    const cur = this.slots[event];
    this.slots[event] = {
      ...cur,
      ...patch,
      params: patch.effect && patch.effect !== cur.effect ? patch.params : { ...cur.params, ...patch.params },
    };
  }

  /** Effective params of an event = effect defaults + style params + call-site params. */
  params(event: UIEvent, extra?: Params): Params {
    const s = this.slots[event];
    const def = EFFECTS[s.effect];
    return { ...(def?.defaults ?? {}), ...s.params, ...extra };
  }

  /** Fire a semantic event on an element: plays its effect and sound. */
  trigger(event: UIEvent, el?: HTMLElement | null, extra?: Params, ev?: { clientX: number; clientY: number }): RunAny {
    const s = this.slots[event];
    if (s.sound && s.sound !== 'none') void this.sound?.play(s.sound);
    const def = EFFECTS[s.effect];
    if (!def || !el) return;
    return def.run(el, this.params(event, extra), ev);
  }

  /** Run any effect by id with params (for one-off use). */
  play(effectId: string, el: HTMLElement, params?: Params): RunAny {
    const def = EFFECTS[effectId];
    if (!def) throw new Error(`[uifx] unknown effect ${effectId}`);
    return def.run(el, { ...def.defaults, ...params });
  }

  // ---------------------------------------------------------------- high-level helpers
  /** Make an element a juicy button: hover + press effect + sounds. `cta` adds the attention loop. */
  button(el: HTMLElement, o: { cta?: boolean } = {}): Handle {
    this.unbind(el);
    const handles: Handle[] = [];
    for (const ev of ['button.hover', 'button.press'] as const) {
      const def = EFFECTS[this.slots[ev].effect];
      if (def?.attach) handles.push(def.attach(el, () => this.params(ev)));
    }
    const hoverSound = () => this.slotSound('button.hover');
    const pressSound = () => this.slotSound('button.press');
    const clickSound = () => this.slotSound('button.click');
    const disabled = () => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
    const onEnter = (e: PointerEvent) => e.pointerType === 'mouse' && !disabled() && hoverSound();
    const onDown = () => (disabled() ? this.trigger('error', el) : pressSound());
    const onClick = () => !disabled() && clickSound();
    el.addEventListener('pointerenter', onEnter);
    el.addEventListener('pointerdown', onDown);
    el.addEventListener('click', onClick);
    handles.push({
      stop: () => {
        el.removeEventListener('pointerenter', onEnter);
        el.removeEventListener('pointerdown', onDown);
        el.removeEventListener('click', onClick);
      },
    });
    if (o.cta) {
      const r = this.trigger('button.cta', el);
      if (r && 'stop' in r) handles.push(r);
    }
    this.attached.set(el, handles);
    return { stop: () => this.unbind(el) };
  }

  unbind(el: HTMLElement): void {
    this.attached.get(el)?.forEach((h) => h.stop());
    this.attached.delete(el);
  }

  /** Open a window/popup: optional backdrop + camera zoom + content stagger. */
  async open(win: HTMLElement, o: { backdrop?: HTMLElement; camera?: HTMLElement; list?: HTMLElement } = {}): Promise<void> {
    win.hidden = false;
    if (o.backdrop) {
      o.backdrop.hidden = false;
      this.trigger('window.backdrop', o.backdrop, { mode: 'show' });
    }
    if (o.camera) this.trigger('window.camera', o.camera);
    const main = this.trigger('window.open', win);
    if (o.list) void settle(this.trigger('list.in', o.list));
    await settle(main);
  }

  async close(win: HTMLElement, o: { backdrop?: HTMLElement; camera?: HTMLElement } = {}): Promise<void> {
    if (o.backdrop) this.trigger('window.backdrop', o.backdrop, { mode: 'hide' });
    if (o.camera && this.slots['window.camera'].effect === 'cameraZoom') EFFECTS.cameraZoom.run(o.camera, { ...this.params('window.camera'), mode: 'out' });
    await settle(this.trigger('window.close', win));
    win.hidden = true;
    if (o.backdrop) o.backdrop.hidden = true;
    for (const ch of ['pop', 'fade', 'slide']) interrupt(win, ch);
    win.style.scale = win.style.opacity = win.style.translate = win.style.rotate = '';
  }

  async panelIn(el: HTMLElement, from?: 'left' | 'right' | 'top' | 'bottom') {
    el.hidden = false;
    await settle(this.trigger('panel.in', el, from ? { from } : undefined));
  }

  async panelOut(el: HTMLElement, to?: 'left' | 'right' | 'top' | 'bottom') {
    await settle(this.trigger('panel.out', el, to ? { to } : undefined));
    el.hidden = true;
    for (const ch of ['slide', 'fade']) interrupt(el, ch);
    el.style.opacity = el.style.translate = '';
  }

  toggle(el: HTMLElement, on: boolean) {
    return this.trigger(on ? 'toggle.on' : 'toggle.off', el);
  }

  async toast(el: HTMLElement, holdMs = 2200): Promise<void> {
    el.hidden = false;
    await settle(this.trigger('toast.in', el));
    await new Promise((r) => setTimeout(r, holdMs));
    await settle(EFFECTS.popOut.run(el, { ...EFFECTS.popOut.defaults, duration: 160 }));
    el.hidden = true;
  }

  notify = (el: HTMLElement) => this.trigger('notify', el);
  success = (el?: HTMLElement) => this.trigger('success', el);
  error = (el?: HTMLElement) => this.trigger('error', el);
  levelUp = (titleEl: HTMLElement) => {
    const r = this.trigger('levelUp', titleEl);
    if (this.slots['reward.big'].effect === 'confetti') EFFECTS.confetti.run(titleEl, this.params('reward.big'));
    return r;
  };

  reward = {
    /** Item obtained: pop + sparkle + sound. */
    item: (el: HTMLElement) => this.trigger('reward.item', el),
    /** Coins fly from `from` into `counter`, then the counter counts up to `newTotal`. */
    coins: async (from: HTMLElement, counter: HTMLElement, newTotal: number, count = 10) => {
      const coinSound = this.slots['reward.coins'].sound;
      let i = 0;
      await flyTo(from, counter, {
        count: prefersReducedMotion() ? 1 : count,
        ...this.slotParams('reward.coins'),
        onArrive: () => {
          if (coinSound && coinSound !== 'none') void this.sound?.play(coinSound, { pitch: Math.min(7, i++ * 0.5), cooldown: 20 });
          EFFECTS.punch.run(counter, { ...EFFECTS.punch.defaults, scale: 0.15 });
        },
      });
      await this.reward.count(counter, newTotal);
    },
    /** Number counts up with ticking sound. */
    count: (el: HTMLElement, to: number, o: { duration?: number } = {}) => {
      const tick = this.slots['reward.count'].sound;
      return countUp(el, {
        to,
        duration: o.duration ?? 800,
        onTick: tick && tick !== 'none' ? () => void this.sound?.play(tick, { cooldown: 35 }) : undefined,
      });
    },
    /** Big moment: confetti from the element. */
    big: (el: HTMLElement) => this.trigger('reward.big', el),
  };

  /**
   * Declarative binding: data-uifx="button" | "button cta" | "list" | "notify" | "title".
   * Watches for new nodes; returns a handle to stop observing.
   */
  bind(root: ParentNode = document): Handle {
    const apply = (el: HTMLElement) => {
      const kinds = (el.dataset.uifx ?? '').split(/\s+/);
      if (el.dataset.uifxBound) return;
      el.dataset.uifxBound = '1';
      if (kinds.includes('button')) this.button(el, { cta: kinds.includes('cta') });
      if (kinds.includes('notify')) this.notify(el);
      if (kinds.includes('title')) this.trigger('title.in', el);
    };
    root.querySelectorAll<HTMLElement>('[data-uifx]').forEach(apply);
    const mo = new MutationObserver((muts) =>
      muts.forEach((m) =>
        m.addedNodes.forEach((n) => {
          if (!(n instanceof HTMLElement)) return;
          if (n.dataset.uifx) apply(n);
          n.querySelectorAll?.<HTMLElement>('[data-uifx]').forEach(apply);
        }),
      ),
    );
    mo.observe(root instanceof Document ? root.body : (root as Node), { childList: true, subtree: true });
    return { stop: () => mo.disconnect() };
  }

  /** Current configuration as JSON — paste into a game's uifx config. */
  exportConfig(): string {
    return JSON.stringify({ style: this.style.id, config: { ...config }, slots: this.slots }, null, 2);
  }

  private slotSound(ev: UIEvent) {
    const s = this.slots[ev].sound;
    if (s && s !== 'none') void this.sound?.play(s);
  }

  private slotParams(ev: UIEvent): Params {
    return { ...this.slots[ev].params };
  }
}

export async function createUIFX(o: CreateOptions = {}): Promise<UIFX> {
  let sound: SoundManager | null = null;
  if (o.soundsUrl) {
    try {
      sound = await SoundManager.load(o.soundsUrl);
    } catch (e) {
      console.warn('[uifx] sounds disabled:', e);
    }
  }
  const fx = new UIFX(sound, o.style, o.overrides);
  if (o.config) configure(o.config);
  return fx;
}
