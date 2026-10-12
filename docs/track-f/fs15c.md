# FS15c (`HPP-822`, Harness Engineer): теги `fs15_v`, `fs15_w`, `fs15_z` на бинаре отгрузки FS15 `bfac84be` — печать до тегов

Трек F, Ф20, отгрузка умолчания `KYTY_FIX_F20=1` пятнадцатым бинарём FS15 (п. 730(г)(3), приёмка FS15a — п. 732, FS15b — п. 733). Разделы
0–8 — печать (до тегов; после неё цепочка, ридер и правила чтения не меняются); раздел 9 — отчёт тегов (строки ридера, без вердикта; приёмка
и установка — FS15d `HPP-823`). Автор всех разделов — Harness Engineer. Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] —
неизвестно. Время — UTC.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_fs15c.py`, отрицательный контроль сдвигом)

- Задание — п. 730: `54e37383:docs/ROADMAP.md:24854` (якорь «730. **Звено F42d трека F (`HPP-782`, лид)»; +1 — «(а) **Приёмка F42a
  строкой»); константы FS15c — (г)(3) в строке `54e37383:docs/ROADMAP.md:24859` (якорь «(г) **Отгрузка FS15 — константы лида.**»; +1 —
  «(д) **Реестр §125**»); не заявляется — `54e37383:docs/ROADMAP.md:24863` (якорь «(з) **Не заявляется:** п. 694(к)»; +1 — «731. **Звено
  F47d»). Текст задания — `C:/kyty/f287/lead/p730_782/fs15c_text.md` (= описание `HPP-822`).
- Приёмка FS15a — п. 732: `54e37383:docs/ROADMAP.md:24873` (якорь «732. **Звено FS15a трека F (`HPP-820`, Emu Engineer»; +1 — «(а)
  **Пересчёт лида [c].**»); приёмка FS15b — п. 733: `54e37383:docs/ROADMAP.md:24879` (якорь «733. **Звено FS15b трека F (`HPP-821`, Red
  Team»; +1 — «(а) **Пересчёт лида [c»).
- Строки кода FS15 (worktree FS15a `C:/kyty/f287/fs15a/wt`, HEAD `6beb3b73`, строка версии `…-1929-g6beb3b73`): ручка Ф20, умолчание 1 —
  `6beb3b73:src/graphics/host_gpu/renderer/pipeline/fixF20.cpp:38` (якорь «const char* env = std::getenv("KYTY_FIX_F20");»; +1 — «const int
  value = (env == nullptr || env[0] == '\0' || Common::EnvValueOn(env)) ? 1 : 0;»); строка режима — `…/fixF20.cpp:40` (якорь
  «LOGF("FixF20: mode=%d\n", value);»; +1 — «return value;»); строка `FixF20Stat:` — `…/fixF20.cpp:26` (якорь «LOGF("FixF20Stat: when=%s
  calls=%"…»; +1 — «" rewritten=%" PRIu64 " unmatched=%" PRIu64 "\n",»); `when=periodic` — `…/fixF20.cpp:54` (+1 — «}»); `when=exit` только
  при `Mode() == 1` — `…/fixF20.cpp:60` (якорь «if (Mode() == 1) {»; +1 — «PrintStat("exit");»); вызов после окна —
  `6beb3b73:src/emulator.cpp:499` (якорь «Libs::Graphics::WindowRun();»; +1 — «Libs::Graphics::FixF20::PrintExitStat();»); первая строка режима
  до precache — `6beb3b73:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:4861` (якорь «(void)FixF20::Mode();»; +1 —
  «InitializeDriverCache();»); `PipelinePrecache: all pipelines created` — `…/pipelineCache.cpp:7066` (+1 — «VulkanLogMemoryStats();»);
  `ShaderPreparation: startup wait finished` — `6beb3b73:src/graphics/presentation/window/window.cpp:1089` (+1 — «"\n",»). Строки Ф24, Ф29,
  Ф25, Ф21, Б12 — как в печати FS14c (`e61fa50a:docs/track-f/fs14c.md` §0; код FS14 входит в FS15 без изменений — п. 733).
- Проверка ссылок — `refs_fs15c.out.txt`: 14 `OK`, 14 сдвигов `NOT OK`, `ALL OK`.
- Образцы харнесса: FS14c (`C:/kyty/f287/fs14c/`, в git `docs/track-f/fs14c/`, печать `e61fa50a`) — форма п. 634 / 660 / 661, установка
  бинаря на тег и возврат установленного из закреплённой копии, кэши — копия и возврат на каждый тег, формы `fs14_v` / `fs14_w`, выход
  харнессом формы `b4_v`; F42c (`C:/kyty/f287/f42c/`, печать `d6b67b21`) — члены `FixF20: mode=1`, строка `FixF20Stat: when=exit`
  (`unmatched`, `modules_bound` = `modules`, `rewritten` ≥ 11) и строки экрана подготовки, `PipelinePrecache:` и блоба драйвера.

## 1. Бинарь

- **Бинарь тегов — FS15:** sha256 `bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c`, копия
  `C:/kyty/f287/bin/kyty_emulator_bfac84be.exe` [c sha 2026-10-11 18:47Z, член набора `test_tools_fs15c.py`]; строка версии в файле
  `KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73` (строка ридера); FS15 = FS14 `eb7e8b91` + `a6342c98`, `a9d6fd1c`, `82570fd2` + `38fc76c1`
  (умолчание `KYTY_FIX_F20=1`), п. 732; ревью FS15b — `PASS`, RC 0, бинарь без изменений (п. 733); подпись трансляции `9177b426…` = FS14.
  Ставится в папку эмулятора только на тег под замком, после копии кэшей; член допуска — установленный во время тега = `bfac84be` по
  полному sha256.
- **Установленный — FS14** `013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd` [c sha 2026-10-11 18:49Z], закреплённая копия
  `C:/kyty/f287/bin/kyty_emulator_013e1974.exe` (= FS14 [c]); до тега (вне и внутри замка) = после возврата из закреплённой копии (член
  допуска). `C:/kyty/build/install` и `C:/kyty/build` не трогаются.
- **Окружение тегов:** цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла (список оставшихся — `runs/<тег>/env_shell_after_unset.txt`); в
  `enter_scene.py` позиционно передаются только:

| тег | `KYTY_*` / `VK_*` окружения процесса эмулятора (поле `env` json; пути — любые) |
|---|---|
| `fs15_v` | `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden` `KYTY_FRAME_TRACE=lite` `KYTY_GATE_FILE=<путь>` `KYTY_SAMPLE_GATE=<путь>` `KYTY_QUEUE_TRACE=1` `KYTY_GPU_CLOCK_PIN=1` `KYTY_GPU_MARKERS=0` `KYTY_GPU_HANG_ABORT_S=8` `KYTY_REC=<путь>` |
| `fs15_w` | те же без `KYTY_REC`, плюс `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin` `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000` |
| `fs15_z` | как `fs15_v`, плюс `KYTY_FIX_F20=0` |

  Ни у одного тега: `KYTY_TEST_*`, иные `KYTY_FIX_*` (умолчания бинаря), `KYTY_GAME_PATCH`, `KYTY_DIAG_*`, `KYTY_S_REPLAY`,
  `KYTY_SHADER_SEED`, `KYTY_PIPELINE_PRECACHE`, `KYTY_GPU_CHECKPOINTS`, `VK_LAYER_MESSAGE_ID_FILTER`. Окно 1280×720,
  `--shader-validation false`, без `--rd`; precache по умолчанию.

## 2. Кэши, сохранения и манифест

- Состав — пять каталогов харнесса FS14c: `_ShaderCache` (с `PPSA21564/pipelines.bin`, каталогом варианта
  `variant_fixb26_fixb1b_fixf10_fixf19` и `replay/`), `_ShaderSeeds`, `_PipelineCache` (блоб драйвера), `_SaveData`, GLCache драйвера.
- **Манифест базы до первого тега** (без замка, только чтение, 2026-10-11 18:49:42Z, в окне между тегами серии F47d — замка не было):
  `C:/kyty/f287/fs15c/base/base.tsv` — 4 832 файла, 1 304 969 313 байт, `listsha`
  `983cc56317a1bccd3c8cf55f46b936a2f2942803728689126b7209322f6977b2`; против базы FS14c (`fs14c/base/base.tsv`, 16:04Z) — `manifest cmp
  EQUAL` (`base/base_vs_fs14c.txt`) [c]; тот же `listsha` — в строках `manifest after` тегов F47d `f47_rd`, `f47_hi` [c `go_f47_hi.out.txt`].
- **Каждый тег — первый запуск FS15 на кэшах базы:** под замком — манифест и копия пяти каталогов (`runs/<тег>/before_*`), затем установка
  копии FS15; после тега — манифест состояния прогона (`manifest_run.tsv`, до возврата), возврат FS14 из закреплённой копии, возврат
  каталогов (`rm` + `mv`) и манифест после; член допуска — `manifest cmp EQUAL` до/после. Сверка «до тега = база» — строкой
  (`runs/<тег>/base_cmp.txt`), не членом. Размер блоба `_PipelineCache` до тега — из `manifest_before.tsv`, после прогона — из
  `manifest_run.tsv` (строка, не член). Сеанс пользователя во время тега — возврат GLCache слиянием (`snap_fs15c.py merge-return`), член —
  «манифест до ⊆ после, лишние — только GLCache» (`mfsub_fs15c.py`); тег — помеха. Неудачный возврат, установленный ≠ FS14 или `cmp` ≠
  EQUAL — `RETURN_FAILED`, замок остаётся, вопрос лиду.

## 3. Форма тегов (один вызов — один замок, одна попытка)

| тег | форма | вызов `enter_scene.py` из `go_fs15c.sh` (кроме общего `--level underwater_aerial_garden --attempts 1 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs15c_seal.md`) |
|---|---|---|
| `fs15_v` | `f20_v` / `fs14_v` без ручки, выход харнессом формы `fs12_v` (= `b4_v`) | `fs15_v --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `fs15_w` | `fs14_w` / `f20_w` без ручки | `fs15_w --stable-draws 100 --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `fs15_z` | контроль отката `KYTY_FIX_F20=0`, V Sky Garden | `fs15_z --stable-draws 300 --timeout 480 --rec --hold 150 KYTY_FIX_F20=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |

