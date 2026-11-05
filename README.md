# CloudRulesAndSkills

Переносимая настройка Claude Code Alex для разработки браузерных игр (GameFactory).

**Новое устройство:** открой Claude Code и напиши:
> Разверни мою настройку из репозитория https://github.com/aillmdevel-tech/CloudRulesAndSkills — следуй BOOTSTRAP.md

Claude склонирует репо, поставит инструменты, правила, скиллы, хуки и проверит результат ([BOOTSTRAP.md](BOOTSTRAP.md)).

## Что внутри
| Папка | Что |
|---|---|
| `claude/CLAUDE.md` | глобальные правила (язык, процесс, автовыбор скиллов, стек, проверка, контекст) |
| `claude/skills/` | свои скиллы: game-project-workflow, game-reference-analysis, levelcopier-asset-pipeline, game-visual-comparison, game-ui-motion-sound, chat-handoff, github-account-router, пропатченный grill-me |
| `claude/hooks/`, `claude/settings.json` | хук контроля контекста + outputStyle |
| `third-party/` | сторонние скиллы (PlayCanvas ×16, frontend-design, webapp-testing, grilling, frontend-visual-qa) — ставятся из официальных репо |
| `mcp/MCP.md` | Blender MCP |
| `GameFactory/` | процесс, шаблоны, UIFX (32 эффекта, 43 звука CC0, демо) |
| `docs/TOKEN_ECONOMY.md` | экономия токенов и автоматический перенос контекста |
| `scripts/install.sh` | развернуть на машине · `scripts/sync.sh` — забрать изменения с машины в репо |

Секретов в репо нет: `sync.sh` проверяет файлы перед коммитом.
