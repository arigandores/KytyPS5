# Сессия 133 — ревью кода переписи `rbcen` (шаг 4, `HPP-195`)

**Вердикт: PASS. BLOCKING — нет.** Замечаний к коду, требующих правки, — 0; замечание чтения — 1 (MINOR-1, владелец — лид /
Harness Engineer шага 6, в код не возвращается).

**Автор: Red Team.** 2026-09-29, 17:16–17:40 UTC по `date -u`. Вход: коммит кода `0f539e02` (16 файлов `src`, +745/−9; дифф —
`git show 0f539e02`, 1 394 строки), принятый проект `docs/session-133/design133.md` ред. 2 (`e9cc8e42`, `HPP-201`), константы
`ROADMAP.md` «СЕССИЯ 122» п. 141(в)(1)–(3), решения п. 142(б), п. 143(б)–(г), приёмка шага 3 п. 144 (`962186ce`), раздел `## Step 3`
`C:/kyty/s133/FACTS.md`. Объём — описание звена плюс расширение п. 143(г) (строка на каждый RC1–RC9) и строка MINOR-1 приёмки
`HPP-201` (порядок замков хука RC4) — внутри строки RC4. Игру не запускал, сборку не собирал, код не правил; проверка — чтение диффа
и дерева `962186ce` (в `src` совпадает с `0f539e02`). Метки: **[I]** — прочитано в коде.

## 1. Путь 0 побайтно

При `rbcen=0` исполняется только добавленное ниже; ни одно не меняет вызовов, аргументов, возвращаемых значений, веток, выделений,
записей в гостя или кэши [I]:

| место | что исполняется при 0 |
|---|---|
| `RbCen::Latch` (`renderDraw.cpp:5146`, `:5338`; `renderCompute.cpp:1002`) | `Gates::Value` (атомарная загрузка), `value == 0` ⇒ `LatchSlow` не зовётся (выделения нет, строк нет); запись `mode`/`b2`/`chain` в TLS; `SetLive(false)` — одна relaxed-загрузка (флаг и так false) |
| `ChainOpen`/`ChainMark`/`ChainFind`/`ChainSkip`/`ChainFlush`, пары `XBegin`/`XEnd` | проверка `rb.chain` / `t_rb.mode` — ложна |
| `RebindBuffers` (`descriptors.cpp:3909`, `:3939`, `:3974`, `:3982–3985`, `:4032`) | `rb_on = false`; все ветки переписи пропущены |
| `ObtainScope` в `ObtainBuffer` (`bufferCache.cpp:1342`) | чтение `t_rb.slot` (0) в конструкторе; `Class()`/`B2()`/деструктор — ветки по `m_outer = false` |
| `SynchronizeBuffer` (`bufferCache.cpp:1013`, `:1027`) | проверка `t_rb.slot` в лямбде загрузки, проверка `rb_up_t0` после `RecordBufferCopies` |
| `SetCls`, `B2Here` (`descriptors.cpp:213`, `:262`, `:285`, `:317`, `:353`) | проверка `t_rb.slot` — 0 |
| 37 хуков `Reset` | одна relaxed-загрузка `g_rb_b2_live` (false) |
| `BumpMapEpoch` (`memoryAddressSpace.inc:167–170`) | хук (одна загрузка), затем прежний `m_map_epoch.fetch_add(1, release)` в том же месте той же критической секции |

`src/graphics/shader/**` не тронут ⇒ подпись кэша трансляции прежняя. Тесты — по отчёту шага 3: `shader_cfg_tests` дельта 0,
`memory_tracker_tests` `all cases passed` (не перепроверял).

## 2. Отметки и счётчики как приняты (п. 141(в)(1)–(3), п. 142(б), §3, §6 ред. 2)

- **48 имён** в конце `enum class Counter` после `DcProtNs` и в конце `named` `videoOut.cpp` после `dc_prot_ns` — поимённо список §6
  ред. 2 (п. 142(в), 143(г)); порядок `rb_b2_rst_*` = порядок `RbCen::Cause` (`Sub, Host, Wait, Rel, Wr, Cond, Emu, Gpuw, Imgw, Ring`) —
  индексация `RbB2RstSub + cause` в `Reset` верна. `micros=false` у всех, кроме `rb_b2_kb` (`true`) — принято п. 144(в).
