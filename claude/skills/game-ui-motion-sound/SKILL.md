---
name: game-ui-motion-sound
description: Use whenever building, restyling or polishing game UI/HUD/menus/popups/shops/reward screens in a browser game (PlayCanvas, Three.js, PixiJS or DOM overlay) — and when the user mentions UI animation, juice, "живой интерфейс", hover/click/jelly/bounce/pop-in effects, transitions, confetti, rewards, level up, UI sounds/SFX, or a reference video/screenshot shows animated UI. Picks fitting animations and sounds from the GameFactory UIFX library (32 spring-based effects, 43 CC0 UI sounds, 5 style presets: Roblox Cartoon, Playful Jelly, Casual Soft, Arcade, Clean Modern) based on the references, integrates them with volume control and reduced motion, and verifies them in the browser.
---

# Game UI motion & sound (GameFactory UIFX)

Library: `/Users/mac/Downloads/WebAIGames/Rules/GameFactory/UIFX` (path is also in `~/.claude/CLAUDE.md`).
Read its `README.md` for the API and the full effect/sound catalogue before integrating.
Demo with live sliders: `npm --prefix <UIFX> run demo` → http://localhost:5199 (use it to tune values and
show Alex options; "Экспорт конфига"/"JSON" give ready params).

## When this applies
Any game UI work: new HUD, menu, shop, inventory, popup, reward/level-up screen, buttons, notifications.
Also when a reference video shows UI motion. Not for tiny unrelated bug fixes. Never modify existing
games' UI unless asked for that game.

## Procedure
1. **Read references first** (video via `game-reference-analysis` `burst` on UI moments, screenshots).
   For each UI moment note: what moves, timing (count frames), overshoot/bounce, blur/dim, sounds heard
   (if the video has audio), particles. Mark facts vs guesses. Alex's references define look (icons,
   textures, fonts, composition) — UIFX only supplies motion and sound.
2. **Pick a base style preset** closest to the reference:
   `roblox-cartoon` (big springy, jelly buttons, pop-ins, coins fly) · `playful-jelly` (max wobble,
   squash & stretch) · `casual-soft` (gentle, slower, chimes) · `arcade` (fast, punchy, retro sounds)
   · `clean-modern` (subtle, no jelly/confetti).
3. **Map UI events → effects/sounds** (table in the plan), then override per event to match the
   reference (`fx.override('button.press', {...})`). Rules:
   - Every interactive control gets hover (mouse only) + press feedback; sound on press, not on hover
     spam (manager has cooldowns).
   - One attention loop per screen at most (shine/glow/heartbeat on the single main CTA or new item).
   - Big celebrations (confetti, level up, coin fly) only for real milestones.
   - Durations: press 60–120 ms, open 250–450 ms (spring), close 120–220 ms — close faster than open.
   - Don't stack effects on one element unless the reference does; less is better than more.
4. **Agree**: core feedback (hover/press/open/close/reward sounds) follows the reference and needs no
   separate approval. Ask Alex before adding *substantial extras* not in the references (camera zoom,
   confetti, idle loops, coin-fly sequences, new sound categories) — show them in the demo or list.
5. **Integrate**:
   `python3 <UIFX>/tools/install_uifx.py <project> --sounds id1,id2,...` (copies `src/` → `src/uifx/`,
   chosen sounds → `public/assets/audio/ui/` with filtered `sounds.json` and credits). Then:
   ```ts
   import './uifx/uifx.css';
   import { createUIFX } from './uifx';
   const fx = await createUIFX({ style: 'roblox-cartoon', soundsUrl: '/assets/audio/ui/',
     overrides: { 'button.press': { sound: 'click_soft' } } });
   fx.bind(document);                     // data-uifx="button" / "button cta"
   await fx.open(win, { backdrop, camera: canvasWrapper, list: grid });
   fx.reward.coins(chestEl, coinCounterEl, newTotal);
   ```
   - In-engine UI (PlayCanvas screen elements, Pixi containers, Three sprites): use `animateValue`,
     `SpringValue`, `bakeSpring` from UIFX and apply values to entity scale/position/opacity; play
     sounds through the same `SoundManager` (or the engine's audio if the project already uses it).
   - Camera zoom on a 3D scene: `cameraZoomSpring(z => camera.fov = baseFov / z)` instead of CSS.
   - Expose a settings UI or at least `fx.sound.volume`/`muted` and `configure({ reducedMotion })`.
   - Record chosen preset + overrides in the project's `docs/DECISIONS.md`; keep params in one
     config file (e.g. `src/ui/fx-config.ts`) so Alex can tweak quickly.
6. **Verify in the browser** (`webapp-testing` / built-in browser, `game-visual-comparison` against the
   reference): no console errors, every control reacts, effects interrupt cleanly when spam-clicked,
   sounds load (network 200) and respect mute/volume, reduced motion = no scale/translate motion,
   no layout shift, 60 fps on the target device (only transform/opacity animate; ≤1 confetti canvas).
   Report what was checked; Alex judges the feel by playing.

## New sounds
Only verified commercial-safe licences: CC0 preferred (Kenney, Freesound CC0). CC-BY only with credit
recorded in `SOUND_CREDITS.md`. Pixabay — usable inside a game, not as a redistributed pack. ElevenLabs /
any paid generation — ask Alex first and check the plan's commercial terms. Add new library sounds via
`UIFX/tools/build_sounds.py` (normalises, encodes ogg+mp3, updates manifest and credits) or synthesise
in `tools/synth_sounds.py`.

## Extending the library
New effects go into `UIFX/src/effects/*.ts` via `defineEffect` (defaults + param schema + run/attach,
reduced-motion branch, interruptible channel) and are registered in `effects/index.ts`; they appear in
the demo automatically. Then run `npm --prefix <UIFX> run typecheck` and re-run GameFactory backup.
