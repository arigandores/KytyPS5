# FS14c (`HPP-814`, Harness Engineer): теги `fs14_v`, `fs14_w`, `fs14_z` на бинаре отгрузки FS14 `013e1974` — печать до тегов

Трек F, Ф24 и Ф29, отгрузка умолчаний `KYTY_FIX_F24=1` и `KYTY_FIX_F29=1` четырнадцатым бинарём FS14 (п. 710(г)(3) с поправкой п. 712(г)(3),
приёмка FS14a — п. 717, FS14b — п. 720). Разделы 0–8 — печать (до тегов; после неё цепочка, ридер и правила чтения не меняются); раздел 9 —
отчёт тегов (строки ридера, без вердикта; приёмка и установка — FS14d `HPP-815`). Автор всех разделов — Harness Engineer. Метки: [c] —
код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно. Время — UTC.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_fs14c.py`, отрицательный контроль сдвигом)

- Задание — п. 710: `45dd78a2:docs/ROADMAP.md:24708` (якорь «710. **Звено F40d трека F (`HPP-773`, лид)»; +1 — «(а) **Приёмка F40c
  строкой.**»); константы FS14c — (г)(3) в строке `45dd78a2:docs/ROADMAP.md:24712` (якорь «(г) **Отгрузка FS14 — константы лида.**»; +1 —
  «(д) **Реестр §121**»); не заявляется — `45dd78a2:docs/ROADMAP.md:24716` (якорь «(з) **Не заявляется:** п. 692(л)»; +1 — «711. **Звено
  F46b»). Текст задания — `C:/kyty/f287/lead/p710_773/fs14c_text.md` (= описание `HPP-814`).
- Поправка п. 712 (Ф29 входит в FS14): `45dd78a2:docs/ROADMAP.md:24724` (якорь «712. **Звено F44d трека F (`HPP-794`, лид)»; +1 — «(а)
  **Приёмка строкой.**»); члены FS14c — (г)(3) в строке `45dd78a2:docs/ROADMAP.md:24728` (якорь «(г) **Отгрузка — в FS14, поправки к
  п. 710(г)»; +1 — «(д) **Реестр §122**»). Текст поправки — `C:/kyty/f287/lead/p712_794/fs14c_add.md`.
- Очередь замка — п. 714(б): `45dd78a2:docs/ROADMAP.md:24742` (якорь «(б) **Правило.** (1) Серия F46c»; +1 — «(в) **Звенья.** `HPP-800`»):
  FS14c — одна серия, после конца серии F46c `HPP-800` (`lock released` последнего тега), в чужую серию не вклинивается.
- Приёмка FS14b — п. 720: `45dd78a2:docs/ROADMAP.md:24781` (якорь «720. **Звено FS14b трека F (`HPP-813`, Red Team»; +1 — «(а) **Приёмка
  строкой. FS14b»); звенья — `45dd78a2:docs/ROADMAP.md:24786` (якорь «(д) **Звенья.** FS14b `HPP-813`»; +1 — «(е) **Не заявляется:**
  п. 710(з) и 712(з)»). FS14a итоговый бинарь — п. 717.
- Строки кода FS14 (коммит FS14a `eb7e8b91`, строка версии бинаря `…-1925-geb7e8b91`): ручка Ф24, умолчание 1 —
  `eb7e8b91:src/graphics/presentation/window/joyPump.cpp:455` (якорь «const char* value = std::getenv("KYTY_FIX_F24");»; +1 —
  «g_enabled.store(value == nullptr || value[0] == '\0'»); строка режима — `eb7e8b91:src/graphics/presentation/window/joyPump.cpp:457`
  (якорь «LOGF("FixF24: mode=%d b24=%d\n", …»; +1 — «}»); `FixF24: init` — `…/joyPump.cpp:203` (якорь «LOGF("FixF24: init tid=%"»; +1 —
  «pump_tid, main_tid);»); `FixF24: init_owner` — `…/joyPump.cpp:97` (якорь «LOGF("FixF24: init_owner hid=%"»; +1 — «helper, msg, pump,
  main_os_tid);»); `FixF24: pump_stop_expired` — `…/joyPump.cpp:440` (+1 — «thread.detach();»); `FixF24: pump_update_long` —
  `…/joyPump.cpp:247` (+1 — «}»); `FixF24: open failed` — `…/joyPump.cpp:351` (+1 — «}»); строки пультов `Controller …` —
  `…/joyPump.cpp:376`, `eb7e8b91:src/graphics/presentation/window/window.cpp:404` и `…/window.cpp:376`; ручка Ф29, умолчание 1 —
  `eb7e8b91:src/graphics/host_gpu/renderer/cache/faultManager.cpp:46` (якорь «const char* value = std::getenv("KYTY_FIX_F29");»; +1 —
  «return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);»); строка режима — `…/faultManager.cpp:84` (якорь
  «LOGF("FixF29: mode=%d\n", FixF29Enabled() ? 1 : 0);»; +1 — пустая строка); `FixF29: overflow` — `…/faultManager.cpp:62` (+1 —
  «pass.area, parse.raw, parse.count, total);»); `Accessed non-GPU cached memory` — `…/faultManager.cpp:255` (+1 — «},»);
  `FixF25: mode=` — `eb7e8b91:src/kernel/fileSystem.cpp:431` (якорь «LOGF("FixF25: mode=%d\n", FixF25Enabled() ? 1 : 0);»; +1 — «}»).
  Полные якоря — в `refs_fs14c.py`.
- Проверка ссылок — `refs_fs14c.out.txt`: 23 `OK`, 23 сдвига `NOT OK`, `ALL OK`.
- Образцы харнесса: FS13c (`C:/kyty/f287/fs13c/`, в git `docs/track-f/fs13c/`, печать `e2ee87ce`) — форма п. 634 / 660 / 661, установка
  бинаря на тег и возврат установленного из закреплённой копии, формы `fs13_v` / `fs13_w` / `fs13_z`, выход харнессом формы `b4_v`; F40c
  (`C:/kyty/f287/f40c/`) — члены Ф24 (`FixF24: mode=`, `init`, `init_owner`, `pump_stop_expired`) и строки пультов; F44c (`C:/kyty/f287/f44c/`)
  — член `FixF29: mode=` и строки `FixF29: overflow` / `Accessed non-GPU cached memory`.

## 1. Бинарь

- **Бинарь тегов — FS14:** sha256 `013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd`, копия
  `C:/kyty/f287/bin/kyty_emulator_013e1974.exe` [c sha 2026-10-11 15:18Z]; строка версии в файле `KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91`
  (член строки ридера); FS14 = FS13 `ea6c6e9e` + `5c21c387`, `e3aa4b4d`, `57f9e528`, `c8836f14` (умолчание `KYTY_FIX_F24=1`) + `15c9d2f2`,
  `78e45af3` (умолчание `KYTY_FIX_F29=1`), worktree `C:/kyty/f287/fs14a/wt` HEAD `eb7e8b91` (п. 717); подпись трансляции `9177b426…` = FS13.
  FS14b — `PASS`, RC 0, бинарь без изменений (п. 720). Ставится в папку эмулятора только на тег под замком, после копии кэшей; член допуска —
  установленный во время тега = `013e1974` по полному sha256.
- **Установленный — FS13** `abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73` [c sha 2026-10-11 15:18Z], закреплённая копия
  `C:/kyty/f287/bin/kyty_emulator_abab2196.exe` (= FS13 [c]); до тега (вне и внутри замка) = после возврата из закреплённой копии (член
  допуска). `C:/kyty/build/install` и `C:/kyty/build` не трогаются.
- **Окружение тегов:** цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла (список оставшихся после снятия —
  `runs/<тег>/env_shell_after_unset.txt`); в `enter_scene.py` позиционно передаются только:

| тег | `KYTY_*` / `VK_*` окружения процесса эмулятора (поле `env` json; пути — любые) |
|---|---|
| `fs14_v` | `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden` `KYTY_FRAME_TRACE=lite` `KYTY_GATE_FILE=<путь>` `KYTY_SAMPLE_GATE=<путь>` `KYTY_QUEUE_TRACE=1` `KYTY_GPU_CLOCK_PIN=1` `KYTY_GPU_MARKERS=0` `KYTY_GPU_HANG_ABORT_S=8` `KYTY_REC=<путь>` |
| `fs14_w` | те же без `KYTY_REC`, плюс `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin` `VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000` |
| `fs14_z` | как `fs14_v`, плюс `KYTY_FIX_F24=0` `KYTY_FIX_F29=0` |

  Ни у одного тега: `KYTY_TEST_*`, иные `KYTY_FIX_*` (умолчания бинаря), `KYTY_GAME_PATCH`, `KYTY_DIAG_*`, `KYTY_S_REPLAY`,
  `KYTY_SHADER_SEED`, `KYTY_PIPELINE_PRECACHE`, `KYTY_GPU_CHECKPOINTS`, `VK_LAYER_MESSAGE_ID_FILTER`. Окно 1280×720,
  `--shader-validation false`, без `--rd`; precache по умолчанию.

## 2. Кэши, сохранения и манифест

- Состав — пять каталогов харнесса FS13c: `_ShaderCache` (с `PPSA21564/pipelines.bin`, каталогом варианта
  `variant_fixb26_fixb1b_fixf10_fixf19` и `replay/`), `_ShaderSeeds`, `_PipelineCache`, `_SaveData`, GLCache драйвера.
- **Манифест до первого тега** (без замка, только чтение, после конца серии F46c, 2026-10-11 16:04:28Z): `C:/kyty/f287/fs14c/base/base.tsv` —
  4 832 файла, 1 304 969 313 байт, `listsha` `983cc56317a1bccd3c8cf55f46b936a2f2942803728689126b7209322f6977b2`. Против манифеста базы FS13c (`fs13c/base/base.tsv`, 08:27Z) — `DIFFER` только в GLCache (6 строк только до, 22 только после: блоб `523f3a9b…` вырос, новые `1bde1f7e…` и др.); прочие четыре каталога — без отличий. Чем дописан GLCache между 08:27Z и 16:04Z — [U] (кэш драйвера общий; сборки и стенды звеньев без замка) (`base/base_vs_fs13c.txt`) [c].
- **Каждый тег:** под замком — манифест и копия пяти каталогов (`runs/<тег>/before_*`), затем установка копии FS14; после тега — возврат
  FS13 из закреплённой копии, возврат каталогов (`rm` + `mv`) и манифест после; член допуска — `manifest cmp EQUAL` до/после. Сверка «до
  тега = база» — строкой (`runs/<тег>/base_cmp.txt`), не членом. Сеанс пользователя во время тега — возврат GLCache слиянием
  (`snap_fs14c.py merge-return`), член — «манифест до ⊆ после, лишние — только GLCache» (`mfsub_fs14c.py`); тег — помеха. Неудачный возврат,
  установленный ≠ FS13 или `cmp` ≠ EQUAL — `RETURN_FAILED`, замок остаётся, вопрос лиду.

## 3. Форма тегов (один вызов — один замок, одна попытка)

| тег | форма | вызов `enter_scene.py` из `go_fs14c.sh` (кроме общего `--level underwater_aerial_garden --attempts 1 --no-install --require-idle --gates-file gates_default.txt --pred pred/fs14c_seal.md`) |
|---|---|---|
| `fs14_v` | `fs13_v` / `f24_n1` без ручки, выход харнессом формы `fs12_v` (= `b4_v`) | `fs14_v --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `fs14_w` | `fs13_w` без ручки | `fs14_w --stable-draws 100 --timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold 310 VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |
| `fs14_z` | контроль отката обеих ручек, V Sky Garden | `fs14_z --stable-draws 300 --timeout 480 --rec --hold 150 KYTY_FIX_F24=0 KYTY_FIX_F29=0 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |

