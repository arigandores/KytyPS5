"""ROADMAP: session 114 item 12 (the pre-seal audit of check114 and the decisions on it), written before the changes."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   презентации `VideoOut`, не гость.
"""
NEW = ANCHOR + """12. **Аудит `check114` до печати (агент, только чтение; записано до правок):** BLOCKER нет. **M1** — счётчик
   `present_overlap` до первого флипа гостя уходит в базовую точку `FlipQueue::Flip` и не печатается ни в одной строке
   `FrameTrace-x`; окно загрузки (главный поток презентует только в `WindowPrepareShaders`, гость стартует после) видит
   лишь строка `PresentOverlap:`. **M2** — PASS `boot114` не доказывает, что нагрузка сработала. MINOR: m1 — при неудачной
   гонке старта поток презентации не паркуется вообще и перекрытие возникло бы при любом `titleasync` (ложный FAIL);
   m2 — `title_default_on` — среднее с запасом ≈ 2×; m3 — нет проверки простоя машины; m4 — `startswith` для строки
   перекрытия; m5 — пробелы фикстур/мутантов. **Решения:** (1) M1 — строка `PresentOverlap:` (поиск подстрокой, m4) —
   главный детектор обоих прогонов; сумма `present_overlap` остаётся проверкой после первого флипа; в печати это
   ограничение. (2) M2 — новый допуск **`adm_boot_parked`**: после строки `startup wait finished` первая строка
   `MainTaskLate: us=X` имеет X ≥ 10 000 000 (на Windows главные задачи ставит только `UpdateTitle`, первая — парковка
   потока презентации; в старых логах 208–328 мс) и строк `ShaderPreparation: progress` ≥ 9 с `elapsed_ms` до ≥ 9 000
   (главный поток презентовал всё удержание). (3) m1 — провал допуска даёт **NOT_ADMITTED**, не FAIL. (4) m3 — допуск
   **`adm_idle`**: `pre_run.gpu_util_median` ≤ 10 у обоих прогонов; плюс цепочка `go114d.sh` перед стартом меряет CPU
   (`Win32_Processor.LoadPercentage`, 3 отсчёта) и GPU (`nvidia-smi`) и отказывается при CPU ≥ 15 % или GPU ≥ 10 %.
   (5) m2 — принимается как консервативное (правило печати 02b), медиана по строкам сообщается. (6) m5 — фикстуры на
   каждый маркер смерти и строку перекрытия в середине строки; мутанты на `binary` видео и фильтр `hold_exit`.
   **Вердикты:** NOT_ADMITTED, если провален любой `adm_*`; иначе PASS/FAIL по остальным. **NOT_ADMITTED ⇒ один повтор**
   провалившего допуск прогона под той же печатью (тег с суффиксом `b`, файлы копируются в `C:/kyty/s114/rep` под
   именами печати и оцениваются `--root`); второй NOT_ADMITTED ⇒ умолчание 0 (непроверенное не отгружается). FAIL ⇒
   умолчание 0 (п. 9 (4)). Поправка к п. 10: строка — `PresentOverlap: thread=` (без `frame=`).
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
