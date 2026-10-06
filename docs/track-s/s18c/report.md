# S18c — каталог повтора 19 известных сцен и теги отгрузки S-replay: отчёт звена (Harness Engineer, `HPP-644`)

Пункты: `ROADMAP.md` «СЕССИЯ 122» п. 569(д)(3)–(5), 571(г)(3), 576(е), 579(в), 585. Печать — `docs/track-s/s18c.md`
(KytyPS5 `4d755301`, sha256 `64eada1c3c2ab55c…`; копия `C:/kyty/s288/s18c/pred/s18c_seal.md`). Вердикта здесь нет — его выносит S18d (`HPP-645`).
Числа взяты из `C:/kyty/s288/s18c/runs/<тег>/read.txt|read.json`; таблица членов — `table.txt` (sha256 `b12f947b87459ae0…`);
время — `C:/kyty/s288/s18c/times.txt` (sha256 `46109d6ba096c782…`, строки `date -u`).

## Аппарат

- Бинарь всех тегов — S18a2 `C:/kyty/s288/bin/kyty_emulator_b3cee576.exe`, sha256 `b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a`,
  строка версии `KytyPS5-2026-09-15-6a2987a-1897-g0005e11f`. Сличается по полю `binary_sha256` и по `installed_sha.txt`: 25 тегов из 25 ✓.
- Установленный бинарь FS8 `2c9b69b9…` — до и после каждого тега один и тот же (25 из 25). Манифест кэшей после возврата — `EQUAL`,
  4 785 файлов, listsha `e2e7e8226f5bd9c1…`, у всех 25 тегов.
- Ридер `s18c_read.py` (sha256 `16570bed3667e5a1…`). Набор `test_s18c_read.py` — 283 проверки, `ALL OK`. Набор `test_tools_s18c.py` — 77 проверок, `ALL OK`.
  Зачётный `mutlib` v4.1 `--control --no-memo` — 118 из 118 убиты, контроли 3 из 3, стена 104,8 с (вывод `mut_s18c_read.run.txt`).
- Окно простоя GPU п. 585(в) — скрипт `idle_s18c.sh` (sha256 `7abbe629d88e833c…`): 15 замеров `nvidia-smi --query-gpu=utilization.gpu` с шагом 20 с,
  медиана ≤ 5 и ни одного замера > 10. При PASS скрипт сразу вызывает `launch_s18c.sh <тег>`. Скрипт применён перед `s18_r` (по п. 585(в)) и перед
  каждым тегом хвоста — это вариант исполнителя, комментарий звена от 12:18Z.

## Таблица тегов (25 из 25 — `READING MEMBERS_PASS`)

