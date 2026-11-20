---
name: threejs-aaa-graphics-builder
description: "Three.js render-quality and performance pass for a game whose look is already set: material library, lighting, tone mapping, shadows, fog, post-processing, shaders, VFX, LOD/instancing, render budgets, 10-category visual scorecard. Use in a Three.js project when screenshots look basic, flat or cheap against the approved Steam reference, or for checkpoint C polish. Style comes from docs/ART_SPEC.md; models come from Blender (game-art-first)."
---

# Three.js AAA Graphics Builder

> **GameFactory rules override this skill.** Style = approved Steam game in `docs/ART_SPEC.md`; scope = ТЗ + Alex's answers. Hero models, characters and locations come from Blender / provided assets (`game-art-first`, `character-animation`), not from generators. Paid generators (`threejs-3d-generator`, `threejs-image-generator`) and the credential probe are **not installed and not used** unless Alex asks. Procedural Three.js only for repeated props, kits, collision proxies, VFX geometry and instancing. Visual comparison goes through `game-visual-comparison`.

Own the production graphics pass: turn basic screenshots into authored, high-density, performance-aware visuals.

## References

| File | Read it when |
| --- | --- |
| `references/visual-scorecard.md` | scoring visuals or making any premium/AAA/showcase claim |
| `references/authoring-recipes.md` | building hero, obstacle, reward, world-kit, or prop models; changing lighting, tone mapping, shadows, fog, post, or graphics architecture |
| `references/technical-art.md` | render budgets, material kits, VFX systems, instancing/LOD, imported asset cleanup, anything that could affect browser performance |
| `references/shader-cookbook.md` | custom shaders, `onBeforeCompile`, skies, or post-processing; use recipes as tested starting points and verify them against the project's Three.js version |

For a broad "still looks basic" or premium pass, read all four before implementing. A narrow graphics edit loads only its relevant references and checks; the requested style and scope override recipe defaults.

## Core rule

Glow does not make primitives look AAA. Build authored forms first, then materials, then lighting, then effects — in that order.

## Workflow

1. Capture or inspect active-play screenshots on the target viewports when a playable scene exists.
2. For an existing game, score the affected views and pick the weakest surfaces. For a new game, establish art direction, camera scale, material roles, and the hero target first; do not invent a before screenshot.
3. Add the graphics architecture the game is missing: material library, procedural textures and decals, model factories, world prop kit, VFX system, render pipeline, diagnostics.
4. Choose a source per high-value surface: Blender model / provided asset (hero surfaces), procedural Three.js (repeated props, VFX geometry), procedural textures and decals.
   Inspect the concept/model before dependent generation or rigging. Finish one representative playable scene with actual assets and feedback before expanding the content kit.
5. Upgrade every weak visible surface, not only the hero: hazards, rewards, ground and track, foreground props, background layers, telegraphs, material variation, state VFX.
6. Add lighting, tone mapping, and render polish once authored forms exist.
7. Add event-driven VFX tied to gameplay state.
8. Re-score against the calibration anchors, citing the inspector's measured metrics. Keep going until every premium category is at least 2, or name the exact blocker.

## Asset sourcing

Hero surfaces (player, characters, vehicles, buildings, signature props, hero environment) come from Blender or Alex's provided assets via `game-art-first`. Free CC0 libraries (Poly Haven, Poly Pizza, Kenney, Quaternius) through Blender MCP are allowed when they fit the approved style. No external generation without Alex's explicit OK.

For animated assets inspect motion as well as silhouettes: locomotion, blend transitions, foot contacts, hit timing, and secondary motion in real gameplay. A focused independent critique may identify defects after a substantial pass; the lead remains responsible for the final score and integration.

## Report

Score before and after with one line of evidence per category, the surfaces you upgraded, files changed, screenshots, renderer diagnostics against the budget table, and what is still weak. Include imported-asset diagnostics (scale, bounds, collision proxy, clips) when imported 3D was used.
