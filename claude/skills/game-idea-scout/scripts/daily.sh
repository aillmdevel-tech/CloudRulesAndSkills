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
  # Daily digest (no AI): growth over 7 days, saturation clusters, Steam fun risers. Read by game-idea-scout.
  D="$GF/DesignLibrary/scout/daily"; mkdir -p "$D"; F="$D/$(date +%F).md"
  for i in $(seq 1 40); do
    $RR bash -c "{ echo '# Scout digest $(date +%F)'; echo; echo '## Roblox: молодые игры, рост за 7 дней'; echo '\`\`\`'; $PY '$K/scout_roblox.py' report '$S/roblox' --max-age 60 --top 30 --days 7; echo '\`\`\`'; echo '## Roblox: кластеры насыщения'; echo '\`\`\`'; $PY '$K/scout_roblox.py' clusters '$S/roblox'; echo '\`\`\`'; echo '## Steam: рост ранга (весёлые)'; echo '\`\`\`'; $PY '$K/scout_steam.py' risers '$S/steam' --fun --top 20; echo '\`\`\`'; echo '## Steam: весёлые в топе вишлистов'; echo '\`\`\`'; $PY '$K/scout_steam.py' fun '$S/steam' --top 25; echo '\`\`\`'; } > '$F'"
    rc=$?; [ $rc -ne 75 ] && break; sleep 60
  done
  echo "digest rc=$rc → $F"
} >> "$S/daily.log" 2>&1
