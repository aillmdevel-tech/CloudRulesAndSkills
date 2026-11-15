# {{GAME_NAME}}

Проектная память для Claude Code. Общие правила Alex — в `~/.claude/CLAUDE.md`, процесс — скилл `game-project-workflow`.

## Суть
- Жанр / референс: _заполнить после анализа_
- Режим и стек: _A PlayCanvas / B TypeScript+Three.js / C 2D PixiJS / D существующий_ — _версии_
- Текущий этап: _изучение / согласование / АРТ (Blender) / MVP-сцена / масштабирование_
- Порядок: сначала визуал (карта, локация, стиль, модели в Blender, скилл `game-art-first`), потом логика MVP, потом UI/локации.

## Команды
- `npm run dev` — запуск (порт: _)
- `npm run build` — сборка
- `npx tsc --noEmit` — типы
- `npx playwright test` — тесты (если есть)

## Ограничения проекта
- Согласованный объём: см. `docs/GAME_DESIGN.md` → «Первый срез». Всё сверх — только после согласования.
- Плейсхолдеры помечаются `// PLACEHOLDER` и перечисляются в `docs/PROJECT_STATE.md`.

## Где что лежит
- Состояние и следующий шаг: `docs/PROJECT_STATE.md` (читать первым)
- Решения: `docs/DECISIONS.md` · Задачи: `docs/TASKS.md` · Архитектура: `docs/ARCHITECTURE.md`
- Мастер-план и шаги: `docs/plans/CURRENT.md` → план · Референсы и ресурсы: `docs/REFERENCES.md`, `references/`
- Ассеты: `public/assets/` · Blender-исходники: `assets/source/` · Спека: `docs/spec/`
