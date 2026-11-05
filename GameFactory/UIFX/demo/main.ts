import '../src/uifx.css';
import {
  createUIFX, EFFECTS, STYLES, configure, config, progressTo, interrupt,
  type EffectDef, type Handle, type Params, type ParamSpec, type UIEvent,
} from '../src';

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;

const fx = await createUIFX({ style: 'roblox-cartoon', soundsUrl: './' });
(window as unknown as { fx: typeof fx }).fx = fx; // for console experiments

// ------------------------------------------------------------------ top controls
const styleSel = $<HTMLSelectElement>('style');
for (const s of Object.values(STYLES)) styleSel.add(new Option(s.name, s.id));
const vol = $<HTMLInputElement>('vol');
const mute = $<HTMLInputElement>('mute');
const rm = $<HTMLSelectElement>('rm');
const intensity = $<HTMLInputElement>('intensity');
const speed = $<HTMLInputElement>('speed');

function syncControls() {
  styleSel.value = fx.style.id;
  $('styleDesc').textContent = fx.style.description;
  intensity.value = String(config.intensity);
  speed.value = String(config.speed);
  $('intensityOut').textContent = config.intensity.toFixed(2);
  $('speedOut').textContent = config.speed.toFixed(2);
  rm.value = config.reducedMotion;
}
vol.value = String(fx.sound?.volume ?? 0.8);
mute.checked = fx.sound?.muted ?? false;
vol.oninput = () => fx.sound && (fx.sound.volume = Number(vol.value));
mute.onchange = () => fx.sound && (fx.sound.muted = mute.checked);
rm.onchange = () => configure({ reducedMotion: rm.value as 'auto' });
intensity.oninput = () => (configure({ intensity: Number(intensity.value) }), syncControls());
speed.oninput = () => (configure({ speed: Number(speed.value) }), syncControls());
styleSel.onchange = () => {
  const keep = config.reducedMotion;
  fx.setStyle(styleSel.value);
  configure({ reducedMotion: keep });
  rebindGame();
  syncControls();
};
$('export').onclick = () => {
  $('exportPre').textContent = fx.exportConfig();
  $<HTMLDialogElement>('exportDlg').showModal();
};

// ------------------------------------------------------------------ game example
let binding: Handle | null = null;
let bellLoop: Handle | null = null;
function rebindGame() {
  binding?.stop();
  document.querySelectorAll<HTMLElement>('#game [data-uifx]').forEach((el) => {
    fx.unbind(el);
    delete el.dataset.uifxBound;
  });
  binding = fx.bind($('game'));
  bellLoop?.stop();
  if (!$('badge').hidden) {
    const r = fx.trigger('notify', $('badge'));
    bellLoop = r && 'stop' in r ? r : null;
  }
}

const coins = $('coins');
let coinTotal = 250;
let xp = 0.3;
let lvl = 3;
const scene = $('scene'), overlay = $('overlay'), shop = $('shop'), title = $('title');

progressTo($('xpbar'), xp);
rebindGame();
fx.trigger('title.in', title);
syncControls();

$('shopBtn').onclick = () => fx.open(shop, { backdrop: overlay, camera: scene, list: $('shopList') });
$('closeShop').onclick = () => fx.close(shop, { backdrop: overlay, camera: scene });
overlay.onclick = () => fx.close(shop, { backdrop: overlay, camera: scene });
$('buyItem').onclick = () => {
  if (coinTotal < 100) return void fx.error($('buyItem'));
  coinTotal -= 100;
  void fx.reward.count(coins, coinTotal, { duration: 400 });
  fx.success($('buyItem'));
};

$('chestBtn').onclick = async () => {
  fx.reward.item($('chestBtn'));
  coinTotal += 120;
  xp = Math.min(1, xp + 0.25);
  void progressTo($('xpbar'), xp);
  await fx.reward.coins($('chestBtn'), coins, coinTotal, 12);
};

$('lvlBtn').onclick = () => {
  lvl += 1;
  $('lvl').textContent = String(lvl);
  xp = 0.05;
  void progressTo($('xpbar'), xp);
  title.dataset.uifxText = `LEVEL ${lvl}!`;
  fx.levelUp(title);
  setTimeout(() => {
    title.dataset.uifxText = 'SKY ISLAND';
    fx.trigger('title.in', title);
  }, 2600);
};

$('dmgBtn').onclick = () => {
  xp = Math.max(0, xp - 0.2);
  void progressTo($('xpbar'), xp);
  fx.error($('xpbar'));
};

$('bell').onclick = () => {
  bellLoop?.stop();
  bellLoop = null;
  $('badge').hidden = true;
  setTimeout(() => {
    $('badge').hidden = false;
    rebindGame();
  }, 4000);
};

