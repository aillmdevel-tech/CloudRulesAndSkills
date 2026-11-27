---
name: game-idea-scout
description: Use when Alex wants ideas for the next game or trend research — "найди идеи для игры", "roblox search", "full search", "что сейчас залетает", "разведка идей", "какие игры растут в Steam/Roblox/CrazyGames/Google Play", "что делать под веб / под Roblox", "проверь конкуренцию", "проверь идею", "прогони идею через фильтр", "что смешать". Finds the best ideas to build fast for the web and Roblox: reads the daily auto-collected stats (Roblox charts, Steam wishlists, fresh Steam releases by current players, YouTube), finds growing fantasies and saturated clusters, builds combinations (fresh fantasy + proven loop + trend seasoning), checks competition on Roblox, Steam, CrazyGames and Playgama with a script, scores each with the constitution's 15 questions, and writes a ranked report with links, why it will be popular, the main goal, competitors and the rejected list. Also checks a single idea Alex brings.
---

# Game idea scout

Principle: a trailer or game that takes off is a free test of a fantasy; the same fantasy with our loop ships in days. The best idea = **proven demand somewhere + free space on the target platform + one clear action + fast MVP**.

Paths: `<GameFactory>` from `~/.claude/CLAUDE.md`; `S=<GameFactory>/DesignLibrary/scout`. Scripts in `~/.claude/skills/game-idea-scout/scripts/`, always via `~/.local/bin/resource-run /usr/local/bin/python3 <script>` (exit 75 = slots busy, wait and retry). Long output → file in the scratchpad, read only the summary. Filter: `<GameFactory>/DESIGN/IDEA_FILTER.md`, constitution `DESIGN/CONSTITUTION.md` (formula, 20 bans, web vs Roblox table), taste `StyleLibrary/TASTE.md`, similar games `DesignLibrary/` (consult mode of `game-design-library`).

## Collected automatically every day
launchd `com.gamefactory.scout`, 10:00, `scripts/daily.sh` (log `$S/snapshots/daily.log`):
- snapshots `$S/snapshots/{steam,steam-new,roblox,youtube}/YYYY-MM-DD.json` (`steam` = upcoming by wishlists, `steam-new` = released ≤ 90 days from top sellers + popular new, with current players);
- digest `$S/daily/YYYY-MM-DD.md` (no AI): young Roblox games with growth over 7 days, Roblox saturation clusters, Steam fun risers, fun released games by current players, fun games in the wishlist top.

Not installed on this Mac (`launchctl print gui/$(id -u)/com.gamefactory.scout` fails) → install: see `BOOTSTRAP.md` of CloudRulesAndSkills (line with `com.gamefactory.scout.plist`). Today's snapshot missing → take it first: `scout_steam.py snapshot $S/snapshots/steam --pages 4`, `scout_steam.py released $S/snapshots/steam-new`, `scout_roblox.py snapshot $S/snapshots/roblox`.

## Step 0. Ask Alex (once, only what is unknown, one short message)
1. Target: web (which portals: CrazyGames, Playgama, Яндекс, Poki), Roblox, or both?
2. MVP time: «быстрая игра» 2–5 days, or 1–2 weeks?
3. Single-player only, or multiplayer allowed (web: async records / ghosts)?
4. Genres or fantasies he wants or bans now; anything to continue (a running project, existing assets/engine modules)?
5. Monetisation preference (rewarded ads only, IAP, Robux passes)?

If Alex says «сам реши» or does not answer: web = CrazyGames + Playgama, MVP ≤ 5 days, single-player, rewarded ads; Roblox = MVP ≤ 10 days, multiplayer. Write the assumptions at the top of the report.

## Step 1. Collect the pool
- **Both modes:**
  - Read the last 1–3 digests in `$S/daily/`.
  - Fresh numbers: `scout_roblox.py report $S/snapshots/roblox --max-age 90 --top 40 --days 7` and `scout_roblox.py clusters $S/snapshots/roblox`.
  - Descriptions of the top 10–15 candidates: `games.roblox.com/v1/games?universeIds=…`.
  - **Fresh Steam hits:** `scout_steam.py hot $S/snapshots/steam-new --top 25`. Wishlists lose a game the day it launches, so this list is the only place post-launch hits show up. A co-op job-sim or incremental with ≥ 3k online and ≤ 30 days old is a top Roblox candidate. Check Roblox for a port the same day: Moon Sweepers (Steam, 23.10.2026) got the Roblox port Sweep The Moon on its launch day, 9k online a month later.
- **«roblox search»** stops here, plus a YouTube check of the top 5: `scout_youtube.py $S/snapshots/youtube --queries "<name> roblox" --per 5`.
- **«full search»** adds:
  - **Steam:**
    - `scout_steam.py fun $S/snapshots/steam --top 45` and `risers … --fun` (honest after ≥ 2 snapshots days apart).
    - Short descriptions via `store.steampowered.com/api/appdetails?appids=…&filters=basic`.
  - **YouTube:** `scout_youtube.py $S/snapshots/youtube` (month by views).
  - **Web search (no login):**
    - TikTok/Reels/Shorts «viral game <month year>».
    - Google Play / App Store new trending casual.
    - CrazyGames/Poki «new / trending».
    - Keep only items with a link and a date; no number → «нет данных».
