# S9b трека S — правка 1 (HPP-458, п. 377)

Зеркало раздела `## S9b — правка 1` файла `C:/kyty/s288/FACTS.md`; копии — `docs/track-s/s9/` (`06b_s.md` = `C:/kyty/s288/pred/06b_s.md`) и `docs/track-s/s9b/r1/`.

## S9b — правка 1: строка допуска `installed_before` = `540c035a` (п. 374(ж)), печать `pred/06b_s.md` (Harness Engineer, `HPP-458`, п. 377)

Основание — `ROADMAP.md` «СЕССИЯ 122» п. 377(б) (KytyPS5 `a387a2d4`) и п. 374(ж) (KytyPS5 `704c13d2`; комментарий лида `088c2da9`). Игра не запускалась, код эмулятора не трогался. Время — `C:/kyty/s288/s9b/r1/times.txt` (только `date -u`). Правки — `s9b/r1/patch377.py` (sha256 `e793f8703c9f6212d9af3b82309a48fc68dec0600d5fb6c676ee12a01c353825`; оригиналы в `s9b/r1/orig/`). Печать 06 не правилась (`0fb11c0e…`); новое издание — `pred/06b_s.md`. Решения п. 371 не менялись; по п. 377(в) код скорера не менялся.

| файл | sha256 |
|---|---|
| `s9/sc_s9.py` | `b8f5e3faed8c512873553293372e509e4ccfafaedb5d0e4d216da3ead580e39a` |
| `s9/go_s9.sh` | `a44064841674012aeb30033648f6728a4b1a9a527e37f1240f5db78eb8888c2c` |
| `s9/test_sc_s9.py` | `104626d1fb34e0134a1da1ec1dca677a26a547722b4e46a84afbbacf24df344e` |
| `s9/test_go_s9.py` | `bf755259fa510b9fa1e07e5cdc222a1d8ad17e1ce545d8e3fbe38a51c4dd2e55` |
| `s9/mut_sc_s9.py` | `a3664f5a839f673389d87adf3bdd3153c0b6b56af333ce6d14f0eb8acfd1c849` |
| `s9/mkseal_s06b.py` | `493d9b03f59875b98787437ac02b0145d52b9954ef47e866057a1b0e4d55b8ae` |
| `s9/seal06b_body.md` / `seal06b_tail.md` | `09db28896be4d69d27e0687ac1086ae81347f9bcf0eea6dea5136b0e25d6ce73` / `ffdbac7381c25b6da9cd7155e82d9e872ad21936710e1e7958f80783ce3231c0` |
| `pred/06b_s.md` | `605ebfa5440ea1ac318749250c625b022f873d0237b37294cc97ffb069e3560b` |

**(б)(1) Константы.** Харнесс: `INST_WANT="540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1"`, `PRED=pred/06b_s.md`; текст отказа — «!= $INST_WANT (item 374 (g)) - no arm». Скорер: отдельная константа `INST_WANT` = `540c035a…` рядом с `BIN_U` (`4aa62e95…`, закреплённая копия бинаря u, не менялась); строка `cache_rows` — «installed binary before the arm = the installed 540c035a of item 374 (g) (item 371 (g), RC1)», сравнение `ib == INST_WANT`; `PRED_PATH` = `pred/06b_s.md`. Строка печати `u binary:` — прежняя (`4aa62e95…` `C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe`); в §2 печати добавлена строка установленного бинаря `installed_before` = `540c035a…`.