- **Цепочка draw §3.1:** L перед `HoldLap::Mark(HoldProgramsNs)` (`renderDraw.cpp:5146/5147`, `:5338/5339`) — цена защёлки в
  `mh_prog`; T0 = `t_hold_t0` (между `HoldProgramsNs` и M1 других `HoldLap::Mark`/`HoldPhase` нет — `frameStats.h:3021–3065`,
  `renderDraw.cpp:4178`, `:4185`); M1 после раннего выхода `:4067`; Pa/Pb только в ветке `!bind_floor`; M2 перед `if (!bind_floor)`;
  M3 после цикла `FindBuffers`; `ReadOwn(BdaPrepareHits)` вокруг `PrepareBda` внутри `rb_bda`; M4, M5, M6, M7 на местах §3.1; F
  сразу после метки `HoldBindingsNs` (T8 — её штамп, цена сброса — в `mh_emit`). Ранние выходы между M1 и F не книжат ни цепочку, ни
  `mh_bind`/`mh_draws` (`HoldLap::Count` после F) ⇒ `rb_find_n` = `mh_draws` по построению; незакрытая цепочка гасится следующей
  защёлкой (`rb.chain = false`).
- **Пары dispatch (В1):** вокруг `PrepareBindings`/`RebindImages`/`RebindBuffers` пути dispatch; `FindBuffers` вне пары.
- **Слоты `RebindBuffers` §3.3:** S0 — первый оператор тела; класс-счёт и решение Вейля `>>61` — внутри пары выбранной итерации;
  время, `rb_samp_n`, калибровка (каждая 64-я выбранная — `(++sel & 63) == 0`) — после `t1`; `RbCensus` — вне пары;
  `rb_bpro` — после `bind_lap_scope` до цикла (включая `ReadOwn` «до» и s₀); `rb_nupload` — от места перед `upload_scope` до конца
  функции (включая `ReadOwn` «после»). Классы — на всех выходах: `NativeStorageBuffer` — Null `:213`, Cbank `:285`, `:353`; прочие
  выходы идут через `ObtainBuffer`, у которого все пять `return` (`bufferCache.cpp:1411`, `:1439`, `:1517`, `:1556`, `:1584`) пишут
  класс (`:1449` — `return` лямбды); остальные выходы `NativeStorageBuffer` — `EXIT`. Класс None ⇒ `rb_cls_bad` (В7).
- **`rb_sync_up`** — в лямбде загрузки при `t_rb.slot ≠ 0` (внутри внешнего `ObtainBuffer` слот = 2 — пара открывается, как §3.4) →
  после `RecordBufferCopies`. **`rb_sync_wait`** — разность своих шардов через цикл слотов.
- **Значение 2:** заметки только у внешнего вызова латченного слота при `b2` (`bufferCache.cpp:1531`, `descriptors.cpp:262`, `:317`
  с `!gpu`); ключ записи и байты сверки совпадают с байтами копии пути: `(vaddr, size)` потоковой и `(address, size)` обеих const-bank
  — те же аргументы `TryReadBacking` пути (`bufferCache.cpp:1535`, `descriptors.cpp:267`, `:323`). Тень только при `size ≤ 64 КиБ`
  (буфер сверки — 64 КиБ; тот же ключ ⇒ тот же размер, переполнения буфера нет); тень непрерывна (`pos % S + size ≤ S`); проверка
  жизни тени `pos_now − pos > S` ⇔ хотя бы один байт тени переписан — верна и при пропуске хвоста круга.

## 3. Каждый источник сброса подключён (§5.2 ред. 2)

