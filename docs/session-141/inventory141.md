# Сессия 141, шаг 0 — инвентарь корректности и сцен под цель (B) (Lever Researcher, `HPP-272`)

**Цель программы с закрытия с. 140 — корректность игры на возможно большем числе сцен** (ответ пользователя (B) на `HPP-261`,
`docs/ROADMAP.md` п. 214–215): картинка, крэши, зависания, вход и удержание уровней. Скорость Sky Garden — не цель и не гейт.
Установленная сборка — `9235a7ac…` (`rtskip=1`) со всеми отгруженными умолчаниями. С. 140 не отгрузила ничего: перепись `pm4c140`
остановлена на шаге 2 без игры. Под (B): `SCENE_OK` — 0 из 114 (критерий новый); список дефектов собирается этим документом.
60 FPS не обещаются. Документ — предложение; решения — у лида.

**Входы (прочитаны по HEAD):** KytyPS5 `main` `00c7264b` (п. 216 — последний пункт `ROADMAP.md`; п. 215 прочитан), ps5-em `75abe3b`;
бриф `docs/next-session-141.md`; заметка `C:/kyty/s140/lead/inventory_B_notes.md`. Игры, кода, сборок и замка нет; логи читались только
python в двоичном режиме потоком (`SEALED_RUN.lock` отсутствовал на каждом скане). Файлы шага — `C:/kyty/s141/step0/`, время —
`C:/kyty/s141/step0/times.txt`.

**P до чтения (18:48:57Z по `date -u`, строка 1 `times.txt`):** P(в списке есть K1/K2 с ценой воспроизведения ≤ 300 с игры на вход) = 0,65 [I]
(априор лида 0,6). **После разбора:** такие строки есть (Б1 — зависание входа BVH, Б2 — заминка кадров ≈ 951–954, Б3 — ожидание неподанного
тика), но у всех трёх p на вход мала или происхождение не установлено; P(«есть K1/K2 ≤ 300 с на вход» — верно) = 0,9 [I],
P(среди них есть исправимое с доказательством за ≤ 2 сессии) = 0,45 [I] (единственный кандидат с P ≥ 0,5 — Б1).

## Карты и выводы шага (sha256 — в `times.txt` строкой того же события)

| файл | что |
|---|---|
| `levels141.py` → `levels141.out.txt`, `levels141.json` | разбор `product_levels.xml` (114 уровней, 10 категорий) и поиск каждого имени по 192 документам (`ROADMAP.md`, `HANDOFF.md`, `env-vars.md`, `CLAUDE.md`, `state-archive.md`, `INDEX.md`, `local-session-*.md`, `next-session-*.md`) |
| `scanscripts141.py` → `scanscripts141.out.txt` | поиск имён уровней по 165 919 малым файлам `C:/kyty` (скрипты, отчёты, json ≤ 2 МБ; без `KytyPS5`, `build`, `scrub`, `tools`) |
| `logscan141.py` → `logscan141.out.txt` | 12 логов последних входов: маркеры смерти `enter_scene.py` (`GpuHangAbort:`, `ErrorDeviceLost`, `Unhandled exception:`), `[Vulkan][E]`, `AsyncPipelines: skipped draw`, `GpuWaitSlow:`, `MainTaskLate:`, командная строка гостя, sha256 |
| `skipscan141.py` → `skipscan141.out.txt` | гистограмма `AsyncPipelines: skipped draw` по кадрам в трёх дымах входа с. 122 |
| `heldscan141.py` → `heldscan141.out.txt` | удержанные неполные флипы, `PriorityStall:`, `[Vulkan][W]`, `SkipCeil` в 6 логах (строка-образец `[Vulkan][W]` `s6s137` вырезана по приватности, sha до/после — в `times.txt`) |
| `prioscan141.py` → `prioscan141.out.txt` | `PriorityStall:` по 12 логам: число, максимум, место |
| `codemap141.py` → `codemap141.out.txt` | якоря дефектов в `src/`, `tests/` по HEAD `00c7264b` (471 отслеживаемый файл) |
| `scenemap141.py` → `scenemap141.md`, `scenemap141.out.txt` | таблица (А) |
| `refs141.py` → `refs141_map.txt` | карта «ссылка файл:строка → текст строки» по всем ссылкам этого документа (общее правило 24(1)); собрана после последней правки документа |

Логи последних входов (sha256 полностью — `logscan141.out.txt`): `C:/kyty/s122/log_{eatl,atl,eght,ght,ednn,dnn,edes,des}122.txt`,
`C:/kyty/s123/log_ght123.txt`, `C:/kyty/s136/log_s6s136.txt`, `C:/kyty/s137/log_s6s137.txt`, `C:/kyty/s137/log_kp137h.txt`. Во всех 12:
`GpuHangAbort:` 0, `ErrorDeviceLost` 0, `Unhandled exception:` 0, `[Vulkan][E]` 0, `GpuWaitSlow:` 0 [c]. Слой валидации присутствовал в
системе во всех (строка `available layer`), включён — по числу `[Vulkan][W]` только в `s6s137` (440 084 строк [c]); в остальных 0 `[Vulkan][E]`
**не** означает прогона с валидацией.

## (А) Карта сцен — 114 уровней

Источник: `C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/data/prein/product_levels.xml`, sha256
`8f50b465ff0856aa4eef79236e933b442294e47f9a97bf691274b9017d8d4fa9`, 31 352 Б; 114 элементов `<Level>`, 114 уникальных `<File>` [c]
(`levels141.out.txt`). **Входили — 8, не входили — 106** [c] (`scenemap141.out.txt`). `SCENE_OK` — 0: ни один вход не проверялся критерием
п. 215(в)(2)(ii) (удержание 300 с есть у 5 сцен, но без видео ≥ 3 000 кадров в том же прогоне и без прогона с валидацией на этой сцене,
кроме Sky Garden). «Держится» ниже значит только «300 с удержания без маркеров смерти в одном логе» — не корректность и не `SCENE_OK`.
Бриф называет 7 входивших; восьмой — `title_controller_ship` (загрузочный путь, перепись с. 113).

