# FS9a (`HPP-671`, Emu Engineer): девятый бинарь отгрузки трека F (FS9) — умолчание `KYTY_FIX_B13=1`

Задание — `ROADMAP.md` п. 604(д)(1) (KytyPS5 `07d31ad3`, якорь «(1) **FS9a (Emu Engineer, без замка).**»), звенья — п. 604(ж), факт —
п. 605 (`4a1e7c97`); критерий Б13 — п. 595(е); правило базы — п. 410(г)(6)(i). Игра не запускалась; установленный
`ps5 em/kyty_emulator.exe` — S18 `b3cee576…` до и после звена, `C:/kyty/build/install` и кэши не тронуты. Время — UTC по `date -u`,
события — `C:/kyty/f287/times.txt` (строки `FS9a`). Метки: [c] — показано кодом или выводом, [I] — вывод, [U] — неизвестно.
Замка `C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` за звено не было (каждая команда начиналась проверкой). В `in_progress` шло звено
Harness Engineer `HPP-669` F25f (серия), поэтому каждая команда дольше 60 с (worktree, configure, сборки, стенд, тесты) шла под сторожем
`watch_fs9a.py` по п. 431(в)(1), а перед ней в `times.txt` писалась строка проверки API (`api_chk.sh`). Сторож не срабатывал ни разу.
**WIP по дыму: бинарь собран и проверен стендом и тестами, игрой не проверялся** (теги — FS9c после FS9b).

## Итог

- **Коммит в `main`: `e4e5701a`** (`--only`, 2 файла, +15/−9): умолчание `KYTY_FIX_B13` 0 → 1 в форме FS4a `17adaf80`; комментарии стенда.
- **Worktree `C:/kyty/f287/fs9a/wt`, HEAD `11164d72`** — база S18a2 `0005e11f` (последний принятый лидом и установленный бинарь отгрузки,
  S18 `b3cee576`, п. 588, 590; другого принятого бинаря отгрузки к сборке нет — п. 604(д)(5)) + cherry-pick `-x`:

  | Шаг | Источник | Коммит в worktree | Конфликт |
  |---|---|---|---|
  | 1 | `1570d110` (стенды и хуки) | `0107f69e` | нет |
  | 2 | `21f8ca76` (F24c) | `21db93d1` | один — строка контекста `#include "common/diagB32.h"` в `regionManager.h`, как у F24c (п. 601(б)) |
  | 3 | `e4e5701a` (FS9a) | `11164d72` | нет |

  Разрешение шага 2 — `resolve_fs9a.py` (копия `resolve_wtB_f24c.py` F24c: допускает ровно один блок заданной формы; сторона S18 без
  `diagB32.h` + добавляемое правкой `#include "common/envFlag.h"`). Иных конфликтов нет; `git status --short` — 0 строк, CR в `src/` — 0 [c `cp.log`, `mk_wt.log`].
- **Бинарь FS9: sha256 `3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5`**, копия
  `C:/kyty/f287/bin/kyty_emulator_3861eeea.exe` (+ `.sha256`; `build/kyty_emulator.exe` = `build/install/kyty_emulator.exe`). Строка версии
  `KytyPS5-2026-09-15-6a2987a-1900-g11164d72`. **Не установка.** В exe: `KYTY_FIX_B13` ×1, `FixB13: mode=` ×1, `KYTY_DIAG_B32` ×0 [c].
