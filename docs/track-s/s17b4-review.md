# S17b4 — код-ревью правки S17a4 (RC1 S17b3) (Red Team, `HPP-623`; `ROADMAP.md` «СЕССИЯ 122» п. 541(в), 546)

**Вердикт: `PASS`.** Буква п. 541(в)(1)–(6) в коде `9238a182` соблюдена [c кода], свой прогон `TestShaderReplayWalkBits` на
бинаре тестов `e9d3664f…` — rc 0, ветви `addr`, `exact` и счётчик по префиксу дают ожидаемые строки (§3). Условие п. 537(г)(6)
для бинаря S17a4 выполнено: при `KYTY_S_REPLAY` = 0 изменённые функции не вызываются (§4) — условие переноса К2(2)
`s17c_v0`/`s17c_w0` без повтора по п. 537(е) в части кода выполнено. Дифф вне `src/graphics/shader/**` и списка подписи —
свой пересчёт К2(1) не нужен и не делался (§1). **RC — 0.** Наблюдения §5 — без RC (сценария отказа на букве нет).

Вход: п. 541 (KytyPS5 `144a41a6`), п. 546 (`1fec7ba7`), дифф `9635cb0f..9238a182`, отчёт `docs/track-s/s17a4/` (`7b1fc3e6`),
бинарь тестов `C:/kyty/s288/s17a4/bin/shader_cfg_tests_e9d3664f.exe`, бинарь эмулятора `C:/kyty/s288/bin/kyty_emulator_ed2686da.exe`.
Пометки: [c] — проверено кодом или своим прогоном; [I] — вывод. Игра не запускалась, код эмулятора не правился. Время —
`C:/kyty/s288/s17b4/times.txt` (`date -u`); файлы звена — `docs/track-s/s17b4/`.

## 1. Дифф (`git diff --stat 9635cb0f 9238a182 -- src tests`)

```
 .../host_gpu/renderer/pipeline/shaderReplay.cpp    | 54 ++++++++----
 .../host_gpu/renderer/pipeline/shaderReplay.h      | 13 ++-
 tests/shaderCfgTests.cpp                           | 99 +++++++++++++++++++++-
 3 files changed, 146 insertions(+), 20 deletions(-)
```

Один коммит кода в диапазоне — `9238a182` (прочие коммиты `9635cb0f..9238a182` — только `docs/`). `git diff --stat 9635cb0f 9238a182
-- src/graphics/shader CMakeLists.txt` и файлы `SHADER_CACHE_EXTRA_FILES` (`9238a182:CMakeLists.txt:156`:
`shaderTranslationCache.cpp`, `guest_gpu/gpu_format.h`, `guest_gpu/gpu_defs.h`, `image/imageInfo.h`) — пусто
(`s17b4/diffstat_sig.out.txt`, 0 байт) [c]. **Пересчёт К2(1) по букве п. 541(в) не нужен.**

## 2. Буква п. 541(в)(1)–(6) по коду [c]

Ссылки — `<коммит>:<путь>:<строка>`, якорь — строка, +1 — следующая; все 24 проверены `s17b4/anchors.py` (`ALL OK`,
`anchors.out.txt`). `SR` = `src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp`.

