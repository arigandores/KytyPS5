
## FS14a издание 2 (`HPP-812`, Emu Engineer) — Ф29 в FS14 по поправке п. 712(г)(1) (2026-10-11, UTC)

- Review лида издания 1 — «Доработать» (Ф29 не исполнен); Ф24-часть издания 1 принята как есть. Отчёт `docs/track-f/fs14a.md` (издание 2), файлы `docs/track-f/fs14a/`.
- Коммит `main` `78e45af3` (`--only`, `src/graphics/host_gpu/renderer/cache/faultManager.cpp`, `faultManager.h`): `KYTY_FIX_F29` не задана / `""` → 1, иначе `EnvValueOn`, в форме FS13a `3630f116`; одно чтение (`static const`); строка `FixF29: mode=` по значению.
- Worktree `C:/kyty/f287/fs14a/wt` HEAD `eb7e8b91` = `76c1058f` + `15c9d2f2` (`c5eb48b0`) + `78e45af3` (`eb7e8b91`); конфликтов 0 (в `CMakeLists.txt` тоже).
- **Итоговый бинарь FS14 sha256 `013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd`**, копия `C:/kyty/f287/bin/kyty_emulator_013e1974.exe` (+ `.sha256`); версия `KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91`; не установка — установленный `abab2196…` до и после. Промежуточный `826fc0a0` (только Ф24) в FS14 не идёт.
- `verify_fs14a_f29.py` `ALL OK`: «содержит» 12 из 12 (`git cherry` `-`, отрицательные контроли `+`, в т.ч. `15c9d2f2`/`78e45af3` в `76c1058f`); `src/` диффа — 8 путей (F40, FS14a, `faultManager.cpp`/`.h`), `src/graphics/shader/` 0, вне `src/` — 4 пути `15c9d2f2`; умолчания 18 → 20 (+ `KYTY_FIX_F24`, `KYTY_FIX_F29`); `KYTY_S_REPLAY` = 3.
- `check_gate_order.py` clean (`main`, worktree); подпись `9177b4267de1…` = базе; `shader_cfg_tests` = FS13 (133/133, `failed:` 0, SPIR-V 360 байт в байт); в exe `FixF24: init_owner`, `TestHidLoss: f24`, `FixF29: mode=` — по ×1 (FS13 ×0).
- Стенд `f29_fault_stand` своей сборки, зерно 71201, `R` = 20 (константы комментарием до данных): процесс без `KYTY_FIX_F29` — `FIXF29 env=(unset) on=1`, P1 PASS (0 из 640), 32 строки `overflow`; контроль `=0` — P0 PASS, O1 `out_area` 77 — 20 из 20, O7 `out_buf` 77 — 20 из 20; `ALL OK`. Строки `FixF29: mode=` стенд не печатает (её печатает только конструктор `FaultManager`) — оговорка в отчёте.
- Серия `HPP-800` в `in_progress` — шаги под сторожем, срабатываний 0; замка и STOP не было.
- WIP по дыму: игрой не проверялся (FS14c). Не заявляется — п. 710(з).
