# M9d (`HPP-869`, трек M, волна 2) — код этапа 1 T188: `KYTY_DIAG_T188` и `T109Stat`, стенды, бинарь теста

Звено Emu Engineer по `ROADMAP.md` п. 785 (KytyPS5 `a73c2cb7`); проект — издание 2 `docs/track-m/m9a2/design_m9a2.md`
(`1ea4fbe2`) с решениями п. 785(б)–(в) (при расхождении действует пункт). Дата 2026-10-13 UTC; время событий —
`times.txt` (строки `date -u`). **Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не запускались
(ГП-стенд — отдельный режим `--t188-gpu-stand`, кейс 224 не исполняется); сборки `--parallel 2`, приоритет Idle (п. 760).**
Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой. Метки: [c] — проверено, [I] — вывод, [U] — неизвестно.
**Код в игре не проверен — WIP до тегов M9f.**

## 1. Итог

| что | значение |
|---|---|
| записка имён и мест | `names_before_code.md` (sha256 `0391ad77…`), зафиксирована 07:13:25Z — до первой правки кода (`patch_m9d.py` 07:24:17Z, `times.txt`) |
| коммит worktree | **`d490f648`** на M6a3 `3d227024` (п. 785(в)(4)), worktree `C:/kyty/m657/m9d/wt` |
| код в `main` | **`4363c35e`** (fast-forward `main` `90a13438` → `4363c35e`); cherry-pick `d490f648`: 2 конфликта в `textureCache.cpp` — соседство вставок с кодом трека F (`CompletePendingUpload`, после `InitializeImage`), разрешены «обе стороны»; строки `+`/`−` по 17 файлам = коммиту worktree, **`patch-id --stable` по `-U0` `fbb8cd11` = `fbb8cd11`**; с контекстом по умолчанию — `558202b4` ≠ `8ac9e2c7` (контекст `main` содержит код трека F, которого нет в базе) (`main_vs_wt.out.txt` `ALL OK`) |
| бинарь теста | `kyty_emulator.exe` **sha256 `751bfa7fd93b5611ec99bb8c6e81a1f46d32b5dac42488805c6b9a2f8a43f885`**, версия `KytyPS5-2026-09-15-6a2987a-1937-gd490f648c`; закреплённая копия **`C:/kyty/m657/bin/kyty_emulator_751bfa7f.exe`**; **не установлен** |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1 = M6a3** [c `kytyGitVersion.h`]; `git show --stat 4363c35e` не трогает `imageInfo.h`, `src/graphics/shader/**`, `gpu_format.h`, `gpu_defs.h` (0 строк) |
| `check_gate_order.py` | `GATE ORDER: clean`; вывод на worktree **байт в байт = выводу M6a3** (`gate_order_wt.out.txt`), на `wtmain` — `clean` (`gate_order_main.out.txt`); новых гейтов и ручек `gates.h` нет |
| `shader_cfg_tests` | 135 тестов, **0 падений** (новых 0; строки со словом `failed` — те же 5, что у M6a3); 374 модуля SPIR-V **байт в байт = M6a3** (`tests_spv_cmp.out.txt`) |
| стенд функций | `t188_stand` **45 из 45** (`stand_wt.out.txt`, `stand_main.out.txt` — и на сборке `main`); плечо CLS `ok=1` |
| ГП-стенд | `--t188-gpu-stand` **16 из 16** при `KYTY_IMAGE_DETILE_FUSE=1` и `=0`; с Khronos-валидацией — 16 из 16 и 0 строк про `vkCmdClearColorImage`/`vkCmdCopyImageToBuffer`; первый прогон — `rc 65` по дефекту стенда (`Image` на адресе 0 — `EXIT invalid data image range`), не сброс драйвера; второй — `rc 0`, драйвер жив ⇒ в `dl_cases.txt` не вносится |
| мутанты | **24 из 24 пойманы** (m1–m15 с m8s, g1–g4, t1–t4); исходники после мутантов = до (sha256 7 файлов); контроль (пересборка обеих целей, 5 плеч) `ALL OK` (`mut_m9d.out.txt`) |
| сборка `main` | `wtmain` @ `4363c35e`: `t188_stand` 45/45 и `kyty_emulator` собраны (проверка компиляции; бинарь `main` не используется) |