- Члены п. 604(д)(1) — все ✓:

  | Член | Итог | Источник |
  |---|---|---|
  | стенд без переменной = ожидания `=1` (forced 11/12/13 × `bdabits` 0/1, free 11/12 × 0/1, контроли — 0; `FixB13: mode=1`) | ✓ 14 плеч по 10⁵, пропусков 0 | `runs_stand/summary.txt` S1–S4 |
  | `=0` forced точка 1 `bdabits` 0 — пропуск ≥ 1, `mode=0` | ✓ 10⁵ из 10⁵ | S5 |
  | `memory_tracker_tests`, `shader_cfg_tests` при умолчаниях = базе | ✓ | `tests.out.txt` |
  | подпись `KYTY_SHADER_SOURCE_HASH` = базе `9177b426…` | ✓ `9177b4267de1fb8bac7d1113afd8733210addfac` у обеих сборок | `binary_fs9a.txt` |
  | таблица умолчаний = базе + `KYTY_FIX_B13` (и только он) | ✓ 13 → 14 | `verify_fs9a.out.txt` V3 |
  | `KYTY_S_REPLAY` = 3 как у базы | ✓ | V4 |
  | дифф против базы — только `1570d110`, `21f8ca76`, FS9a | ✓ | V2 |
  | «бинарь содержит» `21f8ca76` — равенство изменённых строк с отрицательным контролем | ✓ | V1 |
- `check_gate_order.py` (`C:/kyty/s113/`) — `GATE ORDER: clean` на `main` после правки и на worktree до сборки; выводы байт в байт равны (гейтов и ручек правка не добавляет) [c].

## Код (`e4e5701a`, в worktree — `11164d72`)

`src/graphics/host_gpu/regionManager.h` (`e4e5701a`, строки 46–60):

```cpp
// Track F, F24c (HPP-662, ROADMAP s122 item 595(d)): knob KYTY_FIX_B13, read once per process. At 1
// ... (текст F24c о порядке и строке "FixB13: mode=<0|1>" сохранён)
// Track F, FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other
// value as EnvValueOn (the form of FS4a 17adaf80).
[[nodiscard]] inline bool FixB13Enabled() noexcept {
	static const bool on = [] {
		const char* value = std::getenv("KYTY_FIX_B13");
		return value == nullptr || value[0] == '\0' || Common::EnvValueOn(value);
	}();
	return on;
}
```

- До FS9a: `static const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B13"));` — не задана = 0.
- Строка `FixB13: mode=` (`memoryTracker.cpp`), ветки `=1` и `else` `ChangeState<Cpu, true>`, хуки `KYTY_TEST_B13_HOOK` — не тронуты [c `main.diff`:
  изменённые строки только в блоке `FixB13Enabled` и в комментариях стенда].
- **Стенд `tests/B13EpochStand.cpp` правится — только комментарии:** (а) Н4 п. 603(б)(4), строка 6: `KYTY_B13_TEST_HOOK` → `KYTY_TEST_B13_HOOK`;
  (б) строки 10–11 и 34: «unset» теперь — порядок `=1` (прежний текст «at 0 or unset the writer is the text of F24a» после FS9a ложен).
  Логика стенда читает ручку через `FixB13Enabled()` и не менялась. Файлов `src/graphics/shader/**` и `CMakeLists.txt` правка не трогает.
- Пути по коду [c]: без переменной, `""` и `=1` — порядок F24c `=1`; `0/false/off/no` — ветка `else` (текст до F24c дословно).

## Состояние, вводимое правкой

| Состояние | Установка | Снятие | Довод |
|---|---|---|---|
| `on` (static local `FixB13Enabled`, `regionManager.h:54`) | один раз — первый вызов (C++11 magic static, потокобезопасно; первый вызов — конструктор `MemoryTracker`, F24c) | нет — на время процесса | как до FS9a (была static local); меняется только выражение инициализации; значение — функция окружения процесса |

Нового состояния правка не вводит. Выход функции один (`return on`); лямбда без захвата, вызывается один раз при инициализации.

## Стенд (`run_stand_fs9a.py`, сборка worktree, 10⁵ на плечо)

`b13_epoch_stand` sha256 `70b99144…`, `b13_epoch_stand_swap` `6ac7db2c…`; окружение плеча — все `KYTY_*` сняты, ручка — только у плеч `=0`/`=1`.
Стена 17 с (04:49:38–04:49:55Z).