37 мест, сверено по дереву: 22 обработчика `pm4Handlers.cpp` (первой строкой тела: `CpOpAcquireMem` Rel, `CpOpGetLodStats` Wr,
`CpOpDispatchReset` Cond, `CpOpPfpSyncMe` Wait, `CpOpRewind` Wait, `CpOpSetPredication` Cond, `CpOpCondExec` Cond, `CpOpBranch` Cond —
только 14-словная условная форма, `payload_dw != 13` ⇒ `EXIT`, 4-словный вызов идёт мимо, `CpOpCopyData` Wr, `CpOpDmaData` Wr,
`CpOpDumpConstRam` Wr, `CpOpEventWrite`/`Eop`/`Eos` Rel, `CpOpIncrementCe/DeCounter` Wait, `CpOpReleaseMem` Rel, `CpOpWaitFlipDone`
Wait, `CpOpWaitRegMemSized` Wait — общий для 32/64, `CpOpWaitOnCeCounter`/`OnDeCounterDiff` Wait, `CpOpWriteData` Wr); `graphicsRun.cpp`
`:992` Sub и три `Flip*` Wr; `commandScheduler.cpp:782` Host; `kernel/memory.cpp:926` Emu (`TryWriteBacking`); `BumpMapEpoch` Emu
(шесть вызовов); `bufferCache.cpp:2558` Gpuw (`NoteGpuWrite`); `image.h:168` Imgw (только ветка «чистый → грязный»);
`streamBuffer.cpp:304` Ring (только `Usage() == Stream`). Обработчики без хука (`Draw*`, `Dispatch*`, `ClearState`, `ContextState`,
`Set*Reg`, `Index*`, `SetBase`, `IndirectBuffer`/`Indirect*Regs`, `Marker`/`Push`/`Pop`, `Nop`, `NumInstances`, `WriteConstRam`, `Flip` —
зовёт хукнутые `CommandProcessor::Flip*`) — ровно класс §5.3 или не пишут память гостя; нового пути не найдено.

## 4. Порядок ручек и отказ

`RebindCensus` — последний элемент `enum class Knob` перед `Count`, `{"KYTY_REBIND_CENSUS", "rbcen", 0, 2}` — последняя строка
`KNOB_DEFINITIONS`; комментарий «LAST row» перенесён с `dispceil` на `rbcen` в обоих файлах. `check_gate_order.py` — `GATE ORDER: clean`,
Knob 46 = 46 (отчёт шага 3, сверено лидом п. 144; не перезапускал). Харнесс: `C:/kyty/s133/gates_base.txt:11` — `rbcen=0`, одна строка.
Отказ (`LatchSlow`, `frameStats.cpp`): `notrace` → строка раз, `rb_refuse` (без трейса — no-op, В13), режим 0; `mutsite` → то же,
полный (п. 144(а)); `b2alloc` — при первой защёлке ЛЮБОГО значения ≥ 1, значение 2 работает как 1 (`b2 = mode == 2 ∧ chk`); строки
`RbCen: mode N` — раз на значение; однократность — `fetch_or` по битам причин.

## 5. Закрытие RC1–RC9 (п. 143(г); строка на каждый RC)

