---
name: game-art-first
description: Use after the materials of a new or big-stage game project are studied and the plan is agreed, or whenever a game needs its look made before logic — "начинаем с визуала", "собери локацию/карту/модели в Blender", "подбери референсы и ассеты", "адаптируй Roblox-референс для веба", "стиль игры", "как видоизменить референс", "найди готовые ассеты/GitHub/игры для референса". Art-first stage: main Roblox/original reference → Steam style board approved by Alex → found references and free assets → style board → map/location/objects built in Blender (Blender MCP) → GLB export → screenshot comparison → Alex approves the look = MVP checkpoint A. Then game feel (checkpoint B).
---

# Game art-first (GameFactory)

Visual stage that always comes BEFORE gameplay logic. Output: checkpoint A of the MVP (`game-project-workflow` §7) — the starting zone in the approved style in Blender + exported GLB + an engine screenshot beside the Steam reference. Coordinates other skills; does not replace them.

## Rules
- Main reference = the game/video/screenshots Alex gave (usually Roblox). It gets the biggest weight. Default = maximum closeness to the reference in composition, proportions, palette, lighting, camera and effects (own models/assets, no ripped files, no copying others' files). Do NOT simplify or drift to a looser style unless Alex picks it in step 2.
- The lead does map, location, models, style and camera itself; delegation rules: [references/delegation.md](references/delegation.md). Model and effort are Alex's choice.
- Facts vs guesses: mark every gap in the reference as a hypothesis in `docs/ART_SPEC.md`.
- Owner files (LevelCopier dumps, provided GLB) stay untouched; work on derived copies.
- Licences: CC0 preferred; CC-BY only with credit in `docs/CREDITS.md`; no ripped/commercial assets unless Alex supplies them.

## 0. Alex's style library (always first)
Read `GameFactory/StyleLibrary/README.md`, `TASTE.md` and the genre template closest to the spec (`genres/*.md`, game cards in `games/*/CARD.md`). Priority: **Alex's explicit words about graphics in the spec > genre template > TASTE.md defaults**. Then find 3–6 Steam games that fit THIS spec visually (tags, "More like this"), and send Alex a board (link, 1–2 screenshots, why it fits, what we take) for approval before the style board. Link the chosen cards from `docs/ART_SPEC.md`. When Alex sends new liked games → add them to the library (README "Как добавлять").

## 1. Reference intake (script first, short summary to chat)
1. Video → `game-reference-analysis` (`video_frames.py`), screenshots → same skill. Output goes to `docs/spec/{visual,ui,camera,...}` + `ART_REFERENCE.md`.
2. Original game named by Alex: research it on the web (store page, wiki, gameplay), record in `docs/REFERENCE_ANALYSIS.md`: core look, palette, proportions, UI structure, camera.
3. Extract numbers where possible: character height vs props/doors, camera FOV/angle, palette (5–8 hex), outline/shading style, UI layout grid.

## 2. Adaptation = the approved Steam game
The Steam board from §0 is the set of adaptation options: gameplay, elements, VFX and character follow the Roblox original; the look follows the one Steam game Alex approves. Record the pick in `docs/DECISIONS.md`.

### Quality bar (mandatory, not optional)
- Effects checklist per scene: post-processing (bloom, AO/N8AO, tone mapping, vignette as in reference), particles (three.quarks), soft shadows and lighting matching the reference, UI animations (game-ui-motion-sound), material detail (not flat defaults).
- After EVERY batch of visual changes: capture reference vs game pairs (`game-visual-comparison`) and fix top differences until close; record verdict in `PROJECT_STATE.md`.
- Missing effect = listed as a gap, not silently skipped.

## 3. Search for ready things (`game-project-workflow` §5: after style approval, before the plan; one pass, results in `docs/REFERENCES.md`)
Follow [references/asset-sources.md](references/asset-sources.md): open asset packs, GitHub projects/tools, web/Steam games as visual benchmarks. For each: link, licence, what to take, fit 1–5. Max ~10 entries; no filler. Download only after Alex's OK (name, source, size).

## 4. Style board
`docs/ART_SPEC.md`: palette, materials (flat/toon/PBR), lighting (sun angle, ambient, fog, AO), outline/post-fx, proportions & unit scale (1 unit = 1 m), camera, UI style link to `game-ui-motion-sound`. If the stack is Three.js — keep within `GameFactory/THREEJS_STACK.md`.

## 5. Build in Blender (Blender MCP, only now)
Follow [references/blender-rules.md](references/blender-rules.md). Order: blockout of the map (scale + camera check) → key landmarks → modular kit → props → materials/lighting → export. Use `look` after each block, small `max_size`; compare with the reference side by side.
Enable the Blender MCP only for this phase; turn it off after if you enabled it (see `~/.claude/CLAUDE.md`).

## 6. Export + engine check
GLB to `assets/models/`, list in `docs/ASSET_MANIFEST.md` (source, licence, tris, scale, pivots). Load in the engine, capture with the matching camera, run `game-visual-comparison`. Fix the top differences, re-capture.

## 7. Checkpoint A
Show Alex: Steam reference vs Blender render vs engine screenshot, style summary, what is placeholder. Record his verdict in `PROJECT_STATE.md`. Then checkpoint B (game feel) of `game-project-workflow` §7.
