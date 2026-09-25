"""ROADMAP: session 115 item 2 (the build and the boot/video seal 01 design), written before the code and the drafts."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   `KYTY_PREPARE_HOLD_MS`; при PASS — умолчание `titleasync=1` в той же сборке и видео.
"""
NEW = ANCHOR + """2. **Сборка и печать 01 `chk115` (записано до кода и черновиков; нумерация: вердикт v3 — п. 3 или позже):** сборка =
   исправление п. 1 **плюс умолчание `titleasync=1`** (отгрузка решается печатью; до её PASS сборка не остаётся
   установленной). Цепочка `go115a.sh` (замок, простой CPU < 15 % по 3 отсчётам, GPU < 10 %, ни одного чужого процесса
   > 0,5 CPU·с/с по двум снимкам через 10 с): **`vid115`** — видео 120 с, пин, `gates_base.txt` (как `vid114`); **`boot115a`**
   — вход с `KYTY_PREPARE_HOLD_MS=10000`, умолчания; **`boot115b`** — то же плюс `KYTY_PREPARE_MAIN_PRESENT=1`
   (положительный контроль); **`boot115c`** — как `a` плюс `KYTY_TITLE_ASYNC=1` в окружении (конфигурация отгрузки явно).
   Скорер `check115.py` из запечатанного `check114.py` генератором (якоря целыми строками): видео — проверки `vid114`
   (тег, сборка), плюс сообщаемая медиана `bda_scan` (режим BDA); загрузки `a`/`c` — настройка (сборка, пин, удержание в
   окружении, нет расписания/чекпойнтов/сдвига GC/`KYTY_PREPARE_MAIN_PRESENT`, текст гейтов по умолчанию; у `c`
   `KYTY_TITLE_ASYNC=1`), одна допущенная попытка до сцены, ровно одна `PrepareHold: ms=10000`, ровно одна строка
   `startup wait finished in N ms` с N ≥ 10 000, `presents_main=0`, `presents_other` ≥ **300** (≥ 30 в секунду за 10 с),
   ни одной строки `PrepareMainPresent`, `commandRecorder.cpp:326`, `PresentOverlap` и маркеров смерти; загрузка `b` —
   ровно одна `PrepareMainPresent: mode 1`, после `PrepareHold` строка с `commandRecorder.cpp:326`, строки `startup wait
   finished` нет. **Допуск:** `pre_run.gpu_util_median` ≤ 10 у всех четырёх; ожидаемый исход `b` (контроль). **Вердикты
   и следствия (до исхода, неизменны):** NOT_ADMITTED — провал допуска ⇒ один повтор провалившего прогона под этой же
   печатью (суффикс тега `r`); второй NOT_ADMITTED ⇒ как FAIL. **PASS** (все проверки) ⇒ сборка остаётся установленной,
   `titleasync=1` отгружен, C1 закрыт по построению (главный поток не презентует). **FAIL** ⇒ сборка снимается,
   ставится `916f6489`, умолчание 0, исправление пересматривается. Фикстуры — на каждый член, край (`N` 9 999/10 000,
   `presents_other` 299/300, `presents_main` 0/1) и контроль; мутанты — `mutlib` v2 (замороженная копия,
   `--work-dir C:/kyty/s115/work`) на запечатанной копии; перед печатью — независимая проверка черновика агентом.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
