# M2b (`HPP-839`, трек M): темы HLE волны 1 — T265, T272, T231 под ручками `KYTY_M_<тема>`

Исполнитель — Emu Engineer, 2026-10-12 (UTC по `times.txt`). Решения и константы — `ROADMAP.md` п. 756(в)(2) (KytyPS5 `f7208cda`),
правила отчёта — п. 758(б). Игра не запускалась, замок не брался; стенд — без игры. **Код собран, не установлен, в игре не проверен —
WIP до ревью и M3.**

## 1. Итог

| Тема | `=0`: отказ воспроизведён (стенд) | `=1`: ответ по upstream | Мутанты (`=1`) |
|---|---|---|---|
| **T265** ID файлов AMPR | **да** [c стенда]: 5 из 5 настоящих пар `/app0/` пакета с равным 31-битным FNV-1a — у A и B один ID, API ID отдаёт для ID пути A размер B (`keep_a=0`; пара 0 — размер каталога 0 вместо 2 883 584) | 5 из 5: разные ID (1…10), размер и stat A по ID A, повторное разрешение сохраняет ID | `t265_full` пойман (0 из 5), `t265_part` (счётчик не растёт) пойман (0 из 5) |
| **T272** `scePadGetTriggerEffectState` | **да** [c стенда]: после эффектов `mode 1`/`mode 2` и хода курков 192/64 ответ `0,0` (upstream `2,4`); совпали с тестом upstream 3 из 45 проверок | 45 из 45 проверок теста upstream `TestTriggerEffectState` (`3c62359e`, без двух строк настройки интенсивности — её нет в нашем дереве) | `t272_full` пойман (42 из 45 не совпали), `t272_part` (без защёлки выстрела) пойман (шаги 7, 8, 9, 11) |
| **T231** `sceFont` > 128 px | **да** [c стенда]: 10 из 10 глифов шрифта игры `LevelNameFont.otf` при `SetScalePixel` 310 выходят ≤ 128 × 128 (масштаб зажат 128 px по высоте ascent−descent), эталон крупнее — напр. `S` 62×90 при эталоне 172×248, `W` 126×85 при 349×235 | 10 из 10: размер образа, рамка чернил, сумма пикселей и высота метрики = эталону upstream (stb_truetype этой сборки, `ScaleForMappingEmToPixels(310)`, растр по своей ширине) | `t231_full` пойман (0 из 10), `t231_part` (только `f96a14a0`, буфер 128 — «полосы») пойман (0 из 10; образ 128×128, чернила обрезаны) |

Слово «обрезан 128 px» п. 756(в)(2)(i) у нас буквально так: при `=0` высота пикселя зажата в 8..128 и глиф растрируется **целиком, но в
масштабе ≤ 128 px** (в 2,7 раза меньше эталона при 310); обрезание полосами — это половина порта без `58978d15` (мутант `t231_part`).
Семантика масштаба `sceFont` консоли — [I] (как в описи M1a).

## 2. Код (KytyPS5)

| Где | Коммит | Что |
|---|---|---|
| worktree `C:/kyty/m657/m2/wt` | `8a717ac0` (родитель `0361b202` M2a) | код под ручками + стенд, 7 файлов |
| `main` | `274ee39a` (родитель `ef097c75`) | то же; строки `+`/`−` диффов равны (`PATCH_EQUAL`, 853 строки `git show`) |

Файлы: `src/libs/libAmpr.cpp` (T265), `src/libs/controller.cpp`, `src/libs/controller.h`, `src/libs/libPad.cpp` (T272),
`src/libs/libFont.cpp` (T231), `CMakeLists.txt` (цель `m_wave1_hle_stand`, `EXCLUDE_FROM_ALL`), `tests/MWave1HleStand.cpp`.
Патч — `patch_m2b.py` (якоря целыми строками, каждый ровно 1 раз; `ALL OK` на обоих деревьях). У рабочей копии `main` файл
`libPad.cpp` до патча был в CRLF при LF в `HEAD` (первый `git diff` — 911 строк); приведён к LF до коммита, в коммите только 5 строк.

- **Ручки:** `KYTY_M_T265`, `KYTY_M_T272`, `KYTY_M_T231`, умолчание 0, `Common::EnvValueOn`, чтение один раз на процесс (статическая
  локальная), строка журнала `MT265: mode=` / `MT272: mode=` / `MT231: mode=` при первом чтении (T272 — в `Controller::Initialize`, до
  потоков гостя; T265 — первый `ResolveOnePath`, вне `g_mutex`; T231 — первый вызов метрик/растра). Таблицы `Gate`/`Knob` не тронуты.
- **`=0` = FS15:** все пути `=1` — новые ветви под ручкой; при `=0` исполняется прежний код (единственная правка исполняемой при `=0`
  строки — лишний аргумент `image_m231` в `init_image`/`init_stb_image`, ветвь с ним только при `MT231On()`). Подпись трансляции не
  меняется (`src/libs/**` вне набора подписи) — холодного входа M2b не добавляет.
