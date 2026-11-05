# UIFX — анимации и звуки игрового UI

Переиспользуемая библиотека GameFactory: 32 эффекта на пружинной физике, 43 звука CC0, 5 стилевых пресетов,
интерактивная демостраница. TypeScript, **без зависимостей**, работает в любом стеке (DOM-оверлей поверх
PlayCanvas / Three.js / PixiJS; для UI внутри движка — `animateValue` / `SpringValue`).
Автоматически применяется скиллом `game-ui-motion-sound`.

## Демо

```bash
cd /Users/mac/Downloads/WebAIGames/Rules/GameFactory/UIFX && npm install && npm run demo
```

Открой http://localhost:5199. Там можно переключать стиль, громкость, reduced motion, интенсивность и скорость.
Каждый эффект настраивается ползунками, звуки проигрываются по клику. Кнопки «Экспорт конфига» и «JSON» отдают готовые параметры.

## Подключение к игре

```bash
python3 /Users/mac/Downloads/WebAIGames/Rules/GameFactory/UIFX/tools/install_uifx.py <папка-игры> --sounds click,hover,pop,open,close,coin,reward
```

```ts
import './uifx/uifx.css';
import { createUIFX } from './uifx';

const fx = await createUIFX({
  style: 'roblox-cartoon',                 // roblox-cartoon | playful-jelly | casual-soft | arcade | clean-modern
  soundsUrl: '/assets/audio/ui/',
  overrides: { 'button.press': { effect: 'pressDepth', sound: 'click_soft' } },
});
fx.bind(document);                          // <button data-uifx="button">, data-uifx="button cta" (+ блик)
await fx.open(shopEl, { backdrop: overlayEl, camera: sceneEl, list: gridEl });
await fx.close(shopEl, { backdrop: overlayEl, camera: sceneEl });
fx.reward.coins(chestEl, coinCounterEl, 1370);   // монеты летят в счётчик + накрутка + звук
fx.levelUp(titleEl); fx.error(buyBtn); fx.success(el); fx.toast(toastEl); fx.panelIn(panel, 'right');
fx.play('glossyShine', ctaEl, { interval: 2000 });   // любой эффект напрямую
fx.sound?.play('coin', { pitch: 2 });                 // любой звук; volume / muted / setBusVolume
configure({ reducedMotion: 'auto', intensity: 1, speed: 1 });
```

Семантические события стиля: `button.hover`, `button.press`, `button.click`, `button.cta`, `window.open`, `window.close`,
`window.backdrop`, `window.camera`, `panel.in`, `panel.out`, `list.in`, `toast.in`, `toggle.on`, `toggle.off`, `tab.change`,
`notify`, `success`, `error`, `reward.item`, `reward.coins`, `reward.count`, `reward.big`, `levelUp`, `title.in`.
Любое событие можно переопределить: `fx.override(event, { effect, params, sound })`. Для отключения укажи `'none'`.

## Эффекты (32)

