// Window / panel / attention / text effects.
import { play, playSpring, lerp, wait, animateValue } from '../core/animate';
import { amp, prefersReducedMotion, dur } from '../core/config';
import { SpringValue } from '../core/spring';
import { defineEffect, springParams, easeParam, type Handle, type EffectDef, type Params } from './types';

const sp = (p: { stiffness: number; damping: number; mass: number }) => ({ stiffness: p.stiffness, damping: p.damping, mass: p.mass });
const fadeIn = (el: HTMLElement, ms: number, delay = 0) =>
  play(el, [{ opacity: 0 }, { opacity: 1 }], { duration: ms, delay, channel: 'fade', easing: 'out' });
const reducedFade = (el: HTMLElement, show: boolean) =>
  play(el, [{ opacity: show ? 0 : 1 }, { opacity: show ? 1 : 0 }], { duration: 140, channel: 'fade' });

// ---------------------------------------------------------------- Pop In / Pop Out
export const popIn = defineEffect({
  id: 'popIn',
  name: 'Pop In',
  category: 'window',
  description: 'Окно появляется из маленького масштаба с пружинным отскоком (лёгкий поворот по желанию).',
  defaults: { fromScale: 0.5, rotate: 0, fadeMs: 120, delay: 0, stiffness: 520, damping: 15, mass: 1 },
  params: {
    fromScale: { label: 'начальный масштаб', min: 0, max: 1, step: 0.01 },
    rotate: { label: 'поворот, °', min: -20, max: 20, step: 0.5 },
    fadeMs: { label: 'проявление, мс', min: 0, max: 400, step: 10 },
    delay: { label: 'задержка, мс', min: 0, max: 1000, step: 10 },
    ...springParams,
  },
  run(el, p) {
    el.style.visibility = 'visible';
    if (prefersReducedMotion()) return reducedFade(el, true);
    fadeIn(el, p.fadeMs, p.delay);
    const s0 = 1 - amp(1 - p.fromScale), r0 = amp(p.rotate);
    return playSpring(el, sp(p), (t) => ({ scale: String(lerp(s0, 1, t)), rotate: `${lerp(r0, 0, t)}deg` }), {
      channel: 'pop',
      delay: p.delay,
    });
  },
});

export const popOut = defineEffect({
  id: 'popOut',
  name: 'Pop Out',
  category: 'window',
  description: 'Закрытие: короткое "вдох-увеличение" и быстрое сжатие с исчезновением.',
  defaults: { toScale: 0.7, anticipation: 0.04, duration: 180, ease: 'backIn' },
  params: {
    toScale: { label: 'конечный масштаб', min: 0, max: 1, step: 0.01 },
    anticipation: { label: 'подготовка (увеличение)', min: 0, max: 0.2, step: 0.01 },
    duration: { label: 'длительность, мс', min: 60, max: 600, step: 10 },
    ease: easeParam,
  },
  run(el, p) {
    if (prefersReducedMotion()) return reducedFade(el, false);
    return play(
      el,
      [
        { scale: '1', opacity: 1, offset: 0 },
        { scale: String(1 + amp(p.anticipation)), opacity: 1, offset: 0.25 },
        { scale: String(p.toScale), opacity: 0, offset: 1 },
      ],
      { duration: p.duration, easing: p.ease, channel: 'pop' },
    );
  },
});

// ---------------------------------------------------------------- Slide In / Out
const dirVec = (d: string, dist: number): [number, number] =>
  d === 'left' ? [-dist, 0] : d === 'right' ? [dist, 0] : d === 'top' ? [0, -dist] : [0, dist];

export const slideIn = defineEffect({
  id: 'slideIn',
  name: 'Slide In',
  category: 'window',
  description: 'Панель вылетает сбоку/сверху/снизу на пружине; дистанция, сторона и отскок настраиваются.',
  defaults: { from: 'right', distance: 260, fadeMs: 150, delay: 0, stiffness: 380, damping: 26, mass: 1 },
  params: {
    from: { label: 'откуда', options: ['right', 'left', 'top', 'bottom'] },
    distance: { label: 'дистанция, px', min: 10, max: 1000, step: 5 },
    fadeMs: { label: 'проявление, мс', min: 0, max: 400, step: 10 },
    delay: { label: 'задержка, мс', min: 0, max: 1000, step: 10 },
    ...springParams,
  },
  run(el, p) {
    el.style.visibility = 'visible';
    if (prefersReducedMotion()) return reducedFade(el, true);
    fadeIn(el, p.fadeMs, p.delay);
    const [x, y] = dirVec(String(p.from), amp(p.distance));
    return playSpring(el, sp(p), (t) => ({ translate: `${lerp(x, 0, t)}px ${lerp(y, 0, t)}px` }), {
      channel: 'slide',
      delay: p.delay,
    });
  },
});

