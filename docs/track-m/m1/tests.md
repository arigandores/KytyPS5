# M1a (HPP-835), член п. 752(г)(6): тесты upstream, применимые к нашему дереву без кода

Исполнитель — агент-разборщик звена M1a. Репозиторий `C:/kyty/KytyPS5` только читался. Версии: upstream `origin/main` = `dad900c6`,
база `6a2987a7`, наш `main` = `b3dc9c67`. Дата 2026-10-12.

## 0. Метод и пределы

- **Сборки не было.** `agent_rules.md` запрещает worktree, сборку и `cmake`; пробная сборка из задания не делалась. Все выводы
  «компилируется» — статические, **[I]**. Уверенность **c** ставится только фактам, проверенным `git grep`/`git show`/данными:
  отсутствие заголовка, имени, NID, поля; счёт `ophist.tsv`; строка нашего кода.
- Скрипты (временные, вне проекта): извлечение функций верхнего уровня из версий `6a2987a7` / `origin/main` / `b3dc9c67` файла теста;
  «новая» — нет в базе, «изменённая» — тело отличается от базы. Для каждой — транзитивное замыкание по вспомогательным функциям
  upstream-файла, затем:
  - **нет на b3dc9c67** — идентификаторы из замыкания (без комментариев и строк), которые есть в `origin/main:src` и которых нет ни в
    `b3dc9c67:src`/`tests`, ни в заголовках Vulkan/SPIR-V/SDL2 нашего дерева (подмодули Vulkan-Headers, SPIRV-Headers, SPIRV-Tools у нас и
    upstream на одних коммитах); плюс доступ к полю `.x`/`->x`, которого нет ни в нашем `src`, ни в нашем файле теста (ловит новые поля
    `TestCase` харнесса). Ложные срабатывания (члены `std::`, локальные поля) вычищены вручную;
  - читатель `SrtMemoryReader` с `std::span<uint32_t>` — у нас другая сигнатура (см. §1);
  - опкоды — имена `Opcode::`/`O::`/строки `decoded_counts` из замыкания, переведённые в `famop` по таблицам декодера upstream
    (`frontend/decode/*Ops.cpp`), счёт программ и SDWA — из `ophist.tsv` (VOP1/VOP2/VOPC — обе формы). Тесты, кодирующие опкод сырым
    словом (`EncodeVop2(0x..)`), этой колонкой не видны — у них опкод проставлен вручную в «кандидат», где это важно.
- «Что проверяет» для GPU-тестов без ручной пометки — по имени функции (`(по имени)`), не по чтению тела.
- «Применим без кода» = функция переносится в НАШ файл теста (с нашими вспомогательными функциями и нашим харнессом), код эмулятора
  не меняется. Целиком upstream-файлы с изменениями к нам не переносимы (см. §1). «Компилируется» не значит «проходит»: ожидания upstream
  написаны против его транслятора — у каждого кандидата «проверить прогоном».
- «Кандидат гейта» — тест, который (а) переносится без кода, (б) проверяет путь, который ASTRO BOT исполняет (опкод > 0 в `ophist.tsv`,
  функция HLE, которую игра импортирует, общий путь транслятора), (в) не противоречит нашему решению по реестру трека F. «Проба» — тест,
  чей провал на `b3dc9c67` ожидаем или вероятен: он не гейт, а сигнал для M1c.

## 1. Общие факты, общие для всех строк

| факт | основание | ув. |
|---|---|---|
| upstream перешёл на SDL3, мы на SDL2: тесты/источники с `<SDL3/...>` и API `SDL_Gamepad`, `SDL_CreateWindow(…, w, h, flags)` к нам не компилируются | `b3dc9c67:CMakeLists.txt:369` `set(kyty_emulator_link_libraries common Vulkan::Headers spirv-tools-opt spirv-tools SDL2-static imgui xxhash FFmpeg::ffmpeg fmt::fmt nlohmann_json::nlohmann_json LibAtrac9 kyty_git_version Zydis::Zydis xbyak::xbyak)` (+1: пустая строка); у upstream `3rdparty/SDL3` | c |
| сигнатура читателя SRT изменилась: у нас `uint32_t*`, у upstream `std::span<uint32_t>`; тесты с собственным читателем в форме upstream не компилируются | `b3dc9c67:src/graphics/shader/recompiler/ir/passes/SrtWalker.h:12` `using SrtMemoryReader = bool (*)(void* userdata, uint64_t address, uint32_t* value);` (+1: пустая строка) | c |
| наш агрегат `shader_cfg_tests` = `tests/shaderCfgTests.cpp` (+ `#include "S16dProbe.inc"`); upstream включает `ShaderRayTracingTests.inc` в `shaderCfgTests.cpp` и `ShaderRayTracingGpuTests.inc` в `ShaderRecompilerComputeTests.cpp` | `git show <rev>:tests/shaderCfgTests.cpp` (строки `#include`) | c |
| вспомогательные функции нашего `shaderCfgTests.cpp` отличаются: `Check`/`CheckSpirvBinaryValidates` у нас не прерываются при `KYTY_TESTS_CONTINUE`; `MakeCompileOptions` upstream ставит `user_data[3] = 3u << 28u` (режим границ буфера по умолчанию), у нас нули — тесты, опирающиеся на буфер по умолчанию, могут вести себя иначе | тела функций в обеих версиях | c (факт) / U (следствие) |
| харнесс GPU `ShaderRecompilerComputeTests.cpp`: `VulkanHarness`, `RunCase`, `MakeCases` изменены и у нас, и у upstream; новые `TestCase` upstream подключаются к НАШЕМУ харнессу; помощники `EncodeMimg0/1`, `EncodeFlat0/1`, `AppendStoreVgprAtLaneDwordOffset` совпадают | тела функций | c |
| libSce-библиотеки, которые игра импортирует (строки `libSce*` в `eboot.bin`, 64 имени): есть `libSceAudioOut`, `libSceAudioOut2`, `libSceHttp`, `libScePad`, `libScePngEnc`, `libSceSaveData`, `libSceSaveDataDialog`, `libSceNpTrophy2`, `libSceAvPlayer`; нет `libSceCes`, `libSceNgs2` | поиск `libSce[A-Za-z0-9_]+` в `games/PPSA21564-app/eboot.bin` (строки, не таблица импорта) | I |
| известные падения нашего `shader_cfg_tests` (14, `HANDOFF.md` §4) этим отчётом не пересматривались | — | — |

## 2. Новые файлы тестов upstream

| файл | что проверяет | применим без кода | кандидат гейта | ув. |
|---|---|---|---|---|
| `ArchiveFileTests.cpp`, `ArchiveTestFixture.h` | чтение файлов из контейнера ZArchive (`common/archive.h`) | нет: `common/archive.h` нет на b3dc9c67, ZArchive не подключён | нет: игра грузится из папки приложения, не из архива | c |
| `AudioOutTimingTests.cpp` | темп вывода AudioOut (`libs/audio.cpp`): заполнение, недогруз и застой очереди, запасные часы, батчи, темп динамика пада, усиления каналов | нет: `libs/dualSenseHaptics.h` нет на b3dc9c67; заглушки SDL3; наш `audio.cpp` несёт `KYTY_FIX_F8` | нет как есть; тема (темп звука, коммит `70a475ec8`) касается игры (AudioOut импортируется) — сигнал M1c | c |
| `AvPlayerFileTests.cpp` | AvPlayer открывает файлы через архив | нет: `common/archive.h`, `ArchiveTestFixture.h` | нет | c |
| `CesTests.cpp` | `CesMbcsStrToUtf8Str`/`GetUtf8Len` для CP932: отображение, частичный вывод, ошибки | частично: включает наш `libs/libCes.cpp` — компилируется с заголовком SDL2 [I] (цель CMake — связать с SDL2 вместо `SDL3::SDL3-static`, это правка теста); на Windows наш путь `SDL_iconv_open("UTF-8", CP932)` без Win32-ветки (`b3dc9c67:src/libs/libCes.cpp:6` `#include <SDL_stdinc.h>`, +1 `#include <array>`) — ожидаем `EXIT_IF` или провал | нет: `libSceCes` игра не импортирует | c (импорт) / I (провал) |
| `ControllerSettingsTests.cpp` | настройки пада (громкость динамика, вибрация, курки, владение портом) через `controller.cpp` с подменой SDL3 Gamepad | нет: API SDL3 (`SDL_Gamepad`, `SDL_RumbleGamepad`…); наш `controller.cpp` на SDL2 (`b3dc9c67:src/libs/controller.cpp:4` `#include "SDL.h"`, +1 `#include "common/assert.h"`) и несёт `KYTY_FIX_B24`/`KYTY_FIX_F24` | нет | c |
| `HttpUriParseTests.cpp` | `sceHttpUriParse` (пустой/отсутствующий query), `sceHttpUriBuild` (маска опций) | по компиляции да [I]: `InitNet_1_Http`, NID `IWalAn-guFs`/`5LZA+KPISVA`, `FindByNid` есть (`libNet.cpp:621`, `:657`, `:659`); ожидаем провал TestAbsentQuery/TestEmptyUri/TestBuildHonoursOption: правок `025b39c01`, `dc3cd2d2c` у нас нет (`b3dc9c67:src/libs/libNet.cpp:289` `constexpr size_t needed = 3;`, +1 пустая строка) | нет как гейт (падает); libSceHttp импортируется, вызов UriParse/UriBuild игрой не установлен — U | I |
| `LruCacheTests.cpp` | порядок обхода LRU, `ForEachItemBelow` с отсечкой, ранний выход, `Touch` (перестановка, тот же тик), `Free`, повторное использование id | **да**: API `common/lruCache.h` тот же; у нас лишь добавлен `Common::DrawStat::Mark` (`b3dc9c67:src/common/lruCache.h:38` `Common::DrawStat::Mark(Common::DrawStat::Lru);`), `drawStat.h` — header-only, цель без `common` линкуется [I] | **да** (дёшево, отдельная цель): LRU кэшей буферов и текстур рендера (`bufferCache.h:378`, `textureCache.h:401`) | c (API) / I (сборка) |
| `Ngs2SamplerTests.cpp` | HLE NGS2 (`libs/ngs2.cpp`): ресемплинг, ATRAC9, сабмиксеры, PCM16 | нет: `libs/ngs2.cpp` нет на b3dc9c67 | нет: у нас NGS2 не HLE (в `log_fs15_v` NGS2 работает гостевым кодом — `mutex init: sce_Ngs2_*`) | c / I |
| `PadHapticsTests.cpp` | haptics DualSense через аудиопорт вибрации, rumble | нет: `libs/dualSenseBluetooth.cpp`, `libs/dualSenseHaptics.cpp` нет | нет | c |
| `PngEncTests.cpp` | libScePngEnc на stb_image_write | нет: `libs/libPngEnc.cpp` нет | нет как тест; игра импортирует PngEnc (4 строки `unresolved PLT import patched to stub … [PngEnc_v1]` в `C:/kyty/f287/fs15c/log_fs15_v.txt`) — сигнал M1c (`48b52d31b`) | c |
| `SaveDataDialogTests.cpp` | статус SaveDataDialog: RUNNING на первом опросе, FINISHED на втором; Close, Terminate, повторная инициализация | частично: компилируется и линкуется с нашим `dialog.cpp` [I] (внешний вызов только `Config::GetUserId`); полный режим упадёт — у нас `Open` сразу ставит FINISHED (`b3dc9c67:src/libs/dialog.cpp:435` `g_save_status = SAVE_STATUS_FINISHED;`); режим `--consistency-only` пройдёт | нет: полный режим — поведение upstream (`05f92b642`); `--consistency-only` у нас тривиален | I |
| `SaveDataMemoryTests.cpp` | SaveDataMemory2: валидация, изоляция, sync, сбой записи, рестарт, классические пути, аллокации, параметры | нет: `SAVE_DATA_ERROR_BROKEN`, `_INTERNAL`, `_INVALID_LOGIN_USER`, `_MEMORY_NOT_READY`, `_NOT_MOUNTED`, `SaveDataMemorySync` нет в `libSaveData.cpp` | нет как есть; тема (`cfbaee07f` «fixes Astro Bot progress not saving») — у нас своя запись `_SaveData/<title>/sce_sdmemory/memory.bin` (`libSaveData.cpp:249–252`) — сверка M1c | c |
| `TrophySystemTests.cpp` | события UDS → трофеи, прогресс, сохранение разблокировок | нет: `common/trophies.h` нет | нет | c |
| `macosSse4aTests.cpp` | эмуляция SSE4a на macOS | нет: `loader/guestInstructionPatcher.h` нет; платформа macOS | нет (вне цели) | c |

## 3. Агрегат `shader_cfg_tests` (CPU, без Vulkan-устройства)


