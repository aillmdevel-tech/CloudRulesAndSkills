// Press & hover effects: Jelly Press, Squash & Stretch, Press Depth, Ripple, Hover Scale/Tilt, Hover Lift, Magnetic.
import { play, playSpring, lerp } from '../core/animate';
import { SpringValue } from '../core/spring';
import { amp, prefersReducedMotion } from '../core/config';
import { defineEffect, springParams, type Handle } from './types';

const sp = (p: { stiffness: number; damping: number; mass: number }) => ({
  stiffness: p.stiffness,
  damping: p.damping,
  mass: p.mass,
});

/** Attach press listeners that call down/up; handles touch, leave and cancel. */
function pressListeners(el: HTMLElement, down: (e: PointerEvent) => void, up: (e: PointerEvent | null) => void): Handle {
  let pressed = false;
  const onDown = (e: PointerEvent) => {
    if (e.button !== 0) return;
    pressed = true;
    down(e);
  };
  const onUp = (e: PointerEvent) => {
    if (!pressed) return;
    pressed = false;
    up(e);
  };
  const onKeyDown = (e: KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && !pressed && !e.repeat) {
      pressed = true;
      down(new PointerEvent('pointerdown'));
    }
  };
  const onKeyUp = (e: KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && pressed) {
      pressed = false;
      up(null);
    }
  };
  el.addEventListener('pointerdown', onDown);
  window.addEventListener('pointerup', onUp);
  el.addEventListener('pointerleave', onUp);
  el.addEventListener('pointercancel', onUp);
  el.addEventListener('keydown', onKeyDown);
  el.addEventListener('keyup', onKeyUp);
  return {
    stop() {
      el.removeEventListener('pointerdown', onDown);
      window.removeEventListener('pointerup', onUp);
      el.removeEventListener('pointerleave', onUp);
      el.removeEventListener('pointercancel', onUp);
      el.removeEventListener('keydown', onKeyDown);
      el.removeEventListener('keyup', onKeyUp);
    },
  };
}

// ---------------------------------------------------------------- Jelly Press
const jellyDefaults = { squashX: 0.14, squashY: 0.18, pressMs: 90, stiffness: 420, damping: 9, mass: 1 };
type Jelly = typeof jellyDefaults;

function jellyDown(el: HTMLElement, p: Jelly) {
  if (prefersReducedMotion()) return play(el, [{ opacity: 0.85 }], { duration: 60, channel: 'fade' });
  return play(el, [{ scale: `${1 + amp(p.squashX)} ${1 - amp(p.squashY)}` }], {
    duration: p.pressMs,
    easing: 'out',
    channel: 'press',
  });
}

function jellyUp(el: HTMLElement, p: Jelly) {
  if (prefersReducedMotion()) return play(el, [{ opacity: 1 }], { duration: 80, channel: 'fade' });
  const sx = 1 + amp(p.squashX);
  const sy = 1 - amp(p.squashY);
  // Spring progress overshoots past 1 -> the axes swap (stretch), which reads as jelly wobble.
  return playSpring(el, sp(p), (t) => ({ scale: `${lerp(sx, 1, t)} ${lerp(sy, 1, t)}` }), { channel: 'press' });
}

export const jellyPress = defineEffect({
  id: 'jellyPress',
  name: 'Jelly Press',
  category: 'press',
  description: 'Желейное нажатие: сплющивание при нажатии и упругий отскок с покачиванием при отпускании.',
  defaults: jellyDefaults,
  params: {
    squashX: { label: 'растяжение по X', min: 0, max: 0.4, step: 0.01 },
    squashY: { label: 'сжатие по Y', min: 0, max: 0.4, step: 0.01 },
    pressMs: { label: 'длительность нажатия, мс', min: 20, max: 300, step: 5 },
    ...springParams,
  },
  async run(el, p) {
    await jellyDown(el, p).finished.catch(() => {});
    return jellyUp(el, p);
  },
  attach(el, p) {
    return pressListeners(el, () => jellyDown(el, p()), () => jellyUp(el, p()));
  },
});

