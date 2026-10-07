# F25l2 (HPP-683, Red Team): ревью правок RC1, RC2, RC4 (F25k2) и бинаря T2

**Вердикт: `PASS`** — RC 0. Правки RC1, RC2, RC4 ревью F25l закрыты кодом `5064c5bb`, члены п. 616(б)(1)–(3) и п. 618(б)(1)–(3)
выполнены, чтение п. 618(б)(4) воспроизведено своей сборкой; путь `=1` по п. 613(г)(2) не испорчен; состав T2 верен. Серии
F25m ничто из этого отзыва не мешает. Замечания §5 — без RC.

Вход: п. 613 (KytyPS5 `e826a1ea`), 615 (`6da93d63`), 616 (`7a71a482`), 618 (`d062f3b3`) прочитаны целиком до первого
действия; отзыв F25l `5e57aea8:docs/track-f/f25l-review.md` §4; отчёт F25k2 `0c77ffda:docs/track-f/f25k2.md`; код `main`
`5064c5bb`; бинарь T2 `9745eb78…` (worktree `C:/kyty/f287/f25k2/wt`, HEAD `0c8fcba2`). Без замка и без игры; код не менялся;
установленный `kyty_emulator.exe` = FS9 `3861eeea…` (сверено sha256). Ссылки — `5064c5bb:<путь>:<строка>`, якорь и строка
+1 проверены скриптом `f25l2/refs_f25l2.py` по объектам git: на `5064c5bb` 25 из 25 `ALL OK`; на T2 `0c8fcba2` — 24 из 25
(промах — `videoOut.cpp:1366`: в T2 нет 6 строк `DiagF5`/`DiagF6` кода F16d, вызов стоит на строке 1360; то же различие, что
у T, п. 615(а)); отрицательный контроль на `297225af` (код F25k) — `FAILED`, 24 промаха из 25 (совпала только неизменная
`src/emulator.cpp:148`).

## 1. Что сделано своими руками

| Что | Итог | Файл |
|---|---|---|
| Своя сборка из своего worktree `C:/kyty/f287/f25l/wt`, переведённого на `0c8fcba2` (T2; локально — только цели проб в `CMakeLists.txt`), clang-cl Release, флаги `build_f25l.cmd`: `log_async_tests`, `diag_b32_tests`, `shader_cfg_tests`, проба `f25l2_probe`; вариант `log_async_tests_rc4off` — правка `rc4_off.py` F25k2 в моём worktree, сборка, `git checkout` файла | sha256 — `f25l2/bin_sha256.txt` | `f25l2/compose.txt` |
| t1 `log_async_tests` | `cases=19 failures=0`, `ALL OK` | `f25l2/run_f25l2.out`, `tests_mine/log_async_tests.log` |
| t1b `=0` байт в байт против кода до F25k (эталон F25k `log_async_tests_ref.exe`) | `seq0_ref` = `seq0_0` = `seq0_u` = `d268b0b0…`; `seq0_1` = `b11d5fc3…` (отличается) — ok | там же |
| t2 `diag_b32_tests` | `ALL OK` | там же |
| t3 `shader_cfg_tests` (без `KYTY_*`) | 133 теста, 0 строк `failed:` (= F25k2; у эталона FS8a fu нет `log.txt` — счёт сверен с журналом F25k2) | там же |
| t4 SPIR-V t3 против FS8a fu | 360 / 360, 0 различий | там же |
| t5 положительный контроль RC4 (своя сборка без проверки `t_sink_owner` в `Drain` / `ExitDrain`) | ребёнок `0xC0000005` за **11,0 с**, строка `Exception: code=0xe06d7363 depth=1` есть — ok по п. 618(б)(4) | `tests_mine/pc_rc4off.log` |
| Проба `f25l2_probe` (своя цель, в продукт не идёт) | §2 | `tests_mine/probe.out` |
| Состав T2 | §4 | `f25l2/compose.txt` |

## 2. Проба `f25l2_probe` на исходнике T2