### 3.1 `shaderCfgTests.cpp` — новые тест-функции upstream (47)

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestShaderFeatureCollection | CollectShaderInfo: требования SPIR-V по IR (subgroup ballot/shuffle, производные CS, gather, LDS функции, valid mask PS) и стадийность; фатал на битых метаданных (не Windows) | да [I] | - | да (общий путь, все программы); проверить прогоном | I | new |
| TestShaderStageBarriers | S_BARRIER в CS → OpControlBarrier с AcquireRelease\|WorkgroupMemory (264); в VS барьер удаляется | да [I] | - | да: S_BARRIER SOPP:a — 66 программ; часть VS — форма | I | new |
| TestVertexBufferGrouping | PrepareProgram: группировка атрибутов вершин по буферам (stride, instance-rate, константный атрибут, пересчёт смещений при смене таблицы) | да [I] | - | да: путь выборки вершин всех VS | I | new |
| TestNggVertexEntryState | VS NGG (шейдер другой игры): размер волны 32/64 из регистра стадий, разные ключи кэша, экспорт позиции жив | да [I] | - | условно: общий путь VS, фикстура чужой игры; проверить прогоном | I | new |
| TestNativeStoreCompletion | S_WAITCNT_VSCNT как точка завершения записей (StoreCompletion) | нет: нет на b3dc9c67: S_WAITCNT_VSCNT | S_WAITCNT_VSCNT=9 | нет как есть; у нас SOPK 0x17 декодируется как S_WAITCNT (ScalarAluOps.cpp:91), игра исполняет SOPK:17 в 9 программах — сигнал для M1c | c | new |
| TestDisabledDebugBranches | S_CBRANCH_CDBG* декодируются отдельными опкодами и не берутся | нет: нет на b3dc9c67: S_CBRANCH_CDBGSYS_AND_USER, S_CBRANCH_CDBGSYS_OR_USER, S_CBRANCH_CDBGUSER | S_CBRANCH_CDBGSYS=1 S_CBRANCH_CDBGSYS_AND_USER=0 S_CBRANCH_CDBGSYS_OR_USER=0 S_CBRANCH_CDBGUSER=0 | нет как есть; у нас они S_NOP (ScalarAluOps.cpp:116), игра — SOPP:17 в 1 программе | c | new |
| TestNewShaderRecompilerCapturedFractF64 | декод V_FRACT_F64 | нет: нет на b3dc9c67: V_FRACT_F64 | V_FRACT_F64=0 | нет: VOP1:3e = 0 в ophist | c | new |
| TestNewShaderRecompilerF64AluEncodings | декод F64 ALU (ceil/floor/trunc/min/max) | нет: нет на b3dc9c67: V_CEIL_F64, V_FLOOR_F64, V_MAX_F64, V_MIN_F64, V_TRUNC_F64 | V_CEIL_F64=0 V_FLOOR_F64=0 V_MAX_F64=0 V_MIN_F64=0 V_TRUNC_F64=0 | нет: опкоды = 0 в ophist | c | new |
| TestNewShaderRecompilerVop1SdwaBfrev | декод V_BFREV_B32 SDWA (селекторы) и отказ на недопустимых модификаторах | да [I] | V_BFREV_B32=77 | нет: V_BFREV_B32 77 программ, но SDWA 0 | I | new |
| TestVop2SdwaMulI24Destination | SDWA-приёмник V_MUL_I32_I24 и отказ на резервных селекторах | да [I] | V_MUL_I32_I24=0 | нет: VOP2:9 = 0 | I | new |
| TestNewShaderRecompilerVop1SdwaNotDestination | SDWA V_NOT_B32: dst_sel/dst_unused, отказ на модификаторах | да [I] | V_NOT_B32=0 | нет: VOP1:37 = 0 | I | new |
| TestFloatComparisonInputModes | флаги режима сравнения FP (flush_input_denorms) | нет: нет на b3dc9c67: .flush_input_denorms, FPCompareFlags, flush_input_denorms | - | нет: FPCompareFlags нет на b3dc9c67 | c | new |
| TestScalarAshrI64Decoder | декод S_ASHR_I64 | нет: нет на b3dc9c67: S_ASHR_I64 | S_ASHR_I64=0 | нет: SOP2:23 = 0 | c | new |
| TestImageAtomicWidthDecoder | ширина image atomic (compare_swap, 64-бит) | нет: нет на b3dc9c67: compare_swap, supports_64 | IMAGE_ATOMIC_UMAX=0 | нет: опкоды = 0, поля нет | c | new |
| TestNewShaderRecompilerInteger64CompareEncodings | декод V_CMP(X)_*_I64/U64 | нет: нет на b3dc9c67: V_CMPX_EQ_I64, V_CMPX_EQ_U64, V_CMPX_F_I64, V_CMPX_F_U64, V_CMPX_GE_I64, V_CMPX_GE_U64, V_CMPX_GT_I64, V_CMPX_GT_U64 … | V_CMPX_EQ_I64=0 V_CMPX_EQ_U64=0 V_CMPX_F_I64=0 V_CMPX_F_U64=0 V_CMPX_GE_I64=0 V_CMPX_GE_U64=0 V_CMPX_GT_I64=0 V_CMPX_GT_U64=0 … | нет: VOPC I64/U64 CMPX = 0, имён нет | c | new |
| TestVopcCmpxClassF16Decoder | декод V_CMPX_CLASS_F16 | нет: нет на b3dc9c67: V_CMPX_CLASS_F16 | V_CMPX_CLASS_F16=0 | нет: VOPC:9f = 0 | c | new |
| TestPerspectiveCentroidInputs | входы PS perspective centroid VGPR | нет: нет на b3dc9c67: .ps_perspective_centroid_vgpr, ps_perspective_centroid_vgpr | - | нет: поле нет на b3dc9c67 | c | new |
| TestPerspectiveSampleInputs | входы PS perspective sample VGPR | нет: нет на b3dc9c67: .ps_perspective_sample_vgpr, ps_perspective_sample_vgpr | - | нет: поле нет на b3dc9c67 | c | new |
| TestDsFloatMinMaxDecoder | DS_MIN_F32/DS_MAX_F32: src_count 2, читают только адрес и DATA0, offset | да [I] | DS_MAX_F32=1 DS_MIN_F32=1 | да: DS:12 и DS:13 — по 1 программе | I | new |
| TestNewShaderRecompilerCfgLoopHeaderBufferLoadStructured | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNewShaderRecompilerCfgLoopExitSharedWithSelection | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNewShaderRecompilerCfgNestedLoopNonlocalExitStructured | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNewShaderRecompilerCfgMixedContinueNonmergeExitStructured | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNewShaderRecompilerCfgLoopEarlyContinuesStructured | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNestedSelectionPreservesDescriptorSources | источник дескриптора во вложенных ветвях | нет: нет на b3dc9c67: selected_pc | - | нет: selected_pc нет на b3dc9c67 | c | new |
| TestSharedExitPreservesNativeDescriptorSources | при общем выходе ветвей каждому месту использования буфера — дескриптор своей ветви | да [I] | - | проба: провал = кандидат дефекта выбора ресурса; не гейт до прогона | U | new |
| TestNativeScalarReadDescriptorPlanning | план скалярного чтения дескриптора не берёт чужую нативную маску исполнения | да [I] | - | проба (как выше) | U | new |
| TestScalarSelectedVccBufferAddress | 64-бит адрес, выбранный через VCC, копируется в писательный дескриптор буфера без баллота | да [I] | - | проба (как выше) | U | new |
| TestNativeGuardedSamplerSource | самплер под защищённой ветвью не берёт константы соседней ветви | да [I] | - | проба (как выше) | U | new |
| TestBoundedMaterialBufferStores | ограниченные записи буфера материала | нет: нет на b3dc9c67: NoIndirectBuffer, to_array | - | нет: NoIndirectBuffer, to_array нет | c | new |
| TestNativeDescriptorProvenanceKeepsGpuSelection | провенанс дескриптора сохраняет выбор GPU | нет: нет на b3dc9c67: IndirectBuffer | - | нет: IndirectBuffer нет | c | new |
| TestCfgSiblingSharedExit | CFG: сиблинги с общим выходом | нет: нет на b3dc9c67: ConditionExpression | - | нет: ConditionExpression нет | c | new |
| TestNewShaderRecompilerCfgEarlyReturnSharedLoopContinuation | структуризация CFG (циклы, общие выходы/continue) без диспетчера, покрытие инструкций, SPIR-V валиден | да [I] | - | условно: скалярные ветви во всех программах; член dispatcher_fallback — форма, не ответ; гейт — часть валидации | I | new |
| TestNewShaderRecompilerNativeU64Translation | нативный U64 (V_CMPX_NE_I64/U64, V_LSHL/LSHRREV_B64) | да [I] | V_CMPX_NE_I64=0 V_CMPX_NE_U64=0 V_LSHLREV_B64=0 V_LSHRREV_B64=0 | нет: опкоды = 0 в ophist | I | new |
| TestVertexMadU64UsesPortableProduct | V_MAD_U64_U32 в VS → переносимое произведение 32×32 (один OpUMulExtended, без OpIMul %ulong; NVIDIA отвергает) | да [I] | - | проба: VOP3:176 — 4 программы (стадия не проверена); хост NVIDIA | U | new |
| TestGraphicsComputeGetreg | S_GETREG_B32 в графике/compute | нет: нет на b3dc9c67: .async_compute, S_GETREG_B32, async_compute | S_GETREG_B32=0 | нет: SOPK:12 = 0 | c | new |
| TestMemoryFedScalarLeafCall | вызов листовой функции через S_SWAPPC с адресом из памяти | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .call_targets, .capture_specialization_reads, .has_swap_pc, .observed_function, .source_reads, PrepareShaderSource, RefreshShaderSource, call_targets … | S_SETPC_B64=9 | нет: PrepareShaderSource и др. нет | I | new |
| TestWave32MaskProjection | проекция масок wave32 | нет: нет на b3dc9c67: projected | - | нет: projected нет | c | new |
| TestU64RegisterPairRoundTrip | ConstantPropagation: неизменённая пара SGPR возвращает тот же нативный U64, изменённая — нет | да [I] | - | да (общий IR) | I | new |
| TestBlendMappingClassification | классификация смешения (blendMapping.h) | нет: нет на b3dc9c67: BlendMappingSupport, ClassifyBlendMapping, SourceAlpha, SourceAlphaOne, SourceAlphaZero | - | нет: blendMapping.h нет на b3dc9c67 (у нас Б35 своим dualSrcBlend.h) | c | new |
| TestLogicalAlphaBlendExport | экспорт alpha-blend source / dual-source | нет: нет на b3dc9c67: .alpha_blend_source, .dual_source_blending, ShaderAlphaBlendSource, SourceAlpha, SourceAlphaOne, SourceAlphaZero, alpha_blend_source, dual_source_blending | - | нет: ShaderAlphaBlendSource и др. нет; у нас Б35 KYTY_FIX_DUALSRC | c | new |
| TestGpuProducedWritableDescriptor | писательный дескриптор, произведённый GPU | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .capture_specialization_reads, capture_specialization_reads | - | нет: capture_specialization_reads нет | I | new |
| TestImmutableDescriptorPredicate | предикат неизменного дескриптора | нет: нет на b3dc9c67: ImmutableInteger | - | нет: ImmutableInteger нет | c | new |
| TestUniformSelectedWritableDescriptor | равномерно выбранный писательный дескриптор | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*) | - | нет: читатель с std::span | I | new |
| TestUniformSelectedDescriptorLoadAddress | адрес загрузки равномерно выбранного дескриптора | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .capture_specialization_reads, capture_specialization_reads | - | нет | I | new |
| TestBoundedScalarMaterialImageKeys | ключи образов материала | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .capture_specialization_reads, .indirect_descriptor, .table_scalar, .table_stride, capture_specialization_reads, indirect_descriptor, table_scalar, table_stride | - | нет | I | new |
| TestSpirvRepeatedEmission | повторная эмиссия SPIR-V той же программы детерминирована; переключение split-wave (subgroup 32) / native сбрасывает определения | да [I] | - | да: путь split-wave хоста NVIDIA (subgroup 32) для wave64 | I | new |

### 3.2 `ShaderRayTracingTests.inc` (CPU, upstream включает в `shaderCfgTests.cpp`)

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestRayTracingInstructions | декод IMAGE_BVH_INTERSECT_RAY 32/64 (NSA, R128, 11/12 компонент), IR BvhIntersect ×4, uses_dma, без образов; литерал не декодируется как инструкция; фатал на A16/D16/не-R128/усечённом NSA (не Windows) | частично (компилируется [I]; 1 член противоречит нашему имени опкода) | IMAGE_BVH_INTERSECT_RAY=20 | частично: BVH64 у нас — отдельный опкод IMAGE_BVH64_INTERSECT_RAY (ShaderDecoder.h:574), член opcode == IMAGE_BVH_INTERSECT_RAY && opcode_id == 0xe7 упадёт; часть BVH32 — кандидат (MIMG:e6 — 20 программ, MIMG:e7 — 0) | I | new |

### 3.3 `ShaderRayTracingGpuTests.inc` (GPU, upstream включает в `ShaderRecompilerComputeTests.cpp`)

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| FlatStackApertures | GPU: FLAT в сегменте flat — апертуры scratch/shared, неактивные дорожки, неканонические адреса не заворачиваются | да [I] | S_BREV_B32=6 | нет: игра исполняет только FLAT.global (c, d, f), сегмент flat — 0 | I | new |
| BvhIntersections | GPU: IMAGE_BVH_INTERSECT_RAY по узлам треугольников типов 0–3 (5 вершин, тройки GPURT), box16/box32, сортировка детей, box_grow (бит 23), барицентрики (бит 24 dword3), NaN-луч, правило top-left, грань = экстент, узел через границу страниц, предел size (dword2), 64-бит указатель (BVH64) | да [I] | - | проба для Ф10 и Б1б: тройки типов 2–3 совпадают с нашим выбором Ф10 по GPURT ((V2,V3,V4)/(V2,V4,V0) — пересчёт фикстуры [I]); формат ответа (Flag+kind), box_grow, top-left, предел size и BVH64 могут расходиться с нашей реализацией — прогон при KYTY_FIX_F10=1, KYTY_FIX_B1B=1, разбор каждого расхождения по первоисточнику GPURT | U | new |

### 3.4 `shaderCfgTests.cpp` — изменённые upstream функции (146), сводно

Функции, которые есть и в базе, и у upstream, но upstream их тело изменил. Наш вариант этих функций уже в нашем гейте.

