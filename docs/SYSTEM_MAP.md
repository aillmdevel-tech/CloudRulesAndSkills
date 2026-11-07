# SYSTEM_MAP — полная схема настройки Claude Code Alex (GameFactory)

> Для агента: прочитай этот файл первым — он заменяет повторный брифинг. Для Alex: это карта того, что у тебя есть и где лежит.
> Обновлено: 2026-11-07. Репо: `aillmdevel-tech/CloudRulesAndSkills` (приватный).

## 1. Кто такой Alex и что строим
Разработчик браузерных 3D-игр (вдохновение: Roblox, Steam, инди). Общение — по-русски, на «ты», кратко, по делу.
Агент ничего не выдумывает: не запускал — так и говорит. Скиллы Alex сам не называет — агент выбирает их по смыслу задачи.

## 2. Слои системы (что где живёт)

| Слой | Живая копия на машине | В репо | Что делает |
|---|---|---|---|
| Глобальные правила | `~/.claude/CLAUDE.md` | `claude/CLAUDE.md` | Грузятся в каждой сессии: язык, процесс, автовыбор скиллов, стек, проверка, экономия, handoff, «опусплан», формат ответов |
| Настройки + хуки | `~/.claude/settings.json`, `~/.claude/hooks/context_guard.py` | `claude/settings.json`, `claude/hooks/` | Хук контроля контекста + `outputStyle: Concise` |
| Свои скиллы (8 + пропатченный grill-me) | `~/.claude/skills/` | `claude/skills/` | Процесс игры, анализ референсов, LevelCopier, визуальное сравнение, UI-анимации/звуки, автотесты, handoff, GitHub-аккаунты, grill-me |
| Сторонние скиллы (21) | `~/.claude/skills/` (ставит `npx skills`) | `third-party/` (lock + скрипт) | PlayCanvas ×16, frontend-design, webapp-testing, grilling, frontend-visual-qa, grill-me |
| GameFactory | `/Users/mac/Downloads/WebAIGames/Rules/GameFactory` | `GameFactory/` | Процесс, шаблоны документов, шаблоны автотестов, UIFX, токен-экономия |
| MCP | через `claude mcp` | `mcp/MCP.md` | Blender MCP (остальное встроено в Claude Desktop) |
| Перенос | — | `BOOTSTRAP.md`, `scripts/install.sh`, `scripts/sync.sh` | Развернуть на новом устройстве / забрать изменения в репо |

## 3. Глобальные правила (`CLAUDE.md`) — суть
1. **Общение:** русский, «ты», кратко; не выдумывать состояние машины и результаты проверок.
2. **Пути:** GameFactory, папка игр (каждая игра — подпапка со своим `CLAUDE.md`), UIFX, клон облачной копии.
3. **Облачная копия:** после любого изменения правил/скиллов/хуков/GameFactory → `scripts/sync.sh --commit "<что>"` в клоне → `git push` (через `github-account-router`) → одной строкой сказать Alex.
4. **Автовыбор скиллов** (таблица маршрутизации — см. §4).
5. **Стек по словам ТЗ:** «PlayCanvas» → локальный Engine (Direct API) + TS + Vite + npm; «TS без движка»/Three.js → TS + Vite + three (+ Rapier); 2D → PixiJS/Canvas; готовый репо → его стек. Без React/Next/Unity и лишних библиотек. Зависимости — в проекте.
6. **Процесс:** изучение → вопросы → согласование → вертикальный срез → тесты → итерации. До согласования — никакой масштабной реализации; строго в согласованном объёме; реальные модели Alex не заменять примитивами.
7. **Проверка перед «готово»:** tsc, сборка, запуск, консоль, управление, логика, коллизии, камера, UI, скриншот vs референс. Не утверждать про тесты, которые не запускались.
8. **Контекст и экономия:** см. §6.
9. **Передача между чатами:** см. §7.
10. **«Опусплан» вручную:** см. §8.
11. **Формат ответов:** всегда по-русски, кратко, без вступлений и заключений; подробно — только по запросу; субагентам передавать эти правила; качество проверок не урезать.

