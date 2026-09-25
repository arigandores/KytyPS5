"""ROADMAP: session 116 item 2 (the obs116 observation seal design and the draft's choices), written before sealing."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   процесс с `mutlib.py` в командной строке** (п. 11 с. 115).
"""
NEW = ANCHOR + """2. **Печать 01 `obs116` — наблюдение фаз GuestGpu (записано до печати; черновик агента, ни одного прогона):** один
   вход Sky Garden на `d3a981a2` (исходники = `7c73f26`, `git diff` пуст), 300 с, пин, маркеры 0, без записи видео;
   гейты `gates_obs116.txt` = `gates_base.txt` с `mutsite=1` на месте и `pathlap=1`; окружение **`KYTY_GPU_WALL=1`**
   (стена потока GuestGpu по областям); **`plkstat` не включается** (переводит сайты замка на try-lock и раздувает ожидания,
   с. 106/107); `fslean=0`. Скорер `obs116.py` (новый, фикстуры `test_obs116.py` 193 строки, мутанты `mut_obs116.py`
   113/113 на черновике): вердикт только **ADMITTED / NOT_ADMITTED** (сборка, пин, точное окружение, 300 с, одна попытка,
   гейты и строки `Gate:` до стабильного кадра, `GpuWall: mode 1`, нет маркеров, ≥ 6 000 полных строк сцены, счётчики
   взведены, тождества числа удержаний и emit **с допуском 4**, простой GPU); отчёт — без вердикта о скорости: фазы
   `mh_*` (мкс), `pl_*`/`gw_*` (нс → мкс один раз), доли `cpu_gpu_us`, цена операции, остатки, режим BDA по `bda_scan`.
   **Поправка к с. 96 (найдено агентом):** остаток «вне мьютекса» считается как `pl_proc − a_hold_us − a_wait_us`;
   формула с. 96 `pl_proc − (a_hold_us − mh_pres_us) − named` вычитала `mh_pres_us`, которого в `a_hold_us` нет
   (`MutexMark` стоит только в путях draw/dispatch) — старая форма печатается рядом как `residue_s96`. **Следствия (до
   исхода, неизменны):** ADMITTED ⇒ отчёт — вход шага (3); NOT_ADMITTED ⇒ один повтор `go116a.sh obs116r`; второй ⇒ шаг
   (3) решает без разбивки. **Ограничения:** цена `mutsite` ≈ 0,10 мс на кадр (с. 69), цена `pathlap` и
   `KYTY_GPU_WALL` не замерена; `mh_pres_us` смешивает два потока; непересечение внешних областей не проверено. Цепочка
   `go116a.sh` отказывается, пока есть `C:/kyty/s116/V41_GO`, замок, чужая нагрузка (0,5 CPU·с/с — это замер времени)
   или любой процесс `mutlib`. Мутанты запечатанной копии — `mutlib` v4 (полный прогон, `--workers 2`, пока идёт v4.1)
   или v4.1, если принят к тому времени. Перед печатью — независимая проверка черновика агентом.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
