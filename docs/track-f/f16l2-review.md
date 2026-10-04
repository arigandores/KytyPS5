# Трек F, звено F16l2 (`HPP-591`, Red Team): ревью кода F16k2 `ed4f96d8`

**Вердикт: `PASS` — 0 требуемых изменений.** RC1–RC5 ревью F16l исполнены по букве п. 496(б)(1)–(5); тождество п. 496(б)(5) держится по коду;
члены п. 492(з) «Ревью F16l» и поправки п. 495(б) на `ed4f96d8` держатся; три члена сверх буквы (п. 500(в)) — ✓; бинарь `d4328b0c` собран из
`ed4f96d8`. Наблюдения Н1–Н5 (§3) — без требований к коду; два из них (Н1, Н2) — к печати F16m и чтению F16n.

Решение звена — `781ec04f:docs/ROADMAP.md:22795` п. 496 (якорь «496. **Звено F16l трека F (`HPP-584`, Red Team) ПРИНЯТО лидом»; +1 —
«(а) **Приёмка строкой. F16l ✓**»), члены сверх буквы — `b3ec1d4c:docs/ROADMAP.md:22823` п. 500 (якорь «500. **Звено F16k2 трека F (`HPP-590`,
Emu Engineer) ПРИНЯТО лидом»; +1 — «(а) **Приёмка по п. 496(б)(1)–(6). F16k2 ✓.**»), (в). Код — `ed4f96d8` (дифф к `810909e3` по `src`/`tests` —
9 файлов), отчёт — `11faf668:docs/track-f/f16k2.md`. Время — UTC по `date -u`, события — `C:/kyty/f287/times.txt` (строки `F16l2`). Игру не
запускал, код не правил, установленный бинарь (`adb0c82f…`), `C:/kyty/build` и кэши не трогал. Метки: [c] — по коду `ed4f96d8` или по выводу
команды; [I] — вывод без прямого измерения.

## 1. Члены — член за членом

