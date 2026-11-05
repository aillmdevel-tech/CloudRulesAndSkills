# Stack selection

Pick from the spec's wording. Never combine engines in one project. No React/Next/Unity unless needed.

| Spec says | Mode | Stack |
|---|---|---|
| "PlayCanvas", "игра на PlayCanvas", "Roblox-like через PlayCanvas" | A | `playcanvas` Engine (Direct Engine API) + TypeScript + Vite + npm; GLB/glTF; HTML/CSS UI; physics via Ammo (engine `WasmModule`) when needed |
| "TypeScript без движка", "самописная игра", "с нужными библиотеками", "Three.js" | B | TypeScript + Vite + `three`; own game systems; `@dimforge/rapier3d-compat` if physics needed; HTML/CSS UI |
| "без Three.js и аналогов" | B' | propose raw WebGL2 (or WebGPU) and confirm first — big cost increase |
| 2D game | C | TypeScript + Vite + `pixi.js` (or Canvas 2D for very simple games) |
| existing repo | D | whatever the repo uses; read `package.json`/imports; no migration without agreement |

PlayCanvas mode is a **local source project**, not the cloud PlayCanvas Editor (only on explicit request).
Three.js is a renderer, not a game architecture: you still own loop, input, state, entities, camera.

## Scaffolding (after the stack is agreed)

- Mode A: `npm create vite@latest . -- --template vanilla-ts` then `npm i playcanvas`.
  `npx create-playcanvas` also exists (official scaffolder) — check its current templates with
  `npx create-playcanvas --help` and use it only if a template matches "Engine API + TS + Vite".
  Then follow the `build-app` skill (input is opt-in, resize handler, maxPixelRatio, Ammo loading).
- Mode B: `npm create vite@latest . -- --template vanilla-ts` then `npm i three` + `npm i -D @types/three`
  (+ `@dimforge/rapier3d-compat` when physics is agreed).
- Mode C: `npm create vite@latest . -- --template vanilla-ts` then `npm i pixi.js`.
- Tests: `npm i -D @playwright/test` and `npx playwright install chromium` in the project when the
  project gets automated tests; Python Playwright is installed user-wide for the `webapp-testing` skill.

Check the installed version (`npm ls <pkg>`) before relying on an API; prefer the official
examples matching that version (PlayCanvas: `find-examples`).

## Baseline project layout

```
src/
  main.ts            bootstrap only
  game/              state, rules, loop orchestration
  systems/           input, camera, physics, animation, audio, ui-bridge
  entities/          player, enemies, pickups...
  assets/            asset manifest/loaders
  debug/             window.__game, overlays (dev only)
public/assets/{models,textures,ui,audio}
tests/               Playwright specs (smoke, controls, screenshots)
```
Keep it smaller for small games.
