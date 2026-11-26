#!/bin/bash
# Daily scout snapshots (launchd com.gamefactory.scout). Steam + Roblox + YouTube; ~1–3 min, no tokens.
GF="$(sed -n 's/^- GameFactory: `\(.*\)`.*/\1/p' "$HOME/.claude/CLAUDE.md" | head -1)"
S="$GF/DesignLibrary/scout/snapshots"; K="$(cd "$(dirname "$0")" && pwd)"
PY=/usr/local/bin/python3; [ -x "$PY" ] || PY=python3
RR="$HOME/.local/bin/resource-run"; [ -x "$RR" ] || RR=""
{
  echo "== $(date '+%F %T')"
  for i in $(seq 1 40); do
    $RR bash -c "$PY '$K/scout_steam.py' snapshot '$S/steam' --pages 4; $PY '$K/scout_roblox.py' snapshot '$S/roblox'; $PY '$K/scout_youtube.py' '$S/youtube' --per 10 --detail 0 | tail -1"
    rc=$?; [ $rc -ne 75 ] && break; sleep 60
  done
  echo "rc=$rc"
} >> "$S/daily.log" 2>&1