| тег | уровень | чтение | членов (все YES) | каталог после тега (sources / specs / pipes) | строк `skipped draw` (справка) | log sha256 |
|---|---|---|---|---|---|---|
| s18_c01 | title_controller_ship | MEMBERS_PASS | 26 | 128 / 130 / 112 | 80 | `9311299faf1a` |
| s18_c02 | intro_next | MEMBERS_PASS | 27 | 323 / 350 / 371 | 104 | `1a7149423a4d` |
| s18_c03 | worldmap | MEMBERS_PASS | 27 | 342 / 372 / 438 | 101 | `29e74dbf2f26` |
| s18_c04 | ps_logo | MEMBERS_PASS | 27 | 342 / 372 / 480 | 108 | `82072660af07` |
| s18_c05 | hub_crashsite | MEMBERS_PASS | 27 | 434 / 483 / 681 | 120 | `3ee8305db2f2` |
| s18_c06 | underwater_aerial_garden | MEMBERS_PASS | 27 | 549 / 652 / 949 | 409 | `51b4d75245bf` |
| s18_c07 | penguin_atlantis | MEMBERS_PASS | 27 | 564 / 781 / 1242 | 132 | `13009cb5316b` |
| s18_c08 | time_stopper_ghost_world | MEMBERS_PASS | 27 | 596 / 817 / 1413 | 316 | `ec7ba6dd37a4` |
| s18_c09 | rotating_level_day_and_night | MEMBERS_PASS | 27 | 608 / 834 / 1537 | 161 | `e16a240cfd6b` |
| s18_c10 | bumper_enemy_snowy_canyon | MEMBERS_PASS | 27 | 633 / 941 / 1770 | 230 | `059ad0278249` |
| s18_c11 | big_hand_pirate_island | MEMBERS_PASS | 27 | 653 / 1024 / 2083 | 164 | `ba2d9fe356fc` |
| s18_c12 | timestop_casino | MEMBERS_PASS | 27 | 658 / 1074 / 2304 | 99 | `8145227b411a` |
| s18_c13 | mini_giants_garden | MEMBERS_PASS | 27 | 674 / 1097 / 2424 | 238 | `2b49d0857a04` |
| s18_c14 | ice_iceberg | MEMBERS_PASS | 27 | 684 / 1140 / 2567 | 219 | `5fe70f96e642` |
| s18_c15 | sponge_dirty_bath | MEMBERS_PASS | 27 | 701 / 1190 / 2705 | 289 | `1375db5f4071` |
| s18_c16 | hoover_beach | MEMBERS_PASS | 27 | 704 / 1193 / 2819 | 200 | `b278d46b7dc3` |
| s18_c17 | volcano_mountain | MEMBERS_PASS | 27 | 714 / 1204 / 2919 | 325 | `69c12de6f8be` |
| s18_c18 | voxel_world | MEMBERS_PASS | 27 | 721 / 1211 / 2985 | 252 | `237797cf5f81` |
| s18_c19 | enemy_gorilla | MEMBERS_PASS | 27 | 727 / 1218 / 3079 | 15 | `80061394f4a8` |
| s18_ks | underwater_aerial_garden | MEMBERS_PASS | 21 | — | 0 | `335c6a95661f` |
| s18_r | underwater_aerial_garden | MEMBERS_PASS | 25 | — | 0 | `968f13ea9864` |
| s18_e1 | underwater_aerial_garden | MEMBERS_PASS | 28 | — | 0 | `a6d2300204e3` |
| s18_e2 | mini_giants_garden | MEMBERS_PASS | 28 | — | 0 | `cf9b7dbf8988` |
| s18_v | underwater_aerial_garden | MEMBERS_PASS | 25 | — | 0 | `ace54bb3306c` |
| s18_w | underwater_aerial_garden | MEMBERS_PASS | 18 | — | 0 | `e43138e6ad3a` |

Строки `skipped draw` у тегов сбора даны справкой. Сбор идёт при `KYTY_FIX_F19=0` на холодной папке своей подписи; это форма Б5, она считается и не фатальна (п. 221(г)(2)).

## Члены по п. 569(д)

- **(д)(3) накопление.** `ACCUMULATION OK` у 19 тегов из 19:
  - у `s18_c01` — `compat=absent`, поколение 0;
  - со второго тега — `compat=ok`, поколение = `replay.cur` прошлого тега, `catalogue_*` не убывают;
  - `canon_mismatch` 0, `dropped_queue` 0, `R_ADDR` 0.
  Строка п. 571(г)(3) — `SIGNATURE_571G3 s18_c01 OK` (подпись `F19=0`) и `SIGNATURE_571G3 s18_ks OK` (полная строка `…:fixf19`).
- **Каталог** `C:/kyty/s288/s18c/replay_known/`: 3 файла (`replay.45.bin`, `replay.46.bin`, `replay.cur` = 46), 12 503 925 байт, listsha `7f804f71…`.
  Копия = источник `state/s18_c19/replay` (`manifest cmp EQUAL`). Каталог: sources / specs / pipes / words / keep / programs = 727 / 1218 / 3079 / 74169 / 32150 / 493.
  Манифест — `docs/track-s/s18c/replay_known_manifest.tsv` (KytyPS5 `c644e3ad`); файлы каталога — только локально.
