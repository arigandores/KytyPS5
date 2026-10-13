# M9d (`HPP-869`) — записка имён и мест до первой правки кода

Основание — `ROADMAP.md` п. 785 (KytyPS5 `a73c2cb7`), проект — издание 2 `docs/track-m/m9a2/design_m9a2.md` (`1ea4fbe2`).
База — worktree `C:/kyty/m657/m9d/wt` от M6a3 `3d227024` (п. 785(в)(4)). Места — `<файл>:<строка>` worktree `3d227024`
(не `1ffda330`: номера издания 2 сдвинуты). Списки `git grep` — `grep_m9d.out.txt` (21 образец, 212 строк). Метки: [c] — проверено
кодом, [I] — вывод, [U] — неизвестно.

## 1. Ручки и строки (имена — издание 2 §4.1, §4.4, §4.5, §8.3; не меняются)

- `KYTY_DIAG_T188` — раз на процесс, `g_mode` читается статической инициализацией `diagT188.cpp` (только `getenv`, без лога):
  пусто / не задано / `0` / `false` / `off` / `no` → 0; `1`, `2`, `3` → это значение; любое другое → 0.
- `KYTY_DIAG_T188_CLS` — ключи через запятую; токен — 1–16 hex-цифр (без `0x`), иначе токен отбрасывается; `cls=<n>` — число
  принятых ключей, `all` — пусто. Ограничивает только окраску (`=2`, `=3`).
- Строки: `T188: mode= cls= k=4` (раз на процесс — из конструктора `TextureCache` и из стенда; при любом `mode`),
  `T188Stat: when=<periodic|exit> …` (поля §4.4 в порядке таблицы), `T188Img: when=exit key=<16 hex> fmt= tile= w= h= levels=
  layers= cmp= samples= usage= vol= …` (поля §4.5 в порядке списка; до 256 строк по убыванию `lost_bytes + lost_pend_bytes`, затем
  `ev`; строка `key=other` — сумма остальных), `T109Stat: when=<periodic|exit> d32= zx_d32= zx_narrow= bias_d32= bias_narrow= ovr_w=
  ovr_vpc=`. Периодическая — каждые 4096 очередных пушей AudioOut2 (частота `M5W2Stat`): вызов `DiagT188::NoteAudioPush()` рядом с
  `DiagM5W2::NoteAudioPush()` в `libAudio2.cpp:384` под `if (DiagT188::Mode() >= 1)`. Выход — `DiagT188::PrintExitStat()` рядом с
  `DiagM5W2::PrintExitStat()` в обоих выходах `Execute` (`emulator.cpp:491`, `:503`).
- Поля класса: `fmt` = `info.pixel_format` (vk::Format), `tile` = `info.tile_mode`, `w`/`h` = `info.extent`, `levels`/`layers` =
  `info.resources`, `cmp` = бит 0 `info.IsBlock()` | бит 1 `metadata.compression != Uncompressed`, `samples` = `info.samples`,
  `usage` = `ImageUsage` в момент S2 (бит 0 texture, 1 storage, 2 render_target, 3 depth_target, 4 video_out), `vol` =
  `info.IsVolume()`. Ключ — FNV-1a 64 (базис `0xcbf29ce484222325`, простое `0x100000001b3`) по 8 байтам LE каждого поля в этом
  порядке.

## 2. Новые имена кода (не гейты `gates.h`, `check_gate_order.py` — прежний вывод)

- `src/libs/diagT188.{h,cpp}` — пространство `Libs::DiagT188` (счёт, классы, окраска-план, чтение обратно, печать) и `Libs::DiagT109`
  (`NoteDraw`, `NoteRenderOverride`, `Read`). Чистые функции — для стенда: `ClassKey`, `CoversSource`, `WShape`, `MagentaCode`,
  `TexelIsMagenta`, `NoteInvalidate` (S2), `CloseUpload` (S3), `PendDone` (S3b), `PendDrop` (S3c), `CloseNoUpload` (S4, S7, S7b,
  S7c), `NoteFree` (S5), `Propagate` (S8), `NoteSync` (Ss), `NoteDownload` (Sd), `NoteGpuWrite` (Sw, inline), `NoteImageWrite`
  (флаг `rb_wr`, inline), `VerifyTintPlan` (`tint_bad`), `ExitScan` (S6). Каждая функция места берёт `locked` — ответ
  `TrackingSpinLock::HeldByCurrentThread()`; `false` ⇒ `lock_bad += 1`, работы нет.
