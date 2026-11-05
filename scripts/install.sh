#!/usr/bin/env bash
# Deploy Alex's Claude Code setup from this repo onto THIS machine (macOS / Linux; Windows: Git Bash/WSL).
#   scripts/install.sh [--games-dir DIR] [--with-blender-mcp] [--skip-third-party] [--skip-playwright]
# Defaults: games dir = ~/WebAIGames, GameFactory = <this repo>/GameFactory (used in place, so edits
# can be committed back with scripts/sync.sh).
# Existing ~/.claude/CLAUDE.md and settings.json are backed up (*.bak.<time>); settings are MERGED.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
C="$HOME/.claude"
GAMES="$HOME/WebAIGames"; BLENDER=0; TP=1; PW=1
while [ $# -gt 0 ]; do case "$1" in
  --games-dir) GAMES="$2"; shift 2 ;; --with-blender-mcp) BLENDER=1; shift ;;
  --skip-third-party) TP=0; shift ;; --skip-playwright) PW=0; shift ;;
  *) echo "unknown arg $1"; exit 1 ;; esac; done
GAMES="${GAMES/#\~/$HOME}"; GF="$REPO/GameFactory"
for t in git python3; do command -v $t >/dev/null || { echo "missing: $t"; exit 1; }; done
command -v node >/dev/null || echo "WARN: node/npm missing — third-party skills and UIFX demo need them"
mkdir -p "$C/skills" "$C/hooks" "$GAMES"
STAMP="$(date +%Y%m%d%H%M%S)"

# paths on the source machine (written by sync.sh) — replaced with this machine's paths
OLD_REPO="$(sed -n 's/^REPO=//p' "$REPO/claude/ORIGIN_PATHS")"
OLD_GF="$(sed -n 's/^GAMEFACTORY=//p' "$REPO/claude/ORIGIN_PATHS")"
OLD_GAMES="$(sed -n 's/^GAMES=//p' "$REPO/claude/ORIGIN_PATHS")"
rewrite() { OLDR="$OLD_REPO" NEWR="$REPO" OLDGF="$OLD_GF" NEWGF="$GF" OLDG="$OLD_GAMES" NEWG="$GAMES" perl -pi -e \
  's/\Q$ENV{OLDR}\E/$ENV{NEWR}/g; s/\Q$ENV{OLDGF}\E/$ENV{NEWGF}/g; s/\Q$ENV{OLDG}\E(?=[`\/ ]|$)/$ENV{NEWG}/g' "$1"; }

# 1. global rules
[ -f "$C/CLAUDE.md" ] && cp "$C/CLAUDE.md" "$C/CLAUDE.md.bak.$STAMP" && echo "backup: CLAUDE.md.bak.$STAMP"
cp "$REPO/claude/CLAUDE.md" "$C/CLAUDE.md"; rewrite "$C/CLAUDE.md"

# 2. hooks + settings (merge: repo hooks/outputStyle added, everything else of the user kept)
rsync -a "$REPO/claude/hooks/" "$C/hooks/"; chmod +x "$C"/hooks/* 2>/dev/null || true
[ -f "$C/settings.json" ] && cp "$C/settings.json" "$C/settings.json.bak.$STAMP"
python3 - "$REPO/claude/settings.json" "$C/settings.json" <<'EOF'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
new = json.load(open(src))
cur = json.load(open(dst)) if os.path.exists(dst) else {}
for k, v in new.items():
    if k != "hooks":
        cur.setdefault(k, v)
hooks = cur.setdefault("hooks", {})
for ev, groups in new.get("hooks", {}).items():
    have = {h.get("command") for x in hooks.get(ev, []) for h in x.get("hooks", [])}
    for g in groups:
        if all(h["command"] not in have for h in g["hooks"]):
            hooks.setdefault(ev, []).append(g)
json.dump(cur, open(dst, "w"), indent=2, ensure_ascii=False)
print("settings merged:", list(cur))
EOF

# 3. third-party skills (official CLI, telemetry off)
if [ "$TP" = 1 ] && command -v npx >/dev/null; then
  export DO_NOT_TRACK=1 DISABLE_TELEMETRY=1
  bash "$REPO/third-party/install_third_party.sh" || echo "WARN: some third-party skills failed (see above)"
fi

# 4. own skills (overwrite; includes patched grill-me) + path rewrite inside them
for s in "$REPO"/claude/skills/*/; do
  n="$(basename "$s")"; rm -rf "$C/skills/$n"; cp -R "$s" "$C/skills/$n"
  { grep -rlF -e "$OLD_GF" -e "$OLD_REPO" "$C/skills/$n" 2>/dev/null || true; } | while read -r f; do rewrite "$f"; done
done
chmod +x "$C"/skills/*/scripts/* 2>/dev/null || true
ln -sfn "$C/skills/game-project-workflow/templates" "$GF/templates" 2>/dev/null || true

# 5. tools
if [ "$PW" = 1 ]; then
  python3 -m pip install --user -q playwright Pillow && python3 -m playwright install chromium \
    || echo "WARN: Python Playwright install failed"
fi
[ -f "$GF/UIFX/package.json" ] && command -v npm >/dev/null && (cd "$GF/UIFX" && npm install --no-fund --no-audit >/dev/null && echo "UIFX deps ok") || true

# 6. MCP (optional)
if [ "$BLENDER" = 1 ]; then
  if command -v claude >/dev/null; then claude mcp add --scope user blender -- uvx blender-mcp || true
  else echo "add MCP manually: see mcp/MCP.md"; fi
fi

echo; echo "== result"
echo "CLAUDE.md -> GameFactory=$GF, games=$GAMES"
echo "skills: $(ls "$C/skills" | wc -l | tr -d ' ') in $C/skills"
for t in node gh ffmpeg ffprobe yt-dlp blender uvx; do printf "  %-8s %s\n" "$t" "$(command -v $t || echo 'missing — see BOOTSTRAP.md')"; done
echo "Open a NEW Claude Code chat to load rules, skills and hooks."