## 4. Автовыбор скиллов (маршрутизация)

| Запрос | Скиллы |
|---|---|
| Новая игра / ТЗ / прототип / «не определился с механикой» | `game-project-workflow` (+ `grilling` при серьёзной неопределённости, раунды ≤5 вопросов) |
| Видео, скриншоты, «повтори механику» | `game-reference-analysis` |
| LevelCopier, GLB+JSON, «восстанови сцену» | `levelcopier-asset-pipeline` (+ PlayCanvas `inspect-glb`/`load-assets`/`calibrate-model`/`assemble-scene`) |
| «Похоже на скриншот», «проверь визуал» | `game-visual-comparison`; вёрстка UI → + `frontend-visual-qa`; новый UI → + `frontend-design` |
| Проверка игры в браузере | `webapp-testing` (Python Playwright) или встроенный браузер |
| Любой игровой UI (HUD, меню, магазин, награды, кнопки) | всегда `game-ui-motion-sound` (UIFX) |
| PlayCanvas-проект | только подходящие официальные PlayCanvas-скиллы (в Three.js — не применять) |
| «Проверь модератором/смоуком», «можно на площадку?», конец плана правок кода | `game-autotest` (смоук сам после каждого плана; модератор — по просьбе) |
| Любая работа с GitHub-репо | `github-account-router` |
| «Перехожу в новый чат», «продолжи работу» | `chat-handoff` |
| Мелкий баг | точечная диагностика без больших процессов |

## 5. Свои скиллы (8 + пропатченный grill-me)
| Скилл | Назначение |
|---|---|
| `game-project-workflow` | Главный процесс: ориентация → изучение → вопросы → согласование → срез → тесты → итерации; выбор стека; скрипт `new_project.sh` (скелет проекта, `CLAUDE.md`, шаблоны docs); `window.__game` debug-поверхность; ведёт `PROJECT_STATE.md`/`DECISIONS.md` |
| `game-reference-analysis` | Видео/скриншоты → кадры с таймкодами (FFmpeg `video_frames.py`: info/sample/scenes/burst/sheet) → `REFERENCE_ANALYSIS`, `VIDEO_STORYBOARD`, `GAMEPLAY_BREAKDOWN`, `ART_REFERENCE`; факты [факт] отдельно от [гипотез] |
| `levelcopier-asset-pipeline` | Дампы LevelCopier: `scan_assets.py`, схема JSON из реальных файлов, калибровка трансформов, `ASSET_MANIFEST.md`, импортёр; оригиналы read-only |
| `game-visual-comparison` | `capture.py` (Playwright-скриншот с `window.__game`) + `compare_images.py` (side-by-side, diff, blend, статистика) → таблица отличий по приоритету → фиксы → перепроверка |
| `game-ui-motion-sound` | Подбор анимаций и звуков UI из библиотеки UIFX по референсам, громкость, reduced motion, проверка в браузере |
| `game-autotest` | Смоук (`npm run smoke`, ~30–60 с) и модератор площадок (`npm run moderate -- --platform X`, вердикт «можно/нельзя отправлять»); запуск в фоне, читать только вердикт; настройка из шаблонов `GameFactory/templates/autotest/` |
| `chat-handoff` | Режим сохранения: пишет `docs/PROJECT_STATE.md` (правила, пути, команды, сделано, задача, следующий шаг); режим продолжения: читает его + git и сразу делает «Следующий шаг» |
| `github-account-router` | Несколько аккаунтов gh: `repo_account.sh check/setup/status` — привязывает репо к нужному аккаунту локально, глобальный не трогает |
| `grill-me` (пропатченный) | Только ручной вызов `/grill-me` — жёсткое интервью по идее |

