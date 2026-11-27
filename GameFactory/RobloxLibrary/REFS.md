# Референсы Roblox-игр: что открыть под задачу

Кадры лежат в `refs/<игра>/`, имя файла `<videoId>_<mmss>_<что>.jpg`; кадры из записей Alex начинаются с `alex_`. Разбор каждой игры (фантазия, вход, цикл, экономика, монетизация, визуал, сверка с конституцией): `notes/BachaBlox.md`, `notes/FoltynFamily.md`, `notes/Valtric1.md`. Правила и выводы: [STYLE.md](STYLE.md). Картинки и транскрипты лежат только локально (в git не идут). Сначала открывай кадры, потом разбор.

Для веба кадры — референс механики, UI-логики, темпа и VFX, а не внешности: персонажи и UI свои (STYLE.md, главное правило).

## Под задачу
| Нужно | Смотри |
|---|---|
| Вход и первая минута | `robot-fighter` (entry, minigame), `net-a-fish` (first-legendary), `survive-your-ideas`, `fake-an-egg`, `throw-food-for-animals` (j0mZQZG3NH8_0000_new-account), `catch-a-plane` (new-account-hud) |
| HUD и раскладка кнопок | `throw-food-for-animals` (hud-throw), `stone-skipping` (hud), `spider-arm` (hud-ladder), `cut-a-rock` (hud-offers), `ragdoll-physics-sandbox` (alex_0002_hud) |
| Магазин, офферы, две цены | `throw-food-for-animals` (ui-shop), `steal-an-egg` (alex_0015_ui-shop), `ride-a-dino`, `sushi-empire`, `loot-to-forge`, `the-forge` (тёмный UI) |
| Окно ребёрта Before → After | `stone-skipping`, `robot-fighter`, `bow-forge`, `pet-fighters`, `net-a-fish` (rebirth-window), `spider-arm` |
| Индекс и коллекция | `net-a-fish` (index-page-reward), `throw-food-for-animals` (alex_0130_index), `steal-an-egg` |
| Шансы и редкость на экране | `throw-food-for-animals` (insane-luck, vfx-newpet), `throw-seeds-for-plants` (alex_0045_rarity), `stone-skipping` (gacha) |
| VFX-моменты | `throw-food-for-animals` (vfx-newpet, alex_0025_vfx-new), `robot-fighter` (vfx), `stone-skipping` (vfx-portal), `ragdoll-physics-sandbox` (alex_0115_vfx) |
| Мир меняется от действия | `clean-the-moon`, `shred-the-cash` (hud-pile-counter), `eat-everything-grocery-store` (hud-kcal), `chop-a-forest`, `black-hole-mass` |
| Игра с концом и глобальной шкалой | `charge-phone-with-potatoes`, `destroy-the-sun`, `cook-the-chicken-by-slapping`, `shred-the-cash` |
| Социальный хаос | `survive-your-ideas`, `fake-an-egg`, `dont-splash`, `steal-an-egg` (alex_0025_run) |
| Тёмный или неоновый стиль | `net-a-fish`, `bug-evolution`, `the-forge`, `build-a-dungeon` |
| Тёплый стиль без кислоты | `run-a-farm`, `sushi-empire`, `great-wall-builder` |
| Вид от первого лица, руки как инструмент | `shred-the-cash`, `cook-the-chicken-by-slapping`, `chop-a-forest`, `ragdoll-physics-sandbox` |

## Все игры
Яркость 0–255 и насыщенность — средние по кадрам видео; в кадр попадают фейскам и интро, поэтому палитра приблизительная. Точные данные: `refs/_palettes.json`, пересборка: `python3 tools/refs_index.py <RobloxLibrary> [папка кадров]`.

