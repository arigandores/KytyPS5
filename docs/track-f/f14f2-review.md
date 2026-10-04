# F14f2 — ревью F14e2 (трек F, `HPP-546`, Red Team)

**Вердикт: PASS.** Требуемых изменений — 0. Замечаний без правки кода — 3 (Н1–Н3, §7), отклонений процесса звена — 3 (§8).

Код `f98e842c` закрывает RC1 и RC3 отзыва F14f по п. 443(б); члены п. 443(в)(1)–(4) повторены своим worktree, своей сборкой и своим кодом
чтения [c]; пять мутантов на пробу RC3 (M5 F14f и четыре своих) ловятся; поправки RC2, RC4, RC5 сверены с файлами и кодом [c].

Вход (прочитан до первого действия, 12:08–12:10Z): `0d69abc5:docs/ROADMAP.md` п. 443, 456 (строки 22407, 22512), п. 415, 409, 425(б);
комментарий лида `08095d14` в `HPP-546`; отчёт `574bf7ff:docs/track-f/f14e2.md`; отзыв `e975327c:docs/track-f/f14f-review.md` §6.

## 1. Сверка коммита (п. 443(в)(1), п. 456(в)(1)) [c]

| Член | Результат |
|---|---|
| родитель `f98e842c` | `d5d0076a35063ebd…` (`git cat-file -p`) = `d5d0076a` ✓ |
| дерево двух путей = `cde1106c` | `git diff cde1106c f98e842c -- CMakeLists.txt tests/shaderCfgTests.cpp` — пусто ✓; `git patch-id --stable` обоих — `e0af2501…` ✓ |
| состав `f98e842c` | 2 файла, 93+/1− (`git show --stat`) ✓ |
| `CMakeLists.txt` — только строка RC1 | дифф — одна строка `SHADER_CACHE_EXTRA_FILES`, добавлен только `$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h` (`f98e842c:CMakeLists.txt:156`, якорь «$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h»; +1 — «-P ${KYTY_SOURCE_DIR}/generate_version.cmake») ✓ |
| отчёт `574bf7ff` | 33 файла, все под `docs/track-f/f14e2*` (0 вне) ✓ |
| после переноса | `f98e842c` — предок `HEAD` `main`; после него эти пути менял только `9c726d74` (F19c) — `CMakeLists.txt` +5 строк, строка RC1 цела ✓ |

