"""ROADMAP: session 114 item 4 (the titleasync review verdict and the changes it requires), written before the code."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   запечатываются, но не запускаются; `mutlib` v3 (офлайн) — можно. После разрешения — цепочки по порядку п. 2(4).
"""
NEW = ANCHOR + """4. **Враждебный разбор правки `titleasync` (воркфлоу, 15 агентов, `C:/kyty/s114/review_titleasync.{txt,json}`) и
   решения (записано до кода):** **C1 MAJOR (оба скептика подтвердили, по коду, в прогоне не наблюдалось):** при
   `titleasync=1` с самого старта пропадает неявная «парковка» потока презентации: сегодня его первый `UpdateTitle` ждёт
   главный поток до первого `DrainMainThreadTasks` в `WindowRun`, и только это держит его вне `Presenter::Present`, пока
   `WindowPrepareShaders` (`window.cpp:942-984`, `emulator.cpp:187` до `:197`) сам презентует с главного потока; без
   парковки — два потока в `AcquireNextImage`/`Present` одного swapchain (нарушение внешней синхронизации Vulkan).
   **Фикс:** `titleasync` действует только после старта главного цикла SDL (флаг, выставляемый в `WindowContext::Run`
   до первого `DrainMainThreadTasks`); до того — прежний ожидающий путь; главный поток презентует только в
   `WindowPrepareShaders` (проверено: остальные вызовы `Present` — поток презентации, `videoOut.cpp:831-1177`).
   **C2:** строки `MainThreadWait` и счётчик `pres_title_*` — только после старта цикла. **F1 (MINOR):** контроль
   доказывает работу ручки, а не то, что блокировал заголовок, и после отгрузки ничто не назовёт другого блокирующего ⇒
   инструмент: время удержания `VideoOutConfig::mutex` во `FlipQueue::Flip` по фазам (`flip_hold_ns`/`_n`, строки
   `FlipHold: us= present_us= poll_us= other_us=` > 50 мс, ≤ 32) и возраст задач главного потока от постановки до запуска
   (`mt_age_ns`/`mt_n`, строки `MainTaskLate: us=` > 50 мс, ≤ 32) — занятый главный поток виден и при `titleasync=1`.
   **F2:** `titleasync` закрывает только путь заголовка; прочие блокирующие вызовы под мьютексом (сам `Present`,
   `Gates::Poll`, журнал) остаются — долг §7 с фиксами (b) «не держать мьютекс через `Present`» и (c) «подача буфера перед
   `PrepareVideoOutFlip` при неподанных приоритетных операциях». **C3/D4/F3/F4:** в печати 01 строка рывка ищется как первая
   `FrameTrace: n=` после `MainStallTest: queued`, считаются строки n и n+1, оба входа обязаны содержать строки стоп-теста,
   ручка задаётся одинаково (файлом гейтов), удержание ≥ 120 с после стабилизации, M = 3 000 мс (< 8 с `GpuHangAbort`).
   **D2:** константы порта харнесса устарели (`gates.cpp` 143 записи, 44 вне `gates_base.txt`). **Перед отгрузкой
   `titleasync=1`** — вход с `KYTY_TITLE_ASYNC=1` в окружении при настоящей фазе подготовки шейдеров (видео сборки с
   умолчанием 1 покрывает загрузку). Новая сборка; печати 01/02 готовятся на ней.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
