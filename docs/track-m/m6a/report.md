# M6a (`HPP-848`, трек M, волна 2) — код только измерения `KYTY_DIAG_M5W2` и строки сигнатур

Звено Emu Engineer по `ROADMAP.md` п. 767(и), (в), (з) (KytyPS5 `f7a5e258`); основание — отзыв M5b `docs/track-m/m5b/review.md`
(`bc58c115`), отчёт M5a `docs/track-m/m5a/report.md` (`4c1327bc`). Дата 2026-10-13 UTC; время событий — `times.txt` (строки `date -u`).
**Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не запускались; сборки `--parallel 2`, приоритет Idle (п. 760).**
Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; серий звена прогонов в это время не шло (API: `in_progress` — только
`HPP-847` M5c и `HPP-848`). Метки: [c] — проверено, [I] — вывод, [U] — неизвестно. **Код в игре не проверен — WIP до тегов M6c.**

## 1. Итог

| что | значение |
|---|---|
| код в `main` | **`1f95def9`** (cherry-pick коммита worktree; конфликты — только строки `#include` и выхода рядом с кодом F47g, оставлены обе стороны; добавленные/удалённые строки = коммиту worktree в 12 из 12 файлов, `main_vs_wt.out.txt` `ALL OK`) |
| worktree бинаря теста | `C:/kyty/m657/m6a/wt`, HEAD **`6964a58f`** = MS1 `ed94b13d` + коммит M6a |
| бинарь теста | `kyty_emulator.exe` **sha256 `146c93585b664fc98c50fc8a79fdfd99f09430940cb10ecc041720f2cd821202`**, строка версии `KytyPS5-2026-09-15-6a2987a-1934-g6964a58ff`; закреплённая копия `C:/kyty/m657/bin/kyty_emulator_146c9358.exe`; **не установлен** |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1** [c `kytyGitVersion.h` обеих сборок]; файлы набора подписи (`src/graphics/shader/**`, `shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`) не тронуты |
| `check_gate_order.py` | `GATE ORDER: clean` (новых гейтов/ручек в `gates.h` нет — ручка читается `Common::EnvFlagOn`) |
| строки бинаря против MS1 | `binary_m6a.py` `ALL OK`: 8 новых строк x1 в M6a / x0 в MS1; 13 маркеров MS1 (темы волны 1, базы FS15, хэш подписи) — равное число |
| `shader_cfg_tests` | 135 тестов, **0 падений** (= M2d `d` на MS1, база п. 761); 374 модуля SPIR-V **байт в байт = M2d `d`** (`tests_spv_cmp.out.txt`) |
| стенд `m_wave2_diag_stand` | `run_stand_m6a.py` **`ALL OK`** на сборке worktree и на сборке `main` (`wtmain` @ `1f95def9`) |
| мутанты | **26 из 26 пойманы**, контроль восстановленного дерева `ALL OK` (`mut_m6a.out.txt`) |
| сборка `main` | `wtmain` @ `1f95def9`: `kyty_emulator` и стенд собраны (exe `c44f3ce2…`, справка; подпись `main` `aac6db69…` — своя, M6a её не меняет по составу файлов) |

## 2. Имена до кода

Имена строк и полей записаны в `names_before_code.md` в 2026-10-13T02:47:56Z, до первой правки кода (02:51:34Z, `times.txt` стр. 2–3).
Одна поправка до сборки (02:52:31Z, стр. 5): значение поля `why` строки `AmprWriteAddress` — `<state|ensure>` вместо `<state|space>`
(`ensure` = любой отказ `EnsureCommandBufferRecordSpace`; какой именно тест отказал, называет её собственная строка `AmprRecordSpace`).

**Ручка `KYTY_DIAG_M5W2`** (умолчание 0; `0/false/off/no` и пусто — 0; одно чтение на процесс; строка `M5W2: mode=<0|1>` при первом чтении).

**Строка на выходе** `M5W2Stat: when=<periodic|exit> pushes= ao_obj_push= ao_obj_nz= ao_obj_nopcm= ao_bus_push= ao_bus_nz= clr_dw= clr_dw_div=
minlod_views= minlod_div= inv_calls= inv_part= inv_gpu= inv_off= raw_rd= raw_rd_gpu=` и `M5W2Clr: when=… fmt=<vk::Format число> clr_dw= clr_dw_div=` —
по строке на формат с `clr_dw` > 0. `exit` — оба выхода `Execute` (`emulator.cpp`, рядом с `FixF20Stat`/`F47dtStat`); `periodic` — каждые
4 096 поставленных в очередь Push AudioOut2 (страховка, если строка выхода потеряна). Только при `=1`; при `=0` счётчики не трогаются (места
под `if (DiagM5W2::On())`).

