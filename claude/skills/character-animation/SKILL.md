---
name: character-animation
description: Use when a game character needs a rig or animations, or when Alex's Hero character is used in a game ("сделай анимации", "заанимируй персонажа", "риг", "ходьба/бег/прыжок/танец", "Mixamo", "ретаргет", "добавь анимацию герою", "подключи героя в игру", "смени лицо персонажу"). Blocky/Tripo characters: normalise mesh, Mixamo-named skeleton with block weights, IK-legs cartoon keying, Mixamo mocap retarget with a cartoon pass, swappable face decals, GLB export + Three.js module.
---

# Character animation pipeline (Blender MCP + Three.js)

Reference implementation: `/Users/mac/Downloads/WebAIGames/Characters/Hero` (read its
`docs/PROJECT_STATE.md` first). Scripts in `scripts/` are reusable for any blocky humanoid.

## Ready asset: Hero
- `export/hero.glb` — skeleton (Mixamo names, no prefix), clips, 5 face decals. `export/hero.js` —
  `loadHero()`, `play(name,{fade,timeScale})`, `playOnce(name, then)`, `setFace(name)`, `addFace(name,png)`.
- In a game: copy `hero.glb` + `hero.js`, move the root by `meta.clips[clip].speed_mps` for Walk/Run
  (clips are in place). One-shots (Jump, FrontFlip) via `playOnce`.
- New face: 1024² transparent PNG framed like `faces/face_*.png` → `hero.addFace()` at runtime, or add to
  `faces/faces.json` and re-run `scripts/faces_hero.py` + export.

## Pipeline for a new character
1. Source mesh is read-only. Heavy Tripo/AI mesh: `gltf-transform copy` (decodes meshopt) →
   `gltf-transform simplify --ratio … --error 0.002` to ~20–40k tris. Import in Blender; glTF import uses
   quaternion rotation_mode — switch to XYZ before rotating. Normalise: −Y forward, ~1.8 m, feet z=0.
2. Joints: ortho front/side renders + grid overlay → read joint positions. Put them in `rig_hero.py` (`J`).
3. Weights: `rig_hero.py` segment weights (rigid blocks + soft band at joints). Bone heat smears blocky
   shoulders — avoid. Check a stress pose from front/back for webbing and spikes.
4. Faces baked into the texture: do not repaint the texture (Tripo also embosses them in geometry and the
   normal map). Flatten the head-front verts, add a skin-coloured face plate + decals (`faces_hero.py`).
5. Animation: `anim_lib.py` (IK legs, track builder, foot roll pivot, overlap delays, squash) +
   `anims_keyed.py` for cartoon cycles; `retarget_mixamo.py` for mocap (Mixamo FBX, 30 fps, Without Skin,
   In Place) with smoothing, exaggeration (upper body only) and follow-through.
6. Check: IK miss per clip (`foot vs IK target` ≤ 1 cm), frames from side/front, loop seam, no floor
   penetration. Export with `export_hero.py` (strips IK bones/ctrl actions, NLA per clip, 2048 WebP).
7. Preview: `export/viewer.html` (three 0.187 from jsDelivr) served over http — the app's preview server
   cannot read ~/Downloads (macOS privacy), copy the viewer to the session folder to serve it.

## Blender gotchas (learned)
- Drivers on `hide_viewport/hide_render` stop updating (hidden object leaves the depsgraph). Scripted
  driver expressions need Python auto-run → use AVERAGE driver + stepped F-curve. Wire drivers last.
- After `driver`/prop changes, force re-eval with `frame_set(f+1); frame_set(f)`.
- Newly created objects have stale `matrix_world` until `view_layer.update()`.
- Cycles on the M1 is ~50 s/frame for previews: use EEVEE Next.

## Game controller (Roblox-style) — reference: `Hero/demo`
Rapier KCC + Roblox camera (orbit/zoom/1st person/shift lock/wall collision) + animator (speed-synced blend,
jump/fall/land subclips, emote wheel). Gotchas: KCC can't climb a box step at the capsule's foot -> put an invisible
wedge (convex hull) under stairs through the step edges; build ramps as wedges, not rotated boxes (lip at the bottom);
don't overwrite velocity with the projected displacement (slopes slow to a crawl) — only when blocked.
Hidden Browser pane pauses rAF: expose a deterministic `advance(seconds)` for checks.
Mixamo FBX import: armature faces +X and Metallic=1 — rotate to -Y and zero metallic before export.

## Mixamo
Free, needs Alex's Adobe login in the built-in browser. Download only after Alex confirms the file list.
Search names that work: "Front Flip", "Push Up", "Pull Up", "Hip Hop Dancing", "Silly Dancing".