export const slideOut = defineEffect({
  id: 'slideOut',
  name: 'Slide Out',
  category: 'window',
  description: 'Панель уезжает в сторону с ускорением и исчезает.',
  defaults: { to: 'right', distance: 260, duration: 220, ease: 'in' },
  params: {
    to: { label: 'куда', options: ['right', 'left', 'top', 'bottom'] },
    distance: { label: 'дистанция, px', min: 10, max: 1000, step: 5 },
    duration: { label: 'длительность, мс', min: 60, max: 800, step: 10 },
    ease: easeParam,
  },
  run(el, p) {
    if (prefersReducedMotion()) return reducedFade(el, false);
    const [x, y] = dirVec(String(p.to), amp(p.distance));
    return play(el, [{ translate: '0 0', opacity: 1 }, { translate: `${x}px ${y}px`, opacity: 0 }], {
      duration: p.duration,
      easing: p.ease,
      channel: 'slide',
    });
  },
});

// ---------------------------------------------------------------- Drop In (toast)
export const dropIn = defineEffect({
  id: 'dropIn',
  name: 'Drop In',
  category: 'window',
  description: 'Тост/баннер падает сверху и подпрыгивает при "приземлении".',
  defaults: { distance: 120, stiffness: 600, damping: 13, mass: 1.2 },
  params: { distance: { label: 'высота падения, px', min: 10, max: 600, step: 5 }, ...springParams },
  run(el, p) {
    el.style.visibility = 'visible';
    if (prefersReducedMotion()) return reducedFade(el, true);
    fadeIn(el, 90);
    const d = amp(p.distance);
    return playSpring(el, sp(p), (t) => ({ translate: `0 ${lerp(-d, 0, t)}px` }), { channel: 'slide' });
  },
});

// ---------------------------------------------------------------- Flip In (card reveal)
export const flipIn = defineEffect({
  id: 'flipIn',
  name: 'Flip Reveal',
  category: 'window',
  description: 'Карточка переворачивается по оси Y и показывается (награды, карты, сундуки).',
  defaults: { angle: 90, stiffness: 300, damping: 18, mass: 1 },
  params: { angle: { label: 'стартовый угол, °', min: 10, max: 180, step: 1 }, ...springParams },
  run(el, p) {
    el.style.visibility = 'visible';
    if (prefersReducedMotion()) return reducedFade(el, true);
    fadeIn(el, 80);
    const a = Math.min(180, amp(p.angle));
    return playSpring(el, sp(p), (t) => ({ rotate: `y ${lerp(a, 0, t)}deg` }), { channel: 'flip' });
  },
});

// ---------------------------------------------------------------- Background Blur / Dim
export const backdrop = defineEffect({
  id: 'backdrop',
  name: 'Background Blur',
  category: 'window',
  description: 'Размытие и затемнение фона за окном. Элемент — полноэкранный оверлей; mode: show/hide.',
  defaults: { blur: 8, dim: 0.35, duration: 260, mode: 'show', tint: 'black' },
  params: {
    blur: { label: 'размытие, px', min: 0, max: 30, step: 1 },
    dim: { label: 'затемнение', min: 0, max: 0.9, step: 0.05 },
    duration: { label: 'длительность, мс', min: 50, max: 1000, step: 10 },
    mode: { label: 'режим', options: ['show', 'hide'] },
    tint: { label: 'оттенок', options: ['black', 'navy', 'white'] },
  },
  run(el, p) {
    el.classList.add('uifx-backdrop');
    const tint = p.tint === 'white' ? '255,255,255' : p.tint === 'navy' ? '10,20,60' : '0,0,0';
    el.style.backgroundColor = `rgba(${tint},${p.dim})`;
    // Blur is static; opacity animates (compositor-friendly, works where backdrop-filter can't animate).
    const blur = prefersReducedMotion() ? 0 : p.blur;
    el.style.setProperty('-webkit-backdrop-filter', `blur(${blur}px)`);
    el.style.backdropFilter = `blur(${blur}px)`;
    const show = p.mode === 'show';
    if (show) el.style.visibility = 'visible';
    const a = play(el, [{ opacity: show ? 0 : 1 }, { opacity: show ? 1 : 0 }], {
      duration: p.duration,
      easing: show ? 'out' : 'in',
      channel: 'fade',
    });
    if (!show) a.finished.then(() => (el.style.visibility = 'hidden')).catch(() => {});
    return a;
  },
});

