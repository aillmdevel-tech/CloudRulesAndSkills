---
name: game-project-workflow
description: Use when starting or steering a browser game project — a new game, a «быстрая игра» (2–5 day portfolio test), a game spec/ТЗ, a prototype, a Roblox-like or Steam/indie-inspired game, or an undecided game idea ("создаём игру", "вот ТЗ", "новый Roblox-like проект", "материалы в input/", "начинай новый игровой проект", "сделай прототип", "MVP принят", "разбери правки"), and when resuming a game project in a new chat. Runs Alex's single pipeline — idea filter (15 questions) → materials → spec + 17-column player-path skeleton with gaps → gap-only questions → Steam style approval + budget → ready-made assets/projects search → plan → MVP scene with three checkpoints (style frame, game feel + first-minute check, finished scene) → expansion → post-launch funnel — in ONE chat, routes to the right skills, guards the agreed scope, keeps PROJECT_STATE.md / DECISIONS.md current.
---

# Game project workflow (GameFactory)

The human version of this pipeline is `GameFactory/WORKFLOW.md`; keep both identical in meaning. This skill coordinates other skills; it does not replace them.

## Always
- **One chat per project.** Never start sessions or new chats; never offer session cards. Subagents only for bulky routine (video → frames, code search, smoke) with a ≤10-line report; the lead checks the result. New chat only when Alex writes «упакуй контекст» (`chat-handoff` save mode) or starts another project.
- **Model and effort are Alex's choice.** Don't switch or request them; if a task seems to need a different level, say so in one line.
- **Package loop** after every batch of game edits: code → `tsc --noEmit` + build → smoke (`game-autotest`) → reference | game screenshots (`game-visual-comparison`) → fix top diffs → git commit → update `docs/PROJECT_STATE.md` + memory-bank.
- **Add nothing of your own.** Scope = ТЗ + Alex's answers. Any extra idea is a question, never an implementation.
- **Design filter:** every decision is checked against `<GameFactory>/DESIGN/CONSTITUTION.md` (5-step formula, first minute, 3-horizon goals, 20 bans). A violation in the ТЗ or in your plan is raised as a question, never silently fixed.
- **Bug shield:** before a package of edits read the headings + «Правило» lines of `<GameFactory>/LESSONS/<topic>.md` for the touched area; after a non-trivial fix append a lesson there (format in `LESSONS/README.md`).
- **Mechanics library:** a mechanic Alex accepted, or one that took >2 iterations → `<GameFactory>/MECHANICS/<genre>-<name>.md` (template `_TEMPLATE.md`) + its test in `tools/mechanics.py`; new plans look there first.
- Size the process to the request: a bug fix or tweak skips steps −1…6.

## 0. Orient
- Existing project: project `CLAUDE.md`, the current block of `docs/PROJECT_STATE.md`, then only the docs the task needs. `git status` before large edits.
- New project: `bash ~/.claude/skills/game-project-workflow/scripts/new_project.sh <GameName> [parent-dir] [--levelcopier] [--minimal]` (folders, project `CLAUDE.md`, doc templates; code after the plan).

## −1. Idea (no game yet, or the idea was never filtered)
Ideas from `game-idea-scout` or Alex → 15 questions (`DESIGN/IDEA_FILTER.md`) → `docs/IDEA.md` (template). Any of questions 1–3 = 0 → stop and offer two fixes of fantasy/action. Similar games and patterns: `game-design-library` (consult mode).

## 1. Materials
Alex puts the Roblox original video, its transcript and the full ТЗ (whole game loop) into `input/`. Steam links for style → add to `GameFactory/StyleLibrary` (its README). Missing materials are not blocking: note the gap.

## 2. Analysis (no code)
- Video/screenshots → `game-reference-analysis`; LevelCopier/GLB+JSON → `levelcopier-asset-pipeline`; original game named → web research into `docs/REFERENCE_ANALYSIS.md`.
- Output: `docs/spec/` (mechanics, visual, ui, vfx, animation, camera, audio). Tag every item **[видно]** (seen in video), **[из ТЗ]**, or **[пробел]** (gap or contradiction between ТЗ and video).
- Also `docs/GAME_SKELETON.md` (template; questions per column in `DESIGN/SKELETON.md`): 17 columns of the player's path. Empty column = **[пробел]**. Patterns for holes from `game-design-library`, offered as recommendations in step 3. Optional board: `python3 <GameFactory>/DESIGN/tools/skeleton_canvas.py docs/GAME_SKELETON.md`.

## 3. Gap-only questions (start yourself, Alex doesn't call it)
Use the `grilling` round format, with these rules overriding it:
- Ask only about **[пробел]** items and ТЗ/video contradictions. Never ask what the ТЗ or video already answers; never propose new features.
- ≤5 questions per round, numbered, each with your recommended implementation; «не знаю» or «да» accepts it.
- Record every answer in `docs/DECISIONS.md` immediately and retag the spec item and skeleton column.
- **Gate: no code until every [пробел] is closed.**

