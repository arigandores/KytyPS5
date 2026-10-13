# M6a2 (`HPP-854`, трек M, волна 2) — правки RC1–RC2 M6b и члены п. 770 в коде измерения `KYTY_DIAG_M5W2`

Звено Emu Engineer по `ROADMAP.md` п. 770(б)–(е) (KytyPS5 `9a621dbb`); основание — отзыв M6b `docs/track-m/m6b/review.md` (`9eab3363`),
вход — код M6a (worktree `C:/kyty/m657/m6a/wt` HEAD `6964a58f`, `main` `1f95def9`). Дата 2026-10-13 UTC; время событий — `times.txt`
(строки `date -u`). **Игра не запускалась; бинарь теста не установлен; ГП-кейсы `dl_cases.txt` не запускались; сборки `--parallel 2`,
приоритет Idle (п. 760).** Замка `C:/kyty/SEALED_RUN.lock` не было ни перед одной командой; серий звена прогонов не шло (API: `in_progress` —
`HPP-854` и `HPP-852` M7a). Метки: [c] — проверено, [I] — вывод, [U] — неизвестно. **Код в игре не проверен — WIP до тегов M6c.**

## 1. Итог

| что | значение |
|---|---|
| коммит worktree | **`97198ce9`** на `6964a58f` (= MS1 `ed94b13d` + M6a + M6a2), worktree `C:/kyty/m657/m6a/wt` |
| код в `main` | **`fce6480f`** (`git cherry-pick -n 97198ce9` на `9a621dbb`, `textureCache.cpp` слит автоматически; строки `+`/`−` = коммиту worktree, 297 = 297, `main_vs_wt.out.txt` `ALL OK`) |
| бинарь теста | `kyty_emulator.exe` **sha256 `23f3c4e73f69b2246a0250c518dc1a0f799221342ddbfddee0ba6ca7160c39a3`**, строка версии `KytyPS5-2026-09-15-6a2987a-1935-g97198ce90`; закреплённая копия **`C:/kyty/m657/bin/kyty_emulator_23f3c4e7.exe`**; **не установлен** |
| подпись трансляции | `KYTY_SHADER_SOURCE_HASH` = **`8dcf31779bbcb7c6e605653a138dae162f645a46` = MS1** [c `kytyGitVersion.h` сборки]; изменены только `src/libs/diagM5W2.{h,cpp}`, `textureCache.cpp` (место T188), `tests/MWave2DiagStand.cpp` — вне `src/graphics/shader/**` и `SHADER_CACHE_EXTRA_FILES` |
| `check_gate_order.py` | `GATE ORDER: clean` (гейтов и ручек нет) |
| строки бинаря | `minlod_div_x=%` ×1, `clr_dw_div8=%` ×2 (`M5W2Stat` и `M5W2Clr`), `ao_obj_unread=%` ×1, `inv_part_src=%` ×1 — в M6a `146c9358` ×0; `M5W2Stat: when=%s`, `M5W2Clr: when=%s`, `M5W2: mode=%d` — по 1 в обоих. Строка версии `…-1933-ged94b13d4` есть в обоих бинарях по 1 разу (одна единица трансляции со старой строкой — так же у M6a) |
| `shader_cfg_tests` | 135 тестов, **0 падений**; 374 модуля SPIR-V **байт в байт = M6a** (`tests_spv_cmp.out.txt`) |
| стенд | `run_stand_m6a2.py` **`ALL OK`** на сборке worktree и на сборке `main` (`wtmain` @ `fce6480f`) |
| мутанты | **16 из 16 пойманы**, контроль восстановленного дерева `ALL OK`; исходники worktree после мутантов = до (sha256 4 файлов) |
| сборка `main` | `wtmain` @ `fce6480f`: стенд и `kyty_emulator` собраны (exe `32238f14…`, справка) |

## 2. Правки (имена — п. 770, записаны до кода: `names_before_code.md` 03:50:16Z, первая правка — `times.txt` стр. 2)

Новые поля дописаны **в конец** строки `M5W2Stat:` — `… raw_rd_gpu= minlod_div_x= clr_dw_div8= ao_obj_unread= inv_part_src=`; столбец
`clr_dw_div8=` — в конец каждой строки `M5W2Clr:`. Порядок прежних полей не менялся. Все места — под прежним `if (DiagM5W2::On())`.