| группа | число | функции | применим без кода | кандидат гейта | ув. |
|---|---|---|---|---|---|
| изменены и нами (конфликт) | 7 | `TestNewShaderRecompilerCapturedVopcSdwaCmpxClass`, `TestNewShaderRecompilerPixelImageSampleLodSelection`, `TestNewShaderRecompilerBufferLoadsGuardedByExec`, `TestMeshExportStorage`, `TestMeshInputAssembly`, `TestNewShaderRecompilerSpirvSizeBaselines`, `main` | нет: остаётся наша версия (решение M1c по месту) | — | c |
| используют имена, которых нет на b3dc9c67 (кроме уже названных) | 15 | `TestNewShaderDecoderArchitecture` (DS_MSKOR_B32, DS_WRITE_B8_D16_HI), `TestNewShaderRecompilerScalarMemoryBindingDomains`, `…ImageLoad2DMsaa`, `…UnbasedFlatUsesBda`, `TestGraphicsPushConstantPlacement`, `…NativeBindingPlan` (descriptor_counts/index/mask), `TestFusedShaderHandoffPreservesRegisters` (PrepareShaderSource, has_swap_pc), `TestMergedShaderUserDataSnapshot` (EvaluateDescriptor, fast_launch), `TestRenderTargetReverseExportMapping` (target_shader_mask), `TestTypedDescriptorRealWideMoveTranslation` (scalar_writes), `TestTypedDescriptorRealCarryAndScalarLoads` (EvaluateDescriptor), `TestSrtWalkerRealSmemTranslation`, `TestSrtWalkerVccBaseTranslation`, `TestSrtWalkerRealSBufferTranslation`, `TestScalarMemorySourcesCapturedBeforeWrites` (RefreshFlatBuffer); у трёх наших изменённых (`TestMeshExportStorage`, `TestMeshInputAssembly`, `…SpirvSizeBaselines`) версия upstream тоже требует отсутствующих имён | нет | нет | c |
| читатели памяти в форме `std::span` | 4 | `ReadHostTestMemory`, `ReadZeroTestMemory`, `ReadSrtHostDword`, `ReadSrtHostRangeDword` | нет (сигнатура `SrtMemoryReader`, §1) | — | c |
| имена есть, правка upstream не только косметическая (приближённо, после нормализации `Common::ContainsStr` → `find`) | ≈ 70 | ALU/SDWA/F16 (`…MoreAluFamilies`, `…BootF16UnaryOpcodes`, `…BootB16PackedAndSdwaOpcodes`, `…CapturedVop1SdwaByteConvert`, `…SMovB32`, `TestSopkCompareImmediateExtension`), память и буферы (`…MemoryFamilyTranslation`, `…MubufFormatTranslation`, `…TypedBufferTranslation`, `…NativeWideBufferIr`, `…BufferAtomicsGuardedByBounds`, `TestCapturedBufferAtomicsX2`), CFG (≈ 25 функций `…Cfg…`), экспорт/вершины (`…ClipDisabledPosition`, `…AuxPositionExports`, `…ExpPixelOutputs`, `…EarlyZDisabledWhenPixelKillEnabled`, `TestEmbeddedVertexFormatSwizzle`), IR (`TestValuePhiValidation`, `TestNativeWideValueValidation`, `TestU64ShiftConstantPropagation`) и др. | да по компиляции [I]; ожидания — upstream | нет как замена нашей версии: каждая — дельта ожиданий upstream; брать только с прогоном и разбором провалов (провал = отличие нашего транслятора, не обязательно дефект) | I |
| только косметика (`Common::ContainsStr` → `std::string::find`) | ≈ 50 | остальные изменённые | да, но выигрыша нет — наша версия равносильна | нет (уже в гейте нашей версией) | I |

Изменённые upstream функции `ShaderRecompilerComputeTests.cpp` (65): изменены и нами — `VulkanHarness`, `MakeCases`, `main`; с именами,
которых нет у нас, — 29 (в т.ч. `Vop3FmacF32NegatedSourceAccumulates` — `V_FMAC_F32`, `DsAtomicNoReturnVariants` — `DS_INC_U32`/`DS_DEC_U32`,
`FlatVirtualAddressRebasesGuestAllocation` — `kExtendedMemoryBase`, загрузка текстур — `BufferCopies`/`UpdateSize`); с именами — 33, из них
`CheckPs5GameExampleImageClearRuntimeShape` с читателем `std::span`. Остальные 32 (скалярные SAVEEXEC/WQM, `Vop3Med3I16Captured`,
`VectorVop3Lsh*B64Captured`, `VectorMadU64U32UnsignedCarryOut`, `VectorCompareClassF32`, `ImageGatherCompareOpcodes`, `CheckSampled*`,
`CheckPm4ContextStateOperations`, `CheckPm4WaitResume` и др.) — дельты ожиданий upstream к нашим существующим кейсам: да по компиляции [I],
не замена нашей версии без прогона.

## 4. Остальные цели (не `shader_cfg_tests`)

Новые функции upstream в изменённых файлах. Цели у нас существуют под теми же именами (`shader_recompiler_compute_tests`,
`resource_tracking_tests`, `resource_materialization_tests`, `scalar_provenance_tests`, `memory_tracker_tests`, `page_manager_tests`,
`kernel_file_system_tests`, `virtual_memory_allocation_tests`, `audio_out2_port_tests`, `event_queue_lifetime_tests`), `build_tests.cmd`
их не собирает. Весь upstream-файл к нам не переносим там, где он опирается на SDL3 (`KernelFileSystemTests.cpp` `main`), на
`OutputParam::gains` (`AudioOut2PortTests.cpp`: заглушка `AudioOutOutputs` пишет `params[i].gains`, у нас поля нет —
`b3dc9c67:src/libs/audio_internal.h:21` `struct OutputParam {`) или на новый API SRT (`EvaluateDescriptor`, `RefreshFlatBuffer`,
`indirect_descriptor` — `ResourceTracking`/`Materialization`/`ScalarProvenance`); поэтому «да» ниже — перенос функции в НАШ файл.
Файлы с нашими ручками: `memoryTracker.cpp` (`KYTY_FIX_B13`), `pageManager.cpp` (место вызова `KYTY_FIX_B36`), `fileSystem.cpp`
(`KYTY_FIX_B4`, `KYTY_FIX_F25`), `ResourceMaterialization.cpp` (`KYTY_FIX_F19`), `audio.cpp` (`KYTY_FIX_F8`) — ожидания upstream написаны
против их кода без наших правок; провал на них разбирается против строки реестра, а не «исправляется» под upstream.