- **Порядок:** `fs14_v`, `fs14_w`, `fs14_z` — каждый своим вызовом и своим замком; блоков тегов нет, окна между тегами нет, проверка сторожа
  одна на вызов — сразу после взятия замка, до манифеста (п. 634, 660, 661). Серия FS14c начинается после строки `lock released` последнего
  тега серии F46c `HPP-800` (п. 714(б)(2)).
- **Выход (все теги):** в конце удержания `enter_scene.py` посылает `WM_CLOSE` окнам процесса (в логе — `Event: quit`) и ждёт `CLOSE_WAIT_S`
  = 40 с (таймаут харнесса формы `b4_v`), иначе снимает процесс; запись попытки несёт `close_posted`, `close_rc`, `close_killed`, `close_s`.
- **Цепочка:** `chk_fs14c.sh <тег>` (файл `STOP`, замок, новые комментарии `HPP-814`, очередь P > F > S — строка `times.txt`) →
  `launch_fs14c.sh <тег>` (первая строка — линтер `form634_check.py --series`; дисплей: OFF — `dispstate.py --wake` и повторная проверка,
  п. 623(в)(1); очередь; только запуск) → `wait_fs14c.sh <тег>` ≤ 540 с за команду, отдельными командами → `post_fs14c.sh <тег>` вне замка
  (у `fs14_v`, `fs14_z`: `s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`; у `fs14_v` пара `pair_fs14_v_fs13_v.png` — лист тега слева, лист
  `fs13_v` FS13c справа; затем ридер, таблица и член темпа `tempo_fs14c.py` с формой W из строки `dryrun ` сухого плана). `go_fs14c.sh`:
  линтер, sha копии FS14, закреплённой копии FS13 и установленного, шлюз `procload.py` (маска `<app>`), проверка живого прогона по API
  (`runchk_fs14c.py`), загрузка хоста (строка), дисплей ON до замка и удержание до `lock released`, замок `C:/kyty/SEALED_RUN.lock`
  (`noclobber`), строки `lock taken|released <тег> <UTC>` в `runs/lock.log`, **сразу после замка** — сторож игры и сеанса пользователя
  (найден — замок снят, файлы не тронуты, помеха), затем манифест и копия, установка копии FS14, снятие `KYTY_*`/`VK_LAYER_*` шелла со
  строкой оставшихся, сторожа во время тега (опрос ≤ 2 с; найден — убийство своего эмулятора по pid), возврат FS13 и кэшей,
  `manifest cmp`, дисплей после. Повтора тега с тем же именем нет (`runs/<тег>` есть — отказ).

