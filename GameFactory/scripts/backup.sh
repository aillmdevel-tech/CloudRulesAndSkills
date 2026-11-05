#!/usr/bin/env bash
# Snapshot the GameFactory configuration into GameFactory/backup/ (no secrets).
# Copies: ~/.claude/CLAUDE.md, the 4 GameFactory skills, the patched grill-me, the skills lock file.
# Third-party skills are NOT copied — restore.sh reinstalls them from their official repos.
set -euo pipefail
GF="$(cd "$(dirname "$0")/.." && pwd)"
B="$GF/backup"
OWN="game-reference-analysis levelcopier-asset-pipeline game-project-workflow game-visual-comparison game-ui-motion-sound chat-handoff github-account-router"

rm -rf "$B"
mkdir -p "$B/claude/skills"
cp "$HOME/.claude/CLAUDE.md" "$B/claude/CLAUDE.md"
for s in $OWN grill-me; do
  cp -R "$HOME/.claude/skills/$s" "$B/claude/skills/$s"
done
[ -f "$HOME/.agents/.skill-lock.json" ] && cp "$HOME/.agents/.skill-lock.json" "$B/skill-lock.json"

# secret guard: refuse to keep anything that looks like a credential
if grep -rIlE "(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9]{16,})" "$B"; then
  echo "possible secret found in backup — removed backup, check the files above"; rm -rf "$B"; exit 1
fi
date "+%Y-%m-%d %H:%M" > "$B/BACKUP_DATE.txt"
echo "backup -> $B"
find "$B" -maxdepth 3 | sed "s|$GF/||" | sort
