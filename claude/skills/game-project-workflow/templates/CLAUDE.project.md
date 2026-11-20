# {{GAME_NAME}}

Проектная память для Claude Code. Общие правила Alex — в `~/.claude/CLAUDE.md`, процесс — скилл `game-project-workflow`.

## Суть
- Жанр / референс: _заполнить после анализа_
- Режим и стек: _A PlayCanvas / B TypeScript+Three.js / C 2D PixiJS / D существующий_ — _версии_
- Текущий этап: _разбор / вопросы / стиль и план / MVP: A кадр стиля · B геймфил · C готовая сцена / расширение_
- Алгоритм: `GameFactory/WORKFLOW.md` (один чат, вопросы только по пробелам, MVP с проверками A/B/C).

## Команды
- `npm run dev` — запуск (порт: _)
- `npm run build` — сборка
- `npx tsc --noEmit` — типы
- `npx playwright test` — тесты (если есть)

## Ограничения проекта
- Согласованный объём: см. `docs/GAME_DESIGN.md` → «MVP-сцена». Всё сверх — только после согласования.
- Плейсхолдеры помечаются `// PLACEHOLDER` и перечисляются в `docs/PROJECT_STATE.md`.

## Где что лежит
- Состояние и следующий шаг: `docs/PROJECT_STATE.md` (читать первым)
- Решения: `docs/DECISIONS.md` · Задачи: `docs/TASKS.md` · Архитектура: `docs/ARCHITECTURE.md`
- Мастер-план и шаги: `docs/plans/CURRENT.md` → план · Референсы и ресурсы: `docs/REFERENCES.md`, `references/`
- Ассеты: `public/assets/` · Blender-исходники: `assets/source/` · Спека: `docs/spec/`