- `DiagT188::ImageState` — поле `Image::t188` (`image.h`, после `skc3_uid`): под `m_lock` — `open`, `wait`, `ovf`, `pend_ovf`,
  `skip` (окраска эпизода пропущена на S3), `tinted`, `writer`, `n`, `pend_n`, `key`, `pend_key`, `w[8]`, `pend_w[8]`, `rb_first`,
  `rb_count`; атомики — `wseq` (0), `sseq`, `dseq` (`UINT64_MAX`), `rb_pend`, `rb_wr`.
- `DiagT188::Writer {Unk, St, Fill, Copy}` — аргумент `writer` у `TextureCache::InvalidateMemoryFromGPU` (умолчание `Unk`); вызовы
  `descriptors.cpp:1073` → `St`, `bufferCache.cpp:2277` → `Fill`, `:2346` → `Copy` [c — других вызовов нет, `grep_m9d.out.txt`].
- `DiagT188::Close {Smp, Rt, RtClr, Dt, Sto, ClrOp, Oth, Vo, Cover, Cmp, Msaa, Free, Commit, CopyDst, Skip}` — порядок полей `cl_*`.
- `TrackingSpinLock::HeldByCurrentThread()` (`regionManager.h`, чтение `m_owner` == текущему потоку).
- `TextureCache::UpdateImage(ImageId id, bool t188_video_out = false)` — `swapchain.cpp:432` (`ResolveSurface`) передаёт `true`
  (Svo); второй вызов `UpdateImage` — `depthRenderTarget.cpp:442–443` — прежний [c `git grep`: других нет]. Член
  `TextureCache::m_t188_vo` (под `m_lock`) ставится и снимается вокруг `RefreshImage` в `UpdateImage`.
- `T188Gpu::TintFormatOk`, `T188Gpu::TintLevels` (переход в `TransferDstOptimal` + `clearColorImage` `{l, 1, 0, layers}` и сразу
  `Image::Download` центра уровня слоя 0 и последнего слоя в буфер чтения — одна функция, порядок внутри неё) — свободные функции
  в `textureCache.cpp`, объявление в `textureCache.h`; ими пользуются места S3/S3b и ГП-стенд.
- Стенды: `tests/T188Stand.cpp` (цель `t188_stand`, `EXCLUDE_FROM_ALL` как `m_wave2_diag_stand`; функции без игры и ГП, T109);
  ГП-стенд — режим `--t188-gpu-stand` в `tests/ShaderRecompilerComputeTests.cpp` (`VulkanHarness`; другие случаи этого исполняемого
  файла не запускаются — кейс 224 `dl_cases.txt` не исполняется). Драйверы — `run_stand_m9d.py`, мутанты — `mut_m9d.py`.

## 3. Места (worktree `3d227024`)

| сайт | место | замок |
|---|---|---|
| S1 | `InvalidateMemoryFromGPU` аргумент; вызовы `descriptors.cpp:1073`, `bufferCache.cpp:2277`, `:2346` | — |
| S2 | `textureCache.cpp:3059–3074`, цикл, рядом с `NoteInvalidateImage` (`:3065`), до `ClearGpuModified` (`:3070`) | `m_lock` `:3052` |
| S3 | `InitializeImage`, ветка `else if (upload)`, после `UploadImage` и `pending_levels` (`:1848–1853`), до `ClearBufferModified` (`:1862`) | вызывающего |
| S3b | `CompletePendingUpload`, после `UploadImage` (`:1641–1645`) | вызывающего |
| S3c | `ConfigureImageSourceUnlocked` `:1267–1270` (`pending_levels = 0` без заливки) | вызывающего |
| S4 | `InitializeImage` `:1727–1735` (сжатый → `cl_cmp`, MSAA → `cl_msaa`) | вызывающего |
| S5 | тело `FreeImage` (`:481`) | вызывающего |
| S6 | `DiagT188::PrintExitStat` → крюк `TextureCache` (ставит конструктор при `mode ≥ 1`, снимает деструктор): `m_lock` попыткой ≤ 2 с, обход `m_slot_images` (Σ флагов, `ep_bad`(в)), ожидание чтений ≤ 2 с, печать | `m_lock` |
| S7 | тело `CommitGpuWrite` после `CompletePendingUpload` (`:2519`), до `ClearBufferModified` (`:2520`) | вызывающего |
| S7b | `CopyImage`, до `destination.ClearBufferModified()` (`:880`) | вызывающего |
| S7c | `InitializeImage` ветка `skip_gpu_stale`, до `ClearBufferModified` (`:1814`) | вызывающего |
| S8 | `CopyImage` `:848–852`, ветка `destination.MarkBufferModified()` | вызывающего |
| Svo | `UpdateImage` (`:2182–2187`) при `t188_video_out` | `m_lock` `:2183` |
| Ss | `SynchronizeBufferFromImage` перед `return true` (`:2945`) | `m_lock` `:2881` |
| Sd | `DownloadImageMemory` перед `return true` (`:3045`) | вызывающего |
| Sw | `Image::MarkGpuModified()` первым оператором (`image.h:153`, до `SkcStampW3` и до проверки перехода; RC13(а)); при `mode ≥ 1` `wseq.fetch_add(1)` безусловно (RC13(б)) | атомики |
| `in_pass` | S2: `!m_scheduler.Current().IsInvalid() && m_scheduler.Current().IsRendering()` (`render.h:135`) | GuestGpu |
| T109 draw | `SetGraphicsDynamicParams` (`renderDraw.cpp:388`), после `depth_bias_enable` (`:501`), аргумент — `viewports.data()`, `viewport_count` (тот же массив, что `setViewportWithCount` `:461`) | атомики |
| T109 ovr | `HwCtxSetDepthMetadataRegister`, ветвь `cmd_offset == Pm4::DB_RENDER_OVERRIDE` (`pm4Handlers.cpp:327`) — одно место (RC14) | атомики |

