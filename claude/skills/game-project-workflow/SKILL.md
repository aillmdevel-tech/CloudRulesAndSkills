---
name: game-project-workflow
description: Use when starting or steering a browser game project — a new game, a game spec/ТЗ, a prototype, a Roblox-like or Steam/indie-inspired game, or an undecided game idea ("создаём игру", "вот ТЗ", "начинай новый игровой проект", "реализуй Roblox-like", "сделай прототип", "делаем игру на PlayCanvas / на TypeScript без движка / на Three.js / 2D", "хочу придумать игру", "не определился с механикой"), and when resuming a game project in a new chat. Drives spec → material analysis → key questions → design → agreement → vertical slice → tests → fixes → next stage, picks the tech stack (PlayCanvas / Three.js / PixiJS / existing repo), routes to the right skills, guards the agreed scope, and keeps PROJECT_STATE.md / DECISIONS.md current between sessions.
---

# Game project workflow (GameFactory)

The process Alex uses for every game. It coordinates other skills; it does not replace them.

## 0. Orient (every session)

- Existing project: read its `CLAUDE.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/TASKS.md`
  first; `git status` before large edits. Don't re-read the whole codebase for a small change.
- New project: create the skeleton with
  `bash ~/.claude/skills/game-project-workflow/scripts/new_project.sh <GameName> [parent-dir] [--levelcopier] [--minimal]`
  (default parent: the games folder named in `~/.claude/CLAUDE.md`). It creates folders, project
  `CLAUDE.md` and doc templates only — code scaffolding happens after the stack is agreed.
- Size the process to the request: a bug fix or tweak skips stages 1–3 entirely.

## 1. Study

Read the spec. Route materials:
- video / screenshots / "повтори механику" → `game-reference-analysis`
- LevelCopier dumps, GLB+JSON scenes → `levelcopier-asset-pipeline`
- existing repo → detect the real stack from `package.json`/imports; never swap it without agreement.

Pick the stack with [references/stack-selection.md](references/stack-selection.md).

## 2. Clarify

List only questions whose answers change mechanics, architecture or scope. Up to ~5 per round, each
with a recommended answer; never re-ask what the spec/materials already answer. When the idea itself
is undecided or the design has many interlocking unknowns, invoke the `grilling` skill (keep its rounds
to ≤5 questions). Record every answer in `docs/DECISIONS.md` immediately.

## 3. Agree (no large implementation before this)

Present briefly: understanding of the game; core loop; controls & movement; camera; level structure;
UI; stack; architecture (modules, data flow, update order); the first vertical slice (exact contents
and acceptance criteria); what is deferred. Write it to `docs/GAME_DESIGN.md` + `docs/ARCHITECTURE.md`
+ `docs/TASKS.md` and wait for Alex's OK.

## 4. Build the vertical slice

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