## 4. Правило чтения (ридер `fs14c_read.py`; вердикта нет)

**Определения.** Строка входа — первая строка, кончающаяся `GuestOut: Level has started: underwater_aerial_garden`; первая `GuestOut` —
первая строка со словом `GuestOut`. Первый кадр сцены — первая `FrameTrace: n=` после строки входа с `draws` ≥ 100; «после первого кадра
сцены» — строки `FrameTrace` после него (сам он не считается; строка печатает счёт и с ним). `FixF24` — строка `FixF24: mode=<0|1> b24=<0|1>`
(`joyPump.cpp:457`): ≥ 1 разобранная, неразборных 0, каждая `mode=<ожидаемый> b24=1` (1 у `fs14_v`/`fs14_w` — умолчание без переменной, 0 у
`fs14_z`), первая — раньше первой `GuestOut`. `FixF24: init` — строка с `FixF24: init tid=` раньше первой `GuestOut`. `init_owner` — строка
`FixF24: init_owner hid= helper= msg= pump= main=` (`joyPump.cpp:97`): ровно одна разобранная, неразборных 0, раньше первой `GuestOut`;
«жив» — `hid` ≠ 0 и `helper` ≠ 0; «владелец» — `hid` = `helper` = `pump` ≠ `main`. Иные строки `FixF24:` у `fs14_z` — все строки `FixF24:`,
кроме строк режима (`init`, `init_owner`, `pump_*`, `open failed`, `add event`, `wait error`, прочие, неразборные строки режима). `FixF29` —
строка `FixF29: mode=<0|1>` (`faultManager.cpp:84`, конструктор `FaultManager`): ≥ 1 разобранная, неразборных 0, каждая `mode=<ожидаемый>`
(1 у `fs14_v`/`fs14_w`, 0 у `fs14_z`), первая — раньше первой `GuestOut`; иные строки `FixF29:` у `fs14_z` — `overflow`, неразборные, прочие.
`pump_stop_expired` — строка с `FixF24: pump_stop_expired`, `overflow` — с `FixF29: overflow`, `accessed` — с `Accessed non-GPU cached
memory`; счёт по всему логу и всему stdout. `FixF25` — `FixF25: mode=<0|1>` (`fileSystem.cpp:431`), ожидаемый 1; `FixF21` — `FixF21:
mode=<0|1> wait_ms=<n>`, ожидаемый 1; `FixB12` — `FixB12: mode=<n>`, ожидаемый 1 (все — умолчания FS13). `quit` — первая строка лога с
`Event: quit`. `wait_expired` — строка с `FixF21: wait_expired`, счёт по всему логу и всему stdout. `ExitFatal:` — строка стенда (stderr),
счёт по всему логу и всему stdout. Маркеры смерти — `Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`,
`ErrorDeviceLost`.