// ---------------------------------------------------------------- Camera Zoom
/**
 * For engine cameras use `cameraZoomSpring(apply)`: it returns a SpringValue (1 = normal) that you
 * map to FOV (fov = baseFov / v) or to orthoHeight. In DOM the effect scales the given element.
 */
export function cameraZoomSpring(apply: (zoom: number) => void, spring = { stiffness: 120, damping: 18, mass: 1 }) {
  return new SpringValue(1, spring, apply);
}

export const cameraZoom = defineEffect({
  id: 'cameraZoom',
  name: 'Camera Zoom',
  category: 'window',
  description: 'Небольшое приближение "камеры" (сцены/фона) при открытии окна или событии. punch — туда-обратно.',
  defaults: { zoom: 0.06, mode: 'punch', hold: 450, stiffness: 140, damping: 18, mass: 1 },
  params: {
    zoom: { label: 'приближение', min: 0, max: 0.4, step: 0.01 },
    mode: { label: 'режим', options: ['punch', 'in', 'out'] },
    hold: { label: 'удержание (punch), мс', min: 0, max: 2000, step: 10 },
    ...springParams,
  },
  async run(el, p) {
    if (prefersReducedMotion()) return;
    const z = 1 + amp(p.zoom);
    const cur = parseFloat(getComputedStyle(el).scale) || 1;
    if (p.mode === 'out') return playSpring(el, sp(p), (t) => ({ scale: String(lerp(cur, 1, t)) }), { channel: 'zoom' });
    await playSpring(el, sp(p), (t) => ({ scale: String(lerp(cur, z, t)) }), { channel: 'zoom' }).finished.catch(() => {});
    if (p.mode === 'punch') {
      await wait(p.hold);
      return playSpring(el, sp(p), (t) => ({ scale: String(lerp(z, 1, t)) }), { channel: 'zoom' });
    }
  },
});

// ---------------------------------------------------------------- Stagger
/** Runs `effect` on each child (or the given list) with growing delay. */
export async function staggerRun<P extends Params>(
  els: HTMLElement[],
  effect: EffectDef<P>,
  params: P,
  o: { each: number; from?: 'start' | 'end' | 'center' | 'random' } = { each: 60 },
): Promise<void> {
  const n = els.length;
  const order = els.map((_, i) => {
    switch (o.from) {
      case 'end': return n - 1 - i;
      case 'center': return Math.abs(i - (n - 1) / 2);
      case 'random': return Math.random() * n;
      default: return i;
    }
  });
  els.forEach((e) => (e.style.visibility = 'hidden'));
  await Promise.all(
    els.map(async (e, i) => {
      await wait(order[i] * o.each);
      e.style.visibility = 'visible';
      const r = effect.run(e, params);
      if (r && 'finished' in r) await r.finished.catch(() => {});
      else if (r instanceof Promise) await r;
    }),
  );
}

