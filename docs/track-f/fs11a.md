# FS11a (`HPP-714`, Emu Engineer): одиннадцатый бинарь отгрузки трека F (FS11) — умолчание `KYTY_FIX_B12=1`

Задание — `ROADMAP.md` «СЕССИЯ 122» п. 647(д)(1) (KytyPS5 `4801601d`, якорь «(д) **Отгрузка FS11 — константы лида.** (1) **FS11a
(Emu Engineer, без замка).**»); вывод — п. 647(в), Н3 — п. 647(г) (член FS11b); образец — FS10a п. 624(е)(1), отчёт
`docs/track-f/fs10a.md`; правило базы — п. 410(г)(6)(i), 627(г); член «содержит» — п. 615(б)(5). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — FS10 `abfded5e…` до и после звена, `C:/kyty/build/install` и кэши не тронуты. Время — UTC по `date -u`,
события — `C:/kyty/f287/times.txt` (строки `FS11a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно. Замка
`C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). Звено Harness Engineer
`HPP-711` (F30f) было `in_progress` с `executionRunId` (строка API в `times.txt`, 00:50:48Z) — по общему правилу 30 все шаги дольше
нескольких секунд (configure, сборки, тесты, стенд) шли под сторожем `watch_fs11a.py` (п. 431(в)(1)); сторож не срабатывал. **WIP по
дыму: бинарь собран и проверен тестами и стендом без игры, игрой не проверялся** (теги — FS11c после FS11b и F30f).

## Итог

- **Коммит в `main`: `cb022252`** (`--only`, 1 файл `src/graphics/host_gpu/regionManager.h`, +8/−3): умолчание `KYTY_FIX_B12` 0 → 1
  в форме FS4a `17adaf80` / FS9a (`FixB13Enabled`) / FS10a `7f34b1e2`.
- **Worktree `C:/kyty/f287/fs11a/wt`, HEAD `ee9632be`** — база FS10 `dc5d4712` (worktree FS10a, установленный FS10 `abfded5e`,
  п. 627–628; другого принятого лидом бинаря отгрузки нет) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `73a6e411` (F29a: стенд `b12_bdastamp_stand`, цель CMake) | `edebaad9` | нет (авто-слияние `CMakeLists.txt`) |
  | 2 | `c94c49e0` (F29c: `KYTY_FIX_B12`, издание 1) | `2a371d92` | нет (авто-слияние `frameStats.h`, `regionManager.h`, `bufferCache.cpp`, `bufferCache.h`, `videoOut.cpp`) |
  | 3 | `726e751e` (F29c издание 2) | `dab16a57` | нет (авто-слияние `frameStats.h`, `bufferCache.cpp`, `bufferCache.h`, `videoOut.cpp`) |
  | 4 | `0db3b3eb` (F29c3: плечо B12-9b) | `eded064e` | нет |
  | 5 | `cb022252` (FS11a) | `ee9632be` | нет (авто-слияние `regionManager.h`) |

  Конфликтов нет ни одного; `git status --short` — 0 строк, CR в `src/` — 0 [c `cp_*.log`, `mk_wt.log`]. Риск априора лида (п. 647(з):
  конфликт `c94c49e0` в `frameStats.h` / `videoOut.cpp` рядом с полями F30d) не наступил: изменённые строки переноса равны источнику
  (V1), код F30d `585d997d` не предок FS11, счётчиков `rts_bad_b` / `rts_bad_rx` и `KYTY_DIAG_B32` в добавленных строках 0 (V6), в exe
  `rts_bad_b` ×0, `KYTY_DIAG_B32` ×0. Зависимости от кода вне базы нет: сборка `kyty_emulator`, тестов и стенда без него прошла.
