# Three.js skills (conditional install)

Source reviewed 2026-11-04: https://github.com/majidmanzarpour/threejs-game-skills (commit 8286774).
**Not installed globally.** Install only when a real Three.js project starts, and only the relevant ones.

| Skill | Use | External services |
|---|---|---|
| threejs-gameplay-systems | scaffold, loop, input, camera, collision, game feel | none (ships a Vite+TS template) |
| threejs-debug-profiler | blank canvas, loading bugs, draw calls, memory | none |
| threejs-qa-release | playtests, visual regression, canvas pixel inspection, builds | none |
| threejs-aaa-graphics-builder | lighting, materials, post, LOD/instancing | none |
| threejs-game-ui-designer | HUD/menus | none |
| threejs-game-director | router over the sibling skills | `probe_asset_credentials.sh` looks for API keys — skip unless generators are used |
| threejs-3d-generator | Tripo API text/image→3D | paid API, uploads prompts/images |
| threejs-image-generator | Gemini image API | paid API, uploads prompts/images |
| threejs-audio-generator | ElevenLabs audio | paid API |

Default subset when a Three.js project starts (after re-checking the repo is still maintained and
reading the SKILL.md + scripts of each):

```bash
DO_NOT_TRACK=1 npx -y skills add majidmanzarpour/threejs-game-skills \
  --skill threejs-gameplay-systems --skill threejs-debug-profiler --skill threejs-qa-release \
  --skill threejs-aaa-graphics-builder -a claude-code --copy -y
```

Prefer project scope (no `-g`, run inside the project) so they never trigger in PlayCanvas projects.
Generator skills only with Alex's explicit OK (they send data to paid third-party APIs and need keys).
Never use threejs-* skills in a PlayCanvas project.