## 2. Что сделано (по `names_before_code.md`; места — функции коммита `d490f648`)

**Новый `src/libs/diagT188.{h,cpp}`** — `Libs::DiagT188` и `Libs::DiagT109`. Ручка `KYTY_DIAG_T188` читается статической
инициализацией (`g_mode`, только `getenv`); `1`/`2`/`3` — значение, иначе 0. `KYTY_DIAG_T188_CLS` — ключи 1–16 hex через
запятую, плохие токены отбрасываются. Строки: `T188: mode= cls= k=4` (конструктор `TextureCache`, при любом `mode`),
`T188Stat` (поля §4.4 в порядке таблицы, 70 полей), `T188Img` (ключ, 10 полей класса, 27 счётчиков §4.5; до 256 строк по
убыванию `lost_bytes + lost_pend_bytes`, затем `ev`; строка `key=other`), `T109Stat` (7 полей §8.3). Периодические —
каждые 4096 пушей AudioOut2 (`libAudio2.cpp`, рядом с `M5W2Stat`), выход — оба выхода `Execute` (`emulator.cpp`).

**Сайты** (все под `if (DiagT188::Mode() >= 1) [[unlikely]]`; при `=0` — только строка `T188:` раз на процесс):

| сайт | место | работа |
|---|---|---|
| S1 | `InvalidateMemoryFromGPU(addr, size, writer = Unk)`; `descriptors.cpp` → `St`, `bufferCache.cpp` fill → `Fill`, copy → `Copy` | писатель аргументом |
| S2 | цикл `InvalidateMemoryFromGPU` после `NoteInvalidateImage` M5W2, до `ClearGpuModified` → `T188Invalidate` → `NoteInvalidate` | `part`, писатель, форма W, байты, `in_pass`; `reopen` / `part_synced` / `part_dlmem` / новый эпизод; `cl_cover`; W эпизода без `IsGpuModified` — в объединение (решение 1) |
| S3 | `InitializeImage`, ветка перезаливки, после `UploadImage` и `pending_levels`, до `ClearBufferModified` → `T188CloseUpload` | закрытие по `t_upload_site` (или `cl_vo` в Svo), `lost_bytes` по залитым `[first, levels)`, ожидание `[source_first_level, pending_levels)` с `lost_pend_bytes`, план окраски |
| S3b / S3c | `CompletePendingUpload` после `UploadImage` → `T188PendDone`; `ConfigureImageSourceUnlocked` при `pending_levels = 0` → `PendDrop` | `pend_done` + окраска отложенных / `pend_drop` |
| S4 | `InitializeImage`, ранние выходы сжатого и MSAA → `T188Close` | `cl_cmp`, `cl_msaa` |
| S5 | тело `FreeImage` → `NoteFree` | `cl_free`, `pend_free`, отказ от чтений обратно |
| S6 | `DiagT188::PrintExitStat` → крюк `TextureCache::T188ExitHook` | ожидание чтений ≤ 2 с, `TryLock` `m_lock` ≤ 2 с, обход образов (`ep_bad`(в)), печать |
| S7 / S7b / S7c | `CommitGpuWrite` после `CompletePendingUpload`; `CopyImage` до `ClearBufferModified` приёмника; ветка `skip_gpu_stale` | `cl_commit`, `cl_copydst`, `cl_skip` |
| S8 | `CopyImage`, ветка `destination.MarkBufferModified()` → `T188Propagate` | `ep_prop` / `prop_merge` |
| Svo | `UpdateImage(id, t188_video_out)`, `swapchain.cpp` `ResolveSurface` передаёт `true` | флаг `m_t188_vo` вокруг `RefreshImage`, визит |
| Ss / Sd | `SynchronizeBufferFromImage` перед `return true`; `DownloadImageMemory` перед `return true` | `sseq := wseq` при всех уровнях (`sync_full`), иначе `sync_part`; `dseq := wseq` |
| Sw | **первый оператор** `Image::MarkGpuModified` (до `SkcStampW3` и до проверки перехода; RC13(а)), `wseq.fetch_add(1)` безусловно при `mode ≥ 1` (RC13(б)) | + флаг `rb_wr` при ждущем чтении |
| T109 draw | `SetGraphicsDynamicParams` после `depth_bias_enable`, аргумент — `viewports.data()`, `viewport_count` (тот же массив, что `setViewportWithCount` выше) (RC15) | `d32`, `zx_*`, `bias_*` |
| T109 ovr | ветвь `cmd_offset == DB_RENDER_OVERRIDE` в `HwCtxSetDepthMetadataRegister` — одно место (RC14) | `ovr_w`, `ovr_vpc` (бит 16) |