**Допуск (член не выполнен — `NOT_ADMITTED`, тег не читается; повтор — пунктом лида, помеха попытку не тратит, п. 273(з)):** json есть;
`binary_sha256` = FS14 `013e1974`; установленный во время тега = `013e1974`; установленный до = после = FS13 `abab2196`; `prereg` = sha256
этой печати (`pred/fs14c_seal.md`); `env` = форма §1 ровно (ключи `KYTY_*`/`VK_*`; пути — любые; без `KYTY_FIX_*` у `fs14_v`/`fs14_w`,
`KYTY_FIX_F24=0` и `KYTY_FIX_F29=0` у `fs14_z`; без `KYTY_GAME_PATCH`); в `env` нет ключей `KYTY_TEST_*`; строк `ExitFatal:` 0 в логе и 0 во
всём stdout; последний `--vulkan-validation` — `true` только у `fs14_w`, иначе `false`; `--shader-validation false`; без `--rd`; аргументы
гостя `-lvl underwater_aerial_garden` и файл уровня харнесса; опция удержания (330 / 310 / 150); лог есть; stdout есть; исход входа `ok`;
строка входа есть; строк `Window … minimized` и `Recovering Vulkan swapchain` 0; подпись `9177b426` и каталог
`variant_fixb26_fixb1b_fixf10_fixf19`; строк `GamePatch:`, `DiagB32`, `TestLogStall:`, `TestHidLoss` 0; `manifest cmp EQUAL`; итоговая строка
`LogAsync: full_waits=` ровно одна со всеми полями (нет — помеха «снят убийством», п. 615(б)(6)) — 25 членов. Харнесс (вне ридера, п. 620(г),
621(б)): дисплей ON до замка и после `lock released` (OFF после — помеха `DISPLAY_OFF`); темп сцены (`tempo_fs14c.py` = `tempo_fs13c.py`):
средний `dt` < 100 мс (форма W — < 200 мс), иначе `SERIES_STOP` и вопрос лиду; игра и сеанс пользователя во время тега — помеха.

