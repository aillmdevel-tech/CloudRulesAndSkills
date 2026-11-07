# PROJECT_STATE — CloudRulesAndSkills (настройка Claude Code Alex)

> Новый чат: прочитай этот файл, `docs/SYSTEM_MAP.md` (полная схема) и `README.md`, затем выполняй «Следующий шаг».

Обновлено: 2026-11-07 · ветка `main` · аккаунт GitHub репо: aillmdevel-tech (привязан локально через github-account-router)

## Что это
Переносимая копия всей настройки Claude Code Alex (GameFactory): правила, свои скиллы, хуки, список сторонних
скиллов, MCP, GameFactory + UIFX. Развёртывание на новом устройстве — `BOOTSTRAP.md` / `scripts/install.sh`.

## Где что лежит (исходная машина, macOS)
- Клон: `/Users/mac/Downloads/WebAIGames/Rules/CloudRulesAndSkills`
- Живая настройка: `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/hooks/context_guard.py`, `~/.claude/skills/`
- GameFactory: `/Users/mac/Downloads/WebAIGames/Rules/GameFactory` (в репо — копия через `scripts/sync.sh`)

## Правила
- После изменения правил/скиллов/хуков/GameFactory: `scripts/sync.sh --commit "<что>"` → `git push`.
- Секреты в репо запрещены (sync.sh проверяет). Глобальный аккаунт gh не переключать.

## Сделано и проверено
- Репо залит (коммит «Add portable Claude Code setup»), 403 файла, без секретов.
- `install.sh` проверен в песочнице с фейковым HOME: свои скиллы, пути переписаны, settings сливаются без дублей, хук работает.
- Хук context_guard проверен вручную (pipe-тест); в живой сессии сработает с нового чата.

- 2026-11-07: добавлены game-autotest, TOKEN_SAVING, ручной «опусплан», правило github-account-router, `docs/SYSTEM_MAP.md`; починен `sync.sh` (раньше не копировал `GameFactory/templates`); актуализированы пороги хука (150k/200k) и списки скиллов в доках.

## Не проверено
- Полный install на реальном втором устройстве (сторонние скиллы, Playwright, Blender MCP).
- Срабатывание хуков в Claude Desktop (настроены сегодня, загрузятся в новой сессии).

## Следующий шаг
1. В новом чате убедиться, что в первом сообщении есть напоминание/предупреждение от context-guard (при большом контексте).
2. Дальше — обычная работа над играми; репо обновлять по правилу выше.
