# Уроки: SDK площадок, реклама, модерация

### 2026-11 · SpiderArm · замечания модератора Playgama/CrazyGames
- Симптом: ✗ по версии Bridge, title и подключению CrazyGames.
- Причина: старый Playgama Bridge, title по умолчанию, CrazyGames не через Bridge.
- Фикс: Bridge 2.4.4, свой title, CrazyGames через Bridge.
- Правило: перед модерацией — актуальная версия Bridge, title игры, площадки через Bridge (`playgama-crazy-publisher`, этап SDK).
- Проверка: модератор `game-autotest` по обеим площадкам.

### 2026-11 · DO NOT STOP · звук при скрытой вкладке
- Симптом: игра играет звук в фоне вкладки (нарушение правил площадок).
- Причина: не было обработки `visibilitychange`.
- Фикс: пауза и тишина при скрытой вкладке.
- Правило: в каждой игре `visibilitychange` → пауза + mute; то же на рекламе.
- Проверка: проба модератора `pause`.