| пункт | поле | условие | место |
|---|---|---|---|
| (б) RC1 T021 | `minlod_div_x` (поле расхождения правила п. 767(к)) | созданный вид с `min_lod` > 0, `base_level` > 0 и `min_lod` > 256·max(`base_level`, `level_count` − 1); `level_count` 0 → нет | `MinLodDivergesExact`, `NoteMinLodView` (`diagM5W2.cpp`); место — прежнее (`imageView.cpp`, `FindView`); `minlod_div` остаётся справкой |
| (в) RC2 T313 + T179 | `clr_dw_div8` (справка, класс (а3) M5a) | `R8Unorm` (vk 9): `W ≠ (W & 0xff)·0x01010101`; `R8G8Unorm` (vk 16): `(W & 0xffff) ≠ (W >> 16)`; в `clr_dw_div` не входит | `ClearDwordDiverges8`, `NoteClearDword`; итог в `M5W2Stat`, по формату — в `M5W2Clr` |
| (г) член 769(г)(2) T125 | `ao_obj_unread` (справка) | при `=1` гранула объектного порта читается **только копией** через `Libs::LibKernel::Memory::TryReadBacking` (сырого чтения объектного PCM больше нет); отказ копии — `ao_obj_unread`, Push считается в `ao_obj_push`, в `ao_obj_nz` — никогда; гранула > 4 МиБ не копируется и тоже `ao_obj_unread` (реальная ≤ 64 КиБ [I]); порты шин — сырое чтение, как прежде (путь вывода читает их сырым указателем) | `NoteAudioPort` (`diagM5W2.cpp`); место — прежнее (`libAudio2.cpp`, под `g_audioout2_port_mutex`) |
| (д) П1 T188 | `inv_part_src` (справка) | те же пары, что `inv_part` (после `IsGpuModified`), покрытие — по `SourceRange()` (`info.data.address`, `source_size` или `info.data.size`), то есть по диапазону, который проверяет `Image::Overlaps` | `NoteInvalidateImage` (+ параметр `source_size`); место `textureCache.cpp`, `InvalidateMemoryFromGPU` передаёт `image.SourceRange().size` |

Сверка (д) с `Overlaps` (член ревью M6b2): `Overlaps` = `ImageRangeOverlaps(SourceRange().address, SourceRange().size, …)`, `SourceRange()` =
`{info.data.address, source_size != 0 ? source_size : info.data.size}` (`image.h:185–193`); `inv_part_src` берёт тот же адрес (`image_address` =
`info.data.address`) и `SourceRange().size`.

## 3. Стенд

`tests/MWave2DiagStand.cpp` (цель `m_wave2_diag_stand`), драйвер `run_stand_m6a2.py` (копия `run_stand_m6a.py` с ожиданиями M6a2):

- плечи `pure` и `audio` поднимают гостевую память (`Memory::Lifecycle` и `KernelMapNamedFlexibleMemory` 256 КиБ, CPU RW); PCM объектных
  портов лежит в ней (читается через `TryReadBacking`), PCM шин — в памяти хоста; «нечитаемый указатель» — `0x1000` (не покрыт ни гостевым
  отображением, ни страницей хоста: сырое чтение — нарушение доступа, см. мутант `obj_raw_read`);
- `pure` — **103 из 103** (было 60): новые случаи `ao_obj_unread` (`ao_obj_push` 1, `ao_obj_unread` 1, `ao_obj_nz` 0), `clr_r8_div8` (`0x00ff00ff` → 1),
  `clr_r8_rep` (`0x7f7f7f7f` → 0), `clr_rg8_div8` (`0x00001234` → 1), `clr_rg8_rep` (`0x12341234` → 0), `minlod_div` (`B` 1, `count` 3, `M` 768 → `div` 1,
  `x` 1), `minlod_div_not_x` (`B` 2, `count` 2, `M` 384 → `div` 1, `x` 0), `inv_src_cover` (данные 0x4000, источник 0x1000, запись источника целиком →
  `inv_part` 1, `inv_part_src` 0); ко всем прежним случаям добавлены нулевые дельты новых полей. Строка
  `M5W2Stat: when=stand pushes=1 ao_obj_push=5 ao_obj_nz=2 ao_obj_nopcm=1 ao_bus_push=2 ao_bus_nz=1 clr_dw=12 clr_dw_div=5 minlod_views=4
  minlod_div=2 inv_calls=1 inv_part=3 inv_gpu=4 inv_off=1 raw_rd=2 raw_rd_gpu=1 minlod_div_x=1 clr_dw_div8=2 ao_obj_unread=1 inv_part_src=2`;
  `M5W2Clr` — `fmt=9` и `fmt=16` `clr_dw=2 clr_dw_div=0 clr_dw_div8=1`, у прежних шести форматов `clr_dw_div8=0`.
- `audio` — 4 Push через настоящие функции AudioOut2: Push 4 — объектный порт указывает на `0x1000`: при `=1` `d_obj_push=1 d_obj_nz=0
  d_obj_unread=1 rc=0`, процесс жив; при `=0` все дельты 0, процесс жив (объектный PCM никто не читает). Push 1–3 — как в M6a.
- `printf`, `ampr`, `agc` — без изменений, `ALL OK`.

## 4. Мутанты (`mut_m6a2.py`, форма `mut_m6a.py`)