**`t188_rb_wr` (RC12)** — тело `TextureCache::UploadImage` (до выбора ветви: `DetileToImage` и `Image::Upload`, оба вызова),
`Image::Upload` (вызовы вне `UploadImage` — `CopyD16`), `MarkGpuModified`, `ClearImage`, приёмники `CopyImage` и
`CopyImageMip` (там `MarkGpuModified` условный). Полный список мест записи образа по `git grep` базы с пометками —
`names_before_code.md` §3 (`grep_m9d.out.txt`); места без пометки нет.

**Окраска и чтение обратно (`=2`/`=3`)** — `T188Gpu::TintLevels`: конец прохода, переход в `TransferDstOptimal`,
`clearColorImage (1, 0, 1, 1)` `{l, 1, 0, layers}`, сразу копия центрального текселя (слой 0 и последний) в буфер выгрузки
(`GetUtilityBuffer(Download)`, под `m_lock`) и барьер к хосту; итог — `DeferOperation` на завершение тика (rb0). rb1 —
`T188Gpu::ReadTexels` при первом посещении образа S2–S8/Svo в кадре `GpuTimeProfiler::Frame()` больше кадра окраски,
со снимком `rb_wr`. До K = 4 чтений на класс (п. 785(в)(1)). `tint_rb0_nofmt` = 0 по построению (формат без строки
ожидаемого кода не красится — `tint_skip_fmt`).

**Замок (RC6):** каждая функция места берёт `locked` = `TrackingSpinLock::HeldByCurrentThread()` (новый метод, чтение
`m_owner`); без замка — `lock_bad += 1`, работы нет. Таблица классов и реестр чтений — свой `std::mutex` после `m_lock`;
при записи команд и `Map` он не держится; колбэки берут только его.

## 3. Решения исполнителя (на проверку M9e; в записке §4 до кода)

1. W открытого эпизода на образе без `IsGpuModified` (флаг снят прошлым S2) при непокрывающей записи — в объединение без
   счётчика: объединение — все W эпизода; иначе `lost_bytes` и окраска `=2` считали бы потерянными байты, свежие в буфере.
2. Объединение — до 8 непересекающихся интервалов `W ∩ SourceRange()`; девятый не входит (`w_ovf` раз на эпизод, `lost_*` —
   верхняя граница, окраска — `tint_skip_ovf`).
3. Пропуск окраски — на S3 раз на эпизод, порядок `cls`, `vol`, `fmt`, `cpu`, `ovf`; S3b наследует.
4. Новое S3 при ждущих уровнях прошлого — прошлое ожидание `pend_drop`.
5. S6 без `m_lock` за 2 с печатает без обхода (поле не добавлено).
6. **S8 в игре недостижим с открытым эпизодом источника [c кода]:** `CopyImage` → `RefreshCopySource` → `RefreshImage` →
   `InitializeImage`; источник с меткой остаётся помеченным только у MSAA (у сжатого — `EXIT`), а у MSAA ранний выход S4
   закрывает эпизод (`cl_msaa`) раньше S8. Потери там нет (MSAA не перезаливается). Ожидание в игре — `ep_prop` = 0; S8
   проверен стендом функций (m9), место — чтением кода.
