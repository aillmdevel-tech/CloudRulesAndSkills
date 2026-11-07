# BOOTSTRAP — инструкция для Claude на новом устройстве

> Claude: Alex дал тебе этот репозиторий, чтобы ты развернул его настройку у себя. Выполни шаги по порядку,
> отвечай по-русски и кратко. Не выдумывай результаты: что не получилось — так и скажи.

## 0. Что это
Сначала прочитай `docs/SYSTEM_MAP.md` — там полная схема того, что настроено и как работает.

Полная настройка Claude Code для разработки браузерных игр (GameFactory): глобальные правила
(`claude/CLAUDE.md`), собственные скиллы (`claude/skills/`), хуки контроля контекста (`claude/hooks/`,
`claude/settings.json`), список сторонних скиллов (`third-party/`), MCP (`mcp/MCP.md`), процесс и шаблоны
(`GameFactory/`), библиотека UI-анимаций и звуков (`GameFactory/UIFX/`).

## 1. Клонировать
Если репо ещё не на диске — склонируй (он приватный, нужен аккаунт **aillmdevel-tech** в `gh`):
```bash
gh auth status            # нет aillmdevel-tech → gh auth login --web (Alex подтверждает код в браузере)
gh repo clone aillmdevel-tech/CloudRulesAndSkills ~/WebAIGames/Rules/CloudRulesAndSkills
```
Спроси Alex один раз, где держать игры (по умолчанию `~/WebAIGames`). Клон лучше положить в `<игры>/Rules/`.

## 2. Проверить и доставить инструменты
Проверь: `node`, `npm`, `git`, `gh`, `python3`, `ffmpeg`/`ffprobe`, `yt-dlp`, `uv`; опционально `blender`.
Отсутствующие ставь официальным способом для ОС (macOS: Homebrew — `brew install node gh python ffmpeg yt-dlp uv`,
`brew install --cask blender`). Права администратора — только с согласия Alex.

## 3. Развернуть
```bash
bash <клон>/scripts/install.sh --games-dir <папка игр>        # + --with-blender-mcp, если нужен Blender MCP
```
Скрипт: ставит `~/.claude/CLAUDE.md` с путями этой машины (старый → `.bak`), сливает `settings.json`
(хуки + outputStyle, чужие настройки не трогает), копирует хуки и свои скиллы, ставит сторонние скиллы
официальным `npx skills`, Python Playwright + Chromium, зависимости демо UIFX.
Если что-то упало — исправь причину и перезапусти (скрипт идемпотентный).

## 4. Проверить
- `ls ~/.claude/skills` → 16 PlayCanvas + frontend-design, webapp-testing, grilling, grill-me, frontend-visual-qa + свои
  (chat-handoff, game-autotest, game-project-workflow, game-reference-analysis, game-ui-motion-sound, game-visual-comparison,
  github-account-router, levelcopier-asset-pipeline).
- `echo '{"cwd":"/tmp"}' | python3 ~/.claude/hooks/context_guard.py start` — без ошибок.
- `python3 -c "from playwright.sync_api import sync_playwright"`.
- Скажи Alex: открыть **новый чат** (правила, скиллы и хуки загружаются при старте сессии) и спросить
  «какие у тебя правила?» — ответ по-русски с описанием GameFactory = всё работает.

## 5. Дальше (обновления)
- Изменения пришли из репо: `git -C <клон> pull && bash <клон>/scripts/install.sh --skip-playwright`.
- Изменили правила/скиллы на этой машине: `bash <клон>/scripts/sync.sh --commit "что изменилось" && git -C <клон> push`
  (правило уже есть в CLAUDE.md — Claude делает это сам).

## Чего нет в репо (и не должно быть)
Токены, пароли, ключи API, логины `gh`, история чатов, `node_modules`. LevelCopier — отдельный приватный репо
`aillmdevel-tech/LevelCopier`, ставится по запросу.
