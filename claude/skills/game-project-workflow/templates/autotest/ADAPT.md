# Автопроверки: как адаптировать под новый проект

Универсально без правок: `lib/spy.js` (перехват Playgama Bridge, эмуляция рекламы), `moderator/run.py`, `moderator/rules/*.json`, серверная/браузерная часть `lib/harness.py` (build, Server, Session).
Править под игру: `lib/harness.py` → `Session.STATE/prep/tp/fall/click_hud/callouts` (всё через `window.__game`); `smoke.py` (шаги сценария); `moderator/probes.py` и `checks.py` — места с `window.__game.*` (sfx.context, econ.level, player.pos).

## Контракт игры (минимум)
`window.__game` (есть и в проде): `player` (pos, state), прогресс (уровень/XP), `sfx.context()` (AudioContext), способ телепорта и вызова смерти. Без него сначала добавить.
Playgama Bridge в игре — для проб модератора про рекламу/паузу/сохранение; если площадка другая — править `spy.js` и пробы `ads/pause/persist`.

## Установка
cp -r lib moderator → `<проект>/tools/`; `examples/smoke.spiderarm.py` → `tools/smoke.py` (эталон шагов); `pip install playwright && playwright install chromium`; скрипты в package.json (см. SKILL game-autotest).

## Эталон
SpiderArm: `examples/TESTING.spiderarm.md` (описание), `examples/smoke.spiderarm.py`. Площадки: playgama.json (номера из официальных Game Requirements), crazygames.json; Яндекс — добавить `yandex.json` того же формата.
