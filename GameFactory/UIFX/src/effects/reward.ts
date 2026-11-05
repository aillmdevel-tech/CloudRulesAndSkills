// Reward effects: count-up numbers, floating text, coins flying to a counter, confetti, star burst,
// progress fill, reward pop combo.
import { play, playSpring, lerp, animateValue, wait } from '../core/animate';
import { amp, prefersReducedMotion, dur } from '../core/config';
import { defineEffect, springParams } from './types';

const center = (el: Element) => {
  const r = el.getBoundingClientRect();
  return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
};

function layer(): HTMLElement {
  let l = document.getElementById('uifx-layer');
  if (!l) {
    l = document.createElement('div');
    l.id = 'uifx-layer';
    document.body.appendChild(l);
  }
  return l;
}

// ---------------------------------------------------------------- Count Up
export function countUp(
  el: HTMLElement,
  o: { from?: number; to: number; duration?: number; ease?: 'out' | 'linear' | 'inOut'; decimals?: number; prefix?: string; suffix?: string; onTick?: (v: number) => void; tickEvery?: number },
): Promise<void> {
  const from = o.from ?? (parseFloat((el.textContent ?? '').replace(/[^\d.-]/g, '')) || 0);
  const fmt = new Intl.NumberFormat(undefined, { maximumFractionDigits: o.decimals ?? 0, minimumFractionDigits: o.decimals ?? 0 });
  const show = (v: number) => (el.textContent = `${o.prefix ?? ''}${fmt.format(v)}${o.suffix ?? ''}`);
  if (prefersReducedMotion()) return Promise.resolve(void show(o.to));
  let lastTick = from;
  const step = o.tickEvery ?? Math.max(1, Math.abs(o.to - from) / 12);
  return animateValue({
    from,
    to: o.to,
    duration: o.duration ?? 900,
    ease: o.ease ?? 'out',
    onUpdate: (v) => {
      show(v);
      if (o.onTick && Math.abs(v - lastTick) >= step) {
        lastTick = v;
        o.onTick(v);
      }
    },
  }).finished.then(() => void show(o.to));
}

export const countUpFx = defineEffect({
  id: 'countUp',
  name: 'Count Up',
  category: 'reward',
  description: 'Анимированная накрутка числа (монеты, очки, опыт) с "тиками" для звука и толчком в конце.',
  defaults: { to: 1250, duration: 900, ease: 'out', punch: 0.2 },
  params: {
    to: { label: 'до значения', min: 0, max: 100000, step: 10 },
    duration: { label: 'длительность, мс', min: 100, max: 4000, step: 50 },
    ease: { label: 'easing', options: ['out', 'linear', 'inOut'] },
    punch: { label: 'толчок в конце', min: 0, max: 0.6, step: 0.01 },
  },
  async run(el, p) {
    await countUp(el, { from: 0, to: Number(p.to), duration: Number(p.duration), ease: p.ease as 'out' });
    if (p.punch && !prefersReducedMotion())
      return playSpring(el, 'bouncy', (t) => ({ scale: String(lerp(1 + amp(Number(p.punch)), 1, t)) }), { channel: 'punch' });
  },
});

// ---------------------------------------------------------------- Floating text (+10)
export function floatingText(
  text: string,
  at: { x: number; y: number } | Element,
  o: { rise?: number; duration?: number; className?: string; color?: string; scale?: number } = {},
): Promise<void> {
  const pos = at instanceof Element ? center(at) : at;
  const t = document.createElement('div');
  t.className = `uifx-float ${o.className ?? ''}`;
  t.textContent = text;
  if (o.color) t.style.color = o.color;
  Object.assign(t.style, { left: `${pos.x}px`, top: `${pos.y}px` });
  layer().appendChild(t);
  const rise = prefersReducedMotion() ? 0 : amp(o.rise ?? 60);
  const s = o.scale ?? 1.25;
  const a = t.animate(
    [
      { translate: '-50% -50%', scale: '0.4', opacity: 0, offset: 0 },
      { translate: '-50% -50%', scale: String(s), opacity: 1, offset: 0.15 },
      { translate: '-50% -50%', scale: '1', opacity: 1, offset: 0.3 },
      { translate: `-50% calc(-50% - ${rise}px)`, scale: '1', opacity: 0, offset: 1 },
    ],
    { duration: dur(o.duration ?? 1000), easing: 'cubic-bezier(0.22,1,0.36,1)' },
  );
  return a.finished.then(() => t.remove()).catch(() => t.remove());
}