- **Порядок:** `fs15_v`, `fs15_w`, `fs15_z` — каждый своим вызовом и своим замком; блоков тегов нет, окна между тегами нет, проверка сторожа
  одна на вызов — сразу после взятия замка, до манифеста (п. 634, 660, 661). Серия FS15c начинается после конца серии F47d `HPP-809`
  (`lock released` последнего её тега и звено F47d без идущей серии); в чужую серию не вклинивается (п. 730(г)(3)).
- **Выход (все теги):** в конце удержания `enter_scene.py` посылает `WM_CLOSE` окнам процесса (в логе — `Event: quit`) и ждёт `CLOSE_WAIT_S`
  = 40 с (таймаут харнесса формы `b4_v`), иначе снимает процесс; запись попытки несёт `close_posted`, `close_rc`, `close_killed`, `close_s`.
- **Цепочка:** `chk_fs15c.sh <тег>` (файл `STOP`, замок, новые комментарии `HPP-822`, очередь P > F > S — строка `times.txt`) →
  `launch_fs15c.sh <тег>` (первая строка — линтер `form634_check.py --series`; дисплей: OFF — `dispstate.py --wake` и повторная проверка,
  п. 623(в)(1); очередь; только запуск) → `wait_fs15c.sh <тег>` ≤ 540 с за команду, отдельными командами → `post_fs15c.sh <тег>` вне замка
  (у `fs15_v`, `fs15_z`: `s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`; у `fs15_v` пара `pair_fs15_v_fs14_v.png` — лист тега слева, лист
  `fs14_v` FS14c справа; затем ридер, таблица и член темпа `tempo_fs15c.py` с формой W из строки `dryrun ` сухого плана). `go_fs15c.sh`:
  линтер, sha копии FS15, закреплённой копии FS14 и установленного, шлюз `procload.py` (маска `<app>`), проверка живого прогона по API
  (`runchk_fs15c.py`), загрузка хоста (строка), дисплей ON до замка и удержание до `lock released`, замок `C:/kyty/SEALED_RUN.lock`
  (`noclobber`), строки `lock taken|released <тег> <UTC>` в `runs/lock.log`, **сразу после замка** — сторож игры и сеанса пользователя
  (найден — замок снят, файлы не тронуты, помеха), затем манифест и копия, установка копии FS15, снятие `KYTY_*`/`VK_LAYER_*` шелла со
  строкой оставшихся, сторожа во время тега (опрос ≤ 2 с; найден — убийство своего эмулятора по pid), манифест состояния прогона, возврат
  FS14 и кэшей, `manifest cmp`, дисплей после. Повтора тега с тем же именем нет (`runs/<тег>` есть — отказ).