## 6. Экономия токенов и лимитов (все уже автоматические)
| Механизм | Как реализован |
|---|---|
| Контроль контекста | Хук `context_guard.py prompt` (UserPromptSubmit): ≥150k — предупреждение, ≥200k или 2+ сжатия — обязательный handoff и новый чат. Пороги: env `CONTEXT_GUARD_WARN/HARD` |
| Напоминание при старте | Хук `context_guard.py start` (SessionStart: startup/resume/compact): если есть `docs/PROJECT_STATE.md` — прочитать его первым |
| Краткие ответы | `outputStyle: Concise` + правила формата в CLAUDE.md |
| Субагенты для тяжёлого чтения | Видео/кадры, поиск по коду, большие логи — субагенту, в чат только вывод |
| Фоновые команды, узкий вывод | Сборки/смоук/модератор — `run_in_background`, читать вердикт (tail/grep) |
| Точечное чтение | offset/limit, grep, Edit вместо перезаписи; не перечитывать проект ради мелочи |
| Короткие PROJECT_STATE / CLAUDE.md проекта | Их читает каждый новый чат; перезаписывать, не дописывать |
| Лишние MCP | Агент предупреждает Alex: «отключи MCP X» (описания инструментов съедают контекст) |
| Диагностика расхода | «Куда ушли токены» → скилл `explain-usage` |
| Один тип работы — одна сессия | Параллельно в одной папке — только непересекающиеся задачи |
| Качество не режется | tsc/build/smoke/браузер не пропускаются ради экономии |

Подробно: `GameFactory/TOKEN_SAVING.md`, `docs/TOKEN_ECONOMY.md`.

## 7. Перенос контекста между чатами
1. Alex: «перехожу в новый чат» / «собери контекст» (или хук ≥150k/200k) → `chat-handoff` пишет `docs/PROJECT_STATE.md` в корне проекта.
2. В Claude Desktop агент предлагает карточку новой сессии в той же папке с брифом «продолжи работу»; в CLI — просит открыть новый чат и написать «продолжи работу».
3. Новый чат: «продолжи работу» → читает PROJECT_STATE + `git status/log` → сразу «Следующий шаг», без повторного брифинга.
4. `/compact` для преемственности не использовать — резюме теряет детали.

## 8. «Опусплан» вручную (план для Sonnet)
- Триггеры: «составь план по опусплан», «составь план для выполнения сонет». Код не менять — только изучить и записать план.
- Файл: `docs/plans/YYYY-MM-DD-<коротко>.md` в корне игры; в `docs/plans/CURRENT.md` — строка-ссылка на актуальный план.
- Содержание: цель и критерий «готово»; контекст (стек, ключевые файлы, правила, что не трогать); шаги «файл → функция → точечное изменение» с чекбоксами `- [ ]`; риски; проверка. План самодостаточен — исполнитель не видит чат.
- В ответе: путь к плану и фраза «Выполни план».
- Исполнитель: «Выполни план» → `CURRENT.md` → шаги строго по порядку; не сходится с кодом — остановиться и спросить; отмечать `- [x]`; в конце проверка из плана + обновить PROJECT_STATE.
- Идея: дорогая модель думает один раз, дешёвая исполняет по готовому плану.

## 9. GameFactory (`GameFactory/`)
| Файл/папка | Что |
|---|---|
| `README.md`, `WORKFLOW.md` | Карта и процесс для человека |
| `SETUP_NEW_PC.md`, `scripts/backup.sh`, `scripts/restore.sh`, `backup/` | Старый механизм переноса (дублируется облачным репо) |
| `THIRD_PARTY_SKILLS.md` | Список сторонних скиллов и источников |
| `TOKEN_SAVING.md` | Правила экономии |
| `templates/CLAUDE.project.md`, `templates/docs/*` | Шаблоны `CLAUDE.md` проекта и 11 документов (PROJECT_STATE, DECISIONS, TASKS, GAME_DESIGN, ARCHITECTURE, REFERENCE_ANALYSIS, VIDEO_STORYBOARD, GAMEPLAY_BREAKDOWN, ART_REFERENCE, ART_SPEC, ASSET_MANIFEST) |
| `templates/autotest/` | `lib/` (harness.py, spy.js), `moderator/` (run.py, probes, checks, `rules/*.json` — Playgama, CrazyGames; Яндекс — добавить), `examples/` (SpiderArm), `ADAPT.md` |
| `UIFX/` | Библиотека UI: 32 эффекта на пружинах, 43 звука CC0, 5 стилей (Roblox Cartoon, Playful Jelly, Casual Soft, Arcade, Clean Modern), TS без зависимостей, демо `npm run demo` (порт 5199), `tools/install_uifx.py` ставит в игру |