| Проба | Форма | Итог |
|---|---|---|
| `stand0_two` (повтор пробы F25l) | `=0`, `KYTY_TEST_LOGSTALL=1:2000:1`, потоки A и B пишут строку раз в ≈ 1 мс | A **2 005 720** мкс, **B 2 005 607** мкс (на коде F25k было 106) — второй писатель ждёт; `TestLogStall: … on=caller … line="T1 1000?"` |
| `stand1_two` | то же при `=1` | A 27, B 12 мкс; `on=writer`, `line="T0 999?"` |
| `stand0_flush` (отступление 1 F25k2) | `=0`, стенд; поток A пишет, поток B только зовёт `Log::Flush()` раз в ≈ 1 мс | A 2 002 985, **B 2 002 525** мкс — `Flush` ждёт сна стенда |
| `lf_nostand` | `=0`, без стенда (`g_hooks` ложь), `KYTY_LONGFRAME=1`, 20 записей с потока под своим мьютексом | 20 строк `LongFrame:` поля как записаны (`n=0 dt_us=100000 log_async=0 t_ms=7000` …) — поток печати пишет и на пути `=0` без стенда |
| `lf_stand0` / `lf_stand1` | `=0` / `=1`, стенд, `KYTY_LONGFRAME=1` | 20 строк, `log_async` 0 / 1; время под мьютексом «Present» ≤ 1 мкс. Записи этой пробы сделаны до окна сна; запись внутри сна покрыта t1 `longframe_0` / `longframe_1` (`rec_max_us` 20 / 56 при 4 100 записях, 4 096 строк по порядку) |

## 3. Члены п. 616(б), п. 618(б)

