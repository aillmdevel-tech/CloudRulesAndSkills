---
name: game-project-workflow
description: Use when starting or steering a browser game project — a new game, a game spec/ТЗ, a prototype, a Roblox-like or Steam/indie-inspired game, or an undecided game idea ("создаём игру", "вот ТЗ", "начинай новый игровой проект", "реализуй Roblox-like", "сделай прототип", "делаем игру на PlayCanvas / на TypeScript без движка / на Three.js / 2D", "хочу придумать игру", "не определился с механикой"), and when resuming a game project in a new chat. Drives spec → material analysis → reference search → automatic grilling → pitch + staged plan → agreement → kickoff docs → ART FIRST (game-art-first: map/location/style in Blender) → MVP logic → tests → fixes → scale (new UI/locations), picks the tech stack (PlayCanvas / Three.js / PixiJS / existing repo), routes to the right skills, guards the agreed scope, and keeps PROJECT_STATE.md / DECISIONS.md current between sessions.
---

# Game project workflow (GameFactory)

The process Alex uses for every game. It coordinates other skills; it does not replace them.

## 0. Orient (every session)

- Existing project: use its loaded `CLAUDE.md` and the current block of `docs/PROJECT_STATE.md`.
  Read specific sections of `DECISIONS.md`, `TASKS.md` and other docs as needed. Run `git status`
  before large edits.
- New project: create the skeleton with
  `bash ~/.claude/skills/game-project-workflow/scripts/new_project.sh <GameName> [parent-dir] [--levelcopier] [--minimal]`
  (default parent: the games folder named in `~/.claude/CLAUDE.md`). It creates folders, project
  `CLAUDE.md` and doc templates only — code scaffolding happens after the stack is agreed.
- Size the process to the request: a bug fix or tweak skips stages 1–3 entirely.

## 1. Study

Read the spec. Route materials:
- video / screenshots / "повтори механику" → `game-reference-analysis` (for a whole game: also the detailed `docs/spec/` folders — mechanics, visual, ui, vfx, animation, camera, audio)
- LevelCopier dumps, GLB+JSON scenes → `levelcopier-asset-pipeline`
- existing repo → detect the real stack from `package.json`/imports; never swap it without agreement.

- original game named by Alex → research it on the web (store page, wiki, gameplay) into `REFERENCE_ANALYSIS.md`. The main reference (usually a Roblox game) carries the most weight; a web game must match the reference as closely as possible with own assets (no ripped files).
- inputs expected from Alex: short ТЗ (mechanics, requirements), original game name, video, screenshots, optional LevelCopier dump. Missing ones are not blocking — note the gap.
- find ready things (asset packs, GitHub projects, web/Steam games as visual benchmarks) → `game-art-first` §3 → `docs/REFERENCES.md`.

Pick the stack with [references/stack-selection.md](references/stack-selection.md).

## 2. Clarify (grilling starts automatically — Alex does not call it)

Once materials are studied, for any NEW game or big new stage run the `grilling` skill by yourself, no trigger
phrase needed. Rounds of ≤5 questions, each with your recommended answer ("yes" accepts it); never ask what the
spec/materials already answer; facts are found by you, decisions by Alex. Cover: core loop, controls/camera,
level structure, progression, UI, art direction/adaptation option, scope limits, stack. Record every answer in
`docs/DECISIONS.md` immediately. Small tasks: just a few plain questions, no grilling.

## 3. Agree (no large implementation before this)

Present briefly in this order: (a) how you see the game — core loop, controls, camera, level structure, UI;
(b) visual style and 3–4 adaptation options of the reference with a recommendation, plus found references/assets;
(c) stack and architecture; (d) STAGED plan from start to finish — **always visual first**:
1. Art: style board, map, location, key objects in Blender (`game-art-first`) → look approved by Alex.
2. MVP scene: logic on the approved scene (movement, camera, core loop, collisions, minimal UI) + tests.
3. Scale: more UI, locations, content, polish (`game-ui-motion-sound`), final QA.
Per stage: contents, acceptance criteria, who does it (see [../game-art-first/references/model-routing.md](../game-art-first/references/model-routing.md)); what is deferred.
Wait for Alex's OK; adjust until he confirms the understanding is the same.

