# Blender rules (Blender MCP)

Start: `get_addon_status` → `get_scene_info`. Everything scripted via `execute_blender_code`; verify with `look` (small `max_size`, several angles).

## Scene
- Units: metres, +Y up on export; character ≈ 1.8 m (or the reference's own ratio from `ART_SPEC.md`). Set scale before modelling.
- Collections: `Map`, `Kit` (modules), `Props`, `Colliders`, `Lights`, `Camera_Ref`. One object per role, clear names (`Wall_A`, `Tree_01`).
- Blockout first (cubes/planes) with the reference camera; approve proportions, then detail.
- Modular kit: reuse via linked duplicates; snap to grid (1 m / 0.5 m). Apply scale/rotation before export; pivots at bottom-centre for props.
- Colliders: simple boxes named `COL_*` in `Colliders`, exported separately or tagged.

## Materials / look
- Match `ART_SPEC.md`: flat/toon → few Principled materials with solid colours; keep ≤ ~15 materials per scene; atlas or vertex colours for small props.
- Look up nodes by type (`n.type == "BSDF_PRINCIPLED"`), never by name. Colours on node inputs, not `diffuse_color`.
- Read enum values from `bl_rna`, don't hardcode; engine assignment in `try/except TypeError`.
- Bake lighting only if the engine needs it; otherwise light in-engine.

## Budget (web)
- Map ≤ ~150k tris, single props ≤ ~2k, hero ≤ ~10k (tune per game); textures ≤ 1024 (2048 for hero/atlas), KTX2/WebP if the stack supports.
- Merge static meshes per material in the final export, keep dynamic/interactive objects separate.

## Imports
- `search_assets` → `import_asset` (Poly Haven, Sketchfab, Poly Pizza): check licence, size to `world_bounding_box`, put on ground, restyle to match the palette.
- `generate_3d`: one object only, may cost a credit — ask Alex first.
- Characters: use `character-animation` skill (rig, Mixamo, face decals).

## Export
- GLB (`export_scene.gltf`, `export_format='GLB'`, apply modifiers, +Y up, Draco only if the loader is set up). One GLB for the map, separate GLBs for interactive props/characters.
- Re-import test or engine load; record in `docs/ASSET_MANIFEST.md`. Save the `.blend` in `assets/source/`.
