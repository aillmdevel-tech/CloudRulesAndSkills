---
name: levelcopier-asset-pipeline
description: Use when the user provides output of their LevelCopier tool or other scene/asset dumps to rebuild a level ("LevelCopier", "импорт уровня", "вот GLB и JSON", "восстанови сцену", "вот скан локации", folders of models + textures + scene JSON). Inventories the real files and JSON schema, maps models/materials/textures, checks scale/axes/rotation/pivots and broken references, rebuilds the hierarchy, plans colliders and gameplay objects, writes ASSET_MANIFEST.md, and builds an importer for the project's engine (PlayCanvas or Three.js) on derived copies only.
---

# LevelCopier / scene asset pipeline

LevelCopier is Alex's own tool. Its output format is **not known in advance** — learn it from the real
files, its code or its docs every time. Never assume field names, units or axis conventions.

## Hard rules

- Originals are read-only. Work in `imports/levelcopier/<dump-name>/` as delivered and write derived
  files to `public/assets/...` or `imports/levelcopier/<dump-name>/_derived/`.
- If the LevelCopier tool or its output is not on this machine, ask Alex where it is. Do not search
  the internet for a tool by that name and do not download anything to "get" it.
- Before trusting a convention (units, up-axis, handedness, rotation order, quaternion layout,
  pivot), verify it on 2–3 known objects by rendering them, not by reading field names.
- Respect asset ownership: dumps of someone else's game are for analysis/prototyping; flag anything
  that would need rights before publishing.

## Tooling (bundled)

`python3 ~/.claude/skills/levelcopier-asset-pipeline/scripts/scan_assets.py DIR [--json out.json]`
— stdlib only. Lists files by type and size, parses every `.gltf`/`.glb` header (nodes, meshes,
materials, textures, animations, skins, extensions, external URIs and whether they exist), samples the
structure of every `.json` (keys, types, array lengths, numeric ranges of position/rotation/scale-like
fields), and reports missing references and unusually large files.

For deeper GLB work in PlayCanvas projects use the official skills: `inspect-glb` (bounds, grounding,
clips, joints), `load-assets` (Draco/KTX2/preload), `calibrate-model` (scale/grounding/pivot/yaw once
per asset), `assemble-scene` (hierarchy, colliders, rigid bodies), `configure-animation`.
In Three.js projects use GLTFLoader + Box3 checks in a debug page instead.

Conversion of FBX/OBJ/DAE → GLB (into `_derived/`, never over originals) with headless Blender, if
`blender` is on PATH:
`blender -b --factory-startup --python-expr "import bpy; bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath='IN.fbx'); bpy.ops.export_scene.gltf(filepath='OUT.glb')"`
(use `bpy.ops.wm.obj_import` / `wm.collada_import` for other formats). Re-check scale/axes after conversion.

## Procedure

1. **Locate & inventory**: run `scan_assets.py`. Read any README / code of LevelCopier present.
2. **Infer the schema**: from the JSON samples describe each record type (object, prefab, light,
   spawn, trigger, UI, audio...). Write it down with real example values.
3. **Map assets**: object → model file → materials → textures; detect duplicates and instancing
   candidates; list missing/broken references and unsupported formats (FBX, DDS, proprietary).
4. **Calibrate transforms**: pick reference objects (floor, door, character), place them, compare
   with screenshots of the original. Fix one global conversion (axis swap, unit scale, handedness)
   rather than per-object hacks. Record the conversion in `docs/ASSET_MANIFEST.md`.
5. **Rebuild the hierarchy** in the engine; keep the original IDs/names on entities for debugging.
6. **Colliders & gameplay**: static mesh vs primitive colliders (prefer primitives/simplified), spawn
   points, triggers, interactables — from data if present, otherwise propose and confirm.
7. **Audio/UI/other**: catalogue, convert only what the agreed scope needs.
8. **Verify visually**: render the rebuilt scene from the same viewpoints as reference screenshots;
   use `game-visual-comparison`. A clean console is not proof the scene is right.
9. **Importer**: if the dump will be re-imported, write a deterministic script (`tools/import-*.ts`
   or `.py`) that regenerates derived files from the originals.

## ASSET_MANIFEST.md (template: `~/.claude/skills/game-project-workflow/templates/docs/ASSET_MANIFEST.md`)

Source dump + date, schema summary, coordinate conversion, per-asset table (file, type, size,
triangles/materials if known, used-by, status: ok / converted / missing / placeholder), known issues,
licensing notes. Mark every placeholder explicitly.