| RC | ред. 2 (`e9cc8e42`) | код (`0f539e02`) | закрыт |
|---|---|---|---|
| RC1 — поколение до чтения байт копией, в записи; повтор ⇔ `entry.gen` = `gen1` копии B | §5.1 «Интервал», «Заметка», `Census`; §15 п. 4 | `Gen0()` (acquire) до `Map`/`TryReadBacking`: `bufferCache.cpp:1532` (до `:1534`/`:1535`), `descriptors.cpp:263` (до `:265`/`:267`), `:318` (до `:320`/`:323`); `NoteCopy(..., rb_gen0)`; `RbCensus`: `gen1` — загрузка после копии, повтор ⇔ `entry.gen == gen1`, вставка `entry.gen = note.gen0`, вытеснение — по `gen1` | **да** |
| RC2 — снятие защёлки dispatch — только TLS; `g_rb_b2_live` пишет только защёлка при смене; защёлка draw не снимается | §2.2 | `Unlatch()` — `mode`, `b2`, `slot` (`frameStats.h`, вызов `renderCompute.cpp:1053`); `g_rb_b2_live` пишет только `SetLive` (из `Latch`), при `load != live`; в `renderDraw.cpp` снятия нет | **да** |
| RC3 — false → true сдвигает `g_rb_gen` без счётчика причины | §2.2, §5.1, §7, §8 | `SetLive`: `fetch_add(1, release)` ДО `store(true, release)`, без `Add` | **да** |
| RC4 — смена отображения = сброс на каждом сдвиге `m_map_epoch`; `memory.cpp:2092` снято | §0 п. 5, §5.2, §11, §15 п. 5 | `BumpMapEpoch()` (`memoryAddressSpace.inc:167–170`: `Reset(Emu)`, затем `fetch_add(1, release)`); вызовы `:327`, `:339`, `:433`, `:453`, `:502`, `:522` — единственные места записи эпохи в `src` (поиск `m_map_epoch`: объявление `:724`, чтение `MapEpoch()` `:164`, сдвиг только в `:169`); каждый вызов внутри `std::lock_guard lock(m_mutex)` (`:325`, `:337`, `:422`, `:451`, `:500`, `:511`); `memory.cpp:2093` (`ZeroBacking`) без хука | **да** |
| — MINOR-1 приёмки `HPP-201`: порядок `m_mutex` → `registry.mutex` — лист; `g_rb_gen` до `fetch_add` эпохи | — | держатели `registry.mutex` (`frameStats.cpp:68` `~ShardOwner`, `:185` `AttachShard` — `new Shard` ДО замка, `:218` `Read`) под ним только `push_back`/`fetch_add`/загрузки, других замков не берут ⇒ `m_mutex` → `registry.mutex` — лист, обратного порядка нет; `Reset` берёт `registry.mutex` лишь при первом `FS::Add` потока (под `m_mutex` — одно `new Shard` раз на поток). Порядок памяти: `g_rb_gen.fetch_add` упорядочен-до release-сдвига эпохи ⇒ читатель, увидевший новую эпоху acquire-загрузкой (`MapEpoch()`) или замком `m_mutex`, видит и новый `g_rb_gen`. Новые пары замков — только `g_alloc_mutex` (лист, под render mutex, раз) | **да** |
| RC5 — гонка копия ↔ тень/сверка двусторонняя, знак неизвестен | §5.1 «Окно гонки», §9.2, §11, §13 | кода не требует (текст и чтение) | **да** (текст) |
| RC6 — побочные эффекты `TryReadBacking`; `BackingPage*` между плечами не сравнивать | §5.1, §9.2, §13 | кода не требует; тень и сверка — только `TryReadBacking` гостя, слот кольца не читается (`descriptors.cpp` `RbCompare`, вставка тени) | **да** (текст; условие — чтение `bc133.py`) |
| RC7 — `lite` — условие проекта; дым проверяет режим | §2.3, §4, §10, §12 | инструмент режим не проверяет — как проект; проверка — `smk133.py` T1/T2 (шаг 5б, FACTS `## Step 5б`) | **да** (кода не требует) |
| RC8 — выделение и касание при первой защёлке ЛЮБОГО значения ≥ 1; `b2alloc` в обоих плечах | §2.1, §2.3, §10 | `LatchSlow` → `Allocate()` при любом `value ≥ 1` после отказов; таблица и кольцо — `new (nothrow)` + `memset` под `g_alloc_mutex`, публикация `g_alloc_state` release; буфер сверки — на поток, `memset`; строка `b2alloc` — при первой защёлке ≥ 1 | **да** |
| RC9(а) — вложенного `ObtainBuffer` нет; защита `slot = 2` от будущих путей; в `ObtainBufferForImage` ничего | §3.3 | `ObtainScope` (`bufferCache.cpp:1342`): внешний ставит 2 и пишет класс, вложенный молчит; в `ObtainBufferForImage` — ни одного `RbCen` (поиск) | **да** |
| RC9(б) — сведение решений п. 142(б) и п. 143 | §0, §1, §3.3, §4, §5, §6, §7, §8, §14 | `rb_cbank_n` на каждой итерации Cbank (`SlotEnd`), `rb_b2_n` на каждой пробе (тот же цикл, что `rb_b2_would`), `rb_b2_xchk`/`xdiff` (В5), `rb_b2_evict`/`shovf` (В6), `rb_cls_bad` (В7) | **да** |