Таблица политик глубины — `f98e842c:src/graphics/host_gpu/renderer/image/imageInfo.h:193` (якорь «inline constexpr std::array<DepthFormatPolicy, 2>
DEPTH_FORMAT_POLICIES {{»; +1 — «{Prospero::DepthFormat::kZ16,»); `FindGuestDepthFormatPolicy` — там же (`inline constexpr`), её входы — перечисления
`gpu_format.h`/`gpu_defs.h` (уже в наборе) и `vk::Format` (на решение «ручной/нативный» не влияет). Других файлов, от которых зависит решение `=1`
(`f98e842c:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:40`, якорь «return !null_descriptor &&
FindGuestDepthFormatPolicy(format) == nullptr;»; +1 — «}»), вне набора подписи нет [c чтения].

## 2. Контроль подписи (п. 443(в)(2)) — свой повтор [c]

Два независимых способа:

**(а) `generate_version.cmake` напрямую** (`sig_f14f2.py`, те же `-D`, что цель `KytyGitVersion`; список нового набора сверен со строкой
`CMakeLists.txt` worktree — `cmake_list_eq_new True`). Правка — комментарий `// F14f2 positive control comment` перед `struct DepthFormatPolicy {`
в `imageInfo.h`, затем возврат байтов (sha256 файла до = после, `git status` 0 строк):

| Набор файлов | Без правки | С правкой | Откат |
|---|---|---|---|
| база (3 файла, `d5d0076a`) | `1b5f270a…` | `1b5f270a…` (RC1 воспроизведён: правка не видна) | — |
| `f98e842c` (+ `imageInfo.h`) | `a54ae4bd…` | `c0d2ca7e…` (≠) | `a54ae4bd…` |

`sig_f14f2.out.txt` — `ALL OK`. Хэш правки ≠ `18c369ee` F14e2 — другой текст комментария (ожидаемо).

**(б) Настоящая сборка** своего каталога `C:/kyty/f287/f14f2/build`: `kytyGitVersion.h` на `d5d0076a` — `KYTY_SHADER_SOURCE_HASH "1b5f270a…"`, на
`f98e842c` — `"a54ae4bd…"`; после сборки мутанта X4 (правка `ResourceMaterialization.cpp`) — `"da41309e…"`, после восстановления — снова
`"a54ae4bd…"` ✓.

## 3. Набор `shader_cfg_tests` (п. 443(в)(3)) — свой повтор [c]

Свои exe из своего worktree: база `d5d0076a` — `460fd32c…`, звено `f98e842c` — `53b24884…`. Свой читатель `suite_f14f2.py` (написан заново, без
импорта `suite_f14e2.py`); шесть прогонов, все `KYTY_*` сняты, `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 KYTY_TESTS_SPV_DIR`:

| Чтение | Результат |
|---|---|
| (s1) rc 0 и 0 строк `ShaderCfgTests: failed:` в `bu`, `b0`, `b1`, `fu`, `f0`, `f1` | ✓ |
| (s2) тесты звена = тесты базы (129) + `TestF19NullComparisonImage` последним (130) | ✓ |
| (s3) N = 176; `b0` = `bu` байт в байт (без переменной = `=0` на базе); `fu`, `f0` файлы 0..175 = `bu`; `f1` файлы 0..175 = `b1` (`b1` ≠ `bu` в 4 файлах — места `k16UNorm` F14e) | ✓ |
| (s4) у прогонов звена 180 файлов | ✓ |
| (s5) строки `[f19] null T#` по п. 443(б): `=1` — одиночные `native=1 dref=1 manual=0`, общий сэмплер `native=2 manual_images=0 dref=2 manual=0`; `=0` и без переменной — одиночные те же, общий `native=0 manual_images=2 dref=0 manual=2` (C и C_LZ) | ✓ |
| (s6) файлы одиночных проб `f1` = `f0` = `fu`; файлы проб общего сэмплера `f0` = `fu`, `f1` ≠ `f0` | ✓ |

`suite_f14f2.out.txt` — `ALL OK`. Первая попытка печатала (s5) `False` — дефект моего читателя (stdout exe в CRLF), не кода; вывод сохранён как
`suite_f14f2.out.try1_crlf.txt`, правка читателя — `chr(13)` снимается.

Проба — `f98e842c:tests/shaderCfgTests.cpp:5803` (якорь «void TestF19NullComparisonImage() {»; +1 — «const bool fix_f19 =
Common::EnvFlagOn("KYTY_FIX_F19");»), запуск — `f98e842c:tests/shaderCfgTests.cpp:15702` (якорь «RUN(TestF19NullComparisonImage);»; +1 — пустая
строка). Пустой T# пробы (`s[0:7]` = 0) — пустой и по критерию транслятора (`f98e842c:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:123`,
якорь «return descriptor.dwords[0] == 0 && (descriptor.dwords[1] & 0xffu) == 0;»; +1 — «}»), и по критерию рендерера
(`f98e842c:src/graphics/shader/shaderBindings.h:101`, якорь «IsNull() const { return Base40() == 0; }»; +1 — «Prospero::BufferFormat Format()
const {») — оба читают только 40 бит адреса, расхождения критериев нет [c чтения]; заглушка `D32` выбирается рендерером по тому же условию, что
проверяет проба (`f98e842c:src/graphics/host_gpu/renderer/pipeline/descriptors.cpp:1336`, якорь «const bool native_compare = binding ==
TextureCache::BindingType::Texture &&»; +1 — «resource.depth_compare && !resource.manual_depth_compare;»).

## 4. Мутанты (п. 443(в)(4) и свой мутант п. 443(г)) [c]

`mut_f14f2.py`: правка целыми строками (число совпадений 1, байты LF), сборка `shader_cfg_tests` своего каталога, exe сохраняется, откат
`git checkout --`, `git status` 0 строк после каждого; три прогона (`=1`, `=0`, без переменной), исход — по строкам `failed:` (rc у exe 0 и при
падениях — Н2).

| Мутант | Что меняет | `=1` | `=0` | без | Ожидание | Исход |
|---|---|---|---|---|---|---|
| M5 (`docs/track-f/f14f/mut/M5/mutant.diff`) | правило `=1` без `!null_descriptor` | 4 строки падений (обе пробы × C, C_LZ) | 0 | 0 | fail/pass/pass | **ловится** |
| X1 (тест) | проба (2) без общего сэмплера: `k16UNorm` на своём S# `s[20:23]` с тем же `LESS_EQUAL` | 0 | 2 («…must both be the manual compare at KYTY_FIX_F19=0») | 2 | pass/fail/fail | **ловится** |
| X2 (тест) | ожидание `=1` пробы (2) заменено ручным узором | 2 | 0 | 0 | fail/pass/pass | **ловится** |
| X3 (код) | правило `=1` вырождается в правило до правки (`format != k32Float`) | 5 (две старые пробы `k16UNorm`, косвенная таблица и обе новые пробы (2)) | 0 | 0 | fail/pass/pass | **ловится** |
| X4 (код) | место вызова `:603` передаёт `false` вместо `NullImageDescriptor(descriptor)` (M5 другим местом) | 4 (обе пробы × C, C_LZ) | 0 | 0 | fail/pass/pass | **ловится** |

Чтение мутантов: M5 и X4 ловят только новые пробы (у F14f M5 выжил — набор и гейт `ALL OK`); X1 — ожидание `=0` пробы (2) держится общим
сэмплером (проход `f98e842c:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:1213`, якорь «if
(images[pair.image].manual_depth_compare && samplers[pair.sampler].depth_compare) {»; +1 — «samplers[pair.sampler].depth_compare = false;»), то
есть проба действительно исполняет его; при `=1` X1 не отличим — проба (2) при `=1` доказывает только «обе нативные», а общий сэмплер при `=1`
работает лишь против правила, делающего кого-то ручным (X3); X2 — проверка `=1` не тавтологична (код даёт нативный узор).

## 5. Поправки RC2, RC4, RC5 (п. 443(б)) — сверка с файлами [c]

- **RC2.** `cd C:/kyty/f287/f14e && sha256sum -c` по строкам нового манифеста `574bf7ff:docs/track-f/f14e2/bin_f14e_fixed.sha256.txt` — 5 из 5
  `OK`; свой `sha256sum`: `fix_shader_cfg_tests.exe` и `build/shader_cfg_tests.exe` — `feffeec7…`, `build/shader_recompiler_compute_tests.exe` —
  `3dd0c319…`, `C:/kyty/f287/bin/kyty_emulator_c01bde0c.exe` — `c01bde0c…afbe2d7`; старый манифест `f18022a5:docs/track-f/f14e/bin_f14e.sha256.txt`
  называет `4833a35f…`/`9b254b77…` — с текущими файлами не совпадают ✓.
- **RC4.** `C:/kyty/f287/f14e/gpu/c0/run.log` (12 строк) кончается `--- abort() ---`, `SIGABRT in abort:0`, `rc=3221226505 end
  2026-10-04T10:17:31Z` ✓; строка `f18022a5:docs/track-f/f14e.md:191` (якорь «| `c0` `=0 --fix-f19-comparison-depth` |»; +1 — пустая строка)
  печатает «rc 127»; `C:/kyty/f287/f14a/sampled_depth.log` (14 строк) числа rc не содержит, «rc 127» стоит в строке GPU-теста
  `a015bb9f:docs/track-f/f14a.md:69`; сводка `gpu_f14e2.out.txt` для `c0` печатает `watchdog/test rc=127` — поправка верна ✓.
- **RC5.** Стенд `KYTY_RECOMPILE` берёт флаг `manual_depth_compare` из файла кэша и пересчитывает его `FixF19ManualDepthCompare(format, false)`
  (`f98e842c:tests/shaderCfgTests.cpp:15399`, якорь «ShaderRecompiler::IR::FixF19ManualDepthCompare(format, false);»; +1 — «(image.manual_depth_compare
  ? kept_manual : to_native)++;»); место вызова `f98e842c:src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp:603` (якорь
  «FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));»; +1 — «} else {») корпус не исполняет — поправка верна ✓.

Раздел поправок — `574bf7ff:docs/track-f/f14e2.md:130` (якорь «## 6. Поправки к `f14e.md` (п. 443(б); отчёт F14e не переписывается)»; +1 — пустая
строка).

## 6. Чек-лист кода (Red Team)

- Правка в `src/graphics/shader/**` — нет; подпись трансляции меняется правкой `CMakeLists.txt` (`1b5f270a` → `a54ae4bd`) — сказано (п. 456(г)) ✓.
- Ручки: новых нет; `FixF19Enabled()` читается один раз (`static const`), проба читает переменную сама — в одном процессе значения равны ✓.
- Порядок тестов: новая проба последней — номера файлов 0..175 не сдвигаются ((s3)) ✓.
- `src/` не тронут ⇒ поведение эмулятора при любом `KYTY_FIX_F19` не меняется, кроме подписи (холод каталога трансляции) ✓.
- Гонок, ранних возвратов, стека гостя правка не касается (только CMake и тест) ✓.

## 7. Замечания без правки кода (исход — у лида, п. 324(и)(5))

- **Н1 (подпись молча пропускает отсутствующий файл).** `f98e842c:src/generate_version.cmake:51` (якорь «if(EXISTS "${SHADER_SOURCE}")»; +1 —
  «file(SHA1 "${SHADER_SOURCE}" SHADER_DIGEST)»): файл набора, которого нет на диске, исключается без ошибки. Сценарий: перенос или переименование
  `imageInfo.h` (или любого из трёх прежних файлов) при неизменённой строке `CMakeLists.txt` — сборка проходит, подпись перестаёт покрывать таблицу,
  кэш отдаёт старое решение «ручной/нативный» (последствие RC1 F14f возвращается молча). Сейчас путь существует — свой положительный контроль §2 [c].
  Механизм старше звена; правка (например, `message(FATAL_ERROR)` в `else`) — вне задания F14e2.
- **Н2 (rc exe при падениях).** При `KYTY_TESTS_CONTINUE=1` `shader_cfg_tests` возвращает 0 и при строках `failed:` (M5, X1–X4: rc 0, строки 2–5) —
  читатель обязан считать строки; читатели F14e2 (r1) и мой (s1) так и делают.
- **Н3 (сторож F14e2 — ложный отказ воспроизведён).** 13:14:02–13:14:25Z `watch_f14e2.py` отказал 5 сборкам мутантов (`REFUSED: procload`, pids чужих
  bash с подстрокой имени шлюза в тексте команды), при этом `api_chk.sh` (признак argv) — шлюзов 0. По п. 456(в)(3) при порте сторож перенесён в
  `watch_f14f2.py` с признаком «элемент argv оканчивается на `procload.py`»; фикстура `fx_watch_f14f2.py` на поддельных процессах — 7 из 7, `ALL OK`
  (случаи 4–5 — текст команды с именем шлюза — подстрочным признаком считались бы шлюзом). Настоящий отказ сторожа F14e2 в 12:35:45Z (`KILLED:
  procload` pid 54396 — шлюз F18e) верен.

Не находка: пустой T# пробы целиком нулевой, T# с адресом 0 и ненулевыми прочими битами проба не исполняет — критерии транслятора и рендерера
одинаковы (40 бит адреса, §3), сценария расхождения нет.

## 8. Процесс звена (отклонения — у долга одно из трёх, п. 324(и))

1. **Правило 31:** правка `C:/kyty/f287/f14f2/suite_f14f2.py` (снятие `\r`) сделана инструментом Edit прямо в `C:/kyty/` около 12:19:15Z, а не
   черновиком и переносом; замка не было в команде 12:18:58Z и в команде 12:19:23Z [c `times.txt`]. Исправлено далее: все прочие правки — командой
   Bash с проверкой замка. Влияние на данные — нет (файл своего звена).
2. **Строки API в `times.txt`** моих шагов печатает скрипт F14e2 `api_chk.sh` с префиксом «F14e2 API check before 'F14f2 …'» — читать по имени шага в
   кавычках (`F14f2 …`); не исправлено, читать так.
3. **Ожидание замка 12:21–12:26Z:** команда мутанта вышла с кодом 3 до записи; время появления замка — не `date -u` (команда вышла до неё), строка
   `times.txt` 12:26:43Z записана после снятия с временем «~12:21Z» (правило 23: момент события — [I], снятие — по строке FS6a 12:26:30Z [c]).
   Под замком процессов не запускал и файлов не писал (ожидание — `[ -e lock ]` и `sleep`). Серия F18e (`HPP-541`, теги с игрой) — сборки дольше
   60 с ждали её `done` (13:13:55Z); в окне между тегами две попытки X2 сняты/отказаны сторожем (12:35:45Z `KILLED`, 13:13:11Z `REFUSED` — шлюз ждал
   тега); восстановительная сборка 13:18:32–13:18:53Z (21 с) при серии `HPP-561` — команда < 60 с (правило 30).

Серия: до 13:13Z команды дольше 60 с шли только при звене Harness Engineer «без игры» (`HPP-553`, п. 425(б)) — конфигурация 12:15:06–12:15:58Z,
сборка базы 12:16:06–12:17:03Z.

## 9. Не заявляется

Что Ф19 `FIXED` (до F14h); что пустой T# со сравнением встречается в игре; что заглушка `D32` проверена привязкой (набор её не исполняет); что
расхождение видно в кадре игры и его величина; что PCF драйвера равен ответу PS5; порядок «сравнить, затем фильтровать» как текст ISA; ответ PS5 на
`_C` по цветовому формату; формат гостя за `D32_SFLOAT` ручных мест до члена (г)(0)(а); что вариант (A) покрывает все места игры; что Ф10 `FIXED` до
F12h; что Б4 воспроизводится до F15b; что SPIR-V корректен для устройства и картинка верна; что сборка детерминирована (exe одного исходника в одном
каталоге: `53b24884…` и `66e5fa67…`); ни одно число — не выигрыш; 60 FPS не обещаются.

## 10. Файлы и время

Файлы — `C:/kyty/f287/f14f2/`, в git — `docs/track-f/f14f2/` (sha256 — `SHA256SUMS_f14f2.txt`; exe, логи сборок `build_*.log` и `mut/build_*.log`
(предупреждения компилятора; лог конфигурации содержит путь профиля), каталоги `build/`, `wt/`, `suite/` — только локально): `build_f14f2.cmd`, `sig_f14f2.py` → `sig_f14f2.out.txt`, `suite_f14f2.py` → `suite_f14f2.out.txt` (+ `suite_f14f2.out.try1_crlf.txt`),
`mut_f14f2.py` → `mut_M5.out.txt`, `mut_X1.out.txt`…`mut_X4.out.txt`, `mut/*.diff`, `port_watch_f14f2.py`, `watch_f14f2.py`,
`fx_watch_f14f2.py` → `fx_watch_f14f2.out.txt`, `refs_f14f2.py` → `refs_f14f2.out.txt` (ссылки отчёта — 15 из 15 по якорю и +1, `ALL OK`).

| exe | sha256 (16) |
|---|---|
| база `d5d0076a` | `460fd32c668e460d` |
| звено `f98e842c` | `53b2488464a71290` |
| M5 / X1 / X2 / X3 / X4 | `d32c9e20cd510354` / `dc63cffa7d67af27` / `7b9512e3c32c12c7` / `1657da9f3d61f768` / `869ac73e55750c36` |

Время (UTC, `C:/kyty/f287/times.txt`): старт 12:10:05Z; worktree 12:11:09Z; контроль подписи 12:11:41Z; подмодули 12:14:57Z; конфигурация
12:15:06–12:15:58Z; сборки базы и звена 12:16:06–12:17:41Z; набор 12:19:23Z; ожидание замка 12:21–12:26Z; ожидание серии F18e до 13:13:55Z;
сторож и фикстура 13:15:24Z; мутанты 13:15:35–13:18:06Z; восстановление 13:18:55Z; ссылки 13:20Z.