- **`s18_ks`** (стенд `stop`, форма `s17c_ks2`) читается по ветви (ii) (п. 579(в) Н1). Пять строк идут в порядке: `applied` → `close requested precache_active=1` →
  `stand stop seen` → `rebuild … pipelines_bin=stopped` → `close joined`. P 1 539 < R 3 079, `stand stop timeout` 0, `Event: quit` 0, код выхода 0,
  `pipelines.bin` не записан, 0 смертей. `waited_ms` 31, `wait_ms` 92.
- **`s18_r`** (`cat_full`, `KYTY_SHADER_SEED=0`):
  - `compat=ok`, поколение 46 = `replay.cur` `s18_c19`; строка перестройки есть, `rebuild skipped` нет;
  - доля `prepared / records` = 3 079 / 3 079 = 1,0 (≥ 0,90); тождество 3 079 + 0 + 0 = 3 079; разбиение Σ `rej_*` 0 = `rejected` 0;
  - `pipelines_bin=written`, экран подготовки 12 330 мс (≤ 180 с), 0 смертей;
  - `perms_new` 1 218, `perms_cached` 4 656, `rb_spec_changed` 79, `rb_push_moved` 0.
- **`s18_e1`** (Sky Garden) и **`s18_e2`** (`mini_giants_garden`) идут на входе `chain`. Член допуска: манифест входа = манифест состояния прошлого тега
  (`EQUAL`, listsha `30707dd7…` у обоих). У обоих: `rebuild skipped reason=recipes_current`, перестройки нет, 0 смертей, процесс жил до конца удержания 330 с,
  0 одно-кадровых глитчей, лист лида сделан, 0 трансляций программ каталога после строки подготовки.

  | | удержание после первого кадра сцены | кадров ≥ 1 с | видео | лист |
  |---|---|---|---|---|
  | `s18_e1` | 334,2 с | 0 | 9 984 кадра | `runs/s18_e1/sheet_s18_e1.png` |
  | `s18_e2` | 332,2 с | 0 | 20 424 кадра | `runs/s18_e2/sheet_s18_e2.png` |

  У `s18_e1` есть 2 строки `lost keyboard focus` — это не строка допуска.
- **`s18_v`** (`inst_cat`): `rebuild skipped reason=recipes_current` (строку называет печать), удержание 334,3 с, 0 кадров ≥ 1 с, видео 10 086 кадров,
  0 глитчей, лист `runs/s18_v/sheet_s18_v.png`, 0 смертей.
- **`s18_w`** (`cat_full`, `--vulkan-validation true`):
  - вход есть, процесс жил 310,2 с, **0 `[Vulkan][E]`**, строк лимита слоя 0;
  - положительный контроль: `[Vulkan][W]` 875 629 и `DualSrcBlend: supported=1 enabled=1` (строка 78) раньше первой `GuestOut` (строка 12 495);
  - справка: кадров ≥ 1 с под слоем — 1.
- **(д)(5) члены (1)–(2):**
  - S18a принят п. 573;
  - S18a2 принят п. 578 (`03e7ab2d`);
  - S18b принят п. 576 (`PASS_WITH_FIXES`, RC1 закрыт кодом);
  - S18b2 принят п. 579 (`PASS`, RC 0, `abd476c6`).

## Наблюдение для S18d: перестройка под слоем `s18_w` не исполнилась

Печать §4(г), вариант исполнителя: «`s18_w` на входе `cat_full` … W читает перестройку под слоем». На деле перестройки не было:
- при умолчании `KYTY_SHADER_SEED` в пустую папку `_fixf19` встал каталог «известные сцены» из `_ShaderSeeds` — строка 90 лога `ShaderSeed: installed (727 shaders)`;
- поставленный вместе с ним `pipelines.bin` подписи FS8 сделал рецепты текущими — строка 91 `ShaderReplay: rebuild skipped reason=recipes_current`.

