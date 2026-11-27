# C. Алгоритм Roblox, изменения 2026, порог 500 highly engaged, Sponsored Ads, игроки, статы — канал Tap

Источник: 6 транскриптов (авто-субтитры). Исправленные ослышки: «home wrecks» = home recs (рекомендации на главной); «Farmer Die / Farmer Dairy / Farm a Dye» = его игра, видимо **Farm or Die** [вывод]; «Baker Die» = вероятно Bake or Die [вывод]; «Hydro Di» = вероятно Hide or Die (жанр hide and seek) [вывод]; «Grove Garden 2» = Grow a Garden 2; «Steel of Brain Rot» = Steal a Brainrot; «e-combat background» = e-commerce; «18+» в owMnhg3fn_M 13:00 — оговорка, имеется в виду 16+. Его игра-пример во всех видео — **Hack a Business** (совладелец, разработчик David), вдохновлена Oil Empire.

---

## 1. По видео

### 1.1 The Roblox Algorithm Explained Like You're 5 Years Old — `inWzxY26NXo` (18 мин)
**Тезис:** реклама только «кормит» алгоритм первичными данными; в home recs попадает игра, чьи статы лучше конкурентов по той же аудитории, поэтому лечится обновлениями, а не бюджетом.

**Как работает алгоритм (по его словам и документации Roblox):**
1. Нужен трафик: Roblox Sponsored Ads (основной способ), бесплатно — short-form (TikTok, YouTube Shorts), ещё «free UGC» (он сам не разбирается) [01:00].
2. По первичным игрокам с рекламы Roblox смотрит все метрики: average playtime, D1, D7, монетизацию (ARPPU), conversion rate — как «мягкие сигналы» [02:00–04:00]. Это почти единственный момент, когда данные рекламного трафика влияют на home recs [04:00, 12:00].
3. Рекламный трафик — **cold traffic**: Ads оптимизируют под самого дешёвого игрока, а не самого квалифицированного (доли цента за игрока, «боты стоят в лобби»). Низкие первые статы — норма [04:00–05:00]. Игроки из home recs — твоя аудитория: выше D1/D7, playtime, траты [04:00].
4. Сначала Roblox ранжирует игру против **всего жанра** (в аналитике — сравнение с жанром), всё может быть «зелёным» [06:00–07:00].
5. Затем, набрав данных, сравнивает с **Benchmark: experiences with similar players** (игры, в которые играют твои же игроки) — тут статы обычно падают; это и есть реальная конкуренция [08:00–09:00]. Путь: Analytics → Acquisition → Home Recommendations [08:00].
6. Чем быстрее накормишь данными, тем быстрее вход в алгоритм; крупные студии тратят ~$10 000 в день и взлетают за 2–3 дня, но до этого долго оптимизируют статы на рекламном трафике в **beta mode** [07:00–08:00].
7. Beta mode: пока он включён, игра **не показывается в home recommendations** — можно оптимизировать статы на рекламе, а потом «выйти в алгоритм» с лучшими цифрами [03:00–04:00, 08:00].
8. Аналогия «фермерский рынок»: у жанра есть поток игроков home recs (условно 10 000), у входа — игры с лучшими статами (99 Nights in the Forest, затем Bake or Die ~30K CCU, 100 Days at Sea ~4K CCU). Рынок включает смежные игры с похожим лупом [09:00–12:00]. Winner-takes-all: Farm or Die пиковал на 2K CCU и умер, когда пришли игры с лучшими статами [09:00].
9. Sponsored Ads и home recs — **два разных рынка**: реклама не ставит тебя в home recs [12:00–13:00].
10. Метрики во вкладке Home Recommendations: QPTR, deep play-through rate, 7-day playtime per user, 7-day play days per user, intentional co-play (у Farm or Die выше бенчмарка — потому и жива; моно низкая) [14:00–15:00].
11. Окно данных **rolling 7 days** — после крупного апдейта не жди роста на следующий день [17:00].

**Процедура:** реклама → смотреть статы → вход в алгоритм → найти **худший стат** (напр. D1) → значимый апдейт под него → снова реклама, чтобы собрать свежие первичные данные → следующий стат (playtime, D7…) [15:00–17:00]. Если уже много трафика из алгоритма — не нужно запускать/останавливать рекламу, Roblox использует новые данные сам [17:00].

### 1.2 BIG UPDATE! New Roblox Algorithm Changes June 2026 — `pu2o80prNV8` (15 мин)
**Тезис:** QPTR разделили на Play-Through Rate и First Play Bounce Rate, добавили D28; вовлечённость важнее монетизации, кликбейт и клоны «мертвы»; игра — воронка, чини самое узкое место.

