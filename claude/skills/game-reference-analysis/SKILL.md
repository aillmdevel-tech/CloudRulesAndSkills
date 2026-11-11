---
name: game-reference-analysis
description: Use when the user gives gameplay video, a video link, screenshots, or a description of an existing game to study or recreate ("вот видео игры", "разбери референс", "посмотри геймплей", "проанализируй скриншоты", "повтори механику", "составь раскадровку"). Extracts frames with timecodes via FFmpeg, builds contact sheets, and breaks down the core loop, controls, camera/FOV, movement and animation, UI, art style and object behaviour, separating observed facts from guesses. Produces REFERENCE_ANALYSIS.md, VIDEO_STORYBOARD.md, GAMEPLAY_BREAKDOWN.md, ART_REFERENCE.md.
---

# Game reference analysis

Goal: turn raw reference material (video, screenshots, voice-dictated notes) into documents a developer
can build from, without inventing anything that was not actually seen.

## Ground rules

- Only claim to have watched what you actually extracted and looked at. If a link cannot be opened or
  downloaded, say so and ask for the file. Never describe a video from its title or thumbnail.
- Every statement in the output is tagged: **[факт]** (seen in frame/timecode), **[вывод]** (reasoned
  from several observations), **[гипотеза]** (needs confirmation). Give the timecode for facts.
- Do not upload the user's files to third-party services. yt-dlp may download a public link the user
  gave; nothing is sent anywhere.
- Work on copies in the project (`references/` or a scratch dir); never modify the originals.
- Keep it proportional: a single screenshot gets a short analysis, not four documents.

## Tooling (bundled)

`scripts/video_frames.py` — needs `ffmpeg`/`ffprobe` on PATH, Pillow optional (labels on sheets).
Run with `python3 ~/.claude/skills/game-reference-analysis/scripts/video_frames.py <cmd> ...`:

| Command | What it does |
|---|---|
| `info VIDEO` | duration, fps, resolution, codec, audio — check this first |
| `sample VIDEO OUTDIR --every 2 [--start S --end S --width 960]` | uniform frames, file names carry the timecode |
| `scenes VIDEO OUTDIR [--threshold 0.3 --width 960]` | frames at cuts / big visual changes, with timecodes |
| `burst VIDEO OUTDIR --start S --end S [--fps 15]` | dense frames of a short moment (animation, jump, camera move) |
| `sheet FRAMEDIR OUT.jpg [--cols 4 --thumb 480]` | contact sheet with timecode labels |

Links: `yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" -o "references/videos/%(title).80s.%(ext)s" URL`
(only for links the user supplied; respect the site's terms).

## Procedure

1. **Inventory** what was given: files, durations, resolutions, notes. `info` every video.
2. **Overview pass**: `scenes` (or `sample --every 5` for long videos) → `sheet` → look at the sheets.
   Build the storyboard: timecode → what happens → screen/state.
3. **Targeted passes** with `burst` on the moments that matter for the task: locomotion cycle, jump,
   attack, camera turn, UI transitions, spawn/death, level transitions. Look at individual frames
   when a detail matters (pose, foot contact, HUD numbers).
4. **Analyse** (only what the material supports):
   - Core loop: goal → action → reward → progression; session length; fail/win states.
   - Controls: inferred inputs (WASD/mouse/touch/gamepad), on-screen prompts, button hints.
   - Camera: 1st/3rd person, follow distance/height, pitch range, lag/smoothing, collision with walls,
     approximate FOV (estimate from known-size objects / horizon; mark as гипотеза).
   - Movement: speed in body-lengths/s (count frames), acceleration, air control, jump height,
     turning, slopes, how feet/limbs behave (procedural vs clip animation; IK signs: feet adapt to
     terrain, legs step independently, body tilts with surface).
   - Animation: states and transitions, blend smoothness, root motion vs in-place.
   - Objects/enemies/NPC: behaviour patterns, timings, spawn rules.
   - UI/HUD: layout per screen, fonts style, colours (sample hex from frames), animations.
   - Art: palette, lighting (sun direction, ambient, fog, bloom), materials (flat/toon/PBR), scale.
   - Possible procedural systems (terrain, spawning, IK, physics) — always гипотеза until confirmed.
5. **Questions**: list only open points that change implementation (max ~5), each with your
   recommended answer.

## Output (write into the project's `docs/`, create only what the material justifies)

- `REFERENCE_ANALYSIS.md` — summary: what was analysed, key findings, open questions, confidence.
- `VIDEO_STORYBOARD.md` — table: timecode | frame file | event | notes. Link the contact sheets.
- `GAMEPLAY_BREAKDOWN.md` — loop, controls, camera, movement numbers, states, rules, edge cases.
- `ART_REFERENCE.md` — palette (hex), lighting, materials, UI style, reference frame list.

### Обязательно для ТЗ на игру / видео-референса целиком: подробная спецификация по папкам

After studying a spec or a gameplay video of a whole game (not a single screenshot), ALSO break every
aspect into a detailed reference spec under `docs/spec/`, so later work rarely needs the video again:

```
docs/spec/README.md   — index: every file, what it covers, source material + date
docs/spec/mechanics/  — core loop, controls, economy/formulas, progression, rules, states, edge cases
docs/spec/visual/     — palette (hex), lighting, fog/sky per zone, materials/shaders, outline, models, scale
docs/spec/ui/         — every screen/panel/HUD: layout, sizes, fonts, colours, texts, states
docs/spec/vfx/        — every effect: trigger, look, duration, colours, particles
docs/spec/animation/  — character/creature/UI animations: poses, timings, easing
docs/spec/camera/     — modes, FOV, distances, moves, shake, letterbox, transitions
docs/spec/audio/      — sound/music cues with timings (if audible)
docs/spec/timings.md  — one table of all key timings (ms) with timecodes
```

One file per topic/screen/effect (e.g. `vfx/landing_impact.md`, `ui/shop_panel.md`). Each file: what it
is, exact numbers (sizes, ms, hex, counts), timecodes + frame paths, [факт]/[вывод]/[гипотеза] tags,
"Implementation notes". Very detailed: it is the source of truth for building and visual comparison.
Update it when new reference material arrives.

Templates: `~/.claude/skills/game-project-workflow/templates/docs/`. Keep extracted frames under
`references/frames/<video-name>/` (git-ignore large media if the project uses git).

## Hand-off

After the analysis, continue with `game-project-workflow` (questions → plan → agreement). For visual
matching later, the selected reference frames become inputs to `game-visual-comparison`.
