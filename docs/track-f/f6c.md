# Трек F, звено F6c (`HPP-375`): правка Б9а — V1, 16 функций `AudioPropagation` под `KYTY_FIX_B9A`, тест, бинарь

Автор — Emu Engineer. Критерий до кода — п. 287(в) (`38a28a9a:docs/ROADMAP.md:15029` «(в) **Критерий F6 (Б9а), до кода», контроль +1 — 15030
«(1) **Ручка `KYTY_FIX_B9A`**, **умол»); звено — п. 287(д) (`38a28a9a:docs/ROADMAP.md:15069` «(д) **Звенья (этим пунктом», контроль +1 — 15070
«`src/libs/libAudio.cpp` + тест, комм»); проект — `bed17fc0:docs/track-f/f6a-b9a.md` (§1, §3, §5). Время — UTC по строкам `C:/kyty/f287/times.txt`.
Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (проверка — первая строка каждой команды); `HPP-352` — `blocked` по API
(15:03:29Z, 15:08:59Z, перед сборкой тестов). Игра не запускалась; установленная `9235a7ac` не тронута (sha256 `9235a7ac61f1affb…` после звена).
Устройство Vulkan не создавалось (ни один из двух тестов его не создаёт) — п. 277(г) не задействован.

## 0. Итог

- **Коммит правки — `5f67f829d714b9f75204c74e0cc3692a08256550`** (`main`, родитель `378a869d`; `--only`, 3 файла). Не опубликован.
- **Бинарь — `C:/kyty/f287/bin/kyty_emulator_d8756dce.exe`, sha256 `d8756dce0662fb318a24a3fb52a3260d31ea84628372fa9a438ca46ed6a6e43d`**, 24 608 768 байт,
  версия `KytyPS5-2026-09-15-6a2987a-1784-g5f67f829`; сборка из чистого LF worktree на `5f67f829`. **Не установлен, дыма нет — WIP до F6d/F6e.**
- **Подпись трансляции `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`** — равна подписи родителя `378a869d` (строкой, счётом по
  блобам) и заголовку сборки; та же, что у бинаря отгрузки `dac02fb9` (FSa).
- Тесты: `audio_propagation_tests` — **210 проверок, 0 падений, `ALL OK`**; разрешение по NID при `=0` — **6 из 22**, при `=1` — **22 из 22**.
  `shader_cfg_tests` — **127 / 1 (Б11)**, лог равен логу FSa с точностью до одного `elapsed_ms`.
- `check_gate_order.py` — `GATE ORDER: clean`, вывод байт в байт = FSa (гейты и ручки не тронуты).

## 1. До кода (п. 287(в)(1)) — пересчёт своим скриптом на коммите правки

Скрипт `f6c/f6c_chk.py` (sha256 `6452c59a…`, кода F6a не импортирует; своя формула NID — контроль `sceKernelGetProcessTimeCounter` = `fgxnMeTNUtY`),
вывод `f6c/f6c_chk.out.txt` (`47d9f99e…`), **`F6C RECOUNT ALL OK`**. Источник `LIB_FUNC` — `git show 5f67f829:src/libs/libAudio.cpp`; «новая» —
`LIB_FUNC` внутри блока `if (fix_b9a)`; столбец F6a — таблица §1 `C:/kyty/f287/f6a/f6a-b9a.md`.

| GOT | NID | имя | хэш имени | `LIB_FUNC` на `5f67f829` | F6a §1 |
|---|---|---|---|---|---|
| 1233 | `XKCN4gpeYsM` | `sceAudioPropagationSystemUnregisterMaterial` | `XKCN4gpeYsM` | новая (`=1`) | не разрешён |
| 1234 | `VlBT16890mA` | `sceAudioPropagationSystemSetRays` | `VlBT16890mA` | новая (`=1`) | не разрешён |
| 1235 | `ZQXE-xS6MTE` | `sceAudioPropagationPortalDestroy` | `ZQXE-xS6MTE` | новая (`=1`) | не разрешён |
| 1236 | `kIdb+iQUzCs` | `sceAudioPropagationSystemSetAttributes` | `kIdb+iQUzCs` | прежняя | HLE |
| 1237 | `5vzOS2pHMFc` | `sceAudioPropagationSourceSetAudioPaths` | `5vzOS2pHMFc` | новая (`=1`) | не разрешён |
| 1238 | `aNEqtSHdUSo` | `sceAudioPropagationSystemCreate` | `aNEqtSHdUSo` | прежняя | HLE |
| 1239 | `CPLV6G-eXmk` | `sceAudioPropagationSystemRegisterMaterial` | `CPLV6G-eXmk` | прежняя | HLE |
| 1240 | `WXMhENV2NcA` | `sceAudioPropagationPortalSetAttributes` | `WXMhENV2NcA` | новая (`=1`) | не разрешён |
| 1241 | `b-dYXrjSNZU` | `sceAudioPropagationPortalCreate` | `b-dYXrjSNZU` | новая (`=1`) | не разрешён |
| 1242 | `S0JwP2AFTTE` | `sceAudioPropagationRoomDestroy` | `S0JwP2AFTTE` | новая (`=1`) | не разрешён |
| 1243 | `x5VPqg5iyAk` | `sceAudioPropagationSystemDestroy` | `x5VPqg5iyAk` | новая (`=1`) | не разрешён |
| 1244 | `d84otraxt2s` | `sceAudioPropagationSourceCreate` | `d84otraxt2s` | новая (`=1`) | не разрешён |
| 1245 | `-wsUTr31yeg` | `sceAudioPropagationSourceSetAttributes` | `-wsUTr31yeg` | новая (`=1`) | не разрешён |
| 1246 | `aKJZx7wCma8` | `sceAudioPropagationSourceGetRays` | `aKJZx7wCma8` | новая (`=1`) | не разрешён |
| 1247 | `7xyAxrusLko` | `sceAudioPropagationSystemQueryMemory` | `7xyAxrusLko` | прежняя | HLE |
| 1248 | `G+QLTfyLMYk` | `sceAudioPropagationSourceGetAudioPathCount` | `G+QLTfyLMYk` | новая (`=1`) | не разрешён |
| 1249 | `ht-QXT3zGxo` | `sceAudioPropagationSystemGetRays` | `ht-QXT3zGxo` | прежняя | HLE |
| 1250 | `wkseM3LWPuc` | `sceAudioPropagationSourceDestroy` | `wkseM3LWPuc` | новая (`=1`) | не разрешён |
| 1251 | `hhz9pITnC8k` | `sceAudioPropagationSourceRender` | `hhz9pITnC8k` | новая (`=1`) | не разрешён |
| 1252 | `eEeKqFeNI3o` | `sceAudioPropagationSourceGetAudioPath` | `eEeKqFeNI3o` | новая (`=1`) | не разрешён |
| 1253 | `8bI5h8req30` | `sceAudioPropagationRoomCreate` | `8bI5h8req30` | прежняя | HLE |
| 1254 | `PBcrVpEqUVY` | `sceAudioPropagationSourceCalculateAudioPaths` | `PBcrVpEqUVY` | новая (`=1`) | не разрешён |

Итог [c]: `LIB_FUNC` библиотеки — 22 (вне блока 6, в блоке 16), различных NID 22; у 22 из 22 NID = хэш имени; имя функции эмулятора = имя таблицы;
блок каждой строки совпадает со столбцом F6a (16 «не разрешён» — новые, 6 HLE — прежние). **16 новых:** `PortalCreate`, `PortalDestroy`,
`PortalSetAttributes`, `RoomDestroy`, `SourceCalculateAudioPaths`, `SourceCreate`, `SourceDestroy`, `SourceGetAudioPath`, `SourceGetAudioPathCount`,
`SourceGetRays`, `SourceRender`, `SourceSetAttributes`, `SourceSetAudioPaths`, `SystemDestroy`, `SystemSetRays`, `SystemUnregisterMaterial`
(все с префиксом `sceAudioPropagation`).

**Файлы диффа `378a869d..5f67f829`:** `CMakeLists.txt` (+4: цель `audio_propagation_tests`), `src/libs/libAudio.cpp` (+280), `tests/AudioPropagationTests.cpp`
(новый, 434 строки). **В `src/` — только `src/libs/libAudio.cpp`** [c]. От коммита FSa `95eec776` до `5f67f829` по `src/` и `CMakeLists.txt` — только этот
коммит: бинарь F6c = дерево бинаря отгрузки `dac02fb9` + F6c.

**Подпись трансляции** (правило `src/generate_version.cmake`: SHA-1 списка SHA-1 файлов `src/graphics/shader/**/*.{cpp,h,inc}` + 3 файла, по сортировке
путей) — родитель `378a869d`: `56189185f9e9f9a0ea5174f3f85206e6d099db3d` (101 файл); коммит `5f67f829`: `56189185…` (101); заголовок сборки
`f6c/build/kytyGitVersion.h`: `56189185…`; в exe — 1 раз. Транслятор не тронут.

## 2. Правка (`src/libs/libAudio.cpp`)

**Ручка `KYTY_FIX_B9A`, умолчание 0** — `Common::EnvFlagOn` (значение: `0/false/off/no` и незаданная — выкл.), читается при регистрации библиотеки
(`5f67f829:src/libs/libAudio.cpp:372` «const bool fix_b9a = Common::EnvFlagOn("KYTY_FIX_B9A");», контроль +1 — 373 «g_b9a_enabled.store(fix_b9a,»).

- **`=0`:** 16 `LIB_FUNC` блока `if (fix_b9a)` не исполняются — NID не попадают в базу символов, импорт идёт на прежний переходник
  (`Unresolved import stub called`); строк `FixB9a: on` и `AudioPropagation: calls` нет; `B9aCount` возвращается первой строкой, `g_b9a_handles` не растёт.
  Прежние 6 HLE: их выходы и возврат прежние, добавлен только вызов `B9aCount` перед `return 0` (при `=0` — пустой). Поведение и лог — прежние [c по коду;
  в игре — контроль `=0` F6e].
- **`=1` (V1, п. 287(в)(2)):** 16 функций, все возвращают 0, каждая пишет `PRINT_NAME()` (как прежние 6):
  - `PortalCreate(system, options, Handle* out)`, `SourceCreate(system, Handle* out)` — `*out = AudioPropagationNextHandle()` (общий счётчик, ненулевой,
    уникальный); `out == nullptr` — без записи.
  - `SourceGetAudioPathCount(source, uint32_t* count)`, `SourceGetRays(source, rays, uint32_t* count)` — `*count = 0` (лучи не трогаются); `nullptr` — без записи.
  - `SourceGetAudioPath(source, index, out)`, `SourceRender(system, render, n)` — выход не трогают.
  - `PortalSetAttributes`, `SourceSetAttributes`, `SystemSetRays`, `SourceSetAudioPaths` (handle, указатель, число), `SourceCalculateAudioPaths`
    (6 аргументов по месту вызова `0xf52328`), `PortalDestroy`, `RoomDestroy`, `SourceDestroy` (system, handle), `SystemDestroy` (system),
    `SystemUnregisterMaterial` (handle) — только возврат 0. Регистры аргументов сверены с `C:/kyty/f287/f6a/dis_*.txt` (`PortalCreate` — `rdx = this+0x10`,
    `SourceGetRays` — `rdx = this+0x23c0`); имена непрочитанных аргументов — [I].
  - Строка `FixB9a: on` — один раз при регистрации (член исполнителя [I], положительный контроль ручки для харнесса; вердикта не задаёт).
- **Счётчик (п. 287(в)(3), только `=1`):** строка
  `AudioPropagation: calls total=<n> handles=<h> SystemUnregisterMaterial=<..> SystemSetRays=<..> PortalDestroy=<..> SystemSetAttributes=<..>
  SourceSetAudioPaths=<..> SystemCreate=<..> SystemRegisterMaterial=<..> PortalSetAttributes=<..> PortalCreate=<..> RoomDestroy=<..> SystemDestroy=<..>
  SourceCreate=<..> SourceSetAttributes=<..> SourceGetRays=<..> SystemQueryMemory=<..> SourceGetAudioPathCount=<..> SystemGetRays=<..> SourceDestroy=<..>
  SourceRender=<..> SourceGetAudioPath=<..> RoomCreate=<..> SourceCalculateAudioPaths=<..>` (одна строка, порядок — слоты GOT 1233…1254, как §1).
  Печать — когда вызов функции первый для неё или суммарный номер вызова библиотеки кратен 256. Счёт — после записи выходов (handle первого `SourceCreate`
  уже в `handles`). `handles` — все handle, выданные `AudioPropagationNextHandle` при `=1` (включая System / Room / Material прежних HLE).
  Частота `SourceCreate` на удержании — разностью полей `SourceCreate` двух строк (форма п. 287(в)(3)); строк при 1,5 вызова на кадр — ≈ одна на 40–60 кадров [I].

**Состояние и его жизненный цикл** (правило отчёта правки с флагом / счётчиком):

| состояние | установка | снятие | довод |
|---|---|---|---|
| `g_b9a_enabled` (`atomic_bool`, `:82`) | `:373` — при каждой регистрации `InitAudio_1_AudioPropagation` (эмулятор — один раз, `emulator.cpp` → `Libs::InitAll`; тест — дважды, `=0`, затем `=1`) | не снимается | флаг процесса; читается `B9aCount` (`:101`) и `AudioPropagationNextHandle` (`:130`) relaxed; запись — до потоков гостя (регистрация до загрузки игры) |
| `g_b9a_calls[22]`, `g_b9a_total`, `g_b9a_handles` (`:83–85`) | `fetch_add` в `B9aCount` (`:105–106`) и `NextHandle` (`:131`), только при `g_b9a_enabled` | не снимаются | накопленные за процесс по смыслу п. 287(в)(3); ранних выходов с половиной состояния нет — каждая из 22 функций зовёт `B9aCount` одной строкой перед своим единственным `return 0` |

Выходы функций: у каждой из 22 — один `return 0`, `B9aCount` стоит перед ним; ветвей ошибки нет. Строка счётчика собирается из relaxed-чтений —
при вызовах из нескольких потоков (поток звука для `SourceRender` [I]) поля одной строки могут отличаться на вызовы, идущие одновременно; суммы
следующих строк точны.

Хук теста `AudioPropagationB9aCounterForTest(uint32_t)` (`:114–126`) — чтение счётчиков, игрой не вызывается (NID у него нет).

## 3. Тест (п. 287(в)(4))

`tests/AudioPropagationTests.cpp`, цель `add_kyty_full_emulator_test(audio_propagation_tests …)`; Config + Log (тихий), без устройства Vulkan и без игры.
Разрешение — через ту же базу символов, что у загрузчика: `Libs::InitAudio_1(&db)` → `SymbolDatabase::Find` (полное имя `NID[AudioPropagation_v1][AudioPropagation_v1.0][Func]`)
и `FindByNid` (должны совпасть); вызов — указатель `vaddr` с `KYTY_SYSV_ABI`.

- `=0` (`_putenv_s`): 6 из 22 разрешаются, ровно прежние 6; 16 — нет; вызов прежнего `SystemCreate` — счётчики (22 + total + handles) остаются 0.
- `=1`: 22 из 22; все возвращают 0; `PortalCreate` и `SourceCreate` — `*out != 0`, два вызова дают разные значения, отличны от handle системы;
  `SourceGetAudioPathCount` (вход 7) и `SourceGetRays` (вход 6) — `*count == 0`, буфер лучей цел; сторожевые байты 0xA5 (256 байт вокруг выхода) целы
  у всех выходов, кроме записанного слота; `SourceRender` — выход, на который указывает дескриптор, и сам дескриптор целы; все `SetAttributes`,
  `SetRays`, `SetAudioPaths`, `CalculateAudioPaths`, `GetAudioPath` — буферы целы; нулевые указатели (`out`, `count`, буферы) — без падения;
  `Destroy` × 4 и `UnregisterMaterial` — 0; счётчик каждой из 22 функций, `total` (36) и `handles` (7) равны числу сделанных вызовов.

Вывод (`f6c/aptests.log`, `e5becea4…`):

```
AudioPropagationTests: KYTY_FIX_B9A=0 resolved 6 of 22
AudioPropagationTests: KYTY_FIX_B9A=1 resolved 22 of 22
AudioPropagationTests: KYTY_FIX_B9A=1 calls 36 handles 7
AudioPropagationTests: checks 210, failures 0
ALL OK
```

`shader_cfg_tests` (worktree, ни одной переменной `KYTY_*` в окружении, кроме `KYTY_TESTS_CONTINUE`/`KYTY_TESTS_VERBOSE`): **127 тестов, падение 1 — Б11**
(`IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`), rc 0; лог `f6c/cfgtests.log` (`aa122df9…`) равен `C:/kyty/f287/fsa/cfgtests_defaults.log` (`a074f1b3…`) во всех
134 строках, кроме одного `elapsed_ms` (24 против 19). Дельта падений — 0.

Не проверено тестом: строка лога (текст и момент печати) — Log в тесте тихий; формат — §2, проверяется скорером F6e.

## 4. Сборка

- Worktree `C:/kyty/f287/f6c/wt` — `git worktree add --detach` на `5f67f829` с `core.autocrlf=false` (`f6c/mk_wt_f6c.sh` — копия `fsa/mk_wt_fsa.sh` с путём);
  подмодули — как FSa; `git status --short` — 0 строк; файлов `src/` с байтом CR — 0 из 452 (`f6c/mk_wt.log`).
- Сборка — `f6c/build_f6c.cmd` (копия `fsa/build_fsa.cmd`: два пути и цель `audio_propagation_tests` в `tests`; флаги `build_local.cmd`), папка
  `C:/kyty/f287/f6c/build`: configure + build rc 0 (15:08:59Z–15:11:53Z), тесты rc 0 (с 15:12Z).
- Бинарь — §0; копия в `C:/kyty/f287/bin/` сверена по sha256. Строки в exe: `AudioPropagation: calls total=` 1, `FixB9a: on` 1, `KYTY_FIX_B9A` 1,
  подпись `56189185…` 1, `KYTY_FIX_DUALSRC` 1.
- **Умолчания бинаря — как у бинаря отгрузки `dac02fb9`** (FSa): `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC` = 1; `KYTY_FIX_B9A`, `KYTY_FIX_MINIMIZE` = 0.
  Подпись трансляции `56189185` ≠ `699c1e4b` установленной `9235a7ac` — у бинаря F6c кэш трансляции холодный против установленного (как у `dac02fb9`).

## 5. Вопросы лиду

1. **База K3 и подпись.** Бинарь F6c несёт умолчания отгрузки (`KYTY_FIX_DUALSRC=1`, `KYTY_FIX_B1B=1`) и подпись `56189185`, а база п. 287(в)(5) —
   `c142_03` / `v144_13` / `v143_03` на `9235a7ac` (подпись `699c1e4b`). Вариант исполнителя: сравнение K3 — по максимуму «база или контроль `=0` этой серии»,
   как записано; контроль `=0` на том же бинаре закрывает разницу умолчаний; харнессу F6e — копия и возврат кэшей трансляции по образцу FSc (каталог варианта
   `variant_fixb26_fixb1b`). Член исполнителя [I], вердикта не задаёт.
2. **Строка `FixB9a: on`** — сверх пункта (положительный контроль ручки). Вариант исполнителя: скорер F6e требует её 1 раз при `=1` и 0 при `=0`; решение — лиду.
3. **Хук теста `AudioPropagationB9aCounterForTest`** — внешняя функция без NID в бинаре; вариант исполнителя — оставить (тест счётчика без игры).

## 6. Не заявляется

Что игра при `=1` не падает и не зависает на проснувшихся путях (R1 — входы F6e); что строка счётчика печатается с нужной частотой в игре; что звук
верен или слышимо изменится; что бинарь при `=0` поведенчески равен `dac02fb9` в игре (по коду — да; прогон — контроль `=0` F6e); что 12 невызванных
функций не вызываются на других уровнях; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.

## 7. Файлы

`C:/kyty/f287/f6c/` (копия в `docs/track-f/f6c/`): `patch_f6c.py` (`5d97d894…`), `f6c_chk.py`, `f6c_chk.out.txt`, `gate_order.out.txt` (`42d78aa8…`),
`mk_wt_f6c.sh`, `mk_wt.log`, `build_f6c.cmd`, `aptests.log`, `cfgtests.log`. Сборочная папка и worktree — только локально.