- **Pool:** 15–30 candidates. Drop at once and list in «Отсеяно» with the reason:
  - heavy genres (open world, MMO, extraction, RTS, big story);
  - licensed IP and official events;
  - like < 75 %;
  - atmosphere-only horror without a simple action.

## Step 2. Combinations (the main value)
Prefer a mix over a copy. Recipe: **fresh fantasy** (Steam upcoming / YouTube / TikTok, not yet on the target platform) + **proven loop** (a Roblox chart meta or a web evergreen) + **seasoning** (a trend element: ragdoll, cleaning ASMR, «further = luckier», evolution, raising). A saturated cluster (≥ 3 games in `clusters`) is never the base; use only its strongest piece as seasoning.

For each combination write:
- **Смесь:** A (source link, number, date) + B (link, number) + seasoning (link).
- **Как смешиваем:** what exactly comes from each (fantasy from A, loop from B, which mechanic from the seasoning); what we drop.
- **Главная цель игрока:** the one result he wants (step 1 of the formula) and the 3 horizons (now / session / week) shown by the world.
- **Почему залетит:** demand proof (where the fantasy grows, numbers) + the gap (competition on the target is empty or weak) + why the first 10 s sells it (thumbnail, first action).
- **Первая минута:** 0–3 / 3–10 / 10–30 / 30–60 / 60–120 s.
- **Наш твист:** own name, characters, art (inspiration, not a copy).

## Step 3. Competition (script, for every kept idea)
`scout_compete.py "<kw1>|<kw2>|<kw3>" --out <scratchpad>/compete-<slug>.json`. Keywords are 3+ English phrases players would search: fantasy + verb, the verb with another actor, and the Roblox title template of the genre, e.g. `"raccoon steal|steal from house|steal & escape"`. A direct analog under another name counts as competition: Gnomes! [Steal & Escape] (21M visits) was missed when only `raccoon` and `steal from house` were searched. Verdict per platform: **пусто / лидер / забито**.
- **Strong game:**
  - Roblox: ≥ 5k playing.
  - Steam: ≥ 1000 reviews in the last 2 years; older hits are only proof of evergreen demand.
  - CrazyGames: ≥ 50k votes.
  - Playgama: name matches.
- **Read the names:** search returns unrelated popular games; drop them yourself.

How to read it:
| Target | Competition = | Demand proof = |
|---|---|---|
| Roblox | Roblox verdict + young strong games | Steam wishlists / reviews, web votes, YouTube |
| Web | CrazyGames + Playgama verdict | Roblox players, Steam, YouTube |

- **Best:** demand proven elsewhere + target «пусто».
- **OK:** target «лидер», if our twist is clear in one phrase.
- **«забито»:** only with a new verb or fantasy, otherwise reject.

## Step 4. Filter and rank
- **15 questions** (0/1/2 with one line of evidence). Any of 1–3 = 0 → out (or fix the fantasy/action and re-score). Check the 20 bans: 1, 2, 3, 8, 14 and 18 kill most ideas.
- **Final score** = questions 4–15 (0–24) + demand (0–6: +2 per independent source where the fantasy grows) + gap on the target (пусто +4, лидер +2, забито −4) + speed (MVP ≤ 5 d +3, ≤ 10 d +1).
- **Web fit:** one input, ≤ 5 s load, single-player, rewarded-ad points.
- **Roblox fit:** friends value, visible status/envy, impatience to sell.
- **Same engine:** if two winners share a system (e.g. «object = decor + income + rarity»), say so: build it once in `MECHANICS/`.

## Report `$S/YYYY-MM-DD-<mode>.md`
1. **Допущения** (answers from step 0).
2. **Лучше всего под веб:** top 3 combinations in the step 2 format + filter scores + competition verdicts with leader links + MVP days.
3. **Лучше всего под Roblox:** top 3, same.
4. **Общие тренды:** fantasies seen in ≥ 2 sources; saturated clusters (do not build as a base).
5. **Рассмотрено:** table of all candidates (source, link, numbers with date, score).
6. **Отсеяно:** every rejected one with the reason (heavy, IP, saturated + count, weak like, weak first minute, no data).
7. **Методика:** sources that worked, snapshot dates compared, what had no data.

**Chat:** ≤ 15 lines: top web + top Roblox with one-phrase reason and competition verdict, path to the report. The chosen idea starts `game-project-workflow` with `docs/IDEA.md` pre-filled from the report.

## Mode «одна идея» / «проверь конкуренцию»
1. Fill `docs/IDEA.md` (template) honestly; any of 1–3 = 0 → «стоп» + two ways to fix.
2. `scout_compete.py` on 2–3 keywords → competitors with links and the verdict for the target.
3. Name 1–2 combinations that lift the weakest questions or escape a saturated space.

## Rules
- Inspiration, not cloning: take the fantasy and loop type, never names, characters, art, levels or music.
- Numbers only as seen, with date and source. Roblox online swings by hour: compare snapshots of the same hour (the daily job).
- Writes only snapshots, digests and reports; posts and sends nothing.
