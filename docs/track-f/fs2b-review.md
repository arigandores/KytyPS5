# Трек F, звено FS2b (`HPP-382`, Red Team): ревью второго бинаря отгрузки трека F (FS2a, `HPP-381`)

**Вердикт: PASS_WITH_FIXES.** Код `9c9d86ae` и бинарь `bbad499c` принимаются как есть (правок кода и пересборки нет); RC 1 — строка отката в
пункте установки FS2d (владелец — лид), FS2c не блокирует. Замечаний 4 (N1–N4).

Основание — `1452ddc8:docs/ROADMAP.md:15495` «(в) **Отгрузка умолчания — FS2» (контроль +1 — 15496 «идёт на `dac02fb9` — перепечатка FSc»); форма
ревью — `dc44ddc5:docs/ROADMAP.md:14756` «(2) **FSb (Red Team)** — ревью FSa» (контроль +1 — 14757 «чистого worktree — sha и подпись совпадают»);
прочтение (3) — `dc44ddc5:docs/ROADMAP.md:14980` «подтверждает бинарь, если (i)» (контроль +1 — 14981 «кроме `.data`/`.reloc`»); член Б9а —
`dc44ddc5:docs/ROADMAP.md:18094` «(г) **Отгрузка — FS2 (п. 298(в))» (контроль +1 — 18095 «проверяет член (4) своего задания»). Вход: отчёт FS2a
`dc44ddc5:docs/track-f/fs2a.md`, коммит `9c9d86ae`, копия `C:/kyty/f287/bin/kyty_emulator_bbad499c.exe`. Пункты п. 228, 273(е), 282(г), 286, 295(б), 296,
298, 327 прочитаны на KytyPS5 `dc44ddc5` до первого действия (строка `times.txt` 17:32:38Z). Время — UTC по строкам «HPP-382 FS2b» `C:/kyty/f287/times.txt`
(17:32:38Z–17:44:02Z, конец — строкой сдачи). Игра не запускалась; процессов с устройством Vulkan нет; установленный exe — `dac02fb9…` до и после;
замка и `STOP` нет в каждой команде; `HPP-352` — `done` по API перед сборкой (17:35:29Z); комментариев звена — 0.

## 1. Разность коммита по `src/` (член (1))

- `git diff 2e6cfec2 9c9d86ae` — 2 файла, +13 / −8, только `src/`: `swapchain.cpp` и `libAudio.cpp`. Прочитаны целиком (`fs2a/fs2a_diff.patch` = мой вывод).
- **Только чтения умолчаний названных ручек:** `KYTY_FIX_MINIMIZE` (`9c9d86ae:src/graphics/presentation/window/swapchain.cpp:311` «`const char* value =
  std::getenv("KYTY_FIX_MINIMIZE");`», +1 — 312 «`const bool  on    = value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);`») и `KYTY_FIX_B9A`
  (`9c9d86ae:src/libs/libAudio.cpp:374` «`const char* fix_b9a_value = std::getenv("KYTY_FIX_B9A");`», +1 — 375 «`const bool  fix_b9a       = fix_b9a_value
  == nullptr || …`»); прочее — комментарии. Форма = FSa (`9c9d86ae:src/graphics/presentation/window/vulkanWindow.cpp:666`, 667).
- **`=0` — прежний путь [c-код]:** прежнее чтение — `Common::EnvFlagOn(name)` = `EnvValueOn(std::getenv(name))` (`9c9d86ae:src/common/envFlag.h:35`, +1 — 36
  «`return EnvValueOn(std::getenv(name));`»). Новое выражение отличается от прежнего только при `value == nullptr` или `value[0] == '\0'` (прежнее — 0, новое —
  1); при любой непустой строке оба равны `EnvValueOn(value)`; `0/false/off/no` (без учёта регистра, точное совпадение) — 0 в обоих. Значение пишется в те же
  места, что у F5a / F6c (статический `enabled` в `FixMinimizeEnabled()`, `g_b9a_enabled`); нового состояния нет.
- **Чтений каждой ручки — по одному** (`fs2b/readers.out.txt`, `git grep` на `9c9d86ae` по `src/`, `tests/`, `CMakeLists.txt`): `KYTY_FIX_MINIMIZE` — только
  `swapchain.cpp:311` (5 мест использования через `FixMinimizeEnabled()`), `KYTY_FIX_B9A` — только `libAudio.cpp:374` (+ тест, ставит `0`/`1` явно). Расщепления
  умолчания между двумя читателями нет.