| Член | Итог |
|---|---|
| **RC1:** сон стенда при `=0` держит запись | ✓. `HookWrite` при `=0` и `g_hooks`: логгер берётся до замка (`5064c5bb:src/common/logging/log.cpp:644`, якорь «const auto logger = GetLogger(); // before the stand lock: g_logger_mutex is never taken under it»; +1 — «if (logger == nullptr) {»), затем `g_stand_mutex` (`…log.cpp:648`, якорь «std::lock_guard  stand(Async::g_stand_mutex);»; +1 — «Async::SinkOwner owner;»), `StandPoint` внутри замка (`…log.cpp:650`, якорь «Async::StandPoint(logger, text);»; +1 — «// The old write of WriteImpl, unchanged.») и прежняя запись. Свидетельства: t1 `latency_0` `veh_us` 1 513 752 (≥ 1 400 000), проба `stand0_two` B 2 005 607 мкс. Порядок замков: под `g_stand_mutex` — только `StandPoint` (TLS роли, часы, `logger->log`) и запись `spdlog`; ни `g_logger_mutex`, ни замков эмулятора под ним нет — цикла нет. Ожидание замка стенда идёт внутри `WriteImpl` и потому попадает в `LogNs` формы харнесса (`CountWrite`, `…log.cpp:852`) так же, как ожидание замка приёмника `spdlog` при настоящей задержке. Других писателей файла мимо `WriteImpl` нет: `spdlog::` в `src` вне `log.cpp` — только строка сборки `src/common/CMakeLists.txt:28`. |
| RC1: путь `=0` без стенда байт в байт | ✓. `HookWrite` зовётся только при `g_hooks` (`…log.cpp:675`, якорь «if (Async::g_hooks) [[unlikely]] {»; +1 — «if (HookWrite(text, style)) {»), `g_hooks` = `g_on` ∨ `g_stand.armed`; t1b — sha равны. Это равенство файла, не машинного кода (п. 615(г)). |
| RC1: поле `line=` | ✓. `StandLineField` (`…log.cpp:228`, якорь «static std::string StandLineField(std::string_view text) {»; +1 — «std::string out(text.substr(0, 40));»): ≤ 40 байт; < 0x20, ≥ 0x7f, `"`, `\` → `?` (перевод строки виден как `?` в `line="T1 1000?"`); при `=1` поле называет строку, которую задержал писатель. Обрезка многобайтной UTF-8 даёт `?`, не рваный байт. |
| п. 618(б)(1): `Flush` при `=0` со стендом под замком стенда; замок стенда не под `g_logger_mutex` и не на потоке с `t_sink_owner` | ✓. `Flush` (`…log.cpp:589`, якорь «if (!Async::t_sink_owner) {»; +1 — «std::lock_guard stand(Async::g_stand_mutex);») — проба `stand0_flush` B 2 002 525 мкс. Под `g_logger_mutex` `Flush` зовёт только `SetupLogger` (`…log.cpp:603`), а он идёт только из `Initialize` до `InitAsync` (`…log.cpp:767`, якорь «SetupLogger();»; +1 — «InitAsync();»), когда `g_hooks` ещё ложь, — ветвь стенда не берётся; `Initialize` — один раз (`src/emulator.cpp:148`). `Shutdown` берёт `g_logger_mutex` после `Flush`, не вокруг. На потоке с `t_sink_owner` `HookWrite` возвращает «не взято» (`…log.cpp:641`, якорь «if (Async::t_sink_owner) {»; +1 — «return false;»), `Flush` идёт прежним путём. |
| **RC2:** при `=0` и `KYTY_LONGFRAME=1` Present из блока не пишет лог | ✓. В `FlipQueue::Flip` — только `Log::LongFrameRecord(…)` (`5064c5bb:src/graphics/presentation/videoOut.cpp:1366`, якорь «Log::LongFrameRecord(r.cfg->flip_status.count, (now_ns - long_frame_prev_ns) / 1000u, now_ns / 1000000u);»; +1 — «}»); `LOGF` блока удалён (дифф). `LongFrameRecord` (`…log.cpp:563`, якорь «void LongFrameRecord(uint64_t n, uint64_t dt_us, uint64_t t_ms) {»; +1 — «if (!LongFrame::g_on) {») — запись в статический массив и `store(release)`, без выделения, ввода-вывода и замков. Производитель один: `FlipQueue` один (`m_flip_queue`, `videoOut.cpp:288`), вызов под `m_mutex`. t1 `longframe_0`: 4 100 записей внутри сна стенда, наибольшая 20 мкс. |
| RC2: поток печати без замков эмулятора | ✓. `PrinterMain` (`…log.cpp:548`, якорь «static void PrinterMain() {»; +1 — «Async::SetThreadName(L"LongFramePrinter");») — `sleep_for(250 мс)`, `load(acquire)`, `Write`: замки лога (`g_logger_mutex`; `s.mu` при `=1`; `g_stand_mutex` и замок `spdlog` при `=0`), других нет. |
| RC2: поток не создаётся при выключенной мере | ✓. `InitAsync` (`…log.cpp:751`, якорь «LongFrame::g_on = Common::EnvFlagOn("KYTY_LONGFRAME");»; +1 — «if (LongFrame::g_on) {»; `…log.cpp:754`) — безусловное чтение, поток только при мере; t1 `longframe_off` `printer=0`, 0 строк. Чтение в `InitAsync` и в `videoOut.cpp` — одна функция `EnvFlagOn`. |
| **RC4:** признак TLS закрывает самоблокировку слива | ✓. `t_sink_owner` (`…log.cpp:158`) ставит `SinkOwner` (`…log.cpp:163`) после захвата замка у синхронного хвоста `Drain` (`…log.cpp:471`), `WriteSummary` (`…log.cpp:500`), записи и `Flush` стенда; `Drain` / `ExitDrain` при нём возвращаются (`…log.cpp:447`, `:509`, якорь «if (t_writer || t_in_queue || t_sink_owner) {»; +1 — «return;»). Деструктор стража объявлен после замка — признак снят до отпускания замка, прежнее значение восстановлено (вложенность верна). |
| RC4: положительный контроль (буква заменена п. 618(б)(4)) | ✓ своей сборкой: без проверки — 11,0 с и строка `Exception: code=0xe06d7363`; с проверкой — `die_owner` 6,0 с (5 с ожидания слива + остаток сна писателя 6 с), строк `0xe06d7363` в журнале 0. Контроль различает код до и после правки по обоим признакам. |
| п. 618(б)(2): `Enqueue` при `t_sink_owner` не ждёт места | ✓ (`…log.cpp:412`, якорь «if (!t_writer && !t_sink_owner && s.pending != 0 && s.pending + n > s.limit) {»; +1 — «const auto t0 = NowNs();»). При `=1` признак стоит только в хвосте `Drain` и в `WriteSummary`; постановка с такого потока — только строки обработчика исключения, прервавшего запись под `g_sink_mutex`; превышение предела ограничено ими. При `=0` `Enqueue` не зовётся. Ожидание здесь было бы тупиком того же класса, что RC4 (писатель не освободит место, пока поток держит `g_sink_mutex`). |
| п. 618(б)(3): ни одна ветвь кода игры не зовёт `Testing::` | ✓. `git grep "Testing::"` по `src` и `tests` на `5064c5bb`: определения в `log.cpp` и вызовы только в `tests/LogAsyncTests.cpp`. Точка в `SinkWrite` (`…log.cpp:273`, якорь «if (t_sink_owner && g_test_owner_fault.exchange(false)) [[unlikely]] {»; +1 — нарушение доступа): на писателе обрывается на ложном TLS, на пути `=0` `SinkWrite` не зовётся. |
| Путь `=1` по п. 613(г)(2) не испорчен | ✓. Изменения на пути `=1`: условие `Enqueue` и возвраты `Drain`/`ExitDrain` по `t_sink_owner` (ложь на всех потоках вне хвоста — поведение прежнее), строка проверки TLS в `SinkWrite`, поле `line=` строки стенда. Писатель по-прежнему не держит замков эмулятора, замок очереди не держится через ввод-вывод, обработчик исключения идёт в `t_nested` / `Enqueue` без ожидания. t1: `order`, `full`, `latency_1` (`veh_us` 8, `maxlat_us` 95), 7 путей смерти и `die_kill` — ok. |

## 4. Состав T2 (`f25l2/compose.txt`)

`git log 11164d72..0c8fcba2` — 6 переносов `554eaafa..929b6073` + 3 F25k + `0c8fcba2` (= `5064c5bb`); `git cherry -v main 0c8fcba2
11164d72` — `-` у 8, `+` у `554eaafa`, `5836f6d7` (те же, что у T; правило п. 615(б)(5) сверено лидом); блобы `log.cpp`, `log.h`,
`LogAsyncTests.cpp` в `0c8fcba2` = в `5064c5bb`; `git diff 5064c5bb 0c8fcba2 -- videoOut.cpp` — только 6 строк `DiagF5`/`DiagF6`
и `#include` F16d (их нет в линии отгрузки, к F25k2 не относится); `git diff --stat 2afd998c 0c8fcba2` = дифф `5064c5bb`
(4 файла, +327 / −28). sha256 закреплённой копии `C:/kyty/f287/f25k2/kyty_emulator_9745eb78.exe` = `build/install` =
`9745eb7851d541740ce9730b86258f7bb26cab270f0d35434d43037c5cefd885`; строки версии и подписи в exe сверены лидом (п. 618(в)),
мной не повторялись. Правка не трогает `src/graphics/shader/**` — подпись трансляции не меняется (t4 360 / 360).

## 5. Замечания без RC

1. **Поток печати меры пишет через `Write` и считается в `LogNs`.** При форме харнесса (`b36_f0`/`b36_f1`) его время записи (и
   ожидание сна стенда при `=0`, если сон взял он или он стоит за ним) ложится в счётчик лога потока с ролью `other`. Члены
   п. 613(г)(3) для `f0`/`f1` — кадры ≥ 2,5 с / ≥ 1 с, не `log_us`, поэтому серии не мешает; ридеру F25m: сумма `log_us` по
   потокам (чтение F25i RC4) у тегов с `KYTY_LONGFRAME=1` включает поток `LongFramePrinter` — к держателю кадра не относить.
2. **Замок стенда при `=0` сериализует все записи до конца прогона** (и после k снов) — та же сериализация, что даёт один замок
   `basic_file_sink_mt`; добавлен один незанятый замок на строку. Различает ли это что-то в тегах `=0` стенда — [I], ожидаемо нет.
3. **`SetupLogger` → `Flush` под `g_logger_mutex`** — структурно есть, но достижим только до `InitAsync` (ветвь стенда не
   берётся); при повторном `Initialize` со стендом порядок `g_logger_mutex` → `g_stand_mutex` появился бы без цикла (под
   `g_stand_mutex` `g_logger_mutex` не берётся) — тупика нет.
4. **Процесс (моё отступление).** Два файла пробы (`F25l2Probe.cpp`, `add_target.py`) записаны инструментом Write прямо в
   `C:/kyty/f287/f25l2/`, а не черновиком в папку прогона с переносом (общее правило 31); замка не было ни в одной проверке
   хартбита (каждая команда начиналась проверкой `C:/kyty/SEALED_RUN.lock`). Остальные файлы — черновиком и переносом.

## 6. Для лида и F25m

RC нет; член п. 613(г)(2) «с закрытыми RC» выполняется этим отзывом (при приёмке лидом). F25m — бинарь T2 по п. 618(в); в
печать — члены п. 616(г) с окном «≤ 250 мс» (п. 618(б)(5)), строка RC3 (п. 616(б)(4)); замечание §5 п. 1 — ридеру.

## 7. Не заявляется

п. 616(е), 615(г), 613(и), 611(з), 608(е), 596(л) целиком; что код `KYTY_FIX_B36` верен в игре и бинарь T2 работает в игре;
что RC4 был тупиком на этой сборке; что `=0` в машинном коде T2 равен FS9; что стенд воспроизводит настоящую задержку файловой
системы на машине пользователя по длительности и охвату; что слив завершается быстро при медленной файловой системе; что
механизм Ф27 есть или нет на пути по умолчанию; ни одно число — не выигрыш; 60 FPS не обещаются.
