# 2026-11-21 · Скилл game-promo-kit (рекламные ролики, превью, скриншоты)

Скилл: `~/.claude/skills/game-promo-kit/` (SKILL.md, scripts/, references/, templates/). Вызов в алгоритме — шаг 8 WORKFLOW.md.

## Шаги и критерии
1. [x] Захват дубля (Playwright, canvas + звук игры + события). Критерий: видео идёт всю длину дубля без обрывов.
   - Решено: видео и звук — отдельные MediaRecorder (общий h264+opus стопорит видео); чанки копятся в странице и выгружаются после стопа на локальный HTTP-приёмник (чтение чанков во время записи и `expose_function` стопорят аппаратный h264); прогрев энкодера и обрезка головы; `real_fps` в `.events.json`.
2. [x] Поиск моментов (движение, громкость, события) + лист `review/moments.jpg`.
3. [x] Монтаж cartoon: развязка в 1-ю секунду, крючок по словам, чередование переходов xfade на долях бита, слоумо+наезд+тряска+RGB+бум, подписи, финал с лучами и кнопкой CTA, сгенерированный бит, A/B-крючки, вертикаль `stack` из ландшафта. Проверено на SpiderArm: ads_vertical en (2 крючка) + ru.
4. [x] Чистые превью CrazyGames (clean, обложка первым кадром, без звука) + обложки title_only + 6 скриншотов; Poki animated_thumbnail 6 с.
5. [x] Финальный рендер без `--draft` (minterpolate obmc после кропа) — ~2:48 на вертикаль 16 с; громкость −14 LUFS (замер −13,5); финальная карточка «название+кнопка» блоком — проверена 1:1, 16:9, 9:16.
6. [x] Синхронизация CloudRules (`scripts/sync.sh --commit`, push через github-account-router).

## Тестовый проект
Scratchpad-сессии: `…/scratchpad/sa/promo/` (config, scenario для SpiderArm). Игра: `/Users/mac/Downloads/WebAIGames/SpiderArm/dist` + `tools/lib/spy.js`.

## Открыто
- Пресет Яндекс Игр — размеры не сверены с живыми правилами (unverified в platforms.json).
- Внутриигровые таблички в кадре прячет director проекта (promo-hooks), не скилл.
