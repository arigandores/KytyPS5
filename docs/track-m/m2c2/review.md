# M2c2 (`HPP-844`, трек M, Red Team): `t306_mask` на тесте M2a2 и враждебная проверка находки M2a2 §4

**Итог: (1) `CAUGHT` — мутант `t306_mask` пойман тестом `TestMWave1T306OffsetWriteMask`, `main` проходит при `KYTY_M_T306=0` и `=1`
[c своих прогонов]; (2) находка M2a2 §4 ПОДТВЕРЖДЕНА и РАСШИРЕНА — дыра есть и в пиксельной стадии при `s_mov_b64 exec, -1`
[c IR и SPIR-V]; (3) хэш исходников транслятора `main` = `aac6db694d6785bbde0a838953d4565569645996` [c]. Это запись для парковки
п. 762(г), не вердикт MS1 (п. 762(д)); RC к этому звену нет.**

Входы: `ROADMAP.md` п. 761 (KytyPS5 `2b869aa4`), п. 762 (KytyPS5 `864d57aa`, прочитан 11:33:46Z), п. 760; отчёт M2a2
`C:/kyty/m657/m2a2/report.md` (= `docs/track-m/m2a2/report.md`, KytyPS5 `adc3c33d`); комментарий лида `2545462e` в `HPP-844`.
Дерево — мой worktree M2c `C:/kyty/m657/m2c/wt` (`666a434a`; `git diff 666a434a 864d57aa -- src` пуст, файл теста взят из
`864d57aa`), сборка `C:/kyty/m657/m2c/build` (`build_m2c.cmd`, `--parallel 2`, приоритет Idle через `lowrun.py`). Игра не
запускалась, замок не брался; ГП — только кейс `MW1T306SampleOffsetsFourNeighbors` (×2, малый dispatch), кейс 224 (`dl_cases.txt`)
в наборе T306 не участвует; новых `DeviceLost` 0. Время — `times.txt` (UTC, `date -u`). Пометки: [c] — проверено мной, [I] —
вывод, [U] — неизвестно.

## 1. Член (1): `CAUGHT` и PASS `main`

| Прогон | Бинарь | Итог |
|---|---|---|
| `run_mut_m2c2.py C:/kyty/m657/m2c2/mut T306` (= `run_mut_m2c.py`, отличие — одна строка `BIN`) | `mutall_cfg.exe` `d6114515…`, `mutall_compute.exe` `14ac4d41…` (все мутанты `mut_m2c.py` `47d71f4d…`, включение `M2C_MUT`) | `control T306 2 tests PASS`; `t306_mask T306 2 tests CAUGHT cfg:MWave1`; **`ALL OK`** (`mut.out.txt` `ef907dc6…`) |
| строка отказа мутанта | `mut/t306_mask_cfg_T306.txt` | `other: … ConstOffset=1` → `ShaderCfgTests: failed: T306: offset written under another lane mask became a ConstOffset` |
| контроль той же сборки без `M2C_MUT` | `mut/control_cfg_T306.txt` | `same ConstOffset=1`, `other ConstOffset=0`, `failed` нет |
| ГП-кейс `MW1T306SampleOffsetsFourNeighbors` | контроль и мутант | `ALL OK` оба (мутант этим кейсом не ловится — как в M2c) |
| `main` (`cfg_main.exe` `d5e1801f…`, `864d57aa`), фильтр `MWave1` | `=0` / `=1` | `=0`: same 0 / other 0 / full 0, rc 0; `=1`: same 1 / other 0 / full 1, rc 0, `failed` нет (`main_cfg_0.txt` `17d40421…`, `main_cfg_1.txt` `f99c3333…`) |

Чтение теста (что он проверяет именно сторож маски) [c кода `864d57aa`]: формы `same` и `other` отличаются только парой
`v_cmp_gt_u32 vcc, s9, v0` / `s_and_saveexec_b64 s[42:43]` перед записью смещения и `s_mov_b64 exec, s[42:43]` перед выборкой —
запись под A∧B, выборка под A. Мутант меняет ровно сравнение `write->Arg(0).Resolve() == exec` в `MResolveSampleOffset`; обёртка
`Select(A, …, 0)` в `other` не сворачивается (A — не константа), поэтому `ConstOffset` в `other` даёт только снятое сравнение.
Положительный контроль не тавтологичен: `same` при `=1` даёт `ConstOffset ≥ 1` — путь темы жив, ноль в `other` не от мёртвого пути.
Член (2) п. 761(в) по `CAUGHT` исполнен; по букве п. 761(в) это давало бы T306 `PASS`, но п. 762(в) вывел T306 из MS1 — вердикт MS1
этим звеном не выносится.

