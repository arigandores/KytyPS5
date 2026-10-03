# P31c — поправка текста печати: вход правила P34, печать `07c_p31.md` (трек P, `HPP-435`, Harness Engineer)

Основание — `ROADMAP.md` п. 356(в)(1)–(5) (`dd266ea1:docs/ROADMAP.md:19437` «356. **Звено P32b трека P»; +1 — `:19438` «текста печати звеном P31c»);
RC1 отзыва P32b — `697ae5ea:docs/track-p/p32b-review.md:63` «**RC1. Вход правила P34 не защищён»; +1 — `:64`. Игру не запускал, замка и STOP не было,
сборок нет; `scp31b.py`, `scp31.py`, `gop31.sh`, наборы и мутанты не менялись. Время — `C:/kyty/p283/p31c/times.txt` (`date -u`).

## Итог

- **Печать `C:/kyty/p283/pred/07c_p31.md`** — sha256 `eab31e4f8de0d8f2b08693417bde51f8c2cb21ea94a022ba920e424cdde0400e` (123 строки; копия —
  `docs/track-p/p31c-seal-07c_p31.md`); дополняет `07_p31.md` (`a7d62dd5…`) и `07b_p31.md` (`b8ae563f…`), обе названы полным sha256.
- По п. 356(в): (1) итог P34 — последняя строка `VERDICT_P31B` файла `p31/verdict_p31b.txt`, `VERDICT_P31` — справка (заменяет «итог»
  `43a4f29a:docs/track-p/p31-seal-07_p31.md:220`); (2) шаг §3 одной командой `{ … --check-seal && … --all; } > C:/kyty/p283/p31/verdict_p31b.txt` после
  `hw_V4` и `verdict_p31.txt` (заменяет `8ac0afff:docs/track-p/p31b-seal-07b_p31.md:77`); (3) нет файла / нет `SEAL31B: PASS` / e1, e2, p24, e4 ≠ полям
  последней `VERDICT_P31` — член (1) `NOT_DETERMINED`, чтение `VERDICT_P31` запрещено; (4) `--kbar` — только после `hw_V4` (заменяет `…:79`);
  (5) проверки ниже.
- **Вариант исполнителя** (печать §2 (г)–(ж), вопрос лиду §5(1); только в сторону `NOT_DETERMINED`): нет строки `VERDICT_P31B`; нет `verdict_p31.txt`
  или строки `VERDICT_P31`; `SEAL31B: PASS` после вердикта; mtime `verdict_p31b.txt` раньше `verdict_p31.txt` или лога `hw_V4`.
- **`scp31b.py --check-seal`** на прежних sha, код возврата 0: `SEAL: PASS (35 names)`, `SEAL31B: PASS (5 names; the base seal C:/kyty/p283/pred/07_p31.md
  PASS)` — `C:/kyty/p283/p31c/out/check_seal_p31b.txt` sha256 `83e4eb9930921f9a…` (байт в байт = вывод P31b `p31b/out/check_seal_p31b.txt`).
- **`chk_p31c.py`** (sha256 строк §7 печати против файлов): первая строка `suite chk_p31c sha256 5e061a1d… target 07c_p31.md sha256 eab31e4f…`,
  `CHECK07C: PASS (4 names)` — `out/chk_p31c.txt` sha256 `1d38e2e8990d5f58…`.
- `p31/verdict_p31.txt` и `p31/verdict_p31b.txt` на момент печати отсутствуют (генератор отказывает, если есть).

## Файлы `C:/kyty/p283/p31c/`

`pred_src/seal_body.md` `5058e6d2…` (текст исполнителя), `mkpred_p31c.py` `3b0b2371…` (генератор: п. 356 дословно из `dd266ea1`, sha прежних файлов
с отказом при расхождении, LF), `chk_p31c.py` `5e061a1d…`, `out/`, `times.txt`, этот отчёт.

## Не заявляется

Механизм рывка; что удержание уберёт рывки; что FPS показа не упадёт; что метрика видит любой рывок; ни одно число — не выигрыш; 60 FPS не обещаются;
путь без `KYTY_GAME_PATCH` не меняется. P33 не прогонялся.
