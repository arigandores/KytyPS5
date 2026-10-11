
## FS14a (`HPP-812`, Emu Engineer) — бинарь отгрузки FS14: умолчание `KYTY_FIX_F24=1` (2026-10-11, UTC)

- Задание — п. 710(г)(1) (KytyPS5 `5b774c83`). Отчёт `docs/track-f/fs14a.md`, файлы `docs/track-f/fs14a/`, рабочая папка `C:/kyty/f287/fs14a/`.
- Коммит `main` `c8836f14` (`--only`, `src/graphics/presentation/window/joyPump.cpp`, `joyPump.h`): `KYTY_FIX_F24` не задана / `""` → 1, иначе `EnvValueOn`; одно чтение (`JoyPump::ReadKnob`, главный поток, `WindowCreate` до инициализации SDL); строка `FixF24: mode= b24=` по значению.
- Worktree `C:/kyty/f287/fs14a/wt` HEAD `76c1058f` = FS13 `ea6c6e9e` + `5c21c387` (`b50e90e8`), `e3aa4b4d` (`cd422a94`), `57f9e528` (`6eb0f1a1`), `c8836f14` (`76c1058f`); конфликтов 0.
- Бинарь FS14 sha256 `826fc0a0fb93aac9f0620baa7a411d3d0adbdc2fa9464bb2c2a7d9044cfa369e`, копия `C:/kyty/f287/bin/kyty_emulator_826fc0a0.exe` (+ `.sha256`); строка версии `KytyPS5-2026-09-15-6a2987a-1923-g76c1058f`; не установка — установленный `abab2196…` до и после.
- `check_gate_order.py` — clean (`main`, worktree); подпись `9177b4267de1fb8bac7d1113afd8733210addfac` = базе; `shader_cfg_tests` = FS13 (133 / 133, `failed:` 0, SPIR-V 360 байт в байт); в exe `FixF24: init_owner` ×1, `TestHidLoss: f24` ×1 (FS13 ×0).
- `verify_fs14a.py` `ALL OK`: «содержит» `5c21c387`, `57f9e528`, `c8836f14`, `e9dd8604`, `3630f116`, `227e1b36`, `cbfe8375`, `c94c49e0`, `726e751e`, `cb022252` — `git cherry` `-` (отрицательные контроли `+`); дифф против базы — 6 путей `src/` = файлам трёх коммитов F40 и FS14a, под `src/graphics/shader/` 0; умолчания 18 → 19 (+ `KYTY_FIX_F24`); `KYTY_S_REPLAY` = 3; кода Ф20 / F46a / `KYTY_DIAG_B32` нет.
- С 12:17:16Z в `in_progress` — серия `HPP-800`; замка на шагах не было, сторож не срабатывал.
- WIP по дыму: игрой не проверялся (FS14c). Не заявляется — п. 710(з).
