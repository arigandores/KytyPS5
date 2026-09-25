"""ROADMAP: session 114 item 13 (the go114d outcome - vid114 PASS, boot114 FATAL at commandRecorder.cpp:326), written
before any action on it."""
from pathlib import Path

P = Path('C:/kyty/KytyPS5/docs/ROADMAP.md')
raw = P.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
ANCHOR = """   умолчание 0 (п. 9 (4)). Поправка к п. 10: строка — `PresentOverlap: thread=` (без `frame=`).
"""
NEW = ANCHOR + """13. **Итог цепочки `go114d` (печать 03; записано до действий по нему):** машина CPU 2 %, GPU 0 %; мутанты запечатанной
   копии 93/93, контроли 3/3. **`vid114` — все проверки видео PASS**: 4 010 кадров, 0 глитчей, 3 726 строк сцены, стена
   `UpdateTitle` 29 949 нс на вызов (медиана 25 639), `present_overlap` 0, `cs_sync_new` 0, маркеров нет, режим BDA NEW.
   **`boot114` — `--- Fatal Error ---` `commandRecorder.cpp:326`** (`m_producer != self`) сразу после `PrepareHold`, до
   первой строки `progress`: вердикт `check114` — **NOT_ADMITTED** (`adm_boot_parked`). **Причина по коду** — старый
   скрытый баг, не `titleasync`: кольцо записи планировщика презентации однопроизводительное и отдаётся первому
   записавшему потоку (`BeginRecord`: `m_records == 0` ⇒ владелец — вызывающий); первым пишет поток `VideoOut` (пустой
   `Present` при старте, затем парковка в `UpdateTitle`), а первый же `Present` главного потока в
   `WindowPrepareShaders` падает на проверке владельца. В тёплых прогонах подготовка кончается до первой презентации
   главного потока, поэтому баг не виден; любой долгий старт (холодная подготовка, RenderDoc — падение с. 102 на той же
   строке) его вскрывает. До главного цикла `titleasync` 0 и 1 идут одним ожидающим путём (п. 4), поэтому значение
   ручки на это падение не влияет. **Решения:** (1) повтор п. 12 заменяется двумя контрольными входами под печатью
   **03b** (`bootctl114.py`, фикстуры, мутанты): `boot114b` — как `boot114` (умолчание 1), `boot114c` — то же с
   `KYTY_TITLE_ASYNC=0` в окружении и `gates_title0.txt`. Предсказание: оба падают той же строкой после `PrepareHold`, до
   `startup wait finished`. **Оба так ⇒ падение от ручки не зависит ⇒ `titleasync=1` остаётся** (видео PASS; проверка
   загрузки C1 откладывается до исправления бага); **иначе** (хотя бы один вход без этого падения) ⇒ умолчание 0.
   (2) Исправление бага — первый пункт сессии 115 (владение кольцом презентации при смене потока под взаимным
   исключением `Presenter::Present`/`PrepareBlankFrame`, затем повтор `boot114` под новой печатью); до него долгий старт
   падает при любом значении ручки — это долг корректности §7.
"""
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, NEW)
if crlf:
    s = s.replace('\n', '\r\n')
P.write_bytes(s.encode('utf-8'))
print('patched', P)
