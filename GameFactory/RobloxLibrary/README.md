# RobloxLibrary

Сырьё скилла `roblox-game-builder`: транскрипты видео Roblox-разработчиков (автосубтитры, `[MM:00]` абзацы).

- `transcripts/tap/` — канал Tap (23 видео, `_index.txt`: id | длительность | просмотры | название).
- `transcripts/<канал>/` — похожие каналы.

Транскрипты — чужой текст: лежат только локально, в git не синхронизируются (`scripts/sync.sh` исключает `transcripts/`). Выжимки с таймкодами — в `~/.claude/skills/roblox-game-builder/references/`.
Новое видео: `yt-dlp --skip-download --write-auto-subs --sub-langs "en-orig,en" --sub-format vtt <url>` → конвертер в текст → заметка в нужный reference.
