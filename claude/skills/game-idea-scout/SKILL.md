---
name: game-idea-scout
description: Use when Alex wants ideas for the next game or trend research — "найди идеи для игры", "roblox search", "full search", "что сейчас залетает", "разведка идей", "какие игры растут в Steam/Roblox/CrazyGames/Google Play", "что делать под веб / под Roblox", "проверь идею", "прогони идею через фильтр". Two modes: roblox search (Roblox charts only: young games climbing Top Trending / Up-and-Coming — fast, good for web too) and full search (Roblox + Steam upcoming risers filtered to funny/casual/physics/co-op + YouTube, TikTok, Instagram, Google Play, CrazyGames, Google Trends). Watches the top candidates, describes fantasy and core loop, scores each with the 15-question filter, and writes a ranked report with links, web/Roblox fit and the rejected list with reasons. Also scores a single idea Alex brings.
---

# Game idea scout

Principle (studios shipping 20–30 Roblox games a year): a trailer or game that takes off is a free marketing test of a fantasy; the same fantasy and core loop can ship in 1–2 weeks on Roblox or the web. Narrow concrete steps beat «найди хиты»: collect → filter → top candidates → watch → describe → score.

Paths: `<GameFactory>` from `~/.claude/CLAUDE.md`. `S=<GameFactory>/DesignLibrary/scout`, snapshots in `$S/snapshots/{steam,roblox,youtube}/`, reports `$S/YYYY-MM-DD-<mode>.md`. Scripts `~/.claude/skills/game-idea-scout/scripts/`, run through `~/.local/bin/resource-run` with `/usr/local/bin/python3`. Filter `DESIGN/IDEA_FILTER.md`, constitution `DESIGN/CONSTITUTION.md`, taste `StyleLibrary/TASTE.md`.

Daily snapshots run by themselves (launchd `com.gamefactory.scout`, 10:00, script `scripts/daily.sh`, log `$S/snapshots/daily.log`), so risers have history. If today's snapshot is missing, take it first.

## Mode «roblox search» (default when Alex says «roblox search» or only asks about Roblox)
1. `scout_roblox.py snapshot $S/snapshots/roblox` (if not today) → `scout_roblox.py report $S/snapshots/roblox --max-age 90 --top 30`: young games (≤ 90 days) by players now, change vs the previous snapshot, which chart they sit in, genres dominating trending.
2. Candidates: young + in Top Trending/Up-and-Coming + growing, or ≥ 5k players at age ≤ 30 d. Skip pure RP/hangouts, licensed IP, anime fighters, «Steal a …» clones already saturated (≥ 3 similar in top 30) — record as rejected with the reason.
3. Top 5–8: open each game page (web fetch / built-in browser, as text) + a YouTube gameplay video (`scout_youtube.py --queries "<name> roblox"`); description, thumbnail text, first-minute loop.
4. Score (below). Web fit is judged here too: a Roblox hit with a single-player core and one-input action ports well to the web.

## Mode «full search» (Roblox + web, general trends)
Everything from roblox search, plus:
1. **Steam upcoming:** `scout_steam.py snapshot $S/snapshots/steam --pages 4`, `fun … --top 45` (our kind: Funny/Casual/Physics/Co-op/Simulation… without heavy tags, releasing within ~18 months), `risers … --fun` (rank gains; needs ≥ 2 snapshots days apart — else say so and use `fun`). Open the app page + trailer of the top 8 (`StyleLibrary/tools/fetch_steam.py` for metadata/movies).
2. **YouTube:** `scout_youtube.py $S/snapshots/youtube` (this month, by views, ~10 queries: steam trailers, roblox trends, physics/friendslop, mobile). Views/day on top videos = momentum.
3. **TikTok, Instagram Reels, YouTube Shorts** (no scripting without login): web search for this month — «viral game tiktok <month year>», «game everyone is playing tiktok», «#indiegame trend», «roblox tiktok trend». Keep only items with a source link and a date; a number seen → write it with the date, no number → «нет данных».
4. **Google Play / App Store:** web search and store pages for top new / trending casual and simulation games (pre-registration, «early access» hits).
5. **Web portals:** CrazyGames (new, trending, «hot»), Poki, Playgama catalog pages as text.
6. **Google Trends:** web search / trends.google.com explore for the top candidate names and genre words (rising, last 30 days).
7. Cross-signal: a fantasy seen in ≥ 2 sources (e.g. Steam riser + TikTok + Roblox clone climbing) ranks first — that is a general trend, not a single hit.

## Scoring (both modes)
For every candidate kept: fantasy in one phrase, main action, core loop, what the trailer/thumbnail sells in the first 3 s, 15 questions (0/1/2, short evidence), **веб-годность** (one-input action, ≤ 5 s load possible, works single-player, rewarded-ads points), **Roblox-годность** (multiplayer value, social envy, monetisation of impatience), **MVP-дни** for our pipeline, risk (saturation, IP, tech). Similar games from `DesignLibrary` (consult mode of `game-design-library`).

## Report `$S/YYYY-MM-DD-<mode>.md`
1. **Лучше всего под веб** — top 3 with links (every source), why, our twist (own name/art/characters — inspiration, not a copy), MVP days.
2. **Лучше всего под Roblox** — top 3, same format.
3. **Общие тренды** (full only) — fantasies/mechanics seen in several sources, with links.
4. **Рассмотрено** — table of all candidates: name, source, link, numbers with date, score.
5. **Отсеяно** — each rejected candidate with the reason (heavy genre, IP, saturated, weak first minute, needs big tech, no data).
6. **Методика и ограничения** — which sources worked today, snapshot dates compared, what had no data.
Chat: top 3 web + top 3 Roblox in ≤ 15 lines + path to the report. Alex chooses; the chosen one starts `game-project-workflow` with `docs/IDEA.md` pre-filled.

## Mode «одна идея» (Alex's or from a report)
Fill `docs/IDEA.md` (template) honestly. Any of questions 1–3 = 0 → «стоп» and two ways to fix the fantasy/action. Then the weakest 2–3 of the rest with concrete fixes.

## Rules
- Inspiration, not cloning: take the fantasy and loop type; never names, characters, art, levels or music of an existing game.
- Numbers only as seen, with date and source. Concurrent players swing by hour and weekday: compare snapshots at the same hour (daily job).
- Snapshots and reports are the only files written; nothing is posted or sent.