### 4.1 `ShaderRecompilerComputeTests.cpp` — новые функции upstream (148; цель `shader_recompiler_compute_tests`, нужен Vulkan)

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| MakeTilingImage | вспомогательная функция теста | нет: нет на b3dc9c67: UpdateSize; поля харнесса TestCase: .UpdateSize | - | помощник: переносится вместе с тестом, сам не тест | c | new |
| CheckSigninDialogLifecycle | (по имени) Check Signin Dialog Lifecycle | нет: нет на b3dc9c67: HostClose, Signin, SystemDialog | - | нет (не применим без кода) | c | new |
| CheckPixelParameterAliases | (по имени) Check Pixel Parameter Aliases | нет: нет на b3dc9c67: .parameter_mode, LastVertex, Rectangle, ShaderPixelParameterMode, parameter_mode | - | нет (не применим без кода) | c | new |
| ScalarZeroShiftWithRuntimeCount | (по имени) Scalar Zero Shift With Runtime Count | да [I] | S_LSHR_B32=1986 | кандидат (опкоды: макс. 1986 программ); проверить прогоном | I | new |
| ScalarBitcmpB64DynamicOperands | (по имени) Scalar Bitcmp B64 Dynamic Operands | нет: нет на b3dc9c67: S_BITCMP0_B64, S_BITCMP1_B64 | S_BITCMP0_B64=0 S_BITCMP1_B64=0 S_BRANCH=5143 S_CBRANCH_SCC1=2859 S_CSELECT_B32=3772 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarBitcmpB64IntegerConstants | (по имени) Scalar Bitcmp B64 Integer Constants | нет: нет на b3dc9c67: S_BITCMP0_B64, S_BITCMP1_B64 | S_BITCMP0_B64=0 S_BITCMP1_B64=0 S_CSELECT_B32=3772 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarZeroBitOps | (по имени) Scalar Zero Bit Ops | нет: нет на b3dc9c67: S_BCNT0_I32_B32, S_BCNT0_I32_B64, S_FF0_I32_B32, S_FF0_I32_B64 | S_BCNT0_I32_B32=0 S_BCNT0_I32_B64=0 S_CMP_EQ_U32=4835 S_FF0_I32_B32=0 S_FF0_I32_B64=0 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarSextMasks | (по имени) Scalar Sext Masks | нет: нет на b3dc9c67: S_SEXT_I32_I16, S_SEXT_I32_I8 | S_CMP_EQ_U32=4835 S_SEXT_I32_I16=0 S_SEXT_I32_I8=0 V_CNDMASK_B32=4863/sdwa38608 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarSextConstantsAndAliases | (по имени) Scalar Sext Constants And Aliases | нет: нет на b3dc9c67: S_SEXT_I32_I16, S_SEXT_I32_I8 | S_CMP_EQ_U32=4835 S_SEXT_I32_I16=0 S_SEXT_I32_I8=0 | нет (не применим без кода) | c | new |
| ScalarBrevB64OperandsAndMasks | (по имени) Scalar Brev B64 Operands And Masks | да [I] | S_BREV_B64=0 S_CMP_EQ_U32=4835 V_CNDMASK_B32=4863/sdwa38608 V_READFIRSTLANE_B32=1830 | нет: тестируемые опкоды = 0 в ophist | I | new |
| ScalarDynamic64BitOps | (по имени) Scalar Dynamic64 Bit Ops | да [I] | S_ANDN2_B64=3859 S_AND_B64=3343 S_BCNT1_I32_B64=7 S_BFE_U64=1192 S_BFM_B64=8 S_BITREPLICATE_B64_B32=0 S_BITSET0_B64=0 S_BITSET1_B64=0 … | кандидат (опкоды: макс. 4901 программ); проверить прогоном | I | new |
| ReferenceAshrI64 | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| ScalarAshrI64Edges | (по имени) Scalar Ashr I64 Edges | нет: нет на b3dc9c67: S_ASHR_I64 | S_ASHR_I64=0 S_CMP_EQ_U32=4835 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarAshrI64OperandsAndAliases | (по имени) Scalar Ashr I64 Operands And Aliases | нет: нет на b3dc9c67: S_ASHR_I64 | S_ASHR_I64=0 S_CMP_EQ_U32=4835 V_READFIRSTLANE_B32=1830 | нет (не применим без кода) | c | new |
| ScalarAshrI64Masks | (по имени) Scalar Ashr I64 Masks | нет: нет на b3dc9c67: S_ASHR_I64 | S_ASHR_I64=0 S_CMP_EQ_U32=4835 V_CNDMASK_B32=4863/sdwa38608 | нет (не применим без кода) | c | new |
| ScalarB32MaskDataflow | (по имени) Scalar B32 Mask Dataflow | да [I] | S_ANDN2_B32=88 S_AND_B32=2994 S_CMP_EQ_U32=4835 S_CSELECT_B32=3772 S_NAND_B32=2 S_NOR_B32=41 S_NOT_B32=33 S_ORN2_B32=1 … | кандидат (опкоды: макс. 4835 программ); проверить прогоном | I | new |
| VectorIntegerExtremaRuntimeEdges | (по имени) Vector Integer Extrema Runtime Edges | да [I] | V_MAX3_I32=0 V_MAX3_U32=0 V_MAX_I32=8 V_MAX_U32=4 V_MED3_I32=0 V_MED3_U32=715 V_MIN3_I32=0 V_MIN3_U32=1 … | кандидат (опкоды: макс. 715 программ); проверить прогоном | I | new |
| Vop1SdwaBfrevSourceSelectors | (по имени) Vop1 Sdwa Bfrev Source Selectors | да [I] | V_BFREV_B32=77 | нет: SDWA-форма в ophist — 0 | I | new |
| Vop1SdwaFfbhCapturedScalarLowWordSource | (по имени) Vop1 Sdwa Ffbh Captured Scalar Low Word Source | да [I] | S_BUFFER_LOAD_DWORD=5451 V_FFBH_U32=5 | нет: SDWA-форма в ophist — 0 | I | new |
| Vop1SdwaNotPreservesHighWordDestination | (по имени) Vop1 Sdwa Not Preserves High Word Destination | да [I] | V_NOT_B32=0 | нет: тестируемые опкоды = 0 в ophist | I | new |
| Vop1SdwaNotPartialSourcesAndDestinations | (по имени) Vop1 Sdwa Not Partial Sources And Destinations | да [I] | V_NOT_B32=0 | нет: тестируемые опкоды = 0 в ophist | I | new |
| Vop2SdwaBitwiseByteDestinations | (по имени) Vop2 Sdwa Bitwise Byte Destinations | да [I] | V_AND_B32=4429/sdwa92 V_OR_B32=895 V_XNOR_B32=1 V_XOR_B32=15/sdwa4 | кандидат (опкоды: макс. 4429 программ, SDWA 92); проверить прогоном | I | new |
| Vop1SdwaMovByteDestinations | GPU: SDWA V_MOV_B32 — байтовые приёмники | да [I] | - | кандидат: VOP1:1 (V_MOV_B32) SDWA 3094 инструкции; проверить прогоном | I | new |
| Vop1SdwaMovByteSources | GPU: SDWA V_MOV_B32 — байтовые источники | да [I] | - | кандидат: VOP1:1 SDWA 3094; проверить прогоном | I | new |
| Vop2SdwaMaxI32CapturedHighWord | (по имени) Vop2 Sdwa Max I32 Captured High Word | частично: поля харнесса TestCase: .packed_rhs | V_MAX_I32=8 | после правки харнесса | I | new |
| Vop2SdwaMinI32CapturedByte0 | (по имени) Vop2 Sdwa Min I32 Captured Byte0 | частично: поля харнесса TestCase: .packed_rhs | V_MIN_I32=6 | после правки харнесса | I | new |
| Vop2SdwaMulI24Destinations | (по имени) Vop2 Sdwa Mul I24 Destinations | да [I] | V_MUL_I32_I24=0 | нет: тестируемые опкоды = 0 в ophist | I | new |
| Vop2SdwaMulU24Destinations | GPU: SDWA V_MUL_U32_U24 — частичные приёмники, sext байта источника, псевдонимы | да [I] | V_MUL_U32_U24=1767/sdwa16 | да: VOP2:b 1767 программ, SDWA 16 инструкций | I | new |
| Vop3MulLoU16CapturedAndSelectors | (по имени) Vop3 Mul Lo U16 Captured And Selectors | нет: нет на b3dc9c67: V_MUL_LO_U16 | V_MUL_LO_U16=0 | нет (не применим без кода) | c | new |
| Vop3MadI16CapturedSelectorsAndSaturation | (по имени) Vop3 Mad I16 Captured Selectors And Saturation | нет: нет на b3dc9c67: V_MAD_I16 | V_MAD_I16=0 | нет (не применим без кода) | c | new |
| Vop3Min3U16CapturedAndSelectors | (по имени) Vop3 Min3 U16 Captured And Selectors | нет: нет на b3dc9c67: V_MIN3_U16 | V_MIN3_U16=0 | нет (не применим без кода) | c | new |
| VectorAlignByteUsesTwoBitByteOffset | (по имени) Vector Align Byte Uses Two Bit Byte Offset | да [I] | V_ALIGNBYTE_B32=2 | кандидат (тестируемый опкод: макс. 2 программ); проверить прогоном | I | new |
| Vop3pIntegerNegationCapturedAndSelectedHalves | (по имени) Vop3p Integer Negation Captured And Selected Halves | да [I] | V_PK_ADD_U16=0 V_PK_MAX_I16=0 | нет: опкоды = 0 в ophist | I | new |
| Vop3pInt16Ops | (по имени) Vop3p Int16 Ops | да [I] | V_PK_ADD_I16=0 V_PK_ASHRREV_I16=0 V_PK_LSHLREV_B16=0 V_PK_LSHRREV_B16=0 V_PK_MAD_I16=0 V_PK_MAD_U16=0 V_PK_MAX_U16=0 V_PK_MIN_I16=0 … | нет: опкоды = 0 в ophist | I | new |
| VectorCvtF16U16ByteSource | (по имени) Vector Cvt F16 U16 Byte Source | да [I] | V_CVT_F16_U16=0 | нет: тестируемые опкоды = 0 в ophist | I | new |
| VectorReadlaneSelectsTwoKeysWithinWave | (по имени) Vector Readlane Selects Two Keys Within Wave | да [I] | V_CMP_EQ_U32=1939/sdwa2826 V_CNDMASK_B32=4863/sdwa38608 V_LSHRREV_B32=1784/sdwa1024 V_READLANE_B32=834 | кандидат (тестируемый опкод: макс. 834 программ); проверить прогоном | I | new |
| VectorDpp8Captured | GPU: DPP8 | да [I] | - | нет: DPP8 в ophist — 0 | I | new |
| VectorDppRowShare | GPU: DPP16 row_share | да [I] | - | условно: DPP16 игра исполняет (V_MOV_B32 17000, VOP2:4 21146), row_share — не проверено | I | new |
| VectorMadF32RoundsProduct | GPU: V_MAC/V_MAD/V_MADMK/V_MADAK_F32 (VOP2 1f–21, VOP3 11f/141) округляют произведение (не fused), V_FMAC/FMA/FMAMK/FMAAK (VOP2 2b–2d, VOP3 12b/14b) — fused | нет как есть (имена O::V_FMAC_F32/V_FMAMK_F32/V_FMAAK_F32 нет на b3dc9c67) | V_FMAAK_F32=1745 V_FMAC_F32=1444 V_FMAMK_F32=0 V_FMA_F32=2945 V_MAC_F32=5532 V_MADAK_F32=4197 V_MADMK_F32=2785 V_MAD_F32=5540 | проба, ожидаем провал на b3dc9c67: VOP2 2b–2d у нас декодируются как V_MAC/MADMK/MADAK (VectorAluOps.cpp:68), а все они и V_MAD_F32 переводятся в FPFma32 (Vector.cpp:414–418); игра: VOP2:1f 5532, VOP3:141 5540, VOP2:2b 1444, VOP2:2d 1745 программ — сигнал класса А для M1c (upstream d8be245c2) | I | new |
| VectorMadF32FlushesDenorms | GPU: V_MAD_F32 сбрасывает денормали даже при float_mode 0xf0 | да [I] | V_MAD_F32=5540 | проба: V_MAD_F32 — 5540 программ; игра работает с FLOAT_MODE 0xc0 (сброс), поэтому денормальная часть для ASTRO BOT [I] не влияет; округление — см. VectorMadF32RoundsProduct | I | new |
| CubeIdCapturedNegationAndOutputScale | GPU: V_CUBEID_F32 с отрицанием и масштабом выхода | да [I] | V_CUBEID_F32=1731 | да: 1731 программа | I | new |
| Vop3Int16Ops | (по имени) Vop3 Int16 Ops | да [I] | V_ADD_NC_I16=0 V_ASHRREV_I16=0 V_MAX_U16=0 V_MIN_U16=0 V_SUB_NC_U16=0 | нет: опкоды = 0 в ophist | I | new |
| VectorCompareInteger64Edges | (по имени) Vector Compare Integer64 Edges | нет: нет на b3dc9c67: V_CMPX_EQ_I64, V_CMPX_GE_I64, V_CMPX_GT_I64, V_CMP_F_I64, V_CMP_GE_I64, V_CMP_GE_U64, V_CMP_GT_I64, V_CMP_LE_I64 … | V_CMPX_EQ_I64=0 V_CMPX_GE_I64=0 V_CMPX_GT_I64=0 V_CMP_EQ_I64=0 V_CMP_F_I64=0 V_CMP_F_U64=0 V_CMP_GE_I64=0 V_CMP_GE_U64=0 … | нет (не применим без кода) | c | new |
| VectorCompareExecWaveMasks | (по имени) Vector Compare Exec Wave Masks | нет: нет на b3dc9c67: V_CMPX_EQ_F64, V_CMPX_EQ_I16, V_CMPX_EQ_I64, V_CMPX_EQ_U64, V_CMPX_F_F64, V_CMPX_F_I64, V_CMPX_F_U64, V_CMPX_GE_F64 …; поля харнесса TestCase: .update_exec | V_CMPX_EQ_F64=0 V_CMPX_EQ_I16=0 V_CMPX_EQ_I64=0 V_CMPX_EQ_U64=0 V_CMPX_F_F64=0 V_CMPX_F_I64=0 V_CMPX_F_U64=0 V_CMPX_GE_F64=0 … | нет (не применим без кода) | c | new |
| VectorCompareF64Edges | (по имени) Vector Compare F64 Edges | нет: нет на b3dc9c67: V_CMP_EQ_F64, V_CMP_F_F64, V_CMP_GE_F64, V_CMP_GT_F64, V_CMP_LE_F64, V_CMP_LG_F64, V_CMP_LT_F64, V_CMP_NEQ_F64 … | V_CMP_EQ_F64=0 V_CMP_F_F64=0 V_CMP_GE_F64=0 V_CMP_GT_F64=0 V_CMP_LE_F64=0 V_CMP_LG_F64=0 V_CMP_LT_F64=0 V_CMP_NEQ_F64=0 … | нет (не применим без кода) | c | new |
| VectorCompare64WaveMasks | (по имени) Vector Compare64 Wave Masks | нет: нет на b3dc9c67: V_CMP_EQ_F64, V_CMP_NE_I64 | V_CMP_EQ_F64=0 V_CMP_NE_I64=0 | нет (не применим без кода) | c | new |
| VectorF64CapturedScreenSpaceShadows | (по имени) Vector F64 Captured Screen Space Shadows | нет: нет на b3dc9c67: V_CVT_F32_F64, V_CVT_F64_I32, V_FMA_F64, V_MUL_F64, V_RCP_F64 | V_CVT_F32_F64=0 V_CVT_F64_I32=0 V_FMA_F64=0 V_MUL_F64=0 V_RCP_F64=0 | нет (не применим без кода) | c | new |
| VectorFractF64CapturedAndEdges | (по имени) Vector Fract F64 Captured And Edges | нет: нет на b3dc9c67: V_FRACT_F64 | V_AND_B32=4429/sdwa92 V_FRACT_F64=0 | нет (не применим без кода) | c | new |
| VectorMinMaxF64CapturedAndEdges | (по имени) Vector Min Max F64 Captured And Edges | нет: нет на b3dc9c67: V_MAX_F64, V_MIN_F64 | V_MAX_F64=0 V_MIN_F64=0 | нет (не применим без кода) | c | new |
| VectorRoundF64EdgesAndModifiers | (по имени) Vector Round F64 Edges And Modifiers | нет: нет на b3dc9c67: V_CEIL_F64, V_CMP_EQ_F64, V_FLOOR_F64, V_TRUNC_F64 | V_CEIL_F64=0 V_CMP_EQ_F64=0 V_FLOOR_F64=0 V_TRUNC_F64=0 | нет (не применим без кода) | c | new |
| VectorFractF64CapturedChainRuntimeExec | (по имени) Vector Fract F64 Captured Chain Runtime Exec | нет: нет на b3dc9c67: V_CVT_F32_F64, V_CVT_F64_F32, V_CVT_F64_I32, V_FMA_F64, V_FRACT_F64 | S_AND_SAVEEXEC_B64=3415 S_BREV_B32=6 S_BUFFER_LOAD_DWORD=5451 V_AND_B32=4429/sdwa92 V_CMP_EQ_U32=1939/sdwa2826 V_CVT_F32_F64=0 V_CVT_F64_F32=0 V_CVT_F64_I32=0 … | нет (не применим без кода) | c | new |
| VectorF64WideningConversions | (по имени) Vector F64 Widening Conversions | нет: нет на b3dc9c67: V_CVT_F64_F32, V_CVT_F64_U32 | V_AND_B32=4429/sdwa92 V_CVT_F64_F32=0 V_CVT_F64_U32=0 | нет (не применим без кода) | c | new |
| VectorF64ModesModifiersAndExec | (по имени) Vector F64 Modes Modifiers And Exec | нет: нет на b3dc9c67: V_ADD_F64, V_CVT_F32_F64, V_CVT_F64_I32, V_FMA_F64, V_MUL_F64, V_RCP_F64, x1p | V_ADD_F64=0 V_AND_B32=4429/sdwa92 V_CVT_F32_F64=0 V_CVT_F64_I32=0 V_FMA_F64=0 V_MUL_F64=0 V_RCP_F64=0 | нет (не применим без кода) | c | new |
| VectorCompareF32ExposureGuard | (по имени) Vector Compare F32 Exposure Guard | да [I] | V_CMP_EQ_F32=360/sdwa127 V_CNDMASK_B32=4863/sdwa38608 V_RCP_F32=5414/sdwa9771 | кандидат (тестируемый опкод: макс. 360 программ); проверить прогоном | I | new |
| VectorCompareF32DenormalModes | (по имени) Vector Compare F32 Denormal Modes | нет: нет на b3dc9c67: Greater, Less | V_CMP_EQ_F32=360/sdwa127 V_CMP_GE_F32=2524/sdwa637 V_CMP_LE_F32=2987/sdwa3242 V_CNDMASK_B32=4863/sdwa38608 | нет (не применим без кода) | c | new |
| VectorCompareClassF32ImmediateAndDynamicMasks | GPU: V_CMP_CLASS_F32 с непосредственной и динамической маской | да [I] | V_CMP_CLASS_F32=9/sdwa40 V_CNDMASK_B32=4863/sdwa38608 | да: VOPC:88 — 9 программ, SDWA 40 | I | new |
| VectorCmpClassF16 | (по имени) Vector Cmp Class F16 | нет: нет на b3dc9c67: V_CMP_CLASS_F16 | S_CMP_EQ_U32=4835 V_CMP_CLASS_F16=0 | нет (не применим без кода) | c | new |
| VectorCmpxClassF16 | (по имени) Vector Cmpx Class F16 | нет: нет на b3dc9c67: V_CMPX_CLASS_F16 | V_CMPX_CLASS_F16=0 | нет (не применим без кода) | c | new |
| VectorCompareI16U16Ops | (по имени) Vector Compare I16 U16 Ops | да [I] | V_CMP_EQ_I16=0 V_CMP_EQ_U16=0 V_CMP_GE_U16=0 V_CMP_GT_I16=0 V_CMP_GT_U16=0 V_CMP_LE_I16=0 V_CMP_LE_U16=0 V_CMP_NE_I16=0 … | нет: тестируемые опкоды = 0 в ophist | I | new |
| VectorVopcCmpxOrderedCapturedExecMask | (по имени) Vector Vopc Cmpx Ordered Captured Exec Mask | нет: нет на b3dc9c67: V_CMPX_O_F32 | V_CMPX_O_F32=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxLtI16CapturedSdwaExecMask | (по имени) Vector Vopc Cmpx Lt I16 Captured Sdwa Exec Mask | нет: нет на b3dc9c67: V_CMPX_LT_I16 | V_CMPX_LT_I16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxLtI16WaveMasks | (по имени) Vector Vopc Cmpx Lt I16 Wave Masks | нет: нет на b3dc9c67: V_CMPX_LT_I16 | V_CMPX_LT_I16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxU16SdwaCompactVop3ExecMask | (по имени) Vector Vopc Cmpx U16 Sdwa Compact Vop3 Exec Mask | нет: нет на b3dc9c67: V_CMPX_EQ_U16, V_CMPX_NE_U16 | V_CMPX_EQ_U16=0 V_CMPX_NE_U16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxEqU16SdwaCompactVop3ExecMask | (по имени) Vector Vopc Cmpx Eq U16 Sdwa Compact Vop3 Exec Mask | нет: нет на b3dc9c67: V_CMPX_EQ_U16, V_CMPX_NE_U16 | V_CMPX_EQ_U16=0 V_CMPX_NE_U16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxNeU16SdwaCompactVop3ExecMask | (по имени) Vector Vopc Cmpx Ne U16 Sdwa Compact Vop3 Exec Mask | нет: нет на b3dc9c67: V_CMPX_EQ_U16, V_CMPX_NE_U16 | V_CMPX_EQ_U16=0 V_CMPX_NE_U16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpNgtF16CapturedSdwaAndEdges | (по имени) Vector Vopc Cmp Ngt F16 Captured Sdwa And Edges | нет: нет на b3dc9c67: V_CMP_NGT_F16 | V_CMP_NGT_F16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpNltF16CapturedSdwaAndEdges | (по имени) Vector Vopc Cmp Nlt F16 Captured Sdwa And Edges | нет: нет на b3dc9c67: V_CMP_NLT_F16 | V_CMP_NLT_F16=0 | нет (не применим без кода) | c | new |
| VectorVopcCmpxNleF16CapturedSdwaExecMask | (по имени) Vector Vopc Cmpx Nle F16 Captured Sdwa Exec Mask | нет: нет на b3dc9c67: V_CMPX_NLE_F16 | V_CMPX_NLE_F16=0 | нет (не применим без кода) | c | new |
| SiblingSharedExitKeepsCapturedConditions | (по имени) Sibling Shared Exit Keeps Captured Conditions | да [I] | S_ADD_U32=1738 S_AND_B32=2994 S_BRANCH=5143 S_CBRANCH_SCC0=5112 S_CMP_EQ_U32=4835 | кандидат (опкоды: макс. 5143 программ); проверить прогоном | I | new |
| ScalarBranchRestoresInactiveLanes | (по имени) Scalar Branch Restores Inactive Lanes | да [I] | S_CBRANCH_EXECZ=3972 V_READLANE_B32=834 | кандидат (опкоды: макс. 3972 программ); проверить прогоном | I | new |
| ScalarMemRealtimeCapturedPlaceholder | (по имени) Scalar Mem Realtime Captured Placeholder | нет: нет на b3dc9c67: S_MEMREALTIME | S_MEMREALTIME=0 | нет (не применим без кода) | c | new |
| ScalarBufferOffsetAlignmentAndCarry | (по имени) Scalar Buffer Offset Alignment And Carry | да [I] | S_ADD_U32=1738 S_BUFFER_LOAD_DWORD=5451 | кандидат (тестируемый опкод: макс. 5451 программ); проверить прогоном | I | new |
| BufferOffsetsUsePackedWords | (по имени) Buffer Offsets Use Packed Words | частично: поля харнесса TestCase: .storage_buffer_range_bytes | - | после правки харнесса | I | new |
| BufferLoadShortD16Captured | (по имени) Buffer Load Short D16 Captured | нет: нет на b3dc9c67: BUFFER_LOAD_SHORT_D16, BUFFER_LOAD_SHORT_D16_HI; поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_LOAD_SHORT_D16=0 BUFFER_LOAD_SHORT_D16_HI=0 | нет (не применим без кода) | c | new |
| BufferSubwordLoadsAtHostOffset | (по имени) Buffer Subword Loads At Host Offset | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_LOAD_SBYTE=0 BUFFER_LOAD_SSHORT=0 BUFFER_LOAD_UBYTE=8 BUFFER_LOAD_USHORT=1 | после правки харнесса | I | new |
| BufferSubwordHostOffsetOverflow | (по имени) Buffer Subword Host Offset Overflow | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_LOAD_SBYTE=0 BUFFER_LOAD_SSHORT=0 BUFFER_LOAD_UBYTE=8 BUFFER_LOAD_USHORT=1 BUFFER_STORE_SHORT=0 | после правки харнесса | I | new |
| BufferSubwordStoresAtHostOffset | (по имени) Buffer Subword Stores At Host Offset | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_STORE_BYTE=0 BUFFER_STORE_SHORT=0 | после правки харнесса | I | new |
| BufferLoadsGpuSelectedDescriptors | (по имени) Buffer Loads Gpu Selected Descriptors | да [I] | BUFFER_LOAD_DWORDX2=62 BUFFER_LOAD_DWORDX3=1410 BUFFER_LOAD_DWORDX4=2639 S_BUFFER_LOAD_DWORDX4=5242 S_MUL_I32=1865 V_READFIRSTLANE_B32=1830 | кандидат (тестируемый опкод: макс. 5242 программ); проверить прогоном | I | new |
| BufferLoadDwordx3GpuSelectedDescriptors | (по имени) Buffer Load Dwordx3 Gpu Selected Descriptors | да [I] | BUFFER_LOAD_DWORDX2=62 BUFFER_LOAD_DWORDX3=1410 BUFFER_LOAD_DWORDX4=2639 S_BUFFER_LOAD_DWORDX4=5242 S_MUL_I32=1865 V_READFIRSTLANE_B32=1830 | кандидат (тестируемый опкод: макс. 1410 программ); проверить прогоном | I | new |
| BufferLoadDwordGpuSelectedDescriptors | (по имени) Buffer Load Dword Gpu Selected Descriptors | да [I] | BUFFER_LOAD_DWORDX2=62 BUFFER_LOAD_DWORDX3=1410 BUFFER_LOAD_DWORDX4=2639 S_BUFFER_LOAD_DWORDX4=5242 S_MUL_I32=1865 V_READFIRSTLANE_B32=1830 | кандидат (тестируемый опкод: макс. 5242 программ); проверить прогоном | I | new |
| BufferLoadFormatXGpuSelectedDescriptors | (по имени) Buffer Load Format XGpu Selected Descriptors | да [I] | BUFFER_LOAD_FORMAT_X=38 S_ADD_U32=1738 S_BUFFER_LOAD_DWORDX8=3902 S_CBRANCH_SCC1=2859 S_CMP_LT_U32=1793 S_LSHL_B32=2162 V_READFIRSTLANE_B32=1830 | кандидат (тестируемый опкод: макс. 38 программ); проверить прогоном | I | new |
| BufferLoadFormatXRejectsPartialRecord | (по имени) Buffer Load Format XRejects Partial Record | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_LOAD_FORMAT_X=38 | после правки харнесса | I | new |
| BufferStoreFormatXRejectsPartialRecord | (по имени) Buffer Store Format XRejects Partial Record | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_STORE_FORMAT_X=6 | после правки харнесса | I | new |
| BufferLoadFormatXyRejectsPartialRecord | (по имени) Buffer Load Format Xy Rejects Partial Record | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_LOAD_FORMAT_XY=1106 | после правки харнесса | I | new |
| BufferStoreFormatXyRejectsPartialRecord | (по имени) Buffer Store Format Xy Rejects Partial Record | частично: поля харнесса TestCase: .storage_buffer_range_bytes | BUFFER_STORE_FORMAT_XY=2 | после правки харнесса | I | new |
| BufferStoreFormatXyzwPackedUnormSkinningVectors | (по имени) Buffer Store Format Xyzw Packed Unorm Skinning Vectors | да [I] | BUFFER_STORE_FORMAT_XYZW=2 | кандидат (тестируемый опкод: макс. 2 программ); проверить прогоном | I | new |
| BufferStoreFormatXZeroFillsPackedRecord | (по имени) Buffer Store Format XZero Fills Packed Record | да [I] | BUFFER_STORE_FORMAT_X=6 | кандидат (тестируемый опкод: макс. 6 программ); проверить прогоном | I | new |
| BufferStoreFormatXyzwFloat16ConvertsComponents | (по имени) Buffer Store Format Xyzw Float16 Converts Components | да [I] | BUFFER_STORE_FORMAT_XYZW=2 | кандидат (тестируемый опкод: макс. 2 программ); проверить прогоном | I | new |
| BufferStoreFormatXyzwSnorm16CapturedSkinningVectors | (по имени) Buffer Store Format Xyzw Snorm16 Captured Skinning Vectors | да [I] | BUFFER_STORE_FORMAT_XYZW=2 | кандидат (тестируемый опкод: макс. 2 программ); проверить прогоном | I | new |
| BufferStoreFormatXSnorm16ClampsRoundsAndPreservesHalfwords | (по имени) Buffer Store Format XSnorm16 Clamps Rounds And Preserves Halfwords | да [I] | BUFFER_STORE_FORMAT_X=6 | кандидат (тестируемый опкод: макс. 6 программ); проверить прогоном | I | new |
| BufferLoadFormatD16XCases | (по имени) Buffer Load Format D16 XCases | нет: нет на b3dc9c67: BUFFER_LOAD_FORMAT_D16_X | BUFFER_LOAD_FORMAT_D16_X=0 | нет (не применим без кода) | c | new |
| BufferStoreFormatD16XCases | (по имени) Buffer Store Format D16 XCases | нет: нет на b3dc9c67: BUFFER_STORE_FORMAT_D16_X | BUFFER_STORE_FORMAT_D16_X=0 | нет (не применим без кода) | c | new |
| FormattedStoreConversionCases | (по имени) Formatted Store Conversion Cases | да [I] | BUFFER_STORE_FORMAT_X=6 BUFFER_STORE_FORMAT_XY=2 BUFFER_STORE_FORMAT_XYZ=8 BUFFER_STORE_FORMAT_XYZW=2 TBUFFER_STORE_FORMAT_X=0 TBUFFER_STORE_FORMAT_XY=0 TBUFFER_STORE_FORMAT_XYZ=0 TBUFFER_STORE_FORMAT_XYZW=0 | кандидат (тестируемый опкод: макс. 8 программ); проверить прогоном | I | new |
| TBufferCapturedZeroStrideOob | (по имени) TBuffer Captured Zero Stride Oob | частично: поля харнесса TestCase: .expected_buffer_resources | S_BUFFER_LOAD_DWORD=5451 TBUFFER_LOAD_FORMAT_XYZW=24 | после правки харнесса | I | new |
| BufferZeroStrideOobFormatsAndWidths | (по имени) Buffer Zero Stride Oob Formats And Widths | частично: поля харнесса TestCase: .expected_buffer_resources | BUFFER_LOAD_DWORDX2=62 BUFFER_LOAD_DWORDX3=1410 BUFFER_LOAD_FORMAT_X=38 BUFFER_LOAD_FORMAT_XYZW=1094 BUFFER_LOAD_UBYTE=8 BUFFER_LOAD_USHORT=1 | после правки харнесса | I | new |
| FlatLoadDlcCaptured | (по имени) Flat Load Dlc Captured | нет: нет на b3dc9c67: S_WAITCNT_VSCNT | FLAT_LOAD_DWORDX2=2 S_WAITCNT_VSCNT=9 | нет (не применим без кода) | c | new |
| FlatStoreSlcCaptured | (по имени) Flat Store Slc Captured | да [I] | FLAT_LOAD_DWORD=2 FLAT_STORE_DWORD=0 S_BREV_B32=6 V_MED3_U32=715 V_MIN_U32=8 | нет: тестируемые опкоды = 0 в ophist | I | new |
| GlobalLoadShortD16Captured | (по имени) Global Load Short D16 Captured | нет: нет на b3dc9c67: FLAT_LOAD_SHORT_D16 | FLAT_LOAD_SHORT_D16=0 | нет (не применим без кода) | c | new |
| FlatLoadShortD16AddressSegments | (по имени) Flat Load Short D16 Address Segments | нет: нет на b3dc9c67: FLAT_LOAD_SHORT_D16 | FLAT_LOAD_SHORT_D16=0 FLAT_STORE_DWORD=0 | нет (не применим без кода) | c | new |
| ScalarLoadAlignsDynamicBase | (по имени) Scalar Load Aligns Dynamic Base | да [I] | S_ADD_U32=1738 S_LOAD_DWORDX2=689 | кандидат (тестируемый опкод: макс. 689 программ); проверить прогоном | I | new |
| ScalarBufferFromLoopReadlane | (по имени) Scalar Buffer From Loop Readlane | да [I] | S_ADD_U32=1738 S_BUFFER_LOAD_DWORDX4=5242 S_CBRANCH_SCC1=2859 S_CMP_LT_U32=1793 S_LOAD_DWORDX8=4616 V_READLANE_B32=834 | кандидат (тестируемый опкод: макс. 5242 программ); проверить прогоном | I | new |
| DsWriteB8D16HiWritesByteTwo | (по имени) Ds Write B8 D16 Hi Writes Byte Two | нет: нет на b3dc9c67: DS_WRITE_B8_D16_HI | DS_READ_B32=60 DS_WRITE_B32=60 DS_WRITE_B8_D16_HI=0 | нет (не применим без кода) | c | new |
| DsMaskedOrBounds | (по имени) Ds Masked Or Bounds | нет: нет на b3dc9c67: DS_MSKOR_B32 | DS_MSKOR_B32=0 DS_READ_B32=60 DS_WRITE_B32=60 | нет (не применим без кода) | c | new |
| DsMaskedOrContention | (по имени) Ds Masked Or Contention | нет: нет на b3dc9c67: DS_MSKOR_B32 | DS_MSKOR_B32=0 DS_READ_B32=60 DS_WRITE_B32=60 S_BARRIER=66 V_CMP_EQ_U32=1939/sdwa2826 | нет (не применим без кода) | c | new |
| DsAtomic64Bounds | (по имени) Ds Atomic64 Bounds | нет: нет на b3dc9c67: DS_ADD_U64, DS_OR_B64 | DS_ADD_U64=0 DS_OR_B64=0 DS_READ_B32=60 DS_WRITE_B32=60 | нет (не применим без кода) | c | new |
| DsAtomic64Contention | (по имени) Ds Atomic64 Contention | нет: нет на b3dc9c67: DS_ADD_U64, DS_OR_B64 | DS_ADD_U64=0 DS_OR_B64=0 DS_READ_B32=60 DS_WRITE_B32=60 S_BARRIER=66 V_CMP_EQ_U32=1939/sdwa2826 | нет (не применим без кода) | c | new |
| DsFloatMinMaxIgnoresData1 | (по имени) Ds Float Min Max Ignores Data1 | да [I] | DS_MAX_F32=1 DS_MIN_F32=1 DS_READ_B32=60 DS_WRITE_B32=60 | кандидат (тестируемый опкод: макс. 1 программ); проверить прогоном | I | new |
| DsFloatMinMaxClasses | (по имени) Ds Float Min Max Classes | да [I] | BUFFER_LOAD_DWORDX2=62 BUFFER_STORE_DWORDX2=251 DS_MAX_F32=1 DS_MIN_F32=1 DS_READ_B32=60 DS_WRITE_B32=60 | кандидат (тестируемый опкод: макс. 1 программ); проверить прогоном | I | new |
| DsPermuteCapturedExecOffsetAndWrap | (по имени) Ds Permute Captured Exec Offset And Wrap | нет: нет на b3dc9c67: DS_PERMUTE_B32 | DS_PERMUTE_B32=0 V_AND_B32=4429/sdwa92 V_CMP_EQ_U32=1939/sdwa2826 | нет (не применим без кода) | c | new |
| DsPermuteWave64UsesIndependentHalves | (по имени) Ds Permute Wave64 Uses Independent Halves | нет: нет на b3dc9c67: DS_PERMUTE_B32 | DS_PERMUTE_B32=0 V_XOR_B32=15/sdwa4 | нет (не применим без кода) | c | new |
| CheckWave64WholeWaveResults | (по имени) Check Wave64 Whole Wave Results | да [I] | DS_READ_B32=60 DS_WRITE_B32=60 S_BARRIER=66 V_AND_B32=4429/sdwa92 V_CMP_EQ_U32=1939/sdwa2826 V_READFIRSTLANE_B32=1830 V_READLANE_B32=834 V_XOR_B32=15/sdwa4 | кандидат (опкоды: макс. 4429 программ); проверить прогоном | I | new |
| BufferWorkgroupPublication | (по имени) Buffer Workgroup Publication | нет: нет на b3dc9c67: S_WAITCNT_VSCNT | BUFFER_ATOMIC_ADD=1 S_ADD_U32=1738 S_CBRANCH_SCC1=2859 S_CMP_EQ_U32=4835 S_CMP_LG_U32=5022 S_CMP_LT_U32=1793 S_LSHL_B64=20 S_WAITCNT_VSCNT=9 … | нет (не применим без кода) | c | new |
| BufferAtomicAndX2GlcAndExec | (по имени) Buffer Atomic And X2 Glc And Exec | нет: нет на b3dc9c67: BUFFER_ATOMIC_AND_X2 | BUFFER_ATOMIC_AND_X2=0 | нет (не применим без кода) | c | new |
| DsAppendAllocatesAcrossWaves | (по имени) Ds Append Allocates Across Waves | да [I] | BUFFER_ATOMIC_ADD=1 DS_APPEND=239 DS_READ_B32=60 DS_WRITE_B32=60 S_BARRIER=66 V_CMP_EQ_U32=1939/sdwa2826 | кандидат (тестируемый опкод: макс. 239 программ); проверить прогоном | I | new |
| DsOrderedCountAddressAndExec | (по имени) Ds Ordered Count Address And Exec | нет: нет на b3dc9c67: DS_ORDERED_COUNT | DS_ORDERED_COUNT=0 | нет (не применим без кода) | c | new |
| DsAppendConsumeGdsRegionBounds | (по имени) Ds Append Consume Gds Region Bounds | да [I] | DS_APPEND=239 DS_CONSUME=3 | кандидат (тестируемый опкод: макс. 239 программ); проверить прогоном | I | new |
| ImageSamplePacked8 | (по имени) Image Sample Packed8 | частично: поля харнесса TestCase: .expected_float_tolerance, .sampler_filter | IMAGE_GATHER4_LZ=30 | после правки харнесса | I | new |
| ImageCubeGradientsPreserveDerivatives | (по имени) Image Cube Gradients Preserve Derivatives | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| ImageGatherExplicitLod | (по имени) Image Gather Explicit Lod | нет: нет на b3dc9c67: IMAGE_GATHER4_L; поля харнесса TestCase: .expected_mip_descriptors | IMAGE_GATHER4_L=0 | нет (не применим без кода) | c | new |
| ImageGatherLodPerLane | (по имени) Image Gather Lod Per Lane | нет: нет на b3dc9c67: IMAGE_GATHER4_L; поля харнесса TestCase: .expected_mip_descriptors, .sampled_image_view_base_mip | IMAGE_GATHER4_L=0 | нет (не применим без кода) | c | new |
| ImageSampleOffsetsReadFourNeighbors | (по имени) Image Sample Offsets Read Four Neighbors | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckComputeThreadDimensions | (по имени) Check Compute Thread Dimensions | частично: поля харнесса TestCase: .expected_float_tolerance | BUFFER_ATOMIC_ADD=1 S_AND_B64=3343 | после правки харнесса | I | new |
| CheckRuntimeBufferRecords | (по имени) Check Runtime Buffer Records | частично: поля харнесса TestCase: .expected_float_tolerance | - | после правки харнесса | I | new |
| CheckIndirectBufferStore | (по имени) Check Indirect Buffer Store | нет: нет на b3dc9c67: .descriptor_counts, .descriptor_index, .indirect_descriptor, .table_stride, IndirectDescriptor, NoIndirectBuffer, descriptor_counts, descriptor_index …; поля харнесса TestCase: .expected_float_tolerance, .storage_buffer_range_bytes | - | нет (не применим без кода) | c | new |
| CheckFiniteInlineSamplerPhi | (по имени) Check Finite Inline Sampler Phi | нет: нет на b3dc9c67: .integer_border, .snapshot_index, integer_border, snapshot_index; поля харнесса TestCase: .CreateSampler, .expected_float_tolerance | S_BFM_B32=3449 S_CBRANCH_EXECZ=3972 V_CMPX_GT_U32=102/sdwa2 V_CMPX_NE_U32=812/sdwa7 | нет (не применим без кода) | c | new |
| ImageStoreSingleMipBounds | (по имени) Image Store Single Mip Bounds | частично: поля харнесса TestCase: .expected_mip_descriptors | - | после правки харнесса | I | new |
| ImageAtomicCompareSwapGlcAndExec | (по имени) Image Atomic Compare Swap Glc And Exec | нет: нет на b3dc9c67: IMAGE_ATOMIC_CMPSWAP | IMAGE_ATOMIC_CMPSWAP=0 | нет (не применим без кода) | c | new |
| ImageAtomicIntegerGlcAndExec | (по имени) Image Atomic Integer Glc And Exec | да [I] | IMAGE_ATOMIC_AND=0 IMAGE_ATOMIC_UMIN=0 | нет: тестируемые опкоды = 0 в ophist | I | new |
| ImageAtomicSignedMinMax | (по имени) Image Atomic Signed Min Max | нет: нет на b3dc9c67: IMAGE_ATOMIC_SMAX, IMAGE_ATOMIC_SMIN | IMAGE_ATOMIC_SMAX=0 IMAGE_ATOMIC_SMIN=0 | нет (не применим без кода) | c | new |
| ImageAtomicFloatGlcAndExec | (по имени) Image Atomic Float Glc And Exec | нет: нет на b3dc9c67: IMAGE_ATOMIC_FMAX, IMAGE_ATOMIC_FMIN | IMAGE_ATOMIC_FMAX=0 IMAGE_ATOMIC_FMIN=0 | нет (не применим без кода) | c | new |
| ImageAtomicFloatSpecialValues | (по имени) Image Atomic Float Special Values | нет: нет на b3dc9c67: IMAGE_ATOMIC_FMAX, IMAGE_ATOMIC_FMIN | IMAGE_ATOMIC_FMAX=0 IMAGE_ATOMIC_FMIN=0 | нет (не применим без кода) | c | new |
| ImageAtomicFloatContendedWorkgroup | (по имени) Image Atomic Float Contended Workgroup | нет: нет на b3dc9c67: IMAGE_ATOMIC_FMAX, IMAGE_ATOMIC_FMIN | IMAGE_ATOMIC_FMAX=0 IMAGE_ATOMIC_FMIN=0 V_CVT_F32_U32=3369/sdwa21783 | нет (не применим без кода) | c | new |
| GraphicsPackedHalfCentroid | (по имени) Graphics Packed Half Centroid | нет: нет на b3dc9c67: .pixel_custom_interpolation_mask, .pixel_perspective_centroid_vgpr | V_FMA_F32=2945 V_MAC_F32=5532 | нет (не применим без кода) | c | new |
| GraphicsPerspectiveSample | (по имени) Graphics Perspective Sample | нет: нет на b3dc9c67: .pixel_perspective_sample_vgpr | V_MUL_F32=5579/sdwa123148 | нет (не применим без кода) | c | new |
| GraphicsPackedHalfInputAlias | (по имени) Graphics Packed Half Input Alias | нет: нет на b3dc9c67: .pixel_custom_interpolation_mask, .pixel_perspective_centroid_vgpr | V_FMA_F32=2945 V_MAC_F32=5532 | нет (не применим без кода) | c | new |
| GraphicsSmoothRawInputAlias | (по имени) Graphics Smooth Raw Input Alias | нет: нет на b3dc9c67: .pixel_custom_interpolation_mask, .pixel_perspective_centroid_vgpr | V_FMA_F32=2945 V_MAC_F32=5532 | нет (не применим без кода) | c | new |
| GraphicsSmoothFlatInputAlias | (по имени) Graphics Smooth Flat Input Alias | нет: нет на b3dc9c67: .pixel_custom_interpolation_mask, .pixel_perspective_centroid_vgpr, smooth | V_AND_B32=4429/sdwa92 V_CVT_F32_U32=3369/sdwa21783 V_FMA_F32=2945 V_MAC_F32=5532 | нет (не применим без кода) | c | new |
| CheckComputeLdsLimit | (по имени) Check Compute Lds Limit | нет: нет на b3dc9c67: lds_storage; поля харнесса TestCase: .lds_storage | - | нет (не применим без кода) | c | new |
| CheckResourcePlanHandoff | (по имени) Check Resource Plan Handoff | нет: нет на b3dc9c67: .descriptor_counts, descriptor_counts | - | нет (не применим без кода) | c | new |
| CheckDepthFeedbackAspects | (по имени) Check Depth Feedback Aspects | нет: нет на b3dc9c67: DepthFeedbackAspects | - | нет (не применим без кода) | c | new |
| CheckPm4Predication | PM4: предикация | да [I] | - | условно: PM4 — путь игры; проверить прогоном | I | new |
| CheckPm4IndirectShaderRegisters | (по имени) Check Pm4 Indirect Shader Registers | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckPm4IndirectUconfigRegisters | (по имени) Check Pm4 Indirect Uconfig Registers | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckShaderFusion | слияние шейдеров (fused stages) | да [I] | - | условно; проверить прогоном | I | new |
| CheckAgcSystemTable | (по имени) Check Agc System Table | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckPm4WaitPackets | (по имени) Check Pm4 Wait Packets | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckPm4DrawIndirectMultiPacket | (по имени) Check Pm4 Draw Indirect Multi Packet | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| CheckPm4IndirectControlFlow | (по имени) Check Pm4 Indirect Control Flow | нет: нет на b3dc9c67: AgcBranchPatchSetThenTarget, AgcCbBranchGetSize, AgcDcbSetCxRegistersIndirectGetSize, AgcSetNop | - | нет (не применим без кода) | c | new |