// ---------------------------------------------------------------- Squash & Stretch (jump)
export const squashStretch = defineEffect({
  id: 'squashStretch',
  name: 'Squash & Stretch',
  category: 'press',
  description: 'Физичный прыжок: подготовка-сжатие, растяжение в полёте, сжатие при приземлении, успокоение.',
  defaults: { squash: 0.22, stretch: 0.18, height: 28, duration: 620, stiffness: 500, damping: 12, mass: 1 },
  params: {
    squash: { label: 'сила сжатия', min: 0, max: 0.5, step: 0.01 },
    stretch: { label: 'сила растяжения', min: 0, max: 0.5, step: 0.01 },
    height: { label: 'высота прыжка, px', min: 0, max: 120, step: 1 },
    duration: { label: 'длительность, мс', min: 200, max: 1500, step: 10 },
    ...springParams,
  },
  async run(el, p) {
    if (prefersReducedMotion()) return;
    const s = amp(p.squash), st = amp(p.stretch), h = amp(p.height);
    const k = [
      { offset: 0, scale: '1 1', translate: '0 0', easing: 'ease-out' },
      { offset: 0.18, scale: `${1 + s} ${1 - s}`, translate: '0 0', easing: 'cubic-bezier(0.2,0.8,0.4,1)' },
      { offset: 0.5, scale: `${1 - st * 0.6} ${1 + st}`, translate: `0 ${-h}px`, easing: 'cubic-bezier(0.6,0,0.8,0.4)' },
      { offset: 0.78, scale: `${1 - st * 0.3} ${1 + st * 0.5}`, translate: '0 0', easing: 'ease-out' },
      { offset: 0.86, scale: `${1 + s * 0.8} ${1 - s * 0.8}`, translate: '0 0' },
      { offset: 1, scale: `${1 + s * 0.8} ${1 - s * 0.8}`, translate: '0 0' },
    ];
    await play(el, k as Keyframe[], { duration: p.duration * 0.86, easing: 'linear', channel: 'press' }).finished.catch(() => {});
    const sx = 1 + s * 0.8, sy = 1 - s * 0.8;
    return playSpring(el, sp(p), (t) => ({ scale: `${lerp(sx, 1, t)} ${lerp(sy, 1, t)}` }), { channel: 'press' });
  },
});

// ---------------------------------------------------------------- Press Depth (3D button)
export const pressDepth = defineEffect({
  id: 'pressDepth',
  name: 'Press Depth',
  category: 'press',
  description: 'Кнопка "вдавливается" вниз (как объёмная кнопка с нижней гранью) и пружинит обратно. Пара к .uifx-depth.',
  defaults: { depth: 4, pressMs: 60, stiffness: 700, damping: 18, mass: 1 },
  params: {
    depth: { label: 'глубина, px', min: 0, max: 12, step: 0.5 },
    pressMs: { label: 'нажатие, мс', min: 20, max: 200, step: 5 },
    ...springParams,
  },
  async run(el, p) {
    el.classList.add('uifx-depth');
    el.style.setProperty('--uifx-depth', `${p.depth}px`);
    el.dataset.uifxPressed = '';
    await play(el, [{ translate: `0 ${amp(p.depth)}px` }], { duration: p.pressMs, channel: 'press' }).finished.catch(() => {});
    delete el.dataset.uifxPressed;
    return playSpring(el, sp(p), (t) => ({ translate: `0 ${lerp(amp(p.depth), 0, t)}px` }), { channel: 'press' });
  },
  attach(el, p) {
    el.classList.add('uifx-depth');
    el.style.setProperty('--uifx-depth', `${p().depth}px`);
    return pressListeners(
      el,
      () => {
        el.dataset.uifxPressed = '';
        play(el, [{ translate: `0 ${amp(p().depth)}px` }], { duration: p().pressMs, channel: 'press' });
      },
      () => {
        delete el.dataset.uifxPressed;
        const d = amp(p().depth);
        playSpring(el, sp(p()), (t) => ({ translate: `0 ${lerp(d, 0, t)}px` }), { channel: 'press' });
      },
    );
  },
});