## 4. Правило чтения (ридер `fs15c_read.py`; вердикта нет)

**Определения.** Строка входа — первая строка, кончающаяся `GuestOut: Level has started: underwater_aerial_garden`; первая `GuestOut` —
первая строка со словом `GuestOut`. Первый кадр сцены — первая `FrameTrace: n=` после строки входа с `draws` ≥ 100; «после первого кадра
сцены» — строки `FrameTrace` после него (сам он не считается; строка печатает счёт и с ним). `FixF20` — строка `FixF20: mode=<0|1>`
(`fixF20.cpp:40`): ≥ 1 разобранная, неразборных 0, каждая `mode=<ожидаемый>` (1 у `fs15_v`/`fs15_w` — умолчание без переменной, 0 у
`fs15_z`), первая — раньше первой `GuestOut`. `FixF20Stat` — строка `FixF20Stat: when=<w> calls= modules_bound= modules= sites= rewritten=
unmatched=` (`fixF20.cpp:26`); `quit` — первая строка лога с `Event: quit`; **строка выхода** — последняя разобранная `FixF20Stat:
when=exit` ПОСЛЕ строки `quit` (нет такой — каждый член строки выхода «нет»). `FixF24`, `init`, `init_owner`, `FixF29`, `FixF25`, `FixF21`,
`FixB12`, `FixB13`, `LogAsync`, `wait_expired`, `pump_stop_expired`, `ExitFatal:`, маркеры смерти (`Unhandled exception:`, `--- Fatal
Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost`) — как в печати FS14c §4 (ожидаемые значения — умолчания FS15: 1).

**Допуск (член не выполнен — `NOT_ADMITTED`, тег не читается; повтор — пунктом лида, помеха попытку не тратит, п. 273(з)):** json есть;
`binary_sha256` = FS15 `bfac84be`; установленный во время тега = `bfac84be`; установленный до = после = FS14 `013e1974`; `prereg` = sha256
этой печати (`pred/fs15c_seal.md`); `env` = форма §1 ровно (ключи `KYTY_*`/`VK_*`; пути — любые; без `KYTY_FIX_*` у `fs15_v`/`fs15_w`,
`KYTY_FIX_F20=0` и никаких иных `KYTY_FIX_*` у `fs15_z`; без `KYTY_GAME_PATCH`); в `env` нет ключей `KYTY_TEST_*`; строк `ExitFatal:` 0 в
логе и 0 во всём stdout; последний `--vulkan-validation` — `true` только у `fs15_w`, иначе `false`; `--shader-validation false`; без `--rd`;
аргументы гостя `-lvl underwater_aerial_garden` и файл уровня харнесса; опция удержания (330 / 310 / 150); лог есть; stdout есть; исход
входа `ok`; строка входа есть; строк `Window … minimized` и `Recovering Vulkan swapchain` 0; подпись `9177b426` и каталог
`variant_fixb26_fixb1b_fixf10_fixf19`; строк `GamePatch:`, `DiagB32`, `TestLogStall:`, `TestHidLoss` 0; `manifest cmp EQUAL`; итоговая строка
`LogAsync: full_waits=` ровно одна со всеми полями (нет — помеха «снят убийством», п. 615(б)(6)) — 25 членов. Харнесс (вне ридера, п. 620(г),
621(б)): дисплей ON до замка и после `lock released` (OFF после — помеха `DISPLAY_OFF`); темп сцены (`tempo_fs15c.py` = `tempo_fs14c.py`):
средний `dt` < 100 мс (форма W — < 200 мс), иначе `SERIES_STOP` и вопрос лиду; игра и сеанс пользователя во время тега — помеха.