**(б)(2) Фикстуры обоих исходов.** Скорер: A3 (`INST_WANT` = `540c035a`, ≠ `BIN_U`), A6 (печать 06b), F7 (установлен `f3b3aa3b` → падает только эта строка), F7b (установлен `540c035a` → строка проходит у `pi_w1` и `u_2`, строк-провалов нет; установлен `4aa62e95` → падает только эта строка у плеча s и плеча u). Харнесс: в фикстуре установленный бинарь и заглушка бинаря u теперь разные; G23 (`INST_WANT` = `540c035a`, нет `INST_WANT="4aa62e95`, печать 06b), GL1 (игра `pi_w1` видела бинарь s, `installed_before`/`after` = установленный), GL5b (игра `u_1` видела закреплённый бинарь u, установленный ≠ u, установленный вернулся), GL10, GL12 (чужой установленный → `rc 1` внутри замка), GL12b (установлен `4aa62e95` — заглушка u → `rc 1` внутри замка, ничего не установлено, без `IN_ARM` и попытки, замок взят и снят).
- `test_sc_s9.py`: checks: 167, ALL OK — `s9/test_sc_s9.out.txt` sha256 `42b9f2a15ede6f77f3341c501b87ac8b4784c6aed22183e92cc76c665f893310`; первая строка: `suite test_sc_s9.py sha256 104626d1fb34e0134a1da1ec1dca677a26a547722b4e46a84afbbacf24df344e target sc_s9.py sha256 b8f5e3faed8c512873553293372e509e4ccfafaedb5d0e4d216da3ead580e39a`.
- `test_go_s9.py`: checks: 37, ALL OK — `s9/test_go_s9.out.txt` sha256 `738310c2f3c7a475f57c3408a01bf0decae969c866336cbd84463515825716a3`; первая строка: `suite test_go_s9.py sha256 bf755259fa510b9fa1e07e5cdc222a1d8ad17e1ce545d8e3fbe38a51c4dd2e55 target go_s9.sh sha256 a44064841674012aeb30033648f6728a4b1a9a527e37f1240f5db78eb8888c2c`.

**(б)(3) Мутанты — только `--only`** (зачётный полный прогон S9b не повторялся: `s9/mut_sc_s9c.txt` 267 из 268 + `s9b/mut_screen6.txt` 17 из 17). `mutlib` v4.1 `--control --no-memo --workers 12 --only` 25 мутантов строк допуска, пути установки и пути печати (19 строк `cache_rows` с новыми `cr_ib_u`, `cr_ib_old`; константы `inst_want`, `inst_is_u`, `bin_u`; `ad_bin`; `cs_bins`; `pred`): ALL KILLED (25 of 25 selected mutants killed; 272 defined in the mutant script) — `s9b/r1/mut_screen7.txt` sha256 `00d0cebe22c9a16e97332efb7b5c4c34a51241e262bfa0b95ad14f23ca6ece59`, стена 77 с. Ручной мутант харнесса h1 (сравнение с `INST_WANT` выключено, `if false`) через `test_go_s9.py`: rc 1, FAIL GL12 и GL12b — убит; `s9b/r1/hmut_h1.txt` sha256 `092767465d3097cabd2f41c5528e438717c76a1473eace257eeee29487aac9a0`, стена 149 с. Бюджет 30 мин звена S9: ≈ 1 308 + 77 + 149 = 1 534 с из 1 800.

**Регрессия S4/S6:** REGRESSION: ALL OK — `s9/regress_s9.out.txt` sha256 `8444d16522828a63cce31cbe0cd8e5b184fd7932e4659652cb8f466fbb20ffd4` (тот же вывод, что до правки).

**(б)(4)–(5) Печать.** `C:/kyty/s288/pred/06b_s.md` sha256 `605ebfa5440ea1ac318749250c625b022f873d0237b37294cc97ffb069e3560b`, строк `seal:` 29; `sc_s9.py --check-seal --seal pred/06b_s.md` → `SEAL: PASS` (`s9/checkseal_s06b.out.txt` sha256 `9fcccb44149dbb588c9717bc09f8298c5626d26c8c06ace2d51ec1956624744e`). §6 называет п. 371, 374(ж) и 377; строка «S10 stands until a lead item names the new sha» заменена ссылкой на п. 374(ж); в §6 — толкование п. 377(в) («< 2 упавших» — упавших членов S-cat; второе прочтение — строка справки с `DIFFERS (a failing arm without a screen measure)`, слова не даёт).

**«Процесс» (сообщаю сам).** Набор `test_go_s9.py` (111 с) запущен ≈ 07:49Z (оценка по стене, не `date -u`; строка `times.txt` записана после) без проверки API звеньев прогонов перед командой; проверка сразу после (07:50:59Z): `HPP-441`/`449`/`453` — `done`, `HPP-464`/`468`/`433` — `blocked`, `executionRunId` пуст у всех — серии другого трека не было; замка не было. Дальше перед каждой командой дольше 60 с — строка API в `times.txt`.

**Не заявляется:** `FIXED` Б33; что событие `pcw_int` — эффект игры или дефект; что соль без precache нейтрализует кэш драйвера; что гейт `prepare-cold` сработает на настоящем прогоне; полнота каталога; что путь внутри замка пройдёт без ошибки (только фикстуры); ни одно число — не выигрыш; 60 FPS не обещаются; цель (B) не меняется.
