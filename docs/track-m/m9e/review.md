# M9e (`HPP-870`, трек M, Red Team) — враждебное ревью кода этапа 1 T188 `KYTY_DIAG_T188` (M9d)

**Вердикт: `PASS_WITH_FIXES` — 1 RC (RC1, код T109, место `diagT188.cpp` `DiagT109::NoteDraw`), код T188 — PASS.**

Основание — `ROADMAP.md` п. 785 (KytyPS5 `a73c2cb7`), проект — издание 2 `docs/track-m/m9a2/design_m9a2.md` (`1ea4fbe2`).
Вход — отчёт M9d `docs/track-m/m9d/report.md` (KytyPS5 `26343142`), код `main` `4363c35e` = worktree `d490f648` на M6a3
`3d227024`. Читал диф `3d227024..d490f648` целиком (17 файлов), `diagT188.{h,cpp}` построчно. Игра не запускалась;
ГП-кейсы `dl_cases.txt` не запускались (ГП-стенд — отдельный режим `--t188-gpu-stand`, исполнитель показал `rc 0` без
сброса драйвера; мой прогон — тоже `rc 0`); сборки — сценарием M9d (`--parallel 2`), процессы — приоритет Idle; замка
`C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; звено прогонов M3a2 (`HPP-861`) — `executionRunId` пусто при
каждой проверке перед командой > 60 с (`times.txt`). Метки: [c] — проверено, [I] — вывод, [U] — неизвестно.
Мои файлы — `C:/kyty/m657/m9e/` (копия в этой папке): `mut_m9e.py`, `mut_A…D.out.txt`, `mut_control.out.txt`,
`stand_own.out.txt`, `grep_rc12_own.txt`, `sha_bins.txt`, `times.txt`.

## 1. Члены задания

| член | итог | основание |
|---|---|---|
| путь `=0` = `3d227024` по коду, кроме одной строки `T188:` раз на процесс | ✓ [c] | §2 |
| RC12 — места `t188_rb_wr`; список мест записи образа — свой пересчёт `git grep` | ✓ [c] | §3 |
| RC12 — m14 «флаг только в `Image::Upload`» | ✓ [c] — пойман стендом (`gpu1` `member=rc12`, `gpu0` проходит) и чтением кода | §3, §5 |
| RC13 — `Sw` первым оператором, `fetch_add` безусловно при `mode ≥ 1` | ✓ [c] `image.h` `MarkGpuModified`; m13 пойман (`member=sw_first`) | §4 |
| RC14 — одно место счёта `DB_RENDER_OVERRIDE` | ✓ [c] | §4 |
| RC15 — аргумент `NoteDraw` = вычисленный массив, после `minDepth`/`maxDepth` (мутант «вьюпорт гостя») | ✓ [c] чтением | §4; предикат — **RC1** |
| свои прогоны стендов: функций (m1–m15), T109 (t1–t4), ГП-стенд | ✓ [c] `ALL OK`; 24 из 24 мутантов M9d пойманы | §5 |
| все места состояния эпизода под `m_lock` (`lock_bad`) | ✓ [c] | §6 |
| поля `Image` при `=0` не читаются | ✓ [c] | §2 |
| набор подписи трансляции не тронут | ✓ [c] | §7 |
| sha закреплённой копии бинаря | ✓ [c] `751bfa7f…` | §7 |

## 2. Путь `=0` (член п. 785(д))

Каждая новая строка исполняемого кода в эмуляторе при `KYTY_DIAG_T188=0` проверена [c диф `3d227024..d490f648`]:

- Все места S1–S8, Svo, Ss, Sd, Sw, T109 — под `DiagT188::Mode() >= 1` (`image.h`/`image.cpp` — `!= 0`, то же при `g_mode ∈ {0..3}`);
  `Mode()` — чтение глобала `g_mode`, заданного статической инициализацией только из `getenv`.
- `TextureCache::TextureCache` — `PrintModeLine()` при любом режиме (разрешённая строка `T188: mode=0 cls=all k=4`, один раз —
  `g_mode_printed.exchange`); крюк выхода — только при `mode ≥ 1`; деструктор — то же.
- `UpdateImage(id, t188_video_out)`: при `=0` условие `t188_video_out && Mode() >= 1` ложно → прежний `RefreshImage(id)`;
  `swapchain.cpp` передаёт `true` — значение читается только в этом условии.
- `InvalidateMemoryFromGPU(address, size, writer = Unk)`: `writer` читается только в `T188Invalidate` (под `diag_t188`).
- `PrintExitStat()`: `g_mode < 1 ||` — короткое замыкание до `g_exit_printed` и мьютекса крюка; при `=0` ничего.
- `NoteAudioPush` (`libAudio2.cpp`), `NoteRenderOverride` (`pm4Handlers.cpp`), `NoteDraw` (`renderDraw.cpp`) — под `Mode() >= 1`.
- `TrackingSpinLock::HeldByCurrentThread` / `TryLock` — новые методы; при `=0` не вызываются (`lock()`/`unlock()` не тронуты).
- Поля `Image::t188` при `=0` только конструируются (значения по умолчанию); чтений нет: все обращения — в функциях мест под
  гейтом и в `T188ExitHook`, который ставится только при `mode ≥ 1` [c `git grep "\.t188"`].

Отличия по коду, не меняющие решений эмулятора (строка «читать так», не RC): `sizeof(Image)` растёт на `ImageState`
(≈ 340 байт, [I] по полям); на горячем пути `MarkGpuModified` — одна непрошедшая проверка глобала; две `getenv` и пустые
контейнеры статической инициализации. `Image` уже был неперемещаемым (атомик `bind_stamp`), так что атомики `ImageState`
семантику копирования не меняют [c].

## 3. RC12 — места записи образа (свой пересчёт `git grep`)

Свой `git grep` на базе `3d227024` по образцам п. 785(б)(1) и шире (`copyBufferToImage|copyImage|resolveImage|clearColorImage|
clearDepthStencilImage|blitImage|clearAttachments|DetileToImage|.Upload(|vkCmd*|CopyMip(|.Copy(|.Resolve(|eClear`),
`grep_rc12_own.txt` (221 строка; кроме мест таблицы — транслятор, буферы, имена счётчиков). Каждое место записи образа:

| место (база) | функция | флаг `rb_wr` | M9d |
|---|---|---|---|
| `image.cpp:330` `copyBufferToImage` | `Image::Upload` | сам (`image.cpp`, тело `Upload`) | ✓ |
| `textureCache.cpp:1439` `image.Upload`, `:1525` `DetileToImage` | `UploadImage` (оба вызова `:1641`, `:1849`) | сам (тело `UploadImage`, до выбора ветви, ранних выходов до места нет [c]) | ✓ |
| `textureCache.cpp:823`, `:829` `destination.Upload` | `CopyD16` | через `Image::Upload` | ✓ |
| `image.cpp:455` (`Image::CopyImage`), `:610` (`Image::CopyImageWithBuffer`) | вызовы только `textureCache.cpp:861`, `:867` (`TextureCache::CopyImage`) [c] | сам (приёмник `CopyImage`) | ✓ (`:610` в записке не назван строкой, покрыт вызовом `:867`) |
| `image.cpp:646` | `Image::CopyMip` ← `CopyImageMip` | сам | ✓ |
| `image.cpp:506`, `:516` | `Image::Resolve` ← `renderDraw.cpp:5413` | через `MarkGpuWritten`/`CommitGpuWrite` → `MarkGpuModified` | ✓ |
| `textureCache.cpp:2710` (`loadOp eClear`), `:2742`, `:2745` | `ClearImage` (и `TryConsumeComputeImageClear` → `ClearImage` [c]) | сам (вход `ClearImage`) | ✓ |
| `descriptors.cpp:3616` | быстрая заливка | через `MarkGpuWritten` | ✓ |
| `depthRenderTarget.cpp:485`, `renderDraw.cpp:2275` | глубина | вне окраски | ✓ |
| `context.cpp:417`, `:427`, `:435` (`loadOp eClear` цели в `BeginRendering`) | цель кадра | через `MarkGpuModified` при захвате цели (`FindRenderTarget`/`FindDepthTarget`, быстрый путь `renderDraw.cpp:1630`) | в записке не названо (образец п. 785(б)(1) этого вида не включает) — «читать так», не RC |
| `swapchain.cpp:290`, `:300`, `:729` | образы цепочки показа | не образы кэша | ✓ |

Итог: места без флага нет [c]. m14 пойман на ветви `DetileToImage` (`imgfuse=1`: `rb1_bad` 1; `imgfuse=0` — проходит, т. е.
стенд действительно достаёт обе ветви); чтением: строка `NoteImageWrite` стоит в теле `UploadImage` до `UploadBinding`.
Пробные мутанты x1 (нет флага в `ClearImage`) и x2 (нет флага у приёмника `CopyImage`) стендом **не ловятся** (§5) — эти
два места доказаны только чтением кода (п. 785(б)(1) стенда для них не требует); строкой «не доказывает» для M9g.

## 4. RC13, RC14, RC15

- **RC13** [c]: `Image::MarkGpuModified` — первый оператор `if (DiagT188::Mode() != 0) NoteGpuWrite(t188)`, до штампа
  `SkipCeil::t_w3` и до проверки `!m_gpu_modified`; `NoteGpuWrite` — `wseq.fetch_add(1, acq_rel)` без условия + флаг `rb_wr`
  при `rb_pend`. Внешнего условия «уже помечен» у вызывающих нет: из 8 вызовов `MarkGpuModified` по `source.IsGpuModified()` условны
  два у приёмника копии (`textureCache.cpp:894`, `:928` worktree) — там содержимое приёмника = буферу источника, пропуск
  штампа ложного «synced» не создаёт [I]; остальные — захват цели / хранилища, фиксация записи, быстрый путь draw. m13 пойман (`member=sw_first`).
- **RC14** [c]: `git grep DB_RENDER_OVERRIDE` — таблица пакетов (`pm4Dispatch.cpp:16`, `HwCtxSetDepthMetadataRegisters` →
  цикл по регистрам), косвенные лямбды (`pm4Handlers.cpp:3124`) и запись диапазоном сходятся в `HwCtxSetDepthMetadataRegister`;
  `SetDepthRenderOverride` — один вызов (`:339`) в этой же ветви; счёт — в ней одной. Бит 16 = `DISABLE_VIEWPORT_CLAMP`
  (GFX10 `DB_RENDER_OVERRIDE`) [c по описанию регистра; соседние биты 27–30 кода совпадают]. m15 пойман (`member=ovr`).
- **RC15** [c]: в `SetGraphicsDynamicParams` массив `viewports` строится на каждый draw (`minDepth`/`maxDepth` — в том же
  цикле), `setViewportWithCount(viewport_count, viewports.data())` берёт тот же массив (вызов — только при смене, но
  содержимое = состоянию, действующему для draw); `NoteDraw(..., viewports.data(), viewport_count)` стоит после цикла.
  Вьюпорт гостя (`vp.viewports[i]`) в `NoteDraw` не идёт. Оба места вызова `SetGraphicsDynamicParams` (`renderDraw.cpp:4640`
  — хвост пакета, `:4774`) проходят через `NoteDraw`.

## 5. Свои прогоны стендов и мутантов

Сборка — `C:/kyty/m657/m9d/build` (worktree `d490f648`, `git status` чист до и после; `HPP-869` — `done`).

- `run_stand_m9d.py` (все плечи, неизменённая сборка): `pure` 45/45, `cls` ok, `gpu1`/`gpu0` 16/16, `gpuv` 16/16 —
  **`ALL OK`** (`stand_own.out.txt`). В плече `gpuv` 2 строки слоя: `VUID-vkDestroyDevice-device-05137` — **2 утёкших
  `VkImage` при разрушении устройства стенда** (у исполнителя то же: `validation_lines=2`); к `vkCmdClearColorImage` /
  `vkCmdCopyImageToBuffer` не относятся. Отчёт M9d §1 («0 строк про …») верен по букве, утечку не называет — гигиена
  стенда, не путь игры (наблюдение Н1, не RC).
- Мутанты M9d — свой полный прогон `mut_m9e.py` (тот же список и та же подстановка, вывод — в `m9e/mut`): **24 из 24
  пойманы** (A: m1–m6, m8–m12, t1–t4; B: m7, m8s `member=s7`, m13 `member=sw_first`, m14 `member=rc12` при `gpu0` OK, m15
  `member=ovr`; C: g1, g2, g3 — члены окраски, g4 — плечо валидации 20 строк про очистку/копию). Исходники после каждого
  мутанта восстановлены (sha256 5 файлов), контроль (пересборка обеих целей, 5 плеч) `ALL OK`.
- Пробные мутанты рецензента (x*, «чем доказано место»): x3 (`Join` решения 1 убран), x4 (ветвь `synced` убрана),
  x8 (`dseq` не ставится) — **пойманы**; x1 (флаг `ClearImage`), x2 (флаг приёмника `CopyImage`), x7 (`m_t188_vo` не ставится
  — `cl_vo` никогда), x9 (место S3c убрано) — **выживают**: места S3c, Svo и флаги RC12 у очистки и копии доказаны только
  чтением кода. Я их прочёл: стоят там, где названо в записке (S3c — `ConfigureImageSourceUnlocked` при `pending_levels = 0`;
  Svo — флаг вокруг `RefreshImage`; флаги — входы `ClearImage` и приёмник `CopyImage` перед `ClearBufferModified`). Не RC —
  п. 785 стенда на эти места не требует; строка «не доказывает» для чтения M9g (`cl_vo` = 0 в тегах — сначала подозревать
  место, не игру).

## 6. Состояние эпизода под `m_lock`

[c] Каждая функция места в `diagT188.cpp` (`NoteInvalidate`, `CloseUpload`, `PendDone`, `PendDrop`, `CloseNoUpload`,
`NoteFree`, `Propagate`, `NoteSync`, `NoteDownload`) первой строкой проверяет `locked` → `lock_bad`, работы нет. Не-атомарные
поля `ImageState` пишут ещё только `RbBegin` (из `T188Tint`, план непуст только при `locked`), `RbWant1` (из `T188Visit`,
зовётся лишь под `if (locked)` или под `scoped_lock` в `UpdateImage`) и `RbAbandonLocked` (из `NoteFree`/`RbBegin`); обход
выхода — под `TryLock`. `HeldByCurrentThread` — `relaxed`-чтение `m_owner` своим потоком: «держу я» видно точно, чужой
владелец ≠ текущему [c `regionManager.h`]. Порядок замков `m_lock` → `g_mutex` соблюдён: `Map` буфера выгрузки и запись
команд — вне `g_mutex` (в `T188Visit` `RbWant1` отпускает его до `Map`; в `T188Tint` `RbBegin` — после записи команд).
Все 4 места `ClearBufferModified()` имеют место закрытия перед собой (S7b `:901`, S7c `:1858`, S3 `:1909`, S7 `:2880`) [c];
`DeleteImage` зовётся только из `FreeImage` (S5 до него) [c]. При `=1` записи команд ГП нет (`T188Visit` выходит при
`Mode() < 2`, план окраски пуст) — режим только измеряет [c].

## 7. Подпись трансляции, `main`, бинарь

- Набор подписи (`generate_version.cmake`: `src/graphics/shader/**` + `shaderTranslationCache.cpp`, `gpu_format.h`,
  `gpu_defs.h`, `imageInfo.h` из `CMakeLists.txt:156`) — ни один файл не тронут [c `git diff --name-only`];
  `kytyGitVersion.h` сборки — `8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1 = M6a3 (и после моих пересборок).
- `main` `4363c35e` = worktree `d490f648`: `git patch-id --stable` по `-U0` — `fbb8cd111dcb` = `fbb8cd111dcb`, `--numstat`
  равны [c]; места S3 и S3b в `main` после разрешения конфликта стоят после `UploadImage`/`pending_levels` и до
  `ClearBufferModified` / `GpuMark` рядом с кодом трека F [c `git show 4363c35e`].
- Закреплённая копия `C:/kyty/m657/bin/kyty_emulator_751bfa7f.exe` — sha256
  `751bfa7fd93b5611ec99bb8c6e81a1f46d32b5dac42488805c6b9a2f8a43f885` = `build/install/kyty_emulator.exe` [c `sha_bins.txt`];
  в ней строки `T188: mode=%d cls=all k=%u`, `T188Stat: when=`, `T109Stat: when=`, версия `…-1937-gd490f648c`, хеш подписи
  `8dcf3177…` (по 1 вхождению).

## 8. RC

**RC1 — `DiagT109::NoteDraw` (`src/libs/diagT188.cpp`, цикл `narrow`) считает «суженными» вьюпорты, которые не сужают
клэмп глубины, — ложные `zx_narrow` / `bias_narrow`.** Проект (§8.3 издания 2, строка `zx_narrow`): «у любого **активного**
вьюпорта `minDepth > 0` или `maxDepth < 1`». Код проверяет все `viewport_count` слотов сырым сравнением полей:

- (а) **Пустые слоты.** При выходе VS `ViewportIndex` `viewport_count` = 16 (`indexed_viewports`); слот с `xscale = 0`
  получает `width = 1`, `scissor = {0, 0}` (не растеризуется), а `minDepth`/`maxDepth` — из гостя, обычно 0/0 ⇒
  `maxDepth < 1` ⇒ `narrow`. Сценарий: draw в цель D32 с экспортом Z (или смещением) и `ViewportIndex`, активный слот 0 —
  полный `[0, 1]`, слоты 1–15 пусты ⇒ `zx_narrow += 1` при отсутствии сужения.
- (б) **Перевёрнутый диапазон.** Vulkan клэмпит глубину к `[min(minDepth, maxDepth), max(minDepth, maxDepth)]`;
  вьюпорт `minDepth = 1, maxDepth = 0` (обратный Z через вьюпорт) — полный диапазон, но `minDepth > 0` ⇒ `narrow`.
  Сценарий: каждый draw D32 с экспортом Z при обратном Z вьюпортом ⇒ `zx_narrow = zx_d32`.

Следствие для п. 785(г): ложный `zx_narrow ≥ 1` ведёт чтение в (3) («условие достигнуто», T109 открыт) вместо (4)
(`НЕ ДЕФЕКТ` счётной формы) — ошибка консервативна (ложного `НЕ ДЕФЕКТ` не даёт), но серия M9f, единственный источник
данных T109 этапа 1, может не дать ответа (4) там, где он есть. Встречаются ли (а) или (б) в игре — [U]. Стенд T109 обоих
случаев не имеет (6 синтетических draw: `t109_d24`, `_off`, `_full`, `_max`, `_vp1`, `_nozx`).
**Что изменить (выбор лида):**
(1) код — `narrow` только по слотам, которые растеризуются (передать в `NoteDraw` маску или признак пустого слота: ветка
`viewport.width == 0` до замены на 1), с диапазоном `lo = min(minDepth, maxDepth)`, `hi = max(…)`, `narrow ⇔ lo > 0 ∨ hi < 1`;
стенд — два случая (16 слотов, активен 0, пустые 0/0 ⇒ `zx_narrow` 0; `[1, 0]` ⇒ 0) и мутанты «все слоты» / «без min/max»
обязаны ловиться; бинарь теста новый (вне набора подписи, путь `=0` не меняется);
(2) без кода — строка чтения п. 785(г): `zx_narrow ≥ 1` в теге выносит (3) только при доказанном отсутствии (а) и (б)
(иначе — «не определено» по этому тегу), с полем-свидетелем, которого сейчас нет — поэтому (2) почти всегда даёт
«не определено»; рекомендую (1).
Если RC1 не внести: T109 после M9f останется «условие достигнуто» по ложному счёту, следующий шаг (пара или снимок)
будет назначен на артефакт счётчика.

## 9. Наблюдения (не RC)

- Н1. ГП-стенд оставляет 2 `VkImage` при `vkDestroyDevice` (`VUID-vkDestroyDevice-device-05137`) — гигиена стенда.
- Н2. `CloseEpisode` при счётчике `open` = 0 делает `Sub` ⇒ поле `open` печатается как 2⁶⁴ − 1; случай уже помечен `ep_bad`(б),
  читать `open` только при `ep_bad` = 0.
- Н3. `PrintExitStat` вызывает крюк вне `g_hook_mutex`; деструктор `TextureCache`, идущий одновременно с выходом, оставил бы
  висячий `context`. На путях `Execute` (`quick_exit`, деструкторов нет) не достигается [I].
- Н4. Места S3c, Svo и флаги RC12 у `ClearImage` / приёмника `CopyImage` — только чтением кода (x1, x2, x7, x9 выживают), §5.
- Н5. `loadOp eClear` целей кадра (`context.cpp:417–435`) в записке мест не назван; покрыт штампом `MarkGpuModified` при
  захвате цели.

## 10. Что ревью НЕ доказывает

Что код ведёт себя так же в игре (теги — M9f); что все вызывающие держат `m_lock` (это проверит `lock_bad` в тегах);
что окраска, чтение обратно или детектор видят любую потерю; что T109 расходится с консолью; что (а) или (б) RC1 встречаются
в ASTRO BOT; гонку «запись учтена штампом раньше, чем её команды попали в синхронизацию» (RC13(б)) — [I]. Ни одно число —
не выигрыш; 60 FPS не обещаются.