| тег | члены (буква п. 710(г)(3) с п. 712(г)(3)) | группа формы |
|---|---|---|
| `fs14_v` | удержание ≥ 300 с после первого кадра сцены (сумма `dt_us`); процесс жив до конца удержания (`outcome ok`, `hold_exit` пуст); 0 маркеров смерти (лог и stdout); 0 кадров `dt_us` ≥ 1 000 000 после первого кадра сцены; записей `.idx` видео ≥ 3 000; 0 одно-кадровых глитчей `s51_vidglitch.py`; лист для лида сделан; до первой `GuestOut`: `FixF24: mode=1 b24=1`, `FixF24: init`, `init_owner` жив (`hid` ≠ 0, `helper` ≠ 0), `init_owner` `hid` = `helper` = `pump` ≠ `main`, `FixF25: mode=1`, `FixF21: mode=1`, `FixB12: mode=1`, `FixF29: mode=1`; строка `Event: quit` в логе есть; после неё 0 `--- Fatal Error ---` в логе и 0 во всём stdout; 0 `FixF21: wait_expired` (весь лог и весь stdout); 0 `FixF24: pump_stop_expired` (весь лог и весь stdout); процесс кончился до таймаута харнесса (`close_killed` false, `close_rc` не пуст) — 20 | `fs13_v` (= `fs12_v`): `LogAsync: mode=1` ровно один раз до первой `GuestOut`; итоговая строка есть; `drain_timeouts` 0; `FixB13: mode=1` до первой `GuestOut`; строка `FixB12Stat:` есть (≥ 1 разобранная) — 5 |
| `fs14_w` | процесс жив до конца удержания (`hold_s` ≥ 310, `hold_exit` пуст); 0 маркеров смерти; 0 `[Vulkan][E]`; 0 строк предела слоя (`this will be the last time reporting it`); `[Vulkan][W]` > 0 (положительный контроль слоя); до первой `GuestOut`: `DualSrcBlend: supported=1 enabled=1`, `FixF24: mode=1 b24=1`, `FixF29: mode=1` — 8 | `fs13_w`: `FixF25: mode=1`; `FixF21: mode=1`; `LogAsync: mode=1` до первой `GuestOut`; нет `VALIDATION_STOP` (`[Vulkan][E]` и процесс не дожил); `FixB13: mode=1`; `FixB12: mode=1` — 6 |
| `fs14_z` | удержание ≥ 120 с после первого кадра сцены; процесс жив; 0 маркеров смерти (лог и stdout); `FixF24: mode=0 b24=1` до первой `GuestOut`; иных строк `FixF24:` 0; `FixF29: mode=0` до первой `GuestOut`; иных строк `FixF29:` 0 — 7 | — |