| Игра | Кадров | Яркость / насыщ. | Палитра | Кадры UI/HUD |
|---|---|---|---|---|
| `aura-per-click` | 5 | 126 / 39% | #508fb1 #1a284d #b6ded2 #9fa9b2 #265f91 |  |
| `bike-for-egg` | 5 | 157 / 51% | #7ff12b #8ffc2a #319c57 #a25c4a #c0db81 |  |
| `black-hole-mass` | 5 | 114 / 28% | #d9d6d6 #7a6080 #5f89a1 #070137 #272f69 | lyFnadaIPf0_0000_hud-xp-ladder.jpg |
| `bow-forge` | 5 | 117 / 23% | #a48377 #d6caad #2d3e46 #5f7b7e #81c18d | ID2s9IEkJ9Q_0136_ui-rebirth.jpg, ID2s9IEkJ9Q_1630_hud-stage.jpg |
| `break-and-steal-an-egg` | 9 | 142 / 36% | #85ed25 #8892a1 #4d687a #d1c88e #577d6d | AYwVp57ZEdw_0054_ui-shop.jpg, AYwVp57ZEdw_0800_hud-steal.jpg |
| `bug-evolution` | 5 | 61 / 17% | #1c4917 #0a0b0d #374734 #608a65 #232a28 | dN8QWr580us_0106_ui-trait.jpg |
| `build-a-dungeon` | 5 | 91 / 20% | #31344b #7b6b80 #4a6073 #c5c2a8 #0a0b1c | hDTOlingNsc_0530_hud.jpg, hDTOlingNsc_2400_build.jpg |
| `build-and-kill-zombies` | 5 | 129 / 40% | #b1d830 #c7b393 #446444 #262826 #8e6d58 |  |
| `cat-battles` | 5 | 119 / 29% | #6edad6 #140c1c #c2ddcb #a09360 #7f6854 |  |
| `catch-a-plane` | 10 | 115 / 28% | #928c8e #7d6876 #0c0314 #6e6a80 #100a18 | 8SRsojYgNAo_0000_new-account-hud.jpg |
| `charge-phone-with-potatoes` | 5 | 119 / 26% | #d18e5d #0f0a10 #f1e0b3 #8d634b #713a3c | Z6Bkex3SxZ4_0600_ui-upgrade.jpg |
| `chop-a-forest` | 6 | 113 / 24% | #548469 #e3daba #304740 #a18966 #19111e | hA5iwvWtB8c_1530_ui-upgrades.jpg |
| `clean-the-moon` | 9 | 104 / 14% | #060713 #a7b6a5 #a4afa3 #050a15 #a18988 | fhd5LmzW0ms_0630_ui-shop.jpg |
| `cook-the-chicken-by-slapping` | 5 | 118 / 18% | #374044 #6c8373 #ae917b #acb5a7 #1c111a | u9VGWwpULhM_1530_ui-buy.jpg |
| `cut-a-rock` | 5 | 113 / 22% | #d2c7cc #313a47 #705556 #a98f8a #191425 | Xl9mcZS2bv4_0000_hud-offers.jpg |
| `defend-your-plushie` | 5 | 136 / 43% | #52da30 #764850 #8a7f6a #35ba35 #a5cf7d |  |
| `destroy-the-sun` | 6 | 132 / 32% | #e8e6c6 #472b44 #11121f #dab598 #966c79 |  |
| `dont-splash` | 6 | 123 / 23% | #6caf66 #b4b58e #191722 #ac8e5c #b1a66d |  |
| `dragon-arena` | 5 | 162 / 35% | #50ff78 #c2bfa3 #a65854 #799687 #baa095 |  |
| `eat-everything-grocery-store` | 5 | 121 / 21% | #e7e3ca #09050a #1f2b39 #cba39c #815f66 | 0RdfUR7tQUU_0130_hud-kcal.jpg, 0RdfUR7tQUU_0230_ui-upgrades.jpg |
| `fake-an-egg` | 5 | 147 / 60% | #f3b60f #1fff7e #1c2231 #56846e #46e27e | lziw6Wx4pV0_0012_disguise.jpg |
| `great-wall-builder` | 5 | 93 / 19% | #4f7542 #333c31 #7a725e #a8ae8d #644d40 | tKb-dVIu2fA_0124_ui-shop.jpg, tKb-dVIu2fA_0212_hud.jpg |
| `loot-to-forge` | 5 | 142 / 27% | #e0e6d5 #869b9a #a67768 #5d7376 #292d3a | mwsU6-u4pdk_0000_ui-shop.jpg, mwsU6-u4pdk_0142_hud-stage.jpg |
| `net-a-fish` | 5 | 70 / 16% | #232530 #29454c #5e7269 #554a4b #11202b |  |
| `pet-fighters` | 6 | 89 / 32% | #996266 #395d55 #9ac887 #442b4e #0a0331 | Kl6yaM4BWi4_0054_ui-rebirth.jpg, Kl6yaM4BWi4_0224_ui-pet.jpg |
| `ragdoll-football` | 4 | 125 / 26% | #4ca94f #53b457 #aed3c2 #13121f #49354e |  |
| `ragdoll-physics-sandbox` | 9 | 133 / 23% | #bfb48c #83c6d7 #467094 #95857f #141f41 | M3vFWpigkD8_0830_ui-weapons.jpg, alex_0002_hud.jpg, alex_0302_ui-tools.jpg, alex_0405_ui-maps.jpg |
| `ride-a-dino` | 6 | 140 / 31% | #4be269 #89858a #c3e59e #3f8058 #14272f | sHIJScOsmAg_0148_ui-shop.jpg |
| `robot-fighter` | 5 | 133 / 33% | #4af04f #94a5ba #406e69 #1f2d4b #623f4e | kivQtgV7Rpo_0700_ui-rebirth.jpg |
| `run-a-farm` | 5 | 134 / 23% | #b49674 #a57853 #819762 #dbcba6 #4a3e33 |  |
| `shred-the-cash` | 5 | 83 / 25% | #965b59 #395c43 #192024 #392b39 #0d0713 | X0waT3ScjLg_0142_hud-pile-counter.jpg |
| `spider-arm` | 5 | 147 / 25% | #d1dccc #89afb2 #a98276 #2b2d36 #5c7b89 | aI7qoVmn0dc_0000_hud-ladder.jpg |
| `steal-an-egg` | 9 | 133 / 43% | #5ff532 #af6f51 #a8ff4c #151632 #495969 | alex_0015_ui-shop.jpg |
| `steel-fighters` | 5 | 111 / 28% | #9e816b #453f43 #151317 #4f7f63 #5bdd7d | FoQlTzm9grI_0018_build.jpg |
| `stone-skipping` | 6 | 135 / 35% | #e3d4aa #c56a56 #d8a27f #5f6566 #779b85 | EYI8B2Ju-nU_0048_hud.jpg, EYI8B2Ju-nU_0124_ui-rebirth.jpg |
| `summon-a-pet-army` | 5 | 135 / 29% | #8fe671 #446677 #c8e8c7 #121336 #562b4c |  |
| `survive-your-ideas` | 6 | 128 / 38% | #6aff48 #09050a #93575a #c9f7ac #35384d | UrVz9GBZ2JQ_0024_hud-idea-banner.jpg |
| `sushi-empire` | 5 | 115 / 31% | #b98349 #8b623f #e8ba6f #201422 #80795a | AWwYzW2WheU_1600_ui-shop.jpg |
| `the-forge` | 5 | 40 / 8% | #3e3b41 #171215 #1f2226 #0e1011 #37282f | viIbGa0Vq1Q_0248_ui-shop.jpg |
| `throw-food-for-animals` | 15 | 135 / 49% | #4cfd2c #35f920 #4dff2a #82444d #111b38 | DlZXpyrGCw4_0100_ui-shop.jpg, F6rWFXQRX60_0124_hud-throw.jpg, alex_0135_ui-shop.jpg |
| `throw-seeds-for-plants` | 4 | — / —% |  |  |