### 4.2 `ResourceTrackingTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestBoundedImageViewEligibility | (по имени) Test Bounded Image View Eligibility | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .watched_address, .watched_dwords, .watched_reads, indirect_descriptor, table_offset, table_stride | - | нет (не применим без кода) | c | new |
| TestWaterfallImageTable | (по имени) Test Waterfall Image Table | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .table_record_bytes, .watched_address, .watched_dwords, .watched_reads, indirect_descriptor, table_record_bytes | - | нет (не применим без кода) | c | new |
| TestGuardedDirectImageTable | (по имени) Test Guarded Direct Image Table | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .table_offset, .table_source, .watched_address, .watched_dwords, .watched_reads, ConditionRef … | - | нет (не применим без кода) | c | new |
| TestBoundedComputeImageLoop | (по имени) Test Bounded Compute Image Loop | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .table_offset, .watched_address, .watched_dwords, .watched_reads, ConditionRef, active_phi … | - | нет (не применим без кода) | c | new |
| TestUniformizedMaterialImageKeys | (по имени) Test Uniformized Material Image Keys | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .selector_mask, .table_offset, .watched_address, .watched_dwords, .watched_reads, ConditionRef … | - | нет (не применим без кода) | c | new |
| TestImageDescriptorFields | (по имени) Test Image Descriptor Fields | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| TestUniformScalarBufferImage | (по имени) Test Uniform Scalar Buffer Image | нет: нет на b3dc9c67: .descriptor_reads, .indirect_descriptor, .watched_address, .watched_dwords, .watched_reads, indirect_descriptor | - | нет (не применим без кода) | c | new |
| TestGatherLodSamplerValidation | (по имени) Test Gather Lod Sampler Validation | нет: нет на b3dc9c67: .gather_lod, gather_lod | - | нет (не применим без кода) | c | new |
| TestWritableDescriptorPhi | (по имени) Test Writable Descriptor Phi | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| ConditionalSamplerPlan | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestConditionalSamplerPhi | (по имени) Test Conditional Sampler Phi | нет: нет на b3dc9c67: .EvaluateDescriptor, .descriptor_reads, .watched_address, .watched_dwords, .watched_reads, CleanRuntime, EvaluateDescriptor | - | нет (не применим без кода) | c | new |
| TestFiniteImagePhiCycle | (по имени) Test Finite Image Phi Cycle | нет: нет на b3dc9c67: .EvaluateDescriptor, .indirect_descriptor, EvaluateDescriptor, indirect_descriptor | - | нет (не применим без кода) | c | new |
| TestFiniteInlineSampler | (по имени) Test Finite Inline Sampler | нет: нет на b3dc9c67: .indirect_descriptor, .integer_border, .snapshot_index, indirect_descriptor, integer_border, snapshot_index | - | нет (не применим без кода) | c | new |
| TestFiniteImageBitScanSentinel | (по имени) Test Finite Image Bit Scan Sentinel | нет: нет на b3dc9c67: .indirect_descriptor, indirect_descriptor | - | нет (не применим без кода) | c | new |
| TestBufferStoreUsesItsOwnActiveValue | (по имени) Test Buffer Store Uses Its Own Active Value | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| TestBoundedRelativeRegisterWrites | (по имени) Test Bounded Relative Register Writes | нет: нет на b3dc9c67: .EvaluateDescriptor, ConditionRef, EvaluateDescriptor | - | нет (не применим без кода) | c | new |
| TestGuardedScalarDescriptorReads | (по имени) Test Guarded Scalar Descriptor Reads | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .descriptor_reads, .null_reads, .watched_address, .watched_dwords, .watched_reads | - | нет (не применим без кода) | I | new |
| TestShaderInfoCollection | (по имени) Test Shader Info Collection | нет: нет на b3dc9c67: .live_buffers, .uses_lds, live_buffers, uses_lds | - | нет (не применим без кода) | c | new |
| TestLiveShaderDataCollection | (по имени) Test Live Shader Data Collection | нет: нет на b3dc9c67: .uses_dispatch_threads, GetDispatchThreadExtent, uses_dispatch_threads | - | нет (не применим без кода) | c | new |

