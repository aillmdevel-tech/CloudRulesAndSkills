#!/usr/bin/env bash
# Third-party skills, installed globally for Claude Code with the official `npx skills` CLI (copy mode).
# Reviewed 2026-11-04 (SKILL.md + scripts). Details/why: ../GameFactory/THIRD_PARTY_SKILLS.md
set -uo pipefail
export DO_NOT_TRACK=1 DISABLE_TELEMETRY=1
SK="npx -y skills@latest add"
$SK playcanvas/skills -g -a claude-code --copy -y
$SK anthropics/skills --skill frontend-design --skill webapp-testing -g -a claude-code --copy -y
$SK mattpocock/skills --skill grilling -g -a claude-code --copy -y
$SK daymade/claude-code-skills --skill frontend-visual-qa -g -a claude-code --copy -y
# PlayCanvas skills are parked in ~/.claude/spares by install.sh (playcanvas-skills on|off).
# threejs-debug-profiler / threejs-aaa-graphics-builder are adapted copies in claude/skills (not from npx).