**Строки (не члены):** у каждого тега — число строк `FixF24: pump_update_long`, `FixF24: open failed` и строк пультов хоста `Controller …`
(первая — строкой; пульт хоста в теге — справка, не помеха), `FixF24: pump_stop_expired` (лог / весь stdout), строки `FixF24:` по видам и
поля `init_owner`; число `FixF29: overflow` и `Accessed non-GPU cached memory` (лог / весь stdout, первые строки; > 0 `overflow` —
свидетельство Ф29 в игре, пункт лида); строки `FixF25: read failed twice` / `KernelRead: direct read failed` (лог / stdout); код выхода
`close_rc` (и hex) и `close_s` (секунды от посылки `WM_CLOSE` до конца процесса) у каждого тега, строка `Event: quit`, `--- Fatal Error ---`
после неё и во всём stdout (у `fs14_v` они же — члены; у `fs14_z` буква: «выход харнессом — строкой»; у `fs14_w` — справка); последняя
строка `FixB12Stat:` и их число; иные строки `FixF21:`; строки `ExitFatal:` (лог/stdout, они же — допуск); `[Vulkan][E]` у V и `fs14_z`
(валидации нет — справка); у `fs14_z` — кадры ≥ 1 с, видео, глитчи, лист, `FixF21`, `FixF25`, `wait_expired`, `FixB12`, `FixB13`,
`LogAsync`; строка версии в копии бинаря; строка `Fork build`; события окна кроме допуска. Ридер печатает `MEMBERS ALL YES / NOT ALL YES` —
это не вердикт.

**Что читает лид, не ридер:** лист `fs14_v` и пару с `fs13_v` (видимые дефекты); каждый глитч детектора кадрами ± 2; лист `fs14_z`
(справка); чтение и установка — FS14d.

## 5. Повторы, отказы, остановка

- Одна попытка на тег. Повтор `<тег>_r1`…`_r3` — только пунктом лида по помехе (допуск не выполнен; `DISPLAY_OFF`; пользователь во время
  тега; `enter_scene` не запустил эмулятор); `launch_fs14c.sh` без `FS14C_REPEAT_OK=1` повтор не запускает. Провал члена п. 710(г)(3) /
  712(г)(3) — не помеха, повтора нет, чтение FS14d.
- Отказ шлюза `procload`, сторожа после замка, очереди или дисплея до старта эмулятора — не попытка; вывод отказанного вызова переносится
  в `old/` (п. 309(и)). `SERIES_STOP` — следующий тег не запускается до пункта лида. `RETURN_FAILED` — замок остаётся. Файл
  `C:/kyty/f287/STOP` — стоп перед следующей командой. Перед каждым вызовом — `chk_fs14c.sh` (API, комментарии звена, очередь) строкой
  `times.txt`. Очередь замка P > F > S (п. 322(г)); в F — п. 714(б). Выключенный дисплей — не причина остановки, харнесс будит его сам
  (п. 623(в)).
- **Бюджет замка — ≤ 25 мин на тег** (оценка [I]: копия кэшей ≈ 1,3 ГБ, вход ≈ 20–60 с, удержание 330 / 310 / 150 с, вход W до 900 с,
  выход ≤ 40 с, возврат; FS13c — 3 тега, замок 08:31–09:15Z). Вызов `launch_fs14c.sh` — с пределом инструмента ≥ 300 с.

## 6. Не заявляется

П. 710(з), 712(з), 717, 720(е) целиком: что FS14 установлен (до FS14d); что настоящий пульт хоста на `JoyPump` работает; что проход с
≥ 1 024 битами случается в игре; что теги проверяют правки в игре (стенды Ф24 и Ф29 теги не включают — проверено только «нет вреда» и откат);
что откат `KYTY_FIX_F24=0` и `KYTY_FIX_F29=0` на FS14 равен FS13 байт в байт (по поведению); что код выхода 0 — свойство правки; что прочие
`SCENE_OK` держатся на FS14; что реестр полон. Ни одно число — не выигрыш; время кадра — справка; 60 FPS не обещаются; цель (B) не меняется;
установленный FS13 `abab2196` не меняется.

## 7. Инструменты и фикстуры (до первого тега; файлы `C:/kyty/f287/fs14c/`, копия — `docs/track-f/fs14c/`)