## 6. Чек-лист кода Red Team

- Вызовы, вынесенные из хронометрируемой строки, вне её: `RbCensus`, `Add` времени, калибровка — после `t1`; Вейль и класс-счёт —
  внутри пары НАМЕРЕННО (§3.3); сброс цепочки F — после метки `mh_bind`. Да.
- Гонки: `g_rb_b2_live` — атомик, пишет только защёлка; `g_rb_gen` — атомик; таблица, кольцо теней и `g_rb_shadow_pos` — только поток
  командного процессора (`m4baton` = 0 в `bc133`); публикация указателей таблицы — release/acquire `g_alloc_state`. Рваного чтения нет.
- `*_bad` недостижим на корректном пути: все выходы итерации несут класс (§2); третья заметка невозможна (одна копия B2 на выход,
  выровненная const-bank после потоковой невозможна — `adjustment` = 0, §3.3 проекта). Да.
- Ранние выходы: `DispatchDirect` — между `Latch` (`:1002`) и `Unlatch` (`:1053`) `return` нет; draw — см. §2.
- Правки с обратными слэшами / CRLF / якоря: скрипт `step3/patch133.py` (по отчёту — якоря целыми строками, LF); в диффе разорванных
  литералов нет (`LOGF(... "\n")` целые).
- Кадр стека на потоке гостя: новых больших локальных нет (`Note[2]` — в TLS, буфер сверки — в куче).

## 7. Замечание (не BLOCKING, в код не возвращается)

**MINOR-1 (чтение; владелец — лид, при регистрации чтения `pred/01_bc133.md` шага 6).** Счётчики `rb_b2_rst_*` считают **события
хука**, а не границы интервалов между пробами: сброс, за которым до следующего сброса нет ни одной копии B2, тоже считается.
Сценарий [I]: невыполненный `WAIT_REG_MEM` (`graphicsRun.cpp:551–555`, `!pass` ⇒ `SuspendPm4()`) приостанавливает отправку; если
пакет разбирается снова на следующем слайсе (повтор разбора после `SuspendPm4` не проверял — [I]) — каждый повтор даёт `rb_b2_rst_wait` + 1 и `rb_b2_rst_sub` + 1 (повторный слайс — сброс по §5.2); так же
`UnmapOne` без найденного отображения (`memoryAddressSpace.inc:433`, `old.size == 0`) даёт `rb_b2_rst_emu`. Знаменатель правила
п. 143(а) «доля `rb_b2_rst_imgw` среди всех сбросов плеча 2 ≥ 0,10» раздувается холостыми событиями ⇒ доля сбросов образа
занижается ⇒ защитное правило может не сработать, и вывод «B2 не проходит: доля повтора < 0,5» будет сделан при доле повтора —
нижней границе. Код исполняет проект (§1 ред. 2 определяет долю по событиям), новых имён ввести нельзя (п. 143(г)) — исправление
только текстом чтения: печать `bc133` называет долю «долей событий, не интервалов» и рядом печатает `rb_b2_rst_wait` + `rb_b2_rst_sub`
на кадр; вывод «не проходит» при доле `imgw` в [0,05; 0,10) — вопрос закрытия, а не вывод (решение — у лида).

## 8. Что ревью НЕ доказывает

Что код компилируется без предупреждений и что тесты зелёные (принято из отчёта шага 3, не перепроверено); что сборка
`cf414f46` соответствует `0f539e02` (sha сверен лидом, п. 144); что перепись живёт в игре, тождества R1/R2 проходят ±5 %, счётчики
ненулевые и `rb_cls_bad` = 0 — это дымы шага 5 (`HPP-196`); что список сбросов полон для путей вне `9bb1e2ef`/`0f539e02` (п. 143(д));
цену инструмента [I]; что B2 корректен или снимаем. Ни одно число — не выигрыш и не потолок; 60 FPS не обещаются.
