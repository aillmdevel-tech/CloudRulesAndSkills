#!/usr/bin/env bash
# Restore GameFactory on a new machine (macOS/Linux). Run from the copied GameFactory folder.
# usage: restore.sh [--games-dir DIR]
#   --games-dir  where game projects live (default: parent folder of this GameFactory's parent)
# Steps: ~/.claude/CLAUDE.md (old one backed up), own skills, third-party skills, grill-me patch,
#        Python Playwright + Chromium. Never touches secrets.
set -euo pipefail
GF="$(cd "$(dirname "$0")/.." && pwd)"
B="$GF/backup"
GAMES="$(cd "$GF/../.." && pwd)"
while [ $# -gt 0 ]; do
  case "$1" in --games-dir) GAMES="$2"; shift 2 ;; *) echo "unknown arg $1"; exit 1 ;; esac
done
[ -d "$B/claude" ] || { echo "no backup in $B — run scripts/backup.sh on the old machine first"; exit 1; }
for t in node npx git python3; do command -v $t >/dev/null || { echo "missing: $t (install it first, see SETUP_NEW_PC.md)"; exit 1; }; done

mkdir -p "$HOME/.claude/skills"
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
  cp "$HOME/.claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md.bak.$(date +%Y%m%d%H%M%S)"
  echo "existing ~/.claude/CLAUDE.md backed up"
fi
OLD_GF="$(sed -n 's/^- GameFactory[^`]*`\(.*\)`.*/\1/p' "$B/claude/CLAUDE.md" | head -1)"
OLD_GAMES="$(sed -n 's/^- Папка игр: `\(.*\)`.*/\1/p' "$B/claude/CLAUDE.md" | head -1)"
sed -e "s|$OLD_GF|$GF|g" -e "s|\`$OLD_GAMES\`|\`$GAMES\`|g" "$B/claude/CLAUDE.md" > "$HOME/.claude/CLAUDE.md"
echo "CLAUDE.md installed (GameFactory=$GF, games=$GAMES)"

export DO_NOT_TRACK=1 DISABLE_TELEMETRY=1
SK="npx -y skills@latest"
$SK add playcanvas/skills -g -a claude-code --copy -y
$SK add anthropics/skills --skill frontend-design --skill webapp-testing -g -a claude-code --copy -y
$SK add mattpocock/skills --skill grill-me --skill grilling -g -a claude-code --copy -y
$SK add daymade/claude-code-skills --skill frontend-visual-qa -g -a claude-code --copy -y

for s in "$B"/claude/skills/*; do
  n="$(basename "$s")"
  rm -rf "$HOME/.claude/skills/$n"
  cp -R "$s" "$HOME/.claude/skills/$n"
  echo "skill installed: $n"
done
# own skills may contain the old GameFactory path (e.g. game-ui-motion-sound -> UIFX)
if [ -n "$OLD_GF" ] && [ "$OLD_GF" != "$GF" ]; then
  grep -rlF "$OLD_GF" "$HOME/.claude/skills" 2>/dev/null | while read -r f; do
    OLD="$OLD_GF" NEW="$GF" perl -pi -e 's/\Q$ENV{OLD}\E/$ENV{NEW}/g' "$f"
  done
fi
chmod +x "$HOME"/.claude/skills/*/scripts/* 2>/dev/null || true
ln -sfn "$HOME/.claude/skills/game-project-workflow/templates" "$GF/templates"

# UIFX demo dependencies (local to the UIFX folder, not global)
[ -f "$GF/UIFX/package.json" ] && (cd "$GF/UIFX" && npm install --no-fund --no-audit >/dev/null && echo "UIFX deps installed") || true

python3 -m pip install --user -q playwright && python3 -m playwright install chromium || \
  echo "WARN: Python Playwright install failed — webapp-testing/capture.py need it"
python3 -c "import PIL" 2>/dev/null || python3 -m pip install --user -q Pillow || true

echo; echo "check:"; ls "$HOME/.claude/skills"
for t in ffmpeg ffprobe yt-dlp blender; do printf "%-8s %s\n" "$t" "$(command -v $t || echo 'not found')"; done
echo "Done. Open a NEW Claude Code session and follow 'Проверка' in SETUP_NEW_PC.md."
