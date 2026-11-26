#!/usr/bin/env bash
# Copy the CURRENT local Claude setup into this repo (run on the machine where rules/skills were changed).
#   scripts/sync.sh            # copy + secret scan + show diff summary
#   scripts/sync.sh --commit "message"   # also commit (push stays manual: git push)
# What is copied:
#   ~/.claude/CLAUDE.md, ~/.claude/settings.json, ~/.claude/hooks/
#   own skills = every ~/.claude/skills/* NOT installed by `npx skills` (lock file)
#   GameFactory folder (path from CLAUDE.md), without node_modules/backup/build output
#   ~/.local/bin helpers, PlayCanvas list, MCP servers (~/.claude.json, no secrets), Blender MCP addon
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
C="$HOME/.claude"
LOCK="$HOME/.agents/.skill-lock.json"

GF_SRC="$(sed -n 's/^- GameFactory[^`]*`\(.*\)`.*/\1/p' "$C/CLAUDE.md" | head -1)"
GAMES_SRC="$(sed -n 's/^- Папка игр: `\(.*\)`.*/\1/p' "$C/CLAUDE.md" | head -1)"
[ -n "$GF_SRC" ] || { echo "GameFactory path not found in ~/.claude/CLAUDE.md"; exit 1; }

mkdir -p "$REPO/claude/skills" "$REPO/claude/hooks"
cp "$C/CLAUDE.md" "$REPO/claude/CLAUDE.md"
[ -f "$C/settings.json" ] && cp "$C/settings.json" "$REPO/claude/settings.json"
rsync -a --delete "$C/hooks/" "$REPO/claude/hooks/" 2>/dev/null || true
printf 'REPO=%s\nGAMEFACTORY=%s\nGAMES=%s\n' "$REPO" "$GF_SRC" "$GAMES_SRC" > "$REPO/claude/ORIGIN_PATHS"

third_party() { [ -f "$LOCK" ] && python3 -c "import json;print('\n'.join(k for k in json.load(open('$LOCK'))['skills']))" || true; }
TP="$(third_party)"
rm -rf "$REPO/claude/skills"/*
for d in "$C"/skills/*/; do
  n="$(basename "$d")"
  if ! grep -qx "$n" <<<"$TP"; then
    rsync -a --exclude node_modules --exclude __pycache__ "$d" "$REPO/claude/skills/$n/"
  fi
done
[ -f "$LOCK" ] && cp "$LOCK" "$REPO/third-party/skill-lock.json"

# helper tools, PlayCanvas list (skills themselves come from npx), MCP inventory (no env/headers), Blender addon
mkdir -p "$REPO/tools/bin" "$REPO/claude/spares" "$REPO/mcp/blender"
for t in playcanvas-skills claude-profiles; do [ -f "$HOME/.local/bin/$t" ] && cp "$HOME/.local/bin/$t" "$REPO/tools/bin/$t"; done
[ -f "$C/spares/playcanvas.list" ] && cp "$C/spares/playcanvas.list" "$REPO/claude/spares/playcanvas.list"
python3 - "$HOME/.claude.json" "$REPO/mcp/servers.json" <<'PY'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src)) if os.path.exists(src) else {}
keep = lambda m: {k: {kk: vv for kk, vv in v.items() if kk in ("type", "command", "args", "url")} for k, v in m.items()}
out = {"user": keep(d.get("mcpServers", {})), "project": {}}
for proj, v in d.get("projects", {}).items():
    for k, s in keep(v.get("mcpServers", {})).items():
        out["project"].setdefault(k, s)
json.dump(out, open(dst, "w"), indent=2, ensure_ascii=False); print("mcp:", list(out["user"]), "+ project:", list(out["project"]))
PY
ADDON="$(ls -t "$HOME/Library/Application Support/Blender"/*/scripts/addons/blender_mcp_addon.py "$HOME/.config/blender"/*/scripts/addons/blender_mcp_addon.py 2>/dev/null | head -1 || true)"
[ -n "$ADDON" ] && cp "$ADDON" "$REPO/mcp/blender/blender_mcp_addon.py"

if [ "$(cd "$GF_SRC" && pwd)" != "$REPO/GameFactory" ]; then
  rsync -a --delete --exclude node_modules --exclude backup/ --exclude demo-dist \
    --exclude .DS_Store --exclude __pycache__ --exclude 'DesignLibrary/inbox/*/' "$GF_SRC/" "$REPO/GameFactory/"
fi
# PromoLibrary: only our own text (breakdowns, genre patterns, catalogues, cut stats). Other people's
# videos, covers and frame sheets stay on this machine (analysis only, not ours to redistribute).
if [ -n "$GAMES_SRC" ] && [ -d "$GAMES_SRC/PromoLibrary" ]; then
  rsync -a --delete --prune-empty-dirs --exclude '_index/' --include '*/' --include '*.md' --include 'stats.json' \
    --exclude '*' "$GAMES_SRC/PromoLibrary/" "$REPO/PromoLibrary/"
fi
find "$REPO" -name .DS_Store -delete

# secret scan (abort if anything looks like a credential)
if grep -rIlE "(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|xox[baprs]-[A-Za-z0-9-]{10,})" \
     --exclude-dir .git "$REPO"; then
  echo "ABORT: possible secret in the files above"; exit 1
fi
echo "own skills: $(ls "$REPO/claude/skills" | tr '\n' ' ')"
git -C "$REPO" status --short | head -40
if [ "${1:-}" = "--commit" ]; then
  git -C "$REPO" add -A
  git -C "$REPO" commit -q -m "${2:-sync: local Claude rules and skills}" && git -C "$REPO" log --oneline -1
  echo "now: git -C \"$REPO\" push"
fi