### 4.3 `ResourceMaterializationTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| SrtProgram | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| MixedSamplerProgram | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestNativeNestedSrtRefresh | (по имени) Test Native Nested Srt Refresh | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .RefreshFlatBuffer, .srt_code, RefreshFlatBuffer, srt_code | - | нет (не применим без кода) | I | new |
| TestSrtAliasesRetainReadPolicy | (по имени) Test Srt Aliases Retain Read Policy | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .EvaluateDescriptor, .RefreshFlatBuffer, .indirect_descriptor, .srt_code, CleanRuntime, EvaluateDescriptor, IndirectDescriptor, RefreshFlatBuffer … | - | нет (не применим без кода) | I | new |
| TestUniformVectorDescriptorRead | (по имени) Test Uniform Vector Descriptor Read | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .capture_specialization_reads, capture_specialization_reads | - | нет (не применим без кода) | I | new |
| TestExactReciprocalDescriptorArithmetic | (по имени) Test Exact Reciprocal Descriptor Arithmetic | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| TestWrittenDescriptorPredicateReads | (по имени) Test Written Descriptor Predicate Reads | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .capture_specialization_reads, capture_specialization_reads | - | нет (не применим без кода) | I | new |
| TestFailedMaterializationRejectsStage | (по имени) Test Failed Materialization Rejects Stage | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| TestSharedControlPredicates | (по имени) Test Shared Control Predicates | нет: нет на b3dc9c67: .RefreshFlatBuffer, .capture_specialization_reads, .visited_blocks, ConditionRef, RefreshFlatBuffer, capture_specialization_reads, visited_blocks | - | нет (не применим без кода) | c | new |
| TestFiniteImageRefreshReusesScalarReads | (по имени) Test Finite Image Refresh Reuses Scalar Reads | нет: читатель SrtMemoryReader с std::span (у нас uint32_t*); нет на b3dc9c67: .indirect_descriptor, IndirectDescriptor, indirect_descriptor | - | нет (не применим без кода) | I | new |
| TestMixedSamplerVariantsShareRuntimeDescriptor | (по имени) Test Mixed Sampler Variants Share Runtime Descriptor | нет: нет на b3dc9c67: .snapshot_index, snapshot_index | - | нет (не применим без кода) | c | new |