Места записи образа и флаг `t188_rb_wr` (RC12; член записки): **сам** — тело `TextureCache::UploadImage` (`:1382`, обе ветви:
`DetileToImage` `:1525` и `Image::Upload` `:1439`; оба вызова `:1641`, `:1849`), `Image::Upload` (`image.cpp:301`; вызовы вне
`UploadImage` — `CopyD16` `textureCache.cpp:823`, `:829`), `ClearImage` (`textureCache.cpp:2662`, обе ветви `:2720`, `:2742`/`:2745`),
`TextureCache::CopyImage` и `CopyImageMip` для приёмника (`:861`/`:867`, `:896` — `MarkGpuModified` там условный `:876`, `:903`);
**через `MarkGpuModified`** — `FindTexture` Storage `:2290`, `FindRenderTarget` `:2358`, `FindDepthTarget` `:2456`, `CommitGpuWrite`
`:2524`, `renderDraw.cpp:1621`, `:3685`; **через `MarkGpuWritten`/`CommitGpuWrite`** — `Image::Resolve` (`image.cpp:506`, `:516`;
вызов `renderDraw.cpp:5409`), `descriptors.cpp:3616` (`:3630`), `ReinterpretColorAsMsDepth` (`textureCache.cpp:1001` → `:1008`),
копия глубины `depthRenderTarget.cpp:485` (`:456`); **вне окраски (глубина)** — `renderDraw.cpp:2275`, `textureCache.cpp:2745`;
**не образы кэша** — `swapchain.cpp:290`, `:300`, `:729`. Места без пометки нет.

## 4. Решения исполнителя (на проверку M9e)

1. W эпизода, открытого на образе без `IsGpuModified` (после S2 флаг снят), при непокрывающей записи входит в объединение (без
   счётчика, вне И1–И4): объединение — все W эпизода; иначе `lost_bytes` и окраска `=2` считали бы потерянными байты, свежие в
   буфере. Покрывающая — `cl_cover` (издание 2).
2. Объединение хранит до 8 непересекающихся интервалов `W ∩ SourceRange()` (слияние смежных); девятый не входит, `ovf` ⇒ `w_ovf`
   раз на эпизод ⇒ `lost_*` — верхняя граница, окраска — `tint_skip_ovf`.
3. Пропуск окраски решается на S3 раз на эпизод в порядке `cls`, `vol`, `fmt`, `cpu`, `ovf`; S3b наследует решение (`skip`).
4. Новый эпизод S3 при ещё ждущих уровнях прошлого — прошлое ожидание `pend_drop` (его уровни этим буфером не зальются).
5. `tint_rb0_nofmt` = 0 по построению: формат без строки ожидаемого кода не окрашивается (`tint_skip_fmt`).
6. Чтение обратно — буфер выгрузки `GetUtilityBuffer(MemoryUsage::Download)` (под `m_lock`, как `DownloadImageMemory`), итог —
   `DeferOperation` (на завершение тика, без ожидания на месте); `T188` замок `g_rb_mutex` не держится при записи команд и `Map`
   (порядок замков: `m_lock` → `g_rb_mutex`; колбэк берёт только `g_rb_mutex`).
7. rb1 — на первом посещении образа S2–S8/Svo в кадре `GpuTimeProfiler::Frame()` больше кадра окраски; флаг `rb_wr` снимается
   снимком при выдаче rb1.
8. S6 при неудаче `m_lock` за 2 с печатает без обхода (`ep_bad`(в) не проверяется); поле не добавляется.
9. Начальное значение `DB_RENDER_OVERRIDE` — [I] 0; сброс контекста — `CpOpDispatchReset` → `cp.Reset()` (`pm4Handlers.cpp:1453`),
   поле `m_depth_render_override` (`hardwareContext.h:1222`) сбрасывается `Context::Reset` (`:864`).
