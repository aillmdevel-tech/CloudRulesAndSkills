# Восстановление GameFactory на новом компьютере

Локальные настройки Claude Code **не синхронизируются** между компьютерами сами. Переносится
папка GameFactory (с `backup/`), остальное ставится скриптом.

## 0. На старом компьютере

```bash
bash /Users/mac/Downloads/WebAIGames/Rules/GameFactory/scripts/backup.sh
```

Скопируй папку `GameFactory` (вместе с `backup/`, без `UIFX/node_modules`) на новый компьютер — флешка, облако, git-репозиторий.
В `backup/` нет ключей, паролей и токенов: только CLAUDE.md, собственные скиллы, пропатченный grill-me
и lock-файл сторонних скиллов; скрипт проверяет на похожие на секреты строки.

## 1. Базовые инструменты (macOS, через Homebrew)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```bash
brew install node git python ffmpeg yt-dlp
```

Опционально: `brew install --cask blender` (конвертация FBX→GLB, проверка моделей).
Claude Code — десктоп-приложение Claude (вкладка Code) или CLI по официальной инструкции:
https://code.claude.com/docs

Windows: Node.js, Git, Python с официальных сайтов, `winget install Gyan.FFmpeg yt-dlp.yt-dlp`;
`restore.sh` запускать в Git Bash или WSL.

## 2. Восстановление

Положи GameFactory так, чтобы игры жили рядом, например `~/WebAIGames/Rules/GameFactory`, и выполни:

```bash
bash ~/WebAIGames/Rules/GameFactory/scripts/restore.sh
```

Другая папка для игр: `--games-dir /путь/к/играм`. Скрипт:
1. ставит `~/.claude/CLAUDE.md` (старый сохраняет как `.bak.*`), подставляя новые пути;
2. устанавливает сторонние скиллы официальным CLI (список — THIRD_PARTY_SKILLS.md);
3. копирует 5 собственных скиллов и пропатченный grill-me (пути внутри скиллов подставляются заново);
4. ставит Python Playwright + Chromium (нужно для `webapp-testing` и `capture.py`);
5. ставит зависимости демо UIFX (`npm install` внутри `GameFactory/UIFX`), сами звуки уже лежат в папке.

## 3. Проверка

```bash
ls ~/.claude/skills
```

Ожидается 26 папок: 16 PlayCanvas, frontend-design, webapp-testing, grill-me, grilling,
frontend-visual-qa и 5 собственных (game-*, levelcopier-asset-pipeline).

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('playwright ok')"
```

```bash
ffmpeg -version | head -1
```

Затем **новая** сессия Claude Code в папке игр:
- спроси «Какие у тебя правила и скиллы для разработки игр?» — должен ответить по-русски, назвать
  процесс GameFactory и маршрутизацию скиллов (значит CLAUDE.md загружен);
- в CLI можно набрать `/memory` (видно `~/.claude/CLAUDE.md`) и `/context` (видны скиллы);
- напиши «Хочу сделать игру, вот ТЗ: …» — Claude должен сам вызвать `game-project-workflow`.

## LevelCopier

Не входит в GameFactory — это отдельный инструмент Alex. Перенеси его вручную и сообщи Claude путь
(можно добавить строку «- LevelCopier: `<путь>`» в раздел «Пути» `~/.claude/CLAUDE.md`).
