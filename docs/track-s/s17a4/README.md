# S17a4 — правка RC1 S17b3: ветвь и виновник в строке отказа `residual`, счётчик по префиксу (Emu Engineer, `HPP-622`; `ROADMAP.md` «СЕССИЯ 122» п. 541(в))

Без игры. Код — коммит KytyPS5 `9238a182` (родитель `943576e4`; от S17a3 `9635cb0f` в `src`/`tests`/`CMakeLists.txt` меняются
только 3 файла ниже — коммиты между `9635cb0f` и `943576e4` кода не трогают); ветка `main`. Время —
`C:/kyty/s288/s17a4/times.txt` (`date -u`). Пометки: [c] — проверено кодом или прогоном этого звена; [I] — вывод; [U] —
неизвестно. **Код в игре не проверен (WIP по правилу звена до тега сбора S17c на бинаре S17a4).**

## 1. Что изменено (`git diff --stat 9635cb0f 9238a182 -- src tests CMakeLists.txt`)

| Файл | Строк | Что |
|---|---|---|
| `src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp` | +39 −15 | `Canonicalize`: вектор `kept_role` (`:643`, `:705`), проверка `residual` считает всех виновников и называет первого (`:796`–`:798`); `CountReject` (новая, `:823`); `HandleSpec` зовёт `CountReject` (`:1237`) |
| `src/graphics/host_gpu/renderer/pipeline/shaderReplay.h` | +10 −3 | комментарий `Canonicalize` (форма `why`), объявление `CountReject` (`:350`) |
| `tests/shaderCfgTests.cpp` | +97 −2 | `TestShaderReplayWalkBits`: часть (б) — ожидание `residual branch=addr culprit=30:role2 `; новая часть (б2) — ветвь `exact`; новая часть (д) — `CountReject` |

Скрипты правки (якоря целыми строками, CRLF рабочего дерева сохраняется): `patch/patch_s17a4.py` (код),
`patch/patch_s17a4_tests.py` (тест).

## 2. Буква п. 541(в)(1)–(6) по коду [c]

1. **`why` отказа `residual`** — `residual branch=<addr|exact> culprit=<i>:role<r> n=<k>`
   (`9238a182:src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp:797`): обход по всем словам канонического пути
   (`:785`–`:795`); `i` — первое по индексу слово-виновник; `branch=addr`, если у него `kept_address` (и тогда, когда его
   значение подходит и под точную проверку), иначе `exact`; `r` — `kept_role[i]` (роль классификатора до замены на
   `ROLE_KEEP`, записывается рядом с `kept_address`, `:705`) для `addr`, `0` для `exact`; `k` — число виновников обеих ветвей.
   Сырое значение слова в строку не входит. Набор отвергаемых записей прежний: условие виновника — то же выражение, что в
   `9635cb0f:…/shaderReplay.cpp:778`–`:779`; поменялось только то, что обход не прерывается на первом виновнике (цена — на
   пути отказа, поток писателя).
2. **Счётчик по префиксу** — `CountReject` (`:823`): `self…` → `canon_self`, `residual…` → `canon_residual`, `base` →
   `canon_base`, остальное → `canon_big`; `canon_mismatch = canon_self + canon_residual` — та же строка, что раньше (`:834`).
   Порядок проверок прежний (`self` первым), так что `why` вида `self …` в `canon_residual` не попадёт.
3. **Пределы строк отказа** — `CountReject` возвращает «печатать»: для `residual` — `canon_residual <= 20` (свой счётчик);
   для остальных видов — `canon_self + canon_base + canon_big <= 20` (`:835`). **Чтение буквы «предел остальных видов
   прежний» (вариант исполнителя):** предел 20 строк сохранён, но отказы `residual` в него больше не входят — иначе отказы
   `residual` по-прежнему выбирали бы предел остальных видов, и пределы не были бы независимы. Если лид читает «прежний» как
   прежнее выражение суммы четырёх счётчиков — правка в одну строку (`:835`).
