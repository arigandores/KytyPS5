# Трек F, звено F2a (`HPP-307`): правка Б26б — `S_BREV_B64` и `V_CMP_LE_U64` под `KYTY_FIX_B26`

Автор: Emu Engineer. Дата: 2026-10-01 (UTC, строки `C:/kyty/f287/times.txt`). Критерий — `57729aed:docs/ROADMAP.md:12589`
(якорь «(г) **Критерий F2 (Б26б), до кода:**», контроль +1 — 12590 «12.9 «VOPC Instructions»»); форма трека —
`beb36ab0:docs/ROADMAP.md:12074` (п. 228). `S_SWAPPC_B64` (Б26а, `ТУПИК`) не трогался. Игра не запускалась; установленная
`9235a7ac` в папке эмулятора не тронута (sha256 `9235a7ac61f1affb…` до и после).

**Итог:** правка двух опкодов сделана, собрана, протестирована (`ALL OK` при `=1` и `=0`), закоммичена — `ba3be480`
(код + тесты), бинарь `C:/kyty/f287/bin/kyty_emulator_5821482a.exe`. **WIP до F2b/F2c:** не установлен, дыма нет.
**Полный проход до кода нашёл третий неподдержанный опкод** — VOPC `0xf3` (`V_CMPX_LE_U64`) в тех же 4 шейдерах, и
для `57c4d5848e02ecdc` после правки — отказ отслеживания ресурсов, не опкод. Предсказание: **после правки ни один из 5
хэшей не печатает строку успеха** (4 — отказ с `0xf3`, 1 — отказ `ResourceTracking`). По букве (г)(4) «5 из 5» проходят
4 из 5; пятый — решение лида (§3, §8).

Метки: [c] — посчитано программой; [c-код] — по коду; [I] — вывод.

## 1. Опкоды (ISA RDNA2, `C:/kyty/s49/rdna2-official.txt`)

| строка лога | ISA | семантика | место в тексте ISA |
|---|---|---|---|
| SOP1 `0x0c` | 12 `S_BREV_B64` | `D.u64[63:0] = S0.u64[0:63]` | 12.3, строка 4084 |
| VOPC `0xe3` | 227 `V_CMP_LE_U64` | `D[threadId] = (S0 <= S1)`, D = VCC в VOPC | 12.9, строка 6241 |
| VOPC `0xf3` (новое, §2) | 243 `V_CMPX_LE_U64` | `EXEC[threadId] = (S0 <= S1)` | 12.9, строка 6279 |

Литерал 64-битного беззнакового источника — расширение нулём (6.2.1 «Literal Expansion to 64 bits»).

## 2. Полный проход декодера до кода (п. 237(г)(2), RC7 F1b)