7. Начальное `DB_RENDER_OVERRIDE` — [I] 0; сброс контекста — `CpOpDispatchReset` → `cp.Reset()` (`pm4Handlers.cpp`),
   `m_depth_render_override` сбрасывает `Context::Reset`.

Отступления от букв издания 2, кроме решений: файлы мест — ещё `swapchain.cpp` (аргумент Svo), `libAudio2.cpp`
(периодическая строка), `emulator.cpp` (выход), `regionManager.h` дополнительно `TryLock()` (только S6).

## 4. Состояние и его жизненный цикл (правило с. 134)

- `Image::t188` (`image.h`, после `skc3_uid`) — `DiagT188::ImageState`. Под `m_lock`: `open` — ставят `NoteInvalidate`
  (новый эпизод, `diagT188.cpp:520`) и `Propagate` (`:722`), снимает только `CloseEpisode` (`:167`; зовут S2 cover, S3,
  `CloseNoUpload`, `NoteFree`); `wait` — ставит `CloseUpload` (`:590`), снимает `DropWait` (`:224`; S3b, S3c, S5, новое S3);
  `ovf`, `pend_*`, `w[]`, `n`, `key` — переписываются при открытии. Выход функции без снятия — только при `!locked`
  (до любой записи) и при закрытом эпизоде; состояние живёт ровно до закрытия по построению; на выходе процесса
  неснятые флаги считаются `open` / `pend_open` и сверяются обходом (`ep_bad`(в)). При `FreeImage` открытый эпизод закрыт
  `cl_free` до `DeleteImage`.
- Атомики: `wseq` (растёт в `NoteGpuWrite`, `diagT188.h`), `sseq`/`dseq` (пишут только Ss/Sd), `rb_pend` — ставит
  `RbBegin` (`:790`), снимают `RbWant1` (`:824`, `:847`) и `RbAbandonLocked` (`:299`; S5, новая окраска); `rb_wr` —
  ставят `NoteGpuWrite`/`NoteImageWrite` только при `rb_pend`, снимает `RbBegin` (`:789`).
- `TextureCache::m_t188_vo` — ставится и снимается в одном блоке `UpdateImage` (`textureCache.cpp:2537`, `:2539`) под
  `m_lock`; между ними только `RefreshImage` (исключений в коде нет, `EXIT` кончает процесс).
- Крюк выхода `g_exit_hook` — ставит конструктор `TextureCache` при `mode ≥ 1` (`:270`), снимает деструктор только
  своего контекста (`:276`, `SetExitHook(nullptr, this)`).
- `T188ExitHook`: `TryLock` (`:2117`) и `unlock` (`:2131`) на одном пути; без замка — печать без обхода.
- Реестр чтений `g_rb` и `g_rb_final` (`:1004`) — растут за процесс; `g_rb_final` возвращает в `false` только стенд
  (`ResetForStand`, `:1043`); после выхода поздние колбэки ничего не меняют.
- Новых TLS нет. Счётчики — `relaxed`-атомики за процесс.

## 5. Стенды