4. **Строка `capture … at=stop`** не менялась (формат — `:1343`–`:1345`, тот же текст, что `9635cb0f:…/shaderReplay.cpp:1319`–`:1321`).
   Строка `ShaderReplay: capture reject why=%s hash=… words=…` — тот же формат, `why` длиннее.
5. **Фикстуры** (`TestShaderReplayWalkBits`, `9238a182:tests/shaderCfgTests.cpp:15495`):
   - (б) `:15663` — `why` начинается с `residual branch=addr culprit=30:role2 ` (пробел после роли — чтобы `role20` не прошёл),
     содержит ` n=` и не содержит `%08x` сырого `s28`. Прогон: `why=residual branch=addr culprit=30:role2 n=1`.
   - (б2) `:15667` — ветвь `exact`: шейдер части (а), W (`num_records` V# C) = младшее слово адреса чтения D (база C + 0x200).
     Классификатор видит W как `INERT` (биты 8 и 0 оставляют чтения D в границах), каноническая `0x100 | (W & 0xF)` чтения D
     пропускает — замена не держится, W остаётся сырым как `ROLE_KEEP` с `kept_address` 0 (не адресная роль); точная проверка
     находит W среди запросов. Ожидание — ровно `residual branch=exact culprit=<W>:role0 n=1` без сырого значения. Прогон:
     `why=residual branch=exact culprit=36:role0 n=1` (W — слово 36: 2 + 32 + чтение 2).
   - (д) `:15782` — `CountReject`: 25 отказов `residual branch=addr …` + `self …` + `residual branch=exact …` + `base` + `big`
     дают `canon_residual` 26, `canon_big` 1 (суффикс не уводит в `canon_big`), `canon_mismatch` 27; строк `residual`
     напечатано 20, 26-й отказ `residual` не печатается, а `self`, `base`, `big` после 25 отказов `residual` печатаются
     (пределы независимы). Прогон: `residual=26 self=1 base=1 big=1 mismatch=27 printed_residual=20 self=1 exact=0 base=1
     big=1`.
6. **Поток и `KYTY_S_REPLAY=0`:** `Canonicalize` и `CountReject` в эмуляторе зовутся только из `HandleSpec` (`:1234`,
   `:1237`) — `Writer::Drain` (`:1187`), поток писателя захвата. При `KYTY_S_REPLAY=0` `ReplayInit` возвращается до создания
   `Capture` (`9238a182:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:7053` — якорь `if (mode == 0) {`, +1
   `return;`), писатель создаётся только при `CaptureOn()` (`:7082`) — новые места не исполняются [c кода].

**Состояние, которое правка вводит (правило отчёта о флагах):** `kept_role` — локальный вектор `Canonicalize` (`:643`),
ставится в `:705`, живёт один вызов, на каждом выходе разрушается автоматически; `culprit`, `culprit_addr`, `culprits` —
локальные. `CountReject` меняет только переданный `CaptureStats` (в эмуляторе — `m_stats` писателя, поток писателя, как до
правки). TLS, глобальных полей и замков правка не вводит.

## 3. Офлайн по п. 537(г)(4)–(5) (член (в)(7)) [c]

- **К1(7):** `git diff --stat 9635cb0f 9238a182 -- src/graphics/shader CMakeLists.txt` и файлы `SHADER_CACHE_EXTRA_FILES`
  (`shaderTranslationCache.cpp`, `gpu_format.h`, `gpu_defs.h`, `imageInfo.h`) — **пусто** (`k1_7_diffstat.txt`, 0 строк).
  Вывод пробы подписи (`KYTY_S16D_JOBS` с пустым списком) бинаря тестов S17a4 — **байт в байт = S17a3** (`sig/out_S17a4.txt`):
  `S signature=KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19 enabled=1`.
  Строка `ShaderReplayLayout:` = S17a3 (`layout_S17a4.txt`); формат каталога не менялся, `CanonVersion` не поднят (канонические
  формы и набор принимаемых записей те же).
- **К2(1):** корпус T1 при `=0` против родителя — скрипт S17a `docs/track-s/s17a/corpus_s17a.py` без изменений: родитель —
  закреплённый бинарь тестов S17a3 `58daf5c5…` (`9635cb0f`), S17a4 — `e9d3664f…`; 269 строк A (CS 111, PS 158), 807 процессов,
  0 отказов, **0 из 269 отличий SPIR-V** в конфигурациях «ручка не задана» и `KYTY_S_REPLAY=0`, 0 строк `ShaderReplay` —
  **`ALL OK`** (`corpus_s17a4.out.txt`; `corpus_s17a.tsv` sha256 `ef3a0219…` = S17a3). Одно окно, 15,0 с.
- **`shader_cfg_tests`** (бинарь из чистого worktree `9238a182`): **133 теста, 0 строк `ShaderCfgTests: failed:`** (= S17a3: 133 /
  0; новых тестов нет — новые части внутри `TestShaderReplayWalkBits`) — `suite_S17a4.summary.txt`.
- **Порядок гейтов:** `check_gate_order.py --src src` (`C:/kyty/s113/`) — `GATE ORDER: clean`, вывод = S17a3
  (`gate_order_main.txt`; гейтов и ручек правка не добавляет).

## 4. Бинари [c]

Чистый worktree `C:/kyty/s288/s17a/wtS` переведён на `9238a182` (статус 0 строк до и после сборки), `configure` + сборка
`build_s17a.cmd S` (флаги `build_local.cmd`):

| Что | sha256 | Путь |
|---|---|---|
| эмулятор (для S17c) | `ed2686da6fc959b1b4f0f308a9cbd1bae20a2e97750b5823df70ccb8c8f41d5b` | `C:/kyty/s288/bin/kyty_emulator_ed2686da.exe` |
| тесты | `e9d3664f255f08e42756bf40aebdd26cd6a48e12196e5115bca74aae1fda1f7a` | `C:/kyty/s288/s17a4/bin/shader_cfg_tests_e9d3664f.exe` |

Строка версии эмулятора — `KytyPS5-2026-09-15-6a2987a-2336-g9238a182` (2 вхождения в exe). Установленный бинарь (FS7
`8df61c00`, п. 540) не тронут. Бинарь S17a3 `53595859` в S17c не идёт (п. 541(в)).

## 5. Ссылки

`refs_s17a4.py` (якорь — строка N `git show 9238a182:<путь>`, контроль — та же строка не равна N+1): 21 ссылка, `ALL OK`
(`refs_s17a4.out.txt`).

## 6. Не заявляется

Что правка снимет отказы или вернёт R-PIPE; что `canon_residual` в игре будет 0; что слова `ROLE_KEEP` не несут гостевых
адресов; что S-replay выполним или даст тёплый первый вход; что К3–К6 пройдут; что `R_B` 0,9865 — польза; что каталог верен
для первого входа пользователя; что S-replay закрывает промах `u_06`; что фризы входа вызваны шейдерами; полнота корпуса,
каталога и `eboot.bin`; ни одно число — не выигрыш. 60 FPS не обещаются.

## 7. Процесс

Первая команда записи этого звена (создание `C:/kyty/s288/s17a4/` и первая строка `times.txt`, 11:35Z) шла без префикса
проверки замка (замка не было в проверке той же минуты, 11:34:51Z) — нарушение формы общего правила 27, названо исполнителем.
Остальные команды — с проверкой замка и `STOP`; перед сборками — проверка API серий (строки `rule30` в `times.txt`; звеньев
прогонов `in_progress` не было). Сборка в `wtS` вначале упёрлась в `checkout` поверх скопированных файлов (содержимое = коммиту,
проверено `cmp`), файлы возвращены `git checkout --` и сборка повторена.