| Ручка | Режим | Точка | `bdabits` | Пропуск | `FixB13: mode` |
|---|---|---|---|---|---|
| нет | forced | 11 / 12 / 13 | 0 / 1 | **0** (все 6) | 1 |
| нет | free | 11 / 12 | 0 / 1 | **0** (все 4) | 1 |
| нет | before / after | — | 0 / 1 | **0** (все 4) | 1 |
| `0` | forced | 1 | 0 | **10⁵ из 10⁵** | 0 |
| справка: нет | forced | 1 | 0 | отказ `exit 2` (`bad arguments` — точка порядка `=0`) | — |
| справка: `0` | free | 1 | 0 | 8 | 0 |
| справка: `1` | forced | 11 | 0 | 0 | 1 |

Члены S1–S5 — PASS, `ALL OK`. Справочное плечо «нет, точка 1» показывает, что без переменной стенд больше не принимает точку порядка `=0`.
Числа стенда — не частота в игре.

## Тесты (`run_tests_fs9a.py`)

База — та же сборка worktree на `0005e11f` до cherry-pick (04:45–04:47Z), FS9 — после (04:48–04:50Z); все `KYTY_*` сняты.

| Тест | База (умолчания) | FS9 (умолчания) | Равно |
|---|---|---|---|
| `memory_tracker_tests` | rc 0, `all cases passed`, строки `FixB13` нет (в базе ручки нет) | rc 0, `all cases passed`, `FixB13: mode=1` | ✓ |
| `shader_cfg_tests` | rc 0, 133 теста, `ShaderCfgTests: failed:` 0, строк со словом `failed` 5 | то же; мультимножество строк `failed` равно | ✓ |

Справка FS9 при `=0` / `=1`: те же итоги, `FixB13: mode=` по значению. Первый прогон сравнения (`tests_r1.out.txt`) — `FAILED` из-за ошибки
моего члена: я требовал строку `FixB13: mode=1` и от `shader_cfg_tests`, который `MemoryTracker` не создаёт (строки нет ни в базе, ни в FS9).
Член исправлен до повторного сравнения (для `shader_cfg_tests` — строки `FixB13` как у базы); данные тестов не перезапускались.
(Список HANDOFF §4 «14 известных падений» на этом дереве не воспроизводится — 0 падений и у базы, как у F24c.)

## Источник (`verify_fs9a.py`, вывод `verify_fs9a.out.txt`, `ALL OK`)

- **V1 «содержит»:** изменённые строки (по файлам, мультимножества `+`/`-`) коммита worktree = источнику: `1570d110` → `0107f69e` 905/905,
  `21f8ca76` → `21db93d1` 115/115, `e4e5701a` → `11164d72` 24/24. `git cherry`: `1570d110` `-`, `e4e5701a` `-`, `21f8ca76` `+` (patch-id
  отличается строкой контекста `#include`, изменённые строки равны — как у F24c). Отрицательные контроли: `21f8ca76` против `0107f69e` —
  не равно; против своего коммита с одной испорченной строкой — не равно ✓.
- **V2 дифф против базы:** `git diff --name-only 0005e11f 11164d72` — 5 путей (`CMakeLists.txt`, `memoryTracker.cpp`, `regionManager.h`,
  `tests/B13EpochStand.cpp`, `tests/B27DaSlotStand.cpp`) = объединению файлов трёх коммитов; знаковое мультимножество изменённых строк
  диффа = сумме трёх коммитов (1 000 строк). Отрицательный контроль — сумма без FS9a не равна ✓.
- **V3 таблица умолчаний** (свой сканер — форма `knobs_fs8a.py`: чтение `getenv`, в окне 3 строк `== nullptr || … EnvValueOn`):
  база — 13 ручек (`KYTY_FIX_B1B`, `B24`, `B26`, `B4`, `B42`, `B9A`, `DUALSRC`, `F10`, `F19`, `F8`, `MINIMIZE`, `SVAL`, `KYTY_S_PCW` = список FS8a);
  FS9 — те же 13 + `KYTY_FIX_B13`. Отрицательный контроль на `21db93d1` (до FS9a) — разность пуста, член там не выполнен ✓.