**Изменения:**
- **QPTR deprecated** → **Play-through rate (PTR)** = доля home-impressions, перешедших в play sessions (чистый CTR) + **First play bounce rate** = % игроков, ушедших в первые **60 с** (есть и 61–180 с) [00:00–01:00].
- Bounce rate — **негативная** метрика (единственная с пометкой «high rates lower your home recommendations exposure»): нужна как можно ниже. У него ~**20%** — «слишком высоко» [01:00].
- Play days per user теперь меряются и на **D28** (D1, D7, D28) [04:00, 07:00]. Playtime per user = сколько играют в эти дни [05:00].
- Ранжирование занимает столько же времени, остальное без изменений [07:00]. Roblox (product manager Sandy) — «хотим high-quality games» [07:00]. Engagement-сигналы важнее моно «по их же формулировке» [06:00].
- Кликбейт («mysterious game» с клоном Steal a Brainrot внутри, 0 CCU) и X999 модд-клоны/шаблоны больше не работают — bounce rate это ловит [04:00–06:00].
- User detail page CTR (Acquisition) = played from detail page / viewed detail page — часть общего PTR, многие разработчики игнорируют страницу [02:00–03:00].

**Воронка** [08:00–11:00]: home impression → клик (PTR) → не bounce в 60 с → D1 → D7 (дни 2–7) → D28 (дни 8–28). Ищи самое узкое горло, сравнивая с бенчмарком жанра [11:00].
- PTR → упаковка: thumbnail + title; если тайтл хороший — тестируй новые thumbnails [11:00–12:00].
- Bounce → несоответствие ожиданий от title/thumbnail и первых 60 с геймплея; топ-разработчики экспериментируют с катсценами (в Grow a Garden 2 — 15-секундная катсцена) [03:00–04:00, 12:00].
- D1 → туториал/онбординг; в Funnels фильтруй по device type: tutorial completion 77% в среднем, на консоли было ~30% → нашли баг на консоли [12:00].
- D7 → weekly events (admin abuse), достаточно контента и механик глубокой прогрессии [13:00]. Hack a Business проходится за ~**2,5 ч** → большой контент-апдейт [14:00].
- D28 → «пока вопрос», видимо глубокие механики прогрессии (Index) [13:00–14:00] [его догадка].
- Разбивай метрики по device type и traffic source [13:00].
- VP of engineering (Benam) рекомендует **A/B-тесты**: Experiments — апдейт только для % игроков, смотреть влияние на стат; A/B можно и thumbnails, и апдейты [14:00–15:00].

### 1.3 Roblox's 500 Highly Engaged Players Update Explained Like You're 5 — `Rkgbcv6omPg` (13 мин)
**Тезис:** с 19 мая 2026 новые игры видны только 16+, пока не наберут 500 highly engaged players; порог берётся обычной рекламой + выходом в home recs за ~$180.

- Цель: безопасность детей — Roblox делится на Roblox Kids и Roblox Select; бот-накрутка «condo»-игр в алгоритм [00:00–02:00].
- С **19 мая 2026** каждая новая игра доступна только аудитории **16+** до проверки («вышибала в клубе») [02:00–03:00].
- Fast track для детских игр: Roblox «изучает» вариант с pre-launch review и повышенным, возвращаемым (recoupable) взносом; детали — до глобального запуска Kids/Select [04:00]. Его совет: не важно, всё равно иди обычным путём [04:00–05:00].
- **Highly engaged player** = аккаунт, совершивший минимальную покупку где угодно на Roblox за последние **60 дней** (тратить в твоей игре не обязательно); модерация смотрит account age, play history, platform spend; точные пороги скрыты [06:00–08:00].
- Реклама: Roblox recommended targeting; при включении ads всё равно отдаются 16+ автоматически — ставить 16+ руками не нужно [05:00].
- **Его кейс:** реклама с 20.05.2026, **$16/день**, порог пройден за **11 дней**, ~**$180** [08:00]. Трафик: ~45K с ads, лишь 950 plays из home recs [08:00]. Первые 3–4 дня счётчик почти стоял (10–20 из 500); с появлением home rec impressions — 50→80→~250 → быстро до 500 [09:00].
- Чужие кейсы (Twitter): 210K визитов за 2 недели в основном с рекламы → 190; потом с home recs 90K визитов за 5 дней → 350 [09:00–10:00]; «до 500 за несколько дней после входа в алгоритм» [10:00]. Вывод автора: в рекламе много ботов, engaged-игроки приходят из home recs [10:00].
- Можно войти в алгоритм **до** порога 500 — у него так и было [10:00–11:00]. Тратить «тонну» не обязательно; раньше на старт Farm or Die тоже уходило ~$100–200 — порог лишь немного дороже [11:00–12:00]. Нет денег — делай commissions (заказы) и вкладывай в рекламу [12:00].