// ---------------------------------------------------------------- Ripple
export const ripple = defineEffect({
  id: 'ripple',
  name: 'Ripple',
  category: 'press',
  description: 'Круговая волна из точки нажатия (Material-like), цвет и прозрачность настраиваются.',
  defaults: { duration: 550, opacity: 0.35, size: 2.2, color: 'white' },
  params: {
    duration: { label: 'длительность, мс', min: 150, max: 1500, step: 10 },
    opacity: { label: 'интенсивность', min: 0.05, max: 1, step: 0.05 },
    size: { label: 'размер (× ширины)', min: 0.5, max: 4, step: 0.1 },
    color: { label: 'цвет', options: ['white', 'black', 'currentColor', 'gold', 'cyan'] },
  },
  run(el, p, ev) {
    el.classList.add('uifx-clip');
    const r = el.getBoundingClientRect();
    const x = ev ? ev.clientX - r.left : r.width / 2;
    const y = ev ? ev.clientY - r.top : r.height / 2;
    const d = Math.max(r.width, r.height) * p.size;
    const dot = document.createElement('span');
    dot.className = 'uifx-ripple';
    Object.assign(dot.style, { left: `${x - d / 2}px`, top: `${y - d / 2}px`, width: `${d}px`, height: `${d}px`, background: p.color });
    el.appendChild(dot);
    const a = dot.animate(
      [
        { scale: 0, opacity: p.opacity },
        { scale: 1, opacity: 0 },
      ],
      { duration: prefersReducedMotion() ? 200 : p.duration, easing: 'cubic-bezier(0.22,1,0.36,1)' },
    );
    a.finished.finally(() => dot.remove()).catch(() => {});
    return a;
  },
  attach(el, p) {
    const h = (e: PointerEvent) => ripple.run(el, p(), e);
    el.addEventListener('pointerdown', h);
    return { stop: () => el.removeEventListener('pointerdown', h) };
  },
});

// ---------------------------------------------------------------- Hover Scale / Tilt (+ glare)
export const hoverTilt = defineEffect({
  id: 'hoverTilt',
  name: 'Hover Scale/Tilt',
  category: 'hover',
  description: 'Плавное увеличение и наклон к курсору (3D), опционально блик. Пружина — прерывается мгновенно.',
  defaults: { scale: 0.06, angle: 8, glare: 0.25, stiffness: 300, damping: 22, mass: 1 },
  params: {
    scale: { label: 'увеличение', min: 0, max: 0.3, step: 0.01 },
    angle: { label: 'угол наклона, °', min: 0, max: 25, step: 0.5 },
    glare: { label: 'блик', min: 0, max: 0.8, step: 0.05 },
    ...springParams,
  },
  run(el, p) {
    // demo: simulate a hover pass
    const h = this.attach!(el, () => p);
    const r = el.getBoundingClientRect();
    const fire = (type: string, fx: number) =>
      el.dispatchEvent(new PointerEvent(type, { clientX: r.left + r.width * fx, clientY: r.top + r.height * 0.3 }));
    fire('pointerenter', 0.2);
    fire('pointermove', 0.15);
    setTimeout(() => fire('pointermove', 0.85), 350);
    setTimeout(() => fire('pointerleave', 0.85), 800);
    setTimeout(() => h.stop(), 1600);
  },
  attach(el, p) {
    el.classList.add('uifx-tilt');
    const cfg = () => ({ stiffness: p().stiffness, damping: p().damping, mass: p().mass });
    const s = new SpringValue(1, cfg(), (v) => (el.style.scale = String(v)));
    const rx = new SpringValue(0, cfg(), (v) => el.style.setProperty('--uifx-rx', `${v}deg`));
    const ry = new SpringValue(0, cfg(), (v) => el.style.setProperty('--uifx-ry', `${v}deg`));
    const enter = () => {
      if (prefersReducedMotion()) return;
      s.opts = rx.opts = ry.opts = cfg();
      s.set(1 + amp(p().scale));
      el.style.setProperty('--uifx-glare', String(p().glare));
    };
    const move = (e: PointerEvent) => {
      if (prefersReducedMotion()) return;
      const r = el.getBoundingClientRect();
      const nx = (e.clientX - r.left) / r.width - 0.5;
      const ny = (e.clientY - r.top) / r.height - 0.5;
      const a = amp(p().angle);
      ry.set(nx * 2 * a);
      rx.set(-ny * 2 * a);
      el.style.setProperty('--uifx-gx', `${(nx + 0.5) * 100}%`);
      el.style.setProperty('--uifx-gy', `${(ny + 0.5) * 100}%`);
    };
    const leave = () => {
      s.set(1);
      rx.set(0);
      ry.set(0);
      el.style.setProperty('--uifx-glare', '0');
    };
    el.addEventListener('pointerenter', enter);
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', leave);
    return {
      stop() {
        el.removeEventListener('pointerenter', enter);
        el.removeEventListener('pointermove', move);
        el.removeEventListener('pointerleave', leave);
        leave();
      },
    };
  },
});

