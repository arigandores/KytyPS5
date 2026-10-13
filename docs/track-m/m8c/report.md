# Трек M, звено M8c (`HPP-860`, Emu Engineer): кандидат MS2. Издание 2: сборка, подпись, G1, G2, таблица умолчаний

Основание: `ROADMAP.md` «СЕССИЯ 122» п. 778(д), (ж) (KytyPS5 `1ffda330`), п. 783 (KytyPS5 `1f9de46b`), п. 786 (KytyPS5 `7b905f91`,
вариант (А) подписи). Игра не запускалась, замок не брался, бинарь **не установлен**. ГП-кейсы не исполнялись (новых `DeviceLost` 0).
Сборки — `--parallel 2`, процессы и дочерние — `IDLE_PRIORITY_CLASS` (`lowrun.py`). Время событий — `times.txt` (UTC по `date -u`).
**WIP до M3a2 / M3b2** (G3–G7 — прогоны Harness Engineer под замком). Издание 1 (шаг 0 и стоп) — §1–§2 без изменений по существу.

## 0. Итог

| Что | Значение |
|---|---|
| Бинарь MS2 | `C:/kyty/m657/bin/kyty_emulator_c630327b.exe`, sha256 `c630327bc2a3d9ce13c75edb5d64621d594541dafa7d4a5e97a86b95ba6e7bdf` (= `C:/kyty/m657/m8c/build/install/kyty_emulator.exe`) |
| HEAD worktree | `3504ecbced75f64a4a5dbfde85d672f7113c0a86` (`C:/kyty/m657/m8c/wt`, отсоединённый; ссылка `refs/archive/wt/3504ecbc…`) |
| Строка версии | `KytyPS5-2026-09-15-6a2987a-1940-g3504ecbce` (2 вхождения в exe) |
| Хэш исходников транслятора | `0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5` (п. 786(а)) |
| **Член п. 786(д)** — подпись, напечатанная кодом | `--m-wave1-cache` при умолчаниях: `KytySC3:0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5:fixb26:fixb1b:fixf10:fixf19:mw1_3b` = строке п. 786 ✓ (`cachechk.out.txt`, `ALL OK`) |
| Каталог варианта при умолчаниях | `_ShaderCache\PPSA21564\variant_fixb26_fixb1b_fixf10_fixf19_mw1_3b` — новый, первый вход холоден (член G3) |
| `check_gate_order.py` | `GATE ORDER: clean`; вывод = M7a байт в байт (`gate_order_wt.out.txt`) |
| G1 | `shader_cfg_tests` 136 тестов, 0 падений при `d` и `z` (база MS1 — 0) ⇒ ⊆ ✓; `matched=3`, `matched=8` при умолчаниях ✓; стенд T125 `ALL OK`; стенд `MWave2DiagStand` `ALL OK` при `KYTY_M_T125=0` (§3, строка RC2) |
| G2 корпус T1 | `corpus_m8c.py` — `ALL OK`: `z` = FS15 269/269; умолчания MS2 ≠ умолчаниям MS1 ровно в `ps_5a34b303…`, `ps_f47c0c09…`; член п. 775(г)(2) ✓ |
| Строки exe | `binary_m8c.py` — `ALL OK` |

## 1. Шаг 0 — RC3 M8b (п. 783(г)) — издание 1

Правка `MaxDiff` в `tests/MT125Stand.cpp` (неконечный отсчёт ⇒ `+inf`): `main` `1ba722f4`, worktree MS2 `fe26f280`, `git diff --name-only` —
один файл. Стенд `ALL OK` на `main` и MS2 (59 членов на плечо); мутанты m1–m4, m9 — `CAUGHT`, контроль `ALL OK` на обоих деревьях
(`stand_main.out.txt`, `stand_wt.out.txt`, `mut_m8c_main.out.txt`, `mut_m8c_wt.out.txt`). `libAudio2.cpp` и бинарь эмулятора шагом 0 не
менялись. Ревью шага 0 — стадия review лида.

## 2. Состав MS2 и подпись