| мутант | что | итог |
|---|---|---|
| `x_eq_div` | `minlod_div_x` = условию `minlod_div` (`level = level_count − 1`) | CAUGHT (случай `B` 2, `count` 2, `M` 384) |
| `c_minlod_div_x` | счётчик `minlod_div_x` не растёт | CAUGHT |
| `c_clr_dw_div8`, `c_clr_fmt_div8` | итог / столбец формата `clr_dw_div8` не растёт | CAUGHT, CAUGHT |
| `r8_never`, `r8_always`, `rg8_never`, `rg8_always` | правило формата мёртво / всегда истинно | 4 CAUGHT (случаи «≥ 1» и «0» на каждый формат) |
| `c_ao_obj_unread` | отказ копии не считается | CAUGHT |
| `obj_raw_read` | объектная гранула читается сырым указателем вместо копии | CAUGHT (`pure` умер `0xC0000005` на `0x1000`) |
| `c_ao_obj_push`, `c_ao_obj_nz`, `c_ao_bus_push`, `c_ao_bus_nz` | переписанные счётчики `NoteAudioPort` | 4 CAUGHT |
| `c_inv_part_src` | счётчик не растёт | CAUGHT |
| `src_eq_data` | `inv_part_src` по `info.data.size` (= `inv_part`) | CAUGHT (случай `inv_src_cover`) |

Итог: **16 из 16**, контроль восстановленного дерева — сборка и `ALL OK` (`mut_m6a2.out.txt`). Мутант «место T188 передаёт `info.data.size`
вместо `SourceRange().size`» стендом **не ловится** (место графики стендом не исполняется, как в M6a §5) — проверка чтением диффа.

## 5. Состояние и его жизненный цикл (правило с. 134)

- Новые счётчики `g_minlod_div_x`, `g_clr_dw_div8`, `g_ao_obj_unread`, `g_inv_part_src` и массив `g_clr_fmt_div8[256]` (`diagM5W2.cpp`,
  безымянное пространство имён) — `relaxed`-атомики, растут только в `Note…`, не сбрасываются (сумма за процесс), читаются `Read`/`PrintStat`.
- **TLS:** `thread_local std::vector<uint8_t> copy` в `NoteAudioPort` (ветка объектного порта) — буфер копии гранулы потока, который зовёт
  Push; ставится (растёт) только `copy.resize(bytes)` при `=1`, не уменьшается и не снимается до конца потока (освобождает выход потока).
  Значение между вызовами не используется: каждый вызов перезаписывает `bytes` байт перед чтением; при отказе `TryReadBacking` (адресат не тронут
  или частично — не важно) возврат до чтения копии. Выходы `NoteAudioPort`: `bytes == 0` (ранний, до буфера), `bytes > MAX_GRAIN_BYTES`,
  отказ копии, конец объектной ветки, конец ветки шин — ни один не оставляет состояния, кроме этого буфера и счётчиков.
- Замки: `TryReadBacking` берёт `m_mutex` гостевого адресного пространства (лист: внутри — только поиск отображения и `memcpy`) под уже взятым
  `g_audioout2_port_mutex`; обратного порядка нет [I: `m_mutex` пространства не держится при вызове AudioOut2 — внутри `TryTransferBacking` чужого
  кода нет]. Остальные места замков не добавляют.
- При `=0` новых действий нет: все новые счётчики — внутри прежних `Note…`, зовущихся только при `On()`.

## 6. Что M6a2 НЕ доказывает

- что места графики (T021, T313 + T179, T188) исполняются в игре и что `inv_part_src` верно передаётся местом (стенд зовёт функции `Note…`);
- что PCM объектных портов игры лежит в памяти, которую видит `TryReadBacking` [I: гостевая куча — отображения ядра]; если нет — `ao_obj_unread`
  ≈ `ao_obj_push` в теге M6c, и T125 «не определено» по правилу п. 770(г);
- что `TryReadBacking` ловит все нечитаемые указатели (п. 770(ж)); что модели M5a верны железу;
- ни одно число — не выигрыш; 60 FPS не обещаются.

## 7. Файлы (`docs/track-m/m6a2/`)

| файл | что |
|---|---|
| `names_before_code.md` | имена полей до кода |
| `patch_m6a2.py`, `patch_m6a2_stand.py` / `patch_wt.out.txt`, `patch_wt2.out.txt` | правка (якоря целыми строками); первый прогон — отказ якоря `Read()` (`diagM5W2.cpp` не тронут, `.h` возвращён `git checkout`), второй — `ALL OK` |
| `main_vs_wt.out.txt` | сверка строк `main` с worktree |
| `run_stand_m6a2.py` / `stand_wt.out.txt`, `stand_main.out.txt`, `stand/` | драйвер; прогоны на сборках worktree и `main`; вывод плеч и логи `pure`, `audio` |
| `mut_m6a2.py` / `mut_m6a2.out.txt` | мутанты |
| `gate_order_wt.out.txt` | `check_gate_order.py` |
| `run_tests_m6a2.py` / `tests_d.out.txt`, `tests_spv_cmp.out.txt` | `shader_cfg_tests` и сверка SPIR-V с M6a |
| `commit_msg_m6a2.txt`, `times.txt`, `sha256.txt` | сообщение коммита; время событий; sha256 файлов и бинаря |
