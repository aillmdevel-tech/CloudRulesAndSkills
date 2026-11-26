# CloudRulesAndSkills

Переносимая настройка Claude Code Alex для разработки браузерных игр (GameFactory).

**Новое устройство:** открой Claude Code и напиши:
> Разверни мою настройку из репозитория https://github.com/aillmdevel-tech/CloudRulesAndSkills — следуй BOOTSTRAP.md

Claude склонирует репо, поставит инструменты, правила, скиллы, хуки и проверит результат ([BOOTSTRAP.md](BOOTSTRAP.md)).

## Что внутри
| Папка | Что |
|---|---|
| `claude/CLAUDE.md` | глобальные правила (язык, процесс, автовыбор скиллов, стек, проверка, контекст) |
| `claude/skills/` | свои скиллы (20): game-project-workflow, **game-idea-scout** (идеи и тренды), **game-design-library** (база разборов игр), game-art-first, game-reference-analysis, game-visual-comparison, game-ui-motion-sound, game-autotest, **game-promo-kit** (промо по жанрам), **playgama-crazy-publisher** (SDK, реклама, IAP, загрузочный экран, публикация), character-animation, levelcopier-asset-pipeline, diagnosing-bugs, retro, writing-for-agents, chat-handoff, save-context, github-account-router, threejs-debug-profiler, threejs-aaa-graphics-builder |
| `claude/hooks/`, `claude/settings.json` | хуки контекста и memory-bank + outputStyle |
| `third-party/` | сторонние скиллы (frontend-design, webapp-testing, grilling, frontend-visual-qa; PlayCanvas ×16 — выключены) — ставятся из официальных репо |
| `tools/bin/` | утилиты: playcanvas-skills, claude-profiles |
| `mcp/` | MCP: blender (+ аддон), afk-rig, playgama; `servers.json` без ключей |
| `GameFactory/` | алгоритм `WORKFLOW.md`, стек Three.js, StyleLibrary, шаблоны, UIFX (32 эффекта, 43 звука CC0) |
| `PromoLibrary/` | текст библиотеки промо-референсов: разбивки по секундам, паттерны 11 жанров Roblox, каталоги, статистика склеек (чужие видео и кадры не хранятся) → `<папка игр>/PromoLibrary` |
| `docs/SYSTEM_MAP.md` | **полная схема системы** — читать первой |
| `docs/TOKEN_ECONOMY.md` | экономия токенов и автоматический перенос контекста |
| `scripts/install.sh` | развернуть на машине · `scripts/sync.sh` — забрать изменения с машины в репо |

Секретов в репо нет: `sync.sh` проверяет файлы перед коммитом.
