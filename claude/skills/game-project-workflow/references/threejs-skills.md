# Three.js skills

Source: https://github.com/majidmanzarpour/threejs-game-skills (commit 8286774, MIT), reviewed 2026-11-20.

**Installed globally (adapted copies, synced as own skills):**

| Skill | When |
|---|---|
| `threejs-debug-profiler` | blank canvas, loading/animation/input bugs; lags, draw calls, memory, bundle size; budget check in the package loop |
| `threejs-aaa-graphics-builder` | after checkpoint A: materials, light, post, shaders, VFX, LOD/instancing, visual scorecard; checkpoint C polish |

Adaptation: paid generators and the credential probe removed; hero models come from Blender (`game-art-first`); style from `docs/ART_SPEC.md`. When updating from upstream, re-apply the GameFactory override note at the top of `threejs-aaa-graphics-builder/SKILL.md`.

**Not installed:** `threejs-game-director`, `threejs-gameplay-systems`, `threejs-game-ui-designer`, `threejs-qa-release` (overlap with game-project-workflow, game-ui-motion-sound, game-autotest), `threejs-3d-generator` / `threejs-image-generator` / `threejs-audio-generator` (paid APIs; only on Alex's explicit request).

Never use threejs-* skills in a PlayCanvas project.