- `go_fs14c.sh` — порт `go_fs13c.sh` (форма п. 634: сторож один раз сразу после замка; установка копии FS14 на тег и возврат FS13 из
  закреплённой копии; формы `fs13_v` / `fs13_w` / `fs13_z`, у `fs14_z` ручки `KYTY_FIX_F24=0 KYTY_FIX_F29=0`); `launch_fs14c.sh` — порт
  `launch_fs13c.sh` (повтор — только с `FS14C_REPEAT_OK=1`); `post_fs14c.sh` — порт `post_fs13c.sh` (пара `fs14_v` с листом `fs13_v`
  FS13c; план — `grep '^dryrun '`).
- `fs14c_read.py` — ридер (§4), порт `fs13c_read.py` + члены и строки Ф24 из `f40c_read.py` и Ф29 из `f44c_read.py`.
- Копии FS13c (`mk_fs14c.py`): без изменений — `dispstate.py`, `procload.py`, `idle142.py`, `launch_run.py`, `run_safety99.py`,
  `manifest_fs4c.py`, `sheet142.py`, `gates_default.txt`, `gates.req`, `sample.req`; с переносом имён (`fs13c` → `fs14c`, `HPP-789` →
  `HPP-814`): `guard_fs14c.py`, `hold_fs14c.py`, `hostload_fs14c.py`, `runchk_fs14c.py`, `queue_fs14c.py`, `snap_fs14c.py`,
  `mfsub_fs14c.py`, `wait_fs14c.sh`, `chk_fs14c.sh`, `tempo_fs14c.py`; `enter_scene.py` — файл FS13c с перенесённым `ROOT`. Копия
  `launch_run.py` в git — с маской `<app>`.
- **Последний вывод наборов** (полные sha — `SHA256SUMS_seal.txt`):
  - `test_fs14c_read.out.txt` — первая строка `suite test_fs14c_read.py sha256 7f13c55d… target fs14c_read.py sha256 65e8c743…`,
    `checks 471 failed 0`, `ALL OK` (порт набора FS13c: чистые теги трёх форм; каждый член допуска у каждого тега, включая `KYTY_TEST_*`,
    `ExitFatal:` в логе и в stdout, `KYTY_FIX_F24` / `KYTY_FIX_F29` в окружении `fs14_v`/`fs14_w` и их отсутствие у `fs14_z`, строку
    `TestHidLoss`; каждый член каждой формы; края 1 000 000 / 999 999, 300 с, 120 с, `hold_s` 309,9 / 310, 2 999 / 3 000, `draws` 99 / 100;
    по фикстуре на каждый новый член Ф24 и Ф29 (п. 712(г)(3)): `FixF24`/`FixF29` противоположный / нет / неразборный / после `GuestOut` /
    вторая строка противоположная, `b24=0`, `init` нет / после `GuestOut`, `init_owner` нет / два / неразборный / `hid` 0 / `helper` 0 /
    `hid` ≠ `pump` / `pump` = `main`, `pump_stop_expired` в логе и в stdout; у `fs14_z` каждый вид иной строки `FixF24:` и `FixF29:` — член;
    строки `pump_update_long`, `open failed`, `Controller`, `overflow`, `accessed` — строки, не члены; таблица; вывод в строгий cp1250, ASCII).
    Мутантов нет (п. 710(г)(3)).
  - `regress_fs14c.out.txt` — ридер на настоящих файлах: `f24_n1` (F40c, `ddf0ca91`, `KYTY_FIX_F24=1`, установленный FS13) как `fs14_v` —
    допуск не выполнен ровно по 3 членам (бинарь json, установленный на теге, `extra KYTY_FIX_F24=1`), члены — все ДА, кроме `FixF25: mode=1`
    (строки в FS12 нет) и `FixF29: mode=1` (строки до F44a нет): все члены Ф24 — ДА (ближайший положительный контроль буквы Ф24); `f29_v`
    (F44c, `d760708d`, `KYTY_FIX_F29=1`) как `fs14_v` — допуск не выполнен ровно по 3 (бинарь json, установленный на теге, `extra
    KYTY_FIX_F29=1`), члены — все ДА, кроме четырёх членов Ф24 (строк до F40a нет) и `FixF25: mode=1`: `FixF29: mode=1` — ДА (положительный
    контроль буквы Ф29); `fs13_v` / `fs13_w` (FS13) как `fs14_v` / `fs14_w` — допуск не выполнен ровно по 3 (бинарь json, установленный на
    теге, установленный до/после FS12), члены — все ДА, кроме членов Ф24 и Ф29 (`FixF25` — ДА); `fs13_z` как `fs14_z` — допуск не выполнен
    ровно по 4 (+ `missing KYTY_FIX_F24`, `extra KYTY_FIX_F25=0`, `missing KYTY_FIX_F29`), члены — все ДА, кроме `FixF24: mode=0 b24=1` и
    `FixF29: mode=0` (иных строк `FixF24:`/`FixF29:` 0 — ДА); строки пультов, `pump_update_long`, `open failed`, `pump_stop_expired`,
    `overflow` у всех пяти — 0; `Accessed non-GPU cached memory` в логе — 36–37 у всех пяти, в stdout 0 (строка, не член); `close_rc` 0,
    `close_s` 4,0–4,3; первая строка `suite regress_fs14c.py sha256 05cc454a… target fs14c_read.py sha256 65e8c743…`, `ALL OK`.
  - `test_tools_fs14c.out.txt` — первая строка `suite test_tools_fs14c.py sha256 ae82641b… target go_fs14c.sh sha256 95ac520f…`,
    `checks 103 failed 0`, `ALL OK` (сухой план трёх тегов и `_r1`/`_r3`; нет `KYTY_TEST_` в планах; `KYTY_FIX_` только
    `KYTY_FIX_F24=0 KYTY_FIX_F29=0` у `fs14_z`; план `post_fs14c.sh` по строке `dryrun `, форма W, первая строка сухого вывода — `ALL OK`
    линтера; пара с листом `fs13_v`, лист на диске; отказы по имени у `go`/`launch`/`post`; повтор без `FS14C_REPEAT_OK`; линтер `--series`;
    первая исполняемая строка — линтер; литералы sha и пути копий, sha копий на диске; сторож после замка до манифеста; установка после копии
    кэшей; возврат FS13 до `installed_after`; своя задача `HPP-814` у `queue`/`runchk`/`chk`; `tempo_fs14c.py` = `tempo_fs13c.py`; `ROOT` и
    `CLOSE_WAIT_S`; ASCII скриптов; вывод в строгий cp1250).
  - `refs_fs14c.out.txt` — 23 ссылки, `ALL OK`.
  - **Линтер формы п. 634 / 661** — `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` (sha256 — `SHA256SUMS_seal.txt`); он же — первая
    исполняемая строка `launch_fs14c.sh` и `go_fs14c.sh`:

```
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/fs14c
ALL OK
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --text C:/kyty/f287/fs14c/pred/fs14c_seal.md
ALL OK
```

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте звена)

1. «Время выхода — строкой» — `close_s` (от посылки `WM_CLOSE` до конца процесса, мера харнесса формы `b4_v`); у строк лога в `lite`
   своего времени нет.
2. «После `Event: quit` 0 `--- Fatal Error ---`» у `fs14_v` — в логе после строки `quit` и во всём stdout (в stdout строки `quit` нет —
   строже буквы); печатаются оба счёта лога (после `quit` и весь).
3. «0 `FixF21: wait_expired`» и «0 `FixF24: pump_stop_expired`» у `fs14_v` — по всему логу и всему stdout (строже буквы «после
   `Event: quit`»).
4. Группы формы (`fs13_v` у `fs14_v`, `fs13_w` у `fs14_w`) — отдельной группой рядом с буквой п. 710(г)(3) («форма `fs13_v` / `fs13_w`»);
   `FixF25: mode=1` и `FixF21: mode=1` у `fs14_w` — в группе формы (`fs13_w` их несла), в букве `fs14_w` — `DualSrcBlend`, `FixF24`,
   `FixF29`; чтение — лида.
5. «Лист рядом с `fs13_v`» — `sheet_fs14_v.png` и пара `pair_fs14_v_fs13_v.png` (справа — `fs13_v`, установленный FS13); смотрит лид.
6. `fs14_z`: опция удержания 150 с (член — ≥ 120 с после первого кадра сцены); видео и лист пишутся (справка); «иные строки `FixF24:` /
   `FixF29:` 0» — по логу (строки пишутся `LOGF`).
7. Допуск без `KYTY_TEST_*` и без строк `ExitFatal:` и `TestHidLoss` — унаследован из формы FS13c (п. 686(в)) и F40c для всех трёх тегов:
   стенды выхода и потери HID в FS14 есть и включаются только переменной.
8. «`init_owner` с `hid` ≠ 0, `helper` ≠ 0, `hid` = `helper` = `pump` ≠ `main`» — двумя членами (жив / владелец), как в F40c (п. 696).

## 9. Отчёт тегов

(заполняется после тегов; печать выше не меняется)