| тег | члены (буква п. 730(г)(3) и текста задания) | группа формы |
|---|---|---|
| `fs15_v` | 20 членов `fs14_v` (удержание ≥ 300 с после первого кадра сцены; процесс жив до конца удержания; 0 маркеров смерти в логе и stdout; 0 кадров `dt_us` ≥ 1 000 000 после первого кадра сцены; записей `.idx` видео ≥ 3 000; 0 одно-кадровых глитчей `s51_vidglitch.py`; лист для лида сделан; до первой `GuestOut`: `FixF24: mode=1 b24=1`, `FixF24: init`, `init_owner` жив, `init_owner` `hid` = `helper` = `pump` ≠ `main`, `FixF25: mode=1`, `FixF21: mode=1`, `FixB12: mode=1`, `FixF29: mode=1`; строка `Event: quit`; после неё 0 `--- Fatal Error ---` в логе и 0 во всём stdout; 0 `FixF21: wait_expired` и 0 `FixF24: pump_stop_expired` (весь лог и весь stdout); процесс кончился до таймаута харнесса — `close_killed` false, `close_rc` не пуст) + `FixF20: mode=1` до первой `GuestOut` + строка `FixF20Stat: when=exit` после `Event: quit` есть; её `unmatched` = 0; её `modules_bound` = `modules`; её `rewritten` ≥ 11 — 25 | `fs14_v` (= `fs13_v`): `LogAsync: mode=1` ровно один раз до первой `GuestOut`; итоговая строка есть; `drain_timeouts` 0; `FixB13: mode=1` до первой `GuestOut`; строка `FixB12Stat:` есть — 5 |
| `fs15_w` | процесс жив до конца удержания (`hold_s` ≥ 310, `hold_exit` пуст); 0 маркеров смерти; 0 `[Vulkan][E]`; 0 строк предела слоя (`this will be the last time reporting it`); `[Vulkan][W]` > 0 (положительный контроль слоя); до первой `GuestOut`: `DualSrcBlend: supported=1 enabled=1`, `FixF20: mode=1`, `FixF24: mode=1 b24=1`; строка `FixF20Stat: when=exit` после `Event: quit` есть; её `unmatched` = 0; её `modules_bound` = `modules` — 11 | `fs14_w`: `FixF29: mode=1`; `FixF25: mode=1`; `FixF21: mode=1`; `LogAsync: mode=1` до первой `GuestOut`; нет `VALIDATION_STOP` (`[Vulkan][E]` и процесс не дожил); `FixB13: mode=1`; `FixB12: mode=1` — 7 |
| `fs15_z` | удержание ≥ 120 с после первого кадра сцены; процесс жив; 0 маркеров смерти (лог и stdout); `FixF20: mode=0` до первой `GuestOut`; строк `FixF20Stat:` 0 (разобранных любого `when` и неразборных, весь лог) — 5 | — |

**Строки (не члены):** у каждого тега — экран подготовки `ShaderPreparation: startup wait finished in <мс> ms` (`window.cpp:1089`), строка
`PipelinePrecache: all pipelines created, <мс> ms` (`pipelineCache.cpp:7066`) и все строки `PipelinePrecache:` (до 8), строки `Vulkan
pipeline cache:`, размер блоба: байты `_PipelineCache` (и GLCache, `_ShaderCache`) до тега (`manifest_before.tsv`) и после прогона до
возврата (`manifest_run.tsv`); строки `FixF20Stat:` (число, `periodic`, неразборные, наибольший `unmatched`, строка выхода после `quit`,
последняя), иные строки `FixF20`; строки Ф24 (`pump_update_long`, `open failed`, пульты `Controller …`, `pump_stop_expired`), Ф29
(`overflow`, `Accessed non-GPU cached memory`), Ф25 (`read failed twice`, `direct read failed`) — как в печати FS14c; код выхода `close_rc`
(и hex) и `close_s` у каждого тега, строка `Event: quit`, `--- Fatal Error ---` после неё (у `fs15_v` — члены; у `fs15_z` буква: «выход
харнессом — строкой»; у `fs15_w` — справка); у `fs15_z` — строки режима `FixF24`, `FixF29`, `FixF25`, `FixF21`, `FixB12`, `FixB13`,
`LogAsync`, кадры ≥ 1 с, видео, глитчи, лист (справка); `[Vulkan][E]` у V и `fs15_z` (валидации нет — справка); строка версии в копии
бинаря; строка `Fork build`. Ридер печатает `MEMBERS ALL YES / NOT ALL YES` — это не вердикт.

**Что читает лид, не ридер:** лист `fs15_v` и пару с `fs14_v` (видимые дефекты); каждый глитч детектора кадрами ± 2; лист `fs15_z`
(справка); чтение и установка — FS15d.

## 5. Повторы, отказы, остановка

- Одна попытка на тег. Повтор `<тег>_r1`…`_r3` — только пунктом лида по помехе (допуск не выполнен; `DISPLAY_OFF`; пользователь во время
  тега; `enter_scene` не запустил эмулятор — повтор тем же именем); `launch_fs15c.sh` без `FS15C_REPEAT_OK=1` повтор не запускает. Провал
  члена п. 730(г)(3) — не помеха, повтора нет, чтение FS15d.
- Отказ шлюза `procload`, сторожа после замка, очереди или дисплея до старта эмулятора — не попытка; вывод отказанного вызова переносится
  в `old/` (п. 309(и)). `SERIES_STOP` — следующий тег не запускается до пункта лида. `RETURN_FAILED` — замок остаётся. Файл
  `C:/kyty/f287/STOP` — стоп перед следующей командой. Перед каждым вызовом — `chk_fs15c.sh` (API, комментарии звена, очередь) строкой
  `times.txt`, и проверка звена F47d `HPP-809` (нет идущей серии). Очередь замка P > F > S (п. 322(г)). Выключенный дисплей — не причина
  остановки, харнесс будит его сам (п. 623(в)).