| поле | тема | место (MS1 / `main`) | что считается |
|---|---|---|---|
| `ao_obj_push` | T125 | `libAudio2.cpp`, `audioout2_queue_context_audio` (успешный Push, под `g_audioout2_port_mutex`) | на каждый поставленный Push — каждый порт контекста с `pcm_data != nullptr` и `audioout2_port_type_is_object` (`(port_type & 0xff00) == 0x0100`, порты `port_type` 256 игры) |
| `ao_obj_nz` | T125 (**поле расхождения**) | там же | из них — с ≥ 1 ненулевым отсчётом гранулы (`samples_num` × каналы `data_format`; float — `v != 0` или NaN, int16 — ≠ 0) |
| `ao_bus_push`, `ao_bus_nz` | T125 (живой контроль) | там же | то же для необъектных портов (шины, `audio_handle` не требуется) |
| `ao_obj_nopcm` | T125 (справка) | там же | объектные порты контекста без PCM |
| `clr_dw` | T313 + T179 | `textureCache.cpp`, `ClearImageFromBuffer`, перед `ClearImage` (цветовая заливка после успешного декода) | принятые цветовые заливки DWORD, и по `image.info.pixel_format` |
| `clr_dw_div` | T313 + T179 (**поле расхождения**) | там же | из них — R16 (`R16_SFLOAT`, `R16_UNORM`) при `lo ≠ hi`; `R16G16B16A16_SFLOAT`, `R16G16B16A16_UNORM`, `R32G32_SFLOAT` при слове ≠ 0 |
| `minlod_views` | T021 | `imageView.cpp`, `FindView`, созданный вид (перед `views.push_back`) | созданные виды с `min_lod` > 0 |
| `minlod_div` | T021 (**поле расхождения**) | там же | из них `base_level` > 0 и `min_lod` > (`level_count` − 1)·256 |
| `inv_calls` | T188 | `textureCache.cpp`, `InvalidateMemoryFromGPU` (под `m_lock`) | вызовы с годным диапазоном |
| `inv_part` | T188 (**поле расхождения**) | там же, на образ цикла (после фильтра `depth_id`/`Overlaps`, до `ClearGpuModified`) | пары (вызов, образ) с `IsGpuModified` и записью, не покрывающей диапазон образа |
| `inv_gpu`, `inv_off` | T188 (справка) | там же | пары с `IsGpuModified`; из `inv_part` — запись не с базы образа (случай, который пропускает форма upstream `ebe401d05`) |
| `raw_rd` | T258 | `descriptors.cpp`, `NativeStorageBuffer`, перед `ObtainBuffer` | привязки `!written && !formatted` |
| `raw_rd_gpu` | T258 (**поле расхождения**) | там же | из них `FindImageFromRange(address, size)` (по умолчанию `ensure_valid`: база = `address`, `SafeToDownload` = `IsGpuModified && !BufferModified && !CpuDirty`) даёт образ — ровно условие, при котором upstream `743fdc699` синхронизировал бы буфер из образа |
| `pushes` | справка | `libAudio2.cpp`, после разблокировки | поставленные Push |

**Строки без ручки** (вне набора подписи; ни одно решение не меняется):

| строка | тема | место | предел |
|---|---|---|---|
| `GuestPrintf: negative precision prec=<p>` | T031 | `guestPrintf.cpp`, `kyty_printf_internal`, ветка `.*` при `prec < 0` | раз на процесс |
| `AmprRecordSpace: refused why=<arg\|header\|buffer\|space\|backing> cb= record_size= write_offset= size= n=` | T309 | `libAmpr.cpp`, `EnsureCommandBufferRecordSpace` при `false` (те же проверки в том же порядке с тем же коротким замыканием, отказавшая названа) | 20 |
| `AmprWriteAddress: refused why=<state\|ensure> cb= record_size= address= value= n=` | T309 | `libAmpr.cpp`, `AppendWriteAddressRecord` при `false` (→ `EBUSY`) | 20 |
| `AgcReserveDW: cursor state class=<up0\|down0\|both0\|down_lt_up> up= down= reserved_dw= num_dw= callback=<0\|1> n=` | T023 | `agc.cpp`, вход `CommandBuffer::ReserveDW` при нулевом курсоре или `cursor_down < cursor_up` | 20 |