## 4. Style and budget
- `game-art-first` §0: board of 3–6 Steam games fitting this ТЗ (StyleLibrary first) → Alex approves one.
- `docs/ART_SPEC.md`: palette, light, post, brightness/saturation corridor, the one signature trick.
- `docs/GAME_DESIGN.md` «Бюджет»: build size, FPS on a weak laptop, draw calls. Checked in every package loop.
- Stack: [references/stack-selection.md](references/stack-selection.md); Three.js = `GameFactory/THREEJS_STACK.md`.

## 5. Ready-made (after style approval, before the plan)
One pass via `game-art-first` §3: CC0 assets in the approved style (Poly Haven, Poly Pizza, Kenney, Quaternius; Blender MCP `search_assets`), open GitHub projects with similar mechanics, libraries → `docs/REFERENCES.md` (link, licence, what we take, fit 1–5). Download only after Alex's OK.

## 6. Plan
Briefly: how you see the game, what is reused from `REFERENCES.md` and `MECHANICS/` vs built in Blender, exact MVP contents (step 7), stages to the end. Write `docs/plans/YYYY-MM-DD-master.md` (stages, checkboxes, acceptance criteria, verification commands, where each reference/asset lives) + one line in `docs/plans/CURRENT.md`. Start on «приступай».

## 7. MVP scene = the first 2–3 minutes of the game from the ТЗ
Small but fully finished. The first minute is a small version of the whole game: fantasy in 3 s, first action ≤ 10 s, world changes ≤ 30 s, next goal visible ≤ 60 s (`CONSTITUTION.md` §3). Funnel events from the start: copy `templates/funnel/funnel.ts` → `src/funnel.ts`, `funnel.mark(...)` at each step (`DESIGN/FUNNEL.md`). Game feel, mechanics, elements, VFX and character come from the Roblox original; the look from the approved Steam game.
- **Contents:** one starting zone built in Blender in the approved style (ground, borders, 5–10 decor kinds, sky, fog, light); character or vehicle with controls, camera and animations as in the original; 3–5 interactive object kinds with physics and collisions; one complete short loop from the ТЗ (action → result → reward); VFX, post-processing, action sounds and royalty-free music; minimal HUD.
- **Not included:** other locations, progression, shop, saves, platform SDK, mobile controls (unless the ТЗ needs them now).
- **Three checkpoints for Alex**, work autonomously between them:
  - **A. Style frame** — a corner of the zone in Blender + engine screenshot beside the Steam reference (`game-art-first`).
  - **B. Game feel + first minute** — controls, camera and core mechanic on that zone, compared with the original video; all feel parameters in one config file. Then `npm run first-minute` + the cold-read subagent on its sheet (`DESIGN/FIRST_MINUTE.md`, via `game-autotest`) and `npm run mechanics`; failures → `docs/TASKS.md` before showing B.
  - **C. Finished scene** — objects, loop, VFX, sound, HUD, budget met; game link + comparison sheets + «как в оригинале / отличается и почему».
- Real provided models/scenes; primitives only as labelled placeholders (`// PLACEHOLDER` + listed in PROJECT_STATE).
- Debug surface from the start: `window.__game` (state, teleport, set camera, pause, seed RNG) behind `import.meta.env.DEV`.
- Stack skills: Three.js → `threejs-aaa-graphics-builder` (render polish after A, scorecard for C) and `threejs-debug-profiler` (bugs, lags, budget), see [references/threejs-skills.md](references/threejs-skills.md); PlayCanvas → its skills only if Alex enabled them. UI → `frontend-design` + `game-ui-motion-sound` (UIFX). Characters → `character-animation`. Unusual locomotion → [references/procedural-motion.md](references/procedural-motion.md).

## 8. Expansion to the end
After «MVP принят»: stages of the master plan (locations, content, economy, UI, platforms), each package with the package loop. Alex's feedback (text or voice video) is analysed like step 2 → `docs/TASKS.md` → fix → verify. Before submission: moderator (`game-autotest`) and promo materials (`game-promo-kit`: ad/preview videos, screenshots, covers per platform rules and language).

## 9. After launch: funnel
3–7 days after publishing: platform dashboard numbers + our event diary → biggest drop → one gameplay change → new build → new funnel (`DESIGN/FUNNEL.md`; `retro` funnel mode). Numbers in `docs/LAUNCH.md`, card `DesignLibrary/games/our-<slug>.md`. Holds players → invest (content, Roblox port `DESIGN/ROBLOX.md`); doesn't → lesson to the base, next idea.

## Fast game («быстрая игра»)
Portfolio mode, publish in 2–5 days: steps −1 → 2 (skeleton) → 7 reduced. One zone, one main action, one loop, 3-horizon goals (the long one shown, not built), funnel, platform SDK. Style from StyleLibrary without a board (Alex confirms in one phrase). Checkpoints A+B merged (style frame + first minute); C = smoke, moderator, minimal promo (cover + 1 preview). Growth only for the game with the best funnel.

## Testing (before saying «готово»)
`tsc --noEmit`, build, dev server, budget (`threejs-debug-profiler` in Three.js), real browser (Playwright via `webapp-testing` or the built-in browser): no console errors, controls, logic, collisions/physics, camera, UI, frame time, budget. Visual claims need screenshots against the reference. Report only what actually ran.

## Working style
- Dependencies per project (npm), never global. Add a library only when it pays for itself.
- No refactors for beauty. Small runnable iterations.
- Publishing, uploading files to external services, deleting user files — ask first.