| Член | Место | Якорь / +1 | Вывод |
|---|---|---|---|
| (1) строка `why` | `9238a182:SR:797` | `why = fmt::format("residual branch={} culprit={}:role{} n={}", culprit_addr ? "addr" : "exact", culprit,` / `culprit_addr ? static_cast<uint32_t>(kept_role[culprit]) : 0u, culprits);` | форма по букве; сырого значения нет ✓ |
| (1) виновник и ветвь | `9238a182:SR:788` | `if (addr \|\| (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {` / `if (culprits == 0) {` | выражение прежнее (`9635cb0f:SR:778`+1); первый по индексу задаёт ветвь; слово под обе ветви — `addr`; `n` — каждое слово один раз ✓ |
| (1) роль `addr` | `9238a182:SR:704` | `kept_address[i] = role != ROLE_INERT ? 1u : 0u;` / `kept_role[i]    = role;` | роль классификатора до `ROLE_KEEP`; `kept_address` = 1 ⇒ роль ∉ {KEEP, INERT} (у KEEP каноническое = сырому, ветвь не входит) ⇒ `role` ≥ 2 [c кода] ✓ |
| (1) набор отказов | `:785–800` | — | обход без `break`, `return false` ⇔ `culprits` ≠ 0 — набор отвергаемых записей прежний ✓ |
| (2) счётчик | `9238a182:SR:824` | `const bool residual = why.starts_with("residual");` / `if (why.starts_with("self")) {` | было `why == "residual"` (`9635cb0f:SR:1205`+1 `m_stats.canon_residual++;`); `self` по префиксу как было (`9635cb0f:SR:1202`+1) ✓ |
| (2) тождество | `9238a182:SR:834` | `stats.canon_mismatch = stats.canon_self + stats.canon_residual;` / `return residual ? …` | прежнее ✓ |
| (3) пределы | `9238a182:SR:835` | `return residual ? stats.canon_residual <= 20u : stats.canon_self + stats.canon_base + stats.canon_big <= 20u;` / `}` | свой предел `residual`; прочие — 20 по своей сумме (чтение лида п. 546(б)); было общее (`9635cb0f:SR:1213`+1) ✓ |
| (3) место вызова | `9238a182:SR:1237` | `if (CountReject(m_stats, why)) {` / `LOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\n", why.c_str(),` | единственный вызов; все ветви `return false` `Canonicalize` задают `why` (`big`, `base`, `self …`, `residual …`) ✓ |
| (4) `at=stop` | `9238a182:SR:1343` | `LOGF("ShaderReplay: capture sources=%u … canon_mismatch=%u …` / `" gen=%" PRIu64 " canon_self=%u canon_residual=%u …` | не тронута ✓ |
| (5) фикстуры | `9238a182:tests/shaderCfgTests.cpp:15663`, `:15725`, `:15800`, `:15803` | см. `anchors.py` | (б) `addr` `culprit=30:role2` без сырого; (б2) `exact` `role0 n=1` без сырого; (д) суффикс в `canon_residual`, независимость пределов ✓ |
| (6) поток и состояние | `:643`, `:782–784`, `:823–836` | — | новое — локальные `kept_role`, `culprit*` в `Canonicalize` (куча, не стек) и `CountReject` над `m_stats` писателя; без TLS, глобалов, замков ✓ |

## 3. Свой прогон теста [c]

`KYTY_TESTS_FILTER=ShaderReplayWalkBits KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`, бинарь
`shader_cfg_tests_e9d3664f.exe` (sha256 `e9d3664f255f08e42756bf40aebdd26cd6a48e12196e5115bca74aae1fda1f7a` = отчёту S17a4),
rc 0, строк `ShaderCfgTests: failed:` — 0 (лог `s17b4/walkbits_e9d3664f.log`):

- `walk address: reads=4 low=005893c0 exact=0 canonical=0 why=residual branch=addr culprit=30:role2 n=1` — ветвь `addr`,
  `low` (адрес тестовой памяти хоста) в `why` не входит ✓;
- `walk exact: reads=8 w=36 canonical=0 why=residual branch=exact culprit=36:role0 n=1` — ветвь `exact` ✓;
- `count reject: residual=26 self=1 base=1 big=1 mismatch=27 printed_residual=20 self=1 exact=0 base=1 big=1` — суффикс
  считается в `canon_residual`, 21-й и далее `residual` не печатаются, `self`/`base`/`big` после 26 `residual` печатаются ✓;
- части (а) `walk bits` (`canonical=1`, `r_addr=0 stand_addr=6`) и (в) `canon stand` (`self … culprit=2:role6:00001000->00000000`)
  — как у S17b3 на `9635cb0f` ✓.

Бинарь тестов несёт код `9238a182` по поведению: на `9635cb0f` ожидания (б) и (б2) падают (`why=residual` без суффикса) [I по
коду `9635cb0f:SR:778`]. Бинарь эмулятора `kyty_emulator_ed2686da.exe` — sha256
`ed2686da6fc959b1b4f0f308a9cbd1bae20a2e97750b5823df70ccb8c8f41d5b`, строка версии в файле `KytyPS5-2026-09-15-6a2987a-2336-g9238a182`
(`s17b4/sha.txt`, `version.txt`) = отчёту [c].

## 4. п. 537(г)(6) для бинаря S17a4 — достижимость при `KYTY_S_REPLAY` = 0 [c кода]