// ---------------------------------------------------------------- Hover Lift
export const hoverLift = defineEffect({
  id: 'hoverLift',
  name: 'Hover Lift',
  category: 'hover',
  description: 'Мягкий подъём и чуть больше масштаб при наведении (карточки, слоты инвентаря).',
  defaults: { lift: 6, scale: 0.03, stiffness: 400, damping: 24, mass: 1 },
  params: {
    lift: { label: 'подъём, px', min: 0, max: 30, step: 1 },
    scale: { label: 'увеличение', min: 0, max: 0.2, step: 0.01 },
    ...springParams,
  },
  run(el, p) {
    const h = this.attach!(el, () => p);
    el.dispatchEvent(new PointerEvent('pointerenter'));
    setTimeout(() => el.dispatchEvent(new PointerEvent('pointerleave')), 700);
    setTimeout(() => h.stop(), 1500);
  },
  attach(el, p) {
    const cfg = () => ({ stiffness: p().stiffness, damping: p().damping, mass: p().mass });
    const v = new SpringValue(0, cfg(), (t) => {
      el.style.translate = `0 ${-amp(p().lift) * t}px`;
      el.style.scale = String(1 + amp(p().scale) * t);
    });
    const enter = () => !prefersReducedMotion() && ((v.opts = cfg()), v.set(1));
    const leave = () => v.set(0);
    el.addEventListener('pointerenter', enter);
    el.addEventListener('pointerleave', leave);
    return {
      stop() {
        el.removeEventListener('pointerenter', enter);
        el.removeEventListener('pointerleave', leave);
        v.jump(0);
      },
    };
  },
});

// ---------------------------------------------------------------- Magnetic
export const magnetic = defineEffect({
  id: 'magnetic',
  name: 'Magnetic',
  category: 'hover',
  description: 'Кнопка слегка тянется за курсором и пружинит назад (главные CTA, "Play").',
  defaults: { strength: 0.25, stiffness: 250, damping: 15, mass: 1 },
  params: { strength: { label: 'сила притяжения', min: 0, max: 0.8, step: 0.01 }, ...springParams },
  run(el, p) {
    const h = this.attach!(el, () => p);
    const r = el.getBoundingClientRect();
    el.dispatchEvent(new PointerEvent('pointermove', { clientX: r.right, clientY: r.top }));
    setTimeout(() => el.dispatchEvent(new PointerEvent('pointerleave')), 500);
    setTimeout(() => h.stop(), 1400);
  },
  attach(el, p) {
    const cfg = () => ({ stiffness: p().stiffness, damping: p().damping, mass: p().mass });
    let x = 0, y = 0;
    const apply = () => (el.style.translate = `${x}px ${y}px`);
    const sx = new SpringValue(0, cfg(), (v) => ((x = v), apply()));
    const sy = new SpringValue(0, cfg(), (v) => ((y = v), apply()));
    const move = (e: PointerEvent) => {
      if (prefersReducedMotion()) return;
      const r = el.getBoundingClientRect();
      const k = amp(p().strength);
      sx.set((e.clientX - (r.left + r.width / 2)) * k);
      sy.set((e.clientY - (r.top + r.height / 2)) * k);
    };
    const leave = () => (sx.set(0), sy.set(0));
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', leave);
    return {
      stop() {
        el.removeEventListener('pointermove', move);
        el.removeEventListener('pointerleave', leave);
        sx.jump(0);
        sy.jump(0);
      },
    };
  },
});