- Против FS: `git diff --stat 95eec776 9c9d86ae -- src/` — `swapchain.cpp` (FS2a) и `libAudio.cpp` (F6c `5f67f829` + FS2a); `git log 95eec776..9c9d86ae -- src/` —
  ровно `5f67f829`, `9c9d86ae`. `src/graphics/shader/**` не менялся.

## 2. Таблица умолчаний своим сканером (член (2))

`fs2b/knobs_fs2b.py 9c9d86ae` (порт моего `knobs_fsb.py` FSb, кода FS2a не импортирует; класс умолчания — по тексту оператора чтения в вершине; вывод
`knobs_fs2b.out.txt`): дифф `git diff --ignore-cr-at-eol 4fc501f4 9c9d86ae -- src/` — 47 файлов, +7 580 / −130 (= FS2a); строк с вызовом чтения окружения
добавлено 14 (9 вызовов `getenv` + продолжения), удалено 0; имён `KYTY_*` на строках `+`/`−` — 29: 18 в коде (= FS2a), 7 только в комментариях, 4 — макросы
(`KYTY_CLASS_NO_COPY`, `KYTY_PLATFORM`, `KYTY_PLATFORM_WINDOWS`, `KYTY_SYSV_ABI`); строк `KNOB_DEFINITIONS` добавлено 9 (`fallback` 0), удалено 0.

| класс (мой сканер) | ручки |
|---|---|
| ON-IF-UNSET (`== nullptr \|\|` … `EnvValueOn` в одном операторе) | `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_B9A` |
| OFF-IF-UNSET | `KYTY_S_PCW` (`!= nullptr && == "1"`), `KYTY_TEST_MINIMIZE` (`== nullptr` → выход без стенда), `KYTY_DUMP_GCN` `:1254`, `:1298` |
| UNDECIDED сканером → руками OFF | `KYTY_DUMP_GCN` `:3593` (`const auto* value` — регекс сканера не берёт `auto`; `value != nullptr && value[0] != '0'`), `KYTY_S_PCW_FORCE_MS` (`value != nullptr ? strtoul : 0u`) |
| TABLE `fallback` 0 | `KYTY_PROT_CEILING`, `KYTY_ARM_IN_COPY`, `KYTY_ARM_INLINE`, `KYTY_ARM_LOSS_WIN`, `KYTY_DISP_CEILING`, `KYTY_REBIND_CENSUS`, `KYTY_B2_REUSE`, `KYTY_REBIND_SLOW_CENSUS`, `KYTY_BIND_LEAN` |

**Умолчание 1 — ровно `KYTY_FIX_B26`, `KYTY_FIX_B1B`, `KYTY_FIX_DUALSRC`, `KYTY_FIX_MINIMIZE`, `KYTY_FIX_B9A` = таблица FS2a §3 и состав п. 298(в).**
Прежних чтений, изменённых диффом, — 0. `check_gate_order.py --src C:/kyty/f287/fs2b/wt/src` — `GATE ORDER: clean`, вывод байт в байт = FS2a.

## 3. Своя сборка и подтверждение бинаря по п. 286(б) (член (3))

- Worktree `C:/kyty/f287/fs2b/wt` — `git worktree add --detach` на `9c9d86ae`, `core.autocrlf=false` (`fs2b/mk_wt_fs2b.sh` — мой `mk_wt_fsb.sh` с путём);
  `git status --short` 0 строк; файлов `src/` с CR — 0 из 452 (`fs2b/mk_wt.log`). Сборка `fs2b/build_fs2b.cmd` (мой `build_fsb.cmd` с путями,
  `audio_propagation_tests` в `tests`): configure и build rc 0 (17:35:29Z–17:38:07Z). Свой бинарь — sha256 `2255a45f388ef4b6…3bc`, 24 609 280 байт;
  **в `bin/` не кладётся.**