### 4.4 `ScalarProvenanceTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| LoadBuffer | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestOperandMutationLifecycle | (по имени) Test Operand Mutation Lifecycle | да [I] | - | условно (общий путь); проверить прогоном | I | new |
| TestFloatComparisonDescriptorInputs | (по имени) Test Float Comparison Descriptor Inputs | нет: нет на b3dc9c67: .EvaluateDescriptor, .greater_equal, .less_equal, EvaluateDescriptor, FPCompareFlags | - | нет (не применим без кода) | c | new |
| TestDeadPhiCyclesAndPlanningRoots | (по имени) Test Dead Phi Cycles And Planning Roots | да [I] | - | условно (общий путь); проверить прогоном | I | new |

### 4.5 `MemoryTrackerTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| AllocateFixedGuestRange | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestCleanUploadPreservesOwnership | memory tracker: чистая загрузка сохраняет владение регионом | да [I] | - | кандидат с оговоркой: memoryTracker.cpp несёт KYTY_FIX_B13 (Б13, FIXED) — провал разбирать против реестра §77–80 | I | new |
| BenchmarkCleanUploads | memory tracker: замер скорости чистых загрузок | да [I] | - | нет: только скорость (класс Д) | I | new |
| TestConcurrentColdUploads | memory tracker: параллельные холодные загрузки | да [I] | - | кандидат с оговоркой (как выше, Б12/Б13) | I | new |

### 4.6 `PageManagerTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestConcurrentSharedWatchers | page manager: общие наблюдатели страниц из нескольких потоков | да [I] | - | кандидат: защита страниц — путь отслеживания памяти игры (pageManager.cpp с местом вызова KYTY_FIX_B36); проверить прогоном | I | new |

### 4.7 `KernelFileSystemTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestRandomDevices | /dev/urandom, /dev/random — символьные устройства, чтение энтропии | да [I] | - | условно: KernelOpen/Read (fileSystem.cpp, наши KYTY_FIX_B4/F25); обращение игры к /dev/random не установлено | U | new |
| TestFileDescriptorFlags | fcntl F_GETFD/F_SETFD, EBADF/EINVAL | нет (NID 8nY19bKoiZk нет на b3dc9c67) | - | нет: NID fcntl 8nY19bKoiZk не зарегистрирован у нас — символ не найдётся | c | new |
| TestSysmoduleReferences | Sysmodule load/unload/is_loaded: счётчики ссылок, независимые модули | да [I] | - | кандидат: libSceSysmodule игра импортирует; проверить прогоном | I | new |
| TestSystemServiceEntitlementEvents | AppContentUtil init и события SystemService (entitlement) | да [I] | - | условно: AppContentUtil импортируется; событие entitlement в игре не установлено | U | new |
| TestSaveOpenVisibility | /savedata0: созданный файл виден до close, O_EXCL ловит открытый файл, O_TRUNC обнуляет | да [I] | - | кандидат: путь сохранений игры (libSceSaveData импортируется), fileSystem.cpp с KYTY_FIX_B4/F25 — проверить прогоном | I | new |
| TestAioBatches | AIO: пакетная отправка, ожидание, отмена | нет (3 NID AIO нет) | - | нет: NID Ft3EtsZzAoY, o7O4z3jwKzo, lgK+oIWkJyA нет на b3dc9c67 | c | new |
| TestNpCommerceDialog | диалог NpCommerce | нет (2 NID нет) | - | нет: NID r42bWcQbtZY, DfSCDRA3EjY нет | c | new |
| TestNpWebApi2Memory | NpWebApi2: пулы памяти и статистика | нет (NID Xweb+naPZ8Y нет) | - | нет: NID Xweb+naPZ8Y нет | c | new |
| CheckUnmappedPaths | файлы хоста вне смонтированных точек не видны гостю (open/stat/unlink/rmdir дают ENOENT) | да [I] | - | условно (изоляция пространства имён) | I | new |
| CheckArchiveMount | (по имени) Check Archive Mount | нет: нет на b3dc9c67: MakeArchivePath, archive | - | нет (не применим без кода) | c | new |
| CheckUnicodePaths | (по имени) Check Unicode Paths | нет: нет на b3dc9c67: PathFromUtf8 | - | нет (не применим без кода) | c | new |
| CheckUnicodeLogPath | лог эмулятора в путь с Unicode | да [I] | - | нет: хостовая функция лога (у нас LogAsync KYTY_FIX_B36), к игре не относится | I | new |
| CheckAmprOrdering | libSceAmpr: порядок команд APR/AMPR | да [I] | - | кандидат: libSceAmpr игра импортирует; все NID есть у нас; проверить прогоном | I | new |
| CreateTcpPair | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| CheckSocketReceiveConcurrency | сокеты: параллельный приём | да [I] | - | нет как гейт: сетевой путь (у игры часть Net — заглушки PLT) | U | new |
| CheckSocketReceiveBuffer | сокеты: буфер приёма | да [I] | - | нет как гейт (как выше) | U | new |
| RecordNetCtlEvent | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestNetCtlHostIpv4 | NetCtl: IPv4 хоста через getifaddrs | нет (POSIX getifaddrs) | - | нет: getifaddrs/ifaddrs (POSIX) — не Windows | c | new |
| CheckEtherAddressFormatting | sceNetEtherNtostr: формат MAC | да [I] | - | нет как гейт: к картинке и уровням не относится | I | new |

### 4.8 `VirtualMemoryAllocationTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestSparseBackingReadPreservesResidency | (по имени) Test Sparse Backing Read Preserves Residency | нет: нет на b3dc9c67: kExtendedMemoryBase, kExtendedMemorySize | - | нет (не применим без кода) | c | new |
| TestSparseReadDuringDirectCommit | (по имени) Test Sparse Read During Direct Commit | нет: нет на b3dc9c67: TestFailNextVirtualRangeReplacement | - | нет (не применим без кода) | c | new |
| ParkBackingRead | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestConcurrentBackingReads | (по имени) Test Concurrent Backing Reads | нет: нет на b3dc9c67: TestSetBackingReadCallback | - | нет (не применим без кода) | c | new |
| TestBackingReadExcludesWritesAndUnmap | (по имени) Test Backing Read Excludes Writes And Unmap | нет: нет на b3dc9c67: TestSetBackingReadCallback | - | нет (не применим без кода) | c | new |
| TestWindowsBackingViewPermissions | (по имени) Test Windows Backing View Permissions | нет: нет на b3dc9c67: TestWindowsBackingViewModes | - | нет (не применим без кода) | c | new |
| TestDirectMappingNamesTypesAndValidation | ядро: именованные отображения прямой памяти, типы, проверки аргументов | да [I] | - | кандидат: прямая память — путь игры (libkernel); проверить прогоном | I | new |
| TestBatchMappingOperationsAndPartialFailure | ядро: KernelBatchMap, частичный отказ | да [I] | - | кандидат (вызов игрой BatchMap не установлен — U); проверить прогоном | U | new |
| TestFixedDirectReplacementPreservesAccess | (по имени) Test Fixed Direct Replacement Preserves Access | нет: нет на b3dc9c67: TestBeforeNextBackingMap, TestFailNextVirtualRangeReplacement | - | нет (не применим без кода) | c | new |
| TestExtendedAndUserMappingsDoNotAlias | (по имени) Test Extended And User Mappings Do Not Alias | нет: нет на b3dc9c67: kExtendedMemoryBase, kExtendedMemorySize | - | нет (не применим без кода) | c | new |
| TestAutomaticMemoryReuseAndAliases | (по имени) Test Automatic Memory Reuse And Aliases | нет: нет на b3dc9c67: AllocateDirectMemory, MapAutomaticMemory, kExtendedMemoryBase | - | нет (не применим без кода) | c | new |
| TestAutomaticMemoryFragmentedMapRollback | (по имени) Test Automatic Memory Fragmented Map Rollback | нет: нет на b3dc9c67: AllocateDirectMemory, MapAutomaticMemory, kExtendedMemoryBase | - | нет (не применим без кода) | c | new |
| EmulateInstructionContext | вспомогательная функция теста | нет: нет на b3dc9c67: _mm_getcsr, _mm_setcsr | - | помощник: переносится вместе с тестом, сам не тест | c | new |
| InstructionHandler | вспомогательная функция теста | нет: нет на b3dc9c67: _mm_getcsr, _mm_setcsr | - | помощник: переносится вместе с тестом, сам не тест | c | new |
| TestCpuExtensionContexts | (по имени) Test Cpu Extension Contexts | нет: нет на b3dc9c67: .Gpr, .Xmm, Gpr, Xmm, _mm_getcsr, _mm_setcsr | - | нет (не применим без кода) | c | new |
| TestPackedReciprocalSquareRoot | (по имени) Test Packed Reciprocal Square Root | нет: нет на b3dc9c67: .mxcsr, .reciprocal_sqrt, .stc, .vmovups, .vrsqrtps, .vzeroupper, .ymm1, GetError … | - | нет (не применим без кода) | c | new |
| TestPackedBitField | (по имени) Test Packed Bit Field | нет: нет на b3dc9c67: .Skipped, .extrq, .gprs, .insertq, .mxcsr, .reciprocal_sqrt, .stack_after, .stack_before … | - | нет (не применим без кода) | c | new |
| TestPackedBitFieldExtract | (по имени) Test Packed Bit Field Extract | нет: нет на b3dc9c67: .Skipped, .extrq, .gprs, .insertq, .mxcsr, .reciprocal_sqrt, .stack_after, .stack_before … | - | нет (не применим без кода) | c | new |
| TestPackedBitFieldInsert | (по имени) Test Packed Bit Field Insert | нет: нет на b3dc9c67: .Skipped, .extrq, .gprs, .insertq, .mxcsr, .reciprocal_sqrt, .stack_after, .stack_before … | - | нет (не применим без кода) | c | new |
| TestCpuExtensionPatches | (по имени) Test Cpu Extension Patches | нет: нет на b3dc9c67: .clwb, .insertq, .rdpid, .sse4a, .vmovups, .vzeroupper, .ymm8, .ymm9 … | - | нет (не применим без кода) | c | new |
| TestSmallFiberStacksAndMigration | Fiber: малые стеки, миграция между потоками | да [I] | - | кандидат: libSceFiber игра импортирует; проверить прогоном | I | new |

