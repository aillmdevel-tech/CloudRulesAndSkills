// Style presets: map semantic UI events to an effect (+ params) and a sound.
// A game picks one preset, then overrides individual events from its references.
import type { Params } from './effects/types';
import type { UIFXConfig } from './core/config';

export interface FxSlot {
  /** Effect id from EFFECTS, or 'none'. */
  effect: string;
  params?: Params;
  /** Sound id from sounds.json, or 'none'. */
  sound?: string;
}

export type UIEvent =
  | 'button.hover'
  | 'button.press'
  | 'button.click'
  | 'button.cta' // attention loop on the main call-to-action
  | 'window.open'
  | 'window.close'
  | 'window.backdrop'
  | 'window.camera'
  | 'panel.in'
  | 'panel.out'
  | 'list.in'
  | 'toast.in'
  | 'toggle.on'
  | 'toggle.off'
  | 'tab.change'
  | 'notify'
  | 'success'
  | 'error'
  | 'reward.item'
  | 'reward.coins'
  | 'reward.count'
  | 'reward.big'
  | 'levelUp'
  | 'title.in';

export interface StylePreset {
  id: string;
  name: string;
  description: string;
  config?: Partial<UIFXConfig>;
  slots: Record<UIEvent, FxSlot>;
}

const base: Record<UIEvent, FxSlot> = {
  'button.hover': { effect: 'hoverLift', params: { lift: 3, scale: 0.04 }, sound: 'hover' },
  'button.press': { effect: 'jellyPress', sound: 'click' },
  'button.click': { effect: 'none', sound: 'none' },
  'button.cta': { effect: 'glossyShine' },
  'window.open': { effect: 'popIn', sound: 'open' },
  'window.close': { effect: 'popOut', sound: 'close' },
  'window.backdrop': { effect: 'backdrop', params: { blur: 6, dim: 0.35 } },
  'window.camera': { effect: 'none' },
  'panel.in': { effect: 'slideIn', sound: 'whoosh_in' },
  'panel.out': { effect: 'slideOut', sound: 'whoosh_out' },
  'list.in': { effect: 'stagger', params: { each: 50, effect: 'popIn' } },
  'toast.in': { effect: 'dropIn', sound: 'notify' },
  'toggle.on': { effect: 'punch', params: { scale: 0.12 }, sound: 'toggle_on' },
  'toggle.off': { effect: 'punch', params: { scale: -0.08 }, sound: 'toggle_off' },
  'tab.change': { effect: 'punch', params: { scale: 0.08 }, sound: 'select' },
  notify: { effect: 'heartbeat', sound: 'notify' },
  success: { effect: 'punch', params: { scale: 0.2 }, sound: 'success' },
  error: { effect: 'shake', sound: 'error' },
  'reward.item': { effect: 'rewardPop', sound: 'reward' },
  'reward.coins': { effect: 'coinFly', sound: 'coin' },
  'reward.count': { effect: 'countUp', sound: 'counter_tick' },
  'reward.big': { effect: 'confetti', sound: 'confetti' },
  levelUp: { effect: 'textWave', sound: 'level_up' },
  'title.in': { effect: 'textWave', sound: 'none' },
};

const merge = (o: Partial<Record<UIEvent, FxSlot>>): Record<UIEvent, FxSlot> => ({ ...base, ...o });