- **Строки журнала, читаемые скриптами (п. 756(б)(4)):** ни одна прежняя строка не изменена и не удалена (`PadTriggerEffect:`,
  `APR resolve missing path:`, строки `handle = …, w = …, h = …` сохранены); добавлены только `MT265:`, `MT272:`, `MT231:`.

### 2.1 Новое состояние: где ставится и снимается

- **T265** `g_m265_next_file_id` (`libAmpr.cpp:77`, процессная статическая): растёт только в `ResolveOnePath:259` под `g_mutex` при
  вставке нового пути при `=1`; не снимается (как у upstream — ID живут весь процесс); при `0xffffffff` — `ENFILE` в кэш пути
  (`:257`). Локальная `m265` (`:220`) — копия ручки на вызов.
- **T272** `m_m272_effect`, `m_m272_state[2]` (`controller.cpp:693–694`, поля `GameController`): пишутся только при `=1` и только под
  `m_mutex` — `SetTriggerEffect` (`:1355–1365`, после проверки обеих команд — отвергнутый запрос кэш не трогает), `Axis` (`:1080–1083`,
  каждое событие курка), `ResetInputState` (`:1231–1232`), сброс при смене активного пада `CheckActive` (`:1021–1025`, вызывается под
  `m_mutex` из `Connect`/`Disconnect`). Читаются `GetTriggerEffectStateM272` (`:1323–1324`, под `m_mutex`). Живут с объектом
  `GameController`. **Новое при `=1`:** `SetTriggerEffect` берёт `m_mutex` на потоке гостя и при `KYTY_FIX_B24=1` (раньше на этом пути
  замка не было). Под `m_mutex` вызовов SDL при `B24=1` нет, кроме `ReleaseHostPads` на выходе (`SDL_Delay` ≤ `RELEASE_FLUSH_MS`) —
  ожидание возможно только на выходе [c кода]; на ревью.
- **T231** `FontState::fallback_image_m231` (`libFont.cpp:200`), `GlyphState::image_m231` (`:222`) — `std::vector`, живут с объектом
  (`new … {}` / `delete`), заполняются только при `=1` в `init_stb_image:908–935`. **Как у upstream:** `trans_image.address` шрифта
  указывает в вектор, следующий растр того же шрифта может его перевыделить — указатель из прошлого `FontRenderResult` после следующего
  вызова не действителен (при `=0` буфер — постоянный массив) [c кода; поведение консоли — I]; на ревью.

## 3. Стенд `m_wave1_hle_stand` (без игры)

Исходники эмулятора этой сборки линкуются (не копируются); вызовы — через `SymbolDatabase` по NID, как их зовёт игра
(`w5fcCG+t31g`, `ApkYaHb8Sek`, `WvEu7yl3Ivg`; `znaWI0gpuo8`; `KXUpebrFk1U`, `N1EBMeGhf7E`, `L97d+3OgMlE`, `gdUCnU0gHdI`,
`3G4zhgKuxE8`). Драйвер и читатель — `run_stand_m2b.py` (члены записаны в его заголовке до прогона):

- **t265:** пакет `games/PPSA21564-app` монтируется как `/app0` (только resolve/stat/size). Пары — `pairs_t265.py`: 158 205 путей
  (файлы и каталоги), 5 пар с префиксом `/app0/` (одна — файл/каталог) и 5 с `app0/` — **= числу описи M1a**. Формы `app0/` (без
  ведущей косой) не разрешаются вообще (`rc=-1`, ENOENT) при `=0` и `=1` — справка, не член. Пары `/app0/`:
  `atlantis_crown_a_base_ao.gnfp`/каталог `enemy_bird/layers/ui_layer`, `sea_ship_barrel_01_break_horizontal_fx.skel`/`F8B47AF2…anim`,
  `hourgrass_sandfall_a_art_test_anim_idle.anim`/`wildlife_snow_turtle_attachment_tree.pfbhk`, `6FFF9D5E…anim`/`construction_parts_gpu_v2…anim`,
  `enemy_hand_ghost_anim_mat.anim`/`nx_ui_worldmap_bot_icon~~159.odxb`. Встречаются ли обе стороны пары в одном запуске игры — [U].
- **t272:** SDL с выключенными драйверами хоста, `Controller::Initialize`, `Connect(1)`; шаги теста upstream дословно (45 проверок).
- **t231:** шрифт игры `data/common/font/LevelNameFont.otf` (838 748 Б — тот, что игра открывает `sceFontOpenFontMemory` перед
  `SetScalePixel` 300/310 в `log_fs15_v`), масштаб 310, глифы `SkyGardenW`, поверхность 4096×2048×1.

Выводы (итоговые строки скриптов, правило п. 758(б)):