export const floatingTextFx = defineEffect({
  id: 'floatingText',
  name: 'Floating +N',
  category: 'reward',
  description: 'Всплывающий текст "+10", "+1 XP", "CRIT!" над объектом: выскакивает и уплывает вверх.',
  defaults: { text: '+10', rise: 60, duration: 1000, scale: 1.3 },
  params: {
    text: { label: 'текст', options: ['+10', '+1 XP', '+250', 'CRIT!', 'COMBO x3'] },
    rise: { label: 'подъём, px', min: 0, max: 200, step: 1 },
    duration: { label: 'длительность, мс', min: 200, max: 3000, step: 50 },
    scale: { label: 'пик масштаба', min: 1, max: 2.5, step: 0.05 },
  },
  run: (el, p) => floatingText(String(p.text), el, { rise: Number(p.rise), duration: Number(p.duration), scale: Number(p.scale) }),
});

// ---------------------------------------------------------------- Coin fly to counter
export async function flyTo(
  from: Element | { x: number; y: number },
  to: Element,
  o: { count?: number; html?: string; arc?: number; duration?: number; stagger?: number; spread?: number; onArrive?: (i: number) => void } = {},
): Promise<void> {
  const a = from instanceof Element ? center(from) : from;
  const b = center(to);
  const n = prefersReducedMotion() ? Math.min(1, o.count ?? 8) : o.count ?? 8;
  const html = o.html ?? '<span class="uifx-coin"></span>';
  const spread = o.spread ?? 50;
  const tasks: Promise<void>[] = [];
  for (let i = 0; i < n; i++) {
    tasks.push(
      (async () => {
        await wait(i * (o.stagger ?? 45));
        const c = document.createElement('div');
        c.className = 'uifx-fly';
        c.innerHTML = html;
        Object.assign(c.style, { left: `${a.x}px`, top: `${a.y}px` });
        layer().appendChild(c);
        // burst outward first, then arc to the target (quadratic bezier sampled into keyframes)
        const ang = Math.random() * Math.PI * 2;
        const r = Math.random() * spread;
        const p0 = { x: Math.cos(ang) * r, y: Math.sin(ang) * r };
        const p2 = { x: b.x - a.x, y: b.y - a.y };
        const p1 = { x: (p0.x + p2.x) / 2 + (Math.random() - 0.5) * 80, y: Math.min(p0.y, p2.y) - amp(o.arc ?? 120) };
        const frames: Keyframe[] = [{ translate: '-50% -50%', scale: '0.3', offset: 0 }, { translate: `calc(-50% + ${p0.x}px) calc(-50% + ${p0.y}px)`, scale: '1.15', offset: 0.22 }];
        for (let k = 1; k <= 12; k++) {
          const t = k / 12;
          const e = t * t * (3 - 2 * t);
          const x = (1 - e) ** 2 * p0.x + 2 * (1 - e) * e * p1.x + e * e * p2.x;
          const y = (1 - e) ** 2 * p0.y + 2 * (1 - e) * e * p1.y + e * e * p2.y;
          frames.push({ translate: `calc(-50% + ${x}px) calc(-50% + ${y}px)`, scale: String(lerp(1.1, 0.7, t)), offset: 0.22 + 0.78 * t });
        }
        await c.animate(frames, { duration: dur(o.duration ?? 750), easing: 'linear' }).finished.catch(() => {});
        c.remove();
        o.onArrive?.(i);
      })(),
    );
  }
  await Promise.all(tasks);
}