$('panelBtn').onclick = () => fx.panelIn($('panel'), 'right');
$('closePanel').onclick = () => fx.panelOut($('panel'), 'right');
$('toastBtn').onclick = () => fx.toast($('toast'));
const sw = $<HTMLInputElement>('sw');
sw.onchange = () => fx.toggle(sw.parentElement!.querySelector('.knob')!, sw.checked);

// ------------------------------------------------------------------ effects gallery
const CAT_RU: Record<string, string> = {
  press: 'нажатие', hover: 'наведение', window: 'окна', sequence: 'последовательность',
  attention: 'внимание', reward: 'награды', feedback: 'обратная связь', text: 'текст',
};

function stageFor(def: EffectDef): { stage: HTMLElement; target: HTMLElement } {
  const stage = document.createElement('div');
  stage.className = 'stage';
  stage.dataset.uifxScope = '';
  const mk = (cls: string, html: string) => {
    const t = document.createElement('div');
    t.className = cls;
    t.innerHTML = html;
    stage.appendChild(t);
    return t;
  };
  switch (def.id) {
    case 'stagger':
      return { stage, target: mk('chips', '<span>⚔️</span><span>🛡️</span><span>🧪</span><span>💎</span><span>🐲</span>') };
    case 'cameraZoom':
      return { stage, target: mk('mini-scene', '<div class="sun"></div><div class="hill h1"></div>') };
    case 'backdrop': {
      mk('stage-bg', '🏝️ 🌳 🏠 🌳 ⛰️');
      return { stage, target: mk('stage-overlay', '') };
    }
    case 'progressFill': {
      const t = mk('bar demo-bar', '');
      return { stage, target: t };
    }
    case 'countUp':
      return { stage, target: mk('big-num', '0') };
    case 'coinFly': {
      mk('pill mini', '<span class="uifx-coin"></span><span data-uifx-counter>0</span>');
      return { stage, target: mk('btn gold small', '🎁') };
    }
    case 'textWave':
    case 'typewriter':
      return { stage, target: mk('demo-title', def.id === 'textWave' ? 'VICTORY!' : 'Press E to open the chest') };
    case 'popIn': case 'popOut': case 'slideIn': case 'slideOut': case 'dropIn': case 'flipIn':
      return { stage, target: mk('mini-window', '<b>WINDOW</b><span>Lorem ipsum</span>') };
    case 'floatingText': case 'confetti': case 'starBurst': case 'rewardPop':
      return { stage, target: mk('btn gold', '💰') };
    default:
      return { stage, target: mk('btn green', def.category === 'attention' ? 'CLAIM' : 'BUTTON') };
  }
}

function control(name: string, spec: ParamSpec, value: number | string, set: (v: number | string) => void): HTMLElement {
  const row = document.createElement('label');
  row.className = 'param';
  row.append(document.createTextNode(spec.label));
  if ('options' in spec) {
    const s = document.createElement('select');
    spec.options.forEach((o) => s.add(new Option(o, o)));
    s.value = String(value);
    s.onchange = () => set(s.value);
    s.name = name;
    row.append(s);
  } else {
    const i = document.createElement('input');
    Object.assign(i, { type: 'range', min: spec.min, max: spec.max, step: spec.step, value, name });
    const out = document.createElement('output');
    out.textContent = String(value);
    i.oninput = () => {
      out.textContent = i.value;
      set(Number(i.value));
    };
    row.append(i, out);
  }
  return row;
}