- **Бинарь FS11: sha256 `ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce`**, копия
  `C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe` (+ `.sha256`; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка
  версии `KytyPS5-2026-09-15-6a2987a-1910-gee9632be`. **Не установка.** В exe: `KYTY_FIX_B12` ×1, `FixB12: mode=` ×1, `FixB12Stat:` ×1,
  `KYTY_FIX_B13` ×1, `KYTY_FIX_B36` ×1, `LogAsync: mode=` ×2, `KYTY_DIAG_B32` ×0, `rts_bad_b` ×0, строка подписи
  `9177b4267de1fb8bac7d1113afd8733210addfac` ×1 [c `binary_fs11a.txt`].
- Члены п. 647(д)(1):

  | Член | Итог | Источник |
  |---|---|---|
  | «бинарь содержит» `c94c49e0`, `726e751e` — `git cherry` `-` или равенство отсортированных строк `+`/`-`, счёт скриптом с отрицательным контролем | ✓ изменённые строки равны (250 / 250, 95 / 95), `git cherry` `-` у обоих; та же проверка у `73a6e411` (464), `0db3b3eb` (39), `cb022252` (11) — равны, `-`; отрицательные контроли: `726e751e` против переноса `c94c49e0` — не равно; против своего переноса с одной испорченной строкой — не равно | `verify_fs11a.out.txt` V1 |
  | дифф FS11 против базы вне `tests/` — только файлы `c94c49e0`, `726e751e` и FS11a | **по букве — нет: плюс `CMakeLists.txt` из `73a6e411`** (стенд F29a, который п. 647(д)(1) сам велит переносить). Все 11 изменённых строк `CMakeLists.txt` — внутри блока цели `b12_bdastamp_stand` (`EXCLUDE_FROM_ALL`; 3 строки комментария, `add_executable`, 3 источника, `)`, `target_link_libraries`, `target_include_directories`, пустая), удалённых 0; цель `kyty_emulator` не тронута [c V2b]. Прочие пути вне `tests/` (6) — файлы `c94c49e0` / `726e751e` / FS11a. Полный дифф: 8 путей = объединению пяти коммитов, знаковое мультимножество изменённых строк = сумме пяти (807 строк); без FS11a — не равно | V2, V2b |
  | стенд `b12_bdastamp_stand` из того же worktree при умолчании (без переменной) — плечи (е)(1) `=1` `MEMBERS ALL OK` | ✓ стенд берёт ручку из окружения через ту же `Libs::Graphics::FixB12Enabled` [c `B12BdaStampStand.cpp`: `FixB12Enabled()`]. Раннер `run_stand_fs11a.py` = `run_f29c3.py` (матрица члена (е)(1), печать `p0_f29c3.md`) с четвёртым аргументом: `default` — плечи «1» без `KYTY_FIX_B12` (допуск плеча требует `fix_b12=1` от умолчания), плечи «0» — с `KYTY_FIX_B12=0`. 10 000 итераций: `default` — 73 плеча, `MEMBERS ALL OK`; `explicit` (справка, явная `=1`) — `MEMBERS ALL OK`; строки 72 плеч `default` = `explicit` = матрице F29c3 (`run_f29c3.out.txt`) по всем полям. **Отрицательный контроль:** та же форма `default` на стенде F29c3 (`b12_stand_e3.exe`, умолчание 0) — `MEMBERS FAILED` (все плечи «1» — `fix_b12=0`) | `stand/out_default.txt`, `stand/out_explicit.txt`, `stand/out_negctl_e3_default.txt`, `runs/log_stand_*.txt` |
  | `memory_tracker_tests`, `shader_cfg_tests` — строки `failed:` и счёт = базе | ✓ `memory_tracker_tests` rc 0 / 0, строк `failed` 0 / 0, `MemoryTrackerTests: all cases passed` у обоих; `shader_cfg_tests` rc 0 / 0, `[test]` 133 / 133, `ShaderCfgTests: failed:` 0 / 0, мультимножество строк со словом `failed` (5) равно; справка t4: SPIR-V 360 / 360 байт в байт (агрегат `b1376644` = FS10a) | `tests/base/`, `tests/fs11/`, `runs/log_tests_*.txt` |
  | подпись трансляции (`KYTY_SHADER_SOURCE_HASH`) = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у сборки базы и FS11; путей диффа под `src/graphics/shader/` 0 (V5) | `base/kytyGitVersion_base.h`, `kytyGitVersion_fs11.h` |
  | таблица умолчаний своим сканером — база FS10 + `KYTY_FIX_B12` (и только он) | ✓ 15 → 16; отрицательный контроль на `eded064e` (до FS11a) — разность пуста, член там не выполнен | V3 |
  | `KYTY_S_REPLAY` = 3 | ✓ blob `shaderReplay.cpp` базы = FS11 (`e1626ad6…`), `ParseMode` не задана / `""` → 3 | V4 |
  | sha256 и копия `C:/kyty/f287/bin/kyty_emulator_<sha8>.exe`, не установка | ✓ `kyty_emulator_ea51ae80.exe`; установленный `abfded5e…` до и после | `binary_sha.txt` |

- `check_gate_order.py` (`C:/kyty/s113/`) — `GATE ORDER: clean` на `main` после правки и на worktree до сборки; выводы (без строки
  заголовка) байт в байт равны выводам FS10a; гейтов и ручек правка не добавляет [c].

## Код (`cb022252`, в worktree — `ee9632be`)

`src/graphics/host_gpu/regionManager.h`, `FixB12Enabled` (`cb022252:src/graphics/host_gpu/regionManager.h:67`, якорь «// Track F,
FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other»; +1 — «// value as
EnvValueOn (the form of FS4a 17adaf80).»; в worktree — `ee9632be:src/graphics/host_gpu/regionManager.h:66`, те же якоря):

```cpp
// Track F, FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other
// value as EnvValueOn (the form of FS4a 17adaf80).
[[nodiscard]] inline bool FixB12Enabled() noexcept {
	static const bool on = [] {
		const char* value = std::getenv("KYTY_FIX_B12");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return on;
}
```

- До FS11a: `static const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B12"));` — не задана = 0. Из комментария заголовка
  убрано «default OFF - unset, "", 0/false/off/no = OFF (Common::EnvValueOn)»; остальной текст заголовка F29c не тронут.
- Одно чтение сохранено: статическая локальная `on`, инициализация потокобезопасна по C++11; читатели ручки в `src/` FS11 — два
  вызова `FixB12Enabled()`: конструктор `BufferCache` (`ee9632be:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:602`, якорь
  «const bool               fix_b12 = FixB12Enabled();»; +1 — «if (!fix_b12_logged.exchange(true, std::memory_order_relaxed)) {») и
  `RenderContext::PrepareBda` (`ee9632be:src/graphics/host_gpu/renderer/renderContext.cpp:382`, якорь «const bool fix_b12 =
  FixB12Enabled();»; +1 — «if (fix_b12) {») [c `git grep FixB12Enabled() ee9632be -- src`]; ручка `KYTY_FIX_B12` в `src/` читается
  только в `FixB12Enabled`.
- Строка `FixB12: mode=<0|1>` печатается по значению, как в F29c (`ee9632be:src/graphics/host_gpu/renderer/cache/bufferCache.cpp:604`,
  якорь «LOGF("FixB12: mode=%d\n", fix_b12 ? 1 : 0);»; +1 — «}»): без переменной теперь `mode=1`. Строка `FixB12Stat:` и код
  `c94c49e0` / `726e751e` не тронуты.
- Пути по коду [c]: без переменной, `""`, `1/true/on/yes` — `on` = 1; `0/false/off/no` — 0 (путь `=0` по коду = база FS10 — сверка FS11b).
  Файлов `src/graphics/shader/**` и `CMakeLists.txt` правка FS11a не трогает (`CMakeLists.txt` диффа — из `73a6e411`). Тестов, читающих
  умолчание `KYTY_FIX_B12`, кроме стенда, нет [c `git grep KYTY_FIX_B12 ee9632be -- tests`: только `B12BdaStampStand.cpp`, где ручка
  читается через `FixB12Enabled`]; его раннеры F29c/F29d/F29c3 задают `KYTY_FIX_B12` явно в каждом плече — правкой не затронуты.
- Ссылки этого отчёта проверены скриптом `refs_fs11a.py`: `REFS 5 ALL OK`, отрицательный контроль (сдвиг +1) — `FAILED`.

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `on` (статическая локальная `FixB12Enabled`, `regionManager.h:68` в worktree) | один раз — первый вызов `FixB12Enabled` (конструктор `BufferCache` или `PrepareBda`; в стенде — модель) | не снимается (время жизни процесса) | как до FS11a (была статической локальной с тем же временем жизни); меняется только выражение инициализации |

Нового состояния правка не вводит. Лямбда без захвата вызывается один раз; выходов функции не прибавилось.

## Тесты и стенд (`run_tests_fs11a.py`, `run_stand_fs11a.py`)

База — та же сборка worktree на `dc5d4712` до cherry-pick (сборка тестов 00:52:31–00:53:38Z, прогон 00:53:42–00:53:44Z); FS11 — после
(сборка `kyty_emulator` 00:54:11–00:55:00Z, тестов и стенда 00:55:01–00:55:43Z, тесты 00:56:19–00:56:20Z, стенд 00:56:30–00:56:49Z); все
`KYTY_*` сняты (тесты) или заданы плечом (стенд). sha256: `shader_cfg_tests.exe` FS11 `36c1a91e…`, `memory_tracker_tests.exe` `4daf3e30…`,
`b12_bdastamp_stand.exe` `2116221a…`. Список HANDOFF §4 «14 известных падений» на этом дереве не воспроизводится — 0 падений у базы и
у FS11, как у FS10a. Справка: в выводе `memory_tracker_tests` строки `FixB12:` нет ни у базы, ни у FS11 (тест не строит `BufferCache`),
`FixB13: mode=1` у обоих.

## Ход (UTC)

- `00:48:40Z` — первая команда (проверка замка); `00:49:47Z` — строка начала в `times.txt`; `00:50:12Z` — строка коммита `cb022252` и
  `check_gate_order.py` на `main` (`GATE ORDER: clean`).
- `00:50:48Z` — проверка API (`HPP-711` в `in_progress`, серия); `mk_wt_fs11a.sh` (worktree, подмодули архивом).
- `00:51:02–00:51:50Z` — configure; `00:52:23–00:52:26Z` — версия базы; `00:52:31–00:53:38Z` — сборка тестов базы; `00:53:42–00:53:44Z` —
  прогон тестов базы.
- `00:53:49–00:53:52Z` (mtime `cp_*.log`) — cherry-pick 1–5; `00:53:58Z` — `check_gate_order.py` на worktree (`GATE ORDER: clean`).
- `00:54:02–00:54:10Z` — configure; `00:54:11–00:54:44Z` — сборка `kyty_emulator`; `00:54:51–00:54:54Z` — версия FS11; `00:54:55–00:55:00Z` —
  повтор сборки (10 шагов ninja после генерации версии; sha256 FS11 снят после него); `00:55:01–00:55:43Z` — сборка тестов и стенда;
  `00:56:19–00:56:20Z` — тесты FS11; `00:56:30–00:56:49Z` — стенд (`default`, `explicit`, отрицательный контроль); `00:58:30Z` — копия
  бинаря, sha256 установленного — `abfded5e…`.

Флаги сборки = FS10a (`build_fs11a.cmd` — копия `build_fs10a.cmd` с путями `fs11a`); Release, clang-cl, LTO.

## Файлы

`C:/kyty/f287/fs11a/`, копии в `docs/track-f/fs11a/` (текстовые — LF):
- **Скрипты:** `patch_fs11a.py`, `port_fs11a.py` (порт вспомогательных скриптов FS10a со строкой истории), `mk_wt_fs11a.sh`,
  `cp_fs11a.sh`, `build_fs11a.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`, `watch_fs11a.py`, `run_tests_fs11a.py`,
  `mk_run_stand_fs11a.py`, `run_stand_fs11a.py`, `verify_fs11a.py`, `refs_fs11a.py`.
- **Выводы:** `patch_main.out.txt`, `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `mk_wt.log`, `cp_*.log`, `tests/base/` и
  `tests/fs11/` (без `spv/`), `runs/log_*.txt`, `stand/out_*.txt`, `verify_fs11a.out.txt`, `refs_fs11a.out.txt`, `binary_fs11a.txt`,
  `binary_sha.txt`, `kytyGitVersion_fs11.h`, `base/kytyGitVersion_base.h`, `commit_msg_code.txt`.

В копии `cp_fs11a.sh` адрес агента заменён на `<agent-email>` (общее правило 28); в прочих скриптах адреса нет.

## Не заявляется

П. 647(и) целиком; в частности: что FS11 работает в игре (дыма не было, до FS11c); что FS11 установлен (до FS11d); что Б12 проявляется в
игре, с какой частотой и видно ли это на картинке; что игра даёт раскладку дыры; что ветка повторного визита проверена в игре; что путь
`=1` FS11 по машинному коду равен пути `cabbd818` (сверка — FS11b); что набор тестов полон; что реестр полон; ни одно число — не выигрыш;
60 FPS не обещаются; цель (B) не меняется.
