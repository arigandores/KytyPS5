# F44c (`HPP-793`, Harness Engineer): тег `f29_v` «нет вреда» при `KYTY_FIX_F29=1` на бинаре F44a `d760708d` — печать до тега

Трек F, Ф29, итерация кода 1 `KYTY_FIX_F29`, член п. 698(д)(4) (п. 701 — приёмка F44a, бинарь тега `d760708d…`; п. 707 — ревью F44b
`PASS`, RC 0, бинарь тега — копия F44a без изменений). Разделы 0–8 — печать (до тега; после неё цепочка, ридер и правила чтения не
меняются); раздел 9 — отчёт тега (строки ридера, без вердикта; чтение — F44d `HPP-794` по п. 698(д), 701(б), 707(б)). Автор всех
разделов — Harness Engineer. Метки: [c] — код/лог прочитан или пересчитан, [I] — вывод, [U] — неизвестно. Время — UTC.

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f44c.py`, отрицательный контроль сдвигом)

- Задание — п. 698: `d0bfaf1f:docs/ROADMAP.md:24603` (якорь «698. **Звено F43b трека F (`HPP-784`, лид; приёмка F43a `HPP-783`)»;
  +1 — «(а) **Приёмка строкой. F43a ✓**»); член (д)(4) — `d0bfaf1f:docs/ROADMAP.md:24613` (якорь «(4) **Тег под замком — «нет
  вреда»** (F44c;»; +1 — «**Чтение:** (1)–(4) все ✓ — **Ф29 `FIXED`**»); не заявляется — `d0bfaf1f:docs/ROADMAP.md:24623` (якорь
  «(м) **Не заявляется:** что проход с ≥ 1 024 битами бывает в игре»; +1 — пустая строка).
- Приёмка F44a и бинарь тега — п. 701: `d0bfaf1f:docs/ROADMAP.md:24637` (якорь «701. **Звено F44a трека F (`HPP-791`, Emu
  Engineer)»; +1 — «(а) **Приёмка строкой. F44a ✓.**»). Ревью F44b и снятие блокера — п. 707: `d0bfaf1f:docs/ROADMAP.md:24688` (якорь
  «707. **Звено F44b трека F (`HPP-792`, Red Team)»; +1 — «(а) **Приёмка строкой. F44b ✓.**»); звенья — `d0bfaf1f:docs/ROADMAP.md:24691`
  (якорь «(в) **Звенья.** F44b `HPP-792` — approve»; +1 — «(г) **Не заявляется:** что Ф29 исправлен»).
- Строки кода бинаря тега (коммит F44a `15c9d2f2`, в worktree — `e148f54c`, `git cherry` `-`): чтение ручки —
  `15c9d2f2:src/graphics/host_gpu/renderer/cache/faultManager.cpp:43` (якорь «"KYTY_FIX_F29"»; +1 — «return enabled;»); строка
  переполнения — `…/faultManager.cpp:57` (якорь «LOGF("FixF29: overflow pass=%»; +1 — «pass.area, parse.raw, parse.count, total»);
  строка режима — `…/faultManager.cpp:79` (якорь «LOGF("FixF29: mode=%d»; +1 — пустая строка); строка промаха —
  `…/faultManager.cpp:250` (якорь «LOGF("Accessed non-GPU cached memory at 0x%016"»; +1 — «},»). Умолчания FS12 в группе формы:
  `FixF21: mode=` — `730ed40a:src/common/subsystems.cpp:80` (якорь «LOGF("FixF21: mode=%d wait_ms=%u»; +1 — «}»); `FixB12: mode=` —
  `730ed40a:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:604` (якорь «LOGF("FixB12: mode=%d»; +1 — «}»).
- Проверка ссылок — `refs_f44c.out.txt`: 12 `OK`, 12 сдвигов `NOT OK`, `ALL OK` (генератор `draft/gen_refs_f44c.py` — якорь найден
  ровно один раз, +1 сверен).
- Образец харнесса — F38c (`C:/kyty/f287/f38c/`, в git `docs/track-f/f38c/`; сам — порт FS12c): форма п. 634 / 660 / 661, установка
  бинаря на тег и возврат установленного из закреплённой копии, форма `fs12_v`, выход харнессом формы `b4_v`, план `post` по строке
  `dryrun `. Отличия: бинарь тега F44a, установленный FS13 (п. 703–704; общее правило звеньев «после FS13d — бинарь, названный FS13d»),
  ручка `KYTY_FIX_F29=1`, член `FixF29: mode=1`, строки `FixF29: overflow` / `Accessed non-GPU cached memory`.

## 1. Бинарь

- **Бинарь тега — копия F44a:** sha256 `d760708d416d4fb5d494a9ca98c0417f2bf1911403f5334752783ed7a3b27c5f`, копия
  `C:/kyty/f287/bin/kyty_emulator_d760708d.exe` = выход сборки F44a `C:/kyty/f287/f44a/build/install/kyty_emulator.exe` [c sha, набор
  `test_tools_f44c.py`]; строка версии `KytyPS5-2026-09-15-6a2987a-1915-ge148f54c` (worktree `730ed40a` + `e148f54c`, `git cherry` `-`,
  подпись трансляции `9177b426…` = FS12 — п. 701(а) и отчёт F44a §1). F44b — код PASS, бинарь без изменений (п. 707(а)). Ставится в
  папку эмулятора только на тег под замком, после копии кэшей; член допуска — установленный во время тега = `d760708d` по полному sha256.
  Бинарь — от FS12a: умолчания FS12 (`KYTY_FIX_F21`, `KYTY_FIX_B12`, `KYTY_FIX_B13`, `KYTY_FIX_B36` = 1), Ф25 (`KYTY_FIX_F25`) в нём нет.
- **Установленный — FS13** `abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73` [c sha 2026-10-11T11:03:01Z], закреплённая
  копия `C:/kyty/f287/bin/kyty_emulator_abab2196.exe` (= FS13 [c]); до тега (вне и внутри замка) = после возврата из закреплённой копии
  (член допуска). `C:/kyty/build/install` и `C:/kyty/build` не трогаются.
- **Окружение тега:** цепочка снимает все `KYTY_*` и `VK_LAYER_*` шелла (список оставшихся — `runs/f29_v/env_shell_after_unset.txt`); в
  `enter_scene.py` позиционно передаются только `KYTY_FIX_F29=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`. Поле `env` json (что получил
  процесс эмулятора) ровно: `KYTY_GUEST_ARGS=-lvl underwater_aerial_garden` `KYTY_FRAME_TRACE=lite` `KYTY_GATE_FILE=<путь>`
  `KYTY_SAMPLE_GATE=<путь>` `KYTY_QUEUE_TRACE=1` `KYTY_GPU_CLOCK_PIN=1` `KYTY_GPU_MARKERS=0` `KYTY_GPU_HANG_ABORT_S=8` `KYTY_REC=<путь>`
  `KYTY_FIX_F29=1`. Нет: `KYTY_TEST_*`, иные `KYTY_FIX_*` (прочие умолчания FS12 — бинарём), `KYTY_GAME_PATCH`, `KYTY_DIAG_*`,
  `KYTY_S_REPLAY`, `KYTY_SHADER_SEED`, `KYTY_PIPELINE_PRECACHE`, `KYTY_GPU_CHECKPOINTS`, `VK_LAYER_*`. Окно 1280×720,
  `--vulkan-validation false`, `--shader-validation false`, без `--rd`; precache по умолчанию.

## 2. Кэши, сохранения и манифест

- Состав — пять каталогов харнесса F38c: `_ShaderCache` (с `PPSA21564/pipelines.bin`, каталогом варианта
  `variant_fixb26_fixb1b_fixf10_fixf19` и `replay/`), `_ShaderSeeds`, `_PipelineCache`, `_SaveData`, GLCache драйвера.
- **Манифест до тега** (без замка, только чтение, 2026-10-11 10:53Z): `C:/kyty/f287/f44c/base/base.tsv` — `manifest base/base.tsv files 4832 bytes 1304938827 listsha db3e550e95429f28265b9c9cf954d512e3374aa81e9e4ce1253741652a4dc436`; против манифеста после последнего тега F40c (`f24_m1`) — `manifest cmp EQUAL files 4832 listsha db3e550e95429f28265b9c9cf954d512e3374aa81e9e4ce1253741652a4dc436` — строка, не член.
- **Тег:** под замком — манифест и копия пяти каталогов (`runs/f29_v/before_*`), затем установка копии F44a; после тега — возврат FS13 из
  закреплённой копии, возврат каталогов (`rm` + `mv`) и манифест после; член допуска — `manifest cmp EQUAL` до/после (это и есть «возврат
  с `cmp EQUAL`» п. 698(д)(4)). Сверка «до тега = база» — строкой (`runs/f29_v/base_cmp.txt`), не членом. Сеанс пользователя во время
  тега — возврат GLCache слиянием (`snap_f44c.py merge-return`), член — «манифест до ⊆ после, лишние — только GLCache» (`mfsub_f44c.py`);
  тег — помеха. Неудачный возврат, установленный ≠ FS13 или `cmp` ≠ EQUAL — `RETURN_FAILED`, замок остаётся, вопрос лиду.

## 3. Форма тега (один тег, один вызов — один замок, одна попытка)

| тег | форма | вызов `enter_scene.py` из `go_f44c.sh` (кроме общего `--level underwater_aerial_garden --attempts 1 --no-install --require-idle --gates-file gates_default.txt --pred pred/f44c_seal.md`) |
|---|---|---|
| `f29_v` | `fs12_v` (FS12c) с `KYTY_FIX_F29=1`, выход харнессом формы `b4_v` | `f29_v --stable-draws 300 --timeout 480 --rec --hold 330 KYTY_FIX_F29=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` |

- Форма серии — п. 634, 660–661: один тег, один замок; блоков тегов нет, окна нет; проверка сторожа одна на вызов — сразу после взятия
  замка, до манифеста.
- **Выход:** в конце удержания `enter_scene.py` посылает `WM_CLOSE` окнам процесса (в логе — `Event: quit`) и ждёт `CLOSE_WAIT_S` = 40 с,
  иначе снимает процесс; запись попытки несёт `close_posted`, `close_rc`, `close_killed`, `close_s`.
- **Цепочка:** `chk_f44c.sh f29_v` (файл `STOP`, замок, новые комментарии `HPP-793`, очередь P > F > S — строка `times.txt`) →
  `launch_f44c.sh f29_v` (первая строка — линтер `form634_check.py --series`; дисплей: OFF — `dispstate.py --wake` и повторная проверка,
  п. 623(в)(1); очередь; только запуск) → `wait_f44c.sh f29_v` ≤ 540 с за команду, отдельными командами → `post_f44c.sh f29_v` вне замка
  (`s51_vidglitch.py <rec> 4 6`, лист `sheet142.py`, пара `pair_f29_v_fs12_v.png` — лист тега слева, лист `fs12_v` FS12c справа; затем
  ридер, таблица и член темпа `tempo_f44c.py` с формой W из строки `dryrun ` сухого плана). `go_f44c.sh`: линтер, sha копии F44a,
  закреплённой копии FS13 и установленного, шлюз `procload.py` (маска `<app>`), проверка живого прогона по API (`runchk_f44c.py`),
  загрузка хоста (строка), дисплей ON до замка и удержание до `lock released`, замок `C:/kyty/SEALED_RUN.lock` (`noclobber`), строки
  `lock taken|released <тег> <UTC>` в `runs/lock.log`, **сразу после замка** — сторож игры и сеанса пользователя (найден — замок снят,
  файлы не тронуты, помеха), затем манифест и копия, установка копии F44a, снятие `KYTY_*`/`VK_LAYER_*` шелла со строкой оставшихся,
  сторожа во время тега (опрос ≤ 2 с; найден — убийство своего эмулятора по pid), возврат FS13 и кэшей, `manifest cmp`, дисплей после.
  Повтора тега с тем же именем нет (`runs/<тег>` есть — отказ).

## 4. Правило чтения (ридер `f44c_read.py`; вердикта нет)

**Определения.** Строка входа — первая строка, кончающаяся `GuestOut: Level has started: underwater_aerial_garden`; первая `GuestOut` —
первая строка со словом `GuestOut`. Первый кадр сцены — первая `FrameTrace: n=` после строки входа с `draws` ≥ 100; «после первого кадра
сцены» — строки `FrameTrace` после него (сам он не считается; строка печатает счёт и с ним). `FixF29` — строка `FixF29: mode=<0|1>`
(конструктор `FaultManager`, ссылка §0): ≥ 1 разобранная, неразборных 0, каждая `mode=1`, первая — раньше первой `GuestOut`.
`overflow` — строка с `FixF29: overflow` (только при `=1` и `raw` > 1 023, предел 32 на процесс; ссылка §0); `accessed` — строка с
`Accessed non-GPU cached memory` (визитор `ProcessFaultBuffer`, прежний `LOGF`; ссылка §0); обе считаются по всему логу и всему stdout.
`quit` — первая строка лога с `Event: quit`. `wait_expired` — строка с `FixF21: wait_expired` (stderr — пишется в `stdout_f29_v.txt`),
счёт по всему логу и всему stdout. `ExitFatal:` — строка стенда (stderr), счёт по всему логу и всему stdout. Маркеры смерти —
`Unhandled exception:`, `--- Fatal Error ---`, `--- Error ---`, `GpuHangAbort:`, `ErrorDeviceLost`.

**Допуск (член не выполнен — `NOT_ADMITTED`, тег не читается; повтор — пунктом лида, помеха попытку не тратит, п. 273(з)):** json есть;
`binary_sha256` = F44a `d760708d`; установленный во время тега = `d760708d`; установленный до = после = FS13 `abab2196`; `prereg` = sha256
этой печати (`pred/f44c_seal.md`); `env` = форма §1 ровно (ключи `KYTY_*`/`VK_*`; пути — любые; `KYTY_FIX_F29` = `1` ровно); в `env` нет
ключей `KYTY_TEST_*`; строк `ExitFatal:` 0 в логе и во всём stdout; последний `--vulkan-validation` — `false`; `--shader-validation false`;
без `--rd`; аргументы гостя `-lvl underwater_aerial_garden` и файл уровня харнесса; опция удержания 330; лог и stdout есть; исход входа
`ok`; строка входа есть; строк `Window … minimized` и `Recovering Vulkan swapchain` 0; подпись `9177b426` и каталог
`variant_fixb26_fixb1b_fixf10_fixf19`; строк `GamePatch:`, `DiagB32`, `TestLogStall:` 0; `manifest cmp EQUAL`; итоговая строка
`LogAsync: full_waits=` ровно одна со всеми полями (нет — помеха «снят убийством», п. 615(б)(6)) — 24 члена. Харнесс (вне ридера, п.
620(г), 621(б)): дисплей ON до замка и после `lock released` (OFF после — помеха `DISPLAY_OFF`); темп сцены (`tempo_f44c.py` =
`tempo_fs12c.py`): средний `dt` < 100 мс, иначе `SERIES_STOP` и вопрос лиду; игра и сеанс пользователя во время тега — помеха.

| тег | члены (буква п. 698(д)(4)) | группа формы `fs12_v` (FS12c, п. 683(г)(3)) |
|---|---|---|
| `f29_v` | удержание ≥ 300 с после первого кадра сцены (сумма `dt_us`); процесс жив до конца удержания (`outcome ok`, `hold_exit` пуст); 0 маркеров смерти (лог и stdout); 0 кадров `dt_us` ≥ 1 000 000 после первого кадра сцены; записей `.idx` видео ≥ 3 000; 0 одно-кадровых глитчей `s51_vidglitch.py`; лист для лида сделан; `FixF29: mode=1` до первой `GuestOut` — 8 | `FixF21: mode=1` до первой `GuestOut`; `FixB12: mode=1` до первой `GuestOut`; строка `Event: quit` в логе есть; после неё 0 `--- Fatal Error ---` в логе и 0 во всём stdout; 0 `FixF21: wait_expired` (весь лог и весь stdout); процесс кончился до таймаута харнесса (`close_killed` false, `close_rc` не пуст); `LogAsync: mode=1` ровно один раз до первой `GuestOut`; итоговая строка есть; `drain_timeouts` 0; `FixB13: mode=1` до первой `GuestOut`; строка `FixB12Stat:` есть — 11 |

**Строки (не члены):** число строк `FixF29: overflow` и `Accessed non-GPU cached memory` — в логе и во всём stdout, с первой строкой
каждого вида (буква п. 698(д)(4): «строкой отчёта (не член; `overflow` > 0 — свидетельство Ф29 в игре, пункт лида)»); иные строки
`FixF29:`; код выхода `close_rc` (и hex) и `close_s`; последняя строка `FixB12Stat:` и их число; `[Vulkan][E]` (валидации нет — справка);
строка версии в копии бинаря; строка `Fork build`; события окна кроме допуска. Ридер печатает `MEMBERS ALL YES / NOT ALL YES` — это не
вердикт.

**Что читает лид, не ридер:** лист `f29_v` и пару с `fs12_v` (видимые дефекты); каждый глитч детектора кадрами ± 2; чтение п. 698(д) —
F44d.

## 5. Повторы, отказы, остановка, очередь

- Одна попытка. Повтор `f29_v_r1`…`_r3` — только пунктом лида по помехе (допуск не выполнен; `DISPLAY_OFF`; пользователь во время тега;
  `enter_scene` не запустил эмулятор); `launch_f44c.sh` без `F44C_REPEAT_OK=1` повтор не запускает. Провал члена п. 698(д)(4) — не
  помеха, повтора нет, чтение F44d.
- Отказ шлюза `procload`, сторожа после замка, очереди или дисплея до старта эмулятора — не попытка; вывод отказанного вызова переносится в
  `old/` (п. 309(и)). `SERIES_STOP` — тег не запускается до пункта лида. `RETURN_FAILED` — замок остаётся. Файл `C:/kyty/f287/STOP` — стоп
  перед следующей командой. Перед вызовом — `chk_f44c.sh` (API, комментарии звена, очередь P > F > S) строкой `times.txt`.
- **Очередь замка (п. 322(г), 698(д)(4), 707(в)) — после F40c `HPP-772` и F42c `HPP-781`.** `queue_f44c.py` (копия F38c) держит только
  порядок треков P > F > S; порядок внутри F держат блокеры `HPP-793` (F40c и F42c) — тег вызывается, только когда оба `done` (по букве),
  либо пунктом лида, меняющим порядок; проверка — строкой `times.txt` перед вызовом.
- Выключенный дисплей — не причина остановки, харнесс будит его сам (п. 623(в)).
- **Бюджет замка — ≤ 25 мин** (оценка [I]: копия кэшей ≈ 1,3 ГБ, вход ≈ 20–60 с, удержание 330 с, выход ≤ 40 с, возврат). Вызов
  `launch_f44c.sh` — с пределом инструмента ≥ 300 с.

## 6. Не заявляется

П. 698(м) и 707(г) целиком: что Ф29 исправлен (вердикт — F44d по п. 698(д)); что проход с ≥ 1 024 битами бывает в игре (в теге он не
вносится; строк `FixF29: overflow` = 0 этого не доказывают); что чтение за областью роняет игру или портит таблицу страниц; что правка
снимает потерю незаписанных битов (н2); что тег «нет вреда» доказывает исправление в игре; что числа стенда — частота в игре; что реестр
полон. Ни одно число — не выигрыш; время кадра — справка; 60 FPS не обещаются; цель (B) не меняется; установленный FS13 `abab2196` не
меняется.

## 7. Инструменты и фикстуры (до тега; файлы `C:/kyty/f287/f44c/`, копия — `docs/track-f/f44c/`)

- `go_f44c.sh` — порт `go_f38c.sh` (одна форма `f29_v`; бинарь тега F44a, установленный и закреплённый — FS13); `launch_f44c.sh` — порт
  `launch_f38c.sh` (повтор — только с `F44C_REPEAT_OK=1`); `post_f44c.sh` — порт `post_f38c.sh` (пара с листом `fs12_v`; план —
  `grep '^dryrun '`).
- `f44c_read.py` — ридер (§4), порт `f38c_read.py`: член `FixF29: mode=1` вместо `FixF25`, строки F29 вместо строк F25, установленный FS13.
- Копии F38c (`mk_f44c.py`): без изменений — `dispstate.py`, `procload.py`, `idle142.py`, `launch_run.py`, `run_safety99.py`,
  `manifest_fs4c.py`, `sheet142.py`, `gates_default.txt`, `gates.req`, `sample.req`; с переносом имён (`f38c` → `f44c`, `HPP-765` →
  `HPP-793`): `guard_f44c.py`, `hold_f44c.py`, `hostload_f44c.py`, `runchk_f44c.py`, `queue_f44c.py`, `snap_f44c.py`, `mfsub_f44c.py`,
  `wait_f44c.sh`, `chk_f44c.sh`, `tempo_f44c.py`; `enter_scene.py` — файл F38c с перенесённым `ROOT`. Копия `launch_run.py` в git — с
  маской `<app>`.
- **Последний вывод наборов** (полные sha — `SHA256SUMS_seal.txt`):
  - `test_f44c_read.out.txt` (sha256 `6fd73f1a90b491f3c0f2a429bbcbbfea1dd3c2eca684e649e043e7e4f2447975`) — первая строка `suite test_f44c_read.py sha256 41de1cfeb13663547752141bf93339bdf410ca128be2726b8d7abb598e9856f7 target f44c_read.py sha256 80db8b04c6289a5cac781dc9a3f6c31c334e429e5b712086a80fd9c8862053fd`, `checks 143 failed 0`, `ALL OK` (чистый тег; каждый член допуска, включая `KYTY_FIX_F29` = `0` / `true` / пусто / нет, иные `KYTY_FIX_*` (B12, B36, F21, F24, F25, F20, F26), `KYTY_TEST_*` тремя именами, `ExitFatal:` в логе и в stdout, установленный FS12 вместо FS13; каждый член буквы и группы; края 1 000 000 / 999 999, 300 с, 2 999 / 3 000, `draws` 99 / 100; `FixF29` `mode=0` / нет / `mode=10` / хвост / после `GuestOut` / вторая `mode=0` / неразборная / с префиксом / CRLF; строки F29 в логе и stdout — строки, члены ALL YES; вывод в строгий cp1250, ASCII).
  - `neg_f44c.out.txt` (sha256 `561987b32ae770c4fa3fe9fab8acad2cf52f3c5af14f8eb18100c126877f0838`) — 7 ручных правок ридера (вне печати, `neg/`; m2 — падение набора исключением), набор падает на каждой: m1 FixF29 member always YES 1 checks 143 failed 7; m2 env without KYTY_FIX_F29 1 -; m3 installed before / after any 1 checks 143 failed 4; m4 overflow in stdout dead 1 checks 143 failed 2; m5 accessed in log dead 1 checks 143 failed 4; m6 FixF29 moved to the form group 1 checks 143 failed 3; m7 glitches always YES 1 checks 143 failed 3; `ALL OK`.
  - `regress_f44c.out.txt` (sha256 `e7b3e0afb0c618ff79f642125fd63f514f7d9b64bbed988c02101fce765d795e`) — ридер на настоящих файлах `fs12_v` (FS12c) и `f25_v` (F38c) как `f29_v`: допуск не выполнен ровно по 4 членам у каждого (бинарь json, установленный на теге, установленный до/после — не FS13, `missing KYTY_FIX_F29`; у `f25_v` ещё `extra KYTY_FIX_F25=1`), члены обеих групп — все ДА, кроме `FixF29: mode=1` (строки до F44a нет — член жив); строки: `F29 rows of the fs12_v log: FixF29: overflow log 0 stdout 0; Accessed non-GPU cached memory log 36 stdout 0; FixF29 mode lines 0`; `ALL OK`.
  - `test_tools_f44c.out.txt` (sha256 `1da47f0c1d86e0782af630d3d73dcf43f6732dd7bc54bad4fadbffbf8575bb2d`) — первая строка `suite test_tools_f44c.py sha256 02aaadd2215ce1dda65d93a60f1a1ead18a2a0e2f69af456d5f16f061a30cf3f target go_f44c.sh sha256 96fae22bf82df8c4a01b7ba559a2cc87ce692d1de17c0cb5a33e5e4274f9a11a`, `checks 88 failed 0`, `ALL OK` (сухой план `f29_v` и `_r1`/`_r3`; нет `KYTY_TEST_`; `KYTY_FIX_` только `KYTY_FIX_F29=1`; план `post` по строке `dryrun `, форма W `no`; отказы по имени у `go`/`launch`/`post`; повтор без `F44C_REPEAT_OK`; линтер `--series`; первая исполняемая строка — линтер; литералы sha и пути копий, sha копий на диске, копия F44a = выходу сборки F44a; литерала FS12 в `go` нет; сторож после замка до манифеста; установка после копии кэшей; возврат FS13 до `installed_after`; своя задача `HPP-793` у `queue`/`runchk`/`chk`; `tempo_f44c.py` = FS12c; `ROOT` и `CLOSE_WAIT_S`; ASCII скриптов; вывод в строгий cp1250).
  - `refs_f44c.out.txt` (sha256 `46e5994abd6813454334b62522f5e9ad35ce997b1755cf88572d2e532dea1903`) — 12 ссылок, `ALL OK`.
  - **Линтер формы п. 634 / 661** — `C:/kyty/KytyPS5/ps5 em/docs/form634_check.py` (sha256 — `SHA256SUMS_seal.txt`); он же — первая
    исполняемая строка `launch_f44c.sh` и `go_f44c.sh`:

```
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f44c
ALL OK
$ python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --text C:/kyty/f287/f44c/pred/f44c_seal.md
ALL OK
```

## 8. Варианты исполнителя (рядом с буквой; вопрос лиду — в отчёте звена)

1. «Число строк `FixF29: overflow` и `Accessed non-GPU cached memory` — строкой отчёта» — счёт по логу (буква) **и** по всему stdout
   (строки пишутся `LOGF` в лог; stdout — на случай вывода в обход лога); печатаются оба счёта и первая строка каждого вида.
2. Члены формы `fs12_v` (FS12c: `FixF21: mode=1`, `FixB12: mode=1`, выход харнессом, `LogAsync`, `FixB13`, `FixB12Stat:`) — отдельной
   группой рядом с буквой п. 698(д)(4) («формы `fs12_v`»); чтение — лида.
3. «Лист лида» — `sheet_f29_v.png` и пара `pair_f29_v_fs12_v.png` (справа — `fs12_v` FS12c, тот же уровень и форма без ручки); смотрит лид.
4. «0 маркеров смерти» — по логу и всему stdout (форма FS12c).
5. Установленный — FS13 `abab2196` (общее правило звеньев задания: «после FS13d — бинарь, названный FS13d»; п. 703(д)), а не FS12
   `46892c20` из буквы п. 698(к).
6. Очередь внутри F (§5): по букве — после `done` F40c и F42c; если F42c (заблокирован цепочкой F42a2 → F42b2) не готов, а F40c кончился —
   вопрос лиду (прецедент п. 697(е) «по готовности»), тег не вызывается до ответа.

## 9. Отчёт тега

(заполняется после тега; печать выше не меняется)