| № | категория | имя | файл уровня | вход | свидетельство | исход | сборка последнего входа |
|---|---|---|---|---|---|---|---|
| 1 | Meta | Title | `title_controller_ship` | да | загрузочный путь каждой обычной игры; с. 113 перепись: 4 чистых прогона со сценой (`docs/session-113/census/census_summary.md:12`) | неизвестно (проходной экран, удержание не мерено) | разные (с. 7–113) |
| 2 | Meta | Intro | `intro_next` | да | с. 122 `edes122` (дым 120 с, видео 7 262 кадра, 0 однокадровых глитчей, `C:/kyty/s122/vidglitch_edes122.txt`) и `des122` (удержание 300 с, `C:/kyty/s122/go122a.log:140-142`), лог `C:/kyty/s122/log_des122.txt` sha256 `b78016f2…`: 0 маркеров смерти, 0 `[Vulkan][E]` [c] (`logscan141.out.txt`); с. 113: 75 чистых прогонов (`census_summary.md:11`) | держится (300 с без маркеров смерти) [c] | `2baf8742` (с. 122, `docs/local-session-122.md:140`) |
| 3 | Meta | World Map | `worldmap` | да | с. 67 `d67a` через `KYTY_KEYS` дошёл до `worldmap` (`ps5 em/HANDOFF.md:2878-2879`); с. 45 «космическая карта галактики» (`ps5 em/HANDOFF.md:3916`) — та же сцена [I] | неизвестно (замеров удержания нет) | с. 67 (`1307300`) |
| 4 | Meta | Robot Builder | `robot_builder_next` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 5 | Meta | Interactive Credits | `interactive_credit_00` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 6 | Meta | Non Interactive Credits | `non_interactive_credit` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 7 | Meta | Ending Boss After Credit | `ending_boss_after_credit` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 8 | Meta | Pause Menu (In Game) | `ui_pause_next` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 9 | Meta | Pause Menu (Hub) | `ui_pause_hub` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 10 | Meta | Pause Menu (Simple) | `ui_pause_simple` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 11 | Meta | Pause Menu (Cinematics) | `ui_pause_cinematics` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 12 | Meta | PS Logo | `ps_logo` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); загрузочный путь; имя встречается в переписи с. 113 (`census.csv`), сценой не учтено | не входил | — |
| 13 | Meta | Team Logo | `team_logo` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 14 | Meta | Collectible Viewer | `collectible_viewer` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 15 | Meta | VIP Bots | `bot_character_data` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 16 | Meta | Astro Skin | `astro_skin_data` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 17 | Meta | Controller Skin | `controller_skin_data` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 18 | Meta | Photo Mode UI | `ui_photo_mode` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 19 | Meta | Blueprint UI | `ui_blueprint` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 20 | Meta | Camera Reset UI | `ui_camera_reset` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); по имени — интерфейс или данные, не сцена уровня [I] | не входил | — |
| 21 | Hub | Crashsite | `hub_crashsite` | да | с. 45, прогон 2 пользователя: «стартовали `hub_crashsite` и `underwater_aerial_garden`» (`ps5 em/HANDOFF.md:3959-3960`, `docs/local-session-45.md:87-89`); лога с sha нет | неизвестно | с. 45 (`3fe9b23`) |
| 22 | Hub | Diorama 1 - Gatcha | `hub_crashsite_diorama` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 23 | Hub | Diorama 2 - Controller Ship Skin | `diorama_controller_skin` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 24 | Hub | Diorama 3 - Astro Skin | `diorama_astro_skin` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 25 | Hub | Diorama 4 - Zoo | `diorama_zoo` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 26 | Main Levels | G1 - Aerial Garden | `underwater_aerial_garden` | да | опора, сотни входов (с. 113: 423 чистых прогона, `census_summary.md:14`); последний — с. 137 `kp137h` 300 с, лог `C:/kyty/s137/log_kp137h.txt` sha256 `ff3840d9…`: 0 маркеров смерти, 0 `[Vulkan][E]` [c]; валидация `s6s137` (`dced812b…`): 0 `[Vulkan][E]` [c]; видео `shp128` 4 026 кадров на `9235a7ac` (`docs/ROADMAP.md:6214`) | держится (300 с без маркеров смерти) [c]; заминка кадров ≈ 951–954 (`docs/ROADMAP.md:13007`) | `05431dad` (с. 137); установленная `9235a7ac` — `shp128` с. 128 |
| 27 | Main Levels | G1 - Snowy Canyon | `bumper_enemy_snowy_canyon` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 28 | Main Levels | G1 - Sky Aztec | `spring_punch_sky_aztec` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 29 | Main Levels | G1 - Construction | `booster_construction` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 30 | Main Levels | G2 - Pirate Island | `big_hand_pirate_island` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 31 | Main Levels | G2 - Clock Tower | `mini_astro_clock_tower` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 32 | Main Levels | G2 - Mana Tree | `path_maker_mana_tree` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 33 | Main Levels | G2 - Monster Cave | `spring_punch_monster_cave` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 34 | Main Levels | G3 - Casino | `timestop_casino` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 35 | Main Levels | G3 - Dirty Bath | `sponge_dirty_bath` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); жидкость SPH есть только здесь (`ps5 em/HANDOFF.md:4517-4519`) | не входил | — |
| 36 | Main Levels | G3 - Gulliver | `gulliver_island` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 37 | Main Levels | G3 - Hourglass | `rocket_hourglass` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 38 | Main Levels | G4 - Treasure Cave | `pot_treasure_cave` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 39 | Main Levels | G4 - Giants Garden | `mini_giants_garden` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); запасной уровень плана с. 122, не входил (`C:/kyty/s122/go122a.sh:37-40`) | не входил | — |
| 40 | Main Levels | G4 - Atlantis | `penguin_atlantis` | да | с. 122 `eatl122` (дым 120 с, видео 7 461 кадр, 0 глитчей, `docs/local-session-122.md:145,162-163`; лог `56dde051…`) и `atl122` (300 с, `C:/kyty/s122/go122a.log:156-158`), лог `C:/kyty/s122/log_atl122.txt` sha256 `f6925868…`: 0 маркеров смерти, 0 `[Vulkan][E]` [c] | держится (300 с без маркеров смерти) [c] | `2baf8742` (с. 122) |
| 41 | Main Levels | G4 - Horror Time | `time_stopper_ghost_world` | да | с. 122 `eght122` (видео 4 833 кадра, 0 глитчей; лог `11e2aca3…`), `ght122` (300 с; `51a7f9ea…`); с. 123 `ght123` (300 с, `C:/kyty/s123/go123a.log:64-66`), лог `C:/kyty/s123/log_ght123.txt` sha256 `06d155f0…`: 0 маркеров смерти, 0 `[Vulkan][E]` [c] | держится (300 с без маркеров смерти) [c] | `e4bb66ca` (с. 123, `C:/kyty/s123/FACTS.md:201`) |
| 42 | Main Levels | G5 - Big Tornado | `booster_magic_lamp` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 43 | Main Levels | G5 - Day and Night | `rotating_level_day_and_night` | да | с. 122 `ednn122` (видео 7 431 кадр, 0 глитчей; лог `c6f0674e…`) и `dnn122` (300 с, `C:/kyty/s122/go122a.log:176-178`), лог `C:/kyty/s122/log_dnn122.txt` sha256 `d11e3959…`: 0 маркеров смерти, 0 `[Vulkan][E]` [c]; `hostdev` — `STALL_UNATTRIBUTED` (1 окно простоя GPU, `go122a.log:178`) | держится (300 с без маркеров смерти) [c]; одна неатрибутированная заминка | `2baf8742` (с. 122) |
| 44 | Main Levels | G5 - Iceberg | `ice_iceberg` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); запасной уровень плана с. 122, не входил (`C:/kyty/s122/go122a.sh:37-40`) | не входил | — |
| 45 | Main Levels | G5 - Space Station | `rocket_space_station` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 46 | Main Levels | G5 - Lava Ship | `small_pot_lava` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 47 | Main Levels | G6 - Final Shooting | `final_shooting` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 48 | Main Levels | G6 - Final Stage | `final_stage` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 49 | Secret Levels | G1 - Natural Cave | `spin_drill_natural_cave` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); жидкость SPH есть только здесь (`ps5 em/HANDOFF.md:4517-4519`) | не входил | — |
| 50 | Secret Levels | G1 - Weather Station | `jack_in_the_box` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 51 | Secret Levels | G2 - Light Pickup | `picup_light` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 52 | Secret Levels | G2 - Voxel World | `voxel_world` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 53 | Secret Levels | G3 - Volcano | `volcano_mountain` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); жидкость SPH есть только здесь (`ps5 em/HANDOFF.md:4517-4519`) | не входил | — |
| 54 | Secret Levels | G3 - Graveyard | `light_gadget_graveyard` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 55 | Secret Levels | G4 - Ninja Castle | `shuriken_ninja_castle` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 56 | Secret Levels | G4 - Rocket Pull Chain | `mini_rocket_chain` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 57 | Secret Levels | G5 - Hoover Beach | `hoover_beach` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); жидкость SPH есть только здесь (`ps5 em/HANDOFF.md:4517-4519`); запасной уровень плана с. 122, не входил (`C:/kyty/s122/go122a.sh:37-40`) | не входил | — |
| 58 | Secret Levels | G5 - Path Maker Mix | `bonus_path_maker_mix` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 59 | Secret Levels | FINAL - Party Land | `cymbal_party_land` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 60 | Mini Levels | G1 - Fragile Battle 1 | `fragile_battle_1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 61 | Mini Levels | G1 - Voxel Challenge 1 | `voxel_challenge_1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 62 | Mini Levels | G1 - Armadillo Challenge 1 | `armadillo_challenge_1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 63 | Mini Levels | G2 - Fragile Battle 2 | `fragile_battle_2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 64 | Mini Levels | G2 - Voxel Challenge 2 | `voxel_challenge_2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 65 | Mini Levels | G3 - Fragile Battle 3 | `fragile_battle_3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 66 | Mini Levels | G3 - Voxel Challenge 3 | `voxel_challenge_3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 67 | Mini Levels | G3 - Armadillo Challenge 2 | `armadillo_challenge_2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 68 | Mini Levels | G4 - Fragile Battle 4 | `fragile_battle_4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 69 | Mini Levels | G4 - Voxel Challenge 4 | `voxel_challenge_4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 70 | Mini Levels | G5 - Fragile Battle 5 | `fragile_battle_5` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 71 | Mini Levels | G5 - Voxel Challenge 5 | `voxel_challenge_5` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 72 | Mini Levels | G5 - Genie Challenge | `miniboss_challenge_genie` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 73 | Symbol Levels | G2 - Triangle Palace | `symbol_triangle` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 74 | Symbol Levels | G2 - Triangle Challenge 1 | `symbol_challenge_triangle1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 75 | Symbol Levels | G2 - Triangle Challenge 2 | `symbol_challenge_triangle2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 76 | Symbol Levels | G2 - Triangle Challenge 3 | `symbol_challenge_triangle3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 77 | Symbol Levels | G2 - Triangle Challenge 4 | `symbol_challenge_triangle4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 78 | Symbol Levels | G3 - Circle Palace | `symbol_circle` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 79 | Symbol Levels | G3 - Circle Challenge 1 | `symbol_challenge_circle1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 80 | Symbol Levels | G3 - Circle Challenge 2 | `symbol_challenge_circle2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 81 | Symbol Levels | G3 - Circle Challenge 3 | `symbol_challenge_circle3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 82 | Symbol Levels | G3 - Circle Challenge 4 | `symbol_challenge_circle4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 83 | Symbol Levels | G4 - Square Palace | `symbol_square` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 84 | Symbol Levels | G4 - Square Challenge 1 | `symbol_challenge_square1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 85 | Symbol Levels | G4 - Square Challenge 2 | `symbol_challenge_square2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 86 | Symbol Levels | G4 - Square Challenge 3 | `symbol_challenge_square3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 87 | Symbol Levels | G4 - Square Challenge 4 | `symbol_challenge_square4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`); жидкость SPH есть только здесь (`ps5 em/HANDOFF.md:4517-4519`) | не входил | — |
| 88 | Symbol Levels | G5 - Cross Palace | `symbol_cross` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 89 | Symbol Levels | G5 - Cross Challenge 1 | `symbol_challenge_cross1` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 90 | Symbol Levels | G5 - Cross Challenge 2 | `symbol_challenge_cross2` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 91 | Symbol Levels | G5 - Cross Challenge 3 | `symbol_challenge_cross3` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 92 | Symbol Levels | G5 - Cross Challenge 4 | `symbol_challenge_cross4` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 93 | Symbol Levels | Hub - Final Symbol Challenge | `symbol_challenge_all` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 94 | Boss | G1 - Gorilla | `enemy_gorilla` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 95 | Boss | G2 - Octopus | `enemy_taco` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 96 | Boss | G3 - Snake | `enemy_snake` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 97 | Boss | G4 - Chameleon | `enemy_chameleon` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 98 | Boss | G5 - Bird | `enemy_bird` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 99 | Boss | G6 - Alien | `enemy_final` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 100 | Hero | G1 - Ape Escape | `hero_ape_escape` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 101 | Hero | G2 - Kratos | `hero_kratos` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 102 | Hero | G3 - Drake | `hero_drake` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 103 | Hero | G4 - Loco Roco | `hero_locoroco` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 104 | Hero | G5 - Aloy | `hero_aloy` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 105 | PS5 Builder | G1 - Memory | `ps5_builder_memory` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 106 | PS5 Builder | G2 - SSD | `ps5_builder_ssd` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 107 | PS5 Builder | G3 - GPU | `ps5_builder_gpu` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 108 | PS5 Builder | G4 - Cooling | `ps5_builder_cooling` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 109 | PS5 Builder | G5 - Plate | `ps5_builder_plate` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 110 | DLC | Speed Run Booster | `speedrun_booster` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 111 | DLC | Speed Run Path Maker Ice | `speedrun_pathmaker_ice` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 112 | DLC | Speed Run Spring Punch | `speedrun_springpunch` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 113 | DLC | Speed Run Inflator | `speedrun_inflator` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |
| 114 | DLC | Speed Run Big Hand | `speedrun_bighand` | нет | в документах и харнессах входа нет (`levels141.out.txt`, `scanscripts141.out.txt`) | не входил | — |

## (Б) Список дефектов

Классы п. 215(д)(2)(Б). «Свидетельство» — по HEAD (карта `refs141_map.txt`). p на вход — [c] с источником или [I] с основанием.
Критерий — п. 215(в)(2)(i): для крэша/зависания — серия N ≥ ln 0,05 / ln(1 − p) входов без повтора; для картинки — видео-проход
≥ 3 000 кадров с 0 глитчей `s51_vidglitch.py` и просмотренным листом + прогон с валидацией с 0 `[Vulkan][E]`.

| № | класс | дефект | статус | свидетельство | сцены | цена воспроизведения | критерий доказательства | P(≤ 2 сессии) [I] |
|---|---|---|---|---|---|---|---|---|
| Б1 | K2 | зависание ВХОДА в обходе BVH `380bb9d6…` (GPU-сторона); ограничитель `KYTY_BVH_LOOP_CAP` ВКЛ с с. 103, 0 из 67 входов, серия печатью не принята (хвост обходов 4 097…65 536 шагов); ещё 12 BVH-программ, OIT resolve `657ad046…` и хэш-пробы без предела | частично | `docs/ROADMAP.md:12899`, `docs/ROADMAP.md:12941`; ограничитель — `src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h:26-27` | Sky Garden [c]; остальные [U] | вход ≈ 15–20 с до сцены (`C:/kyty/s122/go122a.log:15`); p = 0,0667 на вход без ограничителя [c, с. 76 по `docs/ROADMAP.md:12941`]; с ограничителем p ≤ 0,044 (верх 95 % при 0/67, [c-арифм.]); пользователь не нужен | серия N ≥ ln 0,05 / ln(1 − 0,0667) = 44 входа без зависания на установленной сборке по правилу «эпизод против установившегося режима», записанному до серии (0/67 с. 103 такому N уже равны по числу, но не приняты печатью — нужен именно принятый порядок) | 0,5: механизм уже отгружен, не хватает принятой серии и видео-прохода со сработавшим ограничителем (`docs/ROADMAP.md:12899`, колонка цены) |
| Б2 | K2 (заминка ≈ 0,2 с; см. В1) | `STALL_UNATTRIBUTED` на кадре ≈ 951–954 Sky Garden: 183 / 194 / 194,6 мс в трёх прогонах на трёх сборках; «событие сцены [I]»; на `dnn122` — одна неатрибутированная заминка (окно простоя GPU) | открыт (происхождение [U]) | `docs/ROADMAP.md:13007`; `C:/kyty/s122/go122a.log:178` | Sky Garden, Day and Night [c] — 2 | ≈ 35 с игры на вход (кадр ≈ 951 при ~30 кадрах/с [I]); p ≈ 1 на Sky Garden (3 из 3 названных прогонов [c по документу]); пользователь не нужен | если исправимо — N ≥ ln 0,05 / ln(1 − 0,9) = 2 входа без заминки ≥ 100 мс на кадрах 900–1 000 (p = 0,9 — консервативно к 3/3) | 0,2: не доказано, что это дефект эмулятора, а не работа игры (загрузка содержимого сцены); сначала атрибуция |
| Б3 | K2 | ожидание неподанного тика: поток приоритетных операций ждал тик записываемого буфера 2,975 с, GPU простаивал (`vbn113k`, 1 событие; в `vbn113m`/`vid113` не повторилось); родственные ожидания > 50 мс с `unsub=1` — в 5 из 12 логов (1 / 5 / 2 в дымах `eatl`/`eght`/`ednn122`, ≥ 64 в валидационных `s6s136`/`s6s137`; 0 в запечатанных 300-с прогонах) [c] | открыт | `docs/ROADMAP.md:12916`; место — `src/graphics/host_gpu/renderer/commandScheduler.cpp:641-658` (строки обрезаны на 64, `:654`); `prioscan141.out.txt` | Sky Garden (3 с) [c]; ожидания > 50 мс — Sky Garden, Atlantis, Horror Time, Day and Night [c] | 3-с форма: p на вход [I] ≤ 1/3 (1 из 3 названных прогонов), нужен принудительный OLD (`docs/ROADMAP.md:12916`); ожидания > 50 мс: 5/12 логов, все — с записью видео или валидацией [c] ⇒ связь с инструментом не исключена | для 3-с формы p не измерено ⇒ N не вычисляется до переписи частоты; предложенный фикс — подача буфера перед сном GuestGpu (`docs/ROADMAP.md:12916`) | 0,15: частота неизвестна, видимость ожиданий > 50 мс на кадре [U] |
| Б4 | K1 (при выходе; см. В2) | гонка выхода: `EmergencyShutdown` → `CloseAll` против гостевого `KernelOpen` в полёте ⇒ `EXIT_IF` после `Event: quit` | открыт | `docs/ROADMAP.md:13014`; `src/kernel/fileSystem.cpp:207` (`EXIT_IF(m_files[index] == nullptr)`) | любая (выход) | 1 из 347 логов [c по документу] ⇒ p ≈ 0,0029 на выход | N ≥ ln 0,05 / ln(1 − 0,0029) ≈ 1 032 выхода — непрактично; доказательство критерием (i) недостижимо без ускоренного стенда выхода | 0,1 |
| Б5 | K3 (видимость не доказана; см. В4) | первый (холодный) вход нового уровня: `AsyncPipelines` пропускает draw, пока пайплайн компилируется, и держит неполные флипы; **документ с. 122 ошибся:** не «20 строк на одном кадре», а 1 320 строк на 14 кадрах 193–336 (`eatl122`), 762 на 69 кадрах 255–856 (`eght122`), 185 на 11 кадрах 221–231 (`ednn122`) [c]; удержанных флипов 14 / ≥ 64 / 11 [c]; в тёплых запечатанных прогонах тех же уровней — 0 [c]; seed шейдеров покрывает интро, пустыню и Sky Garden | открыт | ошибка — `docs/local-session-122.md:165-166`; механизм — `src/graphics/host_gpu/renderer/renderDraw.cpp:4439-4455`, `src/graphics/presentation/videoOut.cpp:1199-1203` (лог удержаний обрезан на 64), `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:221-228`; seed — `docs/ROADMAP.md:12900`; `skipscan141.out.txt`, `heldscan141.out.txt` | 3 из 3 впервые входивших уровней [c]; вероятно все 106 невходивших [I] | один холодный вход ≤ 120 с на уровень, p = 1 на холодный вход (3/3 [c]); пользователь не нужен | холодный вход (кэш пайплайнов без уровня) с 0 строк `AsyncPipelines: skipped draw` и 0 удержанных флипов, плюс видео-проход и валидация по (в)(2)(i); N ≥ ln 0,05 / ln(1 − 0,9) = 2 холодных входа на уровень | 0,55: вероятный фикс — расширение seed (с. 104 уже делала для трёх сцен), без правки транслятора; цена — входы на каждый уровень seed |
| Б6 | K3 | «падающие частицы»/дым в комнате с пришельцем — не проверены | открыт (не проверен) | `ps5 em/HANDOFF.md:4622-4623` | `intro_next` (катсцена) | ≈ 185 с от старта обычной игры (катсцена интро, `ps5 em/HANDOFF.md:4522`) [I]; нужен ли пользователь — нет, если путь интро идёт без ввода [I] | видео-проход ≥ 3 000 кадров катсцены с 0 глитчей и листом + валидация | 0,3: неизвестно, есть ли дефект |
| Б7 | K4 | `V_MUL_LEGACY_F32` / `V_FMAC_LEGACY_F32` не декодируются: при встрече — EXIT «VOP2 opcode is not implemented» (скрытый K1 на новой сцене) | открыт | `ps5 em/HANDOFF.md:4634-4635`; `src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp:1475`; в `src/` имени опкода нет [c] (`codemap141.out.txt`) | 0 известных; невходившие [U] | маркер ловится любым входом нового уровня (перепись (Г)) | вход сцены, где опкод встретился, без EXIT + видео | 0,5 при встрече (декод по спецификации), 0 без встречи |
| Б8 | K4 | паттерн `exec ? new : old` исправлен только на верхнем уровне PS; в compute и внутри ветвлений остаётся | открыт | `ps5 em/HANDOFF.md:4629-4631` | 0 известных проявлений | не воспроизводится; нужен шейдер-свидетель | тест транслятора + видео сцены-свидетеля | 0,2 |
| Б9 | K4 | 116 неразрешённых импортов (Json2 26, VoiceChat 17, …), ни один не вызывался | открыт | `ps5 em/HANDOFF.md:7726-7727`; маркер — `src/loader/runtimeLinker.cpp:1214` | 0 известных вызовов | маркер `=== Stubbed function` любым входом нового уровня | 0 строк маркера на входах переписи | — (дефекта нет, пока не вызван) |
| Б10 | K4 | нет PCF в ручном сравнении глубины | открыт | `ps5 em/HANDOFF.md:7727` | [U] | [U] — нужен кадр-свидетель | видео тени сцены-свидетеля | 0,2 |
| Б11 | K4 | `shader_cfg_tests`: два давних падения `IMAGE_SAMPLE_C` (ждёт `OpImageSampleDrefImplicitLod`) и `IMAGE_SAMPLE_C_LZ` (явный LOD dref) — возможный пробел трансляции сравнения глубины | открыт | `tests/shaderCfgTests.cpp:5385`, `tests/shaderCfgTests.cpp:5394`; `C:/kyty/s136/step5a3/tests_run.log:86-87` (sha256 `b50929d4…`) | [U] | без игры: сборка и прогон тестов | тест проходит + видео сцены с тенями | 0,4 |
| Б12 | K4 | дыра `bdastamp`: регион 4 МиБ на два отображённых диапазона обходится только для нижнего — грязные страницы буфера в верхнем не собираются BDA-обходом | открыт | `docs/ROADMAP.md:12915` | [U] (в `vid112` раскладок не найдено) | выгрузка отображённых диапазонов, без игры по логам нет | фикс + проверка раскладок на сцене переписи | 0,3 |
| Б13 | K4 | порядок эпох `ChangeState<Cpu,true>` (`m_cpu_epoch` раньше `m_epoch`): окно, в котором трёхэпохальный кэш пропускает регион | открыт | `docs/ROADMAP.md:12920` | [U] | не воспроизводится | правка порядка + серия без регрессии | 0,35 |
| Б14 | K4 | траектория `rtskip=1` значениями не сверяется (цепочка пропущенных draw проверена индукцией через режим 2 + видео + валидацию, только на опоре); на новых сценах не проверялась | открыт | `docs/ROADMAP.md:12993` | все, кроме Sky Garden [U] | самопроверка `rtskip=2` на сцене ≤ 300 с | 0 расхождений `rtskip=2` + видео на каждой сцене переписи | 0,4 |
| Б15 | K5 | `resource_tracking_tests` падает с с. 60 (лог побайтно тот же, 1 478 Б) | открыт | `ps5 em/HANDOFF.md:2848` | — | без игры | тест проходит | 0,5 |
| Б16 | K5 | список «14 падающих тестов» `HANDOFF` §4 устарел: эталон `shader_cfg_tests` — 0 падений с с. 24, фактически 2 (Б11); в `tests_run.log` с. 136 — 5 строк со словом `failed` (86, 87, 107, 119, 120) [c], ожидаемость трёх последних не проверена | открыт | `ps5 em/HANDOFF.md:7710-7717`; `C:/kyty/s136/step5a3/tests_run.log:107`, `:119-120` | — | без игры | список заменён фактом прогона на HEAD | 0,8 |
| Б17 | K5 | `KYTY_GPU_CHECKPOINTS=1` сам вешает вход (`hg97a`) | открыт | `docs/ROADMAP.md:12940` | Sky Garden | вход при переменной | — (обход: `KYTY_GPU_MARKERS=2`) | 0,3 |
| Б18 | K5 | падение старта под `--rd`: `commandRecorder.cpp:326` (проверка одного производителя рекордера), гонка | открыт | `docs/ROADMAP.md:12963`; `src/graphics/host_gpu/renderer/commandRecorder.cpp:326`; положительный контроль — `ps5 em/docs/env-vars.md:136-137` | старт (режим `--rd`) | p [U]; повтор прошёл | серия стартов под `--rd` по N от измеренного p | 0,3 |
| Б19 | K5 | класс «первый символ» у флагов окружения (`value[0] != '0'`: `false`/`off` читаются как ВКЛ) — 57 мест [c] | открыт | `docs/ROADMAP.md:12964`; пример — `src/graphics/host_gpu/renderer/cache/bufferCache.cpp:54`; `codemap141.out.txt` | — | без игры | замена на `Common::EnvFlagOn` (`src/common/envFlag.h:10`) | 0,7 |
| Б20 | K5 | печати не покрывают `enter_scene.py` и `s51_vidglitch.py` — два инструмента доказательства под (B) | открыт | `docs/ROADMAP.md:12919` | — | без игры | оба файла в SEALS каждой печати под (B) | 0,8 |
| Б21 | K5 | вход через `-lvl` приводит не в ту точку сцены, что ручная игра; `KYTY_KEYS` и вердикт по скриншоту ненадёжны — `SCENE_OK` проверяет только точку `-lvl` | открыт (ограничение) | `ps5 em/HANDOFF.md:2834-2843`, `ps5 em/HANDOFF.md:2878-2879`, `ps5 em/docs/env-vars.md:137-138`, `ps5 em/CLAUDE.md:223` | все | — | — (ограничение критерия, не фикс) | — |
| Б22 | K5 | устаревшие утверждения в документах: «NGG пропускается» (`HANDOFF.md:7727`) против `renderDraw.cpp:2383-2384` (GS/NGG — путь mesh-шейдеров, по умолчанию ВКЛ); комментарий `pm4Handlers.cpp:3832-3833`; §1 п. 6a `HANDOFF.md:4618` «небо открыто» против закрытия с. 32 (`HANDOFF.md:4251`); «20 строк» `local-session-122.md:165-166` (Б5) | открыт | `ps5 em/HANDOFF.md:7727`, `src/graphics/host_gpu/renderer/renderDraw.cpp:2383-2384`, `src/graphics/guest_gpu/command_processor/pm4Handlers.cpp:3832-3833`, `ps5 em/HANDOFF.md:4618`, `ps5 em/HANDOFF.md:4251` | — | без игры | правка текста | 0,9 |
| Б23 | K5 | `protceil=1` вешает GPU (TDR 2 из 2); значение выведено из употребления | открыт (обойдён) | `docs/ROADMAP.md:12998` | Sky Garden | — | — | — |

**Закрытые (для полноты, не ранжируются):** крэш PS `0x1974` — с. 30 (`ps5 em/HANDOFF.md:4269`); небо пустыни — с. 32 (`ps5 em/HANDOFF.md:4251`);
GS веер/restart — с. 47 (`ps5 em/HANDOFF.md:3872-3874`); NaN и исчезновение листвы (CMASK) — с. 49 (`ps5 em/HANDOFF.md:3805-3806`); DeviceLost
от кэша пайплайнов драйвера — с. 57 (`ps5 em/HANDOFF.md:3404-3405`); зависание входа Sky Garden, `acopyidle=1` — с. 58 (`ps5 em/HANDOFF.md:3314`);
NID `strcmp`/`strncmp` — с. 67 (`ps5 em/HANDOFF.md:2815-2816`); «наличие вместо значения» — с. 102–103 (`docs/ROADMAP.md:12950`, `docs/ROADMAP.md:12964`);
seed шейдеров — с. 104 (`docs/ROADMAP.md:12900`). Кандидат `sky2` (один однокадровый) — переход при перелёте корабля, не дефект
(`ps5 em/HANDOFF.md:3408-3409`).

**Не инвентаризованы поштучно (класс вне цели (B)):** строки §7 трека скорости — мутанты скореров, ручки ABBA, цены инструментов, припаркованные
`bindlean`/B2/`armcopy`/A-walker (`docs/ROADMAP.md:12846-13035`, 190 строк [c]; последняя строка — с. 134, долги с. 135–140 в §7 не внесены [c]).
Корректность пакета `bindlean` и B2 не заявляется (долги `docs/ROADMAP.md:13029`, `docs/ROADMAP.md:13033`) — они вне умолчаний установленной сборки.

## (В) Ранжирование по правилу п. 215(д)(2)(В) — предложение, не решение

Ключ 1 — K1/K2 на входе или удержании любой сцены > K3 > K4 > K5; ключ 2 — число затронутых сцен [c]; ключ 3 — цена; равенство — по P.

| место | строка | почему здесь |
|---|---|---|
| 1 | Б2 `STALL_UNATTRIBUTED` (K2-заминка) | K2 на удержании, 2 сцены [c], ≈ 35 с на вход |
| 2 | Б1 зависание входа BVH | K2 на входе, 1 сцена [c], p 0,0667 без ограничителя; P 0,5 — наибольшая в классе |
| 3 | Б3 ожидание неподанного тика | K2 на удержании, 1 сцена [c] (3-с форма), цена выше Б1 (p [I] ≤ 1/3 при принудительном OLD) |
| 4 | Б5 холодный вход: пропуск draw и удержание флипов | K3, 3 сцены [c]; p = 1 на холодный вход, ≤ 120 с |
| 5 | Б6 частицы интро | K3, 1 сцена |

Б4 (K1 при выходе) правилом не покрыт — «на входе или удержании» к выходу не относится; если лид отнесёт его к ключу 1, он встаёт на место 4
(1 сцена «любая», цена ≈ 1 000 выходов на доказательство). **Если заминки < 1 с не K2 (В1),** порядок: 1 — Б1, 2 — Б3, 3 — Б5, 4 — Б2 (как K3),
5 — Б6. По P(≤ 2 сессии): Б1 0,5 и Б5 0,55 — единственные строки верха с P ≥ 0,5 [I].

## (Г) Вариант «перепись сцен» для с. 142

До 10 невходивших уровней, по одному входу `-lvl` на установленной `9235a7ac`, удержание ≤ 120 с, `--rec`, кэш пайплайнов как есть
(холодный для этих уровней — это же воспроизводит Б5). Рецепт — `ps5 em/docs/env-vars.md:697-710` и `C:/kyty/s140/enter_scene.py`
(маркеры смерти — `enter_scene.py:93`, гостевая строка — `:568`; sha256 `e53bb33e…`). Порядок — по разнообразию механизмов:

| № | уровень | почему |
|---|---|---|
| 1 | `bumper_enemy_snowy_canyon` | первый основной уровень G1, снег |
| 2 | `big_hand_pirate_island` | основной G2 |
| 3 | `timestop_casino` | основной G3 |
| 4 | `mini_giants_garden` | основной G4, запасной план с. 122 (`C:/kyty/s122/go122a.sh:37`) |
| 5 | `ice_iceberg` | основной G5, запасной план с. 122 (`C:/kyty/s122/go122a.sh:40`) |
| 6 | `sponge_dirty_bath` | жидкость SPH с ненулевыми частицами (`ps5 em/HANDOFF.md:4517-4519`) — путь, ни разу не исполнявшийся с частицами |
| 7 | `hoover_beach` | SPH; запасной план с. 122 (`C:/kyty/s122/go122a.sh:39`) |
| 8 | `volcano_mountain` | SPH, вулкан |
| 9 | `voxel_world` | воксельная геометрия |
| 10 | `enemy_gorilla` | босс G1 (вход босса через `-lvl` не проверен [I]) |

**Цена:** дым входа с. 122 занимал 141–162 с стены от старта до вердикта при удержании 120 с (`C:/kyty/s122/go122a.log:28-29`, `:92-93`) [c] ⇒
10 входов ≈ 25–30 мин игры на экране пользователя [I] (+ ожидания шлюза `procload`); пользователь не нужен. **Что читается:** вход (да/нет, время),
маркеры смерти, `VOP2 opcode is not implemented` (Б7), `=== Stubbed function` (Б9), `AsyncPipelines: skipped draw` и удержанные флипы (Б5),
`PriorityStall:` (Б3), однокадровые глитчи `s51_vidglitch.py` и лист. **Чего не даёт:** `SCENE_OK` (нужно 300 с и прогон с валидацией —
≈ 342 с стены на вход, `C:/kyty/s122/go122a.log:140-141` ⇒ ≈ 57 мин на 10 [I]); доказательства корректности.

## (Д) Заметка `inventory_B_notes.md` построчно (sha256 `ec509375…`)

| строка заметки | вердикт |
|---|---|
| 7: уровней 114 | подтверждено [c] (`levels141.out.txt`) |
| 8: `intro_next`, десятки входов; `edes122` 32,5 с, 0 глитчей, `local-session-122.md:186` | подтверждено: `docs/local-session-122.md:186`, `C:/kyty/s122/go122a.log:93`; 0 глитчей — `vidglitch_edes122.txt`; «десятки» — 75 чистых прогонов с. 113 (`census_summary.md:11`) |
| 9: Sky Garden «с. 47+» | поправлено: первый вход — с. 45 (`ps5 em/HANDOFF.md:3959-3960`) |
| 9: `worldmap` — с. 45 вручную; с. 67 `d67a` | с. 67 подтверждено (`ps5 em/HANDOFF.md:2878-2879`); с. 45 — только «космическая карта галактики» (`ps5 em/HANDOFF.md:3916`), тождество со сценой `worldmap` [I] |
| 9: `hub_crashsite` (с. 45, замеров нет) | подтверждено (`ps5 em/HANDOFF.md:3959-3960`, `docs/local-session-45.md:87-89`) |
| 10–11: три уровня по одному входу с. 122, `local-session-122.md:143-163`; `ght123` | поправлено: по ДВА входа в с. 122 (дым 120 с и запечатанный 300 с, `C:/kyty/s122/go122a.log:29,42,49,157,167,177`) + `ght123` (`C:/kyty/s123/go123a.log:65`); `docs/local-session-122.md:143-148` подтверждено |
| 12: рецепт `KYTY_GUEST_ARGS="-lvl <имя>"`, `env-vars.md:697-709`; `enter_scene.py` | подтверждено (`ps5 em/docs/env-vars.md:697-710`; копия `C:/kyty/s140/enter_scene.py`) |
| 13: `enter_scene.py:92-93, 533`; `HANDOFF.md:2834-2843` | частично: `FAILURES` — `:93` (копия с. 140), `:533` неверно (там `--level`) — гостевая строка на `:568` (копия с. 140); в копии с. 122 — `C:/kyty/s122/enter_scene.py:534`; `ps5 em/HANDOFF.md:2834-2843` подтверждено |
| 14: `KYTY_KEYS` ненадёжен `HANDOFF.md:2878`; сдвиг `@present` `env-vars.md:137`; `load_test` по скриншоту ненадёжен | подтверждено (`ps5 em/HANDOFF.md:2878-2879`, `ps5 em/docs/env-vars.md:137-138`, `ps5 em/CLAUDE.md:223`) |
| 15: `_SaveData/.../memory.bin` от `sav67a`; `KYTY_SAVE_PERSIST=1`; опции `-worldmap`… `HANDOFF.md:2914` | подтверждено (`ps5 em/HANDOFF.md:2814`, `ps5 em/HANDOFF.md:2805`, `ps5 em/docs/env-vars.md:726`, `ps5 em/HANDOFF.md:2914-2915`); содержимое файла сохранения не описано — верно |
| 18–19: закрытые (0x1974 с. 30 … seed с. 104) | подтверждено все девять — абзац «Закрытые» выше |
| 20–21: BVH 6,67 %, `KYTY_BVH_LOOP_CAP`, 0/67, 12 программ, OIT, хэш-пробы; GPU-сторона; `KYTY_GPU_CHECKPOINTS=1` | подтверждено (`docs/ROADMAP.md:12899`, `:12940`, `:12941`) |
| 22: `vbn113k`; `bdastamp` «с. 53/113»; `ChangeState` | подтверждено (`docs/ROADMAP.md:12915`, `:12916`, `:12920`) |
| 23: `--rd` `commandRecorder.cpp:326`; гонка выхода `fileSystem.cpp:207`; `STALL_UNATTRIBUTED` 951–954 | подтверждено документом и кодом HEAD (`docs/ROADMAP.md:12963`, `:13014`, `:13007`; `src/graphics/host_gpu/renderer/commandRecorder.cpp:326`, `src/kernel/fileSystem.cpp:207`) |
| 24: `AsyncPipelines: skipped draw` ≈ 20 строк на кадре входа | **вычеркнуто как неверное:** 1 320 / 762 / 185 строк на 14 / 69 / 11 кадрах [c] (Б5); источник ошибки — `docs/local-session-122.md:165-166` |
| 24–26: `exec ? new : old`, `V_MUL_LEGACY_F32`, NGG пропускается, нет PCF, 116 импортов, частицы (`HANDOFF.md:4622, 4629-4635, 7725-7727`) | подтверждено, кроме «NGG пропускается» — **вычеркнуто как устаревшее** (`src/graphics/host_gpu/renderer/renderDraw.cpp:2383-2384`) |
| 26: `resource_tracking_tests` падает с с. 60 (`HANDOFF.md:2848`) | подтверждено |
| 27: последний полный лог с 0 `[Vulkan][E]` — `s6s136`; 10 известных предупреждений `out_mrt_1` | поправлено: позже — `s6s137` (0 `[Vulkan][E]` [c]); «10 предупреждений» — число с. 59 (`ps5 em/HANDOFF.md:3471`), в `s6s137` строк `[Vulkan][W]` 440 084 [c], состав не разобран |
| 28: глитчей на Sky Garden, пустыне и трёх уровнях не находилось; `sky2` (`HANDOFF.md:3408`) | подтверждено (`vidglitch_e*122.txt`; `ps5 em/HANDOFF.md:3408-3409`) |
| 31–34: инструменты; `kv136`/`kw136` 3 549; `shp128` 4 026 | подтверждено `docs/ROADMAP.md:10423`, `docs/ROADMAP.md:6214`; список самопроверок построчно не проверялся — не цитировать как проверенный |
| 37–38: §7 ≈ 190 строк, с. 135–140 не дописаны; долги корректности; Д5…Д14 — `bindlean` | подтверждено: 190 строк [c], последняя — с. 134 (`docs/ROADMAP.md:13032-13035`) |
| 41: список 14 устарел; с с. 45 два падения; 5 строк `failed` побайтно одинаковы в с. 130–136 | первые два — подтверждено (`ps5 em/HANDOFF.md:7710-7717`, `C:/kyty/s136/step5a3/tests_run.log:86-87`); побайтная одинаковость с. 130–136 **не проверена** (читался только лог с. 136) |

## Вопросы лиду (константы п. 215 исполнитель не меняет)

- **В1.** Заминка < 1 с (Б2 ≈ 0,2 с) — K2 «зависание» или K3? От ответа зависит место 1 ранжирования.
- **В2.** K1 вне входа и удержания (Б4, выход) — ключ 1 или после K3?
- **В3.** Знаменатель «из 114» включает 12 элементов, по имени не сцены (`ui_*` ×7, `*_data` ×3, `ps_logo`, `team_logo`) [I]: `SCENE_OK` для них,
  вероятно, недостижим; оставлять ли их в знаменателе — решение лида.
- **В4.** Б5 — K3 (удержанные флипы — видимая заминка входа [I]) или K4 (видимость не доказана: однокадровый детектор многокадровое удержание
  не ловит)?

## Не заявляется

60 FPS; что (B) ускоряет игру или сохраняет её скорость; что какая-либо сцена корректна, проходима до конца или `SCENE_OK` («держится» — 300 с без
маркеров смерти в одном логе); что инвентарь полон (106 уровней не входили, логи до с. 122 поштучно не сканировались); ни одно число прошлых сессий —
не выигрыш и не потолок; корректность пакета `bindlean` и B2; 47,98 % — не время `9235a7ac`.
