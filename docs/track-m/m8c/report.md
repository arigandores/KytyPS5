# Трек M, звено M8c (`HPP-860`, Emu Engineer): кандидат MS2. Издание 1: шаг 0 и стоп по подписи

Основание: `ROADMAP.md` «СЕССИЯ 122» п. 778(д), (ж) (KytyPS5 `1ffda330`) и п. 783 (KytyPS5 `1f9de46b`). Игра не запускалась,
замок не брался. Эмулятор MS2 **не собирался**. Время событий — `times.txt` (UTC по `date -u`). **WIP: сборка MS2, G1 и G2
стоят до пункта лида о подписи (§2).**

## 1. Шаг 0 — RC3 M8b (п. 783(г))

| Что | Значение |
|---|---|
| Правка | `MaxDiff` в `tests/MT125Stand.cpp`: неконечный отсчёт выхода ⇒ `+inf` (`std::isfinite`). Было: `std::max(m, NaN)` оставлял `m`, и NaN-смесь сравнивалась как 0 |
| Коммит в `main` | `1ba722f4`, `git show --name-only` — один файл `tests/MT125Stand.cpp` |
| Коммит в worktree MS2 | `fe26f280` (cherry-pick, patch-id `--stable` `d4659e58…` = `main`); `git diff --name-only de23ec44 fe26f280` — один файл |
| `libAudio2.cpp`, бинарь эмулятора | не тронуты (цель стенда `m_t125_stand` — `EXCLUDE_FROM_ALL`) |
| Стенд `main` (worktree `m8c/wtmain` = `1ba722f4`) | драйвер `run_stand_m8a.py` — `ALL OK` (59 членов на плечо) — `stand_main.out.txt` |
| Стенд MS2 (worktree `m8c/wt`) | `ALL OK` (59 членов на плечо) — `stand_wt.out.txt` |
| Мутанты `main` | m1, m2, m3, m4, m9 — `CAUGHT`, контроль `ALL OK` ⇒ `ALL OK` — `mut_m8c_main.out.txt` |
| Мутанты MS2 | то же — `mut_m8c_wt.out.txt` |

m9 (`!(v < 0)` вместо `std::isfinite`, подстановка из `docs/track-m/m8b/mut_m8b.py`) теперь ловят члены `G_f32_invalid_not_applied` и
`G_s16_invalid_not_applied` (`max_diff=inf`); до правки он выживал (M8b, `mut_m8b.out.txt`). Подстановки m1–m4 и m9 взяты из
`mut_m8b.py` байт в байт. Стенд строит `lowrun.py` (Idle), сборка `--parallel 2`.

## 2. Сборка MS2 — стоп по п. 778(д)

Worktree `C:/kyty/m657/m8c/wt` (`mk_wt_m8c.sh`, LF, 0 файлов `src/` с CR):

| Коммит MS2 | Источник | patch-id `--stable` |
|---|---|---|
| `3d227024` | база M6a3 | — |
| `6c795c57` | T306 `91a46dc5` (M7a) | `15dfad37…` = источнику |
| `de23ec44` | T125 `6da84361` (M8a; в `main` `206cdbce`) | `97e3d213…` = источнику |
| `fe26f280` | шаг 0, `main` `1ba722f4` | `d4659e58…` = источнику |
| `3504ecbc` | умолчания MS2: `KYTY_M_T306=1` (`default_on[3]` в `MThemeMask`, маска `0x33` → `0x3b`), `KYTY_M_T125=1` (`MT125On` в форме `MT231On`: не задана или пусто = 1, `0/false/off/no` = 0, иное — `EnvValueOn`) | новый, только в worktree |

Ссылка — `refs/archive/wt/3504ecbced75f64a4a5dbfde85d672f7113c0a86`.

**Хэш исходников транслятора** (`srchash_m8c.py` повторяет `src/generate_version.cmake`: GLOB `src/graphics/shader` + 4 файла
`SHADER_CACHE_EXTRA_FILES`, сортировка, SHA1). Сверка способа: `m7a/wt` → `baeea6e2…`, `m2d/wt` и `m6a/wt` → `8dcf3177…` — равны
отчётам M7a и M2d.

| Дерево | Хэш |
|---|---|
| `fe26f280` (без коммита умолчаний) | `baeea6e209399ed86e67c8f805dddc01ddcf631a` — равен предсказанию |
| `3504ecbc` (MS2 с умолчаниями) | **`0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5` — не равен предсказанию** |

Причина [c]: умолчание T306 задаёт `default_on[]` в `src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp`, а этот файл
входит в набор подписи. Так же было в M2d: коммит умолчаний MS1 вошёл в хэш `8dcf3177`. Предсказание п. 778(д) взяло хэш worktree
M7a, где T306 по умолчанию выключен. По п. 778(д) звено остановлено, вопрос лиду — комментарий `HPP-860` и строка `HPP-3`. Варианты:
(А) принять подпись `KytySC3:0d2da32c…:fixb26:fixb1b:fixf10:fixf19:mw1_3b` — каталог `_mw1_3b` новый при любом хэше, а холодный
первый вход уже учтён гейтом G3; (Б) вынести умолчание T306 за набор подписи, то есть сменить форму M2d. Исполнитель рекомендует (А).

## 3. Строка таблицы умолчаний и отката по RC2 (п. 783(в)) — войдёт в таблицу издания 2

«`KYTY_DIAG_M5W2=1` на MS2 читается только при `KYTY_M_T125=0`; при `KYTY_M_T125=1` счётчики `ao_*` и строка `M5W2Stat:` от
`NoteAudioPush` — 0 по построению, не читаются».

## 4. Файлы (`docs/track-m/m8c/`; рабочая папка — `C:/kyty/m657/m8c/`)

Скрипты: `patch_m8c_step0.py`, `patch_m8c_defaults.py`, `srchash_m8c.py`, `mut_m8c.py`, `mk_wt_m8c.sh`, `mk_scripts_m8c.py`,
`build_m8c.cmd`, `build_m8c_main.cmd`, `bld_m8c.py`, `lowrun.py`. Выводы: `stand_wt.out.txt`, `stand_main.out.txt`,
`mut_m8c_wt.out.txt`, `mut_m8c_main.out.txt`, `cherry.out.txt`, `srchash_nodefaults.out.txt`, `srchash_defaults.out.txt`,
`patch_defaults.out.txt`, `step0_patch_main.out.txt`, `times.txt`.

## 5. Не заявляется

Что MS2 собирается и проходит G1, G2 — эти гейты не запускались. Что подпись `0d2da32c` — подпись, которую напечатает сам код:
проверка ключом кэша (`--m-wave1-cache`) — после сборки. Что смесь T125 слышна. Ни одно число не выигрыш; 60 FPS не обещаются.
