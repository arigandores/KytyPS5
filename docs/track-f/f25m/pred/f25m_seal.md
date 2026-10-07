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

## 6. Строки печати (sha256 файлов и последних выводов наборов)

- `test_f25m_read.out.txt` (sha256 e3eb43da7da82cce): checks 135; ALL OK; первая строка набора: `suite test_f25m_read.py sha256 c7af1e17151ff24798786b4bf7c7abbc36f4f958d252f8cad181998aeebedc84 target f25m_read.py sha256 5e3645e6046d2b9764f2244908fb1be790c33989e16e8787a6cdb2026e4ff9f8`
- `sens_f25m.out.txt` (sha256 8b6ec9af7eaff662): edits 74 caught 74 kept 0; ALL OK; первая строка набора: `suite sens_f25m.py sha256 4181a8c11e7add96641af60b270c2d87b692161585fafd5b2a158d5c4207b8a6 target f25m_read.py sha256 5e3645e6046d2b9764f2244908fb1be790c33989e16e8787a6cdb2026e4ff9f8 test_f25m_read.py`
- `regress_f25m.out.txt` (sha256 d2d813fa70830c48): REGRESS PASS; ALL OK; первая строка набора: `suite regress_f25m.py sha256 f755c2c3fc774561634d80bb9f8defd020a425bb0eebe932fdcecd34b3205e1c target f25m_read.py sha256 5e3645e6046d2b9764f2244908fb1be790c33989e16e8787a6cdb2026e4ff9f8`
- `refs_f25m.out.txt` (sha256 57f8c84e621a07fd): refs 14 bad 0; ALL OK; первая строка набора: `suite refs_f25m.py sha256 97092de11208b4609655b186df733f2b62418fbee08bbfd47c12ac6342c5e60d target 14 references (direct)`
- `refs_neg.out.txt` (sha256 f95c0dc7137ab542): NEG CONTROL OK; ALL OK; первая строка набора: `suite refs_f25m.py sha256 97092de11208b4609655b186df733f2b62418fbee08bbfd47c12ac6342c5e60d target 14 references (negative control)`
- `test_tools_f25m.out.txt` (sha256 15e0a6e2bd482fd6): checks 84; ALL OK; первая строка набора: `suite test_tools_f25m.py sha256 f7b2420f1380a7b895328e67a6df06b0b8bbb53d3f546dd2cdf4484cad6dd1be target snap_f25m.py sha256 1420272df66e2d1a8a06f47c085bd4db36e43ad92f70aae29c5902d0f02ece12 m6_f25m.py `

