# GameFactory

Постоянная система разработки браузерных игр Alex в Claude Code. Не привязана ни к одной игре.

## Где что лежит

| Что | Где |
|---|---|
| Глобальные правила (грузятся в каждой сессии) | `~/.claude/CLAUDE.md` |
| Собственные скиллы | `~/.claude/skills/{game-project-workflow, game-reference-analysis, levelcopier-asset-pipeline, game-visual-comparison, game-ui-motion-sound, chat-handoff, github-account-router, game-autotest}` |
| Геймдизайн: конституция, фильтр идеи (15 вопросов), скелет 17 колонок, первая минута, воронка, перенос на Roblox | [DESIGN/](DESIGN/README.md) |
| База разборов игр: карточки, паттерны, хуки, связки, GUI, механики по жанрам, разведка идей | [DesignLibrary/](DesignLibrary/README.md) · как записывать игры — [RECORDING.md](DesignLibrary/RECORDING.md) |
| Bug shield: уроки по багам всех игр | [LESSONS/](LESSONS/README.md) |
| Готовые механики с тестами | [MECHANICS/](MECHANICS/README.md) |
| Визуальный вкус Alex: игры-референсы, жанровые шаблоны графики/анимаций/VFX/UI | [StyleLibrary/](StyleLibrary/README.md) |
| Анимации и звуки UI | [UIFX/](UIFX/README.md) — 32 эффекта, 43 звука CC0, 5 стилей, демо `npm run demo` |
| Сторонние скиллы | `~/.claude/skills/` (список и источники — [THIRD_PARTY_SKILLS.md](THIRD_PARTY_SKILLS.md)) |
| Шаблоны проекта и документов | [templates/](templates) → ссылка на `~/.claude/skills/game-project-workflow/templates` |
| Процесс | [WORKFLOW.md](WORKFLOW.md) |
| Перенос на другой компьютер | [SETUP_NEW_PC.md](SETUP_NEW_PC.md), `scripts/backup.sh`, `scripts/restore.sh` |
| Снимок конфигурации без секретов | `backup/` (обновляется `scripts/backup.sh`) |
| Игры | `/Users/mac/Downloads/WebAIGames/<ИмяИгры>/` |

## Как пользоваться

Открой новую сессию Claude Code в папке `WebAIGames` (или в папке игры) и пиши обычными словами:

- «Делаем Roblox-like игру на PlayCanvas» + ТЗ, видео, скриншоты
- «Делаем 3D-игру на TypeScript без движка»
- «Найди идеи для игры» / «прогони идею через фильтр»
- «Быстрая игра: <идея>»
- «Разбери записи в inbox» (мои записи игр с голосом → база)
- «Разбери воронку» (после запуска)
- «Вот видео игры, разбери механику»
- «Вот выгрузка LevelCopier, восстанови сцену»
- «Сделай похоже на скриншот» / «проверь игру в браузере»

Скиллы называть не нужно — Claude выбирает их сам по смыслу задачи (правила маршрутизации — в `~/.claude/CLAUDE.md`).
Вопросы по ТЗ задаются сами (только по пробелам), см. [WORKFLOW.md](WORKFLOW.md).

Новый проект вручную (обычно Claude делает это сам):

```bash
bash ~/.claude/skills/game-project-workflow/scripts/new_project.sh MyGame
```

Флаги: `--levelcopier` (папка импорта + ASSET_MANIFEST), `--minimal` (минимальный набор документов).

## После изменения правил или скиллов

```bash
bash /Users/mac/Downloads/WebAIGames/Rules/GameFactory/scripts/backup.sh
```