Изменённые функции — `Canonicalize`, `CountReject`, `Writer::HandleSpec`; вызовов вне `shaderReplay.cpp` и тестов нет (поиск
`Canonicalize(`, `CountReject(` по `src/`). Цепочка единственная: `Writer::Drain` (`9238a182:SR:1187` — якорь
`HandleSpec(*slot.spec);`, +1 `}`) → `HandleSpec` (`9238a182:SR:1234` — якорь `if (!Canonicalize(*item.plan, …`, +1 комментарий
`// S17a4 (item 541(c)(2)-(3)): …`) → `CountReject` (`:1237`). `Writer` создаётся только конструктором `Capture`
(`9238a182:SR:1372` — якорь `Capture::Capture(Store& store, Catalogue initial, uint64_t generation)`, +1
`: m_writer(std::make_unique<Writer>(store, std::move(initial), generation)) {}`), `Capture` — только в `ReplayInit` при
`CaptureOn()` (`9238a182:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:7087` — якорь
`m_replay_capture = std::make_unique<ShaderReplay::Capture>(*m_replay_store, std::move(initial),`, +1
`std::max(generation, corrupt));`), а `ReplayInit` при `mode == 0` возвращается раньше
(`9238a182:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:7053` — якорь `if (mode == 0) {`, +1 `return;`). `Mode()`
читается один раз, «1»/«2»/«3» — включено, иначе 0 (`9238a182:SR:39` — якорь `static const int mode = [] {`, +1
`const char* value = std::getenv("KYTY_S_REPLAY");`); `CaptureOn()` — `Mode() == 1 || Mode() == 2` (`:49`+1). `pipelineCache.cpp`
в диффе не менялся. **При `KYTY_S_REPLAY` = 0 изменённое не исполняется ✓** — условие п. 537(е) в части кода для бинаря
`ed2686da` выполнено; сам перенос К2(2) — решение лида и печати S17c.

## 5. Наблюдения (без RC)

1. **Покрытие (д) одностороннее.** Фикстура проверяет, что `residual` не съедает предел прочих видов, но не проверяет предел
   самих прочих видов: правка `: … <= 20u` → `: true` (строки `base`/`big` без предела) тест проходит. На букве (5) этого члена
   нет, нынешний код верен — пункт не RC; при следующей правке `CountReject` — кандидат фикстуры.
2. **Строка `self` печатает сырое значение** (`culprit=<i>:role<r>:<raw>-><canon>`, `SR:751`, вне диффа) — в т. ч. для адресных
   ролей (`role6:00001000` в части (в)). Довод п. 541(в)(1) «младшее слово гостевого адреса ушло бы в коммитимые файлы чтения»
   к ней относится так же. Форма `self` задана п. 536–537 и служит формой свидетеля `s17c_c2`; менять её — решение лида, не
   этого звена. Для печати S17c изд. 3: ридер `s17c_read.py`, переносящий строки `capture reject` в коммитимые файлы,
   — маскировать значения `self` или не переносить их [I].
3. **Канал п. 541(б) в строке не различим.** INERT-слово, ставшее `ROLE_KEEP` и пойманное точной проверкой, печатается
   `branch=exact … role0`, как слово, которое классификатор сам счёл `KEEP` (`kept_role` для `exact` не печатается по букве (1)).
   По букве; если S17d понадобится различие — `kept_role` уже хранится, правка в одну строку.

## 6. Чек-лист кода

Хронометраж — не задет (в правке нет часов). Гонки — нет: всё новое на потоке писателя, `m_stats` пишется и читается им же
(`LogLine` в том же потоке, как было). Инварианты `*_bad` — не вводились. Ранние возвраты `Canonicalize` — каждый задаёт
`why`, счётчик на единственном месте вызова. Стек — `kept_role` в куче (`std::vector<uint8_t>`, `raw.size()` байт), поток гостя
не задет. Подпись трансляции — не меняется (§1). Новое имя ручки — нет.

## 7. Отступление процесса (называю сам)

Команды 11:49:41Z–11:50:37Z (`date`, `ls`, `git log`, `git diff --stat`, `curl` API) и опросы ожидания 11:52Z–12:30Z (`sleep`,
`grep`, `curl` статуса `HPP-575`) шли, пока у FS8e (`HPP-575`) был непустой `executionRunId`, вне окна `lock released` поправки
п. 535(г) (у серии не было ни одного `lock released`: тег `fs8_i` вышел rc=5 «procload busy» в 11:51:29Z без замка). Замка не было
ни разу. Тяжёлые команды (прогон теста, якоря, sha256) — после 12:30:07Z, когда API показал `executionRunId` FS8e пустым
(прогон закончился 12:21:54Z, серии по определению правила 30 нет). Звено на время ожидания ставилось `blocked` на `HPP-575`
(12:29:57Z) и снято (12:30Z).

## 8. Не заявляется

Что правка в игре верна (код в игре не исполнялся); что правка RC1 снимет отказы или вернёт R-PIPE; что `canon_residual` в игре
будет 0; что S-replay выполним или даст тёплый первый вход; что К3–К6 пройдут; что `R_B` 0,9865 — польза; что каталог верен для
первого входа пользователя; что S-replay закрывает промах `u_06`; что фризы входа вызваны шейдерами; ни одно число — не
выигрыш; 60 FPS не обещаются; цель (B) не меняется.