seal: 5e3645e6046d2b9764f2244908fb1be790c33989e16e8787a6cdb2026e4ff9f8 C:/kyty/f287/f25m/f25m_read.py
seal: 933f36c1f63bbb3159144e1a7ca7395dc000234d6dc3be27349e40b2ff902ddf C:/kyty/f287/f25m/f25_read.py
seal: 5a986c03d161b9a5c52d589ad1da87e4676ceb9bac61acaeaa8f2131525400fa C:/kyty/f287/f25m/f20e_read.py
seal: c7af1e17151ff24798786b4bf7c7abbc36f4f958d252f8cad181998aeebedc84 C:/kyty/f287/f25m/test_f25m_read.py
seal: 4181a8c11e7add96641af60b270c2d87b692161585fafd5b2a158d5c4207b8a6 C:/kyty/f287/f25m/sens_f25m.py
seal: f755c2c3fc774561634d80bb9f8defd020a425bb0eebe932fdcecd34b3205e1c C:/kyty/f287/f25m/regress_f25m.py
seal: 97092de11208b4609655b186df733f2b62418fbee08bbfd47c12ac6342c5e60d C:/kyty/f287/f25m/refs_f25m.py
seal: f7b2420f1380a7b895328e67a6df06b0b8bbb53d3f546dd2cdf4484cad6dd1be C:/kyty/f287/f25m/test_tools_f25m.py
seal: e770a96b0e552d9c9fbbdb82c5f6fbf6e51f48992478fc926b30c0c4517ab20f C:/kyty/f287/f25m/f25m_seal_body.md
seal: 1420272df66e2d1a8a06f47c085bd4db36e43ad92f70aae29c5902d0f02ece12 C:/kyty/f287/f25m/snap_f25m.py
seal: 69b3b16e3479422d6f2fed9cf4e4931c7c9d196df6f6049bf09b9af67639ee5c C:/kyty/f287/f25m/m6_f25m.py
seal: d97fa62809103d0aa33544a36000ac774ca360a6545d6a90a3c05a5008a3e28b C:/kyty/f287/f25m/go_f25m.sh
seal: 09f88cbda86f72d08242c6fafdcb4e6511622b917155247c6018034889d0c748 C:/kyty/f287/f25m/launch_f25m.sh
seal: a4ab390497ba83a1a7e482a170c6722010465d58bd2f47e3868a0c66bcc2d480 C:/kyty/f287/f25m/wait_f25m.sh
seal: 24bc6573f627bfc00b5506952d52e9f3e289acdbb17108ecca01eccfb0651691 C:/kyty/f287/f25m/post_f25m.sh
seal: 4eb5da04f740ae59678367cc24c1914b597bc05898db44d2647df68cc8186cea C:/kyty/f287/f25m/chk_f25m.sh
seal: 2bac5ba3f59936f624f17a4ca671ae70420e991c3b88c40323cd25271ea9169e C:/kyty/f287/f25m/block_f25m.sh
seal: e36db1b996a32b32e47cce6d1725d4f60093a96cc8ddce4279d361d901f51c25 C:/kyty/f287/f25m/guard_f25m.py
seal: fd7ef1a2dc1ffdca6b09eab733b470c1da960a32f08b51fedbf7d381ed4f0a00 C:/kyty/f287/f25m/hold_f25m.py
seal: 7f332b9649b3d32278caaac9411d7ef1100c9b65dbf5cdd9b6b9e5515b4a3aa7 C:/kyty/f287/f25m/queue_f25m.py
seal: 97ba8bf2e840b586ba60e34bb6498f3a1b23d63bb5e311ff4e7536a609c7daed C:/kyty/f287/f25m/runchk_f25m.py
seal: 7f134e4ea1dc42074c612e4f929b245aaa5f683643285ccc0f0f87995cc759b1 C:/kyty/f287/f25m/watch_f25m.py
seal: 4a94fefc911f3294134912874dda86860b9d97d553d7bec0f81be4554fe8a6f5 C:/kyty/f287/f25m/enter_scene.py
seal: d9e7a777404f1aa98eb8e221d2d9b1af0e393b292d91997fade08fae685ce5c0 C:/kyty/f287/f25m/procload.py
seal: a7096fd47f70419a5ed8d541778294f3032ca2c88e7b4b2e946f3d99651182bb C:/kyty/f287/f25m/manifest_fs4c.py
seal: c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d C:/kyty/f287/f25m/sheet142.py
seal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 C:/kyty/f287/f25m/gates_default.txt
seal: c5ee7dc26d2a6d28501c3941fe882448176165b63e4242373fb0a4a80c697a96 C:/kyty/f287/f25m/idle142.py
seal: 77e685e5543d90a0b9cc8c8e48827a42e4bf5263260af53da3a63b4d06529638 C:/kyty/f287/f25m/run_safety99.py
seal: c750e62ae3d6354970e5be70cf5fb19c480292b78beeeb8c9bb7112106d6aa21 C:/kyty/f287/f25m/launch_run.py
seal: 266b1c992908500e0fb8cf7121d0c2d1f707b02e87929182842b28fd64f48b74 C:/kyty/f287/f25m/mk_seal_f25m.py
seal: 7718ec40caaf963b62e87d7446f82f159b91ab77fc203512959a90495809c722 C:/kyty/f287/f25m/snap/A.tsv
seal: 6e1b3b848731f16a77178d21047f478a1d596c68d006f19b04fe87b32f0cfa2c C:/kyty/f287/f25m/snap/B.tsv
seal: b957162f5c692050e720ef8253c4026325cf4de093691ad48d112460dd99fec3 C:/kyty/f287/f25m/snap/A0.tsv
seal: 3b64fd13e3b743f75d3ce7ced6503e15ea114fff5c8c8f96c7105004e86091b8 C:/kyty/f287/f25m/snap/B0.tsv
seal: 8b20af50cef59156be20b001f1ca89792e77ced46782c508f6cf50b24798f361 C:/kyty/f287/f25m/snap/D.tsv
seal: e3eb43da7da82ccefe60ba974c6ae5cb9b241b488046756eb01bf2338be6e2dd C:/kyty/f287/f25m/test_f25m_read.out.txt
seal: 8b6ec9af7eaff662a09bd43b3cc4b18f63c464081d2520f2c98a273a1fa81d6b C:/kyty/f287/f25m/sens_f25m.out.txt
seal: d2d813fa70830c48822050fde1cb0241f241be62a0aebe8b95d0150c002111ee C:/kyty/f287/f25m/regress_f25m.out.txt
seal: 57f8c84e621a07fdb476f40f3b73f83e5c66983a35ff894ee0a53d817baa8835 C:/kyty/f287/f25m/refs_f25m.out.txt
seal: f95c0dc7137ab542efa95300cee29d62ef549e651b8dcd394a8b3d0b92be1260 C:/kyty/f287/f25m/refs_neg.out.txt
seal: 15e0a6e2bd482fd6f3f6c6b010998dc4ea5b61617440797ca5e9ca995c8faf35 C:/kyty/f287/f25m/test_tools_f25m.out.txt
seal: 9745eb7851d541740ce9730b86258f7bb26cab270f0d35434d43037c5cefd885 C:/kyty/f287/f25k2/kyty_emulator_9745eb78.exe
seal: 3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5 C:/kyty/f287/bin/kyty_emulator_3861eeea.exe
seal: 6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c C:/kyty/scripts/s51_vidglitch.py
