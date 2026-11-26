---
name: game-idea-scout
description: Use when Alex wants ideas for the next game or trend research — "найди идеи для игры", "что сейчас залетает", "разведка идей", "какие игры растут в Steam/Roblox/CrazyGames", "что делать следующим", "проверь идею", "прогони идею через фильтр". Takes a daily snapshot of Steam's popular upcoming games and lists the biggest risers, checks rising Roblox experiences and web-portal trends, watches the trailers/pages of the top 5, describes fantasy and core loop, scores each with the 15-question filter, and writes a ranked idea report with web and Roblox fit. Also scores a single idea Alex brings.
---

# Game idea scout

Principle (from studios shipping 20–30 Roblox games a year): a Steam trailer that takes off is a free marketing test of a fantasy; the same fantasy and core loop can ship in 1–2 weeks on Roblox or the web. A narrow, concrete request beats «найди хиты»: filter → top 5 → watch → describe → score.

Paths: `<GameFactory>` from `~/.claude/CLAUDE.md`; reports in `<GameFactory>/DesignLibrary/scout/`; filter `<GameFactory>/DESIGN/IDEA_FILTER.md`; constitution `DESIGN/CONSTITUTION.md`.

## Mode A: scout (no idea given)
1. Steam snapshot, every run (risers need history; snapshots accumulate in git):
   `python3 ~/.claude/skills/game-idea-scout/scripts/scout_steam.py snapshot <GameFactory>/DesignLibrary/scout/snapshots`
   then `... risers <same dir> --days 30 --top 15`. Only one snapshot yet → say so and use today's top 50 filtered by Alex's genres instead of risers.
2. Filter out what we can't ship: big-budget, competitive shooters/MOBA, narrative-only, open-world survival at AAA scale. Keep: one clear fantasy, simple main action, cartoon/stylised, co-op chaos, sim/tycoon, physics comedy — fit with `StyleLibrary/TASTE.md`.
3. Roblox and web (built-in browser or web fetch, read pages as text): Roblox charts (rising/up-and-coming experiences), CrazyGames new and trending. Note name, link, online/date, one-line fantasy. Do not invent numbers: no number seen → «нет данных».
4. Top 5 overall: watch the trailer or gameplay (Steam trailer frames via `StyleLibrary/tools/grab_media.py` or `game-reference-analysis` on a downloaded public trailer, frames to scratchpad), write: fantasy in one phrase, main action, core loop, 3-horizon goals as seen, what sells in the trailer (the first 3 seconds).
5. Score each with the 15 questions (0/1/2, evidence), plus: **веб-годность** (one-input action, ≤ 5 s load possible, works without multiplayer) and **Roblox-годность** (multiplayer, social envy, monetisation of impatience), **MVP-дни** (estimate for our pipeline), similar games from `DesignLibrary` (mode 2 of `game-design-library`).
6. Report `scout/YYYY-MM-DD.md`: ranked table (idea, source link, fantasy, scores, web/Roblox fit, MVP days, risks) + for the top 2 a one-paragraph pitch «наша версия» (our twist, not a copy: own name, art, characters). Chat: top 3 in ≤ 10 lines. Alex chooses; the chosen one starts `game-project-workflow` with `docs/IDEA.md` pre-filled.

## Mode B: one idea (Alex's or from the report)
Fill `docs/IDEA.md` (template `templates/docs/IDEA.md`) honestly. Any of questions 1–3 = 0 → say «стоп» and offer 2 ways to fix the fantasy/action. Then the weakest 2–3 of the rest with concrete fixes.

## Rules
- Inspiration, not cloning: take the fantasy and loop type; never names, characters, art, levels or music of an existing game.
- Snapshot is the only thing written outside the report; nothing is published or sent.
- Model/effort are Alex's choice; this skill works on a mid-level model by design (narrow steps).