- `fs2b/bincmp_fs2b.py` (вывод `bincmp.out.txt`, `BINCMP ALL OK`): копия `bin/kyty_emulator_bbad499c.exe` — sha256 `bbad499c56b744df…eb55` = отчёту FS2a
  (и = выходу сборки FS2a `fs2a/build/install`).
  **(i)** `kytyGitVersion.h` без комментариев — 12 строк, равны (`fs2b/build` против `fs2a/build`); `KYTY_SHADER_SOURCE_HASH` = `56189185f9e9f9a0ea5174f3f85206e6d099db3d`
  (= FS), в каждом exe — 1 раз ✓.
  **(ii)** секции те же 8 по порядку; одной длины все, кроме `.data` (36 579 168 / 36 579 488, −320) и `.reloc` (41 900 / 41 912) ✓.
  **(iii)** `.text` 18 113 558 байт: 61 110 серий различий, длины 1–3 байта (25 / 60 802 / 283), ни одной > 4; дельта 32-битного смещения −320 у 61 050, прочие 17 дельт —
  кратные 16 в пределах 320 и 5 серий «−1» (второй байт смещения, как у FSb); профиль — зеркальный FSb (`fsb/textcmp.out.txt`: +320 у 60 726, те же 18 дельт).
  Строки `.rdata` 29 601 = 29 601, `.data` 782 = 782 после замены пути worktree и маски `?A0x…`; единственное различие — запись PDB (`…LLD PDB.` + GUID) ✓.
  **Бинарь `bbad499c` подтверждён по прочтению п. 286(б).** Первый прогон сравнения дал `FAILED` из-за моего фильтра записи PDB (искал `.pdb`, запись — строка
  `LLD PDB.`); фильтр исправлен, вывод первого прогона сохранён (`bincmp.run1_filter_defect.out.txt`, строка `times.txt` 17:39:03Z).

## 4. Путь `=1` по умолчанию = путь F5c и F6c при `=1` (член (4))

`fs2b/patchid.out.txt`:
- **F5 (Б37):** patch-id `d2811535` = `c723e5ae` = `b6608c04…`, `01ca15d1` = `af7e5ff9` = `ec4d3478…` (вершина `af7e5ff9` = дерево бинаря F5c `6f495a65` по
  `C:/kyty/f287/FACTS.md` F5a2 / F5b2). Файлы F5 (`window.h`, `swapchain.cpp`, `window.cpp`, `testMinimizeLine.h`, `libC.cpp`) после `01ca15d1` менял только
  `9c9d86ae`; `git diff --ignore-cr-at-eol af7e5ff9 9c9d86ae` по этим файлам = `git diff 01ca15d1 9c9d86ae` — один файл `swapchain.cpp`, +6 / −4, ровно хунк FS2a
  (чтение + комментарий). ⇒ при умолчании (= `1`) код F5a + F5a2 тот же, что в `6f495a65` при `=1` ✓.
- **Б9а в бинаре — да** (`KYTY_FIX_B9A` 0 → 1 по п. 327(г)). `libAudio.cpp` после `5f67f829` (F6c, бинарь `d8756dce` собран из чистого LF worktree на этом коммите) менял
  только `9c9d86ae`; `git diff 5f67f829 9c9d86ae -- src/libs/libAudio.cpp` — +7 / −4, чтение + комментарии ⇒ путь при умолчании = путь F6c при `=1` ✓.
  Прочие различия деревьев (F3b, F4, FSa и др. против `6f495a65`) — вне путей F5/F6, их умолчания — §2.

## 5. Тесты своим прогоном (член (5))

Своя сборка, окружение без единой `KYTY_*` (проверено: список снятых переменных пуст), кроме `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1` у `shader_cfg_tests`:
- `shader_cfg_tests` — 127 тестов, rc 0, падает 1 — `TestNewShaderRecompilerPixelImageSampleLodSelection` (Б11: `IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ`); лог после
  нормировки `elapsed_ms` и пути = FS2a = FSb (`7cf25859…`, `fs2b/cfgcmp.out.txt`) ✓.
- `audio_propagation_tests` — `checks 210, failures 0`, `ALL OK`, rc 0; лог = FS2a (`9919aa66…`) ✓.

## 6. Требуемые изменения