Структура проекта игры (создаёт `new_project.sh`): `CLAUDE.md` + `docs/` (PROJECT_STATE первым), `references/`, `imports/levelcopier/`, `public/assets/`, `tools/` (smoke, moderator).

## 10. Сторонние скиллы (21 в lock, включая grill-me; ставятся из официальных репо)
- PlayCanvas ×16: add-effects, apply-conventions, assemble-scene, bake-lighting, build-app, calibrate-model, configure-animation, find-examples, inspect-glb, inspect-runtime, light-scene, load-assets, override-shader-chunks, reduce-draw-calls, reuse-scripts, verify-pixels.
- Прочие: frontend-design, webapp-testing, grilling, frontend-visual-qa, grill-me (пропатченный, свой).
- Версии зафиксированы в `third-party/skill-lock.json`; ставит `third-party/install_third_party.sh` (через `npx skills`).

## 11. MCP и инструменты
- **Blender MCP** (`uvx blender-mcp` + аддон в Blender): живой Blender — bpy, `look`, поиск/импорт ассетов (Poly Haven, Sketchfab), `generate_3d`. Ставит `install.sh --with-blender-mcp`. Подробно — `mcp/MCP.md`.
- Встроенные в Claude Desktop (переносить не нужно): браузер, Claude in Chrome, артефакты, docs, терминал, сессии.
- CLI-инструменты: node/npm, git, gh, python3, ffmpeg/ffprobe, yt-dlp, uv; опционально blender; Python Playwright + Chromium.

## 12. Как работает перенос (облако)
- `scripts/sync.sh [--commit "msg"]` — копирует живую настройку в репо (правила, settings, hooks, свои скиллы, GameFactory), сканирует на секреты и прерывается при находке; затем `git push` (аккаунт `aillmdevel-tech` привязан к клону локально).
- `scripts/install.sh [--games-dir DIR] [--with-blender-mcp]` — разворачивает на новой машине: правила с переписанными путями (старый → `.bak`), слияние `settings.json`, хуки, свои скиллы, сторонние через `npx skills`, Playwright, зависимости UIFX. Идемпотентен.
- Секретов в репо нет: токены, пароли, ключи API, логины `gh`, история чатов, `node_modules` не копируются. LevelCopier — отдельный приватный репо `aillmdevel-tech/LevelCopier`.

## 13. Новое устройство / другой аккаунт — что сказать
В Claude Code напиши:
> Разверни мою настройку из репозитория https://github.com/aillmdevel-tech/CloudRulesAndSkills — следуй BOOTSTRAP.md

Нужен аккаунт `aillmdevel-tech` в `gh` (`gh auth login --web`, код подтверждаешь сам). После установки открой **новый чат** (правила, скиллы и хуки читаются при старте) и спроси «какие у тебя правила?» — ответ по-русски с описанием GameFactory = всё работает. Дальше: «продолжи работу» в папке игры.

## 14. Известные ограничения
- Полный install на реальном втором устройстве не проверялся (только песочница с фейковым HOME).
- Хуки в Claude Desktop срабатывают с новой сессии.
- Правила площадок для модератора — Playgama, CrazyGames; Яндекс добавляется по запросу.
- Аддон Blender ставится вручную.