### 1.4 Roblox Sponsored Ads Explained Like You're 5 Years Old — `owMnhg3fn_M` (17 мин)
**Тезис:** CTR рекламы решают core fantasy + title + thumbnails; запуск рекламы простой — $16/день, всё по рекомендации Roblox, стоп, когда home impressions обгонят ad impressions.

- Кейс: CTR рекламы **1,54% → 3,27%** (более чем ×2) сменой тайтла и thumbnails [00:00].
- **Core fantasy** = базовое эмоциональное переживание, которое обещает игра: роль, действия, чувство; главная причина, почему игрока тянет к игре. Продумывать **до** рекламы и даже до разработки [01:00–02:00, 10:00].
- Тест «пятиклассник рассказывает другу за обедом»: «взламываешь McDonald's, Apple, Netflix» vs «собираешь данные и продаёшь» [02:00–03:00].
- Тайтл: **уровень чтения 3-го класса**; «data» = 4–5 класс, «corporation» = 4–6, «business» = 3–4 → **Hack a Business** вместо **Sell Your Data** [03:00–06:00].
- **Keyword research** в Creator Exchange (он «всегда начинает с тайтла»): вбить ключевое слово, смотреть, есть ли **несколько** игр с большими визитами (data — пусто; cyber — 2,6M/8,6M; hack — 11,1M, 5M, 20M, 12,8M → сильная фантазия) [04:00–06:00].
- Title даёт контекст thumbnail; мозг видит картинку первой, но фантазию передаёт тайтл [07:00].
- Шаблоны тайтлов: verb + noun (Steal a Brainrot, Grow a Garden, Kick a Lucky Block), Be a noun (Be a Lucky Block, Be a Firefighter), Escape the noun. Лучшие — ясная фантазия + понятное эмоциональное состояние + **встроенный вызов** (99 Nights in the Forest, Survive the Cold, Escape the Zoo) [08:00–10:00].
- Thumbnail: скрестил доказанный thumbnail из Be a YouTuber (экран компьютера) с визуалом хакерских игр (зелёная матрица 0/1): «логотип компании слева, матричный хакер справа» [10:00–11:00].
- **Запуск рекламы:** минимум **10 thumbnails, лучше 20**, чем креативнее, тем лучше [12:00]. Кампания: All players / recommended, **16 ad credits в день**, daily budget (не lifetime), выбрать все креативы, больше ничего не менять; advanced targeting (18–24) не нужен — «all ages» и так уходит на 16+ [12:00–13:00].
- Платить Robux → конвертировать в ad credits — сильно дешевле, чем USD [15:00–16:00].
- Данные Roblox обновляются медленно (~раз в 3 дня, против ежечасных у Shopify); у него 60/500 после 45 ad credits — не паниковать [13:00].
- **Алгоритм рекламы:** $16/день минимум **3 дня**, в идеале неделю → статы появляются ~через 3 дня → в тот же день начинать апдейты (играть с живыми игроками, читать фидбек, funnels) → продолжать рекламу и апдейты → вошёл в алгоритм? нет — продолжать; да — **стоп, когда home recommendation impressions превысили sponsored ad impressions** (Acquisition, последние 7 дней; у него ~200K ad impressions — выключил бы, когда home recs дадут ~200K) [13:00–16:00].
- Обычно ≥ **1 недели** рекламы до первых home rec impressions; с хорошим thumbnail/QPTR/статами home impressions «взлетают» и рекламу можно остановить раньше [16:00].

### 1.5 The #1 Reason Nobody Finds Your Roblox Game (How To Get Players) — `dUmh6GAvJ-E` (14 мин)
**Тезис:** игроков нет, потому что ты вошёл в перенасыщенный рынок без мутации; ищи «purple ocean» — высокий спрос, слабое исполнение.