| Коммит MS2 | Источник | patch-id `--stable` |
|---|---|---|
| `3d227024` | база M6a3 (= MS1 `ed94b13d` + `6964a58f`, `97198ce9`, `3d227024`) | — |
| `6c795c57` | T306 `91a46dc5` (M7a; `main` `95ad0de2`) | `15dfad37…` = источнику |
| `de23ec44` | T125 `6da84361` (M8a; `main` `206cdbce`) | `97e3d213…` = источнику |
| `fe26f280` | шаг 0, `main` `1ba722f4` | `d4659e58…` = источнику |
| `3504ecbc` | умолчания MS2 (2 файла): `ShaderDecoder.cpp` `default_on[] = {true, true, false, true, true, true}` (маска `0x33` → `0x3b`); `libAudio2.cpp` `MT125On` — форма `MT231On` (не задана или пусто = 1, `0/false/off/no` = 0, иное — `EnvValueOn`) | новый, только в worktree; в `main` умолчание 0 до M4 |

MS1 `ed94b13d` — предок HEAD ✓; дифф `ed94b13d..3504ecbc` — 19 файлов, строк с `KYTY_FIX_` / `KYTY_S_` в изменённых строках `src/` — 0.
Новых TLS, полей и счётчиков коммит умолчаний не вводит: значения — `static const` процесса.

Хэш исходников транслятора — `0d2da32c…` (своим пересчётом в издании 1; без коммита умолчаний — `baeea6e2…`). По п. 786 принят вариант (А).
**Член п. 786(д)** — `shader_recompiler_compute_tests --m-wave1-cache` той же сборки и того же `kytyGitVersion.h` (exe `e27b40e0…`; режим
только строит ключ кэша, кейсов ГП не исполняет), по своей папке `cwd` на плечо (`cachechk_m8c.py`):

| Плечо | Окружение | Маска | Подпись | Каталог |
|---|---|---|---|---|
| `d` | все `KYTY_*` сняты | `0x3b` | `KytySC3:0d2da32c…:fixb26:fixb1b:fixf10:fixf19:mw1_3b` ✓ | `variant_fixb26_fixb1b_fixf10_fixf19_mw1_3b` ✓ |
| `e` | явные `=1` T234/T233/T306/T032/T203, `=0` T256 | `0x3b` | та же ✓ | тот же ✓ |
| `z` | шесть `KYTY_M_*` транслятора = 0 | `0x00` | `KytySC3:0d2da32c…:fixb26:fixb1b:fixf10:fixf19` ✓ | `variant_fixb26_fixb1b_fixf10_fixf19` (каталог FS15) ✓ |

Отрицательный контроль сравнителя: строка с `baeea6e2…` от ожидаемой отличается — пойман. Итог `ALL OK`.

## 3. G1 (п. 778(д)(1))

- **`shader_cfg_tests`** MS2 (exe `b79836ed…`, копия `tests/shader_cfg_tests_ms2.exe`), драйвер `run_tests_m2.py` (копия M7a), с
  `KYTY_TEST_T306_EBOOT=C:/kyty/m657/m7a/cs7b` (слова `eboot.bin` по sha256 M7a — `sha256sum -c` OK):
  - `d` (умолчания): 136 тестов, rc 0, `failed.txt` пуст; `[mw1] mask=0x3b`; `7b4078750f32db50 … matched=3 ConstOffset=3 fallback=0`,
    `b912bcf29000558d … matched=8 ConstOffset=8 fallback=0`; `SKIP` 0.
  - `z` (шесть `KYTY_M_*` = 0): 136 тестов, rc 0, `failed.txt` пуст; `mask=0x00`; `matched=0`, `records=0` у обоих CS.
  - База MS1 (M2d G1) — 0 падений ⇒ множество падений ⊆ базы ✓. Кейс 224 (`dl_cases.txt`) и прочие ГП-кейсы не запускались.
- **Стенд T125** (`m_t125_stand` дерева MS2, драйвер `run_stand_m8a.py`): `ALL OK` (`g1_stand_t125.out.txt`; `MT125Stat: … mixed=47
  mixed_nz=27` при `=1`, шины 16 из 16 байт в байт, смесь только при `=1`).
