---
name: game-autotest
description: Use when the user asks to check/test a browser game with the factory's automatic checks — "проверь игру модератором", "проверь нашим модератором", "модератор Playgama/CrazyGames/Яндекс", "можно отправлять на площадку?", "прогони смоук", "проверь что игра работает", "настрой автопроверки/смоук/модератор для проекта" — and ALSO on your own: run smoke after every finished change plan/stage before saying «готово» in any game project that has tools/smoke.py. Calls the project's npm scripts, reads the short result, reports to the user; sets up smoke+moderator from GameFactory templates in a project that lacks them.
---

# Автопроверки игры: смоук + модератор (любой проект)

Шаблон и эталон: `/Users/mac/Downloads/WebAIGames/Rules/GameFactory/templates/autotest/` (читай `ADAPT.md` там только при настройке/правке). Эталонная реализация — SpiderArm (`tools/smoke.py`, `tools/lib/`, `tools/moderator/`, `docs/TESTING.md`).

## Что это
- **Смоук** `npm run smoke` — «игра вообще работает?» (~30–60 с, PASS/FAIL, exit 0/1, скриншоты `tools/out/smoke/`). Визуал не оценивает.
- **Модератор** `npm run moderate -- --platform <имя>` — «пройдём модерацию площадки?». Правила `tools/moderator/rules/<площадка>.json`, живой отчёт `docs/moderation/REPORT.md`, вердикт «можно / нельзя отправлять», exit 0/1.

## Когда звать САМ (без просьбы)
- Смоук: после каждого плана/этапа правок кода игры, до слова «готово». Не после правок только документов/конфигов. Не в процессе мелких итераций — один раз в конце.
- Модератор: только когда Alex просит или явно готовится отправка на площадку («залей на Playgama», «отправляем»). Площадку называет Alex; не назвал — спроси одним вопросом (или возьми из PROJECT_STATE, если там указана целевая).

## Как вызывать
1. В корне проекта есть `tools/smoke.py` и `package.json` со скриптами `smoke`/`moderate`? Нет → «Настройка» ниже.
2. Запусти `npm run smoke` (или `npm run moderate -- --platform X`) **в фоне** (`run_in_background`), по завершении читай только итог: строки ✓/✗ и PASS/FAIL; для модератора — раздел «Вердикт» и «Замечания» из `docs/moderation/REPORT.md` (не весь файл). Не читай лог целиком.
3. Флаги: `--no-build` если сборка только что делалась; `--dev` — vite dev вместо prod; `--url` — уже запущенная игра. Порт/сервер скрипт поднимает и гасит сам; браузер Chrome headless=False.
4. Отчёт Alex по-русски, кратко: вердикт; список ✗ «правило → причина → файл для исправления» (поле `fix`); что только «вручную» (👀) — одной строкой. Если ✗ — предложи исправление, чини в рамках согласованного (для смоука — сразу, для модератора — после «ок», если правка меняет вид/геймплей), затем перезапусти ровно проваленное (smoke целиком, модератор целиком).
5. Не заявляй «прошло», если не запускал или упала сама проба (⏳ = не проверено, а не ✓).

## Настройка в проекте без автопроверок
1. Убедись, что у игры есть прод-сборка (`npm run build` → `dist/`, vite) и dev-хэндл `window.__game` (доступен и в проде) с игроком/состоянием; нет — добавь минимальный (читаемое состояние + несколько команд: телепорт/старт/сброс).
2. Скопируй из шаблона: `lib/` → `tools/lib/`, `moderator/` → `tools/moderator/`, `examples/smoke.spiderarm.py` → `tools/smoke.py` (как заготовку). `pip install playwright` + `playwright install chromium` при отсутствии.
3. Перепиши под проект: `STATE`/`prep`/`tp`/`fall`/`click_hud` в `harness.py`, шаги в `smoke.py` (загрузка → ключевой путь цикла игры → смерть/рестарт → звук → консоль чистая), пробы/проверки в `probes.py`/`checks.py`, которые завязаны на `window.__game`. Правила площадок (`rules/*.json`) переносятся как есть; новую площадку — новым JSON по официальным требованиям (номера не выдумывать; источник в поле `source`).
4. `package.json`: `"smoke": "python3 tools/smoke.py"`, `"moderate": "python3 tools/moderator/run.py"`. `tools/out/` и `docs/moderation/` — в `.gitignore` по желанию (отчёт можно коммитить).
5. В `CLAUDE.md` проекта одна строка: `smoke после каждого плана · модератор по просьбе: npm run moderate -- --platform X → docs/moderation/REPORT.md`. Запусти, добейся PASS, покажи Alex результат.

## Поддержка
Новая механика/экран в игре → доп. шаг в `smoke.py`, но только если это ключевой путь. Смоук держать ≤ ~100 строк и ≤ ~1 мин. Изменились требования площадки → обновить `rules/*.json`. Улучшил шаблон в проекте → перенеси и в GameFactory `templates/autotest/` (скрипты универсальных частей).
