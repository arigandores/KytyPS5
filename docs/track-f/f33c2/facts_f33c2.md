

F33c2 (`HPP-748`, Emu Engineer) — стенд `KYTY_TEST_EXITFATAL` издания 3: плечо CN и член C `done_seen` = 0, п. 681(в) (2026-10-10, UTC)

- Код издания 3 в `main` `5237fdff` (только `src/emulator.cpp`, `ExitFatalStand`; `src/common/subsystems.*` = `227e1b36` байт в байт;
  стенд выключен без переменной). Плечо CN: как C, плюс второй фатал (`EXIT_IF`) инжектора внутри его обхода перед первым колбэком,
  строка `ExitFatal: nested_fatal`. Отчёт `docs/track-f/f33c2.md`, файлы `docs/track-f/f33c2/` (копия `C:/kyty/f287/f33c2/`).
- Бинарь F33c2 (только стенд): worktree `ee9632be` + `227e1b36` + `e5979953` + `5237fdff` → `b007ce5f`; `check_gate_order.py` clean
  (main и worktree); sha256 `a086872d30833ac4…`, строка `…-1913-gb007ce5f`, подпись `9177b426…` = FS11; копия
  `C:/kyty/f287/bin/kyty_emulator_a086872d.exe`; не установлен. Бинарь тега F33e — `2b393af8…` без изменений.
- N и seed — комментарий `915b2396` 17:58:54Z до данных. Прогоны 17:59:08–18:01:03Z: `=1` CN 50 (3001–3050), C 50 (3001–3050),
  P2 200 (3001–3200); `=0` CN 50 (справка), C 50 — `read_f33c2.py` `MEMBERS ALL YES`: CN `walks` 1, `nested` 0, `reenter` 2,
  `expired` 0, `expired_seen` 0, код 321, `hang` 0, `crash` 0, 0,150–0,458 с, `nested_fatal` 50 из 50; C `done_seen` 0 в 50 из 50 и
  прежние члены; P2 контроль 200 из 200, классы 0; `=0` C K1 0; `=0` CN `walks` 3, `nested` 2. Остатков процессов 0.
- Фикстуры: `test_read_f33c2.py` 41 случай `ALL OK`, `test_driver_f33c2.py` (образцы F33d) `ALL OK`. Игры, замка и `STOP` не было;
  FS11, `C:/kyty/build/install` и кэши не трогались. Не заявляется — п. 681(ж). Дальше — F33d2 (Red Team).
