# F25m (`HPP-680`, Harness Engineer): стенд, холодная серия и «нет вреда» `KYTY_FIX_B36` на бинаре T2 — печать до первого тега

Трек F, итерация кода 1 `KYTY_FIX_B36` (Ф27; кадры в счёте холодного слоя Б36, Б40), звено F25m по п. 613(г)(3)–(5), (е), (з)(2) с
п. 615(б)(1), (2), (6), п. 616(б)(1), (2), (4), (г), п. 618(б)(5), (в), п. 619(б)(1), (г). Этот файл — печать: после её записи ридер
`f25m_read.py`, его основа `f25_read.py` (копия F25f, sha256 закреплён), цепочка тега и правила чтения не меняются; её sha256 пишется в
json каждого тега (`prereg`), ридер сверяет её в допуске. **Вердикта нет:** чтение — F25n (`HPP-681`, лид). Метки: [c] — код/лог
прочитан или пересчитан, [I] — вывод, [U] — неизвестно. Время — UTC.

theta_load: 0.4562

## 0. Вход (правило 24(1): ссылка, якорь, контроль +1; проверка — `refs_f25m.py`, отрицательный контроль `--neg`)

- Решение звена — п. 613 `bac79f88:docs/ROADMAP.md:23723` (якорь «613. **Звено F25j трека F (`HPP-677`, лид)»; +1 — «(а) **Приёмка
  строкой. F25h ✓**»); поправки — п. 615 `bac79f88:docs/ROADMAP.md:23734` (якорь «615. **Звено F25k трека F (`HPP-678`, Emu Engineer»;
  +1 — «(а) **Приёмка строкой. F25k ✓.**»), п. 616 `bac79f88:docs/ROADMAP.md:23746` (якорь «616. **Звено F25l трека F (`HPP-679`, Red
  Team»; +1 — «(а) **Приёмка строкой. F25l ✓.**»), п. 618 `bac79f88:docs/ROADMAP.md:23759` (якорь «618. **Звено F25k2 трека F
  (`HPP-682`, Emu Engineer»; +1 — «(а) **Приёмка строкой. F25k2 ✓.**»), п. 619 `bac79f88:docs/ROADMAP.md:23771` (якорь «619. **Звено
  F25l2 трека F (`HPP-683`, Red Team»; +1 — «(а) **Приёмка строкой. F25l2 ✓.**»).
- Строки, которые читает ридер (код T2, HEAD worktree `0c8fcba2`):
  `TestLogStall: i=… line="…"` — `0c8fcba2:src/common/logging/log.cpp:261` (якорь «fmt::format("TestLogStall: i={} sleep_ms={} slept_us={}
  t0_ms={} t1_ms={} on={} tid={} role={} line=\"{}\"\n",»; +1 — «i + 1, g_stand.sleep_ms, (t1 - t0) / 1000u, t0 / 1000000u, t1 / 1000000u,»);
  `LogAsync: stall` — `0c8fcba2:src/common/logging/log.cpp:281` (якорь «const auto text = fmt::format("LogAsync: stall us={} queued_bytes={}
  t_ms={}\n", ns / 1000u, left,»; +1 — «NowNs() / 1000000u);»); итоговая `LogAsync: full_waits=` — `0c8fcba2:src/common/logging/log.cpp:494`
  (якорь «text = fmt::format("LogAsync: full_waits={} full_wait_us={} stalls={} stall_cut={} lines={} bytes={} "»; +1 —
  «"max_queued_bytes={} sync_lines={} drain_timeouts={}\n",»); `LongFrame:` (печатает поток `LongFramePrinter`, опрос 250 мс) —
  `0c8fcba2:src/common/logging/log.cpp:556` (якорь «Write(fmt::format("LongFrame: n={} dt_us={} log_async={} t_ms={}\n", r.n, r.dt_us,
  r.log_async, r.t_ms));»; +1 — «}»); `LogAsync: mode=1` — `0c8fcba2:src/common/logging/log.cpp:739` (якорь «Write(fmt::format("LogAsync:
  mode=1 limit_bytes={} drain_ms={} stall_ms={} flush_ms={}\n",»; +1 — «Async::kDefaultLimitBytes, Async::kDrainNs / 1000000u,
  Async::kStallNs / 1000000u,»); `TestLogStall: config` — `0c8fcba2:src/common/logging/log.cpp:746` (якорь «Write(fmt::format("TestLogStall:
  config at_ms={} sleep_ms={} k={} gap_ms={} on={}\n",»; +1 — «Async::g_stand.at_ns / 1000000u, Async::g_stand.sleep_ms,
  Async::g_stand.k,»); запись меры кадра (номер `n` = `flip_status.count`, тот же счётчик, что `FrameTrace` n и окно `DiagB32` n) —
  `0c8fcba2:src/graphics/presentation/videoOut.cpp:1360` (якорь «Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns -
  long_frame_prev_ns) / 1000u, now_ns / 1000000u);»; +1 — «}»); предел строк `FlipHold:` 32 на прогон —
  `0c8fcba2:src/graphics/presentation/videoOut.cpp:3614` (якорь «if (hold_logged.fetch_add(1, std::memory_order_relaxed) < 32) {»; +1 —
  «const uint64_t named = present_ns + poll_ns;»), строка `FlipHold:` с `poll_us` и `flip=` — `0c8fcba2:src/graphics/presentation/videoOut.cpp:3616`
  (якорь «LOGF("FlipHold: us=%llu present_us=%llu poll_us=%llu other_us=%llu flip=%llu\n",»; +1 — «static_cast<unsigned long long>(hold_ns /
  1000), static_cast<unsigned long long>(present_ns / 1000),»).
- Часы: `t_ms` строк `LongFrame`, `LogAsync: stall`, `t0_ms`/`t1_ms` строки `TestLogStall` и `flip_ns` заголовка `DiagB32` — одна шкала
  `Common::FrameStats::NowNs` [c кода T2; п. 615(б)(1)].
- **Бинарь тегов — T2:** sha256 `9745eb7851d541740ce9730b86258f7bb26cab270f0d35434d43037c5cefd885`, копия
  `C:/kyty/f287/f25k2/kyty_emulator_9745eb78.exe`, строка версии `KytyPS5-2026-09-15-6a2987a-1910-g0c8fcba2`, подпись трансляции
  `9177b4267de1fb8bac7d1113afd8733210addfac`, каталог `variant_fixb26_fixb1b_fixf10_fixf19` (п. 618(в), 619(в)); бинарь T `45fff4a3` в
  серию не идёт (п. 616(в)) — член допуска «json `binary_sha256` = T2» и «установлен на тег T2». **Установленный — FS9**:
  `3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5`, закреплённая копия `C:/kyty/f287/bin/kyty_emulator_3861eeea.exe`; до =
  после по полному sha256 у каждого тега (член допуска); в конце серии — sha FS9 и манифест кэшей = A′ (`restoreA`, п. 613(г)(5)).
- Снимки кэшей — A и B серии F25f (`C:/kyty/f287/f25f/snap`, скопированы в `C:/kyty/f287/f25m/snap` 2026-10-07 до первого тега; копии =
  манифестам `A.tsv` 4 790 файлов, `B.tsv` 4 808 файлов — EQUAL [c]); живые кэши перед серией = A (манифест EQUAL, `listsha`
  `7718ec40…` [c]); состав — пять каталогов харнесса F20l3/F25f (`_ShaderCache` с `replay/`, `_ShaderSeeds`, `_PipelineCache`,
  `_SaveData`, GLCache драйвера). A — холодный (снимок до прогревов F25f), B — тёплый (после `f25_c1` pot и `f25_c2` bonus; Sky Garden тёпл
  и в A, и в B — прогрев FS8e). Подпись трансляции T2 = бинаря B F25f ⇒ снимки годны [c п. 618(а)].

## 1. Теги и форма (цепочка `go_f25m.sh`; переменные — позиционно в `enter_scene.py`, `KYTY_*`/`VK_LAYER_*` шелла сняты)

| тег | уровень | форма | ручки | кэши | удержание |
|---|---|---|---|---|---|
| `b36_s0` | `pot_treasure_cave` | пользователя (`--user-form`) | `KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3 KYTY_FIX_B36=0` | B (возврат B, если `snap/STATE` ≠ B), копия до, возврат после | 150 с |
| `b36_s1` | pot | пользователя | то же, `KYTY_FIX_B36=1` | B | 150 с |
| `b36_f0` | pot | харнесса | `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 KYTY_DIAG_B32=1 KYTY_LONGFRAME=1 KYTY_TEST_LOGSTALL=60:3000:3 KYTY_FIX_B36=0`, видео | B | 150 с |
| `b36_f1` | pot | харнесса | то же, `KYTY_FIX_B36=1` | B | 150 с |
| `b36_k01` … `b36_k13` | pot: k01 k03 k05 k07 k09 k11 k12 k13 (8); bonus: k02 k04 k06 k08 k10 (5) | `f25_k` | `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 KYTY_DIAG_B32=1 KYTY_FIX_B36=1`, видео | возврат A перед КАЖДЫМ тегом, копия до, возврат после (= A) | 330 с |
| `b36_v` | `underwater_aerial_garden` | V `fs9_v` (FS9c) | `KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_FIX_B36=1`, видео, `--stable-draws 300 --timeout 480` | B | 330 с |
| `b36_w` | Sky Garden | W п. 295(б) (`fs9_w`) | `VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_FIX_B36=1`, `--vulkan-validation true`, precache по умолчанию, без `VK_LAYER_MESSAGE_ID_FILTER`, `--stable-draws 100 --timeout 900` | B | 310 с |
| `restoreA` | — | не тег | — | возврат A, манифест = A′, FS9 | — |

Форма харнесса (`b36_f*`, `b36_k*`, `b36_v`, `b36_w`) несёт ещё константы `enter_scene.py`: `KYTY_FRAME_TRACE=lite`, `KYTY_GATE_FILE`
(файл ворот `gates_default.txt` — пуст), `KYTY_SAMPLE_GATE`, `KYTY_QUEUE_TRACE=1`, `KYTY_GUEST_ARGS=-lvl <уровень>`, `KYTY_REC` (кроме W);
`KYTY_GPU_HANG_ABORT_S` — 22 у `b36_f*`/`b36_k*` (п. 599(б)(2), форма `f25_k`), 8 у V/W (как `fs9_v`/`fs9_w`). Общие аргументы эмулятора —
окно 1280×720, `--vulkan-validation false` (кроме W), `--shader-validation false`, без `--rd`; `--attempts 1`, `--require-idle`,
`--no-install`.

**Форма пользователя (`b36_s0`/`b36_s1`, п. 613(г)(3)) — решение исполнителя, названо:** json `env` = ровно `KYTY_GUEST_ARGS=-lvl
pot_treasure_cave` (вход им нужен), `KYTY_LONGFRAME=1`, `KYTY_TEST_LOGSTALL=60:3000:3`, `KYTY_FIX_B36=0|1`; **нет** `KYTY_FRAME_TRACE`,
`KYTY_DIAG_B32`, файла ворот и `KYTY_SAMPLE_GATE` (вход им не нужен: файл ворот пуст), `KYTY_QUEUE_TRACE`, `KYTY_GPU_HANG_ABORT_S`,
`KYTY_GPU_CLOCK_PIN`, `KYTY_GPU_MARKERS`, `KYTY_GPU_WALL`, видео (`KYTY_REC` — запись файла в тот же каталог, источник задержек [U] по
п. 613(з)(3)). Вход («ok») — строка `GuestOut: Level has started: pot_treasure_cave` после `LevelDocument Loaded: pot_treasure_cave`
(строк `FrameTrace` нет). **`KYTY_LONGFRAME=1` у `b36_f0`/`b36_f1` — вариант исполнителя:** буква п. 613(г)(3) формы харнесса его не
называет; он нужен, чтобы дать кадру `FrameTrace` n время конца `t_ms` на шкале сна (запасной путь — `flip_ns` окна `DiagB32` n), и
даёт сверку `dt_us` двух мер; запись меры — вне пути кадра (п. 616(б)(2)).

Сон стенда — с 60-й секунды после `Log::Initialize`, 3 раза по 3 000 мс через ≥ 5 с: ≈ 60–63, 68–71, 76–79 с процесса; тёплый вход pot
в F25f — 12,9–14,4 с до «stable» [c json F25f] ⇒ сны на ≈ 46–65 с сцены, удержание 150 с кончается на ≈ 164 с процесса — ≥ 80 с после
последнего сна.

## 2. Порядок, блоки, замок

Порядок тегов (решение исполнителя): `b36_s0`, `b36_s1`, `b36_f0`, `b36_f1`, `b36_v`, `b36_w` (тёплые, снимок B — один возврат), затем
`b36_k01` … `b36_k13` по номерам (холодные; уровни чередуются, последние три — pot), затем `restoreA`. Каждый тег — один замок
`C:/kyty/SEALED_RUN.lock` через `procload.py` (маска `<app>`), строка `lock taken|released <тег> <UTC>` в `runs/lock.log`; блоки п. 534(3)
— две чистые проверки ≥ 600 с, не больше 6 тегов в блоке; перед каждым вызовом — `chk_f25m.sh` (файл `STOP`, замок, новые комментарии
`HPP-680`, очередь замка P > F > S) строкой `times.txt`; запуск — `launch_f25m.sh` (только запуск), ожидание — `wait_f25m.sh` ≤ 540 с,
разными командами; чтение — `post_f25m.sh` вне замка. Посторонний процесс пользователя / сессия ВМ во время тега — убийство своего
эмулятора по pid, тег — помеха (каталог `runs/<тег>.user_*`).

## 3. Правило чтения (ридер `f25m_read.py`; вердикта нет)

**Допуск тега (член не выполнен — `INTERFERENCE`, тег не в счёте):** json есть; θ из печати; json `binary_sha256` = T2; установлен на тег
= T2 (`installed_sha.txt`); установленный до = после = FS9; `prereg` = sha256 печати; `env` = форма тега §1 ровно (лишний, недостающий
ключ или другое значение; значения путей `KYTY_GATE_FILE`, `KYTY_SAMPLE_GATE`, `KYTY_REC` — любые); последний `--vulkan-validation` —
`true` только у W; `--shader-validation false`; без `--rd`; `-lvl` уровня тега = файл уровня харнесса; опция удержания §1; лог есть; исход
входа `ok`; строк `Window … minimized` и `Recovering Vulkan swapchain` 0; подпись `9177b426` и каталог варианта; строк `GamePatch:` 0;
кэши до = снимок формы; кэши возвращены (`manifest cmp EQUAL`). **LogAsync (п. 615(б)(2), (6)):** при `KYTY_FIX_B36=1` — ровно одна
строка `LogAsync: mode=1` (нет — помеха тега) и одна итоговая `LogAsync: full_waits=` со всеми полями (нет — **помеха прогона**: тег снят
убийством, повтор — только пунктом лида, счёт `LongFrame` / `LogAsync: stall` на нём не читается); при `=0` — ни одной строки `LogAsync:`.
**Стенды:** одна строка `TestLogStall: config` с `sleep_ms=3000 k=3 on=caller` (`=0`) / `on=writer` (`=1`); ровно три сна `i=1,2,3` того же
`on=`, `slept_us` ≥ 2 900 000. Не-стенды — ни одной строки `TestLogStall`. `b36_s*`: удержание ≥ 120 с и процесс жив (`hold_exit` null),
0 строк `FrameTrace`/`DiagB32`, 0 маркеров смерти в логе и stdout. `b36_f*`: сцена вошла, сцена ≥ 120 с, 0 маркеров смерти, одна строка
`DiagB32: mode`. `b36_k*`: допуск F25f (сцена ≥ 300 с или `GpuHangAbort` после ≥ 10 с — в счёт как `NO_SAMPLES:abort`; иных маркеров
смерти нет; `--- Error ---` допустима только после `GpuHangAbort:`; одна строка `DiagB32: mode`, `rep_drop` 0).

**Окно сна (п. 615(б)(1)):** строка `LongFrame` или кадр сопоставляется сну, если его `t_ms` конца ∈ [`t0_ms` − 2 000; `t1_ms` + 2 000]
(края включены). Кадр `FrameTrace` n получает `t_ms` из строки `LongFrame` n, иначе — `flip_ns` окна `DiagB32` n / 10⁶.
**Окно у выхода (п. 616(б)(2), 618(б)(5)):** записи `LongFrame` последних ≤ 250 мс перед выходом могут не дойти; член чтения стенда —
оценка выхода (`at_ms` − 60 000 + 1 000 × (`stable_s` + `hold_s`)) не раньше чем через 250 мс после `t1_ms` + 2 000 последнего сна;
иначе стенд не читается (FAIL члена).
**Поле `line=` (п. 616(б)(1)):** у каждого сна печатаются `on`, `tid`, `role` и `line="…"` (первые ≤ 40 байт строки, взявшей сон;
нет поля — `<absent>`) — кто взял сон.

| тег | члены стенда (буква п. 613(г)(3)) | справка / вариант исполнителя |
|---|---|---|
| `b36_s0` | у **каждого** из 3 снов ≥ 1 строка `LongFrame` с `dt_us` ≥ 2 500 000 в окне сна; окно у выхода | число снов с попаданием; иначе по п. 613(г)(3) — «на пути по умолчанию не показан» (чтение F25n) |
| `b36_s1` | 0 строк `LongFrame` с `dt_us` ≥ 1 000 000 во **всём** логе; ≥ 3 строк `LogAsync: stall` с `us` ≥ 2 900 000; `full_waits` = 0 (поле итоговой строки); окно у выхода | вариант: строки `LongFrame` ≥ 1 с только после строки входа |
| `b36_f0` | ≥ 1 кадр сцены (`FrameTrace`) с `dt_us` ≥ 2 500 000 в окне сна; окно у выхода | число снов с таким кадром; вариант — «у каждого сна» |
| `b36_f1` | 0 кадров сцены с `dt_us` ≥ 1 000 000 (все кадры сцены от первого, и до 10 с); окно у выхода | вариант: 0 строк `LongFrame` ≥ 1 с во всём логе; сверка `dt_us` `LongFrame` / `FrameTrace` по n |

**Холодная серия (п. 613(г)(4)):** K — удержания с кадром в счёте по правилу п. 596(д), 599 ридером F25f (`f25_read.py`, без изменений;
кадр удержания — `dt_us` ≥ 100 000 с началом ≥ 10 с сцены; кадр K2 — `dt_us` ≥ 1 000 000, не Б5/Б33/Б1б, не `INSTR_MADE_K2`).
**`INSTR_POLL` (п. 613(з)(2)):** кадр K2 (не Б5/Б33/Б1б, не `INSTR_MADE_K2`), в интервале которого (строки между `FrameTrace` n − 1 и n —
отображение `FlipHold` F25f) есть строка `FlipHold:` с `poll_us` ≥ 100 000 (наибольший `poll_us` интервала) — класс `INSTR_POLL`, в счёт K
не идёт, в K_I идёт. **`POLL_UNKNOWN` (решение исполнителя):** `FlipHold:` печатается не больше 32 раз за прогон — кадр K2 с n > `flip`
32-й строки + 1 помечается `POLL_UNKNOWN` и по букве остаётся в счёте (чтение F25n). **S** — строки `LogAsync: stall` с `us` ≥ 1 000 000
(строки с `flush=1` входят; их доля печатается отдельно), по тегу и по серии. Справкой у каждого кадра в счёте: `poll_us`, `log_us` /
`log_gpu_us` строки `FrameTrace-draw` n, строки `LogAsync: stall`, чей отрезок [`t_ms` − `us`/1 000; `t_ms`] пересекает кадр [конец −
`dt`; конец] (конец — `flip_ns` окна n), цепочка ожиданий ридера F25f. Остановки по уровню нет — серия идёт целиком (pot 8, bonus 5).
**RC3 (п. 616(б)(4)):** тег с `drain_timeouts` ≥ 1 в итоговой строке — строка «порядок строк у конца лога не гарантирован; отрезки у смерти
не читаются», тег читается по остальным членам. **`LongFramePrinter` (п. 619(б)(1)):** у тегов с `KYTY_LONGFRAME=1` время записи (и
ожидание сна стенда) потока `LongFramePrinter` входит в его `log_us` / `LogNs` с ролью `other`; к держателю кадра оно не относится и в
сумму `log_us` по потокам чтения F25i RC4 не входит — ридер печатает `log_us` кадра только справкой.

**«Нет вреда» (п. 613(г)(5)):** `b36_v` — удержание ≥ 300 с после первого кадра сцены (первая строка `FrameTrace` после строки входа с
`draws` ≥ 100), процесс жив, 0 маркеров смерти (лог и stdout), 0 кадров ≥ 1 с после первого кадра сцены, индекс видео ≥ 3 000 записей,
0 одно-кадровых глитчей `s51_vidglitch.py`, лист для лида сделан; `b36_w` — процесс жив до конца удержания (`hold_s` ≥ 310), 0 маркеров
смерти, 0 `[Vulkan][E]`, 0 строк предела слоя, положительный контроль (`[Vulkan][W]` > 0 и `DualSrcBlend: supported=1 enabled=1` до первой
строки `GuestOut`), нет `VALIDATION_STOP`; у обоих — `FixB13: mode=1` до первой строки `GuestOut`.

**Помехи и повторы:** событие окна или посторонний процесс / сессия пользователя — повтор тега тем же именем с `_r1`…`_r3` по правилу
п. 273(з), не в счёт; помеха прогона п. 615(б)(6) (`=1` без итоговой строки) — повтор только пунктом лида; иная помеха — вопрос лиду.
Тег со строкой `minimized` / `Recovering Vulkan swapchain` не читается как исход. Таблица по тегам: `binary_sha256`, K, K_I, в счёте,
`INSTR_POLL`, S, кадры ≥ 1 с (сцена / `LongFrame`), `full_waits`, `drain_timeouts`, члены, глитчи.

## 4. Бюджет

19 тегов + `restoreA`, ≈ 3 ч замка с блоками [I] (п. 613(д)); помехи сверх 6 — стоп и вопрос лиду. Кадр ≥ 1 с у `b36_s1` или два
`FAIL` подряд — не стоп звена: чтение и итерация 2 — пунктом лида (п. 613(д)).

## 5. Аппарат и проверки (до первого тега)

- `test_f25m_read.py` — фикстуры на каждый член и край ридера (§3), строгий cp1250, страж sha `f25_read.py`; `sens_f25m.py` — ручные
  правки ридера (форма F25f `sens_f25.py`, принята п. 608), каждая обязана уронить набор; `regress_f25m.py` — ридер на логах F25f
  (холодные `f25_k01`…`f25_k05`, тёплые `f25_s15`, `f25_s01`, `f25_s14`) даёт K / K_I / в счёте F25f; `test_tools_f25m.py` — снимки,
  reconcile п. 606, M6, guard, hold, очередь, сухой прогон `go_f25m.sh` по каждому тегу, форма пользователя `enter_scene.py`;
  `refs_f25m.py` — ссылки §0 и отрицательный контроль.
- Не заявляется: п. 619(е), 618(е), 616(е), 615(г), 613(и), 611(з), 608(е), 596(л) целиком; что бинарь T2 работает в игре до первого
  тега; что стенд воспроизводит настоящую задержку файловой системы на машине пользователя; что `=1` не меняет поведение игры до (г)(5);
  ни одно число — не выигрыш; 60 FPS не обещаются.
