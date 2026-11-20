---
name: game-promo-kit
description: Use when Alex asks for promo materials of a browser game — "сделай рекламное видео/ролик/трейлер", "промо", "нарежь сочные моменты", "видео для CrazyGames/Poki/Яндекса/Playgama", "превью-видео", "ролик для TikTok/Reels/Shorts", "скриншоты для площадки", "обложка/иконка/кавер", "локализуй ролик/скрины на языки". Records real gameplay from the running game (Playwright: canvas + game audio + event log), finds the juiciest moments automatically, edits a dynamic cartoon montage (punch-zoom, flash cuts, slow-mo at the payoff, shake, pop-in localized texts, SFX, end card) or a clean platform preview, in the exact size/length/audio rules of each platform, plus sharp screenshots and covers per platform and language.
---

# Промо-набор: ролики, скриншоты, обложки

Скрипты: `~/.claude/skills/game-promo-kit/scripts/` (запуск через обёртку `promo`, она сама находит Python с Playwright и Pillow; на этом Mac — через `~/.local/bin/resource-run`).
Требования площадок: `references/platforms.json` (поле `verified` — когда сверено с официальной страницей). Стиль монтажа и локализация: `references/editing-style.md`.

## Правила
- Только реальный геймплей нашей игры. ИИ-видео/генераторы — только по прямой просьбе Alex и только как вставка-крючок, не вместо игры (обманчивая реклама → отказ модерации).
- Размер, fps, длину, звук, текст бери из пресета площадки, не на глаз. Пресет `verified: unverified/guideline` → скажи Alex, что цифры сверить в форме загрузки.
- Звук и музыка: звуки игры, UIFX (CC0) или музыка, которую дал Alex. Чужую музыку не подставляй.
- Ничего не выгружай на площадки и в сервисы — файлы кладёшь в `promo/out/`, загружает Alex.
- Перед «готово» смотри результат: листы `promo/review/*.jpg` (Read) и `ffprobe`-итог из вывода. Финальный вкус — за Alex.

## Шаги
1. **Подготовка (один раз на игру).** `promo/config.json` из `templates/config.example.json`: название и тексты (hook, cta, captions по типам событий) на всех языках игры, шрифт с нужными алфавитами, цвета из ART_SPEC. В игру — `templates/promo-hooks.ts`: `promoEvent(type, weight, label)` в местах сочных событий (комбо, взрыв, крупная награда, босс, рекорд) и `installPromoDirector` (прячет HUD/курсор/dev-панели). Это маленькая правка кода — согласуй с Alex как обычный пакет, после неё смоук. Без хуков всё работает, но моменты ищутся только по движению и громкости.
2. **Сценарий захвата.** `promo/scenario.py` из `templates/scenario.example.py`: короткие проходы через лучшие места игры (через `window.__game` и клавиши), `api.event(...)` на пиках, `api.shot(name)` в красивых кадрах. Альтернатива — `--manual`: Alex играет сам в открытом окне, F9 или ` отмечает момент.
3. **Захват.** Отдельный дубль под каждый формат, игра рендерит его нативно (так нет обрезки и чёрных полос):
   ```bash
   ~/.local/bin/resource-run ~/.claude/skills/game-promo-kit/scripts/promo capture --project . --take land --size 1920x1080 --fps 60 --seconds 40
   ~/.local/bin/resource-run ~/.claude/skills/game-promo-kit/scripts/promo capture --project . --take vert --size 1080x1920 --no-build
   ```
   Сервер: по умолчанию `npm run build` + `vite preview`; `--serve dist` — готовая папка без node; `--url` — уже запущенная игра; `--init-js tools/lib/spy.js` — эмуляция SDK площадки, если игра без неё не стартует; `--ready "() => !!window.__game"` — когда игра готова.
   `--ui` — писать страницу целиком с DOM-HUD (иначе только canvas). `--dpr 2` — скриншоты крупнее. Итог: `promo/raw/<take>.mp4` + `.events.json`.
4. **Моменты.** `promo moments --project . [--take land] [--len 2.2]` → `promo/moments.json`, лист `promo/review/moments.jpg` (3 кадра на момент). Посмотри лист сам, выкинь скучное/битое (`--moments 1,4,2` в монтаже); при сомнении покажи лист Alex.
5. **Монтаж.** `promo edit --project . --platform <имя> [--video <пресет>] [--lang en,ru] [--moments …] [--music track.mp3] [--bpm 128]`.
   - Пресеты с `text: none` (CrazyGames, Poki) → `clean`: без текста, звука, ускорений; первый кадр — обложка (сначала `shots --covers`).
   - Рекламные (`ads_vertical`, `ads_square`, `ads_landscape`, Яндекс) → `cartoon`: крючок-текст в первые 2 с, панч-зум и вспышка на каждой склейке, слоумо + тряска на пике, подписи событий, финальная карточка «название + CTA», whoosh/pop из UIFX. По одному файлу на язык.
   - Вывод `promo/out/<платформа>/<язык|all>/<пресет>.mp4`; строка `FIX` = нарушение пресета (длина, размер, МБ) — исправь (больше моментов, `--duration`) до сдачи.
6. **Скриншоты и обложки.** `promo shots --project . --platform <имя> [--screens] [--covers] [--sizes 1920x1080,1080x1920] [--source promo/art/keyart.png] [--captions]`. Обложку лучше делать из key art: рендер сцены в Blender (`game-art-first`, Blender MCP) → `--source`. Текст на обложке — по правилу пресета (`none` / `title_only` / `title_localized`).
7. **Сдача.** Короткий отчёт: что лежит в `promo/out/`, длины/размеры, что сверить вручную (нечестные кадры, мелкий текст, чужие права, `unverified`-пресеты), и листы для просмотра.

## Площадки (кратко, детали в platforms.json)
- **CrazyGames:** обложки 1920×1080, 800×1200, 800×800 (только название); превью 1080p 16:9 и 2:3 (1080×1620), 15–20 с, ≤50 МБ, без звука, без текста/«Play now», без курсора, без чёрных полос и лого-заставки, первый кадр — обложка.
- **Poki:** квадрат ≥628 px без текста; анимированный 1080×1080, ≥50 fps, 4–6 с, 2–3 сцены, без звука, mp4 ≤100 МБ.
- **Яндекс (не сверено, страница была недоступна):** иконка 512×512, обложка 800×470 PNG; промо-видео вертикальное 9:16 и горизонтальное; все слова переведены на язык локализации; чужой геймплей и одинаковые промо в разных играх запрещены.
- **Playgama:** своих цифр нет, размеры — в форме developer.playgama.com; собирай квадрат/портрет/ландшафт.
- **Реклама (TikTok/Reels/Shorts, лента, YouTube):** не правила площадки, а практика: крючок ≤1,5 с, реальный геймплей, текст вне нижних ~22% и верхних ~12% в 9:16, финальная карточка.

## Если что-то не так
- `ffmpeg does not start` → `brew upgrade ffmpeg`. Тексты рисует Pillow и накладывает ffmpeg `overlay`, libass/drawtext не нужны.
- `recorder produced no data` → canvas «испорчен» внешними текстурами без CORS или WebGL не в canvas: `--ui`.
- Нет звука в дубле → игра звучит не через WebAudio/`<audio>` или звук не разблокирован кликом; проверь `audio_tracks` в выводе capture.
- Мыло на скриншотах → снимай дубль больше (`--size 2560x1440`, `--dpr 2`) или бери кадры `api.shot()`.
