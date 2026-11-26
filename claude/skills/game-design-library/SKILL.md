---
name: game-design-library
description: Use when Alex sends his own gameplay recordings (video with his voice and comments) or game links to study game design — "разбери записи в inbox", "разбери запись <игра> в базу", "добавь игру в базу", "вот я поиграл, разбери", "что в базе есть про <жанр/механику/хук>", "какие паттерны для <жанр>" — and on your own at the «Идея» and «Скелет» steps of game-project-workflow to pull similar games, patterns, hooks and mechanics. Turns recordings into game cards (fantasy, first minute by seconds, loop, 3-horizon goals, hooks, GUI, monetisation, why alive/dead, Alex's quotes) and grows PATTERNS, HOOKS, BUNDLES, GUI and per-genre mechanics in GameFactory/DesignLibrary.
---

# Game design library (DesignLibrary)

Library: `<GameFactory>/DesignLibrary` (path from `~/.claude/CLAUDE.md`). Read its `README.md` first; the card format is `games/_TEMPLATE.md`; the recording guide for Alex is `RECORDING.md`. The constitution that the base feeds: `<GameFactory>/DESIGN/CONSTITUTION.md`.

## Mode 1: intake of recordings
1. Inventory `DesignLibrary/inbox/` (or the files/links Alex gave): per game a folder with video(s) and optional `notes.md`. Links: Roblox/Steam/CrazyGames page → web research for genre, online, dates (state the date of the number).
2. Per video, with `~/.local/bin/resource-run`:
   `python3 ~/.claude/skills/game-design-library/scripts/intake.py prep <video> <scratchpad>/<slug>/`
   → transcript (`transcript.txt`), `sheet.jpg` (every 5 s), `first2min.jpg` (every 3 s of the first 2 minutes), `moments.json` (Alex's phrases tagged фантазия/понял/застрял/результат/скучно/цель/ui/хук/деньги). No transcriber → the script prints the install command: ask Alex once, meanwhile use `notes.md`.
3. Look at `first2min.jpg` and `sheet.jpg`; for every voice moment open the nearest frame (`video_frames.py burst` for a dense moment). Only what you saw or heard.
4. Write `games/<slug>.md` from the template. Tags: [видно] mm:ss, [Alex] quote, [вывод]. Fill «Первая минута» by seconds with the formula step (1–5) and the 15 questions short score (`DESIGN/IDEA_FILTER.md`).
5. Copy 1–3 key frames + `first2min.jpg` to `games/img/<slug>/` (jpg, ≤ 400 KB each). Videos stay local: move the inbox folder to `inbox/_done/`.
6. Grow the shared files: a new transferable decision → `PATTERNS.md`; why started/stayed/returned → `HOOKS.md`; HUD/windows Alex praised → `GUI.md` with frame; mechanics → `mechanics/<жанр>.md`. Existing entry → add the game link, ★ at 3+ games. Contradiction with `CONSTITUTION.md` → list it for Alex, do not edit the constitution yourself.
7. `python3 DesignLibrary/tools/index.py`. Report to Alex in ≤10 lines: cards added, top 3 new patterns/hooks, what this means for current projects.

## Mode 2: consult (other skills call this)
For a project idea or skeleton: by genre and key words, `grep` `INDEX.md`, `mechanics/<жанр>.md`, `PATTERNS.md`, `HOOKS.md`, `BUNDLES.md`; return 3–5 similar games with online and why alive/dead, and the patterns that close [пробел] columns of `docs/GAME_SKELETON.md`, each with a `[[link]]`. Never present a pattern as proven if it has one source.

## Mode 3: our games after launch
`games/our-<slug>.md` with funnel numbers (`DESIGN/FUNNEL.md`), the biggest drop and the change made. Lessons that hold across games are proposed for `CONSTITUTION.md` (Alex approves).

## Rules
- Russian, short. Other people's games: analysis only, no assets taken.
- Do not upload Alex's recordings anywhere; transcription is local.
- Sync: library text and small frames go to git via `scripts/sync.sh` (inbox media excluded).