- **Бюджет замка — ≤ 25 мин на тег** (оценка [I]: копия кэшей ≈ 1,3 ГБ, вход ≈ 20–60 с плюс холодный блоб ≈ 11 с, удержание 330 / 310 /
  150 с, вход W до 900 с, выход ≤ 40 с, возврат; FS14c — 3 тега, замок 16:07:19–16:43:11Z, `fs14c/runs/lock.log`). Вызов `launch_fs15c.sh` — с пределом
  инструмента ≥ 300 с.

## 6. Не заявляется

П. 730(з) целиком: что бит промаха теряется в игре на установленном бинаре и как часто; что потеря видна на кадре; что правка снимает
задержку регистрации страниц; что первый запуск FS15 у пользователя пройдёт без кадров ≥ 1 с вне формы `fs15_v`; что переписанные модули
годны драйверу на всех сценах; что FS15 установлен (до FS15d); что откат `KYTY_FIX_F20=0` на FS15 равен FS14 байт в байт (по поведению); что
код выхода 0 — свойство правки; что прочие `SCENE_OK` держатся на FS15; что реестр полон. Ни одно число — не выигрыш; время кадра и экран
подготовки — справка; 60 FPS не обещаются; цель (B) не меняется; установленный FS14 `013e1974` не меняется.

## 7. Инструменты и фикстуры (до первого тега; файлы `C:/kyty/f287/fs15c/`, копия — `docs/track-f/fs15c/`)

- `go_fs15c.sh`, `launch_fs15c.sh`, `post_fs15c.sh` — сгенерированы из файлов FS14c скриптом `draft/gen_fs15c.py` (фиксированный список
  замен с часовыми, переписанные заголовки; у `fs15_z` ручка `KYTY_FIX_F20=0`; пара `fs15_v` с листом `fs14_v` FS14c; план — `grep '^dryrun '`).
- `fs15c_read.py` — ридер (§4): `fs14c_read.py` FS14c с заменами `draft/patch_read_fs15c.py` (каждая замена — ровно одно совпадение) и
  частями Ф20 из `f42c_read.py` (строка выхода — после `quit`, см. §8).
- Копии FS14c (`gen_fs15c.py`): без изменений — `dispstate.py`, `procload.py`, `idle142.py`, `launch_run.py`, `run_safety99.py`,
  `manifest_fs4c.py`, `sheet142.py`, `gates_default.txt`, `gates.req`, `sample.req`; с переносом имён (`fs14c` → `fs15c`, `HPP-814` →
  `HPP-822`): `guard_fs15c.py`, `hold_fs15c.py`, `hostload_fs15c.py`, `runchk_fs15c.py`, `queue_fs15c.py`, `snap_fs15c.py`,
  `mfsub_fs15c.py`, `wait_fs15c.sh`, `chk_fs15c.sh`, `tempo_fs15c.py`; `enter_scene.py` — файл FS14c с перенесённым `ROOT`; сторож шагов без
  замка — `watch_fs15c.py` (копия `watch_fs15a.py`, п. 431(в)(1)). Копия `launch_run.py` в git — с маской `<app>`.
- **Последний вывод наборов** (полные sha — `SHA256SUMS_seal.txt`):
  - `test_fs15c_read.out.txt` — первая строка `suite test_fs15c_read.py sha256 f35f2949… target fs15c_read.py sha256 9ef29757…`,
    `checks 543 failed 0`, `ALL OK` (порт набора FS14c: чистые теги трёх форм; каждый член допуска у каждого тега, включая `KYTY_FIX_F20`
    `1`/`0`/`""` у `fs15_v`/`fs15_w` и `1`/`""` у `fs15_z`, `KYTY_FIX_F24`/`KYTY_FIX_F29` у всех трёх; каждый член каждой формы; по
    фикстуре на каждый член Ф20: `FixF20` противоположный / нет / неразборный / после `GuestOut` / вторая строка противоположная / с
    префиксом / CR у трёх тегов; строка выхода нет / только до `quit` / нет `quit` / неразборная (3 вида) / `unmatched` 1 / `modules_bound`
    ≠ `modules` (2 вида) / две строки — решает последняя / `rewritten` 10, 11, 0 (член только у `fs15_v`); у `fs15_z` каждый вид строки
    `FixF20Stat:` — член, иные строки `FixF20`, `FixF24`, `FixF29` — строки; `periodic` с `unmatched` 7 — строка; строки экрана подготовки,
    `all pipelines created`, блоба (и без файлов tsv); края FS14c; таблица; вывод в строгий cp1250, ASCII). Мутантов нет (п. 730(г)(3)).
  - `regress_fs15c.out.txt` — ридер на настоящих файлах: `fs14_v` / `fs14_w` FS14c (FS14 `013e1974`, установленный FS13) как `fs15_v` /
    `fs15_w` — допуск не выполнен ровно по 3 членам (бинарь json, установленный на теге, установленный до/после), члены — все ДА, кроме
    `FixF20: mode=1` и членов строки выхода (5 / 4; строк Ф20 до F42a нет); `fs14_z` как `fs15_z` — допуск ровно по 4 (+ `missing
    KYTY_FIX_F20`), члены — все ДА, кроме `FixF20: mode=0` (строк `FixF20Stat:` 0 — ДА); `f20_v` / `f20_w` F42c (`1994a0ce` на FS12,
    `KYTY_FIX_F20=1`, установленный FS14) как `fs15_v` / `fs15_w` — допуск ровно по 3 (бинарь json, установленный на теге, `extra
    KYTY_FIX_F20=1`), члены — все ДА, кроме членов Ф24 / `FixF25` / `FixF29` (6 / 3; строк в FS12 нет): все члены Ф20 — ДА (ближайший
    положительный контроль буквы Ф20: `rewritten` 79, `modules_bound` = `modules` 22, `unmatched` 0); строки: `f20_v` экран подготовки
    2 299 мс, `all pipelines created` 11 190 мс, `_PipelineCache` 192 243 915 → 200 058 789 байт; FS14 — 0 / 578 мс, блоб без изменений;
    первая строка `suite regress_fs15c.py sha256 1f3a8af2… target fs15c_read.py sha256 9ef29757…`, `ALL OK`.
  - `test_tools_fs15c.out.txt` — первая строка `suite test_tools_fs15c.py sha256 17581f68… target go_fs15c.sh sha256 7092c723…`,
    `checks 103 failed 0`, `ALL OK` (сухой план трёх тегов и `_r1`/`_r3`; нет `KYTY_TEST_` в планах; `KYTY_FIX_` только `KYTY_FIX_F20=0` у
    `fs15_z`; план `post_fs15c.sh` по строке `dryrun `, форма W, первая строка сухого вывода — `ALL OK` линтера; пара с листом `fs14_v`, лист
    на диске; отказы по имени у `go`/`launch`/`post`; повтор без `FS15C_REPEAT_OK`; линтер `--series`; первая исполняемая строка — линтер;
    литералы sha и пути копий, sha копий на диске; сторож после замка до манифеста; установка после копии кэшей; возврат FS14 до
    `installed_after`; своя задача `HPP-822` у `queue`/`runchk`/`chk`; `tempo_fs15c.py` = `tempo_fs14c.py`; `ROOT` и `CLOSE_WAIT_S`; ASCII
    скриптов; вывод в строгий cp1250).
  - `refs_fs15c.out.txt` — 14 ссылок, `ALL OK`.
  - **Линтер формы п. 634 / 661** — `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` (sha256 — `SHA256SUMS_seal.txt`); он же — первая
    исполняемая строка `launch_fs15c.sh` и `go_fs15c.sh`:

