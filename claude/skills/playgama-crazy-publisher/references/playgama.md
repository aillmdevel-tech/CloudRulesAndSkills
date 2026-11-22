# Playgama: кабинет и требования

Проверено на Snack Toss Zoo 2026-11-22. Форма меняется: сверяй с тем, что видишь, и с документацией Playgama.

Кабинет: https://developer.playgama.com · вход делает Alex. У него несколько аккаунтов: перед работой проверь, в каком лежит черновик этой игры (`PROJECT_STATE`).

## Поля
- Название как `<title>`, языки **только те, что реально есть в игре**, движок, инструмент, категория, устройства Desktop/iOS/Android, ориентации.
- **Builds:** zip, `index.html` в корне, первым скриптом `playgama-bridge.js`, рядом `playgama-bridge-config.json`, имена файлов латиницей.
- **Cover Images (обязательно):** 1:1 800×800, 9:16 1080×1920, 16:9 1920×1080.
- **Trailer, Gameplay Videos:** по желанию, но Alex хочет те же ролики, что на CrazyGames.
- **Other Assets (скриншоты):** необязательно. Достаточно 4–5 на ориентацию, не грузи 16 штук.
- **Distribution:** партнёров не выбирают, а **исключают**. На Snack Toss Zoo было исключено 14 из 16. Покажи Alex текущий список и спроси решение. На CrazyGames Playgama не публикует, туда отдельная заливка.
- **Continue → Sandbox / Send for Review:** только по «да» Alex.

## Сборка и SDK
- Bridge локально, без CDN. `initialize` до игры, `game_ready` после загрузки мира, `gameplay_started/stopped`.
- Язык из `bridge.platform.language`, звук из `isAudioEnabled` + `AUDIO_STATE_CHANGED`, пауза на рекламу и `PAUSE_STATE_CHANGED`.
- Сохранения только через `bridge.storage`.
- Interstitial в логических паузах, rewarded с наградой только после `rewarded`, баннер не закрывает кнопки.

## Проверка
- QA Tool: https://developer.playgama.com/qa-tool. Он **не грузит localhost** (Chrome Local Network Access): нужен публичный URL или ручная проверка Alex.
- Ручное за Alex: interstitial, rewarded, баннер, пауза и звук, живой телефон.

## Заливка через Chrome (лимит file_upload ≈ 10 МБ)
`pub prep-upload --platform playgama` режет zip на части ≤ 9 МБ и пишет sha256.
1. Загрузи части во вспомогательные input на странице.
2. Склей: `new File([a, b, ...], имя, {type:'application/zip'})`.
3. Положи через DataTransfer в основной `input[type=file]`, вызови `change`.
4. Сохрани, перезагрузи страницу, проверь имя и размер билда.