**`tests/T188Stand.cpp` (цель `t188_stand`)** — каждый из 45 случаев сбрасывает счётчики и сверяет **все 70 полей**
`T188Stat` с точными ожиданиями (неназванное поле обязано быть 0) плюс поля класса и состояния: покрытие по
`SourceRange()`, новый эпизод, `reopen`, `join`, `cl_cover`, полная / частичная синхронизация, запись после синхронизации,
`part_dlmem`, писатель `Unk`, формы W (по уровню, внутри уровня, прочее, объём), `lock_bad` на всех 9 функциях мест,
переполнение объединения и `tint_skip_ovf`, S3 при `=1`/`=2`/`=3`, уровень-часть, квота K, отложенные уровни (S3 + S3b),
исходы ожидания (drop / free / новое S3), пропуски `vol`/`fmt`/`cpu`, класс фиксирован на S2, все закрытия без перезаливки
(второй вызов — `cl_none`), S5, S8, `ep_bad`(б)(в), коды пурпура 10 форматов, ключ FNV-1a (независимый пересчёт),
`VerifyTintPlan`, чтение обратно (rb0 → rb1 через кадр: `over` при записи после окраски, `ok`, `bad`, отказ и выход →
`none`), T109 на 6 синтетических draw и запись `DB_RENDER_OVERRIDE`. Плечо `cls` (отдельный процесс,
`KYTY_DIAG_T188=2`, `KYTY_DIAG_T188_CLS=<ключ>,zz,1`) — строка `T188: mode=2 cls=2 k=4`, чужой класс → `tint_skip_cls`.
Драйвер `run_stand_m9d.py` сверяет и имена полей выходных строк с §4.4/§4.5/§8.3.

**ГП-стенд `--t188-gpu-stand`** (настоящее устройство `VulkanHarness`): 12 членов окраски — RGBA8_UNORM, R16_SFLOAT,
R8G8_UNORM × слои 1 и 4 × уровень 0 и 1 из 3 (уровень 2 не красится: мутант g1 на нём писал бы за пределы образа):
окрашенный уровень во всех слоях = код пурпура, остальные — залитые цвета, rb0 = пурпур; `sw_first` — настоящий
`Image`: переход, полная синхронизация, второй `MarkGpuModified` ⇒ `wseq` 2 ≠ `sseq` 1; `ovr` — настоящие обработчики
PM4: запись диапазоном 0x1–0x4 (`DB_COUNT_CONTROL`), прямая, косвенная — по 1 (1/1, 2/1, 3/2); `s7` — настоящий
`TextureCache`: S2 + `MarkGpuWritten` ⇒ `ep_new` 1, `cl_commit` 1, `lock_bad` 0; `rc12` — тайловая RGBA8 64×64 в гостевой
памяти, окраска `=3` на S3, затем в следующем кадре запись ЦП и перезаливка без эпизода ⇒ `tint_rb0_ok` 1,
`tint_rb1_over` 1, `tint_rb1_bad` 0 при `KYTY_IMAGE_DETILE_FUSE=1` и `=0`.

## 6. Мутанты (`mut_m9d.py`: точная подстановка, сборка цели стенда, плечи драйвера, возврат байт в байт)

| мутант | что | пойман |
|---|---|---|
| m1 | покрытие по `info.data.size` | `cover_src` |
| m2 | `reopen` открывает новый эпизод | `reopen`, `join`, `close_cover` (`ep_bad`) |
| m3 | закрытие без проверки открытого | 5 случаев закрытий (`cl_none`, `ep_bad`) |
| m4 | `=2`: окраска уровня, пересекающего W | `s3_part` (`tint_bad`) |
| m5 | окраска незалитого (отложенного) уровня | `s3_deferred`, `s3b_done` (`tint_bad`) |
| m6 | `sseq` при частичной синхронизации | `sync_part` |
| m7 | `wseq` не растёт (нет `fetch_add`) | `sync_then_write` |
| m8 | `CloseNoUpload(Commit)` ничего не делает | `close_commit` и др. |
| m8s | нет места S7 в `CommitGpuWrite` | ГП `s7` (`cl_commit` 0) |
| m9 | `Propagate` ничего не делает | `propagate` |
| m10 | нет проверки замка (S2) | `lock_bad` (8 ≠ 9) |
| m11 | объём в `w_mipal` | `vol_other`, `skips` |
| m12 | класс берётся на закрытии | `class_at_s2` |
| m13 | `Sw` внутри ветви перехода (`image.h`) | ГП `sw_first` (`wseq` 1 = `sseq` 1) |
| m14 | флаг `rb_wr` только в `Image::Upload` | ГП `rc12` при `imgfuse=1` (`rb1_bad` 1), при `imgfuse=0` — проходит: ветвь `DetileToImage` достигнута стендом [c] |
| m15 | счёт `DB_RENDER_OVERRIDE` в обработчике пакета по первому регистру | ГП `ovr` (диапазон 0/0) |
| g1 | `baseMipLevel = l + 1` | 12 членов окраски |
| g2 | `layerCount = 1` | члены со слоями 4 |
| g3 | чтение обратно записано до очистки | 12 членов (rb0 0) |
| g4 | очистка без перехода в `TransferDstOptimal` | плечо валидации: `VUID-vkCmdClearColorImage-imageLayout-00004` |
| t1 | только вьюпорт 0 | `t109_vp1` |
| t2 | `≥`/`≤` вместо строгих | `t109_full` |
| t3 | `bias_d32` без условия D32 | `t109_d24` и др. |
| t4 | `zx_narrow` без `zx_d32` | `t109_nozx`, `t109_vp1` |