## 2. Член (2): враждебная проверка находки M2a2 §4

### 2.1 Чтение кода `main` [c]

- `Translator::IMAGE_SAMPLE` (`Memory.cpp`): при `T306=1` и флаге смещения `m_offset = ir.Select(ir.GetExec(), offset, 0)`, затем
  `address.Instruction()->SetArg(0, m_offset)` — обёртка становится первым аргументом `MakeImageAddress`.
- `initial_exec` (`Translate.cpp`): `IR::U1(true)`; иначе только (а) compute волны 64 на подгруппе 32 с числом потоков, не кратным 64,
  (б) пиксельная стадия — `helper == 0`.
- Свёртка: `ConstantPropagation.cpp`, `FoldSelect` — при константном условии `Replace(inst, condition ? true_value : false_value)`;
  `Select(true, off, 0)` → `off`.
- Запись литерала в VGPR под маской — `SelectU32(mask, imm, old)`.
- `MResolveSampleOffset` (`spirvEmitterImage.cpp`) берёт первый `SelectU32` за обёртку: `exec := Arg(0)`, `inner := Arg(1)`; если
  `inner` — литерал, `true` сразу (сравнение масок не делается). После свёртки на месте обёртки стоит запись: `inner` = литерал ⇒
  `ConstOffset` всем дорожкам.
- `s_mov_b64 exec, -1`: `ReadMask` литерала → `ThreadBit(-1, -1)`; в IR моей пробы это сворачивается в `true` (ниже, форма 2).
- Опровергающая гипотеза «обёртку убирает ещё и `PredicationElimination`» — нет [c кода]: удаление `Select` требует, чтобы все
  пользователи были «чистыми по дорожке» (`IsLaneLocalPure`), а пользователь обёртки — `MakeImageAddress` (не в списке); свёртка цепочки
  через истинный слот (`FoldSelectChain`) требует `exec ⇒ маска записи` и тогда верна. Других путей подмены обёртки при неконстантной
  маске я не нашёл.

### 2.2 Своя проба (`probe_patch.py`, в git не идёт; бинарь `cfg_probe.exe` `599cd37a…` = `main` + функция пробы)

Смещение `0x0101` = (+1, +1) пишется под A = `s8 > v0`; у форм с «старым» смещением сначала `v_mov_b32 v20, 0x0202` под входным `exec`.
Одна форма — один процесс (`M2C2_FORM`), дамп SPIR-V/IR — `KYTY_TESTS_SPV_DIR`.

| Форма | Стадия | Маска выборки | Верный ответ | `=0` ConstOffset | `=1` ConstOffset | Вывод |
|---|---|---|---|---|---|---|
| 0 `full_old` | compute | `s_mov_b64 exec, s[40:41]` (вход, `true`) | нет `ConstOffset` (дорожки вне A — (+2,+2)) | 0 | **1** | дыра [c] |
| 1 `lit` | compute | `s_mov_b64 exec, -1` | нет | 0 | **1** | дыра [c] |
| 2 `pix_lit` | **pixel** | `s_mov_b64 exec, -1` | нет | 0 | **1** | **дыра в пиксельной стадии** [c] |
| 3 `pix_entry` | pixel | `s_mov_b64 exec, s[40:41]` (вход, `helper == 0`) | нет | 0 | 0 | верно |
| 4 `ctl_same` | compute | A | `ConstOffset` (+1,+1) | 0 | 1 | положительный контроль жив |
| 5 `ctl_other` | compute | A, запись под A∧B | нет | 0 | 0 | отрицательный контроль жив |

IR формы 0 при `=1` (`spv/f0_k1/0.spv.ir.txt` `9e2f0686…`): `%11 = SelectU32 %10, 0x00000101, 0x00000202` (запись под A),
`%14 = MakeImageAddress %11, …` — обёртки нет (свернулась), `ImageWrite …, true`; SPIR-V (`spv/f0_k1/0.spv` `906b27bc…`):
`OpImageSampleExplicitLod … Lod|ConstOffset %float_0 %77`, `%77 = OpConstantComposite %v2int %int_1 %int_1` — всем дорожкам (+1,+1),
дорожки вне A теряют (+2,+2). Неверное число, а не только «потеря оптимизации».