Что это значит:
- члены W по букве печати (§5: вход, 310 с, 0 `[Vulkan][E]`, положительный контроль) выполнены;
- пути вызовов Vulkan перестройки слой в этом теге не видел;
- перестройку в теге исполняли только `s18_ks` и `s18_r` — оба без слоя (`--vulkan-validation false`), оба с `KYTY_SHADER_SEED=0`.

Как читать: у пользователя с установленным `_ShaderSeeds` первый вход после установки S18 перестройку не запускает. Перестройка случится
только при папке варианта без `pipelines.bin` текущей подписи и без каталога семян этой подписи (п. 569(в)). Под слоем такой путь не проверен.
Что с этим делать, решает лид.

## Помехи и ожидание GPU (п. 585)

- `s18_r`: два отказа `enter_scene` в `pre_run` — 11:05:57Z и 11:13:39Z (`BUSY gpu_util_median` 19,0 / 18,0 > 10). Эмулятор не стартовал;
  по п. 585(а)–(б) это не попытки. Отвод `pre` — 11:20:15Z: `runs|state|aside/s18_r.pre_20261006T112015Z`, `moved.txt`. Сверх состава
  скрипта отведён `s18_r.refused.json` — чтобы следующий отказ его не перезаписал.
- Окна простоя GPU, в скобках — медиана / max:

  | перед тегом | FAIL | PASS |
  |---|---|---|
  | `s18_r` | 11:25:32Z (0 / 17), 11:40:30Z (11 / 17), 11:55:27Z (15 / 19) | 12:10:29Z (1 / 7) → вызов 12:10:30Z |
  | `s18_e1` | 12:18:04Z, 12:33:04Z, 12:48:05Z, 13:03:09Z, 13:18:07Z | 13:33:08Z |
  | `s18_e2` | — | 13:56:39Z |
  | `s18_v` | 14:10:46Z, 14:25:46Z, 14:40:51Z, 14:55:54Z, 15:10:58Z, 15:25:57Z, 15:40:58Z, 15:56:07Z, 16:11:15Z, 16:26:22Z, 16:41:33Z, 16:56:40Z, 17:11:41Z | 17:26:44Z |
  | `s18_w` | — | 17:39:41Z |

  Нагрузку по счётчикам GPU engine давали посторонние процессы `<app>`: pid 68452 (3d / videodecode), pid 57332 и pid 42548 (3d до 99 %).
  Ни один не тронут. Отказов `pre_run` после окна PASS — 0.
- Блоки пользователя (общее правило 33):
  - блок 4: `s18_c19`, `s18_ks`, `s18_r`×2 (отказы), `s18_r`, `s18_e1` — закрыт `limit6`;
  - блок 5 открыт двумя проверками 13:41:39Z / 13:51:42Z: `s18_e2`, `s18_v`, `s18_w`.

  Пользовательских эмуляторов и лаунчеров не замечено — `GUARD CLEAN` у всех проверок.
- Помех окна (`minimized`, `Recovering Vulkan swapchain`) — 0. Повторов по п. 273(з) — 0.
- F20l2 (`HPP-648`) до `rc=` у `s18_w` тегов не запускал (17:47:44Z, замок снят).

## Не заявляется

- что S-replay даёт тёплый первый вход пользователя (это решает S18d);
- что каталог верен для уровней вне 19;
- что перестройка верна при любой будущей смене подписи;
- что перестройка чиста под слоем (не исполнялась под слоем, см. выше);
- что 0 трансляций программ каталога убирает фризы входа;
- что фризы входа вызваны шейдерами;
- полнота каталога и `eboot.bin`;
- ни одно число не является выигрышем. 60 FPS не обещается.