export const coinFlyFx = defineEffect({
  id: 'coinFly',
  name: 'Coins Fly To Counter',
  category: 'reward',
  description: 'Монеты/кристаллы разлетаются из награды и по дуге летят в счётчик; счётчик "толкается" на каждую.',
  defaults: { count: 10, arc: 120, duration: 750, stagger: 45, spread: 60 },
  params: {
    count: { label: 'количество', min: 1, max: 40, step: 1 },
    arc: { label: 'высота дуги, px', min: 0, max: 400, step: 5 },
    duration: { label: 'полёт, мс', min: 200, max: 2000, step: 10 },
    stagger: { label: 'интервал вылета, мс', min: 0, max: 200, step: 5 },
    spread: { label: 'разброс, px', min: 0, max: 200, step: 5 },
  },
  run(el, p) {
    const target =
      el.closest('[data-uifx-scope]')?.querySelector<HTMLElement>('[data-uifx-counter]') ??
      document.querySelector<HTMLElement>('[data-uifx-counter]') ??
      el;
    return flyTo(el, target, {
      ...p,
      onArrive: () => playSpring(target, 'bouncy', (t) => ({ scale: String(lerp(1.18, 1, t)) }), { channel: 'punch' }),
    });
  },
});

// ---------------------------------------------------------------- Confetti (canvas)
export interface ConfettiOptions {
  x?: number; // 0..1 of viewport width (default 0.5)
  y?: number; // 0..1 of viewport height (default 0.6)
  count?: number;
  spread?: number; // degrees
  angle?: number; // degrees, 90 = up
  power?: number; // initial speed px/s
  gravity?: number;
  drag?: number;
  duration?: number;
  colors?: string[];
  shapes?: ('rect' | 'circle' | 'star')[];
  size?: number;
}

export function confetti(o: ConfettiOptions = {}): Promise<void> {
  if (prefersReducedMotion()) return Promise.resolve();
  const cv = document.createElement('canvas');
  cv.className = 'uifx-confetti';
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  cv.width = innerWidth * dpr;
  cv.height = innerHeight * dpr;
  layer().appendChild(cv);
  const ctx = cv.getContext('2d')!;
  ctx.scale(dpr, dpr);
  const colors = o.colors ?? ['#ffd23f', '#ff5d8f', '#3bceac', '#4d9de0', '#ff8c42', '#ffffff'];
  const shapes = o.shapes ?? ['rect', 'rect', 'circle', 'star'];
  const n = Math.round(amp(o.count ?? 120));
  const ox = (o.x ?? 0.5) * innerWidth, oy = (o.y ?? 0.6) * innerHeight;
  const spread = ((o.spread ?? 70) * Math.PI) / 180, base = ((o.angle ?? 90) * Math.PI) / 180;
  const power = o.power ?? 900, g = o.gravity ?? 1400, drag = o.drag ?? 1.6, size = o.size ?? 9;
  const parts = Array.from({ length: n }, () => {
    const a = base + (Math.random() - 0.5) * spread;
    const v = power * (0.45 + Math.random() * 0.75);
    return {
      x: ox, y: oy, vx: Math.cos(a) * v, vy: -Math.sin(a) * v,
      r: Math.random() * Math.PI, vr: (Math.random() - 0.5) * 14, flip: Math.random() * Math.PI * 2,
      c: colors[(Math.random() * colors.length) | 0], s: shapes[(Math.random() * shapes.length) | 0],
      w: size * (0.6 + Math.random() * 0.8),
    };
  });
  const total = dur(o.duration ?? 2600);
  const t0 = performance.now();
  let last = t0;
  return new Promise((resolve) => {
    const frame = (now: number) => {
      const dt = Math.min(0.033, (now - last) / 1000);
      last = now;
      const life = (now - t0) / total;
      ctx.clearRect(0, 0, innerWidth, innerHeight);
      ctx.globalAlpha = Math.max(0, 1 - Math.max(0, life - 0.7) / 0.3);
      for (const p of parts) {
        p.vx -= p.vx * drag * dt;
        p.vy += g * dt - p.vy * drag * dt;
        p.x += p.vx * dt + Math.sin(p.flip) * 30 * dt;
        p.y += p.vy * dt;
        p.r += p.vr * dt;
        p.flip += 6 * dt;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.r);
        ctx.scale(1, Math.cos(p.flip));
        ctx.fillStyle = p.c;
        if (p.s === 'circle') {
          ctx.beginPath();
          ctx.arc(0, 0, p.w / 2.4, 0, Math.PI * 2);
          ctx.fill();
        } else if (p.s === 'star') {
          ctx.beginPath();
          for (let i = 0; i < 10; i++) {
            const rr = i % 2 ? p.w / 4 : p.w / 1.6;
            const aa = (i * Math.PI) / 5;
            ctx.lineTo(Math.cos(aa) * rr, Math.sin(aa) * rr);
          }
          ctx.fill();
        } else ctx.fillRect(-p.w / 2, -p.w / 4, p.w, p.w / 2);
        ctx.restore();
      }
      if (life < 1) requestAnimationFrame(frame);
      else {
        cv.remove();
        resolve();
      }
    };
    requestAnimationFrame(frame);
  });
}

