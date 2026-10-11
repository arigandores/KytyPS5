

## F42a2 (`HPP-805`, Emu Engineer) — Ф20: стенд издания 2 (плечо E через `CreateCachedModule` эмулятора), повтор члена (г)(1), бинарь тега F42c (2026-10-11, UTC)

- Задание — `ROADMAP.md` п. 705(б)(1)–(5) (`e4da1f45`). Отчёт `docs/track-f/f42a2.md`, файлы `docs/track-f/f42a2/`, время — `f42a2/times.txt`.
- Код `82570fd2` (`main`, WIP: игрой не проверялся): `CreateCachedModule` вынесена из анонимного пространства имён `pipelineCache.cpp` и объявлена в `pipelineCache.h` (тело = `a9d6fd1c` построчно); геттеры `FixF20::Calls()`, `Rewritten()` (`fixF20.*` +5 / +9, −0 — буква «дифф пуст» п. 705(б)(4) не выполнена, причина — отчёт §1); стенд: плечи E-W, E-X, модуль — `CreateCachedModule(device, перевод, true)` с ручкой `FixF20::Mode()` процесса, `KYTY_PIPELINE_SALT` — отказ. Путей `src/graphics/shader/` 0.
- Стенд издания 2 (R 200, зерно 42051, константы комментарием `e6497623` 10:09:05Z до данных; `=0`/`=1` — отдельные процессы сборки `efa1bf54`): `=0` W `lost` 25 395 200, X 24 348 482, S 0, N 25 395 200, **E-W 25 395 200** (200 из 200), E-X 24 344 311, `calls` 0; `=1` W, X, S, E-W, E-X `lost` 0 во всех 200, N 25 395 200 (`unmatched` 1), `calls` 2, `rewritten` 2; `extra` 0 везде; пересчёт `sum_stand_f42a2.py` `ALL OK`. Первая попытка 11:54Z снята сторожем по шлюзу F44c — не зачётна.
- `check_gate_order.py` clean (worktree и `main`); `shader_cfg_tests` = FS12a (5 строк `failed`, мультимножество равно) при снятой ручке и `=1`; `spirv-val` 12 из 12.
- Бинарь тега F42c — `C:/kyty/f287/bin/kyty_emulator_1994a0ce.exe` sha256 `1994a0ced45c8135f17c8d2aa568278c66375250f1667430c83ba4d0b1a93f29` (≠ `6abebc7b` F42a), версия `KytyPS5-2026-09-15-6a2987a-1917-g5ccb1d31`, подпись `9177b426…` = FS12; worktree `730ed40a` + `23ff0c41` + `adcd0eba` + `5ccb1d31` (`git cherry` `-` `-` `-`); стенд `efa1bf54…`, тесты `779f538d…`.
- Установленный FS13 `abab2196`, `C:/kyty/build`, кэши пользователя не менялись; игра не запускалась; замок не брался.
