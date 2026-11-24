# SYSTEM_MAP — схема настройки Claude Code Alex (GameFactory)

> Для агента: прочитай первым, он заменяет брифинг. Для Alex: карта того, что есть и где лежит.
> Обновлено: 2026-11-20. Репо: `aillmdevel-tech/CloudRulesAndSkills` (приватный).

## 1. Слои

| Слой | На машине | В репо |
|---|---|---|
| Глобальные правила | `~/.claude/CLAUDE.md` | `claude/CLAUDE.md` |
| Настройки + хуки (контекст, memory-bank) | `~/.claude/settings.json`, `~/.claude/hooks/` | `claude/settings.json`, `claude/hooks/` |
| Свои скиллы | `~/.claude/skills/` | `claude/skills/` |
| Сторонние скиллы | `~/.claude/skills/` (`npx skills`), PlayCanvas — в `~/.claude/spares/playcanvas` | `third-party/` (lock + скрипт), `claude/spares/playcanvas.list` |
| Утилиты | `~/.local/bin/` | `tools/bin/` (+ `resource-run` создаёт install) |
| MCP | `~/.claude.json` | `mcp/MCP.md`, `mcp/servers.json`, `mcp/blender/` (аддон) |
| GameFactory | `<игры>/Rules/GameFactory` | `GameFactory/` |
| Перенос | — | `BOOTSTRAP.md`, `scripts/install.sh`, `scripts/sync.sh` |

## 2. Алгоритм разработки игры
Единственное описание — `GameFactory/WORKFLOW.md` (машинная версия — скилл `game-project-workflow`). Один чат на проект.

0 Стиль (StyleLibrary) → 1 Материалы в `input/` → 2 Разбор без кода (`docs/spec/`, [видно]/[из ТЗ]/[пробел]) → 3 Вопросы только по пробелам (код после всех ответов) → 4 Steam-стиль + бюджет → 5 Готовое (CC0-ассеты, GitHub, `docs/REFERENCES.md`) → 6 Мастер-план всей игры (`docs/plans/…-master.md`) → 7 MVP-сцена: проверки A (кадр стиля, Blender), B (геймфил), C (готовая сцена) → 8 Расширение до конца (перед отправкой: модератор + `game-promo-kit`).

Цикл каждого пакета: код → tsc + сборка → смоук → «референс | игра» → правки → коммит → PROJECT_STATE + memory-bank. Модель и уровень мышления выбирает Alex.

## 3. Скиллы

**Свои:**
| Скилл | Что |
|---|---|
| `game-project-workflow` | алгоритм выше, `new_project.sh`, PROJECT_STATE/DECISIONS |
| `game-art-first` | Steam-доска, поиск готового, Blender, проверка A |
| `game-reference-analysis` | видео/скрины → кадры, листы, `docs/spec/` |
| `game-visual-comparison` | снимки игры vs референс, diff, правки |
| `game-ui-motion-sound` | UI-анимации и звуки из UIFX |
| `game-autotest` | смоук и модератор площадок |
| `game-promo-kit` | жанр игры → 3–5 рефов из PromoLibrary (11 жанров Roblox, разбивки по секундам, паттерны) и бриф; захват геймплея, авто-поиск сочных моментов, монтаж по правилам площадок, скриншоты, обложки, локализация. На новой машине работает по тексту библиотеки, видео не обязательны |
| `playgama-crazy-publisher` | аудит → SDK (Playgama Bridge / CrazyGames SDK v3, реклама и IAP по правилам площадки и статусу запуска, загрузочный экран с прогрессом) → локализация → промо и модератор во вложенных сессиях → черновики кабинетов → отправка только по «да» |
| `diagnosing-bugs`, `retro`, `writing-for-agents` | трудные баги; ретро сессии; правка скиллов и CLAUDE.md |
| `character-animation` | риг, анимации, герой Alex |
| `levelcopier-asset-pipeline` | импорт дампов LevelCopier |
| `chat-handoff`, `save-context` | «упакуй контекст» / «продолжи работу», memory-bank |
| `github-account-router` | нужный аккаунт gh на репо, глобальный не трогает |
| `threejs-debug-profiler`, `threejs-aaa-graphics-builder` | адаптированные копии majidmanzarpour/threejs-game-skills: баги/лаги/бюджет; графика и пост после A (без платных генераторов) |

**Сторонние (`npx skills`, версии в `third-party/skill-lock.json`):** frontend-design, webapp-testing (anthropics), grilling (mattpocock), frontend-visual-qa (daymade), PlayCanvas ×16 — выключены, `playcanvas-skills on|off`.

## 4. MCP
| Сервер | Зачем | Установка |
|---|---|---|
| blender | живой Blender: bpy, `look`, ассеты Poly Haven/Sketchfab/Poly Pizza, `generate_3d` | `install.sh --with-mcp` (сервер + аддон в Blender) |
| afk-rig | авториг моделей (человек, паук, змея…), анимации; платно сверх бесплатных | `install.sh --with-mcp` |
| playgama-developer-cabinet | кабинет Playgama (проектный, SpiderArm) | вручную в папке игры, см. `mcp/MCP.md` |

Встроенные в Claude Desktop (браузер, Chrome, артефакты, docs, терминал) ставятся с приложением. По правилам MCP включаются только под задачу.

## 5. Утилиты (`~/.local/bin`)
- `resource-run` / `resource-status` — на исходном Mac лимитирует нагрузку Python/Node; на новой машине install ставит прозрачную заглушку.
- `playcanvas-skills on|off|status` — включить/выключить PlayCanvas-скиллы.
- `claude-profiles` — несколько аккаунтов Claude в одном Claude Desktop (macOS).
- CLI: node/npm, git, gh, python3, ffmpeg/ffprobe, yt-dlp, uv/uvx, Blender 5.2; Python Playwright + Chromium, Pillow.

## 6. GameFactory
`WORKFLOW.md` (алгоритм), `THREEJS_STACK.md` (three 0.187, postprocessing, N8AO, three.quarks, GSAP, Rapier), `StyleLibrary/` (вкус Alex + жанры), `UIFX/` (32 эффекта, 43 звука CC0, 5 стилей), `templates/` (CLAUDE проекта, docs, автотесты), `TOKEN_SAVING.md`, `THIRD_PARTY_SKILLS.md`.

## 7. Перенос
- Забрать изменения с машины: `scripts/sync.sh --commit "что"` → `git push` (аккаунт aillmdevel-tech привязан к клону). sync проверяет секреты и прерывается.
- Развернуть: по `BOOTSTRAP.md` → `scripts/install.sh --games-dir <папка> --with-mcp`. Идемпотентен.
- Не переносится: токены, ключи, логины gh/afk.ai/Playgama, история чатов, `node_modules`, сами игры (у каждой свой репо), LevelCopier (отдельный репо `aillmdevel-tech/LevelCopier`).

## 8. Ограничения
- Полная установка на втором реальном устройстве не проверялась.
- Хуки и правила загружаются с нового чата.
- Модератор: Playgama, CrazyGames; Яндекс — по запросу.