- **Стенд `MWave2DiagStand`** (`m_wave2_diag_stand` дерева MS2, драйвер `run_stand_m6a3.py`):
  - при умолчаниях MS2 (`KYTY_M_T125` не задана = 1) — `FAIL` только в члене `audio k1: total=5 match=0` (`g1_stand_mw2_t125default.out.txt`):
    при `KYTY_M_T125=1` объектный Push идёт путём T125, и счётчики `ao_*` от `NoteAudioPush` — 0. Это ровно строка RC2 п. 783(в); все
    прочие члены (pure 132/132, audio k0 5/5, printf, ampr, agc) — ✓;
  - при `KYTY_M_T125=0` — **`ALL OK`** (`g1_stand_mw2_t125z.out.txt`; pure 132/132, audio k1 5/5, k0 5/5; в журнале `MT125: mode=0`).
  - **Отступление от буквы, на review лида:** п. 778(д)(1) пишет «стенд `MWave2DiagStand` — `ALL OK`» без окружения. Исполнитель читает
    член по строке RC2 (стенд `KYTY_DIAG_M5W2` на MS2 читается только при `KYTY_M_T125=0`) и сдаёт оба вывода. Правки кода нет.

## 4. G2 корпус T1 (п. 778(д)(2), п. 775(г)(2), п. 786(г)(3))

`corpus_m8c.py` (порт `corpus_m7a.py`; строки `t1_base.tsv`, GCN и записи кэша по sha256): 269 строк × 2 плеча + 3 плеча CS = 541 процесс,
отказов 0, 2 потока Idle. `check` — `ALL OK` (`corpus_check.out.txt`, таблица `corpus/corpus_m8c.tsv`):

1. все процессы rc 0 с `out.spv`;
2. `z` (шесть `KYTY_M_*` транслятора = 0) = FS15 (`m2d/corpus/base`) байт в байт **269 из 269**;
3. умолчания MS2 (`d`) ≠ умолчаниям MS1 (`m2d/corpus/d`) ровно в 2 строках — `ps_5a34b303576ee324_914a71d3664b53ab_0`,
   `ps_f47c0c097c598a36_3de3d43ef41686a6_0`;
4. оракул на этих строках: 8 из 8 и 2 из 2 `match`, `path=const`, по одной записи, `fallback (0,0,0,8)` / `(0,0,0,2)`; на 267 прочих — 0
   записей и `fallback (0,0,0,0)`;
5. справка: `d` = дерево M7a при `KYTY_M_T306=1` (`m7a/corpus/m1`) 269 из 269 — прочие коммиты MS2 (T125, `KYTY_DIAG_M5W2`, стенд)
   транслятор не трогают;
6. **член п. 775(г)(2)**: CS `7b4078750f32db50` с записью кэша игры `cs_7b4078750f32db50_28f7a21f24d8d3cc.bin` (sha256 `2b20e2c7…`), perm 0:
   при умолчаниях и при `KYTY_M_T306=1` — 6 записей `recompile-t306`, пары (1,1), (1,0), (0,1) по две, `nonconstant=cube=range=0`; при
   `KYTY_M_T306=0` — 0 записей; `out.spv` при `=1` = M7a `out_1.spv`, при `=0` = M7a `out_0.spv` (sha256).

## 5. Строки exe (`binary_m8c.py`, `ALL OK`)

MS2 против MS1 `ea35b679`: `MT125: mode=` 1 / 0, `MT125Stat: when=exit` 1 / 0, `M5W2: mode=` 1 / 0; `MWave1: mask=`, `MT265: mode=`,
`MT272: mode=`, `MT231: mode=` — по 1 в обоих; строки, читаемые скриптами (п. 756(б)(4)): `AudioStat:` 1 / 1, `AvTrace:` 21 / 21,
`MTexOffset:` 2 / 2; хэш `0d2da32c…` 1 / 0, `8dcf3177…` 0 / 1.

## 6. Таблица умолчаний и отката MS2 (п. 778(д), п. 786(г)(4), п. 783(в))