| Скрипт | Итог |
|---|---|
| `pairs_t265.py` | `ALL OK` (`entries=158205 pairs=10 file_pairs=9`) |
| `run_stand_m2b.py` на `m_wave1_hle_stand_wt1` (до мутантов) | `ALL OK` (6 из 6 плеч) |
| `run_stand_m2b.py` на `wt2` (после мутантов, чистая сборка) | `ALL OK` |
| `run_stand_m2b.py` на сборке `main` (`build_main`) | `ALL OK` |
| `run_stand_m2b.py` на сборке HEAD worktree `abb1d054` (итог) | `ALL OK` |
| `mutant_m2b.py all` | `ALL OK` — 6 из 6 пойманы; worktree восстановлен (sha256 диффа до = после) |
| `frames_t231.py` | `ALL OK` (34 строки) |
| `check_gate_order.py` worktree / `main` | `GATE ORDER: clean` ×2 (вывод = M2a) |
| `patch_m2b.py` worktree / `main` | `ALL OK` ×2 |
| `run_tests_m2.py` (`shader_cfg_tests`, ручки не заданы) | rc 0, `[test]` 134, `failed names 0` (база G1 — 0 падений, ⊆ выполнено); 368 SPIR-V = прогону M2a `dev4_u` байт в байт (`SPV_EQUAL`) |

## 4. T231: кадры крупного текста для пары листов M3 (п. 756(в)(2)(iii))

`log_fs15_v` (`C:/kyty/f287/fs15c/log_fs15_v.txt`, sha256 `bc466977…`) имён функций `sceFont` не пишет; `SetScalePixel` и
`SetupRenderScalePixel` печатают одну и ту же строку `handle = …, w = …, h = …` (пары строк в таблице). Строк с w ≥ 200 — 34
(`frames_t231_fs15_v.tsv`): масштабы 310 / 300 (шрифт 838 748 Б) и 250 / 240 (`LevelNameFont_JP.otf`, 1 512 428 Б); первый растр —
`code=0x53` (`S`) при 310.

- **Кадры растра (номер `FrameTrace: n=` следующей за вызовом строки): 178, 179, 180, 270** (видео `rec_fs15_v` — кадры 177–179, 5,19–5,22 с,
  и 269, 6,72 с; экран там чёрный — загрузка).
- **Кадр показа:** баннер «Sky Garden» виден в `rec_fs15_v` на **19,5–21,5 с — кадры видео 667–718 (`n` 668–719), середина — кадр 692
  (`n` 693, 20,49 с)** [c просмотра `vid/banner_crop.png`, `vid/tile_17_25.png`]. При FS15 надпись мелкая (≈ 140 px по ширине на кадре
  960×540). Это место для пары листов `=0`/`=1` M3; свидетель видимого отличия — только лист M3 (п. 756(в)(2)(iii)).

## 5. Сборки (не установлены)

| Бинарь | sha256 | Откуда |
|---|---|---|
| `bin/kyty_emulator_edc6d65e.exe` | `edc6d65ec7b9d799…` | worktree HEAD `8a717ac0`, `build_m2.cmd version` + сборка; строка версии `…-1931-g8a717ac00` (в бинаре есть и предыдущая `…-1930-g0361b202c` — так же, как у бинаря M2a `cc46e102` есть строка `…-1929-g6beb3b738`; у FS15 `bfac84be` строка одна) [c; причина — U] |
| `bin/m_wave1_hle_stand_abb1d054.exe` | `abb1d054d3025644…` | стенд той же сборки (итоговый прогон) |
| `bin/m_wave1_hle_stand_main.exe` | см. `sha_m2b.txt` | стенд из `main` (`build_main`) |
| `bin/mut_<имя>.exe` ×6 | см. `sha_m2b.txt` | мутанты |
| `bin/shader_cfg_tests_m2b.exe` | см. `sha_m2b.txt` | тесты worktree |

## 6. Файлы `C:/kyty/m657/m2b/`

`report.md` (этот), `times.txt`, `sha_m2b.txt` (sha256 53 выводов, бинарей и скриптов), `patch_m2b.py`, `MWave1HleStand.cpp` (= `tests/`),
`run_stand_m2b.py`, `mutant_m2b.py`, `pairs_t265.py` + `pairs_t265.tsv`, `frames_t231.py` + `frames_t231_fs15_v.tsv`,
`scan_font_log.py`/`ctx_font_log.py` (разведка формата лога), `stand_{wt1,wt2,main,final}/` (выводы плеч `=0`/`=1`), `mut/<имя>/`
(выводы мутантов, журналы сборки), `tests_u/`, `vid/` (кадры `rec_fs15_v`), журналы сборок `build_*.log`, `commit_msg.txt`.

Ключевые sha256: `stand_final.out.txt` `cc724df1…` (= `stand_main.out.txt`), `mutants.out.txt` `bc7962bd…`, `pairs_t265.tsv` `cc7a8938…`,
`frames_t231_fs15_v.tsv` `499473b2…`, `rec_fs15_v.mp4.idx` `4e6f6a43…`.

## 7. Что не доказано

Поведение консоли по всем трём темам — [I] (эталон — тест/код upstream); встречаются ли пары T265 в одном запуске — [U]; влияет ли
T272 на прохождение (удары L2/R2 у upstream — [I]); видимое отличие T231 на экране — только лист M3; код в игре не исполнялся.