| Член | Исход | Основание [c] |
|---|---|---|
| п. 496(б)(1) RC1 `wr_after=large` при пустом точном ответе и `m_large_write_seq` > `since` | ✓ | `ed4f96d8:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3887` (якорь «const bool large = exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;»; +1 — «e.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact»); номер — тот же счётчик `m_gpu_write_seq`, что у корзин: `ed4f96d8:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:2856` (якорь «if (size > (16u << 20)) {»; +1 — «m_large_write_seq = seq;»), сравнение с `since` осмысленно. Решение `PendingDccFillStale` не тронуто. Тест D18 `ed4f96d8:tests/ShaderRecompilerComputeTests.cpp:11124` (якорь «BTA::F16kNoteGpuWrite(buffers, base, 0x1000001); // 16 MB + 1 after the fill»; +1 — «const auto g2 = scan2(dx_large, 6001);»): до заливки — `none`, после — `large`; мутант m8 пойман |
| п. 496(б)(2) RC2 `cpu_mod` по эпохе записи CPU с заливки; без начальной эпохи — 1 | ✓ | штамп эпохи — в `StampPendingDccFill` под `m_lock` рядом с номером заливки; событие — `descriptors.cpp:3898` (якорь «e.cpu_mod = cpu_now \|\| !seen \|\| fill_epoch == 0 \|\| buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch»; +1 — «? 1»). `RangeWriteEpoch` только читает (атомики регионов, регионы не создаёт) и даёт 0 лишь для неотслеживаемого региона: `ed4f96d8:src/graphics/host_gpu/memoryTracker.h:52` (якорь «return mixed == 0 ? 1 : mixed;»; +1 — «}»). Защита от `EXIT` `ValidateRange` — то же условие `GuestRange::Valid`: `bufferCache.cpp:2908` (якорь «if (size == 0 \|\| !GuestRange {vaddr, size}.Valid()) {»; +1 — «return 0;»). Ответ исполнителя «эпохи старта процесса код не даёт ⇒ без заливки 1» — принят лидом (п. 500(а)(2)); D19 (`tests…:11131`, якорь «buffers.InvalidateMemory(dx_cpu + 0x10, 4);»; +1 — «(void)buffers.ObtainBuffer(dx_cpu, 0x10000, false, false);») — 0 без записи, 1 после записи и выгрузки, 1 без заливки; m9–m11 пойманы. Граница прочтения «0» — Н2 |
| п. 496(б)(3) RC3 `stamp_late` последним в сводке; две точки обнаружения | ✓ | точка «конец `DispatchDirect`» — деструктор держателя `ed4f96d8:src/graphics/host_gpu/renderer/renderCompute.cpp:85` (якорь «m_cache->F5IdNoteStampLate();»; +1 — «}»); точка «`TrackDccFill` застал неснятый штамп» — `ed4f96d8:src/graphics/host_gpu/renderer/cache/textureCache.cpp:3460` (якорь «if (m_f5id_stamp_address != 0 && !m_f5id_stamp_late) {»; +1 — «DiagF5Id::NoteStampLate();»). Флаг «уже посчитан» даёт один счёт на штамп (буква его не требует; правило п. 496(б)(3) читает только `= 0` / `> 0` — на чтение не влияет). Имя `stamp_late` последнее в `IdNames`, `kStampLate` перед `kIdCount`; D20 проверяет место в строке сводки. Снятие штампа не менялось |
| п. 496(б)(4) RC4 `why=cpu`, `f5cmu_exact_cpu` | ✓ | `cpu` ставится только вместе с `exact_stale` по `cpu_written`: `textureCache.cpp:3532` (якорь «f5_probe->cpu         = true; // Track F, F16k2 (RC4): why=cpu»; +1 — «} else {»); ответ функции меняет по-прежнему только `textureCache.cpp:3538` (якорь «if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {»; +1 — «return false;»). Счётчик и `why` пишет один деструктор `F5CmuScope`: `textureCache.cpp:1898` (якорь «if (m_decide && DiagF5::On()) [[unlikely]] {»; +1 — «switch (fix) {») и `:1915` (якорь «if (m_out != nullptr) [[unlikely]] {»; +1 — «m_out->fix = fix;»); `f5cmu_exact_cpu` растёт только в ветви `ExactStale` ⇒ `f5cmu_exact_cpu` ≤ `f5cmu_exact_stale` по построению. Имя последнее в `F5Names` (`static_assert` размера). K8: `why=cpu`, оба счётчика +1; m13, m14 пойманы |
| п. 496(б)(5) RC5 строка `cmask_fce_nohit`, свой предел 64 | ✓ | `descriptors.cpp:3995` (якорь «if (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&»; +1 — «f5_cmu.fix != DiagF5::CmuFix::Fresh) [[unlikely]] {»); предел — свой атомик: `ed4f96d8:src/graphics/host_gpu/renderer/diagF5.cpp:674` (якорь «bool NoteCmuNoHit(const CmuEventLine& line, bool drawn) {»; +1 — «const auto n = g_cmu_nohit_events.fetch_add(1, std::memory_order_relaxed) + 1;»), отдельно от `cmask_fce` (`diagF5.cpp:654`, якорь «bool NoteCmuEvent(const CmuEventLine& line) {»; +1 — «const auto n = g_cmu_events.fetch_add(1, std::memory_order_relaxed) + 1;»). Поля по букве (`n`, `b42`, `present`, `gpu`, `image`, `cmask`, `extent`, `fix`, `[why]`), `applied` нет. K7 (`tests…:10783`) — `=1`: `kept_applied` и строка, `=0`: прежнее решение, строки нет; m15, m16 пойманы |
| Тождество п. 496(б)(5) по коду | ✓ | §2.1 |
| п. 500(в)(1) довод «`b42=drawn` кодом не достигается» | ✓ [c] | §2.2 |
| п. 500(в)(2) один `TrackDccFill` на диспетчеризацию — нет ли ложного `stamp_late` от двух заливок | ✓ [c] | §2.3 |
| п. 500(в)(3) порядок `m_lock` в деструкторе держателя на всех выходах `DispatchDirect` | ✓ [c] | §2.4 |
| п. 492(з) «Ревью F16l», п. 495(б) на `ed4f96d8`; `=0` байт в байт; решение только на FCE-захвате; кольцо только при ручке; без нового потока и инверсии замков; набор подписи; имена последними | ✓ | §2.5 |
| Тест-сайт покрывает новые случаи | ✓ (с Н1, Н4) | §2.6 |
| Бинарь из названного коммита | ✓ [c] | §2.7 |

## 2. Разбор

### 2.1 Тождество п. 496(б)(5)

1. Счётчики `f5cmu_*` движутся только в деструкторе `F5CmuScope` при `m_decide && DiagF5::On()` (`textureCache.cpp:1898`), а
   `m_decide = fce && FixCmuOn()` (`textureCache.cpp:1889`, якорь «: m_out(out), m_decide(fce && DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {»;
   +1 — «m_probe.exact_decides = m_decide;»). `fce = true` — только у `PrepareCmaskClear` из `FindRenderTarget` с `fce_materialize`
   (`textureCache.cpp:2599`, якорь «PrepareCmaskClear(id, desc, fce_materialize, f5cmu); // Track F, F16k: the FCE acquisition and its decision»;
   +1 — «}»), а `FindRenderTarget(…, true, …)` в `src` зовётся одним местом — FCE-скан (`descriptors.cpp:3950`, якорь
   «DiagF5::On() ? &f5_cmu : nullptr); // Track F, F16k: its decision for the event line»; +1 — «}»), один раз на слот. Указатель `f5_cmu`
   передаётся при том же `DiagF5::On()`, что разрешает счёт, — тот же деструктор пишет тот же `fix` (`textureCache.cpp:1915`).
2. После захвата ветви взаимоисключающие: `Hit` ⇒ строка `cmask_fce` при любом `fix` (`descriptors.cpp:3967`, якорь
   «if (DiagF5::On() && b42.kind == FixB42Kind::Hit) [[unlikely]] {»; +1 — «// Track F, F16k (item 492(v)(4)): the event line of a B42 hit -
   the last present number of the video»); не `Hit` ⇒ `cmask_fce_nohit` при `fix` ∉ {`off`, `fresh`} (`:3995`). Все значения, двигающие счётчики
   (`kept`, `kept_applied`, `exact_stale`, `fallback`), ∉ {`off`, `fresh`} ⇒ каждое приращение даёт ровно одну строку одного вида с тем же `fix`;
   `off`/`fresh` счётчиков не двигают.
3. `NoteCmuEvent`/`NoteCmuNoHit` в `src` зовутся только в этих двух местах [c `git grep`]. Пределы — раздельные атомики, `n > 64` — без строки.
   Сверх буквы держится и `why=cpu` ↔ `f5cmu_exact_cpu` (одно условие `m_probe.cpu` в одном деструкторе).

Итог: тождество держится, пока ни один вид не исчерпал предел; нарушение при непревышенных пределах — дефект кода (форма п. 492(д)).

### 2.2 Довод «`b42=drawn` кодом не достигается» (п. 500(б)(1), (в)(1))

`FixB42Probe` возвращает `Drawn` только после первого теста `ed4f96d8:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:3708` (якорь
«if (!color.image_id || info.metadata.kind != ImageMetadataKind::None || info.samples != 1 ||»; +1 — «info.resources.levels != 1 ||
info.IsVolume() ||»), значит при `Drawn` у дескриптора `metadata.kind == None` (`Drawn` — `:3728`, якорь «if (fill.b42_draw_seq >
fill.b42_fill_seq) {»; +1 — «probe.kind = FixB42Kind::Drawn;»). Между пробой и захватом дескриптор меняет одно место — `:3927` (якорь
«if (b42.kind == FixB42Kind::Hit && FixB42Enabled()) {»; +1 — «color.desc.info.metadata.kind              = ImageMetadataKind::Cmask;»), только
при `Hit`. Захват требует `kind == Cmask` (`:3934`, якорь «if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {»;
+1 — «// Session 71, candidate C3 (counters only): the second entrance into») ⇒ при `Drawn` захвата нет, `f5_cmu.fix` остаётся значением по
умолчанию `Off` (`ed4f96d8:src/graphics/host_gpu/renderer/diagF5.h:208`, якорь «CmuFix fix = CmuFix::Off;»; +1 — «CmuWhy why = CmuWhy::None;»), и
условие `:3995` ложно. **Довод верен [c]:** строка `cmask_fce_nohit b42=drawn` на `ed4f96d8` не печатается ни при каком входе; её появление в логе
F16m означает не тот бинарь (правило п. 500(б)(1) — пункт лида — остаётся уместным). Строки `nohit` на этом коде — только `b42=none`
(`kind == Cmask` из регистров, проба `None`). Тот же разбор даёт: при `Hit` без `KYTY_FIX_B42` захвата нет, строка `cmask_fce` идёт с `fix=off`,
счётчики не движутся — тождество не задето.

### 2.3 Один `TrackDccFill` на диспетчеризацию (п. 500(в)(2))

`TrackDccFill` в `src` — одно место: `renderCompute.cpp:319` (якорь «cache.TrackDccFill(descriptor.Base48(), size, packed_clear);»; +1 —
«if (f5_tracked != nullptr) [[unlikely]] {»), ветвь `!clear_taken` функции `TryConsumeComputeImageClear`, которая возвращает `false`. Её
единственный вызов — `renderCompute.cpp:654` (якорь «TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,»; +1 —
«thread_group_z, mode, f5_on ? &f5_tracked : nullptr)) {»), один раз на `DispatchDirect`, только при `!indirect && !floor_clear_skip`.
Повторный вход в `DispatchDirect` между `:654` и штампом (`:1267` / `:1294`) исключён мьютексом рендера (`:493`, якорь
«Common::LockGuard            lock(m_context.GetMutex());»; +1 — «Common::FrameStats::MutexMark lock_mark(lock_t0);»). Пути `MetaClear` (`:651`)
и `ImgClear` (`:662`) заливку не ставят (`clear_taken` — без `TrackDccFill`; `ClearImageFromBuffer` и `TryConsumeComputeMetaClear` его не зовут —
[c `git grep`]). Значит, ветвь `textureCache.cpp:3460` в игре достижима только поверх штампа, который деструктор прошлой диспетчеризации уже
посчитал (флаг поднят ⇒ второго счёта нет), — **ложного `stamp_late` от двух заливок одной диспетчеризации нет [c]**; ветвь — страховка (D20
проверяет её прямым вызовом). Выходы между заливкой и штампом — `:1049` (нулевые группы) и `:1103` (`!bind_floor && BindFloorClearSkip()`,
якорь «if (!bind_floor && BindFloorClearSkip()) {»; +1 — «Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorSkipDrop, 1);»); при
`!indirect` и `BindFloorClearSkip()` уже `floor_clear_skip` (`:615`, якорь «const bool floor_clear_skip = !indirect && BindFloorClearSkip();»; +1 —
«if (floor_clear_skip) {») не пускает к `:654` — согласуется с доводом F16l о позднем штампе только при `KYTY_BIND_FLOOR_CLEAR` (если латч
`BindFloorClearSkip` не меняет ответа между `:615` и `:1100` — [I], не проверял: на чтение не влияет, `stamp_late > 0` и так уводит ключи в
«не определено»).

### 2.4 `m_lock` в деструкторе держателя (п. 500(в)(3))

`m_lock` — `TrackingSpinLock` без рекурсии (`ed4f96d8:src/graphics/host_gpu/renderer/cache/textureCache.h:344`, якорь
«TrackingSpinLock                                  m_lock;»; +1 — «PageManager&                                      m_page_manager;»): удержание
тем же потоком на входе деструктора было бы вечным спином. Держатель объявлен на уровне функции (`renderCompute.cpp:636`, якорь
«F5IdCsHolder f5id {f5_refusals};»; +1 — «if (DiagF5Id::On()) [[unlikely]] {»), его деструктор идёт раньше всех локалей, объявленных до него, и
позже всех, объявленных после него, в том числе вложенных областей (`scoped_lock` внутренних блоков снимается до выхода из блока). Локали до
`:636`: мьютекс рендера (`:493`, это не `m_lock`), `MutexMark`, `DispCeilDose`, `HoldLap`, `DispLap`, `CtxTick::OpScope`, `TextureCache::OpScope`
(`:504`, якорь «const SkcCensus::OpScope skc_op(m_context.GetTextureCache(), Common::SkipCeil::KindCS, false);»; +1 — «// Session 97, gate
"bindfloor": latch the floor decision for this whole dispatch before»; конструктор зовёт `SkcCensus::OpBegin`, замка не держит), `MutScope`,
`Lap`, `f5_refusals` — ни одна не держит `m_lock` [c определений `textureCache.h:423`, `commandScheduler.h:203`]. **На каждом выходе после
`:636` (`:651`, `:662`, `:1049`, `:1103`, `:1273`, конец функции) `m_lock` при входе в деструктор не удержан [c].** Порядок — мьютекс рендера →
`m_lock` → мьютекс `DiagF5Id` (лист), как у `StampPendingDccFill` (`textureCache.cpp:3471`, якорь «void TextureCache::StampPendingDccFill() {»;
+1 — «std::scoped_lock lock {m_lock};») и `TrackDccFill`; `Emit` отпускает мьютекс модуля до захвата `m_lock`. Без ручки деструктор не трогает
кэш (`m_d` пуст), `F5IdNoteStampLate` выходит до замка (`textureCache.cpp:3497`, якорь «void TextureCache::F5IdNoteStampLate() {»; +1 —
«if (!DiagF5Id::On()) {»). `m_cache` ставится в `Arm` вместе с `m_d` (`renderCompute.cpp:638`, якорь «f5id.Arm(input_info,
m_context.GetTextureCache());»; +1 — «}») — разыменование нуля исключено.

### 2.5 Члены п. 492(з) и п. 495(б) на новом коммите

- **`=0` байт в байт [c]:** каждое новое место под ручкой — штамп эпохи и `stamp_late` (адрес штампа ненулевой только при `DiagF5Id::On()`),
  `Arm`/деструктор (`m_d`), `F5IdNoteFceMiss` (зовётся при `DiagF5Id::On()`), `cpu` пробы (проба не `nullptr` только при `FixCmuOn()` на FCE или
  `DiagF5Id::On()`), строка `nohit` (`fix` ∉ {`off`, `fresh`} требует `m_decide`). Вывод `--diag-f5-only` — 176 строк = `810909e3` и `c0789a34`
  [отчёт `fin/site_same_*.txt`]. При `KYTY_DIAG_F5=1` строка `DiagF5:` длиннее на `f5cmu_exact_cpu` — вывод измерения (п. 500(б)(2)).
- **Решение только на FCE-захвате, кольцо только при ручке:** правки не касаются `exact_decides`, `ExactRingOn` и записи кольца
  (`bufferCache.cpp:2856`–`:2872` без изменений, кроме нового чтения `LargeGpuWriteSeq`). Ответ `PendingDccFillStale` меняет только `:3538`.
- **Без нового потока доступа:** `LargeGpuWriteSeq` и `F5IdNoteFceMiss` — поток GuestGpu (пишет `m_large_write_seq` тот же поток в
  `NoteGpuWrite`); `RangeWriteEpoch` — атомики регионов «lock free» по замыслу трекера; новых потоков нет.
- **Без инверсии замков:** единственный новый захват — §2.4; `NoteFillSeq`/`FillCpuEpoch`/`NoteStampLate` — мьютекс модуля (лист);
  `IsRegionCpuModified` на событии — прежний член.
- **Набор подписи не тронут [c]:** `git diff --name-only 810909e3 ed4f96d8` по `src`/`tests` — 9 файлов (`renderer/cache/*`, `diagF5.*`,
  `pipeline/descriptors.cpp`, `renderCompute.cpp`, тест-сайт); ни `src/graphics/shader/**`, ни файлов `SHADER_CACHE_EXTRA_FILES`
  (`shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`) в нём нет.
- **Имена последними [c]:** `F5CmuExactCpu` перед `Count`, `"f5cmu_exact_cpu"` последним в `F5Names`; `kStampLate`/`"stamp_late"` последними;
  `WrAfter::Large`, `CmuWhy::Cpu`, `StaleProbe::cpu` — последними членами. Гейтов и `Knob` нет.
- Поправки п. 495(б)(1)–(6): код кольца, ветви 2, пометок, тождества ветви 3, `kind=exit`, поля `n=` этим коммитом не менялся (дифф — только
  места RC1–RC5) — пункты ревью F16l `5271f19c` переносятся без изменений.

### 2.6 Тест-сайт

Новые случаи K7, K8, D18–D20, формы и Z есть и проходят в 7 плечах ручек [отчёт `fin/f16k.txt`, `ALL OK`]; мутанты m8–m16 — 9 из 9.
K1–K5, K8 проверяют, что при `Hit` общий счёт `DiagF5Ev:` растёт ровно на 1 (строки `nohit` нет), K7 — обратное. Не покрыто тест-сайтом:
вызов из деструктора держателя (Н1) и строки `nohit` с `fix` = `exact_stale`/`fallback`/`kept` (Н4) — оба держатся по коду (§2.1, §2.4).

### 2.7 Бинарь

sha256 `C:/kyty/f287/bin/kyty_emulator_d4328b0c.exe` = `d4328b0c8053d7deae0ef34691462af3e244dd3a6be07722146505b642ca203c` [c, = отчёту];
в бинаре строка версии `KytyPS5-2026-09-15-6a2987a-2240-ged4f96d8`; worktree `C:/kyty/f287/f16k/wt` — `HEAD` `ed4f96d8…`, `git status` 0 строк
[c]. Установленный `ps5 em/kyty_emulator.exe` — `adb0c82f…` (не тронут). Вторая строка версии в бинаре — Н3.

## 3. Наблюдения (без требований к коду)

- **Н1. Проводка «конец `DispatchDirect`» не исполняется тест-сайтом.** D20 зовёт `F5IdNoteStampLate` напрямую
  (`tests…:11159`, якорь «cache.TrackDccFill(dx_late, 0x1000, 0);»; +1 — «cache.F5IdNoteStampLate();»); мутант m12 режет тело функции
  (`11faf668:docs/track-f/f16k2/mut_f16k2.py:38`, якорь «"m12_no_stamp_late": (R + "cache/textureCache.cpp",»; +1 — строка старого текста тела),
  а не вызов `renderCompute.cpp:85` и не `Arm(…, cache)`. Вызов на месте [c §2.4], отказа на `ed4f96d8` нет. В игре положительного контроля
  `stamp_late` не будет (поздний штамп на формах тегов без `KYTY_BIND_FLOOR_CLEAR` недостижим, §2.3), поэтому `stamp_late = 0` на тегах F16m
  подтверждает отсутствие позднего штампа только вместе с этим чтением кода — так и читать.
- **Н2. Граница прочтения `cpu_mod=0`.** Эпоха региона двигается только при объявлении записи CPU (сброс в грязное с фолтом) и при провизорной
  выгрузке (`ed4f96d8:src/graphics/host_gpu/regionManager.h:222`, якорь «m_cpu_epoch.fetch_add(1, std::memory_order_release);»; +1 —
  «m_epoch.fetch_add(1, std::memory_order_release);»; `:413`, якорь «const bool provisional = request_pages != 0 || armed_pages != settled_pages;»;
  +1 — «if (provisional) {»). Запись CPU в страницу, уже грязную и открытую на запись в момент штампа, эпоху не двигает: если затем выгрузка
  снимет грязь, событие даст `cpu_mod=0`. На пути игры диапазон заливки в момент штампа чист от CPU: записываемый буфер диспетчеризации
  помечается грязным от GPU, а это `EXIT` при грязи CPU (`regionManager.h:184`, якорь «if (m_cpu_dirty.AnyInRange(start, end)) {»; +1 — строка
  `EXIT("GPU dirty state conflicts with CPU dirty state…")`) [c]; что каждый путь заливки проходит эту пометку — [I]. Чтение «`cpu_mod=0` —
  записи CPU после заливки не было» верно в пределах этой оговорки; отказа на формах тегов не вижу.
- **Н3. Две строки версии в бинаре.** Кроме `…-2240-ged4f96d8` в `d4328b0c` есть `…-2225-gc0789a34` (смещения 18 461 795 и 19 860 893). Та же
  пара у бинаря F16k `9040a667` (`c0789a34` + `810909e3`) и у отгруженного FS5 `631ff987` (`8a56dc2a` + `0e72bc19`) — прецедент принят
  (FS5d: «строка `SDL_REVISION` не читается»): нижняя строка — ревизия собранной ранее SDL дерева сборки, не код эмулятора [I по прецеденту].
  Опознание бинаря F16m — только по sha256, не по строке версии.
- **Н4. `nohit` с `exact_stale`/`fallback`/`kept`** тест-сайтом не проверяются (K7 — только `kept_applied`); тождество §2.1 держит их по коду,
  нарушение в логах F16m — дефект кода по п. 496(б)(5).
- **Н5. Порядок `exact` → `large` → `fallback` → `none`** — принят лидом (п. 500(а)(1)); `large` — один номер на процесс без адреса,
  завышение в сторону «не определено» (долг п. 500(г)(3)).

## 4. Проверено и как

Дифф `810909e3..ed4f96d8` по `src` прочитан целиком; контекст — функции `DispatchDirect`, `TryConsumeComputeImageClear`, `F5IdCsHolder`,
`TrackDccFill`, `StampPendingDccFill`, `F5IdNoteStampLate`, `PendingDccFillStale`, `F5CmuScope`, `PrepareCmaskClear` (начало),
`FindRenderTarget` (до `:2600`), `FixB42Probe`, `MaterializeBoundTargetDccClears` (CMASK-ветвь), `F5IdNoteFceMiss`, `NoteGpuWrite`,
`LastGpuWriteSeqExact`, `MemoryTracker::RangeWriteEpoch`, `RegionManager::ChangeState` и провизорная выгрузка. `git grep` по `ed4f96d8`:
вызыватели `TrackDccFill`, `StampPendingDccFill`, `F5IdNoteStampLate`, `TryConsumeComputeImageClear`, `FindRenderTarget`, `PrepareCmaskClear`,
`NoteCmuEvent`, `NoteCmuNoHit`. Тест-сайт: K7, K8, D18–D20 прочитаны; вывод `fin/f16k.txt` (7 плеч `ALL OK`) и `mut_f16k2.py` — из `11faf668`.
Бинарь — sha256 и строки версии. Ссылки этого отчёта проверены скриптом `refs_f16l2.py` по якорю и +1 (вывод `refs_f16l2.txt`: 53 из 53, `ALL OK`).

## 5. Не заявляется

Что RC1–RC5 достижимы в игре или что их там нет; что `stamp_late = 0` в игре доказывает что-либо сверх чтения кода (Н1); что каждый путь
заливки проходит пометку GPU (Н2); что сброс ветви 1 ложен хоть на одном событии; что правка `KYTY_FIX_F5CMU` меняет картинку или корректна
для железа; что K = 8 достаточно; что бинарь `d4328b0c` работает в игре; что SPIR-V корректен для устройства и картинка верна. Ни одно
число — не выигрыш; 60 FPS не обещаются.