## 3. Стенд и мутанты

Стенд `tests/MWave2DiagStand.cpp` (цель `m_wave2_diag_stand`, `EXCLUDE_FROM_ALL`, без `add_test`; исходники эмулятора линкуются, не копируются),
драйвер `run_stand_m6a.py` (процесс на плечо; `LOGF` — в файл плеча; `Log::DrainForExit` перед `_Exit` — писатель лога асинхронный):

- `pure` — каждый счётчик через его функцию `Note…`: по каждому полю вход, где поле растёт на 1, и вход, где оно стоит (знаменатель растёт):
  60 из 60; строка `M5W2Stat: when=stand` с теми же итогами; `M5W2Clr` по 6 форматам (76, 70, 97, 91, 103, 37) с ожидаемыми `clr_dw`/`clr_dw_div`.
- `audio` — T125 через настоящие `AudioOut2ContextCreate/PortCreate/PortSetAttributes/ContextPush` (объектный порт 0x100 моно float и порт
  шины с 3-канальным float, для которого устройство хоста не открывается): `=1` — Push 1 (оба ненулевые) `obj_push 1 obj_nz 1 bus_push 1
  bus_nz 1`, Push 2 (оба нулевые) `nz 0`, Push 3 (новый объектный порт без PCM) `obj_nopcm 1`; `=0` — все дельты 0 (место закрыто ручкой);
  строки `M5W2: mode=1` / `=0`.
- `printf` — гостевой printf `%.*s` с −1 дважды и с 2: ровно одна строка `GuestPrintf: negative precision prec=-1`, вывод прежний (`[]`, `[]`, `[ab]`).
- `ampr` — настоящие NID Ampr (`8aI7R7WaOlc`, `N-FSPA4S3nI` на 0x40 байт, `j0+3uJMxYJY` ×25): вызовы 1–2 — 0, 3–25 — `EBUSY`;
  `AmprRecordSpace … why=space write_offset=0x40 size=0x40` 20 строк n=1..20, `AmprWriteAddress … why=ensure` 20 строк.
- `agc` — `Gen5::AgcAcbResetQueue` (`AllocateDW(2)` → `ReserveDW`) на буфере с `cursor_up` = 0, `cursor_down` = 0, оба 0, `down < up`
  (обратный вызов роста чинит курсоры), нормальном, затем 22 плохих: 27 из 27 ответов прежние (`ok=1`); 20 строк n=1..20, классы
  первых пяти — `up0, down0, both0, down_lt_up, down0` (нормальный вызов строки не даёт).

Мутанты (`mut_m6a.py`, одна точная подстановка в worktree, пересборка стенда, драйвер, восстановление байт в байт): «счётчик не растёт» — 17
(`ao_obj_push`, `ao_obj_nz`, `ao_obj_nopcm`, `ao_bus_push`, `ao_bus_nz`, `pushes`, `clr_dw`, `clr_dw_div`, строка формата `clr_fmt`,
`minlod_views`, `minlod_div`, `inv_calls`, `inv_gpu`, `inv_part`, `inv_off`, `raw_rd`, `raw_rd_gpu`); место T125 убрано (`site_audio_port`,
`site_audio_push`); ручка не закрывает место (`gate_audio`); строки сигнатур убраны (`sig_t031`, `sig_t309_ensure`, `sig_t309_wa`,
`sig_t023`); предел 20 → 30 (`lim_t309`); класс T023 спутан (`cls_t023`) — **26 из 26 CAUGHT**; контроль восстановленного дерева — сборка и
`ALL OK`. Исходники worktree после мутантов = до мутантов (sha256 набора файлов).

## 4. Состояние и его жизненный цикл (правило с. 134)

Новое состояние — только счётчики процесса; TLS нет, полей объектов нет.
- `Libs::DiagM5W2::On()::on` (`diagM5W2.cpp`, функция `On`) — статическая локальная, ставится один раз при первом вызове, не снимается.
- 16 счётчиков `g_*` и 2×256 счётчиков формата (`diagM5W2.cpp`, безымянное пространство имён) — растут только в `Note…`; не сбрасываются
  (сумма за процесс), читаются `Read`/`PrintStat`.