- **V4 `KYTY_S_REPLAY`:** `shaderReplay.cpp` — blob базы = FS9 (`e1626ad6…`), `ParseMode`: не задана или `""` — 3 ✓.
- **V5:** путей диффа под `src/graphics/shader/` нет; подпись обеих сборок `9177b426…` (`base/kytyGitVersion_base.h`, `kytyGitVersion_fs9.h`) ✓.

## Ход (UTC, `times.txt`)

- `04:43:01Z` — начало; `04:43:36Z` — первая строка правки (`patch_fs9a.py` на `main`); `04:43:52Z` — коммит `e4e5701a`.
- `04:44:29Z` — первая попытка `mk_wt_fs9a.sh` под сторожем: rc 1, `bash` из `PATH` сторожа — не Git Bash (worktree не создан); повтор с
  `C:/Program Files/Git/bin/bash.exe` — `04:44:41Z` worktree готов.
- `04:44:45–04:45:20Z` — configure; `04:45:24–04:46:25Z` — версия, `memory_tracker_tests`, `shader_cfg_tests` базы; `04:47:00–04:47:02Z` — тесты базы.
- `04:47:33Z` — cherry-pick (шаги 1–3), `check_gate_order.py`; `04:47:39–04:48:09Z` — сборка `kyty_emulator`.
- `04:48:20–04:49:02Z` — сборка `memory_tracker_tests`, стендов, `shader_cfg_tests`; `04:49:38–04:49:55Z` — стенд; `04:49:56Z` — тесты FS9.
- `04:51:07Z` — копия бинаря; sha256 установленного — `b3cee576…`.

Флаги сборки = FS8a (`build_fs9a.cmd` — копия `build_fs8a.cmd` с путями `fs9a`); Release, clang-cl, LTO.

## Файлы

`C:/kyty/f287/fs9a/`, копии в `docs/track-f/fs9a/` (текстовые — LF):
- **Скрипты:** `patch_fs9a.py`, `mk_wt_fs9a.sh`, `cp_fs9a.sh`, `resolve_fs9a.py`, `build_fs9a.cmd`, `bstep.sh`, `sstep.sh`, `api_chk.sh`,
  `watch_fs9a.py`, `fixpaths_fs9a.py`, `run_stand_fs9a.py`, `run_tests_fs9a.py`, `verify_fs9a.py`.
- **Выводы:** `patch_main.out.txt`, `main.diff`, `mk_wt.log`, `cp.log`, `gate_order_main.out.txt`, `gate_order_wt.out.txt`, `runs_stand/`
  (18 плеч и `summary.txt`), `tests/base/`, `tests/fs9/`, `tests.out.txt`, `tests_r1.out.txt`, `verify_fs9a.out.txt`, `binary_fs9a.txt`,
  `kytyGitVersion_fs9.h`, `base/kytyGitVersion_base.h`, `runs/log_*.txt` (выводы шагов под сторожем), `commit_msg_code.txt`.

В копиях `mk_wt_fs9a.sh`, `cp_fs9a.sh` адрес агента заменён на `<agent-email>` (общее правило 28).

## Не заявляется

- что Б13 проявляется в игре, с какой частотой и видно ли это на картинке; что правка меняет картинку или время кадра;
- что числа стенда — частота в игре; что машинный код эмулятора сохраняет порядок записей;
- что часть «бит до глобальной» проверена в игре (при `bdabits` 0 она не действует); что путь `armdefer` безопасен при включённом гейте;
- что FS9 работает в игре (дыма не было, до FS9c); что FS9 установлен (до FS9d); что прочие `SCENE_OK` держатся на FS9;
- что набор тестов полон; что реестр полон; ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