```
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/fs15c
ALL OK
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --text C:/kyty/f287/fs15c/pred/fs15c_seal.md
ALL OK
```

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте звена)

1. «Строка выхода `FixF20Stat:`» — последняя разобранная `when=exit` ПОСЛЕ `Event: quit` (буква задания: «после `Event: quit` строка
   `FixF20Stat: when=exit`»); её наличие — отдельный член у `fs15_v` и `fs15_w` (форма N1 F42c, п. 705(в)), без `SERIES_STOP` (одна попытка,
   чтение — FS15d). F42c брал последнюю `when=exit` во всём логе и N1 отдельно — при одной строке выхода после `quit` прочтения совпадают.
2. «`FixF24`» у `fs15_v` (п. 730(г)(3)) — четыре члена Ф24 формы `fs14_v` (`mode=1 b24=1`, `init`, `init_owner` жив, владелец), как в
   тексте задания («`FixF24: mode=1 b24=1`, `FixF24: init_owner`») и в FS14c; `FixF29` у `fs15_w` — в группе формы `fs14_w` (буква текста
   задания для `fs15_w` его не называет; FS14c держал его в букве).
3. «Строк `FixF20Stat:` 0» у `fs15_z` — разобранные любого `when` и неразборные строки с `FixF20Stat:`, по всему логу; иные строки
   `FixF20` — строка, не член.
4. «Размер блоба до и после» — байты `_PipelineCache` по `manifest_before.tsv` (до тега, под замком) и `manifest_run.tsv` (после прогона,
   до возврата); «после возврата» блоб = до (член `manifest cmp EQUAL`).
5. «Выход харнессом — строкой» у `fs15_z` и «0 маркеров смерти» — как в FS14c: маркеры смерти — член, выход (`close_rc`, `close_s`,
   `Event: quit`, Fatal после него) — строка.
6. «0 `FixF21: wait_expired`» и «0 `FixF24: pump_stop_expired`» у `fs15_v` — по всему логу и всему stdout (строже буквы «после
   `Event: quit`»), «после `Event: quit` 0 `--- Fatal Error ---`» — в логе после `quit` и во всём stdout (как в FS14c §8).
7. «Лист рядом с `fs14_v`» — `sheet_fs15_v.png` и пара `pair_fs15_v_fs14_v.png` (справа — `fs14_v` FS14c, установленный FS14); смотрит лид.
8. `fs15_z`: опция удержания 150 с (член — ≥ 120 с после первого кадра сцены); видео и лист пишутся (справка).
9. Серия FS15c ждёт конца серии F47d `HPP-809` (п. 730(г)(3) «в идущую серию F47d не вклинивается»): очередь `queue_fs15c.py` звенья F не
   держит (замок — исключение), поэтому перед каждым тегом — проверка API `HPP-809` строкой `times.txt`.

## 9. Отчёт тегов

(заполняется после тегов; печать выше не меняется)

**Отчёт тегов (дописан после тегов 2026-10-12 ≈ 01:00Z; разделы 0–8 выше не менялись, `pred/fs15c_seal.md` = их копия, sha256 `76e67c26…`).**
Строки ридера, без вердикта; приёмка и установка — FS15d `HPP-823`.

- **Печать до первого замка:** коммит KytyPS5 `df120c32` (2026-10-11 ≈ 18:50Z) < `lock taken fs15_v` 22:01:51Z; `prereg.sha256` всех трёх
  json = sha256 печати `76e67c26…`; ридер `fs15c_read.py` sha256 `9ef29757…` (= набору §7).
- **Очередь замка (п. 730(г)(3), §8(9)):** серия начата после конца серии F47d `HPP-809` (п. 735). Перед каждым вызовом `chk_fs15c.sh` —
  `QUEUE FREE`, новых чужих комментариев 0. Одновременно — один замок.
