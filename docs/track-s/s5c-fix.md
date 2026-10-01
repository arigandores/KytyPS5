# Трек S, звено S5c — правки RC2–RC6 S-pcw и бинарь S6 на `4fc501f4` (`HPP-323`, Emu Engineer)

Решение — `a1e8bc90:docs/ROADMAP.md:12994` «245. **Приёмка звена S5b трека S (`HPP-317`, Red Team; решение лида 2026-10-01 01:46:50 UTC по
`date -u`, записано ДО перевода звена и ДО» (контроль +1 — «заданий S5c/S5d).** Отзыв …»), пункты (а)–(в), (ж). Отзыв — `docs/track-s/s5b-review.md`.
**Игры нет. Бинарь собран, НЕ установлен, дыма нет (прогоны — S6) — WIP по коду до S5d.** Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/s288/STOP`
не было ни перед одной командой. Файлы звена — `C:/kyty/s288/s5c/`; время — `C:/kyty/s288/s5c/times.txt` (`date -u`).

`pc` = `src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp`. Ссылки — `<коммит>:<путь>:<строка>`, якорь — целая строка, контроль — строка +1;
16 ссылок проверены `C:/kyty/s288/s5c/refs_s5c.py` → `refs_s5c.out.txt` (`ALL OK`, sha256 `3b47ada4…`).

## 1. Код — KytyPS5 `2ce6326e` (родитель `e9c0ca61`), одним коммитом, только `pc`

`git show --stat 2ce6326e` — 1 файл, +39/−11; `pipelineCache.h` правок не потребовал. `src/graphics/shader/**` — 0 правок. Новых полей, TLS,
флагов и счётчиков с жизненным циклом нет: все новые величины — локальные переменные функции (таблица установки/снятия пуста).
`check_gate_order.py` (`C:/kyty/s136/step3/`) — `GATE ORDER: clean` (гейты и ручки не трогались).

| RC | что | якорь (`2ce6326e:pc:N`, «якорь», +1) | при `=0` |
|---|---|---|---|
| RC2 | `PcwDriverSaved()` ложно, пока `m_pcw_want_driver` поднят и не обслужен | `:6120` «return SPcwMode() && m_pcw_saved_any && m_pcw_saved_created == m_pcw_created.load() && !m_pcw_want_driver.load();», +1 «}» | `SPcwMode()` первым — ложно, как прежде |
| RC3 gfx | ожидание пайплайна воркера `wait_for`: `gen0` до, `gen1` после, строка `AvTrace: pcw overlap wait gfx id0=<vs> id1=<ps\|0> wait_us=<ожидание> gen0= gen1=` по правилу `PcwNoteOverlap` | `:5220` «const uint64_t pcw_gen0    = pcw_trace ? m_pcw_gen.load() : 0;», +1 «const auto     pcw_wait_t0 = pcw_trace ? HostMicros() : 0;»; `:5228` «PcwNoteOverlap("wait gfx", programs.vertex[0].id, ps_input_info != nullptr ? programs.pixel.id : 0,», +1 «pcw_gen0, HostMicros() - pcw_wait_t0);» | `pcw_trace` ложно (`SPcwMode()` замыкает, `AvTraceEnabled` не зовётся); то же ожидание тем же замком `m_job_mutex` (замок теперь во вложенном блоке, после него в ветке ничего нет) |
| RC3 cs | ожидание без границы `m_ready_cv.wait`: то же, `wait cs id0=<cs> id1=0` | `:5809` «const uint64_t                   pcw_gen0   = PcwOverlapTrace() ? m_pcw_gen.load() : 0; // S5c, RC3», +1 «const auto                       wait_begin = HostMicros();»; `:5816` «PcwNoteOverlap("wait cs", compute_program.id, 0, pcw_gen0, HostMicros() - wait_begin);», +1 «}» | два вызова `PcwOverlapTrace()` (чтение статического `bool`), строки нет |
| RC3 правило | печать, если `gen0` нечётен или `gen1 ≠ gen0` (без изменений) | `:6249` «if ((gen0 & 1u) == 0 && gen1 == gen0) {», +1 «return;» | — |
| RC4 | `AvTrace: pcw recipes copied= count= lock_us= hold_us=`: `lock_us` — ожидание `m_mutex` потоком записи, `hold_us` — удержание (граница ожидания GuestGpu); `wait_us` в строке больше нет | `:6185` «lock_us                      = hold_begin - lock_begin;», +1 «if (m_recipes_path.empty() \|\| m_recipe_count == 0) {»; `:6202` «hold_us   = HostMicros() - hold_begin;», +1 «}»; `:6205` «LOGF("AvTrace: pcw recipes copied=%zu count=%u lock_us=%" PRIu64 " hold_us=%" PRIu64 "\n", copied, count,», +1 «lock_us, hold_us);» | `PcwWriteRecipes` зовётся только при `=1` |
| RC5 | строка `GcnDumpReg: skip type=<тип> hash=<16 hex> size=<байт>` на тихом выходе (`code == nullptr`, `size == 0`, `size % 4 != 0`) | `:1307` «LOGF("GcnDumpReg: skip type=%u hash=%016" PRIx64 " size=%u\n", static_cast<uint32_t>(binary_type), shader_hash,», +1 «size_bytes);»; вызывающий — `:6258` «if (DumpGcnAtRegistration()) {», +1 «DumpShaderGcnRegistered(…» | вызов только при `KYTY_DUMP_GCN=2` |
| RC6 | при `=1` до 8 попыток пары `getPipelineCacheData` при `VK_INCOMPLETE` | `:4853` «const uint32_t attempts = SPcwMode() ? 8u : 3u;», +1 «for (uint32_t attempt = 0; attempt < attempts; attempt++) {» | 3, как прежде |

Замечания исполнителя: (1) RC6 при `=1` действует на все вызовы `WriteDriverCache` — поток записи (`PcwLoop`) и `Save()` на выходе (поток окна
или деструктора, под `m_mutex`, не GuestGpu); прочие три вызова (`MaybeWriteDriverCache`, стенд `=0`, `FinishPreparation`) при `=1` не исполняются.
(2) RC3: окно строки — само ожидание GuestGpu; создание воркером могло начаться раньше `gen0` — запись драйвера, закончившаяся до начала
ожидания, строки не даёт. (3) RC4: при раннем выходе под замком (`m_recipes_path` пуст или 0 записей) строки нет — как прежде.
(4) Правило чтения п. 245(б) — у скорера/печати S3/S6: `wait_us` строк `pcw overlap gfx|cs` — время создания (верхняя граница), строк
`pcw overlap wait gfx|cs` — время ожидания GuestGpu; не складываются как ожидание.

## 2. Бинарь S6 — дерево `4fc501f4` + патч, без коммитов и веток

- **Патч:** `git diff ae704c5d 2ce6326e -- pc src/graphics/host_gpu/renderer/pipeline/pipelineCache.h` → KytyPS5 `docs/track-s/s5c/pcw_on_4fc501f4.patch`,
  sha256 **`752b9f1968ff7663262175bfe9a64a29798a1e29de49ef3164a73b970e6fed8f`** (`git apply --numstat`: `pipelineCache.cpp` +313/−13, `pipelineCache.h` +29/−1; = код S5a `e11a297b` + S5c `2ce6326e`).
  Наложен на дерево до коммита из рабочего дерева `main` (`pcw_pre.patch`); после коммита — тот же патч из коммита, `cmp` — байт в байт равен.
- **Дерево:** `git worktree add --detach C:/kyty/s288/wt_s5c 4fc501f4` (`HEAD` = `4fc501f4f6c3…`, ветки нет — `branch --show-current` пусто,
  коммитов нет); `git apply --check` и `git apply` — чисто (`C:/kyty/s288/s5c/mk_wt.sh`, `mk_wt.log`). Подмодули — гитлинки `4fc501f4` (=
  `HEAD`, сверено `git ls-tree`), содержимое — `git archive <гитлинк>` из локальных репозиториев подмодулей; `3rdparty/ffmpeg-core` — локальный
  `git clone --shared` на `94dde08` (его `CMakeLists.txt` берёт имя готовой сборки из `git rev-parse --short HEAD` своей папки; без `.git`
  получил `4fc501f4` и отказ конфигурации), архив `ffmpeg-94dde08.zip` скопирован из `C:/kyty/build/externals` (sha256 `5038087e…` равен), сети нет.
  FetchContent `xbyak`/`zydis` — уже скачанные `C:/kyty/build/_deps/*-src` (`44a72f36…`, `120e0e70…` = пины `3rdparty/CMakeLists.txt`).
- **Сборка:** `C:/kyty/s288/s5c/build_s5c.cmd` — флаги `build_local.cmd` (Release, ThinLTO, без лаунчера, `clang-cl`), каталог
  `C:/kyty/s288/build_s5c`; опции `CMakeCache` против `C:/kyty/build` различаются только путями и двумя `FETCHCONTENT_SOURCE_DIR_*`. В окружении
  агента нет `PROCESSOR_ARCHITECTURE` → `CMAKE_SYSTEM_PROCESSOR` пуст → `cpuinfo` без x86-исходников, отказ ссылки; скрипт ставит `AMD64` (как у
  `C:/kyty/build`), каталог сборки пересоздан с нуля.
- **Бинарь:** sha256 **`f3b3aa3bef3f0ceadf668d0fc8bd68230ab1e3158d87bbc0b4c66b92a6651ca3`**, копия `C:/kyty/s288/bin/kyty_emulator_f3b3aa3b.exe`;
  `KYTY_GIT_HASH` `4fc501f-dirty` (как у `9235a7ac`); в бинаре есть `S-pcw: KYTY_S_PCW`, `GcnDumpReg: skip type=`, `wait gfx`, `wait cs`, `hold_us=`,
  нет `KYTY_FIX_B26` и прежнего формата `… wait_us` строки рецептов. В папку эмулятора НЕ установлен; установленный `9235a7ac` не тронут.
- **Гейт подписи (способ S5a §5 — `KYTY_SHADER_SOURCE_HASH` сборки = строка в бинаре): `699c1e4b7db359067b461e029b913c4b6e78dc90` — ДА, но
  только после приведения окончаний строк — см. §3, вопрос Q1.**
- **Гейт «`git diff 4fc501f4` дерева — только два файла»:** по содержанию (`git diff --ignore-cr-at-eol 4fc501f4`) — 2 файла, 342/14, дифф совпадает
  с патчем (`wt_diff_stat_ignorecr.txt`); буквально (`git diff --stat 4fc501f4`) — 29 файлов: 2 + 27 файлов, отличающихся только CRLF (`wt_diff_stat.txt`).

## 3. Подпись транслятора и окончания строк

`C:/kyty/s288/s5c/sighash.py` повторяет `src/generate_version.cmake` (sha1 по sha1 файлов `src/graphics/shader/**/*.{cpp,h,inc}` + 3 файла,
сортировка по пути) и сверен с двумя сборками: чистый `4fc501f4` → `95d30c5c…` = первая сборка звена из LF-дерева (`build_lf.log`, бинарь
`c251eae4…`, перезаписан, в работу не идёт); рабочая копия `main` → `846a041a…` = подпись S5a. **`699c1e4b…` = содержимое `4fc501f4`, в
котором ровно те 27 файлов, что лежат в CRLF в рабочей копии `C:/kyty/KytyPS5` (`git ls-files --eol`: `i/lf w/crlf`), записаны в CRLF**
(список — `C:/kyty/s288/s5c/crlf27.txt`, sha256 `913f1d1f…`; все 27 после перевода байт в байт равны файлам рабочей копии `main`). Значит,
`9235a7ac` собран из рабочей копии с этими CRLF; подпись — свойство окончаний строк, не кода. В `wt_s5c` эти 27 файлов переведены LF → CRLF,
после чего пересборка дала `699c1e4b` (`kytyGitVersion.h` и строка в бинаре). Код компилятора от CRLF не меняется.

**Q1 лиду.** Буква п. 245(а) ставит два гейта, которые на этой машине одновременно буквально не выполнимы: подпись `699c1e4b` требует 27 файлов
в CRLF, а с ними буквальный `git diff --stat 4fc501f4` показывает 29 файлов. Правил «стоп» п. 245(а) — «патч не ложится» (лёг чисто) и
«правки вне двух файлов» (по содержанию их нет; CRLF — правка байтов). Другого кода не перенесено. Я не остановился, а собрал бинарь по
второму пути и выношу на приёмку: **вариант исполнителя — принять `f3b3aa3b`: гейт дерева читать по содержанию (`--ignore-cr-at-eol`),
CRLF-27 — воспроизведение состояния сборки `9235a7ac`, доказанное подписью.** Если не принято — альтернатива: бинарь из LF-дерева (подпись
`95d30c5c`, кэш трансляций после возврата `snap0` холодный — ровно то, против чего RC1); его собрать заново — 3 мин.

## 4. Тесты `shader_cfg_tests`

Бинарь тестов собран из того же дерева (`build_s5c.cmd tests`, sha256 `2bc87d73…`). A — `KYTY_S_PCW`/`KYTY_S_PCW_FORCE_MS`/`KYTY_DUMP_GCN` сняты;
B — `KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=15000 KYTY_DUMP_GCN=2`; оба `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`. 127 тестов в обоих, падает 1 —
`TestNewShaderRecompilerPixelImageSampleLodSelection` (2 проверки `IMAGE_SAMPLE_C`/`IMAGE_SAMPLE_C_LZ`, Б11), как у S5a и S5b. Логи A и B равны
байт в байт (sha256 `5a60758a…2f8f3f`, = лог F2a и S5a). **Падений при ручках не больше, чем при 0.** Тест тавтологичен для кода звена
(п. 245(е)): в бинаре тестов кода `PipelineCache` нет.

## 5. Не заявляется

Что код корректен под нагрузкой игры до S6; что запись кэша — причина Б33 (до A/B п. 241(з)(5)); что `=1` убирает кадры ≥ 100 мс; что 8 попыток
исключают `VK_INCOMPLETE`; что бинарь `f3b3aa3b` отличается от `9235a7ac` только кодом S-pcw сверх доказанного (дерево `4fc501f4` + патч, подпись,
опции сборки; побайтного сравнения сборок нет — сборки не воспроизводимы побайтно; строка `SDL_REVISION` в бинаре иная — подмодуль SDL2 без
`.git`, `git describe` берёт дерево Kyty: `SDL-KytyPS5-…-g4fc501f4` против `SDL-2.33.0-g4b69833` у `C:/kyty/build`); ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