Инструмент — режим `--b26-pass <eboot.bin>` тестов `shader_recompiler_compute_tests` (только тестовый код;
`ba3be480:tests/ShaderRecompilerComputeTests.cpp:31417`, якорь «static int RunB26DecodePass(const char *eboot_path) {», контроль +1 —
31418 «namespace SR = Libs::Graphics::ShaderRecompiler;»): код 5 шейдеров из `eboot.bin` по смещениям `docs/track-f/f1a/b26_shaders.tsv`,
проверка XXH3 = хэш лога (5 из 5 `match=1`), `Decoder::DecodeProgram` по всей программе (не до первого отказа), затем
`TranslateProgram` так, как это делает `CsPretranslate` (нулевые user data, перехватчик фатальной ошибки, бюджет).
**Прогон до кода** — сборка тестов на дереве `20b39318` + только этот инструмент, вывод `pass_before.out.txt` [c]:

| хэш | инструкций | неподдержанные (pc: семейство опкод) |
|---|---:|---|
| `57c4d5848e02ecdc` | 2 726 | `0x168` SOP1 `0x0c` (литерал следует, см. ниже) |
| `433e4cede34ca4c3` | 47 | `0x024` VOPC `0xe3`; `0x0c0` VOPC **`0xf3`** |
| `4468d53059c03cba` | 174 | `0x1d4`, `0x244`, `0x318` VOPC `0xe3`; `0x294` VOPC **`0xf3`** |
| `7bb50479b3a32c7c` | 208 | `0x264`, `0x2d4`, `0x3a8` VOPC `0xe3`; `0x324` VOPC **`0xf3`** |
| `f8e350383290ff7b` | 59 | `0x024` VOPC `0xe3`; `0x0fc` VOPC **`0xf3`** |

Всего 13: SOP1 `0x0c` — 1, VOPC `0xe3` — 8, VOPC `0xf3` — 4. Наблюдение: неподдержанная SOP1 с литералом
занимает одно слово, и декодер до правки читает литерал `0x20468000` как следующую инструкцию (2 726 против 2 725 после
правки); вреда нет — CFG останавливается на первом отказе.

**После правки** (`ba3be480`, `pass_after_fix1.out.txt`) [c]: неподдержанных 4 — ровно четыре VOPC `0xf3`; `57c4…` декодируется
целиком (2 725 инструкций, 0 отказов). При `KYTY_FIX_B26=0` (`pass_after_fix0.out.txt`) вывод совпадает с проходом до кода
(сравнение `diff` без строки ручки и вариантов user SGPR — пусто) [c].

Трансляция после правки при wave 32/64 × user SGPR 16/32 (все 4 сочетания дают одно и то же) [c на допущениях, итог [I]]:
- 4 шейдера VOPC — `ShaderCFG.cpp:44 shader CFG build failed: unsupported decoded instruction … VOPC opcode=0xf3`;
- `57c4d5848e02ecdc` — `ResourceTracking.cpp:173 shader resource tracking: … pc=0x000001a0 GetBufferResource dword 1 is not a
  valid runtime value`. Дескриптор `mubuf` в `0x1a0` — `s[16:19]`; его dword 1 (`s17`) собирается на двух ветвях
  (`0x108 s_addc_u32 s17` + `0x10c s_bitset1_b32 s17` против `0x118 s_or_b32 s17, s9, 0x40000`), `S_BREV_B64` пишет другой
  регистр — `s[10:11]` (`0x168`) [c, дизассемблер `rdis.py`]. Отказ — не следствие правки опкода.

Допущение: настоящая регистрация (число user SGPR, потоки) в логах не печатается; поэтому вердикт трансляции —
предсказание, список неподдержанных — нет.

**Новые строки реестра (предложение лиду; правку двух опкодов не останавливают):**
- **Б26в — VOPC `0xf3` `V_CMPX_LE_U64`**: 4 шейдера (те же, что `0xe3`), по одному месту (pc выше); класс как у Б26б —
  наблюдение K4 по п. 228(б) (путь не исполняется [c F1b]), при запросе — K1. Правка — тот же приём, что для `0xe3`
  (`NOT(UGreaterThan64)` с `cmpx = true`, соседи `0xf2`/`0xf5` в таблице есть); не сделана — вне задания.
- **Б26г — `57c4d5848e02ecdc`: `ResourceTracking.cpp:173` на дескрипторе `s[16:19]` (pc `0x1a0`)**: всплывёт в логах вместо
  строки SOP1 `0x0c`; наблюдение K4 тем же доводом; на пути dispatch (без перехватчика) — `EXIT`, т. е. K1 при запросе [c-код].

## 3. Профиль после правки — предсказание числом (на лог, `CsPretranslate`, при `=1`)

| строка | до | после [I] |
|---|---:|---:|
| `unsupported … SOP1 opcode=0x21` | 96 | 96 |
| `unsupported … SOP1 opcode=0x0c` | 1 | **0** |
| `unsupported … VOPC opcode=0xe3` | 4 | **0** |
| `unsupported … VOPC opcode=0xf3` | 0 | **4** (`433e…`, `4468…`, `7bb5…`, `f8e3…`) |
| `shader CFG build failed` всего | 101 | **100** |
| `CsPretranslate: skipped hash=57c4d5848e02ecdc reason=…ResourceTracking.cpp:173…` | 0 | **1** |
| `CsPretranslate: ready hash=<один из 5>` | 0 | **0** |

При `=0` — 96 / 1 / 4 как прежде (декодер байт в байт, §5).

## 4. Правка (`ba3be480`, только `src/graphics/**`, 7 файлов, +56 / −5)

Ссылки — коммит `ba3be480`, якорь и контроль +1 — `refs_f2a.out.txt` (24 из 24 `ALL OK`).

1. **Ручка** — `ShaderDecoder.cpp:329` `bool FixB26Enabled()` (+1 «static const bool enabled = [] {»): `KYTY_FIX_B26`, умолчание 1
   (не задана или пустая — вкл.; `0`/`false`/`off`/`no` — выкл., `Common::EnvValueOn`). `ShaderDecoder.cpp:337`
   `Opcode GateFixB26(Opcode)` (+1 «if ((opcode == Opcode::S_BREV_B64 || …») возвращает `UNSUPPORTED` для двух опкодов при 0.
   Не ручка `gates.h`: файл ворот перечитывается на лету, а подпись кэша трансляции фиксируется при старте — смена значения
   посреди прогона разорвала бы RC5; поэтому чтение один раз, как у `KYTY_BDA_LEAN`. `check_gate_order.py`: `GATE ORDER: clean`,
   `gates.h`/`gates.cpp` не менялись.
2. **Таблицы и все места поиска** — `ScalarAluOps.cpp:48` `{0x0cu, Opcode::S_BREV_B64},`; `VectorAluOps.cpp:248`
   `{0xe3u, Opcode::V_CMP_LE_U64, false}` (DPP не поддержан, как у соседей `0xe1/0xe2/0xe4/0xe5`). Через `GateFixB26` идут все
   три поиска этих таблиц: `ScalarAluOps.cpp:150` (`DecodeSop1`), `VectorAluOps.cpp:372` (`LookupVop3Opcode`, форма VOP3),
   `VectorAluOps.cpp:1539` (`DecodeVopc`). Четвёртое обращение к таблице VOPC — `FindOpcode` в `VectorAluOps.cpp:1151`
   (`DecodeVopcDpp`) — достижимо только при `inst.opcode != UNSUPPORTED` (ранний выход 1147–1150), т. е. при 0 не достигается.
   `Opcode::S_BREV_B64`, `V_CMP_LE_U64` — последними перед `COUNT` (`ShaderDecoder.h:599`).
3. **Трансляция** — `Scalar.cpp:172` `S_BREV_B64`: `ReadU32Pair` (`Translate.cpp:451`: литерал — старшая половина 0, т. е.
   расширение нулём по 6.2.1; отрицательная инлайн-константа — знаком), затем `lo' = BitReverse32(hi)`, `hi' = BitReverse32(lo)`,
   `WriteU32Pair`; SCC не пишется. `Vector.cpp:109` `V_CMP_LE_U64`: `NOT(UGreaterThan64(S0, S1))` на дорожку **до**
   `EmitCompareResult`, который делает `LogicalAnd(EXEC, value)` (`Compare.cpp:11`) — выключенная по EXEC дорожка пишет 0 (RC6).
   Нового IR-опкода нет.
4. **Кэш трансляции (RC5)** — `shaderTranslationCache.cpp:578`: при `=1` токен `:fixb26` входит в `variant`, т. е. и в подпись,
   и в каталог (`_ShaderCache/PPSA21564/variant_fixb26`); при `=0` — прежний каталог и подпись без токена. Проверено тестом
   (§6). Подпись транслятора новой сборки `846a041a…` ≠ `699c1e4b…` у `9235a7ac` [c, строки в бинарях] — **первые входы на бинаре
   правки холодные при любом значении ручки**; при `=0` бинарь правки пишет в каталог установленной сборки (подписи разные) —
   копия и возврат кэшей по п. 228(в) обязательны; затравка `_ShaderSeeds` несовместима при обоих значениях (в её строке совместимости
   подпись).

**Состояние, введённое правкой** (правило отчёта п. 160(а)(4)): одно — локальная статическая `enabled` в `FixB26Enabled`
(`ShaderDecoder.cpp:330`): ставится один раз при первом вызове (потокобезопасная инициализация статической переменной C++11),
не снимается никогда, живёт до конца процесса; TLS нет, полей нет, счётчиков нет; ранних выходов, где снятие пропускалось бы,
нет — снятия не предусмотрено по построению. `GateFixB26` состояния не имеет.

**`=0` байт в байт [c]:** тест `CheckB26Decode(false)` (§6) сравнивает строку декодера с текстом до правки из `log_v142`
(SOP1, VOPC — дословно) и форму VOP3 `0x0e3` с неподдержанным соседом `0x0e0`; полный проход при `=0` совпадает с проходом до
кода; `shader_cfg_tests` при `=0` и `=1` — одинаковые логи.

Наблюдение (не RC): SDWA-форма VOPC `0xe3` при `=1` принимается декодером (`SupportsVopcSdwa` пропускает любой поддержанный
опкод — так же, как у соседей `0xe1/0xe2/0xe4/0xe5`); в ISA SDWA для 64-битных сравнений не определён. В 5 шейдерах SDWA-формы нет.

## 5. Положительный счёт для F2c (п. 237(г)(4), RC2) — строки по коду

- **Успех:** `CsPretranslate: ready hash=<16 hex> us=<n> kb=<n> ready_kb=<n>` —
  `ba3be480:src/graphics/host_gpu/renderer/pipeline/computePretranslation.h:255` (якорь `LOGF("CsPretranslate: ready hash=%016" …`,
  контроль +1 — 256 `job->key.hash, us, cost / 1024, ready_bytes / 1024);`). **Оговорка [c-код]:** строка печатается только при
  `result && !stopping && !job->discard && cost <= limits.ready_bytes` (`:242`); успешная трансляция, не прошедшая это условие,
  не печатает ничего.
- **Отказ:** `CsPretranslate: skipped hash=<16 hex> reason=<файл>:<строка> <текст>` — `:232` (якорь `LOGF("CsPretranslate: skipped hash=%016" PRIx64 " reason=%s\n", …`,
  контроль +1 — 233 `} catch (...) {`); без текста исключения — `… unknown exception` (`:234`). Хэш в строках — без `0x`.
- Счёт F2c: на хэш ровно одна из строк `ready`/`skipped`; для `skipped` — разбор `reason`: опкод (`family=… opcode=0x..`) или иной
  механизм (`ResourceTracking.cpp:173`).
- **Предсказание (§3):** `ready` — 0 из 5; `skipped` с опкодом `0xf3` — 4; `skipped` с `ResourceTracking.cpp:173` — 1.

## 6. Тесты

**Б26б, GPU** — `shader_recompiler_compute_tests --fix-b26-only` (`ba3be480:tests/ShaderRecompilerComputeTests.cpp:31557`, якорь
`if (argc == 2 && std::strcmp(argv[1], "--fix-b26-only") == 0) {`, +1 — комментарий «Track F, F2a (HPP-307)»; проверка кэша RC5
добавлена вторым коммитом звена, только тесты). Исполнение на GPU, сравнение каждого слова результата:

- `B26ScalarBrevB64` (`:20815`): `s_brev_b64 s[10:11], 0x20468000` → `s10 = 0`, **`s11 = 0x00016204`**; литерал `0x80000001` →
  источник `0x00000000_80000001` → `s12 = 0`, `s13 = 0x80000001` (знаковое расширение дало бы `s12 = 0xffffffff`); регистр-источник
  `s[4:5] = {0x00000001, 0x12345678}` → `{0x1e6a2c48, 0x80000000}`, то же на месте (`s[4:5] ← s[4:5]`); инлайн `−1` → все единицы;
  SCC не меняется (0 и 1 до инструкции сохраняются). `decoded S_BREV_B64` — 6 из 6.
- `B26VectorCmpLeU64Wave32` / `Wave64` (`:20861`), 64 дорожки, результат по дорожке: равные / меньше / больше в одном сравнении
  (дорожки 31 / 30 / 32 против 31); решает старшая половина — в обе стороны; `−1` (максимум) ≤ 0 → 0, 0 ≤ максимум → 1
  (беззнаковость); литерал `0x80000000` расширяется нулём; **EXEC `0x0000ffff_0000ffff` → выключенные дорожки пишут 0**; форма VOP3
  с SGPR-назначением `s[22:23]`. `decoded V_CMP_LE_U64` — 8 из 8.
- `CheckB26Decode` (`:20962`): при `=1` три кодировки декодируются в два опкода (SOP1 — 2 слова с литералом); при `=0` — строки до правки.
- RC5: при `=1` — каталог `_ShaderCache\PPSA21564\variant_fixb26`, `:fixb26` в подписи; при `=0` — `_ShaderCache\PPSA21564`, токена нет.

Итог [c]: `KYTY_FIX_B26=1` — `ALL OK` (3 GPU-кейса ok); `=0` — `ALL OK`; не задана — действует 1, `ALL OK`
(`b26_tests_fix1.out.txt`, `b26_tests_fix0.out.txt`, `b26_tests_unset.out.txt`). При `=1` кейсы входят и в общий список
(`AddCase`, под `FixB26Enabled()`).

**`shader_cfg_tests`** (`KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`, сборка `ba3be480`) [c]: 127 тестов при обоих значениях;
падений: **`=1` — 1 тест** (`TestNewShaderRecompilerPixelImageSampleLodSelection`: «pixel IMAGE_SAMPLE_C must use
OpImageSampleDrefImplicitLod», «pixel IMAGE_SAMPLE_C_LZ must use explicit dref lod»); **`=0` — тот же 1 тест, те же 2 проверки**.
Логи совпадают байт в байт (sha256 `5a60758aab7abd57…` у обоих). Падений при `=1` не больше, чем при `=0`. (Падение — строка Б11
`IMAGE_SAMPLE_C`, не связано с правкой.)

## 7. Сборка

- `cmd //c "C:\kyty\build_local.cmd"` на `ba3be480` (без замка; `times.txt`); бинарь **sha256
  `5821482a13a38bb9e42719b75fbd7b6e308a08c8e98caab02afb5398aac368dd`** (sha8 `5821482a`), копия
  `C:/kyty/f287/bin/kyty_emulator_5821482a.exe` (sha256 совпадает). Метка сборки `ba3be48-dirty` — «dirty» от изменённого до звена
  подмодуля `3rdparty/nlohmann_json`, не от кода. Подпись транслятора `846a041a4d4902a2afc2ca8f1d7067c5d2ae982b`.
- Тесты собраны `build_tests.cmd` (`shader_cfg_tests`) и `cmake --build … --target shader_recompiler_compute_tests`
  (`build_target.cmd`, без configure).
- Установленная `C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe` — sha256 `9235a7ac…`, не тронута; игра не запускалась.

## 8. `git diff 4fc501f4 ba3be480 -- src/` (п. 237(г)(3))

33 файла, +6 481 / −110 (`diff_4fc501f4.out.txt`). **Правка F2a — 7 файлов, +56 / −5** (`git diff 20b39318 ba3be480 -- src/`);
`src/` между `a2849aec` и `20b39318` не менялся. **Иные правки кода в диапазоне — 22 коммита сессий 128–136**, все на ручках и
счётчиках, ни одна не установлена отгрузкой:

| коммит | что |
|---|---|
| `55841100`, `252b0c76`, `04ae3390` | ручка `protceil` (`KYTY_PROT_CEILING`, умолч. 0, только измерение) |
| `67962c18`, `76e2a5a3`, `12f0b62b` | ручка `armcopy` (`KYTY_ARM_IN_COPY`): прототип, код отгрузки (умолч. 0 → 1), возврат умолч. 1 → 0 |
| `fb55d93b`, `abb0aa9d` | ручка `acinline` (`KYTY_ARM_INLINE`, умолч. 0), атрибуция `ac_cbad` |
| `f339ce10` | только комментарии `gates.{h,cpp}` |
| `ce08b8ca`, `9bb1e2ef` | ручка `lwin` (`KYTY_ARM_LOSS_WIN`, умолч. 0) |
| `8f88d44e` | ручка `dispceil` (`KYTY_DISP_CEILING`, умолч. 0) + перепись `mh_disp_us` |
| `0f539e02` | ручка `rbcen` (`KYTY_REBIND_CENSUS`, умолч. 0, только измерение) |
| `99468a52`, `5680c2ad`, `cf5fd876` | ручка `b2reuse` (`KYTY_B2_REUSE`, умолч. 0) и исправления CR1/CR5б-1 |
| `ae093d70`, `32cd9fb3` | ручка `rbslow` (`KYTY_REBIND_SLOW_CENSUS`, умолч. 0) |
| `5b972f56`, `e967df69`, `ae8f30e5`, `a2849aec` | ручка `bindlean` (`KYTY_BIND_LEAN`, умолч. 0) и контрольные сборки |

Файлы иных правок: `common/frameStats.{h,cpp}`, `common/gates.{h,cpp}`, `common/parallelCopy.{h,cpp}`, `pm4Handlers.cpp`,
`graphicsRun.cpp`, `memoryTracker.{h,cpp}`, `pageManager.{h,cpp}`, `regionManager.h`, `bufferCache.{h,cpp}`, `streamBuffer.cpp`,
`commandScheduler.cpp`, `image.h`, `descriptors.cpp`, `renderCompute.cpp`, `renderContext.{h,cpp}`, `renderDraw.cpp`, `videoOut.cpp`,
`kernel/memory.cpp`, `kernel/memoryAddressSpace.inc`. Что ручки при умолчании 0 дают поведение `4fc501f4` байт в байт — **не
проверено** этим звеном. По п. 237(г)(3) решение — у лида до прогонов F2c; следствие для (г)(6): прогон (5)(а) не может служить
регрессионным входом п. 228(г)(5) «если в бинаре нет иных правок кода» — иные правки есть.

## 9. Файлы

`docs/track-f/f2a/` (копии `C:/kyty/f287/f2a/`): правки `patchlib.py`, `patch1_pass_tool.py` (инструмент прохода, до кода),
`patch2_fix_b26.py` (src), `patch3_tests.py` (тесты), `patch4_pass_udc.py` (проход: 16/32 user SGPR), `patch5_rc5_check.py`
(тест RC5); `build_target.cmd`; `refs_f2a.py` + `refs_f2a.out.txt`; выводы `pass_before.out.txt`, `pass_after_fix1.out.txt`,
`pass_after_fix0.out.txt`, `b26_tests_fix1.out.txt`, `b26_tests_fix0.out.txt`, `b26_tests_unset.out.txt`, `cfgtests_fix1.log`,
`cfgtests_fix0.log`, `gate_order.out.txt`, `diff_4fc501f4.out.txt`.

## 10. Не заявляется

Что правка меняет картинку или что-либо в сценах (шейдеры не исполнялись, F1b); что 5 шейдеров переведутся (предсказание — 0 из 5);
что предсказание трансляции верно при настоящей регистрации (число user SGPR и потоки — допущение); что ручки иных правок кода при 0
дают поведение `4fc501f4`; что SDWA/DPP-формы `0xe3` встречаются в игре; что строка `ready` печатается на каждый успех (§5, оговорка).