- **Отказы до старта эмулятора (не попытки, §5):** `fs15_v` — шлюз `procload` 19:53:30Z, 20:51:33Z, 21:21:47Z (до замка, rc 5; посторонний
  `<app>` pid 59848, 1,5–2,5 CPU с/с); `fs15_w` — 22:20:30Z `enter_scene` под замком 22:15:02Z–22:20:40Z отказал до старта эмулятора по
  простою GPU (`pre_run REFUSED BUSY gpu_util_median 11.0 > 10`, кэши `cmp EQUAL`, FS14 возвращён), затем шлюз 22:51:15Z и 23:52:20Z (до
  замка, rc 5; `<app>` pid 47132, 1,8–4,8 CPU с/с; процесс пользователя с живым родителем — не снимался). Выводы — `runs/refused/`, строки
  `C:/kyty/f287/times.txt`. Ожидание простоя шлюзом — `PLWAIT=1800`, начиная с вызова, отказавшего в 21:21:47Z.
- **Один тег — один замок** (`runs/lock.log`): `fs15_v` 22:01:51Z–22:13:05Z, `fs15_w` 2026-10-12 00:31:11Z–00:42:29Z, `fs15_z`
  00:44:08Z–00:52:23Z (≤ 25 мин каждый, §5). Одна попытка на тег, помех 0, повторов `_rN` 0. Сторож и сеанс пользователя сразу после замка —
  `GUARD CLEAN`, `HOLD CLEAR` у всех трёх (строки `lock taken; guard…` 22:06:31Z / 00:36:09Z / 00:49:06Z); во время тега пользователь и ВМ не
  найдены. Дисплей ON до замка и после `lock released`, событий дисплея 0; загрузка хоста до и после — `over05 0` у всех трёх.
- **Бинарь:** установленный внутри замка до каждого тега — FS14 `013e1974…`; на тег — копия FS15 `bfac84be…` (`installed_sha.txt`, json
  `binary_sha256`); после каждого тега возвращён из закреплённой копии — `013e1974…`; после серии `ps5 em/kyty_emulator.exe` = `013e1974…` [c
  00:54Z]. Строка `Fork build arigandores/KytyPS5 6beb3b7` в логе — у всех трёх.
- **Кэши:** у каждого тега до тега = база §2 (`base_cmp.txt` EQUAL); после возврата — `manifest cmp EQUAL files 4832 listsha 983cc563…`.
- **Окружение:** ключи `env` json — `fs15_v`: `KYTY_FRAME_TRACE`, `KYTY_GATE_FILE`, `KYTY_GPU_CLOCK_PIN`, `KYTY_GPU_HANG_ABORT_S`,
  `KYTY_GPU_MARKERS`, `KYTY_GUEST_ARGS`, `KYTY_QUEUE_TRACE`, `KYTY_REC`, `KYTY_SAMPLE_GATE`; `fs15_w` — те же без `KYTY_REC`, с `VK_LAYER_PATH`,
  `VK_LAYER_DUPLICATE_MESSAGE_LIMIT`; `fs15_z` — как `fs15_v` и `KYTY_FIX_F20=0`; `KYTY_TEST_*`, иные `KYTY_FIX_*`, `KYTY_GAME_PATCH` — нет ни
  у одного; `KYTY_*`/`VK_LAYER_*` шелла после снятия — 0 строк у всех трёх.

| тег | допуск | члены п. 730(г)(3) | группа формы | ключевые числа | выход (строка) | темп (п. 620(г)(2), 621) |
|---|---|---|---|---|---|---|
| `fs15_v` | PASS (25/25) | ВСЕ ДА (25/25) | `fs14_v` ВСЕ ДА (5/5) | удержание 334,4 с после первого кадра сцены (n 379), жив; 0 маркеров смерти; 0 кадров ≥ 1 с (с первым кадром 0; наибольший 200 794 мкс); видео 10 373 записи, 0 глитчей; лист `runs/fs15_v/sheet_fs15_v.png`, пара `pair_fs15_v_fs14_v.png` (слева `fs15_v`, справа `fs14_v`); до первой `GuestOut` 12 510 без переменных: **`FixF20: mode=1` строка 88**, `FixF24: mode=1 b24=1` строка 20, `FixF24: init` строка 21, `init_owner hid=helper=msg=pump=16960 main=54140` строка 22, `FixF25: mode=1` строка 17, `FixF21: mode=1 wait_ms=12000` строка 705, `FixB12: mode=1` строка 670, `FixF29: mode=1` строка 96; `Event: quit` строка 1 175 666, после неё **`FixF20Stat: when=exit` (одна): `unmatched` 0, `modules_bound` 22 = `modules` 22, `rewritten` 79** (`sites` 79, `calls` 1 271); `--- Fatal Error ---` после `quit` 0 (лог), 0 (stdout); `wait_expired` 0 / 0; `pump_stop_expired` 0 / 0 | код **0** (`0x00000000`), `WM_CLOSE` → конец процесса **4,0 с**, `close_killed` false (таймаут 40 с) | PASS 33,44 мс (29,90 к/с) |
| `fs15_w` | PASS (25/25) | ВСЕ ДА (11/11) | `fs14_w` ВСЕ ДА (7/7) | `hold_s` 310,0, жив; 0 маркеров смерти; **`[Vulkan][E]` 0**; строк предела слоя 0; `[Vulkan][W]` 899 116; до первой `GuestOut` 12 512: `DualSrcBlend: supported=1 enabled=1`, **`FixF20: mode=1` строка 92**, `FixF24: mode=1 b24=1` строка 20; после `Event: quit` (строка 2 347 973) **`FixF20Stat: when=exit` (одна): `unmatched` 0, `modules_bound` 22 = `modules` 22** (`rewritten` 79); форма: `FixF29`, `FixF25`, `FixF21`, `FixB13`, `FixB12: mode=1`, `LogAsync: mode=1`, `VALIDATION_STOP` нет | код 0, 4,0 с, `close_killed` false (справка) | PASS 129,76 мс (форма W, порог 200) |
| `fs15_z` | PASS (25/25) | ВСЕ ДА (5/5) | — | удержание 154,5 с после первого кадра сцены (n 204), жив; 0 маркеров смерти; **`FixF20: mode=0` строка 88** < первой `GuestOut` 12 509; **строк `FixF20Stat:` 0** (разобранных 0, неразборных 0), иных строк `FixF20` 0 | **код 0, 3,7 с**, `close_killed` false; `Event: quit` строка 753 288, `--- Fatal Error ---` после неё 0, stdout 0 | PASS 33,93 мс (29,47 к/с) |