Член ревью M9e по RC15 (аргумент `NoteDraw` — вычисленный массив, не вьюпорт гостя) — чтением кода: стенд функций
проверяет предикаты на синтетике, место вызова — `renderDraw.cpp` после `setViewportWithCount`.

## 7. Что M9d НЕ доказывает

- что окраска, чтение обратно или детектор видят любую потерю в игре; что путей записи образа вне списка нет (список
  `git grep` — база `3d227024`); что поздние перезаписи ловятся rb1 у текстур без повторных посещений мест (иначе
  `tint_rb1_none`); что `=2`/`=3` не меняют дальнейшую работу игры (режимы не измерение);
- гонку «запись учтена штампом раньше, чем её команды попали в синхронизацию» (RC13(б)) — [I];
- что `in_pass`, `w_*` и `img_*` верно оценивают цену формы A; что T109 расходится с консолью;
- ни одно число — не выигрыш; 60 FPS не обещаются.

## 8. Файлы (`docs/track-m/m9d/`)

| файл | что |
|---|---|
| `names_before_code.md`, `grep_m9d.out.txt` | записка имён и мест до кода; списки `git grep` базы |
| `patch_m9d.py` (+ `diagT188.h/.cpp`, `tc_members.inc` в коммите), `patch_m9d_stand.py`, `fix_flush.py`, `fix_addr.py`, `fix_cls.py` / `patch_wt.out.txt`, `patch_stand_wt.out.txt` | правки (якоря целыми строками), все `ALL OK` |
| `run_stand_m9d.py`, `stand_wt.out.txt`, `stand_main.out.txt`, `gpu_wt/` | драйвер стендов и прогоны (worktree, `main`) |
| `mut_m9d.py`, `fix_mut.py`, `mut_m9d.out.txt`, `mut_b1…b5.out.txt`, `mut_control.out.txt`, `wt_before_mut.sha`, `wt_after_mut.check.txt` | мутанты |
| `gate_order_wt.out.txt`, `gate_order_main.out.txt` | `check_gate_order.py` |
| `run_tests_m9d.py`, `tests.out.txt`, `tests_failed_lines.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M6a3 |
| `binary_m9d.out.txt`, `main_vs_wt.py`, `main_vs_wt.out.txt`, `resolve_main.py` | строки бинаря; сверка `main` с worktree; разрешение конфликтов |
| `mk_wt_m9d.sh`, `mkbuild.py`, `mkbuild_main.py`, `lowrun.py` | worktree, сборочные скрипты, приоритет Idle |
| `commit_msg_m9d.txt`, `commit_msg_m9d_main.txt`, `times.txt`, `sha256.txt` | сообщения коммитов; время событий; sha256 файлов и бинаря |