| id | Эффект | Ключевые параметры |
|---|---|---|
| jellyPress | Jelly Press — желейное нажатие и упругий отскок | squashX/Y, pressMs, stiffness, damping, mass |
| squashStretch | Squash & Stretch — прыжок со сжатием/растяжением | squash, stretch, height, duration, spring |
| pressDepth | вдавливание объёмной кнопки | depth, pressMs, spring |
| ripple | волна из точки нажатия | duration, opacity, size, color |
| hoverTilt | Hover Scale/Tilt + блик (3D) | scale, angle, glare, spring |
| hoverLift | подъём при наведении | lift, scale, spring |
| magnetic | кнопка тянется за курсором | strength, spring |
| popIn / popOut | появление из малого масштаба с отскоком / закрытие | fromScale, rotate, fadeMs, delay, spring / toScale, anticipation, duration, ease |
| slideIn / slideOut | вылет панели сбоку/сверху/снизу | from/to, distance, spring / duration, ease |
| dropIn | тост падает с отскоком | distance, spring |
| flipIn | переворот карточки (награда) | angle, spring |
| backdrop | Background Blur — размытие и затемнение фона | blur, dim, duration, tint, mode |
| cameraZoom | приближение «камеры» (punch/in/out) | zoom, mode, hold, spring |
| stagger | последовательное появление детей | each, from, effect (popIn/slideUp/flipIn/fade) |
| glossyShine | периодический блик по кнопке | interval, jitter, duration, angle, width, opacity |
| glow | пульсирующее свечение | color, size, intensity, period |
| heartbeat | двойной «удар сердца» (бейджи) | scale, interval, duration |
| wiggle | покачивание-зов | angle, duration, interval, once |
| breathe | парение/дыхание в покое | float, scale, period |
| shake | затухающая тряска (ошибка) | distance, shakes, duration |
| punch | пружинный толчок масштаба | scale, spring |
| countUp | накрутка числа | to, duration, ease, punch |
| floatingText | всплывающее «+10» | text, rise, duration, scale |
| coinFly | монеты по дуге в счётчик | count, arc, duration, stagger, spread |
| confetti | конфетти (один canvas) | count, spread, power, gravity, duration, size |
| starBurst | искры кольцом | count, distance, size, duration, color |
| progressFill | полоса с «призрачным» следом (XP/HP) | value, spring, ghostDelay |
| rewardPop | комбо награды: толчок + поворот + искры | scale, rotate, spring |
| textWave | буквы выпрыгивают по очереди | each, height, spring |
| typewriter | печать по буквам | cps |

Сверх твоего списка я добавил: pressDepth, ripple, magnetic, hoverLift, dropIn, flipIn, heartbeat, wiggle, breathe, shake, punch,
floatingText, coinFly, starBurst, progressFill, rewardPop, textWave, typewriter. Это стандартные приёмы «game juice».

## Звуки (43, все CC0)

| Группа | id |
|---|---|
| Кнопки | hover, hover_alt, hover_bubble*, click, click_alt, click_soft, jelly_click*, jelly_release*, squish*, select, toggle_on, toggle_off, tick, tick_soft*, back |
| Окна | open, close, open_alt, close_alt, pop*, whoosh_in*, whoosh_out*, drop |
| Обратная связь | notify, notify_chime*, notify_glass, success, success_chime*, success_big, error, error_soft*, error_buzz, question |
| Награды | coin*, counter_tick*, reward*, reward_alt, sparkle*, confetti*, level_up*, level_up_alt, level_up_retro, unlock |

\* — синтезированы скриптом `tools/synth_sounds.py`. Остальные — Kenney: Interface Sounds, UI Audio и Digital Audio.
Источники и лицензии описаны в [SOUND_CREDITS.md](SOUND_CREDITS.md). Каждый звук есть в двух форматах, `.ogg` (Opus) и `.mp3`, менеджер сам выбирает подходящий.
Громкость, вариация высоты тона и категория хранятся в `sounds/sounds.json`.

## Производительность и доступность
- Анимируются только `scale`, `translate`, `rotate` и `opacity`. Это отдельные CSS-свойства, поэтому они не затирают `transform` игры.
- Анимация на том же элементе и канале прерывает предыдущую с текущего положения, без рывков.
- Reduced motion берётся из ОС или задаётся принудительно. Движение тогда заменяется короткими fade, циклы и конфетти отключаются.
- Звук: шины по категориям, master volume и mute сохраняются в localStorage. Есть cooldown против спама hover и лимит голосов. Аудио разблокируется по первому жесту.

## Структура
```
UIFX/
  src/            библиотека (копируется в игру как src/uifx/)
    core/         config (reduced motion, intensity, speed), spring, animate (WAAPI + rAF)
    effects/      interactive, motion, reward, index (реестр EFFECTS)
    sound.ts      SoundManager
    styles.ts     5 стилевых пресетов
    index.ts      createUIFX / UIFX
    uifx.css
  sounds/         43 × (.ogg + .mp3) + sounds.json
  sources/        исходные паки Kenney с License.txt + синтезированные WAV
  tools/          synth_sounds.py, build_sounds.py, install_uifx.py
  demo/           демостраница (Vite)
  SOUND_CREDITS.md
```

Пересобрать звуки после правок генератора или списка: `npm run sounds`.
Проверить типы после добавления эффекта: `npm run typecheck`.