**Строки (не члены, п. 730(г)(3)) — `fs15_v` / `fs15_w` / `fs15_z`:**

| строка | `fs15_v` | `fs15_w` | `fs15_z` |
|---|---|---|---|
| экран подготовки (`ShaderPreparation`, мс) | 1 636 | 65 | 0 |
| `PipelinePrecache: all pipelines created` (мс) | 12 002 | 11 877 | 561 |
| `_PipelineCache` до тега / после прогона (байт) | 192 243 915 / 200 058 845 | 192 243 915 / 200 058 848 | 192 243 915 / 192 243 915 |
| `Vulkan pipeline cache: loaded` / `saved` (байт) | 127 836 218 / 135 651 148 | 127 836 218 / 135 651 151 | 127 836 218 / 127 836 218 |
| GLCache до / после прогона (байт) | 284 887 245 / 292 702 299 | 284 887 245 / 292 702 302 | 284 887 245 / 284 887 245 |

После возврата блоб = до у всех трёх (`manifest cmp EQUAL`): каждый тег при `=1` видел холодный блоб драйвера для переписанных модулей, `fs15_z`
(`=0`) — тёплый. Прочие строки у всех трёх: `FixF24: pump_update_long` 0, `FixF24: open failed` 0, строк пультов хоста `Controller …` 0;
`FixF29: overflow` 0 / 0; `Accessed non-GPU cached memory` 37 / 0, 37 / 0, 36 / 0 (лог / stdout; первая — `… at 0x0000000401c08000`, как на FS14);
`FixF25: read failed twice` и `KernelRead: direct read failed` 0 / 0.

**Справка (не члены).** `fs15_z`: видео 4 743 записи, 0 глитчей, лист `runs/fs15_z/sheet_fs15_z.png`, кадров ≥ 1 с 0 (наибольший 183 690 мкс),
`FixF24: mode=1 b24=1`, `FixF29`, `FixF25`, `FixF21`, `FixB12`, `FixB13: mode=1`. Время кадра после первого кадра сцены: `fs15_v` 9 965 кадров,
средний `dt_us` 33 557 (`fs14_v` FS14c — 9 794, 34 147; не заявляется, §6); `fs15_w` под слоем 2 449 кадров, средний 132 623, наибольший 416 964;
`fs15_z` 4 529 кадров, средний 34 116. Последняя строка `FixB12Stat:` — `passes=232735 / 33612 / 95826 rewalk=0 rwd=0 lskip=0`. Событий окна
`minimized` / `Recovering Vulkan swapchain` 0 (допуск). Вход `stable_s` 24,2 / 34,0 / 16,4 с. Таблица ридера — `runs/table.txt`; sha256 логов,
stdout, json, видео, `read.*`, `tempo.txt` — `runs/artefacts_sha.txt` (`log_fs15_v.txt` `bc466977…`, `log_fs15_w.txt` `1e84c589…`,
`log_fs15_z.txt` `1ca8dd65…`, `rec_fs15_v.mp4` `b84db441…`, `rec_fs15_z.mp4` `d7697552…`).

**Наблюдения для FS15d (не вывод).** (1) Листы исполнитель видел в уменьшенном виде: пара `fs15_v`/`fs14_v` — те же фазы (чёрный старт, полёт
со стаей и карточкой управления, карточка «SKY GARDEN», удержание Астро на тропе сада), видимых отличий не заметил; лист `fs15_z` — те же фазы.
Лист смотрит лид. (2) `fs15_z` (`KYTY_FIX_F20=0`) — только буква п. 730(г)(3) (откат по поведению, не байт в байт FS14, §6). (3) Экран
подготовки `fs15_v` 1 636 мс и `all pipelines created` ≈ 12 с при `=1` против 561 мс при `=0` — цена холодного блоба драйвера, названная в
п. 730 (≈ 11 с), здесь — справка.

**Варианты исполнителя (§8), вопросы лиду.** Прочтения §8(1), (6) совпадают: строка `when=exit` одна во всём логе и лежит после `quit`;
`wait_expired`, `pump_stop_expired` и `--- Fatal Error ---` 0 и в логе, и в stdout. `SERIES_STOP` не создавался. **Вопрос лиду (§5):** отказ
`enter_scene` по простою GPU до старта эмулятора (`fs15_w` 22:20:30Z, под замком) исполнитель счёл «не попыткой» по второму абзацу §5 (отказ до
старта эмулятора) и повторил тем же именем без пункта лида (строка `times.txt` 22:21:27Z); первый абзац §5 можно прочесть так, что такой повтор
идёт пунктом лида. Если верно второе прочтение — допуск `fs15_w` решает FS15d.

**Отступления.** (1) Время замка `fs15_v` в комментарии звена 22:51:44Z названо 22:06:31Z — это строка `lock taken; guard…` после обхода сторожа;
взятие замка — 22:01:51Z (`runs/lock.log`). Иных отступлений нет.

**Не заявляется** — §6 без изменений.
