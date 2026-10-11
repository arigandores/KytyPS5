
## FS15a (`HPP-820`, Emu Engineer) — пятнадцатый бинарь отгрузки трека F FS15: умолчание `KYTY_FIX_F20=1` (п. 730(г)(1))

- Коммит в `main` `38fc76c1` (`fixF20.cpp` +4/−1, `fixF20.h` +3/−2): `FixF20::Mode` — не задана или `""` = 1, иначе `Common::EnvValueOn`
  (форма `c8836f14` / `3630f116`), одно чтение, строка `FixF20: mode=` по значению; `check_gate_order.py` clean на `main` и worktree.
- Worktree `C:/kyty/f287/fs15a/wt` HEAD `6beb3b73` = FS14 `eb7e8b91` + cherry-pick `a6342c98` → `b1179dab`, `a9d6fd1c` → `95e39a17`,
  `82570fd2` → `91b74d09`, `38fc76c1` → `6beb3b73`; конфликтов 0.
- **Бинарь FS15 sha256 `bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c`**, копия `C:/kyty/f287/bin/kyty_emulator_bfac84be.exe`,
  версия `KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73`; не установлен (установленный FS14 `013e1974…` до и после).
- Члены: «содержит» 15 из 15 (`git cherry` `-`, отрицательные контроли `+`); дифф `src/` против FS14 — 6 путей = файлам трёх F42 и FS15a,
  `src/graphics/shader/**` 0; подпись `9177b426…` = FS14; `shader_cfg_tests` = FS14 (rc 0, `[test]` 133, `failed` 0 / 5 строк, SPIR-V 360
  байт в байт); умолчания 20 → 21 (+ только `KYTY_FIX_F20`), `KYTY_S_REPLAY` = 3; в exe `FixF20: mode=` ×1, `FixF20Stat:` ×1 (FS14 ×0) —
  `verify_fs15a.py`, `binary_fs15a.py`, `run_tests_fs15a.py` `ALL OK`.
- Серия F47d параллельно: сторож убил сборку тестов в 18:06:43Z (`procload`), замок ≈ 18:07Z–18:13:26Z — звено ждало, шаг повторён.
- Отчёт `docs/track-f/fs15a.md`, файлы `docs/track-f/fs15a/`. **WIP по дыму:** игрой не проверялся (FS15c). Не заявляется — п. 730(з).