export const STYLES: Record<string, StylePreset> = {
  'roblox-cartoon': {
    id: 'roblox-cartoon',
    name: 'Roblox Cartoon',
    description: 'Крупные пружинные реакции, желейные кнопки, pop-in окна, монеты летят в счётчик, конфетти. Звуки — мультяшные.',
    config: { intensity: 1.1 },
    slots: merge({
      'button.hover': { effect: 'hoverLift', params: { lift: 4, scale: 0.06, stiffness: 500, damping: 18 }, sound: 'hover_bubble' },
      'button.press': { effect: 'jellyPress', params: { squashX: 0.16, squashY: 0.2, stiffness: 420, damping: 9 }, sound: 'jelly_click' },
      'window.open': { effect: 'popIn', params: { fromScale: 0.4, rotate: -4, stiffness: 520, damping: 13 }, sound: 'pop' },
      'window.close': { effect: 'popOut', params: { anticipation: 0.06 }, sound: 'close' },
      'window.camera': { effect: 'cameraZoom', params: { zoom: 0.05, mode: 'in' } },
      'list.in': { effect: 'stagger', params: { each: 45, effect: 'popIn', fromScale: 0.3, stiffness: 520, damping: 13 } },
      error: { effect: 'shake', params: { distance: 12 }, sound: 'error_soft' },
      'reward.item': { effect: 'rewardPop', params: { scale: 0.4, rotate: 10 }, sound: 'reward' },
    }),
  },
  'playful-jelly': {
    id: 'playful-jelly',
    name: 'Playful Jelly',
    description: 'Максимум упругости: всё желейное и покачивается, squash & stretch, мягкие пузырьковые звуки.',
    config: { intensity: 1.25 },
    slots: merge({
      'button.hover': { effect: 'hoverTilt', params: { scale: 0.08, angle: 6, glare: 0.2, stiffness: 300, damping: 14 }, sound: 'hover_bubble' },
      'button.press': { effect: 'jellyPress', params: { squashX: 0.2, squashY: 0.24, stiffness: 380, damping: 7 }, sound: 'jelly_click' },
      'button.click': { effect: 'none', sound: 'jelly_release' },
      'window.open': { effect: 'popIn', params: { fromScale: 0.3, rotate: 6, stiffness: 420, damping: 9 }, sound: 'pop' },
      'toggle.on': { effect: 'squashStretch', params: { height: 10, duration: 450 }, sound: 'squish' },
      'list.in': { effect: 'stagger', params: { each: 55, effect: 'popIn', fromScale: 0.2, stiffness: 400, damping: 9 } },
      notify: { effect: 'wiggle', params: { angle: 14, once: 1 }, sound: 'notify_chime' },
      error: { effect: 'shake', params: { distance: 10, shakes: 5 }, sound: 'error_soft' },
      'reward.item': { effect: 'rewardPop', params: { scale: 0.5, rotate: 14, damping: 7 }, sound: 'reward' },
      success: { effect: 'squashStretch', params: { height: 18 }, sound: 'success_chime' },
    }),
  },
  'casual-soft': {
    id: 'casual-soft',
    name: 'Casual Soft',
    description: 'Мягкие, медленнее и тише: плавные подъёмы, slide панели, лёгкое размытие, колокольчики.',
    config: { intensity: 0.8, speed: 0.9 },
    slots: merge({
      'button.hover': { effect: 'hoverLift', params: { lift: 3, scale: 0.03, stiffness: 260, damping: 24 }, sound: 'none' },
      'button.press': { effect: 'jellyPress', params: { squashX: 0.06, squashY: 0.08, stiffness: 300, damping: 16 }, sound: 'click_soft' },
      'window.open': { effect: 'popIn', params: { fromScale: 0.85, stiffness: 260, damping: 22, fadeMs: 220 }, sound: 'open_alt' },
      'window.close': { effect: 'popOut', params: { anticipation: 0, toScale: 0.92, duration: 220, ease: 'out' }, sound: 'close_alt' },
      'window.backdrop': { effect: 'backdrop', params: { blur: 10, dim: 0.2 } },
      'panel.in': { effect: 'slideIn', params: { distance: 60, stiffness: 220, damping: 26 }, sound: 'whoosh_in' },
      'list.in': { effect: 'stagger', params: { each: 70, effect: 'slideUp', stiffness: 260, damping: 24 } },
      notify: { effect: 'glow', params: { color: 'white', size: 14, period: 2200 }, sound: 'notify_chime' },
      success: { effect: 'punch', params: { scale: 0.1 }, sound: 'success_chime' },
      error: { effect: 'shake', params: { distance: 6, shakes: 3 }, sound: 'error_soft' },
      'reward.big': { effect: 'confetti', params: { count: 70, power: 700 }, sound: 'sparkle' },
    }),
  },
  arcade: {
    id: 'arcade',
    name: 'Arcade',
    description: 'Быстро и резко: короткие тайминги, вспышки, тряска, ретро-звуки power-up, крупные числа.',
    config: { intensity: 1.15, speed: 1.3 },
    slots: merge({
      'button.hover': { effect: 'hoverLift', params: { lift: 2, scale: 0.08, stiffness: 900, damping: 30 }, sound: 'tick' },
      'button.press': { effect: 'pressDepth', params: { depth: 5, stiffness: 900, damping: 20 }, sound: 'click' },
      'window.open': { effect: 'popIn', params: { fromScale: 0.6, stiffness: 900, damping: 22, fadeMs: 60 }, sound: 'open' },
      'window.close': { effect: 'popOut', params: { duration: 120 }, sound: 'close' },
      'window.backdrop': { effect: 'backdrop', params: { blur: 0, dim: 0.55 } },
      'window.camera': { effect: 'cameraZoom', params: { zoom: 0.04, mode: 'punch', hold: 120, stiffness: 400, damping: 20 } },
      notify: { effect: 'heartbeat', params: { scale: 0.2, interval: 900 }, sound: 'notify_glass' },
      success: { effect: 'punch', params: { scale: 0.3 }, sound: 'reward_alt' },
      error: { effect: 'shake', params: { distance: 14, shakes: 5, duration: 300 }, sound: 'error_buzz' },
      'reward.item': { effect: 'rewardPop', sound: 'reward_alt' },
      levelUp: { effect: 'textWave', params: { each: 25, height: 24 }, sound: 'level_up_retro' },
    }),
  },
  'clean-modern': {
    id: 'clean-modern',
    name: 'Clean Modern',
    description: 'Сдержанно: без желе, маленький overshoot, короткие fade/slide, тихие клики, без конфетти.',
    config: { intensity: 0.6 },
    slots: merge({
      'button.hover': { effect: 'hoverLift', params: { lift: 1, scale: 0.02, stiffness: 600, damping: 40 }, sound: 'none' },
      'button.press': { effect: 'jellyPress', params: { squashX: 0.03, squashY: 0.03, pressMs: 60, stiffness: 700, damping: 32 }, sound: 'click_soft' },
      'button.cta': { effect: 'none' },
      'window.open': { effect: 'popIn', params: { fromScale: 0.94, stiffness: 700, damping: 34, fadeMs: 160 }, sound: 'none' },
      'window.close': { effect: 'popOut', params: { anticipation: 0, toScale: 0.96, duration: 140, ease: 'out' }, sound: 'none' },
      'window.backdrop': { effect: 'backdrop', params: { blur: 12, dim: 0.15 } },
      'panel.in': { effect: 'slideIn', params: { distance: 24, stiffness: 700, damping: 40 }, sound: 'none' },
      'list.in': { effect: 'stagger', params: { each: 30, effect: 'fade' } },
      'toast.in': { effect: 'slideIn', params: { from: 'top', distance: 20, stiffness: 700, damping: 40 }, sound: 'notify_glass' },
      notify: { effect: 'none', sound: 'notify_glass' },
      success: { effect: 'none', sound: 'success' },
      error: { effect: 'shake', params: { distance: 5, shakes: 2, duration: 260 }, sound: 'error' },
      'reward.item': { effect: 'punch', params: { scale: 0.08 }, sound: 'success' },
      'reward.big': { effect: 'none', sound: 'success_big' },
      levelUp: { effect: 'slideIn', params: { from: 'bottom', distance: 16 }, sound: 'success_big' },
      'title.in': { effect: 'slideIn', params: { from: 'bottom', distance: 12, stiffness: 700, damping: 40 } },
    }),
  },
};