export const confettiFx = defineEffect({
  id: 'confetti',
  name: 'Confetti',
  category: 'reward',
  description: 'Конфетти-хлопушка из точки элемента (победа, level up, крупная награда). Один canvas, сам удаляется.',
  defaults: { count: 120, spread: 70, power: 900, gravity: 1400, duration: 2600, size: 9 },
  params: {
    count: { label: 'количество', min: 10, max: 400, step: 5 },
    spread: { label: 'разброс, °', min: 10, max: 360, step: 5 },
    power: { label: 'сила выстрела', min: 200, max: 2000, step: 10 },
    gravity: { label: 'гравитация', min: 0, max: 3000, step: 50 },
    duration: { label: 'длительность, мс', min: 500, max: 6000, step: 100 },
    size: { label: 'размер', min: 3, max: 24, step: 1 },
  },
  run(el, p) {
    const c = center(el);
    return confetti({ ...p, x: c.x / innerWidth, y: c.y / innerHeight });
  },
});

// ---------------------------------------------------------------- Star burst
export const starBurst = defineEffect({
  id: 'starBurst',
  name: 'Star Burst',
  category: 'reward',
  description: 'Звёздочки/искры разлетаются кольцом от элемента (сбор предмета, апгрейд, клик по награде).',
  defaults: { count: 10, distance: 70, size: 14, duration: 650, color: 'gold' },
  params: {
    count: { label: 'количество', min: 3, max: 30, step: 1 },
    distance: { label: 'дистанция, px', min: 10, max: 250, step: 1 },
    size: { label: 'размер, px', min: 4, max: 40, step: 1 },
    duration: { label: 'длительность, мс', min: 200, max: 2000, step: 10 },
    color: { label: 'цвет', options: ['gold', 'white', 'cyan', 'hotpink', 'lime'] },
  },
  run(el, p) {
    if (prefersReducedMotion()) return;
    const c = center(el);
    const tasks = Array.from({ length: Number(p.count) }, (_, i) => {
      const s = document.createElement('span');
      s.className = 'uifx-star';
      Object.assign(s.style, { left: `${c.x}px`, top: `${c.y}px`, width: `${p.size}px`, height: `${p.size}px`, background: String(p.color) });
      layer().appendChild(s);
      const a = (i / Number(p.count)) * Math.PI * 2 + Math.random() * 0.4;
      const d = amp(Number(p.distance)) * (0.7 + Math.random() * 0.5);
      return s
        .animate(
          [
            { translate: '-50% -50%', scale: '0', rotate: '0deg', opacity: 1 },
            { translate: `calc(-50% + ${Math.cos(a) * d * 0.8}px) calc(-50% + ${Math.sin(a) * d * 0.8}px)`, scale: '1', rotate: '90deg', opacity: 1, offset: 0.55 },
            { translate: `calc(-50% + ${Math.cos(a) * d}px) calc(-50% + ${Math.sin(a) * d}px)`, scale: '0', rotate: '180deg', opacity: 0 },
          ],
          { duration: dur(Number(p.duration)), easing: 'cubic-bezier(0.22,1,0.36,1)' },
        )
        .finished.then(() => s.remove())
        .catch(() => s.remove());
    });
    return Promise.all(tasks);
  },
});