**RC1 (владелец — лид, строка установки FS2d `HPP-384`; FS2c не блокирует).** Откат переменными окружения назван в п. 298(д) одной ручкой —
`dc44ddc5:docs/ROADMAP.md:15511` «(д) **Установка FS2 — звеном FS2d (лид):**» (контроль +1 — 15512 «FS2 по sha256, откат — копия `dac02fb9` или
`KYTY_FIX_MINIMIZE=0`»); п. 327(г) добавил в FS2 второе умолчание (`KYTY_FIX_B9A`), а строку отката не тронул. **Сценарий отказа:** после установки FS2
на уровне, зовущем `AudioPropagation` (`timestop_casino`, `mini_astro_clock_tower`), появляется смерть или зависание; откат по букве п. 298(д) —
`KYTY_FIX_MINIMIZE=0` — оставляет 16 NID Б9а зарегистрированными (умолчание `KYTY_FIX_B9A` — 1), дефект воспроизводится «на откате», и разбор ложно снимает
подозрение с FS2. Путь `dac02fb9` переменными даёт только пара `KYTY_FIX_MINIMIZE=0 KYTY_FIX_B9A=0` [c-код: §1 — при обоих `=0` код F5 и F6 сводится к
прежнему; иных отличий `src/` от `95eec776` нет]. **Изменить:** в строке установки FS2d назвать откат «копия `dac02fb9` по sha256 или
`KYTY_FIX_MINIMIZE=0` + `KYTY_FIX_B9A=0`» (и откат одной ручкой — только для своей строки реестра).

## 7. Замечания (не RC)

- **N1 (FS2c, к сведению).** Ни один тест не исполняет путь «переменная не задана» для `KYTY_FIX_B9A` (тест ставит `0`/`1` явно) и для `KYTY_FIX_MINIMIZE`;
  умолчание доказано кодом (§1) и в игре — положительными контролями печати: `FixB9a: on` ровно 1 (п. 327(г)(1)) и `FixMinimize: on` (п. 298(г)(1)).
  Расхождение этих строк в `fs2_w`/`fs2_v`/`fs2_t` — дефект формы тега или бинаря, а не «ручка выключена».
- **N2 (Emu Engineer, стиль, без сценария отказа в поведении).** Комментарии `9c9d86ae:src/graphics/presentation/window/swapchain.cpp:342`, `:379`, `:949`, `:957`
  и `libAudio.cpp:211` говорят «`KYTY_FIX_MINIMIZE=1`» / «`KYTY_FIX_B9A=1`» — после FS2a это «ON (по умолчанию)»; на код не влияет, правки не требую.
- **N3 (Emu Engineer, процесс).** В отчёте FS2a время конца — «17:2xZ» (`dc44ddc5:docs/track-f/fs2a.md`, первая строка основания), а не время `date -u`;
  в строках `times.txt` оно есть (17:23:43Z, 17:23:54Z). Цифры не меняются.
- **N4 (свой процесс).** Скрипт сборки первой попыткой писался heredoc-ом с обратными слэшами — запись не состоялась (assert), файл записан Write и
  перенесён командой с проверкой замка; `mk_wt_fs2b.sh` той же командой записан верно (обратных слэшей в нём нет). Первый прогон `bincmp` — дефект моего
  фильтра (§3).

## 8. Чек-лист

Разность — только чтения названных ручек ✓; `=0` — прежний путь (буква `EnvFlagOn` ≡ новая форма при непустом значении) ✓; одно чтение на ручку ✓;
умолчание 1 — ровно пять ручек п. 298(в) ✓; `check_gate_order` clean ✓; `src/graphics/shader/**` не менялся — подпись `56189185` = FS, кэш трансляции
`variant_fixb26_fixb1b` годится ✓; своя сборка — (i)–(iii) п. 286(б) ✓, копия в `bin/` не положена ✓; F5 patch-id ✓, F6c дифф ✓; `shader_cfg_tests` 127 / 1 (Б11) ✓,
`audio_propagation_tests` ALL OK ✓. Нового состояния (таблиц, LRU, эпох) правка не вводит — таблица мест записи не требуется.

**Не доказано этим звеном:** поведение бинаря при умолчаниях в игре (FS2c); что без правки свёрнутое окно никогда не ведёт к крэшу; что звук верен; корректность
любой сцены и проходимость до конца; что `.text` различия — именно RIP-relative (метод — дельта 32-битного окна, как FSb, без дизассемблера); ни одно
число — не выигрыш; 60 FPS не обещаются.

Файлы — `C:/kyty/f287/fs2b/`, копии в `docs/track-f/fs2b/`: `knobs_fs2b.py`, `knobs_fs2b.out.txt`, `readers.out.txt`, `patchid.out.txt`, `mk_wt_fs2b.sh`, `mk_wt.log`,
`build_fs2b.cmd`, `bincmp_fs2b.py`, `bincmp.out.txt`, `bincmp.run1_filter_defect.out.txt`, `cfgtests_defaults.log`, `audio_propagation_tests.log`, `cfgcmp.out.txt`,
`gate_order.out.txt`.