- `negative_precision_logged` (`guestPrintf.cpp`, ветка `prec < 0`), `logged` ×2 (`libAmpr.cpp`, `LogRecordSpaceRefused`,
  `LogWriteAddressRefused`), `cursor_state_logged` (`agc.cpp`, `ReserveDW`) — статические атомики пределов строк, только растут.
Выходы функций: ни одна правка не добавляет раннего выхода, кроме переписанной `EnsureCommandBufferRecordSpace` — у неё два выхода
(`false` после строки, `true`), проверки и их порядок прежние (короткое замыкание: `ValidateCommandBufferHeader` зовётся только при
`state != nullptr && record_size != 0`, `ValidateCommandBufferBacking` — только при пройденных прежних проверках), поэтому её ответ и побочные
действия (`header_validated`, `buffer_validated`) те же. Замки: счётчик T125 — под уже взятым `g_audioout2_port_mutex`; T188 — под уже
взятым `m_lock`; T258 — `FindImageFromRange` берёт `m_lock` текстурного кэша сам (как путь синхронизации в `ObtainBuffer`; вызывающий его не
держит); строки T309 — под уже взятым `g_command_buffer_mutex`.

## 5. Что M6a НЕ доказывает и что проверить M6b / M6c

- **Места графики (T313 + T179, T021, T188, T258) стендом не исполняются** — нужен текстурный кэш и ГП; стенд проверяет функции `Note…`, а
  вызов из места — только чтением кода (§2) и diff. Мутант «вызов из места графики убран» стендом **не ловится**. Живой контроль места — теги
  M6c: знаменатели `clr_dw`, `minlod_views`, `inv_calls`, `raw_rd` обязаны быть > 0 (в логах M3 `clr_ok` 68 906 / 105 430 / 188 889,
  `img_minlod` 31 343 / 1 187 / 5 059 за прогон [c M5a]); 0 при таком входе — дефект места, не «путь не исполнялся».
- T125 читает гостевой буфер PCM объектного порта в момент Push (при `=1`); если игра освободила буфер, а указатель в порту остался, — чтение
  невалидной памяти [I, риск только при `=1`].
- T188 считает записи ГП-путей, которые зовут `InvalidateMemoryFromGPU` (запись буфера хранения, DMA-заливка, DMA-копия), а не записи CPU.
- T021 считает созданные виды (кэш видов), не привязки; знаменатель включает виды пути отложенных мипов (там `base_level` > 0 не бывает при
  `KYTY_MIP_DEFER_LEVELS` = 1 [c M5a]).
- Цена `=0`: проверка ручки на каждом месте (статическая переменная) и одно сравнение курсоров на входе `ReserveDW` без ручки; скорость не
  мерилась (не цель звена).
- Строки без ручки отгружаются ближайшим бинарём отгрузки любого трека (п. 767(з)); до него они есть только на бинаре теста M6a.
- Ни одно число не выигрыш; что любая тема видна в игре — не заявляется; 60 FPS не обещаются.

## 6. Файлы (`docs/track-m/m6a/`)

| файл | что |
|---|---|
| `names_before_code.md` | имена строк и полей до кода |
| `patch_m6a.py`, `patch_m6a_stand.py` / `patch_wt.out.txt` | правка мест и стенда (якоря целыми строками; применены к worktree) |
| `resolve_main.py`, `main_vs_wt.out.txt` | разрешение конфликтов cherry-pick в `main`; сверка строк `main` с worktree |
| `mk_wt_m6a.sh`, `build_m6a.cmd`, `build_m6a_main.cmd`, `lowrun.py` | worktree и сборки (Idle, `--parallel 2`) |
| `run_stand_m6a.py` / `stand_base.out.txt`, `stand_main.out.txt` | драйвер стенда; прогоны на сборке worktree и `main` |
| `mut_m6a.py` / `mut_m6a.out.txt` | мутанты |
| `binary_m6a.py` / `binary_m6a.out.txt` | строки бинаря против MS1 `ea35b679` |
| `gate_order_wt.out.txt` | `check_gate_order.py` |
| `run_tests_m6a.py` / `tests_d.out.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M2d |
| `times.txt`, `sha256.txt` | время событий; sha256 файлов и бинарей |
