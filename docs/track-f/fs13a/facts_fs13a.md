
## FS13a (`HPP-787`, Emu Engineer) — бинарь отгрузки FS13: умолчание `KYTY_FIX_F25=1` (2026-10-11, UTC)

- Задание — п. 697(г)(1) (KytyPS5 `7d62a36a`). Отчёт `docs/track-f/fs13a.md`, файлы `docs/track-f/fs13a/`, рабочая папка `C:/kyty/f287/fs13a/`.
- Коммит `main` `3630f116` (`--only`, `src/kernel/fileSystem.cpp`): `KYTY_FIX_F25` не задана / `""` → 1, иначе `EnvValueOn`; одно чтение (статическая константа `FixF25Enabled`, первый вызов — `FileSystem::Initialize`); строка `FixF25: mode=` по значению.
- Worktree `C:/kyty/f287/fs13a/wt` HEAD `ea6c6e9e` = FS12 `730ed40a` + `51c9e38f` (`1048af45`), `e9dd8604` (`4bd1e865`), `a28c37d5` (`bc3bb65d`), `49aba6a4` (`0861c391`), `3630f116` (`ea6c6e9e`); конфликтов 0.
- Бинарь FS13 sha256 `abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73`, копия `C:/kyty/f287/bin/kyty_emulator_abab2196.exe` (+ `.sha256`); строка версии `KytyPS5-2026-09-15-6a2987a-1919-gea6c6e9e`; не установка — установленный `46892c20…` до и после.
- `check_gate_order.py` — clean (`main`, worktree); подпись `9177b4267de1fb8bac7d1113afd8733210addfac` = базе; `shader_cfg_tests` = FS12 (133 / 133, `failed:` 0, SPIR-V 360 байт в байт); `kernel_file_system_tests --filesystem-only` при не задана / `0` / `1` — rc 0, `all cases passed`.
- `verify_fs13a.py` `ALL OK`: «содержит» `e9dd8604`, `cbfe8375`, `227e1b36`, `c94c49e0`, `726e751e`, `cb022252` — `git cherry` `-` (отрицательные контроли `+`); вне `tests/`, `docs/` и цели CMake стенда — только `src/kernel/fileSystem.cpp` (10 путей `docs/track-f/f37a/` от `51c9e38f` в сборку не входят); умолчания 17 → 18 (+ `KYTY_FIX_F25`); `KYTY_S_REPLAY` = 3.
- N и seed — комментарий `9a91e732` 01:57:22Z до первого испытания 01:58:17Z. Стенд издания 3 своей сборкой без переменной (seed 38701; A 200, K 50, Z 50, E 50, T 20, G 50 на шести входах) — `MEMBERS LETTER YES`, `FixF25: mode=1`; контроль `=0` (seed 38701) — A «отдано 0» 200/200 на каждом входе; отрицательный контроль (форма умолчания на стенде F38a2, умолчание 0) — `MEMBERS LETTER NO`.
- Сторож отказывал дважды (01:46:57Z, 01:50:21Z): строка `procload.py` в ждущем цикле соседнего звена `HPP-785`; шаг повторён после его конца.
- WIP по дыму: игрой не проверялся (FS13c). Не заявляется — п. 697(з).