const cards: { el: HTMLElement; cat: string }[] = [];
for (const def of Object.values(EFFECTS)) {
  const card = document.createElement('article');
  card.className = 'fx-card';
  card.innerHTML = `<header><b>${def.name}</b><code>${def.id}</code><i>${CAT_RU[def.category] ?? def.category}</i></header><p>${def.description}</p>`;
  const { stage, target } = stageFor(def);
  card.appendChild(stage);
  let params: Params = { ...def.defaults };
  let attachH: Handle | null = null;
  let loopH: Handle | null = null;
  const reattach = () => {
    attachH?.stop();
    attachH = def.attach ? def.attach(target, () => params) : null;
  };
  reattach();
  const run = async () => {
    if (def.loop) {
      if (loopH) {
        loopH.stop();
        loopH = null;
        playBtn.textContent = '▶ Старт';
        return;
      }
      const r = def.run(target, params);
      loopH = r && 'stop' in r ? r : null;
      playBtn.textContent = '■ Стоп';
      return;
    }
    if (def.id === 'backdrop') {
      target.style.position = 'absolute';
      await def.run(target, { ...params, mode: 'show' });
      setTimeout(() => def.run(target, { ...params, mode: 'hide' }), 900);
      return;
    }
    const r = def.run(target, params, { clientX: target.getBoundingClientRect().left + 20, clientY: target.getBoundingClientRect().top + 10 });
    if (['popOut', 'slideOut'].includes(def.id)) {
      if (r && 'finished' in r) await r.finished.catch(() => {});
      setTimeout(() => {
        for (const ch of ['pop', 'slide', 'fade']) interrupt(target, ch);
        target.style.opacity = target.style.scale = target.style.translate = '';
      }, 400);
    }
  };
  const playBtn = document.createElement('button');
  playBtn.className = 'btn blue small';
  playBtn.textContent = def.loop ? '▶ Старт' : '▶ Играть';
  playBtn.onclick = run;
  const reset = document.createElement('button');
  reset.className = 'ghost small';
  reset.textContent = 'Сброс';
  const copy = document.createElement('button');
  copy.className = 'ghost small';
  copy.textContent = 'JSON';
  copy.onclick = () => {
    const json = JSON.stringify({ effect: def.id, params }, null, 2);
    navigator.clipboard?.writeText(json).catch(() => {});
    $('exportPre').textContent = json;
    $<HTMLDialogElement>('exportDlg').showModal();
  };
  const actions = document.createElement('div');
  actions.className = 'actions';
  actions.append(playBtn, reset, copy);
  if (def.attach) {
    const hint = document.createElement('small');
    hint.textContent = def.category === 'hover' ? 'наведи на кнопку' : 'нажми на кнопку';
    actions.append(hint);
  }
  card.appendChild(actions);
  const form = document.createElement('div');
  form.className = 'params';
  const buildForm = () => {
    form.innerHTML = '';
    for (const [k, spec] of Object.entries(def.params)) {
      if (!spec) continue;
      form.appendChild(
        control(k, spec, params[k], (v) => {
          params = { ...params, [k]: v };
          if (loopH) {
            loopH.stop();
            loopH = null;
            void run();
          }
        }),
      );
    }
  };
  reset.onclick = () => {
    params = { ...def.defaults };
    buildForm();
    reattach();
  };
  buildForm();
  card.appendChild(form);
  $('fxGrid').appendChild(card);
  cards.push({ el: card, cat: def.category });
}

const filter = $('fxFilter');
for (const cat of ['all', ...new Set(cards.map((c) => c.cat))]) {
  const b = document.createElement('button');
  b.className = 'chip';
  b.textContent = cat === 'all' ? 'все' : CAT_RU[cat] ?? cat;
  b.onclick = () => {
    filter.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === b));
    cards.forEach((c) => (c.el.hidden = cat !== 'all' && c.cat !== cat));
  };
  filter.appendChild(b);
}
(filter.firstElementChild as HTMLElement).classList.add('on');

// ------------------------------------------------------------------ sounds
const CAT_SND: Record<string, string> = { ui: 'Кнопки и элементы', window: 'Окна и панели', feedback: 'Уведомления, успех, ошибки', reward: 'Награды' };
if (fx.sound) {
  const snd = fx.sound;
  const entries = Object.entries(snd.manifest.sounds);
  for (const cat of Object.keys(CAT_SND)) {
    const bus = document.createElement('label');
    bus.className = 'param';
    bus.append(`шина ${cat}`);
    const i = Object.assign(document.createElement('input'), { type: 'range', min: 0, max: 1, step: 0.01, value: snd.getBusVolume(cat) });
    i.oninput = () => snd.setBusVolume(cat, Number(i.value));
    bus.append(i);
    $('buses').append(bus);

    const g = document.createElement('div');
    g.className = 'snd-group';
    g.innerHTML = `<h3>${CAT_SND[cat]}</h3>`;
    const grid = document.createElement('div');
    grid.className = 'snd-grid';
    for (const [id, e] of entries.filter(([, e]) => e.category === cat)) {
      const b = document.createElement('button');
      b.className = 'snd';
      b.innerHTML = `<b>${id}</b><span>${e.description ?? ''}</span><small>${e.duration?.toFixed(2)}s · ${(e.source ?? '').replace('GameFactory synth (tools/synth_sounds.py)', 'synth GameFactory')} · ${e.license}</small>`;
      b.onclick = () => {
        void snd.play(id, { cooldown: 0 });
        fx.play('punch', b, { scale: 0.08 });
      };
      grid.appendChild(b);
    }
    g.appendChild(grid);
    $('soundGrid').appendChild(g);
  }
} else {
  $('soundGrid').textContent = 'Звуки не загрузились (см. консоль).';
}

// expose event names for console use: fx.trigger('success', el)
(window as unknown as { UI_EVENTS: UIEvent[] }).UI_EVENTS = Object.keys(fx.slots) as UIEvent[];