### 4.9 `AudioOut2PortTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| CreatePort | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestUserSupportedAttributes | AudioOut2: UserCreate/GetSupportedAttributes/UserDestroy | нет: нет на b3dc9c67: AudioOut2UserGetSupportedAttributes, port_attributes | - | нет: AudioOut2UserGetSupportedAttributes нет на b3dc9c67 | c | new |
| SetAttribute | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| CaptureOutputPcm | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| OutputPcm | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| PushPcm | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| CheckSamples | вспомогательная функция теста | да [I] | - | помощник: переносится вместе с тестом, сам не тест | I | new |
| TestPcmCopiedBeforeScratchBufferReuse | AudioOut2: два порта с общим буфером — PCM копируется в момент set, а не при push | частично (заглушка вывода в форме upstream пишет OutputParam::gains — у нас поля нет) | - | проба (upstream 313b60e92, #826): нужна заглушка AudioOutOutputs, пишущая PCM (правка теста без поля gains); libSceAudioOut2 игра импортирует | U | new |
| TestPortGainAndValidation | AudioOut2: усиление порта передаётся в вывод, проверка параметров | нет (OutputParam::gains нет на b3dc9c67) | - | нет: проверяет OutputParam::gains (нет на b3dc9c67) | c | new |
| TestObjectGainAndAmbisonics | AudioOut2: объектные порты, усиление, амбисоника | частично (заглушка вывода upstream) | - | проба (upstream c86c8b4d9 — микширование объектов): у нас микширования объектов нет [I] — ожидаем провал | U | new |
| TestObjectBusRouting | AudioOut2: маршрутизация объектов по шинам контекста | частично (заглушка вывода upstream) | - | проба (как выше) | U | new |

### 4.10 `EventQueueLifetimeTests.cpp` — новые функции upstream

| тест-функция | что проверяет | применим без кода | опкоды (программ ASTRO BOT / SDWA) | кандидат гейта | ув. | статус |
|---|---|---|---|---|---|---|
| TestLevelUserEventDelivery | event queue: пользовательские события по уровню | да [I] | - | условно (общий путь ядра) | I | new |
| TestPeriodicTimerEvents | event queue: периодический таймер | нет: нет на b3dc9c67: KernelAddTimerEvent | - | нет: KernelAddTimerEvent нет на b3dc9c67 | c | new |

### 4.11 Прочие изменённые файлы без новых функций

| файл | что изменилось | применим без кода | кандидат | ув. |
|---|---|---|---|---|
| `ImeDialogTests.cpp` | 3 функции, правка ожиданий | да по компиляции [I] | нет: наша версия теста уже в цели `ime_dialog_tests`; дельта — ожидания upstream | I |
| `ShaderVertexMetadataTests.cpp` | 2 функции | да по компиляции [I] | нет нового покрытия | I |
| `ImagePageTableTests.cpp` | 4 строки (вне функций) | да [I] | нет нового покрытия | I |
| `BitArrayTests.cpp`, `SyncOnAddressTests.cpp` | upstream без изменений от базы (`BitArrayTests.cpp` изменён только нами) | — | — | c |

## 5. Итог

### 5.1 Кандидаты в гейт `shader_cfg_tests` (перенос функции в `tests/shaderCfgTests.cpp`, код эмулятора не меняется)

Все — «проверить прогоном» (сборки не было, [I]). Порядок — по силе довода об исполнении игрой.

1. `TestDsFloatMinMaxDecoder` — DS_MIN_F32 / DS_MAX_F32 (DS:12, DS:13 — по 1 программе ASTRO BOT).
2. `TestShaderStageBarriers` — S_BARRIER (SOPP:a — 66 программ): OpControlBarrier с семантикой AcqRel|Workgroup.
3. `TestVertexBufferGrouping` — группировка атрибутов вершин `PrepareProgram` (путь всех VS).
4. `TestSpirvRepeatedEmission` — повторная эмиссия и переключение split-wave (subgroup 32 хоста NVIDIA для wave64).
5. `TestU64RegisterPairRoundTrip` — ConstantPropagation пар U64.
6. `TestShaderFeatureCollection` — сбор требований SPIR-V по IR.
7. `TestRayTracingInstructions` (`ShaderRayTracingTests.inc`) — только после правки ТЕСТА в одном члене: BVH64 у нас отдельный опкод
   `IMAGE_BVH64_INTERSECT_RAY` (`b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h:574`); часть BVH32 — путь игры
   (MIMG:e6 — 20 программ, MIMG:e7 — 0); члены `ExpectFatal` на Windows не исполняются.

Условно (член `dispatcher_fallback` — форма, а не ответ; брать часть «SPIR-V валиден, покрытие инструкций»): 6 CFG-тестов
`TestNewShaderRecompilerCfg{LoopHeaderBufferLoad,LoopExitSharedWithSelection,NestedLoopNonlocalExit,MixedContinueNonmergeExit,LoopEarlyContinues}Structured`,
`…CfgEarlyReturnSharedLoopContinuation`; `TestNggVertexEntryState` (фикстура другой игры).

Отдельная дешёвая CPU-цель вне агрегата: `LruCacheTests.cpp` (LRU кэшей буферов и текстур; API совпадает, `drawStat.h` header-only).

### 5.2 Кандидаты GPU-гейта и прочих целей

`shader_recompiler_compute_tests` (нужен Vulkan; перенос `TestCase` в наш файл; счёт — программ ASTRO BOT): `Vop2SdwaMulU24Destinations`
(1 767, SDWA 16), `Vop1SdwaMovByteDestinations`/`…Sources` (V_MOV_B32 SDWA 3 094), `Vop2SdwaBitwiseByteDestinations` (V_AND_B32 SDWA 92),
`VectorCompareClassF32ImmediateAndDynamicMasks` (9, SDWA 40), `VectorCompareF32ExposureGuard`, `CubeIdCapturedNegationAndOutputScale`
(1 731), `VectorReadlaneSelectsTwoKeysWithinWave` (834), `VectorIntegerExtremaRuntimeEdges`, `VectorAlignByteUsesTwoBitByteOffset` (2),
`ScalarZeroShiftWithRuntimeCount`, `ScalarDynamic64BitOps`, `ScalarB32MaskDataflow`, `SiblingSharedExitKeepsCapturedConditions`,
`ScalarBranchRestoresInactiveLanes`, `ScalarBufferOffsetAlignmentAndCarry`, `ScalarLoadAlignsDynamicBase`, `ScalarBufferFromLoopReadlane`,
`BufferLoadsGpuSelectedDescriptors`, `BufferLoadDwordx3GpuSelectedDescriptors`, `BufferLoadDwordGpuSelectedDescriptors`,
`BufferLoadFormatXGpuSelectedDescriptors`, `BufferStoreFormat{XyzwPackedUnormSkinningVectors,XZeroFillsPackedRecord,XyzwFloat16ConvertsComponents,XyzwSnorm16CapturedSkinningVectors,XSnorm16ClampsRoundsAndPreservesHalfwords}`,
`FormattedStoreConversionCases`, `DsFloatMinMaxIgnoresData1`, `DsFloatMinMaxClasses`, `DsAppendAllocatesAcrossWaves` (239),
`DsAppendConsumeGdsRegionBounds`, `CheckWave64WholeWaveResults`. Условно: `VectorDppRowShare`, `ImageCubeGradientsPreserveDerivatives`,
`ImageSampleOffsetsReadFourNeighbors`, `CheckPm4*`, `CheckShaderFusion`, `CheckAgcSystemTable`. После правки харнесса (поля `TestCase`
`storage_buffer_range_bytes`, `expected_buffer_resources`, `expected_mip_descriptors`, `expected_float_tolerance`, `pixel_*`): тесты
частичных записей буфера, `TBufferCapturedZeroStrideOob` (TBUFFER_LOAD_FORMAT_XYZW — 24 программы), `Graphics*` (входы PS).

Прочие цели: `kernel_file_system_tests` — `TestSaveOpenVisibility`, `TestSysmoduleReferences`, `CheckAmprOrdering`;
`virtual_memory_allocation_tests` — `TestDirectMappingNamesTypesAndValidation`, `TestSmallFiberStacksAndMigration` (и `TestBatchMappingOperationsAndPartialFailure`, U);
`page_manager_tests` — `TestConcurrentSharedWatchers`; `memory_tracker_tests` — `TestCleanUploadPreservesOwnership`, `TestConcurrentColdUploads`
(оговорка: `memoryTracker.cpp` несёт `KYTY_FIX_B13`; провал разбирать против реестра, не «чинить» под upstream).

### 5.3 Пробы — не гейт, сигналы для M1c (провал на b3dc9c67 ожидаем или вероятен)

| тест | что вскроет | наша строка | ув. |
|---|---|---|---|
| `VectorMadF32RoundsProduct` (GPU; как есть не компилируется — имён `V_FMAC/FMAMK/FMAAK_F32` нет), `VectorMadF32FlushesDenorms` (GPU, переносится) | у нас legacy MAD не отделён от fused FMA: VOP2 0x2b–0x2d декодируются как V_MAC/MADMK/MADAK, а V_MAC/V_MAD/V_MADMK/V_MADAK все идут в `FPFma32`; ожидание upstream (`d8be245c2`): MAD округляет произведение. Игра: VOP2:1f — 5 532, VOP3:141 — 5 540, VOP2:2b — 1 444, VOP2:2d — 1 745 программ. Сильнейший сигнал класса А из тестов | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp:68` `{0x2bu, Opcode::V_MAC_F32},` (+1 `{0x2cu, Opcode::V_MADMK_F32},`); `b3dc9c67:src/graphics/shader/recompiler/frontend/translate/Vector.cpp:417` `case O::V_MAD_F32:` (+1 `case O::V_FMA_F32: return FloatTernary(inst, IR::ValueOpcode::FPFma32, false, true);`) | c (наш код, счёт) / I (провал) |
| `BvhIntersections` (GPU) | расхождения нашей реализации BVH с upstream: тройки типов 2–3 в фикстуре = GPURT, т.е. совпадают с нашим выбором Ф10 (`KYTY_FIX_F10=1`); формат ответа (Flag+kind), `box_grow`, правило top-left, предел `size`, BVH64 могут расходиться — каждое расхождение решается по первоисточнику GPURT, не по upstream | наши кейсы `B1bBvhCase`/`F10BvhCase` (`b3dc9c67:tests/ShaderRecompilerComputeTests.cpp:24350`, `:24517`) | U |
| `TestVertexMadU64UsesPortableProduct` (CPU) | OpIMul над `%ulong` в VS (NVIDIA отвергает большие VS); V_MAD_U64_U32 — 4 программы | — | U |
| `TestSharedExitPreservesNativeDescriptorSources`, `TestNativeScalarReadDescriptorPlanning`, `TestScalarSelectedVccBufferAddress`, `TestNativeGuardedSamplerSource` (CPU) | выбор дескриптора буфера/самплера по ветви при общем выходе и нативной маске; провал = кандидат дефекта выбора ресурса | — | U |
| `HttpUriParseTests.cpp` | правки `025b39c01`, `dc3cd2d2c` (query, маска опций) у нас нет | `b3dc9c67:src/libs/libNet.cpp:289` `constexpr size_t needed = 3;` (+1 пустая строка) | I |
| `SaveDataDialogTests.cpp` (полный режим) | протокол RUNNING→FINISHED (`05f92b642`); у нас Open сразу FINISHED | `b3dc9c67:src/libs/dialog.cpp:435` `g_save_status = SAVE_STATUS_FINISHED;` | I |
| `TestPcmCopiedBeforeScratchBufferReuse`, `TestObjectGainAndAmbisonics`, `TestObjectBusRouting` (AudioOut2) | захват PCM в момент set (`313b60e92`), микширование объектов и усиления (`c86c8b4d9`); нужна заглушка вывода в форме upstream без поля `gains` | `b3dc9c67:src/libs/audio_internal.h:21` `struct OutputParam {` | U |
| `TestNativeStoreCompletion`, `TestDisabledDebugBranches` (не переносятся) | у нас SOPK 0x17 (S_WAITCNT_VSCNT, 9 программ) — S_WAITCNT; SOPP 0x17–0x1a (CDBG*, SOPP:17 — 1 программа) — S_NOP; вероятно равносильно (ветви отладки не берутся) — сверка M1c | `b3dc9c67:src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp:91` `{0x13u, Opcode::S_SETREG_B32}, {0x17u, Opcode::S_WAITCNT},    {0x18u, Opcode::S_WAITCNT},` (+1 `{0x19u, Opcode::S_WAITCNT},    {0x1au, Opcode::S_WAITCNT},`); `:116` `{0x17u, Opcode::S_NOP},` (+1 `{0x18u, Opcode::S_NOP},`) | c (наш код) / I |

Темы без переносимого теста, но с доводом исполнения игрой (для M1c): libScePngEnc (у нас нет HLE, 4 заглушки PLT `PngEnc_v1` в
`log_fs15_v`), SaveDataMemory2 (`cfbaee07f`, у нас своя `memory.bin`), темп AudioOut (`70a475ec8`).

### 5.4 Счёт

Новые файлы upstream — 15 (с `ArchiveTestFixture.h`): переносим без кода и годен — `LruCacheTests.cpp`; компилируются [I], но вне игры или
с ожидаемым провалом — `CesTests.cpp`, `SaveDataDialogTests.cpp`, `HttpUriParseTests.cpp`; остальные 11 — нет (нет заголовков/источников
или SDL3). Новые функции в изменённых файлах (переносимы без кода [I] / всего): `shaderCfgTests.cpp` 22/47 (кандидатов 6, условно 7,
проб 5), `ShaderRayTracingTests.inc` 0/1 (частично 1), `ShaderRayTracingGpuTests.inc` 2/2 (проба 1, вне игры 1),
`ShaderRecompilerComputeTests.cpp` 59/148 (+16 после правки харнесса), `ResourceTracking` 4/19, `ResourceMaterialization` 4/11,
`ScalarProvenance` 3/4, `MemoryTracker` 4/4, `PageManager` 1/1, `KernelFileSystem` 12/19 (из них 3 падают на отсутствующих NID при
выполнении), `VirtualMemoryAllocation` 4/21, `AudioOut2Port` 6/11 (+3 частично), `EventQueueLifetime` 1/2. Изменённые функции — §3.4.

### 5.5 Сомнения

- Сборки не было: «компилируется» — [I]. Совпадение имени у нас и upstream не доказывает совместимость сигнатур (найден один такой
  случай — `SrtMemoryReader`; могут быть и другие: `RecompileForTest`, `TestCompileResult`, поля `program.info` проверялись только по
  именам).
- Извлечение функций — регулярным выражением по колонке 0; функции, объявленные макросами или с отступом, могли не попасть.
- Колонка опкодов видит только именованные опкоды; тесты на сырых словах размечены вручную лишь там, где это влияет на вывод; «тестируемый
  опкод» выбран эвристикой по имени функции.
- «Игра импортирует библиотеку» — по строкам `libSce*` в `eboot.bin`, не по разбору таблицы импорта; «NID нет у нас» — по отсутствию
  строки NID где-либо в `b3dc9c67:src` (проверено для `8nY19bKoiZk`, `Ft3EtsZzAoY`, `Xweb+naPZ8Y`, `r42bWcQbtZY`).
- Временные скрипты разбора лежат вне проекта (каталог временных файлов ОС), в репозиторий ничего не записано.