export const stagger = defineEffect({
  id: 'stagger',
  name: 'Stagger',
  category: 'sequence',
  description: 'Последовательное появление детей элемента (кнопки, иконки, строки списка) выбранным эффектом.',
  defaults: { each: 60, from: 'start', effect: 'popIn', fromScale: 0.4, stiffness: 520, damping: 15, mass: 1 },
  params: {
    each: { label: 'шаг задержки, мс', min: 0, max: 400, step: 5 },
    from: { label: 'порядок', options: ['start', 'end', 'center', 'random'] },
    effect: { label: 'эффект', options: ['popIn', 'slideUp', 'flipIn', 'fade'] },
    fromScale: { label: 'начальный масштаб (popIn)', min: 0, max: 1, step: 0.05 },
    ...springParams,
  },
  run(el, p) {
    const kids = Array.from(el.children) as HTMLElement[];
    const each = prefersReducedMotion() ? 0 : p.each;
    const from = p.from as 'start';
    if (p.effect === 'slideUp')
      return staggerRun(kids, slideIn, { ...slideIn.defaults, from: 'bottom', distance: 24, stiffness: p.stiffness, damping: p.damping, mass: p.mass }, { each, from });
    if (p.effect === 'flipIn')
      return staggerRun(kids, flipIn, { ...flipIn.defaults, stiffness: p.stiffness, damping: p.damping, mass: p.mass }, { each, from });
    if (p.effect === 'fade')
      return staggerRun(kids, fadeEffect, { duration: 250 }, { each, from });
    return staggerRun(kids, popIn, { ...popIn.defaults, fromScale: p.fromScale, stiffness: p.stiffness, damping: p.damping, mass: p.mass }, { each, from });
  },
});

const fadeEffect = defineEffect({
  id: 'fade',
  name: 'Fade',
  category: 'window',
  description: 'Простое проявление.',
  defaults: { duration: 250 },
  params: { duration: { label: 'длительность, мс', min: 50, max: 1000, step: 10 } },
  run: (el, p) => play(el, [{ opacity: 0 }, { opacity: 1 }], { duration: p.duration, channel: 'fade' }),
});

// ---------------------------------------------------------------- Attention loops
function loopEvery(intervalMs: number, jitter: number, fn: () => void, immediate = true): Handle {
  let t = 0;
  let stopped = false;
  const next = () => {
    if (stopped) return;
    t = window.setTimeout(() => {
      if (!document.hidden && !prefersReducedMotion()) fn();
      next();
    }, dur(intervalMs) * (1 + (Math.random() * 2 - 1) * jitter));
  };
  if (immediate && !prefersReducedMotion()) fn();
  next();
  return { stop: () => ((stopped = true), clearTimeout(t)) };
}

export const glossyShine = defineEffect({
  id: 'glossyShine',
  name: 'Glossy Shine',
  category: 'attention',
  description: 'Периодический блик-полоса по кнопке (главная кнопка, магазин, "Claim").',
  defaults: { interval: 2800, jitter: 0.2, duration: 750, angle: 20, width: 40, opacity: 0.55 },
  params: {
    interval: { label: 'интервал, мс', min: 400, max: 10000, step: 100 },
    jitter: { label: 'случайность интервала', min: 0, max: 0.8, step: 0.05 },
    duration: { label: 'проход, мс', min: 200, max: 2000, step: 10 },
    angle: { label: 'наклон, °', min: -45, max: 45, step: 1 },
    width: { label: 'ширина, %', min: 5, max: 100, step: 1 },
    opacity: { label: 'яркость', min: 0.05, max: 1, step: 0.05 },
  },
  loop: true,
  run(el, p) {
    el.classList.add('uifx-clip');
    let bar = el.querySelector<HTMLElement>(':scope > .uifx-shine');
    if (!bar) {
      bar = document.createElement('span');
      bar.className = 'uifx-shine';
      el.appendChild(bar);
    }
    Object.assign(bar.style, { width: `${p.width}%`, rotate: `${p.angle}deg`, opacity: String(p.opacity) });
    const b = bar;
    const h = loopEvery(p.interval, p.jitter, () =>
      play(b, [{ translate: '-150% 0' }, { translate: `${100 / (p.width / 100) + 50}% 0` }], {
        duration: p.duration,
        easing: 'inOut',
        channel: 'shine',
        persist: false,
      }),
    );
    return { stop: () => (h.stop(), b.remove()) };
  },
});