// ---------------------------------------------------------------- Progress fill with ghost trail
export function progressTo(bar: HTMLElement, value: number, o: { stiffness?: number; damping?: number; ghostDelay?: number } = {}): Promise<void> {
  bar.classList.add('uifx-progress');
  let fill = bar.querySelector<HTMLElement>(':scope > .uifx-progress-fill');
  let ghost = bar.querySelector<HTMLElement>(':scope > .uifx-progress-ghost');
  if (!ghost) {
    ghost = document.createElement('span');
    ghost.className = 'uifx-progress-ghost';
    bar.prepend(ghost);
  }
  if (!fill) {
    fill = document.createElement('span');
    fill.className = 'uifx-progress-fill';
    bar.appendChild(fill);
  }
  const v = Math.max(0, Math.min(1, value));
  const cur = parseFloat(fill.dataset.v ?? '0');
  fill.dataset.v = String(v);
  const f = fill, gh = ghost;
  if (prefersReducedMotion()) {
    f.style.scale = gh.style.scale = `${v} 1`;
    return Promise.resolve();
  }
  // Increase: light ghost jumps ahead (preview), fill springs after it with slight overshoot.
  // Decrease: fill snaps down, ghost drains after a delay (classic damage bar).
  const spring = { stiffness: o.stiffness ?? 260, damping: o.damping ?? 18, mass: 1 };
  const delay = o.ghostDelay ?? 250;
  let a: Animation;
  if (v >= cur) {
    a = play(gh, [{ scale: `${v} 1` }], { duration: 160, channel: 'progress' });
    a = playSpring(f, spring, (t) => ({ scale: `${Math.max(0, lerp(cur, v, t))} 1` }), { channel: 'progress', delay });
  } else {
    a = play(f, [{ scale: `${v} 1` }], { duration: 90, channel: 'progress' });
    a = play(gh, [{ scale: `${v} 1` }], { duration: 500, delay, easing: 'inOut', channel: 'progress' });
  }
  return a.finished.then(() => {}).catch(() => {});
}

export const progressFx = defineEffect({
  id: 'progressFill',
  name: 'Progress Fill',
  category: 'reward',
  description: 'Полоса прогресса/опыта/HP: пружинное заполнение с "призрачным" следом (вниз — как урон).',
  defaults: { value: 0.75, stiffness: 260, damping: 18, ghostDelay: 250 },
  params: {
    value: { label: 'значение 0..1', min: 0, max: 1, step: 0.01 },
    stiffness: springParams.stiffness,
    damping: springParams.damping,
    ghostDelay: { label: 'задержка следа, мс', min: 0, max: 1500, step: 10 },
  },
  run: (el, p) => progressTo(el, Number(p.value), p),
});

// ---------------------------------------------------------------- Reward pop (combo)
export const rewardPop = defineEffect({
  id: 'rewardPop',
  name: 'Reward Pop',
  category: 'reward',
  description: 'Комбо награды: предмет выпрыгивает с поворотом, вспышка-свечение и искры.',
  defaults: { scale: 0.35, rotate: 8, stiffness: 420, damping: 10, mass: 1 },
  params: {
    scale: { label: 'сила', min: 0, max: 1, step: 0.01 },
    rotate: { label: 'поворот, °', min: 0, max: 30, step: 1 },
    ...springParams,
  },
  run(el, p) {
    if (prefersReducedMotion()) return;
    starBurst.run(el, { ...starBurst.defaults, count: 8, distance: 60 });
    const s = 1 + amp(p.scale), r = amp(p.rotate);
    return playSpring(el, { stiffness: p.stiffness, damping: p.damping, mass: p.mass }, (t) => ({
      scale: String(lerp(s, 1, t)),
      rotate: `${lerp(-r, 0, t)}deg`,
    }), { channel: 'punch' });
  },
});
