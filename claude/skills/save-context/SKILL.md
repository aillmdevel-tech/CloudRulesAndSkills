---
name: save-context
description: Use when the user types /save-context or says "сохрани контекст", "обнови memory bank", "сохрани состояние проекта", or after a big finished step. Refreshes the four files in .claude/memory-bank/ (projectbrief, activeContext, progress, techContext) from the real project state so a new chat or another account can continue exactly where work stopped.
---

# save-context

Обновляет `.claude/memory-bank/` в корне текущего проекта по фактам. Работает в любом проекте; если папки нет, создаёт.

## Шаги
1. Корень проекта: ближайшая папка с `.git` / `package.json` / `docs/PROJECT_STATE.md`. Не scratch-папка и не `~`.
2. Собери факты, не выдумывай: `docs/PROJECT_STATE.md`, `CLAUDE.md`, `git status --short`, `git log --oneline -10`, `package.json`, планы в `docs/plans/` (CURRENT.md), результаты последних проверок (tsc, сборка, смоук) из этой сессии.
3. Перезапиши (не дописывай) файлы, каждый ≤ ~80 строк:
   - `projectbrief.md` — что за игра/проект, главная цель, платформы, принятый объём, что вне объёма.
   - `activeContext.md` — дата; текущая задача; что сделано в последних сессиях; незакоммиченное; блокеры и открытые вопросы к Alex; **следующий шаг** (конкретный, с файлом/командой).
   - `progress.md` — чекбоксы `[x]` сделано / `[ ]` осталось по этапам, заглушки и известные пробелы, последний результат проверок.
   - `techContext.md` — стек и версии, движок, структура папок, команды (dev/build/test/smoke), ограничения (платформы, бюджеты, лицензии, приватные репозитории).
4. Не дублируй длинные тексты: ссылайся на `docs/PROJECT_STATE.md`, планы и спеки путями. Если `docs/PROJECT_STATE.md` есть, при расхождении правда там, и его тоже обнови.
5. Не трогай `session-log.md`: его пишет Stop-хук.
6. Ответь одной-двумя строками: что обновлено и каков следующий шаг. Ничего не коммить без просьбы.

## Автоматика (уже настроена глобально)
- SessionStart-хук подмешивает файлы Memory Bank в начало сессии.
- Stop-хук пишет автолог в `session-log.md` и один раз просит обновить `activeContext.md`, если код менялся позже него.
- Для нового проекта хук сам создаёт заготовки; первым делом выполни `/save-context`.