## 3b. Kickoff — on Alex's «приступай»

Before any work write into the project: `docs/GAME_DESIGN.md`, `ARCHITECTURE.md`, `TASKS.md`, `REFERENCES.md`,
`ASSET_MANIFEST.md`, and the master plan `docs/plans/YYYY-MM-DD-master.md` (stages, step checkboxes, acceptance
criteria, verification commands, WHERE each reference/asset lives, model per step) + one line in `docs/plans/CURRENT.md`.
Project `CLAUDE.md` points to `PROJECT_STATE.md` and the master plan so later agents/chats orient fast.
Then run stage by stage: lead does design-heavy work itself (Opus high), delegates only independent mechanical steps
with a written spec and a verification command; check delegated results yourself. One new chat per big stage via `chat-handoff`.

## 4. Build — art first, then the vertical slice

- Stage 1 is `game-art-first`: no gameplay code until Alex approves the look (placeholders for logic are fine).
- The slice below starts only after that.

- Smallest set of finished, connected mechanics that proves the game. Priority comes from the spec
  (sometimes the lobby, sometimes the unique movement, sometimes the core loop).
- Scope guard: no extra levels, shop, ads, IAP, accounts, multiplayer, progression unless agreed.
  If something seems needed, ask — don't add it.
- Use real provided models/scenes; primitives only as clearly labelled placeholders (`// PLACEHOLDER`
  + listed in PROJECT_STATE).
- Stack skills: PlayCanvas → the relevant official skills only (`build-app` at bootstrap,
  `apply-conventions` when writing engine code, `find-examples`/`reuse-scripts` before writing a
  feature from scratch, `inspect-glb`/`load-assets`/`calibrate-model` for models, `configure-animation`,
  `assemble-scene`, `light-scene`, `add-effects`, `override-shader-chunks`, `reduce-draw-calls`/
  `bake-lighting` only after measuring, `inspect-runtime`/`verify-pixels` for checks).
  Three.js → see [references/threejs-skills.md](references/threejs-skills.md); never PlayCanvas skills.
  UI look → `frontend-design`; UI motion + sounds (every game UI) → `game-ui-motion-sound` (UIFX
  library; plan the event→effect/sound map in stage 3). Unusual locomotion → [references/procedural-motion.md](references/procedural-motion.md).
- Add a small debug surface from the start: `window.__game` (state, teleport, set camera, pause,
  seed RNG) behind `import.meta.env.DEV`, so tests and screenshots are deterministic.

## 5. Test (before saying "done")

`tsc --noEmit`, `npm run build`, run the dev server, then in a real browser (Playwright via
`webapp-testing`, or the built-in browser pane): no console errors, controls respond, game logic,
collisions/physics, camera, UI, frame time sanity. Visual claims need screenshots compared with the
reference (`game-visual-comparison`, `frontend-visual-qa` for DOM UI). A passing build is not proof
of correct graphics. Report what was actually run and its result; never claim untested passes.
Use the `game-autotest` wrapper for concise build and test output with full logs on disk.

## 6. Iterate

Alex playtests → turn feedback into `docs/TASKS.md` items → fix → re-verify the same way → update
`docs/PROJECT_STATE.md` (implemented / works / broken / agreed decisions / open tasks / next step)
at the end of every working session.

## Working style

- One lead agent. Subagents only for clearly independent heavy work (e.g. auditing a large asset
  dump while code is written); no background agents by default.
- Dependencies are per-project (npm), never global. Add a library only when it pays for itself.
- No refactors for beauty. Small iterations, each runnable.
- Publishing, uploading files to external services, deleting user files — ask first.
