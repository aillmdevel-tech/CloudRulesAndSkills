# RobloxLibrary

База по Roblox: как делают, выглядят, затягивают и зарабатывают топовые игры. Читают скилл `roblox-game-builder` (Roblox) и `game-art-first`, `game-project-workflow` (веб-игры по Roblox-референсу).

- [STYLE.md](STYLE.md) — выжимка: формы игр, темп первой сессии, что затягивает, визуал, UI, VFX, экономика, места офферов (Roblox → rewarded в вебе), анти-примеры. **Начинать отсюда.**
- [REFS.md](REFS.md) — какие кадры открыть под задачу + палитры всех игр.
- `notes/` — разборы каналов по играм: BachaBlox (глубокие симуляторы), FoltynFamily (вирусные «глагол + абсурд», игры с концом), Valtric1 (новый аккаунт без Robux: F2P-темп).
- `refs/<игра>/` — ключевые кадры (локально).
- `transcripts/` — транскрипты: `tap/` и `similar/` (советы разработчиков, выжимки в `~/.claude/skills/roblox-game-builder/references/`), `youtubers/` (геймплей-каналы, `_index.txt`).
- `tools/refs_index.py` — палитры и таблица для REFS.md.

Транскрипты и кадры — чужие материалы: только локально, в git не синхронизируются (`scripts/sync.sh`). Текстовые разборы (`STYLE.md`, `REFS.md`, `notes/`) — наши, синхронизируются.

Добавить канал: список видео `yt-dlp --flat-playlist --print "%(id)s|%(duration)s|%(view_count)s|%(title)s" <канал>/videos` → субтитры (`--write-auto-subs --sub-langs "en-orig,en"`) и кадры потоком без сохранения видео (первые 3 мин каждые 6 с + всё видео каждые 30 с) → листы → разбор по шаблону `notes/*.md` → кадры в `refs/` → обновить STYLE.md и REFS.md.