| Ручка | MS1 `ed94b13d` | MS2 `3504ecbc` | Откат на MS2 | Подпись и каталог при откате |
|---|---|---|---|---|
| `KYTY_M_T306` | 0 | **1** | `KYTY_M_T306=0` | маска `0x33`: `KytySC3:0d2da32c…:…:mw1_33`, каталог `…_mw1_33` — **имя каталога MS1 с чужой подписью** (класс RC-M1 п. 761(д): на копии кэшей с возвратом или на холодном каталоге) |
| `KYTY_M_T125` | нет | **1** | `KYTY_M_T125=0` | тема HLE вне набора подписи — подпись и каталог не меняются (`…_mw1_3b`) |
| `KYTY_M_T234`, `T233`, `T032`, `T203` | 1 | 1 | `=0` по ручке | меняют маску и каталог `…_mw1_<маска>` |
| `KYTY_M_T265`, `T272`, `T231` | 1 | 1 | `=0` по ручке | HLE, подпись не меняют |
| `KYTY_M_T256` | 0 | 0 | — | — |
| все шесть `KYTY_M_*` транслятора = 0 | — | — | — | `KytySC3:0d2da32c…:fixb26:fixb1b:fixf10:fixf19`, каталог FS15 `variant_fixb26_fixb1b_fixf10_fixf19` **с подписью `0d2da32c`** — правило RC-M1 п. 761(д) для M3a2 обязательно (п. 786(г)(1)) |
| `KYTY_DIAG_M5W2` | — (MS1 без кода) | 0 | — | вне набора подписи |
| `KYTY_FIX_*` (20), `KYTY_S_PCW`, `KYTY_S_REPLAY` | 1, 1, 3 | без изменений | — | — |
| Бинарь целиком | — | — | копия MS1 `C:/kyty/m657/bin/kyty_emulator_ea35b679.exe` по sha256 `ea35b679…` | каталог MS1 `…_mw1_33` с подписью `8dcf3177` |

**Строка RC2 (п. 783(в)):** «`KYTY_DIAG_M5W2=1` на MS2 читается только при `KYTY_M_T125=0`; при `KYTY_M_T125=1` счётчики `ao_*` и строка
`M5W2Stat:` от `NoteAudioPush` — 0 по построению, не читаются». Подтверждена стендом (§3): при умолчаниях `audio k1 match=0`, при
`KYTY_M_T125=0` — 5 из 5.

Свидетели в журнале игры при умолчаниях MS2: `MWave1: mask=0x3b`, `MT125: mode=1`, `MT265: mode=1`, `MT272: mode=1`, `MT231: mode=1`.

## 7. Не заявляется

Что MS2 работает в игре (не запускался); G3–G7; что смесь T125 слышна; верность картинки при T306; что откат `KYTY_M_T306=0` даёт тёплый
вход (каталог `…_mw1_33` с подписью `0d2da32c` — холодный); ГП-кейсы на MS2; ни одно число — не выигрыш; 60 FPS не обещаются.

## 8. Файлы (`docs/track-m/m8c/`; рабочая папка — `C:/kyty/m657/m8c/`)

Скрипты: `patch_m8c_step0.py`, `patch_m8c_defaults.py`, `srchash_m8c.py`, `mut_m8c.py`, `mk_wt_m8c.sh`, `mk_scripts_m8c.py`,
`build_m8c.cmd`, `build_m8c_main.cmd`, `bld_m8c.py`, `lowrun.py`, `cachechk_m8c.py`, `corpus_m8c.py`, `binary_m8c.py`, `run_tests_m2.py`
(копия M7a); драйверы стендов — `docs/track-m/m8a/run_stand_m8a.py`, `docs/track-m/m6a3/run_stand_m6a3.py`. Выводы издания 1:
`stand_wt.out.txt`, `stand_main.out.txt`, `mut_m8c_wt.out.txt`, `mut_m8c_main.out.txt`, `cherry.out.txt`, `srchash_*.out.txt`,
`patch_defaults.out.txt`, `step0_patch_main.out.txt`; издания 2: `gate_order_wt.out.txt`, `cachechk.out.txt`, `g1_tests_d.out.txt`,
`g1_tests_z.out.txt`, `g1_t306_d.txt`, `g1_t306_z.txt`, `g1_stand_t125.out.txt`, `g1_stand_mw2_t125default.out.txt`,
`g1_stand_mw2_t125z.out.txt`, `corpus_run.out.txt`, `corpus_check.out.txt`, `corpus_m8c.tsv`, `binary_m8c.out.txt`, `sha256.txt`,
`times.txt`. Сборочные логи — в рабочей папке (`build_emu.log`, `build_t.log`, `build_c.log`, `build_stand_g1.log`, `build_stand2_g1.log`).