export const glow = defineEffect({
  id: 'glow',
  name: 'Glow Pulse',
  category: 'attention',
  description: 'Мягкое пульсирующее свечение вокруг элемента (готово к сбору, новое, редкое).',
  defaults: { color: 'gold', size: 18, intensity: 0.9, period: 1400 },
  params: {
    color: { label: 'цвет', options: ['gold', 'cyan', 'lime', 'magenta', 'white', 'orange'] },
    size: { label: 'радиус, px', min: 2, max: 60, step: 1 },
    intensity: { label: 'интенсивность', min: 0.1, max: 1, step: 0.05 },
    period: { label: 'период, мс', min: 300, max: 5000, step: 50 },
  },
  loop: true,
  run(el, p) {
    let g = el.querySelector<HTMLElement>(':scope > .uifx-glow');
    if (!g) {
      g = document.createElement('span');
      g.className = 'uifx-glow';
      el.prepend(g);
    }
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    g.style.boxShadow = `0 0 ${p.size}px ${p.size / 3}px ${p.color}`;
    const reduced = prefersReducedMotion();
    const a = play(g, [{ opacity: reduced ? p.intensity : p.intensity * 0.35, scale: '1' }, { opacity: p.intensity, scale: reduced ? '1' : '1.04' }], {
      duration: p.period / 2,
      easing: 'sine',
      iterations: reduced ? 1 : Infinity,
      direction: 'alternate',
      channel: 'glow',
      persist: false,
    });
    const node = g;
    return { stop: () => (a.cancel(), node.remove()) };
  },
});

export const heartbeat = defineEffect({
  id: 'heartbeat',
  name: 'Heartbeat',
  category: 'attention',
  description: 'Двойной "удар сердца" — бейджи, уведомления, кнопка с новым контентом.',
  defaults: { scale: 0.14, interval: 1600, duration: 520 },
  params: {
    scale: { label: 'сила', min: 0, max: 0.5, step: 0.01 },
    interval: { label: 'интервал, мс', min: 300, max: 6000, step: 50 },
    duration: { label: 'длительность удара, мс', min: 150, max: 1500, step: 10 },
  },
  loop: true,
  run(el, p) {
    const s = amp(p.scale);
    return loopEvery(p.interval, 0, () =>
      play(el, [
        { scale: '1', offset: 0 },
        { scale: String(1 + s), offset: 0.15 },
        { scale: '1', offset: 0.3 },
        { scale: String(1 + s * 0.7), offset: 0.45 },
        { scale: '1', offset: 0.7 },
      ], { duration: p.duration, easing: 'inOut', channel: 'beat' }),
    );
  },
});

export const wiggle = defineEffect({
  id: 'wiggle',
  name: 'Wiggle',
  category: 'attention',
  description: 'Покачивание-"зов" (иконка подарка, непрочитанное). once=1 — один раз.',
  defaults: { angle: 12, duration: 600, interval: 3000, once: 1 },
  params: {
    angle: { label: 'угол, °', min: 0, max: 40, step: 1 },
    duration: { label: 'длительность, мс', min: 100, max: 2000, step: 10 },
    interval: { label: 'интервал (если повтор), мс', min: 500, max: 10000, step: 100 },
    once: { label: 'один раз (1) / повтор (0)', min: 0, max: 1, step: 1 },
  },
  run(el, p) {
    const a = amp(p.angle);
    const once = () =>
      play(el, [0, -a, a * 0.9, -a * 0.7, a * 0.5, -a * 0.25, 0].map((v) => ({ rotate: `${v}deg` })), {
        duration: p.duration,
        easing: 'inOut',
        channel: 'wiggle',
      });
    if (p.once) return prefersReducedMotion() ? undefined : once();
    return loopEvery(p.interval, 0.1, once);
  },
});

export const breathe = defineEffect({
  id: 'breathe',
  name: 'Idle Float',
  category: 'attention',
  description: 'Медленное "дыхание"/парение в покое (лого, персонаж в лобби, награда на пьедестале).',
  defaults: { float: 6, scale: 0.02, period: 2600 },
  params: {
    float: { label: 'амплитуда, px', min: 0, max: 30, step: 0.5 },
    scale: { label: 'дыхание (масштаб)', min: 0, max: 0.1, step: 0.005 },
    period: { label: 'период, мс', min: 500, max: 8000, step: 50 },
  },
  loop: true,
  run(el, p) {
    if (prefersReducedMotion()) return { stop() {} };
    const a = play(el, [
      { translate: `0 ${amp(p.float) / 2}px`, scale: '1' },
      { translate: `0 ${-amp(p.float) / 2}px`, scale: String(1 + amp(p.scale)) },
    ], { duration: p.period / 2, easing: 'sine', iterations: Infinity, direction: 'alternate', channel: 'idle', persist: false });
    return { stop: () => a.cancel() };
  },
});

