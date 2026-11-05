---
name: game-visual-comparison
description: Use when a game's rendered look must match a reference screenshot or video frame, or when graphics look wrong ("сделай похоже на скриншот", "сравни с референсом", "почему графика не такая?", "повтори композицию", "проверь визуал", UI/HUD should match a screenshot). Captures the running game from a matching camera with Playwright, builds side-by-side and diff images plus colour/brightness stats, lists differences in composition, proportions, FOV, lighting, materials, colours and UI by priority, fixes the top ones and re-captures to confirm.
---

# Game visual comparison

Never say the scene matches the reference without having looked at a fresh capture next to it.

## Tooling (bundled)

- `python3 ~/.claude/skills/game-visual-comparison/scripts/capture.py URL OUT.png [--size 1280x720]
  [--wait-ms 1500] [--eval "JS"] [--selector canvas] [--console OUT.log]`
  Opens the local game in headless Chromium (Python Playwright, WebGL works), optionally runs JS
  first (e.g. `window.__game.setCamera(...)`, pause, seed), waits, saves a screenshot and the
  console log; exits non-zero on page errors.
- `python3 ~/.claude/skills/game-visual-comparison/scripts/compare_images.py REF.png SHOT.png OUTDIR
  [--crop x,y,w,h]` — normalises size, writes `side_by_side.png`, `diff.png` (amplified),
  `blend.png` (50/50 overlay for alignment) and prints mean colour, brightness, contrast, saturation,
  per-quadrant brightness and dominant colours for both. Pillow only.
- Interactive looking: the built-in browser pane or `webapp-testing` for multi-step navigation;
  `frontend-visual-qa` for DOM UI layout/typography/responsive defects.

## Procedure

1. **Reference**: identify exactly which frame/screenshot and which game state it shows
   (location, time of day, UI screen). Note its resolution and aspect ratio.
2. **Match the shot**: put the game in the same state and camera — add/use the dev debug API
   (`window.__game`) for camera position/target/FOV, pause, fixed seed, hidden debug UI. Same aspect.
3. **Capture** with `capture.py` (or the browser pane), then **compare** with `compare_images.py`.
   Look at the images themselves, not only the numbers.
4. **List differences by impact** (biggest first), each with evidence:
   composition & framing → FOV/camera height/pitch → proportions & scale → lighting (direction,
   intensity, ambient, shadows, fog, tone mapping/exposure) → materials (roughness/metalness,
   flat vs PBR, textures) → colour/palette/saturation → geometry detail → UI layout/fonts/sizes →
   effects/post.
5. **Fix the top 1–3**, re-capture from the same state, compare again. Repeat while there are
   high-impact gaps; stop and report remaining ones honestly.
6. PlayCanvas: lighting via `light-scene`, effects via `add-effects`, deterministic captures via
   `verify-pixels`. Keep a `tests/visual/` baseline only once Alex approves a look.

## Report format

| # | Отличие | Референс | Сейчас | Причина (гипотеза) | Статус |
Then the before/after image paths. Mention anything that could not be matched (missing assets,
unknown shader) and placeholders still in frame.
