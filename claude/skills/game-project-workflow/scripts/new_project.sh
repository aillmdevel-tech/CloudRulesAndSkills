#!/usr/bin/env bash
# Create a GameFactory project skeleton (folders + CLAUDE.md + doc templates). No code scaffolding.
# usage: new_project.sh <GameName> [parent-dir] [--levelcopier] [--minimal]
#   --levelcopier  add imports/levelcopier/
#   --minimal      only CLAUDE.md, README, PROJECT_STATE/DECISIONS/TASKS, src/, public/assets/
set -euo pipefail

NAME="${1:-}"; shift || true
[ -z "$NAME" ] && { echo "usage: $0 <GameName> [parent-dir] [--levelcopier] [--minimal]"; exit 1; }
PARENT=""; LC=0; MIN=0
for a in "$@"; do
  case "$a" in
    --levelcopier) LC=1 ;;
    --minimal) MIN=1 ;;
    *) PARENT="$a" ;;
  esac
done
if [ -z "$PARENT" ]; then
  PARENT="$(sed -n 's/^- Папка игр: `\(.*\)`.*/\1/p' "$HOME/.claude/CLAUDE.md" 2>/dev/null | head -1)"
  PARENT="${PARENT/#\~/$HOME}"
fi
[ -z "$PARENT" ] && { echo "parent dir not given and not found in ~/.claude/CLAUDE.md"; exit 1; }

DIR="$PARENT/$NAME"
if [ -e "$DIR" ] && [ -n "$(ls -A "$DIR" 2>/dev/null)" ]; then
  echo "refusing: $DIR exists and is not empty"; exit 1
fi
T="$(cd "$(dirname "$0")/../templates" && pwd)"
DATE="$(date +%Y-%m-%d)"

mkdir -p "$DIR"/{src,public/assets/{models,textures,ui,audio},docs}
fill() { sed -e "s/{{GAME_NAME}}/$NAME/g" -e "s/{{DATE}}/$DATE/g" "$1" > "$2"; }
fill "$T/CLAUDE.project.md" "$DIR/CLAUDE.md"
fill "$T/README.md" "$DIR/README.md"
DOCS="PROJECT_STATE DECISIONS TASKS"
if [ "$MIN" -eq 0 ]; then
  mkdir -p "$DIR"/references/{videos,screenshots,notes,frames} "$DIR/tests"
  DOCS="$DOCS GAME_DESIGN ARCHITECTURE REFERENCE_ANALYSIS VIDEO_STORYBOARD GAMEPLAY_BREAKDOWN ART_REFERENCE ART_SPEC"
fi
if [ "$LC" -eq 1 ]; then
  mkdir -p "$DIR/imports/levelcopier"
  DOCS="$DOCS ASSET_MANIFEST"
fi
for d in $DOCS; do fill "$T/docs/$d.md" "$DIR/docs/$d.md"; done
cat > "$DIR/.gitignore" <<'EOF'
node_modules/
dist/
test-results/
playwright-report/
.DS_Store
references/videos/
references/frames/
EOF
echo "created $DIR"
find "$DIR" -maxdepth 3 | sed "s|$PARENT/||" | sort