export const shake = defineEffect({
  id: 'shake',
  name: 'Shake (error)',
  category: 'feedback',
  description: 'Затухающая тряска по горизонтали — ошибка, "нельзя", не хватает денег.',
  defaults: { distance: 10, shakes: 4, duration: 420 },
  params: {
    distance: { label: 'амплитуда, px', min: 0, max: 40, step: 1 },
    shakes: { label: 'колебаний', min: 1, max: 10, step: 1 },
    duration: { label: 'длительность, мс', min: 100, max: 1500, step: 10 },
  },
  run(el, p) {
    if (prefersReducedMotion()) return play(el, [{ opacity: 1 }, { opacity: 0.6 }, { opacity: 1 }], { duration: 240, channel: 'fade' });
    const d = amp(p.distance);
    const k: Keyframe[] = [{ translate: '0 0' }];
    for (let i = 1; i <= p.shakes * 2; i++) k.push({ translate: `${(i % 2 ? 1 : -1) * d * (1 - i / (p.shakes * 2 + 1))}px 0` });
    k.push({ translate: '0 0' });
    return play(el, k, { duration: p.duration, easing: 'linear', channel: 'shake' });
  },
});

// ---------------------------------------------------------------- Punch (scale bump)
export const punch = defineEffect({
  id: 'punch',
  name: 'Punch / Bounce',
  category: 'feedback',
  description: 'Пружинный "толчок" масштаба — значение изменилось, предмет получен, счётчик +1.',
  defaults: { scale: 0.25, stiffness: 600, damping: 12, mass: 1 },
  params: { scale: { label: 'сила', min: -0.5, max: 0.8, step: 0.01 }, ...springParams },
  run(el, p) {
    if (prefersReducedMotion()) return;
    const s = 1 + amp(p.scale);
    return playSpring(el, { ...sp(p), velocity: 0 }, (t) => ({ scale: String(lerp(s, 1, t)) }), { channel: 'punch' });
  },
});

// ---------------------------------------------------------------- Text
function splitChars(el: HTMLElement): HTMLElement[] {
  if (!el.dataset.uifxText) el.dataset.uifxText = el.textContent ?? '';
  const text = el.dataset.uifxText;
  el.textContent = '';
  el.setAttribute('aria-label', text);
  return [...text].map((ch) => {
    const s = document.createElement('span');
    s.className = 'uifx-char';
    s.setAttribute('aria-hidden', 'true');
    s.textContent = ch === ' ' ? ' ' : ch;
    el.appendChild(s);
    return s;
  });
}

export const textWave = defineEffect({
  id: 'textWave',
  name: 'Text Pop Wave',
  category: 'text',
  description: 'Буквы заголовка выпрыгивают по очереди с пружиной ("VICTORY!", "LEVEL UP").',
  defaults: { each: 40, height: 18, stiffness: 500, damping: 14, mass: 1 },
  params: {
    each: { label: 'шаг, мс', min: 0, max: 200, step: 2 },
    height: { label: 'высота прыжка, px', min: 0, max: 60, step: 1 },
    ...springParams,
  },
  async run(el, p) {
    const chars = splitChars(el);
    if (prefersReducedMotion()) return reducedFade(el, true);
    const h = amp(p.height);
    await Promise.all(
      chars.map(async (c, i) => {
        c.style.opacity = '0';
        await wait(i * p.each);
        c.style.opacity = '1';
        return playSpring(c, sp(p), (t) => ({ translate: `0 ${lerp(h, 0, t)}px`, scale: String(lerp(0.3, 1, t)) }), { channel: 'char' }).finished.catch(() => {});
      }),
    );
  },
});

export const typewriter = defineEffect({
  id: 'typewriter',
  name: 'Typewriter',
  category: 'text',
  description: 'Печать текста по буквам (диалоги, подсказки обучения); onChar можно связать со звуком tick.',
  defaults: { cps: 40 },
  params: { cps: { label: 'символов в секунду', min: 5, max: 200, step: 1 } },
  run(el, p) {
    const chars = splitChars(el);
    chars.forEach((c) => (c.style.opacity = '0'));
    if (prefersReducedMotion()) return void chars.forEach((c) => (c.style.opacity = '1'));
    return animateValue({
      from: 0,
      to: chars.length,
      duration: (chars.length / p.cps) * 1000,
      ease: 'linear',
      onUpdate: (v) => chars.forEach((c, i) => (c.style.opacity = i < v ? '1' : '0')),
    }).finished;
  },
});