IR формы 2 при `=1` (`spv/f2_k1/0.spv.ir.txt` `3d8e9930…`): `%11 = IEqual32 helper, 0`, `%14 = LogicalAnd %11, (LogicalAnd %11, A)`,
`%15 = SelectU32 %14, 0x00000101, 0x00000000`, `%18 = MakeImageAddress %15, …`, `ImageWrite …, true` — `ThreadBit(-1)` свернулся в
`true`, обёртка свернулась, запись под `A ∧ ¬helper` принята за обёртку; SPIR-V `Lod|ConstOffset … %85` = (+1,+1).

**Поправка к M2a2 §4 и п. 762(б):** формулировка «начальный `exec` — константа `true` у всех стадий, кроме пиксельной» верна для
входного `exec`, но дыра не ограничена не-пиксельными стадиями: в пиксельной стадии она открывается любым `exec`, ставшим константой
`true` после частичной записи смещения (форма 2, `s_mov_b64 exec, -1`) [c]; при входном `exec` пиксельной стадии (`helper == 0`)
дыры нет (форма 3) [c]. Условие переоткрытия п. 762(г) («пиксельные с `exec` = литерал после частичной записи смещения») этим
подтверждено пробой, а не только кодом. Путь по умолчанию (`=0`) — `ConstOffset` 0 во всех 6 формах [c]: прежний путь не задет.

### 2.3 Для парковки п. 762(г) — член правки [I]

Правка темы обязана держать формы 0, 1, 2 при `=1` с `ConstOffset` = 0 (или со смещением, верным для всех дорожек выборки) и формы 3, 4, 5 —
как сейчас; иначе сценарий отказа — выборка с чужим смещением у дорожек вне маски записи на compute и на пиксельной стадии после
`s_mov_b64 exec, -1`. Сторож, сравнивающий маску записи с маской выборки, после свёртки этого не различит (у свёрнутой обёртки нет
маски) — нужна обёртка, которую `FoldSelect` не снимает, или признак «маска выборки — константа `true` ⇒ маска записи обязана быть
константой `true`» [I].

## 3. Член (3): хэш исходников транслятора

`srchash_m2c.py` (`58ac80b1…`, не изменён) по деревьям `git archive` (`core.autocrlf=false`):

| Дерево | Файлов | Хэш |
|---|---|---|
| `864d57aa` (`main`) | 102 | `aac6db694d6785bbde0a838953d4565569645996` |
| `6beb3b73` (FS15, самопроверка) | 102 | `9177b4267de1fb8bac7d1113afd8733210addfac` |
| `C:/kyty/m657/m2c/wt` (сборка этого звена) | 102 | `aac6db694d6785bbde0a838953d4565569645996` |

`srchash.out.txt` `2f20c67a…`. = ожидаемому п. 762(а).

## 4. Итоги скриптов (п. 758(б))

| Скрипт | Итог |
|---|---|
| `mut_m2c.py patch` / `restore` | `ALL OK` / статус worktree — только файл теста и прежняя правка измерения M2c |
| `run_mut_m2c2.py … T306` | **`ALL OK`** (control PASS, `t306_mask` CAUGHT) |
| `cfg_main.exe` `MWave1` `=0` / `=1` | rc 0 / rc 0, `failed` 0 |
| `probe_patch.py` | `patched probe`; 12 прогонов rc 0 |
| `srchash_m2c.py` | три строки выше |

Первый вызов `cfg_main.exe` (относительный путь) упал в `lowrun.py` до запуска бинаря — повторён с абсолютным путём (`times.txt`).

## 5. Файлы

`C:/kyty/m657/m2c2/`: `review.md`, `run_mut_m2c2.py`, `probe_patch.py`, `mut.out.txt`, `mut/`, `main_cfg_{0,1}.txt`,
`probe_f{0..5}_k{0,1}.txt`, `spv/`, `srchash.out.txt`, `sha_m2c2.txt` (sha256 всех выводов и бинарей), `times.txt`; локально `bin/`,
`trees/`, `build_*.log`. Копии LF — `docs/track-m/m2c2/`. Worktree M2c возвращён (`tests/shaderCfgTests.cpp` = `666a434a`);
объекты `m2c/build` теперь от сборки пробы (свои, не используются другими звеньями).

**Не заявляется:** исполнение пробы на ГП (только SPIR-V); достижимость дыры в игре (программы `image_sample_*_o` после частичной записи
смещения и `exec` = `true` в корпусе T1 не размечались) — [U]; что формы покрывают DPP, SDWA, запись в цикле или через ветвление CFG;
поведение upstream `984cfceb`; вердикт MS1.