- Жизнь тренда: **фаза 1** first to market (Don't Wake the Brainrots, ~9–10 мес. назад) → **фаза 2** рынок забит клонами от template-продавцов, все умирают → выживают те, кто **мутировал** (новый тайтл, новый thumbnail, похожий луп) [00:00–03:00].
- Пример: Don't Steal the Bobo — тот же луп, что Don't Wake the…, но первым сменил тайтл и thumbnail → **9,5K CCU**, клоны на 2–31 CCU [03:00–05:00].
- Документация Roblox (Best practices for discovery): используй уникальные метаданные и оригинальные изображения; не публикуй повторяющиеся тайтлы/картинки; при thumbnail personalization все thumbnails должны отражать игру [01:00]. «Issues that limit exposure → Non-unique experiences»: метаданные и place files, близкие к существующим, **больше не приоритизируются в рекомендациях** и ниже в поиске [02:00–03:00].
- У Hack a Business лучше всех работает полностью оригинальный thumbnail, а не «вдохновлённый» Be a YouTuber [02:00].
- Blue ocean / red ocean: fishing — красный океан (Fish It / Fish первые; My Fishing Tycoon — даже точный тёзка, плохой CTR). Выжили с твистом темы: Ice Fishing, Fish Tank, Cage Fishing; generic (Fishing Simulator, Steal a Fish, Fishing Brainrot) слабее [06:00–10:00].
- Брать новый рынок без спроса — рискованно [11:00]. **Purple ocean = высокий спрос + плохое исполнение**: airport (много RP, но никто не исполняет хорошо), firefighter (доминирует одна игра); Cole: hide and seek — спрос большой, исполнение слабое → Hide or Die забрал долю [11:00–12:00].
- Проверка спроса: вбить фантазию в Creator Exchange, поиграть, сделать в 10 раз лучше — «9 из 10 выиграешь» [12:00].
- Чек-лист Cole, п.2: идея кликабельна, relatable или уже имеет страстную фанбазу? [12:00–13:00]. Blue ocean может быть и недообслуженной аудиторией: в Emergency Roleplay играют реальные взрослые first responders [13:00–14:00].

### 1.6 How to Improve Your Roblox Game Stats FAST — `HFcegpPPvpI` (16 мин)
**Тезис:** каждый апдейт — гипотеза под конкретный стат; усиливай её пересечением трёх источников данных (качественные, количественные, конкуренты), выпускай, проверяй, откатывай.

- Результат: Hack a Business — пик **1K CCU** (ожидают 2K), почти все статы зелёные, кроме D7, **$6K/мес** через **2 недели** после запуска; разработчик обновлял ежедневно, иногда 2 раза в день [00:00–01:00].
- Быстрый справочник «стат → причина» [01:00–04:00]: playtime (core loop не приятен — каждому действию звук и визуал, camera shake), D1 (онбординг/туториал, Funnels), D7 (social flex, контент, admin abuse/события), payer conversion (дешёвый starter pack, consumable dev products: «удвоить offline earnings за 19 Robux» резко подняло конверсию), ARPPU (дорогие game passes для китов, 3 уровня: Starter / Pro / OP pack), QPTR (упаковка).
- Ментальная модель из CRO e-commerce (8–9-значные бренды) [04:00–05:00]: апдейт = гипотеза «если добавлю/уберу/улучшу Y (фичу, экшен, экономику, прогрессию), то X стат вырастет» [05:00–07:00].
- Три вида данных [07:00–09:00]: qualitative (Audience feedback, опросы, баг-репорты в Discord, **наблюдение за живыми игроками** — «самый недооценённый источник»), quantitative (статы, funnels, New user first session retention), competitor research (топ игр жанра).
- Пример [10:00–13:00]: фидбек «собирать данные со всех серверов сразу» (qualitative) + у топа жанра (Oil Empire) такое есть (competitor) + в New user first session retention (Engagement, окно 7 дней) резкий провал на **2:30** (quantitative) → запустить таймер, пройти туториал, посмотреть, что происходит на 2:30 → гипотеза «одновременный сбор, особенно на мобиле → больше playtime» → ship → проверить.
- Цикл: research → hypothesis → launch update → check results → да: следующая гипотеза; нет: **revert** и новая гипотеза [13:00–15:00].

---

## 2. Правила

### Перед разработкой и упаковка
- ★ Определи core fantasy (роль, действие, чувство) до разработки и до рекламы; проверь тестом «школьник объясняет другу за обедом» [owMnhg3fn_M 01:00–03:00, 10:00; dUmh6GAvJ-E 12:00].
- Начинай с тайтла: keyword research в Creator Exchange, ищи **несколько** игр с миллионами визитов по ключевому слову, а не одну [owMnhg3fn_M 04:00–06:00].
- Пиши тайтл на уровне чтения 3-го класса; проверяй сложность каждого слова [owMnhg3fn_M 04:00, 06:00].
- Используй шаблоны Verb a Noun / Be a Noun / Escape the Noun; добавляй встроенный вызов (99 Nights…, Survive the…) [owMnhg3fn_M 09:00–10:00].
- Помни: thumbnail видят первым, но тайтл даёт ему контекст и передаёт фантазию — оценивай их в паре [owMnhg3fn_M 07:00].
- Делай thumbnail, скрещивая доказанную композицию одной игры с визуальным кодом своей фантазии [owMnhg3fn_M 10:00–11:00]; но проверяй и полностью оригинальные — у него оригинальный победил «вдохновлённый» [dUmh6GAvJ-E 02:00].
- ★ Не копируй тайтлы, thumbnails и шаблоны/place files: Roblox не приоритизирует non-unique experiences в рекомендациях и понижает в поиске [dUmh6GAvJ-E 01:00–03:00; pu2o80prNV8 04:00–06:00].
- ★ Если делаешь игру по чужому лупу — сделай значимый твист core loop/темы (Hack a Business vs Oil Empire; Ice/Cage Fishing) [pu2o80prNV8 06:00; dUmh6GAvJ-E 09:00–10:00].
- Не делай кликбейт («mysterious game»): bounce rate его ловит и режет показы [pu2o80prNV8 04:00–06:00].
- Определи фазу рынка фантазии: фаза 1 (first to market) — можно; фаза 2 (red ocean) — только с мутацией [dUmh6GAvJ-E 00:00–03:00, 10:00].
- Ищи purple ocean: высокий спрос в Creator Exchange + слабое исполнение; поиграй в конкурентов и сделай в 10 раз лучше [dUmh6GAvJ-E 11:00–12:00].
- Не входи в фантазию без спроса — это рискованно [dUmh6GAvJ-E 11:00].
- Проверяй идею: кликабельна, relatable или уже есть страстная фанбаза? Рассматривай недообслуженные аудитории (взрослые first responders) [dUmh6GAvJ-E 12:00–14:00].
- Заполняй experience detail page разными лучшими thumbnails (из рекламы или home recs), показывающими разные части геймплея, а не один повтор [pu2o80prNV8 02:00–03:00].

### Запуск и реклама
- ★ Для выхода в алгоритм нужен трафик: Sponsored Ads (основное) или short-form (TikTok, Shorts), если денег нет [inWzxY26NXo 01:00; Rkgbcv6omPg 11:00].
- Подумай о beta mode: оптимизируй статы на рекламном трафике, пока игра скрыта из home recs, затем выключи и выходи в алгоритм с лучшими цифрами [inWzxY26NXo 03:00, 07:00–08:00].
- ★ Запускай с бюджетом минимум **$16 (16 ad credits) в день**, daily budget, минимум 3 дня, в идеале неделю [owMnhg3fn_M 12:00–14:00; Rkgbcv6omPg 08:00].
- Загружай в кампанию минимум 10 thumbnails, лучше 20, максимально разные [owMnhg3fn_M 12:00].
- ★ Ставь всё по рекомендации Roblox (All players, recommended targeting); не трогай advanced targeting и не выставляй 16+ руками — всё равно отдаётся 16+ [owMnhg3fn_M 12:00–13:00; Rkgbcv6omPg 05:00].
- Плати Robux, конвертированными в ad credits, а не USD — дешевле [owMnhg3fn_M 15:00–16:00].
- ★ Не паникуй из-за плохих первых статов: рекламный трафик холодный, оптимизирован под дешевизну, много ботов [inWzxY26NXo 04:00–05:00; Rkgbcv6omPg 10:00; owMnhg3fn_M 14:00].
- Жди ~3 дня, пока статы появятся (данные Roblox медленные); не делай выводов раньше [owMnhg3fn_M 13:00–14:00, 17:00].
- В тот же день, когда пришли статы, начинай апдейты: играй с живыми игроками, читай фидбек, смотри funnels [owMnhg3fn_M 14:00].
- Продолжай рекламу + апдейты, пока нет home rec impressions; ожидай ≥1 недели до первых [owMnhg3fn_M 14:00, 16:00].
- ★ Выключай рекламу, когда home recommendation impressions за 7 дней превысили sponsored ad impressions (Acquisition) [owMnhg3fn_M 15:00–16:00].
- ★ Не лечи умирающую игру «просто больше рекламы»: Ads и home recs — разные рынки; без апдейтов, улучшающих статы, реклама не даёт места в алгоритме [inWzxY26NXo 12:00–14:00, 18:00].
- После значимого апдейта снова запускай рекламу, чтобы дать Roblox свежие первичные данные [inWzxY26NXo 16:00].
- Если трафика из алгоритма уже много, не дёргай рекламу вкл/выкл — Roblox и так учтёт новые данные [inWzxY26NXo 17:00].
- Чем быстрее кормишь данными на старте, тем быстрее вход в алгоритм (большие студии — $10K/день) [inWzxY26NXo 07:00].
- Нет денег на рекламу — бери commissions и вкладывай в ads [Rkgbcv6omPg 12:00; owMnhg3fn_M 14:00].

### Порог 500 highly engaged (16+)
- Не жди порога, чтобы войти в алгоритм: вход возможен раньше, и именно home recs быстро добирают порог [Rkgbcv6omPg 09:00–11:00].
- Бери порог обычной схемой: реклама $16/день → вход в home recs; не заливай огромный бюджет [Rkgbcv6omPg 11:00].
- Не ориентируйся на fast track для детских игр — пока только «исследуется» [Rkgbcv6omPg 04:00–05:00].
- Не верь слухам в Twitter: определение highly engaged — платёж где угодно на Roblox за 60 дней [Rkgbcv6omPg 05:00–07:00].

### Аналитика и метрики
- ★ Смотри не Overview, а Analytics → Acquisition → Home Recommendations и **Benchmark: experiences with similar players**, а не сравнение со всем жанром [inWzxY26NXo 06:00, 08:00, 14:00; pu2o80prNV8 00:00, 11:00].
- Проверяй, какой бенчмарк выбран в чужих скриншотах на YouTube — «зелёный против жанра» ничего не значит [inWzxY26NXo 06:00].
- ★ Рассматривай игру как воронку: impression → PTR → bounce 60 с → D1 → D7 → D28; чини самое узкое место относительно бенчмарка [pu2o80prNV8 08:00–11:00, 14:00; inWzxY26NXo 16:00].
- Держи bounce rate как можно ниже — это негативная метрика, режущая показы [pu2o80prNV8 01:00, 05:00].
- Следи за User detail page CTR (Acquisition) [pu2o80prNV8 02:00–03:00].
- ★ Отслеживай каждый шаг туториала в Analytics → Funnels [HFcegpPPvpI 02:00; pu2o80prNV8 12:00].
- Фильтруй funnels/метрики по device type и traffic source — так находятся платформенные баги [pu2o80prNV8 12:00–13:00].
- Смотри New user first session retention (Engagement, окно 7 дней) как «hook retention»; найди резкий провал по времени и воспроизведи его с таймером в игре [HFcegpPPvpI 11:00–12:00].
- Учитывай rolling 7-day window: эффект апдейта виден не на следующий день [inWzxY26NXo 17:00].
- Учитывай метрику intentional co-play — кооп-дизайн может держать игру [inWzxY26NXo 15:00].

### Апдейты
- ★ Каждый апдейт — под один конкретный стат, начиная с худшего [inWzxY26NXo 16:00; pu2o80prNV8 08:00; HFcegpPPvpI 06:00].
- Формулируй гипотезу: «если добавлю/уберу/улучшу Y, то X вырастет» [HFcegpPPvpI 05:00–07:00].
- Подкрепляй гипотезу тремя источниками: фидбек игроков, конкуренты, свои цифры [HFcegpPPvpI 07:00–13:00].
- Наблюдай за живыми игроками в игре — самый недооценённый источник данных [HFcegpPPvpI 08:00; owMnhg3fn_M 14:00].
- После релиза проверь стат; не сработало — revert и новая гипотеза [HFcegpPPvpI 13:00–15:00].
- Обновляй часто: ежедневно, иногда дважды в день [HFcegpPPvpI 00:00; owMnhg3fn_M 16:00].
- Используй Experiments (A/B): выкатывай апдейт на % игроков и меряй влияние на стат; A/B-тестируй и thumbnails [pu2o80prNV8 14:00–15:00].

### Под конкретные статы
- Playtime: каждому действию — звук и визуальный эффект (camera shake), «action and response» [HFcegpPPvpI 01:00].
- ★ D1: туториал по принципу show, don't tell — игрок сам действует и видит результат (посадил семя → вырос) [HFcegpPPvpI 02:00–03:00; pu2o80prNV8 12:00].
- ★ D7: weekly events / admin abuse, social flex, достаточно контента и механик глубокой прогрессии; меряй время прохождения игры (2,5 ч — мало) [HFcegpPPvpI 03:00; pu2o80prNV8 13:00–14:00].
- D28: добавляй глубокую прогрессию (Index, новые способы взаимодействия), а не просто больше моделей [pu2o80prNV8 13:00–14:00].
- Payer conversion: дешёвый starter pack + consumable dev products в естественные моменты (удвоить offline earnings за 19 Robux) [HFcegpPPvpI 03:00].
- ARPPU: дорогие game passes для китов, три цены (Starter / Pro / OP) [HFcegpPPvpI 04:00].
- Bounce: устрани разрыв между обещанием title/thumbnail и первыми 60 с; рассмотри короткую катсцену (~15 с, как Grow a Garden 2) [pu2o80prNV8 04:00, 12:00].
- PTR/QPTR: правь упаковку; если тайтл уже хороший — тестируй новые thumbnails [pu2o80prNV8 11:00–12:00; HFcegpPPvpI 04:00].

---

## 3. Диагностика

| Симптом / низкий стат | Вероятная причина | Что делать |
|---|---|---|
| Низкий CTR рекламы / PTR / QPTR | Слабая или непонятная core fantasy, сложные слова в тайтле, посредственный thumbnail; red ocean с одинаковыми тайтлами | Keyword research, тайтл 3-го класса, 10–20 новых thumbnails; мутировать фантазию [owMnhg3fn_M; dUmh6GAvJ-E 08:00] |
| Хороший CTR в целом, но мало игроков | Перенасыщенный рынок (фаза 2), клон шаблона | Мутация: новый тайтл, новый thumbnail, твист темы; purple ocean [dUmh6GAvJ-E] |
| Высокий first play bounce rate (~20% — много) | Ожидание от тайтла/thumbnail ≠ первые 60 с; кликбейт; «вводящий в заблуждение тайтл» | Совместить обещание и старт, катсцена, честная упаковка [pu2o80prNV8 01:00, 05:00, 12:00] |
| Низкий User detail page CTR | Пустая страница игры, нет thumbnails | Выложить лучшие разные thumbnails, показать геймплей [pu2o80prNV8 02:00–03:00] |
| Низкий average playtime | Core loop не приятный, нет отклика на действия | SFX + VFX + camera shake на каждое действие; смотреть провалы в first session retention [HFcegpPPvpI 01:00, 12:00] |
| Низкий D1 | Онбординг/туториал | Funnels по шагам, show don't tell, фильтр по устройствам (баг консоли 30% vs 77%) [HFcegpPPvpI 02:00; pu2o80prNV8 12:00] |
| Низкий D7 | Мало контента, нет событий, нет social flex; игра проходится быстро | Weekly events/admin abuse, контент-апдейт, глубокая прогрессия [HFcegpPPvpI 03:00; pu2o80prNV8 13:00–14:00] |
| Низкий D28 | Нет глубоких систем прогрессии | Index и подобные механики [pu2o80prNV8 13:00–14:00] |
| Низкая payer conversion | Нет дешёвого входа | Дешёвый starter pack, consumable dev products [HFcegpPPvpI 03:00] |
| Низкий ARPPU | Нет дорогих предложений | Дорогие game passes, 3 ценовых уровня [HFcegpPPvpI 04:00] |
| Статы «зелёные», а CCU ~100 | Сравниваешь со всем жанром, а не с similar players | Смотреть Benchmark: experiences with similar players [inWzxY26NXo 06:00] |
| Игра была в алгоритме и умерла | Пришли конкуренты с лучшими статами по той же аудитории (winner-takes-all); низкий retention после изменений алгоритма | Апдейты под худший стат, затем реклама для свежих данных [inWzxY26NXo 09:00, 16:00; pu2o80prNV8 09:00] |
| Много тратишь на рекламу, а алгоритма нет | Не обновляешь игру, статы не растут | Сначала апдейт под стат, потом реклама [inWzxY26NXo 12:00–14:00, 18:00] |
| Игроки с рекламы стоят в лобби | Холодный/ботовый трафик | Норма; оценивать по home recs и бенчмарку [inWzxY26NXo 05:00; Rkgbcv6omPg 10:00] |
| Счётчик 500 highly engaged растёт медленно | Почти весь трафик с рекламы | Довести игру до home recs; данные обновляются раз в ~3 дня — подождать [Rkgbcv6omPg 09:00; owMnhg3fn_M 13:00] |
| Апдейт вышел, а статы не изменились на следующий день | Rolling 7-day window | Ждать неделю, затем оценивать [inWzxY26NXo 17:00] |
| Гипотеза не подтвердилась | Неверное предположение | Откат и новая гипотеза [HFcegpPPvpI 13:00] |

---

## 4. Цифры-ориентиры

- Бюджет рекламы: минимум **$16/день** (16 ad credits), ≥3 дня, лучше неделя [owMnhg3fn_M 12:00–14:00].
- Первые home rec impressions — обычно через ≥1 неделю рекламы [owMnhg3fn_M 16:00].
- Статы после старта рекламы — через ~3 дня; данные Roblox обновляются примерно раз в 3 дня [owMnhg3fn_M 13:00–14:00].
- Окно расчёта алгоритма — rolling **7 дней** [inWzxY26NXo 17:00].
- Стартовый бюджет раньше (Farm or Die): ~$100–200 [Rkgbcv6omPg 12:00].
- Порог 500 highly engaged: у него **11 дней, ~$180** при $16/день; ~45K визитов с ads, 950 из home recs; первые 3–4 дня — 10–20/500 [Rkgbcv6omPg 08:00–09:00]. Чужие: 210K визитов/2 нед. → 190; 90K за 5 дней с home recs → 350 [Rkgbcv6omPg 09:00]. В другом видео: 60/500 после 45 ad credits [owMnhg3fn_M 13:00].
- Highly engaged = покупка на Roblox за последние **60 дней** [Rkgbcv6omPg 06:00]. Ограничение 16+ для новых игр с **19 мая 2026** [Rkgbcv6omPg 02:00].
- Крупные студии: до **$10 000/день** на рекламу, взлёт за 2–3 дня [inWzxY26NXo 07:00].
- CTR рекламы: 1,54% — «ужасно», 3,27% — после фикса [owMnhg3fn_M 00:00].
- First play bounce: окно **60 с** (+ 61–180 с); ~**20%** — слишком высоко [pu2o80prNV8 01:00].
- Tutorial completion: **77%** — «довольно хорошо»; 30% на консоли — признак бага [pu2o80prNV8 12:00].
- Время прохождения 2,5 ч — мало для D7 [pu2o80prNV8 14:00].
- Провал в first session retention на 2:30 — точка для расследования [HFcegpPPvpI 12:00].
- Consumable dev product: удвоить offline earnings за **19 Robux** [HFcegpPPvpI 03:00].
- Hack a Business: 1K CCU пик, $6K/мес, через 2 недели после запуска [HFcegpPPvpI 00:00–01:00]. Farm or Die: пик 2K CCU, затем умер [inWzxY26NXo 09:00].
- Ориентиры рынка: Bake or Die ~30K CCU, 100 Days at Sea ~4K CCU [inWzxY26NXo 10:00]; Don't Steal the Bobo 9,5K CCU vs клоны 2–31 CCU [dUmh6GAvJ-E 03:00–05:00].
- Keyword «hack»: игры по 5M–20M визитов → сильная фантазия; «cyber» 2,6M–8,6M — «не то» [owMnhg3fn_M 05:00–06:00].
- Thumbnails в рекламу: 10 минимум, 20 оптимально [owMnhg3fn_M 12:00].
- Стоп рекламы: home rec impressions ≥ ad impressions за 7 дней (пример ~200K) [owMnhg3fn_M 15:00].
- CPM/CPC в цифрах не называются; только «игроки за доли цента» [inWzxY26NXo 05:00].

---

## 5. Инструменты

- Creator Hub Analytics: Overview; **Acquisition** (impressions по источникам: sponsored ads vs home recommendations; User detail page CTR); **Acquisition → Home Recommendations** (PTR, First play bounce rate, play days/playtime per user D1/D7/D28, deep play-through rate, intentional co-play; Benchmark: genre vs experiences with similar players).
- **Engagement → New user first session retention** (окно 7 дней).
- **Funnels** (шаги туториала, фильтр по device type).
- **Audience feedback** (опросы игроков).
- **Experiments** (A/B-тесты апдейтов на % игроков; A/B thumbnails; thumbnail personalization).
- **Beta mode** (скрывает игру из home recs).
- **Roblox Sponsored Ads** (кампания, daily budget, recommended targeting, ad credits из Robux).
- **Creator Exchange** — поиск по ключевым словам/фантазиям для keyword research и оценки спроса.
- Документация Roblox / Roblox Learn (Best practices for discovery, FAQ по Kids/Select, видео product manager Sandy и VP of engineering Benam).
- Google («what reading level is the word X»), таймер в Google для воспроизведения провала по времени.
- Discord игры (баг-репорты, предложения), Twitter-сообщество разработчиков, его Discord-сервер.
- Short-form платформы: TikTok, YouTube Shorts; free UGC (упомянут, не разобран).
- ИИ-генерация thumbnail по описанию («логотип слева, матричный хакер справа») — инструмент не назван [owMnhg3fn_M 11:00].

---

## 6. Цитаты

1. «Roblox ads optimize for the cheapest possible player to your game.» [inWzxY26NXo 05:00]
2. «This is the sponsored ads market. This is the home algo market.» [inWzxY26NXo 13:00]
3. «Bounce rate is not a good thing.» [pu2o80prNV8 01:00]
4. «You have to think about your game as a funnel.» [pu2o80prNV8 14:00]
5. «Once your home recommendation impressions have surpassed your ad impressions, stop ads.» [owMnhg3fn_M 15:00]
6. «Purple ocean equals high demand, but poor execution.» [dUmh6GAvJ-E 12:00]
